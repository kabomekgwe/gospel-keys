"""Reggae Right Hand Patterns

Implements authentic reggae chord patterns:
- Skank (offbeat chord stabs)
- Bubble rhythm (sustained chords with accent)
- Double skank (two offbeat hits per bar)
"""

from typing import List
from app.gospel import Note, ChordContext, HandPattern
from app.gospel.patterns.left_hand import get_chord_tones


# Available patterns
REGGAE_RIGHT_HAND_PATTERNS = [
    "skank",
    "bubble_rhythm",
    "double_skank",
    "sustained_chords"
]


def generate_reggae_right_hand_pattern(pattern_name: str, context: ChordContext) -> HandPattern:
    """Generate reggae right hand pattern based on name and context.

    Args:
        pattern_name: Name of pattern to generate
        context: Chord context with key, chord, tempo info

    Returns:
        HandPattern with generated notes
    """
    pattern_map = {
        "skank": _skank,
        "bubble_rhythm": _bubble_rhythm,
        "double_skank": _double_skank,
        "sustained_chords": _sustained_chords
    }

    generator = pattern_map.get(pattern_name, _skank)
    return generator(context)


def _skank(context: ChordContext) -> HandPattern:
    """Classic reggae skank - offbeat chord stabs.

    Staccato chords on beats 2 and 4 (the upbeats).
    """
    notes: List[Note] = []
    # Take up to 4 notes
    chord_notes = get_chord_tones(context.chord, octave=4, previous_voicing=context.previous_voicing)[:4]

    # Beats 2 and 4 - offbeat emphasis
    for beat in [1.0, 3.0]:
        for note_pitch in chord_notes:
            notes.append(Note(
                pitch=note_pitch + 12,  # Octave up for brightness
                time=float(beat),
                duration=0.15,  # Short, staccato
                velocity=70,
                hand="right"
            ))

    return HandPattern(
        name="skank",
        notes=notes,
        difficulty="beginner",
        tempo_range=(60, 120)
    )


def _bubble_rhythm(context: ChordContext) -> HandPattern:
    """Bubble rhythm - sustained chords with accent on 3.

    Characteristic reggae keyboard pattern.
    """
    notes: List[Note] = []
    chord_notes = get_chord_tones(context.chord, octave=4, previous_voicing=context.previous_voicing)[:4]

    # Sustained chord with accent on beat 3
    for note_pitch in chord_notes:
        # Beat 1: Start sustained
        notes.append(Note(
            pitch=note_pitch + 12,
            time=0.0,
            duration=2.5,  # Hold through beat 3
            velocity=60,
            hand="right"
        ))

        # Beat 3: Accent
        notes.append(Note(
            pitch=note_pitch + 12,
            time=2.0,
            duration=1.5,
            velocity=85,  # Accented
            hand="right"
        ))

    return HandPattern(
        name="bubble_rhythm",
        notes=notes,
        difficulty="intermediate",
        tempo_range=(60, 100)
    )


def _double_skank(context: ChordContext) -> HandPattern:
    """Double skank - two quick offbeat hits.

    More active skank pattern with doubled hits.
    """
    notes: List[Note] = []
    chord_notes = get_chord_tones(context.chord, octave=4, previous_voicing=context.previous_voicing)[:4]

    # Two quick hits on offbeats
    for beat in [1.0, 1.25, 3.0, 3.25]:
        for note_pitch in chord_notes:
            notes.append(Note(
                pitch=note_pitch + 12,
                time=float(beat),
                duration=0.1,  # Very short
                velocity=65,
                hand="right"
            ))

    return HandPattern(
        name="double_skank",
        notes=notes,
        difficulty="advanced",
        tempo_range=(80, 120)
    )


def _sustained_chords(context: ChordContext) -> HandPattern:
    """Sustained chords - whole bar voicings.

    Simple sustained harmony for laid-back feel.
    """
    notes: List[Note] = []
    chord_notes = get_chord_tones(context.chord, octave=4, previous_voicing=context.previous_voicing)[:4]

    # Sustain entire bar
    for note_pitch in chord_notes:
        notes.append(Note(
            pitch=note_pitch + 12,
            time=0.0,
            duration=4.0,  # Full bar
            velocity=55,
            hand="right"
        ))

    return HandPattern(
        name="sustained_chords",
        notes=notes,
        difficulty="beginner",
        tempo_range=(50, 90)
    )
