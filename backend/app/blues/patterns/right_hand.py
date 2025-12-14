"""Blues Piano Right Hand Patterns

Implements authentic blues piano right hand patterns:
- Blues licks (blues scale melodies)
- Call and response (question-answer phrases)
- Blues bends (grace notes simulating guitar bends)
- Double stops in sixths (classic blues piano sound)
- Blues tremolo (fast repeated notes for intensity)

Key Blues Concepts:
- Blues scale: 1, b3, 4, b5, 5, b7
- Blue notes: b3, b5, b7 (microtonal bends in practice)
- Call and response: musical conversation
- Grace notes: quick decorative notes (simulate bends)
- Influences: Professor Longhair, Dr. John, Ray Charles
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Blues scale intervals (minor blues scale)
BLUES_SCALE = [0, 3, 5, 6, 7, 10]  # Root, b3, 4, b5, 5, b7


def parse_chord_symbol(chord: str) -> Tuple[str, str]:
    """Parse chord symbol into root and quality."""
    if len(chord) > 1 and chord[1] in ('b', '#'):
        root = chord[:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]

    if not quality:
        quality = "7"  # Default to dominant 7th for blues

    return root, quality


def get_root_midi(root: str, octave: int = 5) -> int:
    """Get MIDI note for root in right hand register."""
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


# Pattern Generators

def blues_lick_pattern(context: ChordContext) -> HandPattern:
    """Generate blues lick pattern.

    Classic blues scale lick with bends and slides.
    Uses blues scale (1, b3, 4, b5, 5, b7).

    Pattern:
    Ascending or descending blues scale run with rhythm variation

    Args:
        context: Chord context

    Returns:
        HandPattern with blues lick notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=4)

    notes = []

    # Classic blues lick: b7 - b3 - 4 - b5 - 5 - b3
    lick_intervals = [10, 7, 3, 5, 6, 7, 3]  # In semitones from root

    for i, interval in enumerate(lick_intervals):
        time = i * 0.5  # 8th notes
        if time >= 4.0:
            break

        pitch = root_midi + interval

        note = Note(
            pitch=pitch,
            time=time,
            duration=0.4,
            velocity=85 - (i % 3) * 5,  # Dynamic variation
            hand="right"
        )
        notes.append(note)

    return HandPattern(
        name="Blues Lick",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(80, 160),
        characteristics=["blues", "lick", "blues_scale", "eighth_notes"]
    )


def call_response_pattern(context: ChordContext) -> HandPattern:
    """Generate call and response pattern.

    Musical conversation: question (call) and answer (response).
    Typical of blues phrasing.

    Pattern:
    - Beats 1-2: Call (ascending phrase)
    - Beats 3-4: Response (descending resolution)

    Args:
        context: Chord context

    Returns:
        HandPattern with call and response notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=5)

    notes = []

    # Call (beats 1-2): Ascending blues phrase
    call_phrase = [
        (0.0, root_midi, 0.5, 80),           # Root
        (0.5, root_midi + 3, 0.5, 85),       # b3
        (1.0, root_midi + 5, 0.5, 88),       # 4
        (1.5, root_midi + 7, 0.5, 90),       # 5 (peak)
    ]

    for time, pitch, duration, velocity in call_phrase:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="right"
        ))

    # Response (beats 3-4): Descending resolution
    response_phrase = [
        (2.0, root_midi + 7, 0.5, 85),       # 5
        (2.5, root_midi + 5, 0.5, 82),       # 4
        (3.0, root_midi + 3, 0.5, 78),       # b3
        (3.5, root_midi, 0.5, 75),           # Root (resolution)
    ]

    for time, pitch, duration, velocity in response_phrase:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="right"
        ))

    return HandPattern(
        name="Call and Response",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 140),
        characteristics=["blues", "call_response", "phrasing"]
    )


def blues_bends_pattern(context: ChordContext) -> HandPattern:
    """Generate blues bends pattern.

    Simulate guitar-style bends using grace notes.
    Quick grace note before target note.

    Pattern:
    Grace notes (1 semitone below) leading to target blues notes

    Args:
        context: Chord context

    Returns:
        HandPattern with blues bend notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=5)

    notes = []

    # Bends to blue notes: b3, 5, b7
    target_notes = [
        (0.0, root_midi + 3),    # Bend to b3
        (1.5, root_midi + 7),    # Bend to 5
        (3.0, root_midi + 10),   # Bend to b7
    ]

    for time, target_pitch in target_notes:
        # Grace note (half-step below target)
        notes.append(Note(
            pitch=target_pitch - 1,
            time=time,
            duration=0.1,  # Very short
            velocity=70,
            hand="right"
        ))

        # Target note (the "bent" note)
        notes.append(Note(
            pitch=target_pitch,
            time=time + 0.1,
            duration=0.9,
            velocity=90,  # Accent the target
            hand="right"
        ))

    return HandPattern(
        name="Blues Bends",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(60, 130),
        characteristics=["blues", "bends", "grace_notes", "expressive"]
    )


def double_stop_sixths_pattern(context: ChordContext) -> HandPattern:
    """Generate double stops in sixths pattern.

    Classic blues piano sound: melody doubled in sixths.
    Rich, full sound typical of New Orleans piano.

    Pattern:
    Melody line with harmony a sixth below

    Args:
        context: Chord context

    Returns:
        HandPattern with double stop notes
    """
    root, quality = parse_chord_symbol(context.chord)
    melody_midi = get_root_midi(root, octave=5)

    notes = []

    # Melody line using blues scale
    melody_sequence = [
        (0.0, melody_midi + 7, 1.0),       # 5th
        (1.0, melody_midi + 5, 1.0),       # 4th
        (2.0, melody_midi + 3, 1.0),       # b3
        (3.0, melody_midi, 1.0),           # Root
    ]

    for time, melody_pitch, duration in melody_sequence:
        # Melody note (top)
        notes.append(Note(
            pitch=melody_pitch,
            time=time,
            duration=duration,
            velocity=85,
            hand="right"
        ))

        # Harmony note (sixth below = 9 semitones below)
        harmony_pitch = melody_pitch - 9
        notes.append(Note(
            pitch=harmony_pitch,
            time=time,
            duration=duration,
            velocity=80,
            hand="right"
        ))

    return HandPattern(
        name="Double Stops (Sixths)",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 140),
        characteristics=["blues", "double_stops", "sixths", "new_orleans"]
    )


def blues_tremolo_pattern(context: ChordContext) -> HandPattern:
    """Generate blues tremolo pattern.

    Fast repeated notes for intensity and excitement.
    Builds tension and energy.

    Pattern:
    Rapid 16th-note repetition of a single note

    Args:
        context: Chord context

    Returns:
        HandPattern with tremolo notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=5)

    # Tremolo on the 5th (power and intensity)
    tremolo_pitch = root_midi + 7  # 5th

    notes = []

    # 16 16th notes (4 beats)
    for i in range(16):
        time = i * 0.25  # 16th notes
        note = Note(
            pitch=tremolo_pitch,
            time=time,
            duration=0.2,
            velocity=80 + (i % 4) * 5,  # Slight dynamic variation
            hand="right"
        )
        notes.append(note)

    return HandPattern(
        name="Blues Tremolo",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(90, 160),
        characteristics=["blues", "tremolo", "sixteenth_notes", "intensity"]
    )


# Pattern library
BLUES_RIGHT_HAND_PATTERNS = {
    "blues_lick": blues_lick_pattern,
    "call_response": call_response_pattern,
    "blues_bends": blues_bends_pattern,
    "double_stop_sixths": double_stop_sixths_pattern,
    "blues_tremolo": blues_tremolo_pattern,
}


def generate_blues_right_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate a blues right hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in BLUES_RIGHT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown blues right hand pattern: {pattern_name}. "
            f"Available: {list(BLUES_RIGHT_HAND_PATTERNS.keys())}"
        )

    generator = BLUES_RIGHT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "generate_blues_right_hand_pattern",
    "BLUES_RIGHT_HAND_PATTERNS",
]
