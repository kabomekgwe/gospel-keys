"""Classical Piano Left Hand Patterns

Implements authentic classical piano left hand patterns:
- Alberti bass (Classical period arpeggiation)
- Waltz bass (3/4 time: root on 1, chord on 2-3)
- Broken chord classical (structured arpeggios)
- Bass melody counterpoint (independent melodic bass)
- Pedal tone (sustained bass with moving harmony)

Key Classical Concepts:
- Voice independence (each hand has melodic integrity)
- Strict voice leading (avoid parallel 5ths/octaves)
- Functional harmony (I-IV-V-I progressions)
- Period structure (antecedent-consequent phrases)
- Influences: Mozart, Haydn, Beethoven, Chopin
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Classical chord intervals (triadic harmony)
CLASSICAL_CHORD_INTERVALS = {
    "maj": [0, 4, 7],           # Major triad
    "min": [0, 3, 7],           # Minor triad
    "dim": [0, 3, 6],           # Diminished triad
    "aug": [0, 4, 8],           # Augmented triad
    "7": [0, 4, 7, 10],         # Dominant 7th
    "maj7": [0, 4, 7, 11],      # Major 7th
    "min7": [0, 3, 7, 10],      # Minor 7th
}


def parse_chord_symbol(chord: str) -> Tuple[str, str]:
    """Parse chord symbol into root and quality."""
    if len(chord) > 1 and chord[1] in ('b', '#'):
        root = chord[:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]

    # Default to major if no quality
    if not quality:
        quality = "maj"

    # Map common symbols
    if quality == "m":
        quality = "min"
    elif quality in ["", "M"]:
        quality = "maj"

    return root, quality


def get_root_midi(root: str, octave: int = 3) -> int:
    """Get MIDI note for root in left hand register."""
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


def get_chord_tones(chord: str, octave: int = 3) -> List[int]:
    """Get MIDI notes for chord tones."""
    root, quality = parse_chord_symbol(chord)
    root_midi = get_root_midi(root, octave)

    # Get intervals for chord quality
    base_quality = quality.replace("7", "").replace("maj", "").replace("min", "")
    if not base_quality:
        base_quality = "min" if "min" in quality or quality == "m" else "maj"

    intervals = CLASSICAL_CHORD_INTERVALS.get(quality) or CLASSICAL_CHORD_INTERVALS.get(base_quality) or [0, 4, 7]

    return [root_midi + interval for interval in intervals]


# Pattern Generators

def alberti_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate Alberti bass pattern (Classical period).

    Pattern: Low - High - Middle - High (arpeggiated)
    Typical of Mozart, Haydn piano sonatas.

    Args:
        context: Chord context

    Returns:
        HandPattern with Alberti bass notes
    """
    chord_tones = get_chord_tones(context.chord, octave=3)

    # Ensure we have at least 3 tones
    while len(chord_tones) < 3:
        chord_tones.append(chord_tones[0] + 12)

    root = chord_tones[0]
    third = chord_tones[1]
    fifth = chord_tones[2]

    notes = []

    # Alberti pattern: Low-High-Middle-High (in 8th notes)
    # 4 beats per bar
    for beat in range(4):
        time_offset = beat * 1.0

        # Low (root)
        notes.append(Note(
            pitch=root,
            time=time_offset + 0.0,
            duration=0.4,
            velocity=75,
            hand="left"
        ))

        # High (fifth)
        notes.append(Note(
            pitch=fifth,
            time=time_offset + 0.5,
            duration=0.4,
            velocity=70,
            hand="left"
        ))

    return HandPattern(
        name="Alberti Bass",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(80, 144),
        characteristics=["classical", "alberti", "arpeggiation", "eighth_notes"]
    )


def waltz_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate waltz bass pattern (3/4 time).

    Pattern: Root on beat 1, chord on beats 2-3
    Classic Viennese waltz accompaniment.

    Args:
        context: Chord context

    Returns:
        HandPattern with waltz bass notes
    """
    chord_tones = get_chord_tones(context.chord, octave=3)

    root = chord_tones[0]
    # Chord voicing (3rd + 5th or higher tones)
    chord_voicing = chord_tones[1:3] if len(chord_tones) >= 3 else [chord_tones[0] + 7]

    notes = []

    # Beat 1: Root (bass note)
    notes.append(Note(
        pitch=root,
        time=0.0,
        duration=0.9,
        velocity=85,  # Accent
        hand="left"
    ))

    # Beat 2: Chord
    for pitch in chord_voicing:
        notes.append(Note(
            pitch=pitch,
            time=1.0,
            duration=0.9,
            velocity=70,
            hand="left"
        ))

    # Beat 3: Chord (repeat)
    for pitch in chord_voicing:
        notes.append(Note(
            pitch=pitch,
            time=2.0,
            duration=0.9,
            velocity=68,
            hand="left"
        ))

    return HandPattern(
        name="Waltz Bass",
        notes=notes,
        difficulty="beginner",
        tempo_range=(120, 180),
        characteristics=["classical", "waltz", "3/4", "accompaniment"]
    )


def broken_chord_classical_pattern(context: ChordContext) -> HandPattern:
    """Generate classical broken chord pattern.

    Pattern: Ascending/descending arpeggios in structured rhythm
    More formal than gospel broken chords.

    Args:
        context: Chord context

    Returns:
        HandPattern with broken chord notes
    """
    chord_tones = get_chord_tones(context.chord, octave=3)

    # Extend to two octaves for fuller sound
    extended_tones = chord_tones + [t + 12 for t in chord_tones]

    notes = []

    # Ascending arpeggio (first 2 beats)
    for i, pitch in enumerate(extended_tones[:6]):
        notes.append(Note(
            pitch=pitch,
            time=i * 0.333,  # Triplet feel
            duration=0.3,
            velocity=75 - (i % 3) * 3,  # Slight dynamic shaping
            hand="left"
        ))

    # Descending arpeggio (last 2 beats)
    for i, pitch in enumerate(reversed(extended_tones[:6])):
        notes.append(Note(
            pitch=pitch,
            time=2.0 + i * 0.333,
            duration=0.3,
            velocity=72 - (i % 3) * 3,
            hand="left"
        ))

    return HandPattern(
        name="Broken Chord (Classical)",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(90, 160),
        characteristics=["classical", "arpeggio", "broken_chord", "triplets"]
    )


def bass_melody_counterpoint_pattern(context: ChordContext) -> HandPattern:
    """Generate independent melodic bass line (counterpoint).

    Pattern: Melodic bass that moves by step or small leaps
    Typical of Bach, Baroque counterpoint.

    Args:
        context: Chord context

    Returns:
        HandPattern with contrapuntal bass notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=3)

    notes = []

    # Create a stepwise melodic bass line
    # Example: Root -> scale step down -> third -> step up
    melodic_line = [
        (0.0, root_midi, 1.0, 80),           # Root
        (1.0, root_midi - 2, 1.0, 75),       # Step down (whole step)
        (2.0, root_midi + 4, 1.0, 78),       # Third
        (3.0, root_midi + 5, 1.0, 76),       # Fourth (passing tone)
    ]

    for time, pitch, duration, velocity in melodic_line:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="left"
        ))

    return HandPattern(
        name="Bass Melody Counterpoint",
        notes=notes,
        difficulty="advanced",
        tempo_range=(60, 120),
        characteristics=["classical", "counterpoint", "melodic_bass", "baroque"]
    )


def pedal_tone_pattern(context: ChordContext) -> HandPattern:
    """Generate pedal tone pattern.

    Pattern: Sustained bass note (pedal point) with moving harmony above
    Creates harmonic tension and resolution.

    Args:
        context: Chord context

    Returns:
        HandPattern with pedal tone notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=3)
    chord_tones = get_chord_tones(context.chord, octave=3)

    notes = []

    # Sustained pedal tone (root) - held for full bar
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=4.0,  # Whole note
        velocity=75,
        hand="left"
    ))

    # Moving harmony above the pedal (3rd and 5th)
    if len(chord_tones) >= 3:
        # Beat 1-2: Higher chord tones
        notes.append(Note(
            pitch=chord_tones[1],  # Third
            time=0.0,
            duration=2.0,
            velocity=65,
            hand="left"
        ))

        # Beat 3-4: Different voicing
        notes.append(Note(
            pitch=chord_tones[2],  # Fifth
            time=2.0,
            duration=2.0,
            velocity=63,
            hand="left"
        ))

    return HandPattern(
        name="Pedal Tone",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(60, 100),
        characteristics=["classical", "pedal_point", "sustained_bass", "romantic"]
    )


# Pattern library
CLASSICAL_LEFT_HAND_PATTERNS = {
    "alberti_bass": alberti_bass_pattern,
    "waltz_bass": waltz_bass_pattern,
    "broken_chord_classical": broken_chord_classical_pattern,
    "bass_melody_counterpoint": bass_melody_counterpoint_pattern,
    "pedal_tone": pedal_tone_pattern,
}


def generate_classical_left_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate a classical left hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in CLASSICAL_LEFT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown classical left hand pattern: {pattern_name}. "
            f"Available: {list(CLASSICAL_LEFT_HAND_PATTERNS.keys())}"
        )

    generator = CLASSICAL_LEFT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "generate_classical_left_hand_pattern",
    "CLASSICAL_LEFT_HAND_PATTERNS",
]
