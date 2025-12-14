"""Blues Piano Generation API Routes"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.schemas.blues import (
    GenerateBluesRequest,
    GenerateBluesResponse,
    BluesGeneratorStatus
)
from app.services.blues_generator import blues_generator_service
from app.core.config import settings

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
