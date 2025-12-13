"""Gospel Piano Generation Module

Core data structures and utilities for generating realistic gospel piano MIDI.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Note:
    """Represents a single MIDI note with timing and expression.

    Attributes:
        pitch: MIDI note number (0-127)
        time: Beat position relative to bar start (0.0 = downbeat)
        duration: Note length in beats
        velocity: MIDI velocity (0-127)
        hand: Which hand plays this note ("left" or "right")
    """
    pitch: int
    time: float
    duration: float
    velocity: int
    hand: str

    def __post_init__(self):
        """Validate note parameters."""
        if not 0 <= self.pitch <= 127:
            raise ValueError(f"Invalid MIDI pitch: {self.pitch} (must be 0-127)")
        if not 0 <= self.velocity <= 127:
            raise ValueError(f"Invalid velocity: {self.velocity} (must be 0-127)")
        if self.hand not in ("left", "right"):
            raise ValueError(f"Invalid hand: {self.hand} (must be 'left' or 'right')")
        if self.duration <= 0:
            raise ValueError(f"Invalid duration: {self.duration} (must be positive)")


@dataclass
class ChordContext:
    """Context information for generating chord patterns.

    Provides all necessary context for pattern generators to make
    intelligent decisions about voicing, rhythm, and improvisation.

    Attributes:
        chord: Chord symbol (e.g., "Cmaj9", "G7", "Dm11")
        key: Key signature (e.g., "C", "F", "Bb")
        position: Bar number in progression (0-indexed)
        tempo: Tempo in beats per minute
        time_signature: Time signature as (numerator, denominator)
        previous_chord: Previous chord symbol for voice leading
        next_chord: Next chord symbol for anticipation
    """
    chord: str
    key: str
    position: int
    tempo: int
    time_signature: Tuple[int, int] = (4, 4)
    previous_chord: Optional[str] = None
    next_chord: Optional[str] = None

    @property
    def is_phrase_start(self) -> bool:
        """Check if this is the start of a musical phrase."""
        return self.position % 4 == 0

    @property
    def is_phrase_end(self) -> bool:
        """Check if this is the end of a musical phrase."""
        return (self.position + 1) % 4 == 0

    @property
    def beats_per_bar(self) -> int:
        """Number of beats in one bar."""
        return self.time_signature[0]


@dataclass
class HandPattern:
    """Represents a complete pattern for one hand.

    Encapsulates a musical pattern with metadata for intelligent
    pattern selection and variation.

    Attributes:
        name: Pattern identifier (e.g., "stride_bass", "gospel_run")
        notes: List of Note objects comprising the pattern
        difficulty: Skill level ("beginner", "intermediate", "advanced", "expert")
        tempo_range: Minimum and maximum suitable BPM
        characteristics: Musical characteristics for pattern selection
    """
    name: str
    notes: List[Note]
    difficulty: str
    tempo_range: Tuple[int, int]
    characteristics: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate pattern parameters."""
        valid_difficulties = {"beginner", "intermediate", "advanced", "expert"}
        if self.difficulty not in valid_difficulties:
            raise ValueError(
                f"Invalid difficulty: {self.difficulty} "
                f"(must be one of {valid_difficulties})"
            )
        if self.tempo_range[0] > self.tempo_range[1]:
            raise ValueError(
                f"Invalid tempo range: {self.tempo_range} "
                "(min must be <= max)"
            )

    def is_suitable_for_tempo(self, tempo: int) -> bool:
        """Check if this pattern works at the given tempo."""
        return self.tempo_range[0] <= tempo <= self.tempo_range[1]

    def has_characteristic(self, characteristic: str) -> bool:
        """Check if pattern has a specific characteristic."""
        return characteristic in self.characteristics


@dataclass
class Arrangement:
    """Complete two-hand gospel piano arrangement.

    Represents the final output of the arrangement engine,
    ready for MIDI export.

    Attributes:
        left_hand_notes: All notes for the left hand
        right_hand_notes: All notes for the right hand
        tempo: Arrangement tempo in BPM
        time_signature: Time signature
        key: Key signature
        total_bars: Number of bars in arrangement
        application: Application type variant
    """
    left_hand_notes: List[Note]
    right_hand_notes: List[Note]
    tempo: int
    time_signature: Tuple[int, int]
    key: str
    total_bars: int
    application: str

    @property
    def total_duration_beats(self) -> float:
        """Total duration in beats."""
        return self.total_bars * self.time_signature[0]

    @property
    def total_duration_seconds(self) -> float:
        """Total duration in seconds."""
        beats = self.total_duration_beats
        return (beats / self.tempo) * 60

    def get_all_notes(self) -> List[Note]:
        """Get all notes from both hands, sorted by time."""
        all_notes = self.left_hand_notes + self.right_hand_notes
        return sorted(all_notes, key=lambda n: n.time)


__all__ = [
    "Note",
    "ChordContext",
    "HandPattern",
    "Arrangement",
]
