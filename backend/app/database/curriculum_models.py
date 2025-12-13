"""Curriculum-related SQLAlchemy database models for Gospel Keys

Defines curriculum, modules, lessons, exercises, and user skill profiles
using SQLAlchemy 2.0 declarative style with async support.
"""

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models import Base

if TYPE_CHECKING:
    from app.database.models import User


def generate_uuid() -> str:
    """Generate a new UUID string for primary keys."""
    return str(uuid.uuid4())


class UserSkillProfile(Base):
    """User's skill levels across different musical areas"""
    __tablename__ = "user_skill_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    # Skill levels (1-10 scale)
    technical_ability: Mapped[int] = mapped_column(Integer, default=1)
    theory_knowledge: Mapped[int] = mapped_column(Integer, default=1)
    rhythm_competency: Mapped[int] = mapped_column(Integer, default=1)
    ear_training: Mapped[int] = mapped_column(Integer, default=1)
    improvisation: Mapped[int] = mapped_column(Integer, default=1)
    
    # Style familiarity (JSON: {"gospel": 7, "jazz": 5, ...})
    style_familiarity_json: Mapped[str] = mapped_column(Text, default="{}")
    
    # Learning preferences
    learning_velocity: Mapped[str] = mapped_column(String(20), default="medium")  # slow/medium/fast
    preferred_style: Mapped[Optional[str]] = mapped_column(String(50))  # visual/audio/kinesthetic
    weekly_practice_hours: Mapped[float] = mapped_column(Float, default=5.0)
    
    # Goals
    primary_goal: Mapped[Optional[str]] = mapped_column(String(100))  # jazz_pianist, gospel_keys, etc.
    interests_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON list of genres/styles
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="skill_profile")


class Curriculum(Base):
    """Master learning plan for a user"""
    __tablename__ = "curricula"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=12)
    current_week: Mapped[int] = mapped_column(Integer, default=1)
    
    # Status: active, paused, completed, archived
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    # AI generation metadata
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(50))
    generation_prompt_hash: Mapped[Optional[str]] = mapped_column(String(64))

    # Adaptive curriculum (Phase 2)
    adaptation_history_json: Mapped[str] = mapped_column(Text, default='[]')  # Log of adaptations
    last_adapted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="curricula")
    modules: Mapped[List["CurriculumModule"]] = relationship(
        back_populates="curriculum", 
        cascade="all, delete-orphan",
        order_by="CurriculumModule.order_index"
    )


class CurriculumModule(Base):
    """Themed learning block (typically 4-8 weeks)"""
    __tablename__ = "curriculum_modules"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    curriculum_id: Mapped[str] = mapped_column(ForeignKey("curricula.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    theme: Mapped[str] = mapped_column(String(100))  # e.g., "gospel_fundamentals", "jazz_voicings"
    
    # Ordering and timing
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    start_week: Mapped[int] = mapped_column(Integer)
    end_week: Mapped[int] = mapped_column(Integer)
    
    # Prerequisites (JSON: list of module_ids)
    prerequisites_json: Mapped[str] = mapped_column(Text, default="[]")
    
    # Learning outcomes (JSON list of strings)
    outcomes_json: Mapped[str] = mapped_column(Text, default="[]")
    
    # Completion tracking
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    curriculum: Mapped["Curriculum"] = relationship(back_populates="modules")
    lessons: Mapped[List["CurriculumLesson"]] = relationship(
        back_populates="module", 
        cascade="all, delete-orphan",
        order_by="CurriculumLesson.week_number"
    )


class CurriculumLesson(Base):
    """Weekly learning unit within a module"""
    __tablename__ = "curriculum_lessons"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    module_id: Mapped[str] = mapped_column(ForeignKey("curriculum_modules.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    week_number: Mapped[int] = mapped_column(Integer)
    
    # Content structure (JSON)
    theory_content_json: Mapped[str] = mapped_column(Text, default="{}")
    concepts_json: Mapped[str] = mapped_column(Text, default="[]")

    # Tutorial content (Phase 2)
    tutorial_content_json: Mapped[str] = mapped_column(Text, default='{}')
    tutorial_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Time estimates
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Completion tracking
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    module: Mapped["CurriculumModule"] = relationship(back_populates="lessons")
    exercises: Mapped[List["CurriculumExercise"]] = relationship(
        back_populates="lesson", 
        cascade="all, delete-orphan",
        order_by="CurriculumExercise.order_index"
    )


class CurriculumExercise(Base):
    """Daily practice item within a lesson"""
    __tablename__ = "curriculum_exercises"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("curriculum_lessons.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Exercise type: scale, progression, voicing, pattern, lick, rhythm, ear_training
    exercise_type: Mapped[str] = mapped_column(String(50))
    
    # Content (JSON - structure varies by exercise_type)
    # Examples:
    # progression: {"chords": ["Dm7", "G7", "Cmaj7"], "key": "C", "roman": ["ii7", "V7", "Imaj7"]}
    # scale: {"scale": "major", "key": "C", "octaves": 2}
    # voicing: {"chord": "Cmaj7", "voicing_type": "drop2", "notes": ["E", "G", "B", "C"]}
    content_json: Mapped[str] = mapped_column(Text, default="{}")
    
    # Difficulty: beginner, intermediate, advanced, expert
    difficulty: Mapped[str] = mapped_column(String(20), default="beginner")
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=10)
    target_bpm: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Practice tracking
    practice_count: Mapped[int] = mapped_column(Integer, default=0)
    best_score: Mapped[Optional[float]] = mapped_column(Float)
    is_mastered: Mapped[bool] = mapped_column(Boolean, default=False)
    mastered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # SRS fields (same as Snippet model for consistency)
    next_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    interval_days: Mapped[float] = mapped_column(Float, default=1.0)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    repetition_count: Mapped[int] = mapped_column(Integer, default=0)

    # Audio generation fields (Phase 1)
    midi_file_path: Mapped[Optional[str]] = mapped_column(String)
    audio_files_json: Mapped[str] = mapped_column(Text, default='{}')  # {"fluidsynth": "path", "stable_audio": "path"}
    audio_generation_status: Mapped[str] = mapped_column(String(20), default='pending')  # pending, generating, complete, failed
    audio_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    lesson: Mapped["CurriculumLesson"] = relationship(back_populates="exercises")


class Assessment(Base):
    """Milestone check or diagnostic test result"""
    __tablename__ = "assessments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    curriculum_id: Mapped[Optional[str]] = mapped_column(ForeignKey("curricula.id", ondelete="SET NULL"))
    
    # Assessment type: diagnostic, milestone, weekly, skill_check
    assessment_type: Mapped[str] = mapped_column(String(50))
    
    # Scores (JSON: {"technical": 7, "theory": 5, "rhythm": 6, ...})
    scores_json: Mapped[str] = mapped_column(Text, default="{}")
    overall_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # AI analysis and recommendations
    ai_feedback_json: Mapped[str] = mapped_column(Text, default="{}")
    recommendations_json: Mapped[str] = mapped_column(Text, default="[]")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship()
    curriculum: Mapped[Optional["Curriculum"]] = relationship()
