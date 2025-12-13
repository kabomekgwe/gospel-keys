"""Gospel Rhythm Patterns

Implements rhythm transformations for gospel piano:
- Gospel shuffle (12/8 feel in 4/4)
- Gospel swing (2:3 ratio)
- Syncopation (backbeat, off-beat, cross-rhythm)

These functions transform note timing rather than generating new notes.
"""

from typing import List, Callable
from app.gospel import Note
import copy


def apply_gospel_shuffle(notes: List[Note], intensity: float = 0.6) -> List[Note]:
    """Apply gospel shuffle feel to notes.

    Converts straight 8th notes to shuffle (triplet) feel.
    Typical pattern: Dotted 8th + 16th instead of two 8ths.

    Args:
        notes: List of notes to transform
        intensity: Shuffle intensity (0.0 = straight, 1.0 = full triplet)
                  0.6 is traditional gospel shuffle

    Returns:
        New list of notes with shuffled timing
    """
    shuffled_notes = []

    for note in notes:
        new_note = copy.deepcopy(note)

        # Quantize to nearest 8th note beat
        eighth_position = round(note.time * 2) / 2  # Round to nearest 0.5
        offset_from_eighth = note.time - eighth_position

        # Check if this is an off-beat 8th note
        is_offbeat_eighth = (eighth_position % 1.0) == 0.5

        if is_offbeat_eighth and abs(offset_from_eighth) < 0.1:
            # This is an off-beat 8th note - apply shuffle
            # In shuffle, off-beat comes at 2/3 of beat instead of 1/2
            beat_number = int(eighth_position)
            shuffled_time = beat_number + (2.0 / 3.0)

            # Blend between straight and shuffled based on intensity
            new_note.time = note.time + (shuffled_time - note.time) * intensity

        shuffled_notes.append(new_note)

    return shuffled_notes


def apply_gospel_swing(notes: List[Note], swing_ratio: float = 0.6) -> List[Note]:
    """Apply gospel swing to 8th note patterns.

    Transforms straight 8th notes to swing feel with adjustable ratio.
    Ratio of 0.5 = straight, 0.67 = triplet swing, 0.6 = standard gospel swing.

    Args:
        notes: List of notes to transform
        swing_ratio: Ratio for swing (0.5-0.75, default 0.6 for gospel)

    Returns:
        New list of notes with swing timing
    """
    swung_notes = []

    # Group notes by beat
    for note in notes:
        new_note = copy.deepcopy(note)

        beat_number = int(note.time)
        position_in_beat = note.time - beat_number

        # Check if this is an off-beat 8th note (around 0.5 position)
        if 0.4 <= position_in_beat <= 0.6:
            # Apply swing to off-beat
            swung_time = beat_number + swing_ratio
            new_note.time = swung_time

        swung_notes.append(new_note)

    return swung_notes


def apply_backbeat_emphasis(notes: List[Note], emphasis_factor: float = 1.3) -> List[Note]:
    """Emphasize backbeat (beats 2 and 4) for gospel feel.

    Args:
        notes: List of notes to transform
        emphasis_factor: Velocity multiplier for backbeats (default 1.3)

    Returns:
        New list of notes with backbeat emphasis
    """
    emphasized_notes = []

    for note in notes:
        new_note = copy.deepcopy(note)

        # Get beat number (0, 1, 2, 3 in 4/4)
        beat_number = int(note.time) % 4

        # Beats 1 and 3 are backbeats (using 0-indexing, so actually 2 and 4)
        # In music terminology, beats 2 and 4 are backbeats
        is_backbeat = beat_number in (1, 3)  # Beats 2 and 4 in 1-indexed

        if is_backbeat:
            # Increase velocity for backbeat
            new_velocity = int(note.velocity * emphasis_factor)
            new_note.velocity = min(new_velocity, 127)  # Cap at MIDI max

        emphasized_notes.append(new_note)

    return emphasized_notes


def apply_offbeat_syncopation(notes: List[Note], probability: float = 0.3) -> List[Note]:
    """Shift some downbeat notes to off-beat positions for syncopation.

    Args:
        notes: List of notes to transform
        probability: Probability of syncopating a note (0.0-1.0)

    Returns:
        New list of notes with syncopation
    """
    import random

    syncopated_notes = []

    for note in notes:
        new_note = copy.deepcopy(note)

        # Check if note is on a downbeat (integer beat)
        beat_number = note.time
        is_downbeat = abs(beat_number - round(beat_number)) < 0.1

        if is_downbeat and random.random() < probability:
            # Shift to off-beat (anticipate by 0.5 beats)
            new_note.time = max(0, note.time - 0.5)
            # Slightly reduce velocity for off-beat notes
            new_note.velocity = int(note.velocity * 0.9)

        syncopated_notes.append(new_note)

    return syncopated_notes


def apply_cross_rhythm(notes: List[Note], pattern: str = "3over4") -> List[Note]:
    """Apply cross-rhythm pattern (polyrhythm).

    Args:
        notes: List of notes to transform
        pattern: Cross-rhythm pattern ("3over4", "5over4")

    Returns:
        New list of notes with cross-rhythm
    """
    cross_notes = []

    if pattern == "3over4":
        # 3 evenly spaced notes over 4 beats
        divisions = 3
    elif pattern == "5over4":
        # 5 evenly spaced notes over 4 beats
        divisions = 5
    else:
        # Default: no transformation
        return notes.copy()

    # Only apply to notes in first 4 beats
    bar_notes = [n for n in notes if n.time < 4.0]
    other_notes = [n for n in notes if n.time >= 4.0]

    if len(bar_notes) == 0:
        return notes.copy()

    # Redistribute notes evenly across 4 beats
    beat_interval = 4.0 / divisions

    for i, note in enumerate(bar_notes[:divisions]):
        new_note = copy.deepcopy(note)
        new_note.time = i * beat_interval
        cross_notes.append(new_note)

    # Add any remaining notes
    cross_notes.extend(other_notes)

    return cross_notes


def apply_rhythmic_displacement(notes: List[Note], displacement: float = 0.25) -> List[Note]:
    """Displace note timing slightly for humanization or rhythmic variation.

    Args:
        notes: List of notes to transform
        displacement: Maximum time displacement in beats (default 0.25 = 16th note)

    Returns:
        New list of notes with displacement
    """
    import random

    displaced_notes = []

    for note in notes:
        new_note = copy.deepcopy(note)

        # Random displacement between -displacement and +displacement
        offset = random.uniform(-displacement, displacement)
        new_note.time = max(0, note.time + offset)

        displaced_notes.append(new_note)

    return displaced_notes


def quantize_to_grid(notes: List[Note], grid_size: float = 0.25) -> List[Note]:
    """Quantize notes to rhythmic grid.

    Args:
        notes: List of notes to quantize
        grid_size: Grid size in beats (0.25 = 16th note, 0.5 = 8th note)

    Returns:
        New list of quantized notes
    """
    quantized_notes = []

    for note in notes:
        new_note = copy.deepcopy(note)

        # Round to nearest grid position
        grid_position = round(note.time / grid_size) * grid_size
        new_note.time = grid_position

        quantized_notes.append(new_note)

    return quantized_notes


def apply_tempo_rubato(notes: List[Note], rubato_curve: str = "ritardando") -> List[Note]:
    """Apply tempo rubato (tempo variation).

    Args:
        notes: List of notes to transform
        rubato_curve: Type of rubato ("ritardando", "accelerando", "agogic")

    Returns:
        New list of notes with rubato
    """
    rubato_notes = []

    # Find total time span
    if not notes:
        return notes

    max_time = max(n.time for n in notes)

    for note in notes:
        new_note = copy.deepcopy(note)

        if rubato_curve == "ritardando":
            # Gradual slowing down
            # Notes later in the phrase get stretched more
            progress = note.time / max_time if max_time > 0 else 0
            stretch_factor = 1.0 + (progress * 0.3)  # Up to 30% slower
            new_note.time = note.time * stretch_factor

        elif rubato_curve == "accelerando":
            # Gradual speeding up
            progress = note.time / max_time if max_time > 0 else 0
            compress_factor = 1.0 - (progress * 0.2)  # Up to 20% faster
            new_note.time = note.time * compress_factor

        elif rubato_curve == "agogic":
            # Emphasize important beats with slight delay
            beat_number = int(note.time)
            is_important = beat_number % 2 == 0  # Every other beat

            if is_important:
                new_note.time = note.time + 0.05  # Slight delay

        rubato_notes.append(new_note)

    return rubato_notes


# Rhythm transformation registry
RHYTHM_TRANSFORMATIONS: dict[str, Callable[[List[Note]], List[Note]]] = {
    "gospel_shuffle": apply_gospel_shuffle,
    "gospel_swing": apply_gospel_swing,
    "backbeat_emphasis": apply_backbeat_emphasis,
    "offbeat_syncopation": apply_offbeat_syncopation,
    "cross_rhythm": apply_cross_rhythm,
    "rhythmic_displacement": apply_rhythmic_displacement,
    "quantize": quantize_to_grid,
    "rubato": apply_tempo_rubato,
}


def apply_rhythm_pattern(
    notes: List[Note],
    pattern_name: str,
    **kwargs
) -> List[Note]:
    """Apply a rhythm transformation pattern by name.

    Args:
        notes: List of notes to transform
        pattern_name: Name of rhythm pattern to apply
        **kwargs: Additional arguments for specific patterns

    Returns:
        Transformed notes

    Raises:
        ValueError: If pattern name is unknown
    """
    if pattern_name not in RHYTHM_TRANSFORMATIONS:
        raise ValueError(
            f"Unknown rhythm pattern: {pattern_name}. "
            f"Available: {list(RHYTHM_TRANSFORMATIONS.keys())}"
        )

    transformation = RHYTHM_TRANSFORMATIONS[pattern_name]

    # Apply transformation with any additional kwargs
    if kwargs:
        return transformation(notes, **kwargs)
    else:
        return transformation(notes)


__all__ = [
    "apply_gospel_shuffle",
    "apply_gospel_swing",
    "apply_backbeat_emphasis",
    "apply_offbeat_syncopation",
    "apply_cross_rhythm",
    "apply_rhythmic_displacement",
    "quantize_to_grid",
    "apply_tempo_rubato",
    "apply_rhythm_pattern",
    "RHYTHM_TRANSFORMATIONS",
]
