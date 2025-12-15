"""
Exercise Generator Engine - Phase 8 Week 1

Main orchestrator for exercise generation following Phase 7's proven pattern.

Implements 90% local, 10% AI approach:
- Complexity 1-7: 100% local generation (zero cost)
- Complexity 8-10: AI enhancement (Qwen2.5-7B local or Gemini fallback)

Key Features:
- Unified entry point for all exercise types
- Type-specific generator routing
- Complexity-based strategy selection
- Automatic variant generation (beginner/intermediate/advanced)
- Phase 4/5/7 integration
- Lazy generator loading for performance

Supported Exercise Types:
1. Scale (complexity 1) - Pattern-based
2. Arpeggio (complexity 2) - Pattern-based
3. Rhythm (complexity 3) - Pattern-based
4. Progression (complexity 4) - Phase 4 chord substitutions
5. Pattern (complexity 5) - Phase 7 lick database
6. Voicing (complexity 5) - Phase 5 voice leading templates
7. Voice Leading (complexity 6) - Phase 5 voice leading analyzer
8. Lick (complexity 6) - Phase 7 Markov models
9. Ear Training (complexity 7) - AI-enhanced (local Qwen2.5-7B)
"""

from typing import List, Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
from datetime import datetime


# ============================================================================
# Data Classes
# ============================================================================

class ExerciseType(str, Enum):
    """Supported exercise types"""
    SCALE = "scale"
    ARPEGGIO = "arpeggio"
    PROGRESSION = "progression"
    VOICING = "voicing"
    VOICE_LEADING = "voice_leading"
    RHYTHM = "rhythm"
    PATTERN = "pattern"
    LICK = "lick"
    EAR_TRAINING = "ear_training"


class Difficulty(str, Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class Exercise:
    """Generated exercise representation"""
    exercise_type: str                # Exercise type
    title: str                        # Display title
    description: str                  # Explanation

    # Musical content
    notes: List[str]                  # Note names (e.g., ['C4', 'E4', 'G4'])
    midi_notes: List[int]             # MIDI note numbers
    rhythm: List[float]               # Note durations in beats
    duration_beats: float             # Total duration

    # Context
    key: str                          # Musical key
    time_signature: Tuple[int, int] = (4, 4)  # Time signature
    tempo_bpm: int = 100              # Suggested tempo

    # Metadata
    difficulty: str = "intermediate"
    characteristics: List[str] = field(default_factory=list)
    practice_tips: List[str] = field(default_factory=list)

    # Additional content (optional)
    chords: Optional[List[str]] = None
    roman_numerals: Optional[List[str]] = None
    voicings: Optional[List[List[int]]] = None

    # Generation metadata
    technique: Optional[str] = None
    complexity: int = 5
    generation_method: str = "local"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API response"""
        return {
            'exercise_type': self.exercise_type,
            'title': self.title,
            'description': self.description,
            'notes': self.notes,
            'midi_notes': self.midi_notes,
            'rhythm': self.rhythm,
            'duration_beats': self.duration_beats,
            'key': self.key,
            'time_signature': list(self.time_signature),
            'tempo_bpm': self.tempo_bpm,
            'difficulty': self.difficulty,
            'characteristics': self.characteristics,
            'practice_tips': self.practice_tips,
            'chords': self.chords,
            'roman_numerals': self.roman_numerals,
            'voicings': self.voicings,
            'technique': self.technique,
            'complexity': self.complexity,
            'generation_method': self.generation_method,
            'created_at': self.created_at
        }


@dataclass
class ExerciseGenerationRequest:
    """Request for exercise generation"""
    exercise_type: str                # Exercise type
    difficulty: str                   # "beginner", "intermediate", "advanced"
    key: str                          # Musical key

    # Optional context
    style: Optional[str] = None       # "bebop", "gospel", "blues", etc.
    context_chords: Optional[List[str]] = None
    tempo_bpm: Optional[int] = None
    length_beats: Optional[float] = None
    focus_area: Optional[str] = None  # Specific technique or concept

    # Generation preferences
    use_ai: bool = False              # Force AI enhancement
    seed: Optional[int] = None        # For reproducibility


# ============================================================================
# Exercise Generator Engine
# ============================================================================

class ExerciseGeneratorEngine:
    """
    Main orchestrator for exercise generation.

    Follows Phase 7's lick_generator_engine.py pattern:
    - Single entry point for all exercise types
    - Complexity-based routing (local vs AI)
    - Lazy generator loading
    - Automatic variant generation
    """

    # Exercise complexity mapping (1-10 scale)
    EXERCISE_COMPLEXITY = {
        ExerciseType.SCALE: 1,           # 100% local, pattern-based
        ExerciseType.ARPEGGIO: 2,        # 100% local, pattern-based
        ExerciseType.RHYTHM: 3,          # 100% local, pattern-based
        ExerciseType.PROGRESSION: 4,     # Phase 4 chord_substitutions.py
        ExerciseType.PATTERN: 5,         # Phase 7 lick_database_expanded.py
        ExerciseType.VOICING: 5,         # Phase 5 voice_leading_templates.py
        ExerciseType.VOICE_LEADING: 6,   # Phase 5 voice_leading_analyzer.py
        ExerciseType.LICK: 6,            # Phase 7 markov_lick_model.py
        ExerciseType.EAR_TRAINING: 7,    # AI-enhanced (Qwen2.5-7B local)
    }

    def __init__(self):
        """Initialize engine with lazy generator loading"""
        self._generators = {}  # Lazy-loaded generators
        self._cache = {}       # Generation cache (optional)

    def generate_exercise(
        self,
        exercise_type: str,
        context: Dict[str, Any],
        difficulty: str = "intermediate",
        use_ai: bool = False
    ) -> Exercise:
        """
        Main entry point for exercise generation.

        Args:
            exercise_type: Type of exercise to generate
            context: Generation context (key, chords, tempo, etc.)
            difficulty: Difficulty level
            use_ai: Force AI enhancement

        Returns:
            Generated Exercise object

        Examples:
            >>> engine = ExerciseGeneratorEngine()
            >>> exercise = engine.generate_exercise(
            ...     exercise_type="scale",
            ...     context={"key": "C", "scale_type": "major"},
            ...     difficulty="beginner"
            ... )
            >>> print(exercise.title)
            "C Major Scale - Ascending"
        """
        # Validate exercise type
        try:
            ex_type = ExerciseType(exercise_type)
        except ValueError:
            raise ValueError(
                f"Unknown exercise type: {exercise_type}. "
                f"Valid types: {[t.value for t in ExerciseType]}"
            )

        # Get complexity
        complexity = self.EXERCISE_COMPLEXITY[ex_type]

        # Route to appropriate generator
        generator_func = self._get_generator(ex_type)

        # Generate exercise
        exercise = generator_func(
            context=context,
            difficulty=difficulty,
            complexity=complexity,
            use_ai=use_ai
        )

        return exercise

    def generate_variants(
        self,
        exercise: Exercise,
        count: int = 3
    ) -> List[Exercise]:
        """
        Generate difficulty variants of an exercise.

        Creates beginner/intermediate/advanced versions by adjusting:
        - Tempo (beginner slower, advanced faster)
        - Range (beginner smaller, advanced larger)
        - Complexity (beginner simpler patterns, advanced more complex)

        Args:
            exercise: Base exercise
            count: Number of variants (default 3 for each difficulty)

        Returns:
            List of Exercise variants

        Examples:
            >>> variants = engine.generate_variants(base_exercise, count=3)
            >>> len(variants)
            3
            >>> [v.difficulty for v in variants]
            ['beginner', 'intermediate', 'advanced']
        """
        variants = []
        difficulties = [Difficulty.BEGINNER, Difficulty.INTERMEDIATE, Difficulty.ADVANCED]

        for difficulty in difficulties[:count]:
            variant = self._create_variant(exercise, difficulty.value)
            variants.append(variant)

        return variants

    def _get_generator(self, exercise_type: ExerciseType) -> Callable:
        """
        Get generator function for exercise type (lazy loading).

        Args:
            exercise_type: Type of exercise

        Returns:
            Generator function
        """
        # Check cache
        if exercise_type in self._generators:
            return self._generators[exercise_type]

        # Lazy load generator
        if exercise_type == ExerciseType.SCALE:
            from app.services.generators.scale_generator import generate_scale_exercise
            generator = generate_scale_exercise
        elif exercise_type == ExerciseType.ARPEGGIO:
            from app.services.generators.arpeggio_generator import generate_arpeggio_exercise
            generator = generate_arpeggio_exercise
        elif exercise_type == ExerciseType.RHYTHM:
            from app.services.generators.rhythm_generator import generate_rhythm_exercise
            generator = generate_rhythm_exercise
        elif exercise_type == ExerciseType.PROGRESSION:
            from app.services.generators.progression_generator import generate_progression_exercise
            generator = generate_progression_exercise
        elif exercise_type == ExerciseType.PATTERN:
            from app.services.generators.pattern_generator import generate_pattern_exercise
            generator = generate_pattern_exercise
        elif exercise_type == ExerciseType.VOICING:
            from app.services.generators.voicing_generator import generate_voicing_exercise
            generator = generate_voicing_exercise
        elif exercise_type == ExerciseType.VOICE_LEADING:
            from app.services.generators.voice_leading_generator import generate_voice_leading_exercise
            generator = generate_voice_leading_exercise
        elif exercise_type == ExerciseType.LICK:
            from app.services.generators.lick_generator import generate_lick_exercise
            generator = generate_lick_exercise
        elif exercise_type == ExerciseType.EAR_TRAINING:
            from app.services.generators.ear_training_generator import generate_ear_training_exercise
            generator = generate_ear_training_exercise
        else:
            raise ValueError(f"No generator for {exercise_type}")

        # Cache and return
        self._generators[exercise_type] = generator
        return generator

    def _create_variant(self, base: Exercise, difficulty: str) -> Exercise:
        """
        Create a difficulty variant of an exercise.

        Args:
            base: Base exercise
            difficulty: Target difficulty

        Returns:
            Variant exercise
        """
        # Copy base exercise
        variant = Exercise(
            exercise_type=base.exercise_type,
            title=f"{base.title} ({difficulty.capitalize()})",
            description=base.description,
            notes=base.notes.copy(),
            midi_notes=base.midi_notes.copy(),
            rhythm=base.rhythm.copy(),
            duration_beats=base.duration_beats,
            key=base.key,
            time_signature=base.time_signature,
            tempo_bpm=base.tempo_bpm,
            difficulty=difficulty,
            characteristics=base.characteristics.copy(),
            practice_tips=base.practice_tips.copy(),
            chords=base.chords.copy() if base.chords else None,
            roman_numerals=base.roman_numerals.copy() if base.roman_numerals else None,
            voicings=base.voicings.copy() if base.voicings else None,
            technique=base.technique,
            complexity=base.complexity,
            generation_method=base.generation_method
        )

        # Adjust tempo based on difficulty
        if difficulty == "beginner":
            variant.tempo_bpm = int(base.tempo_bpm * 0.7)  # 70% of base
        elif difficulty == "intermediate":
            variant.tempo_bpm = base.tempo_bpm  # Keep base tempo
        elif difficulty == "advanced":
            variant.tempo_bpm = int(base.tempo_bpm * 1.2)  # 120% of base

        # Adjust practice tips
        if difficulty == "beginner":
            variant.practice_tips.insert(0, "Start very slowly and focus on accuracy")
            variant.practice_tips.append("Practice hands separately first")
        elif difficulty == "advanced":
            variant.practice_tips.append("Try playing at faster tempos")
            variant.practice_tips.append("Experiment with different articulations")

        return variant

    def get_complexity(self, exercise_type: str) -> int:
        """
        Get complexity level for an exercise type.

        Args:
            exercise_type: Type of exercise

        Returns:
            Complexity level (1-10)
        """
        try:
            ex_type = ExerciseType(exercise_type)
            return self.EXERCISE_COMPLEXITY[ex_type]
        except (ValueError, KeyError):
            return 5  # Default to moderate complexity

    def is_local_generation(self, exercise_type: str) -> bool:
        """
        Check if exercise type uses local generation.

        Args:
            exercise_type: Type of exercise

        Returns:
            True if local (complexity 1-7), False if AI (8-10)
        """
        complexity = self.get_complexity(exercise_type)
        return complexity <= 7


# ============================================================================
# Global Instance
# ============================================================================

# Create global instance (singleton pattern)
exercise_generator_engine = ExerciseGeneratorEngine()


# ============================================================================
# Convenience Functions
# ============================================================================

def generate_exercise(
    exercise_type: str,
    context: Dict[str, Any],
    difficulty: str = "intermediate",
    use_ai: bool = False
) -> Exercise:
    """
    Convenience function for exercise generation.

    Args:
        exercise_type: Type of exercise
        context: Generation context
        difficulty: Difficulty level
        use_ai: Force AI enhancement

    Returns:
        Generated Exercise

    Examples:
        >>> exercise = generate_exercise(
        ...     exercise_type="scale",
        ...     context={"key": "D", "scale_type": "minor"},
        ...     difficulty="intermediate"
        ... )
    """
    return exercise_generator_engine.generate_exercise(
        exercise_type=exercise_type,
        context=context,
        difficulty=difficulty,
        use_ai=use_ai
    )


def generate_exercise_variants(
    exercise: Exercise,
    count: int = 3
) -> List[Exercise]:
    """
    Convenience function for variant generation.

    Args:
        exercise: Base exercise
        count: Number of variants

    Returns:
        List of Exercise variants
    """
    return exercise_generator_engine.generate_variants(exercise, count)


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("EXERCISE GENERATOR ENGINE - Phase 8 Week 1")
    print("=" * 70)

    # Example 1: Generate scale exercise
    print("\nExample 1: Scale Exercise")
    print("-" * 70)

    try:
        scale_exercise = generate_exercise(
            exercise_type="scale",
            context={
                "key": "C",
                "scale_type": "major",
                "octaves": 1
            },
            difficulty="beginner"
        )
        print(f"Title: {scale_exercise.title}")
        print(f"Difficulty: {scale_exercise.difficulty}")
        print(f"Tempo: {scale_exercise.tempo_bpm} BPM")
        print(f"Complexity: {scale_exercise.complexity}")
        print(f"Generation: {scale_exercise.generation_method}")
    except ImportError as e:
        print(f"⚠️  Generator not yet implemented: {e}")

    # Example 2: Generate variants
    print("\n\nExample 2: Generate Variants")
    print("-" * 70)

    print("Note: Variant generation available once base exercise is created")

    # Example 3: Check complexity levels
    print("\n\nExample 3: Exercise Complexity Levels")
    print("-" * 70)

    for exercise_type in ExerciseType:
        complexity = exercise_generator_engine.get_complexity(exercise_type.value)
        is_local = exercise_generator_engine.is_local_generation(exercise_type.value)
        method = "LOCAL (free)" if is_local else "AI (cost)"
        print(f"{exercise_type.value:15} - Complexity {complexity} - {method}")

    print("\n" + "=" * 70)
    print("✅ Exercise Generator Engine initialized successfully!")
    print("=" * 70)
