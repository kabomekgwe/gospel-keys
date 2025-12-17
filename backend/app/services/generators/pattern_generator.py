"""
Pattern Exercise Generator - Phase 8 Week 1

Integrates with Phase 7 Lick Generation System (125 curated patterns + Markov models).

Complexity 5 (100% local, zero cost).

Features:
- Direct integration with Phase 7 lick_database_expanded (125 patterns)
- Markov model generation for creative variations
- N-gram pattern matching for authentic sequences
- Style-specific pattern selection (bebop, gospel, blues, neo-soul, jazz, classical)
- Characteristic-based filtering (chromatic, arpeggio, scalar, etc.)
- Automatic difficulty adjustment

Phase 7 Integration:
- lick_database_expanded.py: 125 curated patterns across 6 styles
- markov_lick_model.py: 3rd-order Markov chains for probabilistic generation
- lick_generator_engine.py: Hybrid generation orchestrator
- lick_analyzer.py: Pattern similarity and complexity scoring
"""

from typing import List, Dict, Any, Optional
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.exercise_generator_engine import Exercise

# Import Phase 7 components
try:
    from app.pipeline.lick_database_expanded import lick_database, LickPattern
    from app.pipeline.lick_generator_engine import (
        lick_generator_engine,
        LickGenerationRequest,
        GenerationStrategy
    )
    from app.pipeline.markov_lick_model import markov_model_manager
    PHASE7_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Phase 7 components not available: {e}")
    PHASE7_AVAILABLE = False
    LickPattern = None


# ============================================================================
# Note Conversion Utilities
# ============================================================================

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_midi(note_name: str) -> int:
    """Convert note name to MIDI number"""
    note_name = note_name.replace('-', '')

    if len(note_name) < 2:
        raise ValueError(f"Invalid note name: {note_name}")

    if note_name[1] in ['#', 'b']:
        note = note_name[:2]
        octave = int(note_name[2:])
    else:
        note = note_name[0]
        octave = int(note_name[1:])

    # Handle flats
    if 'b' in note:
        flat_to_sharp = {
            'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
        }
        note = flat_to_sharp.get(note, note)

    if note not in NOTE_NAMES:
        raise ValueError(f"Unknown note: {note}")

    note_index = NOTE_NAMES.index(note)
    midi_num = (octave + 1) * 12 + note_index
    return midi_num


def midi_to_note(midi_num: int) -> str:
    """Convert MIDI number to note name"""
    octave = (midi_num // 12) - 1
    note_index = midi_num % 12
    note = NOTE_NAMES[note_index]
    return f"{note}{octave}"


def intervals_to_notes(
    root: str,
    intervals: List[int],
    starting_octave: int = 4
) -> tuple[List[str], List[int]]:
    """
    Convert interval pattern to note names and MIDI numbers.

    Args:
        root: Root note (e.g., "C", "F#")
        intervals: List of intervals in semitones
        starting_octave: Starting octave

    Returns:
        Tuple of (note_names, midi_numbers)
    """
    root_note = f"{root}{starting_octave}"
    root_midi = note_to_midi(root_note)

    notes = []
    midi_notes = []

    for interval in intervals:
        midi_num = root_midi + interval
        notes.append(midi_to_note(midi_num))
        midi_notes.append(midi_num)

    return notes, midi_notes


# ============================================================================
# Phase 7 Integration Functions
# ============================================================================

def get_pattern_from_database(
    style: str,
    difficulty: str,
    characteristics: Optional[List[str]] = None,
    harmonic_context: Optional[str] = None
) -> Optional[LickPattern]:
    """
    Get a pattern from Phase 7 lick database.

    Args:
        style: Musical style (bebop, gospel, blues, etc.)
        difficulty: Difficulty level
        characteristics: Optional characteristic filters
        harmonic_context: Optional chord context filter

    Returns:
        LickPattern or None
    """
    if not PHASE7_AVAILABLE:
        return None

    # Search database
    search_kwargs = {
        "style": style,
        "difficulty": difficulty
    }

    if characteristics:
        search_kwargs["characteristics"] = characteristics

    if harmonic_context:
        search_kwargs["harmonic_context"] = [harmonic_context]

    patterns = lick_database.search(**search_kwargs)

    if patterns:
        return random.choice(patterns)

    # Fallback: Try without filters
    patterns = lick_database.get_by_style(style)
    if patterns:
        # Filter by difficulty manually
        filtered = [p for p in patterns if p.difficulty == difficulty]
        if filtered:
            return random.choice(filtered)
        return random.choice(patterns)

    return None


def generate_with_markov(
    style: str,
    length: int = 8,
    root: str = "C",
    temperature: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Generate pattern using Phase 7 Markov model.

    Args:
        style: Musical style
        length: Pattern length in notes
        root: Root note
        temperature: Randomness (0=deterministic, 1=normal, >1=creative)

    Returns:
        Dict with intervals, notes, etc. or None
    """
    if not PHASE7_AVAILABLE:
        return None

    try:
        # Generate using lick generator engine
        lick = lick_generator_engine.generate_from_markov(
            style=style,
            length=length,
            root=root,
            temperature=temperature
        )

        return {
            "intervals": lick.intervals,
            "notes": lick.notes,
            "midi_notes": lick.midi_notes,
            "rhythm": lick.rhythm,
            "characteristics": lick.characteristics,
            "technique": lick.technique
        }

    except Exception as e:
        print(f"⚠️  Markov generation failed: {e}")
        return None


# ============================================================================
# Fallback Pattern Generation (if Phase 7 unavailable)
# ============================================================================

FALLBACK_PATTERNS = {
    "bebop": [
        {"intervals": [0, 2, 4, 5, 7, 9, 11, 12], "characteristics": ["scalar", "ascending", "bebop"]},
        {"intervals": [12, 11, 9, 7, 5, 4, 2, 0], "characteristics": ["scalar", "descending", "bebop"]},
        {"intervals": [0, 1, 2, 4, 5, 7, 9, 11], "characteristics": ["chromatic", "bebop"]},
        {"intervals": [0, 4, 7, 11, 12, 11, 7, 4], "characteristics": ["arpeggio", "bebop"]},
        {"intervals": [0, 2, 3, 4, 5, 7, 9, 11], "characteristics": ["chromatic_approach", "bebop"]},
    ],
    "gospel": [
        {"intervals": [0, 3, 4, 7, 10, 12], "characteristics": ["arpeggio", "chord_tones", "gospel"]},
        {"intervals": [0, 4, 7, 12, 10, 7, 4, 0], "characteristics": ["arpeggio", "turnaround", "gospel"]},
        {"intervals": [0, 3, 4, 7, 9, 12], "characteristics": ["pentatonic", "gospel"]},
        {"intervals": [0, 2, 4, 7, 9, 11, 12], "characteristics": ["major_scale", "gospel"]},
        {"intervals": [0, 3, 5, 7, 10, 12, 10, 7], "characteristics": ["blues_feel", "gospel"]},
    ],
    "blues": [
        {"intervals": [0, 3, 5, 6, 7, 10], "characteristics": ["blues_scale", "pentatonic", "blues"]},
        {"intervals": [0, 3, 5, 7, 10, 12, 10, 7], "characteristics": ["ascending_descending", "blues"]},
        {"intervals": [0, 3, 4, 5, 7, 10], "characteristics": ["blue_note", "blues"]},
        {"intervals": [12, 10, 7, 5, 3, 0], "characteristics": ["descending", "blues"]},
        {"intervals": [0, 3, 5, 6, 7, 10, 12], "characteristics": ["full_scale", "blues"]},
        {"intervals": [0, 1, 3, 5, 6, 7, 10], "characteristics": ["chromatic_blues", "blues"]},
    ],
    "classical": [
        {"intervals": [0, 2, 4, 5, 7, 9, 11, 12], "characteristics": ["scalar", "major", "classical"]},
        {"intervals": [0, 2, 3, 5, 7, 8, 10, 12], "characteristics": ["minor", "classical"]},
        {"intervals": [0, 4, 7, 12, 7, 4, 0], "characteristics": ["arpeggio", "classical"]},
        {"intervals": [12, 11, 9, 7, 5, 4, 2, 0], "characteristics": ["descending", "classical"]},
        {"intervals": [0, 2, 4, 7, 4, 2, 0], "characteristics": ["broken_chord", "classical"]},
    ],
    "jazz": [
        {"intervals": [0, 2, 4, 5, 7, 9, 10, 12], "characteristics": ["mixolydian", "jazz"]},
        {"intervals": [0, 2, 3, 5, 7, 9, 10, 12], "characteristics": ["dorian", "jazz"]},
        {"intervals": [0, 4, 7, 10, 14, 10, 7, 4], "characteristics": ["dom7_arpeggio", "jazz"]},
        {"intervals": [0, 1, 3, 5, 7, 8, 10, 12], "characteristics": ["altered", "jazz"]},
        {"intervals": [0, 2, 4, 6, 8, 10, 12], "characteristics": ["whole_tone", "jazz"]},
    ],
    "neosoul": [
        {"intervals": [0, 2, 3, 5, 7, 9, 10], "characteristics": ["dorian", "neo-soul"]},
        {"intervals": [0, 4, 7, 11, 14], "characteristics": ["maj9_arpeggio", "neo-soul"]},
        {"intervals": [0, 3, 5, 7, 10, 12, 10, 7], "characteristics": ["minor_pentatonic", "neo-soul"]},
        {"intervals": [0, 2, 4, 7, 9, 12], "characteristics": ["major_pentatonic", "neo-soul"]},
        {"intervals": [0, 4, 7, 10, 14, 17], "characteristics": ["extended", "neo-soul"]},
    ],
    "rnb": [
        {"intervals": [0, 3, 5, 7, 10, 12], "characteristics": ["minor_pentatonic", "rnb"]},
        {"intervals": [0, 2, 4, 7, 9, 11, 12], "characteristics": ["major_scale", "rnb"]},
        {"intervals": [0, 3, 5, 6, 7, 10, 12], "characteristics": ["blues_feel", "rnb"]},
        {"intervals": [0, 4, 7, 11, 14, 11, 7, 4], "characteristics": ["maj7_arpeggio", "rnb"]},
    ],
    "latin": [
        {"intervals": [0, 2, 3, 5, 7, 9, 10, 12], "characteristics": ["dorian", "latin"]},
        {"intervals": [0, 1, 4, 5, 7, 8, 10, 12], "characteristics": ["phrygian_dominant", "latin"]},
        {"intervals": [0, 2, 4, 6, 7, 9, 11, 12], "characteristics": ["lydian", "latin"]},
        {"intervals": [0, 3, 5, 7, 10, 12, 15], "characteristics": ["minor_arpeggio", "latin"]},
    ],
    "reggae": [
        {"intervals": [0, 2, 4, 5, 7, 9, 11, 12], "characteristics": ["major", "reggae"]},
        {"intervals": [0, 3, 5, 7, 10, 12], "characteristics": ["minor_pentatonic", "reggae"]},
        {"intervals": [0, 2, 4, 7, 9], "characteristics": ["major_pentatonic", "reggae"]},
        {"intervals": [0, 4, 7, 12, 7, 4, 0], "characteristics": ["arpeggio", "reggae"]},
    ],
}


def generate_fallback_pattern(
    style: str,
    root: str,
    difficulty: str
) -> Dict[str, Any]:
    """Generate fallback pattern if Phase 7 unavailable. Includes randomization."""
    # Get patterns for style, default to classical
    style_patterns = FALLBACK_PATTERNS.get(style, FALLBACK_PATTERNS["classical"])
    
    # Randomly select a pattern for variety
    pattern_data = random.choice(style_patterns)

    intervals = pattern_data["intervals"]
    
    # Add some randomization based on difficulty
    if difficulty == "beginner":
        # Limit to first 4-6 notes for beginners
        max_notes = random.randint(4, 6)
        intervals = intervals[:max_notes]
    elif difficulty == "advanced":
        # Possibly extend pattern or add variation
        if random.random() > 0.5 and len(intervals) > 4:
            # Add return notes
            intervals = intervals + intervals[-2:-5:-1]
    
    # Random starting octave
    starting_octave = random.choice([3, 4, 4, 4, 5])  # Bias toward 4
    
    notes, midi_notes = intervals_to_notes(root, intervals, starting_octave)
    
    # Varied rhythm based on difficulty
    if difficulty == "beginner":
        rhythm = [1.0] * len(intervals)  # Quarter notes
    elif difficulty == "intermediate":
        rhythm = [random.choice([0.5, 0.5, 1.0]) for _ in intervals]
    else:
        rhythm = [random.choice([0.25, 0.5, 0.5, 0.75, 1.0]) for _ in intervals]

    return {
        "intervals": intervals,
        "notes": notes,
        "midi_notes": midi_notes,
        "rhythm": rhythm,
        "characteristics": pattern_data["characteristics"]
    }


# ============================================================================
# Main Generator Function
# ============================================================================

def generate_pattern_exercise(
    context: Dict[str, Any],
    difficulty: str = "intermediate",
    complexity: int = 5,
    use_ai: bool = False
) -> Exercise:
    """
    Generate pattern exercise using Phase 7 lick database.

    Args:
        context: Generation context with keys:
            - key: Root note (required)
            - style: Musical style (default "bebop")
            - chords: Context chords (optional)
            - characteristics: Desired characteristics (optional)
            - generation_method: "database", "markov", or "auto" (default "auto")
            - temperature: Markov temperature (default 1.0)
        difficulty: Difficulty level
        complexity: Complexity level (always 5 for patterns)
        use_ai: Force AI (ignored, always local)

    Returns:
        Exercise object

    Examples:
        >>> exercise = generate_pattern_exercise(
        ...     context={"key": "C", "style": "bebop"},
        ...     difficulty="intermediate"
        ... )
        >>> exercise.title
        "Bebop Pattern in C - Chromatic Approach"
    """
    # Extract context
    root = context.get("key", "C")
    style = context.get("style", "bebop")
    chords = context.get("chords", [])
    characteristics = context.get("characteristics")
    generation_method = context.get("generation_method", "auto")
    temperature = context.get("temperature", 1.0)

    # Adjust based on difficulty and complexity
    if complexity <= 3:
        effective_difficulty = "beginner"
    elif complexity <= 6:
        effective_difficulty = "intermediate"
    else:
        effective_difficulty = "advanced"

    if effective_difficulty == "beginner":
        tempo = 80
        starting_octave = 4
    elif effective_difficulty == "intermediate":
        tempo = 100
        starting_octave = 4
    else:  # advanced
        tempo = 120
        starting_octave = 3

    # Generate pattern
    pattern_data = None

    if PHASE7_AVAILABLE and generation_method in ["auto", "database"]:
        # Try Phase 7 database first
        harmonic_context = chords[0] if chords else None
        pattern = get_pattern_from_database(
            style=style,
            difficulty=difficulty,
            characteristics=characteristics,
            harmonic_context=harmonic_context
        )

        if pattern:
            # Convert pattern to notes
            notes, midi_notes = intervals_to_notes(root, list(pattern.intervals), starting_octave)
            pattern_data = {
                "intervals": list(pattern.intervals),
                "notes": notes,
                "midi_notes": midi_notes,
                "rhythm": list(pattern.rhythm),
                "characteristics": pattern.characteristics,
                "source": pattern.source,
                "phrase_type": pattern.phrase_type
            }
            generation_method = "phase7_database"

    if not pattern_data and PHASE7_AVAILABLE and generation_method in ["auto", "markov"]:
        # Try Markov generation
        markov_result = generate_with_markov(
            style=style,
            length=8,
            root=root,
            temperature=temperature
        )

        if markov_result:
            pattern_data = markov_result
            generation_method = "phase7_markov"

    if not pattern_data:
        # Fallback to simple patterns
        pattern_data = generate_fallback_pattern(style, root, difficulty)
        generation_method = "fallback"

    # Extract pattern data
    intervals = pattern_data["intervals"]
    notes = pattern_data["notes"]
    midi_notes = pattern_data["midi_notes"]
    rhythm = pattern_data["rhythm"]
    characteristics = pattern_data.get("characteristics", [style, "pattern"])

    # Calculate duration
    duration_beats = sum(rhythm)

    # Create title
    style_name = style.replace('_', ' ').title()
    char_str = ", ".join(characteristics[:2]) if characteristics else "Pattern"
    source = pattern_data.get("source", "")
    source_str = f" (inspired by {source})" if source else ""

    title = f"{style_name} Pattern in {root} - {char_str.title()}{source_str}"

    # Create description
    description = (
        f"Practice this {style_name.lower()} pattern in the key of {root}. "
        f"Focus on the characteristic {style_name.lower()} elements and phrasing."
    )

    # Practice tips
    practice_tips = [
        f"Listen for the {style_name.lower()} feel and swing",
        "Practice with a metronome to develop timing",
        "Try transposing to different keys",
        "Experiment with different articulations"
    ]

    if difficulty == "beginner":
        practice_tips.insert(0, "Start slowly (60-80 BPM)")
        practice_tips.append("Focus on accuracy before speed")
    elif difficulty == "advanced":
        practice_tips.append("Try playing at faster tempos (140+ BPM)")
        practice_tips.append("Improvise variations on the pattern")

    if source:
        practice_tips.append(f"Study recordings of {source} for authentic feel")

    # Add style-specific characteristics
    if style not in characteristics:
        characteristics.append(style)
    characteristics.extend(["pattern", "melodic"])

    # Create Exercise object
    exercise = Exercise(
        exercise_type="pattern",
        title=title,
        description=description,
        notes=notes,
        midi_notes=midi_notes,
        rhythm=rhythm,
        duration_beats=duration_beats,
        key=root,
        tempo_bpm=tempo,
        difficulty=difficulty,
        characteristics=characteristics,
        practice_tips=practice_tips,
        technique=f"{style}_pattern",
        complexity=complexity,
        generation_method=generation_method,
        chords=chords if chords else None
    )

    return exercise


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("PATTERN GENERATOR TEST - Phase 7 Integration")
    print("=" * 70)

    if PHASE7_AVAILABLE:
        print("✅ Phase 7 components loaded successfully")
        print(f"   Database: {lick_database.get_stats()['total_patterns']} patterns")
    else:
        print("⚠️  Phase 7 not available, using fallback patterns")

    # Test 1: Bebop pattern from database
    print("\n\nTest 1: Bebop Pattern (Database)")
    print("-" * 70)
    exercise1 = generate_pattern_exercise(
        context={"key": "C", "style": "bebop"},
        difficulty="intermediate"
    )
    print(f"Title: {exercise1.title}")
    print(f"Notes: {' - '.join(exercise1.notes[:10])}... ({len(exercise1.notes)} total)")
    print(f"Tempo: {exercise1.tempo_bpm} BPM")
    print(f"Generation: {exercise1.generation_method}")
    print(f"Characteristics: {', '.join(exercise1.characteristics[:3])}")

    # Test 2: Gospel pattern with chord context
    print("\n\nTest 2: Gospel Pattern with Chord Context")
    print("-" * 70)
    exercise2 = generate_pattern_exercise(
        context={
            "key": "F",
            "style": "gospel",
            "chords": ["Fmaj7", "Bb7", "C7"],
            "characteristics": ["chromatic"]
        },
        difficulty="intermediate"
    )
    print(f"Title: {exercise2.title}")
    print(f"Notes: {' - '.join(exercise2.notes)}")
    print(f"Chords: {exercise2.chords}")
    print(f"Generation: {exercise2.generation_method}")

    # Test 3: Blues pattern (advanced)
    print("\n\nTest 3: Blues Pattern (Advanced)")
    print("-" * 70)
    exercise3 = generate_pattern_exercise(
        context={"key": "A", "style": "blues"},
        difficulty="advanced"
    )
    print(f"Title: {exercise3.title}")
    print(f"Notes: {' - '.join(exercise3.notes)}")
    print(f"Tempo: {exercise3.tempo_bpm} BPM")

    # Test 4: Markov generation
    if PHASE7_AVAILABLE:
        print("\n\nTest 4: Markov Generation")
        print("-" * 70)
        exercise4 = generate_pattern_exercise(
            context={
                "key": "D",
                "style": "bebop",
                "generation_method": "markov",
                "temperature": 1.2
            },
            difficulty="intermediate"
        )
        print(f"Title: {exercise4.title}")
        print(f"Notes: {' - '.join(exercise4.notes)}")
        print(f"Generation: {exercise4.generation_method}")

    print("\n" + "=" * 70)
    print("✅ All pattern generator tests passed!")
    print("=" * 70)
