"""Gospel Piano Generation API Routes - Gemini + MLX Hybrid + Theory Integration"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.schemas.gospel import (
    GenerateGospelRequest,
    GenerateGospelResponse,
    GospelGeneratorStatus,
)
from app.services.gospel_generator import gospel_generator_service
from app.gospel.theory_integration import gospel_theory


router = APIRouter(prefix="/gospel", tags=["Gospel Piano Generation"])


@router.get("/status", response_model=GospelGeneratorStatus)
async def get_gospel_generator_status():
    """
    Get status of gospel generation system.

    Returns information about:
    - MLX availability and training status
    - Gemini API availability
    - Recommended AI percentage
    - Dataset size
    - Production readiness
    """
    return gospel_generator_service.get_status()


@router.post("/generate", response_model=GenerateGospelResponse)
async def generate_gospel_arrangement(request: GenerateGospelRequest):
    """
    Generate complete gospel piano arrangement from natural language description.

    Pipeline:
    1. Gemini API generates chord progression from description
    2. HybridGospelArranger creates MIDI (MLX AI or rules-based)
    3. Export to MIDI file with metadata

    Example requests:

    ```json
    {
      "description": "Kirk Franklin style uptempo in C major",
      "tempo": 138,
      "num_bars": 16,
      "application": "uptempo",
      "ai_percentage": 0.0
    }
    ```

    ```json
    {
      "description": "Slow worship ballad with rich harmonies",
      "key": "Bb",
      "tempo": 68,
      "num_bars": 8,
      "application": "worship",
      "ai_percentage": 0.5
    }
    ```

    Args:
        request: Generation parameters

    Returns:
        GenerateGospelResponse with:
        - MIDI file (base64 and file path)
        - Chord progression analysis
        - Arrangement metadata
        - Notes preview for visualization

    Note: Set ai_percentage=0.0 until MLX model is trained.
    Check /gospel/status for recommended AI percentage.
    """
    try:
        return await gospel_generator_service.generate_gospel_arrangement(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gospel generation failed: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_gospel_midi(filename: str):
    """
    Download a generated gospel MIDI file.

    Args:
        filename: MIDI filename (e.g., "gospel_C_120bpm_1234567890.mid")

    Returns:
        FileResponse with MIDI file
    """
    from pathlib import Path
    from app.core.config import settings

    file_path = settings.OUTPUTS_DIR / "gospel_generated" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found")

    return FileResponse(
        path=file_path,
        media_type="audio/midi",
        filename=filename
    )


# ========================================
# THEORY-POWERED GOSPEL ENDPOINTS (Phase 5)
# ========================================

class TheoryProgressionRequest(BaseModel):
    """Request for theory-enhanced gospel progression."""
    base_progression: List[List[str]]  # List of [root, quality] pairs
    key: str = "C"
    complexity: str = "moderate"  # simple, moderate, advanced
    techniques: Optional[List[str]] = None  # modal_interchange, chromatic_approach, backdoor, negative_harmony


class VoicingRequest(BaseModel):
    """Request for theory-optimized gospel voicings."""
    progression: List[List[str]]  # List of [root, quality] pairs
    voicing_style: str = "contemporary"  # traditional, contemporary, jazz_influenced


@router.post("/theory/progression")
async def generate_theory_progression(request: TheoryProgressionRequest):
    """
    Generate gospel progression enhanced with advanced music theory.

    Applies gospel-specific theory techniques:
    - **Modal Interchange**: Borrowed chords from parallel minor for emotional color
    - **Chromatic Approach**: Half-step approach chords (common in gospel)
    - **Backdoor Progression**: bVII7 → I for smooth resolution
    - **Negative Harmony**: Alternative harmonic endings

    Example request:
    ```json
    {
      "base_progression": [["C", "maj7"], ["Am", "m7"], ["Dm", "m7"], ["G", "7"]],
      "key": "C",
      "complexity": "moderate",
      "techniques": ["modal_interchange", "chromatic_approach"]
    }
    ```

    Returns:
    - Enhanced progression with theory techniques applied
    - Explanation of each technique
    - Gospel-specific context
    """
    try:
        # Convert list format to tuple format
        base = [(chord[0], chord[1]) for chord in request.base_progression]

        result = gospel_theory.generate_gospel_progression_with_theory(
            base_progression=base,
            key=request.key,
            complexity=request.complexity,
            techniques=request.techniques
        )

        return {
            "success": True,
            "original_progression": request.base_progression,
            "enhanced_progression": [list(chord) for chord in result["enhanced_progression"]],
            "techniques_applied": result["techniques_applied"],
            "key": result["key"],
            "complexity": result["complexity"],
            "style": result["style"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Theory progression generation failed: {str(e)}"
        )


@router.post("/theory/voicing")
async def generate_theory_voicing(request: VoicingRequest):
    """
    Generate gospel voicings optimized for smooth voice leading.

    Voicing styles:
    - **traditional**: Root position, close voicings (beginner-friendly)
    - **contemporary**: Rootless, spread voicings with extensions (modern gospel)
    - **jazz_influenced**: Drop-2, drop-3 voicings (advanced)

    Returns detailed voice leading analysis:
    - Total voice movement (semitones)
    - Common tones between chords
    - Smoothness rating

    Example request:
    ```json
    {
      "progression": [["C", "maj9"], ["G", "7"], ["F", "maj9"]],
      "voicing_style": "contemporary"
    }
    ```
    """
    try:
        # Convert list format to tuple format
        progression = [(chord[0], chord[1]) for chord in request.progression]

        result = gospel_theory.generate_gospel_voicing_with_voice_leading(
            progression=progression,
            voicing_style=request.voicing_style
        )

        return {
            "success": True,
            "voicings": [
                {
                    "chord": list(v["chord"]),
                    "voicing": v["voicing"],
                    "style": v["style"]
                }
                for v in result["voicings"]
            ],
            "voice_leading_analysis": result["voice_leading_analysis"],
            "style": result["style"],
            "avg_smoothness": result["avg_smoothness"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Theory voicing generation failed: {str(e)}"
        )
