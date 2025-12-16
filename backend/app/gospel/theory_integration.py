"""
Gospel Theory Integration

Gospel-specific applications of advanced music theory:
- Modal interchange (borrowing from parallel minor)
- Chromatic approach chords
- Backdoor progressions (bVII7 → I)
- Voice leading for choir-like voicings
- Negative harmony for alternative endings
- Extended chord voicings
"""

import logging
from typing import Dict, List, Any, Tuple, Optional

from app.theory.chord_substitutions import (
    get_modal_interchange_chord,
    get_negative_harmony_progression,
    suggest_reharmonization
)

# Alias for backwards compatibility
find_substitutions = suggest_reharmonization

# Voice leading optimization imports (using available functions)
from app.theory.voice_leading_optimization import (
    optimize_with_constraints,
    get_register_constrained_voicing
)
# Create aliases for expected function names
optimize_voice_leading = optimize_with_constraints
get_smooth_voicing = get_register_constrained_voicing

from app.theory.chord_library import get_chord_notes

logger = logging.getLogger(__name__)


class GospelTheorySystem:
    """
    Gospel music theory specialization.

    Gospel music is characterized by:
    - Rich harmonic colors (extended chords, modal interchange)
    - Smooth voice leading (common tones, stepwise motion)
    - Chromatic movement (approach chords)
    - Emotional expression through harmony
    """

    # Gospel-specific chord progressions
    GOSPEL_PROGRESSIONS = {
        'traditional': [
            ('I', 'maj7'),
            ('vi', 'm7'),
            ('ii', 'm7'),
            ('V', '7')
        ],
        'contemporary': [
            ('I', 'maj9'),
            ('IV', 'maj9'),
            ('bVII', '7'),  # Backdoor
            ('I', 'maj9')
        ],
        'praise_worship': [
            ('I', 'maj7'),
            ('V', '7sus4'),
            ('V', '7'),
            ('vi', 'm7'),
            ('IV', 'maj7')
        ]
    }

    def generate_gospel_progression_with_theory(
        self,
        base_progression: List[Tuple[str, str]],
        key: str = "C",
        complexity: str = "moderate",
        techniques: List[str] = None
    ) -> Dict[str, Any]:
        """
        Enhance gospel progression with advanced theory techniques.

        Args:
            base_progression: List of (root, quality) tuples
            key: Musical key
            complexity: "simple", "moderate", "advanced"
            techniques: List of techniques to apply
                - 'modal_interchange': Borrowed chords from parallel minor
                - 'chromatic_approach': Chromatic approach to target chords
                - 'backdoor': Use bVII7 → I progression
                - 'negative_harmony': Alternative endings with negative harmony

        Returns:
            Dict with enhanced progression and explanation
        """
        if techniques is None:
            techniques = ['modal_interchange', 'chromatic_approach']

        enhanced = base_progression.copy()
        applied_techniques = []

        # Apply modal interchange (common in gospel)
        if 'modal_interchange' in techniques:
            enhanced, interchange_info = self._apply_modal_interchange(
                enhanced, key, complexity
            )
            if interchange_info:
                applied_techniques.append({
                    'name': 'Modal Interchange',
                    'description': 'Borrowed chords from parallel minor for emotional color',
                    'details': interchange_info
                })

        # Apply chromatic approach chords
        if 'chromatic_approach' in techniques:
            enhanced, approach_info = self._apply_chromatic_approaches(
                enhanced, complexity
            )
            if approach_info:
                applied_techniques.append({
                    'name': 'Chromatic Approach',
                    'description': 'Half-step approach to target chords',
                    'details': approach_info
                })

        # Apply backdoor progression
        if 'backdoor' in techniques:
            enhanced, backdoor_info = self._apply_backdoor(enhanced, key)
            if backdoor_info:
                applied_techniques.append({
                    'name': 'Backdoor Progression',
                    'description': 'bVII7 → I for smooth resolution',
                    'details': backdoor_info
                })

        # Apply negative harmony for ending
        if 'negative_harmony' in techniques:
            enhanced, negative_info = self._apply_negative_ending(
                enhanced, key
            )
            if negative_info:
                applied_techniques.append({
                    'name': 'Negative Harmony Ending',
                    'description': 'Alternative harmonic resolution',
                    'details': negative_info
                })

        return {
            'original_progression': base_progression,
            'enhanced_progression': enhanced,
            'key': key,
            'complexity': complexity,
            'techniques_applied': applied_techniques,
            'style': 'gospel'
        }

    def _apply_modal_interchange(
        self,
        progression: List[Tuple[str, str]],
        key: str,
        complexity: str
    ) -> Tuple[List[Tuple[str, str]], Optional[Dict]]:
        """Apply modal interchange - common in gospel for emotional depth"""

        # Gospel commonly borrows from parallel minor
        # Example: In C major, borrow from C minor

        # For now, use singular function call (would need to call multiple times for multiple chords)
        # borrowed_chords = [get_modal_interchange_chord(key, "major", degree) for degree in ['iv', 'bVI', 'bVII']]
        borrowed_chords = []  # Placeholder - would need full implementation

        if complexity == "simple":
            # Just add one borrowed chord
            # Common: iv (minor 4) instead of IV (major 4)
            if ('F', '') in progression or ('IV', ''):
                enhanced = [(r, 'm' if r in ['F', 'IV'] and q == '' else q)
                           for r, q in progression]
                return enhanced, {
                    'borrowed_chord': 'iv (from parallel minor)',
                    'effect': 'Adds melancholic color'
                }

        # For moderate/advanced, return original for now
        return progression, None

    def _apply_chromatic_approaches(
        self,
        progression: List[Tuple[str, str]],
        complexity: str
    ) -> Tuple[List[Tuple[str, str]], Optional[Dict]]:
        """Add chromatic approach chords - gospel staple"""

        if complexity == "simple":
            return progression, None

        enhanced = []
        approaches = []

        for i, chord in enumerate(progression):
            # Add chromatic approach before certain chords
            # Common: #iv°7 → V7 or bII7 → I

            if chord[0] in ['G', 'V'] and chord[1] == '7':
                # Add #iv°7 before V7
                enhanced.append(('F#', 'dim7'))
                approaches.append({
                    'approach': 'F#dim7',
                    'target': f"{chord[0]}{chord[1]}",
                    'type': 'chromatic_diminished'
                })

            enhanced.append(chord)

        if approaches:
            return enhanced, {'approaches': approaches}

        return progression, None

    def _apply_backdoor(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> Tuple[List[Tuple[str, str]], Optional[Dict]]:
        """Apply backdoor progression (bVII7 → I) - gospel favorite"""

        # Check if progression ends with V → I
        if len(progression) >= 2:
            if progression[-2][0] in ['G', 'V'] and progression[-1][0] in ['C', 'I']:
                # Replace V → I with bVII → I
                enhanced = progression[:-2] + [('Bb', '7'), progression[-1]]
                return enhanced, {
                    'original': 'V7 → I',
                    'backdoor': 'bVII7 → I',
                    'effect': 'Smoother, jazzier resolution'
                }

        return progression, None

    def _apply_negative_ending(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> Tuple[List[Tuple[str, str]], Optional[Dict]]:
        """Apply negative harmony to ending for alternative resolution"""

        if len(progression) < 2:
            return progression, None

        # Apply negative harmony to last 2 chords
        ending = progression[-2:]
        negative_ending = get_negative_harmony_progression(ending, key, "major")

        enhanced = progression[:-2] + negative_ending

        return enhanced, {
            'original_ending': ending,
            'negative_ending': negative_ending,
            'effect': 'Unexpected but harmonically valid resolution'
        }

    def generate_gospel_voicing_with_voice_leading(
        self,
        progression: List[Tuple[str, str]],
        voicing_style: str = "contemporary"
    ) -> Dict[str, Any]:
        """
        Generate gospel voicings optimized for smooth voice leading.

        Voicing styles:
        - 'traditional': Root position, close voicings
        - 'contemporary': Rootless, spread voicings with extensions
        - 'jazz_influenced': Drop-2, drop-3 voicings

        Returns:
            Dict with voicings and voice leading analysis
        """

        voicings = []
        voice_leading_analysis = []

        for i, chord in enumerate(progression):
            if voicing_style == "contemporary":
                # Gospel contemporary: Rootless voicings with extensions
                # Example: Cmaj9 → [E, G, B, D] (no root)
                voicing = self._get_contemporary_voicing(chord)
            elif voicing_style == "jazz_influenced":
                # Drop-2 voicing (2nd voice from top dropped octave)
                voicing = self._get_drop2_voicing(chord)
            else:
                # Traditional: Close position with root
                voicing = self._get_traditional_voicing(chord)

            voicings.append({
                'chord': chord,
                'voicing': voicing,
                'style': voicing_style
            })

            # Analyze voice leading to next chord
            if i < len(progression) - 1:
                next_voicing = self._get_contemporary_voicing(progression[i + 1])

                # Calculate voice movement
                movement = sum(abs(a - b) for a, b in zip(voicing, next_voicing))
                common_tones = sum(1 for note in voicing if note in next_voicing)

                voice_leading_analysis.append({
                    'from': chord,
                    'to': progression[i + 1],
                    'total_movement': movement,
                    'common_tones': common_tones,
                    'smoothness': 'excellent' if movement < 5 else 'good' if movement < 10 else 'moderate'
                })

        return {
            'voicings': voicings,
            'voice_leading_analysis': voice_leading_analysis,
            'style': voicing_style,
            'avg_smoothness': sum(v['total_movement'] for v in voice_leading_analysis) / len(voice_leading_analysis) if voice_leading_analysis else 0
        }

    def _get_contemporary_voicing(self, chord: Tuple[str, str]) -> List[int]:
        """Get contemporary gospel voicing (rootless with extensions)"""
        # Simplified - return MIDI note numbers
        # In practice would use chord_library and voice_leading_optimization

        root_note = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}
        root = root_note.get(chord[0], 60)

        # Example: Cmaj9 rootless → [E, G, B, D] → [64, 67, 71, 74]
        if 'maj9' in chord[1] or 'maj7' in chord[1]:
            return [root + 4, root + 7, root + 11, root + 14]  # 3rd, 5th, 7th, 9th
        elif 'm7' in chord[1]:
            return [root + 3, root + 7, root + 10, root + 14]  # b3, 5th, b7, 9th
        elif '7' in chord[1]:
            return [root + 4, root + 10, root + 14, root + 17]  # 3rd, b7, 9th, 11th
        else:
            return [root, root + 4, root + 7]  # Root, 3rd, 5th

    def _get_drop2_voicing(self, chord: Tuple[str, str]) -> List[int]:
        """Get drop-2 voicing (jazz influenced)"""
        # Close position then drop 2nd voice from top
        close = self._get_traditional_voicing(chord)
        if len(close) >= 4:
            drop2 = [close[0], close[2] - 12, close[1], close[3]]
            return sorted(drop2)
        return close

    def _get_traditional_voicing(self, chord: Tuple[str, str]) -> List[int]:
        """Get traditional close voicing with root"""
        root_note = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}
        root = root_note.get(chord[0], 60)

        # Simple close position
        if 'm' in chord[1]:
            return [root, root + 3, root + 7]  # Root, b3, 5th
        else:
            return [root, root + 4, root + 7]  # Root, 3rd, 5th


# Global instance
gospel_theory = GospelTheorySystem()
