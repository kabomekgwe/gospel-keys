"""
Blues Theory Integration

Blues-specific applications of music theory:
- Blues scale and blue notes
- Dominant 7th embellishments
- Quick IV changes
- Diminished passing chords
- Turnarounds
- Call and response patterns
"""

import logging
from typing import Dict, List, Any, Tuple, Optional

from app.theory.chord_substitutions import suggest_reharmonization
# Create alias for backwards compatibility
find_substitutions = suggest_reharmonization

logger = logging.getLogger(__name__)


class BluesTheorySystem:
    """
    Blues music theory specialization.

    Blues harmony characteristics:
    - 12-bar blues form
    - Dominant 7th chords throughout (I7, IV7, V7)
    - Blue notes (b3, b5, b7)
    - Quick IV change (bar 2)
    - Diminished passing chords
    - Turnarounds in bars 11-12
    """

    # Standard 12-bar blues progression
    TWELVE_BAR_BLUES = {
        'basic': [
            ('I', '7'),   # Bar 1
            ('I', '7'),   # Bar 2
            ('I', '7'),   # Bar 3
            ('I', '7'),   # Bar 4
            ('IV', '7'),  # Bar 5
            ('IV', '7'),  # Bar 6
            ('I', '7'),   # Bar 7
            ('I', '7'),   # Bar 8
            ('V', '7'),   # Bar 9
            ('IV', '7'),  # Bar 10
            ('I', '7'),   # Bar 11
            ('V', '7'),   # Bar 12 (turnaround)
        ],
        'quick_four': [
            ('I', '7'),   # Bar 1
            ('IV', '7'),  # Bar 2 - Quick IV
            ('I', '7'),   # Bar 3
            ('I', '7'),   # Bar 4
            ('IV', '7'),  # Bar 5
            ('IV', '7'),  # Bar 6
            ('I', '7'),   # Bar 7
            ('I', '7'),   # Bar 8
            ('V', '7'),   # Bar 9
            ('IV', '7'),  # Bar 10
            ('I', '7'),   # Bar 11
            ('V', '7'),   # Bar 12
        ]
    }

    def generate_blues_progression_with_theory(
        self,
        key: str = "C",
        style: str = "quick_four",
        sophistication: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Generate blues progression with theory enhancements.

        Args:
            key: Blues key
            style: "basic" or "quick_four"
            sophistication: "simple", "moderate", "jazz_blues"

        Returns:
            Dict with progression and theory analysis
        """

        base = self.TWELVE_BAR_BLUES[style].copy()

        # Convert roman numerals to actual chords
        progression = self._resolve_roman_numerals(base, key)

        if sophistication == "moderate":
            # Add diminished passing chords
            progression = self._add_diminished_passing(progression, key)

        elif sophistication == "jazz_blues":
            # Full jazz blues treatment
            progression = self._apply_jazz_blues_changes(progression, key)

        return {
            'progression': progression,
            'key': key,
            'style': style,
            'sophistication': sophistication,
            'form': '12-bar blues',
            'characteristics': self._analyze_blues_characteristics(progression)
        }

    def _resolve_roman_numerals(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> List[Tuple[str, str]]:
        """Convert roman numerals to actual chord roots"""
        # Simplified mapping
        mapping = {
            'I': key,
            'IV': self._transpose(key, 5),  # Perfect 4th
            'V': self._transpose(key, 7)    # Perfect 5th
        }

        resolved = []
        for numeral, quality in progression:
            root = mapping.get(numeral, key)
            resolved.append((root, quality))

        return resolved

    def _add_diminished_passing(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> List[Tuple[str, str]]:
        """Add diminished passing chords between I and IV"""

        enhanced = []

        for i, chord in enumerate(progression):
            enhanced.append(chord)

            # Add passing dim between I → IV
            if i < len(progression) - 1:
                current = chord[0]
                next_chord = progression[i + 1][0]

                # If going from I to IV, add #Idim7
                if current == key and next_chord == self._transpose(key, 5):
                    passing_root = self._transpose(key, 1)  # Half step up
                    enhanced.append((passing_root, 'dim7'))

        return enhanced

    def _apply_jazz_blues_changes(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> List[Tuple[str, str]]:
        """Apply jazz blues substitutions and additions"""

        # Start with base 12-bar
        jazz_blues = []

        # Bar 1-2: I7 → IV7 (quick change often kept)
        jazz_blues.extend([
            (key, 'maj7'),  # I major 7 instead of dom7
            (self._transpose(key, 5), '7'),  # IV7
        ])

        # Bar 3-4: I7 → I7 (often add #iv dim)
        jazz_blues.extend([
            (key, '7'),
            (self._transpose(key, 6), 'dim7'),  # #iv dim passing
        ])

        # Bar 5-6: IV7 → #iv dim7
        jazz_blues.extend([
            (self._transpose(key, 5), '7'),
            (self._transpose(key, 6), 'dim7'),
        ])

        # Bar 7-8: I7 → vi7 (common jazz blues move)
        jazz_blues.extend([
            (key, 'maj7'),
            (self._transpose(key, 9), 'm7'),  # vi7
        ])

        # Bar 9-10: ii7 → V7 (instead of V7 → IV7)
        jazz_blues.extend([
            (self._transpose(key, 2), 'm7'),  # ii7
            (self._transpose(key, 7), '7'),   # V7
        ])

        # Bar 11-12: I7 → VI7 (turnaround with secondary dominant)
        jazz_blues.extend([
            (key, 'maj7'),
            (self._transpose(key, 9), '7'),  # VI7 (secondary dominant)
        ])

        return jazz_blues[:12]  # Ensure exactly 12 bars

    def _analyze_blues_characteristics(
        self,
        progression: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """Analyze blues-specific characteristics"""

        dom7_count = sum(1 for _, q in progression if q == '7' and 'm' not in q)
        dim_count = sum(1 for _, q in progression if 'dim' in q)
        has_quick_four = len(progression) > 1 and progression[1][1] == '7'

        return {
            'dominant_7th_density': f"{dom7_count}/{len(progression)}",
            'diminished_passing': dim_count > 0,
            'quick_four_change': has_quick_four,
            'authenticity': 'high' if dom7_count >= len(progression) * 0.6 else 'moderate'
        }

    def get_blues_scale(self, key: str) -> Dict[str, Any]:
        """
        Get blues scale with blue notes.

        Blues scale: 1, b3, 4, #4/b5 (blue note), 5, b7, 1

        Returns:
            Dict with scale degrees and blue notes
        """

        return {
            'key': key,
            'scale_degrees': [1, 'b3', 4, 'b5', 5, 'b7', 1],
            'blue_notes': ['b3', 'b5', 'b7'],
            'description': 'Minor pentatonic + blue note (b5)',
            'usage': 'Works over all chords in blues progression'
        }

    def _transpose(self, root: str, semitones: int) -> str:
        """Transpose a note by semitones"""
        notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        if root not in notes:
            return root
        index = notes.index(root)
        return notes[(index + semitones) % 12]


# Global instance
blues_theory = BluesTheorySystem()
