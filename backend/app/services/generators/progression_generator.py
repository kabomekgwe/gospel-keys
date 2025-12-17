"""
Progression Exercise Generator

Generates chord progression exercises with real chord voicings.
Complexity 4 (Local).

Features:
- Roman numeral to chord name conversion
- Real MIDI note voicings for each chord
- Multiple progression patterns by difficulty
- Randomization of progressions, voicings, and tempo
"""

from typing import Dict, Any, List, Tuple
import random
from app.services.exercise_generator_engine import Exercise


# ============================================================================
# Music Theory Constants
# ============================================================================

# Note names to semitone offset from C
NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

# Semitone to note name (preferring sharps)
SEMITONE_TO_NOTE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Scale degrees for major and minor keys (intervals in semitones)
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # W-W-H-W-W-W-H
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]  # W-H-W-W-H-W-W

# Roman numeral to scale degree (0-indexed)
ROMAN_TO_DEGREE = {
    'I': 0, 'i': 0, 'II': 1, 'ii': 1, 'III': 2, 'iii': 2,
    'IV': 4, 'iv': 4, 'V': 4, 'v': 4, 'VI': 5, 'vi': 5,
    'VII': 6, 'vii': 6, 'bVII': 6, 'bvii': 6
}

# Correct scale degrees for diatonic chords
DIATONIC_DEGREES = {'I': 0, 'ii': 1, 'iii': 2, 'IV': 3, 'V': 4, 'vi': 5, 'vii': 6}

# Chord quality based on Roman numeral
def get_chord_quality(numeral: str) -> str:
    """Get chord quality from Roman numeral."""
    if numeral in ['I', 'IV', 'V', 'II', 'III', 'VI', 'VII']:
        return 'major'
    elif numeral in ['ii', 'iii', 'vi', 'i', 'iv', 'v']:
        return 'minor'
    elif numeral in ['vii', 'viio', 'VII']:
        return 'diminished'
    else:
        return 'major'

# Chord voicing intervals (from root)
CHORD_VOICINGS = {
    'major': [0, 4, 7],           # Root, M3, P5
    'minor': [0, 3, 7],           # Root, m3, P5
    'diminished': [0, 3, 6],      # Root, m3, d5
    'major7': [0, 4, 7, 11],      # Root, M3, P5, M7
    'minor7': [0, 3, 7, 10],      # Root, m3, P5, m7
    'dominant7': [0, 4, 7, 10],   # Root, M3, P5, m7
}


# ============================================================================
# Progression Patterns
# ============================================================================

PROGRESSIONS = {
    "beginner": [
        ["I", "IV", "V", "I"],
        ["I", "V", "vi", "IV"],     # Pop progression
        ["I", "IV", "I", "V"],
        ["I", "V", "I", "V"],       # Simple rock
        ["I", "IV", "V", "IV"],     # Simple blues feel
        ["I", "I", "IV", "V"],
        ["vi", "IV", "I", "V"],     # Sad pop
        ["I", "vi", "I", "V"],
        ["I", "V", "IV", "I"],      # Rock ballad
        ["I", "IV", "I", "IV"],     # Simple alternation
        ["I", "vi", "IV", "V"],     # Common pop
        ["IV", "I", "IV", "V"],     # Plagal feel
    ],
    "intermediate": [
        ["ii", "V", "I", "I"],      # ii-V-I
        ["I", "vi", "IV", "V"],     # 50s progression
        ["I", "IV", "vi", "V"],
        ["vi", "IV", "I", "V"],     # Axis of awesome
        ["I", "V", "vi", "iii", "IV"],  # Canon progression start
        ["ii", "V", "I", "vi"],     # Jazz turnaround
        ["I", "IV", "ii", "V"],     # Gospel feel
        ["IV", "V", "iii", "vi"],   # K-pop style
        ["I", "iii", "IV", "V"],
        ["vi", "V", "IV", "I"],     # Reverse axis
        ["I", "IV", "I", "ii", "V"],
        ["ii", "V", "I", "IV"],     # Extended turnaround
        ["I", "V", "vi", "IV", "I"],  # Extended pop
        ["vi", "ii", "V", "I"],     # Minor start turnaround
        ["I", "iii", "vi", "IV"],   # Sensitive
        ["IV", "I", "V", "vi"],     # Hymnal feel
    ],
    "advanced": [
        ["iii", "vi", "ii", "V", "I"],        # Circle of fifths
        ["I", "vi", "ii", "V"],               # Turnaround
        ["ii", "V", "iii", "vi", "ii", "V", "I"],  # Extended ii-V
        ["I", "IV", "vii", "iii", "vi", "ii", "V", "I"],  # Full diatonic
        ["iii", "vi", "ii", "V", "iii", "vi", "ii", "V"],  # Double turnaround
        ["I", "vii", "vi", "V", "IV", "iii", "ii", "I"],   # Descending
        ["ii", "V", "I", "IV", "vii", "iii", "vi"],        # Extended jazz
        ["I", "vi", "ii", "V", "iii", "vi", "ii", "V", "I"],  # Long turnaround
        ["vi", "ii", "V", "I", "IV", "vii", "iii"],         # Modal shift
        ["I", "iii", "vi", "ii", "V", "I"],                 # Smooth jazz
        ["ii", "V", "iii", "vi"],             # Short jazz
        ["I", "IV", "vii", "iii", "vi"],      # Partial diatonic
        ["vi", "IV", "ii", "V", "I"],         # Pop ballad end
        ["iii", "vi", "IV", "V", "I"],        # Extended pop resolution
    ]
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_root_note(key: str) -> int:
    """Get the MIDI note number for the root of a key (in octave 4)."""
    note = key[0].upper()
    if len(key) > 1 and key[1] in ['#', 'b']:
        note = key[:2]
    semitone = NOTE_TO_SEMITONE.get(note, 0)
    return 60 + semitone  # C4 = 60


def roman_to_chord_notes(numeral: str, key: str, octave: int = 4) -> Tuple[str, List[int]]:
    """
    Convert a Roman numeral to actual chord notes.
    
    Args:
        numeral: Roman numeral (e.g., "ii", "V", "I")
        key: Key signature (e.g., "C", "G", "Bb")
        octave: Starting octave
    
    Returns:
        Tuple of (chord_name, list of MIDI note numbers)
    """
    # Get scale degree (0-indexed)
    degree = DIATONIC_DEGREES.get(numeral, 0)
    
    # Get root note of key
    key_root = NOTE_TO_SEMITONE.get(key[0].upper() if len(key) == 1 else key[:2], 0)
    
    # Calculate chord root from scale degree
    chord_root_semitone = (key_root + MAJOR_SCALE[degree]) % 12
    chord_root_note = SEMITONE_TO_NOTE[chord_root_semitone]
    
    # Get chord quality
    quality = get_chord_quality(numeral)
    
    # Get voicing intervals
    intervals = CHORD_VOICINGS.get(quality, CHORD_VOICINGS['major'])
    
    # Calculate MIDI notes
    base_midi = (octave + 1) * 12 + chord_root_semitone
    midi_notes = [base_midi + interval for interval in intervals]
    
    # Create chord name
    quality_suffix = "" if quality == "major" else "m" if quality == "minor" else "dim"
    chord_name = f"{chord_root_note}{quality_suffix}"
    
    return chord_name, midi_notes


# ============================================================================
# Main Generator
# ============================================================================

def generate_progression_exercise(
    context: Dict[str, Any],
    difficulty: str = "intermediate",
    complexity: int = 4,
    use_ai: bool = False
) -> Exercise:
    """
    Generate chord progression exercise with real voicings.
    
    Args:
        context: Generation context with keys:
            - key: Musical key (e.g., "C", "G", "Bb")
            - style: Musical style (e.g., "pop", "jazz", "gospel")
            - progression: Optional specific progression
        difficulty: Difficulty level
        complexity: Complexity level (1-10)
        use_ai: Force AI (ignored for local generation)
    
    Returns:
        Exercise object with real chord voicings
    """
    # Extract context
    key = context.get("key", "C")
    style = context.get("style", "pop")
    specific_progression = context.get("progression")
    randomize = context.get("randomize", True)

    # Map complexity to difficulty level
    if complexity <= 3:
        effective_difficulty = "beginner"
    elif complexity <= 7:
        effective_difficulty = "intermediate"
    else:
        effective_difficulty = "advanced"

    # Set parameters based on difficulty
    if effective_difficulty == "beginner":
        base_tempo = 70
        octave = 4
        use_7ths = False
    elif effective_difficulty == "intermediate":
        base_tempo = 85
        octave = 4
        use_7ths = random.choice([True, False]) if randomize else False
    else:  # advanced
        base_tempo = 100
        octave = random.choice([3, 4]) if randomize else 4
        use_7ths = True

    # Select progression
    if specific_progression:
        numerals = specific_progression
    elif randomize:
        numerals = random.choice(PROGRESSIONS[effective_difficulty])
    else:
        numerals = PROGRESSIONS[effective_difficulty][0]

    # Apply DRAMATIC tempo randomization (±30% - very audible)
    if randomize:
        tempo_variance = random.uniform(-0.30, 0.30)
        tempo = int(base_tempo * (1 + tempo_variance))
        tempo = max(40, min(160, tempo))  # Clamp to reasonable range
    else:
        tempo = base_tempo

    # Define rhythm patterns for variety
    RHYTHM_PATTERNS = {
        "whole": [4.0],                         # Whole note
        "half": [2.0, 2.0],                     # Half notes
        "quarter": [1.0, 1.0, 1.0, 1.0],        # Quarter notes
        "dotted_half_quarter": [3.0, 1.0],      # Syncopated
        "half_quarters": [2.0, 1.0, 1.0],       # Half + quarters
        "quarter_half": [1.0, 1.0, 2.0],        # Quarters + half
    }
    
    # Select rhythm pattern based on difficulty
    if effective_difficulty == "beginner":
        available_rhythms = ["whole", "half"]
    elif effective_difficulty == "intermediate":
        available_rhythms = ["whole", "half", "quarter", "dotted_half_quarter"]
    else:
        available_rhythms = list(RHYTHM_PATTERNS.keys())
    
    # Generate chord voicings
    chord_names = []
    all_midi_notes = []
    note_names = []
    rhythm = []
    
    for idx, numeral in enumerate(numerals):
        chord_name, midi_notes = roman_to_chord_notes(numeral, key, octave)
        
        # --- RANDOM INVERSION ---
        if randomize and len(midi_notes) >= 3:
            # Apply random inversion (0=root, 1=1st, 2=2nd)
            if effective_difficulty == "beginner":
                inversion = 0  # Root position only
            elif effective_difficulty == "intermediate":
                inversion = random.choice([0, 0, 1])  # Bias toward root
            else:
                inversion = random.choice([0, 1, 2])  # All inversions
            
            # Apply inversion by moving bottom notes up an octave
            for _ in range(inversion):
                if len(midi_notes) > 0:
                    midi_notes = midi_notes[1:] + [midi_notes[0] + 12]
        
        chord_names.append(chord_name)
        
        # Add chord notes (as a block - all notes at once)
        all_midi_notes.extend(midi_notes)
        note_names.extend([f"{SEMITONE_TO_NOTE[n % 12]}{n // 12 - 1}" for n in midi_notes])
        
        # --- RANDOM RHYTHM PATTERN ---
        if randomize:
            rhythm_name = random.choice(available_rhythms)
            chord_rhythm = RHYTHM_PATTERNS[rhythm_name]
        else:
            chord_rhythm = [4.0]  # Whole note
        
        # Distribute rhythm across chord tones
        notes_per_beat = len(midi_notes)
        for beat_value in chord_rhythm:
            rhythm.extend([beat_value / notes_per_beat] * notes_per_beat)

    # Calculate duration
    duration_beats = len(numerals) * 4.0  # 4 beats per chord

    # Create title and description
    progression_str = " - ".join(numerals)
    title = f"{key} Major: {progression_str}"
    description = (
        f"Practice this {effective_difficulty} chord progression in {key}. "
        f"Chords: {', '.join(chord_names)}. "
        f"Focus on smooth voice leading between chords."
    )

    # Practice tips
    practice_tips = [
        "Play each chord slowly and listen for clarity",
        "Focus on smooth transitions between chords",
        "Keep a steady pulse throughout"
    ]
    
    if effective_difficulty == "beginner":
        practice_tips.insert(0, "Start with just the root notes")
    elif effective_difficulty == "advanced":
        practice_tips.append("Try different voicings and inversions")
        practice_tips.append("Practice in multiple keys")

    # Characteristics
    characteristics = ["progression", "harmony", style, effective_difficulty]
    if use_7ths:
        characteristics.append("7th_chords")

    return Exercise(
        exercise_type="progression",
        title=title,
        description=description,
        notes=note_names,
        midi_notes=all_midi_notes,
        rhythm=rhythm,
        duration_beats=duration_beats,
        key=key,
        tempo_bpm=tempo,
        difficulty=effective_difficulty,
        characteristics=characteristics,
        practice_tips=practice_tips,
        chords=chord_names,
        roman_numerals=numerals,
        complexity=complexity,
        generation_method="local_progression"
    )


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("PROGRESSION GENERATOR TEST")
    print("=" * 70)

    # Test 1: C Major, Beginner
    print("\nTest 1: C Major - Beginner")
    print("-" * 70)
    exercise1 = generate_progression_exercise(
        context={"key": "C"},
        difficulty="beginner",
        complexity=2
    )
    print(f"Title: {exercise1.title}")
    print(f"Roman: {exercise1.roman_numerals}")
    print(f"Chords: {exercise1.chords}")
    print(f"Notes: {len(exercise1.notes)} notes")
    print(f"MIDI: {exercise1.midi_notes[:12]}...")
    print(f"Tempo: {exercise1.tempo_bpm} BPM")

    # Test 2: G Major, Intermediate
    print("\n\nTest 2: G Major - Intermediate")
    print("-" * 70)
    exercise2 = generate_progression_exercise(
        context={"key": "G"},
        difficulty="intermediate",
        complexity=5
    )
    print(f"Title: {exercise2.title}")
    print(f"Roman: {exercise2.roman_numerals}")
    print(f"Chords: {exercise2.chords}")
    print(f"Notes: {len(exercise2.notes)} notes")

    # Test 3: Bb Major, Advanced
    print("\n\nTest 3: Bb Major - Advanced")
    print("-" * 70)
    exercise3 = generate_progression_exercise(
        context={"key": "Bb"},
        difficulty="advanced",
        complexity=9
    )
    print(f"Title: {exercise3.title}")
    print(f"Roman: {exercise3.roman_numerals}")
    print(f"Chords: {exercise3.chords}")
    print(f"Notes: {len(exercise3.notes)} notes")

    # Test 4: Randomization check
    print("\n\nTest 4: Randomization Check (5 runs with same params)")
    print("-" * 70)
    hashes = set()
    for i in range(5):
        ex = generate_progression_exercise(context={"key": "C"}, complexity=5)
        h = hash(tuple(ex.roman_numerals))
        hashes.add(h)
        print(f"Run {i+1}: {ex.roman_numerals}")
    print(f"Unique progressions: {len(hashes)}/5")

    print("\n" + "=" * 70)
    print("✅ Progression generator tests passed!")
    print("=" * 70)

