"""SQLAlchemy database models for Gospel Keys

Defines all database tables using SQLAlchemy 2.0 declarative style with async support.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models"""
    pass


class User(Base):
    """User account entity"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    songs: Mapped[List["Song"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    collections: Mapped[List["Collection"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    practice_sessions: Mapped[List["PracticeSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    # Curriculum relationships
    skill_profile: Mapped["UserSkillProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    curricula: Mapped[List["Curriculum"]] = relationship(back_populates="user", cascade="all, delete-orphan")



class Song(Base):
    """Main song/transcription entity"""
    __tablename__ = "songs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[Optional[str]] = mapped_column(String)
    source_url: Mapped[Optional[str]] = mapped_column(String)
    source_file: Mapped[Optional[str]] = mapped_column(String)
    duration: Mapped[Optional[float]] = mapped_column(Float)
    tempo: Mapped[Optional[float]] = mapped_column(Float)
    key_signature: Mapped[Optional[str]] = mapped_column(String)
    time_signature: Mapped[Optional[str]] = mapped_column(String)
    difficulty: Mapped[Optional[str]] = mapped_column(String)
    midi_file_path: Mapped[Optional[str]] = mapped_column(String)
    audio_file_path: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Analysis Relationships
    song_tags: Mapped[List["SongTag"]] = relationship(back_populates="song", cascade="all, delete-orphan", lazy="selectin")
    notes: Mapped[List["SongNote"]] = relationship(back_populates="song", cascade="all, delete-orphan", lazy="selectin")
    chords: Mapped[List["SongChord"]] = relationship(back_populates="song", cascade="all, delete-orphan", lazy="selectin")
    practice_sessions: Mapped[List["PracticeSession"]] = relationship(back_populates="song", cascade="all, delete-orphan", lazy="selectin")
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="song", cascade="all, delete-orphan", lazy="selectin")
    snippets: Mapped[List["Snippet"]] = relationship(back_populates="song", cascade="all, delete-orphan", lazy="selectin")
    
    # New Phase 4 Analysis Relationships
    genre_analysis: Mapped["GenreAnalysis"] = relationship(back_populates="song", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    patterns: Mapped[List["DetectedPattern"]] = relationship(back_populates="song", cascade="all, delete-orphan", lazy="selectin")
    melody: Mapped["MelodyLine"] = relationship(
        back_populates="song",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # User Relationship
    user: Mapped[Optional["User"]] = relationship(back_populates="songs")


class Collection(Base):
    """User-created collection of songs (playlist/setlist)"""
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="collections")
    items: Mapped[List["CollectionSong"]] = relationship(
        back_populates="collection", 
        cascade="all, delete-orphan",
        order_by="CollectionSong.order_index"
    )

class CollectionSong(Base):
    """Link table for songs in a collection with ordering"""
    __tablename__ = "collection_songs"

    collection_id: Mapped[str] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(String)  # User notes for this song in this collection
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    collection: Mapped["Collection"] = relationship(back_populates="items")
    song: Mapped["Song"] = relationship()



class SongNote(Base):
    """Individual MIDI note within a song"""
    __tablename__ = "song_notes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    pitch: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    velocity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="notes")


class SongChord(Base):
    """Detected chord within a song"""
    __tablename__ = "song_chords"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    chord: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    root: Mapped[str] = mapped_column(String, nullable=False)
    quality: Mapped[str] = mapped_column(String, nullable=False)
    bass_note: Mapped[Optional[str]] = mapped_column(String)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="chords")
    voicing_analysis: Mapped["ChordVoicing"] = relationship(back_populates="song_chord", uselist=False, cascade="all, delete-orphan")


class Tag(Base):
    """Tag for organizing songs"""
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    # Relationship
    songs: Mapped[List["SongTag"]] = relationship(back_populates="tag", cascade="all, delete-orphan")


class SongTag(Base):
    """Many-to-many relationship between songs and tags"""
    __tablename__ = "song_tags"
    
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    song: Mapped["Song"] = relationship(back_populates="song_tags")
    tag: Mapped["Tag"] = relationship(back_populates="songs")


class GenreAnalysis(Base):
    """
    Stores genre classification results
    """
    __tablename__ = "genre_analysis"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    song_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), index=True)
    
    primary_genre: Mapped[str] = mapped_column(String)  # jazz, gospel, blues, classical, contemporary
    confidence: Mapped[float] = mapped_column(Float)
    sub_genres: Mapped[Optional[str]] = mapped_column(String)  # JSON list stored as string
    harmonic_complexity: Mapped[Optional[float]] = mapped_column(Float)
    tempo: Mapped[Optional[float]] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    song: Mapped["Song"] = relationship(back_populates="genre_analysis")


class DetectedPattern(Base):
    """
    Stores recognized musical patterns (ii-V-I, turnarounds, etc.)
    """
    __tablename__ = "detected_patterns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    song_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), index=True)
    
    pattern_type: Mapped[str] = mapped_column(String)  # ii-V-I, turnaround, tritone_sub, blue_note_run
    start_time: Mapped[float] = mapped_column(Float)
    duration: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    key_context: Mapped[Optional[str]] = mapped_column(String)
    metadata_json: Mapped[Optional[str]] = mapped_column(String)  # JSON string for extra details
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    song: Mapped["Song"] = relationship(back_populates="patterns")


class MelodyLine(Base):
    """
    Stores extracted melody notes
    """
    __tablename__ = "melody_lines"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    song_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), index=True)
    
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    notes_json: Mapped[str] = mapped_column(String)  # JSON list of dicts: {time, pitch, confidence}
    contour_type: Mapped[Optional[str]] = mapped_column(String)  # ascending, descending, arch
    average_confidence: Mapped[float] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    song: Mapped["Song"] = relationship(back_populates="melody")


class ChordVoicing(Base):
    """
    Stores detailed analysis of specific chord voicings
    """
    __tablename__ = "chord_voicings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    song_chord_id: Mapped[int] = mapped_column(ForeignKey("song_chords.id", ondelete="CASCADE"), index=True)
    
    voicing_type: Mapped[str] = mapped_column(String)  # rootless, quartal, upper_structure, spread
    notes_json: Mapped[str] = mapped_column(String)  # JSON list of notes
    inversion: Mapped[int] = mapped_column(Integer, default=0)
    width_semitones: Mapped[int] = mapped_column(Integer) # Total span in semitones
    complexity_score: Mapped[float] = mapped_column(Float)
    
    # Relationships
    song_chord: Mapped["SongChord"] = relationship(back_populates="voicing_analysis")


class Annotation(Base):
    """User annotation on a song at a specific timestamp"""
    __tablename__ = "annotations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    time: Mapped[float] = mapped_column(Float, nullable=False)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # practice_note, theory_insight, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="annotations")


class Snippet(Base):
    """Extracted practice snippet from a song"""
    __tablename__ = "snippets"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    practice_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # SRS / Adaptive Practice Fields
    next_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    interval_days: Mapped[float] = mapped_column(Float, default=1.0)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    repetition_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="snippets")
    practice_sessions: Mapped[List["PracticeSession"]] = relationship(
        back_populates="snippet",
        cascade="all, delete-orphan"
    )


class PracticeSession(Base):
    """Record of a practice session"""
    __tablename__ = "practice_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[Optional[str]] = mapped_column(ForeignKey("songs.id", ondelete="SET NULL"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    snippet_id: Mapped[Optional[str]] = mapped_column(ForeignKey("snippets.id", ondelete="SET NULL"))
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    tempo_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationships
    song: Mapped[Optional["Song"]] = relationship(back_populates="practice_sessions")
    user: Mapped[Optional["User"]] = relationship(back_populates="practice_sessions")
    snippet: Mapped[Optional["Snippet"]] = relationship(back_populates="practice_sessions")


class ModelUsageLog(Base):
    """Log of AI model API usage for cost tracking and analytics"""
    __tablename__ = "model_usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    model: Mapped[str] = mapped_column(String, nullable=False, index=True)  # flash, pro, ultra
    task_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # curriculum_planning, etc.
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)  # Up to $9999.999999
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


# =============================================================================
# Phase 3: Real-Time Performance Analysis Tables
# =============================================================================

class RealtimeSession(Base):
    """
    Real-time practice session with WebSocket analysis.
    Tracks a complete practice session from start to finish.
    """
    __tablename__ = "realtime_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    # Session metadata
    piece_name: Mapped[Optional[str]] = mapped_column(String(255))
    genre: Mapped[Optional[str]] = mapped_column(String(50))
    target_tempo: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(20))

    # Session timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # WebSocket session tracking
    websocket_session_id: Mapped[Optional[str]] = mapped_column(String(255))
    chunks_processed: Mapped[int] = mapped_column(Integer, default=0)

    # Session status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, completed, abandoned

    # Relationships
    user: Mapped["User"] = relationship()
    performances: Mapped[List["Performance"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Performance(Base):
    """
    Individual performance recording within a real-time session.
    Stores audio/MIDI data and links to analysis results.
    """
    __tablename__ = "performances"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("realtime_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # Recording metadata
    recording_started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    recording_duration: Mapped[float] = mapped_column(Float)  # seconds

    # File paths
    audio_path: Mapped[Optional[str]] = mapped_column(String(500))
    midi_path: Mapped[Optional[str]] = mapped_column(String(500))

    # Recording format/quality
    sample_rate: Mapped[int] = mapped_column(Integer, default=44100)
    audio_format: Mapped[Optional[str]] = mapped_column(String(20))  # wav, mp3, etc.

    # Performance context
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    session: Mapped["RealtimeSession"] = relationship(back_populates="performances")
    analysis_results: Mapped[List["AnalysisResult"]] = relationship(
        back_populates="performance",
        cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnalysisResult(Base):
    """
    Real-time analysis results for a performance.
    Stores pitch accuracy, rhythm accuracy, dynamics, and AI feedback.
    """
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    performance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("performances.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # Analysis scores (0.0 - 1.0)
    pitch_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    rhythm_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    dynamics_range: Mapped[Optional[float]] = mapped_column(Float)
    overall_score: Mapped[Optional[float]] = mapped_column(Float)

    # Detailed metrics
    avg_pitch_deviation_cents: Mapped[Optional[float]] = mapped_column(Float)
    timing_consistency: Mapped[Optional[float]] = mapped_column(Float)
    tempo_stability: Mapped[Optional[float]] = mapped_column(Float)
    note_accuracy_rate: Mapped[Optional[float]] = mapped_column(Float)  # Correct notes / total notes

    # Detected events counts
    total_notes_detected: Mapped[Optional[int]] = mapped_column(Integer)
    total_onsets_detected: Mapped[Optional[int]] = mapped_column(Integer)
    total_dynamics_events: Mapped[Optional[int]] = mapped_column(Integer)

    # AI-generated feedback (JSONB for structured data)
    feedback_json: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    # Example structure: {
    #   "strengths": ["Good pitch accuracy", "Consistent tempo"],
    #   "areas_for_improvement": ["Work on dynamics", "Practice transitions"],
    #   "specific_tips": ["Focus on measures 4-8", "Try slower tempo first"],
    #   "practice_recommendations": [...]
    # }

    # Performance characteristics
    difficulty_estimate: Mapped[Optional[str]] = mapped_column(String(20))  # beginner, intermediate, advanced
    genre_match_score: Mapped[Optional[float]] = mapped_column(Float)  # How well it matches expected genre

    # Analysis metadata
    analysis_engine_version: Mapped[Optional[str]] = mapped_column(String(50))
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    performance: Mapped["Performance"] = relationship(back_populates="analysis_results")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class ProgressMetric(Base):
    """
    Aggregated progress metrics over time for a user.
    Used for dashboard visualization and trend analysis.
    """
    __tablename__ = "progress_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    # Time period
    metric_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily, weekly, monthly

    # Practice volume
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    total_practice_time_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Performance averages (0.0 - 1.0)
    avg_pitch_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    avg_rhythm_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    avg_dynamics_range: Mapped[Optional[float]] = mapped_column(Float)
    avg_overall_score: Mapped[Optional[float]] = mapped_column(Float)

    # Progress indicators
    improvement_rate: Mapped[Optional[float]] = mapped_column(Float)  # Rate of improvement over previous period
    consistency_score: Mapped[Optional[float]] = mapped_column(Float)  # How consistent practice is

    # Genre distribution (JSON string)
    genre_breakdown_json: Mapped[Optional[str]] = mapped_column(Text)
    # Example: {"gospel": 45, "jazz": 30, "classical": 25}

    # Achievements/milestones (JSON string)
    milestones_json: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    user: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
