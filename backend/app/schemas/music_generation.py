"""
Pydantic schemas for hybrid music generation system.

Combines musiclang_predict, Qwen 2.5-14B, and MidiTok for complete
local music generation pipeline.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class MusicGenre(str, Enum):
    """Supported music genres"""
    GOSPEL = "gospel"
    JAZZ = "jazz"
    BLUES = "blues"
    CLASSICAL = "classical"
    NEOSOUL = "neosoul"
    LATIN = "latin"
    RNB = "rnb"
    REGGAE = "reggae"


class MusicKey(str, Enum):
    """Music keys (major and minor)"""
    # Major keys
    C = "C"
    C_SHARP = "C#"
    D_FLAT = "Db"
    D = "D"
    E_FLAT = "Eb"
    E = "E"
    F = "F"
    F_SHARP = "F#"
    G_FLAT = "Gb"
    G = "G"
    A_FLAT = "Ab"
    A = "A"
    B_FLAT = "Bb"
    B = "B"

    # Minor keys
    C_MINOR = "Cm"
    C_SHARP_MINOR = "C#m"
    D_MINOR = "Dm"
    E_FLAT_MINOR = "Ebm"
    E_MINOR = "Em"
    F_MINOR = "Fm"
    F_SHARP_MINOR = "F#m"
    G_MINOR = "Gm"
    G_SHARP_MINOR = "G#m"
    A_MINOR = "Am"
    B_FLAT_MINOR = "Bbm"
    B_MINOR = "Bm"


class ChordVoicing(BaseModel):
    """Represents a single chord voicing"""
    chord_symbol: str = Field(..., description="Chord symbol (e.g., 'Cmaj7', 'Dm7')")
    root: int = Field(..., description="Root note MIDI number", ge=0, le=127)
    notes: List[int] = Field(..., description="MIDI note numbers for voicing", min_items=1)
    inversion: int = Field(0, description="Inversion number (0=root position)", ge=0)
    bass_note: int = Field(..., description="Bass note MIDI number", ge=0, le=127)

    @validator('notes')
    def validate_notes(cls, v):
        if not all(0 <= note <= 127 for note in v):
            raise ValueError("All MIDI notes must be 0-127")
        return v


class ChordProgression(BaseModel):
    """Chord progression with voicings and metadata"""
    chords: List[str] = Field(..., description="Chord symbols", min_items=1)
    roman_numerals: List[str] = Field(..., description="Roman numeral analysis")
    voicings: List[ChordVoicing] = Field(..., description="Specific voicings for each chord")
    key: MusicKey = Field(..., description="Key of progression")
    genre: MusicGenre = Field(..., description="Musical genre/style")
    num_bars: int = Field(..., description="Number of bars", ge=1)
    time_signature: str = Field("4/4", description="Time signature")


class MelodyNote(BaseModel):
    """Single melody note with timing"""
    pitch: int = Field(..., description="MIDI note number", ge=0, le=127)
    start_time: float = Field(..., description="Start time in beats", ge=0)
    duration: float = Field(..., description="Duration in beats", gt=0)
    velocity: int = Field(80, description="MIDI velocity", ge=0, le=127)


class MelodySequence(BaseModel):
    """Melody sequence with metadata"""
    notes: List[MelodyNote] = Field(..., description="Melody notes")
    key: MusicKey = Field(..., description="Key of melody")
    scale: str = Field(..., description="Scale used (e.g., 'major', 'blues', 'dorian')")
    range_low: int = Field(..., description="Lowest MIDI note in melody")
    range_high: int = Field(..., description="Highest MIDI note in melody")
    approach: str = Field(
        "chord_tones",
        description="Melodic approach (chord_tones, extensions, passing_tones, etc.)"
    )


class VoiceLeadingRules(BaseModel):
    """Voice leading guidelines from music theory"""
    max_leap: int = Field(7, description="Maximum interval leap in semitones")
    prefer_stepwise: bool = Field(True, description="Prefer stepwise motion")
    avoid_parallel_fifths: bool = Field(True, description="Avoid parallel perfect fifths")
    common_tone_retention: bool = Field(True, description="Keep common tones between chords")
    smooth_transitions: bool = Field(True, description="Minimize voice movement")


class VariationType(str, Enum):
    """Types of algorithmic variations for unique bar generation"""
    TRANSPOSE = "transpose"
    RHYTHM = "rhythm"
    DENSITY = "density"
    OCTAVE = "octave"
    CHORDS = "chords"
    INVERSION = "inversion"
    LICK = "lick"
    VOICING = "voicing"
    HARMONY = "harmony"
    SUBSTITUTION = "substitution"
    ARRANGEMENT = "arrangement"


class MusicGenerationRequest(BaseModel):
    """Request for hybrid music generation"""
    genre: MusicGenre = Field(..., description="Musical genre")
    key: MusicKey = Field(..., description="Key signature")
    tempo: int = Field(120, description="Tempo in BPM", ge=40, le=240)
    num_bars: int = Field(8, description="Number of bars to generate", ge=2, le=64)
    time_signature: str = Field("4/4", description="Time signature")

    # Style options
    style: str = Field("traditional", description="Style variation within genre")
    complexity: int = Field(5, description="Complexity level 1-10", ge=1, le=10)
    variations: Optional[List[VariationType]] = Field(
        default=None, 
        description="List of variations to apply to repeated bars"
    )

    # Generation options
    include_melody: bool = Field(True, description="Generate melody")
    include_bass: bool = Field(True, description="Generate bass line")
    include_chords: bool = Field(True, description="Include chord voicings")

    # Advanced options
    chord_progression: Optional[List[str]] = Field(
        None,
        description="Custom chord progression (overrides auto-generation)"
    )
    voice_leading_rules: Optional[VoiceLeadingRules] = Field(
        None,
        description="Custom voice leading rules"
    )

    # Output options
    synthesize_audio: bool = Field(True, description="Generate audio file")
    use_gpu_synthesis: bool = Field(True, description="Use GPU-accelerated synthesis")
    add_reverb: bool = Field(True, description="Add reverb effect")

    # Template override
    template_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Full template data (musicSheetTemplate) to override generation"
    )


class MusicGenerationResponse(BaseModel):
    """Response from hybrid music generation"""
    # Generated structures
    chord_progression: ChordProgression
    melody: Optional[MelodySequence] = None

    # File outputs
    midi_file: str = Field(..., description="Path to generated MIDI file")
    audio_file: Optional[str] = Field(None, description="Path to synthesized audio (WAV)")

    # Tokens (for ML training)
    midi_tokens: List[int] = Field(..., description="MidiTok REMI tokens")

    # Metadata
    generation_time_ms: int = Field(..., description="Total generation time")
    model_info: Dict[str, str] = Field(
        ...,
        description="Models used (chord_model, theory_model, etc.)"
    )

    # Theory analysis (from Qwen 2.5-14B)
    theory_analysis: Optional[str] = Field(
        None,
        description="Music theory explanation of the generated piece"
    )


class TrainingDataSample(BaseModel):
    """Single training sample for fine-tuning"""
    prompt: str = Field(..., description="Text prompt describing the music")
    tokens: List[int] = Field(..., description="MidiTok tokens representing the music")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

    # Original file info
    source_file: str = Field(..., description="Original MIDI file path")
    genre: MusicGenre
    key: Optional[MusicKey] = None
    tempo: Optional[int] = None
    num_bars: Optional[int] = None


class TrainingDataset(BaseModel):
    """Complete training dataset"""
    samples: List[TrainingDataSample] = Field(..., description="Training samples")
    vocab_size: int = Field(..., description="Token vocabulary size")
    total_tokens: int = Field(..., description="Total number of tokens in dataset")

    # Split info
    train_samples: int = Field(..., description="Number of training samples")
    val_samples: int = Field(..., description="Number of validation samples")

    # Metadata
    tokenizer_config: Dict[str, Any] = Field(..., description="MidiTok configuration")
    created_at: str = Field(..., description="Dataset creation timestamp")


class ChordPredictionRequest(BaseModel):
    """Request for chord progression prediction (musiclang)"""
    seed_chords: List[str] = Field(..., description="Initial chord sequence", min_items=1)
    num_chords: int = Field(4, description="Number of chords to predict", ge=1, le=32)
    genre: MusicGenre = Field(..., description="Musical genre for style")
    key: Optional[MusicKey] = Field(None, description="Key signature (auto-detect if None)")


class ChordPredictionResponse(BaseModel):
    """Response from chord prediction"""
    predicted_chords: List[str] = Field(..., description="Predicted chord symbols")
    full_progression: List[str] = Field(..., description="Seed + predicted chords")
    score_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw MusicLang score data"
    )


class TheoryExplanationRequest(BaseModel):
    """Request for music theory explanation (Qwen 2.5-14B)"""
    concept: str = Field(..., description="Music theory concept to explain")
    context: str = Field("general", description="Context (genre, level, etc.)")
    include_examples: bool = Field(True, description="Include musical examples")


class TheoryExplanationResponse(BaseModel):
    """Response from theory explanation"""
    explanation: str = Field(..., description="Theory explanation from LLM")
    examples: Optional[List[str]] = Field(None, description="Musical examples")
    related_concepts: Optional[List[str]] = Field(None, description="Related topics")
