"""
Interval Utilities Module

Core music theory utilities for interval calculations, note manipulation,
and enharmonic equivalence.
"""

from typing import Tuple, Optional
from enum import Enum


class NoteClass(Enum):
    """Pitch class enumeration (0=C, 11=B)"""
    C = 0
    Cs = 1  # C#/Db
    D = 2
    Ds = 3  # D#/Eb
    E = 4
    F = 5
    Fs = 6  # F#/Gb
    G = 7
    Gs = 8  # G#/Ab
    A = 9
    As = 10  # A#/Bb
    B = 11


# Note name to semitone mapping (supports sharps, flats, double accidentals)
NOTE_TO_SEMITONE = {
    "C": 0, "B#": 0, "Dbb": 0,
    "C#": 1, "Db": 1, "B##": 1,
    "D": 2, "C##": 2, "Ebb": 2,
    "D#": 3, "Eb": 3, "Fbb": 3,
    "E": 4, "Fb": 4, "D##": 4,
    "F": 5, "E#": 5, "Gbb": 5,
    "F#": 6, "Gb": 6, "E##": 6,
    "G": 7, "F##": 7, "Abb": 7,
    "G#": 8, "Ab": 8,
    "A": 9, "G##": 9, "Bbb": 9,
    "A#": 10, "Bb": 10, "Cbb": 10,
    "B": 11, "Cb": 11, "A##": 11,
}

# Semitone to preferred note name (sharps)
SEMITONE_TO_NOTE_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SEMITONE_TO_NOTE_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Interval names
INTERVAL_NAMES = {
    0: "P1",   # Perfect unison
    1: "m2",   # Minor 2nd
    2: "M2",   # Major 2nd
    3: "m3",   # Minor 3rd
    4: "M3",   # Major 3rd
    5: "P4",   # Perfect 4th
    6: "TT",   # Tritone (A4/d5)
    7: "P5",   # Perfect 5th
    8: "m6",   # Minor 6th
    9: "M6",   # Major 6th
    10: "m7",  # Minor 7th
    11: "M7",  # Major 7th
    12: "P8",  # Octave
}

INTERVAL_FULL_NAMES = {
    0: "Unison",
    1: "Minor Second",
    2: "Major Second",
    3: "Minor Third",
    4: "Major Third",
    5: "Perfect Fourth",
    6: "Tritone",
    7: "Perfect Fifth",
    8: "Minor Sixth",
    9: "Major Sixth",
    10: "Minor Seventh",
    11: "Major Seventh",
    12: "Octave",
}


def note_to_semitone(note: str) -> int:
    """
    Convert note name to semitone value (0-11).
    
    Args:
        note: Note name (e.g., "C", "F#", "Bb", "G##")
    
    Returns:
        Semitone value (0=C, 11=B)
    
    Raises:
        ValueError: If note name is invalid
    """
    # Handle octave suffix (e.g., "C4" -> "C")
    clean_note = ''.join(c for c in note if not c.isdigit())
    
    if clean_note not in NOTE_TO_SEMITONE:
        raise ValueError(f"Invalid note name: {note}")
    
    return NOTE_TO_SEMITONE[clean_note]


def semitone_to_note(semitone: int, prefer_sharps: bool = True) -> str:
    """
    Convert semitone value to note name.
    
    Args:
        semitone: Semitone value (0-11)
        prefer_sharps: If True, use sharps; otherwise use flats
    
    Returns:
        Note name
    """
    semitone = semitone % 12
    if prefer_sharps:
        return SEMITONE_TO_NOTE_SHARP[semitone]
    return SEMITONE_TO_NOTE_FLAT[semitone]


def get_interval(note1: str, note2: str) -> int:
    """
    Calculate interval in semitones between two notes.
    
    Args:
        note1: First note name
        note2: Second note name
    
    Returns:
        Interval in semitones (0-11)
    """
    s1 = note_to_semitone(note1)
    s2 = note_to_semitone(note2)
    return (s2 - s1) % 12


def get_interval_name(semitones: int, short: bool = True) -> str:
    """
    Get the name of an interval given semitones.
    
    Args:
        semitones: Number of semitones
        short: If True, return abbreviated name (e.g., "M3")
    
    Returns:
        Interval name
    """
    semitones = semitones % 12
    if short:
        return INTERVAL_NAMES.get(semitones, f"{semitones}st")
    return INTERVAL_FULL_NAMES.get(semitones, f"{semitones} semitones")


def transpose(note: str, semitones: int, prefer_sharps: bool = True) -> str:
    """
    Transpose a note by a given number of semitones.
    
    Args:
        note: Note name to transpose
        semitones: Semitones to transpose (positive=up, negative=down)
        prefer_sharps: If True, use sharps in result
    
    Returns:
        Transposed note name
    """
    current = note_to_semitone(note)
    new = (current + semitones) % 12
    return semitone_to_note(new, prefer_sharps)


def is_enharmonic(note1: str, note2: str) -> bool:
    """
    Check if two notes are enharmonically equivalent.
    
    Args:
        note1: First note name
        note2: Second note name
    
    Returns:
        True if notes are enharmonic equivalents
    """
    return note_to_semitone(note1) == note_to_semitone(note2)


def get_circle_of_fifths_position(note: str) -> int:
    """
    Get position on circle of fifths (C=0, G=1, D=2, ..., F=-1, Bb=-2, etc.)
    
    Args:
        note: Note name
    
    Returns:
        Position on circle of fifths
    """
    circle = ["C", "G", "D", "A", "E", "B", "F#", "C#", "Ab", "Eb", "Bb", "F"]
    semitone = note_to_semitone(note)
    # Map semitone to circle position
    circle_positions = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: 7, 8: -4, 3: -3, 10: -2, 5: -1}
    return circle_positions.get(semitone, 0)


def get_key_signature(key: str, mode: str = "major") -> Tuple[int, str]:
    """
    Get key signature accidentals.
    
    Args:
        key: Key root note
        mode: "major" or "minor"
    
    Returns:
        Tuple of (number of accidentals, type: "sharps" or "flats")
    """
    # Major key signatures
    major_keys = {
        "C": (0, "sharps"), "G": (1, "sharps"), "D": (2, "sharps"),
        "A": (3, "sharps"), "E": (4, "sharps"), "B": (5, "sharps"),
        "F#": (6, "sharps"), "C#": (7, "sharps"),
        "F": (1, "flats"), "Bb": (2, "flats"), "Eb": (3, "flats"),
        "Ab": (4, "flats"), "Db": (5, "flats"), "Gb": (6, "flats"),
        "Cb": (7, "flats"),
    }
    
    # Minor uses relative major
    minor_to_major = {
        "A": "C", "E": "G", "B": "D", "F#": "A", "C#": "E", "G#": "B",
        "D#": "F#", "A#": "C#", "D": "F", "G": "Bb", "C": "Eb",
        "F": "Ab", "Bb": "Db", "Eb": "Gb", "Ab": "Cb"
    }
    
    if mode == "minor":
        key = minor_to_major.get(key, key)
    
    return major_keys.get(key, (0, "sharps"))


# MIDI utilities
def note_to_midi(note: str, octave: int = 4) -> int:
    """
    Convert note name and octave to MIDI number.
    
    Args:
        note: Note name
        octave: Octave number (default 4, middle C is C4=60)
    
    Returns:
        MIDI note number
    """
    # Extract octave from note if included (e.g., "C4")
    if note[-1].isdigit():
        octave = int(note[-1])
        note = note[:-1]
    
    semitone = note_to_semitone(note)
    return (octave + 1) * 12 + semitone


def midi_to_note(midi: int, prefer_sharps: bool = True) -> str:
    """
    Convert MIDI number to note name with octave.
    
    Args:
        midi: MIDI note number (0-127)
        prefer_sharps: If True, use sharps
    
    Returns:
        Note name with octave (e.g., "C4")
    """
    octave = (midi // 12) - 1
    semitone = midi % 12
    note = semitone_to_note(semitone, prefer_sharps)
    return f"{note}{octave}"


def frequency_to_midi(freq: float, a4_freq: float = 440.0) -> int:
    """
    Convert frequency to nearest MIDI note number.
    
    Args:
        freq: Frequency in Hz
        a4_freq: Reference A4 frequency (default 440 Hz)
    
    Returns:
        MIDI note number
    """
    import math
    if freq <= 0:
        return 0
    return round(69 + 12 * math.log2(freq / a4_freq))


def midi_to_frequency(midi: int, a4_freq: float = 440.0) -> float:
    """
    Convert MIDI note number to frequency.
    
    Args:
        midi: MIDI note number
        a4_freq: Reference A4 frequency (default 440 Hz)
    
    Returns:
        Frequency in Hz
    """
    return a4_freq * (2 ** ((midi - 69) / 12))
