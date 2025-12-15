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


class CreativityLevel(str, Enum):
    """Creativity levels for AI generation"""
    CONSERVATIVE = "conservative"  # Stay within established patterns
    BALANCED = "balanced"          # Mix familiar with fresh ideas
    ADVENTUROUS = "adventurous"    # Push boundaries while staying musical
    EXPERIMENTAL = "experimental"  # Think outside the box


class PhrasePosition(str, Enum):
    """Position within a musical phrase (for contextual lick generation)"""
    START = "start"        # Beginning of phrase - establish motif
    MIDDLE = "middle"      # Middle of phrase - develop ideas
    END = "end"            # End of phrase - resolve
    TURNAROUND = "turnaround"  # Transition back to beginning


class Emotion(str, Enum):
    """Emotional color for voicings and arrangements"""
    NEUTRAL = "neutral"
    WARM = "warm"
    BRIGHT = "bright"
    DARK = "dark"
    TENSE = "tense"
    ETHEREAL = "ethereal"
    POWERFUL = "powerful"
    INTIMATE = "intimate"


# === Educational & Creative Response Models ===

class EducationalContent(BaseModel):
    """Educational context for any generated musical content"""
    why_it_works: str = Field(..., description="Theory explanation of why this works")
    alternatives: list[str] = Field(default_factory=list, description="Other valid options that could work")
    common_mistakes: list[str] = Field(default_factory=list, description="What to avoid / common pitfalls")
    practice_suggestions: list[str] = Field(default_factory=list, description="How to practice this effectively")
    listen_to: list[str] = Field(default_factory=list, description="Reference tracks to study")
    theory_concepts: list[str] = Field(default_factory=list, description="Music theory concepts involved")


class CreativeVariation(BaseModel):
    """A single creative variation with metadata"""
    label: str = Field(..., description="Variation label (e.g., 'Safe Bet', 'Bold Move', 'Wow Factor')")
    creativity_score: float = Field(..., ge=0.0, le=1.0, description="How adventurous this option is")
    description: str = Field(..., description="Why someone might choose this variation")
    # The actual data is stored in the parent response


class VoiceLeadingAnalysis(BaseModel):
    """Analysis of voice leading between chords"""
    common_tones: list[str] = Field(default_factory=list, description="Notes held between chords")
    voice_movements: list[str] = Field(default_factory=list, description="Description of each voice's movement")
    smoothness_score: float = Field(..., ge=0.0, le=1.0, description="How smooth the voice leading is")
    parallel_motion_warnings: list[str] = Field(default_factory=list, description="Any parallel 5ths/8ves detected")


# === Request Models ===

class ProgressionRequest(BaseModel):
    """Request for chord progression generation"""
    key: str = Field("C", description="Musical key (e.g., C, F#, Bb)")
    mode: str = Field("major", description="Scale mode (major, minor, dorian, etc.)")
    style: ProgressionStyle = Field(ProgressionStyle.JAZZ, description="Musical style")
    mood: Optional[Mood] = Field(None, description="Emotional mood")
    length: int = Field(4, ge=2, le=16, description="Number of chords in progression")
    include_extensions: bool = Field(True, description="Include 7ths, 9ths, etc.")
    # Arrangement generation support
    arrange_as_midi: bool = Field(False, description="Generate full two-hand piano arrangement")
    application: Optional[str] = Field(None, description="Application type (ballad, uptempo, shuffle, etc.)")
    tempo: Optional[int] = Field(None, ge=40, le=300, description="Tempo in BPM (for MIDI arrangement)")
    ai_percentage: float = Field(0.0, ge=0.0, le=1.0, description="AI hybrid percentage (0.0 = pure rules, 1.0 = pure AI)")
    # Enhanced generation options
    creativity: CreativityLevel = Field(CreativityLevel.BALANCED, description="Creativity level for generation")
    style_reference: Optional[str] = Field(None, description="Artist/track reference (e.g., 'Kirk Franklin', 'Bill Evans')")
    generate_variations: bool = Field(False, description="Generate multiple creative variations")
    include_education: bool = Field(True, description="Include educational content with response")


class ReharmonizationRequest(BaseModel):
    """Request for reharmonization suggestions"""
    original_progression: list[str] = Field(..., description="Original chord symbols")
    key: str = Field("C", description="Musical key")
    style: ProgressionStyle = Field(ProgressionStyle.JAZZ, description="Target style")
    # Enhanced generation options
    creativity: CreativityLevel = Field(CreativityLevel.BALANCED, description="How bold the reharmonization should be")
    style_reference: Optional[str] = Field(None, description="Artist reference for style guidance")
    generate_variations: bool = Field(False, description="Generate multiple reharmonization options")
    include_education: bool = Field(True, description="Include educational explanations")


class VoicingRequest(BaseModel):
    """Request for chord voicing generation"""
    chord: str = Field(..., description="Chord symbol (e.g., Cmaj7, Dm9, G7#11)")
    style: VoicingStyle = Field(VoicingStyle.OPEN, description="Voicing style")
    hand: str = Field("both", description="'left', 'right', or 'both'")
    include_fingering: bool = Field(True, description="Include fingering suggestions")
    # Context for voice leading
    previous_chord: Optional[str] = Field(None, description="Previous chord for voice leading context")
    next_chord: Optional[str] = Field(None, description="Following chord for preparation")
    emotion: Emotion = Field(Emotion.NEUTRAL, description="Emotional color for voicing")
    # Enhanced generation options
    style_reference: Optional[str] = Field(None, description="Artist reference (e.g., 'Bill Evans')")
    include_education: bool = Field(True, description="Include voice leading analysis")


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
    # Phrase context (for contextual lick generation)
    preceding_chords: Optional[list[str]] = Field(None, description="Chords before current context")
    following_chord: Optional[str] = Field(None, description="Chord after the lick")
    phrase_position: PhrasePosition = Field(PhrasePosition.MIDDLE, description="Position in musical phrase")
    target_note: Optional[str] = Field(None, description="Target note to land on (e.g., 'G4')")
    # Enhanced generation options
    creativity: CreativityLevel = Field(CreativityLevel.BALANCED, description="Creativity level")
    style_reference: Optional[str] = Field(None, description="Artist reference (e.g., 'Charlie Parker')")
    generate_variations: bool = Field(False, description="Generate multiple lick variations")
    include_chromatics: bool = Field(True, description="Include chromatic approaches")


class ArrangeRequest(BaseModel):
    """Request for converting chord progression to full MIDI arrangement"""
    chords: list[str] = Field(..., description="Chord symbols to arrange")
    key: str = Field("C", description="Musical key")
    style: ProgressionStyle = Field(ProgressionStyle.JAZZ, description="Genre/style")
    tempo: int = Field(120, ge=40, le=300, description="Tempo in BPM")
    application: Optional[str] = Field(None, description="Application type (ballad, uptempo, etc.)")
    ai_percentage: float = Field(0.0, ge=0.0, le=1.0, description="AI hybrid percentage")
    time_signature: tuple = Field((4, 4), description="Time signature (numerator, denominator)")


class SplitVoicingRequest(BaseModel):
    """Request for split-hand chord voicing"""
    chord: str = Field(..., description="Chord symbol")
    style: ProgressionStyle = Field(ProgressionStyle.JAZZ, description="Genre/style")
    previous_left: Optional[list[int]] = Field(None, description="Previous left hand MIDI notes for voice leading")
    previous_right: Optional[list[int]] = Field(None, description="Previous right hand MIDI notes for voice leading")


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
    # Arrangement data (when arrange_as_midi=True)
    midi_file_path: Optional[str] = Field(None, description="Path to generated MIDI file")
    midi_base64: Optional[str] = Field(None, description="Base64-encoded MIDI data")
    arrangement_info: Optional[dict] = Field(None, description="Arrangement metadata (tempo, bars, notes, etc.)")
    # Enhanced response data
    education: Optional[EducationalContent] = Field(None, description="Educational context for learning")
    variations: Optional[list[CreativeVariation]] = Field(None, description="Alternative creative options")
    variations_data: Optional[list[list[ChordInfo]]] = Field(None, description="Chord data for each variation")


class ReharmonizationResponse(BaseModel):
    """Response with reharmonization options"""
    original: list[str] = Field(..., description="Original progression")
    reharmonized: list[ChordInfo] = Field(..., description="Reharmonized version")
    explanation: str = Field(..., description="Explanation of changes")
    techniques_used: list[str] = Field(..., description="Reharmonization techniques applied")
    source: Optional[str] = Field(None, description="Source: 'local_rules' or 'hybrid' (local + AI)")
    complexity: Optional[int] = Field(None, description="Task complexity (1-10)")
    # Enhanced response data
    education: Optional[EducationalContent] = Field(None, description="Educational content")
    variations: Optional[list[CreativeVariation]] = Field(None, description="Alternative reharmonization options")
    variations_data: Optional[list[list[ChordInfo]]] = Field(None, description="Chord data for each variation")


class VoicingResponse(BaseModel):
    """Response with voicing options"""
    chord: str = Field(..., description="Original chord symbol")
    voicings: list[VoicingInfo] = Field(..., description="Voicing options")
    tips: Optional[list[str]] = Field(None, description="Performance tips")
    # Enhanced response data
    voice_leading_analysis: Optional[VoiceLeadingAnalysis] = Field(None, description="Voice leading analysis from previous chord")
    education: Optional[EducationalContent] = Field(None, description="Educational content about voicing choices")


class VoiceLeadingResponse(BaseModel):
    """Response with voice leading paths"""
    chord1: VoicingInfo = Field(..., description="Starting voicing")
    chord2: VoicingInfo = Field(..., description="Target voicing")
    common_tones: list[str] = Field(..., description="Common tones held")
    movement: str = Field(..., description="Description of voice movement")
    tips: Optional[list[str]] = Field(None, description="Performance tips")
    # Enhanced response data
    analysis: Optional[VoiceLeadingAnalysis] = Field(None, description="Detailed voice leading analysis")
    education: Optional[EducationalContent] = Field(None, description="Educational explanation of voice leading")


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


class ArrangeResponse(BaseModel):
    """Response with full piano arrangement"""
    success: bool = Field(..., description="Whether arrangement was successful")
    midi_file_path: Optional[str] = Field(None, description="Path to MIDI file")
    midi_base64: Optional[str] = Field(None, description="Base64-encoded MIDI data")
    arrangement_info: dict = Field(default_factory=dict, description="Arrangement metadata")
    error: Optional[str] = Field(None, description="Error message if failed")


class SplitVoicingResponse(BaseModel):
    """Response with split left/right hand voicings"""
    chord: str = Field(..., description="Chord symbol")
    left_hand: VoicingInfo = Field(..., description="Left hand voicing")
    right_hand: VoicingInfo = Field(..., description="Right hand voicing")
    voice_leading_tips: Optional[list[str]] = Field(None, description="Voice leading suggestions")


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
