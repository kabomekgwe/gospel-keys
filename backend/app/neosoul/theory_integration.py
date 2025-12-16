"""
Neo-Soul Theory Integration

Neo-soul specific applications of music theory:
- Extended chord voicings (9th, 11th, 13th)
- Negative harmony for unexpected progressions
- Modal mixture and borrowed chords
- Jazz-influenced harmony
- Smooth voice leading
- Rhythmic chord patterns
"""

import logging
from typing import Dict, List, Any, Tuple, Optional

from app.theory.chord_substitutions import (
    get_negative_harmony_progression,
    get_modal_interchange_chord
)
from app.theory.voice_leading_optimization import optimize_with_constraints
# Create alias for expected function name
optimize_voice_leading = optimize_with_constraints

logger = logging.getLogger(__name__)


class NeoSoulTheorySystem:
    """
    Neo-soul music theory specialization.

    Neo-soul harmony characteristics:
    - Rich extended chords (maj9, min11, dom13)
    - Jazz-influenced progressions
    - Negative harmony for alternative colors
    - Modal interchange (borrowed chords)
    - Smooth, sophisticated voice leading
    - Chromaticism
    """

    # Common neo-soul progressions
    NEOSOUL_PROGRESSIONS = {
        'classic': [
            ('Imaj7', 'maj9'),
            ('vi', 'm11'),
            ('ii', 'm9'),
            ('V', '13')
        ],
        'modern': [
            ('Imaj9', 'maj9'),
            ('bVII', 'maj7'),
            ('IV', 'maj9'),
            ('ii', 'm11')
        ],
        'jazzy': [
            ('iiim7', 'm7'),
            ('VI', '7b9'),
            ('iim7', 'm11'),
            ('V', '7#5')
        ]
    }

    def generate_neosoul_progression_with_theory(
        self,
        key: str = "C",
        style: str = "classic",
        use_negative_harmony: bool = False,
        modal_interchange: bool = True
    ) -> Dict[str, Any]:
        """
        Generate neo-soul progression with advanced theory.

        Args:
            key: Musical key
            style: Progression style
            use_negative_harmony: Apply negative harmony to part of progression
            modal_interchange: Use borrowed chords

        Returns:
            Dict with progression and theory analysis
        """

        # Get base progression
        base = self.NEOSOUL_PROGRESSIONS[style].copy()
        progression = self._resolve_roman_numerals(base, key)

        techniques_used = []

        # Apply modal interchange
        if modal_interchange:
            progression, interchange_info = self._apply_modal_mixture(
                progression, key
            )
            if interchange_info:
                techniques_used.append({
                    'name': 'Modal Interchange',
                    'details': interchange_info
                })

        # Apply negative harmony
        if use_negative_harmony:
            progression, negative_info = self._apply_negative_section(
                progression, key
            )
            if negative_info:
                techniques_used.append({
                    'name': 'Negative Harmony',
                    'details': negative_info
                })

        # Add extensions
        progression = self._ensure_rich_extensions(progression)

        return {
            'progression': progression,
            'key': key,
            'style': style,
            'techniques': techniques_used,
            'characteristics': {
                'extended_chords': True,
                'jazz_influence': 'high',
                'smoothness': 'sophisticated'
            }
        }

    def generate_neosoul_voicing(
        self,
        chord: Tuple[str, str],
        register: str = "mid"
    ) -> Dict[str, Any]:
        """
        Generate characteristic neo-soul voicing.

        Neo-soul voicings:
        - Often rootless (bass plays root)
        - Extensions in upper voices
        - Spread voicings (not too close)
        - Cluster chords for modern sound

        Args:
            chord: (root, quality)
            register: "low", "mid", "high"

        Returns:
            Dict with voicing and explanation
        """

        voicing_notes = []
        voicing_style = ""

        if 'maj9' in chord[1] or 'maj7' in chord[1]:
            # Rootless maj9: 3, 5, 7, 9
            voicing_notes = self._get_rootless_maj9(chord[0], register)
            voicing_style = "Rootless maj9 - classic neo-soul"

        elif 'm11' in chord[1] or 'm9' in chord[1]:
            # Minor 11: 3, 5, 7, 9, 11
            voicing_notes = self._get_minor11(chord[0], register)
            voicing_style = "Minor 11 - lush and sophisticated"

        elif '13' in chord[1]:
            # Dominant 13: 3, 7, 9, 13
            voicing_notes = self._get_dom13(chord[0], register)
            voicing_style = "Dominant 13 - jazzy resolution"

        else:
            # Default: Add 9th to any chord
            voicing_notes = self._get_basic_with_9th(chord, register)
            voicing_style = "Basic with 9th extension"

        return {
            'chord': chord,
            'voicing': voicing_notes,
            'style': voicing_style,
            'register': register,
            'is_rootless': True,
            'extensions': self._identify_extensions(chord[1])
        }

    def _apply_modal_mixture(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> Tuple[List[Tuple[str, str]], Optional[Dict]]:
        """Apply modal mixture - borrow from parallel minor"""

        # Neo-soul often borrows bVII (major) from minor
        # Example: In C major, borrow Bb major

        enhanced = []
        borrowed = []

        for chord in progression:
            # Example: Replace IV with bVII for neo-soul color
            if chord[0] == self._transpose(key, 5):  # IV chord
                # Borrow bVII instead
                bVII_root = self._transpose(key, 10)
                enhanced.append((bVII_root, 'maj7'))
                borrowed.append({
                    'original': chord,
                    'borrowed': (bVII_root, 'maj7'),
                    'from': 'parallel minor'
                })
            else:
                enhanced.append(chord)

        if borrowed:
            return enhanced, {'chords_borrowed': borrowed}

        return progression, None

    def _apply_negative_section(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> Tuple[List[Tuple[str, str]], Optional[Dict]]:
        """Apply negative harmony to a section"""

        if len(progression) < 4:
            return progression, None

        # Apply negative harmony to last 2 chords
        original_ending = progression[-2:]
        negative_ending = get_negative_harmony_progression(
            original_ending, key, "major"
        )

        enhanced = progression[:-2] + negative_ending

        return enhanced, {
            'original_section': original_ending,
            'negative_section': negative_ending,
            'position': 'ending'
        }

    def _ensure_rich_extensions(
        self,
        progression: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """Ensure all chords have rich extensions"""

        enhanced = []

        for root, quality in progression:
            # Upgrade to extended chords
            if quality == 'maj7':
                enhanced.append((root, 'maj9'))
            elif quality == 'm7':
                enhanced.append((root, 'm11'))
            elif quality == '7':
                enhanced.append((root, '13'))
            else:
                enhanced.append((root, quality))

        return enhanced

    def _get_rootless_maj9(self, root: str, register: str) -> List[int]:
        """Get rootless maj9 voicing"""
        root_midi = self._note_to_midi(root)
        offset = {'low': -12, 'mid': 0, 'high': 12}.get(register, 0)

        # 3, 5, 7, 9
        return [
            root_midi + 4 + offset,   # Major 3rd
            root_midi + 7 + offset,   # Perfect 5th
            root_midi + 11 + offset,  # Major 7th
            root_midi + 14 + offset   # Major 9th
        ]

    def _get_minor11(self, root: str, register: str) -> List[int]:
        """Get minor 11 voicing"""
        root_midi = self._note_to_midi(root)
        offset = {'low': -12, 'mid': 0, 'high': 12}.get(register, 0)

        # 3, 7, 9, 11
        return [
            root_midi + 3 + offset,   # Minor 3rd
            root_midi + 10 + offset,  # Minor 7th
            root_midi + 14 + offset,  # Major 9th
            root_midi + 17 + offset   # Perfect 11th
        ]

    def _get_dom13(self, root: str, register: str) -> List[int]:
        """Get dominant 13 voicing"""
        root_midi = self._note_to_midi(root)
        offset = {'low': -12, 'mid': 0, 'high': 12}.get(register, 0)

        # 3, 7, 9, 13
        return [
            root_midi + 4 + offset,   # Major 3rd
            root_midi + 10 + offset,  # Minor 7th
            root_midi + 14 + offset,  # Major 9th
            root_midi + 21 + offset   # Major 13th
        ]

    def _get_basic_with_9th(
        self,
        chord: Tuple[str, str],
        register: str
    ) -> List[int]:
        """Add 9th to basic chord"""
        root_midi = self._note_to_midi(chord[0])
        offset = {'low': -12, 'mid': 0, 'high': 12}.get(register, 0)

        if 'm' in chord[1]:
            # Minor with 9th
            return [
                root_midi + 3 + offset,
                root_midi + 7 + offset,
                root_midi + 14 + offset
            ]
        else:
            # Major with 9th
            return [
                root_midi + 4 + offset,
                root_midi + 7 + offset,
                root_midi + 14 + offset
            ]

    def _identify_extensions(self, quality: str) -> List[str]:
        """Identify extensions in chord quality"""
        extensions = []
        if '9' in quality:
            extensions.append('9th')
        if '11' in quality:
            extensions.append('11th')
        if '13' in quality:
            extensions.append('13th')
        return extensions

    def _note_to_midi(self, note: str) -> int:
        """Convert note name to MIDI number (middle C = 60)"""
        notes = {'C': 60, 'Db': 61, 'D': 62, 'Eb': 63, 'E': 64, 'F': 65,
                'F#': 66, 'G': 67, 'Ab': 68, 'A': 69, 'Bb': 70, 'B': 71}
        return notes.get(note, 60)

    def _transpose(self, root: str, semitones: int) -> str:
        """Transpose note by semitones"""
        notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        if root not in notes:
            return root
        index = notes.index(root)
        return notes[(index + semitones) % 12]

    def _resolve_roman_numerals(
        self,
        progression: List[Tuple[str, str]],
        key: str
    ) -> List[Tuple[str, str]]:
        """Convert roman numerals to actual chords"""
        # Simplified mapping for common progressions
        mapping = {
            'I': key,
            'ii': self._transpose(key, 2),
            'iii': self._transpose(key, 4),
            'IV': self._transpose(key, 5),
            'V': self._transpose(key, 7),
            'vi': self._transpose(key, 9),
            'bVII': self._transpose(key, 10),
            'VI': self._transpose(key, 9)
        }

        # Handle variations
        for numeral in ['maj7', 'maj9', 'm7', 'm9', 'm11', 'Imaj7', 'Imaj9', 'iim7', 'iiim7']:
            base = numeral.replace('maj7', '').replace('maj9', '').replace('m7', '').replace('m9', '').replace('m11', '')
            if base in mapping:
                mapping[numeral] = mapping[base]

        resolved = []
        for numeral, quality in progression:
            root = mapping.get(numeral, key)
            resolved.append((root, quality))

        return resolved


# Global instance
neosoul_theory = NeoSoulTheorySystem()
