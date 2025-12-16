"""Reggae Left Hand Patterns

Implements authentic reggae bass patterns:
- Dub bass (heavy low-end roots)
- Walking bass (roots and 5ths)
- Offbeat bass (syncopated roots)
"""

from typing import List
from app.gospel import Note, ChordContext, HandPattern


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
    root = context.root_note
    notes: List[Note] = []

    # Beats 1 and 3 - heavy roots
    for beat in [0.0, 2.0]:
        notes.append(Note(
            pitch=root - 12,  # Octave lower for heavy bass
            time=context.bar_start + beat,
            duration=0.5,
            velocity=100  # Heavy
        ))

    return HandPattern(notes=notes, pattern_name="dub_bass")


def _walking_bass_reggae(context: ChordContext) -> HandPattern:
    """Walking bass pattern - roots, 5ths, and chromatic passing.

    Creates movement while maintaining reggae groove.
    """
    root = context.root_note
    fifth = root + 7
    notes: List[Note] = []

    # Beat 1: Root
    notes.append(Note(
        pitch=root - 12,
        time=context.bar_start,
        duration=0.5,
        velocity=90
    ))

    # Beat 2: Fifth
    notes.append(Note(
        pitch=fifth - 12,
        time=context.bar_start + 1.0,
        duration=0.5,
        velocity=70
    ))

    # Beat 3: Root
    notes.append(Note(
        pitch=root - 12,
        time=context.bar_start + 2.0,
        duration=0.5,
        velocity=85
    ))

    # Beat 4: Chromatic approach (leading to next chord)
    notes.append(Note(
        pitch=(root - 12) + 1,  # Half step below next root
        time=context.bar_start + 3.0,
        duration=0.5,
        velocity=65
    ))

    return HandPattern(notes=notes, pattern_name="walking_bass_reggae")


def _offbeat_bass(context: ChordContext) -> HandPattern:
    """Offbeat bass pattern - emphasizes upbeats.

    Syncopated roots on offbeats (2 and 4).
    """
    root = context.root_note
    notes: List[Note] = []

    # Beats 2 and 4 (offbeats)
    for beat in [1.0, 3.0]:
        notes.append(Note(
            pitch=root - 12,
            time=context.bar_start + beat,
            duration=0.25,
            velocity=85
        ))

    return HandPattern(notes=notes, pattern_name="offbeat_bass")


def _roots_and_fifths(context: ChordContext) -> HandPattern:
    """Roots and fifths pattern - stable foundation.

    Alternates between root and fifth notes.
    """
    root = context.root_note
    fifth = root + 7
    notes: List[Note] = []

    # Beat 1: Root
    notes.append(Note(
        pitch=root - 12,
        time=context.bar_start,
        duration=0.5,
        velocity=95
    ))

    # Beat 3: Fifth
    notes.append(Note(
        pitch=fifth - 12,
        time=context.bar_start + 2.0,
        duration=0.5,
        velocity=80
    ))

    return HandPattern(notes=notes, pattern_name="roots_and_fifths")
