"""
Arrangement Humanizer

Applies micro-timing, velocity curves, and groove to make
AI-generated arrangements sound more human and musically expressive.

Features:
- Micro-timing variations based on beat position
- Dynamic velocity curves (genre-specific)
- Ghost notes for groove
- Beat emphasis patterns (backbeat for gospel, swing for jazz)
- Phrase-level dynamics (build, peak, resolve)
"""

import random
from typing import Optional
from dataclasses import dataclass


@dataclass
class Note:
    """Musical note for arrangement (compatible with gospel.Note)."""
    pitch: int
    time: float
    duration: float
    velocity: int
    hand: str = "right"


# =============================================================================
# GROOVE PROFILES BY GENRE
# =============================================================================

GROOVE_PROFILES = {
    "gospel": {
        "timing_style": "behind_beat",  # Slightly late for warmth
        "beat_emphasis": [1, 3],         # Beats 2 and 4 (0-indexed)
        "swing_amount": 0.15,            # Moderate shuffle
        "ghost_note_probability": 0.15,
        "velocity_variance": 12,
        "push_beats": [1],               # Beat 2 slightly early
        "lay_back_beats": [3],           # Beat 4 slightly late
    },
    "jazz": {
        "timing_style": "swing",
        "beat_emphasis": [1, 3],
        "swing_amount": 0.25,            # Strong swing
        "ghost_note_probability": 0.1,
        "velocity_variance": 15,
        "push_beats": [],
        "lay_back_beats": [2, 3],        # Behind on beats 3 and 4
    },
    "neo_soul": {
        "timing_style": "behind_beat",
        "beat_emphasis": [1, 3],
        "swing_amount": 0.08,            # Subtle swing
        "ghost_note_probability": 0.12,
        "velocity_variance": 10,
        "push_beats": [],
        "lay_back_beats": [0, 1, 2, 3],  # Everything laid back
    },
    "blues": {
        "timing_style": "shuffle",
        "beat_emphasis": [1, 3],
        "swing_amount": 0.3,             # Heavy shuffle
        "ghost_note_probability": 0.2,
        "velocity_variance": 18,
        "push_beats": [],
        "lay_back_beats": [2, 3],
    },
    "classical": {
        "timing_style": "straight",
        "beat_emphasis": [0],            # Downbeat emphasis
        "swing_amount": 0.0,             # No swing
        "ghost_note_probability": 0.0,
        "velocity_variance": 8,
        "push_beats": [],
        "lay_back_beats": [],
    },
}


class ArrangementHumanizer:
    """
    Post-process AI-generated arrangements to sound more human.
    
    Applies subtle timing, velocity, and articulation variations
    that give the music a performed, rather than programmed, feel.
    """
    
    def __init__(self, genre: str = "gospel"):
        """
        Initialize humanizer with genre-specific groove profile.
        
        Args:
            genre: One of 'gospel', 'jazz', 'neo_soul', 'blues', 'classical'
        """
        self.genre = genre.lower()
        self.profile = GROOVE_PROFILES.get(self.genre, GROOVE_PROFILES["gospel"])
    
    def humanize(
        self,
        notes: list[Note],
        humanization_amount: float = 0.5,
        apply_phrase_dynamics: bool = True
    ) -> list[Note]:
        """
        Apply humanization to a list of notes.
        
        Args:
            notes: Input notes from arranger
            humanization_amount: 0.0 = robotic, 1.0 = heavily humanized
            apply_phrase_dynamics: Apply crescendo/decrescendo over phrases
        
        Returns:
            Humanized notes with natural feel
        """
        if not notes:
            return notes
        
        humanized = []
        
        # Calculate phrase boundaries for dynamics
        total_duration = max(n.time + n.duration for n in notes)
        
        for note in notes:
            humanized_note = Note(
                pitch=note.pitch,
                time=self._humanize_timing(note.time, humanization_amount),
                duration=self._humanize_duration(note.duration, humanization_amount),
                velocity=self._humanize_velocity(
                    note, 
                    humanization_amount,
                    total_duration if apply_phrase_dynamics else None
                ),
                hand=note.hand
            )
            humanized.append(humanized_note)
        
        # Add ghost notes for groove (genre-specific)
        if humanization_amount > 0.3:
            ghost_notes = self._generate_ghost_notes(humanized, humanization_amount)
            humanized.extend(ghost_notes)
        
        # Sort by time
        humanized.sort(key=lambda n: n.time)
        
        return humanized
    
    def _humanize_timing(self, time: float, amount: float) -> float:
        """
        Add micro-timing variations based on beat position.
        
        Different genres have different "pocket" feels:
        - Gospel: Push beat 2, lay back on beat 4
        - Jazz: Swing on off-beats
        - Neo-soul: Everything slightly behind
        """
        beat_in_bar = int(time) % 4
        fractional_beat = time - int(time)
        
        # Base random variation (Gaussian for natural feel)
        base_offset = random.gauss(0, 0.015) * amount
        
        # Genre-specific timing adjustments
        if beat_in_bar in self.profile["push_beats"]:
            # Push this beat slightly ahead
            base_offset += 0.025 * amount
        elif beat_in_bar in self.profile["lay_back_beats"]:
            # Lay back on this beat
            base_offset -= 0.03 * amount
        
        # Apply swing to off-beats
        if fractional_beat > 0.4 and fractional_beat < 0.6:  # "And" of the beat
            swing_offset = self.profile["swing_amount"] * amount
            if self.profile["timing_style"] == "shuffle":
                base_offset += swing_offset
            elif self.profile["timing_style"] == "swing":
                base_offset += swing_offset * 0.67  # Triplet-based swing
        
        # Ensure time doesn't go negative
        return max(0, time + base_offset)
    
    def _humanize_duration(self, duration: float, amount: float) -> float:
        """
        Add subtle duration variations.
        
        Shorter notes get slightly shorter, longer notes slightly longer
        for a more natural feel.
        """
        # Small random variation
        variance = random.gauss(0, 0.03) * amount
        
        # Tendency: short notes get shorter, long notes get longer
        if duration < 0.5:
            variance -= 0.02 * amount
        elif duration > 2.0:
            variance += 0.03 * amount
        
        return max(0.1, duration * (1 + variance))
    
    def _humanize_velocity(
        self, 
        note: Note, 
        amount: float,
        total_duration: Optional[float] = None
    ) -> int:
        """
        Apply dynamic velocity curves.
        
        Includes:
        - Beat emphasis (backbeat for gospel/jazz)
        - Random variation
        - Phrase-level dynamics (optional)
        - Hand-specific adjustments
        """
        base_velocity = note.velocity
        beat_in_bar = int(note.time) % 4
        
        # Beat emphasis
        if beat_in_bar in self.profile["beat_emphasis"]:
            beat_boost = int(12 * amount)
        else:
            beat_boost = 0
        
        # Random variation
        variance = self.profile["velocity_variance"]
        # Gaussian distribution for more natural center-weighted variation
        random_variation = int(random.gauss(0, variance / 2.0) * amount)
        
        # Phrase dynamics (build toward middle, resolve at end)
        phrase_adjustment = 0
        if total_duration and total_duration > 0:
            position_ratio = note.time / total_duration
            if position_ratio < 0.3:
                # Beginning: building
                phrase_adjustment = int((position_ratio / 0.3) * 8 * amount)
            elif position_ratio < 0.7:
                # Middle/climax: full intensity
                phrase_adjustment = int(10 * amount)
            else:
                # Ending: resolving
                phrase_adjustment = int((1 - (position_ratio - 0.7) / 0.3) * 8 * amount)
        
        # Hand-specific adjustments
        hand_adjustment = 0
        if note.hand == "left":
            # Left hand typically slightly softer (supporting role)
            hand_adjustment = -5
        
        # Calculate final velocity
        final_velocity = (
            base_velocity 
            + beat_boost 
            + random_variation 
            + phrase_adjustment 
            + hand_adjustment
        )
        
        # Clamp to valid MIDI range
        return max(20, min(127, final_velocity))
    
    def _generate_ghost_notes(
        self, 
        notes: list[Note], 
        amount: float
    ) -> list[Note]:
        """
        Add subtle ghost notes for groove.
        
        Ghost notes are very soft notes that fill in the groove
        without being heard as distinct musical events.
        """
        ghost_notes = []
        ghost_probability = self.profile["ghost_note_probability"] * amount
        
        for note in notes:
            if note.hand == "left" and random.random() < ghost_probability:
                # Add ghost note slightly before the main note
                ghost_time = note.time - random.uniform(0.15, 0.25)
                if ghost_time >= 0:
                    ghost = Note(
                        pitch=note.pitch,
                        time=ghost_time,
                        duration=0.1,
                        velocity=random.randint(25, 40),  # Very soft
                        hand="left"
                    )
                    ghost_notes.append(ghost)
            
            # Occasional right-hand grace notes
            if note.hand == "right" and random.random() < ghost_probability * 0.5:
                grace_pitch = note.pitch - random.choice([1, 2])  # Half/whole step below
                grace_time = note.time - 0.08
                if grace_time >= 0:
                    grace = Note(
                        pitch=grace_pitch,
                        time=grace_time,
                        duration=0.06,
                        velocity=note.velocity - 20,
                        hand="right"
                    )
                    ghost_notes.append(grace)
        
        return ghost_notes
    
    def set_groove_profile(self, profile: dict) -> None:
        """
        Set a custom groove profile.
        
        Args:
            profile: Dict with timing_style, beat_emphasis, swing_amount, etc.
        """
        self.profile = {**GROOVE_PROFILES["gospel"], **profile}


def humanize_arrangement(
    notes: list,
    genre: str = "gospel",
    amount: float = 0.5
) -> list:
    """
    Convenience function to humanize an arrangement.
    
    Args:
        notes: List of Note-like objects with pitch, time, duration, velocity, hand
        genre: Genre for groove profile
        amount: Humanization amount (0.0-1.0)
    
    Returns:
        List of humanized notes
    """
    humanizer = ArrangementHumanizer(genre)
    
    # Convert to internal Note format if needed
    internal_notes = []
    for n in notes:
        internal_notes.append(Note(
            pitch=getattr(n, 'pitch', n.get('pitch', 60)),
            time=getattr(n, 'time', n.get('time', 0.0)),
            duration=getattr(n, 'duration', n.get('duration', 1.0)),
            velocity=getattr(n, 'velocity', n.get('velocity', 80)),
            hand=getattr(n, 'hand', n.get('hand', 'right'))
        ))
    
    return humanizer.humanize(internal_notes, amount)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ArrangementHumanizer",
    "humanize_arrangement",
    "GROOVE_PROFILES",
    "Note",
]
