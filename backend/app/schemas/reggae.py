"""Reggae Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class ReggaeStyle(str, Enum):
    """Reggae music styles"""
    ROOTS = "roots"
    DANCEHALL = "dancehall"
    DUB = "dub"
    LOVERS_ROCK = "lovers_rock"


class ReggaeApplication(str, Enum):
    """Reggae piano application types"""
    ROOTS = "roots"           # Classic roots (70-80 BPM), dub bass, heavy skank
    DANCEHALL = "dancehall"   # Faster dancehall (90-110 BPM), double skank
    DUB = "dub"              # Minimal dub (60-75 BPM), sparse, heavy bass


class GenerateReggaeRequest(BaseModel):
    """Request for reggae piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "Roots reggae in G major with heavy dub bass",
            "Upbeat dancehall in D with double skank pattern",
            "Minimal dub reggae in Am with sparse bubble rhythm"
        ]
    )
    key: Optional[str] = Field(
        None,
        description="Musical key (e.g., 'C', 'G', 'Am'). If not specified, extracted from description"
    )
    tempo: Optional[int] = Field(
        None,
        ge=50,
        le=120,
        description="Tempo in BPM. If not specified, inferred from style"
    )
    num_bars: int = Field(
        8,
        ge=4,
        le=64,
        description="Number of bars to generate"
    )
    application: ReggaeApplication = Field(
        ReggaeApplication.ROOTS,
        description="Application type for arrangement style"
    )
    include_progression: bool = Field(
        True,
        description="Include chord progression analysis in response"
    )


class ChordAnalysis(BaseModel):
    """Analysis of a single chord"""
    symbol: str = Field(..., description="Chord symbol (e.g., 'C', 'Gsus4')")
    function: str = Field(..., description="Harmonic function (e.g., 'I', 'IV', 'V')")
    notes: List[str] = Field(..., description="Note names in the chord")
    comment: Optional[str] = Field(None, description="Additional context")


class MIDINoteInfo(BaseModel):
    """MIDI note information for visualization"""
    pitch: int = Field(..., ge=0, le=127, description="MIDI note number")
    time: float = Field(..., description="Time position in beats")
    duration: float = Field(..., description="Note duration in beats")
    velocity: int = Field(..., ge=0, le=127, description="MIDI velocity")
    hand: str = Field(..., description="left or right hand")


class ArrangementInfo(BaseModel):
    """Arrangement metadata"""
    tempo: int
    key: str
    time_signature: tuple[int, int]
    total_bars: int
    total_notes: int
    duration_seconds: float
    application: str


class GenerateReggaeResponse(BaseModel):
    """Response for reggae piano generation"""
    success: bool = Field(..., description="Whether generation succeeded")
    midi_file_path: Optional[str] = Field(None, description="Path to generated MIDI file")
    midi_base64: Optional[str] = Field(None, description="Base64 encoded MIDI data")
    arrangement_info: Optional[ArrangementInfo] = Field(None, description="Arrangement metadata")
    chord_analysis: Optional[List[ChordAnalysis]] = Field(None, description="Chord progression analysis")
    notes_preview: Optional[List[MIDINoteInfo]] = Field(None, description="Preview of first bars")
    generation_method: Optional[str] = Field(None, description="Method used (gemini+rules, rules-only)")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class ReggaeGeneratorStatus(BaseModel):
    """Status of reggae generator"""
    gemini_available: bool = Field(..., description="Whether Gemini API is available")
    ready: bool = Field(..., description="Whether generator is ready")
