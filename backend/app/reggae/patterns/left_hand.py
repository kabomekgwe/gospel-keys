"""Reggae Left Hand Patterns

Implements authentic reggae bass patterns:
- Dub bass (heavy low-end roots)
- Walking bass (roots and 5ths)
- Offbeat bass (syncopated roots)
"""

from typing import List
from app.gospel import Note, ChordContext, HandPattern
from app.gospel.patterns.left_hand import get_chord_tones


# Available patterns
REGGAE_LEFT_HAND_PATTERNS = [
    "dub_bass",
    "walking_bass_reggae",
    "offbeat_bass",
    "roots_and_fifths"
]


def generate_reggae_left_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate reggae left hand pattern based on name and context.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context with key, chord, tempo info

    Returns:
        HandPattern with generated notes
    """
    pattern_map = {
        "dub_bass": _dub_bass,
        "walking_bass_reggae": _walking_bass_reggae,
        "offbeat_bass": _offbeat_bass,
        "roots_and_fifths": _roots_and_fifths
    }

    generator = pattern_map.get(pattern_name, _dub_bass)
    return generator(context)


def _dub_bass(context: ChordContext) -> HandPattern:
    """Heavy dub bass pattern - roots on beats 1 and 3.

    Classic reggae bass emphasizing low-end.
    """
    chord_tones = get_chord_tones(context.chord, octave=3)
    root = chord_tones[0]
    notes: List[Note] = []

    # Beats 1 and 3 - heavy roots
    for beat in [0.0, 2.0]:
        notes.append(Note(
            pitch=root - 12,  # Octave lower for heavy bass
            time=float(beat),
            duration=0.5,
            velocity=100,  # Heavy
            hand="left"
        ))

    return HandPattern(
        name="dub_bass",
        notes=notes,
        difficulty="beginner",
        tempo_range=(60, 90)
    )


def _walking_bass_reggae(context: ChordContext) -> HandPattern:
    """Walking bass pattern - roots, 5ths, and chromatic passing.

    Creates movement while maintaining reggae groove.
    """
    chord_tones = get_chord_tones(context.chord, octave=3)
    root = chord_tones[0]
    fifth = root + 7
    notes: List[Note] = []

    # Beat 1: Root
    notes.append(Note(
        pitch=root - 12,
        time=0.0,
        duration=0.5,
        velocity=90,
        hand="left"
    ))

    # Beat 2: Fifth
    notes.append(Note(
        pitch=fifth - 12,
        time=1.0,
        duration=0.5,
        velocity=70,
        hand="left"
    ))

    # Beat 3: Root
    notes.append(Note(
        pitch=root - 12,
        time=2.0,
        duration=0.5,
        velocity=85,
        hand="left"
    ))

    # Beat 4: Chromatic approach (leading to next chord)
    notes.append(Note(
        pitch=(root - 12) + 1,  # Half step below next root
        time=3.0,
        duration=0.5,
        velocity=65,
        hand="left"
    ))

    return HandPattern(
        name="walking_bass_reggae",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(70, 100)
    )


def _offbeat_bass(context: ChordContext) -> HandPattern:
    """Offbeat bass pattern - emphasizes upbeats.

    Syncopated roots on offbeats (2 and 4).
    """
    chord_tones = get_chord_tones(context.chord, octave=3)
    root = chord_tones[0]
    notes: List[Note] = []

    # Beats 2 and 4 (offbeats)
    for beat in [1.0, 3.0]:
        notes.append(Note(
            pitch=root - 12,
            time=float(beat),
            duration=0.25,
            velocity=85,
            hand="left"
        ))

    return HandPattern(
        name="offbeat_bass",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(80, 120)
    )


def _roots_and_fifths(context: ChordContext) -> HandPattern:
    """Roots and fifths pattern - stable foundation.

    Alternates between root and fifth notes.
    """
    chord_tones = get_chord_tones(context.chord, octave=3)
    root = chord_tones[0]
    fifth = root + 7
    notes: List[Note] = []

    # Beat 1: Root
    notes.append(Note(
        pitch=root - 12,
        time=0.0,
        duration=0.5,
        velocity=95,
        hand="left"
    ))

    # Beat 3: Fifth
    notes.append(Note(
        pitch=fifth - 12,
        time=2.0,
        duration=0.5,
        velocity=80,
        hand="left"
    ))

    return HandPattern(
        name="roots_and_fifths",
        notes=notes,
        difficulty="beginner",
        tempo_range=(60, 120)
    )
