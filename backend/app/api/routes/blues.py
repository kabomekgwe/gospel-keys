"""Blues Piano Generation API Routes + Theory Integration"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel

from app.schemas.blues import (
    GenerateBluesRequest,
    GenerateBluesResponse,
    BluesGeneratorStatus
)
from app.services.blues_generator import blues_generator_service
from app.core.config import settings
from app.blues.theory_integration import blues_theory

router = APIRouter(prefix="/blues", tags=["blues"])


@router.get("/status", response_model=BluesGeneratorStatus)
async def get_blues_status():
    """Get blues generator system status"""
    return blues_generator_service.get_status()


@router.post("/generate", response_model=GenerateBluesResponse)
async def generate_blues(request: GenerateBluesRequest):
    """Generate blues piano arrangement from description

    Examples:
    - Slow blues in E with expressive bends
    - Classic Chicago shuffle in A
    - Fast uptempo blues in C
    """
    return await blues_generator_service.generate_blues_arrangement(request)


@router.get("/download/{filename}")
async def download_blues_midi(filename: str):
    """Download generated blues MIDI file"""
    file_path = settings.OUTPUTS_DIR / "blues_generated" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")

    return FileResponse(
        path=str(file_path),
        media_type="audio/midi",
        filename=filename
    )


# ========================================
# THEORY-POWERED BLUES ENDPOINTS (Phase 5)
# ========================================

class BluesProgressionRequest(BaseModel):
    """Request for theory-enhanced blues progression."""
    key: str = "C"
    style: str = "quick_four"  # basic, quick_four
    sophistication: str = "moderate"  # simple, moderate, jazz_blues


@router.post("/theory/progression")
async def generate_blues_progression(request: BluesProgressionRequest):
    """
    Generate 12-bar blues progression with theory enhancements.

    Styles:
    - **basic**: Standard 12-bar (I-I-I-I-IV-IV-I-I-V-IV-I-V)
    - **quick_four**: Quick IV change in bar 2 (I-IV-I-I-IV-IV-I-I-V-IV-I-V)

    Sophistication:
    - **simple**: Basic dominant 7th chords throughout
    - **moderate**: Add diminished passing chords
    - **jazz_blues**: Full jazz blues treatment with ii-V's and substitutions

    Example request:
    ```json
    {
      "key": "A",
      "style": "quick_four",
      "sophistication": "moderate"
    }
    ```

    Returns:
    - 12-bar blues progression
    - Blues characteristics analysis
    - Dominant 7th density metrics
    """
    try:
        result = blues_theory.generate_blues_progression_with_theory(
            key=request.key,
            style=request.style,
            sophistication=request.sophistication
        )

        return {
            "success": True,
            "progression": [list(chord) for chord in result["progression"]],
            "key": result["key"],
            "style": result["style"],
            "sophistication": result["sophistication"],
            "form": result["form"],
            "characteristics": result["characteristics"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Blues progression generation failed: {str(e)}"
        )


@router.get("/theory/blues-scale/{key}")
async def get_blues_scale(key: str):
    """
    Get the blues scale for a given key.

    Blues scale: 1, b3, 4, b5 (blue note), 5, b7, 1

    The blues scale is the minor pentatonic scale plus the blue note (b5).
    It works over all chords in a blues progression.

    Example:
    - C blues scale: C, Eb, F, Gb (blue note), G, Bb, C

    Returns:
    - Scale degrees
    - Blue notes (b3, b5, b7)
    - Usage guidance
    """
    try:
        result = blues_theory.get_blues_scale(key=key)

        return {
            "success": True,
            "key": result["key"],
            "scale_degrees": result["scale_degrees"],
            "blue_notes": result["blue_notes"],
            "description": result["description"],
            "usage": result["usage"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Blues scale retrieval failed: {str(e)}"
        )
