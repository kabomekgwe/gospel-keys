"""
Chord Inversion System

Functions for generating chord inversions (Phase 1).
Inversions rotate chord tones so different notes become the bass.
"""

from typing import List, Tuple
from app.theory.chord_types import get_chord_type
from app.theory.interval_utils import semitone_to_note, note_to_semitone


def get_inversion_intervals(intervals: Tuple[int, ...], inversion: int) -> List[int]:
    """
    Calculate intervals for a specific inversion.

    Inversions rotate chord tones so a different note becomes the bass.
    Notes below the new bass are raised by an octave (12 semitones).

    Args:
        intervals: Original chord intervals (semitones from root)
        inversion: Inversion number (0=root, 1=1st, 2=2nd, 3=3rd, 4=4th)

    Returns:
        List of intervals for the inversion (from new bass note)

    Examples:
        Cmaj7 root position:  (0, 4, 7, 11) → [0, 4, 7, 11]   # C E G B
        Cmaj7 1st inversion:  (0, 4, 7, 11) → [0, 3, 7, 12]   # E G B C (bass E)
        Cmaj7 2nd inversion:  (0, 4, 7, 11) → [0, 4, 5, 9]    # G B C E (bass G)
        Cmaj7 3rd inversion:  (0, 4, 7, 11) → [0, 1, 5, 8]    # B C E G (bass B)
    """
    if inversion == 0:
        return list(intervals)

    if inversion < 0 or inversion >= len(intervals):
        raise ValueError(
            f"Invalid inversion {inversion} for chord with {len(intervals)} notes. "
            f"Valid inversions: 0 to {len(intervals) - 1}"
        )

    # Get the interval of the new bass note
    bass_interval = intervals[inversion]

    # Calculate new intervals relative to the new bass
    result = []
    for i, interval in enumerate(intervals):
        if i == inversion:
            # This is the new bass note
            result.append(0)
        elif i > inversion:
            # Notes that were above the new bass stay above
            distance = interval - bass_interval
            result.append(distance)
        else:
            # Notes that were below the new bass go up an octave
            distance = (12 - bass_interval) + interval
            result.append(distance)

    return result


def get_chord_notes_with_inversion(
    root: str,
    quality: str,
    inversion: int = 0,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Get chord notes in specified inversion with octave numbers.

    Uses MIDI note number approach for clarity and correctness.

    Args:
        root: Root note (e.g., "C", "F#")
        quality: Chord quality (e.g., "maj7", "m7", "7")
        inversion: 0=root, 1=1st, 2=2nd, 3=3rd, 4=4th (for 9/11/13)
        octave: Starting octave for bass note
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves (e.g., ["E4", "G4", "B4", "C5"])

    Examples:
        >>> get_chord_notes_with_inversion("C", "maj7", 0, 4)
        ["C4", "E4", "G4", "B4"]  # Root position

        >>> get_chord_notes_with_inversion("C", "maj7", 1, 4)
        ["E4", "G4", "B4", "C5"]  # 1st inversion (E on bass)

        >>> get_chord_notes_with_inversion("C", "maj7", 2, 4)
        ["G4", "B4", "C5", "E5"]  # 2nd inversion (G on bass)
    """
    chord = get_chord_type(quality)

    if inversion < 0 or inversion >= len(chord.intervals):
        raise ValueError(
            f"Invalid inversion {inversion} for chord with {len(chord.intervals)} notes"
        )

    # Calculate MIDI note numbers for root position
    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone  # MIDI note for root in given octave

    # Create list of MIDI notes in root position
    midi_notes = [base_midi + interval for interval in chord.intervals]

    if inversion > 0:
        # Move the first 'inversion' notes up an octave
        for i in range(inversion):
            midi_notes[i] += 12

        # Sort to maintain ascending order
        midi_notes.sort()

    # Convert MIDI notes to note names with octaves
    notes_with_octaves = []
    for midi_note in midi_notes:
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes_with_octaves.append(f"{note_name}{note_octave}")

    return notes_with_octaves


__all__ = [
    'get_inversion_intervals',
    'get_chord_notes_with_inversion',
]
