"""R&B Piano Arranger

Implements R&B piano arrangements with:
- Extended harmony voicings (9ths, 11ths, 13ths)
- Smooth voice leading
- Syncopated rhythms with groove feel
"""

from typing import List
import random

from app.core.arrangers.base_arranger import BaseArranger
from app.gospel import Note, ChordContext, HandPattern


class RnBArranger(BaseArranger):
    """R&B arranger with extended harmonies and smooth grooves."""

    def __init__(self):
        super().__init__()

        self.application_configs = {
            "ballad": {
                "left_patterns": ["simple_bass", "octave_bass"],
                "right_patterns": ["lush_voicings", "arpeggios"],
                "rhythm": ["straight"],
                "tempo_range": (60, 75),
                "velocity_range": (50, 85),
            },
            "groove": {
                "left_patterns": ["syncopated_bass", "walking"],
                "right_patterns": ["syncopated_chords", "neo_soul_voicings"],
                "rhythm": ["backbeat"],
                "tempo_range": (80, 95),
                "velocity_range": (65, 95),
            },
            "uptempo": {
                "left_patterns": ["walking", "bounce_bass"],
                "right_patterns": ["16th_chords", "contemporary_voicings"],
                "rhythm": ["16th_feel"],
                "tempo_range": (95, 110),
                "velocity_range": (75, 105),
            },
        }

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate R&B left hand bass pattern."""
        root = context.root_note
        fifth = root + 7
        notes: List[Note] = []

        if "syncopated" in pattern_name or "bounce" in pattern_name:
            # Syncopated bass with anticipations
            positions = [0.0, 1.75, 2.0, 3.5]
            pitches = [root - 12, fifth - 12, root - 12, fifth - 12]

            for pos, pitch in zip(positions, pitches):
                notes.append(Note(
                    pitch=pitch,
                    time=context.bar_start + pos,
                    duration=0.2,
                    velocity=85 if pos in [0.0, 2.0] else 70
                ))
        elif "walking" in pattern_name:
            # Walking bass
            for beat in range(4):
                pitch = root - 12 if beat % 2 == 0 else fifth - 12
                notes.append(Note(
                    pitch=pitch,
                    time=context.bar_start + beat,
                    duration=0.8,
                    velocity=80
                ))
        else:
            # Simple roots
            notes.append(Note(
                pitch=root - 12,
                time=context.bar_start,
                duration=2.0,
                velocity=75
            ))

        return HandPattern(notes=notes, pattern_name=pattern_name)

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext) -> HandPattern:
        """Generate R&B right hand voicings with extensions."""
        notes: List[Note] = []
        chord_notes = context.chord_notes[:5]  # Include extensions (9ths, 11ths)

        if "lush" in pattern_name or "neo_soul" in pattern_name:
            # Sustained lush voicings
            for pitch in chord_notes:
                notes.append(Note(
                    pitch=pitch + 12,
                    time=context.bar_start,
                    duration=3.5,
                    velocity=60
                ))
        elif "syncopated" in pattern_name or "16th" in pattern_name:
            # Syncopated chord hits
            positions = [0.0, 1.5, 2.0, 3.25, 3.5]
            for pos in positions:
                for pitch in chord_notes[:4]:
                    notes.append(Note(
                        pitch=pitch + 12,
                        time=context.bar_start + pos,
                        duration=0.2,
                        velocity=65
                    ))
        else:
            # Arpeggios
            for i, pitch in enumerate(chord_notes):
                notes.append(Note(
                    pitch=pitch + 12,
                    time=context.bar_start + (i * 0.5),
                    duration=0.4,
                    velocity=70
                ))

        return HandPattern(notes=notes, pattern_name=pattern_name)

    def _apply_rhythm_pattern(self, notes: List[Note], rhythm_name: str) -> List[Note]:
        """Apply R&B rhythm feel."""
        if "backbeat" in rhythm_name:
            # Emphasize beats 2 and 4
            transformed = []
            for note in notes:
                beat_pos = note.time % 4.0
                if 1.0 <= beat_pos < 2.0 or 3.0 <= beat_pos < 4.0:
                    velocity = min(127, int(note.velocity * 1.15))
                else:
                    velocity = note.velocity

                transformed.append(Note(
                    pitch=note.pitch,
                    time=note.time,
                    duration=note.duration,
                    velocity=velocity
                ))
            return transformed

        return notes

    def _select_left_hand_pattern(self, context: ChordContext, application: str) -> str:
        config = self.application_configs.get(application, self.application_configs["groove"])
        return random.choice(config["left_patterns"])

    def _select_right_hand_pattern(self, context: ChordContext, application: str) -> str:
        config = self.application_configs.get(application, self.application_configs["groove"])
        return random.choice(config["right_patterns"])

    def _select_rhythm_pattern(self, application: str) -> str:
        config = self.application_configs.get(application, self.application_configs["groove"])
        return random.choice(config["rhythm"])

    def _get_default_application(self) -> str:
        return "groove"

    def _adjust_velocity_for_dynamics(self, notes: List[Note], application: str) -> List[Note]:
        """Adjust velocities for smooth R&B dynamics."""
        config = self.application_configs.get(application, self.application_configs["groove"])
        min_vel, max_vel = config["velocity_range"]

        return [Note(
            pitch=n.pitch,
            time=n.time,
            duration=n.duration,
            velocity=max(min_vel, min(max_vel, n.velocity))
        ) for n in notes]
