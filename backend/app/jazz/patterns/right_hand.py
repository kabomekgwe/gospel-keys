"""Jazz Right Hand Patterns

Implements authentic jazz piano right hand patterns:
- Bebop lines (8th note runs using bebop scales)
- Chord melody (melody + harmony in one hand)
- Block chords / Locked hands (melody doubled in octaves)
- Single note improvisation (solo lines)
- Upper structure triads (polychords over bass)

Key Jazz Concepts:
- Bebop scales: Add chromatic passing tones to target chord tones on downbeats
- Chord melody: Harmonize melody with guide tones underneath
- Locked hands: Melody in octaves with chord tones between (George Shearing style)
- Upper structures: Triad built from upper extensions (e.g., D triad over Cmaj7)
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Bebop scale intervals (major bebop scale: adds chromatic between 5-6)
BEBOP_MAJOR_SCALE = [0, 2, 4, 5, 7, 8, 9, 11]  # C D E F G G# A B
BEBOP_DORIAN_SCALE = [0, 2, 3, 5, 7, 9, 10, 11]  # C D Eb F G A Bb B (for minor chords)
BEBOP_DOMINANT_SCALE = [0, 2, 4, 5, 7, 9, 10, 11]  # C D E F G A Bb B (for dominant chords)

# Chord melody voicings (melody note + guide tones)
CHORD_MELODY_INTERVALS = {
    "maj7": [0, 4, 7, 11],      # Root, 3rd, 5th, 7th
    "7": [0, 4, 7, 10],         # Root, 3rd, 5th, b7
    "min7": [0, 3, 7, 10],      # Root, b3, 5th, b7
    "m7b5": [0, 3, 6, 10],      # Root, b3, b5, b7
}


def parse_chord_symbol(chord: str) -> Tuple[str, str]:
    """Parse chord symbol into root and quality."""
    if len(chord) > 1 and chord[1] in ('b', '#'):
        root = chord[:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]

    if not quality or quality == "7":
        quality = "7" if quality == "7" else "maj"

    return root, quality


def get_root_midi(root: str, octave: int = 5) -> int:
    """Get MIDI note for root in right hand register."""
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


# Pattern Generators

def bebop_line_pattern(context: ChordContext) -> HandPattern:
    """Generate bebop line pattern.

    Bebop line: 8th note run using bebop scale.
    Targets chord tones on downbeats.

    Pattern (4 beats of 8th notes):
    Ascending or descending bebop scale run

    Args:
        context: Chord context

    Returns:
        HandPattern with bebop line notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=5)

    # Select bebop scale based on chord quality
    if "min" in quality or "m7" in quality:
        scale = BEBOP_DORIAN_SCALE
    elif quality == "7" or "dom" in quality:
        scale = BEBOP_DOMINANT_SCALE
    else:
        scale = BEBOP_MAJOR_SCALE

    notes = []

    # Create 8th note run (8 notes over 4 beats)
    for i, interval in enumerate(scale):
        beat_time = i * 0.5  # 8th notes
        pitch = root_midi + interval

        note = Note(
            pitch=pitch,
            time=beat_time,
            duration=0.4,  # Slightly shorter for articulation
            velocity=85 - (i * 2),  # Slight dynamic variation
            hand="right"
        )
        notes.append(note)

    return HandPattern(
        name="Bebop Line",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(120, 240),
        characteristics=["jazz", "bebop", "eighth_notes", "scale_run"]
    )


def chord_melody_pattern(context: ChordContext) -> HandPattern:
    """Generate chord melody pattern.

    Chord melody: Melody note on top with harmony underneath.
    Typical jazz piano voicing with melody + 3rd + 7th.

    Pattern:
    - Top note: Melody (5th or 7th of chord)
    - Middle notes: Guide tones (3rd + 7th)
    - Sustained voicing (2 beats), then movement

    Args:
        context: Chord context

    Returns:
        HandPattern with chord melody notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=4)

    # Get chord melody voicing
    if quality in CHORD_MELODY_INTERVALS:
        intervals = CHORD_MELODY_INTERVALS[quality]
    else:
        intervals = [0, 4, 7, 11]  # Default to maj7

    voicing = [root_midi + interval for interval in intervals]

    notes = []

    # Beat 1-2: Full chord
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=0.0,
            duration=2.0,
            velocity=75,
            hand="right"
        ))

    # Beat 3-4: Move to upper extensions (9th, 11th)
    upper_voicing = [v + 2 for v in voicing[-2:]]  # Move top two voices up
    for pitch in voicing[:-2] + upper_voicing:
        notes.append(Note(
            pitch=pitch,
            time=2.0,
            duration=2.0,
            velocity=70,
            hand="right"
        ))

    return HandPattern(
        name="Chord Melody",
        notes=notes,
        difficulty="advanced",
        tempo_range=(60, 140),
        characteristics=["jazz", "chord_melody", "voicing"]
    )


def block_chords_locked_hands_pattern(context: ChordContext) -> HandPattern:
    """Generate block chords (locked hands style).

    Locked hands: Melody doubled in octaves with chord tones between.
    George Shearing / Milt Buckner style.

    Pattern:
    - Top: Melody note
    - Middle: Guide tones (3rd, 7th)
    - Bottom: Melody octave below

    Args:
        context: Chord context

    Returns:
        HandPattern with locked hands notes
    """
    root, quality = parse_chord_symbol(context.chord)
    melody_midi = get_root_midi(root, octave=5) + 7  # 5th as melody

    # Guide tones
    guide_tones = [
        get_root_midi(root, octave=4) + 4,   # 3rd
        get_root_midi(root, octave=4) + 10,  # 7th
    ]

    # Locked hands voicing: melody octave + guide tones + melody
    voicing = [melody_midi - 12] + guide_tones + [melody_midi]

    notes = []

    # Create 4 quarter-note chords with slight rhythmic variation
    chord_times = [0.0, 1.0, 2.0, 3.0]
    for time in chord_times:
        for pitch in voicing:
            notes.append(Note(
                pitch=pitch,
                time=time,
                duration=0.8,  # Slightly shorter for articulation
                velocity=80,
                hand="right"
            ))

    return HandPattern(
        name="Block Chords (Locked Hands)",
        notes=notes,
        difficulty="advanced",
        tempo_range=(100, 180),
        characteristics=["jazz", "locked_hands", "block_chords", "shearing"]
    )


def single_note_improvisation_pattern(context: ChordContext) -> HandPattern:
    """Generate single-note improvisation pattern.

    Single-note solo line focusing on chord tones and passing tones.
    Creates melodic phrases with rhythmic variety.

    Pattern:
    Mixture of quarter notes and 8th notes, targeting chord tones

    Args:
        context: Chord context

    Returns:
        HandPattern with improvisation line
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=5)

    # Get chord tones
    if quality in CHORD_MELODY_INTERVALS:
        intervals = CHORD_MELODY_INTERVALS[quality]
    else:
        intervals = [0, 4, 7, 11]

    notes = []

    # Create melodic phrase: mix of quarter and 8th notes
    # Beat 1: Root (quarter)
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=0.9,
        velocity=85,
        hand="right"
    ))

    # Beats 2-3: 8th notes (3rd, chromatic, 5th, 7th)
    phrase = [
        (1.0, root_midi + intervals[1], 0.4),  # 3rd
        (1.5, root_midi + intervals[1] + 1, 0.4),  # Chromatic
        (2.0, root_midi + intervals[2], 0.4),  # 5th
        (2.5, root_midi + intervals[3], 0.4),  # 7th
    ]

    for time, pitch, duration in phrase:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=80,
            hand="right"
        ))

    # Beat 4: Target chord tone (9th)
    notes.append(Note(
        pitch=root_midi + 14,  # 9th
        time=3.0,
        duration=1.0,
        velocity=85,
        hand="right"
    ))

    return HandPattern(
        name="Single Note Improvisation",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(120, 240),
        characteristics=["jazz", "solo", "improvisation", "melodic"]
    )


def upper_structure_triads_pattern(context: ChordContext) -> HandPattern:
    """Generate upper structure triad pattern.

    Upper structures: Triad built from upper extensions of chord.
    Example: D triad over Cmaj7 = Cmaj9#11

    Pattern:
    Play triad built from 5th, 7th, 9th of original chord

    Args:
        context: Chord context

    Returns:
        HandPattern with upper structure notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=4)

    # Build upper structure triad (5th, 7th, 9th as root-3rd-5th of upper triad)
    if "min" in quality:
        # Minor chord: build minor triad from 5th
        upper_triad = [root_midi + 7, root_midi + 10, root_midi + 14]  # 5th, b7, 9
    else:
        # Major/dominant: build major triad from 5th
        upper_triad = [root_midi + 7, root_midi + 11, root_midi + 14]  # 5th, 7th, 9th

    notes = []

    # Play upper triad as sustained chord
    for pitch in upper_triad:
        notes.append(Note(
            pitch=pitch,
            time=0.0,
            duration=4.0,
            velocity=75,
            hand="right"
        ))

    return HandPattern(
        name="Upper Structure Triads",
        notes=notes,
        difficulty="advanced",
        tempo_range=(60, 160),
        characteristics=["jazz", "upper_structures", "polychord", "modern"]
    )


# Pattern library
JAZZ_RIGHT_HAND_PATTERNS = {
    "bebop_line": bebop_line_pattern,
    "chord_melody": chord_melody_pattern,
    "block_chords_locked_hands": block_chords_locked_hands_pattern,
    "single_note_improvisation": single_note_improvisation_pattern,
    "upper_structure_triads": upper_structure_triads_pattern,
}


def generate_jazz_right_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate a jazz right hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in JAZZ_RIGHT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown jazz right hand pattern: {pattern_name}. "
            f"Available: {list(JAZZ_RIGHT_HAND_PATTERNS.keys())}"
        )

    generator = JAZZ_RIGHT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "generate_jazz_right_hand_pattern",
    "JAZZ_RIGHT_HAND_PATTERNS",
]
