
"""Neo-Soul Right Hand Patterns

Implements authentic neo-soul piano right hand patterns:
- Extended chord voicings (add9, maj7#11, m11)
- Suspended melody (sus2/4 tones)
- Sparse chord stabs (minimal off-beat hits)
- Arpeggiated extensions (9th/11th arpeggios)
- Chromatic fills (half-step approaches)

Key Neo-Soul Concepts:
- Extended harmonies with color tones
- Suspended sounds (sus2, sus4)
- Sparse, spacious voicings (less is more)
- Chromatic melodic movement
- Influences: D'Angelo, Erykah Badu, Robert Glasper, James Poyser
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext, HandPattern

# MIDI note mappings
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Extended neo-soul chord voicings (right hand, mid-high register)
NEOSOUL_VOICINGS = {
    "maj7": [7, 11, 14],         # 5th, maj7, 9th
    "maj9": [7, 11, 14],         # 5th, maj7, 9th
    "maj7#11": [11, 14, 18],     # maj7, 9th, #11
    "add9": [7, 14, 16],         # 5th, 9th, 10th
    "7": [7, 10, 14],            # 5th, b7, 9th
    "9": [10, 14, 16],           # b7, 9th, 10th
    "min7": [7, 10, 14],         # 5th, b7, 9th
    "m7": [7, 10, 14],           # 5th, b7, 9th
    "min9": [10, 14, 17],        # b7, 9th, 11
    "m9": [10, 14, 17],          # b7, 9th, 11
    "min11": [10, 14, 17],       # b7, 9th, 11
    "m11": [10, 14, 17],         # b7, 9th, 11
    "sus2": [2, 7, 14],          # 2nd, 5th, 9th
    "sus4": [5, 7, 12],          # 4th, 5th, octave
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
        quality = "maj"

    return root, quality


def get_root_midi(root: str, octave: int = 5) -> int:
    """Get MIDI note for root in right hand register."""
    return 12 * (octave + 1) + NOTE_TO_MIDI[root]


# Pattern Generators

def extended_chord_voicing_pattern(context: ChordContext, complexity: int = 5) -> HandPattern:
    """Generate extended chord voicing pattern.

    Rich extended voicings: add9, maj7#11, m11, 13th chords.
    Creates lush, sophisticated harmonies.

    Pattern:
    Sustained extended chord (whole note or dotted half)

    Args:
        context: Chord context
        complexity: Complexity level (1-10)

    Returns:
        HandPattern with extended voicing notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=4)

    # Get extended voicing
    if quality in NEOSOUL_VOICINGS:
        intervals = NEOSOUL_VOICINGS[quality]
    else:
        intervals = [7, 11, 14]  # Default: 5th, 7th, 9th

    voicing = [root_midi + interval for interval in intervals]

    notes = []

    if complexity < 4:
        # Low complexity: Pure sustained voicing (no movement)
        for pitch in voicing:
            notes.append(Note(
                pitch=pitch,
                time=0.0,
                duration=4.0,
                velocity=75,
                hand="right"
            ))
    elif complexity < 7:
        # Mid complexity: Shift on Beat 4 (Standard)
        # Beat 1-3
        for pitch in voicing:
            notes.append(Note(
                pitch=pitch,
                time=0.0,
                duration=3.0,
                velocity=75,
                hand="right"
            ))
        
        # Beat 4: Shifted voicing
        shifted_voicing = [root_midi + interval + 2 for interval in intervals[:2]]
        shifted_voicing.append(root_midi + intervals[2])
        for pitch in shifted_voicing:
            notes.append(Note(
                pitch=pitch,
                time=3.0,
                duration=1.0,
                velocity=70,
                hand="right"
            ))
    else:
        # High complexity: Shift on Beat 3 and 4 (More movement)
        # Beat 1-2
        for pitch in voicing:
            notes.append(Note(
                pitch=pitch,
                time=0.0,
                duration=2.0,
                velocity=75,
                hand="right"
            ))
        
        # Beat 3: Slightly altered (sus2 feel if possible)
        for pitch in [v + 2 for v in voicing]:
            notes.append(Note(
                pitch=pitch,
                time=2.0,
                duration=1.0,
                velocity=72,
                hand="right"
            ))
            
        # Beat 4: Resolution or tension
        shifted_voicing = [root_midi + interval + 2 for interval in intervals[:2]]
        shifted_voicing.append(root_midi + intervals[2])
        for pitch in shifted_voicing:
            notes.append(Note(
                pitch=pitch,
                time=3.0,
                duration=1.0,
                velocity=70,
                hand="right"
            ))

    return HandPattern(
        name="Extended Chord Voicing",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(60, 100),
        characteristics=["neosoul", "extended", "voicing", "harmonic"]
    )


def suspended_melody_pattern(context: ChordContext) -> HandPattern:
    """Generate suspended melody pattern.

    Melody using sus2/sus4 tones.
    Creates tension and resolution typical of neo-soul.

    Pattern:
    Suspended tones resolving to chord tones

    Args:
        context: Chord context

    Returns:
        HandPattern with suspended melody
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=5)

    notes = []

    # Beat 1: Sus4 (tension)
    sus4_note = root_midi + 5  # 4th
    notes.append(Note(
        pitch=sus4_note,
        time=0.0,
        duration=1.0,
        velocity=80,
        hand="right"
    ))

    # Beat 2: Resolve to 3rd
    third = 4 if "maj" in quality or quality == "7" else 3
    third_note = root_midi + third
    notes.append(Note(
        pitch=third_note,
        time=1.0,
        duration=1.5,
        velocity=75,
        hand="right"
    ))

    # Beat 3: Sus2 (tension)
    sus2_note = root_midi + 2  # 2nd
    notes.append(Note(
        pitch=sus2_note,
        time=2.5,
        duration=0.75,
        velocity=78,
        hand="right"
    ))

    # Beat 4: Resolve to root/9th
    ninth_note = root_midi + 14  # 9th
    notes.append(Note(
        pitch=ninth_note,
        time=3.25,
        duration=0.75,
        velocity=73,
        hand="right"
    ))

    return HandPattern(
        name="Suspended Melody",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 100),
        characteristics=["neosoul", "suspended", "melody", "tension"]
    )


def chord_stabs_sparse_pattern(context: ChordContext) -> HandPattern:
    """Generate sparse chord stabs pattern.

    Minimal off-beat chord hits.
    Creates space and groove (less is more).

    Pattern:
    Sparse chord stabs on off-beats (& of 2, & of 4)

    Args:
        context: Chord context

    Returns:
        HandPattern with sparse chord stabs
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=4)

    # Get voicing
    if quality in NEOSOUL_VOICINGS:
        intervals = NEOSOUL_VOICINGS[quality]
    else:
        intervals = [7, 11, 14]

    voicing = [root_midi + interval for interval in intervals]

    notes = []

    # & of 2: Chord stab
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=1.5,
            duration=0.4,
            velocity=80,
            hand="right"
        ))

    # & of 4: Chord stab (slightly softer)
    for pitch in voicing:
        notes.append(Note(
            pitch=pitch,
            time=3.5,
            duration=0.4,
            velocity=75,
            hand="right"
        ))

    return HandPattern(
        name="Sparse Chord Stabs",
        notes=notes,
        difficulty="beginner",
        tempo_range=(80, 110),
        characteristics=["neosoul", "sparse", "stabs", "syncopated"]
    )


def arpeggiated_extensions_pattern(context: ChordContext) -> HandPattern:
    """Generate arpeggiated extensions pattern.

    Arpeggios emphasizing 9ths, 11ths, 13ths.
    Creates flowing, cascading melodic lines.

    Pattern:
    8th note arpeggios through extended chord tones

    Args:
        context: Chord context

    Returns:
        HandPattern with arpeggiated extension notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=4)

    # Extended arpeggio pattern (9th, 11th, 13th)
    if "maj" in quality:
        arpeggio_intervals = [7, 11, 14, 18]  # 5th, 7th, 9th, 11th
    elif "min" in quality or "m" in quality:
        arpeggio_intervals = [7, 10, 14, 17]  # 5th, b7, 9th, 11th
    else:
        arpeggio_intervals = [7, 10, 14, 16]  # 5th, b7, 9th, 10th

    notes = []

    # Create 8th note arpeggio
    for i, interval in enumerate(arpeggio_intervals * 2):  # Repeat pattern
        time = i * 0.5  # 8th notes
        if time >= 4.0:
            break

        pitch = root_midi + interval
        note = Note(
            pitch=pitch,
            time=time,
            duration=0.4,
            velocity=80 - (i % 4) * 2,  # Slight dynamic variation
            hand="right"
        )
        notes.append(note)

    return HandPattern(
        name="Arpeggiated Extensions",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 110),
        characteristics=["neosoul", "arpeggio", "extensions", "eighth_notes"]
    )


def chromatic_fills_pattern(context: ChordContext) -> HandPattern:
    """Generate chromatic fills pattern.

    Half-step chromatic approaches and fills.
    Creates smooth melodic connections between chords.

    Pattern:
    Chromatic approach tones leading to chord tones

    Args:
        context: Chord context

    Returns:
        HandPattern with chromatic fill notes
    """
    root, quality = parse_chord_symbol(context.chord)
    root_midi = get_root_midi(root, octave=5)

    notes = []

    # Target: 5th of chord
    target_note = root_midi + 7  # 5th

    # Beat 1-2: Chromatic approach from below
    chromatic_phrase = [
        (0.0, target_note - 3, 0.5, 75),    # Start 3 semitones below
        (0.5, target_note - 2, 0.5, 78),    # Chromatic up
        (1.0, target_note - 1, 0.5, 80),    # Chromatic up
        (1.5, target_note, 1.0, 85),        # Resolve to target
    ]

    for time, pitch, duration, velocity in chromatic_phrase:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="right"
        ))

    # Beat 3-4: Chromatic fill to 9th
    target_note_2 = root_midi + 14  # 9th

    chromatic_phrase_2 = [
        (2.5, target_note_2 - 2, 0.5, 78),  # Start 2 semitones below
        (3.0, target_note_2 - 1, 0.5, 82),  # Chromatic up
        (3.5, target_note_2, 0.5, 85),      # Resolve to 9th
    ]

    for time, pitch, duration, velocity in chromatic_phrase_2:
        notes.append(Note(
            pitch=pitch,
            time=time,
            duration=duration,
            velocity=velocity,
            hand="right"
        ))

    return HandPattern(
        name="Chromatic Fills",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 100),
        characteristics=["neosoul", "chromatic", "fills", "melodic"]
    )


# Pattern library
NEOSOUL_RIGHT_HAND_PATTERNS = {
    "extended_chord_voicing": extended_chord_voicing_pattern,
    "suspended_melody": suspended_melody_pattern,
    "chord_stabs_sparse": chord_stabs_sparse_pattern,
    "arpeggiated_extensions": arpeggiated_extensions_pattern,
    "chromatic_fills": chromatic_fills_pattern,
}


def generate_neosoul_right_hand_pattern(pattern_name: str, context: ChordContext, complexity: int = 5) -> HandPattern:
    """Generate a neo-soul right hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context
        complexity: Complexity level (1-10)

    Returns:
        HandPattern with generated notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name not in NEOSOUL_RIGHT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown neo-soul right hand pattern: {pattern_name}. "
            f"Available: {list(NEOSOUL_RIGHT_HAND_PATTERNS.keys())}"
        )

    generator = NEOSOUL_RIGHT_HAND_PATTERNS[pattern_name]
    try:
        return generator(context, complexity=complexity)
    except TypeError:
        return generator(context)


__all__ = [
    "generate_neosoul_right_hand_pattern",
    "NEOSOUL_RIGHT_HAND_PATTERNS",
]
