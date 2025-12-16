"""Neo-Soul Piano Generation API Routes - Gemini + Rule-Based + Theory Integration"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.schemas.neosoul import (
    GenerateNeosoulRequest,
    GenerateNeosoulResponse,
    NeosoulGeneratorStatus,
)
from app.services.neosoul_generator import neosoul_generator_service
from app.neosoul.theory_integration import neosoul_theory


router = APIRouter(prefix="/neosoul", tags=["Neo-Soul Piano Generation"])


@router.get("/status", response_model=NeosoulGeneratorStatus)
async def get_neosoul_generator_status():
    """
    Get status of neo-soul generation system.

    Returns information about:
    - Gemini API availability
    - Rule-based arranger availability
    - Production readiness
    """
    return neosoul_generator_service.get_status()


@router.post("/generate", response_model=GenerateNeosoulResponse)
async def generate_neosoul_arrangement(request: GenerateNeosoulRequest):
    """
    Generate complete neo-soul piano arrangement from natural language description.

    Pipeline:
    1. Gemini API generates chord progression from description
    2. NeosoulArranger creates MIDI (rule-based with authentic neo-soul patterns)
    3. Export to MIDI file with metadata

    Example requests:

    ```json
    {
      "description": "D'Angelo style smooth groove in Dm with extended voicings",
      "tempo": 85,
      "num_bars": 16,
      "application": "smooth"
    }
    ```

    ```json
    {
      "description": "Erykah Badu style uptempo in Eb with chromatic fills",
      "key": "Eb",
      "tempo": 95,
      "num_bars": 16,
      "application": "uptempo"
    }
    ```

    ```json
    {
      "description": "Robert Glasper contemporary with sus chords and 16th grooves",
      "key": "Am",
      "tempo": 100,
      "num_bars": 32,
      "application": "uptempo"
    }
    ```

    Args:
        request: Generation parameters

    Returns:
        GenerateNeosoulResponse with:
        - MIDI file (base64 and file path)
        - Chord progression analysis
        - Arrangement metadata
        - Notes preview for visualization

    Neo-Soul Applications:
    - smooth: Slow tempo (70-90 BPM), sustained extended voicings, laid-back timing
    - uptempo: Medium tempo (90-110 BPM), syncopated 16th-note grooves, rhythmic activity
    """
    try:
        return await neosoul_generator_service.generate_neosoul_arrangement(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Neo-soul generation failed: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_neosoul_midi(filename: str):
    """
    Download a generated neo-soul MIDI file.

    Args:
        filename: MIDI filename (e.g., "neosoul_Dm_85bpm_1234567890.mid")

    Returns:
        FileResponse with MIDI file
    """
    from pathlib import Path
    from app.core.config import settings

    file_path = settings.OUTPUTS_DIR / "neosoul_generated" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found")

    return FileResponse(
        path=file_path,
        media_type="audio/midi",
        filename=filename
    )


# ========================================
# THEORY-POWERED NEO-SOUL ENDPOINTS (Phase 5)
# ========================================

class NeosoulProgressionRequest(BaseModel):
    """Request for theory-enhanced neo-soul progression."""
    key: str = "C"
    style: str = "classic"  # classic, modern, jazzy
    use_negative_harmony: bool = False
    modal_interchange: bool = True


class NeosoulVoicingRequest(BaseModel):
    """Request for neo-soul voicing generation."""
    chord: List[str]  # [root, quality]
    register: str = "mid"  # low, mid, high


@router.post("/theory/progression")
async def generate_neosoul_progression(request: NeosoulProgressionRequest):
    """
    Generate neo-soul progression with advanced theory techniques.

    Styles:
    - **classic**: Imaj9 - vim11 - iim9 - V13 (traditional neo-soul)
    - **modern**: Imaj9 - bVIImaj7 - IVmaj9 - iim11 (contemporary sound)
    - **jazzy**: iiim7 - VI7b9 - iim7 - V7#5 (jazz-influenced)

    Theory techniques:
    - **Extended chords**: Rich maj9, m11, 13 voicings throughout
    - **Modal interchange**: Borrowed chords from parallel minor (bVII)
    - **Negative harmony**: Alternative progressions for unexpected color
    - **Smooth voice leading**: Sophisticated chord transitions

    Example request:
    ```json
    {
      "key": "Eb",
      "style": "modern",
      "use_negative_harmony": true,
      "modal_interchange": true
    }
    ```

    Returns:
    - Neo-soul progression with extended chords
    - Theory techniques applied
    - Harmonic characteristics
    """
    try:
        result = neosoul_theory.generate_neosoul_progression_with_theory(
            key=request.key,
            style=request.style,
            use_negative_harmony=request.use_negative_harmony,
            modal_interchange=request.modal_interchange
        )

        return {
            "success": True,
            "progression": [list(chord) for chord in result["progression"]],
            "key": result["key"],
            "style": result["style"],
            "techniques": result["techniques"],
            "characteristics": result["characteristics"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Neo-soul progression generation failed: {str(e)}"
        )


@router.post("/theory/voicing")
async def generate_neosoul_voicing(request: NeosoulVoicingRequest):
    """
    Generate characteristic neo-soul voicing for a chord.

    Neo-soul voicing characteristics:
    - **Rootless**: Bass plays root, voicing omits it
    - **Extensions in upper voices**: 9th, 11th, 13th on top
    - **Spread voicings**: Not too close, airy sound
    - **Cluster chords**: For modern neo-soul color

    Voicing types:
    - **maj9**: Rootless maj9 (3, 5, 7, 9) - classic neo-soul
    - **m11**: Minor 11 (3, 7, 9, 11) - lush and sophisticated
    - **13**: Dominant 13 (3, 7, 9, 13) - jazzy resolution

    Example request:
    ```json
    {
      "chord": ["Eb", "maj9"],
      "register": "mid"
    }
    ```

    Returns:
    - MIDI note numbers for voicing
    - Voicing style explanation
    - Extensions identified
    - Rootless status
    """
    try:
        # Convert list to tuple
        chord = (request.chord[0], request.chord[1])

        result = neosoul_theory.generate_neosoul_voicing(
            chord=chord,
            register=request.register
        )

        return {
            "success": True,
            "chord": request.chord,
            "voicing": result["voicing"],
            "style": result["style"],
            "register": result["register"],
            "is_rootless": result["is_rootless"],
            "extensions": result["extensions"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Neo-soul voicing generation failed: {str(e)}"
        )
