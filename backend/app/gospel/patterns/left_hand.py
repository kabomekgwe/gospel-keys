"""Left Hand Gospel Piano Patterns

Implements traditional gospel, contemporary, and jazz-gospel left hand patterns:
- Stride bass (traditional Thomas Dorsey style)
- Walking bass (jazz-gospel Richard Smallwood style)
- Alberti bass (classical/contemporary blend)
- Shell voicing (modern minimalist)
- Syncopated comping (contemporary Kirk Franklin style)
"""

from typing import List, Tuple, Optional
from app.gospel import Note, ChordContext, HandPattern


# MIDI note mappings (C2 = 36 is low C for left hand bass)
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Interval mappings for chord construction
CHORD_INTERVALS = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "maj7": [0, 4, 7, 11],
    "7": [0, 4, 7, 10],
    "min7": [0, 3, 7, 10],
    "maj9": [0, 4, 7, 11, 14],
    "9": [0, 4, 7, 10, 14],
    "min9": [0, 3, 7, 10, 14],
    "maj13": [0, 4, 7, 11, 14, 21],
    "13": [0, 4, 7, 10, 14, 21],
    "min11": [0, 3, 7, 10, 14, 17],
    "11": [0, 4, 7, 10, 14, 17],
    "dim7": [0, 3, 6, 9],
    "m7b5": [0, 3, 6, 10],
    "sus4": [0, 5, 7],
}


def parse_chord_symbol(chord: str) -> Tuple[str, str, List[str]]:
    """Parse chord symbol into root, quality, and extensions.

    Args:
        chord: Chord symbol (e.g., "Cmaj9", "Dm7", "G7#9")

    Returns:
        Tuple of (root_note, quality, extensions)

    Examples:
        >>> parse_chord_symbol("Cmaj9")
        ("C", "maj9", [])
        >>> parse_chord_symbol("G7#9")
        ("G", "7", ["#9"])
    """
    # Extract root note
    if len(chord) > 1 and chord[1] in ('b', '#'):
        root = chord[:2]
        rest = chord[2:]
    else:
        root = chord[0]
        rest = chord[1:]

    # Extract quality and extensions
    extensions = []
    quality = rest

    # Handle alterations (#9, b9, #11, etc.)
    if '#' in rest or 'b' in rest:
        parts = rest.split('#')
        if len(parts) > 1:
            quality = parts[0]
            for p in parts[1:]:
                extensions.append(f"#{p}")
        else:
            parts = rest.split('b')
            quality = parts[0]
            for p in parts[1:]:
                if p and p[0].isdigit():
                    extensions.append(f"b{p}")

    # Default to major if no quality specified
    if not quality or quality.isdigit():
        quality = "maj" + quality if quality else "maj"

    return root, quality, extensions


def get_chord_tones(chord: str, octave: int = 2) -> List[int]:
    """Get MIDI note numbers for chord tones.

    Args:
        chord: Chord symbol (e.g., "Cmaj7")
        octave: Base octave (default 2 for left hand bass register)

    Returns:
        List of MIDI note numbers for chord tones
    """
    root, quality, _ = parse_chord_symbol(chord)

    # Get base MIDI note for root
    root_midi = NOTE_TO_MIDI.get(root, 0) + (octave * 12)

    # Find matching chord quality
    intervals = None
    for pattern, interval_list in CHORD_INTERVALS.items():
        if quality.startswith(pattern):
            intervals = interval_list
            break

    if intervals is None:
        # Default to major triad
        intervals = CHORD_INTERVALS["maj"]

    # Generate chord tones
    return [root_midi + interval for interval in intervals]


def stride_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate traditional gospel stride bass pattern.

    Pattern: Root (beat 1) -> Chord (beat 2) -> Root (beat 3) -> Chord (beat 4)
    Classic Thomas Dorsey/traditional gospel style.

    Args:
        context: Chord context with tempo and position info

    Returns:
        HandPattern with stride bass notes
    """
    chord_tones = get_chord_tones(context.chord, octave=2)
    root = chord_tones[0]

    # Chord voicing (3rd and 7th, or available tones)
    if len(chord_tones) >= 4:
        chord_notes = [chord_tones[2], chord_tones[3]]  # 5th and 7th
    elif len(chord_tones) >= 3:
        chord_notes = [chord_tones[1], chord_tones[2]]  # 3rd and 5th
    else:
        chord_notes = [chord_tones[1]]  # Just 3rd

    # Higher octave root for variety
    root_high = root + 12

    notes = [
        # Beat 1: Low root
        Note(pitch=root, time=0.0, duration=1.0, velocity=90, hand="left"),

        # Beat 2: Chord tones
        *[Note(pitch=p, time=1.0, duration=1.0, velocity=75, hand="left")
          for p in chord_notes],

        # Beat 3: High root
        Note(pitch=root_high, time=2.0, duration=1.0, velocity=85, hand="left"),

        # Beat 4: Chord tones (repeat)
        *[Note(pitch=p, time=3.0, duration=1.0, velocity=70, hand="left")
          for p in chord_notes],
    ]

    return HandPattern(
        name="stride_bass",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(60, 140),
        characteristics=["rhythmic", "traditional", "energetic"]
    )


def walking_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate jazz-gospel walking bass pattern.

    Pattern: Four quarter notes connecting chord tones chromatically
    Richard Smallwood/jazz-gospel style.

    Args:
        context: Chord context with voice leading info

    Returns:
        HandPattern with walking bass notes
    """
    chord_tones = get_chord_tones(context.chord, octave=2)
    root = chord_tones[0]

    # Get next chord root for voice leading
    next_root = root
    if context.next_chord:
        next_chord_tones = get_chord_tones(context.next_chord, octave=2)
        next_root = next_chord_tones[0]

    # Build walking line: root -> 3rd -> 5th -> chromatic approach to next root
    if len(chord_tones) >= 3:
        # Standard walking pattern
        beat_1 = root
        beat_2 = chord_tones[1]  # 3rd
        beat_3 = chord_tones[2]  # 5th

        # Chromatic approach to next root (half step below)
        if next_root > beat_3:
            beat_4 = next_root - 1  # Approach from below
        else:
            beat_4 = next_root + 1  # Approach from above

        notes = [
            Note(pitch=beat_1, time=0.0, duration=1.0, velocity=85, hand="left"),
            Note(pitch=beat_2, time=1.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=beat_3, time=2.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=beat_4, time=3.0, duration=1.0, velocity=75, hand="left"),
        ]
    else:
        # Simplified for dyads
        notes = [
            Note(pitch=root, time=0.0, duration=1.0, velocity=85, hand="left"),
            Note(pitch=chord_tones[1], time=1.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=root + 12, time=2.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=chord_tones[1], time=3.0, duration=1.0, velocity=75, hand="left"),
        ]

    return HandPattern(
        name="walking_bass",
        notes=notes,
        difficulty="advanced",
        tempo_range=(80, 160),
        characteristics=["melodic", "jazz", "smooth", "chromatic"]
    )


def alberti_bass_pattern(context: ChordContext) -> HandPattern:
    """Generate Alberti bass arpeggiation pattern.

    Pattern: Root -> 3rd -> 5th -> 3rd (arpeggiated)
    Classical/contemporary gospel blend.

    Args:
        context: Chord context

    Returns:
        HandPattern with arpeggiated notes
    """
    chord_tones = get_chord_tones(context.chord, octave=2)

    # Ensure we have at least 3 tones
    if len(chord_tones) < 3:
        chord_tones.append(chord_tones[0] + 12)  # Add octave

    root = chord_tones[0]
    third = chord_tones[1]
    fifth = chord_tones[2] if len(chord_tones) >= 3 else chord_tones[1] + 12

    # Alberti pattern: Low High Middle High (in 16th notes)
    notes = [
        # Beat 1
        Note(pitch=root, time=0.0, duration=0.5, velocity=75, hand="left"),
        Note(pitch=fifth, time=0.5, duration=0.5, velocity=70, hand="left"),
        Note(pitch=third, time=1.0, duration=0.5, velocity=70, hand="left"),
        Note(pitch=fifth, time=1.5, duration=0.5, velocity=65, hand="left"),

        # Beat 2 (repeat)
        Note(pitch=root, time=2.0, duration=0.5, velocity=75, hand="left"),
        Note(pitch=fifth, time=2.5, duration=0.5, velocity=70, hand="left"),
        Note(pitch=third, time=3.0, duration=0.5, velocity=70, hand="left"),
        Note(pitch=fifth, time=3.5, duration=0.5, velocity=65, hand="left"),
    ]

    return HandPattern(
        name="alberti_bass",
        notes=notes,
        difficulty="beginner",
        tempo_range=(60, 120),
        characteristics=["arpeggiated", "flowing", "classical"]
    )


def shell_voicing_pattern(context: ChordContext) -> HandPattern:
    """Generate modern shell voicing pattern.

    Pattern: Root + (3rd + 7th) sustained
    Modern minimalist gospel style.

    Args:
        context: Chord context

    Returns:
        HandPattern with shell voicing
    """
    chord_tones = get_chord_tones(context.chord, octave=2)
    root = chord_tones[0]

    # Shell: root in bass + 3rd and 7th in mid-range
    if len(chord_tones) >= 4:
        # Full shell: root + 3rd + 7th
        notes = [
            Note(pitch=root, time=0.0, duration=4.0, velocity=85, hand="left"),
            Note(pitch=chord_tones[1] + 12, time=0.0, duration=4.0, velocity=75, hand="left"),  # 3rd up octave
            Note(pitch=chord_tones[3] + 12, time=0.0, duration=4.0, velocity=75, hand="left"),  # 7th up octave
        ]
    elif len(chord_tones) >= 3:
        # Simplified shell: root + 3rd + 5th
        notes = [
            Note(pitch=root, time=0.0, duration=4.0, velocity=85, hand="left"),
            Note(pitch=chord_tones[1] + 12, time=0.0, duration=4.0, velocity=75, hand="left"),
            Note(pitch=chord_tones[2] + 12, time=0.0, duration=4.0, velocity=75, hand="left"),
        ]
    else:
        # Minimal: root + 3rd
        notes = [
            Note(pitch=root, time=0.0, duration=4.0, velocity=85, hand="left"),
            Note(pitch=chord_tones[1] + 12, time=0.0, duration=4.0, velocity=75, hand="left"),
        ]

    return HandPattern(
        name="shell_voicing",
        notes=notes,
        difficulty="beginner",
        tempo_range=(50, 100),
        characteristics=["sustained", "minimal", "modern", "sparse"]
    )


def syncopated_comping_pattern(context: ChordContext) -> HandPattern:
    """Generate syncopated gospel comping pattern.

    Pattern: Off-beat chord stabs with backbeat emphasis
    Contemporary Kirk Franklin/modern gospel style.

    Args:
        context: Chord context

    Returns:
        HandPattern with syncopated chords
    """
    chord_tones = get_chord_tones(context.chord, octave=2)

    # Use mid-register chord voicing (3rd, 5th, 7th)
    if len(chord_tones) >= 4:
        voicing = [chord_tones[1] + 12, chord_tones[2] + 12, chord_tones[3] + 12]
    elif len(chord_tones) >= 3:
        voicing = [chord_tones[1] + 12, chord_tones[2] + 12]
    else:
        voicing = [chord_tones[1] + 12]

    # Syncopated rhythm: off-beat stabs with backbeat emphasis
    notes = [
        # Beat 1.5 (off-beat)
        *[Note(pitch=p, time=0.5, duration=0.5, velocity=75, hand="left") for p in voicing],

        # Beat 2 (backbeat - stronger)
        *[Note(pitch=p, time=2.0, duration=0.5, velocity=90, hand="left") for p in voicing],

        # Beat 3.5 (off-beat)
        *[Note(pitch=p, time=2.5, duration=0.5, velocity=70, hand="left") for p in voicing],

        # Beat 4 (backbeat - stronger)
        *[Note(pitch=p, time=3.0, duration=1.0, velocity=95, hand="left") for p in voicing],
    ]

    return HandPattern(
        name="syncopated_comping",
        notes=notes,
        difficulty="advanced",
        tempo_range=(100, 160),
        characteristics=["syncopated", "rhythmic", "contemporary", "energetic"]
    )


# Pattern generator registry
LEFT_HAND_PATTERNS = {
    "stride_bass": stride_bass_pattern,
    "walking_bass": walking_bass_pattern,
    "alberti_bass": alberti_bass_pattern,
    "shell_voicing": shell_voicing_pattern,
    "syncopated_comping": syncopated_comping_pattern,
}


def generate_left_hand_pattern(
    pattern_name: str,
    context: ChordContext
) -> HandPattern:
    """Generate a left hand pattern by name.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context for pattern generation

    Returns:
        Generated HandPattern

    Raises:
        ValueError: If pattern name is unknown
    """
    if pattern_name not in LEFT_HAND_PATTERNS:
        raise ValueError(
            f"Unknown left hand pattern: {pattern_name}. "
            f"Available: {list(LEFT_HAND_PATTERNS.keys())}"
        )

    generator = LEFT_HAND_PATTERNS[pattern_name]
    return generator(context)


__all__ = [
    "stride_bass_pattern",
    "walking_bass_pattern",
    "alberti_bass_pattern",
    "shell_voicing_pattern",
    "syncopated_comping_pattern",
    "generate_left_hand_pattern",
    "LEFT_HAND_PATTERNS",
]
