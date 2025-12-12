"""Transcription endpoints"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional

from app.schemas.transcription import (
    TranscribeUrlRequest,
    TranscriptionJob,
    TranscriptionResult,
    TranscriptionOptions,
)
from app.services.transcription import TranscriptionService

router = APIRouter(prefix="/transcribe", tags=["transcription"])

# Global service instance (will be initialized in main.py)
transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get the transcription service instance"""
    if transcription_service is None:
        raise HTTPException(status_code=500, detail="Transcription service not initialized")
    return transcription_service


@router.post("/url", response_model=TranscriptionJob, status_code=202)
async def transcribe_from_url(request: TranscribeUrlRequest):
    """
    Start transcription from YouTube URL
    
    Returns immediately with job ID. Poll GET /transcribe/{job_id} for status.
    """
    service = get_transcription_service()
    job_id = await service.process_url(request.url, request.options)
    return service.get_job(job_id)


@router.post("/upload", response_model=TranscriptionJob, status_code=202)
async def transcribe_from_upload(
    file: UploadFile = File(...),
    isolate_piano: bool = Form(True),
    detect_chords: bool = Form(True),
    detect_tempo: bool = Form(True),
    detect_key: bool = Form(True),
):
    """
    Start transcription from uploaded audio/video file
    
    Returns immediately with job ID. Poll GET /transcribe/{job_id} for status.
    """
    service = get_transcription_service()
    
    # Create options from form data
    options = TranscriptionOptions(
        isolate_piano=isolate_piano,
        detect_chords=detect_chords,
        detect_tempo=detect_tempo,
        detect_key=detect_key,
    )
    
    job_id = await service.process_file(file, options)
    return service.get_job(job_id)


@router.get("/{job_id}", response_model=TranscriptionJob)
async def get_job_status(job_id: str):
    """
    Get transcription job status and progress
    
    Poll this endpoint to track progress. When status is 'complete', the result field will be populated.
    """
    service = get_transcription_service()
    job = service.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return job


@router.get("/{job_id}/result", response_model=TranscriptionResult)
async def get_job_result(job_id: str):
    """
    Get complete transcription result
    
    Only available when job status is 'complete'. Returns full result with notes, chords, etc.
    """
    service = get_transcription_service()
    job = service.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job.status.value != "complete":
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not complete yet (current status: {job.status.value})"
        )
    
    if job.result is None:
        raise HTTPException(status_code=500, detail="Job marked complete but result is missing")
    
    return job.result
