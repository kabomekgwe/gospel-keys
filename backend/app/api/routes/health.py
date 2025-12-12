"""Health check endpoints"""

import shutil
from fastapi import APIRouter

from app.core.config import settings
from app.schemas.transcription import HealthResponse, DetailedHealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.app_name
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Detailed health check with component status"""
    checks = {
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "storage": settings.upload_dir.exists() and settings.output_dir.exists(),
    }
    
    # Overall status is healthy if all checks pass
    overall_status = "healthy" if all(checks.values()) else "degraded"
    
    return DetailedHealthResponse(
        status=overall_status,
        service=settings.app_name,
        version=settings.version,
        checks=checks
    )
