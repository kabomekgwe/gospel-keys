"""Jazz Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class JazzStyle(str, Enum):
    """Jazz music styles"""
    BEBOP = "bebop"
    SWING = "swing"
    BALLAD = "ballad"
    LATIN = "latin"
    MODAL = "modal"


class JazzApplication(str, Enum):
    """Jazz piano application types"""
    BALLAD = "ballad"         # Slow tempo (60-80 BPM), sustained voicings
    STANDARD = "standard"     # Medium swing (120-200 BPM), walking bass
    UPTEMPO = "uptempo"       # Fast swing (200-300 BPM), continuous motion


class GenerateJazzRequest(BaseModel):
    """Request for jazz piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "Bill Evans style ballad in Cm with rootless voicings",
            "Uptempo bebop in F major with walking bass",
            "Oscar Peterson style swing in Bb with block chords"
        ]
    )
    key: Optional[str] = Field(
        None,
        description="Musical key (e.g., 'C', 'Bb', 'F#m'). If not specified, extracted from description"
    )
    tempo: Optional[int] = Field(
        None,
        ge=50,
        le=300,
        description="Tempo in BPM. If not specified, inferred from style"
    )
    num_bars: int = Field(
        16,
        ge=4,
        le=64,
        description="Number of bars to generate"
    )
    application: JazzApplication = Field(
        JazzApplication.STANDARD,
        description="Application type for arrangement style"
    )
    include_progression: bool = Field(
        True,
        description="Include chord progression analysis in response"
    )


class ChordAnalysis(BaseModel):
    """Analysis of a single chord"""
    symbol: str = Field(..., description="Chord symbol (e.g., 'Dm7', 'G7#11')")
    function: str = Field(..., description="Harmonic function (e.g., 'ii7', 'V7')")
    notes: List[str] = Field(..., description="Note names in the chord")
    comment: Optional[str] = Field(None, description="Additional context")


class MIDINoteInfo(BaseModel):
    """MIDI note information for visualization"""
    pitch: int = Field(..., ge=0, le=127, description="MIDI note number")
    time: float = Field(..., description="Time position in beats")
    duration: float = Field(..., description="Note duration in beats")
    velocity: int = Field(..., ge=0, le=127, description="MIDI velocity")
    hand: str = Field(..., description="left or right hand")


class GenerateJazzResponse(BaseModel):
    """Response for jazz piano generation"""
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
        description="'gemini+rules' (hybrid not yet available for jazz)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )


class JazzGeneratorStatus(BaseModel):
    """Status of jazz generation system"""
    gemini_available: bool = Field(..., description="Whether Gemini API is configured")
    rules_available: bool = Field(..., description="Whether rule-based arranger is available")
    ready_for_production: bool = Field(
        ...,
        description="Whether system is ready for generation"
    )
