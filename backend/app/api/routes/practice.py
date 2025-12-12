"""Practice mode endpoints for interactive learning"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.database.models import Song, PracticeSession
from app.core.config import settings
from app.pipeline.audio_effects import time_stretch_audio

router = APIRouter(prefix="/practice", tags=["practice"])


class PracticeSessionRequest(BaseModel):
    """Request to create a practice session"""
    song_id: str
    start_time: Optional[float] = Field(None, ge=0, description="Start time in seconds")
    end_time: Optional[float] = Field(None, gt=0, description="End time in seconds")
    tempo_multiplier: float = Field(1.0, gt=0.25, le=2.0, description="Tempo multiplier (0.5-2.0)")
    loop: bool = Field(False, description="Loop the section")
    duration_seconds: int = Field(0, ge=0, description="Practice duration")
    notes: Optional[str] = None


class PracticeSessionResponse(BaseModel):
    """Practice session response"""
    id: int
    song_id: str
    audio_url: str
    tempo_multiplier: float
    duration_seconds: int
    notes: Optional[str] = None
    created_at: datetime


@router.post("/session", response_model=PracticeSessionResponse, status_code=201)
async def create_practice_session(
    request: PracticeSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a practice session with optional time-stretching and sectioning
    
    This generates a time-stretched audio file if tempo_multiplier != 1.0
    and/or extracts a specific section if start_time/end_time are provided.
    """
    # Get song
    song = await db.get(Song, request.song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {request.song_id} not found")
    
    # Build audio URL
    audio_filename = "audio.wav"
    
    # Generate time-stretched/sectioned audio if needed
    if request.tempo_multiplier != 1.0 or request.start_time is not None:
        from pathlib import Path
        
        # Source audio path
        source_audio = settings.output_dir / request.song_id / "audio.wav"
        if not source_audio.exists():
            raise HTTPException(
                status_code=404,
                detail="Source audio not found. Transcription may not be complete."
            )
        
        # Generate unique filename for this tempo/section combo
        tempo_str = f"{request.tempo_multiplier:.2f}".replace(".", "_")
        start_str = f"{request.start_time:.1f}".replace(".", "_") if request.start_time else "0"
        end_str = f"{request.end_time:.1f}".replace(".", "_") if request.end_time else "end"
        
        audio_filename = f"practice_{tempo_str}_{start_str}_{end_str}.wav"
        output_audio = settings.output_dir / request.song_id / audio_filename
        
        # Generate if doesn't exist
        if not output_audio.exists():
            # Calculate inverse rate for librosa (rate > 1 speeds up)
            rate = 1.0 / request.tempo_multiplier
            
            await time_stretch_audio(
                source_audio,
                output_audio,
                rate=rate,
                start_time=request.start_time,
                end_time=request.end_time
            )
    
    # Create practice session record
    session = PracticeSession(
        song_id=request.song_id,
        duration_seconds=request.duration_seconds,
        tempo_multiplier=request.tempo_multiplier,
        notes=request.notes,
        created_at=datetime.now()
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return PracticeSessionResponse(
        id=session.id,
        song_id=session.song_id,
        audio_url=f"/files/{request.song_id}/{audio_filename}",
        tempo_multiplier=session.tempo_multiplier,
        duration_seconds=session.duration_seconds,
        notes=session.notes,
        created_at=session.created_at
    )


@router.get("/sessions", response_model=list[PracticeSessionResponse])
async def list_practice_sessions(
    song_id: Optional[str] = Query(None, description="Filter by song ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List practice session history"""
    from sqlalchemy import select
    
    query = select(PracticeSession).order_by(PracticeSession.created_at.desc())
    
    if song_id:
        query = query.where(PracticeSession.song_id == song_id)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return [
        PracticeSessionResponse(
            id=session.id,
            song_id=session.song_id,
            audio_url=f"/files/{session.song_id}/audio.wav",  # Default audio
            tempo_multiplier=session.tempo_multiplier,
            duration_seconds=session.duration_seconds,
            notes=session.notes,
            created_at=session.created_at
        )
        for session in sessions
    ]
