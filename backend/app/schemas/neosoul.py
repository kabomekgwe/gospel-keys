"""Neo-Soul Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class NeosoulStyle(str, Enum):
    """Neo-soul music styles"""
    SMOOTH = "smooth"
    UPTEMPO = "uptempo"
    CONTEMPORARY = "contemporary"
    ALTERNATIVE = "alternative"


class NeosoulApplication(str, Enum):
    """Neo-soul piano application types"""
    SMOOTH = "smooth"         # Slow tempo (70-90 BPM), sustained voicings
    UPTEMPO = "uptempo"       # Medium tempo (90-110 BPM), syncopated grooves


class GenerateNeosoulRequest(BaseModel):
    """Request for neo-soul piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "D'Angelo style smooth groove in Dm with extended voicings",
            "Erykah Badu style uptempo in Eb with chromatic fills",
            "Robert Glasper style contemporary in Am with sus chords"
        ]
    )
    key: Optional[str] = Field(
        None,
        description="Musical key (e.g., 'C', 'Bb', 'F#m'). If not specified, extracted from description"
    )
    tempo: Optional[int] = Field(
        None,
        ge=60,
        le=120,
        description="Tempo in BPM. If not specified, inferred from style"
    )
    num_bars: int = Field(
        16,
        ge=4,
        le=64,
        description="Number of bars to generate"
    )
    application: NeosoulApplication = Field(
        NeosoulApplication.SMOOTH,
        description="Application type for arrangement style"
    )
    include_progression: bool = Field(
        True,
        description="Include chord progression analysis in response"
    )


class ChordAnalysis(BaseModel):
    """Analysis of a single chord"""
    symbol: str = Field(..., description="Chord symbol (e.g., 'Dm9', 'Emaj7#11')")
    function: str = Field(..., description="Harmonic function (e.g., 'i9', 'IVmaj7#11')")
    notes: List[str] = Field(..., description="Note names in the chord")
    comment: Optional[str] = Field(None, description="Additional context")


class MIDINoteInfo(BaseModel):
    """MIDI note information for visualization"""
    pitch: int = Field(..., ge=0, le=127, description="MIDI note number")
    time: float = Field(..., description="Time position in beats")
    duration: float = Field(..., description="Note duration in beats")
    velocity: int = Field(..., ge=0, le=127, description="MIDI velocity")
    hand: str = Field(..., description="left or right hand")


class GenerateNeosoulResponse(BaseModel):
    """Response for neo-soul piano generation"""
    success: bool = Field(..., description="Whether generation succeeded")
    midi_file_path: Optional[str] = Field(
        None,
        description="Path to generated MIDI file"
    )
    midi_base64: Optional[str] = Field(
        None,
        description="Base64-encoded MIDI file for direct download"
    )
    progression: Optional[List[ChordAnalysis]] = Field(
        None,
        description="Generated chord progression with analysis"
    )
    arrangement_info: dict = Field(
        default_factory=dict,
        description="Metadata about the arrangement"
    )
    notes_preview: Optional[List[MIDINoteInfo]] = Field(
        None,
        description="Preview of first 4 bars for visualization"
    )
    generation_method: str = Field(
        ...,
        description="'gemini+rules' (hybrid not yet available for neo-soul)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )


class NeosoulGeneratorStatus(BaseModel):
    """Status of neo-soul generation system"""
    gemini_available: bool = Field(..., description="Whether Gemini API is configured")
    rules_available: bool = Field(..., description="Whether rule-based arranger is available")
    ready_for_production: bool = Field(
        ...,
        description="Whether system is ready for generation"
    )
