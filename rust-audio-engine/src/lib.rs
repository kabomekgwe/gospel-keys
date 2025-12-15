//! Rust Audio Engine with Metal GPU Acceleration for M4 MacBook Pro
//!
//! High-performance MIDI synthesis and audio processing using:
//! - rustysynth for SoundFont MIDI synthesis
//! - Metal GPU for effects (reverb, EQ, mixing)
//! - PyO3 for Python integration

use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use std::path::Path;
use anyhow::Result;

mod synthesizer;
mod metal_effects;
mod waveform;
mod analyzer;

use synthesizer::MidiSynthesizer;
use metal_effects::MetalEffectsProcessor;
use waveform::WaveformGenerator;
use analyzer::{detect_pitch_yin, YinParams, PitchResult, detect_onsets, OnsetParams, OnsetEvent};

/// Synthesize a MIDI file to WAV audio with optional GPU effects
///
/// Args:
///     midi_path: Path to input MIDI file
///     output_path: Path to output WAV file
///     soundfont_path: Path to SoundFont (.sf2) file
///     sample_rate: Sample rate in Hz (default: 44100)
///     use_gpu: Enable Metal GPU effects (default: true)
///     reverb: Enable reverb effect (default: true)
///
/// Returns:
///     Duration in seconds of generated audio
#[pyfunction]
#[pyo3(signature = (midi_path, output_path, soundfont_path, sample_rate=44100, use_gpu=true, reverb=true))]
fn synthesize_midi(
    midi_path: String,
    output_path: String,
    soundfont_path: String,
    sample_rate: u32,
    use_gpu: bool,
    reverb: bool,
) -> PyResult<f64> {
    synthesize_midi_internal(
        &midi_path,
        &output_path,
        &soundfont_path,
        sample_rate,
        use_gpu,
        reverb,
    )
    .map_err(|e| PyRuntimeError::new_err(format!("Synthesis failed: {}", e)))
}

fn synthesize_midi_internal(
    midi_path: &str,
    output_path: &str,
    soundfont_path: &str,
    sample_rate: u32,
    use_gpu: bool,
    reverb: bool,
) -> Result<f64> {
    // 1. Synthesize MIDI using rustysynth (CPU)
    let mut synthesizer = MidiSynthesizer::new(soundfont_path, sample_rate)?;
    let audio_samples = synthesizer.synthesize_file(midi_path)?;

    // 2. Apply GPU effects if enabled
    let processed_samples = if use_gpu {
        let mut effects = MetalEffectsProcessor::new()?;
        effects.process(&audio_samples, reverb)?
    } else {
        audio_samples
    };

    // 3. Write to WAV file
    let duration = processed_samples.len() as f64 / sample_rate as f64;
    write_wav(output_path, &processed_samples, sample_rate)?;

    Ok(duration)
}

/// Generate waveform image from audio file
///
/// Args:
///     audio_path: Path to audio file (WAV)
///     width: Image width in pixels
///     height: Image height in pixels
///     use_gpu: Use Metal GPU for faster processing
///
/// Returns:
///     PNG image as bytes
#[pyfunction]
#[pyo3(signature = (audio_path, width=1000, height=200, use_gpu=true))]
fn generate_waveform(
    audio_path: String,
    width: u32,
    height: u32,
    use_gpu: bool,
) -> PyResult<Vec<u8>> {
    let generator = WaveformGenerator::new();
    generator
        .generate(&audio_path, width, height, use_gpu)
        .map_err(|e| PyRuntimeError::new_err(format!("Waveform generation failed: {}", e)))
}

/// Detect pitch in audio samples using YIN algorithm
///
/// Args:
///     audio_samples: Audio samples as Vec<f32> (mono, normalized ±1.0)
///     sample_rate: Sample rate in Hz (default: 44100)
///     use_gpu: Reserved for future GPU implementation (currently unused)
///
/// Returns:
///     Dictionary with pitch detection results or None if no pitch detected
///     {
///         "frequency": float,      // Hz
///         "confidence": float,     // 0.0-1.0
///         "midi_note": int,        // 21-108
///         "cents_offset": float,   // -50 to +50
///         "rms_level": float,      // 0.0-1.0
///         "note_name": str         // e.g., "A4"
///     }
#[pyfunction]
#[pyo3(signature = (audio_samples, sample_rate=44100, use_gpu=false))]
fn detect_pitch(
    py: pyo3::Python,
    audio_samples: Vec<f32>,
    sample_rate: u32,
    use_gpu: bool,
) -> PyResult<Option<pyo3::Py<pyo3::types::PyDict>>> {
    // Note: use_gpu parameter reserved for future Metal GPU implementation
    // Currently uses CPU-based YIN algorithm

    let params = YinParams {
        sample_rate,
        ..Default::default()
    };

    match detect_pitch_yin(&audio_samples, &params) {
        Some(result) => {
            let dict = pyo3::types::PyDict::new_bound(py);
            dict.set_item("frequency", result.frequency)?;
            dict.set_item("confidence", result.confidence)?;
            dict.set_item("midi_note", result.midi_note)?;
            dict.set_item("cents_offset", result.cents_offset)?;
            dict.set_item("rms_level", result.rms_level)?;
            dict.set_item("note_name", analyzer::midi_to_note_name(result.midi_note))?;
            Ok(Some(dict.unbind()))
        }
        None => Ok(None),
    }
}

/// Detect note onsets in audio samples
///
/// Args:
///     audio_samples: Audio samples as Vec<f32> (mono, normalized ±1.0)
///     sample_rate: Sample rate in Hz (default: 44100)
///     hop_size: STFT hop size (default: 256)
///     threshold: Onset detection threshold (default: 0.3)
///
/// Returns:
///     List of dictionaries with onset detection results
///     [
///         {
///             "timestamp": float,      // seconds
///             "sample_index": int,     // sample position
///             "strength": float,       // 0.0-1.0
///             "confidence": float      // 0.0-1.0
///         },
///         ...
///     ]
#[pyfunction]
#[pyo3(signature = (audio_samples, sample_rate=44100, hop_size=256, threshold=0.3))]
fn detect_onsets_python(
    py: pyo3::Python,
    audio_samples: Vec<f32>,
    sample_rate: u32,
    hop_size: usize,
    threshold: f32,
) -> PyResult<Vec<pyo3::Py<pyo3::types::PyDict>>> {
    let params = OnsetParams {
        sample_rate,
        hop_size,
        threshold,
        ..Default::default()
    };

    let onsets = detect_onsets(&audio_samples, &params);

    // Convert to Python list of dicts
    let mut result = Vec::new();
    for onset in onsets {
        let dict = pyo3::types::PyDict::new_bound(py);
        dict.set_item("timestamp", onset.timestamp)?;
        dict.set_item("sample_index", onset.sample_index)?;
        dict.set_item("strength", onset.strength)?;
        dict.set_item("confidence", onset.confidence)?;
        result.push(dict.unbind());
    }

    Ok(result)
}

/// Analyze audio performance against expected MIDI
///
/// Args:
///     recording_path: Path to recorded audio (WAV)
///     expected_midi_path: Path to expected MIDI file
///     use_gpu: Use Metal GPU for FFT analysis
///
/// Returns:
///     JSON string with analysis results
#[pyfunction]
#[pyo3(signature = (_recording_path, _expected_midi_path, _use_gpu=true))]
fn analyze_performance(
    _recording_path: String,
    _expected_midi_path: String,
    _use_gpu: bool,
) -> PyResult<String> {
    // TODO: Implement in future phase (STORY-2.3, 2.4)
    Ok(r#"{"pitch_accuracy": 0.95, "rhythm_accuracy": 0.88}"#.to_string())
}

/// Helper function to write WAV file
fn write_wav(path: &str, samples: &[f32], sample_rate: u32) -> Result<()> {
    let spec = hound::WavSpec {
        channels: 2,  // Stereo
        sample_rate,
        bits_per_sample: 16,
        sample_format: hound::SampleFormat::Int,
    };

    let mut writer = hound::WavWriter::create(path, spec)?;

    for &sample in samples {
        // Convert f32 (-1.0 to 1.0) to i16
        let amplitude = (sample * 32767.0) as i16;
        writer.write_sample(amplitude)?;
    }

    writer.finalize()?;
    Ok(())
}

/// Python module definition
#[pymodule]
fn rust_audio_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(synthesize_midi, m)?)?;
    m.add_function(wrap_pyfunction!(generate_waveform, m)?)?;
    m.add_function(wrap_pyfunction!(detect_pitch, m)?)?;
    m.add_function(wrap_pyfunction!(detect_onsets_python, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_performance, m)?)?;
    Ok(())
}
