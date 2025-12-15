"""
Basic Chord Voicings (Phase 2)

Drop voicings, rootless voicings, shell voicings, and So What voicing.
Standard jazz piano voicing techniques.
"""

from typing import List
from app.theory.chord_types import get_chord_type
from app.theory.interval_utils import semitone_to_note, note_to_semitone


# ============================================================================
# DROP VOICINGS
# ============================================================================

def apply_drop_2(midi_notes: List[int]) -> List[int]:
    """
    Apply drop-2 voicing: drop 2nd voice from top down an octave.

    Args:
        midi_notes: List of MIDI note numbers in close position (ascending)

    Returns:
        List of MIDI notes with drop-2 voicing

    Example:
        Cmaj7 close: [60, 64, 67, 71] (C4, E4, G4, B4)
        Drop-2:      [60, 55, 64, 71] (C4, G3, E4, B4)
    """
    if len(midi_notes) < 4:
        return midi_notes  # Need at least 4 notes for drop-2

    result = midi_notes.copy()
    # Drop 2nd from top (index -2) down an octave
    result[-2] -= 12
    return sorted(result)


def apply_drop_3(midi_notes: List[int]) -> List[int]:
    """
    Apply drop-3 voicing: drop 3rd voice from top down an octave.

    Args:
        midi_notes: List of MIDI note numbers in close position

    Returns:
        List of MIDI notes with drop-3 voicing
    """
    if len(midi_notes) < 4:
        return midi_notes

    result = midi_notes.copy()
    # Drop 3rd from top (index -3) down an octave
    result[-3] -= 12
    return sorted(result)


def apply_drop_2_4(midi_notes: List[int]) -> List[int]:
    """
    Apply drop-2-4 voicing: drop 2nd AND 4th voices down an octave.

    Creates very wide voicing, common in big band arranging.

    Args:
        midi_notes: List of MIDI note numbers in close position

    Returns:
        List of MIDI notes with drop-2-4 voicing
    """
    if len(midi_notes) < 4:
        return midi_notes

    result = midi_notes.copy()
    # Drop 2nd from top (index -2)
    result[-2] -= 12
    # Drop 4th from top (index -4)
    result[-4] -= 12
    return sorted(result)


# ============================================================================
# ROOTLESS VOICINGS (Bill Evans Style)
# ============================================================================

def get_rootless_voicing_a(
    root: str,
    quality: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate rootless voicing Type A: 3-5-7-9.

    Bill Evans style left-hand voicing.
    3rd on bottom, assumes bass player covers root.

    Args:
        root: Root note
        quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        Cmaj7 → [E3, G3, B3, D4] (3-5-7-9)
    """
    chord = get_chord_type(quality)

    # Find intervals for 3, 5, 7, 9
    intervals = list(chord.intervals)

    # Identify chord tones
    third_idx = None
    fifth_idx = None
    seventh_idx = None
    ninth_interval = None

    # Common interval patterns
    for i, interval in enumerate(intervals):
        if interval in (3, 4):  # m3 or M3
            third_idx = i
        elif interval == 7:  # P5
            fifth_idx = i
        elif interval in (10, 11):  # m7 or M7
            seventh_idx = i
        elif interval == 14:  # 9th
            ninth_interval = interval

    # Build rootless voicing
    voicing_intervals = []
    if third_idx is not None:
        voicing_intervals.append(intervals[third_idx])
    if fifth_idx is not None:
        voicing_intervals.append(intervals[fifth_idx])
    if seventh_idx is not None:
        voicing_intervals.append(intervals[seventh_idx])
    if ninth_interval is not None:
        voicing_intervals.append(ninth_interval)

    # Generate notes
    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in voicing_intervals:
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


def get_rootless_voicing_b(
    root: str,
    quality: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate rootless voicing Type B: 7-9-3-5.

    Bill Evans style left-hand voicing.
    7th on bottom (inverted form of Type A).

    Args:
        root: Root note
        quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        Cmaj7 → [B3, D4, E4, G4] (7-9-3-5)
    """
    # Get Type A voicing
    type_a = get_rootless_voicing_a(root, quality, octave, prefer_sharps)

    if len(type_a) < 4:
        return type_a

    # Convert to MIDI, rotate, convert back
    # Type A: [3, 5, 7, 9] → Type B: [7, 9, 3, 5]
    # This is essentially moving first two notes up an octave
    midi_notes = []
    for note_str in type_a:
        # Parse note name and octave
        note_name = ''.join(c for c in note_str if not c.isdigit())
        note_oct = int(''.join(c for c in note_str if c.isdigit()))
        semitone = note_to_semitone(note_name)
        midi = note_oct * 12 + semitone
        midi_notes.append(midi)

    # Rotate: move first two up an octave
    if len(midi_notes) >= 2:
        midi_notes[0] += 12
        midi_notes[1] += 12
        midi_notes.sort()

    # Convert back to note names
    notes = []
    for midi_note in midi_notes:
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


# ============================================================================
# SHELL VOICINGS
# ============================================================================

def get_shell_voicing(
    root: str,
    quality: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate shell voicing: Root-3-7 only.

    Essential tones for jazz comping.
    Omits the 5th.

    Args:
        root: Root note
        quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves (3 notes)

    Example:
        Cmaj7 → [C3, E3, B3]
    """
    chord = get_chord_type(quality)
    intervals = list(chord.intervals)

    # Always include root (0)
    # Find 3rd and 7th
    third_idx = None
    seventh_idx = None

    for i, interval in enumerate(intervals):
        if interval in (3, 4):  # m3 or M3
            third_idx = i
        elif interval in (10, 11):  # m7 or M7
            seventh_idx = i

    # Build shell voicing
    shell_intervals = [0]  # Root
    if third_idx is not None:
        shell_intervals.append(intervals[third_idx])
    if seventh_idx is not None:
        shell_intervals.append(intervals[seventh_idx])

    # Generate notes
    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in shell_intervals:
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


# ============================================================================
# SO WHAT VOICING
# ============================================================================

def get_so_what_voicing(
    root: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate So What voicing: Quartal stack + major 3rd.

    Bill Evans voicing from Miles Davis "So What".
    Structure: 4ths stacked, then major 3rd on top.

    Args:
        root: Root note
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of 5 note names

    Example:
        D So What → [D3, G3, C4, F4, A4]
                     (P4, P4, P4, M3)
    """
    # So What voicing intervals: 0, 5, 10, 15, 19
    # (root, +P4, +P4, +P4, +M3)
    intervals = [0, 5, 10, 15, 19]

    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in intervals:
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


__all__ = [
    'apply_drop_2',
    'apply_drop_3',
    'apply_drop_2_4',
    'get_rootless_voicing_a',
    'get_rootless_voicing_b',
    'get_shell_voicing',
    'get_so_what_voicing',
]
