"""Jazz Improvisation Patterns

Implements jazz improvisation elements:
- ii-V-I licks (classic bebop vocabulary)
- Turnarounds (I-VI-ii-V patterns)
- Bebop runs (chromatic approach patterns)
- Arpeggios with chromatic approach

Key Concepts:
- ii-V-I: Most common jazz progression (Dm7 - G7 - Cmaj7)
- Turnaround: Harmonic pattern to return to tonic
- Bebop vocabulary: Standard jazz licks and phrases
- Chromatic approach: Half-step leading tones
"""

from typing import List
from app.gospel import Note, ChordContext


def generate_ii_v_lick(
    context: ChordContext,
    start_time: float = 0.0,
    duration_beats: float = 2.0,
    hand: str = "right"
) -> List[Note]:
    """Generate ii-V lick pattern.

    Classic bebop ii-V lick: Targets chord tones with chromatic approaches.

    Pattern (over 2 beats):
    - 8th notes targeting chord tones
    - Chromatic approach tones
    - Resolves to chord tone on beat 3

    Args:
        context: Chord context
        start_time: Start time in beats
        duration_beats: Duration of lick
        hand: Which hand ("left" or "right")

    Returns:
        List of lick notes
    """
    notes = []

    # ii-V lick pattern (8th notes)
    # Ascending pattern: Root, 2nd, 3rd, chromatic, 5th, 6th, 7th, root
    lick_intervals = [0, 2, 4, 5, 7, 9, 11, 12]  # C D E F G A B C
    base_midi = 60  # C4

    for i, interval in enumerate(lick_intervals):
        time = start_time + (i * 0.25)  # 16th notes for faster lick
        if time >= start_time + duration_beats:
            break

        pitch = base_midi + interval

        note = Note(
            pitch=pitch,
            time=time,
            duration=0.2,
            velocity=85 - (i % 2) * 5,  # Alternating dynamics
            hand=hand
        )
        notes.append(note)

    return notes


def generate_turnaround(
    context: ChordContext,
    start_time: float = 0.0,
    duration_beats: float = 4.0,
    hand: str = "right"
) -> List[Note]:
    """Generate jazz turnaround pattern.

    Turnaround: I-VI-ii-V progression (e.g., C-A7-Dm7-G7)
    Creates harmonic movement back to tonic.

    Pattern:
    - Arpeggiated chords with chromatic approaches
    - Quarter note pulse with 8th note fills

    Args:
        context: Chord context
        start_time: Start time in beats
        duration_beats: Duration of turnaround
        hand: Which hand

    Returns:
        List of turnaround notes
    """
    notes = []

    # Turnaround pattern (simplified to fit in 4 beats)
    # I: Root, 3rd, 5th
    # VI: Root, 3rd, 5th (chromatic approach)
    # ii: Root, b3, 5th
    # V: Root, 3rd, 5th (resolves to I)

    base_midi = 60  # C4

    # I chord (C) - beat 1
    i_chord = [0, 4, 7]  # Root, 3rd, 5th
    for i, interval in enumerate(i_chord):
        notes.append(Note(
            pitch=base_midi + interval,
            time=start_time + (i * 0.25),
            duration=0.2,
            velocity=80,
            hand=hand
        ))

    # VI chord (A7) - beat 2
    # Chromatic approach from above
    vi_chord = [9, 13, 16]  # A, C#, E (A7)
    for i, interval in enumerate(vi_chord):
        notes.append(Note(
            pitch=base_midi + interval,
            time=start_time + 1.0 + (i * 0.25),
            duration=0.2,
            velocity=78,
            hand=hand
        ))

    # ii chord (Dm7) - beat 3
    ii_chord = [2, 5, 9]  # D, F, A (Dm7)
    for i, interval in enumerate(ii_chord):
        notes.append(Note(
            pitch=base_midi + interval,
            time=start_time + 2.0 + (i * 0.25),
            duration=0.2,
            velocity=76,
            hand=hand
        ))

    # V chord (G7) - beat 4 (with chromatic approach to I)
    v_chord = [7, 11, 14]  # G, B, D (G7)
    for i, interval in enumerate(v_chord):
        notes.append(Note(
            pitch=base_midi + interval,
            time=start_time + 3.0 + (i * 0.25),
            duration=0.2,
            velocity=82,  # Louder to lead back
            hand=hand
        ))

    return notes


def generate_bebop_run(
    context: ChordContext,
    start_time: float = 0.0,
    duration_beats: float = 2.0,
    hand: str = "right",
    ascending: bool = True
) -> List[Note]:
    """Generate bebop run pattern.

    Bebop run: Fast 8th/16th note run using bebop scale.
    Adds chromatic passing tones to target chord tones on downbeats.

    Args:
        context: Chord context
        start_time: Start time
        duration_beats: Duration
        hand: Which hand
        ascending: If True, run ascends; else descends

    Returns:
        List of run notes
    """
    notes = []

    # Bebop scale (major with chromatic between 5-6)
    bebop_scale = [0, 2, 4, 5, 7, 8, 9, 11]  # C D E F G G# A B
    base_midi = 60  # C4

    if not ascending:
        bebop_scale = list(reversed([i + 12 for i in bebop_scale]))

    # Create 8th note run
    num_notes = int(duration_beats * 2)  # 8th notes
    for i in range(num_notes):
        interval = bebop_scale[i % len(bebop_scale)]
        octave_adjust = (i // len(bebop_scale)) * 12

        pitch = base_midi + interval + (octave_adjust if ascending else -octave_adjust)
        time = start_time + (i * 0.5)

        note = Note(
            pitch=pitch,
            time=time,
            duration=0.4,
            velocity=85 - (i % 4) * 3,  # Dynamic variation
            hand=hand
        )
        notes.append(note)

    return notes


def generate_chromatic_approach(
    target_pitch: int,
    start_time: float,
    hand: str = "right"
) -> List[Note]:
    """Generate chromatic approach to target note.

    Chromatic approach: Half-step below → target note.
    Classic bebop technique.

    Args:
        target_pitch: Target MIDI note
        start_time: Start time
        hand: Which hand

    Returns:
        List of approach notes
    """
    notes = []

    # Approach note (half-step below)
    notes.append(Note(
        pitch=target_pitch - 1,
        time=start_time,
        duration=0.25,
        velocity=75,
        hand=hand
    ))

    # Target note
    notes.append(Note(
        pitch=target_pitch,
        time=start_time + 0.25,
        duration=0.75,
        velocity=85,
        hand=hand
    ))

    return notes


__all__ = [
    "generate_ii_v_lick",
    "generate_turnaround",
    "generate_bebop_run",
    "generate_chromatic_approach",
]
