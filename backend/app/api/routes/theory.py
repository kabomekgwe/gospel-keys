"""Theory API Routes - Neo-Riemannian Transformations & Voice Leading Optimization"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.theory.voice_leading_neo_riemannian import (
    apply_parallel_transform,
    apply_leading_tone_transform,
    apply_relative_transform,
    get_plr_transformation_sequence,
    get_tonnetz_path,
    generate_tonnetz_neighbors,
    get_hexatonic_pole,
)
from app.theory.voice_leading_optimization import (
    optimize_with_constraints,
    optimize_with_dynamic_programming,
    multi_objective_optimization,
)
from app.theory.chord_parser import parse_chord_symbol


router = APIRouter(prefix="/theory", tags=["Music Theory"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class TransformRequest(BaseModel):
    """Request for Neo-Riemannian transformation"""
    chord: str = Field(..., description="Chord symbol (e.g., 'C', 'Fmaj', 'Am')")
    transformation: str = Field(..., description="Transformation type: 'P', 'L', or 'R'")
    octave: int = Field(default=4, description="Base octave for voicing")


class TransformResponse(BaseModel):
    """Response for Neo-Riemannian transformation"""
    original_chord: str
    transformation: str
    new_root: str
    new_quality: str
    new_chord: str
    voicing: List[str]
    metadata: dict


class TonnetzPathRequest(BaseModel):
    """Request for Tonnetz path finding"""
    chord1: str = Field(..., description="Starting chord")
    chord2: str = Field(..., description="Target chord")
    max_steps: int = Field(default=6, description="Maximum path length")


class TonnetzPathResponse(BaseModel):
    """Response for Tonnetz path"""
    chord1: str
    chord2: str
    path: Optional[List[str]]
    distance: int
    path_description: str


class VoiceLeadingRequest(BaseModel):
    """Request for voice leading optimization"""
    progression: List[str] = Field(..., description="List of chord symbols")
    constraints: dict = Field(default_factory=dict, description="Optimization constraints")
    octave: int = Field(default=4, description="Base octave")


class VoiceLeadingResponse(BaseModel):
    """Response for optimized voice leading"""
    progression: List[str]
    voicings: List[List[int]]
    total_movement: float
    method: str


class NeighborsRequest(BaseModel):
    """Request for Tonnetz neighbors"""
    chord: str = Field(..., description="Chord symbol")
    octave: int = Field(default=4, description="Base octave")


class NeighborsResponse(BaseModel):
    """Response for Tonnetz neighbors"""
    original: str
    neighbors: dict


class HexatonicPoleRequest(BaseModel):
    """Request for hexatonic pole"""
    chord: str = Field(..., description="Chord symbol")
    octave: int = Field(default=4, description="Base octave")


class HexatonicPoleResponse(BaseModel):
    """Response for hexatonic pole"""
    original: str
    pole_chord: str
    pole_root: str
    pole_quality: str
    voicing: List[str]
    path: List[str]
    metadata: dict


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/transform", response_model=TransformResponse)
async def apply_transformation(request: TransformRequest):
    """
    Apply a Neo-Riemannian transformation (P, L, or R) to a chord.
    
    - **P (Parallel)**: Major ↔ Minor (moves 3rd by semitone)
    - **L (Leading-tone)**: Moves root/third by semitone
    - **R (Relative)**: Major ↔ relative minor
    """
    try:
        # Parse chord
        parsed = parse_chord_symbol(request.chord)
        root = parsed.get('root', request.chord[0])
        quality = parsed.get('quality', '')
        
        # Select transformation function
        transform_funcs = {
            'P': apply_parallel_transform,
            'L': apply_leading_tone_transform,
            'R': apply_relative_transform,
        }
        
        if request.transformation.upper() not in transform_funcs:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transformation. Use 'P', 'L', or 'R'"
            )
        
        transform_func = transform_funcs[request.transformation.upper()]
        new_root, new_quality, voicing, metadata = transform_func(
            root, quality, request.octave
        )
        
        return TransformResponse(
            original_chord=request.chord,
            transformation=request.transformation.upper(),
            new_root=new_root,
            new_quality=new_quality,
            new_chord=f"{new_root}{new_quality}",
            voicing=voicing,
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")


@router.post("/tonnetz-path", response_model=TonnetzPathResponse)
async def find_tonnetz_path(request: TonnetzPathRequest):
    """
    Find the shortest PLR transformation path between two chords on the Tonnetz lattice.
    """
    try:
        # Parse chords
        parsed1 = parse_chord_symbol(request.chord1)
        parsed2 = parse_chord_symbol(request.chord2)
        
        root1 = parsed1.get('root', request.chord1[0])
        quality1 = parsed1.get('quality', '')
        root2 = parsed2.get('root', request.chord2[0])
        quality2 = parsed2.get('quality', '')
        
        # Find path
        path = get_tonnetz_path(
            root1, quality1,
            root2, quality2,
            max_steps=request.max_steps
        )
        
        distance = len(path) if path else -1
        
        # Build description
        if path:
            path_str = ' → '.join(path)
            description = f"Transform via: {path_str}"
        else:
            description = f"No path found within {request.max_steps} steps"
        
        return TonnetzPathResponse(
            chord1=request.chord1,
            chord2=request.chord2,
            path=path,
            distance=distance,
            path_description=description
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Path finding failed: {str(e)}")


@router.post("/optimize-voice-leading", response_model=VoiceLeadingResponse)
async def optimize_voice_leading(request: VoiceLeadingRequest):
    """
    Optimize voice leading for a chord progression using CSP (Constraint Satisfaction Problem).
    
    Available constraints:
    - max_movement: Maximum semitones per voice (default: 12)
    - avoid_parallel_fifths: Boolean (default: True)
    - avoid_parallel_octaves: Boolean (default: True)
    - min_pitch: Minimum MIDI note (default: 48)
    - max_pitch: Maximum MIDI note (default: 84)
    """
    try:
        # Parse progression
        parsed_progression = []
        for chord_str in request.progression:
            parsed = parse_chord_symbol(chord_str)
            root = parsed.get('root', chord_str[0])
            quality = parsed.get('quality', '')
            parsed_progression.append((root, quality))
        
        # Run CSP optimization
        voicings = optimize_with_constraints(
            parsed_progression,
            request.constraints,
            octave=request.octave
        )
        
        # Calculate total movement
        total_movement = 0.0
        for i in range(len(voicings) - 1):
            for note1 in voicings[i]:
                min_dist = min(abs(note2 - note1) for note2 in voicings[i + 1])
                total_movement += min_dist
        
        return VoiceLeadingResponse(
            progression=request.progression,
            voicings=voicings,
            total_movement=total_movement,
            method="CSP (Constraint Satisfaction Problem)"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/neighbors", response_model=NeighborsResponse)
async def get_neighbors(request: NeighborsRequest):
    """
    Get all Tonnetz neighbors (one PLR transformation away) for a chord.
    """
    try:
        parsed = parse_chord_symbol(request.chord)
        root = parsed.get('root', request.chord[0])
        quality = parsed.get('quality', '')
        
        neighbors = generate_tonnetz_neighbors(root, quality, request.octave)
        
        # Format neighbors for response
        formatted = {}
        for transform, (new_root, new_quality, voicing) in neighbors.items():
            formatted[transform] = {
                'chord': f"{new_root}{new_quality}",
                'voicing': voicing
            }
        
        return NeighborsResponse(
            original=request.chord,
            neighbors=formatted
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get neighbors: {str(e)}")


@router.post("/hexatonic-pole", response_model=HexatonicPoleResponse)
async def get_hexatonic_pole_endpoint(request: HexatonicPoleRequest):
    """
    Get the hexatonic pole (maximally contrasting chord via two PLR transformations).
    """
    try:
        parsed = parse_chord_symbol(request.chord)
        root = parsed.get('root', request.chord[0])
        quality = parsed.get('quality', '')
        
        pole_root, pole_quality, voicing, metadata = get_hexatonic_pole(
            root, quality, request.octave
        )
        
        return HexatonicPoleResponse(
            original=request.chord,
            pole_chord=f"{pole_root}{pole_quality}",
            pole_root=pole_root,
            pole_quality=pole_quality,
            voicing=voicing,
            path=metadata.get('path', []),
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hexatonic pole: {str(e)}")


@router.post("/sequence")
async def apply_sequence(
    chord: str,
    sequence: str,
    octave: int = 4
):
    """
    Apply a sequence of PLR transformations (e.g., "PRL", "LPLR").
    """
    try:
        parsed = parse_chord_symbol(chord)
        root = parsed.get('root', chord[0])
        quality = parsed.get('quality', '')
        
        results = get_plr_transformation_sequence(
            root, quality, sequence, octave
        )
        
        formatted_results = []
        for new_root, new_quality, voicing, metadata in results:
            formatted_results.append({
                'chord': f"{new_root}{new_quality}",
                'voicing': voicing,
                'metadata': metadata
            })
        
        return {
            'original': chord,
            'sequence': sequence,
            'results': formatted_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sequence failed: {str(e)}")
