"""
Enhanced chord service using musiclang_predict.

Provides structured chord generation with genre-specific patterns,
voice leading, and integration with hybrid music generator.
"""

import logging
from typing import List, Optional, Dict, Any
try:
    from musiclang_predict import MusicLangPredictor
    from musiclang import Score
    MUSICLANG_AVAILABLE = True
except ImportError:
    MUSICLANG_AVAILABLE = False
    Score = None

from app.schemas.music_generation import (
    ChordProgression,
    ChordVoicing,
    ChordPredictionRequest,
    ChordPredictionResponse,
    MusicGenre,
    MusicKey,
)

logger = logging.getLogger(__name__)


# Genre-specific chord progression templates
GENRE_TEMPLATES = {
    MusicGenre.GOSPEL: {
        "traditional": ["I", "IV", "I", "V", "I", "IV", "V", "I"],
        "contemporary": ["I", "V/vi", "vi", "IV", "I", "V", "vi", "IV"],
        "shout": ["I", "IV", "I", "V7", "IV", "I", "V7", "I"],
    },
    MusicGenre.JAZZ: {
        "ii_v_i": ["iim7", "V7", "Imaj7", "VImaj7"],
        "rhythm_changes": ["Imaj7", "VIm7", "iim7", "V7"],
        "modal": ["im7", "im7", "IVm7", "IVm7"],
    },
    MusicGenre.BLUES: {
        "standard": ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
        "minor": ["im", "im", "im", "im", "ivm", "ivm", "im", "im", "V7", "ivm", "im", "V7"],
    },
}


# MIDI note mapping for chord roots
NOTE_TO_MIDI = {
    "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
    "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
    "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71,
}


class ChordService:
    """
    Enhanced service for chord prediction and generation using MusicLang.

    Features:
    - Chord progression prediction with musiclang_predict
    - Genre-specific templates
    - Structured output with voicings and bass notes
    - Roman numeral analysis
    """

    def __init__(self):
        self.predictor = None
        if MUSICLANG_AVAILABLE:
            try:
                # Predictor loads models, might be heavy
                # loading 'musiclang/musiclang-v2' by default
                self.predictor = MusicLangPredictor('musiclang/musiclang-v2')
                logger.info("✅ MusicLang Predictor initialized.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize MusicLang Predictor: {e}")
                self.predictor = None
        else:
            logger.warning("⚠️ musiclang_predict not installed. Chord service disabled.")

    async def generate_progression(
        self,
        genre: MusicGenre,
        key: MusicKey,
        num_bars: int = 8,
        style: str = "traditional",
        custom_progression: Optional[List[str]] = None,
        complexity: int = 5,
    ) -> ChordProgression:
        """
        Generate a complete chord progression with voicings.

        Args:
            genre: Musical genre (gospel, jazz, blues, etc.)
            key: Key signature
            num_bars: Number of bars
            style: Style variation within genre
            custom_progression: Optional custom chord progression
            complexity: Harmonic complexity (1-10) affects voicing richness

        Returns:
            ChordProgression with full voicings and metadata
        """
        # Use custom progression or generate from template
        if custom_progression:
            chord_symbols = custom_progression
            roman_numerals = self._analyze_roman_numerals(custom_progression, key)
        else:
            roman_numerals = self._get_template_progression(genre, style, num_bars)
            chord_symbols = self._roman_to_chords(roman_numerals, key)

        # Generate voicings for each chord with complexity-aware variation
        voicings = self._generate_voicings(chord_symbols, key, genre, complexity)

        return ChordProgression(
            chords=chord_symbols,
            roman_numerals=roman_numerals,
            voicings=voicings,
            key=key,
            genre=genre,
            num_bars=num_bars,
            time_signature="4/4",
        )

    async def predict_next_chords(
        self,
        request: ChordPredictionRequest
    ) -> ChordPredictionResponse:
        """
        Predict next chords using musiclang_predict.

        Args:
            request: Prediction request with seed chords

        Returns:
            Predicted chords with full progression
        """
        if not self.predictor:
            logger.error("MusicLang predictor not available")
            # Fallback to template-based generation
            return ChordPredictionResponse(
                predicted_chords=request.seed_chords[:request.num_chords],
                full_progression=request.seed_chords,
                score_data={"error": "MusicLang not available"},
            )

        try:
            # MusicLang expects a string or Score
            prompt = " ".join(request.seed_chords)

            # Predict chords
            prediction = self.predictor.predict_chords(
                chords=prompt,
                nb_tokens=request.num_chords * 8  # ~8 tokens per chord
            )

            # Parse prediction (MusicLang returns Score object)
            predicted_chords = self._parse_musiclang_score(prediction)
            full_progression = request.seed_chords + predicted_chords

            return ChordPredictionResponse(
                predicted_chords=predicted_chords,
                full_progression=full_progression,
                score_data={"raw": str(prediction)},
            )

        except Exception as e:
            logger.error(f"Error predicting chords: {e}")
            # Fallback
            return ChordPredictionResponse(
                predicted_chords=request.seed_chords[:request.num_chords],
                full_progression=request.seed_chords,
                score_data={"error": str(e)},
            )

    def _get_template_progression(
        self,
        genre: MusicGenre,
        style: str,
        num_bars: int
    ) -> List[str]:
        """Get chord template for genre/style"""
        templates = GENRE_TEMPLATES.get(genre, {})
        template = templates.get(style, templates.get("traditional", ["I", "IV", "V", "I"]))

        # Repeat template to fill num_bars
        repetitions = (num_bars + len(template) - 1) // len(template)
        progression = (template * repetitions)[:num_bars]

        return progression

    def _roman_to_chords(self, roman_numerals: List[str], key: MusicKey) -> List[str]:
        """Convert Roman numerals to chord symbols"""
        # Simplified conversion (expand in production)
        key_root = key.value.replace('m', '')
        is_minor = 'm' in key.value

        chord_mapping = {
            "I": key_root, "IV": self._transpose(key_root, 5),
            "V": self._transpose(key_root, 7), "V7": self._transpose(key_root, 7) + "7",
            "vi": self._transpose(key_root, 9) + "m",
            "iim7": self._transpose(key_root, 2) + "m7",
            "Imaj7": key_root + "maj7",
        }

        return [chord_mapping.get(rn, key_root) for rn in roman_numerals]

    def _analyze_roman_numerals(self, chords: List[str], key: MusicKey) -> List[str]:
        """Analyze chord progression to extract Roman numerals (simplified)"""
        # Placeholder: return generic analysis
        return [f"Chord_{i}" for i in range(len(chords))]

    def _generate_voicings(
        self,
        chord_symbols: List[str],
        key: MusicKey,
        genre: MusicGenre,
        complexity: int = 5
    ) -> List[ChordVoicing]:
        """Generate specific voicings for chords with dynamic variation.
        
        Each chord gets a unique voicing based on:
        - Bar index (for voicing alternation)
        - Complexity level
        - Random octave/inversion selection
        """
        import random
        voicings = []

        for bar_index, chord_symbol in enumerate(chord_symbols):
            root_note = self._parse_root(chord_symbol)
            root_midi = NOTE_TO_MIDI.get(root_note, 60)
            
            # Random octave offset for variety (-1, 0, or +1 octave)
            octave_offset = random.choice([-12, 0, 0, 0])  # Bias toward normal register
            adjusted_root = root_midi + octave_offset

            # Generate voicing based on chord type, genre, and bar index
            notes = self._get_chord_notes(
                chord_symbol, 
                adjusted_root, 
                genre,
                complexity=complexity,
                bar_index=bar_index  # Now passed for voicing variation!
            )
            
            # Random inversion selection (0, 1, or 2)
            inversion = random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
            if inversion > 0 and len(notes) >= inversion:
                # Rotate notes to create inversion
                notes = notes[inversion:] + [n + 12 for n in notes[:inversion]]
            
            bass_note = min(notes) if notes else adjusted_root

            voicing = ChordVoicing(
                chord_symbol=chord_symbol,
                root=adjusted_root,
                notes=sorted(notes),  # Keep sorted for consistency
                inversion=inversion,
                bass_note=bass_note,
            )
            voicings.append(voicing)

        return voicings

    def _parse_root(self, chord_symbol: str) -> str:
        """Extract root note from chord symbol"""
        # Simple parser: assumes root is first 1-2 chars
        if len(chord_symbol) > 1 and chord_symbol[1] in ['#', 'b']:
            return chord_symbol[:2]
        return chord_symbol[0]

    def _get_chord_notes(
        self,
        chord_symbol: str,
        root_midi: int,
        genre: MusicGenre,
        complexity: int = 5,
        bar_index: int = 0
    ) -> List[int]:
        """Get MIDI notes for a chord voicing with complexity awareness
        
        Jazz and Gospel use sophisticated voicings with bar-based alternation.
        Other genres use simpler but still varied voicings.
        """
        import random
        
        # Jazz and Gospel both use sophisticated extended harmony
        if genre in (MusicGenre.JAZZ, MusicGenre.GOSPEL):
            return self._get_jazz_voicing(chord_symbol, root_midi, complexity, bar_index)
        
        # Neo-Soul also uses extended harmony
        if genre == MusicGenre.NEO_SOUL:
            return self._get_jazz_voicing(chord_symbol, root_midi, min(complexity, 6), bar_index)
            
        # Standard Triad Logic with randomization for other genres
        notes = [root_midi]  # Root

        # Add thirds and fifths (basic triad)
        if 'm' in chord_symbol.lower() and 'maj' not in chord_symbol.lower():
             # Check for dim/half-dim
             if 'dim' in chord_symbol or 'b5' in chord_symbol:
                  notes.append(root_midi + 3) # Minor 3rd
                  if 'dim' in chord_symbol and '7' not in chord_symbol:
                      notes.append(root_midi + 6) # Dim 5th
                  elif 'b5' in chord_symbol:
                      notes.append(root_midi + 6) # Flat 5th
             else:
                notes.append(root_midi + 3)  # Minor third
                notes.append(root_midi + 7)  # Perfect fifth
        else:
            # Major or Dominant
            notes.append(root_midi + 4)  # Major third
            notes.append(root_midi + 7)  # Perfect fifth

        # Add 7th if present
        if '7' in chord_symbol:
            if 'maj7' in chord_symbol.lower():
                notes.append(root_midi + 11)  # Major 7th
            elif 'dim7' in chord_symbol:
                 notes.append(root_midi + 9) # Diminished 7th (technically bb7 = 9)
            elif 'm7b5' in chord_symbol:
                 notes.append(root_midi + 10) # Minor 7th
            else:
                notes.append(root_midi + 10)  # Dominant 7th
        
        # Randomly add extensions for higher complexity
        if complexity >= 5 and random.random() > 0.5:
            notes.append(root_midi + 14)  # Add 9th
        if complexity >= 7 and random.random() > 0.6:
            notes.append(root_midi + 17)  # Add 11th
        if complexity >= 9 and random.random() > 0.7:
            notes.append(root_midi + 21)  # Add 13th

        return sorted(notes)

    def _get_jazz_voicing(
        self, 
        chord_symbol: str, 
        root_midi: int,
        complexity: int = 5,
        bar_index: int = 0
    ) -> List[int]:
        """
        Generate sophisticated Jazz voicings based on complexity and bar index.
        
        Complexity levels (Bill Evans inspired):
        - 1-3: Shell voicings (3rd + 7th only)
        - 4-6: Rootless A/B voicings (alternating per bar)
        - 7-10: Drop 2 / Quartal / Polychord voicings
        
        Bar index variation:
        - Alternates between voicing types to prevent static/robotic sound
        """
        import random
        
        # Determine chord quality
        is_minor = 'm' in chord_symbol and 'maj' not in chord_symbol.lower()
        is_dom = '7' in chord_symbol and 'maj' not in chord_symbol.lower() and 'm' not in chord_symbol
        is_maj = 'maj' in chord_symbol.lower()
        is_dim = 'dim' in chord_symbol
        is_m7b5 = 'm7b5' in chord_symbol
        
        # Calculate intervals
        third = 3 if (is_minor or is_dim or is_m7b5) else 4
        seventh = 11 if is_maj else (9 if is_dim else 10)
        ninth = 14  # Natural 9
        thirteenth = 21  # Natural 13 (9 + 12)
        
        # Handle alterations
        if 'b9' in chord_symbol: ninth = 13
        elif '#9' in chord_symbol: ninth = 15
        if 'b13' in chord_symbol: thirteenth = 20
        elif '#11' in chord_symbol: thirteenth = 18  # #11 instead of 13
        
        notes = []
        
        # === COMPLEXITY-BASED VOICING SELECTION ===
        
        if complexity <= 3:
            # SHELL VOICINGS: Simple, sparse
            # Just 3rd and 7th (no root - bass covers it)
            notes = [
                root_midi + third,
                root_midi + seventh
            ]
            # Add root in bass for solo piano context
            notes.insert(0, root_midi - 12)
            
        elif complexity <= 6:
            # ROOTLESS VOICINGS (Bill Evans Style)
            # Alternate between A and B forms based on bar index
            use_a_form = (bar_index % 2 == 0)
            
            if use_a_form:
                # A Form: 3rd on bottom (3-5-7-9)
                notes = [
                    root_midi + third,
                    root_midi + 7,  # 5th (optional, for fullness)
                    root_midi + seventh,
                    root_midi + ninth
                ]
            else:
                # B Form: 7th on bottom (7-9-3-13)
                notes = [
                    root_midi + seventh - 12,  # 7th dropped octave
                    root_midi + ninth - 12,    # 9th in lower register
                    root_midi + third,
                    root_midi + thirteenth - 12 if is_dom else root_midi + 7
                ]
                
            # Bass note for context
            notes.insert(0, root_midi - 12)
            
        else:
            # HIGH COMPLEXITY: Drop 2, Quartal, Extensions
            voicing_type = bar_index % 4
            
            if voicing_type == 0:
                # Drop 2 Voicing: Take close position, drop 2nd note from top
                close_pos = [third, 7, seventh, ninth + 12]  # Close position
                # Drop 2nd from top (the seventh) down an octave
                notes = [
                    root_midi - 12,  # Bass
                    root_midi + close_pos[0],
                    root_midi + close_pos[1],
                    root_midi + close_pos[2] - 12 if close_pos[2] > 7 else root_midi + close_pos[2],
                    root_midi + close_pos[3]
                ]
                
            elif voicing_type == 1:
                # Quartal Voicing: Stacked 4ths
                notes = [
                    root_midi - 12,  # Bass
                    root_midi + 5,   # 4th
                    root_midi + 10,  # b7 (2 4ths up)
                    root_midi + 15,  # 9th (another 4th)
                    root_midi + 20   # Another 4th
                ]
                
            elif voicing_type == 2:
                # Upper Structure Triad (UST)
                # maj triad a major 9th above root for dom7
                if is_dom:
                    ust_root = root_midi + 14  # 9th
                    notes = [
                        root_midi - 12,  # Bass
                        root_midi + third,
                        root_midi + seventh,
                        ust_root,        # Root of UST
                        ust_root + 4,    # 3rd of UST (= #11)
                        ust_root + 7     # 5th of UST (= 13)
                    ]
                else:
                    # Fallback to rootless
                    notes = [
                        root_midi - 12,
                        root_midi + third,
                        root_midi + seventh,
                        root_midi + ninth
                    ]
                    
            else:
                # Full extension stack with random variation
                base_notes = [
                    root_midi - 12,  # Bass
                    root_midi + third,
                    root_midi + seventh,
                    root_midi + ninth,
                ]
                # Add 13th sometimes
                if random.random() > 0.5 and (is_dom or is_maj):
                    base_notes.append(root_midi + thirteenth)
                # Sometimes add #11 instead of 5th
                if random.random() > 0.6 and is_dom:
                    base_notes.append(root_midi + 18)  # #11
                notes = base_notes
        
        # Ensure notes are within playable range and deduplicated
        notes = sorted(list(set(notes)))
        
        # Keep voicings in reasonable piano range (C2=36 to C7=96)
        notes = [n for n in notes if 36 <= n <= 96]
        
        return notes

    def _transpose(self, note: str, semitones: int) -> str:
        """Transpose a note by semitones"""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        if note not in notes:
            return note

        idx = notes.index(note)
        new_idx = (idx + semitones) % 12
        return notes[new_idx]

    def _parse_musiclang_score(self, score) -> List[str]:
        """Parse MusicLang Score object to extract chords"""
        try:
            # MusicLang Score has chord representation
            # This is a simplified extraction - expand based on actual API
            score_str = str(score)
            # Extract chord symbols from score representation
            # Placeholder: split and clean
            chords = [c.strip() for c in score_str.split() if c.strip()]
            return chords[:8]  # Limit to reasonable number
        except Exception as e:
            logger.error(f"Error parsing MusicLang score: {e}")
            return ["C", "F", "G", "C"]  # Fallback


# Global singleton instance
chord_service = ChordService()
