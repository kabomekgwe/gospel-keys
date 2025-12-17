"""MIDI Generation Service for Curriculum Exercises

Converts exercise content (progressions, scales, voicings) into playable MIDI files.
Supports various exercise types with intelligent voicing and arrangement.
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import pretty_midi
import musicpy as mp
from music21 import note, chord as m21_chord, scale, stream, tempo

from app.database.curriculum_models import CurriculumExercise
from app.core.config import settings

logger = logging.getLogger(__name__)


class MIDIGenerationService:
    """Service for generating MIDI files from curriculum exercises
    
    All MIDI generation is DYNAMIC - even with identical input parameters,
    output will vary due to humanization (velocity, timing, duration).
    """

    def __init__(self):
        self.output_dir = Path(settings.OUTPUTS_DIR) / "exercises" / "midi"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # MIDI settings (base values - will be humanized)
        self.default_velocity = 80
        self.piano_program = 0  # Acoustic Grand Piano
        
        # Humanization parameters
        self.velocity_variance = 8      # ±8 from base velocity
        self.timing_variance_ms = 15    # ±15ms timing offset
        self.duration_variance = 0.05   # ±5% duration variation
    
    def _humanize_velocity(self, base_velocity: int = None) -> int:
        """Add human-like velocity variation"""
        base = base_velocity or self.default_velocity
        humanized = base + random.randint(-self.velocity_variance, self.velocity_variance)
        return max(1, min(127, humanized))  # Clamp to valid MIDI range
    
    def _humanize_timing(self, base_time: float) -> float:
        """Add subtle timing variation (in seconds)"""
        offset = random.uniform(-self.timing_variance_ms, self.timing_variance_ms) / 1000.0
        return max(0.0, base_time + offset)
    
    def _humanize_duration(self, base_duration: float) -> float:
        """Add duration variation"""
        variance = random.uniform(-self.duration_variance, self.duration_variance)
        return base_duration * (1.0 + variance)

        # Note mappings
        self.note_to_midi = {
            'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
            'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
            'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
        }

    async def generate_exercise_midi(
        self,
        exercise: CurriculumExercise
    ) -> Path:
        """Generate MIDI file for a curriculum exercise

        Args:
            exercise: CurriculumExercise model instance

        Returns:
            Path to generated MIDI file
        """
        try:
            content = json.loads(exercise.content_json)
            exercise_type = exercise.exercise_type

            # Route to appropriate generator based on exercise type
            if exercise_type == "progression":
                midi_path = await self.generate_progression_midi(
                    exercise_id=exercise.id,
                    chords=content.get("chords", []),
                    key=content.get("key", "C"),
                    bpm=exercise.target_bpm or 90
                )
            elif exercise_type == "scale":
                midi_path = await self.generate_scale_midi(
                    exercise_id=exercise.id,
                    scale_name=content.get("scale", "major"),
                    key=content.get("key", "C"),
                    octaves=content.get("octaves", 2),
                    bpm=exercise.target_bpm or 100
                )
            elif exercise_type == "voicing":
                midi_path = await self.generate_voicing_midi(
                    exercise_id=exercise.id,
                    chord=content.get("chord", "Cmaj7"),
                    voicing_type=content.get("voicing_type", "open"),
                    notes=content.get("notes", []),
                    bpm=exercise.target_bpm or 60
                )
            elif exercise_type == "pattern":
                midi_path = await self.generate_pattern_midi(
                    exercise_id=exercise.id,
                    pattern=content.get("pattern", []),
                    key=content.get("key", "C"),
                    bpm=exercise.target_bpm or 100
                )
            else:
                logger.warning(f"Unsupported exercise type: {exercise_type}")
                # Generate a simple placeholder MIDI
                midi_path = await self._generate_placeholder_midi(exercise.id)

            logger.info(f"Generated MIDI for exercise {exercise.id}: {midi_path}")
            return midi_path

        except Exception as e:
            logger.error(f"Failed to generate MIDI for exercise {exercise.id}: {e}")
            raise e

    async def generate_progression_midi(
        self,
        exercise_id: str,
        chords: List[str],
        key: str = "C",
        bpm: int = 90,
        beats_per_chord: int = 4
    ) -> Path:
        """Generate MIDI for a chord progression

        Args:
            exercise_id: Unique exercise identifier
            chords: List of chord symbols (e.g., ["Dm7", "G7", "Cmaj7"])
            key: Key signature
            bpm: Tempo in beats per minute
            beats_per_chord: How many beats each chord lasts

        Returns:
            Path to generated MIDI file
        """
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        piano = pretty_midi.Instrument(program=self.piano_program)

        current_time = 0.0
        beat_duration = 60.0 / bpm
        chord_duration = beat_duration * beats_per_chord

        for chord_symbol in chords:
            try:
                # Use musicpy to parse chord and get voicing
                musicpy_chord = mp.translate(chord_symbol)

                # Get MIDI note numbers for the chord
                midi_notes = [n.degree for n in musicpy_chord.notes]

                # Add notes to MIDI with humanization for dynamic output
                for i, midi_note in enumerate(midi_notes):
                    # Humanize each note slightly differently
                    humanized_start = self._humanize_timing(current_time)
                    humanized_duration = self._humanize_duration(chord_duration)
                    humanized_velocity = self._humanize_velocity()
                    
                    # Slight stagger for chord notes (more realistic)
                    stagger = i * random.uniform(0.005, 0.015)
                    
                    note = pretty_midi.Note(
                        velocity=humanized_velocity,
                        pitch=midi_note,
                        start=humanized_start + stagger,
                        end=humanized_start + humanized_duration
                    )
                    piano.notes.append(note)

                current_time += chord_duration

            except Exception as e:
                logger.warning(f"Failed to parse chord {chord_symbol}: {e}")
                continue

        midi.instruments.append(piano)

        # Save MIDI file
        output_path = self.output_dir / f"{exercise_id}_progression.mid"
        midi.write(str(output_path))

        return output_path

    async def generate_scale_midi(
        self,
        exercise_id: str,
        scale_name: str,
        key: str = "C",
        octaves: int = 2,
        bpm: int = 100
    ) -> Path:
        """Generate MIDI for a scale exercise

        Args:
            exercise_id: Unique exercise identifier
            scale_name: Scale type (major, minor, dorian, etc.)
            key: Root note
            octaves: Number of octaves to play
            bpm: Tempo

        Returns:
            Path to generated MIDI file
        """
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        piano = pretty_midi.Instrument(program=self.piano_program)

        # Use music21 to generate scale
        try:
            if scale_name.lower() == "major":
                m21_scale = scale.MajorScale(key)
            elif scale_name.lower() == "minor":
                m21_scale = scale.MinorScale(key)
            elif scale_name.lower() == "dorian":
                m21_scale = scale.DorianScale(key)
            elif scale_name.lower() == "mixolydian":
                m21_scale = scale.MixolydianScale(key)
            else:
                # Default to major
                m21_scale = scale.MajorScale(key)

            # Get scale pitches
            pitches = []
            base_octave = 4
            for octave in range(octaves):
                for degree in range(1, 8):  # 1-7 scale degrees
                    pitch_name = m21_scale.pitchFromDegree(degree)
                    pitch_name.octave = base_octave + octave
                    pitches.append(pitch_name.midi)

            # Add descending
            pitches.extend(reversed(pitches[:-1]))

            # Generate notes
            beat_duration = 60.0 / bpm
            note_duration = beat_duration / 2  # Eighth notes
            current_time = 0.0

            for pitch in pitches:
                note = pretty_midi.Note(
                    velocity=self._humanize_velocity(),
                    pitch=pitch,
                    start=self._humanize_timing(current_time),
                    end=self._humanize_timing(current_time) + self._humanize_duration(note_duration)
                )
                piano.notes.append(note)
                current_time += note_duration

        except Exception as e:
            logger.error(f"Failed to generate scale: {e}")
            raise e

        midi.instruments.append(piano)

        # Save MIDI file
        output_path = self.output_dir / f"{exercise_id}_scale.mid"
        midi.write(str(output_path))

        return output_path

    async def generate_voicing_midi(
        self,
        exercise_id: str,
        chord: str,
        voicing_type: str = "open",
        notes: List[str] = None,
        bpm: int = 60
    ) -> Path:
        """Generate MIDI for a chord voicing exercise

        Args:
            exercise_id: Unique exercise identifier
            chord: Chord symbol
            voicing_type: Type of voicing (open, closed, drop2, etc.)
            notes: Explicit note names if provided
            bpm: Tempo

        Returns:
            Path to generated MIDI file
        """
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        piano = pretty_midi.Instrument(program=self.piano_program)

        # Get MIDI notes
        if notes:
            # Use provided notes
            midi_notes = [self._note_name_to_midi(n) for n in notes]
        else:
            # Generate voicing using musicpy
            try:
                musicpy_chord = mp.translate(chord)

                # Apply voicing type transformations
                if voicing_type == "drop2":
                    musicpy_chord = musicpy_chord.drop(2)
                elif voicing_type == "rootless":
                    musicpy_chord = musicpy_chord.omit(1)

                midi_notes = [n.degree for n in musicpy_chord.notes]

            except Exception as e:
                logger.error(f"Failed to generate voicing for {chord}: {e}")
                raise e

        # Create a held chord (4 beats)
        beat_duration = 60.0 / bpm
        chord_duration = beat_duration * 4

        for i, midi_note in enumerate(midi_notes):
            # Add human-like stagger to chord notes
            stagger = i * random.uniform(0.005, 0.015)
            note = pretty_midi.Note(
                velocity=self._humanize_velocity(),
                pitch=midi_note,
                start=stagger,
                end=self._humanize_duration(chord_duration)
            )
            piano.notes.append(note)

        midi.instruments.append(piano)

        # Save MIDI file
        output_path = self.output_dir / f"{exercise_id}_voicing.mid"
        midi.write(str(output_path))

        return output_path

    async def generate_pattern_midi(
        self,
        exercise_id: str,
        pattern: List[Dict],
        key: str = "C",
        bpm: int = 100
    ) -> Path:
        """Generate MIDI for a musical pattern/lick

        Args:
            exercise_id: Unique exercise identifier
            pattern: List of notes with timing info
                     [{"note": "C", "duration": 0.5}, ...]
            key: Key context
            bpm: Tempo

        Returns:
            Path to generated MIDI file
        """
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        piano = pretty_midi.Instrument(program=self.piano_program)

        current_time = 0.0

        for note_info in pattern:
            note_name = note_info.get("note", "C")
            duration = note_info.get("duration", 0.5)

            midi_note = self._note_name_to_midi(note_name)

            note = pretty_midi.Note(
                velocity=self._humanize_velocity(),
                pitch=midi_note,
                start=self._humanize_timing(current_time),
                end=self._humanize_timing(current_time) + self._humanize_duration(duration)
            )
            piano.notes.append(note)
            current_time += duration

        midi.instruments.append(piano)

        # Save MIDI file
        output_path = self.output_dir / f"{exercise_id}_pattern.mid"
        midi.write(str(output_path))

        return output_path

    async def _generate_placeholder_midi(self, exercise_id: str) -> Path:
        """Generate a simple placeholder MIDI for unsupported types"""
        midi = pretty_midi.PrettyMIDI(initial_tempo=60)
        piano = pretty_midi.Instrument(program=self.piano_program)

        # Simple C major chord
        for pitch in [60, 64, 67]:  # C, E, G
            note = pretty_midi.Note(
                velocity=self.default_velocity,
                pitch=pitch,
                start=0.0,
                end=2.0
            )
            piano.notes.append(note)

        midi.instruments.append(piano)

        output_path = self.output_dir / f"{exercise_id}_placeholder.mid"
        midi.write(str(output_path))

        return output_path

    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI number

        Args:
            note_name: Note name like "C4", "Eb5", etc.

        Returns:
            MIDI note number (0-127)
        """
        # Parse note name
        if len(note_name) >= 2:
            # Extract note and octave
            if note_name[1] in ['#', 'b']:
                note_part = note_name[:2]
                octave = int(note_name[2]) if len(note_name) > 2 else 4
            else:
                note_part = note_name[0]
                octave = int(note_name[1]) if len(note_name) > 1 else 4

            # Get base MIDI number (C4 = 60)
            base_midi = self.note_to_midi.get(note_part, 60)

            # Adjust for octave (C4 = 60, so each octave is 12 semitones)
            return base_midi + (octave - 4) * 12

        return 60  # Default to middle C


# Singleton instance
midi_generation_service = MIDIGenerationService()
