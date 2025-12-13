"""Enhanced MIDI Exporter for Gospel Piano

Exports gospel piano arrangements to professional multi-track MIDI files:
- Separate tracks for left and right hands
- Velocity curves and dynamic expression
- Sustain pedal automation
- Articulation markers (staccato, legato, tenuto)
"""

from pathlib import Path
from typing import List, Optional
from mido import MidiFile, MidiTrack, Message, MetaMessage

from app.gospel import Arrangement, Note


def export_enhanced_midi(
    arrangement: Arrangement,
    output_path: Path,
    include_pedal: bool = True,
    humanize: bool = True,
    program: int = 0  # 0 = Acoustic Grand Piano
) -> Path:
    """Export arrangement to multi-track MIDI file.

    Args:
        arrangement: Complete gospel piano arrangement
        output_path: Path to save MIDI file
        include_pedal: Add sustain pedal automation
        humanize: Add slight timing/velocity variations
        program: MIDI program number (default 0 = Acoustic Grand Piano)

    Returns:
        Path to created MIDI file
    """
    # Create MIDI file (Type 1 = multi-track)
    mid = MidiFile(type=1)

    # Ticks per beat (480 is standard for high resolution)
    ticks_per_beat = mid.ticks_per_beat

    # Calculate tempo in microseconds per beat
    microseconds_per_beat = int(60_000_000 / arrangement.tempo)

    # Track 0: Meta track (tempo, time signature, key signature)
    meta_track = MidiTrack()
    mid.tracks.append(meta_track)

    meta_track.append(MetaMessage('track_name', name='Gospel Piano', time=0))
    meta_track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat, time=0))
    meta_track.append(MetaMessage(
        'time_signature',
        numerator=arrangement.time_signature[0],
        denominator=arrangement.time_signature[1],
        time=0
    ))

    # Add key signature
    key_sharps = _get_key_sharps(arrangement.key)
    meta_track.append(MetaMessage('key_signature', key=key_sharps, time=0))
    meta_track.append(MetaMessage('end_of_track', time=0))

    # Track 1: Left hand
    left_track = _create_hand_track(
        notes=arrangement.left_hand_notes,
        track_name="Left Hand",
        channel=0,
        program=program,
        ticks_per_beat=ticks_per_beat,
        humanize=humanize,
        include_pedal=include_pedal
    )
    mid.tracks.append(left_track)

    # Track 2: Right hand
    right_track = _create_hand_track(
        notes=arrangement.right_hand_notes,
        track_name="Right Hand",
        channel=1,
        program=program,
        ticks_per_beat=ticks_per_beat,
        humanize=humanize,
        include_pedal=include_pedal
    )
    mid.tracks.append(right_track)

    # Save MIDI file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(output_path))

    return output_path


def _create_hand_track(
    notes: List[Note],
    track_name: str,
    channel: int,
    program: int,
    ticks_per_beat: int,
    humanize: bool,
    include_pedal: bool
) -> MidiTrack:
    """Create MIDI track for one hand.

    Args:
        notes: List of notes for this hand
        track_name: Track name
        channel: MIDI channel (0-15)
        program: MIDI program number
        ticks_per_beat: MIDI ticks per beat
        humanize: Add humanization
        include_pedal: Add sustain pedal

    Returns:
        MidiTrack object
    """
    import random

    track = MidiTrack()

    # Track metadata
    track.append(MetaMessage('track_name', name=track_name, time=0))
    track.append(Message('program_change', program=program, channel=channel, time=0))

    # Sort notes by time
    sorted_notes = sorted(notes, key=lambda n: n.time)

    if not sorted_notes:
        track.append(MetaMessage('end_of_track', time=0))
        return track

    # Convert notes to MIDI messages
    midi_events = []

    for note in sorted_notes:
        # Convert beat time to MIDI ticks
        note_start_ticks = int(note.time * ticks_per_beat)
        note_end_ticks = int((note.time + note.duration) * ticks_per_beat)

        # Humanization: slight random variations
        if humanize:
            # Timing jitter: +/-10 ticks (about +/-20ms at 480 ticks/beat, 120 BPM)
            timing_jitter = random.randint(-10, 10)
            note_start_ticks = max(0, note_start_ticks + timing_jitter)  # Ensure non-negative
            note_end_ticks = max(note_start_ticks + 1, note_end_ticks)  # Ensure end > start

            # Velocity variation: +/-3
            velocity_jitter = random.randint(-3, 3)
            velocity = max(1, min(127, note.velocity + velocity_jitter))
        else:
            velocity = note.velocity

        # Note on event
        midi_events.append({
            'type': 'note_on',
            'time': note_start_ticks,
            'note': note.pitch,
            'velocity': velocity,
            'channel': channel
        })

        # Note off event
        midi_events.append({
            'type': 'note_off',
            'time': note_end_ticks,
            'note': note.pitch,
            'velocity': 0,
            'channel': channel
        })

    # Add sustain pedal events
    if include_pedal and sorted_notes:
        # Add pedal down at start
        midi_events.append({
            'type': 'control_change',
            'time': 0,
            'control': 64,  # Sustain pedal CC
            'value': 127,  # Pedal down
            'channel': channel
        })

        # Add pedal up at end
        last_note_end = max(int((n.time + n.duration) * ticks_per_beat) for n in sorted_notes)
        midi_events.append({
            'type': 'control_change',
            'time': last_note_end,
            'control': 64,
            'value': 0,  # Pedal up
            'channel': channel
        })

    # Sort events by time
    midi_events.sort(key=lambda e: e['time'])

    # Convert to delta times and add to track
    current_time = 0
    for event in midi_events:
        delta_time = event['time'] - current_time
        current_time = event['time']

        if event['type'] == 'note_on':
            track.append(Message(
                'note_on',
                note=event['note'],
                velocity=event['velocity'],
                time=delta_time,
                channel=event['channel']
            ))
        elif event['type'] == 'note_off':
            track.append(Message(
                'note_off',
                note=event['note'],
                velocity=0,
                time=delta_time,
                channel=event['channel']
            ))
        elif event['type'] == 'control_change':
            track.append(Message(
                'control_change',
                control=event['control'],
                value=event['value'],
                time=delta_time,
                channel=event['channel']
            ))

    # End of track
    track.append(MetaMessage('end_of_track', time=0))

    return track


def _get_key_sharps(key: str) -> str:
    """Get key signature in sharps/flats.

    Args:
        key: Key name (e.g., "C", "F", "G")

    Returns:
        Key signature string for MIDI
    """
    # Major key signatures
    key_signatures = {
        "C": "C",
        "G": "G",
        "D": "D",
        "A": "A",
        "E": "E",
        "B": "B",
        "F#": "F#",
        "Gb": "Gb",
        "Db": "Db",
        "Ab": "Ab",
        "Eb": "Eb",
        "Bb": "Bb",
        "F": "F",
    }

    return key_signatures.get(key, "C")


def apply_crescendo(
    notes: List[Note],
    start_velocity: int = 60,
    end_velocity: int = 100
) -> List[Note]:
    """Apply crescendo (gradual increase in volume).

    Args:
        notes: Notes to transform
        start_velocity: Starting velocity
        end_velocity: Ending velocity

    Returns:
        Notes with crescendo applied
    """
    if not notes:
        return notes

    transformed = []
    num_notes = len(notes)

    for i, note in enumerate(notes):
        # Linear interpolation
        progress = i / (num_notes - 1) if num_notes > 1 else 0
        new_velocity = int(start_velocity + (end_velocity - start_velocity) * progress)

        transformed.append(Note(
            pitch=note.pitch,
            time=note.time,
            duration=note.duration,
            velocity=max(1, min(127, new_velocity)),
            hand=note.hand
        ))

    return transformed


def apply_decrescendo(
    notes: List[Note],
    start_velocity: int = 100,
    end_velocity: int = 60
) -> List[Note]:
    """Apply decrescendo (gradual decrease in volume).

    Args:
        notes: Notes to transform
        start_velocity: Starting velocity
        end_velocity: Ending velocity

    Returns:
        Notes with decrescendo applied
    """
    return apply_crescendo(notes, start_velocity, end_velocity)


def apply_accent_pattern(
    notes: List[Note],
    accent_positions: List[int],
    accent_boost: int = 20
) -> List[Note]:
    """Apply accents to specific beat positions.

    Args:
        notes: Notes to transform
        accent_positions: Beat positions to accent (e.g., [0, 2] for beats 1 and 3)
        accent_boost: Velocity increase for accented notes

    Returns:
        Notes with accents applied
    """
    transformed = []

    for note in notes:
        beat_position = int(note.time) % 4  # Beat within 4/4 bar

        if beat_position in accent_positions:
            new_velocity = min(127, note.velocity + accent_boost)
        else:
            new_velocity = note.velocity

        transformed.append(Note(
            pitch=note.pitch,
            time=note.time,
            duration=note.duration,
            velocity=new_velocity,
            hand=note.hand
        ))

    return transformed


__all__ = [
    "export_enhanced_midi",
    "apply_crescendo",
    "apply_decrescendo",
    "apply_accent_pattern",
]
