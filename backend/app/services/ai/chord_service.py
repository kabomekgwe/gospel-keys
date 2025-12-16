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
    ) -> ChordProgression:
        """
        Generate a complete chord progression with voicings.

        Args:
            genre: Musical genre (gospel, jazz, blues, etc.)
            key: Key signature
            num_bars: Number of bars
            style: Style variation within genre
            custom_progression: Optional custom chord progression

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

        # Generate voicings for each chord
        voicings = self._generate_voicings(chord_symbols, key, genre)

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
        genre: MusicGenre
    ) -> List[ChordVoicing]:
        """Generate specific voicings for chords"""
        voicings = []

        for chord_symbol in chord_symbols:
            root_note = self._parse_root(chord_symbol)
            root_midi = NOTE_TO_MIDI.get(root_note, 60)

            # Generate voicing based on chord type and genre
            notes = self._get_chord_notes(chord_symbol, root_midi, genre)
            bass_note = min(notes) if notes else root_midi

            voicing = ChordVoicing(
                chord_symbol=chord_symbol,
                root=root_midi,
                notes=notes,
                inversion=0,
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
        genre: MusicGenre
    ) -> List[int]:
        """Get MIDI notes for a chord voicing"""
        if genre == MusicGenre.JAZZ:
            return self._get_jazz_voicing(chord_symbol, root_midi)
            
        # Standard Triad Logic (Default)
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

        # Gospel-specific voicings: add 9ths
        if genre == MusicGenre.GOSPEL:
            notes.append(root_midi + 14)  # Add 9th (octave + 2)

        return sorted(notes)

    def _get_jazz_voicing(self, chord_symbol: str, root_midi: int) -> List[int]:
        """
        Generate sophisticated Jazz voicings (Shells + Extensions).
        Strategy:
        - Root is usually played by bass (simulated here as lowest note)
        - Piano LH: Shell (3rd + 7th)
        - Piano RH: Extensions (9th, 11th, 13th)
        """
        notes = [root_midi - 12] # Bass note (octave down)
        
        # Determine chord quality
        is_minor = 'm' in chord_symbol and 'maj' not in chord_symbol.lower()
        is_dom = '7' in chord_symbol and 'maj' not in chord_symbol.lower() and 'm' not in chord_symbol
        is_maj = 'maj' in chord_symbol.lower()
        is_dim = 'dim' in chord_symbol
        is_m7b5 = 'm7b5' in chord_symbol
        
        # Shells (3rd and 7th) in middle register (around C4=60)
        # We start with basic intervals relative to root
        third_interval = 4 # Major 3rd
        seventh_interval = 10 # Minor 7th
        
        if is_minor or is_dim or is_m7b5:
            third_interval = 3
        
        if is_maj:
            seventh_interval = 11
        elif is_dim:
            seventh_interval = 9 # Diminished 7th
        
        # Add Shells (moved to center register)
        # We simply add them relative to root for now, verify range later?
        # Actually simplest is to build the stack and then voicing analysis will invert/spread if needed.
        # But for "World Class" we want open voicings.
        
        notes.append(root_midi + third_interval)
        notes.append(root_midi + seventh_interval)
        
        # Extensions (9, 11, 13) for "Color"
        # 9th (Root + 14)
        if not is_dim: # Dim usually doesn't take 9 unless dim7(9)
            # Flatten 9 for Phrygian/Minor? Usually natural 9 for m7, maj7, dom7.
            # b9 for dom7b9.
            if 'b9' in chord_symbol:
                notes.append(root_midi + 13)
            elif '#9' in chord_symbol:
                notes.append(root_midi + 15)
            else:
                notes.append(root_midi + 14)
                
        # 13th (Root + 21) or #11?
        if is_dom or is_maj:
             # Add 13th (Major 6th + Octave) = 9 + 12 = 21? No. 
             # 6th is 9 semitones from root? No. 
             # M6 is 9 semitones. (C to A).
             # 13th is same pitch class as 6.
             notes.append(root_midi + 21) 
             
        # Altered Dominants (simplified)
        if 'alt' in chord_symbol:
             # #9, b13
             notes.append(root_midi + 15) # #9
             notes.append(root_midi + 20) # b13
             
        return sorted(list(set(notes))) # Remove logic duplications if any

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
