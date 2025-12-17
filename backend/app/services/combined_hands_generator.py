"""Combined Hands Generator Service

Generates musically coherent two-hand piano arrangements by combining
left and right hand patterns with proper voice leading and timing alignment.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple
from pathlib import Path

import pretty_midi

from app.core.config import settings
from app.gospel import Note, ChordContext, HandPattern, Arrangement

logger = logging.getLogger(__name__)

# Import pattern generators
from app.neosoul.patterns.left_hand import (
    NEOSOUL_LEFT_HAND_PATTERNS,
    generate_neosoul_left_hand_pattern,
)
from app.neosoul.patterns.right_hand import (
    NEOSOUL_RIGHT_HAND_PATTERNS,
    generate_neosoul_right_hand_pattern,
)

Style = Literal["neosoul", "gospel", "jazz"]
Hand = Literal["left", "right", "both"]


@dataclass
class HandsPracticeConfig:
    """Configuration for hands practice session."""
    chords: List[str]
    key: str = "C"
    tempo: int = 80
    time_signature: Tuple[int, int] = (4, 4)
    left_pattern: str = "syncopated_groove"
    right_pattern: str = "extended_chord_voicing"
    style: Style = "neosoul"
    active_hand: Hand = "both"
    bars_per_chord: int = 1
    complexity: int = 5


class CombinedHandsGenerator:
    """
    Generate complete two-hand piano arrangements.
    
    Combines left and right hand patterns with:
    - Proper voice leading between chords
    - Time alignment and synchronization
    - Hand-specific velocity curves
    - Style-appropriate pattern selection
    """
    
    def __init__(self):
        self.output_dir = Path(settings.OUTPUTS_DIR) / "hands"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Available patterns by style
        self.patterns = {
            "neosoul": {
                "left": list(NEOSOUL_LEFT_HAND_PATTERNS.keys()),
                "right": list(NEOSOUL_RIGHT_HAND_PATTERNS.keys()),
            },
            "gospel": {
                "left": ["stride_bass", "walking_bass", "block_chords"],
                "right": ["gospel_run", "block_voicing", "tremolo"],
            },
            "jazz": {
                "left": ["shell_voicing", "walking_bass", "comping"],
                "right": ["chord_melody", "block_voicing", "bebop_line"],
            },
        }
    
    def get_available_patterns(self, style: Style) -> Dict[str, List[str]]:
        """Get available left and right hand patterns for a style."""
        return self.patterns.get(style, self.patterns["neosoul"])
    
    def generate_arrangement(
        self,
        config: HandsPracticeConfig,
    ) -> Arrangement:
        """
        Generate a complete two-hand arrangement.
        
        Args:
            config: Practice configuration with chords and patterns
        
        Returns:
            Arrangement with left and right hand notes
        """
        left_notes: List[Note] = []
        right_notes: List[Note] = []
        
        beats_per_bar = config.time_signature[0]
        beats_per_chord = beats_per_bar * config.bars_per_chord
        
        for i, chord in enumerate(config.chords):
            # Create context for this chord
            context = ChordContext(
                chord=chord,
                key=config.key,
                position=i,
                tempo=config.tempo,
                time_signature=config.time_signature,
                previous_chord=config.chords[i - 1] if i > 0 else None,
                next_chord=config.chords[i + 1] if i < len(config.chords) - 1 else None,
            )
            
            bar_start_time = i * beats_per_chord
            
            # Generate left hand pattern
            if config.active_hand in ("left", "both"):
                left_pattern = self._generate_hand_pattern(
                    context, 
                    config.left_pattern, 
                    config.style, 
                    "left",
                    config.complexity
                )
                
                for note in left_pattern.notes:
                    # Offset note time to bar position
                    adjusted_note = Note(
                        pitch=note.pitch,
                        time=bar_start_time + note.time,
                        duration=note.duration,
                        velocity=note.velocity,
                        hand="left",
                    )
                    left_notes.append(adjusted_note)
            
            # Generate right hand pattern
            if config.active_hand in ("right", "both"):
                right_pattern = self._generate_hand_pattern(
                    context,
                    config.right_pattern,
                    config.style,
                    "right",
                    config.complexity
                )
                
                for note in right_pattern.notes:
                    adjusted_note = Note(
                        pitch=note.pitch,
                        time=bar_start_time + note.time,
                        duration=note.duration,
                        velocity=note.velocity,
                        hand="right",
                    )
                    right_notes.append(adjusted_note)
        
        return Arrangement(
            left_hand_notes=left_notes,
            right_hand_notes=right_notes,
            tempo=config.tempo,
            time_signature=config.time_signature,
            key=config.key,
            total_bars=len(config.chords) * config.bars_per_chord,
            application=f"{config.style}_practice",
        )
    
    def _generate_hand_pattern(
        self,
        context: ChordContext,
        pattern_name: str,
        style: Style,
        hand: str,
        complexity: int = 5,
    ) -> HandPattern:
        """Generate a specific hand pattern."""
        try:
            if style == "neosoul":
                if hand == "left":
                    return generate_neosoul_left_hand_pattern(pattern_name, context, complexity=complexity)
                else:
                    return generate_neosoul_right_hand_pattern(pattern_name, context, complexity=complexity)
            else:
                # Fallback to neosoul patterns for other styles
                # (Gospel and Jazz patterns can be added similarly)
                if hand == "left":
                    return generate_neosoul_left_hand_pattern(
                        "syncopated_groove", context, complexity=complexity
                    )
                else:
                    return generate_neosoul_right_hand_pattern(
                        "extended_chord_voicing", context, complexity=complexity
                    )
        except Exception as e:
            logger.warning(f"Pattern generation failed: {e}, using fallback")
            return self._fallback_pattern(context, hand)
    
    def _fallback_pattern(self, context: ChordContext, hand: str) -> HandPattern:
        """Generate a simple fallback pattern."""
        from app.neosoul.patterns.left_hand import get_root_note_midi
        from app.neosoul.patterns.right_hand import get_root_midi
        
        notes = []
        
        if hand == "left":
            # Simple bass note pattern
            root_midi = get_root_note_midi(context.chord[0], octave=2)
            notes.append(Note(
                pitch=root_midi,
                time=0.0,
                duration=4.0,
                velocity=80,
                hand="left",
            ))
        else:
            # Simple chord pattern
            root_midi = get_root_midi(context.chord[0], octave=4)
            for interval in [0, 4, 7]:  # Major triad
                notes.append(Note(
                    pitch=root_midi + interval,
                    time=0.0,
                    duration=4.0,
                    velocity=70,
                    hand="right",
                ))
        
        return HandPattern(
            name="fallback",
            notes=notes,
            difficulty="beginner",
            tempo_range=(60, 120),
            characteristics=["fallback"],
        )
    
    def arrangement_to_midi(
        self,
        arrangement: Arrangement,
        output_id: str,
        hand_filter: Optional[Hand] = None,
    ) -> Path:
        """
        Export arrangement to MIDI file.
        
        Args:
            arrangement: The arrangement to export
            output_id: Unique identifier for the file
            hand_filter: Optional filter for left/right/both hands
        
        Returns:
            Path to the generated MIDI file
        """
        midi = pretty_midi.PrettyMIDI(
            initial_tempo=arrangement.tempo
        )
        
        # Create separate tracks for each hand for easier audio separation
        left_track = pretty_midi.Instrument(program=0, name="Left Hand")
        right_track = pretty_midi.Instrument(program=0, name="Right Hand")
        
        seconds_per_beat = 60.0 / arrangement.tempo
        
        # Add left hand notes
        if hand_filter in (None, "left", "both"):
            for note in arrangement.left_hand_notes:
                midi_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.time * seconds_per_beat,
                    end=(note.time + note.duration) * seconds_per_beat,
                )
                left_track.notes.append(midi_note)
        
        # Add right hand notes
        if hand_filter in (None, "right", "both"):
            for note in arrangement.right_hand_notes:
                midi_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.time * seconds_per_beat,
                    end=(note.time + note.duration) * seconds_per_beat,
                )
                right_track.notes.append(midi_note)
        
        midi.instruments.append(left_track)
        midi.instruments.append(right_track)
        
        output_path = self.output_dir / f"{output_id}_hands.mid"
        midi.write(str(output_path))
        
        logger.info(f"Generated hands MIDI: {output_path}")
        return output_path
    
    def split_notes_by_hand(
        self,
        notes: List[dict],
        split_point: int = 60,  # Middle C
    ) -> Tuple[List[dict], List[dict]]:
        """
        Split a list of notes into left and right hand based on pitch.
        
        Simple heuristic: notes below split_point = left hand.
        
        Args:
            notes: List of note dictionaries with 'pitch' key
            split_point: MIDI note number for hand split (default: middle C)
        
        Returns:
            Tuple of (left_hand_notes, right_hand_notes)
        """
        left_notes = []
        right_notes = []
        
        for note in notes:
            pitch = note.get("pitch", 60)
            note_copy = dict(note)
            
            if pitch < split_point:
                note_copy["hand"] = "left"
                left_notes.append(note_copy)
            else:
                note_copy["hand"] = "right"
                right_notes.append(note_copy)
        
        return left_notes, right_notes


# Singleton instance
combined_hands_generator = CombinedHandsGenerator()
