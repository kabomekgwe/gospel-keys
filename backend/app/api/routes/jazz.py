"""Jazz Piano Generation API Routes - Gemini + Rule-Based"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.jazz import (
    GenerateJazzRequest,
    GenerateJazzResponse,
    JazzGeneratorStatus,
)
from app.services.jazz_generator import jazz_generator_service


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
