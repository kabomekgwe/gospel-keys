# STORY-2.3: Dynamic Expression Analysis

**Epic**: EPIC-2 (Real-Time Performance Analysis)
**Status**: 📋 Planned
**Priority**: Should Have
**Effort**: 3 story points
**Dependencies**: STORY-2.1 (Pitch Detection)
**Target**: Week 4 of Phase 2

---

## User Story

**As a** piano student working on musical expression
**I want** feedback on my use of dynamics (soft to loud)
**So that** I can develop expressive playing and dynamic control

## Acceptance Criteria

- [ ] Measure RMS (Root Mean Square) level for each note
- [ ] Measure peak amplitude for each note
- [ ] Classify dynamics into standard levels (pp, p, mp, mf, f, ff)
- [ ] Detect dynamic range (difference between softest and loudest notes)
- [ ] Compare to reference MIDI velocity values
- [ ] Visualize dynamics over time
- [ ] Latency <100ms
- [ ] Python API for backend integration
- [ ] Unit and integration tests

## Technical Specification

### Dynamic Levels

| Level | Name | MIDI Velocity | RMS dB Range |
|-------|------|---------------|--------------|
| **pp** | Pianissimo | 1-31 | -60 to -48 dB |
| **p** | Piano | 32-47 | -48 to -36 dB |
| **mp** | Mezzo-piano | 48-63 | -36 to -24 dB |
| **mf** | Mezzo-forte | 64-79 | -24 to -12 dB |
| **f** | Forte | 80-111 | -12 to -6 dB |
| **ff** | Fortissimo | 112-127 | -6 to 0 dB |

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Visualizations:                                      │ │
│  │  - Real-time dynamics meter (pp → ff)                │ │
│  │  - Dynamic range histogram                           │ │
│  │  - Note-by-note velocity comparison                  │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │ WebSocket / REST
                             ↓
┌────────────────────────────────────────────────────────────┐
│                Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  DynamicsAnalyzer Service                             │ │
│  │  - Call Rust RMS/peak analyzer                       │ │
│  │  - Classify into dynamic levels                      │ │
│  │  - Compare to reference MIDI                         │ │
│  │  - Calculate dynamic range score                     │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │ PyO3
                             ↓
┌────────────────────────────────────────────────────────────┐
│            Rust Audio Engine (analyzer.rs)                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  pub fn analyze_dynamics(                             │ │
│  │      audio: &[f32],                                   │ │
│  │      onsets: &[OnsetEvent],                          │ │
│  │      sample_rate: u32                                 │ │
│  │  ) -> Vec<DynamicsEvent> {                           │ │
│  │      let mut results = Vec::new();                   │ │
│  │                                                        │ │
│  │      for i in 0..onsets.len() {                      │ │
│  │          // Extract note segment                     │ │
│  │          let start = onsets[i].sample_index;         │ │
│  │          let end = if i + 1 < onsets.len() {         │ │
│  │              onsets[i+1].sample_index                │ │
│  │          } else {                                     │ │
│  │              audio.len()                              │ │
│  │          };                                            │ │
│  │                                                        │ │
│  │          let segment = &audio[start..end];           │ │
│  │                                                        │ │
│  │          // Calculate RMS and peak                   │ │
│  │          let rms = calculate_rms(segment);           │ │
│  │          let peak = find_peak(segment);              │ │
│  │          let db = amplitude_to_db(rms);              │ │
│  │                                                        │ │
│  │          results.push(DynamicsEvent {                │ │
│  │              timestamp: onsets[i].timestamp,         │ │
│  │              rms_level: rms,                         │ │
│  │              peak_level: peak,                       │ │
│  │              db_level: db,                           │ │
│  │              midi_velocity: db_to_velocity(db),     │ │
│  │          });                                          │ │
│  │      }                                                 │ │
│  │                                                        │ │
│  │      results                                          │ │
│  │  }                                                     │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Data Structures

```rust
// Rust side (rust-audio-engine/src/analyzer.rs)

#[derive(Debug, Clone)]
pub struct DynamicsEvent {
    pub timestamp: f64,        // Time in seconds
    pub rms_level: f32,        // RMS amplitude (0.0-1.0)
    pub peak_level: f32,       // Peak amplitude (0.0-1.0)
    pub db_level: f32,         // Decibels (-60 to 0 dB)
    pub midi_velocity: u8,     // Velocity (0-127)
}

// Helper functions
fn calculate_rms(samples: &[f32]) -> f32 {
    if samples.is_empty() {
        return 0.0;
    }

    let sum_squares: f32 = samples.iter().map(|&s| s * s).sum();
    (sum_squares / samples.len() as f32).sqrt()
}

fn find_peak(samples: &[f32]) -> f32 {
    samples.iter()
        .map(|&s| s.abs())
        .fold(0.0f32, f32::max)
}

fn amplitude_to_db(amplitude: f32) -> f32 {
    if amplitude < 1e-6 {
        -60.0  // Silence floor
    } else {
        20.0 * amplitude.log10()
    }
}

fn db_to_velocity(db: f32) -> u8 {
    // Map -60dB to 0dB → 0 to 127 velocity
    let normalized = (db + 60.0) / 60.0;  // 0.0 to 1.0
    (normalized.clamp(0.0, 1.0) * 127.0) as u8
}
```

```python
# Python side (backend/app/services/dynamics_analyzer.py)

from enum import Enum
from pydantic import BaseModel
from typing import List

class DynamicLevel(str, Enum):
    PIANISSIMO = "pp"
    PIANO = "p"
    MEZZO_PIANO = "mp"
    MEZZO_FORTE = "mf"
    FORTE = "f"
    FORTISSIMO = "ff"

class DynamicsEvent(BaseModel):
    timestamp: float
    rms_level: float
    peak_level: float
    db_level: float
    midi_velocity: int
    dynamic_level: DynamicLevel

class DynamicsScore(BaseModel):
    average_velocity: float          # Average MIDI velocity
    dynamic_range_db: float          # Max - Min dB
    softest_note_db: float
    loudest_note_db: float
    level_distribution: dict[DynamicLevel, int]  # Count per level
    consistency_score: float         # 0-100, lower variance = higher score
    expression_score: float          # 0-100, based on range and variety

class DynamicsAnalyzer:
    @staticmethod
    def classify_dynamic_level(velocity: int) -> DynamicLevel:
        if velocity < 32:
            return DynamicLevel.PIANISSIMO
        elif velocity < 48:
            return DynamicLevel.PIANO
        elif velocity < 64:
            return DynamicLevel.MEZZO_PIANO
        elif velocity < 80:
            return DynamicLevel.MEZZO_FORTE
        elif velocity < 112:
            return DynamicLevel.FORTE
        else:
            return DynamicLevel.FORTISSIMO

    async def analyze(
        self,
        audio_samples: List[float],
        onsets: List[dict],
        sample_rate: int = 44100
    ) -> DynamicsScore:
        # Call Rust analyzer
        events = analyze_dynamics(audio_samples, onsets, sample_rate)

        # Classify each event
        classified_events = [
            DynamicsEvent(
                **event,
                dynamic_level=self.classify_dynamic_level(event["midi_velocity"])
            )
            for event in events
        ]

        # Calculate score
        return self._calculate_score(classified_events)

    def _calculate_score(self, events: List[DynamicsEvent]) -> DynamicsScore:
        if not events:
            return DynamicsScore(
                average_velocity=0,
                dynamic_range_db=0,
                softest_note_db=-60,
                loudest_note_db=-60,
                level_distribution={},
                consistency_score=0,
                expression_score=0
            )

        velocities = [e.midi_velocity for e in events]
        db_levels = [e.db_level for e in events]

        # Dynamic range
        min_db = min(db_levels)
        max_db = max(db_levels)
        dynamic_range = max_db - min_db

        # Level distribution
        distribution = {}
        for level in DynamicLevel:
            distribution[level] = sum(1 for e in events if e.dynamic_level == level)

        # Consistency (inverse of standard deviation)
        import statistics
        std_dev = statistics.stdev(velocities) if len(velocities) > 1 else 0
        consistency = max(0, 100 - std_dev)

        # Expression (reward wider dynamic range)
        expression = min(100, (dynamic_range / 48.0) * 100)  # 48dB = full range

        return DynamicsScore(
            average_velocity=sum(velocities) / len(velocities),
            dynamic_range_db=dynamic_range,
            softest_note_db=min_db,
            loudest_note_db=max_db,
            level_distribution=distribution,
            consistency_score=consistency,
            expression_score=expression
        )
```

### API Endpoint

```python
# backend/app/api/routes/analysis.py

@router.post("/dynamics/analyze")
async def analyze_dynamics(
    audio_file: UploadFile,
    onsets_json: str  # JSON array of onset timestamps
) -> DynamicsScore:
    """
    Analyze dynamic expression in a performance.

    Args:
        audio_file: Audio recording (WAV)
        onsets_json: Detected onset times from rhythm analysis

    Returns:
        DynamicsScore with velocity and expression metrics
    """
    # Load audio
    audio_data = await audio_file.read()
    samples, sample_rate = load_audio(audio_data)

    # Parse onsets
    onsets = json.loads(onsets_json)

    # Analyze
    analyzer = DynamicsAnalyzer()
    score = await analyzer.analyze(samples, onsets, sample_rate)

    return score
```

---

## Implementation Plan

### Phase 1: Rust Implementation (Days 1-2)

- [ ] Implement `calculate_rms()`
- [ ] Implement `find_peak()`
- [ ] Implement `amplitude_to_db()`
- [ ] Implement `db_to_velocity()`
- [ ] Implement `analyze_dynamics()` main function
- [ ] Write Rust unit tests
- [ ] Benchmark performance

### Phase 2: Python Integration (Day 3)

- [ ] Expose `analyze_dynamics()` via PyO3
- [ ] Create `DynamicsAnalyzer` service
- [ ] Implement dynamic level classification
- [ ] Implement scoring logic
- [ ] Write Python integration tests

### Phase 3: Testing & Validation (Day 4)

- [ ] Record test audio at different dynamic levels
- [ ] Validate velocity mapping (RMS → MIDI velocity)
- [ ] Test dynamic range detection
- [ ] Tune dB thresholds if needed

---

## Testing Strategy

### Unit Tests (Rust)

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn test_rms_sine_wave() {
        // RMS of sine wave = amplitude / sqrt(2)
        let amplitude = 0.5;
        let samples: Vec<f32> = (0..1000)
            .map(|i| amplitude * (2.0 * std::f32::consts::PI * i as f32 / 100.0).sin())
            .collect();

        let rms = calculate_rms(&samples);
        let expected = amplitude / 2.0f32.sqrt();

        assert!((rms - expected).abs() < 0.01);
    }

    #[test]
    fn test_db_conversion() {
        assert_eq!(amplitude_to_db(1.0), 0.0);  // Full scale = 0dB
        assert_eq!(amplitude_to_db(0.5), 20.0 * 0.5f32.log10());
        assert_eq!(amplitude_to_db(0.0), -60.0);  // Silence floor
    }

    #[test]
    fn test_velocity_mapping() {
        assert_eq!(db_to_velocity(0.0), 127);   // 0dB = max velocity
        assert_eq!(db_to_velocity(-60.0), 0);   // -60dB = min velocity
        assert_eq!(db_to_velocity(-30.0), 63);  // -30dB = mid velocity
    }
}
```

### Integration Tests (Python)

```python
@pytest.mark.asyncio
async def test_dynamics_classification():
    analyzer = DynamicsAnalyzer()

    # Test each dynamic level
    test_cases = [
        (20, DynamicLevel.PIANISSIMO),
        (40, DynamicLevel.PIANO),
        (55, DynamicLevel.MEZZO_PIANO),
        (70, DynamicLevel.MEZZO_FORTE),
        (95, DynamicLevel.FORTE),
        (120, DynamicLevel.FORTISSIMO),
    ]

    for velocity, expected_level in test_cases:
        level = analyzer.classify_dynamic_level(velocity)
        assert level == expected_level
```

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| Processing latency | <100ms |
| RMS accuracy | ±1 dB |
| Velocity mapping accuracy | ±5 MIDI units |

---

## Definition of Done

- [ ] Code merged to `develop`
- [ ] All tests passing
- [ ] API documented
- [ ] Code reviewed

---

**Created**: 2025-12-15
**Assigned To**: Audio Engine Team
