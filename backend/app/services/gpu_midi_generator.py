"""GPU-Accelerated MIDI Generator Service

Leverage MLX for fast matrix operations on Apple Silicon for neo-soul 
pattern generation and chord voicing computation.
"""

import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional

import numpy as np
import pretty_midi

from app.core.config import settings
from app.core.gpu import get_device, is_gpu_available

logger = logging.getLogger(__name__)

# Optional MLX import (Apple Silicon optimized)
try:
    import mlx.core as mx
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    logger.info("MLX not available. Using numpy fallback for matrix operations.")

VoicingStyle = Literal["closed", "open", "drop2", "drop3", "quartet", "shell"]
PatternStyle = Literal["neosoul", "gospel", "jazz", "rb"]


@dataclass
class GeneratedNote:
    """A single generated note."""
    pitch: int
    start_time: float
    duration: float
    velocity: int = 80


class GPUMIDIGenerator:
    """
    GPU-accelerated MIDI generation using MLX for Apple Silicon.
    
    Provides fast chord voicing computation and pattern generation
    optimized for neo-soul and gospel styles.
    """
    
    def __init__(self):
        self.output_dir = Path(settings.OUTPUTS_DIR) / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Note mappings
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Chord templates (intervals from root)
        self.chord_templates = {
            'maj7': [0, 4, 7, 11],
            'm7': [0, 3, 7, 10],
            '7': [0, 4, 7, 10],
            'dim7': [0, 3, 6, 9],
            'm7b5': [0, 3, 6, 10],
            'maj9': [0, 4, 7, 11, 14],
            'm9': [0, 3, 7, 10, 14],
            '9': [0, 4, 7, 10, 14],
            '13': [0, 4, 7, 10, 14, 21],
            'maj': [0, 4, 7],
            'min': [0, 3, 7],
            'aug': [0, 4, 8],
            'sus4': [0, 5, 7],
            'sus2': [0, 2, 7],
        }
        
        # Neo-soul extensions and alterations
        self.neosoul_extensions = {
            'add9': 14,
            'add11': 17,
            'add13': 21,
            '#11': 18,
            'b9': 13,
            '#9': 15,
        }
        
    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI number (e.g., 'C4' -> 60)."""
        # Extract note and octave
        if len(note_name) == 2:
            note, octave = note_name[0], int(note_name[1])
        elif len(note_name) == 3:
            note, octave = note_name[0:2], int(note_name[2])
        else:
            raise ValueError(f"Invalid note name: {note_name}")
        
        # Get pitch class
        try:
            pitch_class = self.note_names.index(note)
        except ValueError:
            # Try flats
            flat_to_sharp = {'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#', 
                           'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B'}
            if note in flat_to_sharp:
                pitch_class = self.note_names.index(flat_to_sharp[note])
            else:
                raise ValueError(f"Unknown note: {note}")
        
        return pitch_class + (octave + 1) * 12
    
    def _parse_chord(self, chord_symbol: str) -> tuple[int, str]:
        """Parse chord symbol to get root and quality."""
        # Find root
        if len(chord_symbol) > 1 and chord_symbol[1] in ['#', 'b']:
            root = chord_symbol[:2]
            quality = chord_symbol[2:] or 'maj'
        else:
            root = chord_symbol[0]
            quality = chord_symbol[1:] or 'maj'
        
        # Normalize quality
        quality_map = {
            '': 'maj', 'M7': 'maj7', 'M9': 'maj9', 'Maj7': 'maj7',
            'min7': 'm7', 'minor7': 'm7', '-7': 'm7',
            'dom7': '7', 'dominant7': '7',
        }
        quality = quality_map.get(quality, quality)
        
        try:
            root_pc = self.note_names.index(root)
        except ValueError:
            flat_to_sharp = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
            root = flat_to_sharp.get(root, root)
            root_pc = self.note_names.index(root)
        
        return root_pc, quality
    
    def generate_voicing(
        self,
        chord: str,
        style: VoicingStyle = "open",
        root_octave: int = 3,
        add_extensions: bool = True,
    ) -> List[GeneratedNote]:
        """
        Generate a chord voicing with GPU-accelerated computations.
        
        Args:
            chord: Chord symbol (e.g., "Dm7", "Cmaj9")
            style: Voicing style
            root_octave: Octave for the root note
            add_extensions: Whether to add neo-soul extensions
        
        Returns:
            List of GeneratedNote objects
        """
        root_pc, quality = self._parse_chord(chord)
        
        # Get base intervals
        intervals = self.chord_templates.get(quality, self.chord_templates['maj7'])
        
        # Compute voicing using MLX if available (batch matrix ops)
        if MLX_AVAILABLE:
            notes = self._compute_voicing_mlx(root_pc, intervals, style, root_octave)
        else:
            notes = self._compute_voicing_numpy(root_pc, intervals, style, root_octave)
        
        # Add neo-soul extensions
        if add_extensions and quality in ['maj7', 'm7', '7', '9']:
            ext_note = self._add_neosoul_extension(root_pc, quality, root_octave)
            if ext_note:
                notes.append(ext_note)
        
        return notes
    
    def _compute_voicing_mlx(
        self,
        root_pc: int,
        intervals: List[int],
        style: VoicingStyle,
        root_octave: int,
    ) -> List[GeneratedNote]:
        """Compute voicing using MLX tensor operations."""
        # Create interval array
        intervals_mx = mx.array(intervals, dtype=mx.int32)
        
        # Base MIDI notes
        root_midi = root_pc + (root_octave + 1) * 12
        base_pitches = intervals_mx + root_midi
        
        # Apply voicing style transformations
        if style == "open":
            # Spread across 2 octaves
            spread = mx.array([0, 0, 12, 12] + [12] * (len(intervals) - 4), dtype=mx.int32)
            base_pitches = base_pitches + spread[:len(intervals)]
        elif style == "drop2":
            # Drop second voice down an octave
            if len(intervals) >= 2:
                drop = mx.array([0] * len(intervals), dtype=mx.int32)
                drop = mx.put(drop, mx.array([1]), mx.array([-12]))
                base_pitches = base_pitches + drop
        elif style == "shell":
            # Only root, 3rd, 7th
            keep_indices = mx.array([0, 1, len(intervals) - 1], dtype=mx.int32)
            base_pitches = mx.take(base_pitches, keep_indices)
        
        # Convert to Python list
        pitches = base_pitches.tolist()
        
        # Add humanization for dynamic output
        return [
            GeneratedNote(
                pitch=int(p),
                start_time=random.uniform(-0.01, 0.01),  # Micro-timing variation
                duration=2.0 * random.uniform(0.95, 1.05),  # Duration variation
                velocity=max(1, min(127, (75 if i == 0 else 70) + random.randint(-8, 8))),
            )
            for i, p in enumerate(pitches)
        ]
    
    def _compute_voicing_numpy(
        self,
        root_pc: int,
        intervals: List[int],
        style: VoicingStyle,
        root_octave: int,
    ) -> List[GeneratedNote]:
        """Fallback numpy implementation."""
        intervals_np = np.array(intervals, dtype=np.int32)
        
        root_midi = root_pc + (root_octave + 1) * 12
        base_pitches = intervals_np + root_midi
        
        if style == "open":
            spread = np.zeros(len(intervals), dtype=np.int32)
            spread[2:] = 12
            base_pitches = base_pitches + spread
        elif style == "drop2" and len(intervals) >= 2:
            base_pitches[1] -= 12
        elif style == "shell":
            keep_indices = [0, 1, len(intervals) - 1]
            base_pitches = base_pitches[keep_indices]
        
        # Add humanization for dynamic output
        return [
            GeneratedNote(
                pitch=int(p),
                start_time=random.uniform(-0.01, 0.01),  # Micro-timing variation
                duration=2.0 * random.uniform(0.95, 1.05),  # Duration variation
                velocity=max(1, min(127, (75 if i == 0 else 70) + random.randint(-8, 8))),
            )
            for i, p in enumerate(base_pitches)
        ]
    
    def _add_neosoul_extension(
        self,
        root_pc: int,
        quality: str,
        root_octave: int,
    ) -> Optional[GeneratedNote]:
        """Add a characteristic neo-soul extension."""
        # Common neo-soul additions
        if quality in ['maj7', 'm7']:
            # Add 9th
            extension = self.neosoul_extensions['add9']
        elif quality == '7':
            # Add #9 or b9 for that neo-soul crunch
            extension = self.neosoul_extensions['#9']
        else:
            return None
        
        pitch = root_pc + (root_octave + 2) * 12 + extension - 12
        
        return GeneratedNote(
            pitch=pitch,
            start_time=random.uniform(-0.01, 0.01),  # Micro-timing
            duration=2.0 * random.uniform(0.95, 1.05),  # Duration variation
            velocity=max(1, min(127, 65 + random.randint(-8, 8))),  # Velocity variation
        )
    
    def generate_progression_midi(
        self,
        chords: List[str],
        output_id: str,
        style: VoicingStyle = "open",
        bpm: int = 72,
        beats_per_chord: int = 4,
    ) -> Path:
        """
        Generate MIDI file for a chord progression.
        
        Args:
            chords: List of chord symbols
            output_id: Unique identifier for output file
            style: Voicing style to use
            bpm: Tempo in BPM
            beats_per_chord: Duration of each chord in beats
        
        Returns:
            Path to generated MIDI file
        """
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        piano = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano
        
        seconds_per_beat = 60.0 / bpm
        chord_duration = beats_per_chord * seconds_per_beat
        
        for i, chord in enumerate(chords):
            start_time = i * chord_duration
            
            # Generate voicing
            notes = self.generate_voicing(chord, style=style)
            
            # Add to MIDI
            for note in notes:
                midi_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=start_time,
                    end=start_time + chord_duration * 0.95,
                )
                piano.notes.append(midi_note)
        
        midi.instruments.append(piano)
        
        output_path = self.output_dir / f"{output_id}_progression.mid"
        midi.write(str(output_path))
        
        logger.info(f"Generated progression MIDI: {output_path}")
        return output_path
    
    def generate_neosoul_pattern(
        self,
        chord: str,
        output_id: str,
        pattern_type: str = "broken",
        bpm: int = 72,
        bars: int = 2,
    ) -> Path:
        """
        Generate a neo-soul rhythmic pattern for a chord.
        
        Args:
            chord: Chord symbol
            output_id: Unique identifier
            pattern_type: "broken", "arpeggio", "block"
            bpm: Tempo
            bars: Number of bars to generate
        
        Returns:
            Path to generated MIDI file
        """
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        piano = pretty_midi.Instrument(program=0)
        
        seconds_per_beat = 60.0 / bpm
        
        # Generate base voicing
        voicing_notes = self.generate_voicing(chord, style="open")
        pitches = [n.pitch for n in voicing_notes]
        
        total_beats = bars * 4
        
        if pattern_type == "broken":
            # Neo-soul broken chord with syncopation
            rhythm = [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.75]  # Syncopated
            for bar in range(bars):
                for beat_offset in rhythm:
                    beat = bar * 4 + beat_offset
                    for i, pitch in enumerate(pitches):
                        delay = i * 0.02  # Slight stagger for human feel
                        note = pretty_midi.Note(
                            velocity=np.random.randint(65, 80),
                            pitch=pitch,
                            start=(beat + delay) * seconds_per_beat,
                            end=(beat + 0.4 + delay) * seconds_per_beat,
                        )
                        piano.notes.append(note)
                        
        elif pattern_type == "arpeggio":
            # Rising arpeggio pattern
            for bar in range(bars):
                for beat in range(4):
                    for i, pitch in enumerate(pitches):
                        start = (bar * 4 + beat + i * 0.125) * seconds_per_beat
                        note = pretty_midi.Note(
                            velocity=70,
                            pitch=pitch,
                            start=start,
                            end=start + 0.2 * seconds_per_beat,
                        )
                        piano.notes.append(note)
        else:
            # Block chords on each beat
            for bar in range(bars):
                for beat in range(4):
                    start = (bar * 4 + beat) * seconds_per_beat
                    for pitch in pitches:
                        note = pretty_midi.Note(
                            velocity=75,
                            pitch=pitch,
                            start=start,
                            end=start + 0.9 * seconds_per_beat,
                        )
                        piano.notes.append(note)
        
        midi.instruments.append(piano)
        
        output_path = self.output_dir / f"{output_id}_pattern.mid"
        midi.write(str(output_path))
        
        logger.info(f"Generated neo-soul pattern: {output_path}")
        return output_path
    
    def benchmark(self, iterations: int = 100) -> Dict[str, float]:
        """
        Benchmark GPU vs CPU performance.
        
        Returns timing results for comparison.
        """
        import time
        
        test_chords = ["Dm9", "G13", "Cmaj9", "Am7", "Fmaj7", "Bm7b5", "E7"]
        
        # MLX timing
        if MLX_AVAILABLE:
            start = time.time()
            for _ in range(iterations):
                for chord in test_chords:
                    root_pc, quality = self._parse_chord(chord)
                    intervals = self.chord_templates.get(quality, [0, 4, 7, 11])
                    self._compute_voicing_mlx(root_pc, intervals, "open", 3)
            mlx_time = time.time() - start
        else:
            mlx_time = None
        
        # Numpy timing
        start = time.time()
        for _ in range(iterations):
            for chord in test_chords:
                root_pc, quality = self._parse_chord(chord)
                intervals = self.chord_templates.get(quality, [0, 4, 7, 11])
                self._compute_voicing_numpy(root_pc, intervals, "open", 3)
        numpy_time = time.time() - start
        
        results = {
            "iterations": iterations,
            "chords_per_iteration": len(test_chords),
            "numpy_time_seconds": numpy_time,
            "mlx_time_seconds": mlx_time,
            "gpu_available": is_gpu_available(),
            "mlx_available": MLX_AVAILABLE,
        }
        
        if mlx_time:
            results["speedup"] = numpy_time / mlx_time
        
        return results


# Singleton instance
gpu_midi_generator = GPUMIDIGenerator()
