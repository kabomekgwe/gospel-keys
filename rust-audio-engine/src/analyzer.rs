//! Audio analysis module for real-time performance evaluation
//!
//! Implements:
//! - YIN pitch detection algorithm
//! - Onset detection (spectral flux + energy)
//! - Dynamic range analysis (RMS, peak, dB)
//!
//! Phase 2: Real-Time Performance Analysis

use serde::{Deserialize, Serialize};

/// Result of pitch detection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PitchResult {
    pub frequency: f32,      // Detected frequency in Hz
    pub confidence: f32,     // Detection confidence (0.0-1.0)
    pub midi_note: u8,       // MIDI note number (21-108, A0-C8)
    pub cents_offset: f32,   // Tuning offset in cents (-50 to +50)
    pub rms_level: f32,      // Audio level (for silence detection)
}

/// Parameters for YIN pitch detection algorithm
#[derive(Debug, Clone)]
pub struct YinParams {
    pub threshold: f32,          // Absolute threshold (default 0.1)
    pub min_frequency: f32,      // Min detectable freq (default 27.5 Hz = A0)
    pub max_frequency: f32,      // Max detectable freq (default 4186 Hz = C8)
    pub sample_rate: u32,        // Audio sample rate (44100 or 48000)
}

impl Default for YinParams {
    fn default() -> Self {
        Self {
            threshold: 0.1,
            min_frequency: 27.5,      // A0
            max_frequency: 4186.0,    // C8
            sample_rate: 44100,
        }
    }
}

/// YIN pitch detection implementation (CPU-based)
///
/// Based on: de Cheveigné, A., & Kawahara, H. (2002).
/// "YIN, a fundamental frequency estimator for speech and music"
/// The Journal of the Acoustical Society of America, 111(4), 1917-1930.
///
/// # Algorithm Overview:
/// 1. Difference function (similar to autocorrelation)
/// 2. Cumulative mean normalized difference function
/// 3. Absolute threshold search
/// 4. Parabolic interpolation for sub-sample accuracy
///
/// # Arguments:
/// * `samples` - Audio samples (mono, f32, normalized to ±1.0)
/// * `params` - YIN algorithm parameters
///
/// # Returns:
/// * `Some(PitchResult)` if pitch detected
/// * `None` if no pitch detected (silence, noise, etc.)
pub fn detect_pitch_yin(samples: &[f32], params: &YinParams) -> Option<PitchResult> {
    // Minimum buffer size check
    if samples.len() < 2048 {
        return None;
    }

    // Calculate RMS for silence detection
    let rms = calculate_rms(samples);
    if rms < 0.01 {
        // Too quiet, likely silence
        return None;
    }

    // Calculate lag range from frequency range
    let min_lag = (params.sample_rate as f32 / params.max_frequency) as usize;
    let max_lag = (params.sample_rate as f32 / params.min_frequency) as usize;
    let buffer_size = samples.len().min(8192); // Use up to 8192 samples
    let half_buffer = buffer_size / 2;

    if max_lag >= half_buffer {
        return None; // Invalid parameters
    }

    // Step 1: Calculate difference function
    let mut diff = vec![0.0f32; half_buffer];
    for tau in 0..half_buffer {
        let mut sum = 0.0;
        for j in 0..half_buffer {
            let delta = samples[j] - samples[j + tau];
            sum += delta * delta;
        }
        diff[tau] = sum;
    }

    // Step 2: Cumulative mean normalized difference function
    let mut cmnd = vec![1.0f32; half_buffer];
    cmnd[0] = 1.0; // By definition

    let mut running_sum = 0.0;
    for tau in 1..half_buffer {
        running_sum += diff[tau];
        if running_sum > 0.0 {
            cmnd[tau] = diff[tau] / (running_sum / tau as f32);
        }
    }

    // Step 3: Absolute threshold search
    let mut tau = min_lag;
    while tau < max_lag {
        if cmnd[tau] < params.threshold {
            // Found a candidate
            while tau + 1 < max_lag && cmnd[tau + 1] < cmnd[tau] {
                tau += 1; // Continue to local minimum
            }
            break;
        }
        tau += 1;
    }

    if tau >= max_lag || cmnd[tau] >= params.threshold {
        // No pitch found
        return None;
    }

    // Step 4: Parabolic interpolation for sub-sample accuracy
    let better_tau = if tau > 0 && tau < half_buffer - 1 {
        let s0 = cmnd[tau - 1];
        let s1 = cmnd[tau];
        let s2 = cmnd[tau + 1];
        tau as f32 + (s2 - s0) / (2.0 * (2.0 * s1 - s0 - s2))
    } else {
        tau as f32
    };

    // Calculate frequency
    let frequency = params.sample_rate as f32 / better_tau;

    // Confidence: inverse of CMND value (lower = better)
    let confidence = 1.0 - cmnd[tau].min(1.0);

    // Convert to MIDI note number
    let midi_note = frequency_to_midi(frequency);

    // Calculate cents offset from nearest MIDI note
    let exact_midi = 69.0 + 12.0 * (frequency / 440.0).log2();
    let cents_offset = (exact_midi - midi_note as f32) * 100.0;

    Some(PitchResult {
        frequency,
        confidence,
        midi_note,
        cents_offset,
        rms_level: rms,
    })
}

/// Calculate RMS (Root Mean Square) level of audio samples
fn calculate_rms(samples: &[f32]) -> f32 {
    if samples.is_empty() {
        return 0.0;
    }

    let sum_squares: f32 = samples.iter().map(|&s| s * s).sum();
    (sum_squares / samples.len() as f32).sqrt()
}

/// Convert frequency (Hz) to MIDI note number
///
/// MIDI note 69 = A4 = 440 Hz
/// Formula: n = 69 + 12 * log2(f / 440)
fn frequency_to_midi(frequency: f32) -> u8 {
    let midi_float = 69.0 + 12.0 * (frequency / 440.0).log2();
    midi_float.round().clamp(21.0, 108.0) as u8
}

/// Convert MIDI note number to frequency (Hz)
fn midi_to_frequency(midi_note: u8) -> f32 {
    440.0 * 2.0f32.powf((midi_note as f32 - 69.0) / 12.0)
}

/// Convert MIDI note number to note name (e.g., "C4", "A#5")
pub fn midi_to_note_name(midi_note: u8) -> String {
    let notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    let note_index = (midi_note as usize) % 12;
    let octave = (midi_note as i32 / 12) - 1;
    format!("{}{}", notes[note_index], octave)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Generate sine wave for testing
    fn generate_sine_wave(frequency: f32, sample_rate: u32, num_samples: usize) -> Vec<f32> {
        (0..num_samples)
            .map(|i| {
                let t = i as f32 / sample_rate as f32;
                (2.0 * std::f32::consts::PI * frequency * t).sin()
            })
            .collect()
    }

    #[test]
    fn test_pitch_detection_a440() {
        // Generate A4 (440 Hz)
        let samples = generate_sine_wave(440.0, 44100, 4096);
        let params = YinParams::default();

        let result = detect_pitch_yin(&samples, &params).unwrap();

        assert!((result.frequency - 440.0).abs() < 2.0, "Frequency should be ~440 Hz");
        assert_eq!(result.midi_note, 69, "MIDI note should be 69 (A4)");
        assert!(result.confidence > 0.9, "Confidence should be high");
        assert!(result.cents_offset.abs() < 10.0, "Should be in tune");
    }

    #[test]
    fn test_pitch_detection_c4() {
        // Generate C4 (261.63 Hz)
        let samples = generate_sine_wave(261.63, 44100, 4096);
        let params = YinParams::default();

        let result = detect_pitch_yin(&samples, &params).unwrap();

        assert!((result.frequency - 261.63).abs() < 2.0);
        assert_eq!(result.midi_note, 60, "MIDI note should be 60 (C4)");
    }

    #[test]
    fn test_silence_returns_none() {
        let samples = vec![0.0; 4096];
        let params = YinParams::default();

        let result = detect_pitch_yin(&samples, &params);

        assert!(result.is_none(), "Silence should return None");
    }

    #[test]
    fn test_low_frequency_a0() {
        // Generate A0 (27.5 Hz) - lowest piano note
        let samples = generate_sine_wave(27.5, 44100, 8192);
        let params = YinParams::default();

        let result = detect_pitch_yin(&samples, &params).unwrap();

        assert!((result.frequency - 27.5).abs() < 2.0);
        assert_eq!(result.midi_note, 21, "MIDI note should be 21 (A0)");
    }

    #[test]
    fn test_high_frequency_c8() {
        // Generate C8 (4186 Hz) - highest piano note
        let samples = generate_sine_wave(4186.0, 44100, 4096);
        let params = YinParams::default();

        let result = detect_pitch_yin(&samples, &params).unwrap();

        assert!((result.frequency - 4186.0).abs() < 10.0);
        assert_eq!(result.midi_note, 108, "MIDI note should be 108 (C8)");
    }

    #[test]
    fn test_rms_calculation() {
        // RMS of sine wave with amplitude A = A / sqrt(2)
        let amplitude = 0.5;
        let samples = generate_sine_wave(440.0, 44100, 1000);
        let scaled: Vec<f32> = samples.iter().map(|&s| s * amplitude).collect();

        let rms = calculate_rms(&scaled);
        let expected = amplitude / 2.0f32.sqrt();

        assert!((rms - expected).abs() < 0.01);
    }

    #[test]
    fn test_frequency_to_midi_conversion() {
        assert_eq!(frequency_to_midi(440.0), 69);   // A4
        assert_eq!(frequency_to_midi(261.63), 60);  // C4
        assert_eq!(frequency_to_midi(880.0), 81);   // A5
        assert_eq!(frequency_to_midi(27.5), 21);    // A0
    }

    #[test]
    fn test_midi_to_note_name() {
        assert_eq!(midi_to_note_name(60), "C4");
        assert_eq!(midi_to_note_name(69), "A4");
        assert_eq!(midi_to_note_name(61), "C#4");
        assert_eq!(midi_to_note_name(21), "A0");
        assert_eq!(midi_to_note_name(108), "C8");
    }

    #[test]
    fn test_buffer_too_small() {
        let samples = vec![0.5; 100]; // Too small
        let params = YinParams::default();

        let result = detect_pitch_yin(&samples, &params);

        assert!(result.is_none(), "Should return None for buffer too small");
    }
}
