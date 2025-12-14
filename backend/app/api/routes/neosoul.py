"""Neo-Soul Piano Generation API Routes - Gemini + Rule-Based"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.neosoul import (
    GenerateNeosoulRequest,
    GenerateNeosoulResponse,
    NeosoulGeneratorStatus,
)
from app.services.neosoul_generator import neosoul_generator_service


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
