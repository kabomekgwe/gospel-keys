"""Chord building utilities for Phase 6 integration"""

from typing import List, Dict
from app.theory.interval_utils import note_to_semitone, semitone_to_note


# Quality to interval pattern mapping (semitones from root)
CHORD_INTERVALS: Dict[str, List[int]] = {
    '': [0, 4, 7],  # Major triad
    'M': [0, 4, 7],  # Major triad
    'maj': [0, 4, 7],  # Major triad
    'm': [0, 3, 7],  # Minor triad
    'min': [0, 3, 7],  # Minor triad
    'dim': [0, 3, 6],  # Diminished triad
    'aug': [0, 4, 8],  # Augmented triad
    '7': [0, 4, 7, 10],  # Dominant 7th
    'maj7': [0, 4, 7, 11],  # Major 7th
    'M7': [0, 4, 7, 11],  # Major 7th
    'm7': [0, 3, 7, 10],  # Minor 7th
    'min7': [0, 3, 7, 10],  # Minor 7th
    'dim7': [0, 3, 6, 9],  # Diminished 7th
    'm7b5': [0, 3, 6, 10],  # Half-diminished 7th
    'aug7': [0, 4, 8, 10],  # Augmented 7th
    '9': [0, 4, 7, 10, 14],  # Dominant 9th
    'maj9': [0, 4, 7, 11, 14],  # Major 9th
    'm9': [0, 3, 7, 10, 14],  # Minor 9th
    '11': [0, 4, 7, 10, 14, 17],  # Dominant 11th
    '13': [0, 4, 7, 10, 14, 17, 21],  # Dominant 13th
}


def get_chord_notes(root: str, quality: str) -> List[str]:
    """Build chord notes from root and quality

    Args:
        root: Root note (e.g., 'C', 'D#', 'Bb')
        quality: Chord quality (e.g., '', 'm', '7', 'maj7')

    Returns:
        List of note names in the chord

    Examples:
        >>> get_chord_notes('C', '')
        ['C', 'E', 'G']
        >>> get_chord_notes('D', 'm7')
        ['D', 'F', 'A', 'C']
    """
    # Get interval pattern for quality
    intervals = CHORD_INTERVALS.get(quality, CHORD_INTERVALS[''])

    # Convert root to semitone
    try:
        root_semitone = note_to_semitone(root)
    except Exception:
        # Fallback
        return [root]

    # Build notes
    notes = []
    for interval in intervals:
        note_semitone = (root_semitone + interval) % 12
        note = semitone_to_note(note_semitone)
        notes.append(note)

    return notes


def chord_to_midi(root: str, quality: str, octave: int = 4) -> List[int]:
    """Convert chord to MIDI note numbers

    Args:
        root: Root note (e.g., 'C', 'D#', 'Bb')
        quality: Chord quality (e.g., '', 'm', '7', 'maj7')
        octave: Base octave (default: 4 = middle C octave)

    Returns:
        List of MIDI note numbers

    Examples:
        >>> chord_to_midi('C', '', 4)
        [60, 64, 67]  # C4, E4, G4
        >>> chord_to_midi('D', 'm7', 4)
        [62, 65, 69, 72]  # D4, F4, A4, C5
    """
    # Get interval pattern for quality
    intervals = CHORD_INTERVALS.get(quality, CHORD_INTERVALS[''])

    # Convert root to semitone
    try:
        root_semitone = note_to_semitone(root)
    except Exception:
        # Fallback to middle C
        return [60]

    # Base MIDI note (C4 = 60)
    base_midi = 12 + octave * 12 + root_semitone

    # Build MIDI notes
    midi_notes = []
    for interval in intervals:
        midi_note = base_midi + interval
        midi_notes.append(midi_note)

    return midi_notes


def simplify_quality(quality: str) -> str:
    """Normalize chord quality to canonical form

    Args:
        quality: Chord quality string

    Returns:
        Simplified quality

    Examples:
        >>> simplify_quality('min7')
        'm7'
        >>> simplify_quality('M7')
        'maj7'
    """
    quality_map = {
        'min': 'm',
        'min7': 'm7',
        'M': 'maj',
        'M7': 'maj7',
        'major': 'maj',
        'major7': 'maj7',
        'dominant': '7',
        'dom7': '7',
    }

    return quality_map.get(quality, quality)
