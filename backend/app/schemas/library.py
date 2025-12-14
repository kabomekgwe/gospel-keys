"""Pydantic schemas for library management"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SongSummary(BaseModel):
    """Summary view of a song for list displays"""
    id: str
    title: str
    artist: Optional[str] = None
    duration: Optional[float] = None
    tempo: Optional[float] = None
    key_signature: Optional[str] = None
    favorite: bool = False
    created_at: datetime
    last_accessed_at: Optional[datetime] = None


class SongDetail(BaseModel):
    """Detailed song information"""
    id: str
    title: str
    artist: Optional[str] = None
    source_url: Optional[str] = None
    source_file: Optional[str] = None
    duration: Optional[float] = None
    tempo: Optional[float] = None
    key_signature: Optional[str] = None
    time_signature: Optional[str] = None
    difficulty: Optional[str] = None
    midi_file_path: Optional[str] = None
    note_count: int = 0
    chord_count: int = 0
    annotation_count: int = 0
    snippet_count: int = 0
    unique_notes_count: int = 0
    favorite: bool = False
    created_at: datetime
    last_accessed_at: Optional[datetime] = None


class SongUpdate(BaseModel):
    """Update song metadata"""
    title: Optional[str] = None
    artist: Optional[str] = None
    difficulty: Optional[str] = None

class SongNoteResponse(BaseModel):
    """MIDI note data"""
    id: int
    pitch: int
    start_time: float
    end_time: float
    velocity: int


class SongChordResponse(BaseModel):
    """Detected chord data"""
    id: int
    time: float
    duration: float
    chord: str
    root: str
    quality: str
    bass_note: Optional[str] = None
