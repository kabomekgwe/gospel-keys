"""Classical Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class ClassicalPeriod(str, Enum):
    """Classical music periods"""
    BAROQUE = "baroque"
    CLASSICAL = "classical"
    ROMANTIC = "romantic"


class ClassicalApplication(str, Enum):
    """Classical piano application types (period styles)"""
    BAROQUE = "baroque"      # Baroque period (1600-1750), counterpoint
    CLASSICAL = "classical"  # Classical period (1750-1820), balanced
    ROMANTIC = "romantic"    # Romantic period (1820-1900), expressive


class GenerateClassicalRequest(BaseModel):
    """Request for classical piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "Mozart-style piano sonata in C major with Alberti bass",
            "Baroque fugue subject in D minor with counterpoint",
            "Romantic nocturne in E-flat major with arpeggios"
        ]
    )
    key: Optional[str] = Field(None, description="Musical key")
    tempo: Optional[int] = Field(None, ge=40, le=200, description="Tempo in BPM")
    num_bars: int = Field(8, ge=4, le=64, description="Number of bars")
    application: ClassicalApplication = Field(ClassicalApplication.CLASSICAL, description="Period style")
    include_progression: bool = Field(True, description="Include progression analysis")
    time_signature: tuple = Field((4, 4), description="Time signature (numerator, denominator)")


class ChordAnalysis(BaseModel):
    """Analysis of a single chord"""
    symbol: str
    function: str
    notes: List[str]
    comment: Optional[str] = None


class MIDINoteInfo(BaseModel):
    """MIDI note information"""
    pitch: int = Field(..., ge=0, le=127)
    time: float
    duration: float
    velocity: int = Field(..., ge=0, le=127)
    hand: str


class GenerateClassicalResponse(BaseModel):
    """Response for classical piano generation"""
    success: bool
    midi_file_path: Optional[str] = None
    midi_base64: Optional[str] = None
    progression: Optional[List[ChordAnalysis]] = None
    arrangement_info: dict = Field(default_factory=dict)
    notes_preview: Optional[List[MIDINoteInfo]] = None
    generation_method: str
    error: Optional[str] = None


class ClassicalGeneratorStatus(BaseModel):
    """Status of classical generation system"""
    gemini_available: bool
    rules_available: bool
    ready_for_production: bool
