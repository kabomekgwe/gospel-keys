"""Latin/Salsa Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class LatinStyle(str, Enum):
    """Latin music styles"""
    SALSA = "salsa"
    MAMBO = "mambo"
    CHA_CHA = "cha_cha"
    BOSSA_NOVA = "bossa_nova"


class LatinApplication(str, Enum):
    """Latin piano application types"""
    SALSA = "salsa"           # Classic salsa (90-100 BPM), montuno, tumbao
    BALLAD = "ballad"         # Slow bolero (60-80 BPM), sustained voicings
    UPTEMPO = "uptempo"       # Fast mambo (110-140 BPM), driving rhythm


class GenerateLatinRequest(BaseModel):
    """Request for Latin piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "Upbeat salsa in C major with montuno patterns",
            "Slow bolero ballad in Dm with Cuban harmony",
            "Fast mambo in F with clave rhythm and tumbao bass"
        ]
    )
    key: Optional[str] = Field(
        None,
        description="Musical key (e.g., 'C', 'Dm', 'F'). If not specified, extracted from description"
    )
    tempo: Optional[int] = Field(
        None,
        ge=50,
        le=180,
        description="Tempo in BPM. If not specified, inferred from style"
    )
    num_bars: int = Field(
        8,
        ge=4,
        le=64,
        description="Number of bars to generate"
    )
    application: LatinApplication = Field(
        LatinApplication.SALSA,
        description="Application type for arrangement style"
    )
    include_progression: bool = Field(
        True,
        description="Include chord progression analysis in response"
    )


class ChordAnalysis(BaseModel):
    """Analysis of a single chord"""
    symbol: str = Field(..., description="Chord symbol (e.g., 'Cmaj7', 'A7')")
    function: str = Field(..., description="Harmonic function (e.g., 'I', 'VI7', 'ii-V')")
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


class GenerateLatinResponse(BaseModel):
    """Response for Latin piano generation"""
    success: bool = Field(..., description="Whether generation succeeded")
    midi_file_path: Optional[str] = Field(None, description="Path to generated MIDI file")
    midi_base64: Optional[str] = Field(None, description="Base64 encoded MIDI data")
    arrangement_info: Optional[ArrangementInfo] = Field(None, description="Arrangement metadata")
    chord_analysis: Optional[List[ChordAnalysis]] = Field(None, description="Chord progression analysis")
    notes_preview: Optional[List[MIDINoteInfo]] = Field(None, description="Preview of first bars")
    generation_method: Optional[str] = Field(None, description="Method used (gemini+rules, rules-only)")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class LatinGeneratorStatus(BaseModel):
    """Status of Latin generator"""
    gemini_available: bool = Field(..., description="Whether Gemini API is available")
    ready: bool = Field(..., description="Whether generator is ready")
