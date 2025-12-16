"""MIDI Generation Services

Specialized MIDI generators for different exercise types:
- Lick Generator: Jazz licks and melodic phrases
- Scale Generator: Scale patterns and arpeggios
- Generic Generator: AI-based interpretation of midi_prompts
"""

from .lick_generator import LickMIDIGenerator
from .scale_generator import ScaleMIDIGenerator
from .generic_generator import GenericMIDIGenerator

__all__ = [
    "LickMIDIGenerator",
    "ScaleMIDIGenerator",
    "GenericMIDIGenerator",
]
