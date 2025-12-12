"""Job management endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.transcription import TranscriptionJob, JobStatus
from app.services.transcription import TranscriptionService

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Global service instance (will be initialized in main.py)
transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get the transcription service instance"""
    if transcription_service is None:
        raise HTTPException(status_code=500, detail="Transcription service not initialized")
    return transcription_service


@router.get("", response_model=list[TranscriptionJob])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
):
    """
    List all transcription jobs with optional filtering
    """
    service = get_transcription_service()
    
    # Validate status if provided
    if status is not None:
        try:
            JobStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status: {status}. Must be one of: {[s.value for s in JobStatus]}"
            )
    
    return service.list_jobs(status=status, limit=limit, offset=offset)


@router.delete("/{job_id}", status_code=204)
async def cancel_job(job_id: str):
    """
    Cancel a running transcription job
    
    If the job is already complete or failed, this has no effect.
    """
    service = get_transcription_service()
    
    success = service.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return None


@router.delete("/{job_id}/result", status_code=204)
async def delete_job(job_id: str):
    """
    Delete a job and all associated files
    
    This removes the job from the system and cleans up uploaded/output files.
    """
    service = get_transcription_service()
    
    success = service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return None
