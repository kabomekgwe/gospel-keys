"""Export endpoints for MusicXML and quantized MIDI"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.database.session import get_db
from app.database.models import Song
from app.core.config import settings
from app.pipeline.notation_export import export_to_musicxml, export_with_quantization

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/songs/{song_id}/musicxml")
async def export_song_to_musicxml(
    song_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Export song as MusicXML for notation software (MuseScore, Finale, Sibelius)
    
    Returns a downloadable .musicxml file
    """
    # Get song
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Check if MIDI exists
    midi_path = Path(song.midi_file_path) if song.midi_file_path else None
    if not midi_path or not midi_path.exists():
        raise HTTPException(
            status_code=404,
            detail="MIDI file not found. Song may not have been transcribed yet."
        )
    
    # Output path
    output_dir = settings.output_dir / song_id
    musicxml_path = output_dir / "notation.musicxml"
    
    # Export (cache result)
    if not musicxml_path.exists():
        await export_to_musicxml(
            midi_path,
            musicxml_path,
            song_metadata={
                'title': song.title,
                'artist': song.artist
            }
        )
    
    # Return file
    return FileResponse(
        musicxml_path,
        media_type="application/vnd.recordare.musicxml+xml",
        filename=f"{song.title or 'song'}.musicxml"
    )


@router.post("/songs/{song_id}/midi")
async def export_quantized_midi(
    song_id: str,
    quantize: str = Query("16th", regex="^(quarter|8th|16th|32nd)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export song as quantized MIDI for cleaner notation
    
    Quantization options:
    - quarter: Quarter note grid
    - 8th: Eighth note grid  
    - 16th: Sixteenth note grid (default)
    - 32nd: Thirty-second note grid
    
    Returns a downloadable .mid file
    """
    # Get song
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Check if MIDI exists
    midi_path = Path(song.midi_file_path) if song.midi_file_path else None
    if not midi_path or not midi_path.exists():
        raise HTTPException(
            status_code=404,
            detail="MIDI file not found. Song may not have been transcribed yet."
        )
    
    # Output path
    output_dir = settings.output_dir / song_id
    quantized_midi_path = output_dir / f"quantized_{quantize}.mid"
    
    # Export (cache result)
    if not quantized_midi_path.exists():
        await export_with_quantization(
            midi_path,
            quantized_midi_path,
            quantize_to=quantize,
            tempo_bpm=song.tempo
        )
    
    # Return file
    return FileResponse(
        quantized_midi_path,
        media_type="audio/midi",
        filename=f"{song.title or 'song'}_quantized_{quantize}.mid"
    )
