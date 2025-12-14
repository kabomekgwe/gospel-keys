"""Gospel Piano Arranger - Main Orchestrator

Coordinates all aspects of gospel piano arrangement generation:
- Pattern selection (context-aware)
- Voice distribution (left/right hands)
- Rhythm application (shuffle, swing, syncopation)
- Improvisation insertion (runs, fills, turnarounds)
- Dynamic expression (velocity curves)
"""

from typing import List, Tuple, Optional
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern, Arrangement
from app.gospel.patterns.left_hand import LEFT_HAND_PATTERNS, generate_left_hand_pattern
from app.gospel.patterns.right_hand import RIGHT_HAND_PATTERNS, generate_right_hand_pattern
from app.gospel.patterns.rhythm import apply_rhythm_pattern
from app.gospel.patterns.improvisation import (
    generate_gospel_fill,
    generate_turnaround,
    generate_chromatic_run
)


class GospelArranger(BaseArranger):
    """Main orchestrator for gospel piano arrangement generation.

    Coordinates pattern selection, voice distribution, timing,
    and improvisation to create complete two-hand gospel piano arrangements.
    """

    def __init__(self):
        """Initialize the gospel arranger."""
        # Application configurations (defined in Phase 4)
        self.application_configs = {
            "worship": {
                "left_patterns": ["shell_voicing", "alberti_bass"],
                "right_patterns": ["block_chord", "melody_with_fills"],
                "rhythm": ["backbeat_emphasis"],
                "improvisation_probability": 0.1,
                "tempo_range": (60, 80),
                "velocity_range": (40, 80),
            },
            "uptempo": {
                "left_patterns": ["stride_bass", "walking_bass", "syncopated_comping"],
                "right_patterns": ["octave_doubling", "chord_fills"],
                "rhythm": ["gospel_shuffle", "backbeat_emphasis"],
                "improvisation_probability": 0.5,
                "tempo_range": (120, 140),
                "velocity_range": (80, 120),
            },
            "practice": {
                "left_patterns": ["shell_voicing", "stride_bass"],
                "right_patterns": ["block_chord", "chord_fills"],
                "rhythm": [],  # Straight feel for learning
                "improvisation_probability": 0.2,
                "tempo_range": (80, 100),
                "velocity_range": (60, 90),
            },
            "concert": {
                "left_patterns": ["walking_bass", "stride_bass", "syncopated_comping"],
                "right_patterns": ["polychord", "octave_doubling", "arpeggiated_voicing"],
                "rhythm": ["gospel_shuffle", "gospel_swing", "offbeat_syncopation"],
                "improvisation_probability": 0.75,
                "tempo_range": (70, 160),
                "velocity_range": (20, 127),
            },
        }

    # Gospel-specific pattern generation (implements abstract methods)

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate gospel left hand pattern.

        Args:
            pattern_name: Name of gospel pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_left_hand_pattern(pattern_name, context)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate gospel right hand pattern.

        Args:
            pattern_name: Name of gospel pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_right_hand_pattern(pattern_name, context)

    def _apply_rhythm_transformations(self, notes: List[Note], rhythm_patterns: List[str]) -> List[Note]:
        """Apply gospel rhythm transformations.

        Args:
            notes: Notes to transform
            rhythm_patterns: List of gospel rhythm pattern names

        Returns:
            Transformed notes with gospel rhythm feel
        """
        transformed = notes
        for rhythm_pattern in rhythm_patterns:
            transformed = apply_rhythm_pattern(transformed, rhythm_pattern)
        return transformed

    def _select_left_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate left hand pattern based on context.

        Args:
            context: Chord context
            config: Application configuration
            position: Position in progression

        Returns:
            Pattern name
        """
        available_patterns = config["left_patterns"]

        # Context-aware selection rules
        if context.is_phrase_start:
            # Start phrases with strong patterns (stride, walking)
            preferred = [p for p in available_patterns if p in ["stride_bass", "walking_bass"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End phrases with resolution (shell voicing for sustain)
            preferred = [p for p in available_patterns if p in ["shell_voicing", "alberti_bass"]]
            if preferred:
                return random.choice(preferred)

        # Default: random selection from available patterns
        return random.choice(available_patterns)

    def _select_right_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate right hand pattern based on context.

        Args:
            context: Chord context
            config: Application configuration
            position: Position in progression

        Returns:
            Pattern name
        """
        available_patterns = config["right_patterns"]

        # Context-aware selection rules
        if context.is_phrase_start:
            # Start with strong voicings
            preferred = [p for p in available_patterns if p in ["block_chord", "polychord"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End with fills or arpeggios
            preferred = [p for p in available_patterns if p in ["chord_fills", "arpeggiated_voicing"]]
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
        """Add improvisation elements (fills, runs, turnarounds).

        Args:
            context: Chord context
            position: Position in progression
            application: Application type

        Returns:
            List of improvisation notes
        """
        improv_notes = []

        # Add turnarounds at phrase ends
        if context.is_phrase_end and application in ["concert", "uptempo"]:
            turnaround = generate_turnaround(
                context,
                start_time=position * 4 + 2.0,  # Start at beat 3
                duration_beats=2.0,
                hand="right"
            )
            improv_notes.extend(turnaround)

        # Add fills between chord changes
        elif context.next_chord and random.random() < 0.3:
            fill_type = random.choice(["ascending", "chromatic", "pentatonic"])
            fill = generate_gospel_fill(
                context,
                fill_type=fill_type,
                start_time=position * 4 + 2.0,  # Beat 3
                duration_beats=2.0,
                hand="right"
            )
            improv_notes.extend(fill)

        return improv_notes


__all__ = ["GospelArranger"]
