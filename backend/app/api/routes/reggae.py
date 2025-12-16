"""Reggae Piano Generation API Routes"""

from fastapi import APIRouter, HTTPException
from app.schemas.reggae import (
    GenerateReggaeRequest,
    GenerateReggaeResponse,
    ReggaeGeneratorStatus,
)
from app.services.reggae_generator import reggae_generator_service


router = APIRouter(prefix="/reggae", tags=["Reggae Piano Generation"])


@router.get("/status", response_model=ReggaeGeneratorStatus)
async def get_reggae_generator_status():
    """
    Get status of reggae generation system.

    Returns information about:
    - Gemini API availability
    - Rule-based arranger availability
    - Production readiness
    """
    return reggae_generator_service.get_status()


@router.post("/generate", response_model=GenerateReggaeResponse)
async def generate_reggae_arrangement(request: GenerateReggaeRequest):
    """
    Generate complete reggae piano arrangement from natural language description.

    Pipeline:
    1. Gemini API generates chord progression from description (or use fallback)
    2. ReggaeArranger creates MIDI with authentic reggae patterns
    3. Export to MIDI file with metadata

    Example requests:

    ```json
    {
      "description": "Roots reggae in G major with heavy dub bass",
      "tempo": 75,
      "num_bars": 8,
      "application": "roots"
    }
    ```

    ```json
    {
      "description": "Upbeat dancehall in D with double skank pattern",
      "key": "D",
      "tempo": 100,
      "num_bars": 16,
      "application": "dancehall"
    }
    ```

    Applications:
    - `roots`: Classic roots reggae (70-80 BPM), dub bass, heavy skank
    - `dancehall`: Faster dancehall style (90-110 BPM), double skank
    - `dub`: Minimal dub reggae (60-75 BPM), sparse, heavy bass
    """
    try:
        response = await reggae_generator_service.generate_arrangement(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
