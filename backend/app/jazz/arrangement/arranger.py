"""Jazz Piano Arranger - Main Orchestrator

Coordinates jazz piano arrangement generation:
- Pattern selection (context-aware jazz patterns)
- Rootless voicings and walking bass
- Swing rhythm application
- Bebop improvisation (ii-V licks, turnarounds)
- Dynamic expression

Extends BaseArranger with jazz-specific implementations.
"""

from typing import List
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern
from app.jazz.patterns.left_hand import (
    generate_jazz_left_hand_pattern,
    JAZZ_LEFT_HAND_PATTERNS
)
from app.jazz.patterns.right_hand import (
    generate_jazz_right_hand_pattern,
    JAZZ_RIGHT_HAND_PATTERNS
)
from app.jazz.patterns.rhythm import apply_jazz_rhythm_pattern
from app.jazz.patterns.improvisation import (
    generate_ii_v_lick,
    generate_turnaround,
    generate_bebop_run
)


class JazzArranger(BaseArranger):
    """Main orchestrator for jazz piano arrangement generation.

    Extends BaseArranger with jazz-specific pattern selection,
    swing rhythm, and bebop improvisation.

    Applications:
    - ballad: Slow tempo (60-80 BPM), sustained voicings, minimal improvisation
    - standard: Medium swing (120-200 BPM), walking bass, moderate improvisation
    - uptempo: Fast swing (200-300 BPM), continuous motion, heavy improvisation
    """

    def __init__(self):
        """Initialize jazz arranger with application configurations."""
        super().__init__()

        # Jazz application configurations
        self.application_configs = {
            "ballad": {
                "left_patterns": ["rootless_voicing", "comping_syncopated"],
                "right_patterns": ["chord_melody", "upper_structure_triads"],
                "rhythm": ["swing"],  # Light swing
                "improvisation_probability": 0.2,
                "tempo_range": (60, 80),
                "velocity_range": (50, 90),
            },
            "standard": {
                "left_patterns": ["walking_bass", "rootless_voicing", "comping_syncopated"],
                "right_patterns": ["bebop_line", "chord_melody", "single_note_improvisation"],
                "rhythm": ["swing"],  # Moderate swing
                "improvisation_probability": 0.5,
                "tempo_range": (120, 200),
                "velocity_range": (70, 110),
            },
            "uptempo": {
                "left_patterns": ["walking_bass", "stride_jazz", "bass_line_chromatic"],
                "right_patterns": ["bebop_line", "block_chords_locked_hands", "single_note_improvisation"],
                "rhythm": ["heavy_swing"],  # Heavy swing
                "improvisation_probability": 0.75,
                "tempo_range": (200, 300),
                "velocity_range": (80, 120),
            },
        }

    # Implement abstract methods from BaseArranger

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5) -> HandPattern:
        """Generate jazz left hand pattern.

        Args:
            pattern_name: Name of jazz pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_jazz_left_hand_pattern(pattern_name, context)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5) -> HandPattern:
        """Generate jazz right hand pattern.

        Args:
            pattern_name: Name of jazz pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_jazz_right_hand_pattern(pattern_name, context)

    def _apply_rhythm_transformations(self, notes: List[Note], rhythm_patterns: List[str]) -> List[Note]:
        """Apply jazz rhythm transformations (swing).

        Args:
            notes: Notes to transform
            rhythm_patterns: List of jazz rhythm pattern names

        Returns:
            Transformed notes with swing feel
        """
        transformed = notes
        for rhythm_pattern in rhythm_patterns:
            transformed = apply_jazz_rhythm_pattern(transformed, rhythm_pattern)
        return transformed

    def _select_left_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate left hand pattern based on context.

        Jazz-specific selection rules:
        - Walking bass for continuous motion
        - Rootless voicings for ballads
        - Comping for syncopated feel

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
            # Start phrases with clear root (walking bass or rootless voicing)
            preferred = [p for p in available_patterns if p in ["walking_bass", "rootless_voicing"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End phrases with sustained voicing (rootless)
            preferred = [p for p in available_patterns if p == "rootless_voicing"]
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

        Jazz-specific selection rules:
        - Bebop lines for motion
        - Chord melody for harmonic density
        - Block chords for rhythm section feel

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
            # Start with clear statement (chord melody or block chords)
            preferred = [p for p in available_patterns if p in ["chord_melody", "block_chords_locked_hands"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End with resolution (bebop line or chord melody)
            preferred = [p for p in available_patterns if p in ["bebop_line", "chord_melody"]]
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
        """Add jazz improvisation elements.

        Jazz improvisation:
        - ii-V licks over ii-V progressions
        - Turnarounds at phrase ends
        - Bebop runs for connecting phrases

        Args:
            context: Chord context
            position: Position in progression
            application: Application type

        Returns:
            List of improvisation notes
        """
        improv_notes = []

        # Add turnarounds at phrase ends
        if context.is_phrase_end and application in ["standard", "uptempo"]:
            turnaround = generate_turnaround(
                context,
                start_time=position * 4 + 2.0,  # Start at beat 3
                duration_beats=2.0,
                hand="right"
            )
            improv_notes.extend(turnaround)

        # Add ii-V licks when appropriate
        elif context.previous_chord and "m7" in context.chord and "7" in str(context.next_chord):
            # Detected ii-V progression
            lick = generate_ii_v_lick(
                context,
                start_time=position * 4 + 1.5,  # Start mid-bar
                duration_beats=2.0,
                hand="right"
            )
            improv_notes.extend(lick)

        # Add bebop runs for connection
        elif context.next_chord and random.random() < 0.3:
            run = generate_bebop_run(
                context,
                start_time=position * 4 + 2.5,  # Beat 3.5
                duration_beats=1.5,
                hand="right",
                ascending=True
            )
            improv_notes.extend(run)

        return improv_notes


__all__ = ["JazzArranger"]
