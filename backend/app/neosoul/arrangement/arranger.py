"""Neo-Soul Piano Arranger - Main Orchestrator

Coordinates neo-soul piano arrangement generation:
- Pattern selection (extended voicings, suspended chords)
- 16th-note grooves and laid-back timing
- Sparse, spacious arrangements
- Chromatic melodic movement
- Dynamic expression

Extends BaseArranger with neo-soul-specific implementations.
"""

from typing import List
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern
from app.neosoul.patterns.left_hand import (
    generate_neosoul_left_hand_pattern,
    NEOSOUL_LEFT_HAND_PATTERNS
)
from app.neosoul.patterns.right_hand import (
    generate_neosoul_right_hand_pattern,
    NEOSOUL_RIGHT_HAND_PATTERNS
)
from app.neosoul.patterns.rhythm import apply_neosoul_rhythm_pattern


class NeosoulArranger(BaseArranger):
    """Main orchestrator for neo-soul piano arrangement generation.

    Extends BaseArranger with neo-soul-specific pattern selection,
    16th-note grooves, and laid-back timing.

    Applications:
    - smooth: Slow tempo (70-90 BPM), sustained extended voicings, minimal movement
    - uptempo: Medium tempo (90-110 BPM), syncopated grooves, more rhythmic activity
    """

    def __init__(self):
        """Initialize neo-soul arranger with application configurations."""
        super().__init__()

        # Neo-soul application configurations
        self.application_configs = {
            "smooth": {
                "left_patterns": ["sustained_root_with_pedal", "low_interval_voicing", "chromatic_bass_walk"],
                "right_patterns": ["extended_chord_voicing", "suspended_melody", "chromatic_fills"],
                "rhythm": ["laid_back"],  # Laid-back timing
                "tempo_range": (70, 90),
                "velocity_range": (60, 90),
            },
            "uptempo": {
                "left_patterns": ["syncopated_groove", "broken_chord_arpeggio", "chromatic_bass_walk"],
                "right_patterns": ["chord_stabs_sparse", "arpeggiated_extensions", "suspended_melody"],
                "rhythm": ["16th_groove", "syncopated"],  # 16th-note groove
                "tempo_range": (90, 110),
                "velocity_range": (70, 100),
            },
        }

    # Implement abstract methods from BaseArranger

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate neo-soul left hand pattern.

        Args:
            pattern_name: Name of neo-soul pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_neosoul_left_hand_pattern(pattern_name, context)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate neo-soul right hand pattern.

        Args:
            pattern_name: Name of neo-soul pattern
            context: Chord context

        Returns:
            HandPattern with generated notes
        """
        return generate_neosoul_right_hand_pattern(pattern_name, context)

    def _apply_rhythm_transformations(self, notes: List[Note], rhythm_patterns: List[str]) -> List[Note]:
        """Apply neo-soul rhythm transformations.

        Args:
            notes: Notes to transform
            rhythm_patterns: List of neo-soul rhythm pattern names

        Returns:
            Transformed notes with neo-soul feel
        """
        transformed = notes
        for rhythm_pattern in rhythm_patterns:
            transformed = apply_neosoul_rhythm_pattern(transformed, rhythm_pattern)
        return transformed

    def _select_left_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate left hand pattern based on context.

        Neo-soul-specific selection rules:
        - Sustained patterns for smooth feel
        - Syncopated grooves for uptempo
        - Chromatic movement for transitions

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
            # Start phrases with sustained root or pedal
            preferred = [p for p in available_patterns if p in ["sustained_root_with_pedal", "low_interval_voicing"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End phrases with chromatic movement
            preferred = [p for p in available_patterns if p == "chromatic_bass_walk"]
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

        Neo-soul-specific selection rules:
        - Extended voicings for harmonic richness
        - Sparse stabs for groove
        - Chromatic fills for connecting phrases

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
            # Start with extended voicing or suspended sound
            preferred = [p for p in available_patterns if p in ["extended_chord_voicing", "suspended_melody"]]
            if preferred:
                return random.choice(preferred)

        elif context.is_phrase_end:
            # End with chromatic fill or resolution
            preferred = [p for p in available_patterns if p in ["chromatic_fills", "extended_chord_voicing"]]
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
        """Add neo-soul improvisation elements.

        Neo-soul improvisation:
        - Chromatic fills at phrase ends
        - Suspended resolutions
        - Sparse melodic fragments

        Args:
            context: Chord context
            position: Position in progression
            application: Application type

        Returns:
            List of improvisation notes
        """
        improv_notes = []

        # Add chromatic fills at phrase ends
        if context.is_phrase_end and random.random() < 0.4:
            # Simple chromatic fill (3-note ascending)
            root_midi = 60  # C4
            fill_start = position * 4 + 3.0  # Beat 4

            for i in range(3):
                note = Note(
                    pitch=root_midi + 12 + i,  # C5 chromatic up
                    time=fill_start + (i * 0.25),  # 16th notes
                    duration=0.2,
                    velocity=75 - (i * 5),
                    hand="right"
                )
                improv_notes.append(note)

        return improv_notes


__all__ = ["NeosoulArranger"]
