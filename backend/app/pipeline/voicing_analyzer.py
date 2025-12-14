"""
Voicing Analyzer

Analyzes how chords are actually voiced on piano from MIDI note data.
Classifies voicing types and identifies chord tones vs extensions.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

from app.schemas.transcription import Note, ChordEvent
from app.theory.interval_utils import note_to_semitone, get_interval
from app.theory.chord_library import get_chord_notes


class VoicingType(Enum):
    """Types of piano voicings"""
    CLOSE = "close"              # All notes within an octave
    OPEN = "open"                # Notes span more than an octave
    DROP_2 = "drop_2"            # Second voice from top dropped an octave
    DROP_3 = "drop_3"            # Third voice from top dropped an octave
    DROP_2_4 = "drop_2_4"        # Second and fourth voices dropped
    ROOTLESS = "rootless"        # No root in voicing
    SHELL = "shell"              # Just root-3rd-7th (or root-7th-3rd)
    SPREAD = "spread"            # Wide spacing (>2 octaves)
    QUARTAL = "quartal"          # Built on fourths instead of thirds
    CLUSTER = "cluster"          # Multiple adjacent semitones


@dataclass
class VoicingInfo:
    """Complete voicing analysis for a chord"""
    chord_symbol: str
    voicing_type: VoicingType
    notes: List[int]             # MIDI note numbers (sorted low to high)
    note_names: List[str]        # Note names (e.g., ["C3", "E3", "G3"])
    intervals: List[int]         # Intervals between consecutive notes
    width_semitones: int         # Total span of voicing
    inversion: int               # 0=root position, 1=1st inversion, etc.
    has_root: bool
    has_third: bool
    has_seventh: bool
    extensions: List[str]        # e.g., ["9", "11", "13"]
    complexity_score: float      # 0-1, higher = more complex
    hand_span_inches: float      # Approximate physical span on keyboard


def semitone_to_note_name(semitone: int, octave: int) -> str:
    """Convert MIDI note to name with octave"""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note = note_names[semitone % 12]
    return f"{note}{octave}"


def midi_to_note_name(midi_note: int) -> str:
    """Convert MIDI number to note name with octave"""
    octave = (midi_note // 12) - 1
    semitone = midi_note % 12
    return semitone_to_note_name(semitone, octave)


def group_notes_by_time(notes: List[Note], chord: ChordEvent, window: float = 0.2) -> List[int]:
    """
    Group MIDI notes that fall within a chord's time window.

    Args:
        notes: All MIDI notes from transcription
        chord: Chord event with start/end times
        window: Time tolerance in seconds

    Returns:
        List of MIDI note numbers (sorted)
    """
    chord_notes = []
    chord_start = chord.start_time
    chord_end = chord.end_time

    for note in notes:
        # Check if note overlaps with chord time window
        note_overlaps = (
            (note.start_time >= chord_start - window and note.start_time <= chord_end) or
            (note.end_time >= chord_start and note.end_time <= chord_end + window) or
            (note.start_time <= chord_start and note.end_time >= chord_end)
        )

        if note_overlaps:
            chord_notes.append(note.pitch)

    # Remove duplicates and sort
    return sorted(list(set(chord_notes)))


def classify_voicing_type(intervals: List[int], width: int, has_root: bool) -> VoicingType:
    """
    Classify the voicing type based on interval patterns.

    Args:
        intervals: Intervals between consecutive notes (semitones)
        width: Total span in semitones
        has_root: Whether root is present

    Returns:
        VoicingType classification
    """
    if len(intervals) == 0:
        return VoicingType.CLOSE

    # Check for quartal voicing (built on fourths)
    if all(i in [5, 6] for i in intervals):  # Perfect 4th or tritone
        return VoicingType.QUARTAL

    # Check for cluster (adjacent semitones)
    if any(i <= 2 for i in intervals) and len([i for i in intervals if i <= 2]) >= 2:
        return VoicingType.CLUSTER

    # Rootless voicing
    if not has_root:
        return VoicingType.ROOTLESS

    # Shell voicing (typically 3 notes: root-3rd-7th)
    if len(intervals) == 2 and width <= 14:  # Within an octave + 2nd
        return VoicingType.SHELL

    # Close voicing (all within octave)
    if width <= 12:
        return VoicingType.CLOSE

    # Spread voicing (very wide)
    if width > 24:
        return VoicingType.SPREAD

    # Drop voicings (require specific interval patterns)
    # Drop-2: 2nd voice from top is dropped an octave
    # This creates a characteristic interval pattern
    if len(intervals) >= 3:
        # Drop-2 typically has a large interval in the middle
        if intervals[1] > 7 or intervals[2] > 7:
            # Check if it might be drop-2-4
            if len(intervals) >= 4 and intervals[3] > 7:
                return VoicingType.DROP_2_4
            return VoicingType.DROP_2

        # Drop-3: 3rd voice from top is dropped
        if len(intervals) >= 2 and intervals[0] > 7:
            return VoicingType.DROP_3

    # Default to open voicing
    if width > 12:
        return VoicingType.OPEN

    return VoicingType.CLOSE


def identify_chord_tones(
    midi_notes: List[int],
    chord_root: str,
    chord_quality: str
) -> Tuple[bool, bool, bool, List[str]]:
    """
    Identify which chord tones are present and what extensions.

    Returns:
        (has_root, has_third, has_seventh, extensions)
    """
    # Get expected chord notes
    expected_notes = get_chord_notes(chord_root, chord_quality)

    if not expected_notes:
        return False, False, False, []

    # Convert MIDI notes to pitch classes (0-11)
    pitch_classes = [n % 12 for n in midi_notes]

    # Get root pitch class
    root_semitone = note_to_semitone(chord_root)

    # Identify chord tones
    has_root = root_semitone in pitch_classes

    # Third is 3 or 4 semitones above root
    has_third = ((root_semitone + 3) % 12 in pitch_classes or  # minor 3rd
                 (root_semitone + 4) % 12 in pitch_classes)    # major 3rd

    # Seventh is 10 or 11 semitones above root
    has_seventh = ((root_semitone + 10) % 12 in pitch_classes or  # minor 7th
                   (root_semitone + 11) % 12 in pitch_classes)     # major 7th

    # Identify extensions (9, 11, 13)
    extensions = []

    # 9th = 2 semitones above root (next octave)
    if (root_semitone + 2) % 12 in pitch_classes:
        extensions.append("9")

    # 11th = 5 semitones above root
    if (root_semitone + 5) % 12 in pitch_classes:
        extensions.append("11")

    # 13th = 9 semitones above root
    if (root_semitone + 9) % 12 in pitch_classes:
        extensions.append("13")

    # Check for altered extensions
    if (root_semitone + 1) % 12 in pitch_classes:  # b9
        extensions.append("b9")
    if (root_semitone + 3) % 12 in pitch_classes and not has_third:  # #9
        extensions.append("#9")
    if (root_semitone + 6) % 12 in pitch_classes:  # #11
        extensions.append("#11")

    return has_root, has_third, has_seventh, extensions


def calculate_complexity_score(
    voicing_type: VoicingType,
    num_notes: int,
    extensions: List[str],
    width: int
) -> float:
    """
    Calculate complexity score (0-1) based on voicing characteristics.

    Higher score = more complex/advanced voicing
    """
    score = 0.0

    # Base complexity from voicing type
    type_scores = {
        VoicingType.CLOSE: 0.1,
        VoicingType.SHELL: 0.2,
        VoicingType.OPEN: 0.3,
        VoicingType.ROOTLESS: 0.5,
        VoicingType.DROP_2: 0.6,
        VoicingType.DROP_3: 0.7,
        VoicingType.DROP_2_4: 0.8,
        VoicingType.QUARTAL: 0.7,
        VoicingType.SPREAD: 0.6,
        VoicingType.CLUSTER: 0.9,
    }
    score += type_scores.get(voicing_type, 0.3)

    # Number of notes (more = more complex)
    if num_notes >= 6:
        score += 0.2
    elif num_notes >= 5:
        score += 0.1

    # Extensions (each adds complexity)
    score += len(extensions) * 0.1

    # Very wide voicings are harder
    if width > 24:
        score += 0.1

    # Cap at 1.0
    return min(1.0, score)


def estimate_hand_span(width_semitones: int) -> float:
    """
    Estimate physical hand span in inches on piano keyboard.

    One octave (12 semitones) ≈ 6.5 inches on standard piano
    """
    return (width_semitones / 12.0) * 6.5


async def analyze_voicing(
    notes: List[Note],
    chord: ChordEvent
) -> Optional[VoicingInfo]:
    """
    Analyze how a chord is voiced from MIDI note data.

    Args:
        notes: All MIDI notes from transcription
        chord: Chord event to analyze

    Returns:
        VoicingInfo with complete analysis, or None if insufficient data
    """
    def _analyze():
        # Parse chord symbol (e.g., "Cmaj7" -> root="C", quality="maj7")
        chord_symbol = chord.chord

        # Extract root and quality
        # Simple parsing - assumes format like "Cmaj7", "Dm7", "G7"
        root = chord_symbol[0]
        if len(chord_symbol) > 1 and chord_symbol[1] in ['#', 'b']:
            root = chord_symbol[:2]
            quality = chord_symbol[2:]
        else:
            quality = chord_symbol[1:] if len(chord_symbol) > 1 else ''

        # Group notes that belong to this chord
        midi_notes = group_notes_by_time(notes, chord)

        if len(midi_notes) < 2:
            return None  # Need at least 2 notes to analyze voicing

        # Calculate intervals between consecutive notes
        intervals = [midi_notes[i+1] - midi_notes[i] for i in range(len(midi_notes) - 1)]

        # Total width
        width = midi_notes[-1] - midi_notes[0]

        # Identify chord tones and extensions
        has_root, has_third, has_seventh, extensions = identify_chord_tones(
            midi_notes, root, quality
        )

        # Classify voicing type
        voicing_type = classify_voicing_type(intervals, width, has_root)

        # Determine inversion
        root_semitone = note_to_semitone(root)
        bass_note_class = midi_notes[0] % 12

        if bass_note_class == root_semitone:
            inversion = 0
        elif bass_note_class == (root_semitone + 4) % 12 or bass_note_class == (root_semitone + 3) % 12:
            inversion = 1  # 3rd in bass
        elif bass_note_class == (root_semitone + 7) % 12:
            inversion = 2  # 5th in bass
        else:
            inversion = 1  # Assume some inversion

        # Convert MIDI notes to note names
        note_names = [midi_to_note_name(n) for n in midi_notes]

        # Calculate complexity
        complexity = calculate_complexity_score(voicing_type, len(midi_notes), extensions, width)

        # Estimate hand span
        hand_span = estimate_hand_span(width)

        return VoicingInfo(
            chord_symbol=chord_symbol,
            voicing_type=voicing_type,
            notes=midi_notes,
            note_names=note_names,
            intervals=intervals,
            width_semitones=width,
            inversion=inversion,
            has_root=has_root,
            has_third=has_third,
            has_seventh=has_seventh,
            extensions=extensions,
            complexity_score=complexity,
            hand_span_inches=hand_span
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _analyze)


async def analyze_all_voicings(
    notes: List[Note],
    chords: List[ChordEvent]
) -> List[VoicingInfo]:
    """
    Analyze voicings for all chords in a progression.

    Args:
        notes: All MIDI notes
        chords: All detected chords

    Returns:
        List of voicing analyses
    """
    voicings = []

    for chord in chords:
        voicing = await analyze_voicing(notes, chord)
        if voicing:
            voicings.append(voicing)

    return voicings
