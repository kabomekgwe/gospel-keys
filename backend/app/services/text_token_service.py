"""
Text Token Service - Human-Readable Music Token System

Converts between MidiTok REMI integer tokens and human-readable text tokens
for fine-tuning Qwen 2.5-14B on music generation.

Text tokens enable better transfer learning and are easier to debug than
integer tokens.

Example:
    MidiTok: [1, 234, 567, 12, 890]
    Text: "BAR_START NOTE_ON_60 DUR_QUARTER VEL_MF CHORD_Cmaj7"
"""

import logging
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class TextTokenVocab:
    """Complete text token vocabulary for music generation"""

    # Structure tokens (10)
    STRUCTURE = [
        "SONG_START", "SONG_END",
        "SECTION_INTRO", "SECTION_VERSE", "SECTION_CHORUS",
        "SECTION_BRIDGE", "SECTION_OUTRO",
        "REPEAT_START", "REPEAT_END", "BAR_START"
    ]

    # Timing tokens (16) - 4/4 time with subdivisions
    TIMING = [
        "BEAT_0", "BEAT_1", "BEAT_2", "BEAT_3",
        "BEAT_0.5", "BEAT_1.5", "BEAT_2.5", "BEAT_3.5",
        "BEAT_0.25", "BEAT_0.75", "BEAT_1.25", "BEAT_1.75",
        "BEAT_2.25", "BEAT_2.75", "BEAT_3.25", "BEAT_3.75",
    ]

    # Note events (176) - Piano range A0 to C8
    NOTES_ON = [f"NOTE_ON_{pitch}" for pitch in range(21, 109)]
    NOTES_OFF = [f"NOTE_OFF_{pitch}" for pitch in range(21, 109)]
    NOTES = NOTES_ON + NOTES_OFF

    # Duration tokens (24)
    DURATIONS = [
        "DUR_WHOLE", "DUR_HALF", "DUR_QUARTER", "DUR_EIGHTH", "DUR_SIXTEENTH",
        "DUR_THIRTYSECOND",
        "DUR_DOTTED_WHOLE", "DUR_DOTTED_HALF", "DUR_DOTTED_QUARTER",
        "DUR_DOTTED_EIGHTH", "DUR_DOTTED_SIXTEENTH",
        "DUR_TRIPLET_WHOLE", "DUR_TRIPLET_HALF", "DUR_TRIPLET_QUARTER",
        "DUR_TRIPLET_EIGHTH", "DUR_TRIPLET_SIXTEENTH",
        "DUR_WHOLE_TIED", "DUR_HALF_TIED", "DUR_QUARTER_TIED",
        "DUR_EIGHTH_TIED", "DUR_SIXTEENTH_TIED",
        "DUR_SUSTAIN", "DUR_RELEASE", "DUR_HOLD"
    ]

    # Velocity/Dynamics (16)
    VELOCITIES = [
        "VEL_SILENT",     # 0
        "VEL_PPP",        # 20
        "VEL_PP",         # 35
        "VEL_P",          # 50
        "VEL_MP",         # 65
        "VEL_MF",         # 80 (default)
        "VEL_F",          # 95
        "VEL_FF",         # 110
        "VEL_FFF",        # 125
        "VEL_CRESC",      # Crescendo
        "VEL_DECRESC",    # Decrescendo
        "VEL_ACCENT",     # Accent
        "VEL_SOFT_ACCENT", # Soft accent
        "VEL_STACCATO",   # Short
        "VEL_TENUTO",     # Full value
        "VEL_MARCATO"     # Emphasized
    ]

    # Build chord tokens programmatically
    CHORD_ROOTS = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    CHORD_QUALITIES = [
        "maj", "min", "dim", "aug",
        "maj7", "min7", "dom7", "dim7", "halfdim7",
        "maj9", "min9", "dom9",
        "maj11", "min11", "dom11",
        "maj13", "min13", "dom13",
        "sus2", "sus4",
        "6", "min6",
        "add9", "minadd9"
    ]

    # Generate all chord combinations
    CHORDS = [
        f"CHORD_{root}{quality}"
        for root in CHORD_ROOTS
        for quality in CHORD_QUALITIES
    ]

    # Articulation (12)
    ARTICULATION = [
        "PEDAL_ON", "PEDAL_OFF", "PEDAL_HALF",
        "STACCATO", "LEGATO", "ACCENT",
        "GRACE_NOTE", "GRACE_BEFORE", "GRACE_AFTER",
        "TRILL", "ARPEGGIO", "FERMATA"
    ]

    # Special MidiTok tokens
    SPECIAL = [
        "PAD", "BOS", "EOS", "MASK", "UNKNOWN"
    ]

    @classmethod
    def get_full_vocabulary(cls) -> List[str]:
        """Get complete text token vocabulary"""
        return (
            cls.STRUCTURE +
            cls.TIMING +
            cls.NOTES +
            cls.DURATIONS +
            cls.VELOCITIES +
            cls.CHORDS +
            cls.ARTICULATION +
            cls.SPECIAL
        )

    @classmethod
    def vocab_size(cls) -> int:
        """Get vocabulary size"""
        return len(cls.get_full_vocabulary())


class TextTokenService:
    """
    Service for converting between MidiTok REMI tokens and text tokens.

    Features:
    - Bidirectional conversion (REMI ↔ Text)
    - Human-readable token names
    - Round-trip validation
    - Vocabulary management
    """

    def __init__(self):
        self.vocab = TextTokenVocab()

        # Build bidirectional mappings
        self._build_mappings()

        logger.info(f"✅ Text token service initialized")
        logger.info(f"   Vocabulary size: {self.vocab.vocab_size()} tokens")

    def _build_mappings(self):
        """Build REMI ↔ Text token mappings"""

        # Get MidiTok vocabulary (from existing midi_service)
        try:
            from app.services.ai.midi_service import midi_service
            self.midi_tokenizer = midi_service.tokenizer
            remi_vocab_size = self.midi_tokenizer.vocab_size

            logger.info(f"📊 MidiTok REMI vocabulary: {remi_vocab_size} tokens")
        except Exception as e:
            logger.warning(f"Could not load MidiTok tokenizer: {e}")
            self.midi_tokenizer = None
            remi_vocab_size = 2048  # Default estimate

        # Create REMI → Text mapping
        self.remi_to_text: Dict[int, str] = {}
        self.text_to_remi: Dict[str, int] = {}

        # Map structure tokens (0-9)
        for i, token in enumerate(self.vocab.STRUCTURE):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map timing tokens (10-25)
        for i, token in enumerate(self.vocab.TIMING, start=10):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map note ON tokens (30-117)
        for i, token in enumerate(self.vocab.NOTES_ON, start=30):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map note OFF tokens (120-207)
        for i, token in enumerate(self.vocab.NOTES_OFF, start=120):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map duration tokens (210-233)
        for i, token in enumerate(self.vocab.DURATIONS, start=210):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map velocity tokens (240-255)
        for i, token in enumerate(self.vocab.VELOCITIES, start=240):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map chord tokens (300-599)
        for i, token in enumerate(self.vocab.CHORDS, start=300):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map articulation tokens (600-611)
        for i, token in enumerate(self.vocab.ARTICULATION, start=600):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        # Map special tokens (1000+)
        for i, token in enumerate(self.vocab.SPECIAL, start=1000):
            self.remi_to_text[i] = token
            self.text_to_remi[token] = i

        logger.info(f"✅ Built {len(self.remi_to_text)} token mappings")

    def remi_to_text_tokens(self, remi_tokens: List[int]) -> List[str]:
        """
        Convert MidiTok REMI integer tokens to text tokens.

        Args:
            remi_tokens: List of REMI integer tokens

        Returns:
            List of text tokens

        Example:
            >>> service.remi_to_text_tokens([0, 30, 210, 240])
            ["SONG_START", "NOTE_ON_21", "DUR_WHOLE", "VEL_SILENT"]
        """
        text_tokens = []

        for remi_token in remi_tokens:
            if remi_token in self.remi_to_text:
                text_tokens.append(self.remi_to_text[remi_token])
            else:
                # Unknown token - create placeholder
                text_tokens.append(f"UNKNOWN_{remi_token}")
                logger.warning(f"Unknown REMI token: {remi_token}")

        return text_tokens

    def text_to_remi_tokens(self, text_tokens: List[str]) -> List[int]:
        """
        Convert text tokens back to MidiTok REMI integer tokens.

        Args:
            text_tokens: List of text tokens

        Returns:
            List of REMI integer tokens

        Example:
            >>> service.text_to_remi_tokens(["SONG_START", "NOTE_ON_21"])
            [0, 30]
        """
        remi_tokens = []

        for text_token in text_tokens:
            if text_token in self.text_to_remi:
                remi_tokens.append(self.text_to_remi[text_token])
            elif text_token.startswith("UNKNOWN_"):
                # Handle unknown tokens
                try:
                    token_id = int(text_token.split("_")[1])
                    remi_tokens.append(token_id)
                except:
                    logger.error(f"Cannot parse unknown token: {text_token}")
                    remi_tokens.append(1000)  # PAD token
            else:
                logger.warning(f"Unknown text token: {text_token}")
                remi_tokens.append(1000)  # PAD token

        return remi_tokens

    def tokens_to_string(self, text_tokens: List[str]) -> str:
        """
        Convert text token list to space-separated string.

        Args:
            text_tokens: List of text tokens

        Returns:
            Space-separated token string

        Example:
            >>> service.tokens_to_string(["SONG_START", "NOTE_ON_60"])
            "SONG_START NOTE_ON_60"
        """
        return " ".join(text_tokens)

    def string_to_tokens(self, token_string: str) -> List[str]:
        """
        Parse space-separated token string to list.

        Args:
            token_string: Space-separated tokens

        Returns:
            List of text tokens

        Example:
            >>> service.string_to_tokens("SONG_START NOTE_ON_60")
            ["SONG_START", "NOTE_ON_60"]
        """
        return token_string.strip().split()

    def validate_round_trip(self, remi_tokens: List[int]) -> bool:
        """
        Validate round-trip conversion (REMI → Text → REMI).

        Args:
            remi_tokens: Original REMI tokens

        Returns:
            True if round-trip preserves tokens

        Example:
            >>> original = [0, 30, 210]
            >>> service.validate_round_trip(original)
            True
        """
        try:
            # REMI → Text
            text_tokens = self.remi_to_text_tokens(remi_tokens)

            # Text → REMI
            reconstructed = self.text_to_remi_tokens(text_tokens)

            # Compare
            if remi_tokens == reconstructed:
                return True
            else:
                logger.error(f"Round-trip failed!")
                logger.error(f"  Original: {remi_tokens[:10]}...")
                logger.error(f"  Reconstructed: {reconstructed[:10]}...")
                return False

        except Exception as e:
            logger.error(f"Round-trip validation error: {e}")
            return False

    def get_vocab_info(self) -> Dict[str, int]:
        """Get vocabulary statistics"""
        return {
            "total_tokens": self.vocab.vocab_size(),
            "structure": len(self.vocab.STRUCTURE),
            "timing": len(self.vocab.TIMING),
            "notes": len(self.vocab.NOTES),
            "durations": len(self.vocab.DURATIONS),
            "velocities": len(self.vocab.VELOCITIES),
            "chords": len(self.vocab.CHORDS),
            "articulation": len(self.vocab.ARTICULATION),
            "special": len(self.vocab.SPECIAL),
        }


# Global singleton instance
text_token_service = TextTokenService()
