"""Blues Piano Arranger - Main Orchestrator

Coordinates blues piano arrangement generation:
- Pattern selection (boogie-woogie, shuffle bass, blues licks)
- Shuffle rhythm application
- 12-bar blues structure awareness
- Blues phrasing and dynamics

Extends BaseArranger with blues-specific implementations.
"""

from typing import List
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern
from app.blues.patterns.left_hand import (
    generate_blues_left_hand_pattern,
    BLUES_LEFT_HAND_PATTERNS
)
from app.blues.patterns.right_hand import (
    generate_blues_right_hand_pattern,
    BLUES_RIGHT_HAND_PATTERNS
)
from app.blues.patterns.rhythm import apply_blues_rhythm_pattern


class BluesArranger(BaseArranger):
    """Main orchestrator for blues piano arrangement generation.

    Extends BaseArranger with blues-specific pattern selection,
    shuffle rhythm, and blues phrasing.

    Applications:
    - slow: Slow blues (60-80 BPM), expressive, straight feel or light shuffle
    - shuffle: Medium shuffle (100-120 BPM), classic blues shuffle
    - fast: Fast blues (140-180 BPM), uptempo boogie-woogie energy
    """

    def __init__(self):
        """Initialize blues arranger with application configurations."""
        super().__init__()

        # Blues application configurations
        self.application_configs = {
            "slow": {
                "left_patterns": ["blues_chord_voicing", "walking_blues_bass", "shuffle_bass"],
                "right_patterns": ["call_response", "blues_bends", "double_stop_sixths"],
                "rhythm": ["straight"],  # Straight 8ths for slow blues
                "improvisation_probability": 0.5,
                "tempo_range": (60, 80),
                "velocity_range": (50, 85),
            },
            "shuffle": {
                "left_patterns": ["shuffle_bass", "walking_blues_bass", "boogie_woogie"],
                "right_patterns": ["blues_lick", "call_response", "double_stop_sixths"],
                "rhythm": ["shuffle"],  # Medium shuffle
                "improvisation_probability": 0.6,
                "tempo_range": (100, 120),
                "velocity_range": (70, 100),
            },
            "fast": {
                "left_patterns": ["boogie_woogie", "octave_bass", "shuffle_bass"],
                "right_patterns": ["blues_tremolo", "blues_lick", "double_stop_sixths"],
                "rhythm": ["heavy_shuffle"],  # Heavy shuffle for uptempo
                "improvisation_probability": 0.7,
                "tempo_range": (140, 180),
                "velocity_range": (80, 110),
            },
        }

    # Implement abstract methods from BaseArranger

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5) -> HandPattern:
        """Generate blues left hand pattern.

        Args:
            pattern_name: Name of blues pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_blues_left_hand_pattern(pattern_name, context)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5) -> HandPattern:
        """Generate blues right hand pattern.

        Args:
            pattern_name: Name of blues pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_blues_right_hand_pattern(pattern_name, context)

    def _apply_rhythm_transformations(self, notes: List[Note], rhythm_patterns: List[str]) -> List[Note]:
        """Apply blues rhythm transformations (shuffle).

        Args:
            notes: Notes to transform
            rhythm_patterns: List of blues rhythm pattern names

        Returns:
            Transformed notes with blues shuffle feel
        """
        transformed = notes
        for rhythm_pattern in rhythm_patterns:
            transformed = apply_blues_rhythm_pattern(transformed, rhythm_pattern)
        return transformed

    def _select_left_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate left hand pattern based on context.

        Blues-specific selection rules:
        - Boogie-woogie for continuous drive
        - Shuffle bass for classic blues feel
        - Walking bass for movement

        Args:
            context: Chord context
            config: Application configuration
            position: Position in progression

        Returns:
            Pattern name
        """
        available_patterns = config["left_patterns"]

        # Context-aware selection
        if context.is_phrase_start:
            # Start with strong pattern (boogie or shuffle)
            preferred = [p for p in available_patterns if p in ["boogie_woogie", "shuffle_bass"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End with walking bass for movement
            preferred = [p for p in available_patterns if p == "walking_blues_bass"]
            if preferred:
                return preferred[0]

        # Default: random selection
        return random.choice(available_patterns)

    def _select_right_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate right hand pattern based on context.

        Blues-specific selection rules:
        - Blues licks for melodic phrases
        - Call and response for phrasing
        - Double stops for harmonic richness

        Args:
            context: Chord context
            config: Application configuration
            position: Position in progression

        Returns:
            Pattern name
        """
        available_patterns = config["right_patterns"]

        # Context-aware selection
        if context.is_phrase_start:
            # Start with call (question)
            preferred = [p for p in available_patterns if p in ["call_response", "blues_lick"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End with response or bends
            preferred = [p for p in available_patterns if p in ["call_response", "blues_bends"]]
            if preferred:
                return random.choice(preferred)

        # Default: random selection
        return random.choice(available_patterns)

    def _add_improvisation(
        self,
        context: ChordContext,
        position: int,
        application: str
    ) -> List[Note]:
        """Add blues improvisation elements.

        Blues improvisation:
        - Blues licks at phrase ends
        - Grace note bends
        - Tremolos for intensity

        Args:
            context: Chord context
            position: Position in progression
            application: Application type

        Returns:
            List of improvisation notes
        """
        improv_notes = []

        # Add blues lick at phrase end
        if context.is_phrase_end and random.random() < 0.5:
            # Simple descending blues lick
            root_midi = 72  # C5

            lick = [
                (position * 4 + 3.0, root_midi + 10, 0.25, 80),   # b7
                (position * 4 + 3.25, root_midi + 7, 0.25, 78),   # 5
                (position * 4 + 3.5, root_midi + 5, 0.25, 75),    # 4
                (position * 4 + 3.75, root_midi + 3, 0.25, 73),   # b3
            ]

            for time, pitch, duration, velocity in lick:
                note = Note(
                    pitch=pitch,
                    time=time,
                    duration=duration,
                    velocity=velocity,
                    hand="right"
                )
                improv_notes.append(note)

        return improv_notes


__all__ = ["BluesArranger"]
