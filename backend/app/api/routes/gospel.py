"""Gospel Piano Generation API Routes - Gemini + MLX Hybrid"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.gospel import (
    GenerateGospelRequest,
    GenerateGospelResponse,
    GospelGeneratorStatus,
)
from app.services.gospel_generator import gospel_generator_service


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
