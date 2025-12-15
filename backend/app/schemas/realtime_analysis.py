"""
Pydantic schemas for Real-Time Analysis API
STORY-3.2: Database Schema & Progress Tracking

Request and response models for Phase 3 real-time analysis endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


# =============================================================================
# Session Schemas
# =============================================================================

class SessionCreate(BaseModel):
    """Request schema for creating a practice session."""
    user_id: int = Field(..., description="User ID")
    piece_name: Optional[str] = Field(None, max_length=255, description="Name of the piece")
    genre: Optional[str] = Field(None, max_length=50, description="Music genre")
    target_tempo: Optional[int] = Field(None, ge=20, le=300, description="Target tempo in BPM")
    difficulty_level: Optional[str] = Field(None, description="beginner, intermediate, or advanced")
    websocket_session_id: Optional[str] = Field(None, description="WebSocket session UUID")

    @field_validator('difficulty_level')
    @classmethod
    def validate_difficulty(cls, v):
        if v and v not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError('difficulty_level must be beginner, intermediate, or advanced')
        return v


class SessionResponse(BaseModel):
    """Response schema for practice session."""
    id: uuid.UUID
    user_id: int
    piece_name: Optional[str] = None
    genre: Optional[str] = None
    target_tempo: Optional[int] = None
    difficulty_level: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    websocket_session_id: Optional[str] = None
    chunks_processed: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Performance Schemas
# =============================================================================

class PerformanceCreate(BaseModel):
    """Request schema for creating a performance recording."""
    session_id: uuid.UUID = Field(..., description="Parent session ID")
    audio_path: Optional[str] = Field(None, max_length=500, description="Path to audio file")
    midi_path: Optional[str] = Field(None, max_length=500, description="Path to MIDI file")
    sample_rate: int = Field(44100, ge=8000, le=192000, description="Sample rate in Hz")
    audio_format: Optional[str] = Field(None, max_length=20, description="Audio format (wav, mp3, etc.)")
    notes: Optional[str] = Field(None, description="User notes about the performance")


class PerformanceResponse(BaseModel):
    """Response schema for performance recording."""
    id: uuid.UUID
    session_id: uuid.UUID
    recording_started_at: datetime
    recording_duration: Optional[float] = None
    audio_path: Optional[str] = None
    midi_path: Optional[str] = None
    sample_rate: int
    audio_format: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Analysis Result Schemas
# =============================================================================

class AnalysisResultCreate(BaseModel):
    """Request schema for creating analysis results."""
    performance_id: uuid.UUID = Field(..., description="Parent performance ID")

    # Core accuracy scores (0.0 - 1.0)
    pitch_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Pitch accuracy score")
    rhythm_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Rhythm accuracy score")
    dynamics_range: Optional[float] = Field(None, ge=0.0, le=1.0, description="Dynamics range score")
    overall_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall performance score")

    # Detailed metrics
    avg_pitch_deviation_cents: Optional[float] = Field(None, description="Average pitch deviation in cents")
    timing_consistency: Optional[float] = Field(None, ge=0.0, le=1.0, description="Timing consistency")
    tempo_stability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Tempo stability")
    note_accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Correct notes / total notes")

    # Event counts
    total_notes_detected: Optional[int] = Field(None, ge=0, description="Total notes detected")
    total_onsets_detected: Optional[int] = Field(None, ge=0, description="Total onsets detected")
    total_dynamics_events: Optional[int] = Field(None, ge=0, description="Total dynamics events")

    # AI feedback (JSON string)
    feedback_json: Optional[str] = Field(None, description="JSON string with AI feedback")

    # Performance characteristics
    difficulty_estimate: Optional[str] = Field(None, description="Estimated difficulty level")
    genre_match_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Genre match score")

    # Analysis metadata
    analysis_engine_version: Optional[str] = Field(None, max_length=50, description="Analysis engine version")
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time in milliseconds")


class AnalysisResultResponse(BaseModel):
    """Response schema for analysis results."""
    id: uuid.UUID
    performance_id: uuid.UUID
    pitch_accuracy: Optional[float] = None
    rhythm_accuracy: Optional[float] = None
    dynamics_range: Optional[float] = None
    overall_score: Optional[float] = None
    avg_pitch_deviation_cents: Optional[float] = None
    timing_consistency: Optional[float] = None
    tempo_stability: Optional[float] = None
    note_accuracy_rate: Optional[float] = None
    total_notes_detected: Optional[int] = None
    total_onsets_detected: Optional[int] = None
    total_dynamics_events: Optional[int] = None
    feedback_json: Optional[str] = None
    difficulty_estimate: Optional[str] = None
    genre_match_score: Optional[float] = None
    analysis_engine_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Progress Metric Schemas
# =============================================================================

class ProgressMetricResponse(BaseModel):
    """Response schema for progress metrics."""
    id: uuid.UUID
    user_id: int
    metric_date: datetime
    period_type: str  # daily, weekly, monthly
    total_sessions: int
    total_practice_time_seconds: int
    avg_pitch_accuracy: Optional[float] = None
    avg_rhythm_accuracy: Optional[float] = None
    avg_dynamics_range: Optional[float] = None
    avg_overall_score: Optional[float] = None
    improvement_rate: Optional[float] = None
    consistency_score: Optional[float] = None
    genre_breakdown_json: Optional[str] = None
    milestones_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Analytics Schemas
# =============================================================================

class UserStatsResponse(BaseModel):
    """Response schema for user aggregate statistics."""
    total_sessions: int = Field(..., description="Total practice sessions")
    total_practice_hours: float = Field(..., description="Total practice time in hours")
    total_analyses: int = Field(..., description="Total analysis results")
    avg_pitch_accuracy: float = Field(..., description="Average pitch accuracy (0.0-1.0)")
    avg_rhythm_accuracy: float = Field(..., description="Average rhythm accuracy (0.0-1.0)")
    avg_overall_score: float = Field(..., description="Average overall score (0.0-1.0)")
    period_days: int = Field(..., description="Number of days included in statistics")


# =============================================================================
# Utility Schemas for Complex Responses
# =============================================================================

class PerformanceWithAnalysis(BaseModel):
    """Performance with all its analysis results."""
    performance: PerformanceResponse
    analysis_results: list[AnalysisResultResponse]


class SessionCompleteData(BaseModel):
    """Complete session data with all performances and analyses."""
    session: SessionResponse
    performances: list[PerformanceWithAnalysis]
    total_performances: int
    total_analyses: int
