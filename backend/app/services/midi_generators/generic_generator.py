"""Generic MIDI Generator

AI-powered MIDI generation for exercise types without dedicated generators.
Interprets midi_prompt and uses AI to generate appropriate MIDI content.
"""

from pathlib import Path
from typing import Optional
from midiutil import MIDIFile

from app.schemas.curriculum import TemplateExercise


class GenericMIDIGenerator:
    """Generate MIDI files using AI interpretation of midi_prompts"""

    def __init__(self):
        self.default_tempo = 60
        self.default_velocity = 100

    async def generate(
        self,
        exercise: TemplateExercise,
        output_path: Path
    ) -> Optional[Path]:
        """Generate MIDI file by interpreting midi_prompt with AI

        Args:
            exercise: TemplateExercise with midi_prompt
            output_path: Where to save the MIDI file

        Returns:
            Path to generated MIDI file, or None if generation failed

        Note:
            This is a placeholder implementation. Full implementation would:
            1. Send midi_prompt to AI (Gemini/Claude)
            2. AI returns structured MIDI instructions (notes, rhythms, etc.)
            3. Generate MIDI file from AI response
        """
        if not exercise.midi_prompt:
            print(f"Warning: No MIDI prompt for exercise '{exercise.title}'")
            return None

        print(f"Generic MIDI generation for: {exercise.title}")
        print(f"  Prompt: {exercise.midi_prompt[:100]}...")

        # TODO: Implement AI-based MIDI generation
        # For now, generate a placeholder MIDI file (middle C held for 4 beats)
        midi_file = MIDIFile(1)
        track = 0
        channel = 0
        time = 0

        tempo = (
            exercise.content.midi_hints.tempo_bpm
            if exercise.content.midi_hints
            else self.default_tempo
        )

        midi_file.addTempo(track, time, tempo)
        midi_file.addTrackName(track, time, exercise.title)

        # Placeholder: Single note
        midi_file.addNote(
            track=track,
            channel=channel,
            pitch=60,  # Middle C
            time=0,
            duration=4.0,
            volume=self.default_velocity
        )

        # Write MIDI file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            midi_file.writeFile(f)

        print(f"  ⚠️  Generated placeholder MIDI (AI implementation pending)")

        return output_path if output_path.exists() else None


# Global instance
generic_midi_generator = GenericMIDIGenerator()
