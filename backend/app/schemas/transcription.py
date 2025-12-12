"""Data schemas for transcription API"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class JobStatus(str, Enum):
    """Transcription job status"""
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NoteEvent(BaseModel):
    """Individual MIDI note event"""
    pitch: int = Field(..., ge=0, le=127, description="MIDI pitch (0-127)")
    start_time: float = Field(..., ge=0, description="Note start time in seconds")
    end_time: float = Field(..., ge=0, description="Note end time in seconds")
    velocity: int = Field(..., ge=0, le=127, description="Note velocity (0-127)")
    
    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: float, info) -> float:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ChordEvent(BaseModel):
    """Detected chord event"""
    time: float = Field(..., ge=0, description="Chord start time in seconds")
    duration: float = Field(..., gt=0, description="Chord duration in seconds")
    chord: str = Field(..., description="Chord name (e.g., 'Cmaj7', 'Dm9')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    root: str = Field(..., description="Root note (e.g., 'C', 'D')")
    quality: str = Field(..., description="Chord quality (e.g., 'maj7', 'm9')")
    bass_note: Optional[str] = Field(None, description="Bass note for slash chords")
    voicing_notes: Optional[list[str]] = Field(None, description="Actual notes in the voicing")


class GospelPattern(BaseModel):
    """Detected gospel progression pattern"""
    pattern_type: str = Field(..., description="Pattern type (e.g., '2-5-1', 'passing_diminished')")
    start_time: float = Field(..., ge=0, description="Pattern start time")
    end_time: float = Field(..., ge=0, description="Pattern end time")
    chords: list[str] = Field(..., description="Chord names in the pattern")
    key: str = Field(..., description="Key of the pattern")
    description: str = Field(..., description="Human-readable explanation")


class TranscriptionOptions(BaseModel):
    """Options for transcription processing"""
    isolate_piano: bool = Field(True, description="Use source separation to isolate piano")
    detect_chords: bool = Field(True, description="Perform chord detection")
    detect_tempo: bool = Field(True, description="Estimate tempo")
    detect_key: bool = Field(True, description="Detect musical key")
    start_time: Optional[float] = Field(None, ge=0, description="Process from this timestamp (seconds)")
    end_time: Optional[float] = Field(None, gt=0, description="Process until this timestamp (seconds)")


class TranscriptionResult(BaseModel):
    """Complete transcription result"""
    notes: list[NoteEvent] = Field(..., description="Detected MIDI notes")
    chords: list[ChordEvent] = Field(default_factory=list, description="Detected chords")
    patterns: list[GospelPattern] = Field(default_factory=list, description="Gospel patterns (Phase 2)")
    tempo: Optional[float] = Field(None, gt=0, description="Estimated tempo in BPM")
    time_signature: Optional[str] = Field(None, description="Time signature (e.g., '4/4')")
    key: Optional[str] = Field(None, description="Detected key (e.g., 'C major', 'G minor')")
    duration: float = Field(..., gt=0, description="Total duration in seconds")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    midi_url: Optional[str] = Field(None, description="URL to download MIDI file")
    source_title: Optional[str] = Field(None, description="Original video/file title")


class TranscriptionJob(BaseModel):
    """Transcription job tracking"""
    id: str = Field(..., description="Unique job ID")
    status: JobStatus = Field(..., description="Current job status")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current processing step")
    source_url: Optional[str] = Field(None, description="YouTube URL (if URL-based)")
    source_file: Optional[str] = Field(None, description="Uploaded filename (if file-based)")
    options: TranscriptionOptions = Field(..., description="Processing options")
    result: Optional[TranscriptionResult] = Field(None, description="Result when complete")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.now, description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")


class TranscribeUrlRequest(BaseModel):
    """Request to transcribe from YouTube URL"""
    url: str = Field(..., description="YouTube video URL")
    options: TranscriptionOptions = Field(default_factory=TranscriptionOptions)
    
    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        """Validate YouTube URL format"""
        if not any(domain in v for domain in ["youtube.com", "youtu.be"]):
            raise ValueError("Must be a valid YouTube URL")
        return v


class TranscribeUploadRequest(BaseModel):
    """Request to transcribe from uploaded file"""
    options: TranscriptionOptions = Field(default_factory=TranscriptionOptions)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")


class DetailedHealthResponse(BaseModel):
    """Detailed health check response"""
    status: str = Field(..., description="Overall status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    checks: dict[str, bool] = Field(..., description="Individual component checks")
