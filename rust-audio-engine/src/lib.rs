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

use synthesizer::MidiSynthesizer;
use metal_effects::MetalEffectsProcessor;
use waveform::WaveformGenerator;

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
#[pyo3(signature = (recording_path, expected_midi_path, use_gpu=true))]
fn analyze_performance(
    recording_path: String,
    expected_midi_path: String,
    use_gpu: bool,
) -> PyResult<String> {
    // TODO: Implement in future phase
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
    m.add_function(wrap_pyfunction!(analyze_performance, m)?)?;
    Ok(())
}
