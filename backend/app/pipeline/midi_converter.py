"""MIDI transcription using Spotify's basic-pitch"""

import asyncio
from pathlib import Path
from typing import Optional
import numpy as np
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import pretty_midi

from app.schemas.transcription import NoteEvent


class TranscriptionError(Exception):
    """MIDI transcription failed"""
    pass


async def transcribe_audio(
    audio_path: Path,
    midi_output_path: Path,
    onset_threshold: float = 0.5,
    frame_threshold: float = 0.3,
) -> tuple[list[NoteEvent], Path, Optional[float]]:
    """
    Transcribe audio to MIDI using basic-pitch
    
    Args:
        audio_path: Input audio file (WAV)
        midi_output_path: Output MIDI file path
        onset_threshold: Note onset threshold (0-1)
        frame_threshold: Note frame threshold (0-1)
    
    Returns:
        Tuple of (note events list, MIDI file path, estimated tempo)
    
    Raises:
        TranscriptionError: If transcription fails
    """
    try:
        midi_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _transcribe():
            # Run basic-pitch prediction
            model_output, midi_data, note_events_data = predict(
                str(audio_path),
                ICASSP_2022_MODEL_PATH,
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold,
            )
            
            # Save MIDI file
            midi_data.write(str(midi_output_path))
            
            return midi_data, note_events_data
        
        loop = asyncio.get_event_loop()
        midi_data, note_events_data = await loop.run_in_executor(None, _transcribe)
        
        # Convert to our NoteEvent schema
        notes = []
        for start_time, end_time, pitch, velocity, _ in note_events_data:
            notes.append(NoteEvent(
                pitch=int(pitch),
                start_time=float(start_time),
                end_time=float(end_time),
                velocity=int(velocity * 127),  # Convert 0-1 to 0-127
            ))
        
        # Estimate tempo from MIDI data
        tempo = estimate_tempo(midi_data)
        
        return notes, midi_output_path, tempo
        
    except Exception as e:
        raise TranscriptionError(f"MIDI transcription failed: {str(e)}")


def estimate_tempo(midi_data: pretty_midi.PrettyMIDI) -> Optional[float]:
    """
    Estimate tempo from MIDI data
    
    Args:
        midi_data: PrettyMIDI object
    
    Returns:
        Estimated tempo in BPM, or None if cannot estimate
    """
    try:
        # Get tempo changes
        if hasattr(midi_data, '_tick_scales'):
            # Use tempo changes if available
            tempo_changes = midi_data.get_tempo_changes()
            if len(tempo_changes[1]) > 0:
                # Return the first (or most common) tempo
                return float(tempo_changes[1][0])
        
        # Fallback: estimate from note IOIs (inter-onset intervals)
        all_notes = []
        for instrument in midi_data.instruments:
            all_notes.extend([(note.start, note.end) for note in instrument.notes])
        
        if len(all_notes) < 10:
            return None
        
        all_notes.sort(key=lambda x: x[0])
        
        # Calculate inter-onset intervals
        iois = []
        for i in range(1, min(len(all_notes), 100)):  # Use first 100 notes
            ioi = all_notes[i][0] - all_notes[i-1][0]
            if 0.1 < ioi < 2.0:  # Filter outliers
                iois.append(ioi)
        
        if not iois:
            return None
        
        # Estimate beat duration as median IOI
        median_ioi = np.median(iois)
        estimated_bpm = 60.0 / median_ioi
        
        # Clamp to reasonable range
        estimated_bpm = np.clip(estimated_bpm, 40, 200)
        
        return float(estimated_bpm)
        
    except Exception:
        return None


def estimate_key(notes: list[NoteEvent]) -> Optional[str]:
    """
    Estimate musical key from notes
    
    Args:
        notes: List of note events
    
    Returns:
        Estimated key (e.g., "C major"), or None
    """
    if not notes:
        return None
    
    try:
        # Count note occurrences (mod 12 for pitch classes)
        pitch_class_counts = [0] * 12
        for note in notes:
            pc = note.pitch % 12
            duration = note.end_time - note.start_time
            pitch_class_counts[pc] += duration  # Weight by duration
        
        # Major and minor key profiles (Krumhansl-Schmuckler)
        major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        best_correlation = -1
        best_key = None
        
        # Try all 24 keys
        for shift in range(12):
            # Rotate pitch class counts
            rotated = pitch_class_counts[shift:] + pitch_class_counts[:shift]
            
            # Correlate with major profile
            major_corr = np.corrcoef(rotated, major_profile)[0, 1]
            if major_corr > best_correlation:
                best_correlation = major_corr
                best_key = f"{note_names[shift]} major"
            
            # Correlate with minor profile
            minor_corr = np.corrcoef(rotated, minor_profile)[0, 1]
            if minor_corr > best_correlation:
                best_correlation = minor_corr
                best_key = f"{note_names[shift]} minor"
        
        return best_key if best_correlation > 0.6 else None
        
    except Exception:
        return None
