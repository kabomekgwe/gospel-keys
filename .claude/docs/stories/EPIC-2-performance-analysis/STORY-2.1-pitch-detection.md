# STORY-2.1: Real-Time Pitch Detection with GPU FFT

**Epic**: EPIC-2 (Real-Time Performance Analysis)
**Status**: 📋 Planned
**Priority**: Must Have
**Effort**: 8 story points
**Dependencies**: None
**Target**: Week 1-2 of Phase 2

---

## User Story

**As a** piano student practicing scales and melodies
**I want** real-time detection of which notes I'm playing
**So that** I can immediately see if I'm playing the correct pitches

## Acceptance Criteria

- [ ] System detects fundamental frequency (F0) of piano notes A0-C8 (27.5Hz - 4186Hz)
- [ ] Pitch detection accuracy >91% on test dataset (100 recordings, various skill levels)
- [ ] Detection latency <50ms (audio input → pitch output)
- [ ] GPU-accelerated FFT using Metal API compute shaders
- [ ] Graceful CPU fallback if Metal unavailable
- [ ] Handles polyphonic input (detects strongest pitch when multiple notes played)
- [ ] Python API exposed for backend integration
- [ ] Unit tests cover edge cases (noise, silence, out-of-range frequencies)
- [ ] Integration test with WebAudio API frontend

## Technical Specification

### Algorithm Selection

**Chosen Approach**: YIN Algorithm (de Cheveigné & Kawahara, 2002)

**Why YIN**:
- Designed specifically for musical pitch detection
- Robust to noise and harmonics
- Well-suited for piano (harmonic instruments)
- Computationally efficient for real-time use
- Open-source implementations available

**Alternative considered**: Crepe (deep learning)
- Rejected: Too slow for <50ms latency requirement (100-200ms on GPU)

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Frontend (WebAudio API)                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  navigator.mediaDevices.getUserMedia()               │ │
│  │  → Audio buffer (2048 samples @ 44.1kHz = 46ms)      │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │ WebSocket
                             ↓
┌────────────────────────────────────────────────────────────┐
│                Backend (FastAPI WebSocket)                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Performance Analysis Orchestrator                    │ │
│  │  - Receive audio chunks                              │ │
│  │  - Buffer management (sliding window)                │ │
│  │  - Call Rust pitch detector                          │ │
│  │  - Map frequency → MIDI note number                  │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │ PyO3 call
                             ↓
┌────────────────────────────────────────────────────────────┐
│            Rust Audio Engine (rust-audio-engine)           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  analyzer.rs                                          │ │
│  │                                                       │ │
│  │  pub fn detect_pitch(                                │ │
│  │      audio_samples: &[f32],                          │ │
│  │      sample_rate: u32,                               │ │
│  │      use_gpu: bool                                   │ │
│  │  ) -> Option<PitchResult> {                          │ │
│  │      if use_gpu && metal_available() {               │ │
│  │          detect_pitch_gpu(samples, rate)             │ │
│  │      } else {                                         │ │
│  │          detect_pitch_cpu(samples, rate)             │ │
│  │      }                                                │ │
│  │  }                                                    │ │
│  │                                                       │ │
│  │  GPU Path:                                            │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │ Metal Compute Shader (pitch_detect.metal)      │ │ │
│  │  │ 1. GPU FFT (2048-point, ~2ms on M4)            │ │ │
│  │  │ 2. Autocorrelation in frequency domain         │ │ │
│  │  │ 3. YIN difference function                     │ │ │
│  │  │ 4. Parabolic interpolation for sub-bin accuracy│ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  │                                                       │ │
│  │  CPU Path (Fallback):                                │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │ Rust YIN Implementation                        │ │ │
│  │  │ 1. Difference function (autocorrelation)       │ │ │
│  │  │ 2. Cumulative mean normalization              │ │ │
│  │  │ 3. Absolute threshold (0.1 typical)            │ │ │
│  │  │ 4. Parabolic interpolation                     │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  │                                                       │ │
│  │  Returns:                                             │ │
│  │  struct PitchResult {                                │ │
│  │      frequency: f32,        // Hz                    │ │
│  │      confidence: f32,       // 0.0-1.0               │ │
│  │      midi_note: u8,         // 21-108 (A0-C8)        │ │
│  │      cents_offset: f32,     // -50 to +50            │ │
│  │  }                                                    │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Data Structures

```rust
// Rust side (rust-audio-engine/src/analyzer.rs)

#[derive(Debug, Clone)]
pub struct PitchResult {
    pub frequency: f32,      // Detected frequency in Hz
    pub confidence: f32,     // Detection confidence 0.0-1.0
    pub midi_note: u8,       // MIDI note number (21-108)
    pub cents_offset: f32,   // Tuning offset in cents (-50 to +50)
    pub rms_level: f32,      // Audio level (for silence detection)
}

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
            min_frequency: 27.5,
            max_frequency: 4186.0,
            sample_rate: 44100,
        }
    }
}
```

```python
# Python side (backend/app/services/pitch_analyzer.py)

from rust_audio_engine import detect_pitch
from pydantic import BaseModel

class PitchDetectionResult(BaseModel):
    frequency: float
    confidence: float
    midi_note: int
    cents_offset: float
    note_name: str  # e.g., "A4", "C#5"
    is_in_tune: bool  # True if within ±10 cents

class PitchAnalyzer:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.buffer_size = 2048
        self.sample_rate = 44100

    async def analyze(self, audio_samples: List[float]) -> PitchDetectionResult:
        # Call Rust function
        result = detect_pitch(
            audio_samples=audio_samples,
            sample_rate=self.sample_rate,
            use_gpu=self.use_gpu
        )

        # Convert to Python model
        return PitchDetectionResult(
            frequency=result["frequency"],
            confidence=result["confidence"],
            midi_note=result["midi_note"],
            cents_offset=result["cents_offset"],
            note_name=self._midi_to_note_name(result["midi_note"]),
            is_in_tune=abs(result["cents_offset"]) <= 10
        )
```

### API Endpoint

```python
# backend/app/api/routes/analysis.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.pitch_analyzer import PitchAnalyzer

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.websocket("/pitch/stream")
async def pitch_detection_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time pitch detection.

    Client sends: Audio buffer (Float32Array, 2048 samples)
    Server sends: PitchDetectionResult JSON
    """
    await websocket.accept()
    analyzer = PitchAnalyzer(use_gpu=True)

    try:
        while True:
            # Receive audio samples
            audio_data = await websocket.receive_bytes()
            samples = np.frombuffer(audio_data, dtype=np.float32)

            # Analyze pitch
            result = await analyzer.analyze(samples.tolist())

            # Send result
            await websocket.send_json(result.model_dump())

    except WebSocketDisconnect:
        print("Client disconnected from pitch detection stream")
```

### Performance Requirements

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Latency** | <50ms | Time from audio input to result return |
| **Accuracy** | >91% | % correct notes on test dataset (100 recordings) |
| **Throughput** | 100+ concurrent streams | Load test with 100 WebSocket connections |
| **GPU FFT Time** | <5ms | Metal profiler timing |
| **CPU Fallback Time** | <30ms | Rust benchmark on M4 CPU |
| **False Positive Rate** | <5% | % of silence/noise incorrectly detected as notes |

### Test Dataset

**Create test recordings**:
- 100 piano recordings (50 beginner, 30 intermediate, 20 advanced)
- Cover all octaves A0-C8
- Include: scales, arpeggios, single notes, simple melodies
- Various noise levels (quiet room, background music, traffic)
- Ground truth: MIDI files aligned with audio

**Test cases**:
1. **Single note accuracy**: Play C4, expect MIDI note 60
2. **Octave range**: Test A0 (27.5Hz) to C8 (4186Hz)
3. **Tuning accuracy**: Detect cents offset (sharp/flat detection)
4. **Silence handling**: No output when input is silent
5. **Noise rejection**: Don't detect pitch in pure noise
6. **Polyphonic handling**: Detect strongest note in chord
7. **Latency benchmark**: <50ms on M4 chip
8. **GPU vs CPU accuracy**: Both paths produce same results

---

## Implementation Plan

### Phase 1: CPU YIN Implementation (Days 1-3)

- [ ] Set up `analyzer.rs` module in Rust project
- [ ] Implement CPU-based YIN algorithm:
  - [ ] Difference function (autocorrelation)
  - [ ] Cumulative mean normalization
  - [ ] Absolute threshold search
  - [ ] Parabolic interpolation
- [ ] Implement freq → MIDI note conversion
- [ ] Write Rust unit tests (10+ test cases)
- [ ] Benchmark on M4 (target <30ms for 2048 samples)

### Phase 2: GPU Metal Acceleration (Days 4-6)

- [ ] Write Metal compute shader (`pitch_detect.metal`):
  - [ ] GPU FFT kernel (2048-point)
  - [ ] Autocorrelation in frequency domain
  - [ ] YIN difference function on GPU
- [ ] Integrate Metal shader with Rust (`metal-rs` crate)
- [ ] Benchmark GPU path (target <5ms for FFT)
- [ ] Write GPU-specific tests
- [ ] Ensure GPU/CPU results match (±1Hz tolerance)

### Phase 3: Python Bindings (Days 7-8)

- [ ] Expose `detect_pitch()` via PyO3
- [ ] Create `PitchAnalyzer` service in Python
- [ ] Write integration tests (Python → Rust)
- [ ] Document Python API usage

### Phase 4: WebSocket Integration (Days 9-10)

- [ ] Implement WebSocket endpoint `/analysis/pitch/stream`
- [ ] Handle audio buffer streaming
- [ ] Test with frontend WebAudio API
- [ ] Measure end-to-end latency

### Phase 5: Testing & Optimization (Days 11-12)

- [ ] Record test dataset (100 samples)
- [ ] Run accuracy tests (target >91%)
- [ ] Load test (100 concurrent streams)
- [ ] Optimize if targets not met
- [ ] Documentation and code review

---

## Testing Strategy

### Unit Tests (Rust)

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pitch_detection_a440() {
        // Generate 440Hz sine wave
        let samples = generate_sine_wave(440.0, 44100, 2048);
        let result = detect_pitch(&samples, 44100, false).unwrap();

        assert!((result.frequency - 440.0).abs() < 1.0);
        assert_eq!(result.midi_note, 69); // A4
        assert!(result.confidence > 0.9);
    }

    #[test]
    fn test_silence_returns_none() {
        let samples = vec![0.0; 2048];
        let result = detect_pitch(&samples, 44100, false);

        assert!(result.is_none());
    }

    #[test]
    fn test_gpu_cpu_match() {
        let samples = generate_sine_wave(261.63, 44100, 2048); // C4

        let gpu_result = detect_pitch(&samples, 44100, true).unwrap();
        let cpu_result = detect_pitch(&samples, 44100, false).unwrap();

        assert!((gpu_result.frequency - cpu_result.frequency).abs() < 1.0);
    }
}
```

### Integration Tests (Python)

```python
# backend/tests/test_pitch_analyzer.py

import pytest
from app.services.pitch_analyzer import PitchAnalyzer
import numpy as np

@pytest.mark.asyncio
async def test_pitch_analyzer_c4():
    analyzer = PitchAnalyzer(use_gpu=True)

    # Generate C4 (261.63 Hz)
    t = np.linspace(0, 2048/44100, 2048)
    samples = np.sin(2 * np.pi * 261.63 * t).astype(np.float32)

    result = await analyzer.analyze(samples.tolist())

    assert result.midi_note == 60  # C4
    assert abs(result.frequency - 261.63) < 2.0
    assert result.confidence > 0.9
    assert result.note_name == "C4"

@pytest.mark.asyncio
async def test_latency_under_50ms():
    analyzer = PitchAnalyzer(use_gpu=True)
    samples = [0.0] * 2048

    import time
    start = time.perf_counter()
    await analyzer.analyze(samples)
    duration_ms = (time.perf_counter() - start) * 1000

    assert duration_ms < 50, f"Latency {duration_ms}ms exceeds 50ms target"
```

---

## Dependencies

- **Rust Crates**:
  - `metal-rs` (0.27+) - Metal API bindings
  - `pyo3` (0.20+) - Python bindings
  - `rustfft` (6.1+) - CPU FFT fallback
  - `approx` (0.5+) - Float comparison in tests

- **Python Packages**:
  - `numpy` (already installed) - Audio buffer handling
  - `websockets` (already installed via FastAPI)

- **External**:
  - WebAudio API (browser) - Audio capture
  - Test dataset (to be recorded)

---

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **GPU FFT latency >5ms** | Medium | High | Optimize shader, reduce FFT size if needed |
| **Accuracy <91% on test dataset** | Low | High | Tune YIN threshold, try PYIN variant |
| **Browser mic latency >50ms** | High | Medium | Document min requirements, use low-latency mode |
| **Polyphonic input confuses detector** | High | Low | Document as known limitation, detect strongest pitch |

---

## Definition of Done

- [ ] Code merged to `develop` branch
- [ ] All unit tests passing (Rust + Python)
- [ ] Integration tests passing
- [ ] Accuracy >91% on test dataset
- [ ] Latency <50ms on M4 chip
- [ ] Documentation updated:
  - [ ] API endpoint documented
  - [ ] Python usage examples
  - [ ] Rust function docs
- [ ] Code review completed
- [ ] Performance benchmarks recorded in ADR or EPIC

---

## References

- [YIN Pitch Detection Paper](https://asa.scitation.org/doi/10.1121/1.1458024)
- [Metal Shading Language Guide](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf)
- [PyO3 Documentation](https://pyo3.rs)
- [WebAudio API Spec](https://www.w3.org/TR/webaudio/)
- ADR-001: Rust Audio Engine Architecture

---

**Created**: 2025-12-15
**Last Updated**: 2025-12-15
**Assigned To**: Audio Engine Team
