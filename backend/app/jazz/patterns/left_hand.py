"""Jazz Left Hand Patterns

Implements authentic jazz piano left hand patterns:
- Rootless voicings (3rd + 7th + extensions, omit root/5th)
- Walking bass (chromatic approach tones, quarter-note pulse)
- Stride jazz (jazz stride with swing feel)
- Comping syncopated (off-beat chord stabs)
- Bass line chromatic (chromatic passing tones)

Key Jazz Concepts:
- Rootless voicings let bass player handle the root
- Walking bass uses chromatic approach tones (half-step below target)
- Swing feel: triplet-based 8th notes
- Comping: Syncopated chord voicings on off-beats
"""

from typing import List, Tuple, Optional
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings (C2 = 36 is low C for left hand bass)
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Jazz chord intervals (rootless voicings)
JAZZ_CHORD_INTERVALS = {
    # Rootless voicings - omit root and 5th
    "maj7": [4, 7, 11],          # 3rd, 5th, 7th (for rootless: 3rd, 7th, 9th)
    "7": [4, 10, 14],            # 3rd, b7, 9th (dominant)
    "min7": [3, 10, 14],         # b3, b7, 9th
    "m7b5": [3, 6, 10],          # b3, b5, b7 (half-diminished)
    "dim7": [3, 6, 9],           # b3, b5, bb7
    "maj9": [4, 11, 14],         # 3rd, 7th, 9th
    "9": [4, 10, 14],            # 3rd, b7, 9th
    "min9": [3, 10, 14],         # b3, b7, 9th
    "7#11": [4, 10, 18],         # 3rd, b7, #11 (lydian dominant)
    "7b9": [4, 10, 13],          # 3rd, b7, b9
    "7#9": [4, 10, 15],          # 3rd, b7, #9
    "min11": [3, 10, 17],        # b3, b7, 11
}

# Full chord intervals for walking bass root notes
FULL_CHORD_INTERVALS = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "maj7": [0, 4, 7, 11],
    "7": [0, 4, 7, 10],
    "min7": [0, 3, 7, 10],
    "m7b5": [0, 3, 6, 10],
    "dim7": [0, 3, 6, 9],
}


def parse_chord_symbol(chord: str) -> Tuple[str, str]:
    """Parse chord symbol into root and quality.

    Args:
        chord: Chord symbol (e.g., "Cmaj7", "Dm7", "G7#11")

    Returns:
        Tuple of (root_note, quality)
    """
    # Extract root note
    if len(chord) > 1 and chord[1] in ('b', '#'):
        root = chord[:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]

    # Default to dominant 7 if just a number
    if quality == "7":
        quality = "7"
    elif not quality:
        quality = "maj"

    return root, quality


def get_root_note_midi(root: str, octave: int = 3) -> int:
    """Get MIDI note number for root note.

    Args:
        root: Root note (e.g., "C", "Db", "F#")
        octave: Octave number (default 3 for bass)

    Returns:
        MIDI note number
    """
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


def get_rootless_voicing(chord: str, octave: int = 3) -> List[int]:
    """Get rootless voicing MIDI notes (3rd, 7th, extensions).

    Jazz rootless voicings omit the root and often the 5th,
    focusing on guide tones (3rd and 7th) plus color tones.

    Args:
        chord: Chord symbol
        octave: Base octave (default 3 for left hand)

    Returns:
        List of MIDI note numbers for rootless voicing
    """
    root, quality = parse_chord_symbol(chord)
    base_midi = get_root_note_midi(root, octave)

    # Get intervals for rootless voicing
    if quality in JAZZ_CHORD_INTERVALS:
        intervals = JAZZ_CHORD_INTERVALS[quality]
    else:
        # Fallback to 3rd + 7th
        intervals = [4, 10]  # 3rd + b7 (dominant)

    return [base_midi + interval for interval in intervals]


def get_chromatic_approach(target_midi: int, from_below: bool = True) -> int:
    """Get chromatic approach tone to target note.

    Args:
        target_midi: Target MIDI note
        from_below: If True, approach from half-step below; else from above

    Returns:
        MIDI note number for approach tone
    """
    return target_midi - 1 if from_below else target_midi + 1


# Pattern Generators

def rootless_voicing_pattern(context: ChordContext) -> HandPattern:
    """Generate jazz rootless voicing pattern.

    Rootless voicings emphasize guide tones (3rd + 7th) with extensions.
    Omits root (bass player covers it) and often 5th.

    Pattern: Sustained rootless chord (whole note or dotted half)

    Args:
        context: Chord context

    Returns:
        HandPattern with rootless voicing notes
    """
    voicing = get_rootless_voicing(context.chord, octave=3)

    # Create sustained chord (4 beats)
    notes = []
    for pitch in voicing:
        note = Note(
            pitch=pitch,
            time=0.0,
            duration=4.0,  # Whole note
            velocity=70,
            hand="left"
        )
        notes.append(note)

    return HandPattern(
        name="Rootless Voicing",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(80, 200),
        characteristics=["jazz", "rootless", "guide_tones"]
    )


def walking_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate jazz walking bass pattern.

    Walking bass: Quarter-note pulse with chromatic approach tones.
    Classic bebop/swing style.

    Pattern (4 beats):
    - Beat 1: Root
    - Beat 2: Chord tone (3rd or 5th)
    - Beat 3: Passing tone or chromatic approach
    - Beat 4: Chromatic approach to next root

    Args:
        context: Chord context

    Returns:
        HandPattern with walking bass notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)  # Lower octave for bass

    # Get chord tones
    if quality in FULL_CHORD_INTERVALS:
        intervals = FULL_CHORD_INTERVALS[quality]
    else:
        intervals = [0, 4, 7]  # Default to major triad

    chord_tones = [root_midi + interval for interval in intervals]

    notes = []

    # Beat 1: Root
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=1.0,
        velocity=85,
        hand="left"
    ))

    # Beat 2: 3rd or 5th
    beat2_pitch = chord_tones[1] if len(chord_tones) > 1 else root_midi + 4
    notes.append(Note(
        pitch=beat2_pitch,
        time=1.0,
        duration=1.0,
        velocity=80,
        hand="left"
    ))

    # Beat 3: Passing tone (5th or 7th)
    beat3_pitch = chord_tones[2] if len(chord_tones) > 2 else root_midi + 7
    notes.append(Note(
        pitch=beat3_pitch,
        time=2.0,
        duration=1.0,
        velocity=75,
        hand="left"
    ))

    # Beat 4: Chromatic approach to next root
    if context.next_chord:
        next_root, _ = parse_chord_symbol(context.next_chord)
        next_root_midi = get_root_note_midi(next_root, octave=2)
        approach_note = get_chromatic_approach(next_root_midi, from_below=True)
    else:
        # No next chord - use chromatic approach to current root
        approach_note = root_midi - 1

    notes.append(Note(
        pitch=approach_note,
        time=3.0,
        duration=1.0,
        velocity=78,
        hand="left"
    ))

    return HandPattern(
        name="Walking Bass",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(100, 200),
        characteristics=["jazz", "walking", "chromatic", "quarter_notes"]
    )


def stride_jazz_pattern(context: ChordContext) -> HandPattern:
    """Generate jazz stride bass pattern.

    Stride pattern with swing feel:
    - Beats 1 & 3: Root note (low)
    - Beats 2 & 4: Rootless chord (mid-range)

    Args:
        context: Chord context

    Returns:
        HandPattern with stride notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi_low = get_root_note_midi(root, octave=2)  # Low root
    voicing = get_rootless_voicing(context.chord, octave=3)  # Mid-range chord

    notes = []

    # Beat 1: Low root
    notes.append(Note(
        pitch=root_midi_low,
        time=0.0,
        duration=1.0,
        velocity=90,
        hand="left"
    ))

    # Beat 2: Rootless chord
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=1.0,
            duration=0.5,
            velocity=75,
            hand="left"
        ))

    # Beat 3: Low root
    notes.append(Note(
        pitch=root_midi_low,
        time=2.0,
        duration=1.0,
        velocity=85,
        hand="left"
    ))

    # Beat 4: Rootless chord
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=3.0,
            duration=0.5,
            velocity=70,
            hand="left"
        ))

    return HandPattern(
        name="Stride Jazz",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(120, 180),
        characteristics=["jazz", "stride", "swing"]
    )


def comping_syncopated_pattern(context: ChordContext) -> HandPattern:
    """Generate syncopated comping pattern.

    Jazz comping: Off-beat chord stabs on beats 2 and 4 (and & of beats).
    Creates syncopated rhythmic feel.

    Pattern:
    - Beat 2: Rootless chord (short stab)
    - Beat 4: Rootless chord (short stab)

    Args:
        context: Chord context

    Returns:
        HandPattern with comping notes
    """
    voicing = get_rootless_voicing(context.chord, octave=3)

    notes = []

    # Beat 2: Chord stab (short duration)
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=1.0,
            duration=0.5,
            velocity=80,
            hand="left"
        ))

    # Beat 4: Chord stab
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=3.0,
            duration=0.5,
            velocity=75,
            hand="left"
        ))

    return HandPattern(
        name="Comping Syncopated",
        notes=notes,
        difficulty="beginner",
        tempo_range=(100, 200),
        characteristics=["jazz", "comping", "syncopated", "off_beat"]
    )


def bass_line_chromatic_pattern(context: ChordContext) -> HandPattern:
    """Generate chromatic bass line pattern.

    Chromatic bass line with strong quarter-note pulse.
    Uses chromatic passing tones between chord tones.

    Pattern (4 beats):
    - Beat 1: Root
    - Beat 2: Chromatic passing tone
    - Beat 3: Chord tone (3rd or 5th)
    - Beat 4: Chromatic approach to next root

    Args:
        context: Chord context

    Returns:
        HandPattern with chromatic bass line
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)

    notes = []

    # Beat 1: Root
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=1.0,
        velocity=85,
        hand="left"
    ))

    # Beat 2: Chromatic passing tone (half-step above root)
    notes.append(Note(
        pitch=root_midi + 1,
        time=1.0,
        duration=1.0,
        velocity=75,
        hand="left"
    ))

    # Beat 3: 3rd
    third_midi = root_midi + (4 if "maj" in quality or quality == "7" else 3)
    notes.append(Note(
        pitch=third_midi,
        time=2.0,
        duration=1.0,
        velocity=80,
        hand="left"
    ))

    # Beat 4: Chromatic approach to next root
    if context.next_chord:
        next_root, _ = parse_chord_symbol(context.next_chord)
        next_root_midi = get_root_note_midi(next_root, octave=2)
        approach_note = get_chromatic_approach(next_root_midi, from_below=True)
    else:
        approach_note = root_midi - 1

    notes.append(Note(
        pitch=approach_note,
        time=3.0,
        duration=1.0,
        velocity=78,
        hand="left"
    ))

    return HandPattern(
        name="Bass Line Chromatic",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(100, 180),
        characteristics=["jazz", "chromatic", "bass_line", "quarter_notes"]
    )


# Pattern library
JAZZ_LEFT_HAND_PATTERNS = {
    "rootless_voicing": rootless_voicing_pattern,
    "walking_bass": walking_bass_pattern,
    "stride_jazz": stride_jazz_pattern,
    "comping_syncopated": comping_syncopated_pattern,
    "bass_line_chromatic": bass_line_chromatic_pattern,
}


def generate_jazz_left_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate a jazz left hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in JAZZ_LEFT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown jazz left hand pattern: {pattern_name}. "
            f"Available: {list(JAZZ_LEFT_HAND_PATTERNS.keys())}"
        )

    generator = JAZZ_LEFT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "generate_jazz_left_hand_pattern",
    "JAZZ_LEFT_HAND_PATTERNS",
    "get_rootless_voicing",
    "parse_chord_symbol",
]
