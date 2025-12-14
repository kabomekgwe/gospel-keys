"""Gospel Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class GospelStyle(str, Enum):
    """Gospel music styles"""
    TRADITIONAL = "traditional"
    CONTEMPORARY = "contemporary"
    WORSHIP = "worship"
    UPTEMPO = "uptempo"
    JAZZ_GOSPEL = "jazz-gospel"


class GospelApplication(str, Enum):
    """Gospel piano application types"""
    PRACTICE = "practice"
    CONCERT = "concert"
    WORSHIP = "worship"
    UPTEMPO = "uptempo"


class GenerateGospelRequest(BaseModel):
    """Request for gospel piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "Kirk Franklin style uptempo in C major",
            "Slow worship ballad in Bb with rich harmonies",
            "Traditional Thomas Dorsey style in F"
        ]
    )
    key: Optional[str] = Field(
        None,
        description="Musical key (e.g., 'C', 'Bb', 'F#m'). If not specified, extracted from description"
    )
    tempo: Optional[int] = Field(
        None,
        ge=50,
        le=180,
        description="Tempo in BPM. If not specified, inferred from style"
    )
    num_bars: int = Field(
        16,
        ge=4,
        le=64,
        description="Number of bars to generate"
    )
    application: GospelApplication = Field(
        GospelApplication.WORSHIP,
        description="Application type for arrangement complexity"
    )
    ai_percentage: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="AI vs rules percentage (0.0=pure rules, 1.0=pure AI). Use 0.0 until MLX model is trained"
    )
    include_progression: bool = Field(
        True,
        description="Include chord progression analysis in response"
    )


class ChordAnalysis(BaseModel):
    """Analysis of a single chord"""
    symbol: str = Field(..., description="Chord symbol (e.g., 'Cmaj9')")
    function: str = Field(..., description="Harmonic function (e.g., 'I', 'V7')")
    notes: List[str] = Field(..., description="Note names in the chord")
    comment: Optional[str] = Field(None, description="Additional context")


class MIDINoteInfo(BaseModel):
    """MIDI note information for visualization"""
    pitch: int = Field(..., ge=0, le=127, description="MIDI note number")
    time: float = Field(..., description="Time position in beats")
    duration: float = Field(..., description="Note duration in beats")
    velocity: int = Field(..., ge=0, le=127, description="MIDI velocity")
    hand: str = Field(..., description="left or right hand")


class GenerateGospelResponse(BaseModel):
    """Response for gospel piano generation"""
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
        description="'gemini+rules', 'gemini+mlx', or 'gemini+hybrid'"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )


class GospelGeneratorStatus(BaseModel):
    """Status of gospel generation system"""
    mlx_available: bool = Field(..., description="Whether MLX model is loaded")
    mlx_trained: bool = Field(..., description="Whether MLX model is trained on gospel data")
    gemini_available: bool = Field(..., description="Whether Gemini API is configured")
    recommended_ai_percentage: float = Field(
        ...,
        description="Recommended AI percentage based on training status"
    )
    dataset_size: int = Field(..., description="Number of gospel MIDIs in training dataset")
    ready_for_production: bool = Field(
        ...,
        description="Whether system is ready for high-quality generation"
    )
