"""Reggae Rhythm Patterns

Applies reggae-specific rhythm transformations:
- One-drop feel (emphasis on beat 3)
- Laid-back timing (slight delay)
- Offbeat emphasis
"""

from typing import List
from app.gospel import Note


def apply_reggae_rhythm_pattern(notes: List[Note], rhythm_name: str) -> List[Note]:
    """Apply reggae rhythm transformation to notes.

    Args:
        notes: List of notes to transform
        rhythm_name: Name of rhythm pattern to apply

    Returns:
        Transformed notes with reggae rhythm
    """
    if rhythm_name == "one_drop":
        return _apply_one_drop(notes)
    elif rhythm_name == "laid_back":
        return _apply_laid_back(notes)
    elif rhythm_name == "offbeat_emphasis":
        return _apply_offbeat_emphasis(notes)
    else:
        return notes


def _apply_one_drop(notes: List[Note]) -> List[Note]:
    """Apply one-drop feel - emphasis on beat 3.

    Characteristic reggae drum pattern (kick on 3).
    """
    transformed = []

    for note in notes:
        # Calculate beat position (0-3)
        beat_position = note.time % 4.0

        # Emphasize beat 3 (2.0-3.0)
        if 2.0 <= beat_position < 3.0:
            # Stronger attack on beat 3
            transformed.append(Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=min(127, int(note.velocity * 1.2))  # 20% louder
            ))
        else:
            transformed.append(note)

    return transformed


def _apply_laid_back(notes: List[Note]) -> List[Note]:
    """Apply laid-back timing - slight delay.

    Notes slightly behind the beat for reggae feel.
    """
    transformed = []
    delay_amount = 0.03  # 30ms delay (subtle)

    for note in notes:
        transformed.append(Note(
            pitch=note.pitch,
            time=note.time + delay_amount,
            duration=note.duration,
            velocity=note.velocity
        ))

    return transformed


def _apply_offbeat_emphasis(notes: List[Note]) -> List[Note]:
    """Apply offbeat emphasis - louder on 2 and 4.

    Emphasizes the skank rhythm.
    """
    transformed = []

    for note in notes:
        # Calculate beat position
        beat_position = note.time % 4.0

        # Emphasize beats 2 and 4 (1.0-2.0 and 3.0-4.0)
        if (1.0 <= beat_position < 2.0) or (3.0 <= beat_position < 4.0):
            transformed.append(Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=min(127, int(note.velocity * 1.15))  # 15% louder
            ))
        else:
            transformed.append(note)

    return transformed
