"""Neo-Soul Left Hand Patterns

Implements authentic neo-soul piano left hand patterns:
- Broken chord arpeggios (9ths, 11ths, 13ths)
- Chromatic bass walks (half-step movement)
- Sustained root with pedal (low root, mid chords)
- Syncopated grooves (16th-note patterns)
- Low interval voicings (wide root + 7th)

Key Neo-Soul Concepts:
- Extended harmonies (add9, maj7#11, m11, 13th chords)
- Chromatic bass movement (D'Angelo style)
- 16th-note grooves with syncopation
- Wide voicings with space
- Influences: D'Angelo, Erykah Badu, Robert Glasper
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings (C2 = 36 is low C for left hand bass)
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Extended neo-soul chord intervals
NEOSOUL_CHORD_INTERVALS = {
    # Extended voicings with color tones
    "maj7": [0, 7, 11, 14],          # Root, 5th, 7th, 9th
    "maj9": [0, 7, 11, 14],          # Root, 5th, 7th, 9th
    "maj7#11": [0, 7, 11, 18],       # Root, 5th, 7th, #11
    "add9": [0, 4, 7, 14],           # Root, 3rd, 5th, 9th
    "7": [0, 7, 10, 14],             # Root, 5th, b7, 9th
    "9": [0, 7, 10, 14],             # Root, 5th, b7, 9th
    "min7": [0, 7, 10, 14],          # Root, 5th, b7, 9th
    "m7": [0, 7, 10, 14],            # Root, 5th, b7, 9th
    "min9": [0, 7, 10, 14],          # Root, 5th, b7, 9th
    "m9": [0, 7, 10, 14],            # Root, 5th, b7, 9th
    "min11": [0, 7, 10, 17],         # Root, 5th, b7, 11
    "m11": [0, 7, 10, 17],           # Root, 5th, b7, 11
    "sus2": [0, 2, 7],               # Root, 2nd, 5th
    "sus4": [0, 5, 7],               # Root, 4th, 5th
    "13": [0, 7, 10, 21],            # Root, 5th, b7, 13th
}


def parse_chord_symbol(chord: str) -> Tuple[str, str]:
    """Parse chord symbol into root and quality."""
    # Extract root note
    if len(chord) > 1 and chord[1] in ('b', '#'):
        root = chord[:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]

    # Default quality
    if not quality:
        quality = "maj"

    return root, quality


def get_root_note_midi(root: str, octave: int = 3) -> int:
    """Get MIDI note number for root note."""
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


def get_extended_voicing(chord: str, octave: int = 3) -> List[int]:
    """Get extended neo-soul voicing MIDI notes."""
    root, quality = parse_chord_symbol(chord)
    base_midi = get_root_note_midi(root, octave)

    # Get intervals for extended voicing
    if quality in NEOSOUL_CHORD_INTERVALS:
        intervals = NEOSOUL_CHORD_INTERVALS[quality]
    else:
        # Fallback to extended voicing
        intervals = [0, 7, 11, 14]  # Root, 5th, 7th, 9th

    return [base_midi + interval for interval in intervals]


# Pattern Generators

def broken_chord_arpeggio_pattern(context: ChordContext) -> HandPattern:
    """Generate broken chord arpeggio pattern with extended harmonies.

    Neo-soul arpeggios emphasize 9ths, 11ths, and 13ths.
    Creates flowing, cascading patterns.

    Pattern (4 beats of 16th notes):
    Ascending arpeggio through extended chord tones

    Args:
        context: Chord context

    Returns:
        HandPattern with arpeggio notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)  # Low octave for bass

    # Get extended voicing
    if quality in NEOSOUL_CHORD_INTERVALS:
        intervals = NEOSOUL_CHORD_INTERVALS[quality]
    else:
        intervals = [0, 7, 11, 14]  # Default extended

    # Create arpeggio pattern (16th notes)
    notes = []
    arpeggio = [root_midi + interval for interval in intervals]

    # Ascending pattern with some repetition
    pattern_notes = arpeggio + [arpeggio[2], arpeggio[1]]  # Up and back down

    for i, pitch in enumerate(pattern_notes):
        time = i * 0.25  # 16th notes
        if time >= 4.0:
            break

        note = Note(
            pitch=pitch,
            time=time,
            duration=0.2,
            velocity=80 - (i % 4) * 3,  # Slight dynamic variation
            hand="left"
        )
        notes.append(note)

    return HandPattern(
        name="Broken Chord Arpeggio",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 110),
        characteristics=["neosoul", "arpeggio", "extended", "16th_notes"]
    )


def chromatic_bass_walk_pattern(context: ChordContext) -> HandPattern:
    """Generate chromatic bass walk pattern.

    D'Angelo-style chromatic bass movement.
    Half-step approaches and chromatic fills.

    Pattern:
    - Beat 1: Root
    - Beat 2: Chromatic approach
    - Beat 3: Chord tone
    - Beat 4: Chromatic leading to next root

    Args:
        context: Chord context

    Returns:
        HandPattern with chromatic bass notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)

    notes = []

    # Beat 1: Root (sustained)
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=1.5,
        velocity=90,
        hand="left"
    ))

    # Beat 2: Chromatic approach (half-step above)
    notes.append(Note(
        pitch=root_midi + 1,
        time=1.5,
        duration=0.5,
        velocity=75,
        hand="left"
    ))

    # Beat 3: Chord tone (3rd or 5th)
    third = 4 if "maj" in quality or quality == "7" else 3
    notes.append(Note(
        pitch=root_midi + third,
        time=2.0,
        duration=1.0,
        velocity=85,
        hand="left"
    ))

    # Beat 4: Chromatic leading to next root
    if context.next_chord:
        next_root, _ = parse_chord_symbol(context.next_chord)
        next_root_midi = get_root_note_midi(next_root, octave=2)
        approach_note = next_root_midi - 1  # Half-step below
    else:
        approach_note = root_midi - 1

    notes.append(Note(
        pitch=approach_note,
        time=3.0,
        duration=1.0,
        velocity=80,
        hand="left"
    ))

    return HandPattern(
        name="Chromatic Bass Walk",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 100),
        characteristics=["neosoul", "chromatic", "bass_walk"]
    )


def sustained_root_with_pedal_pattern(context: ChordContext) -> HandPattern:
    """Generate sustained root with pedal pattern.

    Low root sustains throughout while mid-range chords move above.
    Creates space and depth typical of neo-soul.

    Pattern:
    - Low root (sustained whole note)
    - Mid-range chord hits on beats 2 and 4

    Args:
        context: Chord context

    Returns:
        HandPattern with pedal notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)  # Low root

    # Get mid-range chord voicing
    voicing = get_extended_voicing(context.chord, octave=3)

    notes = []

    # Sustained low root (whole note)
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=4.0,
        velocity=85,
        hand="left"
    ))

    # Mid-range chord on beat 2
    for pitch in voicing[1:]:  # Skip root (already in bass)
        notes.append(Note(
            pitch=pitch,
            time=1.0,
            duration=0.75,
            velocity=75,
            hand="left"
        ))

    # Mid-range chord on beat 4
    for pitch in voicing[1:]:
        notes.append(Note(
            pitch=pitch,
            time=3.0,
            duration=0.75,
            velocity=70,
            hand="left"
        ))

    return HandPattern(
        name="Sustained Root with Pedal",
        notes=notes,
        difficulty="beginner",
        tempo_range=(60, 90),
        characteristics=["neosoul", "pedal", "sustained"]
    )


def syncopated_groove_pattern(context: ChordContext) -> HandPattern:
    """Generate syncopated groove pattern.

    16th-note syncopated patterns typical of neo-soul.
    Off-beat accents and rhythmic displacement.

    Pattern:
    16th-note groove with off-beat accents

    Args:
        context: Chord context

    Returns:
        HandPattern with syncopated groove
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)

    voicing = get_extended_voicing(context.chord, octave=3)

    notes = []

    # 16th-note groove pattern
    # Beat 1: Root
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=0.25,
        velocity=90,
        hand="left"
    ))

    # & of 1: Chord
    for pitch in voicing[1:3]:
        notes.append(Note(
            pitch=pitch,
            time=0.5,
            duration=0.2,
            velocity=75,
            hand="left"
        ))

    # Beat 2: Root
    notes.append(Note(
        pitch=root_midi,
        time=1.0,
        duration=0.25,
        velocity=85,
        hand="left"
    ))

    # e & a of 2: Syncopated chord stabs
    for pitch in voicing[2:4]:
        notes.append(Note(
            pitch=pitch,
            time=1.75,
            duration=0.15,
            velocity=80,
            hand="left"
        ))

    # Beat 3: Root
    notes.append(Note(
        pitch=root_midi,
        time=2.0,
        duration=0.25,
        velocity=88,
        hand="left"
    ))

    # & of 3: Chord
    for pitch in voicing[1:3]:
        notes.append(Note(
            pitch=pitch,
            time=2.5,
            duration=0.2,
            velocity=73,
            hand="left"
        ))

    # Beat 4: Root
    notes.append(Note(
        pitch=root_midi,
        time=3.0,
        duration=0.25,
        velocity=86,
        hand="left"
    ))

    return HandPattern(
        name="Syncopated Groove",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(80, 110),
        characteristics=["neosoul", "groove", "syncopated", "16th_notes"]
    )


def low_interval_voicing_pattern(context: ChordContext) -> HandPattern:
    """Generate low interval voicing pattern.

    Wide voicings with root and 7th in low register.
    Creates depth and space.

    Pattern:
    - Root (low)
    - 7th (mid)
    - Sustained voicing

    Args:
        context: Chord context

    Returns:
        HandPattern with wide interval voicing
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)

    # Determine 7th
    if "maj" in quality:
        seventh = 11  # Major 7th
    else:
        seventh = 10  # Minor/dominant 7th

    notes = []

    # Low root
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=4.0,
        velocity=85,
        hand="left"
    ))

    # 7th in mid register (sustained)
    notes.append(Note(
        pitch=root_midi + seventh,
        time=0.0,
        duration=4.0,
        velocity=75,
        hand="left"
    ))

    return HandPattern(
        name="Low Interval Voicing",
        notes=notes,
        difficulty="beginner",
        tempo_range=(60, 100),
        characteristics=["neosoul", "interval", "wide_voicing"]
    )


# Pattern library
NEOSOUL_LEFT_HAND_PATTERNS = {
    "broken_chord_arpeggio": broken_chord_arpeggio_pattern,
    "chromatic_bass_walk": chromatic_bass_walk_pattern,
    "sustained_root_with_pedal": sustained_root_with_pedal_pattern,
    "syncopated_groove": syncopated_groove_pattern,
    "low_interval_voicing": low_interval_voicing_pattern,
}


def generate_neosoul_left_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate a neo-soul left hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in NEOSOUL_LEFT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown neo-soul left hand pattern: {pattern_name}. "
            f"Available: {list(NEOSOUL_LEFT_HAND_PATTERNS.keys())}"
        )

    generator = NEOSOUL_LEFT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "generate_neosoul_left_hand_pattern",
    "NEOSOUL_LEFT_HAND_PATTERNS",
    "parse_chord_symbol",
    "get_extended_voicing",
]
