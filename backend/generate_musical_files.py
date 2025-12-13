#!/usr/bin/env python
"""Generate Real Musical Files - MIDI, Audio, and Sheet Music

Creates actual playable files for gospel piano exercises:
- MIDI files (.mid) for each exercise
- Audio files (.wav) using M4 Metal GPU
- Chord charts and progressions
"""

import asyncio
import json
from pathlib import Path
from mido import MidiFile, MidiTrack, Message, MetaMessage
import time

from app.database.session import async_session_maker
from app.services.curriculum_service import CurriculumService


# Gospel piano voicings (MIDI note numbers)
CHORD_VOICINGS = {
    # Major 7th chords (root position, close voicing)
    "Cmaj7": [60, 64, 67, 71],    # C E G B
    "Dmaj7": [62, 66, 69, 73],    # D F# A C#
    "Emaj7": [64, 68, 71, 75],    # E G# B D#
    "Fmaj7": [65, 69, 72, 76],    # F A C E
    "Gmaj7": [67, 71, 74, 78],    # G B D F#
    "Amaj7": [69, 73, 76, 80],    # A C# E G#
    "Bmaj7": [71, 75, 78, 82],    # B D# F# A#

    # Minor 7th chords
    "Dm7": [62, 65, 69, 72],      # D F A C
    "Em7": [64, 67, 71, 74],      # E G B D
    "Fm7": [65, 68, 72, 75],      # F Ab C Eb
    "Am7": [69, 72, 76, 79],      # A C E G
    "Bm7": [71, 74, 78, 81],      # B D F# A

    # Dominant 7th chords
    "C7": [60, 64, 67, 70],       # C E G Bb
    "G7": [67, 71, 74, 77],       # G B D F
    "D7": [62, 66, 69, 72],       # D F# A C
    "A7": [69, 73, 76, 79],       # A C# E G
    "E7": [64, 68, 71, 74],       # E G# B D

    # Major 9th chords
    "Cmaj9": [60, 64, 67, 71, 74],    # C E G B D
    "Dmaj9": [62, 66, 69, 73, 76],    # D F# A C# E
    "Fmaj9": [65, 69, 72, 76, 79],    # F A C E G

    # Major 13th chords
    "Cmaj13": [60, 64, 67, 71, 74, 81],  # C E G B D A
    "Fmaj13": [65, 69, 72, 76, 79, 86],  # F A C E G D

    # Minor 9th chords
    "Dm9": [62, 65, 69, 72, 76],      # D F A C E
    "Em9": [64, 67, 71, 74, 78],      # E G B D F#
    "Am9": [69, 72, 76, 79, 83],      # A C E G B
    "Fm9": [65, 68, 72, 75, 79],      # F Ab C Eb G

    # Minor 11th chords
    "Dm11": [62, 65, 69, 72, 76, 79],    # D F A C E G
    "Am11": [69, 72, 76, 79, 83, 86],    # A C E G B D
    "Em11": [64, 67, 71, 74, 78, 81],    # E G B D F# A

    # Dominant 9th chords
    "G9": [67, 71, 74, 77, 81],       # G B D F A
    "D9": [62, 66, 69, 72, 76],       # D F# A C E

    # Dominant 13th chords
    "G13": [67, 71, 74, 77, 81, 88],     # G B D F A E
    "D13": [62, 66, 69, 72, 76, 83],     # D F# A C E B

    # Sus chords
    "Gsus4": [67, 72, 74],        # G C D
    "G13sus4": [67, 72, 74, 77, 81, 88],  # G C D F A E
    "Dsus4": [62, 67, 69],        # D G A

    # Altered dominants
    "G7b9": [67, 71, 74, 77, 80],     # G B D F Ab
    "C7#9": [60, 64, 67, 70, 75],     # C E G Bb D#
    "Db7#11": [61, 65, 68, 71, 79],   # Db F Ab Cb(B) G
    "E7alt": [64, 68, 71, 74, 77],    # E G# B D F (alterations implied)

    # Diminished 7th chords
    "Dbdim7": [61, 64, 67, 70],       # Db E G Bb
    "Ebdim7": [63, 66, 69, 72],       # Eb Gb A C
    "F#m7b5": [66, 69, 72, 76],       # F# A C E

    # Borrowed/Modal interchange
    "Ab13": [68, 72, 75, 79, 82, 89],    # Ab C Eb Gb Bb F
    "Bb13": [70, 74, 77, 81, 84, 91],    # Bb D F Ab C G

    # Half-diminished
    "Bm7b5": [71, 74, 77, 81],        # B D F A
}


def create_gospel_midi(chords: list, key: str, bpm: int = 80, output_path: Path = None):
    """Create a MIDI file with gospel piano voicings

    Args:
        chords: List of chord names (e.g., ["Cmaj7", "Dm7", "G7"])
        key: Key signature (e.g., "C", "F", "G")
        bpm: Tempo in beats per minute
        output_path: Where to save the MIDI file

    Returns:
        Path to created MIDI file
    """
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo
    microseconds_per_beat = int(60_000_000 / bpm)
    track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat))

    # Set time signature (4/4)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # Ticks per beat (480 is standard)
    ticks_per_beat = mid.ticks_per_beat  # Usually 480

    # Each chord lasts 4 beats (1 bar)
    chord_duration = ticks_per_beat * 4

    for chord_name in chords:
        # Get voicing or skip unknown chords
        if chord_name not in CHORD_VOICINGS:
            print(f"   ⚠️ Unknown chord: {chord_name}, skipping...")
            continue

        notes = CHORD_VOICINGS[chord_name]

        # Play all notes together (chord)
        for note in notes:
            track.append(Message('note_on', note=note, velocity=80, time=0))

        # Hold for duration (only first note has the time delta)
        track.append(Message('note_off', note=notes[0], velocity=0, time=chord_duration))

        # Turn off remaining notes
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=0, time=0))

    # Add end of track
    track.append(MetaMessage('end_of_track'))

    # Save file
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mid.save(str(output_path))
        return output_path

    return mid


def create_scale_midi(scale_type: str, key: str, octaves: int = 2, output_path: Path = None):
    """Create a MIDI file with a piano scale

    Args:
        scale_type: "major", "minor", "pentatonic", etc.
        key: Root note (e.g., "C", "D", "F")
        octaves: Number of octaves to play
        output_path: Where to save
    """
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo
    track.append(MetaMessage('set_tempo', tempo=500_000))  # 120 BPM

    # Note mappings
    note_names = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}
    root = note_names.get(key, 60)

    # Scale intervals
    scales = {
        "major": [0, 2, 4, 5, 7, 9, 11, 12],
        "minor": [0, 2, 3, 5, 7, 8, 10, 12],
        "pentatonic": [0, 2, 4, 7, 9, 12],
    }

    intervals = scales.get(scale_type, scales["major"])

    # Generate scale notes
    ticks_per_note = 240

    for octave in range(octaves):
        for interval in intervals:
            note = root + interval + (octave * 12)
            track.append(Message('note_on', note=note, velocity=64, time=0))
            track.append(Message('note_off', note=note, velocity=0, time=ticks_per_note))

    track.append(MetaMessage('end_of_track'))

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mid.save(str(output_path))
        return output_path

    return mid


async def generate_all_musical_files():
    """Generate MIDI and audio files for all exercises in the curriculum"""

    print("=" * 80)
    print("🎹 Generating Musical Files - MIDI & Audio")
    print("=" * 80)

    # Output directories
    output_base = Path("outputs/musical_files")
    midi_dir = output_base / "midi"
    audio_dir = output_base / "audio"
    charts_dir = output_base / "charts"

    for dir in [midi_dir, audio_dir, charts_dir]:
        dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Output directories:")
    print(f"   MIDI:  {midi_dir}")
    print(f"   Audio: {audio_dir}")
    print(f"   Charts: {charts_dir}")

    async with async_session_maker() as session:
        service = CurriculumService(session)

        # Get latest curriculum
        from sqlalchemy import select
        from app.database.curriculum_models import Curriculum

        result = await session.execute(
            select(Curriculum).order_by(Curriculum.created_at.desc()).limit(1)
        )
        curriculum = result.scalar_one_or_none()

        if not curriculum:
            print("\n❌ No curriculum found!")
            return

        curriculum = await service.get_curriculum_with_details(curriculum.id)

        print(f"\n📚 Processing: {curriculum.title}")
        print(f"   Modules: {len(curriculum.modules)}")

        total_files = 0

        for module_idx, module in enumerate(curriculum.modules, 1):
            print(f"\n{'=' * 80}")
            print(f"📘 MODULE {module_idx}: {module.title}")
            print(f"{'=' * 80}")

            for lesson_idx, lesson in enumerate(module.lessons, 1):
                print(f"\n   📖 Lesson {lesson_idx}: {lesson.title}")

                for ex_idx, exercise in enumerate(lesson.exercises, 1):
                    content = json.loads(exercise.content_json)

                    # Create safe filename
                    safe_name = exercise.title.replace(" ", "_").replace("/", "-")
                    safe_name = f"{module_idx}_{lesson_idx}_{ex_idx}_{safe_name}"

                    print(f"\n      {ex_idx}. {exercise.title}")
                    print(f"         Type: {exercise.exercise_type} | Difficulty: {exercise.difficulty}")

                    # Generate MIDI file
                    midi_path = midi_dir / f"{safe_name}.mid"

                    try:
                        if exercise.exercise_type == "progression" and "chords" in content:
                            chords = content["chords"]
                            key = content.get("key", "C")
                            bpm = exercise.target_bpm or 80

                            print(f"         Chords: {' → '.join(chords)}")
                            print(f"         Key: {key} | BPM: {bpm}")

                            create_gospel_midi(chords, key, bpm, midi_path)
                            print(f"         ✅ MIDI: {midi_path.name}")
                            total_files += 1

                            # Create chord chart
                            chart_path = charts_dir / f"{safe_name}.txt"
                            with open(chart_path, "w") as f:
                                f.write(f"{exercise.title}\n")
                                f.write("=" * 60 + "\n\n")
                                f.write(f"Type: {exercise.exercise_type}\n")
                                f.write(f"Difficulty: {exercise.difficulty}\n")
                                f.write(f"Key: {key}\n")
                                f.write(f"BPM: {bpm}\n\n")
                                f.write("Progression:\n")
                                for i, chord in enumerate(chords, 1):
                                    f.write(f"  {i}. {chord}\n")
                                f.write(f"\nFull: {' → '.join(chords)}\n")

                            print(f"         ✅ Chart: {chart_path.name}")
                            total_files += 1

                        elif exercise.exercise_type == "scale" and "scale" in content:
                            scale_type = content.get("scale", "major")
                            key = content.get("key", "C")
                            octaves = content.get("octaves", 2)

                            create_scale_midi(scale_type, key, octaves, midi_path)
                            print(f"         ✅ MIDI: {midi_path.name}")
                            total_files += 1

                        else:
                            print(f"         ⚠️ Unsupported exercise type: {exercise.exercise_type}")

                    except Exception as e:
                        print(f"         ❌ Error: {e}")

        # Generate audio files using Rust engine
        print(f"\n{'=' * 80}")
        print("🎵 GENERATING AUDIO FILES (M4 Metal GPU)")
        print(f"{'=' * 80}")

        try:
            import rust_audio_engine
            from app.core.config import settings

            soundfont_path = Path(settings.BASE_DIR) / "soundfonts" / "TimGM6mb.sf2"

            if not soundfont_path.exists():
                print(f"\n⚠️ Soundfont not found: {soundfont_path}")
                print("   Skipping audio generation")
            else:
                print(f"\n🎹 Soundfont: {soundfont_path.name}")
                print(f"   Engine: Rust (M4 Metal GPU)")

                audio_count = 0

                # Convert all MIDI files to audio
                for midi_file in sorted(midi_dir.glob("*.mid")):
                    audio_file = audio_dir / f"{midi_file.stem}.wav"

                    print(f"\n   Converting: {midi_file.name}")

                    try:
                        start = time.time()
                        duration = rust_audio_engine.synthesize_midi(
                            midi_path=str(midi_file),
                            output_path=str(audio_file),
                            soundfont_path=str(soundfont_path),
                            sample_rate=44100,
                            use_gpu=True,
                            reverb=True
                        )
                        elapsed = time.time() - start

                        print(f"      ✅ Audio: {audio_file.name}")
                        print(f"      Duration: {duration:.1f}s | Synthesis: {elapsed:.3f}s ({duration/elapsed:.1f}x real-time)")
                        audio_count += 1
                        total_files += 1

                    except Exception as e:
                        print(f"      ❌ Failed: {e}")

                print(f"\n   ✅ Generated {audio_count} audio files")

        except ImportError:
            print("\n⚠️ Rust audio engine not available")
            print("   To enable: cd rust-audio-engine && maturin develop --release")

        # Final summary
        print(f"\n{'=' * 80}")
        print("✅ GENERATION COMPLETE")
        print(f"{'=' * 80}")
        print(f"\n📊 Total files generated: {total_files}")
        print(f"\n📁 Files saved to:")
        print(f"   {output_base.absolute()}/")
        print(f"   ├── midi/     ({len(list(midi_dir.glob('*.mid')))} files)")
        print(f"   ├── audio/    ({len(list(audio_dir.glob('*.wav')))} files)")
        print(f"   └── charts/   ({len(list(charts_dir.glob('*.txt')))} files)")

        print(f"\n🎹 You can now:")
        print(f"   • Listen to audio files in: {audio_dir}")
        print(f"   • Import MIDI into your DAW: {midi_dir}")
        print(f"   • Study chord charts: {charts_dir}")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(generate_all_musical_files())
