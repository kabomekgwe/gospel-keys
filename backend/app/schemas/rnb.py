"""R&B Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class RnBStyle(str, Enum):
    """R&B music styles"""
    CLASSIC_SOUL = "classic_soul"
    NEO_SOUL = "neo_soul"
    CONTEMPORARY_RNB = "contemporary_rnb"
    BALLAD = "ballad"


class RnBApplication(str, Enum):
    """R&B piano application types"""
    BALLAD = "ballad"         # Slow soul ballad (60-75 BPM), lush voicings
    GROOVE = "groove"         # Mid-tempo R&B groove (80-95 BPM), syncopated
    UPTEMPO = "uptempo"       # Upbeat contemporary (95-110 BPM), 16th notes


class GenerateRnBRequest(BaseModel):
    """Request for R&B piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "Smooth neo-soul ballad in F major with extended chords",
            "Mid-tempo R&B groove in D with syncopation",
            "Contemporary R&B in C with lush maj9 and 11th chords"
        ]
    )
    key: Optional[str] = Field(
        None,
        description="Musical key (e.g., 'C', 'F', 'Dm'). If not specified, extracted from description"
    )
    tempo: Optional[int] = Field(
        None,
        ge=50,
        le=140,
        description="Tempo in BPM. If not specified, inferred from style"
    )
    num_bars: int = Field(
        8,
        ge=4,
        le=64,
        description="Number of bars to generate"
    )
    application: RnBApplication = Field(
        RnBApplication.GROOVE,
        description="Application type for arrangement style"
    )
    include_progression: bool = Field(
        True,
        description="Include chord progression analysis in response"
    )


class ChordAnalysis(BaseModel):
    """Analysis of a single chord"""
    symbol: str = Field(..., description="Chord symbol (e.g., 'Cmaj9', 'Am7', 'G9')")
    function: str = Field(..., description="Harmonic function (e.g., 'I', 'vi7', 'V9')")
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


class GenerateRnBResponse(BaseModel):
    """Response for R&B piano generation"""
    success: bool = Field(..., description="Whether generation succeeded")
    midi_file_path: Optional[str] = Field(None, description="Path to generated MIDI file")
    midi_base64: Optional[str] = Field(None, description="Base64 encoded MIDI data")
    arrangement_info: Optional[ArrangementInfo] = Field(None, description="Arrangement metadata")
    chord_analysis: Optional[List[ChordAnalysis]] = Field(None, description="Chord progression analysis")
    notes_preview: Optional[List[MIDINoteInfo]] = Field(None, description="Preview of first bars")
    generation_method: Optional[str] = Field(None, description="Method used (gemini+rules, rules-only)")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class RnBGeneratorStatus(BaseModel):
    """Status of R&B generator"""
    gemini_available: bool = Field(..., description="Whether Gemini API is available")
    ready: bool = Field(..., description="Whether generator is ready")
