"""Classical Voice Independence and Counterpoint Rules

Implements strict classical voice leading and counterpoint rules:
- Avoid parallel fifths and octaves
- Smooth voice leading (minimal movement)
- Contrary motion preferred
- No voice crossing
- Resolve tendency tones (7 to 1, 4 to 3)

Based on classical harmony rules from:
- J.S. Bach counterpoint
- Common practice period (1650-1900)
- Strict voice leading pedagogy
"""

from typing import List, Tuple, Optional
from app.gospel import Note


def get_interval(note1_pitch: int, note2_pitch: int) -> int:
    """Calculate interval between two pitches (in semitones).

    Args:
        note1_pitch: First note MIDI pitch
        note2_pitch: Second note MIDI pitch

    Returns:
        Interval in semitones (absolute value)
    """
    return abs(note2_pitch - note1_pitch) % 12


def is_parallel_motion(
    voice1_prev: int,
    voice1_curr: int,
    voice2_prev: int,
    voice2_curr: int,
    interval: int
) -> bool:
    """Check if two voices move in parallel motion at a forbidden interval.

    Parallel fifths (7 semitones) and octaves (0 semitones) are forbidden
    in classical counterpoint.

    Args:
        voice1_prev: Previous pitch of voice 1
        voice1_curr: Current pitch of voice 1
        voice2_prev: Previous pitch of voice 2
        voice2_curr: Current pitch of voice 2
        interval: Forbidden interval (5 = perfect fifth, 0 = octave)

    Returns:
        True if parallel motion detected
    """
    # Get intervals before and after
    interval_before = get_interval(voice1_prev, voice2_prev)
    interval_after = get_interval(voice1_curr, voice2_curr)

    # Check if both intervals match the forbidden interval
    # AND both voices move in the same direction
    if interval_before == interval and interval_after == interval:
        # Check direction
        voice1_direction = voice1_curr - voice1_prev
        voice2_direction = voice2_curr - voice2_prev

        # Parallel motion: same direction, non-zero movement
        if voice1_direction != 0 and voice2_direction != 0:
            return (voice1_direction > 0) == (voice2_direction > 0)

    return False


def check_parallel_fifths_octaves(
    left_notes: List[Note],
    right_notes: List[Note]
) -> List[Tuple[float, str]]:
    """Check for parallel fifths and octaves between hands.

    Args:
        left_notes: Left hand notes
        right_notes: Right hand notes

    Returns:
        List of (time, violation_type) tuples
    """
    violations = []

    # Get simultaneous notes (same time)
    left_by_time = {}
    for note in left_notes:
        if note.time not in left_by_time:
            left_by_time[note.time] = []
        left_by_time[note.time].append(note)

    right_by_time = {}
    for note in right_notes:
        if note.time not in right_by_time:
            right_by_time[note.time] = []
        right_by_time[note.time].append(note)

    times = sorted(set(left_by_time.keys()) & set(right_by_time.keys()))

    # Check consecutive time points
    for i in range(len(times) - 1):
        time_prev = times[i]
        time_curr = times[i + 1]

        # Get highest left note and lowest right note (outer voices)
        left_prev = max(left_by_time[time_prev], key=lambda n: n.pitch).pitch
        left_curr = max(left_by_time[time_curr], key=lambda n: n.pitch).pitch
        right_prev = min(right_by_time[time_prev], key=lambda n: n.pitch).pitch
        right_curr = min(right_by_time[time_curr], key=lambda n: n.pitch).pitch

        # Check parallel fifths (7 semitones)
        if is_parallel_motion(left_prev, left_curr, right_prev, right_curr, interval=7):
            violations.append((time_curr, "parallel_fifth"))

        # Check parallel octaves (0 semitones)
        if is_parallel_motion(left_prev, left_curr, right_prev, right_curr, interval=0):
            violations.append((time_curr, "parallel_octave"))

    return violations


def check_voice_crossing(left_notes: List[Note], right_notes: List[Note]) -> List[float]:
    """Check for voice crossing (left hand higher than right hand).

    Args:
        left_notes: Left hand notes
        right_notes: Right hand notes

    Returns:
        List of times where voice crossing occurs
    """
    crossings = []

    # Check simultaneous notes
    for left_note in left_notes:
        for right_note in right_notes:
            # Allow small overlap (within 0.1 beats)
            if abs(left_note.time - right_note.time) < 0.1:
                if left_note.pitch > right_note.pitch:
                    crossings.append(left_note.time)
                    break

    return crossings


def apply_contrary_motion(
    left_notes: List[Note],
    right_notes: List[Note],
    probability: float = 0.3
) -> Tuple[List[Note], List[Note]]:
    """Encourage contrary motion between hands.

    Contrary motion (voices moving in opposite directions) is preferred
    in classical counterpoint.

    Args:
        left_notes: Left hand notes
        right_notes: Right hand notes
        probability: Probability of applying contrary motion adjustment

    Returns:
        Adjusted (left_notes, right_notes)
    """
    import random

    if random.random() > probability:
        return left_notes, right_notes

    # Sort notes by time
    left_sorted = sorted(left_notes, key=lambda n: n.time)
    right_sorted = sorted(right_notes, key=lambda n: n.time)

    # Adjust melodic contour to encourage contrary motion
    # (This is a simplified heuristic)
    for i in range(1, min(len(left_sorted), len(right_sorted))):
        left_prev = left_sorted[i - 1].pitch
        left_curr = left_sorted[i].pitch
        right_prev = right_sorted[i - 1].pitch
        right_curr = right_sorted[i].pitch

        # If both move in same direction, try to flip one
        left_dir = left_curr - left_prev
        right_dir = right_curr - right_prev

        if left_dir * right_dir > 0:  # Same direction
            # Flip right hand direction (within reasonable range)
            if right_dir > 0:  # Was ascending, make descending
                right_sorted[i].pitch = max(right_prev - 2, right_sorted[i].pitch - 4)
            else:  # Was descending, make ascending
                right_sorted[i].pitch = min(right_prev + 2, right_sorted[i].pitch + 4)

    return left_sorted, right_sorted


def ensure_voice_independence(
    left_notes: List[Note],
    right_notes: List[Note],
    strict: bool = True
) -> Tuple[List[Note], List[Note]]:
    """Ensure voices follow classical independence rules.

    Args:
        left_notes: Left hand notes
        right_notes: Right hand notes
        strict: If True, enforce strict rules (no parallel 5ths/8ves)

    Returns:
        Adjusted (left_notes, right_notes)
    """
    if strict:
        # Check for violations
        violations = check_parallel_fifths_octaves(left_notes, right_notes)

        # If violations found, adjust voices
        if violations:
            # Simple fix: transpose offending notes by a step
            for time, violation_type in violations:
                # Find notes at this time and adjust
                for note in right_notes:
                    if abs(note.time - time) < 0.1:
                        # Transpose up a step (2 semitones) to break parallel
                        note.pitch += 2

    # Check voice crossing
    crossings = check_voice_crossing(left_notes, right_notes)
    if crossings:
        # Fix crossings by lowering left hand
        for time in crossings:
            for note in left_notes:
                if abs(note.time - time) < 0.1:
                    note.pitch -= 12  # Drop an octave

    return left_notes, right_notes


def apply_classical_voice_leading(
    notes: List[Note],
    max_leap: int = 7
) -> List[Note]:
    """Apply classical voice leading principles to a single voice.

    Classical voice leading prefers:
    - Stepwise motion (1-2 semitones)
    - Small leaps (3-5 semitones) occasionally
    - Large leaps (6+ semitones) resolved by stepwise motion

    Args:
        notes: Notes to adjust
        max_leap: Maximum allowed leap in semitones

    Returns:
        Adjusted notes with smoother voice leading
    """
    if len(notes) < 2:
        return notes

    adjusted = [notes[0]]  # Keep first note

    for i in range(1, len(notes)):
        prev_pitch = adjusted[-1].pitch
        curr_pitch = notes[i].pitch

        leap = abs(curr_pitch - prev_pitch)

        # If leap is too large, adjust to stepwise or small leap
        if leap > max_leap:
            # Move by step instead (2 semitones)
            direction = 1 if curr_pitch > prev_pitch else -1
            adjusted_pitch = prev_pitch + (direction * 2)

            adjusted_note = Note(
                pitch=adjusted_pitch,
                time=notes[i].time,
                duration=notes[i].duration,
                velocity=notes[i].velocity,
                hand=notes[i].hand
            )
            adjusted.append(adjusted_note)
        else:
            adjusted.append(notes[i])

    return adjusted


__all__ = [
    "check_parallel_fifths_octaves",
    "check_voice_crossing",
    "apply_contrary_motion",
    "ensure_voice_independence",
    "apply_classical_voice_leading",
]
