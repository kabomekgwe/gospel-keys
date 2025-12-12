"""Music notation export using music21 and pretty_midi

Provides MusicXML export for notation software and MIDI quantization.
"""

import asyncio
from pathlib import Path
from typing import Optional
import pretty_midi
from music21 import converter, stream, note, chord, tempo, key, meter, metadata


class NotationExportError(Exception):
    """Notation export failed"""
    pass


async def export_to_musicxml(
    midi_path: Path,
    output_path: Path,
    song_metadata: Optional[dict] = None
) -> Path:
    """
    Convert MIDI to MusicXML using music21
    
    Args:
        midi_path: Input MIDI file
        output_path: Output MusicXML file (.musicxml or .xml)
        song_metadata: Dict with title, composer/artist, etc.
    
    Returns:
        Path to MusicXML file
    
    Raises:
        NotationExportError: If conversion fails
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _convert():
            # Parse MIDI with music21
            score = converter.parse(str(midi_path))
            
            # Add metadata
            if song_metadata:
                if not score.metadata:
                    score.metadata = metadata.Metadata()
                
                if 'title' in song_metadata and song_metadata['title']:
                    score.metadata.title = song_metadata['title']
                if 'artist' in song_metadata and song_metadata['artist']:
                    score.metadata.composer = song_metadata['artist']
            
            # Quantize for better notation (snap to 16th notes)
            # This helps clean up transcription artifacts
            try:
                score = score.quantize(quarterLengthDivisors=[4])  # 16th note grid
            except:
                pass  # Skip if quantization fails
            
            # Export to MusicXML
            score.write('musicxml', fp=str(output_path))
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _convert)
        
        return output_path
        
    except Exception as e:
        raise NotationExportError(f"MusicXML export failed: {str(e)}")


async def export_with_quantization(
    midi_path: Path,
    output_path: Path,
    quantize_to: str = "16th",
    tempo_bpm: Optional[float] = None
) -> Path:
    """
    Export MIDI with quantization for cleaner notation
    
    Reads existing MIDI and quantizes note timing to a grid.
    
    Args:
        midi_path: Input MIDI file
        output_path: Output quantized MIDI file
        quantize_to: Grid size - "quarter", "8th", "16th", "32nd"
        tempo_bpm: Override tempo (uses original if None)
    
    Returns:
        Path to quantized MIDI file
    
    Raises:
        NotationExportError: If quantization fails
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _quantize():
            # Load MIDI
            midi_data = pretty_midi.PrettyMIDI(str(midi_path))
            
            # Get tempo
            if tempo_bpm is None:
                tempo_changes = midi_data.get_tempo_changes()
                current_tempo = tempo_changes[1][0] if len(tempo_changes[1]) > 0 else 120.0
            else:
                current_tempo = tempo_bpm
            
            # Calculate quantize grid in seconds
            beat_duration = 60.0 / current_tempo
            grid_divisions = {"quarter": 1, "8th": 2, "16th": 4, "32nd": 8}
            grid_size = beat_duration / grid_divisions.get(quantize_to, 4)
            
            # Create new MIDI with quantized notes
            quantized_midi = pretty_midi.PrettyMIDI(initial_tempo=current_tempo)
            
            for instrument in midi_data.instruments:
                new_instrument = pretty_midi.Instrument(
                    program=instrument.program,
                    is_drum=instrument.is_drum,
                    name=instrument.name
                )
                
                for note in instrument.notes:
                    # Snap start and end to grid
                    quantized_start = round(note.start / grid_size) * grid_size
                    quantized_end = round(note.end / grid_size) * grid_size
                    
                    # Ensure minimum note duration (one grid unit)
                    if quantized_end - quantized_start < grid_size:
                        quantized_end = quantized_start + grid_size
                    
                    quantized_note = pretty_midi.Note(
                        velocity=note.velocity,
                        pitch=note.pitch,
                        start=quantized_start,
                        end=quantized_end
                    )
                    new_instrument.notes.append(quantized_note)
                
                quantized_midi.instruments.append(new_instrument)
            
            # Write quantized MIDI
            quantized_midi.write(str(output_path))
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _quantize)
        
        return output_path
        
    except Exception as e:
        raise NotationExportError(f"MIDI quantization failed: {str(e)}")
