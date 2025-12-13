"""Right Hand Gospel Piano Patterns

Implements gospel right hand patterns for melody, fills, and voicings:
- Melody with harmonic fills
- Chord-based fills (beat 3-4)
- Octave doubling
- Block chord voicings
- Polychord structures
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern


# Import chord parsing utilities from left_hand
from app.gospel.patterns.left_hand import (
    parse_chord_symbol,
    get_chord_tones,
    NOTE_TO_MIDI,
    CHORD_INTERVALS
)


def melody_with_fills_pattern(context: ChordContext) -> HandPattern:
    """Generate melody line with harmonic fills.

    Pattern: Sustained melody notes with fills between chord changes.
    Traditional gospel melodic style.

    Args:
        context: Chord context

    Returns:
        HandPattern with melody and fills
    """
    chord_tones = get_chord_tones(context.chord, octave=4)  # C4 register

    # Use top note of chord as melody
    if len(chord_tones) >= 4:
        melody_note = chord_tones[3]  # 7th
        harmony_notes = [chord_tones[1], chord_tones[2]]  # 3rd, 5th
    elif len(chord_tones) >= 3:
        melody_note = chord_tones[2]  # 5th
        harmony_notes = [chord_tones[1]]  # 3rd
    else:
        melody_note = chord_tones[1]  # 3rd
        harmony_notes = [chord_tones[0]]  # Root

    notes = [
        # Beat 1-2: Sustained melody with harmony
        Note(pitch=melody_note, time=0.0, duration=2.0, velocity=85, hand="right"),
        *[Note(pitch=p, time=0.0, duration=2.0, velocity=75, hand="right")
          for p in harmony_notes],

        # Beat 3: Fill (scalar approach)
        Note(pitch=melody_note - 2, time=2.0, duration=0.5, velocity=70, hand="right"),
        Note(pitch=melody_note - 1, time=2.5, duration=0.5, velocity=75, hand="right"),

        # Beat 4: Melody resolution
        Note(pitch=melody_note, time=3.0, duration=1.0, velocity=80, hand="right"),
        *[Note(pitch=p, time=3.0, duration=1.0, velocity=70, hand="right")
          for p in harmony_notes],
    ]

    return HandPattern(
        name="melody_with_fills",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(60, 120),
        characteristics=["melodic", "expressive", "traditional"]
    )


def chord_fills_pattern(context: ChordContext) -> HandPattern:
    """Generate chord-based fills on beats 3-4.

    Pattern: Block chords on beats 1-2, fills on beats 3-4.
    Common gospel transitional pattern.

    Args:
        context: Chord context

    Returns:
        HandPattern with chord fills
    """
    chord_tones = get_chord_tones(context.chord, octave=4)

    # Close voicing for right hand (within octave)
    if len(chord_tones) >= 4:
        voicing = chord_tones[1:5]  # 3rd, 5th, 7th, 9th
    elif len(chord_tones) >= 3:
        voicing = chord_tones[:3]  # Root, 3rd, 5th
    else:
        voicing = chord_tones[:2]  # Root, 3rd

    # Fill notes (scalar approach to next chord)
    fill_start = voicing[-1]  # Top note
    fill_notes = [fill_start + i for i in range(-3, 1)]  # Descending fill

    notes = [
        # Beats 1-2: Sustained chord
        *[Note(pitch=p, time=0.0, duration=2.0, velocity=80, hand="right")
          for p in voicing],

        # Beat 3: Fill (descending run)
        *[Note(pitch=fill_notes[i], time=2.0 + (i * 0.25), duration=0.25,
               velocity=75 - (i * 5), hand="right")
          for i in range(len(fill_notes))],

        # Beat 4: Resolution chord
        *[Note(pitch=p, time=3.0, duration=1.0, velocity=75, hand="right")
          for p in voicing],
    ]

    return HandPattern(
        name="chord_fills",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 130),
        characteristics=["rhythmic", "transitional", "fills"]
    )


def octave_doubling_pattern(context: ChordContext) -> HandPattern:
    """Generate powerful octave-doubled melody.

    Pattern: Melody notes doubled in octaves for emphasis.
    Contemporary gospel power style (Kirk Franklin).

    Args:
        context: Chord context

    Returns:
        HandPattern with octave doubling
    """
    chord_tones = get_chord_tones(context.chord, octave=4)

    # Use chord tones as melodic sequence
    if len(chord_tones) >= 4:
        melody_sequence = [chord_tones[0], chord_tones[2], chord_tones[3], chord_tones[2]]
    elif len(chord_tones) >= 3:
        melody_sequence = [chord_tones[0], chord_tones[1], chord_tones[2], chord_tones[1]]
    else:
        melody_sequence = [chord_tones[0], chord_tones[1], chord_tones[0], chord_tones[1]]

    notes = []
    for i, note in enumerate(melody_sequence):
        beat_time = float(i)
        # Play note and its octave
        notes.append(Note(pitch=note, time=beat_time, duration=1.0, velocity=95, hand="right"))
        notes.append(Note(pitch=note + 12, time=beat_time, duration=1.0, velocity=90, hand="right"))

    return HandPattern(
        name="octave_doubling",
        notes=notes,
        difficulty="advanced",
        tempo_range=(100, 160),
        characteristics=["powerful", "contemporary", "energetic", "doubled"]
    )


def block_chord_pattern(context: ChordContext) -> HandPattern:
    """Generate sustained block chord voicing.

    Pattern: Full chord voicing sustained for entire bar.
    Worship/ballad style.

    Args:
        context: Chord context

    Returns:
        HandPattern with block chords
    """
    chord_tones = get_chord_tones(context.chord, octave=4)

    # Drop-2 voicing for rich sound (drop second-highest note by octave)
    if len(chord_tones) >= 4:
        # Sort and apply drop-2
        sorted_tones = sorted(chord_tones[:4])
        voicing = [
            sorted_tones[0],
            sorted_tones[2] - 12,  # Drop second-highest
            sorted_tones[2],
            sorted_tones[3]
        ]
    elif len(chord_tones) >= 3:
        # Simple close voicing
        voicing = chord_tones[:3]
    else:
        # Just play what we have
        voicing = chord_tones[:2]

    # Remove duplicates and sort
    voicing = sorted(list(set(voicing)))

    notes = [
        Note(pitch=p, time=0.0, duration=4.0, velocity=75, hand="right")
        for p in voicing
    ]

    return HandPattern(
        name="block_chord",
        notes=notes,
        difficulty="beginner",
        tempo_range=(50, 100),
        characteristics=["sustained", "harmonic", "worship", "simple"]
    )


def polychord_pattern(context: ChordContext) -> HandPattern:
    """Generate polychord voicing (upper structure triad).

    Pattern: Triad stacked on top of bass chord for modern sound.
    Jazz-gospel/modern gospel style.

    Args:
        context: Chord context

    Returns:
        HandPattern with polychord voicing
    """
    chord_tones = get_chord_tones(context.chord, octave=4)
    root = chord_tones[0]

    # Build upper structure triad
    # For major chords: stack major triad on 3rd (e.g., Cmaj9 = Em/C)
    # For dominant chords: stack major triad on 5th (e.g., G7 = D/G)
    root_note, quality, _ = parse_chord_symbol(context.chord)

    if "maj" in quality.lower():
        # Stack major triad on 3rd
        if len(chord_tones) >= 4:
            upper_root = chord_tones[1]  # 3rd
            upper_structure = [upper_root, upper_root + 4, upper_root + 7]  # Major triad
        else:
            upper_structure = chord_tones[:3]
    elif "7" in quality and "maj" not in quality.lower():
        # Dominant: stack major triad on 5th
        if len(chord_tones) >= 3:
            upper_root = chord_tones[2]  # 5th
            upper_structure = [upper_root, upper_root + 4, upper_root + 7]
        else:
            upper_structure = chord_tones[:3]
    else:
        # Default to close voicing
        upper_structure = chord_tones[:min(4, len(chord_tones))]

    notes = [
        Note(pitch=p, time=0.0, duration=4.0, velocity=80, hand="right")
        for p in upper_structure
    ]

    return HandPattern(
        name="polychord",
        notes=notes,
        difficulty="expert",
        tempo_range=(60, 140),
        characteristics=["modern", "jazz", "sophisticated", "upper_structure"]
    )


def arpeggiated_voicing_pattern(context: ChordContext) -> HandPattern:
    """Generate arpeggiated chord voicing.

    Pattern: Chord tones played as ascending/descending arpeggio.
    Contemporary ballad style.

    Args:
        context: Chord context

    Returns:
        HandPattern with arpeggiated voicing
    """
    chord_tones = get_chord_tones(context.chord, octave=4)

    # Extend to higher octave for full arpeggio
    if len(chord_tones) >= 4:
        arpeggio = chord_tones[:4] + [chord_tones[0] + 12]
    elif len(chord_tones) >= 3:
        arpeggio = chord_tones[:3] + [chord_tones[0] + 12]
    else:
        arpeggio = chord_tones + [chord_tones[0] + 12]

    # Ascending pattern in 16th notes (or 8th notes at slower tempo)
    note_duration = 0.5  # 8th notes
    notes = []

    for i, pitch in enumerate(arpeggio):
        time = i * note_duration
        if time < 4.0:  # Stay within 4 beats
            velocity = 70 + (i * 3)  # Slight crescendo
            notes.append(
                Note(pitch=pitch, time=time, duration=note_duration,
                     velocity=min(velocity, 90), hand="right")
            )

    return HandPattern(
        name="arpeggiated_voicing",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(60, 110),
        characteristics=["flowing", "arpeggiated", "ballad", "contemporary"]
    )


# Pattern generator registry
RIGHT_HAND_PATTERNS = {
    "melody_with_fills": melody_with_fills_pattern,
    "chord_fills": chord_fills_pattern,
    "octave_doubling": octave_doubling_pattern,
    "block_chord": block_chord_pattern,
    "polychord": polychord_pattern,
    "arpeggiated_voicing": arpeggiated_voicing_pattern,
}


def generate_right_hand_pattern(
    pattern_name: str,
    context: ChordContext
) -> HandPattern:
    """Generate a right hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context for pattern generation

    Returns:
        Generated HandPattern

    Raises:
        ValueError: If pattern name is unknown
    """
    if pattern_name not in RIGHT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown right hand pattern: {pattern_name}. "
            f"Available: {list(RIGHT_HAND_PATTERNS.keys())}"
        )

    generator = RIGHT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "melody_with_fills_pattern",
    "chord_fills_pattern",
    "octave_doubling_pattern",
    "block_chord_pattern",
    "polychord_pattern",
    "arpeggiated_voicing_pattern",
    "generate_right_hand_pattern",
    "RIGHT_HAND_PATTERNS",
]
