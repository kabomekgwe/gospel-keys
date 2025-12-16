"""Latin/Salsa Piano Arranger

Implements Latin piano arrangements with:
- Montuno patterns (syncopated 2-bar cycles)
- Tumbao bass (roots and fifths with clave)
- Cuban harmony and voicings
"""

from typing import List
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern


class LatinArranger(BaseArranger):
    """Latin/Salsa arranger with montuno and tumbao patterns."""

    def __init__(self):
        super().__init__()

        self.application_configs = {
            "salsa": {
                "left_patterns": ["tumbao_bass", "montuno_bass"],
                "right_patterns": ["montuno", "guajeo"],
                "rhythm": ["clave"],
                "tempo_range": (90, 100),
                "velocity_range": (75, 105),
            },
            "ballad": {
                "left_patterns": ["sustained_bass", "walking"],
                "right_patterns": ["sustained_chords", "arpeggios"],
                "rhythm": ["straight"],
                "tempo_range": (60, 80),
                "velocity_range": (60, 90),
            },
            "uptempo": {
                "left_patterns": ["fast_tumbao", "montuno_bass"],
                "right_patterns": ["montuno", "fast_guajeo"],
                "rhythm": ["clave_fast"],
                "tempo_range": (110, 140),
                "velocity_range": (85, 115),
            },
        }

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate Latin left hand bass pattern."""
        root = context.root_note
        fifth = root + 7
        notes: List[Note] = []

        if pattern_name in ["tumbao_bass", "montuno_bass", "fast_tumbao"]:
            # Tumbao: Root, Fifth, Root+octave pattern
            positions = [0.0, 1.5, 2.5, 3.5] if "fast" in pattern_name else [0.0, 2.0, 3.0]
            pitches = [root - 12, fifth - 12, root]

            for i, pos in enumerate(positions):
                pitch = pitches[i % len(pitches)]
                notes.append(Note(
                    pitch=pitch,
                    time=context.bar_start + pos,
                    duration=0.4,
                    velocity=90 if i == 0 else 75
                ))
        else:
            # Simple roots
            notes.append(Note(pitch=root - 12, time=context.bar_start, duration=2.0, velocity=80))

        return HandPattern(notes=notes, pattern_name=pattern_name)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate Latin right hand montuno pattern."""
        notes: List[Note] = []
        chord_notes = context.chord_notes[:4]

        if "montuno" in pattern_name or "guajeo" in pattern_name:
            # Syncopated montuno pattern
            positions = [0.5, 1.5, 2.0, 3.5]  # Anticipations
            for pos in positions:
                for pitch in chord_notes:
                    notes.append(Note(
                        pitch=pitch + 12,
                        time=context.bar_start + pos,
                        duration=0.2,
                        velocity=70
                    ))
        else:
            # Sustained chords
            for pitch in chord_notes:
                notes.append(Note(pitch=pitch + 12, time=context.bar_start, duration=4.0, velocity=65))

        return HandPattern(notes=notes, pattern_name=pattern_name)

    def _apply_rhythm_pattern(self, notes: List[Note], rhythm_name: str) -> List[Note]:
        """Apply clave rhythm feel."""
        return notes  # Simplified - rhythm already in patterns

    def _select_left_hand_pattern(self, context: ChordContext, application: str) -> str:
        config = self.application_configs.get(application, self.application_configs["salsa"])
        return random.choice(config["left_patterns"])

    def _select_right_hand_pattern(self, context: ChordContext, application: str) -> str:
        config = self.application_configs.get(application, self.application_configs["salsa"])
        return random.choice(config["right_patterns"])

    def _select_rhythm_pattern(self, application: str) -> str:
        config = self.application_configs.get(application, self.application_configs["salsa"])
        return random.choice(config["rhythm"])

    def _get_default_application(self) -> str:
        return "salsa"

    def _adjust_velocity_for_dynamics(self, notes: List[Note], application: str) -> List[Note]:
        """Adjust velocities for Latin dynamics."""
        config = self.application_configs.get(application, self.application_configs["salsa"])
        min_vel, max_vel = config["velocity_range"]

        return [Note(
            pitch=n.pitch,
            time=n.time,
            duration=n.duration,
            velocity=max(min_vel, min(max_vel, n.velocity))
        ) for n in notes]
