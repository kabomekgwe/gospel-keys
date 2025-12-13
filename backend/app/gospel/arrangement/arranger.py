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

from app.gospel import Note, ChordContext, HandPattern, Arrangement
from app.gospel.patterns.left_hand import LEFT_HAND_PATTERNS, generate_left_hand_pattern
from app.gospel.patterns.right_hand import RIGHT_HAND_PATTERNS, generate_right_hand_pattern
from app.gospel.patterns.rhythm import apply_rhythm_pattern
from app.gospel.patterns.improvisation import (
    generate_gospel_fill,
    generate_turnaround,
    generate_chromatic_run
)


class GospelArranger:
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

    def arrange_progression(
        self,
        chords: List[str],
        key: str,
        bpm: int,
        application: str = "practice",
        time_signature: Tuple[int, int] = (4, 4)
    ) -> Arrangement:
        """Generate complete two-hand gospel piano arrangement.

        Args:
            chords: List of chord symbols (e.g., ["Cmaj9", "Am11", "Fmaj13", "G13"])
            key: Key signature (e.g., "C", "F", "Bb")
            bpm: Tempo in beats per minute
            application: Application variant ("worship", "uptempo", "practice", "concert")
            time_signature: Time signature tuple (default 4/4)

        Returns:
            Complete Arrangement with left and right hand notes
        """
        if application not in self.application_configs:
            raise ValueError(
                f"Unknown application: {application}. "
                f"Available: {list(self.application_configs.keys())}"
            )

        config = self.application_configs[application]

        # Build chord contexts
        contexts = self._build_chord_contexts(chords, key, bpm, time_signature)

        # Generate patterns for each chord
        left_hand_notes = []
        right_hand_notes = []

        for i, context in enumerate(contexts):
            # Select patterns based on application and context
            left_pattern_name = self._select_left_pattern(context, config, i)
            right_pattern_name = self._select_right_pattern(context, config, i)

            # Generate patterns
            left_pattern = generate_left_hand_pattern(left_pattern_name, context)
            right_pattern = generate_right_hand_pattern(right_pattern_name, context)

            # Adjust note times for current bar position
            left_notes_adjusted = self._adjust_note_times(left_pattern.notes, i * 4)
            right_notes_adjusted = self._adjust_note_times(right_pattern.notes, i * 4)

            left_hand_notes.extend(left_notes_adjusted)
            right_hand_notes.extend(right_notes_adjusted)

            # Add improvisation (fills, runs, turnarounds)
            if random.random() < config["improvisation_probability"]:
                improv_notes = self._add_improvisation(context, i, application)
                right_hand_notes.extend(improv_notes)

        # Apply rhythm transformations
        if config["rhythm"]:
            for rhythm_pattern in config["rhythm"]:
                left_hand_notes = apply_rhythm_pattern(left_hand_notes, rhythm_pattern)
                right_hand_notes = apply_rhythm_pattern(right_hand_notes, rhythm_pattern)

        # Apply velocity adjustments based on application
        left_hand_notes = self._apply_velocity_range(left_hand_notes, config["velocity_range"])
        right_hand_notes = self._apply_velocity_range(right_hand_notes, config["velocity_range"])

        # Create arrangement
        return Arrangement(
            left_hand_notes=left_hand_notes,
            right_hand_notes=right_hand_notes,
            tempo=bpm,
            time_signature=time_signature,
            key=key,
            total_bars=len(chords),
            application=application
        )

    def _build_chord_contexts(
        self,
        chords: List[str],
        key: str,
        bpm: int,
        time_signature: Tuple[int, int]
    ) -> List[ChordContext]:
        """Build ChordContext objects for each chord in progression.

        Args:
            chords: List of chord symbols
            key: Key signature
            bpm: Tempo
            time_signature: Time signature

        Returns:
            List of ChordContext objects
        """
        contexts = []

        for i, chord in enumerate(chords):
            previous_chord = chords[i - 1] if i > 0 else None
            next_chord = chords[i + 1] if i < len(chords) - 1 else None

            context = ChordContext(
                chord=chord,
                key=key,
                position=i,
                tempo=bpm,
                time_signature=time_signature,
                previous_chord=previous_chord,
                next_chord=next_chord
            )

            contexts.append(context)

        return contexts

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

    def _adjust_note_times(self, notes: List[Note], bar_offset: float) -> List[Note]:
        """Adjust note times for current bar position.

        Args:
            notes: Notes to adjust
            bar_offset: Offset in beats (bar_number * beats_per_bar)

        Returns:
            Notes with adjusted times
        """
        adjusted = []
        for note in notes:
            new_note = Note(
                pitch=note.pitch,
                time=note.time + bar_offset,
                duration=note.duration,
                velocity=note.velocity,
                hand=note.hand
            )
            adjusted.append(new_note)

        return adjusted

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

    def _apply_velocity_range(
        self,
        notes: List[Note],
        velocity_range: Tuple[int, int]
    ) -> List[Note]:
        """Apply velocity range constraints to notes.

        Args:
            notes: Notes to adjust
            velocity_range: (min_velocity, max_velocity)

        Returns:
            Notes with adjusted velocities
        """
        min_vel, max_vel = velocity_range
        adjusted = []

        for note in notes:
            # Scale velocity to fit within range
            scaled_velocity = int(
                min_vel + (note.velocity / 127.0) * (max_vel - min_vel)
            )

            new_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(min_vel, min(scaled_velocity, max_vel)),
                hand=note.hand
            )
            adjusted.append(new_note)

        return adjusted


__all__ = ["GospelArranger"]
