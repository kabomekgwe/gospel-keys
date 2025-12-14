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


# -------------------------------------------------------------------------
# SRS / Adaptive Practice Endpoints
# -------------------------------------------------------------------------

class ReviewRequest(BaseModel):
    """Review rating submission"""
    quality: int = Field(..., ge=0, le=5, description="0=Blackout, 5=Perfect")


@router.post("/snippets/{snippet_id}/review", status_code=200)
async def review_snippet(
    snippet_id: str,
    request: ReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a practice review for a snippet.
    Updates the scheduling based on SM-2 algorithm.
    """
    from app.database.models import Snippet
    from app.services.srs_service import SRSService
    
    snippet = await db.get(Snippet, snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    # Calculate new schedule
    updates = SRSService.get_review_schedule(request.quality, snippet)
    
    # Apply updates
    for key, value in updates.items():
        setattr(snippet, key, value)
        
    # Also log a practice session implicitly
    session = PracticeSession(
        song_id=snippet.song_id,
        snippet_id=snippet.id,
        duration_seconds=0, # Unknown duration for quick review
        notes=f"SRS Review: Quality {request.quality}",
        created_at=datetime.now()
    )
    db.add(session)
    
    await db.commit()
    await db.refresh(snippet)
    
    return {
        "message": "Review recorded",
        "next_review_at": snippet.next_review_at,
        "interval_days": snippet.interval_days
    }


@router.get("/snippets/due")
async def get_due_snippets(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get snippets due for review today.
    """
    from sqlalchemy import select
    from app.database.models import Snippet
    
    now = datetime.now()
    
    query = (
        select(Snippet)
        .where(Snippet.next_review_at <= now)
        .order_by(Snippet.next_review_at.asc())  # Most overdue first
        .limit(limit)
    )
    
    result = await db.execute(query)
    snippets = result.scalars().all()
    
    # If not enough due items, fill with "new" items (never reviewed)
    if len(snippets) < limit:
        remaining = limit - len(snippets)
        new_query = (
            select(Snippet)
            .where(Snippet.next_review_at == None)
            .order_by(Snippet.created_at.desc()) # Newest first
            .limit(remaining)
        )
        new_result = await db.execute(new_query)
        new_snippets = new_result.scalars().all()
        snippets.extend(new_snippets)
        
    return snippets


# -------------------------------------------------------------------------
# Combined Hands Practice Endpoints
# -------------------------------------------------------------------------

class HandsPracticeRequest(BaseModel):
    """Request to generate hands practice material"""
    chords: list[str] = Field(..., description="List of chord symbols", min_length=1)
    key: str = Field("C", description="Key signature")
    tempo: int = Field(80, ge=40, le=200, description="Tempo in BPM")
    left_pattern: str = Field("syncopated_groove", description="Left hand pattern name")
    right_pattern: str = Field("extended_chord_voicing", description="Right hand pattern name")
    style: str = Field("neosoul", description="Musical style (neosoul, gospel, jazz)")
    active_hand: str = Field("both", description="Which hand(s) to generate: left, right, both")
    bars_per_chord: int = Field(1, ge=1, le=4, description="Bars per chord change")


class HandsPracticeResponse(BaseModel):
    """Response with generated hands practice material"""
    midi_url: str
    left_notes_count: int
    right_notes_count: int
    total_bars: int
    duration_seconds: float
    patterns_used: dict


class PatternInfo(BaseModel):
    """Information about an available pattern"""
    name: str
    difficulty: str
    characteristics: list[str]


@router.get("/patterns/{style}")
async def list_patterns(style: str = "neosoul"):
    """
    List available left and right hand patterns for a style.
    
    Returns pattern names that can be used with the hands practice endpoint.
    """
    from app.services.combined_hands_generator import combined_hands_generator
    
    patterns = combined_hands_generator.get_available_patterns(style)
    
    if not patterns:
        raise HTTPException(
            status_code=404, 
            detail=f"Unknown style: {style}. Available: neosoul, gospel, jazz"
        )
    
    return {
        "style": style,
        "left_hand_patterns": patterns.get("left", []),
        "right_hand_patterns": patterns.get("right", []),
    }


@router.post("/hands", response_model=HandsPracticeResponse, status_code=201)
async def generate_hands_practice(request: HandsPracticeRequest):
    """
    Generate combined hands practice material.
    
    Creates a MIDI file with left and right hand patterns for the given
    chord progression. Patterns can be filtered by hand (left, right, both).
    
    Example request:
    ```json
    {
        "chords": ["Dm7", "G7", "Cmaj7", "Am7"],
        "tempo": 72,
        "left_pattern": "broken_chord_arpeggio",
        "right_pattern": "extended_chord_voicing",
        "style": "neosoul"
    }
    ```
    """
    import uuid
    from app.services.combined_hands_generator import (
        combined_hands_generator,
        HandsPracticeConfig,
    )
    
    # Build config
    config = HandsPracticeConfig(
        chords=request.chords,
        key=request.key,
        tempo=request.tempo,
        left_pattern=request.left_pattern,
        right_pattern=request.right_pattern,
        style=request.style,
        active_hand=request.active_hand,
        bars_per_chord=request.bars_per_chord,
    )
    
    # Generate arrangement
    try:
        arrangement = combined_hands_generator.generate_arrangement(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Export to MIDI
    output_id = f"hands_{uuid.uuid4().hex[:8]}"
    midi_path = combined_hands_generator.arrangement_to_midi(
        arrangement, 
        output_id,
        hand_filter=request.active_hand,
    )
    
    return HandsPracticeResponse(
        midi_url=f"/files/hands/{midi_path.name}",
        left_notes_count=len(arrangement.left_hand_notes),
        right_notes_count=len(arrangement.right_hand_notes),
        total_bars=arrangement.total_bars,
        duration_seconds=arrangement.total_duration_seconds,
        patterns_used={
            "left": request.left_pattern,
            "right": request.right_pattern,
        },
    )


@router.get("/hands/demo")
async def get_hands_demo():
    """
    Get a demo hands practice with default settings.
    
    Uses a classic ii-V-I progression in neo-soul style.
    """
    import uuid
    from app.services.combined_hands_generator import (
        combined_hands_generator,
        HandsPracticeConfig,
    )
    
    config = HandsPracticeConfig(
        chords=["Dm9", "G13", "Cmaj9", "Am11"],
        key="C",
        tempo=72,
        left_pattern="syncopated_groove",
        right_pattern="extended_chord_voicing",
        style="neosoul",
        active_hand="both",
        bars_per_chord=2,
    )
    
    arrangement = combined_hands_generator.generate_arrangement(config)
    
    output_id = f"demo_{uuid.uuid4().hex[:8]}"
    midi_path = combined_hands_generator.arrangement_to_midi(arrangement, output_id)
    
    return {
        "midi_url": f"/files/hands/{midi_path.name}",
        "chords": config.chords,
        "left_notes": len(arrangement.left_hand_notes),
        "right_notes": len(arrangement.right_hand_notes),
        "duration_seconds": arrangement.total_duration_seconds,
        "message": "Demo ii-V-I progression in neo-soul style",
    }

