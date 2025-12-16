"""
Music Theory Generator using Qwen 2.5-14B for melody generation and theory guidance.

Provides:
- Voice leading rules and suggestions
- Melody note generation
- Scale and mode recommendations
- Rhythmic pattern suggestions
"""

import logging
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.services.multi_model_service import multi_model_service
from app.schemas.music_generation import (
    MusicKey,
    MusicGenre,
    MelodyNote,
    MelodySequence,
    VoiceLeadingRules,
)

logger = logging.getLogger(__name__)


# Scale definitions for different genres
SCALE_TEMPLATES = {
    MusicGenre.GOSPEL: {
        "major": [0, 2, 4, 5, 7, 9, 11],  # Major scale
        "pentatonic": [0, 2, 4, 7, 9],    # Major pentatonic
        "blues": [0, 3, 5, 6, 7, 10],      # Blues scale
    },
    MusicGenre.JAZZ: {
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "altered": [0, 1, 3, 4, 6, 8, 10],
    },
    MusicGenre.BLUES: {
        "blues": [0, 3, 5, 6, 7, 10],
        "minor_pentatonic": [0, 3, 5, 7, 10],
    },
}


class MelodyGenerationPrompt(BaseModel):
    """Structured prompt for melody generation"""
    chord_progression: List[str]
    key: str
    genre: str
    num_notes: int
    approach: str  # chord_tones, passing_tones, extensions


class MelodyGenerationOutput(BaseModel):
    """Structured output from LLM for melody"""
    notes: List[Dict[str, Any]]  # List of {pitch, start, duration, velocity}
    scale_used: str
    approach_description: str


class MusicTheoryGenerator:
    """
    Generate melodies and music theory guidance using Qwen 2.5-14B.

    Uses multi_model_service for local LLM inference with complexity routing.
    """

    def __init__(self):
        self.llm = multi_model_service
        if not self.llm or not self.llm.is_available():
            logger.warning("⚠️ Multi-model LLM service not available")

    async def generate_melody(
        self,
        chord_progression: List[str],
        key: MusicKey,
        genre: MusicGenre,
        num_notes: int = 16,
        approach: str = "chord_tones",
    ) -> MelodySequence:
        """
        Generate a melody that fits the chord progression.

        Args:
            chord_progression: Chord symbols
            key: Key signature
            genre: Musical genre
            num_notes: Number of melody notes to generate
            approach: Melodic approach (chord_tones, passing_tones, extensions)

        Returns:
            MelodySequence with generated notes
        """
        if not self.llm or not self.llm.is_available():
            # Fallback to algorithmic generation
            return self._algorithmic_melody(
                chord_progression, key, genre, num_notes, approach
            )

        try:
            # Use Qwen 2.5-14B for intelligent melody generation
            prompt = self._create_melody_prompt(
                chord_progression, key, genre, num_notes, approach
            )

            # Complexity 6: Medium task (uses Qwen 2.5-14B)
            response_text = self.llm.generate(
                prompt=prompt,
                complexity=6,
                max_tokens=1024,
                temperature=0.7,
            )

            # Parse structured output
            melody_data = self._parse_melody_response(response_text)

            # Convert to MelodySequence
            notes = [
                MelodyNote(
                    pitch=note["pitch"],
                    start_time=note["start"],
                    duration=note["duration"],
                    velocity=note.get("velocity", 80),
                )
                for note in melody_data["notes"]
            ]

            # Calculate range
            pitches = [n.pitch for n in notes]
            range_low = min(pitches) if pitches else 60
            range_high = max(pitches) if pitches else 72

            return MelodySequence(
                notes=notes,
                key=key,
                scale=melody_data.get("scale_used", "major"),
                range_low=range_low,
                range_high=range_high,
                approach=approach,
            )

        except Exception as e:
            logger.error(f"Error generating melody with LLM: {e}")
            # Fallback to algorithmic generation
            return self._algorithmic_melody(
                chord_progression, key, genre, num_notes, approach
            )

    async def suggest_voice_leading(
        self,
        chord_progression: List[str],
        genre: MusicGenre,
    ) -> VoiceLeadingRules:
        """
        Generate voice leading rules for a chord progression.

        Args:
            chord_progression: Chord symbols
            genre: Musical genre

        Returns:
            VoiceLeadingRules with genre-specific guidelines
        """
        # Genre-specific defaults
        if genre == MusicGenre.GOSPEL:
            return VoiceLeadingRules(
                max_leap=12,  # Gospel allows larger leaps
                prefer_stepwise=True,
                avoid_parallel_fifths=False,  # Gospel allows parallel motion
                common_tone_retention=True,
                smooth_transitions=True,
            )
        elif genre == MusicGenre.JAZZ:
            return VoiceLeadingRules(
                max_leap=7,
                prefer_stepwise=True,
                avoid_parallel_fifths=True,
                common_tone_retention=False,  # Jazz uses chromatic movement
                smooth_transitions=True,
            )
        else:
            # Default classical rules
            return VoiceLeadingRules()

    async def suggest_melody_notes_for_chord(
        self,
        chord: str,
        key: MusicKey,
        genre: MusicGenre,
        approach: str = "chord_tones",
    ) -> List[int]:
        """
        Suggest appropriate melody notes for a single chord.

        Args:
            chord: Chord symbol
            key: Key signature
            genre: Musical genre
            approach: Melodic approach

        Returns:
            List of MIDI note numbers
        """
        # Get scale for genre/key
        scale = self._get_scale(genre, key)

        if approach == "chord_tones":
            # Use chord tones only
            return self._get_chord_tones(chord, scale)
        elif approach == "extensions":
            # Add 9ths, 11ths, 13ths
            chord_tones = self._get_chord_tones(chord, scale)
            extensions = [n + 12 for n in chord_tones[:3]]  # Octave up
            return sorted(chord_tones + extensions)
        elif approach == "passing_tones":
            # Full scale (includes passing tones)
            return scale
        else:
            return scale

    def _create_melody_prompt(
        self,
        chord_progression: List[str],
        key: MusicKey,
        genre: MusicGenre,
        num_notes: int,
        approach: str,
    ) -> str:
        """Create prompt for melody generation"""
        chords_str = " - ".join(chord_progression)

        prompt = f"""Generate a {genre.value} melody in the key of {key.value}.

Chord progression: {chords_str}

Requirements:
- Generate {num_notes} melody notes
- Use {approach} approach
- Follow {genre.value} style conventions
- Create a natural, singable melody

Respond with JSON in this format:
{{
  "notes": [
    {{"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80}},
    {{"pitch": 64, "start": 1.0, "duration": 0.5, "velocity": 75}}
  ],
  "scale_used": "major pentatonic",
  "approach_description": "Uses mostly chord tones with passing notes"
}}

Each note needs:
- pitch: MIDI note number (60 = middle C)
- start: Start time in beats
- duration: Note length in beats
- velocity: Volume (0-127, typically 60-100)

Generate the melody:"""

        return prompt

    def _parse_melody_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract melody data"""
        try:
            # Try to parse JSON from response
            # Handle markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response

            # Find JSON object
            start = json_str.find('{')
            end = json_str.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = json_str[start:end]

            melody_data = json.loads(json_str)
            return melody_data

        except Exception as e:
            logger.error(f"Failed to parse melody response: {e}")
            # Return minimal fallback
            return {
                "notes": [
                    {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80}
                ],
                "scale_used": "major",
                "approach_description": "Fallback melody",
            }

    def _algorithmic_melody(
        self,
        chord_progression: List[str],
        key: MusicKey,
        genre: MusicGenre,
        num_notes: int,
        approach: str,
    ) -> MelodySequence:
        """
        Fallback algorithmic melody generation (no LLM).

        Simple rule-based melody using scale degrees.
        """
        scale = self._get_scale(genre, key)
        notes = []

        # Generate notes using simple pattern
        beat = 0.0
        for i in range(num_notes):
            # Cycle through scale degrees
            scale_degree = i % len(scale)
            pitch = scale[scale_degree]

            note = MelodyNote(
                pitch=pitch,
                start_time=beat,
                duration=0.5,  # Eighth note
                velocity=80,
            )
            notes.append(note)
            beat += 0.5

        pitches = [n.pitch for n in notes]
        return MelodySequence(
            notes=notes,
            key=key,
            scale="algorithmic",
            range_low=min(pitches),
            range_high=max(pitches),
            approach=approach,
        )

    def _get_scale(self, genre: MusicGenre, key: MusicKey) -> List[int]:
        """Get scale MIDI notes for genre/key"""
        # Get root note
        key_root = key.value.replace('m', '')
        is_minor = 'm' in key.value

        # Map root to MIDI
        note_map = {
            "C": 60, "C#": 61, "Db": 61, "D": 62, "Eb": 63, "E": 64,
            "F": 65, "F#": 66, "Gb": 66, "G": 67, "Ab": 68, "A": 69,
            "Bb": 70, "B": 71,
        }
        root_midi = note_map.get(key_root, 60)

        # Get scale template
        genre_scales = SCALE_TEMPLATES.get(genre, SCALE_TEMPLATES[MusicGenre.GOSPEL])
        scale_type = "minor_pentatonic" if is_minor else "pentatonic"
        intervals = genre_scales.get(scale_type, [0, 2, 4, 7, 9])

        # Build scale
        return [root_midi + interval for interval in intervals]

    def _get_chord_tones(self, chord: str, scale: List[int]) -> List[int]:
        """Extract chord tones from a scale"""
        # Simplified: return scale degrees 1, 3, 5 (root, third, fifth)
        if len(scale) >= 5:
            return [scale[0], scale[2], scale[4]]
        return scale[:3]


# Global singleton instance
music_theory_generator = MusicTheoryGenerator()
