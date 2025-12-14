"""Gospel Improvisation Patterns

Implements gospel piano improvisation elements:
- Chromatic runs (connecting chord tones)
- Pentatonic fills (bluesy gospel runs)
- Scalar runs (mode-based runs)
- Turnarounds (phrase endings)
- Gospel fills (between chord changes)
"""

from typing import List, Tuple
from app.gospel import Note, ChordContext
from app.gospel.patterns.left_hand import parse_chord_symbol, get_chord_tones, NOTE_TO_MIDI


# Pentatonic scale intervals (major and minor)
PENTATONIC_SCALES = {
    "major": [0, 2, 4, 7, 9],  # Major pentatonic
    "minor": [0, 3, 5, 7, 10],  # Minor pentatonic (blues scale base)
}

# Mode intervals
MODES = {
    "ionian": [0, 2, 4, 5, 7, 9, 11],      # Major scale
    "dorian": [0, 2, 3, 5, 7, 9, 10],      # Minor with raised 6th
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],  # Major with lowered 7th
    "aeolian": [0, 2, 3, 5, 7, 8, 10],     # Natural minor
}


def generate_chromatic_run(
    start_note: int,
    target_note: int,
    start_time: float,
    duration_beats: float,
    hand: str = "right"
) -> List[Note]:
    """Generate chromatic run connecting two notes.

    Creates a chromatic (half-step) run from start to target.
    Classic gospel run between chord changes.

    Args:
        start_note: Starting MIDI note number
        target_note: Target MIDI note number
        start_time: Beat position to start run
        duration_beats: Total duration for run
        hand: Which hand plays ("left" or "right")

    Returns:
        List of notes forming chromatic run
    """
    # Determine direction (ascending or descending)
    direction = 1 if target_note > start_note else -1
    distance = abs(target_note - start_note)

    # Generate chromatic notes
    chromatic_notes = []
    current_pitch = start_note

    # Calculate note duration (evenly spaced)
    if distance > 0:
        note_duration = duration_beats / distance
    else:
        return [Note(pitch=start_note, time=start_time, duration=duration_beats,
                    velocity=80, hand=hand)]

    # Create run
    for i in range(distance):
        time = start_time + (i * note_duration)

        # Velocity curve: crescendo into target
        velocity = 70 + int((i / distance) * 20)

        chromatic_notes.append(
            Note(
                pitch=current_pitch,
                time=time,
                duration=note_duration,
                velocity=min(velocity, 100),
                hand=hand
            )
        )

        current_pitch += direction

    return chromatic_notes


def generate_pentatonic_fill(
    root_note: int,
    scale_type: str,
    start_time: float,
    duration_beats: float,
    direction: str = "ascending",
    hand: str = "right"
) -> List[Note]:
    """Generate pentatonic fill (bluesy gospel run).

    Args:
        root_note: Root note MIDI number
        scale_type: "major" or "minor" pentatonic
        start_time: Beat position to start
        duration_beats: Total duration
        direction: "ascending", "descending", or "both"
        hand: Which hand plays

    Returns:
        List of notes forming pentatonic fill
    """
    intervals = PENTATONIC_SCALES.get(scale_type, PENTATONIC_SCALES["major"])

    # Generate pentatonic scale notes
    scale_notes = [root_note + interval for interval in intervals]

    # Add octave for longer runs
    if direction == "both":
        scale_notes.extend([root_note + interval + 12 for interval in intervals])

    if direction == "descending":
        scale_notes.reverse()
    elif direction == "both":
        # Ascending then descending
        full_pattern = scale_notes + list(reversed(scale_notes[:-1]))
        scale_notes = full_pattern

    # Create notes with timing
    num_notes = len(scale_notes)
    note_duration = duration_beats / num_notes if num_notes > 0 else duration_beats

    fill_notes = []
    for i, pitch in enumerate(scale_notes):
        time = start_time + (i * note_duration)

        # Velocity curve with slight accents on beats
        base_velocity = 75
        is_on_beat = (i % 2 == 0)
        velocity = base_velocity + (10 if is_on_beat else 0)

        fill_notes.append(
            Note(
                pitch=pitch,
                time=time,
                duration=note_duration,
                velocity=velocity,
                hand=hand
            )
        )

    return fill_notes


def generate_scalar_run(
    root_note: int,
    mode: str,
    start_time: float,
    duration_beats: float,
    octaves: int = 1,
    direction: str = "ascending",
    hand: str = "right"
) -> List[Note]:
    """Generate modal scalar run.

    Args:
        root_note: Root note MIDI number
        mode: Mode name ("ionian", "dorian", "mixolydian", "aeolian")
        start_time: Beat position to start
        duration_beats: Total duration
        octaves: Number of octaves to span
        direction: "ascending" or "descending"
        hand: Which hand plays

    Returns:
        List of notes forming scalar run
    """
    intervals = MODES.get(mode, MODES["ionian"])

    # Generate scale notes across octaves
    scale_notes = []
    for octave in range(octaves):
        for interval in intervals:
            scale_notes.append(root_note + interval + (octave * 12))

    # Add final octave note
    scale_notes.append(root_note + (octaves * 12))

    if direction == "descending":
        scale_notes.reverse()

    # Create notes with timing
    num_notes = len(scale_notes)
    note_duration = duration_beats / num_notes if num_notes > 0 else duration_beats

    run_notes = []
    for i, pitch in enumerate(scale_notes):
        time = start_time + (i * note_duration)

        # Velocity curve
        progress = i / num_notes if num_notes > 0 else 0
        if direction == "ascending":
            velocity = 70 + int(progress * 25)  # Crescendo
        else:
            velocity = 95 - int(progress * 25)  # Decrescendo

        run_notes.append(
            Note(
                pitch=pitch,
                time=time,
                duration=note_duration,
                velocity=velocity,
                hand=hand
            )
        )

    return run_notes


def generate_turnaround(
    context: ChordContext,
    start_time: float,
    duration_beats: float = 2.0,
    hand: str = "right"
) -> List[Note]:
    """Generate gospel turnaround phrase.

    Turnarounds are short phrases (2-4 beats) that return to tonic.
    Common at end of 4 or 8 bar phrases.

    Args:
        context: Chord context for turnaround
        start_time: Beat position to start
        duration_beats: Duration of turnaround
        hand: Which hand plays

    Returns:
        List of notes forming turnaround
    """
    chord_tones = get_chord_tones(context.chord, octave=4 if hand == "right" else 2)

