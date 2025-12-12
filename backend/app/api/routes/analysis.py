"""
Advanced Analysis API Routes

Endpoints for multi-genre analysis:
- Genre detection
- Jazz pattern recognition
- Pitch analysis (CREPE)
- Advanced chord voicings
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from typing import Optional, List

from app.database.session import get_db
from app.database.models import Song
from app.pipeline.genre_classifier import analyze_genre
from app.pipeline.jazz_analyzer import analyze_jazz_patterns, JAZZ_CHORD_TEMPLATES
from app.pipeline.crepe_analysis import extract_pitch_contour, detect_blue_notes, detect_vibrato, analyze_pitch_bends

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/genre")
async def analyze_song_genre(
    song_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect genre and subgenre classification
    """
    # Check if analysis already exists
    from sqlalchemy import select
    from app.database.models import GenreAnalysis
    import json
    
    existing_stmt = select(GenreAnalysis).where(GenreAnalysis.song_id == song_id)
    result = await db.execute(existing_stmt)
    existing_analysis = result.scalar_one_or_none()
    
    if existing_analysis:
        return JSONResponse(content={
            "primary_genre": existing_analysis.primary_genre,
            "confidence": existing_analysis.confidence,
            "subgenres": json.loads(existing_analysis.sub_genres) if existing_analysis.sub_genres else [],
            "harmonic_complexity_score": existing_analysis.harmonic_complexity,
            "tempo": existing_analysis.tempo,
            "source": "database"
        })

    # Get song
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Check audio exists
    audio_path = Path(song.audio_file_path) if song.audio_file_path else None
    if not audio_path or not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Get chords from database
    await db.refresh(song, ["chords"])
    chords_data = [
        {
            "root": chord.root,
            "quality": chord.quality,
            "time": chord.time,
            "duration": chord.duration,
            "symbol": f"{chord.root}{chord.quality}"
        }
        for chord in song.chords
    ]
    
    # Perform genre analysis
    try:
        result = analyze_genre(audio_path, chords_data)
        
        # Save to database
        db_analysis = GenreAnalysis(
            song_id=song_id,
            primary_genre=result["primary_genre"],
            confidence=result["confidence"],
            sub_genres=json.dumps(result["subgenres"]),
            harmonic_complexity=result["harmonic_complexity_score"],
            tempo=result["tempo"]
        )
        db.add(db_analysis)
        await db.commit()
        
        return JSONResponse(content={**result, "source": "computed"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genre analysis failed: {str(e)}")


@router.post("/jazz-patterns")
async def analyze_jazz_progression_patterns(
    song_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect jazz-specific patterns
    """
    # Check if analysis already exists
    from sqlalchemy import select, delete
    from app.database.models import DetectedPattern
    import json
    
    # Use select w/ scalar logic or check count
    # For a list of patterns, we just check if any exist for this song
    existing_stmt = select(DetectedPattern).where(DetectedPattern.song_id == song_id)
    result = await db.execute(existing_stmt)
    existing_patterns = result.scalars().all()
    
    if existing_patterns:
        # Reconstruct response structure
        ii_v_i = []
        turnarounds = []
        tritones = []
        
        for p in existing_patterns:
            pattern_data = {
                "pattern_type": p.pattern_type,
                "start_time": p.start_time,
                "duration": p.duration,
                "confidence": p.confidence,
                "key": p.key_context,
                "chords": [], # We don't store chord list in DB currently, might need to parse from metadata_json or SongChords
                "metadata": json.loads(p.metadata_json) if p.metadata_json else {}
            }
             # Best effort reconstruction or just return what we have
             # If we need exact parity with `JazzPattern` dataclass, we might store the chords list in metadata_json
            
            if p.pattern_type == "ii-V-I":
                ii_v_i.append(pattern_data)
            elif p.pattern_type == "turnaround":
                turnarounds.append(pattern_data)
            elif p.pattern_type == "tritone_substitution":
                tritones.append(pattern_data)

        # Basic complexity score logic if not stored
        complexity = 0.5 # placeholder if not stored
        
        return JSONResponse(content={
            "ii_v_i_progressions": ii_v_i,
            "turnarounds": turnarounds,
            "tritone_substitutions": tritones,
            "total_patterns": len(existing_patterns),
            "jazz_complexity_score": complexity,
            "source": "database"
        })

    # Get song
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Get chords
    await db.refresh(song, ["chords"])
    chords_data = [
        {
            "root": chord.root,
            "quality": chord.quality,
            "time": chord.time,
            "duration": chord.duration,
            "symbol": f"{chord.root}{chord.quality}"
        }
        for chord in song.chords
    ]
    
    if not chords_data:
        raise HTTPException(status_code=400, detail="No chords found. Song must be transcribed first.")
    
    # Analyze jazz patterns
    try:
        patterns_result = analyze_jazz_patterns(chords_data)
        
        # Save to database
        # We need to flatten the structure
        db_patterns = []
        
        for p in patterns_result["ii_v_i_progressions"]:
            db_patterns.append(DetectedPattern(
                song_id=song_id,
                pattern_type="ii-V-I",
                start_time=p.start_time,
                duration=p.duration,
                confidence=p.confidence,
                key_context=p.key,
                metadata_json=json.dumps(p.metadata)
            ))
            
        for p in patterns_result["turnarounds"]:
             db_patterns.append(DetectedPattern(
                song_id=song_id,
                pattern_type="turnaround",
                start_time=p.start_time,
                duration=p.duration,
                confidence=p.confidence,
                key_context=p.key,
                metadata_json=json.dumps(p.metadata)
            ))
            
        for p in patterns_result["tritone_substitutions"]:
             db_patterns.append(DetectedPattern(
                song_id=song_id,
                pattern_type="tritone_substitution",
                start_time=p.start_time,
                duration=p.duration,
                confidence=p.confidence,
                key_context=p.key,
                metadata_json=json.dumps(p.metadata)
            ))

        db.add_all(db_patterns)
        await db.commit()
        
        return JSONResponse(content={**jsonable_encoder(patterns_result), "source": "computed"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Jazz analysis failed: {str(e)}")


@router.post("/pitch-tracking")
async def track_pitch_with_crepe(
    song_id: str,
    model_capacity: str = "medium",
    detect_blue_notes_flag: bool = True,
    detect_vibrato_flag: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Neural pitch tracking with CREPE
    
    Args:
        song_id: Song UUID
        model_capacity: "tiny", "small", "medium", "large", "full"
        detect_blue_notes_flag: Detect microtonal/blue notes
        detect_vibrato_flag: Detect vibrato regions
    
    Returns:
        - Detailed pitch contour
        - Blue notes (if enabled)
        - Vibrato regions (if enabled)
        - Pitch bends analysis
    """
    # Get song
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    # Check audio exists
    audio_path = Path(song.audio_file_path) if song.audio_file_path else None
    if not audio_path or not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Extract pitch contour
        pitch_data = await extract_pitch_contour(
            audio_path,
            model_capacity=model_capacity
        )
        
        result = {
            "pitch_contour": {
                "time": pitch_data["time"][:1000],  # Limit for response size
                "frequency": pitch_data["frequency"][:1000],
                "confidence": pitch_data["confidence"][:1000],
                "notes": pitch_data["notes"][:1000]
            },
            "total_frames": len(pitch_data["time"])
        }
        
        # Optional analyses
        if detect_blue_notes_flag:
            blue_notes = detect_blue_notes(pitch_data)
            result["blue_notes"] = blue_notes
            result["blue_notes_count"] = len(blue_notes)
        
        if detect_vibrato_flag:
            vibrato = detect_vibrato(pitch_data)
            result["vibrato_regions"] = vibrato
            result["vibrato_count"] = len(vibrato)
        
        # Pitch bends
        bends = analyze_pitch_bends(pitch_data)
        result["pitch_bends"] = bends
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pitch tracking failed: {str(e)}")


@router.get("/chord-library")
async def get_extended_chord_library(
    genre: Optional[str] = None
):
    """
    Get extended chord template library
    
    Returns jazz voicings and chord templates for reference.
    
    Args:
        genre: Filter by genre (e.g., "jazz")
    """
    if genre == "jazz" or genre is None:
        return JSONResponse(content={
            "genre": "jazz" if genre else "all",
            "chord_templates": {
                name: {
                    "intervals": intervals,
                    "semitones": intervals,
                    "description": _get_chord_description(name)
                }
                for name, intervals in JAZZ_CHORD_TEMPLATES.items()
            },
            "total_voicings": len(JAZZ_CHORD_TEMPLATES)
        })
    
    return JSONResponse(content={"message": "No templates for this genre"})


def _get_chord_description(chord_name: str) -> str:
    """Get human-readable description of chord"""
    descriptions = {
        "maj7": "Major 7th - bright, stable",
        "maj9": "Major 9th - lush, extended",
        "maj7#11": "Major 7#11 - Lydian sound",
        "m7": "Minor 7th - mellow, contemplative",
        "m11": "Minor 11th - rich, modal",
        "7": "Dominant 7th - tension, wants to resolve",
        "7alt": "Altered dominant - maximum tension",
        "dim7": "Diminished 7th - unstable, passing",
    }
    return descriptions.get(chord_name, "Extended jazz voicing")


@router.post("/melody")
async def extract_melody_line(
    song_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Extract primary melody line
    
    Uses pitch tracking to identify the melodic contour.
    Note: For now uses CREPE. In future can use MELODIA (Essentia).
    """
    # Get song
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    
    audio_path = Path(song.audio_file_path) if song.audio_file_path else None
    if not audio_path or not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Use CREPE for melody extraction
        pitch_data = await extract_pitch_contour(audio_path, model_capacity="medium")
        
        # Filter high-confidence regions as melody
        melody_notes = []
        for i, (time, freq, conf, note) in enumerate(zip(
            pitch_data["time"],
            pitch_data["frequency"],
            pitch_data["confidence"],
            pitch_data["notes"]
        )):
            if conf > 0.8 and note:  # High confidence = likely melody
                melody_notes.append({
                    "time": float(time),
                    "note": note,
                    "frequency": float(freq),
                    "confidence": float(conf)
                })
        
        return JSONResponse(content={
            "melody_notes": melody_notes[:500],  # Limit response
            "total_notes": len(melody_notes),
            "method": "crepe_high_confidence",
            "average_confidence": sum(n["confidence"] for n in melody_notes) / len(melody_notes) if melody_notes else 0
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Melody extraction failed: {str(e)}")

@router.post("/blues-form")
async def analyze_blues_form(
    song_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect Blues forms (12-bar, shuffle, etc)
    """
    from app.pipeline.blues_analyzer import analyze_blues_structure
    
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    await db.refresh(song, ["chords"])
    chords_data = [
        {"root": c.root, "quality": c.quality, "time": c.time, "duration": c.duration}
        for c in song.chords
    ]
    
    return JSONResponse(content=analyze_blues_structure(chords_data, song.tempo or 100))


@router.post("/classical-form")
async def analyze_classical_form(
    song_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze Classical form structural markers
    """
    from app.pipeline.classical_analyzer import analyze_classical_form as analyze_classical
    
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    await db.refresh(song, ["chords"])
    chords_data = [
         {"root": c.root, "quality": c.quality, "time": c.time}
         for c in song.chords
    ]
    
    return JSONResponse(content=analyze_classical(chords_data, song.tempo or 80))


@router.post("/compare")
async def compare_transcription_engines(
    song_id: str,
    engines: List[str] = ["basic-pitch"],
    db: AsyncSession = Depends(get_db)
):
    """
    Run and compare multiple transcription engines (Basic Pitch vs others)
    """
    from app.pipeline.transcription_comparison import compare_transcriptions
    
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.audio_file_path:
         raise HTTPException(status_code=400, detail="Audio file required")
         
    # Assuming the audio path is absolute or handled by the helper
    result = await compare_transcriptions(song.audio_file_path, engines)
    return JSONResponse(content=result)
