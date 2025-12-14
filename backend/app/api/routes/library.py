"""Library management endpoints for browsing and managing songs"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database.session import get_db
from app.database.models import Song, Tag, SongTag
from app.schemas.library import SongSummary, SongDetail, SongUpdate, SongNoteResponse, SongChordResponse

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/songs", response_model=list[SongSummary])
async def list_songs(
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    search: Optional[str] = Query(None, description="Search in title or artist"),
    favorites_only: bool = Query(False, description="Show only favorites"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all songs in library with optional filtering
    
    Filters:
    - tag: Filter by tag name
    - search: Search in title or artist
    - favorites_only: Show only favorited songs
    """
    query = select(Song)
    
    # Filter by favorites
    if favorites_only:
        query = query.where(Song.favorite == True)
    
    # Search in title or artist
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Song.title.ilike(search_pattern),
                Song.artist.ilike(search_pattern)
            )
        )
    
    # Filter by tag
    if tag:
        # Join with tags
        query = query.join(Song.tags).join(SongTag.tag).where(Tag.name == tag)
    
    # Order by most recently accessed
    query = query.order_by(Song.last_accessed_at.desc().nullsfirst())
    
    # Pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    songs = result.scalars().all()
    
    # Convert to summary format
    return [
        SongSummary(
            id=song.id,
            title=song.title,
            artist=song.artist,
            duration=song.duration,
            tempo=song.tempo,
            key_signature=song.key_signature,
            favorite=song.favorite,
            created_at=song.created_at,
            last_accessed_at=song.last_accessed_at,
        )
        for song in songs
    ]


@router.get("/songs/{song_id}", response_model=SongDetail)
async def get_song(song_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get complete song details including notes, chords, and annotations
    
    Also updates last_accessed_at timestamp
    """
    song = await db.get(Song, song_id)
    
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Update last accessed timestamp
    from datetime import datetime
    song.last_accessed_at = datetime.now()
    await db.commit()
    
    return SongDetail(
        id=song.id,
        title=song.title,
        artist=song.artist,
        source_url=song.source_url,
        source_file=song.source_file,
        duration=song.duration,
        tempo=song.tempo,
        key_signature=song.key_signature,
        time_signature=song.time_signature,
        difficulty=song.difficulty,
        midi_file_path=song.midi_file_path,
        note_count=len(song.notes),
        chord_count=len(song.chords),
        annotation_count=len(song.annotations),
        snippet_count=len(song.snippets),
        unique_notes_count=len(set(note.pitch % 12 for note in song.notes)),
        favorite=song.favorite,
        created_at=song.created_at,
        last_accessed_at=song.last_accessed_at,
    )


@router.put("/songs/{song_id}")
async def update_song(
    song_id: str,
    data: SongUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update song metadata (title, artist, favorite, etc.)"""
    song = await db.get(Song, song_id)
    
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Update fields
    if data.title is not None:
        song.title = data.title
    if data.artist is not None:
        song.artist = data.artist
    if data.difficulty is not None:
        song.difficulty = data.difficulty
    if data.favorite is not None:
        song.favorite = data.favorite
    
    await db.commit()
    
    return {"message": "Song updated successfully"}


@router.delete("/songs/{song_id}", status_code=204)
async def delete_song(song_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete song and all related data (notes, chords, annotations, snippets)
    
    Cascade delete will handle all relationships
    """
    song = await db.get(Song, song_id)
    
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    await db.delete(song)
    await db.commit()
    
    # Also clean up files if they exist
    from pathlib import Path
    from app.core.config import settings
    import shutil
    
    output_dir = settings.output_dir / song_id
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    return None


@router.post("/songs/{song_id}/tags")
async def add_tags(
    song_id: str,
    tags: list[str],
    db: AsyncSession = Depends(get_db)
):
    """Add tags to a song (creates tags if they don't exist)"""
    song = await db.get(Song, song_id)
    
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    for tag_name in tags:
        # Get or create tag
        tag_query = select(Tag).where(Tag.name == tag_name)
        result = await db.execute(tag_query)
        tag = result.scalar_one_or_none()
        
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            await db.flush()  # Get tag ID
        
        # Check if relationship already exists
        existing = await db.execute(
            select(SongTag).where(
                SongTag.song_id == song_id,
                SongTag.tag_id == tag.id
            )
        )
        
        if not existing.scalar_one_or_none():
            song_tag = SongTag(song_id=song_id, tag_id=tag.id)
            db.add(song_tag)
    
    await db.commit()
    
    return {"message": f"Added {len(tags)} tags to song"}


@router.get("/songs/{song_id}/notation/svg")
async def get_notation_svg(song_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get Verovio-rendered SVG notation for the song
    
    Renders the MIDI file to SVG using the backend Verovio service.
    """
    from app.services.verovio_service import verovio_service, VEROVIO_AVAILABLE
    from pathlib import Path
    
    if not VEROVIO_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Verovio notation rendering is not available on the server"
        )
        
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    midi_path = Path(song.midi_file_path) if song.midi_file_path else None
    if not midi_path or not midi_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found")
        
    # Render SVG
    svg_content = verovio_service.render_midi_to_svg(midi_path)
    
    if not svg_content:
        raise HTTPException(status_code=500, detail="Failed to render notation")
        
    return {"svg": svg_content}


@router.get("/songs/{song_id}/notes", response_model=list[SongNoteResponse])
async def get_song_notes(song_id: str, db: AsyncSession = Depends(get_db)):
    """Get all MIDI notes for a song"""
    from app.schemas.library import SongNoteResponse
    
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    # Ensure notes are loaded
    await db.refresh(song, ["notes"])
    
    return [
        SongNoteResponse(
            id=note.id,
            pitch=note.pitch,
            start_time=note.start_time,
            end_time=note.end_time,
            velocity=note.velocity
        )
        for note in song.notes
    ]


@router.get("/songs/{song_id}/chords", response_model=list[SongChordResponse])
async def get_song_chords(song_id: str, db: AsyncSession = Depends(get_db)):
    """Get all detected chords for a song"""
    from app.schemas.library import SongChordResponse
    
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    # Ensure chords are loaded
    await db.refresh(song, ["chords"])
    
    return [
        SongChordResponse(
            id=chord.id,
            time=chord.time,
            duration=chord.duration,
            chord=chord.chord,
            root=chord.root,
            quality=chord.quality,
            bass_note=chord.bass_note
        )
        for chord in song.chords
    ]
