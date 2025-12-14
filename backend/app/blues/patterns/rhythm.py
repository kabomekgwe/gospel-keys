"""Blues Rhythm Transformations

Implements blues rhythm feel transformations:
- Shuffle feel (triplet-based swing, heavier than jazz swing)
- 12/8 feel (compound meter, rolling triplets)
- Straight blues (even 8ths for slow blues)

Key Concepts:
- Shuffle: Long-short triplet feel (2:1 ratio or heavier)
- 12/8: Each beat divided into 3 (ternary feel)
- Blues timing: Slightly behind the beat for laid-back feel
"""

from typing import List
from app.gospel import Note


def apply_shuffle_feel(notes: List[Note], shuffle_ratio: float = 2.5) -> List[Note]:
    """Apply shuffle feel to straight 8th notes.

    Shuffle is similar to swing but with a heavier ratio.
    Converts straight 8ths to triplet-based long-short pattern.

    Shuffle ratio:
    - 2.0 = light shuffle (like jazz swing)
    - 2.5 = medium shuffle (typical blues)
    - 3.0 = heavy shuffle (extreme blues)

    Args:
        notes: Notes to shuffle
        shuffle_ratio: Shuffle ratio (2.0-3.0)

    Returns:
        Notes with shuffle feel applied
    """
    shuffled_notes = []

    for note in notes:
        # Calculate beat position
        beat_position = note.time % 1.0

        # Check if note is on off-beat 8th (around 0.5 position)
        is_off_beat_eighth = 0.4 <= beat_position <= 0.6

        if is_off_beat_eighth:
            # Apply shuffle delay (heavier than swing)
            # Triplet shuffle: delay by more than jazz swing
            delay = (shuffle_ratio - 1.0) / 12.0

            shuffled_note = Note(
                pitch=note.pitch,
                time=note.time + delay,
                duration=note.duration * 0.85,  # Shorter duration
                velocity=note.velocity - 8,  # Softer (shuffle lilt)
                hand=note.hand
            )
        else:
            # On-beat notes stay the same but slightly accented
            shuffled_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=min(note.velocity + 3, 127),  # Slight accent
                hand=note.hand
            )

        shuffled_notes.append(shuffled_note)

    return shuffled_notes


def apply_12_8_feel(notes: List[Note]) -> List[Note]:
    """Apply 12/8 compound meter feel.

    12/8 time: 4 beats per bar, each beat divided into 3.
    Creates rolling, triplet feel throughout.

    Args:
        notes: Notes to transform

    Returns:
        Notes quantized to 12/8 grid
    """
    twelve_eight_notes = []

    for note in notes:
        # Quantize to nearest 12/8 subdivision (1/12 of a bar = 0.333...)
        # In 12/8: 12 subdivisions per 4-beat bar
        subdivision = 4.0 / 12  # 0.333...

        # Find nearest subdivision
        subdivisions = round(note.time / subdivision)
        quantized_time = subdivisions * subdivision

        twelve_eight_note = Note(
            pitch=note.pitch,
            time=quantized_time,
            duration=note.duration,
            velocity=note.velocity,
            hand=note.hand
        )
        twelve_eight_notes.append(twelve_eight_note)

    return twelve_eight_notes


def apply_straight_blues(notes: List[Note]) -> List[Note]:
    """Apply straight blues feel (no shuffle).

    For slow blues ballads, sometimes straight 8ths sound better.
    Just adds slight dynamic variation.

    Args:
        notes: Notes to transform

    Returns:
        Notes with straight blues feel
    """
    straight_notes = []

    for note in notes:
        beat_position = note.time % 1.0
        is_downbeat = beat_position < 0.1

        if is_downbeat:
            # Accent downbeats
            straight_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=min(note.velocity + 5, 127),
                hand=note.hand
            )
        else:
            # Keep off-beats normal
            straight_note = note

        straight_notes.append(straight_note)

    return straight_notes


def apply_blues_rhythm_pattern(notes: List[Note], pattern_name: str) -> List[Note]:
    """Apply blues rhythm pattern transformation.

    Args:
        notes: Notes to transform
        pattern_name: Name of rhythm pattern
                     - "shuffle": Medium shuffle feel (typical blues)
                     - "heavy_shuffle": Heavy shuffle (extreme blues)
                     - "12_8": 12/8 compound meter
                     - "straight": Straight 8ths (slow blues)

    Returns:
        Transformed notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name == "shuffle":
        return apply_shuffle_feel(notes, shuffle_ratio=2.5)
    elif pattern_name == "heavy_shuffle":
        return apply_shuffle_feel(notes, shuffle_ratio=3.0)
    elif pattern_name == "12_8":
        return apply_12_8_feel(notes)
    elif pattern_name == "straight":
        return apply_straight_blues(notes)
    else:
        raise ValueError(
            f"Unknown blues rhythm pattern: {pattern_name}. "
            f"Available: shuffle, heavy_shuffle, 12_8, straight"
        )


__all__ = [
    "apply_shuffle_feel",
    "apply_12_8_feel",
    "apply_straight_blues",
    "apply_blues_rhythm_pattern",
]
