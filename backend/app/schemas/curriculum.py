"""Pydantic schemas for Curriculum API

Defines request/response models for curriculum-related endpoints.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


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
