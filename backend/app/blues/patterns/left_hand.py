"""Blues Piano Left Hand Patterns

Implements authentic blues piano left hand patterns:
- Boogie-woogie (classic root-3-5-6 pattern)
- Shuffle bass (root on 1+3, chord on 2+4)
- Walking blues bass (12-bar blues progression)
- Blues chord voicings (7th chords with blue notes)
- Octave bass (root doubled with shuffle feel)

Key Blues Concepts:
- Shuffle rhythm (triplet feel, swung 8ths)
- Boogie-woogie bass: repetitive root-3-5-6-5-3 pattern
- 12-bar blues form (I-I-I-I-IV-IV-I-I-V-IV-I-I)
- Dominant 7th chords throughout
- Influences: Albert Ammons, Pete Johnson, Otis Spann
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Blues chord intervals
BLUES_CHORD_INTERVALS = {
    "7": [0, 4, 7, 10],          # Dominant 7th (root, 3rd, 5th, b7)
    "9": [0, 4, 7, 10, 14],      # Dominant 9th
    "maj": [0, 4, 7],            # Major triad
    "min": [0, 3, 7],            # Minor triad
}


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


def get_root_note_midi(root: str, octave: int = 2) -> int:
    """Get MIDI note number for root note in bass register."""
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


# Pattern Generators

def boogie_woogie_pattern(context: ChordContext) -> HandPattern:
    """Generate classic boogie-woogie bass pattern.

    The iconic boogie-woogie pattern: root-3-5-6-5-3 (or variations).
    Continuous 8th-note pulse with shuffle feel.

    Pattern (8 beats of shuffled 8th notes):
    Root, 3rd, 5th, 6th, 5th, 3rd, Root, 3rd...

    Args:
        context: Chord context

    Returns:
        HandPattern with boogie-woogie bass notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)

    # Boogie-woogie intervals: root, 3rd, 5th, 6th
    intervals = [0, 4, 7, 9]  # Root, major 3rd, 5th, 6th

    notes = []

    # Classic boogie pattern (8 8th notes): R-3-5-6-5-3-R-3
    boogie_sequence = [0, 1, 2, 3, 2, 1, 0, 1]  # Indices into intervals array

    for i, interval_idx in enumerate(boogie_sequence):
        time = i * 0.5  # 8th notes
        pitch = root_midi + intervals[interval_idx]

        note = Note(
            pitch=pitch,
            time=time,
            duration=0.45,  # Slightly shorter for shuffle articulation
            velocity=85 if i % 2 == 0 else 75,  # Accent on beats
            hand="left"
        )
        notes.append(note)

    return HandPattern(
        name="Boogie-Woogie",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(100, 160),
        characteristics=["blues", "boogie_woogie", "eighth_notes", "shuffle"]
    )


def shuffle_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate shuffle bass pattern.

    Root on beats 1 and 3, chord voicing on beats 2 and 4.
    Classic blues shuffle feel.

    Pattern:
    - Beats 1, 3: Low root (bass)
    - Beats 2, 4: Mid-range chord voicing

    Args:
        context: Chord context

    Returns:
        HandPattern with shuffle bass notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi_low = get_root_note_midi(root, octave=2)

    # Get chord voicing for beats 2 and 4
    if quality in BLUES_CHORD_INTERVALS:
        intervals = BLUES_CHORD_INTERVALS[quality]
    else:
        intervals = [0, 4, 7, 10]  # Default to dom7

    chord_voicing = [root_midi_low + interval + 12 for interval in intervals[1:3]]  # 3rd and 5th up an octave

    notes = []

    # Beat 1: Low root
    notes.append(Note(
        pitch=root_midi_low,
        time=0.0,
        duration=1.0,
        velocity=90,
        hand="left"
    ))

    # Beat 2: Chord voicing
    for pitch in chord_voicing:
        notes.append(Note(
            pitch=pitch,
            time=1.0,
            duration=0.8,
            velocity=75,
            hand="left"
        ))

    # Beat 3: Low root
    notes.append(Note(
        pitch=root_midi_low,
        time=2.0,
        duration=1.0,
        velocity=88,
        hand="left"
    ))

    # Beat 4: Chord voicing
    for pitch in chord_voicing:
        notes.append(Note(
            pitch=pitch,
            time=3.0,
            duration=0.8,
            velocity=73,
            hand="left"
        ))

    return HandPattern(
        name="Shuffle Bass",
        notes=notes,
        difficulty="beginner",
        tempo_range=(80, 140),
        characteristics=["blues", "shuffle", "swing"]
    )


def walking_blues_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate walking blues bass pattern.

    Quarter-note walking bass with blues scale tones.
    Walks through chord tones and passing tones.

    Pattern (4 beats):
    Root, 3rd, 5th, chromatic approach to next root

    Args:
        context: Chord context

    Returns:
        HandPattern with walking blues bass notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)

    notes = []

    # Beat 1: Root
    notes.append(Note(
        pitch=root_midi,
        time=0.0,
        duration=1.0,
        velocity=90,
        hand="left"
    ))

    # Beat 2: 3rd (major or minor depending on context, but blues uses both)
    third = 4  # Major 3rd (blues often uses both major and minor 3rds)
    notes.append(Note(
        pitch=root_midi + third,
        time=1.0,
        duration=1.0,
        velocity=85,
        hand="left"
    ))

    # Beat 3: 5th
    notes.append(Note(
        pitch=root_midi + 7,
        time=2.0,
        duration=1.0,
        velocity=83,
        hand="left"
    ))

    # Beat 4: b7 or chromatic approach to next root
    if context.next_chord:
        next_root, _ = parse_chord_symbol(context.next_chord)
        next_root_midi = get_root_note_midi(next_root, octave=2)
        # Chromatic approach from below
        approach_note = next_root_midi - 1
    else:
        # Use b7 of current chord
        approach_note = root_midi + 10

    notes.append(Note(
        pitch=approach_note,
        time=3.0,
        duration=1.0,
        velocity=80,
        hand="left"
    ))

    return HandPattern(
        name="Walking Blues Bass",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(90, 160),
        characteristics=["blues", "walking", "quarter_notes"]
    )


def blues_chord_voicing_pattern(context: ChordContext) -> HandPattern:
    """Generate blues chord voicing pattern.

    Full dominant 7th chord voicings in left hand.
    Typical of piano blues comping.

    Pattern:
    Sustained 7th chord voicing (whole note or half notes)

    Args:
        context: Chord context

    Returns:
        HandPattern with blues chord voicing
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_note_midi(root, octave=2)

    # Get dominant 7th voicing
    if quality in BLUES_CHORD_INTERVALS:
        intervals = BLUES_CHORD_INTERVALS[quality]
    else:
        intervals = [0, 4, 7, 10]  # Dom7

    voicing = [root_midi + interval for interval in intervals]

    notes = []

    # Beat 1-2: Full chord
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=0.0,
            duration=2.0,
            velocity=80,
            hand="left"
        ))

    # Beat 3-4: Same chord (could vary slightly)
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=2.0,
            duration=2.0,
            velocity=75,
            hand="left"
        ))

    return HandPattern(
        name="Blues Chord Voicing",
        notes=notes,
        difficulty="beginner",
        tempo_range=(60, 120),
        characteristics=["blues", "chord", "voicing"]
    )


def octave_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate octave bass pattern with shuffle.

    Root note doubled in octaves with shuffle feel.
    Creates powerful bass sound.

    Pattern:
    Root (low) + Root (high) on beats 1 and 3

    Args:
        context: Chord context

    Returns:
        HandPattern with octave bass notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi_low = get_root_note_midi(root, octave=2)
    root_midi_high = root_midi_low + 12  # Octave above

    notes = []

    # Beat 1: Octave root
    notes.append(Note(
        pitch=root_midi_low,
        time=0.0,
        duration=1.0,
        velocity=95,
        hand="left"
    ))
    notes.append(Note(
        pitch=root_midi_high,
        time=0.0,
        duration=1.0,
        velocity=90,
        hand="left"
    ))

    # Beat 2.5: Passing note (5th)
    notes.append(Note(
        pitch=root_midi_low + 7,
        time=1.5,
        duration=0.5,
        velocity=75,
        hand="left"
    ))

    # Beat 3: Octave root
    notes.append(Note(
        pitch=root_midi_low,
        time=2.0,
        duration=1.0,
        velocity=93,
        hand="left"
    ))
    notes.append(Note(
        pitch=root_midi_high,
        time=2.0,
        duration=1.0,
        velocity=88,
        hand="left"
    ))

    # Beat 4.5: Passing note (6th)
    notes.append(Note(
        pitch=root_midi_low + 9,
        time=3.5,
        duration=0.5,
        velocity=73,
        hand="left"
    ))

    return HandPattern(
        name="Octave Bass",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(100, 180),
        characteristics=["blues", "octaves", "shuffle", "powerful"]
    )


# Pattern library
BLUES_LEFT_HAND_PATTERNS = {
    "boogie_woogie": boogie_woogie_pattern,
    "shuffle_bass": shuffle_bass_pattern,
    "walking_blues_bass": walking_blues_bass_pattern,
    "blues_chord_voicing": blues_chord_voicing_pattern,
    "octave_bass": octave_bass_pattern,
}


def generate_blues_left_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate a blues left hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in BLUES_LEFT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown blues left hand pattern: {pattern_name}. "
            f"Available: {list(BLUES_LEFT_HAND_PATTERNS.keys())}"
        )

    generator = BLUES_LEFT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "generate_blues_left_hand_pattern",
    "BLUES_LEFT_HAND_PATTERNS",
    "parse_chord_symbol",
]
