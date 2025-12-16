"""Latin/Salsa Piano Generation API Routes"""

from fastapi import APIRouter, HTTPException
from app.schemas.latin import (
    GenerateLatinRequest,
    GenerateLatinResponse,
    LatinGeneratorStatus,
)
from app.services.latin_generator import latin_generator_service


router = APIRouter(prefix="/latin", tags=["Latin Piano Generation"])


@router.get("/status", response_model=LatinGeneratorStatus)
async def get_latin_generator_status():
    """
    Get status of Latin generation system.

    Returns information about:
    - Gemini API availability
    - Rule-based arranger availability
    - Production readiness
    """
    return latin_generator_service.get_status()


@router.post("/generate", response_model=GenerateLatinResponse)
async def generate_latin_arrangement(request: GenerateLatinRequest):
    """
    Generate complete Latin/Salsa piano arrangement from natural language description.

    Pipeline:
    1. Gemini API generates chord progression from description (or use fallback)
    2. LatinArranger creates MIDI with authentic Latin patterns
    3. Export to MIDI file with metadata

    Example requests:

    ```json
    {
      "description": "Upbeat salsa in C major with montuno patterns",
      "tempo": 95,
      "num_bars": 8,
      "application": "salsa"
    }
    ```

    ```json
    {
      "description": "Slow bolero ballad in Dm with Cuban harmony",
      "key": "Dm",
      "tempo": 70,
      "num_bars": 16,
      "application": "ballad"
    }
    ```

    Applications:
    - `salsa`: Classic salsa (90-100 BPM), montuno, tumbao
    - `ballad`: Slow bolero (60-80 BPM), sustained voicings
    - `uptempo`: Fast mambo (110-140 BPM), driving rhythm
    """
    try:
        response = await latin_generator_service.generate_arrangement(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
