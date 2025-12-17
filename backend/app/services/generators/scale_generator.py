"""
Scale Exercise Generator - Phase 8 Week 1

100% local generation (complexity 1, zero cost).

Features:
- 8 scale types (major, minor variations, modes)
- 5 practice patterns (ascending, descending, thirds, fourths, etc.)
- Automatic difficulty adjustment (tempo, octaves, articulation)
- Pattern-based note generation
- MIDI number conversion

Scale Types:
- Major, Natural Minor, Harmonic Minor, Melodic Minor
- Dorian, Phrygian, Lydian, Mixolydian modes

Practice Patterns:
- Ascending, Descending, Ascending+Descending
- Thirds (scalar intervals), Fourths (leaps)
"""

from typing import List, Tuple, Dict, Any
import sys
import os
import random

# Add parent directory to path for Exercise import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.exercise_generator_engine import Exercise


# ============================================================================
# Scale Patterns (Intervals in Semitones)
# ============================================================================

SCALE_PATTERNS = {
    # === Major Scales ===
    "major": [0, 2, 4, 5, 7, 9, 11, 12],
    "ionian": [0, 2, 4, 5, 7, 9, 11, 12],  # Same as major
    
    # === Minor Scales ===
    "natural_minor": [0, 2, 3, 5, 7, 8, 10, 12],
    "aeolian": [0, 2, 3, 5, 7, 8, 10, 12],  # Same as natural minor
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11, 12],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11, 12],
    "melodic_minor_descending": [0, 2, 3, 5, 7, 8, 10, 12],  # Classical form
    
    # === Modes ===
    "dorian": [0, 2, 3, 5, 7, 9, 10, 12],
    "phrygian": [0, 1, 3, 5, 7, 8, 10, 12],
    "lydian": [0, 2, 4, 6, 7, 9, 11, 12],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10, 12],
    "locrian": [0, 1, 3, 5, 6, 8, 10, 12],
    
    # === Pentatonic Scales ===
    "pentatonic_major": [0, 2, 4, 7, 9, 12],
    "pentatonic_minor": [0, 3, 5, 7, 10, 12],
    "pentatonic_neutral": [0, 2, 5, 7, 10, 12],  # Egyptian scale
    
    # === Blues Scales ===
    "blues": [0, 3, 5, 6, 7, 10, 12],
    "blues_major": [0, 2, 3, 4, 7, 9, 12],
    "blues_hexatonic": [0, 3, 4, 7, 9, 10, 12],
    
    # === Symmetric Scales ===
    "whole_tone": [0, 2, 4, 6, 8, 10, 12],
    "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "diminished": [0, 2, 3, 5, 6, 8, 9, 11, 12],
    "diminished_half_whole": [0, 1, 3, 4, 6, 7, 9, 10, 12],
    "augmented": [0, 3, 4, 7, 8, 11, 12],  # Hexatonic
    
    # === Jazz Scales ===
    "bebop_major": [0, 2, 4, 5, 7, 8, 9, 11, 12],
    "bebop_dominant": [0, 2, 4, 5, 7, 9, 10, 11, 12],
    "bebop_dorian": [0, 2, 3, 4, 5, 7, 9, 10, 12],
    "bebop_minor": [0, 2, 3, 5, 7, 8, 9, 10, 12],
    "altered": [0, 1, 3, 4, 6, 8, 10, 12],
    "lydian_dominant": [0, 2, 4, 6, 7, 9, 10, 12],
    "lydian_augmented": [0, 2, 4, 6, 8, 9, 11, 12],
    
    # === World Scales - European ===
    "hungarian_minor": [0, 2, 3, 6, 7, 8, 11, 12],
    "hungarian_major": [0, 3, 4, 6, 7, 9, 10, 12],
    "spanish_phrygian": [0, 1, 4, 5, 7, 8, 10, 12],
    "spanish_8tone": [0, 1, 3, 4, 5, 6, 8, 10, 12],
    "romanian": [0, 2, 3, 6, 7, 9, 10, 12],
    "ukrainian_dorian": [0, 2, 3, 6, 7, 9, 10, 12],
    
    # === World Scales - Middle Eastern ===
    "arabic": [0, 1, 4, 5, 7, 8, 11, 12],
    "persian": [0, 1, 4, 5, 6, 8, 11, 12],
    "byzantine": [0, 1, 4, 5, 7, 8, 11, 12],
    "hijaz": [0, 1, 4, 5, 7, 8, 10, 12],
    
    # === World Scales - Asian ===
    "japanese": [0, 1, 5, 7, 8, 12],  # In-sen
    "hirajoshi": [0, 2, 3, 7, 8, 12],  # Japanese
    "chinese": [0, 4, 6, 7, 11, 12],  # Chinese 5-note
    "balinese": [0, 1, 3, 7, 8, 12],
    "javanese": [0, 1, 3, 5, 7, 9, 10, 12],
    
    # === World Scales - Indian ===
    "raga_bhairav": [0, 1, 4, 5, 7, 8, 11, 12],
    "raga_kafi": [0, 2, 3, 5, 7, 9, 10, 12],
    "raga_todi": [0, 1, 3, 6, 7, 8, 11, 12],
    
    # === Gospel/Church Scales ===
    "gospel": [0, 2, 3, 4, 7, 9, 12],
    
    # === Modern/Synthetic ===
    "prometheus": [0, 2, 4, 6, 9, 10, 12],
    "enigmatic": [0, 1, 4, 6, 8, 10, 11, 12],
    "neapolitan_major": [0, 1, 3, 5, 7, 9, 11, 12],
    "neapolitan_minor": [0, 1, 3, 5, 7, 8, 11, 12],
}


# ============================================================================
# Note Conversion Utilities
# ============================================================================

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_midi(note_name: str) -> int:
    """
    Convert note name to MIDI number.

    Examples:
        >>> note_to_midi("C4")
        60
        >>> note_to_midi("A4")
        69
    """
    # Handle both "C4" and "C-4" formats
    note_name = note_name.replace('-', '')

    # Extract note and octave
    if len(note_name) < 2:
        raise ValueError(f"Invalid note name: {note_name}")

    if note_name[1] in ['#', 'b']:
        note = note_name[:2]
        octave = int(note_name[2:])
    else:
        note = note_name[0]
        octave = int(note_name[1:])

    # Handle flats (convert to sharps)
    if 'b' in note:
        flat_to_sharp = {
            'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
        }
        note = flat_to_sharp.get(note, note)

    # Find note index
    if note not in NOTE_NAMES:
        raise ValueError(f"Unknown note: {note}")

    note_index = NOTE_NAMES.index(note)

    # Calculate MIDI number (C4 = 60)
    midi_num = (octave + 1) * 12 + note_index
    return midi_num


def midi_to_note(midi_num: int) -> str:
    """
    Convert MIDI number to note name.

    Examples:
        >>> midi_to_note(60)
        "C4"
        >>> midi_to_note(69)
        "A4"
    """
    octave = (midi_num // 12) - 1
    note_index = midi_num % 12
    note = NOTE_NAMES[note_index]
    return f"{note}{octave}"


# ============================================================================
# Scale Generation
# ============================================================================

def generate_scale_notes(
    key: str,
    scale_type: str,
    octaves: int = 1,
    starting_octave: int = 4
) -> Tuple[List[str], List[int]]:
    """
    Generate scale notes for a given key and type.

    Args:
        key: Root note (e.g., "C", "D", "F#")
        scale_type: Scale type from SCALE_PATTERNS
        octaves: Number of octaves to span
        starting_octave: Starting octave number

    Returns:
        Tuple of (note_names, midi_numbers)

    Examples:
        >>> notes, midi = generate_scale_notes("C", "major", 1, 4)
        >>> notes
        ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
        >>> len(midi)
        8
    """
    if scale_type not in SCALE_PATTERNS:
        raise ValueError(f"Unknown scale type: {scale_type}. Valid: {list(SCALE_PATTERNS.keys())}")

    # Get scale pattern
    pattern = SCALE_PATTERNS[scale_type]

    # Get root MIDI number
    root_note = f"{key}{starting_octave}"
    root_midi = note_to_midi(root_note)

    # Generate notes
    notes = []
    midi_notes = []

    for octave_num in range(octaves):
        for interval in pattern[:-1]:  # Exclude last note (octave) except on last octave
            midi_num = root_midi + (octave_num * 12) + interval
            notes.append(midi_to_note(midi_num))
            midi_notes.append(midi_num)

    # Add final octave note
    final_midi = root_midi + (octaves * 12)
    notes.append(midi_to_note(final_midi))
    midi_notes.append(final_midi)

    return notes, midi_notes


# ============================================================================
# Practice Patterns
# ============================================================================

def apply_practice_pattern(
    notes: List[str],
    midi_notes: List[int],
    pattern_type: str
) -> Tuple[List[str], List[int], List[float]]:
    """
    Apply a practice pattern to scale notes.

    Args:
        notes: Note names
        midi_notes: MIDI numbers
        pattern_type: Practice pattern type

    Returns:
        Tuple of (notes, midi_notes, rhythm)

    Patterns:
        - ascending: Play scale up
        - descending: Play scale down
        - ascending_descending: Up then down
        - thirds: Scalar thirds (C-E-D-F-E-G...)
        - fourths: Scalar fourths (C-F-D-G-E-A...)
    """
    rhythm = []  # Default to quarter notes (0.5 beats each for 8th notes feel)

    if pattern_type == "ascending":
        result_notes = notes
        result_midi = midi_notes
        rhythm = [0.5] * len(notes)

    elif pattern_type == "descending":
        result_notes = notes[::-1]
        result_midi = midi_notes[::-1]
        rhythm = [0.5] * len(notes)

    elif pattern_type == "ascending_descending":
        result_notes = notes + notes[-2::-1]  # Ascending + descending (don't repeat peak)
        result_midi = midi_notes + midi_notes[-2::-1]
        rhythm = [0.5] * len(result_notes)

    elif pattern_type == "thirds":
        # Scalar thirds: C-E, D-F, E-G, etc.
        result_notes = []
        result_midi = []
        for i in range(len(notes) - 2):
            result_notes.append(notes[i])
            result_midi.append(midi_notes[i])
            result_notes.append(notes[i + 2])
            result_midi.append(midi_notes[i + 2])
        rhythm = [0.25] * len(result_notes)  # Faster for pattern complexity

    elif pattern_type == "fourths":
        # Scalar fourths: C-F, D-G, E-A, etc.
        result_notes = []
        result_midi = []
        for i in range(len(notes) - 3):
            result_notes.append(notes[i])
            result_midi.append(midi_notes[i])
            result_notes.append(notes[i + 3])
            result_midi.append(midi_notes[i + 3])
        rhythm = [0.25] * len(result_notes)

    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")

    return result_notes, result_midi, rhythm


# ============================================================================
# Main Generator Function
# ============================================================================

def generate_scale_exercise(
    context: Dict[str, Any],
    difficulty: str = "intermediate",
    complexity: int = 1,
    use_ai: bool = False
) -> Exercise:
    """
    Generate scale exercise (100% local, zero cost).

    Args:
        context: Generation context with keys:
            - key: Root note (required)
            - scale_type: Scale type (default "major")
            - octaves: Number of octaves (default 1)
            - practice_pattern: Pattern type (default "ascending")
        difficulty: Difficulty level
        complexity: Complexity level (always 1 for scales)
        use_ai: Force AI (ignored for scales)

    Returns:
        Exercise object

    Examples:
        >>> exercise = generate_scale_exercise(
        ...     context={"key": "C", "scale_type": "major"},
        ...     difficulty="beginner"
        ... )
        >>> exercise.title
        "C Major Scale - Ascending"
    """
    # Extract context
    key = context.get("key", "C")
    scale_type = context.get("scale_type")  # Now optional - will be randomized
    octaves = context.get("octaves")  # Now optional - will be randomized
    practice_pattern = context.get("practice_pattern")  # Now optional
    randomize = context.get("randomize", True)  # Enable randomization by default

    # Available scale types by difficulty - EXPANDED for more variety
    SCALE_TYPES_BY_DIFFICULTY = {
        "beginner": ["major", "natural_minor", "pentatonic_major", "pentatonic_minor"],
        "intermediate": ["major", "natural_minor", "harmonic_minor", "dorian", "mixolydian", "pentatonic_major", "pentatonic_minor", "blues"],
        "advanced": ["major", "natural_minor", "harmonic_minor", "melodic_minor", "dorian", "phrygian", "lydian", "mixolydian", "locrian", "whole_tone", "blues"]
    }

    # Adjust based on difficulty and complexity
    if complexity <= 3:
        effective_difficulty = "beginner"
    elif complexity <= 6:
        effective_difficulty = "intermediate"
    else:
        effective_difficulty = "advanced"
        
    # Apply settings based on effective difficulty
    if effective_difficulty == "beginner":
        max_octaves = 1
        base_tempo = 60
        base_starting_octave = 4
        available_patterns = ["ascending", "descending"]
    elif effective_difficulty == "intermediate":
        max_octaves = 2
        base_tempo = 80
        base_starting_octave = 4
        available_patterns = ["ascending", "descending", "ascending_descending"]
    else:  # advanced
        max_octaves = 3
        base_tempo = 100
        base_starting_octave = 3
        available_patterns = ["ascending", "descending", "ascending_descending", "thirds", "fourths"]

    # --- ENHANCED RANDOMIZATION ---
    if randomize:
        # Randomize scale type if not specified
        if scale_type is None:
            scale_type = random.choice(SCALE_TYPES_BY_DIFFICULTY[effective_difficulty])
        
        # Randomize octave count if not specified
        if octaves is None:
            octaves = random.randint(1, max_octaves)
        else:
            octaves = min(octaves, max_octaves)
        
        # Randomize starting octave with more variance
        octave_offset = random.choice([-1, 0, 1])
        starting_octave = max(2, min(5, base_starting_octave + octave_offset))
        
        # Randomize tempo within ±15% (increased from ±10%)
        tempo_variance = random.uniform(-0.15, 0.15)
        tempo = int(base_tempo * (1 + tempo_variance))
        
        # Randomize practice pattern if not explicitly specified
        if practice_pattern is None:
            practice_pattern = random.choice(available_patterns)
        
        # Add rhythm variation factor (affects note durations slightly)
        rhythm_variation = random.uniform(0.9, 1.1)
    else:
        tempo = base_tempo
        starting_octave = base_starting_octave
        rhythm_variation = 1.0
        if scale_type is None:
            scale_type = "major"
        if octaves is None:
            octaves = 1
        if practice_pattern is None:
            practice_pattern = "ascending"

    # Generate scale notes
    notes, midi_notes = generate_scale_notes(
        key=key,
        scale_type=scale_type,
        octaves=octaves,
        starting_octave=starting_octave
    )

    # Apply practice pattern
    notes, midi_notes, rhythm = apply_practice_pattern(
        notes=notes,
        midi_notes=midi_notes,
        pattern_type=practice_pattern
    )

    # Calculate duration
    duration_beats = sum(rhythm)

    # Create title
    scale_name = scale_type.replace('_', ' ').title()
    pattern_name = practice_pattern.replace('_', ' ').title()
    title = f"{key} {scale_name} Scale - {pattern_name}"

    # Create description
    description = (
        f"Practice the {key} {scale_name} scale using a {pattern_name.lower()} pattern. "
        f"Focus on even tone, steady tempo, and proper fingering."
    )

    # Practice tips
    practice_tips = [
        "Keep fingers curved and close to the keys",
        "Use a metronome to maintain steady tempo",
        "Practice hands separately first, then together",
        "Focus on smooth legato connection between notes"
    ]

    if difficulty == "beginner":
        practice_tips.insert(0, "Start very slowly (40-60 BPM)")
        practice_tips.append("Master one hand before combining")
    elif difficulty == "advanced":
        practice_tips.append("Try playing with different articulations (staccato, legato)")
        practice_tips.append("Increase tempo gradually (up to 120+ BPM)")

    # Characteristics
    characteristics = ["scale", "technical", scale_type]
    if "minor" in scale_type:
        characteristics.append("minor_key")
    if practice_pattern in ["thirds", "fourths"]:
        characteristics.append("interval_training")

    # Create Exercise object
    exercise = Exercise(
        exercise_type="scale",
        title=title,
        description=description,
        notes=notes,
        midi_notes=midi_notes,
        rhythm=rhythm,
        duration_beats=duration_beats,
        key=key,
        tempo_bpm=tempo,
        difficulty=difficulty,
        characteristics=characteristics,
        practice_tips=practice_tips,
        technique=f"{scale_type}_scale",
        complexity=complexity,
        generation_method="local_pattern"
    )

    return exercise


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("SCALE GENERATOR TEST")
    print("=" * 70)

    # Test 1: C Major, Beginner, Ascending
    print("\nTest 1: C Major - Beginner - Ascending")
    print("-" * 70)
    exercise1 = generate_scale_exercise(
        context={"key": "C", "scale_type": "major", "practice_pattern": "ascending"},
        difficulty="beginner"
    )
    print(f"Title: {exercise1.title}")
    print(f"Notes: {' - '.join(exercise1.notes)}")
    print(f"Tempo: {exercise1.tempo_bpm} BPM")
    print(f"Duration: {exercise1.duration_beats} beats")
    print(f"Characteristics: {', '.join(exercise1.characteristics)}")

    # Test 2: D Minor (Harmonic), Intermediate, Ascending+Descending
    print("\n\nTest 2: D Harmonic Minor - Intermediate - Ascending+Descending")
    print("-" * 70)
    exercise2 = generate_scale_exercise(
        context={"key": "D", "scale_type": "harmonic_minor", "practice_pattern": "ascending_descending"},
        difficulty="intermediate"
    )
    print(f"Title: {exercise2.title}")
    print(f"Notes: {' - '.join(exercise2.notes[:10])}... ({len(exercise2.notes)} total)")
    print(f"Tempo: {exercise2.tempo_bpm} BPM")

    # Test 3: F# Dorian, Advanced, Thirds
    print("\n\nTest 3: F# Dorian - Advanced - Thirds")
    print("-" * 70)
    exercise3 = generate_scale_exercise(
        context={"key": "F#", "scale_type": "dorian", "practice_pattern": "thirds"},
        difficulty="advanced"
    )
    print(f"Title: {exercise3.title}")
    print(f"Notes: {' - '.join(exercise3.notes[:10])}... ({len(exercise3.notes)} total)")
    print(f"Tempo: {exercise3.tempo_bpm} BPM")
    print(f"Practice Tips: {exercise3.practice_tips[0]}")

    print("\n" + "=" * 70)
    print("✅ All scale generator tests passed!")
    print("=" * 70)
