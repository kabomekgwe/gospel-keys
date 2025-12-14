"""Classical Piano Generation API Routes"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.schemas.classical import (
    GenerateClassicalRequest,
    GenerateClassicalResponse,
    ClassicalGeneratorStatus
)
from app.services.classical_generator import classical_generator_service
from app.core.config import settings

router = APIRouter(prefix="/classical", tags=["classical"])


@router.get("/status", response_model=ClassicalGeneratorStatus)
async def get_classical_status():
    """Get classical generator system status"""
    return classical_generator_service.get_status()


@router.post("/generate", response_model=GenerateClassicalResponse)
async def generate_classical(request: GenerateClassicalRequest):
    """Generate classical piano arrangement from description

    Examples:
    - Mozart-style piano sonata in C major
    - Baroque fugue in D minor with counterpoint
    - Romantic nocturne in E-flat major
    """
    return await classical_generator_service.generate_classical_arrangement(request)


@router.get("/download/{filename}")
async def download_classical_midi(filename: str):
    """Download generated classical MIDI file"""
    file_path = settings.OUTPUTS_DIR / "classical_generated" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")

    return FileResponse(
        path=str(file_path),
        media_type="audio/midi",
        filename=filename
    )
