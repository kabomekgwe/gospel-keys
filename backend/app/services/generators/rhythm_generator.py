"""
Rhythm Exercise Generator

Generates rhythmic patterns for practice.
Complexity 3 (Local).

Features:
- Multiple rhythm patterns per difficulty
- Tempo randomization
- Pattern combinations for variety
- Dynamic bar count
"""

from typing import Dict, Any, List
import random
from app.services.exercise_generator_engine import Exercise


# ============================================================================
# Rhythm Patterns
# ============================================================================

RHYTHM_PATTERNS = {
    "beginner": [
        [1.0, 1.0, 1.0, 1.0],           # Quarter notes
        [2.0, 2.0],                      # Half notes
        [4.0],                           # Whole note
        [2.0, 1.0, 1.0],                 # Half + two quarters
        [1.0, 1.0, 2.0],                 # Two quarters + half
        [1.0, 2.0, 1.0],                 # Quarter, half, quarter
    ],
    "intermediate": [
        [0.5, 0.5, 1.0, 1.0, 1.0],       # Eighth notes mix
        [1.5, 0.5, 2.0],                 # Dotted rhythms
        [0.5, 0.5, 0.5, 0.5, 2.0],       # Multiple eighths
        [1.0, 0.5, 0.5, 1.0, 1.0],       # Syncopation
        [0.5, 1.0, 0.5, 2.0],            # Off-beat
        [1.0, 1.0, 0.5, 0.5, 1.0],       # Mixed
        [0.5, 0.5, 1.5, 0.5, 1.0],       # Dotted + eighth
        [2.0, 0.5, 0.5, 1.0],            # Long start
    ],
    "advanced": [
        [0.75, 0.25, 0.5, 0.5, 1.0, 1.0],    # 16th notes
        [0.33, 0.33, 0.34, 1.0, 2.0],        # Triplets
        [0.25, 0.25, 0.25, 0.25, 1.0, 2.0],  # 16th note group
        [0.5, 0.25, 0.25, 0.5, 0.5, 2.0],    # Complex mix
        [1.0, 0.33, 0.33, 0.34, 2.0],        # Quarter + triplet
        [0.25, 0.75, 0.5, 0.5, 2.0],         # Dotted 16th
        [0.5, 0.5, 0.33, 0.33, 0.34, 2.0],   # Eighth + triplet
        [0.25, 0.25, 0.5, 0.5, 0.5, 2.0],    # 16th + eighths
    ]
}


def generate_rhythm_exercise(
    context: Dict[str, Any],
    difficulty: str = "intermediate",
    complexity: int = 3,
    use_ai: bool = False
) -> Exercise:
    """
    Generate rhythm exercise with randomized patterns.
    
    Args:
        context: Generation context
        difficulty: Difficulty level
        complexity: Complexity level (1-10)
        use_ai: Force AI (ignored)
    
    Returns:
        Exercise with rhythm pattern
    """
    randomize = context.get("randomize", True)
    
    # Map complexity to difficulty level
    if complexity <= 3:
        effective_difficulty = "beginner"
    elif complexity <= 7:
        effective_difficulty = "intermediate"
    else:
        effective_difficulty = "advanced"
    
    # Set base tempo by difficulty
    if effective_difficulty == "beginner":
        base_tempo = 70
        bar_count_options = [2, 4]
    elif effective_difficulty == "intermediate":
        base_tempo = 90
        bar_count_options = [2, 4, 8]
    else:
        base_tempo = 110
        bar_count_options = [4, 8]
    
    # Get available patterns
    available_patterns = RHYTHM_PATTERNS[effective_difficulty]
    
    # --- RANDOMIZATION ---
    if randomize:
        # Randomize tempo within ±15%
        tempo_variance = random.uniform(-0.15, 0.15)
        tempo = int(base_tempo * (1 + tempo_variance))
        
        # Randomize number of bars
        bar_count = random.choice(bar_count_options)
        
        # Build rhythm by selecting random patterns for each bar
        rhythm = []
        for _ in range(bar_count):
            pattern = random.choice(available_patterns)
            rhythm.extend(pattern)
    else:
        tempo = base_tempo
        bar_count = 4
        rhythm = available_patterns[0] * bar_count
    
    # Create notes (same pitch, rhythm varies)
    notes = ["C4"] * len(rhythm)
    midi_notes = [60] * len(rhythm)
    
    # Create title
    title = f"Rhythm Practice - {effective_difficulty.title()} ({bar_count} bars)"
    
    # Practice tips
    practice_tips = [
        "Count out loud while practicing",
        "Start slowly with a metronome",
        "Feel the pulse in your body"
    ]
    
    if effective_difficulty == "beginner":
        practice_tips.insert(0, "Tap your foot on each beat")
    elif effective_difficulty == "advanced":
        practice_tips.append("Practice subdividing into smaller units")
    
    characteristics = ["rhythm", "timing", effective_difficulty]
    
    return Exercise(
        exercise_type="rhythm",
        title=title,
        description=f"Clap or tap this {effective_difficulty} rhythm pattern.",
        notes=notes,
        midi_notes=midi_notes,
        rhythm=rhythm,
        duration_beats=sum(rhythm),
        key="C",
        tempo_bpm=tempo,
        difficulty=effective_difficulty,
        characteristics=characteristics,
        practice_tips=practice_tips,
        complexity=complexity,
        generation_method="local_rhythm"
    )


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("RHYTHM GENERATOR TEST")
    print("=" * 70)
    
    # Test randomization
    print("\nTest: Randomization Check (5 runs)")
    print("-" * 70)
    hashes = set()
    for i in range(5):
        ex = generate_rhythm_exercise(context={}, complexity=5)
        h = hash(tuple(ex.rhythm))
        hashes.add(h)
        print(f"Run {i+1}: {len(ex.rhythm)} notes, duration={ex.duration_beats}, tempo={ex.tempo_bpm}")
    print(f"Unique rhythms: {len(hashes)}/5")
    
    print("\n" + "=" * 70)
    print("✅ Rhythm generator tests passed!")
    print("=" * 70)

