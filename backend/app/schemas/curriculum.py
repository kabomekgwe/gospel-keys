"""Pydantic schemas for Curriculum API

Defines request/response models for curriculum-related endpoints.
Enhanced with template-driven exercise library support.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# Enhanced Exercise Type Enums
# ============================================================================

class ExerciseTypeEnum(str, Enum):
    """Comprehensive exercise types from templates"""
    # Original types
    SCALE = "scale"
    PROGRESSION = "progression"
    VOICING = "voicing"
    RHYTHM = "rhythm"
    LICK = "lick"
    REPERTOIRE = "repertoire"
    ARPEGGIO = "arpeggio"
    DYNAMICS = "dynamics"

    # Enhanced types from templates
    AURAL = "aural"  # Ear training
    TRANSCRIPTION = "transcription"
    REHARMONIZATION = "reharmonization"
    SIGHT_READING = "sight_reading"
    IMPROVISATION = "improvisation"
    COMPING = "comping"
    WALKING_BASS = "walking_bass"
    MELODY_HARMONIZATION = "melody_harmonization"
    MODAL_EXPLORATION = "modal_exploration"
    POLYRHYTHM = "polyrhythm"
    PRODUCTION = "production"
    DRILL = "drill"


class DifficultyLevelEnum(str, Enum):
    """Exercise difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"


class SkillLevelEnum(str, Enum):
    """Overall skill level categories from templates"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"
    BEGINNER_TO_INTERMEDIATE = "beginner_to_intermediate"
    INTERMEDIATE_TO_ADVANCED = "intermediate_to_advanced"


# ============================================================================
# User Skill Profile Schemas
# ============================================================================

class SkillLevels(BaseModel):
    """Individual skill area ratings"""
    technical_ability: int = Field(ge=1, le=10, default=1)
    theory_knowledge: int = Field(ge=1, le=10, default=1)
    rhythm_competency: int = Field(ge=1, le=10, default=1)
    ear_training: int = Field(ge=1, le=10, default=1)
    improvisation: int = Field(ge=1, le=10, default=1)


class StyleFamiliarity(BaseModel):
    """Familiarity levels with different musical styles"""
    gospel: int = Field(ge=0, le=10, default=0)
    jazz: int = Field(ge=0, le=10, default=0)
    blues: int = Field(ge=0, le=10, default=0)
    classical: int = Field(ge=0, le=10, default=0)
    neo_soul: int = Field(ge=0, le=10, default=0)
    contemporary: int = Field(ge=0, le=10, default=0)


class AssessmentSubmission(BaseModel):
    """User assessment input for curriculum generation"""
    skill_levels: SkillLevels
    style_familiarity: StyleFamiliarity
    primary_goal: str = Field(..., description="Main learning goal: jazz_pianist, gospel_keys, etc.")
    interests: List[str] = Field(default_factory=list, description="List of genres/styles of interest")
    weekly_practice_hours: float = Field(ge=0.5, le=40, default=5.0)
    learning_velocity: str = Field(default="medium", pattern="^(slow|medium|fast)$")
    preferred_style: Optional[str] = Field(default=None, pattern="^(visual|audio|kinesthetic)$")


class UserSkillProfileResponse(BaseModel):
    """User's complete skill profile"""
    id: int
    user_id: int
    skill_levels: SkillLevels
    style_familiarity: StyleFamiliarity
    primary_goal: Optional[str]
    interests: List[str]
    weekly_practice_hours: float
    learning_velocity: str
    preferred_style: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Exercise Schemas
# ============================================================================

class ExerciseContent(BaseModel):
    """Generic exercise content - structure varies by exercise_type"""
    # For progression exercises
    chords: Optional[List[str]] = None
    key: Optional[str] = None
    roman_numerals: Optional[List[str]] = None
    
    # For scale exercises
    scale: Optional[str] = None
    octaves: Optional[int] = None
    
    # For voicing exercises
    chord: Optional[str] = None
    voicing_type: Optional[str] = None
    notes: Optional[List[str]] = None
    
    # For pattern/lick exercises
    pattern: Optional[str] = None
    midi_notes: Optional[List[int]] = None


class CurriculumExerciseResponse(BaseModel):
    """Single exercise within a lesson"""
    id: str
    lesson_id: str
    title: str
    description: Optional[str]
    order_index: int
    exercise_type: str  # scale, progression, voicing, pattern, lick, rhythm, ear_training
    content: ExerciseContent
    difficulty: str
    estimated_duration_minutes: int
    target_bpm: Optional[int]
    practice_count: int
    best_score: Optional[float]
    is_mastered: bool
    mastered_at: Optional[datetime]
    next_review_at: Optional[datetime]
    last_reviewed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseCompleteRequest(BaseModel):
    """Request to mark exercise as practiced with quality rating"""
    quality: int = Field(ge=0, le=5, description="Quality rating: 0=blackout, 5=perfect")
    score: Optional[float] = Field(ge=0, le=100, description="Optional accuracy score")
    duration_seconds: Optional[int] = Field(ge=0, description="Time spent practicing")


class AddLickToPracticeRequest(BaseModel):
    """Request to add a lick to practice queue"""
    lick_name: str = Field(..., description="Lick name/description")
    notes: List[str] = Field(..., description="Note names")
    midi_notes: List[int] = Field(..., description="MIDI note numbers")
    context: str = Field(..., description="Chord or progression context")
    style: str = Field(..., description="Jazz style")
    difficulty: str = Field(..., description="Difficulty level")
    duration_beats: float = Field(..., description="Duration in beats")


# ============================================================================
# Lesson Schemas
# ============================================================================

class CurriculumLessonResponse(BaseModel):
    """Weekly lesson within a module"""
    id: str
    module_id: str
    title: str
    description: Optional[str]
    week_number: int
    theory_content: dict
    concepts: List[str]
    estimated_duration_minutes: int
    is_completed: bool
    completed_at: Optional[datetime]
    exercises: List[CurriculumExerciseResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class LessonSummary(BaseModel):
    """Brief lesson info for listings"""
    id: str
    title: str
    week_number: int
    is_completed: bool
    exercise_count: int
    completed_exercises: int


# ============================================================================
# Module Schemas
# ============================================================================

class CurriculumModuleResponse(BaseModel):
    """Themed learning block (typically 4-8 weeks)"""
    id: str
    curriculum_id: str
    title: str
    description: Optional[str]
    theme: str
    order_index: int
    start_week: int
    end_week: int
    prerequisites: List[str]
    outcomes: List[str]
    completion_percentage: float
    lessons: List[LessonSummary]
    created_at: datetime

    class Config:
        from_attributes = True


class ModuleSummary(BaseModel):
    """Brief module info for listings"""
    id: str
    title: str
    theme: str
    start_week: int
    end_week: int
    completion_percentage: float
    lesson_count: int


# ============================================================================
# Curriculum Schemas
# ============================================================================

class CurriculumGenerateRequest(BaseModel):
    """Request to generate a new curriculum"""
    title: Optional[str] = Field(default=None, description="Optional custom title")
    duration_weeks: int = Field(ge=4, le=52, default=12)
    # Wizard data for personalization
    genre: Optional[str] = Field(default=None, description="Primary genre: gospel, jazz, blues, etc.")
    skill_level: Optional[str] = Field(default=None, pattern="^(beginner|intermediate|advanced)$")
    goals: Optional[List[str]] = Field(default=None, description="Learning goals selected from wizard")
    days_per_week: Optional[int] = Field(ge=1, le=7, default=None)
    session_length: Optional[str] = Field(default=None, description="Practice session length: 15min, 30min, 60min")


class CurriculumDefaultRequest(BaseModel):
    """Request to create a curriculum from a default template"""

class CurriculumFromTemplateRequest(BaseModel):
    """Request to create a curriculum from a dynamic template file"""
    template_id: str = Field(..., description="ID of the dynamic template (file path or internal ID)")



class CurriculumResponse(BaseModel):
    """Full curriculum with modules"""
    id: str
    user_id: int
    title: str
    description: Optional[str]
    duration_weeks: int
    current_week: int
    status: str  # active, paused, completed, archived
    ai_model_used: Optional[str]
    modules: List[ModuleSummary]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CurriculumSummary(BaseModel):
    """Brief curriculum info for listings"""
    id: str
    title: str
    description: Optional[str]
    status: str
    duration_weeks: int
    current_week: int
    module_count: int
    overall_progress: float


# ============================================================================
# Daily Practice Schemas
# ============================================================================

class DailyPracticeItem(BaseModel):
    """An exercise scheduled for today's practice"""
    exercise: CurriculumExerciseResponse
    lesson_title: str
    module_title: str
    priority: int  # 1 = highest priority (overdue), 2 = due today, 3 = new


class DailyPracticeQueue(BaseModel):
    """Today's practice queue"""
    date: datetime
    curriculum_id: str
    curriculum_title: str
    current_week: int
    items: List[DailyPracticeItem]
    total_estimated_minutes: int
    overdue_count: int
    new_count: int


# ============================================================================
# Assessment Schemas
# ============================================================================

class AssessmentResponse(BaseModel):
    """Assessment result"""
    id: str
    user_id: int
    curriculum_id: Optional[str]
    assessment_type: str
    scores: dict
    overall_score: Optional[float]
    ai_feedback: dict
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Template-Driven Exercise Library Schemas
# ============================================================================

class MIDIHints(BaseModel):
    """Hints for MIDI generation from templates"""
    tempo_bpm: int = 60
    swing: bool = False
    articulation: str = "legato"
    voicing_type: Optional[str] = None
    time_signature: str = "4/4"


class EnhancedExerciseContent(BaseModel):
    """Extended exercise content supporting all template formats"""
    # Common fields
    key: Optional[str] = None
    chords: Optional[List[str]] = None

    # Scale exercises
    scale: Optional[str] = None
    pattern: Optional[str] = None
    notes_per_step: Optional[int] = None
    include_inversions: Optional[bool] = None
    hands: Optional[str] = None
    octaves: Optional[int] = None

    # Progression exercises
    roman_numerals: Optional[List[str]] = None
    left_hand: Optional[Dict[str, Any]] = None
    right_hand: Optional[Dict[str, Any]] = None

    # Voicing exercises
    chord: Optional[str] = None
    voicing_type: Optional[str] = None
    notes: Optional[List[str]] = None
    inversions: Optional[List[str]] = None

    # Pattern/lick exercises
    pattern: Optional[str] = None
    midi_notes: Optional[List[int]] = None

    # Production exercises
    effects: Optional[str] = None
    style: Optional[str] = None

    # MIDI generation hints
    midi_hints: Optional[MIDIHints] = None

    # Catch-all for template-specific fields
    extra: Dict[str, Any] = Field(default_factory=dict)


class TheoryContent(BaseModel):
    """Theory explanation from templates"""
    summary: str
    key_points: List[str] = Field(default_factory=list)
    recommended_keys: Optional[List[str]] = None


class TemplateExercise(BaseModel):
    """Exercise as defined in curriculum templates"""
    id: Optional[str] = None
    title: str
    description: str
    exercise_type: ExerciseTypeEnum
    content: EnhancedExerciseContent
    midi_prompt: Optional[str] = None
    difficulty: DifficultyLevelEnum
    estimated_duration_minutes: int = 10
    tags: List[str] = Field(default_factory=list)

    # Generated content (populated after MIDI generation)
    midi_file_path: Optional[str] = None
    audio_file_path: Optional[str] = None
    generated_at: Optional[datetime] = None


class TemplateLesson(BaseModel):
    """Lesson structure from templates"""
    id: Optional[str] = None
    title: str
    description: str
    week_number: int
    concepts: List[str] = Field(default_factory=list)
    theory_content: Optional[TheoryContent] = None
    exercises: List[TemplateExercise] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)


class TemplateModule(BaseModel):
    """Module structure from templates"""
    id: Optional[str] = None
    title: str
    description: str
    theme: Optional[str] = None
    start_week: int
    end_week: int
    prerequisites: List[str] = Field(default_factory=list)
    outcomes: List[str] = Field(default_factory=list)
    lessons: List[TemplateLesson] = Field(default_factory=list)


class TemplateCurriculum(BaseModel):
    """Complete curriculum from template file"""
    id: Optional[str] = None
    title: str
    description: str
    style_tags: List[str] = Field(default_factory=list)
    level: SkillLevelEnum
    estimated_total_weeks: int
    modules: List[TemplateModule] = Field(default_factory=list)

    # Metadata
    source_file: Optional[str] = None
    created_at: Optional[datetime] = None
    ai_provider: Optional[str] = None  # claude, gemini, deepseek, grok, etc.


# ============================================================================
# Template Parsing and Indexing Schemas
# ============================================================================

class TemplateMetadata(BaseModel):
    """Metadata extracted from a template file"""
    file_path: str
    file_name: str
    file_format: str  # json, markdown, python
    ai_provider: str  # claude, gemini, deepseek, grok, perplexity, chatgpt
    curriculum_count: int
    total_modules: int
    total_lessons: int
    total_exercises: int
    genres_covered: List[str]
    skill_levels: List[SkillLevelEnum]
    has_midi_prompts: bool
    has_ear_training: bool
    has_theory_content: bool
    avg_weeks_per_curriculum: float


class TemplateIndex(BaseModel):
    """Index of all curriculum templates"""
    templates: List[TemplateMetadata]
    total_curriculums: int
    total_exercises: int
    genres_available: List[str]
    providers: List[str]
    indexed_at: datetime


class GetExerciseRequest(BaseModel):
    """Request for searching/filtering exercises"""
    exercise_type: Optional[ExerciseTypeEnum] = None
    difficulty: Optional[DifficultyLevelEnum] = None
    tags: List[str] = Field(default_factory=list)
    curriculum_id: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)


class GetExerciseResponse(BaseModel):
    """Response with exercise list and pagination"""
    exercises: List[Dict[str, Any]]
    total_count: int


class GenerateExercisesFromTemplateRequest(BaseModel):
    """Request to batch-generate exercises from template file"""
    template_file: str
    curriculum_id: Optional[str] = None  # Process specific curriculum only
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None
    force_regenerate: bool = False
    generate_audio: bool = False  # Also generate WAV files


class GenerateExercisesFromTemplateResponse(BaseModel):
    """Response from batch exercise generation"""
    success: bool
    template_file: str
    curriculums_processed: int
    exercises_generated: int
    midi_files_created: int
    audio_files_created: int
    errors: List[str] = Field(default_factory=list)
    exercise_ids: List[str] = Field(default_factory=list)
    generation_time_seconds: float
