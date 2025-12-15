# Priority Features - Technical Implementation Guide

**Document Version:** 1.1
**Last Updated:** December 15, 2025
**Status:** Implementation Ready + Production Features

---

## Overview

This document provides detailed technical specifications and implementation guides for six priority features selected for immediate development. All features leverage the existing Rust audio engine (GPU-accelerated) and multi-model LLM service (Phi-3.5 Mini + Qwen2.5-7B).

**Selected Features:**
1. Automatic Music Transcription
2. Personalized Learning Paths
3. AI-Generated Practice Exercises
4. Interactive Music Theory Lessons
5. Composition Assistant
6. Multi-Format Export

---

# Feature 1: Automatic Music Transcription

## Overview

Convert audio recordings (student performances, songs) into sheet music automatically using AI-powered note detection and rhythm analysis.

**Target Accuracy:** 86%+ for monophonic/simple polyphonic content
**Supported Inputs:** WAV, MP3, FLAC, OGG
**Output Formats:** MusicXML, MIDI, PDF sheet music

## Technical Architecture

### Phase 1: Audio Analysis (Rust)

```rust
// File: rust-audio-engine/src/transcriber.rs

use anyhow::Result;
use std::collections::HashMap;

/// Audio transcription service using GPU-accelerated analysis
pub struct AudioTranscriber {
    device: metal::Device,
    fft_pipeline: Option<metal::ComputePipelineState>,
    sample_rate: u32,
}

impl AudioTranscriber {
    pub fn new(use_gpu: bool) -> Result<Self> {
        let device = if use_gpu {
            metal::Device::system_default()
                .context("No Metal device found")?
        } else {
            // CPU fallback
            return Ok(Self::new_cpu());
        };

        let mut transcriber = Self {
            device,
            fft_pipeline: None,
            sample_rate: 44100,
        };

        // Compile FFT shader for pitch detection
        transcriber.compile_fft_shader()?;

        Ok(transcriber)
    }

    /// Transcribe audio file to note events
    pub fn transcribe(&mut self, audio_path: &str) -> Result<TranscriptionResult> {
        // 1. Load audio file
        let audio = load_audio_file(audio_path)?;

        // 2. GPU-accelerated pitch detection
        let pitch_contour = self.detect_pitches_gpu(&audio)?;

        // 3. Note onset detection
        let onsets = self.detect_onsets(&audio)?;

        // 4. Segment into note events
        let notes = self.segment_notes(&pitch_contour, &onsets)?;

        // 5. Detect time signature and tempo
        let tempo = self.detect_tempo(&onsets)?;
        let time_signature = self.detect_time_signature(&onsets)?;

        // 6. Detect key signature
        let key_signature = self.detect_key(&notes)?;

        Ok(TranscriptionResult {
            notes,
            tempo,
            time_signature,
            key_signature,
            confidence: self.calculate_confidence(&notes),
        })
    }

    /// GPU-accelerated pitch detection using FFT
    fn detect_pitches_gpu(&self, audio: &[f32]) -> Result<Vec<PitchFrame>> {
        let frame_size = 4096; // ~93ms @ 44.1kHz
        let hop_size = 1024;   // 75% overlap

        let mut pitches = Vec::new();

        // Process audio in overlapping frames
        for i in (0..audio.len() - frame_size).step_by(hop_size) {
            let frame = &audio[i..i + frame_size];

            // GPU FFT
            let spectrum = self.compute_fft_gpu(frame)?;

            // Extract dominant frequency
            let (frequency, confidence) = self.extract_pitch(&spectrum)?;

            if confidence > 0.5 {
                pitches.push(PitchFrame {
                    time: i as f64 / self.sample_rate as f64,
                    frequency,
                    midi_note: Self::frequency_to_midi(frequency),
                    confidence,
                });
            }
        }

        Ok(pitches)
    }

    /// Detect note onsets using spectral flux
    fn detect_onsets(&self, audio: &[f32]) -> Result<Vec<f64>> {
        let frame_size = 2048;
        let hop_size = 512;

        let mut onsets = Vec::new();
        let mut prev_spectrum = vec![0.0; frame_size / 2];

        for i in (0..audio.len() - frame_size).step_by(hop_size) {
            let frame = &audio[i..i + frame_size];
            let spectrum = self.compute_fft_gpu(frame)?;

            // Calculate spectral flux
            let flux: f32 = spectrum
                .iter()
                .zip(&prev_spectrum)
                .map(|(curr, prev)| (curr - prev).max(0.0))
                .sum();

            // Onset detected if flux exceeds threshold
            if flux > ONSET_THRESHOLD {
                let time = i as f64 / self.sample_rate as f64;
                onsets.push(time);
            }

            prev_spectrum = spectrum;
        }

        Ok(onsets)
    }

    /// Segment pitch contour into discrete notes
    fn segment_notes(
        &self,
        pitches: &[PitchFrame],
        onsets: &[f64]
    ) -> Result<Vec<Note>> {
        let mut notes = Vec::new();
        let mut current_note: Option<Note> = None;

        for pitch in pitches {
            // Check if this is a new note (onset nearby)
            let is_onset = onsets.iter()
                .any(|&onset| (onset - pitch.time).abs() < 0.05);

            if is_onset || current_note.is_none() {
                // Finalize previous note
                if let Some(note) = current_note.take() {
                    notes.push(note);
                }

                // Start new note
                current_note = Some(Note {
                    start_time: pitch.time,
                    end_time: pitch.time,
                    midi_note: pitch.midi_note,
                    velocity: 80, // Default velocity
                    confidence: pitch.confidence,
                });
            } else if let Some(ref mut note) = current_note {
                // Continue current note
                note.end_time = pitch.time;

                // Average pitch for stability
                let new_midi = (note.midi_note + pitch.midi_note) / 2;
                note.midi_note = new_midi;
            }
        }

        // Finalize last note
        if let Some(note) = current_note {
            notes.push(note);
        }

        Ok(notes)
    }

    /// Detect tempo using autocorrelation of onset times
    fn detect_tempo(&self, onsets: &[f64]) -> Result<f32> {
        if onsets.len() < 8 {
            return Ok(120.0); // Default tempo
        }

        // Calculate inter-onset intervals (IOIs)
        let iois: Vec<f64> = onsets
            .windows(2)
            .map(|w| w[1] - w[0])
            .collect();

        // Find most common IOI (beat period)
        let beat_period = Self::mode(&iois)?;

        // Convert to BPM
        let bpm = 60.0 / beat_period;

        // Quantize to reasonable tempos (40-240 BPM)
        Ok(bpm.clamp(40.0, 240.0) as f32)
    }

    /// Detect time signature from onset patterns
    fn detect_time_signature(&self, onsets: &[f64]) -> Result<TimeSignature> {
        // Analyze onset strength patterns
        // Strong-weak patterns suggest meter

        // Simplified: default to 4/4
        // TODO: Implement accent detection
        Ok(TimeSignature {
            numerator: 4,
            denominator: 4,
        })
    }

    /// Detect key signature using pitch class histogram
    fn detect_key(&self, notes: &[Note]) -> Result<KeySignature> {
        // Build pitch class histogram
        let mut histogram = [0; 12]; // C, C#, D, ... B

        for note in notes {
            let pitch_class = (note.midi_note % 12) as usize;
            histogram[pitch_class] += 1;
        }

        // Use Krumhansl-Schmuckler key-finding algorithm
        let key = self.krumhansl_schmuckler(&histogram)?;

        Ok(key)
    }

    /// Convert frequency to MIDI note number
    fn frequency_to_midi(freq: f32) -> u8 {
        let midi = 69.0 + 12.0 * (freq / 440.0).log2();
        midi.round().clamp(0.0, 127.0) as u8
    }

    /// Compile Metal shader for FFT
    fn compile_fft_shader(&mut self) -> Result<()> {
        let shader_source = r#"
            #include <metal_stdlib>
            using namespace metal;

            // FFT kernel for pitch detection
            kernel void compute_fft(
                device const float* input [[buffer(0)]],
                device float* output [[buffer(1)]],
                constant uint& fft_size [[buffer(2)]],
                uint id [[thread_position_in_grid]]
            ) {
                // Simplified FFT (use Metal Performance Shaders in production)
                if (id >= fft_size / 2) return;

                float real = 0.0;
                float imag = 0.0;

                for (uint k = 0; k < fft_size; k++) {
                    float angle = -2.0 * M_PI_F * float(id * k) / float(fft_size);
                    real += input[k] * cos(angle);
                    imag += input[k] * sin(angle);
                }

                output[id] = sqrt(real * real + imag * imag);
            }
        "#;

        let library = self.device
            .new_library_with_source(shader_source, &metal::CompileOptions::new())
            .map_err(|e| anyhow::anyhow!("FFT shader compile failed: {}", e))?;

        let kernel = library
            .get_function("compute_fft", None)
            .map_err(|_| anyhow::anyhow!("FFT kernel not found"))?;

        let pipeline = self.device
            .new_compute_pipeline_state_with_function(&kernel)
            .map_err(|e| anyhow::anyhow!("Pipeline creation failed: {}", e))?;

        self.fft_pipeline = Some(pipeline);
        Ok(())
    }
}

/// Transcription result structure
#[derive(Debug, Clone)]
pub struct TranscriptionResult {
    pub notes: Vec<Note>,
    pub tempo: f32,
    pub time_signature: TimeSignature,
    pub key_signature: KeySignature,
    pub confidence: f32,
}

#[derive(Debug, Clone)]
pub struct Note {
    pub start_time: f64,
    pub end_time: f64,
    pub midi_note: u8,
    pub velocity: u8,
    pub confidence: f32,
}

#[derive(Debug, Clone)]
pub struct PitchFrame {
    pub time: f64,
    pub frequency: f32,
    pub midi_note: u8,
    pub confidence: f32,
}

#[derive(Debug, Clone)]
pub struct TimeSignature {
    pub numerator: u8,
    pub denominator: u8,
}

#[derive(Debug, Clone)]
pub struct KeySignature {
    pub root: u8,        // 0-11 (C=0, C#=1, ...)
    pub mode: KeyMode,   // Major or Minor
}

#[derive(Debug, Clone)]
pub enum KeyMode {
    Major,
    Minor,
}

const ONSET_THRESHOLD: f32 = 0.1;
```

### Phase 2: Export to MusicXML/MIDI

```rust
// File: rust-audio-engine/src/music_export.rs

impl TranscriptionResult {
    /// Export to MIDI file
    pub fn to_midi(&self, output_path: &str) -> Result<()> {
        use midly::{Smf, Track, TrackEventKind, MidiMessage, MetaMessage};

        let mut tracks = vec![Track::new()];
        let track = &mut tracks[0];

        // Set tempo
        let tempo = (60_000_000.0 / self.tempo as f64) as u32;
        track.push(TrackEvent {
            delta: 0.into(),
            kind: TrackEventKind::Meta(MetaMessage::Tempo(tempo.into())),
        });

        // Set time signature
        track.push(TrackEvent {
            delta: 0.into(),
            kind: TrackEventKind::Meta(MetaMessage::TimeSignature(
                self.time_signature.numerator,
                self.time_signature.denominator.ilog2() as u8,
                24,
                8,
            )),
        });

        // Add notes
        let ticks_per_beat = 480;
        for note in &self.notes {
            let start_tick = (note.start_time * self.tempo as f64 / 60.0 * ticks_per_beat as f64) as u32;
            let duration_tick = ((note.end_time - note.start_time) * self.tempo as f64 / 60.0 * ticks_per_beat as f64) as u32;

            // Note On
            track.push(TrackEvent {
                delta: start_tick.into(),
                kind: TrackEventKind::Midi {
                    channel: 0.into(),
                    message: MidiMessage::NoteOn {
                        key: note.midi_note.into(),
                        vel: note.velocity.into(),
                    },
                },
            });

            // Note Off
            track.push(TrackEvent {
                delta: duration_tick.into(),
                kind: TrackEventKind::Midi {
                    channel: 0.into(),
                    message: MidiMessage::NoteOff {
                        key: note.midi_note.into(),
                        vel: 0.into(),
                    },
                },
            });
        }

        // Write MIDI file
        let smf = Smf::new(midly::Header::new(
            midly::Format::SingleTrack,
            midly::Timing::Metrical(ticks_per_beat.into()),
        ));
        smf.save(output_path)?;

        Ok(())
    }

    /// Export to MusicXML
    pub fn to_musicxml(&self, output_path: &str) -> Result<()> {
        // Generate MusicXML structure
        let xml = format!(r#"<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Transcription</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>480</divisions>
        <key>
          <fifths>{}</fifths>
          <mode>{}</mode>
        </key>
        <time>
          <beats>{}</beats>
          <beat-type>{}</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      {}
    </measure>
  </part>
</score-partwise>"#,
            self.key_signature.fifths(),
            match self.key_signature.mode {
                KeyMode::Major => "major",
                KeyMode::Minor => "minor",
            },
            self.time_signature.numerator,
            self.time_signature.denominator,
            self.notes_to_musicxml()
        );

        std::fs::write(output_path, xml)?;
        Ok(())
    }
}
```

### Phase 3: Python API

```python
# File: backend/app/services/transcription_service.py

from rust_audio_engine import transcribe_audio
from typing import Dict, List
import json

class TranscriptionService:
    """Service for automatic music transcription."""

    def __init__(self):
        self.cache_dir = "/storage/transcriptions"

    async def transcribe_recording(
        self,
        audio_path: str,
        output_format: str = "musicxml",  # "musicxml", "midi", "pdf"
        use_gpu: bool = True
    ) -> Dict:
        """
        Transcribe audio to sheet music.

        Args:
            audio_path: Path to audio file (WAV, MP3, FLAC)
            output_format: Desired output format
            use_gpu: Use GPU acceleration for analysis

        Returns:
            {
                "transcription_id": str,
                "notes": List[Note],
                "tempo": float,
                "time_signature": str,
                "key_signature": str,
                "confidence": float,
                "output_path": str
            }
        """
        # Call Rust transcription engine
        result_json = transcribe_audio(
            audio_path=audio_path,
            use_gpu=use_gpu
        )

        result = json.loads(result_json)

        # Export to requested format
        output_path = f"{self.cache_dir}/{result['id']}.{output_format}"

        if output_format == "midi":
            export_to_midi(result, output_path)
        elif output_format == "musicxml":
            export_to_musicxml(result, output_path)
        elif output_format == "pdf":
            # Generate PDF using music21 or similar
            export_to_pdf(result, output_path)

        return {
            "transcription_id": result['id'],
            "notes": result['notes'],
            "tempo": result['tempo'],
            "time_signature": f"{result['time_sig']['num']}/{result['time_sig']['denom']}",
            "key_signature": result['key_signature'],
            "confidence": result['confidence'],
            "output_path": output_path
        }

    async def transcribe_with_ai_cleanup(
        self,
        audio_path: str,
        multi_model_service
    ) -> Dict:
        """
        Transcribe + AI-powered notation cleanup.

        Uses LLM to correct common transcription errors.
        """
        # Step 1: Raw transcription
        transcription = await self.transcribe_recording(audio_path)

        # Step 2: AI review and correction
        if transcription['confidence'] < 0.90:
            correction_prompt = f"""Review this music transcription:
            - Detected notes: {len(transcription['notes'])} notes
            - Key: {transcription['key_signature']}
            - Tempo: {transcription['tempo']} BPM
            - Confidence: {transcription['confidence'] * 100:.1f}%

            Common errors to check:
            1. Octave errors (notes in wrong octave)
            2. Enharmonic spelling (C# vs Db)
            3. Rhythm quantization issues

            Suggest corrections if needed."""

            ai_review = multi_model_service.generate(
                prompt=correction_prompt,
                complexity=6  # Qwen2.5-7B for music theory
            )

            transcription['ai_review'] = ai_review

        return transcription
```

### Usage Example

```python
# FastAPI endpoint
@app.post("/transcribe")
async def transcribe_audio_endpoint(
    file: UploadFile,
    format: str = "musicxml"
):
    """Transcribe uploaded audio to sheet music."""

    # Save uploaded file
    audio_path = f"/tmp/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # Transcribe
    service = TranscriptionService()
    result = await service.transcribe_with_ai_cleanup(
        audio_path=audio_path,
        multi_model_service=multi_model_service
    )

    return {
        "status": "success",
        "transcription": result,
        "download_url": f"/downloads/{result['transcription_id']}.{format}"
    }
```

---

# Feature 2: Personalized Learning Paths

## Overview

AI-generated custom curriculum tailored to each student's skill level, goals, and learning pace. Powered by local LLM for zero-cost personalization at scale.

## Technical Implementation

### Student Profile Schema

```python
# File: backend/app/models/student_profile.py

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class StudentProfile(BaseModel):
    """Comprehensive student learning profile."""

    student_id: int
    current_level: int  # 1-10 scale

    # Skill assessments (0.0 - 1.0)
    skills: Dict[str, float] = {
        "pitch_accuracy": 0.0,
        "rhythm_accuracy": 0.0,
        "sight_reading": 0.0,
        "music_theory": 0.0,
        "ear_training": 0.0,
        "technique": 0.0
    }

    # Learning preferences
    practice_frequency: str  # "daily", "3x_week", "weekend"
    session_duration: int     # minutes per session
    preferred_genres: List[str]
    learning_style: str       # "visual", "auditory", "kinesthetic"

    # Goals
    short_term_goals: List[str]
    long_term_goals: List[str]
    target_songs: List[str]

    # Performance history
    total_practice_hours: float
    completed_exercises: int
    practice_consistency_score: float  # 0.0 - 1.0

    # Weaknesses to address
    identified_weaknesses: List[str]

    # Last updated
    updated_at: datetime
```

### AI Curriculum Generator

```python
# File: backend/app/services/curriculum_service.py

from app.services.multi_model_service import MultiModelService
from app.models.student_profile import StudentProfile
from pydantic import BaseModel
from typing import List

class LessonPlan(BaseModel):
    """Weekly lesson plan structure."""
    week_number: int
    focus_areas: List[str]
    daily_exercises: List[Dict]
    milestone_song: str
    theory_topics: List[str]
    estimated_duration: int  # minutes

class CurriculumService:
    """Generate personalized learning paths using AI."""

    def __init__(self, multi_model_service: MultiModelService):
        self.llm = multi_model_service

    async def generate_curriculum(
        self,
        student_profile: StudentProfile,
        weeks: int = 4
    ) -> List[LessonPlan]:
        """
        Generate personalized multi-week curriculum.

        Args:
            student_profile: Student's current state and preferences
            weeks: Number of weeks to plan

        Returns:
            List of weekly lesson plans
        """
        # Build comprehensive prompt
        prompt = self._build_curriculum_prompt(student_profile, weeks)

        # Generate curriculum using Qwen2.5-7B
        curriculum_json = self.llm.generate(
            prompt=prompt,
            complexity=7,  # Complex structured generation
            response_format=CurriculumSchema,
            max_tokens=4000
        )

        # Parse and enhance with Rust-generated audio
        curriculum = self._parse_and_enhance(curriculum_json, student_profile)

        return curriculum

    def _build_curriculum_prompt(
        self,
        profile: StudentProfile,
        weeks: int
    ) -> str:
        """Build detailed curriculum generation prompt."""

        # Identify top 3 weaknesses
        weaknesses = sorted(
            profile.skills.items(),
            key=lambda x: x[1]
        )[:3]

        # Identify top 3 strengths
        strengths = sorted(
            profile.skills.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        prompt = f"""You are an expert music education curriculum designer. Generate a personalized {weeks}-week learning plan for a student with the following profile:

**Student Level:** {profile.current_level}/10

**Current Skills:**
{chr(10).join(f"- {skill}: {score * 100:.1f}%" for skill, score in profile.skills.items())}

**Strengths:**
{chr(10).join(f"- {skill}: {score * 100:.1f}%" for skill, score in strengths)}

**Areas Needing Improvement:**
{chr(10).join(f"- {skill}: {score * 100:.1f}%" for skill, score in weaknesses)}

**Learning Preferences:**
- Practice frequency: {profile.practice_frequency}
- Session duration: {profile.session_duration} minutes
- Preferred genres: {', '.join(profile.preferred_genres)}
- Learning style: {profile.learning_style}

**Goals:**
Short-term: {', '.join(profile.short_term_goals)}
Long-term: {', '.join(profile.long_term_goals)}

**Instructions:**
Generate a {weeks}-week curriculum that:
1. Addresses the student's weaknesses (focus on {weaknesses[0][0]}, {weaknesses[1][0]})
2. Builds on their strengths ({strengths[0][0]}, {strengths[1][0]})
3. Incorporates their preferred genres
4. Matches their {profile.learning_style} learning style
5. Fits {profile.session_duration}-minute practice sessions
6. Includes progressive difficulty
7. Balances technique, theory, and musicality

For each week, provide:
- Focus areas (2-3 skills)
- Daily exercises (specific, actionable)
- One milestone song to learn
- Music theory topics
- Estimated practice time

Output as structured JSON."""

        return prompt

    async def _parse_and_enhance(
        self,
        curriculum_json: str,
        profile: StudentProfile
    ) -> List[LessonPlan]:
        """Parse LLM output and enhance with Rust-generated audio."""

        curriculum = json.loads(curriculum_json)
        enhanced_lessons = []

        for week_data in curriculum['weeks']:
            lesson = LessonPlan(**week_data)

            # Generate audio for each exercise using Rust engine
            for exercise in lesson.daily_exercises:
                if 'midi_sequence' in exercise:
                    # Rust synthesizes the exercise
                    audio_path = await self._generate_exercise_audio(
                        exercise['midi_sequence'],
                        exercise['id']
                    )
                    exercise['audio_url'] = audio_path

            enhanced_lessons.append(lesson)

        return enhanced_lessons

    async def _generate_exercise_audio(
        self,
        midi_sequence: List[int],
        exercise_id: str
    ) -> str:
        """Generate audio for practice exercise using Rust engine."""

        from rust_audio_engine import synthesize_midi

        # Create MIDI file from sequence
        midi_path = self._create_midi_from_sequence(midi_sequence, exercise_id)

        # Synthesize with Rust
        audio_path = f"/storage/exercises/{exercise_id}.wav"
        synthesize_midi(
            midi_path=midi_path,
            output_path=audio_path,
            soundfont_path="/data/soundfonts/piano.sf2",
            use_gpu=True,
            reverb=True
        )

        return audio_path

    async def adapt_curriculum_realtime(
        self,
        student_id: int,
        recent_performance: Dict
    ) -> LessonPlan:
        """
        Adapt curriculum based on recent performance.

        If student is struggling or excelling, adjust difficulty.
        """
        profile = await self._get_student_profile(student_id)

        # Analyze recent performance
        adaptation_needed = self._analyze_performance(recent_performance)

        if adaptation_needed:
            adjustment_prompt = f"""The student's recent performance shows:
            - Pitch accuracy: {recent_performance['pitch_accuracy'] * 100:.1f}%
            - Rhythm accuracy: {recent_performance['rhythm_accuracy'] * 100:.1f}%
            - Practice consistency: {recent_performance['consistency']}

            Current curriculum difficulty: Level {profile.current_level}

            Should we:
            1. Maintain current difficulty
            2. Increase difficulty (student excelling)
            3. Decrease difficulty (student struggling)
            4. Shift focus to different skill areas

            Provide reasoning and adjusted exercises for next week."""

            adjustment = self.llm.generate(
                prompt=adjustment_prompt,
                complexity=6
            )

            # Apply adjustments
            next_week = self._apply_adjustments(adjustment, profile)
            return next_week

        return await self._get_next_lesson(student_id)
```

### Adaptive Difficulty System

```python
# File: backend/app/services/adaptive_difficulty.py

class AdaptiveDifficultySystem:
    """Dynamically adjust difficulty based on performance."""

    def calculate_optimal_difficulty(
        self,
        student_profile: StudentProfile,
        recent_sessions: List[PracticeSession]
    ) -> float:
        """
        Calculate optimal difficulty level (1.0 - 10.0).

        Uses "Zone of Proximal Development" principle:
        - Too easy → boredom
        - Too hard → frustration
        - Just right → flow state
        """
        # Analyze recent performance trend
        accuracy_trend = self._calculate_trend(
            [s.avg_accuracy for s in recent_sessions]
        )

        current_difficulty = student_profile.current_level

        # Adjustment rules
        if accuracy_trend > 0.90:
            # Student excelling → increase difficulty
            new_difficulty = current_difficulty + 0.5
        elif accuracy_trend < 0.70:
            # Student struggling → decrease difficulty
            new_difficulty = current_difficulty - 0.5
        else:
            # Sweet spot → maintain
            new_difficulty = current_difficulty

        # Clamp to valid range
        return max(1.0, min(10.0, new_difficulty))

    def select_exercises(
        self,
        difficulty: float,
        focus_skill: str
    ) -> List[Exercise]:
        """Select exercises matching difficulty and skill focus."""

        # Query exercise database
        exercises = Exercise.query.filter(
            Exercise.skill_type == focus_skill,
            Exercise.difficulty >= difficulty - 0.5,
            Exercise.difficulty <= difficulty + 0.5
        ).all()

        return exercises
```

---

# Feature 3: AI-Generated Practice Exercises

## Overview

Generate unlimited, contextually relevant practice exercises on-demand using AI + Rust synthesis pipeline.

## Implementation

### Exercise Generator

```python
# File: backend/app/services/exercise_generator.py

from pydantic import BaseModel
from typing import List, Optional

class ExerciseRequest(BaseModel):
    """Request parameters for exercise generation."""
    skill_type: str  # "scales", "arpeggios", "chords", "sight_reading", "rhythm"
    difficulty: int  # 1-10
    key_signature: str  # "C", "Am", "F#", etc.
    duration_bars: int
    tempo: int
    special_focus: Optional[str] = None  # "triplets", "syncopation", etc.

class GeneratedExercise(BaseModel):
    """Generated exercise with audio."""
    exercise_id: str
    title: str
    description: str
    midi_notes: List[int]
    audio_url: str
    sheet_music_url: Optional[str]
    difficulty: int
    estimated_duration: int  # seconds

class ExerciseGenerator:
    """Generate practice exercises using AI + Rust synthesis."""

    def __init__(self, multi_model_service, audio_service):
        self.llm = multi_model_service
        self.audio = audio_service

    async def generate_exercise(
        self,
        request: ExerciseRequest
    ) -> GeneratedExercise:
        """
        Generate custom practice exercise.

        Workflow:
        1. LLM generates MIDI note sequence
        2. Rust synthesizes to audio
        3. Optionally generate sheet music
        """
        # Step 1: LLM generates exercise
        prompt = self._build_exercise_prompt(request)

        exercise_json = self.llm.generate(
            prompt=prompt,
            complexity=5,  # Phi-3.5 Mini sufficient for exercises
            response_format=ExerciseSchema
        )

        exercise_data = json.loads(exercise_json)

        # Step 2: Rust synthesizes audio
        audio_url = await self._synthesize_exercise(exercise_data)

        # Step 3: Generate sheet music (optional)
        sheet_music_url = None
        if request.include_sheet_music:
            sheet_music_url = await self._generate_sheet_music(exercise_data)

        return GeneratedExercise(
            exercise_id=exercise_data['id'],
            title=exercise_data['title'],
            description=exercise_data['description'],
            midi_notes=exercise_data['notes'],
            audio_url=audio_url,
            sheet_music_url=sheet_music_url,
            difficulty=request.difficulty,
            estimated_duration=exercise_data['duration']
        )

    def _build_exercise_prompt(self, request: ExerciseRequest) -> str:
        """Build LLM prompt for exercise generation."""

        return f"""Generate a {request.skill_type} practice exercise with these parameters:

**Requirements:**
- Skill type: {request.skill_type}
- Difficulty: {request.difficulty}/10
- Key: {request.key_signature}
- Duration: {request.duration_bars} bars
- Tempo: {request.tempo} BPM
{f"- Special focus: {request.special_focus}" if request.special_focus else ""}

**Instructions:**
1. Create an exercise appropriate for difficulty level {request.difficulty}
2. Use the key of {request.key_signature}
3. Make it exactly {request.duration_bars} bars long
4. Include helpful practice tips
5. Output MIDI note numbers with timing

**Output Format (JSON):**
{{
  "title": "Descriptive title",
  "description": "What this exercise trains",
  "notes": [
    {{"midi": 60, "start": 0.0, "duration": 0.5}},  // Middle C, quarter note
    {{"midi": 62, "start": 0.5, "duration": 0.5}},  // D, quarter note
    ...
  ],
  "practice_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Generate the exercise now:"""

    async def _synthesize_exercise(self, exercise_data: Dict) -> str:
        """Convert exercise to audio using Rust engine."""

        from rust_audio_engine import synthesize_midi

        # Create MIDI file
        midi_path = f"/tmp/exercise_{exercise_data['id']}.mid"
        self._notes_to_midi(exercise_data['notes'], midi_path)

        # Synthesize
        audio_path = f"/storage/exercises/{exercise_data['id']}.wav"
        synthesize_midi(
            midi_path=midi_path,
            output_path=audio_path,
            soundfont_path="/data/soundfonts/piano.sf2",
            use_gpu=True,
            reverb=False  # Dry sound for exercises
        )

        return f"/audio/exercises/{exercise_data['id']}.wav"

    def _notes_to_midi(self, notes: List[Dict], output_path: str):
        """Convert note list to MIDI file."""

        # Use mido or similar library
        from mido import MidiFile, MidiTrack, Message

        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Add notes
        for note in notes:
            # Note On
            track.append(Message(
                'note_on',
                note=note['midi'],
                velocity=64,
                time=int(note['start'] * 480)  # Convert to ticks
            ))

            # Note Off
            track.append(Message(
                'note_off',
                note=note['midi'],
                velocity=0,
                time=int(note['duration'] * 480)
            ))

        mid.save(output_path)
```

### Exercise Types

```python
# Predefined exercise templates

EXERCISE_TYPES = {
    "scales": {
        "major": "Ascending and descending major scale",
        "minor_natural": "Natural minor scale pattern",
        "minor_harmonic": "Harmonic minor with raised 7th",
        "chromatic": "All 12 notes ascending/descending"
    },

    "arpeggios": {
        "major_triad": "Root, 3rd, 5th pattern",
        "minor_triad": "Minor chord arpeggiation",
        "dominant_7th": "7th chord arpeggio",
        "diminished": "Diminished chord pattern"
    },

    "chord_progressions": {
        "I_IV_V_I": "Basic major progression",
        "ii_V_I": "Jazz turnaround",
        "I_vi_IV_V": "50s progression",
        "circle_of_fifths": "Full circle progression"
    },

    "rhythm": {
        "quarter_notes": "Steady quarter note pulse",
        "eighth_notes": "Even eighth note subdivision",
        "triplets": "Triplet feel exercises",
        "syncopation": "Off-beat rhythm patterns",
        "dotted_rhythms": "Dotted quarter and eighth"
    },

    "sight_reading": {
        "stepwise_motion": "Mostly adjacent notes",
        "interval_jumps": "Practice larger intervals",
        "key_signature_reading": "Accidentals in context",
        "rhythm_reading": "Complex rhythmic patterns"
    },

    "ear_training": {
        "interval_recognition": "Identify melodic intervals",
        "chord_quality": "Major vs minor vs diminished",
        "melodic_dictation": "Remember and repeat melodies",
        "rhythm_dictation": "Clap back rhythm patterns"
    }
}
```

---

# Feature 4: Interactive Music Theory Lessons

## Overview

AI tutor that explains music theory concepts with interactive audio examples, Socratic questioning, and instant practice feedback.

## Implementation

### Music Theory Tutor

```python
# File: backend/app/services/theory_tutor.py

class MusicTheoryTutor:
    """Interactive AI music theory teacher."""

    def __init__(self, multi_model_service, audio_service):
        self.llm = multi_model_service
        self.audio = audio_service
        self.conversation_history = []

    async def teach_concept(
        self,
        concept: str,
        student_question: Optional[str] = None
    ) -> Dict:
        """
        Teach a music theory concept interactively.

        Args:
            concept: Topic to teach (e.g., "intervals", "chord progressions")
            student_question: Optional specific question

        Returns:
            {
                "explanation": str,
                "audio_examples": List[str],
                "practice_exercise": Dict,
                "follow_up_questions": List[str]
            }
        """
        # Build teaching prompt
        prompt = self._build_teaching_prompt(concept, student_question)

        # Generate explanation using Qwen2.5-7B
        response = self.llm.generate(
            prompt=prompt,
            complexity=6,  # Music theory requires nuanced explanation
            max_tokens=1500
        )

        # Parse response
        lesson = self._parse_lesson(response)

        # Generate audio examples using Rust
        audio_urls = await self._generate_audio_examples(lesson['examples'])

        # Create practice exercise
        practice = await self._create_practice_exercise(concept)

        return {
            "explanation": lesson['explanation'],
            "audio_examples": audio_urls,
            "practice_exercise": practice,
            "follow_up_questions": lesson['follow_up_questions']
        }

    def _build_teaching_prompt(
        self,
        concept: str,
        question: Optional[str]
    ) -> str:
        """Build Socratic teaching prompt."""

        base_prompt = f"""You are an expert music theory teacher using the Socratic method.

Topic: {concept}

{f'Student question: {question}' if question else ''}

Teaching guidelines:
1. Start with a clear, simple explanation
2. Use analogies and real-world examples
3. Provide 2-3 musical examples (describe as MIDI sequences)
4. Ask thought-provoking follow-up questions
5. Connect to practical music-making
6. Be encouraging and supportive

Previous conversation:
{self._format_conversation_history()}

Respond with:
- Explanation (2-3 paragraphs)
- Musical examples (as MIDI note sequences)
- Practice suggestion
- 2-3 follow-up questions to deepen understanding"""

        return base_prompt

    async def _generate_audio_examples(
        self,
        examples: List[Dict]
    ) -> List[str]:
        """Generate audio for theory examples using Rust."""

        audio_urls = []

        for idx, example in enumerate(examples):
            # Create MIDI from example description
            midi_path = self._concept_to_midi(example)

            # Synthesize with Rust
            audio_path = f"/storage/theory/{example['id']}.wav"
            await self.audio.synthesize_midi(
                midi_path=midi_path,
                output_path=audio_path,
                soundfont_path="/data/soundfonts/piano.sf2",
                use_gpu=True
            )

            audio_urls.append(f"/audio/theory/{example['id']}.wav")

        return audio_urls

    async def answer_student_question(
        self,
        question: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Answer student's music theory question.

        Uses conversation history for context.
        """
        self.conversation_history.append({
            "role": "student",
            "content": question
        })

        prompt = f"""Student asks: "{question}"

{f'Context: {context}' if context else ''}

Provide a clear, helpful answer that:
1. Directly addresses the question
2. Includes a musical example if relevant
3. Connects to broader concepts
4. Suggests next learning step

Answer:"""

        answer = self.llm.generate(
            prompt=prompt,
            complexity=6
        )

        self.conversation_history.append({
            "role": "tutor",
            "content": answer
        })

        # Generate audio example if mentioned
        audio_url = None
        if "example:" in answer.lower():
            audio_url = await self._generate_example_from_text(answer)

        return {
            "answer": answer,
            "audio_example": audio_url
        }
```

### Example Concepts

```python
THEORY_CONCEPTS = {
    "intervals": {
        "title": "Musical Intervals",
        "subtopics": [
            "Major and minor seconds",
            "Perfect intervals (4th, 5th, octave)",
            "Augmented and diminished intervals",
            "Interval inversion"
        ]
    },

    "scales": {
        "title": "Scales and Modes",
        "subtopics": [
            "Major scale construction",
            "Minor scales (natural, harmonic, melodic)",
            "Pentatonic scales",
            "Modes of major scale"
        ]
    },

    "chords": {
        "title": "Chord Theory",
        "subtopics": [
            "Triads (major, minor, diminished, augmented)",
            "7th chords",
            "Chord inversions",
            "Extended chords (9th, 11th, 13th)"
        ]
    },

    "progressions": {
        "title": "Chord Progressions",
        "subtopics": [
            "Diatonic progressions",
            "ii-V-I (jazz)",
            "Circle of fifths",
            "Modal interchange"
        ]
    },

    "rhythm": {
        "title": "Rhythm and Meter",
        "subtopics": [
            "Note values and rests",
            "Time signatures",
            "Syncopation",
            "Polyrhythm"
        ]
    },

    "harmony": {
        "title": "Harmonic Analysis",
        "subtopics": [
            "Roman numeral analysis",
            "Functional harmony",
            "Non-chord tones",
            "Modulation"
        ]
    }
}
```

---

# Feature 5: Composition Assistant

## Overview

AI-powered composition tool that helps students create original music using text prompts, with instant audio playback via Rust synthesis.

## Implementation

### Composition Service

```python
# File: backend/app/services/composition_service.py

class CompositionAssistant:
    """AI composition helper for students."""

    def __init__(self, multi_model_service, audio_service):
        self.llm = multi_model_service
        self.audio = audio_service

    async def compose_from_prompt(
        self,
        prompt: str,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Generate musical composition from text prompt.

        Args:
            prompt: User description (e.g., "sad piano melody in A minor")
            constraints: Optional parameters (tempo, length, style, etc.)

        Returns:
            {
                "composition_id": str,
                "midi_data": bytes,
                "audio_url": str,
                "sheet_music_url": str,
                "description": str
            }
        """
        # Build composition prompt
        full_prompt = self._build_composition_prompt(prompt, constraints)

        # Generate composition using Qwen2.5-7B
        composition_json = self.llm.generate(
            prompt=full_prompt,
            complexity=7,  # Complex creative task
            response_format=CompositionSchema,
            max_tokens=3000
        )

        composition = json.loads(composition_json)

        # Synthesize with Rust
        audio_url = await self._synthesize_composition(composition)

        # Generate sheet music
        sheet_music_url = await self._generate_sheet_music(composition)

        return {
            "composition_id": composition['id'],
            "midi_data": composition['midi'],
            "audio_url": audio_url,
            "sheet_music_url": sheet_music_url,
            "description": composition['description']
        }

    def _build_composition_prompt(
        self,
        user_prompt: str,
        constraints: Optional[Dict]
    ) -> str:
        """Build detailed composition generation prompt."""

        return f"""You are a skilled music composer. Create an original composition based on this description:

**User Request:** {user_prompt}

**Constraints:**
{self._format_constraints(constraints) if constraints else '- None specified (composer\'s choice)'}

**Composition Guidelines:**
1. Create a cohesive, musical piece
2. Use appropriate harmony for the mood
3. Include variation and development
4. Consider voice leading and counterpoint
5. Make it playable and musically satisfying

**Output Format (JSON):**
{{
  "title": "Composition title",
  "description": "Brief description of the piece",
  "key": "Key signature",
  "tempo": 120,
  "time_signature": "4/4",
  "sections": [
    {{
      "name": "A (Main Theme)",
      "bars": 8,
      "notes": [
        {{"midi": 60, "start": 0.0, "duration": 1.0, "velocity": 80}},
        ...
      ]
    }},
    {{
      "name": "B (Contrasting Section)",
      ...
    }}
  ],
  "composition_notes": "Explanation of compositional choices"
}}

Compose now:"""

    async def iterate_composition(
        self,
        composition_id: str,
        feedback: str
    ) -> Dict:
        """
        Modify existing composition based on user feedback.

        Examples:
        - "Make the middle section more dramatic"
        - "Add a bass line"
        - "Change to major key"
        """
        # Load existing composition
        composition = await self._load_composition(composition_id)

        # Generate modification
        modification_prompt = f"""Original composition:
{json.dumps(composition, indent=2)}

User feedback: "{feedback}"

Modify the composition to incorporate this feedback while maintaining musical coherence.

Output the complete modified composition in the same JSON format."""

        modified = self.llm.generate(
            prompt=modification_prompt,
            complexity=7
        )

        # Re-synthesize
        audio_url = await self._synthesize_composition(json.loads(modified))

        return {
            "composition_id": composition_id,
            "audio_url": audio_url,
            "changes_made": self._summarize_changes(composition, modified)
        }

    async def harmonize_melody(
        self,
        melody_midi: List[int],
        style: str = "classical"
    ) -> Dict:
        """
        Add harmony to a user-provided melody.

        Args:
            melody_midi: MIDI note sequence
            style: Harmonization style ("classical", "jazz", "pop", etc.)

        Returns:
            Full composition with melody + harmony
        """
        prompt = f"""Add {style}-style harmony to this melody:

Melody (MIDI notes): {melody_midi}

Create:
1. Chord progression that supports the melody
2. Bass line
3. Optional inner voices (for 4-part harmony)

Follow {style} harmonic practices.

Output as full composition JSON:"""

        harmonized = self.llm.generate(
            prompt=prompt,
            complexity=7,
            response_format=CompositionSchema
        )

        composition = json.loads(harmonized)
        audio_url = await self._synthesize_composition(composition)

        return {
            "composition": composition,
            "audio_url": audio_url
        }

    async def generate_variations(
        self,
        theme: Dict,
        num_variations: int = 3
    ) -> List[Dict]:
        """
        Generate variations on a musical theme.

        Classical variation techniques:
        - Rhythmic variation
        - Melodic ornamentation
        - Harmonic reharmonization
        - Textural changes
        """
        prompt = f"""Create {num_variations} variations on this musical theme:

{json.dumps(theme, indent=2)}

Use classical variation techniques:
1. Variation 1: Rhythmic variation (change note durations)
2. Variation 2: Melodic ornamentation (add passing tones, trills)
3. Variation 3: Harmonic variation (different chord progression)

Output as array of variation objects."""

        variations_json = self.llm.generate(
            prompt=prompt,
            complexity=7,
            max_tokens=4000
        )

        variations = json.loads(variations_json)

        # Synthesize each variation
        for variation in variations:
            variation['audio_url'] = await self._synthesize_composition(variation)

        return variations
```

### Style Transfer

```python
async def apply_style_transfer(
    self,
    composition: Dict,
    target_style: str
) -> Dict:
    """
    Transform composition to different musical style.

    Examples:
    - "Make this sound like Chopin"
    - "Jazz version"
    - "Baroque style"
    """
    prompt = f"""Transform this composition into {target_style} style:

Original:
{json.dumps(composition, indent=2)}

Target style: {target_style}

Apply stylistic characteristics of {target_style}:
- Typical harmonic progressions
- Characteristic rhythms
- Melodic contours
- Texture and voicing

Output transformed composition:"""

    styled = self.llm.generate(
        prompt=prompt,
        complexity=7,
        max_tokens=4000
    )

    styled_composition = json.loads(styled)
    audio_url = await self._synthesize_composition(styled_composition)

    return {
        "composition": styled_composition,
        "audio_url": audio_url,
        "style_analysis": styled_composition.get('style_notes', '')
    }
```

---

# Feature 6: Multi-Format Export

## Overview

Export audio and sheet music in multiple formats for sharing, submission, and archival.

## Implementation

### Export Service

```python
# File: backend/app/services/export_service.py

from enum import Enum

class AudioFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    AAC = "aac"

class SheetMusicFormat(str, Enum):
    PDF = "pdf"
    MUSICXML = "musicxml"
    MIDI = "midi"
    PNG = "png"

class ExportService:
    """Multi-format export for audio and sheet music."""

    def __init__(self, audio_service):
        self.audio = audio_service

    async def export_audio(
        self,
        audio_id: str,
        format: AudioFormat,
        quality: str = "high"  # "low", "medium", "high", "lossless"
    ) -> bytes:
        """
        Export audio in requested format.

        Args:
            audio_id: ID of audio file to export
            format: Target audio format
            quality: Quality preset

        Returns:
            Exported audio bytes
        """
        # Load source audio (WAV)
        source_path = f"/storage/audio/{audio_id}.wav"

        if format == AudioFormat.WAV:
            # Already WAV, return as-is or re-encode for quality
            return await self._read_file(source_path)

        elif format == AudioFormat.MP3:
            return await self._export_mp3(source_path, quality)

        elif format == AudioFormat.FLAC:
            return await self._export_flac(source_path, quality)

        elif format == AudioFormat.OGG:
            return await self._export_ogg(source_path, quality)

        elif format == AudioFormat.AAC:
            return await self._export_aac(source_path, quality)

    async def _export_mp3(
        self,
        source_path: str,
        quality: str
    ) -> bytes:
        """Export to MP3 using ffmpeg."""

        # Quality presets
        bitrates = {
            "low": "128k",
            "medium": "192k",
            "high": "320k"
        }

        bitrate = bitrates.get(quality, "192k")
        output_path = f"/tmp/export_{uuid.uuid4()}.mp3"

        # Use ffmpeg via subprocess
        cmd = [
            "ffmpeg", "-i", source_path,
            "-codec:a", "libmp3lame",
            "-b:a", bitrate,
            "-ar", "44100",
            output_path
        ]

        await asyncio.create_subprocess_exec(*cmd)

        # Read and return
        data = await self._read_file(output_path)
        os.remove(output_path)
        return data

    async def _export_flac(
        self,
        source_path: str,
        quality: str
    ) -> bytes:
        """Export to FLAC (lossless)."""

        # Compression levels for FLAC (0-8)
        compression = {
            "low": "0",      # Fastest
            "medium": "5",   # Default
            "high": "8"      # Best compression
        }

        level = compression.get(quality, "5")
        output_path = f"/tmp/export_{uuid.uuid4()}.flac"

        cmd = [
            "ffmpeg", "-i", source_path,
            "-codec:a", "flac",
            "-compression_level", level,
            output_path
        ]

        await asyncio.create_subprocess_exec(*cmd)

        data = await self._read_file(output_path)
        os.remove(output_path)
        return data

    async def export_sheet_music(
        self,
        midi_id: str,
        format: SheetMusicFormat
    ) -> bytes:
        """
        Export sheet music in requested format.

        Args:
            midi_id: ID of MIDI file
            format: Target format (PDF, MusicXML, PNG)

        Returns:
            Exported sheet music bytes
        """
        midi_path = f"/storage/midi/{midi_id}.mid"

        if format == SheetMusicFormat.MIDI:
            # Return MIDI as-is
            return await self._read_file(midi_path)

        elif format == SheetMusicFormat.MUSICXML:
            return await self._midi_to_musicxml(midi_path)

        elif format == SheetMusicFormat.PDF:
            return await self._midi_to_pdf(midi_path)

        elif format == SheetMusicFormat.PNG:
            return await self._midi_to_png(midi_path)

    async def _midi_to_pdf(self, midi_path: str) -> bytes:
        """Convert MIDI to PDF sheet music using music21."""

        from music21 import converter, environment

        # Load MIDI
        score = converter.parse(midi_path)

        # Configure music21 for PDF export
        environment.set('musicxmlPath', '/usr/bin/musescore')

        # Export to PDF
        output_path = f"/tmp/score_{uuid.uuid4()}.pdf"
        score.write('pdf', fp=output_path)

        # Read and return
        data = await self._read_file(output_path)
        os.remove(output_path)
        return data

    async def _midi_to_musicxml(self, midi_path: str) -> bytes:
        """Convert MIDI to MusicXML."""

        from music21 import converter

        score = converter.parse(midi_path)
        output_path = f"/tmp/score_{uuid.uuid4()}.musicxml"
        score.write('musicxml', fp=output_path)

        data = await self._read_file(output_path)
        os.remove(output_path)
        return data

    async def create_video_with_scrolling_score(
        self,
        audio_id: str,
        midi_id: str
    ) -> str:
        """
        Create YouTube-style video with scrolling sheet music.

        Returns:
            URL to generated video
        """
        # 1. Generate sheet music images (frame by frame)
        frames = await self._generate_score_frames(midi_id)

        # 2. Sync with audio timeline
        video_path = await self._create_video_from_frames(
            frames=frames,
            audio_path=f"/storage/audio/{audio_id}.wav"
        )

        return video_path

    async def batch_export(
        self,
        items: List[Dict],
        formats: List[str]
    ) -> str:
        """
        Export multiple items in multiple formats.

        Returns:
            ZIP file path containing all exports
        """
        import zipfile

        zip_path = f"/tmp/export_{uuid.uuid4()}.zip"

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for item in items:
                for format in formats:
                    data = await self.export_audio(item['id'], format)
                    zipf.writestr(f"{item['name']}.{format}", data)

        return zip_path
```

### FastAPI Endpoints

```python
# File: backend/app/routes/export.py

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/export/audio/{audio_id}")
async def export_audio_endpoint(
    audio_id: str,
    format: AudioFormat = AudioFormat.MP3,
    quality: str = "high"
):
    """Export audio file in requested format."""

    service = ExportService(audio_service)
    data = await service.export_audio(audio_id, format, quality)

    return Response(
        content=data,
        media_type=f"audio/{format}",
        headers={
            "Content-Disposition": f"attachment; filename={audio_id}.{format}"
        }
    )

@router.get("/export/sheet-music/{midi_id}")
async def export_sheet_music_endpoint(
    midi_id: str,
    format: SheetMusicFormat = SheetMusicFormat.PDF
):
    """Export sheet music in requested format."""

    service = ExportService(audio_service)
    data = await service.export_sheet_music(midi_id, format)

    media_types = {
        "pdf": "application/pdf",
        "musicxml": "application/vnd.recordare.musicxml+xml",
        "midi": "audio/midi",
        "png": "image/png"
    }

    return Response(
        content=data,
        media_type=media_types[format],
        headers={
            "Content-Disposition": f"attachment; filename={midi_id}.{format}"
        }
    )

@router.post("/export/batch")
async def batch_export_endpoint(request: BatchExportRequest):
    """Export multiple files in multiple formats as ZIP."""

    service = ExportService(audio_service)
    zip_path = await service.batch_export(request.items, request.formats)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="export.zip"
    )
```

---

## Integration Summary

### Technology Stack Utilization

**Rust Audio Engine:**
- ✅ GPU-accelerated FFT (transcription, analysis)
- ✅ MIDI synthesis (exercises, compositions, examples)
- ✅ Audio export (WAV baseline for format conversion)

**Multi-Model LLM:**
- ✅ Phi-3.5 Mini: Quick exercises, simple explanations (Complexity 1-4)
- ✅ Qwen2.5-7B: Curriculum generation, theory teaching, composition (Complexity 5-7)
- ✅ Zero cost at scale (local processing)

**Combined Workflow Example:**
```
User: "I want to learn jazz piano"
    ↓
LLM generates personalized 4-week curriculum
    ↓
For each exercise in curriculum:
    LLM generates MIDI sequence → Rust synthesizes → Student practices
    ↓
Student records practice attempt
    ↓
Rust analyzes performance (GPU FFT pitch detection)
    ↓
LLM interprets results → Personalized feedback
    ↓
Adapt next lesson based on performance
```

---

## Next Steps

1. **Review implementation priorities**
2. **Create detailed Control Manifests for each feature**
3. **Begin with highest ROI features**:
   - Personalized Learning Paths (easiest, LLM-only)
   - AI-Generated Exercises (LLM + Rust synthesis)
   - Multi-Format Export (infrastructure)

4. **Parallel development tracks**:
   - Track 1: Rust engine enhancements (transcription, analysis)
   - Track 2: LLM service integration (curriculum, theory, composition)
   - Track 3: Export infrastructure

---

**Document Owner:** Development Team
**Implementation Status:** Ready for Development
**Estimated Timeline:** 4-6 weeks for all features

---

# Feature 7: Music Generator System

## Overview

**Status:** ✅ Production Ready

The Music Generator System is a comprehensive AI-powered music composition engine that spans 5 distinct genres (Gospel, Jazz, Blues, Classical, Neo-Soul) with **32 scales**, **36 chord types**, and genre-specific patterns for left/right hand voicings and rhythms.

**Core Capabilities:**
- Natural language input → Full MIDI arrangement
- Genre-specific musical intelligence
- GPU-accelerated MIDI synthesis (Rust engine)
- 32 scales from major modes to exotic world scales
- 36 chord types from triads to complex alterations
- Genre-authentic rhythm and voicing patterns
- Real-time audio playback with professional-quality SoundFont rendering

**Technical Position:**
- **Frontend:** Natural language input + MIDI player + analysis display
- **Backend:** FastAPI routes → Genre-specific generators → Gemini API for progressions
- **Rust Engine:** GPU-accelerated MIDI → WAV synthesis
- **LLM Integration:** Gemini Pro for chord progression generation

---

## Architecture

### System Flow

```
User Input (Natural Language)
    ↓
FastAPI Endpoint (/[genre]/generate)
    ↓
Genre Service (gospel_generator.py, jazz_generator.py, etc.)
    ↓
Gemini API (Chord Progression Generation)
    ↓
Genre-Specific Arranger (arranger.py)
    ├─ Left Hand Pattern Selection
    ├─ Right Hand Pattern Selection
    ├─ Rhythm Pattern Application
    ├─ Improvisation Insertion (context-aware)
    └─ Dynamic Expression (velocity curves)
    ↓
MIDI File Creation
    ↓
[Optional] Rust GPU Synthesis → WAV Audio
    ↓
Response: {
  midi_base64,
  chord_progression,
  metadata,
  note_preview
}
```

### Technology Stack Integration

**AI/LLM:**
- **Gemini Pro API:** Natural language → Chord progressions
- Converts text like "uplifting gospel song in C major" to structured chord sequence
- Context-aware progression generation based on genre conventions

**Rule-Based Arrangement:**
- Genre-specific arrangers apply musical intelligence
- Pattern libraries for authentic genre sound
- Context-aware improvisation insertion

**Rust Audio Engine:**
- GPU-accelerated MIDI synthesis (optional)
- Professional SoundFont rendering
- Export-ready WAV audio

---

## Scale Library (32 Scales Total)

### Implementation

```python
# File: backend/app/theory/scale_library.py

SCALE_LIBRARY = {
    # Major Modes (7 scales)
    "Ionian": {
        "intervals": [2, 2, 1, 2, 2, 2, 1],
        "description": "Major Scale - bright, happy",
        "use_cases": ["Pop", "Classical", "Gospel", "All genres"]
    },
    "Dorian": {
        "intervals": [2, 1, 2, 2, 2, 1, 2],
        "description": "Minor with raised 6th - jazz favorite",
        "use_cases": ["Jazz", "Folk", "Neo-Soul"]
    },
    # ... (continues for all 32 scales)
}
```

### Complete Scale Catalog

| Category | Scales | Count |
|----------|--------|-------|
| **Major Modes** | Ionian (Major), Dorian, Phrygian, Lydian, Mixolydian, Aeolian (Natural Minor), Locrian | 7 |
| **Minor Variants** | Harmonic Minor, Melodic Minor (Jazz Minor) | 2 |
| **Blues & Pentatonic** | Blues Scale, Major Blues, Major Pentatonic, Minor Pentatonic | 4 |
| **Symmetric & Advanced** | Whole Tone, Diminished (W-H), Diminished (H-W), Altered Scale, Lydian Dominant, Bebop Dominant, Bebop Major, Bebop Minor, Augmented Scale | 9 |
| **Exotic & World** | Phrygian Dominant, Hungarian Minor, Double Harmonic Major, Hirajoshi, Iwato, Yo Scale | 6 |
| **Gospel Specific** | Gospel Minor Scale, Gospel Pentatonic with #4, Gospel Blues Scale, Gospel Melodic Minor | 4 |

### Scale Details

**Major Modes (7):**
- **Ionian (Major):** Bright, happy - all genres
- **Dorian:** Minor with raised 6th - jazz/folk favorite
- **Phrygian:** Spanish/Flamenco with b2
- **Lydian:** Dreamy, floating with #4
- **Mixolydian:** Blues/rock with b7
- **Aeolian (Natural Minor):** Standard minor scale
- **Locrian:** Diminished mode with b2 and b5

**Minor Variants (2):**
- **Harmonic Minor:** Natural minor with raised 7th (dramatic resolution)
- **Melodic Minor (Jazz Minor):** Minor with raised 6th and 7th (smooth melodic motion)

**Blues & Pentatonic (4):**
- **Blues Scale:** Minor pentatonic + added b5 "blue note"
- **Major Blues:** Major pentatonic + added b3
- **Major Pentatonic:** 5-note major (rock/country staple)
- **Minor Pentatonic:** 5-note minor (rock & blues foundation)

**Symmetric & Advanced (9):**
- **Whole Tone:** All whole steps - augmented/dreamy sound (Debussy)
- **Diminished (Whole-Half):** Alternating W-H - tension/resolution
- **Diminished (Half-Whole):** Alternating H-W - dominant function
- **Altered Scale (Super Locrian):** 7th mode of melodic minor - jazz alterations
- **Lydian Dominant:** 4th mode of melodic minor - #4 + b7
- **Bebop Dominant:** Mixolydian + added M7 (8-note scale)
- **Bebop Major:** Major + added #5 (8-note)
- **Bebop Minor (Bebop Dorian):** Dorian + added M3 (8-note)
- **Augmented Scale:** Alternating m3-m2 pattern

**Exotic & World (6):**
- **Phrygian Dominant:** Spanish/Middle Eastern - b2 with major 3rd
- **Hungarian Minor:** Eastern European gypsy minor - exotic augmented 2nd intervals
- **Double Harmonic Major:** Arabic/Byzantine - two augmented 2nds
- **Hirajoshi:** Japanese pentatonic - traditional koto sound
- **Iwato:** Japanese with unsettling quality - no perfect 5th
- **Yo Scale:** Traditional Japanese pentatonic - serene, pentatonic

---

## Chord Library (36 Types Total)

### Implementation

```python
# File: backend/app/theory/chord_library.py

CHORD_LIBRARY = {
    # Triads (6 types)
    "major": {
        "intervals": [0, 4, 7],  # Root, M3, P5
        "symbols": ["", "M", "maj"],
        "quality": "consonant",
        "function": "tonic/dominant"
    },
    "minor": {
        "intervals": [0, 3, 7],  # Root, m3, P5
        "symbols": ["m", "min", "-"],
        "quality": "consonant",
        "function": "tonic/subdominant"
    },
    # ... (continues for all 36 chord types)
}
```

### Complete Chord Catalog

| Category | Chord Types | Count |
|----------|-------------|-------|
| **Triads** | Major, Minor, Diminished, Augmented, Sus2, Sus4 | 6 |
| **Seventh Chords** | Maj7, m7, Dom7, mMaj7, m7b5 (half-dim), dim7, augMaj7, aug7, 7b5 | 9 |
| **Extended Chords** | Maj9, m9, Dom9, Maj11, m11, Dom11, Maj13, m13, Dom13 | 9 |
| **Altered Chords** | 7b9, 7#9, 7b5, 7#5, 7#11, 7alt, 13b9, 13#11 | 8 |
| **Add Chords** | add9 (add2), add11 (add4), madd9, 6/9 | 4 |

### Chord Type Details

**Triads (6):**
```python
Major Triad:       [C, E, G]      # Root, major 3rd, perfect 5th
Minor Triad:       [C, Eb, G]     # Root, minor 3rd, perfect 5th
Diminished Triad:  [C, Eb, Gb]    # Root, minor 3rd, diminished 5th
Augmented Triad:   [C, E, G#]     # Root, major 3rd, augmented 5th
Suspended 2nd:     [C, D, G]      # Root, major 2nd, perfect 5th
Suspended 4th:     [C, F, G]      # Root, perfect 4th, perfect 5th
```

**Seventh Chords (9):**
```python
Major 7th (maj7):      [C, E, G, B]    # Major triad + M7
Minor 7th (m7):        [C, Eb, G, Bb]  # Minor triad + m7
Dominant 7th (7):      [C, E, G, Bb]   # Major triad + m7
Minor-Major 7th:       [C, Eb, G, B]   # Minor triad + M7
Half-Diminished 7th:   [C, Eb, Gb, Bb] # Dim triad + m7
Fully Diminished 7th:  [C, Eb, Gb, A]  # Dim triad + dim7
Augmented Major 7th:   [C, E, G#, B]   # Aug triad + M7
Augmented 7th:         [C, E, G#, Bb]  # Aug triad + m7
Dominant 7 flat 5:     [C, E, Gb, Bb]  # French augmented 6th
```

**Extended Chords (9):**
```python
Major 9th:    [C, E, G, B, D]      # Maj7 + M9
Minor 9th:    [C, Eb, G, Bb, D]    # m7 + M9
Dominant 9th: [C, E, G, Bb, D]     # Dom7 + M9
Major 11th:   [C, E, G, B, D, F]   # Maj9 + P11
Minor 11th:   [C, Eb, G, Bb, D, F] # m9 + P11
Dominant 11th:[C, E, G, Bb, D, F]  # Dom9 + P11
Major 13th:   [C, E, G, B, D, A]   # Maj9 + M13
Minor 13th:   [C, Eb, G, Bb, D, A] # m9 + M13
Dominant 13th:[C, E, G, Bb, D, A]  # Dom9 + M13
```

**Altered Chords (8):**
```python
Dominant 7 flat 9:     [C, E, G, Bb, Db]     # Tension chord
Dominant 7 sharp 9:    [C, E, G, Bb, D#]     # "Hendrix chord"
Dominant 7 flat 5:     [C, E, Gb, Bb]        # French aug 6th
Dominant 7 sharp 5:    [C, E, G#, Bb]        # Augmented dominant
Dominant 7 sharp 11:   [C, E, G, Bb, F#]     # Lydian dominant
Altered Dominant (7alt):[C, E, Gb/G#, Bb, Db/D#] # All alterations
Dominant 13 flat 9:    [C, E, G, Bb, Db, A]  # 13th + b9 tension
Dominant 13 sharp 11:  [C, E, G, Bb, F#, A]  # 13th + Lydian dominant
```

**Add Chords (4):**
```python
Add 9 (add2):     [C, E, G, D]     # Major triad + 9th
Add 11 (add4):    [C, E, G, F]     # Major triad + 11th
Minor Add 9:      [C, Eb, G, D]    # Minor triad + 9th
6/9:              [C, E, G, A, D]  # Major triad + 6th + 9th
```

---

## Rhythm Patterns by Genre

### Gospel Rhythm Patterns

```python
# File: backend/app/gospel/patterns/rhythm.py

class GospelRhythmPatterns:
    """Gospel-specific rhythm transformations."""

    PATTERNS = {
        "Gospel Shuffle": {
            "feel": "12/8 in 4/4",
            "intensity": 0.6,  # Default swing ratio
            "application": "Triplet-based swing feel"
        },
        "Gospel Swing": {
            "feel": "2:3 ratio",
            "intensity": 0.55,
            "application": "Moderate swing for worship"
        },
        "Backbeat Emphasis": {
            "beats": [2, 4],
            "velocity_multiplier": 1.3,
            "application": "Emphasize beats 2 and 4"
        },
        "Offbeat Syncopation": {
            "emphasis": "offbeats",
            "application": "Syncopated notes emphasized"
        },
        "Straight Feel": {
            "quantize": "strict",
            "application": "For learning/practice"
        }
    }
```

**Gospel Patterns:**
- **Gospel Shuffle:** 12/8 feel in 4/4 time (0.6 intensity default) - rolling triplet groove
- **Gospel Swing:** 2:3 ratio swing feel (0.55 intensity) - moderate worship swing
- **Backbeat Emphasis:** Emphasize beats 2 and 4 (velocity multiplier 1.3) - driving rhythm
- **Offbeat Syncopation:** Off-beat emphasis creating rhythmic tension
- **Straight Feel:** No rhythmic transformation - for learning/practice

### Jazz Rhythm Patterns

```python
# File: backend/app/jazz/patterns/rhythm.py

JAZZ_RHYTHM_PATTERNS = {
    "Swing Feel": {
        "ratio_range": (1.0, 3.0),
        "default_ratio": 2.0,  # Moderate swing
        "description": "Triplet-based swing (1.5 = light, 2.0 = moderate, 2.5 = heavy)"
    },
    "Syncopation": {
        "type": "off-beat_emphasis",
        "description": "Off-beat emphasis creating rhythmic tension"
    },
    "Walking Bass": {
        "pattern": "steady_quarter_notes",
        "description": "Steady quarter-note movement in bass line"
    }
}
```

**Jazz Patterns:**
- **Swing Feel:** Triplet-based swing (ratio 1.0-3.0, default 2.0 for moderate)
- **Syncopation:** Off-beat emphasis creating rhythmic tension
- **Walking Bass:** Steady quarter-note movement

### Blues Rhythm Patterns

```python
# File: backend/app/blues/patterns/rhythm.py

BLUES_RHYTHM_PATTERNS = {
    "Shuffle Feel": {
        "ratio_range": (2.0, 3.0),
        "default_ratio": 2.5,  # Heavy shuffle
        "description": "Heavy triplet-based swing characteristic of blues"
    },
    "12/8 Feel": {
        "meter": "compound",
        "description": "Compound meter with rolling triplets"
    },
    "Straight Blues": {
        "quantize": "eighth_notes",
        "description": "Even 8ths for slow blues"
    }
}
```

**Blues Patterns:**
- **Shuffle Feel:** Heavy triplet-based swing (ratio 2.0-3.0, default 2.5)
- **12/8 Feel:** Compound meter with rolling triplets
- **Straight Blues:** Even 8ths for slow blues

### Neo-Soul Rhythm Patterns

```python
# File: backend/app/neosoul/patterns/rhythm.py

NEOSOUL_RHYTHM_PATTERNS = {
    "16th-note Groove": {
        "grid": "16th_notes",
        "description": "Quantized to 16th-note grid with pocket"
    },
    "Laid-back Timing": {
        "delay": "0.03-0.08 beats",
        "description": "Behind-the-beat feel (D'Angelo/Questlove style)"
    },
    "Syncopation Emphasis": {
        "type": "off-beat",
        "description": "Off-beat emphasis creating groove"
    }
}
```

**Neo-Soul Patterns:**
- **16th-note Groove:** Quantized to 16th-note grid with pocket
- **Laid-back Timing:** Behind-the-beat feel (0.03-0.08 beat delay, D'Angelo/Questlove style)
- **Syncopation Emphasis:** Off-beat emphasis creating groove

### Classical Rhythm Patterns

**Classical Patterns:**
- **Straight Rhythms:** Precise classical timing (no swing/shuffle)
- **Period-appropriate feels:** Baroque (ornate), Classical (balanced), Romantic (expressive)

---

## Left Hand Patterns

### Gospel Left Hand Patterns

```python
# File: backend/app/gospel/arrangement/arranger.py

LEFT_HAND_PATTERNS = {
    "Shell Voicing": {
        "notes": ["root", "3rd", "7th"],
        "description": "Jazz shell voicing - root, 3rd, 7th",
        "use_case": "Smooth harmonic movement"
    },
    "Alberti Bass": {
        "pattern": "broken_chord",
        "description": "Broken chord pattern (classical/elegant)",
        "use_case": "Ballads, elegant arrangements"
    },
    "Stride Bass": {
        "pattern": "jump_bass_chord",
        "description": "Jump between bass note and chord",
        "use_case": "Uptempo, energetic feel"
    },
    "Walking Bass": {
        "pattern": "quarter_note_movement",
        "description": "Steady quarter-note bass movement",
        "use_case": "Jazz-influenced gospel"
    },
    "Syncopated Comping": {
        "pattern": "offbeat_chords",
        "description": "Off-beat chord hits",
        "use_case": "Contemporary gospel, rhythmic drive"
    }
}
```

**Gospel Left Hand:**
- Shell Voicing, Alberti Bass, Stride Bass, Walking Bass, Syncopated Comping

**Jazz Left Hand:**
- Walking Bass, Stride Bass, Shell Voicing, Syncopated Comping

**Blues Left Hand:**
- Boogie-Woogie Bass, 12-Bar Blues Bass, Shuffle Patterns

**Neo-Soul Left Hand:**
- Comping with extended voicings, Rhythmic syncopation, Syncopated bass lines

**Classical Left Hand:**
- Alberti Bass (standard classical), Broken Chord Accompaniment, Arpeggiated patterns

---

## Right Hand Patterns

### Gospel Right Hand Patterns

```python
RIGHT_HAND_PATTERNS = {
    "Block Chord": {
        "voicing": "vertical",
        "description": "Vertical chord voicing",
        "use_case": "Strong harmonic statements"
    },
    "Melody with Fills": {
        "pattern": "melodic_line_with_fills",
        "description": "Melodic line + improvised fills",
        "use_case": "Expressive melody treatment"
    },
    "Octave Doubling": {
        "pattern": "doubled_octaves",
        "description": "Doubled octave melodic lines",
        "use_case": "Power and presence"
    },
    "Chord Fills": {
        "pattern": "short_improvisations",
        "description": "Short improvisational fills between phrases",
        "use_case": "Contemporary gospel style"
    },
    "Polychord": {
        "voicing": "layered_complex",
        "description": "Complex layered voicings",
        "use_case": "Advanced harmonic color"
    },
    "Arpeggiated Voicing": {
        "pattern": "broken_chord_melody",
        "description": "Broken chord melodic lines",
        "use_case": "Flowing, lyrical passages"
    }
}
```

**Gospel Right Hand:**
- Block Chord, Melody with Fills, Octave Doubling, Chord Fills, Polychord, Arpeggiated Voicing

**Jazz Right Hand:**
- Block Chord, Chord Melody, Octave Doubling, Improvisation with licks, Rootless Voicings

**Blues Right Hand:**
- Block Chords, Chord Fills, 12-Bar Blues Melody, Call-Response patterns, Tremolo/Double Stops

**Neo-Soul Right Hand:**
- Extended Voicings (Maj7#11, m11, add9, sus), Chromatic Fills, Sustained Voicings

**Classical Right Hand:**
- Melodic Lines, Chord Voicing, Contrapuntal patterns, Arpeggiated patterns

---

## Genre-Specific Features & API

### Gospel Piano

**API Endpoint:** `POST /gospel/generate`

**Request Schema:**
```python
class GospelGenerateRequest(BaseModel):
    description: str  # Natural language (required)
    key: Optional[str] = None  # Extracted from description if not provided
    tempo: Optional[int] = None  # Inferred from style if not provided
    num_bars: int = 8  # Default 8 bars
    application: GospelApplication = GospelApplication.PRACTICE
    include_progression: bool = True
    ai_percentage: float = 0.0  # 0.0 = pure rules, 1.0 = pure AI

class GospelApplication(str, Enum):
    PRACTICE = "practice"     # 80-100 BPM, straight feel for learning
    CONCERT = "concert"       # 70-160 BPM (full range), dynamics 20-127
    WORSHIP = "worship"       # 60-80 BPM, dynamics 40-80
    UPTEMPO = "uptempo"       # 120-140 BPM, dynamics 80-120
```

**Unique Features:**
- **AI Blending:** Mix rule-based and MLX AI generation (0.0-1.0 ratio)
- **Improvisation Probability:** Context-dependent (10-75%) gospel fills, turnarounds, chromatic runs
- **Application Types:** PRACTICE, CONCERT, WORSHIP, UPTEMPO

**Example Request:**
```python
{
    "description": "Uplifting worship song in C major with soulful gospel feel",
    "num_bars": 16,
    "application": "WORSHIP",
    "ai_percentage": 0.3,  # 30% AI, 70% rules
    "include_progression": true
}
```

### Jazz Piano

**API Endpoint:** `POST /jazz/generate`

**Request Schema:**
```python
class JazzGenerateRequest(BaseModel):
    description: str
    key: Optional[str] = None
    tempo: Optional[int] = None
    num_bars: int = 16  # Default 16 bars
    application: JazzApplication = JazzApplication.STANDARD
    include_progression: bool = True

class JazzApplication(str, Enum):
    BALLAD = "ballad"      # 60-80 BPM, sustained rootless voicings
    STANDARD = "standard"  # 120-200 BPM, walking bass, moderate improvisation
    UPTEMPO = "uptempo"    # 200-300 BPM, continuous motion, heavy improvisation
```

**Unique Features:**
- **ii-V-I Progressions:** Built-in jazz patterns
- **Bebop Phrasing:** Genre-authentic improvisation
- **Walking Bass Variations:** Context-aware bass movement
- **Rootless Voicings:** Advanced harmonic voicings

**Example Request:**
```python
{
    "description": "Bebop standard in Bb with ii-V-I turnarounds",
    "tempo": 180,
    "application": "STANDARD",
    "num_bars": 32
}
```

### Blues Piano

**API Endpoint:** `POST /blues/generate`

**Request Schema:**
```python
class BluesGenerateRequest(BaseModel):
    description: str
    key: Optional[str] = None
    tempo: Optional[int] = None
    num_bars: int = 12  # Default 12-bar blues
    application: BluesApplication = BluesApplication.SHUFFLE
    include_progression: bool = True

class BluesApplication(str, Enum):
    SLOW = "slow"      # 60-80 BPM, expressive bends
    SHUFFLE = "shuffle"  # 100-120 BPM, classic shuffle feel
    FAST = "fast"      # 140-180 BPM, uptempo blues
```

**Unique Features:**
- **12-Bar Blues Structure:** Standard blues form
- **Call-Response Patterns:** Blues conversational style
- **Blues Bends & Expression:** Expressive techniques
- **Tremolo/Double Stops:** Advanced blues techniques

### Classical Piano

**API Endpoint:** `POST /classical/generate`

**Request Schema:**
```python
class ClassicalGenerateRequest(BaseModel):
    description: str
    key: Optional[str] = None
    tempo: Optional[int] = None
    time_signature: str = "4/4"
    num_bars: int = 16
    application: ClassicalApplication = ClassicalApplication.CLASSICAL
    include_progression: bool = True

class ClassicalApplication(str, Enum):
    BAROQUE = "baroque"      # 1600-1750: Counterpoint, fugal, ornate
    CLASSICAL = "classical"  # 1750-1820: Balanced, elegant, I-IV-V-I
    ROMANTIC = "romantic"    # 1820-1900: Expressive, chromatic harmony
```

**Unique Features:**
- **Period-Specific Styles:** Baroque, Classical, Romantic characteristics
- **Contrapuntal Patterns:** Baroque counterpoint
- **Time Signature Support:** Configurable (default 4/4)

### Neo-Soul Piano

**API Endpoint:** `POST /neosoul/generate`

**Request Schema:**
```python
class NeoSoulGenerateRequest(BaseModel):
    description: str
    key: Optional[str] = None
    tempo: Optional[int] = None
    num_bars: int = 8
    application: NeoSoulApplication = NeoSoulApplication.SMOOTH
    include_progression: bool = True

class NeoSoulApplication(str, Enum):
    SMOOTH = "smooth"    # 70-90 BPM, sustained extended voicings, laid-back
    UPTEMPO = "uptempo"  # 90-110 BPM, syncopated 16th-note grooves
```

**Unique Features:**
- **Extended Harmony:** 9ths, 11ths, 13ths, add9, sus2/4 chords
- **Laid-Back Timing:** Behind-the-beat feel (D'Angelo, Questlove influence)
- **Chromatic Fills:** Sophisticated harmonic movement

---

## Generation Pipeline & Response Format

### Standard Response Structure

```python
class GenerationResponse(BaseModel):
    """Standard response for all generators."""

    # Core output
    midi_base64: str           # Base64-encoded MIDI file
    download_url: str          # Download endpoint for MIDI

    # Chord progression analysis
    chord_progression: List[ChordInfo] = []

    # Metadata
    metadata: GenerationMetadata

    # Note preview (first 4 bars, max 100 notes)
    note_preview: List[NotePreview]

class ChordInfo(BaseModel):
    """Chord progression detail."""
    chord_symbol: str          # e.g., "Cmaj9"
    harmonic_function: str     # e.g., "I", "V7"
    notes: List[str]           # e.g., ["C", "E", "G", "B", "D"]
    comments: Optional[str]    # Context-specific comment

class GenerationMetadata(BaseModel):
    """Arrangement metadata."""
    tempo: int                 # BPM
    key: str                   # Key signature (e.g., "C", "Am")
    time_signature: str        # e.g., "4/4"
    num_bars: int              # Total bars generated
    note_count: int            # Total MIDI notes
    generation_method: str     # e.g., "gemini+rules", "gemini+mlx"
```

### Example Response

```json
{
    "midi_base64": "TVRoZAAAAAYAAQACBABNVHJrAAAA...",
    "download_url": "/gospel/download/abc123.mid",
    "chord_progression": [
        {
            "chord_symbol": "Cmaj9",
            "harmonic_function": "I",
            "notes": ["C", "E", "G", "B", "D"],
            "comments": "Extended tonic chord for gospel richness"
        },
        {
            "chord_symbol": "Fmaj7",
            "harmonic_function": "IV",
            "notes": ["F", "A", "C", "E"],
            "comments": "Subdominant with major 7th"
        }
    ],
    "metadata": {
        "tempo": 80,
        "key": "C",
        "time_signature": "4/4",
        "num_bars": 8,
        "note_count": 147,
        "generation_method": "gemini+rules"
    },
    "note_preview": [
        {
            "midi_note": 60,
            "start_time": 0.0,
            "duration": 1.0,
            "velocity": 80,
            "note_name": "C4"
        },
        // ... (up to 100 notes)
    ]
}
```

---

## Usage Examples

### Gospel Generation (Full Example)

```python
# File: backend/app/api/routes/gospel.py

@router.post("/generate", response_model=GospelGenerateResponse)
async def generate_gospel(
    request: GospelGenerateRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """Generate gospel piano arrangement from natural language."""

    # Step 1: Gemini generates chord progression
    progression = await gemini_service.generate_progression(
        description=request.description,
        key=request.key,
        genre="gospel",
        num_bars=request.num_bars
    )

    # Step 2: Gospel arranger creates MIDI
    arranger = GospelArranger(
        ai_percentage=request.ai_percentage,
        application=request.application
    )

    midi_file = arranger.arrange(
        progression=progression,
        tempo=request.tempo or 80,  # Default worship tempo
        num_bars=request.num_bars
    )

    # Step 3: Encode and return
    midi_base64 = encode_midi_base64(midi_file)

    return GospelGenerateResponse(
        midi_base64=midi_base64,
        download_url=f"/gospel/download/{midi_file.id}.mid",
        chord_progression=progression.chords,
        metadata=midi_file.metadata,
        note_preview=midi_file.notes[:100]  # First 100 notes
    )
```

### Jazz Generation (Bebop Example)

```python
@router.post("/generate", response_model=JazzGenerateResponse)
async def generate_jazz(request: JazzGenerateRequest):
    """Generate jazz piano arrangement with ii-V-I patterns."""

    # Gemini generates jazz progression
    progression = await gemini_service.generate_progression(
        description=request.description,
        key=request.key,
        genre="jazz",
        num_bars=request.num_bars,
        constraints={"include_ii_v_i": True}
    )

    # Jazz arranger with bebop patterns
    arranger = JazzArranger(application=request.application)
    midi_file = arranger.arrange(
        progression=progression,
        tempo=request.tempo or 180,  # Default bebop tempo
        walking_bass=True,
        rootless_voicings=True,
        improvisation_level=0.6  # 60% improvisation
    )

    return JazzGenerateResponse(...)
```

### Blues Generation (12-Bar Blues)

```python
@router.post("/generate", response_model=BluesGenerateResponse)
async def generate_blues(request: BluesGenerateRequest):
    """Generate 12-bar blues arrangement."""

    # Blues typically uses standard 12-bar structure
    # Gemini can suggest variations
    progression = await gemini_service.generate_progression(
        description=request.description,
        key=request.key or "E",  # Default blues key
        genre="blues",
        num_bars=request.num_bars or 12,
        constraints={"form": "12_bar_blues"}
    )

    # Blues arranger with shuffle feel
    arranger = BluesArranger(application=request.application)
    midi_file = arranger.arrange(
        progression=progression,
        tempo=request.tempo or 120,  # Default shuffle tempo
        shuffle_feel=True,
        call_response=True,
        blues_bends=True
    )

    return BluesGenerateResponse(...)
```

---

## Performance Characteristics

### Generation Speed

| Genre | Gemini API Call | Arrangement | MIDI Creation | Total |
|-------|----------------|-------------|---------------|-------|
| Gospel | 1-2s | 0.3-0.5s | 0.1s | **1.4-2.6s** |
| Jazz | 1-2s | 0.4-0.6s | 0.1s | **1.5-2.7s** |
| Blues | 1-2s | 0.3-0.4s | 0.1s | **1.4-2.5s** |
| Classical | 1-2s | 0.4-0.7s | 0.1s | **1.5-2.8s** |
| Neo-Soul | 1-2s | 0.3-0.5s | 0.1s | **1.4-2.6s** |

### Output Quality

- **MIDI Fidelity:** 100% (lossless note data)
- **Chord Progression Accuracy:** 95%+ (Gemini Pro)
- **Genre Authenticity:** High (rule-based patterns verified by musicians)
- **Musical Coherence:** Very High (context-aware pattern selection)

### Scalability

- **Concurrent Generations:** 50+ (FastAPI async)
- **Cache Strategy:** Gemini responses cached by (description, genre, key)
- **Storage:** ~5KB per MIDI file (efficient)

---

## Critical Files Reference

### Theory Libraries
- `backend/app/theory/scale_library.py` - 32 scale definitions
- `backend/app/theory/chord_library.py` - 36 chord type definitions

### Genre Generators
- `backend/app/services/gospel_generator.py` - Gospel generation service
- `backend/app/services/jazz_generator.py` - Jazz generation service
- `backend/app/services/blues_generator.py` - Blues generation service
- `backend/app/services/classical_generator.py` - Classical generation service
- `backend/app/services/neosoul_generator.py` - Neo-soul generation service

### Arrangement Engine
- `backend/app/gospel/arrangement/arranger.py` - Pattern arrangement logic
- `backend/app/gospel/patterns/rhythm.py` - Gospel rhythm patterns
- `backend/app/jazz/patterns/rhythm.py` - Jazz rhythm patterns
- `backend/app/blues/patterns/rhythm.py` - Blues rhythm patterns
- `backend/app/neosoul/patterns/rhythm.py` - Neo-soul rhythm patterns

### API Routes
- `backend/app/api/routes/gospel.py` - Gospel API endpoints
- `backend/app/api/routes/jazz.py` - Jazz API endpoints
- `backend/app/api/routes/blues.py` - Blues API endpoints
- `backend/app/api/routes/classical.py` - Classical API endpoints
- `backend/app/api/routes/neosoul.py` - Neo-soul API endpoints

### Request/Response Schemas
- `backend/app/schemas/gospel.py` - Gospel request/response models
- `backend/app/schemas/jazz.py` - Jazz request/response models
- `backend/app/schemas/blues.py` - Blues request/response models
- `backend/app/schemas/classical.py` - Classical request/response models
- `backend/app/schemas/neosoul.py` - Neo-soul request/response models

---

## Integration with Existing Systems

### Rust Audio Engine

```python
# Optional: Synthesize generated MIDI to audio
from rust_audio_engine import synthesize_midi

audio_path = synthesize_midi(
    midi_path="generated_gospel.mid",
    output_path="output.wav",
    soundfont_path="/data/soundfonts/piano.sf2",
    use_gpu=True,      # M4 GPU acceleration
    reverb=True        # Add reverb effect
)
```

### Multi-Model LLM Service

**Complexity Routing:**
- **Chord Progression Generation:** Complexity 8-10 (Gemini Pro fallback)
- **Arrangement Refinement:** Complexity 5-7 (Qwen2.5-7B if needed)
- **Practice Tips:** Complexity 1-4 (Phi-3.5 Mini)

### Frontend Integration

```typescript
// Frontend: TanStack Query for generation
const { mutate: generateGospel } = useMutation({
    mutationFn: async (request: GospelGenerateRequest) => {
        return api.post('/gospel/generate', request);
    },
    onSuccess: (data) => {
        // Play MIDI in browser
        playMidi(data.midi_base64);

        // Display chord progression
        displayChordProgression(data.chord_progression);
    }
});
```

---

## Feature Comparison Matrix

| Feature | Gospel | Jazz | Blues | Classical | Neo-Soul |
|---------|--------|------|-------|-----------|----------|
| **Natural Language Input** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Gemini Progression Gen** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AI Blending** | ✅ (0.0-1.0) | ❌ | ❌ | ❌ | ❌ |
| **Improvisation** | ✅ High | ✅ Very High | ✅ Medium | ❌ | ✅ Medium |
| **Application Types** | 4 (PRACTICE, CONCERT, WORSHIP, UPTEMPO) | 3 (BALLAD, STANDARD, UPTEMPO) | 3 (SLOW, SHUFFLE, FAST) | 3 (BAROQUE, CLASSICAL, ROMANTIC) | 2 (SMOOTH, UPTEMPO) |
| **Tempo Range** | 60-160 BPM | 60-300 BPM | 60-180 BPM | Context-dependent | 70-110 BPM |
| **Extended Chords** | ✅ High | ✅ Very High | ✅ Medium | ✅ Medium | ✅ Very High |
| **Rhythm Complexity** | High | Very High | Medium-High | Medium | High |
| **Left Hand Patterns** | 5 | 4 | 3 | 3 | 3 |
| **Right Hand Patterns** | 6 | 5 | 5 | 4 | 3 |

---

## Next Steps

1. **Rust Synthesis Integration:** Auto-generate WAV audio for all generations
2. **Sheet Music Export:** MusicXML/PDF export via Verovio or similar
3. **AI Fine-Tuning:** Train genre-specific models on Qwen2.5-7B for better arrangements
4. **Practice Mode Integration:** Generated MIDI → Performance analysis pipeline
5. **Curriculum Integration:** Auto-generate exercises based on student progress

---

**Feature Owner:** Backend Team
**Status:** ✅ Production Ready
**Last Updated:** December 15, 2025
**Estimated Complexity:** High (multi-genre system)
**User Impact:** Core platform feature - enables unlimited music generation
