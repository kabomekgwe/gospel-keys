"""Base Arranger - Abstract base class for multi-genre piano arrangers

Extracts common arrangement logic shared across all genres (Gospel, Jazz, Neo-Soul, Blues, Classical).
Genre-specific pattern selection and improvisation are implemented in subclasses.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import random

from app.gospel import Note, ChordContext, Arrangement


class BaseArranger(ABC):
    """Abstract base class for genre-specific piano arrangers.

    Provides the core orchestration logic for two-hand piano arrangements:
    - Building chord contexts
    - Pattern selection (abstract - implemented by subclasses)
    - Voice leading coordination
    - Timing adjustments
    - Velocity normalization

    Subclasses must implement:
    - __init__() with genre-specific application configurations
    - _select_left_pattern() for genre-specific left hand selection
    - _select_right_pattern() for genre-specific right hand selection
    - _add_improvisation() for genre-specific fills/runs/turnarounds
    """

    def __init__(self):
        """Initialize base arranger.

        Subclasses should define self.application_configs as a dict mapping
        application names to configuration dicts containing:
        - left_patterns: List of available left hand pattern names
        - right_patterns: List of available right hand pattern names
        - rhythm: List of rhythm transformation names
        - improvisation_probability: Float between 0-1
        - tempo_range: Tuple of (min_bpm, max_bpm)
        - velocity_range: Tuple of (min_velocity, max_velocity)
        """
        self.application_configs = {}

    def arrange_progression(
        self,
        chords: List[str],
        key: str,
        bpm: int,
        application: str,
        time_signature: Tuple[int, int] = (4, 4),
        complexity: int = 5
    ) -> Arrangement:
        """Generate complete two-hand piano arrangement.

        Main orchestrator method - coordinates all steps of arrangement generation.
        This method is concrete (same logic for all genres).

        Args:
            chords: List of chord symbols (e.g., ["Cmaj9", "Am11", "Fmaj13", "G13"])
            key: Key signature (e.g., "C", "F", "Bb")
            bpm: Tempo in beats per minute
            application: Application variant (genre-specific, e.g., "worship", "ballad")
            time_signature: Time signature tuple (default 4/4)
            complexity: Complexity level (1-10) for note density and pattern selection

        Returns:
            Complete Arrangement with left and right hand notes

        Raises:
            ValueError: If application is not in self.application_configs
        """
        if application not in self.application_configs:
            raise ValueError(
                f"Unknown application: {application}. "
                f"Available: {list(self.application_configs.keys())}"
            )

        config = self.application_configs[application]

        # Step 1: Build chord contexts with harmonic metadata
        contexts = self._build_chord_contexts(chords, key, bpm, time_signature)

        # Step 2: Generate patterns for each chord (genre-specific)
        left_hand_notes = []
        right_hand_notes = []
        previous_left_voicing = None
        previous_right_voicing = None

        for i, context in enumerate(contexts):
            # Update context with previous voicings for voice leading
            context.previous_voicing = previous_left_voicing

            # Select patterns (genre-specific abstract methods)
            left_pattern_name = self._select_left_pattern(context, config, i)
            right_pattern_name = self._select_right_pattern(context, config, i)

            # Generate patterns (calls genre-specific pattern generators)
            left_pattern = self._generate_left_pattern(left_pattern_name, context, complexity)
            right_pattern = self._generate_right_pattern(right_pattern_name, context, complexity)

            # Track current voicing for next chord (use unique pitches for voice leading)
            if left_pattern.notes:
                previous_left_voicing = sorted(list(set([n.pitch for n in left_pattern.notes])))
            if right_pattern.notes:
                previous_right_voicing = sorted(list(set([n.pitch for n in right_pattern.notes])))

            # Adjust note times for current bar position
            left_notes_adjusted = self._adjust_note_times(left_pattern.notes, i * 4)
            right_notes_adjusted = self._adjust_note_times(right_pattern.notes, i * 4)

            left_hand_notes.extend(left_notes_adjusted)
            right_hand_notes.extend(right_notes_adjusted)

            # Step 3: Add improvisation (genre-specific)
            if random.random() < config["improvisation_probability"]:
                improv_notes = self._add_improvisation(context, i, application)
                right_hand_notes.extend(improv_notes)

        # Step 4: Apply rhythm transformations (genre-specific)
        if config["rhythm"]:
            left_hand_notes = self._apply_rhythm_transformations(
                left_hand_notes, config["rhythm"]
            )
            right_hand_notes = self._apply_rhythm_transformations(
                right_hand_notes, config["rhythm"]
            )

        # Step 5: Apply velocity normalization (shared)
        left_hand_notes = self._apply_velocity_range(left_hand_notes, config["velocity_range"])
        right_hand_notes = self._apply_velocity_range(right_hand_notes, config["velocity_range"])

        # Step 6: Create final arrangement
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

        Shared method - same for all genres.

        Args:
            chords: List of chord symbols
            key: Key signature
            bpm: Tempo
            time_signature: Time signature

        Returns:
            List of ChordContext objects with harmonic metadata
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

    def _adjust_note_times(self, notes: List[Note], bar_offset: float) -> List[Note]:
        """Adjust note times for current bar position.

        Shared method - same for all genres.

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

    def _apply_velocity_range(
        self,
        notes: List[Note],
        velocity_range: Tuple[int, int]
    ) -> List[Note]:
        """Apply velocity range constraints to notes.

        Shared method - same for all genres.
        Normalizes velocities to fit within the application's dynamic range.

        Args:
            notes: Notes to adjust
            velocity_range: (min_velocity, max_velocity) tuple

        Returns:
            Notes with normalized velocities
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

    # Abstract methods - must be implemented by subclasses

    @abstractmethod
    def _select_left_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate left hand pattern based on context.

        Genre-specific - each genre has different pattern selection rules.

        Args:
            context: Chord context with harmonic metadata
            config: Application configuration
            position: Position in progression (0-indexed)

        Returns:
            Pattern name (string matching genre's pattern library)
        """
        pass

    @abstractmethod
    def _select_right_pattern(
        self,
        context: ChordContext,
        config: dict,
        position: int
    ) -> str:
        """Select appropriate right hand pattern based on context.

        Genre-specific - each genre has different pattern selection rules.

        Args:
            context: Chord context with harmonic metadata
            config: Application configuration
            position: Position in progression (0-indexed)

        Returns:
            Pattern name (string matching genre's pattern library)
        """
        pass

    @abstractmethod
    def _add_improvisation(
        self,
        context: ChordContext,
        position: int,
        application: str
    ) -> List[Note]:
        """Add improvisation elements (fills, runs, turnarounds).

        Genre-specific - each genre has different improvisation styles.
        - Gospel: Turnarounds, gospel fills, chromatic runs
        - Jazz: ii-V licks, bebop runs, turnarounds
        - Neo-soul: Chromatic fills, extended arpeggios
        - Blues: Blues licks, call-response phrases
        - Classical: Ornaments, passing tones (minimal)

        Args:
            context: Chord context
            position: Position in progression
            application: Application type

        Returns:
            List of improvisation notes
        """
        pass

    @abstractmethod
    def _generate_left_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5):
        """Generate left hand pattern.

        Genre-specific - calls genre's pattern generation function.

        Args:
            pattern_name: Name of pattern to generate
            context: Chord context
            complexity: Complexity level (1-10)

        Returns:
            HandPattern with generated notes
        """
        pass

    @abstractmethod
    def _generate_right_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5):
        """Generate right hand pattern.

        Genre-specific - calls genre's pattern generation function.

        Args:
            pattern_name: Name of pattern to generate
            context: Chord context
            complexity: Complexity level (1-10)

        Returns:
            HandPattern with generated notes
        """
        pass

    @abstractmethod
    def _apply_rhythm_transformations(self, notes: List[Note], rhythm_patterns: List[str]) -> List[Note]:
        """Apply rhythm transformations.

        Genre-specific - each genre has different rhythm feels.
        - Gospel: Gospel shuffle, backbeat emphasis, gospel swing
        - Jazz: Swing transformations (triplet-based)
        - Neo-soul: 16th-note grooves
        - Blues: Shuffle (12/8 feel in 4/4)
        - Classical: Minimal (usually straight)

        Args:
            notes: Notes to transform
            rhythm_patterns: List of rhythm pattern names

        Returns:
            Transformed notes
        """
        pass


__all__ = ["BaseArranger"]
