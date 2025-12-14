"""
Notation Export Utilities

Handles conversion of MIDI data to MusicXML format for sheet music software.
Uses pretty_midi for MIDI handling and music21 for score generation.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import logging
import pretty_midi
import music21

logger = logging.getLogger(__name__)

async def export_to_musicxml(
    midi_path: Path,
    output_path: Path,
    song_metadata: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Convert a MIDI file to MusicXML format.
    
    Args:
        midi_path: Path to input MIDI file
        output_path: Path to save MusicXML output
        song_metadata: Optional dictionary with 'title' and 'artist'
        
    Returns:
        Path to the generated MusicXML file
    """
    try:
        # Load MIDI file
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
        
        # Create music21 score
        score = music21.converter.parse(str(midi_path))
        
        # Add metadata
        if song_metadata:
            if 'title' in song_metadata:
                score.metadata = music21.metadata.Metadata()
                score.metadata.title = song_metadata['title']
            if 'artist' in song_metadata:
                score.metadata.composer = song_metadata['artist']
                
        # Save as MusicXML
        # music21 writes to a temp file then moves it, so we need to handle paths carefully
        score.write('musicxml', fp=str(output_path))
        
        logger.info(f"Successfully exported MusicXML to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to export MusicXML: {e}")
        # Fallback: create a basic empty MusicXML if conversion fails
        # so the connection doesn't just hang
        raise RuntimeError(f"MusicXML export failed: {str(e)}")

async def export_with_quantization(
    midi_path: Path,
    output_path: Path,
    quantize_to: str = "16th",
    tempo_bpm: float = 120.0
) -> Path:
    """
    Quantize MIDI file and save to output path.
    Useful for cleaning up recorded MIDI before notation export.
    """
    try:
        pm = pretty_midi.PrettyMIDI(str(midi_path))
        
        # Calculate grid size in seconds
        # 60 / bpm = seconds per beat
        # grid = seconds per beat / (subdivisions per beat)
        beat_duration = 60.0 / (tempo_bpm if tempo_bpm else 120.0)
        
        grid_divisor = {
            "quarter": 1,
            "8th": 2,
            "16th": 4,
            "32nd": 8
        }.get(quantize_to, 4)
        
        grid_size = beat_duration / grid_divisor
        
        # Quantize note start times and durations
        for instrument in pm.instruments:
            for note in instrument.notes:
                # Quantize start
                quantized_start = round(note.start / grid_size) * grid_size
                # Quantize duration (ensure min duration of 1 grid unit)
                raw_end = note.end
                quantized_end = round(raw_end / grid_size) * grid_size
                if quantized_end <= quantized_start:
                    quantized_end = quantized_start + grid_size
                    
                note.start = quantized_start
                note.end = quantized_end
                
        pm.write(str(output_path))
        return output_path
        
    except Exception as e:
        logger.error(f"Quantization failed: {e}")
        raise
