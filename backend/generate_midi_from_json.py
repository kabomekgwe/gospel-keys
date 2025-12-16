#!/usr/bin/env python
"""Generate MIDI files from JSON exercise content

Reads exercises from generated_content/exercises/exercises.json and creates
MIDI files for all exercises with musical content.
"""

import json
import sys
from pathlib import Path
from mido import MidiFile, MidiTrack, Message, MetaMessage


# Gospel piano voicings (MIDI note numbers)
CHORD_VOICINGS = {
    # Major 7th chords
    "Cmaj7": [60, 64, 67, 71], "Dmaj7": [62, 66, 69, 73], "Emaj7": [64, 68, 71, 75],
    "Fmaj7": [65, 69, 72, 76], "Gmaj7": [67, 71, 74, 78], "Amaj7": [69, 73, 76, 80],
    "Bmaj7": [71, 75, 78, 82],

    # Minor 7th chords
    "Dm7": [62, 65, 69, 72], "Em7": [64, 67, 71, 74], "Fm7": [65, 68, 72, 75],
    "Am7": [69, 72, 76, 79], "Bm7": [71, 74, 78, 81], "Cm7": [60, 63, 67, 70],
    "Gm7": [67, 70, 74, 77],

    # Dominant 7th chords
    "C7": [60, 64, 67, 70], "D7": [62, 66, 69, 72], "E7": [64, 68, 71, 74],
    "F7": [65, 69, 72, 75], "G7": [67, 71, 74, 77], "A7": [69, 73, 76, 79],
    "B7": [71, 75, 78, 81],

    # Extended chords (9th, 11th, 13th)
    "Cmaj9": [60, 64, 67, 71, 74], "Dmaj9": [62, 66, 69, 73, 76],
    "Fmaj9": [65, 69, 72, 76, 79], "Gmaj9": [67, 71, 74, 78, 81],

    "Dm9": [62, 65, 69, 72, 76], "Em9": [64, 67, 71, 74, 78],
    "Am9": [69, 72, 76, 79, 83], "Fm9": [65, 68, 72, 75, 79],
    "Cm9": [60, 63, 67, 70, 74], "Gm9": [67, 70, 74, 77, 81],

    "Dm11": [62, 65, 69, 72, 76, 79], "Am11": [69, 72, 76, 79, 83, 86],
    "Em11": [64, 67, 71, 74, 78, 81],

    "Cmaj13": [60, 64, 67, 71, 74, 81], "Fmaj13": [65, 69, 72, 76, 79, 86],

    "G9": [67, 71, 74, 77, 81], "D9": [62, 66, 69, 72, 76],
    "G13": [67, 71, 74, 77, 81, 88], "D13": [62, 66, 69, 72, 76, 83],
    "C13": [60, 64, 67, 70, 74, 81], "F13": [65, 69, 72, 75, 79, 86],

    # Sus chords
    "Gsus4": [67, 72, 74], "Dsus4": [62, 67, 69], "Csus4": [60, 65, 67],
    "G13sus4": [67, 72, 74, 77, 81, 88],

    # Altered dominants
    "G7b9": [67, 71, 74, 77, 80], "C7#9": [60, 64, 67, 70, 75],
    "Db7#11": [61, 65, 68, 71, 79], "E7alt": [64, 68, 71, 74, 77],
    "G7#11": [67, 71, 74, 77, 85], "A7b9": [69, 73, 76, 79, 82],

    # Diminished
    "Dbdim7": [61, 64, 67, 70], "Ebdim7": [63, 66, 69, 72],
    "Cdim7": [60, 63, 66, 69], "Ddim7": [62, 65, 68, 71],

    # Half-diminished
    "Bm7b5": [71, 74, 77, 81], "F#m7b5": [66, 69, 72, 76],
    "Dm7b5": [62, 65, 68, 72], "Em7b5": [64, 67, 70, 74],

    # Modal interchange
    "Ab13": [68, 72, 75, 79, 82, 89], "Bb13": [70, 74, 77, 81, 84, 91],
    "Ebmaj7": [63, 67, 70, 74], "Abmaj7": [68, 72, 75, 79],

    # Additional jazz voicings
    "Bbmaj7": [70, 74, 77, 81], "Dbmaj7": [61, 65, 68, 72],
    "Bb7": [70, 74, 77, 80], "Eb7": [63, 67, 70, 73],
    "Ab7": [68, 72, 75, 78], "Db7": [61, 65, 68, 71],
}


def create_chord_progression_midi(chords: list[str], key: str, bpm: int, output_path: Path):
    """Create a MIDI file from a chord progression"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo
    microseconds_per_beat = int(60_000_000 / bpm)
    track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat))

    # Set time signature (4/4)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # Ticks per beat
    ticks_per_beat = mid.ticks_per_beat

    # Each chord lasts 4 beats (1 bar)
    chord_duration = ticks_per_beat * 4

    for chord_name in chords:
        # Get voicing or use basic triad
        if chord_name not in CHORD_VOICINGS:
            print(f"      ⚠️  Unknown chord: {chord_name}, using C major")
            notes = CHORD_VOICINGS["Cmaj7"]
        else:
            notes = CHORD_VOICINGS[chord_name]

        # Play all notes together (chord)
        for note in notes:
            track.append(Message('note_on', note=note, velocity=80, time=0))

        # Hold for duration
        track.append(Message('note_off', note=notes[0], velocity=0, time=chord_duration))

        # Turn off remaining notes
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=0, time=0))

    # End of track
    track.append(MetaMessage('end_of_track'))

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(output_path))
    return output_path


def create_scale_midi(scale_notes: list[int], output_path: Path):
    """Create a MIDI file from scale notes"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo (120 BPM)
    track.append(MetaMessage('set_tempo', tempo=500_000))

    ticks_per_note = 240

    for note in scale_notes:
        track.append(Message('note_on', note=note, velocity=64, time=0))
        track.append(Message('note_off', note=note, velocity=0, time=ticks_per_note))

    track.append(MetaMessage('end_of_track'))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(output_path))
    return output_path


def create_lick_midi(midi_notes: list[dict], output_path: Path, bpm: int = 120):
    """Create a MIDI file from lick notes"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo
    microseconds_per_beat = int(60_000_000 / bpm)
    track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat))

    ticks_per_beat = mid.ticks_per_beat

    for note_data in midi_notes:
        pitch = note_data.get('pitch', 60)
        duration = note_data.get('duration', 0.5)  # in beats
        velocity = note_data.get('velocity', 64)

        duration_ticks = int(duration * ticks_per_beat)

        track.append(Message('note_on', note=pitch, velocity=velocity, time=0))
        track.append(Message('note_off', note=pitch, velocity=0, time=duration_ticks))

    track.append(MetaMessage('end_of_track'))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(output_path))
    return output_path


def main():
    """Generate MIDI files for all exercises"""
    print("=" * 80)
    print("🎹 MIDI File Generator from JSON Content")
    print("=" * 80)

    # Paths
    content_dir = Path(__file__).parent / "app" / "data" / "generated_content"
    exercises_file = content_dir / "exercises" / "exercises.json"
    midi_output_dir = content_dir / "midi"

    if not exercises_file.exists():
        print(f"❌ Exercises file not found: {exercises_file}")
        sys.exit(1)

    # Load exercises
    print(f"\n📂 Loading exercises from: {exercises_file}")
    with open(exercises_file, 'r') as f:
        exercises = json.load(f)  # Direct array load

    print(f"   Found {len(exercises)} exercises")

    # Generate MIDI files
    midi_output_dir.mkdir(parents=True, exist_ok=True)

    generated_count = 0
    skipped_count = 0

    print(f"\n🎵 Generating MIDI files...")
    print(f"   Output: {midi_output_dir}\n")

    for idx, exercise in enumerate(exercises, 1):
        exercise_type = exercise.get('exercise_type', 'unknown')
        title = exercise.get('title', f'Exercise {idx}')
        content = exercise.get('content', {})

        # Create safe filename
        safe_name = title.replace(" ", "_").replace("/", "-").replace(":", "")
        safe_name = f"{idx:03d}_{safe_name}"

        try:
            if exercise_type == "progression" and "chords" in content:
                chords = content.get('chords', [])
                key = content.get('key', 'C')
                bpm = content.get('bpm', 80)

                midi_path = midi_output_dir / f"{safe_name}.mid"
                create_chord_progression_midi(chords, key, bpm, midi_path)

                print(f"   ✅ {idx:3d}. {title}")
                print(f"         Type: {exercise_type} | Chords: {len(chords)} | {midi_path.name}")
                generated_count += 1

            elif exercise_type == "scale" and "notes" in content:
                notes = content.get('notes', [])

                midi_path = midi_output_dir / f"{safe_name}.mid"
                create_scale_midi(notes, midi_path)

                print(f"   ✅ {idx:3d}. {title}")
                print(f"         Type: {exercise_type} | Notes: {len(notes)} | {midi_path.name}")
                generated_count += 1

            elif exercise_type == "lick" and "midi_notes" in content:
                midi_notes = content.get('midi_notes', [])
                bpm = content.get('bpm', 120)

                midi_path = midi_output_dir / f"{safe_name}.mid"
                create_lick_midi(midi_notes, midi_path, bpm)

                print(f"   ✅ {idx:3d}. {title}")
                print(f"         Type: {exercise_type} | Notes: {len(midi_notes)} | {midi_path.name}")
                generated_count += 1

            else:
                skipped_count += 1
                if idx <= 10:  # Only show first 10 skipped
                    print(f"   ⏭️  {idx:3d}. {title} (type: {exercise_type}, no musical content)")

        except Exception as e:
            print(f"   ❌ {idx:3d}. {title} - Error: {e}")
            skipped_count += 1

    # Summary
    print(f"\n{'=' * 80}")
    print("✅ MIDI GENERATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"\n📊 Summary:")
    print(f"   Total exercises: {len(exercises)}")
    print(f"   MIDI files generated: {generated_count}")
    print(f"   Skipped (no musical content): {skipped_count}")
    print(f"\n📁 Output directory: {midi_output_dir.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
