"""Blues Piano Generation Schemas"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class BluesStyle(str, Enum):
    """Blues music styles"""
    DELTA = "delta"
    CHICAGO = "chicago"
    TEXAS = "texas"
    BOOGIE_WOOGIE = "boogie_woogie"


class BluesApplication(str, Enum):
    """Blues piano application types"""
    SLOW = "slow"             # Slow blues (60-80 BPM), expressive
    SHUFFLE = "shuffle"       # Medium shuffle (100-120 BPM), classic
    FAST = "fast"             # Fast blues (140-180 BPM), uptempo


class GenerateBluesRequest(BaseModel):
    """Request for blues piano generation"""
    description: str = Field(
        ...,
        description="Natural language description of desired arrangement",
        examples=[
            "Slow blues in E with expressive bends and call-response",
            "Classic Chicago shuffle in A with boogie-woogie bass",
            "Fast uptempo blues in C with tremolo and double stops"
        ]
    )
    key: Optional[str] = Field(None, description="Musical key")
    tempo: Optional[int] = Field(None, ge=50, le=200, description="Tempo in BPM")
    num_bars: int = Field(12, ge=4, le=64, description="Number of bars (typically 12)")
    application: BluesApplication = Field(BluesApplication.SHUFFLE, description="Application type")
    include_progression: bool = Field(True, description="Include progression analysis")


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


class GenerateBluesResponse(BaseModel):
    """Response for blues piano generation"""
    success: bool
    midi_file_path: Optional[str] = None
    midi_base64: Optional[str] = None
    progression: Optional[List[ChordAnalysis]] = None
    arrangement_info: dict = Field(default_factory=dict)
    notes_preview: Optional[List[MIDINoteInfo]] = None
    generation_method: str
    error: Optional[str] = None


class BluesGeneratorStatus(BaseModel):
    """Status of blues generation system"""
    gemini_available: bool
    rules_available: bool
    ready_for_production: bool
