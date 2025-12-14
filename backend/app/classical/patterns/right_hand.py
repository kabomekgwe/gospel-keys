"""Classical Piano Right Hand Patterns

Implements authentic classical piano right hand patterns:
- Melody solo (single-line melodies)
- Melody with accompaniment (melody + chord support)
- Scale runs (diatonic scalar passages)
- Arpeggios broken (virtuosic broken chords)
- Counterpoint melody (independent contrapuntal line)

Key Classical Concepts:
- Melodic contour (arch-shaped phrases)
- Stepwise motion (conjunct melodic movement)
- Ornaments (trills, turns, mordents)
- Phrasing (antecedent-consequent structure)
- Influences: Mozart, Beethoven, Chopin, Liszt
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Major scale intervals (diatonic)
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # W-W-H-W-W-W-H
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]  # W-H-W-W-H-W-W


def parse_chord_symbol(chord: str) -> Tuple[str, str]:
    """Parse chord symbol into root and quality."""
    if len(chord) > 1 and chord[1] in ('b', '#'):
        root = chord[:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]

    if not quality or quality == "M":
        quality = "maj"
    elif quality == "m":
        quality = "min"

    return root, quality


def get_root_midi(root: str, octave: int = 5) -> int:
    """Get MIDI note for root in right hand register."""
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


def get_scale_for_chord(chord: str, octave: int = 5) -> List[int]:
    """Get scale tones for a chord in MIDI."""
    root, quality = parse_chord_symbol(chord)
    root_midi = get_root_midi(root, octave)

    # Choose scale based on chord quality
    if "min" in quality or quality == "m":
        scale_intervals = MINOR_SCALE
    else:
        scale_intervals = MAJOR_SCALE

    return [root_midi + interval for interval in scale_intervals]


# Pattern Generators

def melody_solo_pattern(context: ChordContext) -> HandPattern:
    """Generate single-line melody pattern (Classical period).

    Pattern: Conjunct melodic motion with arch contour
    Typical of Mozart, Haydn melodies.

    Args:
        context: Chord context

    Returns:
        HandPattern with melody notes
    """
    scale_tones = get_scale_for_chord(context.chord, octave=5)

    notes = []

    # Create arch-shaped melodic phrase (ascending then descending)
    # Use scale degrees: 1-2-3-5-4-3-2-1
    melody_sequence = [
        (0.0, scale_tones[0], 1.0, 80),   # Root
        (1.0, scale_tones[1], 1.0, 82),   # 2nd
        (2.0, scale_tones[2], 1.0, 85),   # 3rd (peak starts)
        (3.0, scale_tones[4], 1.0, 83),   # 5th (peak)
    ]

    for time, pitch, duration, velocity in melody_sequence:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="right"
        ))

    return HandPattern(
        name="Melody Solo",
        notes=notes,
        difficulty="beginner",
        tempo_range=(80, 160),
        characteristics=["classical", "melody", "single_line", "conjunct"]
    )


def melody_with_accompaniment_pattern(context: ChordContext) -> HandPattern:
    """Generate melody with chord accompaniment.

    Pattern: Melody on top with supporting chord tones below
    Common in classical piano repertoire.

    Args:
        context: Chord context

    Returns:
        HandPattern with melody and accompaniment notes
    """
    scale_tones = get_scale_for_chord(context.chord, octave=5)
    chord_tones = scale_tones[::2]  # 1st, 3rd, 5th, 7th

    notes = []

    # Melody line (upper notes)
    melody = [
        (0.0, scale_tones[4], 2.0, 85),   # 5th (sustained)
        (2.0, scale_tones[2], 2.0, 83),   # 3rd (resolution)
    ]

    for time, pitch, duration, velocity in melody:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="right"
        ))

    # Accompaniment chords (lower notes, softer)
    # Beat 1 and 3: chord voicings
    for beat in [0, 2]:
        for i, pitch in enumerate(chord_tones[:3]):  # Lower 3 chord tones
            notes.append(Note(
                pitch=pitch - 12,  # Octave lower than melody
                time=beat,
                duration=1.9,
                velocity=65 - i * 3,  # Softer than melody
                hand="right"
            ))

    return HandPattern(
        name="Melody with Accompaniment",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 140),
        characteristics=["classical", "melody", "accompaniment", "homophonic"]
    )


def scale_runs_pattern(context: ChordContext) -> HandPattern:
    """Generate diatonic scale runs (virtuosic).

    Pattern: Fast ascending/descending scales
    Typical of Beethoven, Liszt passages.

    Args:
        context: Chord context

    Returns:
        HandPattern with scale run notes
    """
    scale_tones = get_scale_for_chord(context.chord, octave=5)

    # Extend to two octaves
    extended_scale = scale_tones + [t + 12 for t in scale_tones]

    notes = []

    # Ascending run (first 2 beats) - 16th notes
    for i, pitch in enumerate(extended_scale[:8]):
        notes.append(Note(
            pitch=pitch,
            time=i * 0.25,  # 16th notes
            duration=0.2,
            velocity=78 + (i % 4) * 2,  # Crescendo
            hand="right"
        ))

    # Descending run (last 2 beats)
    for i, pitch in enumerate(reversed(extended_scale[:8])):
        notes.append(Note(
            pitch=pitch,
            time=2.0 + i * 0.25,
            duration=0.2,
            velocity=85 - (i % 4) * 2,  # Diminuendo
            hand="right"
        ))

    return HandPattern(
        name="Scale Runs",
        notes=notes,
        difficulty="advanced",
        tempo_range=(100, 180),
        characteristics=["classical", "virtuosic", "scales", "sixteenth_notes"]
    )


def arpeggios_broken_pattern(context: ChordContext) -> HandPattern:
    """Generate broken arpeggio pattern (Chopin-style).

    Pattern: Flowing arpeggios spanning wide range
    Typical of Romantic piano writing.

    Args:
        context: Chord context

    Returns:
        HandPattern with arpeggio notes
    """
    scale_tones = get_scale_for_chord(context.chord, octave=4)
    # Use chord tones (1, 3, 5, 7)
    chord_tones = [scale_tones[0], scale_tones[2], scale_tones[4], scale_tones[6]]

    notes = []

    # Ascending arpeggio across 3 octaves (flowing)
    arpeggio_sequence = []
    for octave_shift in [0, 12, 24]:
        for tone in chord_tones:
            arpeggio_sequence.append(tone + octave_shift)

    # Generate notes (triplet feel)
    for i, pitch in enumerate(arpeggio_sequence[:12]):
        notes.append(Note(
            pitch=pitch,
            time=i * 0.333,  # Triplets
            duration=0.4,
            velocity=70 + (i % 3) * 3,  # Gentle dynamic wave
            hand="right"
        ))

    return HandPattern(
        name="Arpeggios (Broken)",
        notes=notes,
        difficulty="advanced",
        tempo_range=(60, 120),
        characteristics=["classical", "romantic", "arpeggios", "broken_chord"]
    )


def counterpoint_melody_pattern(context: ChordContext) -> HandPattern:
    """Generate independent contrapuntal melody (Bach-style).

    Pattern: Melodic line that moves independently
    Creates polyphonic texture.

    Args:
        context: Chord context

    Returns:
        HandPattern with contrapuntal melody notes
    """
    scale_tones = get_scale_for_chord(context.chord, octave=5)

    notes = []

    # Create a melodic line with clear direction and independence
    # Example: stepwise motion with occasional leaps
    contrapuntal_line = [
        (0.0, scale_tones[0], 0.5, 78),     # Root
        (0.5, scale_tones[1], 0.5, 76),     # 2nd (stepwise)
        (1.0, scale_tones[2], 0.5, 80),     # 3rd
        (1.5, scale_tones[4], 0.5, 82),     # 5th (leap)
        (2.0, scale_tones[3], 0.5, 79),     # 4th (stepwise down)
        (2.5, scale_tones[2], 0.5, 77),     # 3rd
        (3.0, scale_tones[1], 0.5, 75),     # 2nd
        (3.5, scale_tones[0], 0.5, 73),     # Root (resolution)
    ]

    for time, pitch, duration, velocity in contrapuntal_line:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="right"
        ))

    return HandPattern(
        name="Counterpoint Melody",
        notes=notes,
        difficulty="advanced",
        tempo_range=(60, 120),
        characteristics=["classical", "counterpoint", "baroque", "polyphonic"]
    )


# Pattern library
CLASSICAL_RIGHT_HAND_PATTERNS = {
    "melody_solo": melody_solo_pattern,
    "melody_with_accompaniment": melody_with_accompaniment_pattern,
    "scale_runs": scale_runs_pattern,
    "arpeggios_broken": arpeggios_broken_pattern,
    "counterpoint_melody": counterpoint_melody_pattern,
}


def generate_classical_right_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate a classical right hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in CLASSICAL_RIGHT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown classical right hand pattern: {pattern_name}. "
            f"Available: {list(CLASSICAL_RIGHT_HAND_PATTERNS.keys())}"
        )

    generator = CLASSICAL_RIGHT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "generate_classical_right_hand_pattern",
    "CLASSICAL_RIGHT_HAND_PATTERNS",
]
