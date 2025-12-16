"""Jazz Piano Generation API Routes - Gemini + Rule-Based + Theory Integration"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.schemas.jazz import (
    GenerateJazzRequest,
    GenerateJazzResponse,
    JazzGeneratorStatus,
)
from app.services.jazz_generator import jazz_generator_service
from app.jazz.theory_integration import jazz_theory


router = APIRouter(prefix="/jazz", tags=["Jazz Piano Generation"])


@router.get("/status", response_model=JazzGeneratorStatus)
async def get_jazz_generator_status():
    """
    Get status of jazz generation system.

    Returns information about:
    - Gemini API availability
    - Rule-based arranger availability
    - Production readiness
    """
    return jazz_generator_service.get_status()


@router.post("/generate", response_model=GenerateJazzResponse)
async def generate_jazz_arrangement(request: GenerateJazzRequest):
    """
    Generate complete jazz piano arrangement from natural language description.

    Pipeline:
    1. Gemini API generates chord progression from description
    2. JazzArranger creates MIDI (rule-based with authentic jazz patterns)
    3. Export to MIDI file with metadata

    Example requests:

    ```json
    {
      "description": "Bill Evans style ballad in Cm with rootless voicings",
      "tempo": 72,
      "num_bars": 16,
      "application": "ballad"
    }
    ```

    ```json
    {
      "description": "Uptempo bebop in F with walking bass and ii-V licks",
      "key": "F",
      "tempo": 220,
      "num_bars": 32,
      "application": "uptempo"
    }
    ```

    ```json
    {
      "description": "Medium swing with rootless comping and chord melody",
      "key": "Bb",
      "tempo": 140,
      "num_bars": 16,
      "application": "standard"
    }
    ```

    Args:
        request: Generation parameters

    Returns:
        GenerateJazzResponse with:
        - MIDI file (base64 and file path)
        - Chord progression analysis
        - Arrangement metadata
        - Notes preview for visualization

    Jazz Applications:
    - ballad: Slow tempo (60-80 BPM), sustained rootless voicings, minimal improvisation
    - standard: Medium swing (120-200 BPM), walking bass, moderate improvisation
    - uptempo: Fast swing (200-300 BPM), continuous motion, heavy improvisation
    """
    try:
        return await jazz_generator_service.generate_jazz_arrangement(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Jazz generation failed: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_jazz_midi(filename: str):
    """
    Download a generated jazz MIDI file.

    Args:
        filename: MIDI filename (e.g., "jazz_C_140bpm_1234567890.mid")

    Returns:
        FileResponse with MIDI file
    """
    from pathlib import Path
    from app.core.config import settings

    file_path = settings.OUTPUTS_DIR / "jazz_generated" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found")

    return FileResponse(
        path=file_path,
        media_type="audio/midi",
        filename=filename
    )


# ========================================
# THEORY-POWERED JAZZ ENDPOINTS (Phase 5)
# ========================================

class ColtraneRequest(BaseModel):
    """Request for Coltrane changes application."""
    key: str = "C"
    complexity: int = 1  # 1-3 (number of tonal centers)


class BebopLineRequest(BaseModel):
    """Request for Barry Harris bebop line generation."""
    chord_progression: List[List[str]]  # List of [root, quality] pairs
    key: str = "C"


class TritoneSubRequest(BaseModel):
    """Request for tritone substitution application."""
    progression: List[List[str]]  # List of [root, quality] pairs
    density: str = "moderate"  # sparse, moderate, dense


class ModalAnalysisRequest(BaseModel):
    """Request for modal jazz analysis."""
    progression: List[List[str]]  # List of [root, quality] pairs
    key: str = "C"


@router.post("/theory/coltrane")
async def apply_coltrane_changes(request: ColtraneRequest):
    """
    Apply Coltrane Changes (Giant Steps pattern) to ii-V-I progression.

    Complexity levels:
    - **1**: Simple modulation through one tonal center
    - **2**: Modulation through two tonal centers
    - **3**: Full Giant Steps pattern (three tonal centers separated by major thirds)

    Example: Transforms Dm7-G7-Cmaj7 into rapid modulation pattern

    Example request:
    ```json
    {
      "key": "C",
      "complexity": 2
    }
    ```

    Returns:
    - Original and enhanced progressions
    - Tonal centers identified
    - Technique explanation
    """
    try:
        result = jazz_theory.apply_coltrane_to_ii_v_i(
            key=request.key,
            complexity=request.complexity
        )

        return {
            "success": True,
            "original": [list(chord) for chord in result["original"]],
            "enhanced": [list(chord) for chord in result["enhanced"]],
            "tonal_centers": result["tonal_centers"],
            "complexity": result["complexity"],
            "technique": result["technique"],
            "description": result["description"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Coltrane changes application failed: {str(e)}"
        )


@router.post("/theory/bebop-line")
async def generate_bebop_line(request: BebopLineRequest):
    """
    Generate bebop line using Barry Harris diminished system.

    Barry Harris approach:
    - Over major chords: Use 6th-diminished scale
    - Over dominant: Four dominant 7ths from diminished
    - Chromatic passing tones

    Example request:
    ```json
    {
      "chord_progression": [["C", "maj7"], ["G", "7"], ["F", "maj7"]],
      "key": "C"
    }
    ```

    Returns:
    - Line segments for each chord
    - Scale/approach recommendations
    - Barry Harris theory explanations
    """
    try:
        # Convert list format to tuple format
        progression = [(chord[0], chord[1]) for chord in request.chord_progression]

        result = jazz_theory.generate_bebop_line_with_diminished(
            chord_progression=progression,
            key=request.key
        )

        return {
            "success": True,
            "chord_progression": request.chord_progression,
            "line_segments": result["line_segments"],
            "key": result["key"],
            "style": result["style"],
            "theory": result["theory"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bebop line generation failed: {str(e)}"
        )


@router.post("/theory/tritone-sub")
async def apply_tritone_subs(request: TritoneSubRequest):
    """
    Apply tritone substitutions to dominant chords.

    Density levels:
    - **sparse**: Substitute only at cadences (V → I)
    - **moderate**: Substitute 50% of dominants
    - **dense**: Substitute all dominant chords

    Example request:
    ```json
    {
      "progression": [["Dm", "m7"], ["G", "7"], ["C", "maj7"]],
      "density": "moderate"
    }
    ```

    Returns:
    - Original and substituted progressions
    - Details of each substitution
    - Density metrics
    """
    try:
        # Convert list format to tuple format
        progression = [(chord[0], chord[1]) for chord in request.progression]

        result = jazz_theory.apply_tritone_substitutions(
            progression=progression,
            density=request.density
        )

        return {
            "success": True,
            "original": request.progression,
            "substituted": [list(chord) for chord in result["substituted"]],
            "substitutions": result["substitutions"],
            "density": result["density"],
            "count": result["count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tritone substitution failed: {str(e)}"
        )


@router.post("/theory/modal-analysis")
async def analyze_modal_jazz(request: ModalAnalysisRequest):
    """
    Analyze progression for modal jazz characteristics.

    Modal jazz features:
    - Static harmony (few chord changes)
    - Modal scales (Dorian, Phrygian, Lydian, etc.)
    - Pedal points
    - Chord quality emphasis over function

    Example request:
    ```json
    {
      "progression": [["Dm", "m7"], ["Dm", "m7"], ["Em", "m7"]],
      "key": "C"
    }
    ```

    Returns:
    - Modal vs functional classification
    - Recommended mode for each chord
    - Scale notes, characteristic notes, avoid notes
    - Horizontal vs vertical approach
    """
    try:
        # Convert list format to tuple format
        progression = [(chord[0], chord[1]) for chord in request.progression]

        result = jazz_theory.analyze_modal_jazz_progression(
            progression=progression,
            key=request.key
        )

        return {
            "success": True,
            "progression": request.progression,
            "is_modal": result["is_modal"],
            "style": result["style"],
            "chord_analysis": result["chord_analysis"],
            "approach": result["approach"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Modal analysis failed: {str(e)}"
        )
