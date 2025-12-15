"""
Advanced Lick Generation Engine - Phase 7

Implements multiple generation strategies:
1. Pattern-based: Transpose and vary curated patterns
2. Markov-based: Probabilistic generation using trained models
3. N-gram-based: Data-driven pattern chaining
4. Motif variation: Creative transformation of existing licks
5. Context-aware: Harmonic function and voice leading consideration

Key Features:
- Local-first approach (90% local, 10% AI)
- Multiple variation types (sequence, inversion, retrograde, etc.)
- Context-aware generation (chord progression, phrase position)
- Hybrid orchestration with complexity-based routing
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import random


# ============================================================================
# Data Classes
# ============================================================================

class GenerationStrategy(str, Enum):
    """Lick generation strategies"""
    PATTERN = "pattern"           # Use curated pattern
    MARKOV = "markov"            # Markov chain model
    NGRAM = "ngram"              # N-gram pattern matching
    MOTIF_VARIATION = "motif"    # Vary existing motif
    CONTEXT_AWARE = "context"    # Context-driven generation
    AUTO = "auto"                # Auto-select best strategy


class VariationType(str, Enum):
    """Motif variation types"""
    STANDARD = "standard"         # Exact transposition
    RHYTHMIC = "rhythmic"        # Vary rhythm, keep intervals
    INTERVALLIC = "intervallic"  # Vary intervals, keep rhythm
    INVERSION = "inversion"      # Invert intervals
    RETROGRADE = "retrograde"    # Reverse sequence
    AUGMENTATION = "augmentation"  # Double durations
    DIMINUTION = "diminution"    # Half durations
    SEQUENCE = "sequence"        # Repeat at different pitch


@dataclass
class Lick:
    """Generated lick representation"""
    notes: List[str]              # Note names (e.g., ['C4', 'E4', 'G4'])
    midi_notes: List[int]         # MIDI note numbers
    intervals: List[int]          # Interval pattern (semitones)
    rhythm: List[float]           # Note durations in beats
    duration_beats: float         # Total duration
    characteristics: List[str]    # Tags: "chromatic", "arpeggio", etc.
    style: str                    # "bebop", "blues", "gospel", etc.
    difficulty: str               # "beginner", "intermediate", "advanced"

    # Metadata
    technique: Optional[str] = None      # Source technique
    harmonic_function: Optional[str] = None  # "tonic", "dominant", etc.
    target_notes: List[int] = field(default_factory=list)  # Emphasized notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API response"""
        return {
            'notes': self.notes,
            'midi_notes': self.midi_notes,
            'intervals': self.intervals,
            'rhythm': self.rhythm,
            'duration_beats': self.duration_beats,
            'characteristics': self.characteristics,
            'style': self.style,
            'difficulty': self.difficulty,
            'technique': self.technique,
            'harmonic_function': self.harmonic_function,
            'target_notes': self.target_notes
        }


@dataclass
class LickGenerationRequest:
    """Request for lick generation"""
    style: str                           # "bebop", "blues", "gospel", etc.
    difficulty: str                      # "beginner", "intermediate", "advanced"
    context_chords: List[str]            # Chord context
    key: str                             # Musical key

    # Optional parameters
    generation_strategy: Optional[GenerationStrategy] = GenerationStrategy.AUTO
    variation_type: Optional[VariationType] = VariationType.STANDARD
    phrase_position: Optional[str] = None    # "beginning", "middle", "ending"
    previous_licks: Optional[List[Lick]] = None
    length_beats: float = 2.0
    use_ai_enhancement: bool = False


@dataclass
class LickGenerationResult:
    """Result of lick generation"""
    lick: Lick
    source: str          # "local_rules", "hybrid", "ai"
    complexity: int      # 1-10
    confidence: float    # 0-1
    explanation: Optional[str] = None


# ============================================================================
# Lick Generator Engine
# ============================================================================

class LickGeneratorEngine:
    """Core lick generation engine with multiple strategies"""

    def __init__(self):
        """Initialize generation engine"""
        self.pattern_library = None  # Old library (fallback)
        self.lick_database = None    # New expanded database (125+ patterns)
        self.markov_model = None     # Will be loaded on demand
        self.ngram_analyzer = None   # Will be loaded on demand
        self.lick_analyzer = None    # Will be loaded on demand

    # ========================================================================
    # Pattern-Based Generation
    # ========================================================================

    def generate_from_pattern(
        self,
        pattern_name: str,
        root: str,
        style: str,
        variation: VariationType = VariationType.STANDARD
    ) -> Lick:
        """Generate lick from named pattern with transposition

        Strategies:
        - standard: Exact pattern transposition
        - rhythmic: Vary rhythm while keeping intervals
        - intervallic: Vary intervals while keeping rhythm
        - inversion: Invert intervals (ascending <-> descending)
        - retrograde: Reverse note sequence
        - augmentation: Double note durations
        - diminution: Half note durations
        - sequence: Repeat pattern at different pitch levels

        Args:
            pattern_name: Name of pattern to use
            root: Root note for transposition
            style: Musical style
            variation: Type of variation to apply

        Returns:
            Generated Lick object
        """
        # Load expanded database on demand (125+ patterns)
        if not self.lick_database:
            from app.pipeline.lick_database_expanded import lick_database
            self.lick_database = lick_database

        # Get pattern from expanded database
        pattern = self.lick_database.get_by_name(pattern_name)

        # Fallback to old library if not found in expanded database
        if not pattern:
            if not self.pattern_library:
                from app.jazz.lick_patterns import lick_pattern_service
                self.pattern_library = lick_pattern_service
            patterns = self.pattern_library.patterns.get(style, [])
            pattern = next((p for p in patterns if p.name == pattern_name), None)

        if not pattern:
            # Fallback: use first pattern of style
            pattern = patterns[0] if patterns else None
            if not pattern:
                raise ValueError(f"No patterns found for style: {style}")

        # Transpose pattern to root
        from app.theory.interval_utils import note_to_semitone
        root_semitone = note_to_semitone(root) if len(root) <= 2 else 60  # Default to C4

        # Apply variation
        if variation == VariationType.STANDARD:
            intervals = pattern.intervals
            rhythm = pattern.rhythm
        elif variation == VariationType.RHYTHMIC:
            intervals = pattern.intervals
            rhythm = self._vary_rhythm(pattern.rhythm)
        elif variation == VariationType.INTERVALLIC:
            intervals = self._vary_intervals(pattern.intervals)
            rhythm = pattern.rhythm
        elif variation == VariationType.INVERSION:
            intervals = self._invert_intervals(pattern.intervals)
            rhythm = pattern.rhythm
        elif variation == VariationType.RETROGRADE:
            intervals = tuple(reversed(pattern.intervals))
            rhythm = list(reversed(pattern.rhythm))
        elif variation == VariationType.AUGMENTATION:
            intervals = pattern.intervals
            rhythm = [d * 2 for d in pattern.rhythm]
        elif variation == VariationType.DIMINUTION:
            intervals = pattern.intervals
            rhythm = [d / 2 for d in pattern.rhythm]
        else:  # SEQUENCE
            intervals = pattern.intervals
            rhythm = pattern.rhythm

        # Build MIDI notes
        midi_notes = [root_semitone + interval for interval in intervals]

        # Convert to note names
        from app.theory.interval_utils import semitone_to_note
        notes = [f"{semitone_to_note(m % 12)}{(m // 12) - 1}" for m in midi_notes]

        # Calculate duration
        duration_beats = sum(rhythm)

        return Lick(
            notes=notes,
            midi_notes=midi_notes,
            intervals=list(intervals),
            rhythm=rhythm,
            duration_beats=duration_beats,
            characteristics=pattern.characteristics,
            style=style,
            difficulty=pattern.difficulty,
            technique=f"pattern_{variation.value}",
            harmonic_function=None
        )

    def _vary_rhythm(self, rhythm: List[float]) -> List[float]:
        """Vary rhythmic pattern while maintaining overall feel"""
        # Simple variation: swap adjacent durations occasionally
        varied = rhythm.copy()
        for i in range(len(varied) - 1):
            if random.random() < 0.3:  # 30% chance of swap
                varied[i], varied[i+1] = varied[i+1], varied[i]
        return varied

    def _vary_intervals(self, intervals: Tuple[int, ...]) -> Tuple[int, ...]:
        """Vary intervals while maintaining contour"""
        # Simple variation: adjust intervals by ±1 semitone occasionally
        varied = list(intervals)
        for i in range(1, len(varied)):  # Skip first (root)
            if random.random() < 0.3:  # 30% chance of variation
                adjustment = random.choice([-1, 1])
                varied[i] = max(0, min(12, varied[i] + adjustment))
        return tuple(varied)

    def _invert_intervals(self, intervals: Tuple[int, ...]) -> Tuple[int, ...]:
        """Invert interval pattern (ascending <-> descending)"""
        if not intervals:
            return intervals

        inverted = [intervals[0]]  # Keep root
        for i in range(1, len(intervals)):
            # Invert direction relative to previous note
            prev_interval = intervals[i] - intervals[i-1]
            inverted_interval = inverted[i-1] - prev_interval
            inverted.append(inverted_interval)

        return tuple(inverted)

    # ========================================================================
    # Motif Variation
    # ========================================================================

    def generate_motif_variation(
        self,
        source_lick: Lick,
        variation_type: VariationType,
        preserve: List[str] = None
    ) -> Lick:
        """Generate variation of existing lick

        Variation types:
        - sequence: Repeat pattern at different pitch levels
        - fragmentation: Use portion of lick as new motif
        - expansion: Add passing tones, ornaments
        - contraction: Remove non-essential notes
        - inversion: Mirror intervals
        - retrograde: Reverse time
        - rhythmic_displacement: Shift rhythmic accents

        Preserve options:
        - contour: Keep melodic shape
        - rhythm: Keep rhythmic pattern
        - key_tones: Keep chord tones

        Args:
            source_lick: Original lick to vary
            variation_type: Type of variation
            preserve: List of elements to preserve

        Returns:
            Varied Lick object
        """
        preserve = preserve or ['contour']

        if variation_type == VariationType.INVERSION:
            # Invert intervals
            intervals = self._invert_intervals(tuple(source_lick.intervals))
            rhythm = source_lick.rhythm if 'rhythm' in preserve else self._vary_rhythm(source_lick.rhythm)

        elif variation_type == VariationType.RETROGRADE:
            # Reverse sequence
            intervals = list(reversed(source_lick.intervals))
            rhythm = list(reversed(source_lick.rhythm))

        elif variation_type == VariationType.AUGMENTATION:
            # Double durations
            intervals = source_lick.intervals
            rhythm = [d * 2 for d in source_lick.rhythm]

        elif variation_type == VariationType.DIMINUTION:
            # Half durations
            intervals = source_lick.intervals
            rhythm = [d / 2 for d in source_lick.rhythm]

        elif variation_type == VariationType.SEQUENCE:
            # Sequence up a 3rd (4 semitones)
            intervals = [i + 4 for i in source_lick.intervals]
            rhythm = source_lick.rhythm

        else:  # STANDARD or others
            intervals = source_lick.intervals
            rhythm = source_lick.rhythm

        # Rebuild lick
        base_midi = source_lick.midi_notes[0] if source_lick.midi_notes else 60
        midi_notes = [base_midi + interval for interval in intervals]

        from app.theory.interval_utils import semitone_to_note
        notes = [f"{semitone_to_note(m % 12)}{(m // 12) - 1}" for m in midi_notes]

        return Lick(
            notes=notes,
            midi_notes=midi_notes,
            intervals=intervals,
            rhythm=rhythm,
            duration_beats=sum(rhythm),
            characteristics=source_lick.characteristics + [f"variation_{variation_type.value}"],
            style=source_lick.style,
            difficulty=source_lick.difficulty,
            technique=f"motif_variation_{variation_type.value}"
        )

    # ========================================================================
    # Markov-Based Generation
    # ========================================================================

    def generate_from_markov(
        self,
        style: str,
        length: int = 8,
        root: str = "C",
        temperature: float = 1.0
    ) -> Lick:
        """Generate lick using Markov chain model

        Args:
            style: Musical style (bebop, gospel, blues, etc.)
            length: Target length in notes
            root: Root note for transposition
            temperature: Randomness (0=deterministic, 1=normal, >1=creative)

        Returns:
            Generated Lick object
        """
        # Load Markov model on demand
        if not self.markov_model:
            from app.pipeline.markov_lick_model import markov_model_manager
            self.markov_model = markov_model_manager

        # Generate interval sequence using Markov chain
        intervals = self.markov_model.generate_lick(
            style=style,
            length=length,
            temperature=temperature
        )

        if not intervals:
            # Fallback to pattern-based
            return self.generate_from_pattern(
                pattern_name=f"{style}_default",
                root=root,
                style=style,
                variation=VariationType.STANDARD
            )

        # Convert intervals to notes
        root_midi = self._note_to_midi(root + "4")
        midi_notes = [root_midi + interval for interval in intervals]
        notes = [self._midi_to_note(midi) for midi in midi_notes]

        # Generate rhythm (for now, use equal durations)
        # TODO: Add rhythm Markov model
        rhythm = [0.5] * len(intervals)
        duration_beats = sum(rhythm)

        # Analyze characteristics
        if not hasattr(self, 'lick_analyzer') or not self.lick_analyzer:
            from app.pipeline.lick_analyzer import lick_analyzer
            self.lick_analyzer = lick_analyzer

        characteristics = self.lick_analyzer.detect_characteristics(intervals, rhythm)

        return Lick(
            notes=notes,
            midi_notes=midi_notes,
            intervals=intervals,
            rhythm=rhythm,
            duration_beats=duration_beats,
            characteristics=characteristics,
            style=style,
            difficulty="intermediate",
            technique=f"markov_t{temperature}"
        )

    # ========================================================================
    # N-gram Generation
    # ========================================================================

    def generate_from_ngram(
        self,
        style: str,
        length: int = 8,
        root: str = "C",
        n: int = 3
    ) -> Lick:
        """Generate lick using N-gram pattern matching

        Args:
            style: Musical style
            length: Target length
            root: Root note
            n: N-gram size (3-5)

        Returns:
            Generated Lick object
        """
        # Load database for n-gram extraction
        if not self.lick_database:
            from app.pipeline.lick_database_expanded import lick_database
            self.lick_database = lick_database

        # Get patterns of this style
        patterns = self.lick_database.get_by_style(style)

        if not patterns:
            return self.generate_from_pattern(
                pattern_name=f"{style}_default",
                root=root,
                style=style,
                variation=VariationType.STANDARD
            )

        # Extract n-grams from all patterns
        if not self.lick_analyzer:
            from app.pipeline.lick_analyzer import lick_analyzer
            self.lick_analyzer = lick_analyzer

        ngrams = []
        for pattern in patterns:
            pattern_ngrams = self.lick_analyzer.get_ngrams(
                list(pattern.intervals),
                n=n
            )
            ngrams.extend(pattern_ngrams)

        if not ngrams:
            # Fallback
            return self.generate_from_pattern(
                pattern_name=f"{style}_default",
                root=root,
                style=style,
                variation=VariationType.STANDARD
            )

        # Build lick by chaining n-grams
        intervals = list(random.choice(ngrams))  # Start with random n-gram

        while len(intervals) < length:
            # Find n-grams that start with last (n-1) intervals
            current_suffix = tuple(intervals[-(n-1):])
            matching = [ng for ng in ngrams if ng[:n-1] == current_suffix]

            if matching:
                next_ngram = random.choice(matching)
                intervals.append(next_ngram[-1])  # Add last note
            else:
                break  # No matching continuation

        # Convert to notes
        root_midi = self._note_to_midi(root + "4")
        midi_notes = [root_midi + interval for interval in intervals[:length]]
        notes = [self._midi_to_note(midi) for midi in midi_notes]

        rhythm = [0.5] * len(intervals[:length])
        duration_beats = sum(rhythm)

        characteristics = self.lick_analyzer.detect_characteristics(
            intervals[:length], rhythm
        )

        return Lick(
            notes=notes,
            midi_notes=midi_notes,
            intervals=intervals[:length],
            rhythm=rhythm,
            duration_beats=duration_beats,
            characteristics=characteristics,
            style=style,
            difficulty="intermediate",
            technique=f"ngram_n{n}"
        )

    # ========================================================================
    # Context-Aware Generation
    # ========================================================================

    def generate_context_aware(
        self,
        chord_progression: List[str],
        phrase_position: str,
        previous_licks: List[Lick],
        style: str,
        difficulty: str
    ) -> Lick:
        """Generate contextually appropriate lick

        Considers:
        - Harmonic function (T/S/D)
        - Phrase position (beginning/middle/end)
        - Voice leading from previous phrase
        - Avoid repetition of recent patterns
        - Build tension/release arc

        Args:
            chord_progression: Chord context
            phrase_position: Position in phrase
            previous_licks: Recently generated licks
            style: Musical style
            difficulty: Difficulty level

        Returns:
            Contextually appropriate Lick
        """
        # Analyze harmonic function
        from app.pipeline.harmonic_function_analyzer import analyze_chord_function

        primary_chord = chord_progression[0] if chord_progression else 'C'

        try:
            # Parse chord
            from app.theory.chord_parser import parse_chord_symbol
            parsed = parse_chord_symbol(primary_chord)
            root = parsed['root']
            quality = parsed['quality']

            # Get harmonic function
            function = analyze_chord_function(root, quality, 'C')  # Simplified: assume C major
        except Exception:
            function = 'tonic'
            root = 'C'

        # Select pattern based on context
        if phrase_position == 'ending':
            # Use resolution patterns
            pattern_name = self._select_resolution_pattern(style, function)
        elif phrase_position == 'beginning':
            # Use opening patterns
            pattern_name = self._select_opening_pattern(style, function)
        else:
            # Use continuation patterns
            pattern_name = self._select_continuation_pattern(style, function, previous_licks)

        # Generate from pattern
        try:
            lick = self.generate_from_pattern(pattern_name, root, style)
            lick.harmonic_function = function
            return lick
        except Exception:
            # Fallback: generate simple arpeggio
            return self._generate_simple_arpeggio(root, style, difficulty)

    def _select_resolution_pattern(self, style: str, function: str) -> str:
        """Select appropriate resolution pattern"""
        if style == 'bebop':
            return 'Bebop Descending 8th Line'
        elif style == 'blues':
            return 'Blues Bend Lick'
        elif style == 'gospel':
            return 'Gospel Turnaround'
        else:
            return 'Swing Eighth Line'

    def _select_opening_pattern(self, style: str, function: str) -> str:
        """Select appropriate opening pattern"""
        if style == 'bebop':
            return 'Parker Lick'
        elif style == 'blues':
            return 'Call-Response Blues'
        elif style == 'gospel':
            return 'Gospel Run'
        else:
            return 'Swing Arpeggio'

    def _select_continuation_pattern(
        self,
        style: str,
        function: str,
        previous_licks: List[Lick]
    ) -> str:
        """Select pattern that continues musical narrative"""
        # Avoid repetition of recent techniques
        recent_techniques = {lick.technique for lick in (previous_licks or [])[-3:]}

        if style == 'bebop':
            candidates = ['Enclosure Lick', 'Parker Lick', 'Bebop Descending 8th Line']
        elif style == 'blues':
            candidates = ['Blues Bend Lick', 'Call-Response Blues']
        elif style == 'gospel':
            candidates = ['Gospel Run', 'Gospel Turnaround']
        else:
            candidates = ['Swing Eighth Line', 'Swing Arpeggio']

        # Filter out recently used patterns
        available = [c for c in candidates if f"pattern_standard" not in recent_techniques]
        return available[0] if available else candidates[0]

    def _generate_simple_arpeggio(self, root: str, style: str, difficulty: str) -> Lick:
        """Fallback: generate simple chord arpeggio"""
        from app.theory.interval_utils import note_to_semitone

        root_semitone = note_to_semitone(root) if len(root) <= 2 else 60

        # Major triad arpeggio
        intervals = [0, 4, 7, 12]  # Root, 3rd, 5th, octave
        rhythm = [0.5, 0.5, 0.5, 0.5]
        midi_notes = [root_semitone + i + 60 for i in intervals]

        from app.theory.interval_utils import semitone_to_note
        notes = [f"{semitone_to_note(m % 12)}{(m // 12) - 1}" for m in midi_notes]

        return Lick(
            notes=notes,
            midi_notes=midi_notes,
            intervals=intervals,
            rhythm=rhythm,
            duration_beats=2.0,
            characteristics=['arpeggio', 'simple'],
            style=style,
            difficulty=difficulty,
            technique='fallback_arpeggio'
        )

    # ========================================================================
    # Hybrid Generation Orchestration
    # ========================================================================

    def generate_hybrid(
        self,
        request: LickGenerationRequest,
        use_ai: bool = False
    ) -> LickGenerationResult:
        """Hybrid local + AI generation

        Strategy:
        1. Calculate complexity (1-10)
        2. If complexity ≤ 7: Use local generation (90% of cases)
        3. If complexity 8+: Enhance with AI (10% of cases)

        Complexity factors:
        - Style (bebop=8, blues=5, gospel=6, neo-soul=9)
        - Difficulty (beginner=0, intermediate=+2, advanced=+4)
        - Context complexity (simple chord=0, progression=+2)
        - Variation requests (+2)

        Args:
            request: Generation request
            use_ai: Force AI enhancement

        Returns:
            LickGenerationResult with lick and metadata
        """
        # Calculate complexity
        complexity = self._calculate_complexity(request)

        # Local generation
        if complexity <= 7 and not use_ai:
            # Select generation strategy
            if request.generation_strategy == GenerationStrategy.PATTERN:
                lick = self._generate_from_pattern_auto(request)
            elif request.generation_strategy == GenerationStrategy.MOTIF_VARIATION:
                if request.previous_licks:
                    lick = self.generate_motif_variation(
                        request.previous_licks[-1],
                        request.variation_type or VariationType.STANDARD
                    )
                else:
                    lick = self._generate_from_pattern_auto(request)
            elif request.generation_strategy == GenerationStrategy.CONTEXT_AWARE:
                lick = self.generate_context_aware(
                    request.context_chords,
                    request.phrase_position or 'middle',
                    request.previous_licks or [],
                    request.style,
                    request.difficulty
                )
            else:  # AUTO
                lick = self._auto_select_strategy(request)

            return LickGenerationResult(
                lick=lick,
                source='local_rules',
                complexity=complexity,
                confidence=0.85,
                explanation=f"Generated using {lick.technique} with local pattern library"
            )

        else:
            # AI enhancement (placeholder for now)
            # In production, would call AI service
            base_lick = self._generate_from_pattern_auto(request)

            return LickGenerationResult(
                lick=base_lick,
                source='hybrid',
                complexity=complexity,
                confidence=0.92,
                explanation="Generated with AI enhancement (placeholder)"
            )

    def _calculate_complexity(self, request: LickGenerationRequest) -> int:
        """Calculate task complexity (1-10)"""
        complexity = 5  # Base

        # Style factor
        style_complexity = {
            'bebop': 3,
            'blues': 0,
            'gospel': 1,
            'modern': 4,
            'swing': 0,
            'bossa': 1,
            'neosoul': 4
        }
        complexity += style_complexity.get(request.style, 2)

        # Difficulty factor
        if request.difficulty == 'advanced':
            complexity += 4
        elif request.difficulty == 'intermediate':
            complexity += 2

        # Context complexity
        if len(request.context_chords) > 1:
            complexity += 2

        # Variation complexity
        if request.variation_type != VariationType.STANDARD:
            complexity += 2

        return min(10, max(1, complexity))

    def _generate_from_pattern_auto(self, request: LickGenerationRequest) -> Lick:
        """Auto-select and generate from pattern"""
        # Use first chord as root
        root = 'C'  # Default
        if request.context_chords:
            try:
                from app.theory.chord_parser import parse_chord_symbol
                parsed = parse_chord_symbol(request.context_chords[0])
                root = parsed['root']
            except Exception:
                pass

        # Select pattern name based on style
        pattern_name = self._select_default_pattern(request.style)

        return self.generate_from_pattern(
            pattern_name,
            root,
            request.style,
            request.variation_type or VariationType.STANDARD
        )

    def _select_default_pattern(self, style: str) -> str:
        """Select default pattern for style"""
        defaults = {
            'bebop': 'Parker Lick',
            'blues': 'Blues Bend Lick',
            'gospel': 'Gospel Run',
            'modern': 'Altered Scale Run',
            'swing': 'Swing Eighth Line',
            'bossa': 'Bossa Chromatic Approach'
        }
        return defaults.get(style, 'Swing Eighth Line')

    def _auto_select_strategy(self, request: LickGenerationRequest) -> Lick:
        """Automatically select best generation strategy

        Strategy selection logic:
        1. Context-aware: If rich harmonic context (3+ chords) or phrase position specified
        2. Markov: For intermediate difficulty, moderate length (6-10 notes)
        3. N-gram: For complex patterns, advanced difficulty
        4. Pattern-based: Default for beginners and short licks
        """
        # 1. Context-aware for rich harmonic context
        if len(request.context_chords) > 2 or request.phrase_position:
            return self.generate_context_aware(
                request.context_chords,
                request.phrase_position or 'middle',
                request.previous_licks or [],
                request.style,
                request.difficulty
            )

        # 2. Markov for intermediate difficulty and moderate length
        target_length = int(request.length_beats / 0.5)  # Assume 8th notes
        if request.difficulty == "intermediate" and 6 <= target_length <= 10:
            return self.generate_from_markov(
                style=request.style,
                length=target_length,
                root="C",  # Will be transposed later if needed
                temperature=1.0
            )

        # 3. N-gram for advanced difficulty
        if request.difficulty == "advanced":
            return self.generate_from_ngram(
                style=request.style,
                length=target_length,
                root="C",
                n=4  # Larger n-grams for advanced patterns
            )

        # 4. Pattern-based as default (beginner, short licks)
        return self._generate_from_pattern_auto(request)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _note_to_midi(self, note: str) -> int:
        """Convert note name to MIDI number (C4 = 60)"""
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        # Parse note and octave
        if len(note) == 2:  # e.g., "C4"
            note_name = note[0]
            octave = int(note[1])
        elif len(note) == 3:  # e.g., "C#4" or "Db4"
            note_name = note[:2]
            octave = int(note[2])
        else:
            raise ValueError(f"Invalid note format: {note}")

        if note_name not in note_map:
            raise ValueError(f"Unknown note: {note_name}")

        return (octave + 1) * 12 + note_map[note_name]

    def _midi_to_note(self, midi: int) -> str:
        """Convert MIDI number to note name"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi // 12) - 1
        note_index = midi % 12
        return f"{note_names[note_index]}{octave}"


# ============================================================================
# Global Service Instance
# ============================================================================

lick_generator_engine = LickGeneratorEngine()
