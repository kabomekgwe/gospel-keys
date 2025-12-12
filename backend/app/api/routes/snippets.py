"""Snippets and annotations endpoints"""

from typing import Optional
from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.database.models import Song, Snippet, Annotation

router = APIRouter(tags=["snippets & annotations"])


# Snippet schemas
class SnippetCreate(BaseModel):
    """Create a new snippet"""
    label: str = Field(..., min_length=1, max_length=100)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)
    difficulty: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    notes: Optional[str] = None


class SnippetResponse(BaseModel):
    """Snippet response"""
    id: str
    song_id: str
    label: str
    start_time: float
    end_time: float
    difficulty: Optional[str] = None
    notes: Optional[str] = None
    practice_count: int
    created_at: datetime


# Annotation schemas
class AnnotationCreate(BaseModel):
    """Create a new annotation"""
    time: float = Field(..., ge=0, description="Timestamp in seconds")
    note_text: str = Field(..., min_length=1)
    type: str = Field(
        "practice_note",
        pattern="^(practice_note|theory_insight|fingering|question|other)$"
    )


class AnnotationResponse(BaseModel):
    """Annotation response"""
    id: int
    song_id: str
    time: float
    note_text: str
    type: str
    created_at: datetime


# Snippet endpoints
@router.post("/library/songs/{song_id}/snippets", response_model=SnippetResponse, status_code=201)
async def create_snippet(
    song_id: str,
    data: SnippetCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a practice snippet from a song section
    
    Snippets are extractable sections that can be practiced independently.
    """
    # Verify song exists
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Validate time range
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=400, detail="end_time must be greater than start_time")
    
    # Create snippet
    snippet = Snippet(
        id=str(uuid.uuid4()),
        song_id=song_id,
        label=data.label,
        start_time=data.start_time,
        end_time=data.end_time,
        difficulty=data.difficulty,
        notes=data.notes,
        practice_count=0,
        created_at=datetime.now()
    )
    
    db.add(snippet)
    await db.commit()
    await db.refresh(snippet)
    
    return SnippetResponse(**snippet.__dict__)


@router.get("/library/songs/{song_id}/snippets", response_model=list[SnippetResponse])
async def list_snippets(song_id: str, db: AsyncSession = Depends(get_db)):
    """List all snippets for a song"""
    query = select(Snippet).where(Snippet.song_id == song_id).order_by(Snippet.start_time)
    result = await db.execute(query)
    snippets = result.scalars().all()
    
    return [SnippetResponse(**snippet.__dict__) for snippet in snippets]


@router.get("/snippets/{snippet_id}/midi")
async def export_snippet_midi(snippet_id: str, db: AsyncSession = Depends(get_db)):
    """
    Export snippet as isolated MIDI file
    
    TODO: Generate MIDI file with only notes within snippet time range
    """
    snippet = await db.get(Snippet, snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail=f"Snippet {snippet_id} not found")
    
    # For now, return info about what would be exported
    return {
        "message": "MIDI export coming soon",
        "snippet": {
            "id": snippet.id,
            "label": snippet.label,
            "start_time": snippet.start_time,
            "end_time": snippet.end_time
        }
    }


# Annotation endpoints
@router.post("/library/songs/{song_id}/annotations", response_model=AnnotationResponse, status_code=201)
async def create_annotation(
    song_id: str,
    data: AnnotationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Add an annotation to a song at a specific timestamp
    
    Annotations are user notes/insights attached to moments in the song.
    """
    # Verify song exists
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Create annotation
    annotation = Annotation(
        song_id=song_id,
        time=data.time,
        note_text=data.note_text,
        type=data.type,
        created_at=datetime.now()
    )
    
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    
    return AnnotationResponse(**annotation.__dict__)


@router.get("/library/songs/{song_id}/annotations", response_model=list[AnnotationResponse])
async def list_annotations(song_id: str, db: AsyncSession = Depends(get_db)):
    """Get all annotations for a song ordered by timestamp"""
    query = select(Annotation).where(Annotation.song_id == song_id).order_by(Annotation.time)
    result = await db.execute(query)
    annotations = result.scalars().all()
    
    return [AnnotationResponse(**ann.__dict__) for ann in annotations]


@router.delete("/annotations/{annotation_id}", status_code=204)
async def delete_annotation(annotation_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an annotation"""
    annotation = await db.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail=f"Annotation {annotation_id} not found")
    
    await db.delete(annotation)
    await db.commit()
    
    return None
