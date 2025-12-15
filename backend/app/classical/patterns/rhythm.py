"""Classical Rhythm Transformations

Implements classical period rhythm transformations:
- Baroque articulation (detached, precise)
- Classical phrasing (balanced, clear)
- Romantic rubato (expressive timing)
- Waltz feel (3/4 emphasis)
- Agogic accents (metric emphasis)

Key Concepts:
- Baroque: Precise, ornamented, terrace dynamics
- Classical: Balanced, clear phrasing, metric regularity
- Romantic: Rubato, expressive timing, crescendo/diminuendo
- Articulation: Staccato, legato, tenuto
"""

from typing import List
from app.gospel import Note


def apply_baroque_articulation(notes: List[Note]) -> List[Note]:
    """Apply Baroque articulation style.

    Baroque: Detached, precise articulation with terrace dynamics
    Notes are shortened, creating space between them

    Args:
        notes: Notes to transform

    Returns:
        Notes with Baroque articulation
    """
    baroque_notes = []

    for note in notes:
        # Baroque style: shorten notes for detached articulation
        baroque_note = Note(
            pitch=note.pitch,
            time=note.time,
            duration=note.duration * 0.7,  # Shortened (non-legato)
            velocity=note.velocity,
            hand=note.hand
        )
        baroque_notes.append(baroque_note)

    return baroque_notes


def apply_classical_phrasing(notes: List[Note]) -> List[Note]:
    """Apply Classical period phrasing.

    Classical: Balanced phrases with clear metric structure
    Emphasis on beat 1, slight de-emphasis on weak beats

    Args:
        notes: Notes to transform

    Returns:
        Notes with Classical phrasing
    """
    classical_notes = []

    for note in notes:
        beat_number = int(note.time) % 4

        # Emphasize strong beats (1, 3), soften weak beats (2, 4)
        if beat_number == 0:  # Beat 1 (strongest)
            velocity_adjustment = 10
        elif beat_number == 2:  # Beat 3 (secondary accent)
            velocity_adjustment = 5
        else:  # Beats 2, 4 (weak)
            velocity_adjustment = -8

        classical_note = Note(
            pitch=note.pitch,
            time=note.time,
            duration=note.duration * 0.95,  # Slightly detached
            velocity=max(20, min(127, note.velocity + velocity_adjustment)),
            hand=note.hand
        )
        classical_notes.append(classical_note)

    return classical_notes


def apply_romantic_rubato(notes: List[Note], intensity: float = 0.15) -> List[Note]:
    """Apply Romantic rubato (expressive timing).

    Rubato: "Stolen time" - slight tempo variations for expression
    Notes are pushed/pulled slightly from strict time

    Args:
        notes: Notes to transform
        intensity: Amount of rubato (0.0-0.3, default 0.15)

    Returns:
        Notes with rubato timing
    """
    import random

    rubato_notes = []

    for note in notes:
        # Apply random rubato within intensity range
        # Bias towards delaying (romantic style often delays)
        rubato_offset = random.triangular(-intensity * 0.5, intensity, intensity * 0.3)

        rubato_note = Note(
            pitch=note.pitch,
            time=max(0, note.time + rubato_offset),
            duration=note.duration,
            velocity=note.velocity,
            hand=note.hand
        )
        rubato_notes.append(rubato_note)

    return rubato_notes


def apply_waltz_feel(notes: List[Note]) -> List[Note]:
    """Apply waltz feel (3/4 time emphasis).

    Waltz: Strong beat 1, lighter beats 2 and 3
    Creates "oom-pah-pah" pattern

    Args:
        notes: Notes to transform

    Returns:
        Notes with waltz feel
    """
    waltz_notes = []

    for note in notes:
        beat_in_measure = int(note.time) % 3

        if beat_in_measure == 0:  # Beat 1 (strong)
            waltz_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 1.1,  # Slightly longer
                velocity=min(127, note.velocity + 15),  # Louder
                hand=note.hand
            )
        else:  # Beats 2, 3 (light)
            waltz_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 0.85,  # Shorter
                velocity=max(30, note.velocity - 10),  # Softer
                hand=note.hand
            )

        waltz_notes.append(waltz_note)

    return waltz_notes


def apply_agogic_accent(notes: List[Note]) -> List[Note]:
    """Apply agogic accents (emphasis through duration).

    Agogic accent: Emphasis created by lengthening notes
    Common in Classical/Romantic music for expressive peaks

    Args:
        notes: Notes to transform

    Returns:
        Notes with agogic accents on metric strong beats
    """
    accented_notes = []

    for note in notes:
        beat_position = note.time % 4.0
        is_strong_beat = beat_position < 0.1  # Beat 1, 2, 3, 4

        if is_strong_beat:
            # Lengthen strong beat notes (agogic accent)
            accented_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 1.15,  # Longer
                velocity=min(127, note.velocity + 5),
                hand=note.hand
            )
        else:
            accented_note = note

        accented_notes.append(accented_note)

    return accented_notes


def apply_staccato(notes: List[Note], staccato_ratio: float = 0.5) -> List[Note]:
    """Apply staccato articulation.

    Staccato: Short, detached notes
    Typical ratio: 0.5 (half duration)

    Args:
        notes: Notes to transform
        staccato_ratio: Duration ratio (0.3-0.7, default 0.5)

    Returns:
        Notes with staccato articulation
    """
    staccato_notes = []

    for note in notes:
        staccato_note = Note(
            pitch=note.pitch,
            time=note.time,
            duration=note.duration * staccato_ratio,
            velocity=note.velocity,
            hand=note.hand
        )
        staccato_notes.append(staccato_note)

    return staccato_notes


def apply_legato(notes: List[Note]) -> List[Note]:
    """Apply legato articulation.

    Legato: Smooth, connected notes
    Notes extended to touch the next note

    Args:
        notes: Notes to transform

    Returns:
        Notes with legato articulation
    """
    if not notes:
        return notes

    legato_notes = []
    sorted_notes = sorted(notes, key=lambda n: n.time)

    for i, note in enumerate(sorted_notes):
        if i < len(sorted_notes) - 1:
            next_note = sorted_notes[i + 1]
            # Extend duration to almost reach next note
            gap_to_next = next_note.time - note.time
            new_duration = min(note.duration * 1.2, gap_to_next * 0.98)
        else:
            # Last note: extend slightly
            new_duration = note.duration * 1.1

        legato_note = Note(
            pitch=note.pitch,
            time=note.time,
            duration=new_duration,
            velocity=note.velocity,
            hand=note.hand
        )
        legato_notes.append(legato_note)

    return legato_notes


def apply_tenuto(notes: List[Note]) -> List[Note]:
    """Apply tenuto articulation.

    Tenuto: Full-length, emphasized notes
    Notes held for full value with slight emphasis

    Args:
        notes: Notes to transform

    Returns:
        Notes with tenuto articulation
    """
    tenuto_notes = []

    for note in notes:
        tenuto_note = Note(
            pitch=note.pitch,
            time=note.time,
            duration=note.duration * 1.0,  # Full duration
            velocity=min(127, note.velocity + 8),  # Slight emphasis
            hand=note.hand
        )
        tenuto_notes.append(tenuto_note)

    return tenuto_notes


def apply_classical_rhythm_pattern(notes: List[Note], pattern_name: str) -> List[Note]:
    """Apply Classical rhythm pattern transformation.

    Args:
        notes: Notes to transform
        pattern_name: Name of rhythm pattern
                     - "baroque": Baroque articulation
                     - "classical": Classical phrasing
                     - "romantic_rubato": Romantic expressive timing
                     - "waltz": 3/4 waltz feel
                     - "agogic": Agogic accents
                     - "staccato": Short, detached
                     - "legato": Smooth, connected
                     - "tenuto": Full-length, emphasized

    Returns:
        Transformed notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name == "baroque":
        return apply_baroque_articulation(notes)
    elif pattern_name == "classical":
        return apply_classical_phrasing(notes)
    elif pattern_name == "romantic_rubato":
        return apply_romantic_rubato(notes, intensity=0.15)
    elif pattern_name == "waltz":
        return apply_waltz_feel(notes)
    elif pattern_name == "agogic":
        return apply_agogic_accent(notes)
    elif pattern_name == "staccato":
        return apply_staccato(notes, staccato_ratio=0.5)
    elif pattern_name == "legato":
        return apply_legato(notes)
    elif pattern_name == "tenuto":
        return apply_tenuto(notes)
    else:
        raise ValueError(
            f"Unknown Classical rhythm pattern: {pattern_name}. "
            f"Available: baroque, classical, romantic_rubato, waltz, agogic, "
            f"staccato, legato, tenuto"
        )


__all__ = [
    "apply_baroque_articulation",
    "apply_classical_phrasing",
    "apply_romantic_rubato",
    "apply_waltz_feel",
    "apply_agogic_accent",
    "apply_staccato",
    "apply_legato",
    "apply_tenuto",
    "apply_classical_rhythm_pattern",
]
