"""
Jazz Theory Integration

Jazz-specific applications of advanced music theory:
- Coltrane Changes (Giant Steps pattern)
- Barry Harris diminished system
- Tritone substitutions
- Extended chord alterations
- Modal jazz concepts
- Bebop scales
"""

import logging
from typing import Dict, List, Any, Tuple, Optional

from app.theory.chord_substitutions import (
    apply_coltrane_changes,
    get_giant_steps_cycle,
    get_sixth_diminished_scale,
    suggest_reharmonization
)
# Create alias for backwards compatibility
find_substitutions = suggest_reharmonization

from app.theory.voice_leading_neo_riemannian import get_tonnetz_path

logger = logging.getLogger(__name__)


class JazzTheorySystem:
    """
    Jazz music theory specialization.

    Jazz harmony is characterized by:
    - Complex chord progressions (Coltrane changes)
    - Tritone substitutions
    - Extended and altered chords (9th, 11th, 13th, #5, b9)
    - Modal concepts (Dorian, Mixolydian, etc.)
    - Barry Harris diminished approach
    """

    def apply_coltrane_to_ii_v_i(
        self,
        key: str,
        complexity: int = 1
    ) -> Dict[str, Any]:
        """
        Apply Coltrane changes to standard ii-V-I progression.

        Complexity levels:
        - 1: Simple modulation through one tonal center
        - 2: Modulation through two tonal centers
        - 3: Full Giant Steps pattern (three tonal centers)

        Args:
            key: Starting key
            complexity: 1-3, number of tonal centers

        Returns:
            Dict with enhanced progression and analysis
        """

        # Standard ii-V-I in C: Dm7 - G7 - Cmaj7
        base_progression = [
            (f"{key}", "m7"),  # ii (relative to key)
            (self._get_dominant(key), "7"),  # V
            (key, "maj7")  # I
        ]

        if complexity == 1:
            # Add one intermediate tonal center
            # Dm7 - F#7 - Bmaj7 - G7 - Cmaj7
            enhanced = [
                base_progression[0],
                (self._transpose_key(key, 6), "7"),  # Tritone away
                (self._transpose_key(key, 11), "maj7"),  # Major 3rd cycle
                base_progression[1],
                base_progression[2]
            ]
        elif complexity == 2:
            # Two intermediate centers
            # Full Coltrane progression
            enhanced = apply_coltrane_changes(
                base_progression,
                key,
                num_cycles=2
            )
        else:
            # Full Giant Steps pattern (3 tonal centers)
            enhanced = get_giant_steps_cycle(key)

        return {
            'original': base_progression,
            'enhanced': enhanced,
            'tonal_centers': self._identify_tonal_centers(enhanced),
            'complexity': complexity,
            'technique': 'Coltrane Changes',
            'description': f'Rapid modulation through {complexity + 1} tonal centers separated by major thirds'
        }

    def generate_bebop_line_with_diminished(
        self,
        chord_progression: List[Tuple[str, str]],
        key: str
    ) -> Dict[str, Any]:
        """
        Generate bebop line using Barry Harris diminished system.

        Barry Harris approach:
        - Over major chords: Use 6th-diminished scale
        - Over dominant: Four dominant 7ths from diminished
        - Chromatic passing tones

        Args:
            chord_progression: List of (root, quality) tuples
            key: Musical key

        Returns:
            Dict with bebop line and theory explanation
        """

        line_segments = []

        for chord in chord_progression:
            if 'maj' in chord[1]:
                # Use 6th-diminished scale
                scale = get_sixth_diminished_scale(chord[0])
                line_segments.append({
                    'chord': chord,
                    'scale': scale,
                    'approach': '6th-diminished',
                    'notes': scale[:8]  # One octave
                })

            elif '7' in chord[1] and 'm' not in chord[1]:
                # Dominant chord - use diminished approach
                # Four dominant 7ths from single diminished 7th
                dim_root = self._transpose_key(chord[0], 1)  # Half step up
                dominants = self._get_four_dominants_from_dim(dim_root)

                line_segments.append({
                    'chord': chord,
                    'approach': 'four_dominants_diminished',
                    'available_dominants': dominants,
                    'notes': self._generate_dom_line(chord[0])
                })

            else:
                # Minor chord - use dorian or minor scale
                line_segments.append({
                    'chord': chord,
                    'approach': 'dorian',
                    'notes': self._get_dorian_scale(chord[0])
                })

        return {
            'chord_progression': chord_progression,
            'line_segments': line_segments,
            'key': key,
            'style': 'bebop',
            'theory': 'Barry Harris diminished system'
        }

    def apply_tritone_substitutions(
        self,
        progression: List[Tuple[str, str]],
        density: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Apply tritone substitutions to dominant chords.

        Density levels:
        - sparse: Substitute only at cadences
        - moderate: Substitute 50% of dominants
        - dense: Substitute all dominants

        Args:
            progression: Original chord progression
            density: How many substitutions to apply

        Returns:
            Dict with substituted progression and analysis
        """

        substituted = []
        substitutions_made = []

        for i, chord in enumerate(progression):
            # Check if dominant 7th
            if '7' in chord[1] and 'm' not in chord[1]:
                should_substitute = False

                if density == "sparse":
                    # Only substitute at cadences (V → I)
                    if i < len(progression) - 1:
                        next_chord = progression[i + 1]
                        if 'maj' in next_chord[1]:
                            should_substitute = True

                elif density == "moderate":
                    # Substitute every other dominant
                    should_substitute = i % 2 == 0

                else:  # dense
                    should_substitute = True

                if should_substitute:
                    # Apply tritone sub
                    sub_root = self._transpose_key(chord[0], 6)  # Tritone away
                    substituted.append((sub_root, chord[1]))

                    substitutions_made.append({
                        'position': i,
                        'original': chord,
                        'substitution': (sub_root, chord[1]),
                        'reason': 'tritone_substitution'
                    })
                else:
                    substituted.append(chord)
            else:
                substituted.append(chord)

        return {
            'original': progression,
            'substituted': substituted,
            'substitutions': substitutions_made,
            'density': density,
            'count': len(substitutions_made)
        }

    def analyze_modal_jazz_progression(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> Dict[str, Any]:
        """
        Analyze progression for modal jazz characteristics.

        Modal jazz features:
        - Static harmony (few chord changes)
        - Modal scales (Dorian, Phrygian, Lydian, etc.)
        - Pedal points
        - Chord quality emphasis over function

        Returns:
            Analysis with recommended modes and scales
        """

        analysis = []

        for chord in progression:
            # Determine appropriate mode
            mode_recommendation = self._get_modal_recommendation(chord, key)

            analysis.append({
                'chord': chord,
                'recommended_mode': mode_recommendation['mode'],
                'scale_notes': mode_recommendation['notes'],
                'characteristic_notes': mode_recommendation['characteristic'],
                'avoid_notes': mode_recommendation['avoid']
            })

        # Check if progression is modal (static harmony)
        is_modal = len(set(progression)) <= 2  # 2 or fewer unique chords

        return {
            'progression': progression,
            'is_modal': is_modal,
            'style': 'modal_jazz' if is_modal else 'functional_jazz',
            'chord_analysis': analysis,
            'approach': 'horizontal' if is_modal else 'vertical'
        }

    def _get_dominant(self, root: str) -> str:
        """Get the V (dominant) of a key"""
        # Simplified - in practice would use proper music theory
        dom_map = {'C': 'G', 'D': 'A', 'E': 'B', 'F': 'C', 'G': 'D', 'A': 'E', 'B': 'F#'}
        return dom_map.get(root, 'G')

    def _transpose_key(self, root: str, semitones: int) -> str:
        """Transpose a root note by semitones"""
        notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        if root not in notes:
            return root
        index = notes.index(root)
        new_index = (index + semitones) % 12
        return notes[new_index]

    def _identify_tonal_centers(self, progression: List[Tuple[str, str]]) -> List[str]:
        """Identify tonal centers in progression"""
        centers = []
        for chord in progression:
            if 'maj' in chord[1]:
                centers.append(chord[0])
        return list(set(centers))

    def _get_four_dominants_from_dim(self, dim_root: str) -> List[Tuple[str, str]]:
        """Get four dominant 7th chords from single diminished 7th"""
        # Barry Harris: From any dim7, you can derive 4 dominant 7ths
        # Example: Cdim7 → C7, Eb7, F#7, A7
        roots = [
            dim_root,
            self._transpose_key(dim_root, 3),  # Minor 3rd
            self._transpose_key(dim_root, 6),  # Tritone
            self._transpose_key(dim_root, 9)   # Major 6th
        ]
        return [(r, '7') for r in roots]

    def _generate_dom_line(self, root: str) -> List[int]:
        """Generate dominant line with alterations"""
        # Simplified - return scale degrees
        # In practice would return full bebop scale with chromatic passing
        return [0, 2, 4, 5, 7, 9, 10, 11]  # Mixolydian with b9, #9

    def _get_dorian_scale(self, root: str) -> List[int]:
        """Get Dorian mode"""
        return [0, 2, 3, 5, 7, 9, 10, 12]  # Dorian scale degrees

    def _get_modal_recommendation(
        self,
        chord: Tuple[str, str],
        key: str
    ) -> Dict[str, Any]:
        """Get modal recommendation for a chord"""

        if 'm7' in chord[1]:
            return {
                'mode': 'Dorian',
                'notes': self._get_dorian_scale(chord[0]),
                'characteristic': ['6th degree (major 6th)'],
                'avoid': ['b6 (unless Aeolian desired)']
            }
        elif '7' in chord[1] and 'm' not in chord[1]:
            return {
                'mode': 'Mixolydian',
                'notes': [0, 2, 4, 5, 7, 9, 10, 12],
                'characteristic': ['b7 (natural for dominant)'],
                'avoid': ['natural 7 (would create maj7)']
            }
        elif 'maj7' in chord[1]:
            return {
                'mode': 'Lydian' if '#11' in chord[1] else 'Ionian',
                'notes': [0, 2, 4, 6, 7, 9, 11, 12] if '#11' in chord[1] else [0, 2, 4, 5, 7, 9, 11, 12],
                'characteristic': ['#4 (Lydian)' if '#11' in chord[1] else 'natural 4'],
                'avoid': ['natural 4 (if Lydian)' if '#11' in chord[1] else 'none']
            }
        else:
            return {
                'mode': 'Ionian',
                'notes': [0, 2, 4, 5, 7, 9, 11, 12],
                'characteristic': ['natural 7'],
                'avoid': []
            }


# Global instance
jazz_theory = JazzTheorySystem()
