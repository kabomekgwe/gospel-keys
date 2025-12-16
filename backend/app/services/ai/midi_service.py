
import logging
from typing import List, Union, Optional
from pathlib import Path
from miditok import REMI, TokenizerConfig
from miditok import TokSequence

logger = logging.getLogger(__name__)

class MidiService:
    """
    Service for MIDI tokenization and manipulation using MidiTok.
    """
    
    def __init__(self):
        # Configure REMI tokenizer - good for pop/gospel/piano
        config = TokenizerConfig(
            pitch_range=(21, 108),  # Piano range
            beat_res={(0, 4): 8, (4, 12): 4},  # Resolution
            num_velocities=32,
            special_tokens=["PAD", "BOS", "EOS", "MASK"]
        )
        self.tokenizer = REMI(config)

    def tokenize_midi_file(self, midi_path: str) -> List[int]:
        """
        Reads a MIDI file and converts it to a sequence of tokens.
        """
        try:
            if not Path(midi_path).exists():
                raise FileNotFoundError(f"MIDI file not found: {midi_path}")
            
            # MidiTok loads the midi file directly
            tokens = self.tokenizer(midi_path)
            
            # MidiTok returns a list of TokenSequence objects (one per track usually)
            # For simplicity, we'll take the first track if multiple
            if isinstance(tokens, list) and len(tokens) > 0:
                # tokens[0] is the first track
                return tokens[0].ids
            return []
        except Exception as e:
            logger.error(f"Error tokenizing MIDI: {e}")
            raise e

    def detokenize_to_midi(self, tokens: List[int], output_path: str) -> str:
        """
        Converts a sequence of tokens back to a MIDI file.
        """
        try:
            generated_midi = self.tokenizer(tokens)
            generated_midi.dump(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Error creating MIDI from tokens: {e}")
            raise e

midi_service = MidiService()
