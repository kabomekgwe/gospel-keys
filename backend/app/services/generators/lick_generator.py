"""
Lick Exercise Generator - Phase 8 Week 1

Wraps the app.pipeline.lick_generator_engine to provide exercise generation.
Complexity 6 (Hybrid: 90% local rules, 10% AI enhancement).
"""

from typing import List, Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.exercise_generator_engine import Exercise
from app.pipeline.lick_generator_engine import (
    lick_generator_engine,
    LickGenerationRequest,
    GenerationStrategy,
    VariationType,
    Lick
)

def generate_lick_exercise(
    context: Dict[str, Any],
    difficulty: str = "intermediate",
    complexity: int = 6,
    use_ai: bool = False
) -> Exercise:
    """
    Generate lick exercise using LickGeneratorEngine.

    Args:
        context: Context dictionary
            - key: Root key (default "C")
            - style: Musical style (default "bebop")
            - chords: Context chords (optional)
            - strategy: GenerationStrategy (optional)
            - variation: VariationType (optional)
        difficulty: Difficulty level
        complexity: Complexity level (1-10)
        use_ai: Force AI usage

    Returns:
        Exercise object
    """
    # map complexity to difficulty if needed, 
    # but LickGeneratorEngine uses complexity internally too.
    # We'll pass both.
    
    key = context.get("key", "C")
    style = context.get("style", "bebop")
    chords = context.get("chords", [])
    
    # Create request
    request = LickGenerationRequest(
        style=style,
        difficulty=difficulty,
        context_chords=chords,
        key=key,
        generation_strategy=context.get("strategy", GenerationStrategy.AUTO),
        variation_type=context.get("variation", VariationType.STANDARD),
        use_ai_enhancement=use_ai or (complexity >= 8)
    )

    # Generate lick
    result = lick_generator_engine.generate_hybrid(request, use_ai=use_ai)
    lick = result.lick

    # Create description
    description = (
        f"Practice this {style} lick in {key}. "
        f"Focus on the {lick.technique or 'phrasing'}."
    )
    
    if result.source == "ai":
        description += " (AI Enhanced)"

    # Practice tips
    practice_tips = [
        "Listen to the phrasing carefully",
        "Practice slowly with a metronome",
        "Try to transpose this lick to other keys"
    ]

    return Exercise(
        exercise_type="lick",
        title=f"{style.title()} Lick in {key}",
        description=description,
        notes=lick.notes,
        midi_notes=lick.midi_notes,
        rhythm=lick.rhythm,
        duration_beats=lick.duration_beats,
        key=key,
        tempo_bpm=120, # Default, engine doesn't return tempo yet
        difficulty=difficulty,
        characteristics=lick.characteristics + [result.source],
        practice_tips=practice_tips,
        technique=lick.technique or f"{style}_lick",
        complexity=complexity,
        generation_method=f"lick_engine_{result.source}",
        chords=chords
    )

if __name__ == "__main__":
    print("="*50)
    print("LICK GENERATOR TEST")
    print("="*50)
    
    # Test 1: Simple Bebop Lick
    ex1 = generate_lick_exercise(
        context={"key": "C", "style": "bebop"},
        difficulty="intermediate"
    )
    print(f"Title: {ex1.title}")
    print(f"Notes: {ex1.notes}")
    print(f"Technique: {ex1.technique}")
    
    # Test 2: Context Aware
    ex2 = generate_lick_exercise(
        context={"key": "F", "style": "blues", "chords": ["F7", "Bb7"]},
        difficulty="advanced",
        complexity=8
    )
    print(f"\nTitle: {ex2.title}")
    print(f"Example 2 Source: {ex2.generation_method}")
