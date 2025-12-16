"""Lick MIDI Generator

Generates MIDI files for jazz licks and melodic phrase exercises.
Converts lick specifications (notes, rhythms, articulations) into playable MIDI.
"""

from pathlib import Path
from typing import List, Optional, Tuple
from midiutil import MIDIFile

from app.schemas.curriculum import TemplateExercise, ExerciseTypeEnum


class LickMIDIGenerator:
    """Generate MIDI files from lick exercise specifications"""

    def __init__(self):
        self.default_tempo = 120
        self.default_velocity = 100

    def generate(
        self,
        exercise: TemplateExercise,
        output_path: Path
    ) -> Optional[Path]:
        """Generate MIDI file for a lick exercise

        Args:
            exercise: TemplateExercise with lick specifications
            output_path: Where to save the MIDI file

        Returns:
            Path to generated MIDI file, or None if generation failed
        """
        if exercise.exercise_type != ExerciseTypeEnum.LICK:
            raise ValueError(f"Exercise type must be LICK, got {exercise.exercise_type}")

        content = exercise.content

        # Extract lick data
        midi_notes = content.midi_notes
        notes_str = content.notes  # Note names like ["C4", "D4", "E4"]

        if not midi_notes and not notes_str:
            print(f"Warning: No notes specified for lick exercise '{exercise.title}'")
            return None

        # Convert note names to MIDI if needed
        if not midi_notes and notes_str:
            midi_notes = self._note_names_to_midi(notes_str)

        # Get tempo
        tempo = (
            content.midi_hints.tempo_bpm
            if content.midi_hints
            else self.default_tempo
        )

        # Get duration (default to quarter notes)
        duration_beats = self._calculate_duration(len(midi_notes))

        # Generate MIDI
        midi_file = MIDIFile(1)  # 1 track
        track = 0
        channel = 0
        time = 0  # Start at beginning

        midi_file.addTempo(track, time, tempo)

        # Add title
        midi_file.addTrackName(track, time, exercise.title)

        # Add notes
        beat_duration = duration_beats / len(midi_notes)  # Evenly spaced for now
        for i, midi_note in enumerate(midi_notes):
            midi_file.addNote(
                track=track,
                channel=channel,
                pitch=midi_note,
                time=time + (i * beat_duration),
                duration=beat_duration * 0.9,  # 90% duration for slight articulation
                volume=self.default_velocity
            )

        # Write MIDI file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            midi_file.writeFile(f)

        return output_path if output_path.exists() else None

    def _note_names_to_midi(self, note_names: List[str]) -> List[int]:
        """Convert note names like 'C4', 'D#5' to MIDI numbers

        Args:
            note_names: List of note names with octaves

        Returns:
            List of MIDI note numbers (0-127)
        """
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        midi_notes = []
        for note_str in note_names:
            # Parse note name and octave
            # Support formats: C4, C#4, Db4
            note_str = note_str.strip()
            if len(note_str) < 2:
                continue

            # Extract octave (last character)
            if note_str[-1].isdigit():
                octave = int(note_str[-1])
                note_name = note_str[:-1]
            else:
                # No octave specified, default to 4
                octave = 4
                note_name = note_str

            # Get pitch class
            pitch_class = note_map.get(note_name)
            if pitch_class is None:
                print(f"Warning: Unknown note name '{note_name}', skipping")
                continue

            # Calculate MIDI number: C4 = 60
            midi_num = (octave + 1) * 12 + pitch_class
            midi_notes.append(midi_num)

        return midi_notes

    def _calculate_duration(self, num_notes: int) -> float:
        """Calculate total duration in beats based on number of notes

        Args:
            num_notes: Number of notes in the lick

        Returns:
            Total duration in beats (4 beats = 1 bar in 4/4 time)
        """
        # Heuristic: Short licks (1-4 notes) = 1 bar, medium (5-8) = 2 bars, long (9+) = 4 bars
        if num_notes <= 4:
            return 4.0
        elif num_notes <= 8:
            return 8.0
        else:
            return 16.0


# Global instance
lick_midi_generator = LickMIDIGenerator()
