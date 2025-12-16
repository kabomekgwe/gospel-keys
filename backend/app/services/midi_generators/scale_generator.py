"""Scale and Arpeggio MIDI Generator

Generates MIDI files for scale patterns, arpeggios, and technical exercises.
Supports various patterns (ascending, descending, contrary motion, etc.)
"""

from pathlib import Path
from typing import List, Optional, Dict
from midiutil import MIDIFile

from app.schemas.curriculum import TemplateExercise, ExerciseTypeEnum


class ScaleMIDIGenerator:
    """Generate MIDI files from scale/arpeggio exercise specifications"""

    # Scale patterns (intervals from root)
    SCALE_PATTERNS = {
        "major": [0, 2, 4, 5, 7, 9, 11, 12],
        "natural_minor": [0, 2, 3, 5, 7, 8, 10, 12],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11, 12],
        "melodic_minor": [0, 2, 3, 5, 7, 9, 11, 12],
        "dorian": [0, 2, 3, 5, 7, 9, 10, 12],
        "phrygian": [0, 1, 3, 5, 7, 8, 10, 12],
        "lydian": [0, 2, 4, 6, 7, 9, 11, 12],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10, 12],
        "chromatic": list(range(13)),  # All 12 notes + octave
        "pentatonic_major": [0, 2, 4, 7, 9, 12],
        "pentatonic_minor": [0, 3, 5, 7, 10, 12],
        "blues": [0, 3, 5, 6, 7, 10, 12],
    }

    # Arpeggio patterns
    ARPEGGIO_PATTERNS = {
        "major_triad": [0, 4, 7, 12],
        "minor_triad": [0, 3, 7, 12],
        "diminished_triad": [0, 3, 6, 12],
        "augmented_triad": [0, 4, 8, 12],
        "major_7th": [0, 4, 7, 11, 12],
        "minor_7th": [0, 3, 7, 10, 12],
        "dominant_7th": [0, 4, 7, 10, 12],
        "major_9th": [0, 4, 7, 11, 14],
        "minor_9th": [0, 3, 7, 10, 14],
    }

    NOTE_TO_MIDI_BASE = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }

    def __init__(self):
        self.default_tempo = 60
        self.default_velocity = 100
        self.base_octave = 4  # C4 = middle C = MIDI 60

    def generate(
        self,
        exercise: TemplateExercise,
        output_path: Path
    ) -> Optional[Path]:
        """Generate MIDI file for a scale/arpeggio exercise

        Args:
            exercise: TemplateExercise with scale/arpeggio specifications
            output_path: Where to save the MIDI file

        Returns:
            Path to generated MIDI file, or None if generation failed
        """
        if exercise.exercise_type not in [ExerciseTypeEnum.SCALE, ExerciseTypeEnum.ARPEGGIO]:
            raise ValueError(f"Exercise type must be SCALE or ARPEGGIO, got {exercise.exercise_type}")

        content = exercise.content

        # Extract parameters
        scale_name = content.scale  # e.g., "C Major", "D Minor", "G Blues"
        pattern_type = content.pattern  # e.g., "ascending", "descending", "Diatonic 7ths"
        key = content.key or "C"
        octaves = content.octaves or 1

        if not scale_name:
            print(f"Warning: No scale specified for exercise '{exercise.title}'")
            return None

        # Parse scale name
        root_note, scale_type = self._parse_scale_name(scale_name)

        # Get pattern
        if exercise.exercise_type == ExerciseTypeEnum.ARPEGGIO:
            intervals = self._get_arpeggio_pattern(scale_type or "major_triad")
        else:
            intervals = self._get_scale_pattern(scale_type or "major")

        # Generate MIDI notes
        midi_notes = self._generate_scale_notes(
            root_note or key,
            intervals,
            octaves=octaves,
            pattern=pattern_type
        )

        # Get tempo
        tempo = (
            content.midi_hints.tempo_bpm
            if content.midi_hints
            else self.default_tempo
        )

        # Generate MIDI file
        midi_file = MIDIFile(1)
        track = 0
        channel = 0
        time = 0

        midi_file.addTempo(track, time, tempo)
        midi_file.addTrackName(track, time, exercise.title)

        # Add notes (quarter notes)
        beat_duration = 1.0  # Quarter note
        for i, midi_note in enumerate(midi_notes):
            midi_file.addNote(
                track=track,
                channel=channel,
                pitch=midi_note,
                time=time + (i * beat_duration),
                duration=beat_duration * 0.9,
                volume=self.default_velocity
            )

        # Write MIDI file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            midi_file.writeFile(f)

        return output_path if output_path.exists() else None

    def _parse_scale_name(self, scale_name: str) -> tuple[Optional[str], Optional[str]]:
        """Parse scale name like 'C Major' or 'D Minor' into root and type

        Args:
            scale_name: Scale name string

        Returns:
            Tuple of (root_note, scale_type)
        """
        parts = scale_name.strip().split()
        if len(parts) < 2:
            return None, scale_name.lower().replace(" ", "_")

        root = parts[0]
        scale_type = "_".join(parts[1:]).lower()

        return root, scale_type

    def _get_scale_pattern(self, scale_type: str) -> List[int]:
        """Get interval pattern for a scale type

        Args:
            scale_type: Type of scale (major, minor, etc.)

        Returns:
            List of intervals (semitones from root)
        """
        return self.SCALE_PATTERNS.get(scale_type, self.SCALE_PATTERNS["major"])

    def _get_arpeggio_pattern(self, arpeggio_type: str) -> List[int]:
        """Get interval pattern for an arpeggio type

        Args:
            arpeggio_type: Type of arpeggio (major_triad, minor_7th, etc.)

        Returns:
            List of intervals (semitones from root)
        """
        return self.ARPEGGIO_PATTERNS.get(arpeggio_type, self.ARPEGGIO_PATTERNS["major_triad"])

    def _generate_scale_notes(
        self,
        root_note: str,
        intervals: List[int],
        octaves: int = 1,
        pattern: Optional[str] = None
    ) -> List[int]:
        """Generate MIDI note numbers for a scale pattern

        Args:
            root_note: Root note (e.g., "C", "D#", "Bb")
            intervals: Interval pattern (semitones from root)
            octaves: Number of octaves to generate
            pattern: Pattern type (ascending, descending, etc.)

        Returns:
            List of MIDI note numbers
        """
        # Get root MIDI number
        root_pitch_class = self.NOTE_TO_MIDI_BASE.get(root_note, 0)
        root_midi = (self.base_octave + 1) * 12 + root_pitch_class  # C4 = 60

        notes = []

        # Generate ascending notes
        for octave_offset in range(octaves + 1):  # +1 to include top note
            for interval in intervals[:-1]:  # Exclude last (octave) except on final octave
                note = root_midi + interval + (octave_offset * 12)
                notes.append(note)

        # Add final octave note
        notes.append(root_midi + (octaves * 12))

        # Apply pattern
        if pattern and "descending" in pattern.lower():
            # Descending only
            notes = list(reversed(notes))
        elif pattern and "contrary" in pattern.lower():
            # Ascending then descending (remove duplicate top note)
            notes = notes + list(reversed(notes[:-1]))
        elif pattern and "ascending" not in pattern.lower() and pattern != "Diatonic 7ths":
            # Default to ascending + descending
            notes = notes + list(reversed(notes[:-1]))

        return notes


# Global instance
scale_midi_generator = ScaleMIDIGenerator()
