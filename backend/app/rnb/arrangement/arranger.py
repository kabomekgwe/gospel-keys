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


from app.gospel.patterns.left_hand import get_chord_tones

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
                "tempo_range": (60, 75),
                "velocity_range": (50, 85),
                "improvisation_probability": 0.1,
            },
            "groove": {
                "left_patterns": ["syncopated_bass", "walking"],
                "right_patterns": ["syncopated_chords", "neo_soul_voicings"],
                "rhythm": ["backbeat"],
                "tempo_range": (80, 95),
                "tempo_range": (80, 95),
                "velocity_range": (65, 95),
                "improvisation_probability": 0.3,
            },
            "uptempo": {
                "left_patterns": ["walking", "bounce_bass"],
                "right_patterns": ["16th_chords", "contemporary_voicings"],
                "rhythm": ["16th_feel"],
                "tempo_range": (95, 110),
                "tempo_range": (95, 110),
                "velocity_range": (75, 105),
                "improvisation_probability": 0.4,
            },
        }

    def _generate_left_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5) -> HandPattern:
        """Generate R&B left hand bass pattern."""
        # Parse chords to get root (Octave 3 for bass)
        chord_tones = get_chord_tones(context.chord, octave=3)
        root = chord_tones[0]
        fifth = root + 7
        notes: List[Note] = []

        if "syncopated" in pattern_name or "bounce" in pattern_name:
            # Syncopated bass with anticipations
            positions = [0.0, 1.75, 2.0, 3.5]
            pitches = [root - 12, fifth - 12, root - 12, fifth - 12]

            # Higher complexity = more syncopation
            if complexity > 6:
                positions.extend([1.0, 2.75])
                pitches.extend([root - 12, fifth - 12])

            for pos, pitch in zip(positions, pitches):
                notes.append(Note(
                    pitch=pitch,
                    time=float(pos),
                    duration=0.2,
                    velocity=85 if pos in [0.0, 2.0] else 70,
                    hand="left"
                ))
        elif "walking" in pattern_name:
            # Walking bass
            for beat in range(4):
                pitch = root - 12 if beat % 2 == 0 else fifth - 12
                # Complexity variation: passing tones
                if complexity > 5 and beat == 3:
                     pitch += 1 # Chromatic approach

                notes.append(Note(
                    pitch=pitch,
                    time=float(beat),
                    duration=0.8,
                    velocity=80,
                    hand="left"
                ))
        else:
            # Simple roots (Ballad style usually)
            notes.append(Note(
                pitch=root - 12,
                time=0.0,
                duration=2.0,
                velocity=75,
                hand="left"
            ))
            # Complexity: add 5th on beat 3
            if complexity >= 4:
                notes.append(Note(
                    pitch=fifth - 12,
                    time=2.0,
                    duration=2.0,
                    velocity=70,
                    hand="left"
                ))

        return HandPattern(
            name=pattern_name,
            notes=notes,
            difficulty="intermediate",
            tempo_range=(60, 120)
        )

    def _generate_right_pattern(self, pattern_name: str, context: ChordContext, complexity: int = 5) -> HandPattern:
        """Generate R&B right hand voicings with extensions."""
        notes: List[Note] = []
        # Get chord tones with extensions (Octave 4 for RH)
        chord_notes = get_chord_tones(context.chord, octave=4, previous_voicing=context.previous_voicing)
        
        if "lush" in pattern_name or "neo_soul" in pattern_name:
            # Sustained lush voicings
            if complexity < 5:
                # Simple block chords
                for pitch in chord_notes:
                    notes.append(Note(
                        pitch=pitch + 12,
                        time=0.0,
                        duration=3.5,
                        velocity=60,
                        hand="right"
                    ))
            else:
                # Arpeggiated or broken chords for higher complexity
                for i, pitch in enumerate(chord_notes):
                    # Basic arpeggio offset
                    time_offset = i * 0.05 if complexity < 7 else i * 0.1
                    
                    # Beat 1
                    notes.append(Note(
                        pitch=pitch + 12,
                        time=0.0 + time_offset,
                        duration=3.5,
                        velocity=60,
                        hand="right"
                    ))
                    
                    # Re-trigger some notes on beat 3 for movement if high complexity
                    if complexity >= 7 and i % 2 == 0:
                         notes.append(Note(
                            pitch=pitch + 12,
                            time=2.0 + time_offset,
                            duration=1.5,
                            velocity=55,
                            hand="right"
                        ))
                    
        elif "syncopated" in pattern_name or "16th" in pattern_name:
            # Syncopated chord hits
            positions = [0.0, 1.5, 2.0, 3.25, 3.5]
            # Prune positions for low complexity
            if complexity < 4:
                positions = [0.0, 2.0]
                
            for pos in positions:
                for pitch in chord_notes[:4]:
                    notes.append(Note(
                        pitch=pitch + 12,
                        time=float(pos),
                        duration=0.2,
                        velocity=65,
                        hand="right"
                    ))
        else:
            # Arpeggios
            step = 0.5 if complexity < 6 else 0.25
            for i, pitch in enumerate(chord_notes):
                notes.append(Note(
                    pitch=pitch + 12,
                    time=float(i * step),
                    duration=0.4,
                    velocity=70,
                    hand="right"
                ))

        return HandPattern(
            name=pattern_name,
            notes=notes,
            difficulty="intermediate",
            tempo_range=(60, 120)
        )

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
                    velocity=velocity,
                    hand=note.hand
                ))
            return transformed

        return notes

    def _select_left_pattern(self, context: ChordContext, config: dict, position: int) -> str:
        return random.choice(config["left_patterns"])

    def _select_right_pattern(self, context: ChordContext, config: dict, position: int) -> str:
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
            velocity=max(min_vel, min(max_vel, n.velocity)),
            hand=n.hand
        ) for n in notes]

    def _add_improvisation(self, context: ChordContext, config: dict, position: int) -> List[Note]:
        """Add R&B-specific improvisation elements."""
        # R&B focuses on groove and feel rather than complex improvisation
        return []

    def _apply_rhythm_transformations(self, notes: List[Note], rhythm_patterns: List[str]) -> List[Note]:
        """Apply rhythm transformations."""
        transformed = notes
        for rhythm in rhythm_patterns:
            transformed = self._apply_rhythm_pattern(transformed, rhythm)
        return transformed
