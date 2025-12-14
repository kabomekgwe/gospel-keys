"""Neo-Soul Rhythm Transformations

Implements neo-soul rhythm feel transformations:
- 16th-note groove quantization
- Syncopation emphasis
- Laid-back/behind-the-beat timing
- Micro-timing adjustments

Key Concepts:
- 16th-note grooves with pocket
- Laid-back feel (slightly behind the beat)
- Syncopated patterns emphasizing off-beats
- D'Angelo/Questlove-style groove
"""

from typing import List
from app.gospel import Note


def apply_16th_note_groove(notes: List[Note]) -> List[Note]:
    """Apply 16th-note groove quantization.

    Quantizes notes to 16th-note grid while preserving groove.

    Args:
        notes: Notes to quantize

    Returns:
        Quantized notes with 16th-note groove
    """
    grooved_notes = []

    for note in notes:
        # Quantize to nearest 16th note (0.25 beats)
        time_in_16ths = round(note.time / 0.25)
        quantized_time = time_in_16ths * 0.25

        grooved_note = Note(
            pitch=note.pitch,
            time=quantized_time,
            duration=note.duration,
            velocity=note.velocity,
            hand=note.hand
        )
        grooved_notes.append(grooved_note)

    return grooved_notes


def apply_laid_back_timing(notes: List[Note], amount: float = 0.05) -> List[Note]:
    """Apply laid-back (behind-the-beat) timing.

    Delays certain notes to create relaxed, laid-back feel.
    Typical of D'Angelo, Erykah Badu style.

    Args:
        notes: Notes to adjust
        amount: How much to delay (in beats, typically 0.03-0.08)

    Returns:
        Notes with laid-back timing
    """
    laid_back_notes = []

    for note in notes:
        # Apply laid-back to notes NOT on strong beats
        beat_position = note.time % 1.0
        is_strong_beat = beat_position < 0.1  # Beat 1, 2, 3, 4

        if not is_strong_beat:
            # Delay off-beat notes slightly
            laid_back_note = Note(
                pitch=note.pitch,
                time=note.time + amount,
                duration=note.duration * 0.95,  # Slightly shorter
                velocity=note.velocity,
                hand=note.hand
            )
        else:
            # Keep strong beats on time
            laid_back_note = note

        laid_back_notes.append(laid_back_note)

    return laid_back_notes


def apply_syncopation_emphasis(notes: List[Note]) -> List[Note]:
    """Apply syncopation emphasis.

    Emphasizes off-beat notes, de-emphasizes on-beats.
    Creates syncopated rhythmic feel.

    Args:
        notes: Notes to transform

    Returns:
        Notes with syncopation emphasis
    """
    syncopated_notes = []

    for note in notes:
        beat_position = note.time % 1.0

        # Determine if note is on off-beat
        # Off-beats: & of beats (0.5), e (0.25, 0.75), a (1.75)
        is_off_beat = (
            (0.4 <= beat_position <= 0.6) or    # & of beat
            (0.2 <= beat_position <= 0.3) or    # e
            (0.7 <= beat_position <= 0.8)       # a
        )

        if is_off_beat:
            # Emphasize off-beats
            syncopated_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=min(note.velocity + 8, 127),  # Louder
                hand=note.hand
            )
        else:
            # De-emphasize on-beats
            syncopated_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(note.velocity - 8, 20),  # Softer
                hand=note.hand
            )

        syncopated_notes.append(syncopated_note)

    return syncopated_notes


def apply_micro_timing(notes: List[Note]) -> List[Note]:
    """Apply micro-timing variations.

    Slight random variations in timing to humanize.
    Creates organic, human feel.

    Args:
        notes: Notes to humanize

    Returns:
        Notes with micro-timing variations
    """
    import random

    humanized_notes = []

    for note in notes:
        # Small random timing variation (-0.02 to +0.02 beats)
        timing_offset = random.uniform(-0.02, 0.02)

        humanized_note = Note(
            pitch=note.pitch,
            time=max(0.0, note.time + timing_offset),  # Don't go negative
            duration=note.duration,
            velocity=note.velocity,
            hand=note.hand
        )
        humanized_notes.append(humanized_note)

    return humanized_notes


def apply_neosoul_rhythm_pattern(notes: List[Note], pattern_name: str) -> List[Note]:
    """Apply neo-soul rhythm pattern transformation.

    Args:
        notes: Notes to transform
        pattern_name: Name of rhythm pattern
                     - "16th_groove": Quantize to 16th-note grid
                     - "laid_back": Behind-the-beat timing
                     - "syncopated": Off-beat emphasis
                     - "humanized": Micro-timing variations

    Returns:
        Transformed notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name == "16th_groove":
        return apply_16th_note_groove(notes)
    elif pattern_name == "laid_back":
        return apply_laid_back_timing(notes, amount=0.05)
    elif pattern_name == "syncopated":
        return apply_syncopation_emphasis(notes)
    elif pattern_name == "humanized":
        return apply_micro_timing(notes)
    else:
        raise ValueError(
            f"Unknown neo-soul rhythm pattern: {pattern_name}. "
            f"Available: 16th_groove, laid_back, syncopated, humanized"
        )


__all__ = [
    "apply_16th_note_groove",
    "apply_laid_back_timing",
    "apply_syncopation_emphasis",
    "apply_micro_timing",
    "apply_neosoul_rhythm_pattern",
]
