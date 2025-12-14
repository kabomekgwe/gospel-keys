"""Voicing API Endpoints

Provides chord voicing data for the interactive keyboard visualization.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/voicing", tags=["voicing"])


class VoicingNote(BaseModel):
    """A single note in a voicing with hand assignment."""
    pitch: int = Field(..., ge=0, le=127)
    hand: str = Field(..., description="'left' or 'right'")
    finger: Optional[int] = Field(None, ge=1, le=5, description="Finger number 1-5")


class VoicingResponse(BaseModel):
    """Complete voicing information for a chord."""
    chord: str
    voicing_type: str
    notes: list[VoicingNote]
    intervals: list[int] = Field(default_factory=list)
    width_semitones: int = 0
    complexity_score: float = Field(0.5, ge=0, le=1)
    hand_span_inches: Optional[float] = None
    has_root: bool = True
    has_third: bool = True
    has_seventh: bool = False
    extensions: list[str] = Field(default_factory=list)


class VoicingGenerationRequest(BaseModel):
    """Request for generating a chord voicing."""
    chord: str = Field(..., description="Chord symbol (e.g., Dm7, Cmaj9)")
    style: str = Field("open", description="Voicing style: closed, open, drop2, shell")
    root_octave: int = Field(3, ge=1, le=6, description="Octave for root note")
    add_extensions: bool = Field(True, description="Add neo-soul extensions")


@router.get("/{chord}", response_model=VoicingResponse)
async def get_voicing(
    chord: str,
    style: str = Query("open", description="Voicing style"),
    root_octave: int = Query(3, ge=1, le=6),
    add_extensions: bool = Query(True),
):
    """
    Get voicing information for a chord.
    
    Returns note pitches with hand assignments, intervals, and complexity metrics.
    """
    try:
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        notes = generator.generate_voicing(
            chord=chord,
            style=style,
            root_octave=root_octave,
            add_extensions=add_extensions,
        )
        
        if not notes:
            raise HTTPException(status_code=400, detail=f"Could not generate voicing for {chord}")
        
        # Convert to VoicingNote format
        # Split by pitch: lower half = left hand, upper half = right hand
        pitches = [n.pitch for n in notes]
        mid_pitch = sum(pitches) / len(pitches) if pitches else 60
        
        voicing_notes = []
        for note in notes:
            hand = "left" if note.pitch < mid_pitch else "right"
            voicing_notes.append(VoicingNote(
                pitch=note.pitch,
                hand=hand,
                finger=None,  # TODO: Add fingering suggestions
            ))
        
        # Calculate intervals
        sorted_pitches = sorted(pitches)
        intervals = []
        for i in range(1, len(sorted_pitches)):
            intervals.append(sorted_pitches[i] - sorted_pitches[i-1])
        
        # Width and complexity
        width = max(pitches) - min(pitches) if pitches else 0
        complexity = min(1.0, width / 24 * 0.5 + len(notes) / 8 * 0.5)
        
        # Hand span (approximate: each semitone ≈ 0.7 inches on piano)
        hand_span = width * 0.7 / 12  # Normalize to inches
        
        # Determine chord tones present
        from app.services.gpu_midi_generator import GPUMIDIGenerator as gen
        root_pc = gen._parse_chord(generator, chord)[0]
        has_root = any(p % 12 == root_pc for p in pitches)
        has_third = any(p % 12 == (root_pc + 4) % 12 or p % 12 == (root_pc + 3) % 12 for p in pitches)
        has_seventh = any(p % 12 == (root_pc + 10) % 12 or p % 12 == (root_pc + 11) % 12 for p in pitches)
        
        # Detect extensions
        extensions = []
        if any(p % 12 == (root_pc + 14) % 12 for p in pitches):
            extensions.append("9")
        if any(p % 12 == (root_pc + 17) % 12 for p in pitches):
            extensions.append("11")
        if any(p % 12 == (root_pc + 21) % 12 for p in pitches):
            extensions.append("13")
        
        return VoicingResponse(
            chord=chord,
            voicing_type=style,
            notes=voicing_notes,
            intervals=intervals,
            width_semitones=width,
            complexity_score=complexity,
            hand_span_inches=hand_span,
            has_root=has_root,
            has_third=has_third,
            has_seventh=has_seventh,
            extensions=extensions,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=VoicingResponse)
async def generate_voicing(request: VoicingGenerationRequest):
    """
    Generate a chord voicing with specified parameters.
    
    Same as GET but allows more control via request body.
    """
    return await get_voicing(
        chord=request.chord,
        style=request.style,
        root_octave=request.root_octave,
        add_extensions=request.add_extensions,
    )


@router.get("/styles")
async def list_voicing_styles():
    """
    List available voicing styles.
    """
    return {
        "styles": [
            {"name": "closed", "description": "All notes within an octave"},
            {"name": "open", "description": "Spread voicing with wider intervals"},
            {"name": "drop2", "description": "Second note dropped an octave"},
            {"name": "shell", "description": "Root, 3rd, 7th only"},
        ]
    }
