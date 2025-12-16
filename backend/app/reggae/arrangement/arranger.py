"""Reggae Piano Arranger - Main Orchestrator

Coordinates reggae piano arrangement generation:
- Pattern selection (skank, bubble rhythm, dub bass)
- Offbeat emphasis and one-drop feel
- Laid-back groove with heavy low-end
- Authentic Jamaican reggae characteristics

Extends BaseArranger with reggae-specific implementations.
"""

from typing import List
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern
from app.reggae.patterns.left_hand import (
    generate_reggae_left_hand_pattern,
    REGGAE_LEFT_HAND_PATTERNS
)
from app.reggae.patterns.right_hand import (
    generate_reggae_right_hand_pattern,
    REGGAE_RIGHT_HAND_PATTERNS
)
from app.reggae.patterns.rhythm import apply_reggae_rhythm_pattern


class ReggaeArranger(BaseArranger):
    """Main orchestrator for reggae piano arrangement generation.

    Extends BaseArranger with reggae-specific pattern selection,
    offbeat emphasis, and one-drop rhythm.

    Applications:
    - roots: Classic roots reggae (70-80 BPM), dub bass, heavy skank
    - dancehall: Faster dancehall style (90-110 BPM), double skank
    - dub: Minimal dub reggae (60-75 BPM), sparse, heavy bass
    """

    def __init__(self):
        """Initialize reggae arranger with application configurations."""
        super().__init__()

        # Reggae application configurations
        self.application_configs = {
            "roots": {
                "left_patterns": ["dub_bass", "walking_bass_reggae"],
                "right_patterns": ["skank", "bubble_rhythm"],
                "rhythm": ["one_drop", "laid_back"],
                "tempo_range": (70, 80),
                "velocity_range": (70, 100),
            },
            "dancehall": {
                "left_patterns": ["offbeat_bass", "roots_and_fifths"],
                "right_patterns": ["double_skank", "skank"],
                "rhythm": ["offbeat_emphasis"],
                "tempo_range": (90, 110),
                "velocity_range": (80, 110),
            },
            "dub": {
                "left_patterns": ["dub_bass"],
                "right_patterns": ["sustained_chords", "bubble_rhythm"],
                "rhythm": ["one_drop", "laid_back"],
                "tempo_range": (60, 75),
                "velocity_range": (60, 90),
            },
        }

    # Implement abstract methods from BaseArranger

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate reggae left hand pattern.

        Args:
            pattern_name: Name of reggae pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_reggae_left_hand_pattern(pattern_name, context)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate reggae right hand pattern.

        Args:
            pattern_name: Name of reggae pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_reggae_right_hand_pattern(pattern_name, context)

    def _apply_rhythm_pattern(self, notes: List[Note], rhythm_name: str) -> List[Note]:
        """Apply reggae rhythm transformation.

        Args:
            notes: List of notes to transform
            rhythm_name: Rhythm pattern name

        Returns:
            Transformed notes with reggae rhythm
        """
        return apply_reggae_rhythm_pattern(notes, rhythm_name)

    def _select_left_hand_pattern(self, context: ChordContext, application: str) -> str:
        """Select appropriate left hand pattern based on context.

        Args:
            context: Chord context
            application: Application type

        Returns:
            Pattern name
        """
        config = self.application_configs.get(application, self.application_configs["roots"])
        return random.choice(config["left_patterns"])

    def _select_right_hand_pattern(self, context: ChordContext, application: str) -> str:
        """Select appropriate right hand pattern based on context.

        Args:
            context: Chord context
            application: Application type

        Returns:
            Pattern name
        """
        config = self.application_configs.get(application, self.application_configs["roots"])
        return random.choice(config["right_patterns"])

    def _select_rhythm_pattern(self, application: str) -> str:
        """Select appropriate rhythm pattern for application.

        Args:
            application: Application type

        Returns:
            Rhythm pattern name
        """
        config = self.application_configs.get(application, self.application_configs["roots"])
        return random.choice(config["rhythm"])

    def _get_default_application(self) -> str:
        """Get default application type.

        Returns:
            Default application name
        """
        return "roots"

    def _adjust_velocity_for_dynamics(self, notes: List[Note], application: str) -> List[Note]:
        """Adjust note velocities for reggae dynamics.

        Reggae typically has:
        - Heavy bass (high velocity)
        - Moderate chord velocity
        - Emphasis on offbeats

        Args:
            notes: Notes to adjust
            application: Application type

        Returns:
            Notes with adjusted velocities
        """
        config = self.application_configs.get(application, self.application_configs["roots"])
        min_vel, max_vel = config["velocity_range"]

        adjusted = []
        for note in notes:
            # Boost bass notes (lower octaves)
            if note.pitch < 48:  # Below C3
                velocity = min(127, int(note.velocity * 1.3))
            else:
                velocity = note.velocity

            # Clamp to range
            velocity = max(min_vel, min(max_vel, velocity))

            adjusted.append(Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=velocity
            ))

        return adjusted
