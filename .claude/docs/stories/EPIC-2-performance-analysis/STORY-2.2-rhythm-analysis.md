# STORY-2.2: Rhythm Accuracy Analysis

**Epic**: EPIC-2 (Real-Time Performance Analysis)
**Status**: 📋 Planned
**Priority**: Must Have
**Effort**: 5 story points
**Dependencies**: STORY-2.1 (Pitch Detection)
**Target**: Week 3 of Phase 2

---

## User Story

**As a** piano student practicing rhythm and timing
**I want** real-time feedback on my note timing accuracy
**So that** I can develop precise rhythm and stay on tempo

## Acceptance Criteria

- [ ] Detect note onset (attack) with ±50ms accuracy
- [ ] Detect note offset (release) with ±50ms accuracy
- [ ] Calculate Inter-Onset Interval (IOI) between consecutive notes
- [ ] Compare student performance to reference MIDI timing
- [ ] Overall rhythm accuracy >91% on test dataset
- [ ] Detect tempo drift (speeding up or slowing down)
- [ ] Handle rubato (intentional tempo variations)
- [ ] Latency <100ms (onset detection → feedback)
- [ ] Python API for backend integration
- [ ] Unit and integration tests

## Technical Specification

### Algorithm Selection

**Chosen Approach**: Spectral Flux + Energy-Based Onset Detection

**Why**:
- Fast computation (suitable for real-time)
- Works well with piano (percussive transients)
- Robust to background noise
- Compatible with existing pitch detection pipeline

**Workflow**:
1. **Onset Detection**: Identify note attack times
2. **Offset Detection**: Identify note release times
3. **IOI Calculation**: Measure time between onsets
4. **Tempo Tracking**: Estimate current tempo
5. **Accuracy Scoring**: Compare to reference MIDI

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Display:                                             │ │
│  │  - Note timing visualization (reference vs actual)    │ │
│  │  - Tempo graph (expected vs performed)               │ │
│  │  - Accuracy score (% notes on time)                  │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │ WebSocket
                             ↓
┌────────────────────────────────────────────────────────────┐
│                Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  RhythmAnalyzer Service                               │ │
│  │  - Load reference MIDI timing                        │ │
│  │  - Call Rust onset detector                          │ │
│  │  - Calculate IOI and tempo                           │ │
│  │  - Score accuracy vs reference                       │ │
│  │  - Generate feedback                                 │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │ PyO3
                             ↓
┌────────────────────────────────────────────────────────────┐
│            Rust Audio Engine (analyzer.rs)                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  pub fn detect_onsets(                                │ │
│  │      audio: &[f32],                                   │ │
│  │      sample_rate: u32,                                │ │
│  │      use_gpu: bool                                    │ │
│  │  ) -> Vec<OnsetEvent> {                               │ │
│  │      // 1. Short-Time Fourier Transform (STFT)       │ │
│  │      let stft = compute_stft(audio, 512, 256);       │ │
│  │                                                        │ │
│  │      // 2. Spectral flux (change in spectrum)        │ │
│  │      let flux = spectral_flux(&stft);                │ │
│  │                                                        │ │
│  │      // 3. Energy envelope                            │ │
│  │      let energy = compute_energy_envelope(audio);     │ │
│  │                                                        │ │
│  │      // 4. Peak picking                               │ │
│  │      let onsets = find_peaks(&flux, threshold);      │ │
│  │                                                        │ │
│  │      // 5. Refine with energy check                  │ │
│  │      filter_onsets(&onsets, &energy)                 │ │
│  │  }                                                     │ │
│  │                                                        │ │
│  │  pub fn detect_offsets(...) -> Vec<OffsetEvent>      │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Data Structures

```rust
// Rust side (rust-audio-engine/src/analyzer.rs)

#[derive(Debug, Clone)]
pub struct OnsetEvent {
    pub timestamp: f64,      // Time in seconds
    pub sample_index: usize, // Sample position
    pub strength: f32,       // Onset strength (0.0-1.0)
    pub confidence: f32,     // Detection confidence
}

#[derive(Debug, Clone)]
pub struct OffsetEvent {
    pub timestamp: f64,
    pub sample_index: usize,
    pub note_duration: f64,  // Duration from matching onset
}

#[derive(Debug, Clone)]
pub struct OnsetParams {
    pub hop_size: usize,         // STFT hop size (default 256)
    pub threshold: f32,          // Onset threshold (default 0.3)
    pub min_inter_onset: f64,    // Min time between onsets (default 50ms)
    pub energy_threshold: f32,   // Silence gate (default 0.01)
}
```

```python
# Python side (backend/app/services/rhythm_analyzer.py)

from pydantic import BaseModel
from typing import List

class OnsetEvent(BaseModel):
    timestamp: float  # Seconds
    strength: float   # 0.0-1.0
    confidence: float

class RhythmScore(BaseModel):
    accuracy_percent: float      # Overall accuracy (0-100)
    average_deviation_ms: float  # Average timing error
    on_time_notes: int           # Notes within ±50ms
    early_notes: int             # Notes played early
    late_notes: int              # Notes played late
    missed_notes: int            # Expected but not detected
    extra_notes: int             # Detected but not expected
    tempo_drift: float           # % tempo change (+ = faster, - = slower)

class RhythmAnalyzer:
    def __init__(self, reference_midi_path: str):
        self.reference_onsets = self._load_midi_onsets(reference_midi_path)
        self.tolerance_ms = 50  # ±50ms timing tolerance

    async def analyze(
        self,
        audio_samples: List[float],
        sample_rate: int = 44100
    ) -> RhythmScore:
        # Detect onsets in student performance
        detected_onsets = detect_onsets(
            audio_samples,
            sample_rate,
            use_gpu=True
        )

        # Match detected onsets to reference
        matches = self._match_onsets(detected_onsets, self.reference_onsets)

        # Calculate scoring metrics
        return self._calculate_score(matches)
```

### Onset Detection Algorithm

**Step 1: Spectral Flux**
```rust
fn spectral_flux(stft: &[Vec<Complex<f32>>]) -> Vec<f32> {
    let mut flux = vec![0.0; stft.len() - 1];

    for i in 1..stft.len() {
        let mut sum = 0.0;
        for k in 0..stft[i].len() {
            let mag_curr = stft[i][k].norm();
            let mag_prev = stft[i-1][k].norm();
            let diff = mag_curr - mag_prev;
            sum += if diff > 0.0 { diff } else { 0.0 };  // Half-wave rectification
        }
        flux[i - 1] = sum;
    }

    flux
}
```

**Step 2: Peak Picking**
```rust
fn find_peaks(flux: &[f32], threshold: f32) -> Vec<OnsetEvent> {
    let mut onsets = Vec::new();
    let hop_size = 256;
    let sample_rate = 44100;

    for i in 1..flux.len()-1 {
        // Local maximum
        if flux[i] > flux[i-1] && flux[i] > flux[i+1] {
            // Above threshold
            if flux[i] > threshold {
                onsets.push(OnsetEvent {
                    timestamp: (i * hop_size) as f64 / sample_rate as f64,
                    sample_index: i * hop_size,
                    strength: flux[i],
                    confidence: calculate_confidence(flux, i),
                });
            }
        }
    }

    onsets
}
```

### Accuracy Scoring

```python
def _calculate_score(self, matches: List[OnsetMatch]) -> RhythmScore:
    on_time = 0
    early = 0
    late = 0
    total_deviation = 0.0

    for match in matches:
        deviation_ms = (match.detected_time - match.reference_time) * 1000

        if abs(deviation_ms) <= self.tolerance_ms:
            on_time += 1
        elif deviation_ms < 0:
            early += 1
        else:
            late += 1

        total_deviation += abs(deviation_ms)

    # Calculate metrics
    total_notes = len(self.reference_onsets)
    detected_notes = len([m for m in matches if m.detected_time is not None])

    accuracy = (on_time / total_notes) * 100 if total_notes > 0 else 0
    avg_deviation = total_deviation / len(matches) if matches else 0
    missed = total_notes - detected_notes
    extra = len(matches) - total_notes

    return RhythmScore(
        accuracy_percent=accuracy,
        average_deviation_ms=avg_deviation,
        on_time_notes=on_time,
        early_notes=early,
        late_notes=late,
        missed_notes=max(0, missed),
        extra_notes=max(0, extra),
        tempo_drift=self._calculate_tempo_drift(matches)
    )
```

### API Endpoint

```python
# backend/app/api/routes/analysis.py

@router.post("/rhythm/analyze")
async def analyze_rhythm(
    audio_file: UploadFile,
    reference_midi: str  # Path to reference MIDI
) -> RhythmScore:
    """
    Analyze rhythm accuracy of a recorded performance.

    Args:
        audio_file: Student's audio recording (WAV)
        reference_midi: Path to reference MIDI file

    Returns:
        RhythmScore with accuracy metrics
    """
    # Load audio
    audio_data = await audio_file.read()
    samples, sample_rate = load_audio(audio_data)

    # Analyze
    analyzer = RhythmAnalyzer(reference_midi)
    score = await analyzer.analyze(samples, sample_rate)

    return score
```

---

## Implementation Plan

### Phase 1: Onset Detection (Days 1-2)

- [ ] Implement STFT in Rust (512-sample window, 256 hop)
- [ ] Implement spectral flux calculation
- [ ] Implement energy envelope calculation
- [ ] Implement peak picking with adaptive threshold
- [ ] Write Rust unit tests (10+ test cases)
- [ ] Benchmark (target <50ms for 10-second audio)

### Phase 2: Offset Detection (Day 3)

- [ ] Implement energy-based offset detection
- [ ] Match offsets to onsets (note duration)
- [ ] Handle sustained vs staccato notes
- [ ] Write offset detection tests

### Phase 3: Python Integration (Days 4-5)

- [ ] Expose onset/offset detection via PyO3
- [ ] Create `RhythmAnalyzer` service
- [ ] Implement onset matching algorithm
- [ ] Implement accuracy scoring
- [ ] Write Python integration tests

### Phase 4: Testing & Validation (Days 6-7)

- [ ] Record test dataset (50 performances)
- [ ] Generate ground truth onset times
- [ ] Run accuracy tests (target >91%)
- [ ] Tune parameters (threshold, hop size)
- [ ] Document API and usage

---

## Testing Strategy

### Unit Tests (Rust)

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn test_onset_detection_single_note() {
        // Generate impulse at t=1.0s
        let mut audio = vec![0.0; 88200]; // 2 seconds @ 44.1kHz
        audio[44100] = 1.0; // Impulse at 1 second

        let onsets = detect_onsets(&audio, 44100, false);

        assert_eq!(onsets.len(), 1);
        assert!((onsets[0].timestamp - 1.0).abs() < 0.05); // Within 50ms
    }

    #[test]
    fn test_no_false_positives_on_silence() {
        let audio = vec![0.0; 44100];
        let onsets = detect_onsets(&audio, 44100, false);
        assert_eq!(onsets.len(), 0);
    }
}
```

### Integration Tests (Python)

```python
@pytest.mark.asyncio
async def test_rhythm_accuracy_perfect_timing():
    # Load reference MIDI
    analyzer = RhythmAnalyzer("tests/data/c_major_scale.mid")

    # Load perfectly timed audio
    samples, sr = load_audio("tests/data/c_major_scale_perfect.wav")

    score = await analyzer.analyze(samples, sr)

    assert score.accuracy_percent > 95
    assert score.average_deviation_ms < 20
    assert score.missed_notes == 0
```

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| Onset detection latency | <50ms |
| Accuracy (±50ms tolerance) | >91% |
| False positive rate | <10% |
| Processing speed | >10x real-time |

---

## Definition of Done

- [ ] Code merged to `develop`
- [ ] All tests passing
- [ ] Accuracy >91% on test dataset
- [ ] API documented
- [ ] Code reviewed

---

**Created**: 2025-12-15
**Assigned To**: Audio Engine Team
