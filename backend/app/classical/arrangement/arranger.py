"""Classical Piano Arranger - Main Orchestrator

Coordinates classical piano arrangement generation:
- Period-appropriate pattern selection (Baroque, Classical, Romantic)
- Strict voice leading and counterpoint rules
- Voice independence (no parallel 5ths/octaves)
- Proper phrase structure (antecedent-consequent)

Extends BaseArranger with classical-specific implementations.
"""

from typing import List
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern
from app.classical.patterns.left_hand import (
    generate_classical_left_hand_pattern,
    CLASSICAL_LEFT_HAND_PATTERNS
)
from app.classical.patterns.right_hand import (
    generate_classical_right_hand_pattern,
    CLASSICAL_RIGHT_HAND_PATTERNS
)
from app.classical.patterns.voice_independence import (
    ensure_voice_independence,
    apply_classical_voice_leading
)


class ClassicalArranger(BaseArranger):
    """Main orchestrator for classical piano arrangement generation.

    Extends BaseArranger with classical-specific pattern selection,
    strict voice leading, and period-appropriate styles.

    Applications (Period Styles):
    - baroque: Baroque period (1600-1750), counterpoint, ornate
    - classical: Classical period (1750-1820), balanced, elegant
    - romantic: Romantic period (1820-1900), expressive, virtuosic
    """

    def __init__(self):
        """Initialize classical arranger with period configurations."""
        super().__init__()

        # Period-specific configurations
        self.application_configs = {
            "baroque": {
                "left_patterns": ["alberti_bass", "broken_chord_classical", "bass_melody_counterpoint"],
                "right_patterns": ["counterpoint_melody", "melody_solo", "arpeggios_broken"],
                "rhythm": [],  # No rhythm transformations (use strict time)
                "improvisation_probability": 0.3,  # Ornaments
                "tempo_range": (60, 120),
                "velocity_range": (65, 90),
                "strict_voice_leading": True,  # Bach-style counterpoint
            },
            "classical": {
                "left_patterns": ["alberti_bass", "waltz_bass", "broken_chord_classical"],
                "right_patterns": ["melody_solo", "melody_with_accompaniment", "scale_runs"],
                "rhythm": [],
                "improvisation_probability": 0.2,  # Minimal ornamentation
                "tempo_range": (80, 144),
                "velocity_range": (70, 95),
                "strict_voice_leading": True,  # Mozart-style elegance
            },
            "romantic": {
                "left_patterns": ["broken_chord_classical", "arpeggios_broken", "pedal_tone"],
                "right_patterns": ["melody_with_accompaniment", "arpeggios_broken", "scale_runs"],
                "rhythm": [],
                "improvisation_probability": 0.4,  # Expressive ornamentation
                "tempo_range": (60, 160),
                "velocity_range": (60, 100),
                "strict_voice_leading": False,  # More freedom for expression
            },
        }

    # Implement abstract methods from BaseArranger

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate classical left hand pattern.

        Args:
            pattern_name: Name of classical pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_classical_left_hand_pattern(pattern_name, context)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate classical right hand pattern.

        Args:
            pattern_name: Name of classical pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_classical_right_hand_pattern(pattern_name, context)

    def _apply_rhythm_transformations(self, notes: List[Note], rhythm_patterns: List[str]) -> List[Note]:
        """Apply rhythm transformations.

        Classical music uses strict time (no swing/shuffle).
        This method is a no-op for classical.

        Args:
            notes: Notes to transform
            rhythm_patterns: List of rhythm pattern names (unused)

        Returns:
            Notes unchanged (strict time)
        """
        # Classical music uses strict time - no transformations
        return notes

    def _select_left_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate left hand pattern based on context.

        Classical-specific selection rules:
        - Alberti bass for accompaniment texture
        - Waltz bass for 3/4 time
        - Broken chords for flowing texture
        - Counterpoint for polyphonic texture

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
            # Start with clear harmonic foundation
            preferred = [p for p in available_patterns if p in ["alberti_bass", "broken_chord_classical"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End with grounded bass (pedal or counterpoint)
            preferred = [p for p in available_patterns if p in ["bass_melody_counterpoint", "pedal_tone"]]
            if preferred:
                return preferred[0] if len(preferred) == 1 else random.choice(preferred)

        # Default: random selection from available patterns
        return random.choice(available_patterns)

    def _select_right_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate right hand pattern based on context.

        Classical-specific selection rules:
        - Melody for lyrical phrases
        - Scale runs for virtuosic passages
        - Arpeggios for romantic texture
        - Counterpoint for polyphonic texture

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
            # Start with clear melodic statement
            preferred = [p for p in available_patterns if p in ["melody_solo", "melody_with_accompaniment"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End with resolution or cadence
            preferred = [p for p in available_patterns if p in ["melody_solo", "arpeggios_broken"]]
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
        """Add classical ornamentation and embellishments.

        Classical improvisation:
        - Trills at cadences
        - Turns and mordents
        - Passing tones
        - Appoggiaturas

        Args:
            context: Chord context
            position: Position in progression
            application: Application type (period)

        Returns:
            List of ornamentation notes
        """
        ornament_notes = []

        # Add trill at phrase end (cadence)
        if context.is_phrase_end and random.random() < 0.4:
            # Simple trill: rapid alternation between two adjacent notes
            root_midi = 72  # C5

            trill = [
                (position * 4 + 3.0, root_midi + 7, 0.125, 75),      # Main note
                (position * 4 + 3.125, root_midi + 9, 0.125, 73),    # Upper neighbor
                (position * 4 + 3.25, root_midi + 7, 0.125, 75),     # Main note
                (position * 4 + 3.375, root_midi + 9, 0.125, 73),    # Upper neighbor
                (position * 4 + 3.5, root_midi + 7, 0.5, 78),        # Resolution
            ]

            for time, pitch, duration, velocity in trill:
                note = Note(
                    pitch=pitch,
                    time=time,
                    duration=duration,
                    velocity=velocity,
                    hand="right"
                )
                ornament_notes.append(note)

        return ornament_notes

    def arrange_progression(
        self,
        chords: List[str],
        key: str,
        bpm: int,
        application: str,
        time_signature: tuple = (4, 4)
    ):
        """Override arrange_progression to add classical voice leading.

        Extends base implementation with strict voice independence rules.

        Args:
            chords: List of chord symbols
            key: Musical key
            bpm: Tempo in BPM
            application: Period style (baroque, classical, romantic)
            time_signature: Time signature tuple

        Returns:
            Arrangement with classical voice leading applied
        """
        # Call base implementation
        arrangement = super().arrange_progression(chords, key, bpm, application, time_signature)

        # Apply classical voice leading rules
        config = self.application_configs.get(application, self.application_configs["classical"])
        strict = config.get("strict_voice_leading", True)

        # Ensure voice independence (no parallel 5ths/octaves)
        left_notes, right_notes = ensure_voice_independence(
            arrangement.left_hand_notes,
            arrangement.right_hand_notes,
            strict=strict
        )

        # Apply smooth voice leading to each hand
        left_notes = apply_classical_voice_leading(left_notes, max_leap=7)
        right_notes = apply_classical_voice_leading(right_notes, max_leap=12)

        # Update arrangement
        arrangement.left_hand_notes = left_notes
        arrangement.right_hand_notes = right_notes

        return arrangement


__all__ = ["ClassicalArranger"]
