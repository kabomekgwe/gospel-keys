"""R&B Piano Generation API Routes"""

from fastapi import APIRouter, HTTPException
from app.schemas.rnb import (
    GenerateRnBRequest,
    GenerateRnBResponse,
    RnBGeneratorStatus,
)
from app.services.rnb_generator import rnb_generator_service


router = APIRouter(prefix="/rnb", tags=["R&B Piano Generation"])


@router.get("/status", response_model=RnBGeneratorStatus)
async def get_rnb_generator_status():
    """
    Get status of R&B generation system.

    Returns information about:
    - Gemini API availability
    - Rule-based arranger availability
    - Production readiness
    """
    return rnb_generator_service.get_status()


@router.post("/generate", response_model=GenerateRnBResponse)
async def generate_rnb_arrangement(request: GenerateRnBRequest):
    """
    Generate complete R&B piano arrangement from natural language description.

    Pipeline:
    1. Gemini API generates chord progression from description (or use fallback)
    2. RnBArranger creates MIDI with authentic R&B patterns
    3. Export to MIDI file with metadata

    Example requests:

    ```json
    {
      "description": "Smooth neo-soul ballad in F major with extended chords",
      "tempo": 70,
      "num_bars": 8,
      "application": "ballad"
    }
    ```

    ```json
    {
      "description": "Mid-tempo R&B groove in D with syncopation",
      "key": "D",
      "tempo": 88,
      "num_bars": 16,
      "application": "groove"
    }
    ```

    Applications:
    - `ballad`: Slow soul ballad (60-75 BPM), lush voicings
    - `groove`: Mid-tempo R&B groove (80-95 BPM), syncopated
    - `uptempo`: Upbeat contemporary (95-110 BPM), 16th notes
    """
    try:
        response = await rnb_generator_service.generate_arrangement(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
