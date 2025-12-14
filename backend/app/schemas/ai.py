"""AI Generator Schemas for Gemini-powered music theory generation"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# === Enums ===

class ProgressionStyle(str, Enum):
    """Musical styles for progression generation"""
    JAZZ = "jazz"
    GOSPEL = "gospel"
    POP = "pop"
    CLASSICAL = "classical"
    NEO_SOUL = "neo_soul"
    RNB = "rnb"
    BLUES = "blues"


class Mood(str, Enum):
    """Emotional mood for generated content"""
    HAPPY = "happy"
    SAD = "sad"
    TENSE = "tense"
    PEACEFUL = "peaceful"
    ENERGETIC = "energetic"
    MYSTERIOUS = "mysterious"
    ROMANTIC = "romantic"


class VoicingStyle(str, Enum):
    """Voicing styles for chord voicings"""
    OPEN = "open"
    CLOSED = "closed"
    DROP2 = "drop2"
    DROP3 = "drop3"
    ROOTLESS = "rootless"
    SPREAD = "spread"
    GOSPEL = "gospel"


class ExerciseType(str, Enum):
    """Types of practice exercises"""
    SCALES = "scales"
    ARPEGGIOS = "arpeggios"
    PROGRESSIONS = "progressions"
    VOICE_LEADING = "voice_leading"
    RHYTHM = "rhythm"


class Difficulty(str, Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class GeneratorCategory(str, Enum):
    """Categories of AI generators"""
    PROGRESSIONS = "progressions"
    VOICINGS = "voicings"
    EXERCISES = "exercises"
    ANALYSIS = "analysis"


class LickStyle(str, Enum):
    """Jazz lick styles"""
    BEBOP = "bebop"
    BLUES = "blues"
    MODERN = "modern"
    GOSPEL = "gospel"
    SWING = "swing"
    BOSSA = "bossa"


class ContextType(str, Enum):
    """Lick generation context"""
    CHORD = "chord"
    PROGRESSION = "progression"


# === Request Models ===

class ProgressionRequest(BaseModel):
    """Request for chord progression generation"""
    key: str = Field("C", description="Musical key (e.g., C, F#, Bb)")
    mode: str = Field("major", description="Scale mode (major, minor, dorian, etc.)")
    style: ProgressionStyle = Field(ProgressionStyle.JAZZ, description="Musical style")
    mood: Optional[Mood] = Field(None, description="Emotional mood")
    length: int = Field(4, ge=2, le=16, description="Number of chords in progression")
    include_extensions: bool = Field(True, description="Include 7ths, 9ths, etc.")


class ReharmonizationRequest(BaseModel):
    """Request for reharmonization suggestions"""
    original_progression: list[str] = Field(..., description="Original chord symbols")
    key: str = Field("C", description="Musical key")
    style: ProgressionStyle = Field(ProgressionStyle.JAZZ, description="Target style")


class VoicingRequest(BaseModel):
    """Request for chord voicing generation"""
    chord: str = Field(..., description="Chord symbol (e.g., Cmaj7, Dm9, G7#11)")
    style: VoicingStyle = Field(VoicingStyle.OPEN, description="Voicing style")
    hand: str = Field("both", description="'left', 'right', or 'both'")
    include_fingering: bool = Field(True, description="Include fingering suggestions")


class VoiceLeadingRequest(BaseModel):
    """Request for voice leading optimization"""
    chord1: str = Field(..., description="Starting chord")
    chord2: str = Field(..., description="Target chord")
    style: Optional[ProgressionStyle] = Field(None, description="Style context")


class ExerciseRequest(BaseModel):
    """Request for practice exercise generation"""
    type: ExerciseType = Field(..., description="Type of exercise")
    key: str = Field("C", description="Musical key")
    difficulty: Difficulty = Field(Difficulty.INTERMEDIATE, description="Difficulty level")
    focus: Optional[str] = Field(None, description="Specific focus area")


class SubstitutionRequest(BaseModel):
    """Request for chord substitution suggestions"""
    chord: str = Field(..., description="Chord to substitute")
    context: Optional[list[str]] = Field(None, description="Surrounding chords for context")
    style: ProgressionStyle = Field(ProgressionStyle.JAZZ, description="Style context")


class LicksRequest(BaseModel):
    """Request for jazz licks generation"""
    style: LickStyle = Field(..., description="Jazz style (bebop, blues, etc.)")
    context_type: ContextType = Field(..., description="Single chord or progression")
    context: str = Field(..., description="Chord symbol or space-separated progression")
    difficulty: Difficulty = Field(Difficulty.INTERMEDIATE, description="Difficulty level")
    length_bars: int = Field(2, ge=1, le=4, description="Length in bars")
    starting_note: Optional[str] = Field(None, description="Suggested starting note")
    direction: Optional[str] = Field("mixed", description="Melodic direction")
    include_chromatics: bool = Field(True, description="Include chromatic approaches")


# === Response Models ===

class ChordInfo(BaseModel):
    """Information about a single chord"""
    symbol: str = Field(..., description="Chord symbol")
    notes: list[str] = Field(..., description="Note names in the chord")
    midi_notes: list[int] = Field(..., description="MIDI note numbers")
    function: Optional[str] = Field(None, description="Harmonic function (I, ii, V, etc.)")
    comment: Optional[str] = Field(None, description="Additional explanation")


class VoicingInfo(BaseModel):
    """Information about a chord voicing"""
    name: str = Field(..., description="Voicing name/description")
    notes: list[str] = Field(..., description="Note names from low to high")
    midi_notes: list[int] = Field(..., description="MIDI note numbers")
    fingering: Optional[list[int]] = Field(None, description="Fingering (1-5 for each note)")
    hand: str = Field("both", description="Which hand(s)")


class ExerciseStep(BaseModel):
    """A step in an exercise"""
    instruction: str = Field(..., description="What to practice")
    notes: Optional[list[str]] = Field(None, description="Notes involved")
    midi_notes: Optional[list[int]] = Field(None, description="MIDI notes")
    duration: Optional[str] = Field(None, description="How long to hold/play")


class ProgressionResponse(BaseModel):
    """Response with generated progression"""
    progression: list[ChordInfo] = Field(..., description="Generated chords")
    key: str = Field(..., description="Key of the progression")
    style: str = Field(..., description="Style applied")
    analysis: Optional[str] = Field(None, description="Brief analysis of the progression")
    tips: Optional[list[str]] = Field(None, description="Performance tips")


class ReharmonizationResponse(BaseModel):
    """Response with reharmonization options"""
    original: list[str] = Field(..., description="Original progression")
    reharmonized: list[ChordInfo] = Field(..., description="Reharmonized version")
    explanation: str = Field(..., description="Explanation of changes")
    techniques_used: list[str] = Field(..., description="Reharmonization techniques applied")


class VoicingResponse(BaseModel):
    """Response with voicing options"""
    chord: str = Field(..., description="Original chord symbol")
    voicings: list[VoicingInfo] = Field(..., description="Voicing options")
    tips: Optional[list[str]] = Field(None, description="Performance tips")


class VoiceLeadingResponse(BaseModel):
    """Response with voice leading paths"""
    chord1: VoicingInfo = Field(..., description="Starting voicing")
    chord2: VoicingInfo = Field(..., description="Target voicing")
    common_tones: list[str] = Field(..., description="Common tones held")
    movement: str = Field(..., description="Description of voice movement")
    tips: Optional[list[str]] = Field(None, description="Performance tips")


class ExerciseResponse(BaseModel):
    """Response with generated exercise"""
    title: str = Field(..., description="Exercise title")
    description: str = Field(..., description="What this exercise develops")
    steps: list[ExerciseStep] = Field(..., description="Exercise steps")
    variations: Optional[list[str]] = Field(None, description="Variation ideas")
    difficulty: str = Field(..., description="Difficulty level")


class SubstitutionResponse(BaseModel):
    """Response with substitution options"""
    original: str = Field(..., description="Original chord")
    substitutions: list[ChordInfo] = Field(..., description="Substitution options")
    explanations: dict[str, str] = Field(..., description="Explanation for each sub")


class TheoryAnalysis(BaseModel):
    """Music theory analysis of a lick"""
    chord_tones: list[bool] = Field(..., description="Which notes are chord tones (vs passing)")
    scale_degrees: list[str] = Field(..., description="Scale degree for each note (e.g., '1', 'b3', '5')")
    approach_tones: list[str] = Field(..., description="Chromatic/diatonic approach notes explained")
    voice_leading: str = Field(..., description="Explanation of melodic contour and direction")
    harmonic_function: str = Field(..., description="How the lick outlines the harmony")


class LickInfo(BaseModel):
    """Information about a single lick"""
    name: str = Field(..., description="Lick name/description")
    notes: list[str] = Field(..., description="Note names in sequence")
    midi_notes: list[int] = Field(..., description="MIDI note numbers")
    fingering: Optional[list[int]] = Field(None, description="Suggested fingering")
    start_note: str = Field(..., description="First note")
    end_note: str = Field(..., description="Last note")
    duration_beats: float = Field(..., description="Total duration in beats")
    style_tags: list[str] = Field(..., description="Style characteristics")
    theory_analysis: Optional[TheoryAnalysis] = Field(None, description="Music theory breakdown")


class LicksResponse(BaseModel):
    """Response with generated licks"""
    context: str = Field(..., description="Chord or progression context")
    style: str = Field(..., description="Style applied")
    difficulty: str = Field(..., description="Difficulty level")
    licks: list[LickInfo] = Field(..., description="Generated lick variations")
    analysis: str = Field(..., description="How licks fit the harmonic context")
    practice_tips: list[str] = Field(..., description="Performance suggestions")


# === Category Response ===

class GeneratorInfo(BaseModel):
    """Information about an available generator"""
    id: str = Field(..., description="Generator ID")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="What it does")
    category: GeneratorCategory = Field(..., description="Category")


class GeneratorsListResponse(BaseModel):
    """List of available generators"""
    generators: dict[str, list[GeneratorInfo]] = Field(
        ..., description="Generators grouped by category"
    )


# === Model Usage Stats ===

class ModelUsageStats(BaseModel):
    """Statistics for a specific model"""
    model: str = Field(..., description="Model name (flash, pro, ultra)")
    total_requests: int = Field(..., description="Total number of requests")
    successful_requests: int = Field(..., description="Number of successful requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    total_input_tokens: int = Field(..., description="Total input tokens used")
    total_output_tokens: int = Field(..., description="Total output tokens used")
    total_cost_usd: float = Field(..., description="Total cost in USD")
    avg_latency_ms: float = Field(..., description="Average latency in milliseconds")


class TaskTypeStats(BaseModel):
    """Statistics for a specific task type"""
    task_type: str = Field(..., description="Task type")
    total_requests: int = Field(..., description="Total number of requests")
    total_cost_usd: float = Field(..., description="Total cost in USD")


class UsageStatsResponse(BaseModel):
    """Overall usage statistics"""
    period_days: int = Field(..., description="Number of days in the period")
    total_requests: int = Field(..., description="Total requests across all models")
    total_cost_usd: float = Field(..., description="Total cost in USD")
    models: list[ModelUsageStats] = Field(..., description="Stats per model")
    task_types: list[TaskTypeStats] = Field(..., description="Stats per task type")
    date_range: dict[str, str] = Field(..., description="Start and end dates")
