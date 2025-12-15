"""
Pydantic schemas for AI-powered performance feedback
STORY-2.4: AI-Powered Performance Feedback Generation
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class SkillLevel(str, Enum):
    """Student skill level for personalized feedback"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class FeedbackCategory(str, Enum):
    """Categories of performance feedback"""
    PITCH = "pitch_accuracy"
    RHYTHM = "rhythm_timing"
    DYNAMICS = "dynamic_expression"
    TECHNIQUE = "playing_technique"
    MUSICALITY = "musical_interpretation"


class FeedbackItem(BaseModel):
    """Single feedback item with observation and suggestion"""
    category: FeedbackCategory
    observation: str = Field(
        description="Specific observation about performance"
    )
    suggestion: str = Field(
        description="Actionable improvement suggestion"
    )
    priority: int = Field(
        ge=1, le=3,
        description="1=high priority, 3=low priority"
    )


class PracticeExercise(BaseModel):
    """Recommended practice exercise"""
    title: str
    description: str
    duration_minutes: int
    difficulty: SkillLevel


class PerformanceFeedback(BaseModel):
    """Complete AI-generated performance feedback"""
    overall_score: float = Field(
        ge=0, le=100,
        description="Overall performance score (0-100)"
    )
    summary: str = Field(
        description="2-3 sentence overall summary"
    )
    strengths: List[str] = Field(
        max_length=3,
        description="Top 3 strengths in this performance"
    )
    areas_to_improve: List[FeedbackItem] = Field(
        max_length=5,
        description="Specific areas needing improvement"
    )
    practice_exercises: List[PracticeExercise] = Field(
        max_length=3,
        description="Recommended practice exercises"
    )
    encouragement: str = Field(
        description="Motivational closing message"
    )


class AnalysisSummary(BaseModel):
    """Internal model for summarizing analysis results before LLM generation"""
    pitch_accuracy: float  # 0-100
    rhythm_accuracy: float  # 0-100
    dynamics_range: float  # dB
    tempo_stability: float  # 0-100
    average_velocity: float  # 0-127
    common_pitch_errors: List[str]
    common_rhythm_errors: List[str]
    skill_level: SkillLevel
    piece_name: str
    piece_difficulty: str  # e.g., "Grade 3", "Beginner"


class RhythmScore(BaseModel):
    """Rhythm analysis results (placeholder for STORY-2.2 integration)"""
    accuracy_percent: float
    on_time_notes: int
    early_notes: int
    late_notes: int
    tempo_drift: float  # Percentage drift from expected tempo


class DynamicsScore(BaseModel):
    """Dynamics analysis results (from STORY-2.3)"""
    average_velocity: float
    dynamic_range_db: float
    softest_note_db: float
    loudest_note_db: float
    consistency_score: float  # 0-100
    expression_score: float  # 0-100
