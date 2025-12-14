"""Jazz Rhythm Transformations

Implements jazz rhythm feel transformations:
- Swing transformation (triplet-based 8th notes)
- Syncopation (off-beat emphasis)
- Shuffle feel (similar to swing but heavier)

Key Concepts:
- Swing: Straight 8ths → triplet 8ths (long-short pattern)
- Swing ratio: 2:1 (moderate swing) or 3:1 (heavy swing)
- Syncopation: Emphasize off-beats, weaken on-beats
"""

from typing import List
from app.gospel import Note


def apply_swing_feel(notes: List[Note], swing_ratio: float = 2.0) -> List[Note]:
    """Apply swing feel to straight 8th notes.

    Swing feel: Convert straight 8th notes to triplet-based swing.
    - On-beat 8ths: Play on time
    - Off-beat 8ths: Delay to create long-short pattern

    Swing ratio:
    - 1.0 = straight (no swing)
    - 2.0 = moderate swing (most common)
    - 3.0 = heavy swing

    Args:
        notes: Notes to swing
        swing_ratio: Swing ratio (1.0-3.0)

    Returns:
        Notes with swing feel applied
    """
    swung_notes = []

    for note in notes:
        # Calculate beat position
        beat_position = note.time % 1.0  # Position within beat (0.0-1.0)

        # Check if note is on off-beat 8th (around 0.5 position)
        is_off_beat_eighth = 0.4 <= beat_position <= 0.6

        if is_off_beat_eighth:
            # Apply swing delay
            # Triplet swing: delay by 1/12 of a beat (1/3 of a quarter note triplet)
            delay = (swing_ratio - 1.0) / 12.0

            swung_note = Note(
                pitch=note.pitch,
                time=note.time + delay,
                duration=note.duration * 0.9,  # Slightly shorter
                velocity=note.velocity - 5,  # Slightly softer (swing lilt)
                hand=note.hand
            )
        else:
            # On-beat notes stay the same
            swung_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=note.velocity,
                hand=note.hand
            )

        swung_notes.append(swung_note)

    return swung_notes


def apply_syncopation(notes: List[Note]) -> List[Note]:
    """Apply syncopation (off-beat emphasis).

    Emphasize off-beats, weaken on-beats.
    Creates rhythmic tension.

    Args:
        notes: Notes to syncopate

    Returns:
        Notes with syncopation applied
    """
    syncopated_notes = []

    for note in notes:
        beat_position = note.time % 1.0

        # Off-beat notes get emphasized
        is_off_beat = 0.3 <= beat_position <= 0.7

        if is_off_beat:
            # Emphasize off-beats
            syncopated_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=min(note.velocity + 10, 127),  # Louder
                hand=note.hand
            )
        else:
            # Weaken on-beats
            syncopated_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(note.velocity - 10, 20),  # Softer
                hand=note.hand
            )

        syncopated_notes.append(syncopated_note)

    return syncopated_notes


def apply_jazz_rhythm_pattern(notes: List[Note], pattern_name: str) -> List[Note]:
    """Apply jazz rhythm pattern transformation.

    Args:
        notes: Notes to transform
        pattern_name: Name of rhythm pattern
                     - "swing": Moderate swing feel
                     - "heavy_swing": Heavy swing feel
                     - "syncopation": Off-beat emphasis

    Returns:
        Transformed notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name == "swing":
        return apply_swing_feel(notes, swing_ratio=2.0)
    elif pattern_name == "heavy_swing":
        return apply_swing_feel(notes, swing_ratio=2.5)
    elif pattern_name == "syncopation":
        return apply_syncopation(notes)
    else:
        raise ValueError(
            f"Unknown jazz rhythm pattern: {pattern_name}. "
            f"Available: swing, heavy_swing, syncopation"
        )


__all__ = [
    "apply_swing_feel",
    "apply_syncopation",
    "apply_jazz_rhythm_pattern",
]
