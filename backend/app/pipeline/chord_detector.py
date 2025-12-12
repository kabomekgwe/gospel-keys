"""Chord detection using chromagram analysis"""

import asyncio
from pathlib import Path
import numpy as np
import librosa
from scipy.signal import medfilt

from app.schemas.transcription import ChordEvent


class ChordDetectionError(Exception):
    """Chord detection failed"""
    pass


# Gospel chord templates (12-dimensional chroma vectors)
CHORD_TEMPLATES = {
    'maj': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],  # C major: C, E, G
    'min': [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],  # C minor: C, Eb, G
    'maj7': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],  # Cmaj7: C, E, G, B
    'min7': [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0],  # Cm7: C, Eb, G, Bb
    '7': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0],  # C7: C, E, G, Bb
    'maj9': [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],  # Cmaj9: C, D, E, G, B
    'min9': [1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0],  # Cm9: C, D, Eb, G, Bb
    'dim': [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Cdim: C, Eb, Gb
    'aug': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],  # Caug: C, E, G#
    'sus4': [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],  # Csus4: C, F, G
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


async def detect_chords(
    audio_path: Path,
    hop_length: int = 4096,
    frame_length: int = 8192,
) -> list[ChordEvent]:
    """
    Detect chords using chromagram analysis
    
    Args:
        audio_path: Input audio file (WAV)
        hop_length: Hop length for chromagram  
        frame_length: Frame length for chromagram
    
    Returns:
        List of detected chord events
    
    Raises:
        ChordDetectionError: If detection fails
    """
    try:
        def _detect():
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
            
            # Compute chromagram
            chroma = librosa.feature.chroma_cqt(
                y=y,
                sr=sr,
                hop_length=hop_length,
                n_chroma=12,
            )
            
            # Normalize each frame
            chroma = librosa.util.normalize(chroma, axis=0, norm=2)
            
            # Detect chord for each frame
            chord_sequence = []
            confidence_sequence = []
            
            for frame_idx in range(chroma.shape[1]):
                chroma_frame = chroma[:, frame_idx]
                chord, confidence = match_chord_template(chroma_frame)
                chord_sequence.append(chord)
                confidence_sequence.append(confidence)
            
            # Median filter to smooth chord sequence
            # This helps remove spurious detections
            chord_indices = [chord_to_index(c) for c in chord_sequence]
            filtered_indices = medfilt(chord_indices, kernel_size=5).astype(int)
            chord_sequence = [index_to_chord(idx) for idx in filtered_indices]
            
            # Convert frame indices to time
            times = librosa.frames_to_time(
                np.arange(len(chord_sequence)),
                sr=sr,
                hop_length=hop_length
            )
            
            return chord_sequence, confidence_sequence, times
        
        loop = asyncio.get_event_loop()
        chord_sequence, confidence_sequence, times = await loop.run_in_executor(None, _detect)
        
        # Merge consecutive identical chords into events
        chord_events = []
        if len(chord_sequence) == 0:
            return chord_events
        
        current_chord = chord_sequence[0]
        current_start = times[0]
        current_confidences = [confidence_sequence[0]]
        
        for i in range(1, len(chord_sequence)):
            if chord_sequence[i] != current_chord:

                # End current chord, start new one
                avg_confidence = np.mean(current_confidences)
                root, quality = parse_chord_name(current_chord)
                
                duration = float(times[i] - current_start)
                if duration > 0.001:  # Filter out near-zero durations
                    chord_events.append(ChordEvent(
                        time=float(current_start),
                        duration=duration,
                        chord=current_chord,
                        confidence=float(avg_confidence),
                        root=root,
                        quality=quality,
                    ))
                
                current_chord = chord_sequence[i]
                current_start = times[i]
                current_confidences = [confidence_sequence[i]]
            else:
                current_confidences.append(confidence_sequence[i])
        
        # Add final chord
        avg_confidence = np.mean(current_confidences)
        root, quality = parse_chord_name(current_chord)
        duration = float(times[-1] - current_start)
        if duration > 0.001:
            chord_events.append(ChordEvent(
                time=float(current_start),
                duration=duration,
                chord=current_chord,
                confidence=float(avg_confidence),
                root=root,
                quality=quality,
            ))
        
        return chord_events
        
    except Exception as e:
        raise ChordDetectionError(f"Chord detection failed: {str(e)}")


def match_chord_template(chroma_frame: np.ndarray) -> tuple[str, float]:
    """
    Match chroma frame to best chord template
    
    Args:
        chroma_frame: 12-dimensional chroma vector
    
    Returns:
        Tuple of (chord name, confidence)
    """
    best_chord = "N"  # No chord
    best_score = 0.0
    
    # Try all root notes and qualities
    for root_idx in range(12):
        for quality, template in CHORD_TEMPLATES.items():
            # Rotate template to this root
            rotated_template = np.roll(template, root_idx)
            
            # Cosine similarity
            score = np.dot(chroma_frame, rotated_template) / (
                np.linalg.norm(chroma_frame) * np.linalg.norm(rotated_template) + 1e-8
            )
            
            if score > best_score:
                best_score = score
                chord_name = f"{NOTE_NAMES[root_idx]}{quality}"
                best_chord = chord_name
    
    # Only return chord if confidence is reasonable
    if best_score < 0.5:
        return "N", best_score
    
    return best_chord, best_score


def parse_chord_name(chord: str) -> tuple[str, str]:
    """
    Parse chord name into root and quality
    
    Args:
        chord: Chord name (e.g., "Cmaj7", "Dm9")
    
    Returns:
        Tuple of (root note, quality)
    """
    if chord == "N":
        return "N", "none"
    
    # Find where the quality starts
    if len(chord) > 1 and chord[1] in ['#', 'b']:
        root = chord[:2]
        quality = chord[2:] if len(chord) > 2 else "maj"
    else:
        root = chord[0]
        quality = chord[1:] if len(chord) > 1 else "maj"
    
    return root, quality


def chord_to_index(chord: str) -> int:
    """Convert chord name to unique index for median filtering"""
    if chord == "N":
        return 0
    
    root, quality = parse_chord_name(chord)
    root_idx = NOTE_NAMES.index(root) if root in NOTE_NAMES else 0
    quality_idx = list(CHORD_TEMPLATES.keys()).index(quality) if quality in CHORD_TEMPLATES else 0
    
    return root_idx * 100 + quality_idx


def index_to_chord(idx: int) -> str:
    """Convert index back to chord name"""
    if idx == 0:
        return "N"
    
    root_idx = idx // 100
    quality_idx = idx % 100
    
    root = NOTE_NAMES[root_idx % 12]
    quality = list(CHORD_TEMPLATES.keys())[quality_idx % len(CHORD_TEMPLATES)]
    
    return f"{root}{quality}"
