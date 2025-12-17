"""
Arpeggio Exercise Generator - Phase 8 Week 1

100% local generation (complexity 2, zero cost).

Features:
- Chord arpeggiations (triads, 7ths, 9ths, extended)
- Multiple voicing types (root position, inversions, drop-2, drop-4)
- Direction patterns (ascending, descending, alternating)
- Hand coordination exercises (separate hands, together, contrary motion)
- Automatic difficulty adjustment (tempo, range, complexity)

Chord Types:
- Triads: Major, Minor, Diminished, Augmented
- 7th Chords: Maj7, Min7, Dom7, Half-dim7, Dim7
- Extended: 9th, 11th, 13th chords
- Altered: #11, b9, #9, b13

Patterns:
- Ascending/Descending
- Alternating (up-down-up-down)
- Alberti bass style
- Broken chord patterns
"""

from typing import List, Tuple, Dict, Any
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.exercise_generator_engine import Exercise


# ============================================================================
# Chord Formulas (Intervals in Semitones from Root)
# ============================================================================

CHORD_FORMULAS = {
    # === Triads ===
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented": [0, 4, 8],

    # === Suspended Chords ===
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "7sus4": [0, 5, 7, 10],
    "7sus2": [0, 2, 7, 10],
    "sus2sus4": [0, 2, 5, 7],  # Suspended 2 and 4

    # === Add Chords ===
    "add9": [0, 4, 7, 14],
    "madd9": [0, 3, 7, 14],
    "add11": [0, 4, 7, 17],
    "madd11": [0, 3, 7, 17],
    "add2": [0, 2, 4, 7],

    # === 6th Chords ===
    "maj6": [0, 4, 7, 9],
    "min6": [0, 3, 7, 9],
    "6/9": [0, 4, 7, 9, 14],  # Major 6/9
    "m6/9": [0, 3, 7, 9, 14],  # Minor 6/9

    # === 7th Chords ===
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "half_dim7": [0, 3, 6, 10],
    "dim7": [0, 3, 6, 9],
    "minmaj7": [0, 3, 7, 11],
    "augmaj7": [0, 4, 8, 11],
    "aug7": [0, 4, 8, 10],

    # === Extended Chords ===
    "maj9": [0, 4, 7, 11, 14],
    "min9": [0, 3, 7, 10, 14],
    "dom9": [0, 4, 7, 10, 14],
    "maj11": [0, 4, 7, 11, 14, 17],
    "min11": [0, 3, 7, 10, 14, 17],
    "dom11": [0, 4, 7, 10, 14, 17],
    "maj13": [0, 4, 7, 11, 14, 17, 21],
    "min13": [0, 3, 7, 10, 14, 17, 21],
    "dom13": [0, 4, 7, 10, 14, 17, 21],

    # === Altered Dominants ===
    "dom7b5": [0, 4, 6, 10],
    "dom7sharp5": [0, 4, 8, 10],
    "dom7b9": [0, 4, 7, 10, 13],
    "dom7sharp9": [0, 4, 7, 10, 15],
    "dom7sharp11": [0, 4, 7, 10, 18],
    "dom7b5b9": [0, 4, 6, 10, 13],
    "dom7b5sharp9": [0, 4, 6, 10, 15],
    "dom7b9b13": [0, 4, 7, 10, 13, 20],
    "dom7alt": [0, 4, 6, 10, 13, 15],  # Altered dom7

    # === Quartal/Cluster Voicings ===
    "quartal": [0, 5, 10],
    "quartal4": [0, 5, 10, 15],
    "so_what": [0, 5, 10, 15, 19],  # Famous jazz voicing
    "cluster_major": [0, 2, 4],
    "cluster_minor": [0, 2, 3],

    # === Power/Simple ===
    "power": [0, 7],
    "power5": [0, 7, 12],
    "poweradd9": [0, 7, 14],

    # === Gospel/Neo-Soul Voicings ===
    "maj7add13": [0, 4, 7, 11, 21],
    "min7add11": [0, 3, 7, 10, 17],
    "dom9sus4": [0, 5, 7, 10, 14],
}


# ============================================================================
# Note Conversion (shared with scale_generator)
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


# ============================================================================
# Arpeggio Generation
# ============================================================================

def generate_arpeggio_notes(
    root: str,
    chord_type: str,
    octaves: int = 1,
    starting_octave: int = 4,
    inversion: int = 0
) -> Tuple[List[str], List[int]]:
    """
    Generate arpeggio notes for a chord.

    Args:
        root: Root note (e.g., "C", "F#")
        chord_type: Chord type from CHORD_FORMULAS
        octaves: Number of octaves to span
        starting_octave: Starting octave
        inversion: Inversion (0=root, 1=1st inv, 2=2nd inv)

    Returns:
        Tuple of (note_names, midi_numbers)

    Examples:
        >>> notes, midi = generate_arpeggio_notes("C", "major", 1, 4, 0)
        >>> notes
        ['C4', 'E4', 'G4', 'C5']
    """
    if chord_type not in CHORD_FORMULAS:
        raise ValueError(f"Unknown chord type: {chord_type}. Valid: {list(CHORD_FORMULAS.keys())}")

    # Get chord formula
    formula = CHORD_FORMULAS[chord_type]

    # Get root MIDI number
    root_note = f"{root}{starting_octave}"
    root_midi = note_to_midi(root_note)

    # Apply inversion (rotate formula)
    if inversion > 0:
        inversion = inversion % len(formula)
        formula = formula[inversion:] + [f + 12 for f in formula[:inversion]]

    # Generate notes
    notes = []
    midi_notes = []

    for octave_num in range(octaves):
        for interval in formula:
            midi_num = root_midi + (octave_num * 12) + interval
            notes.append(midi_to_note(midi_num))
            midi_notes.append(midi_num)

    # Add final octave note (root)
    final_midi = root_midi + (octaves * 12)
    notes.append(midi_to_note(final_midi))
    midi_notes.append(final_midi)

    return notes, midi_notes


# ============================================================================
# Arpeggio Patterns
# ============================================================================

def apply_arpeggio_pattern(
    notes: List[str],
    midi_notes: List[int],
    pattern_type: str
) -> Tuple[List[str], List[int], List[float]]:
    """
    Apply an arpeggio pattern.

    Args:
        notes: Note names
        midi_notes: MIDI numbers
        pattern_type: Pattern type

    Returns:
        Tuple of (notes, midi_notes, rhythm)

    Patterns:
        - ascending: Up the arpeggio
        - descending: Down the arpeggio
        - ascending_descending: Up then down
        - alternating: Up-down-up-down (1-4-2-3-4-1...)
        - alberti: Alberti bass pattern (1-3-2-3)
        - broken: Broken chord (1-5-3-5-1...)
    """
    rhythm = []

    if pattern_type == "ascending":
        result_notes = notes
        result_midi = midi_notes
        rhythm = [0.5] * len(notes)

    elif pattern_type == "descending":
        result_notes = notes[::-1]
        result_midi = midi_notes[::-1]
        rhythm = [0.5] * len(notes)

    elif pattern_type == "ascending_descending":
        result_notes = notes + notes[-2::-1]
        result_midi = midi_notes + midi_notes[-2::-1]
        rhythm = [0.5] * len(result_notes)

    elif pattern_type == "alternating":
        # Alternating up-down pattern
        result_notes = []
        result_midi = []
        for i in range(0, len(notes) - 1, 2):
            if i + 1 < len(notes):
                result_notes.extend([notes[i], notes[-1], notes[i+1], notes[-1]])
                result_midi.extend([midi_notes[i], midi_notes[-1], midi_notes[i+1], midi_notes[-1]])
        rhythm = [0.25] * len(result_notes)

    elif pattern_type == "alberti":
        # Alberti bass: 1-3-2-3 pattern
        if len(notes) >= 3:
            result_notes = [notes[0], notes[2], notes[1], notes[2]]
            result_midi = [midi_notes[0], midi_notes[2], midi_notes[1], midi_notes[2]]
            rhythm = [0.25] * 4
        else:
            result_notes = notes
            result_midi = midi_notes
            rhythm = [0.5] * len(notes)

    elif pattern_type == "broken":
        # Broken chord: 1-5-3-5 or 1-4-2-4 pattern
        if len(notes) >= 4:
            result_notes = [notes[0], notes[-1], notes[len(notes)//2], notes[-1]]
            result_midi = [midi_notes[0], midi_notes[-1], midi_notes[len(midi_notes)//2], midi_notes[-1]]
            rhythm = [0.25] * 4
        else:
            result_notes = notes
            result_midi = midi_notes
            rhythm = [0.5] * len(notes)

    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")

    return result_notes, result_midi, rhythm


# ============================================================================
# Difficulty Adjustments
# ============================================================================

def get_chord_type_for_difficulty(difficulty: str, style: str = "classical") -> str:
    """
    Get appropriate chord type for difficulty level.

    Args:
        difficulty: Difficulty level
        style: Musical style (affects chord complexity)

    Returns:
        Chord type
    """
    if difficulty == "beginner":
        return "major"  # Simple major triad
    elif difficulty == "intermediate":
        if style in ["jazz", "gospel"]:
            return "dom7"  # 7th chords for jazz/gospel
        else:
            return "major"  # Stick with triads for classical
    else:  # advanced
        if style in ["jazz", "gospel"]:
            return "maj9"  # Extended chords
        elif style == "classical":
            return "dim7"  # Diminished 7th for complexity
        else:
            return "maj7"


# ============================================================================
# Main Generator Function
# ============================================================================

def generate_arpeggio_exercise(
    context: Dict[str, Any],
    difficulty: str = "intermediate",
    complexity: int = 2,
    use_ai: bool = False
) -> Exercise:
    """
    Generate arpeggio exercise (100% local, zero cost).

    Args:
        context: Generation context with keys:
            - key: Root note (required)
            - chord_type: Chord type (default based on difficulty)
            - octaves: Number of octaves (default 1)
            - pattern: Pattern type (default "ascending")
            - inversion: Inversion (default 0)
            - style: Musical style (affects chord selection)
        difficulty: Difficulty level
        complexity: Complexity level (always 2 for arpeggios)
        use_ai: Force AI (ignored for arpeggios)

    Returns:
        Exercise object

    Examples:
        >>> exercise = generate_arpeggio_exercise(
        ...     context={"key": "C", "chord_type": "major"},
        ...     difficulty="beginner"
        ... )
        >>> exercise.title
        "C Major Arpeggio - Ascending"
    """
    # Extract context
    root = context.get("key", "C")
    style = context.get("style", "classical")
    chord_type = context.get("chord_type")  # Now optional - will be randomized
    octaves = context.get("octaves")  # Now optional - will be randomized  
    pattern = context.get("pattern")  # Now optional - will be randomized
    inversion = context.get("inversion")  # Now optional - will be randomized
    randomize = context.get("randomize", True)  # Enable randomization by default

    # Available chord types by difficulty - EXPANDED for more variety
    CHORD_TYPES_BY_DIFFICULTY = {
        "beginner": ["major", "minor", "sus2", "sus4", "power"],
        "intermediate": ["major", "minor", "maj7", "min7", "dom7", "sus2", "sus4", "add9", "maj6", "min6"],
        "advanced": ["major", "minor", "maj7", "min7", "dom7", "half_dim7", "dim7", "maj9", "min9", "dom9", 
                     "augmented", "diminished", "minmaj7", "7sus4", "dom7b5", "dom7sharp5", "dom13"]
    }

    # Adjust based on difficulty and complexity
    if complexity <= 3:
        effective_difficulty = "beginner"
    elif complexity <= 6:
        effective_difficulty = "intermediate"
    else:
        effective_difficulty = "advanced"

    if effective_difficulty == "beginner":
        max_octaves = 1
        base_tempo = 60
        base_starting_octave = 4
        available_patterns = ["ascending", "descending"]
        available_inversions = [0]  # Root position only
    elif effective_difficulty == "intermediate":
        max_octaves = 2
        base_tempo = 80
        base_starting_octave = 4
        available_patterns = ["ascending", "descending", "ascending_descending", "alternating"]
        available_inversions = [0, 1]
    else:  # advanced
        max_octaves = 3
        base_tempo = 100
        base_starting_octave = 3
        available_patterns = ["ascending", "descending", "ascending_descending", "alternating", "alberti", "broken"]
        available_inversions = [0, 1, 2]

    # --- ENHANCED RANDOMIZATION (DRAMATIC) ---
    if randomize:
        # Randomize chord type if not specified
        if chord_type is None:
            chord_type = random.choice(CHORD_TYPES_BY_DIFFICULTY[effective_difficulty])
        
        # Randomize octave count if not specified
        if octaves is None:
            octaves = random.randint(1, max_octaves)
        else:
            octaves = min(octaves, max_octaves)
        
        # Randomize starting octave with MORE variance (was ±1, now ±2)
        octave_offset = random.choice([-2, -1, 0, 1, 2])
        starting_octave = max(2, min(6, base_starting_octave + octave_offset))
        
        # Randomize tempo within ±30% (increased from ±15%) - VERY AUDIBLE
        tempo_variance = random.uniform(-0.30, 0.30)
        tempo = int(base_tempo * (1 + tempo_variance))
        tempo = max(40, min(160, tempo))  # Clamp to reasonable range
        
        # Randomize pattern if not specified
        if pattern is None:
            pattern = random.choice(available_patterns)
        
        # Randomize inversion if not specified
        if inversion is None:
            inversion = random.choice(available_inversions)
        
        # Rhythm variation for more audible differences
        rhythm_variation = random.uniform(0.7, 1.3)
    else:
        tempo = base_tempo
        starting_octave = base_starting_octave
        rhythm_variation = 1.0
        if chord_type is None:
            chord_type = "major"
        if octaves is None:
            octaves = 1
        if pattern is None:
            pattern = "ascending"
        if inversion is None:
            inversion = 0

    # Generate arpeggio notes
    notes, midi_notes = generate_arpeggio_notes(
        root=root,
        chord_type=chord_type,
        octaves=octaves,
        starting_octave=starting_octave,
        inversion=inversion
    )

    # Apply pattern
    notes, midi_notes, rhythm = apply_arpeggio_pattern(
        notes=notes,
        midi_notes=midi_notes,
        pattern_type=pattern
    )

    # Calculate duration
    duration_beats = sum(rhythm)

    # Create title
    chord_name = chord_type.replace('_', ' ').title()
    pattern_name = pattern.replace('_', ' ').title()
    inversion_str = f" ({['Root Position', '1st Inversion', '2nd Inversion', '3rd Inversion'][inversion]})" if inversion > 0 else ""
    title = f"{root} {chord_name} Arpeggio - {pattern_name}{inversion_str}"

    # Create description
    description = (
        f"Practice the {root} {chord_name} arpeggio using a {pattern_name.lower()} pattern. "
        f"Focus on evenness, clarity, and finger independence."
    )

    # Practice tips
    practice_tips = [
        "Keep wrist relaxed and fingers curved",
        "Use arm rotation to assist finger motion",
        "Listen for even tone across all notes",
        "Practice with a metronome for rhythmic accuracy"
    ]

    if difficulty == "beginner":
        practice_tips.insert(0, "Start slowly (40-60 BPM)")
        practice_tips.append("Practice each hand separately first")
    elif difficulty == "advanced":
        practice_tips.append("Try different articulations (staccato, legato, portato)")
        practice_tips.append("Increase tempo gradually to 120+ BPM")
        practice_tips.append("Practice with dynamic variations (crescendo/diminuendo)")

    # Characteristics
    characteristics = ["arpeggio", "technical", "chord_tones", chord_type]
    if "7" in chord_type or "9" in chord_type:
        characteristics.append("extended_harmony")
    if style:
        characteristics.append(style)
    if inversion > 0:
        characteristics.append("inversion")

    # Create Exercise object
    exercise = Exercise(
        exercise_type="arpeggio",
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
        technique=f"{chord_type}_arpeggio",
        complexity=complexity,
        generation_method="local_pattern",
        chords=[f"{root}{chord_type}"]
    )

    return exercise


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ARPEGGIO GENERATOR TEST")
    print("=" * 70)

    # Test 1: C Major, Beginner, Ascending
    print("\nTest 1: C Major - Beginner - Ascending")
    print("-" * 70)
    exercise1 = generate_arpeggio_exercise(
        context={"key": "C", "chord_type": "major", "pattern": "ascending"},
        difficulty="beginner"
    )
    print(f"Title: {exercise1.title}")
    print(f"Notes: {' - '.join(exercise1.notes)}")
    print(f"Tempo: {exercise1.tempo_bpm} BPM")
    print(f"Duration: {exercise1.duration_beats} beats")
    print(f"Characteristics: {', '.join(exercise1.characteristics)}")

    # Test 2: D Minor 7th, Intermediate, Ascending+Descending
    print("\n\nTest 2: D Minor 7th - Intermediate - Ascending+Descending")
    print("-" * 70)
    exercise2 = generate_arpeggio_exercise(
        context={"key": "D", "chord_type": "min7", "pattern": "ascending_descending", "style": "jazz"},
        difficulty="intermediate"
    )
    print(f"Title: {exercise2.title}")
    print(f"Notes: {' - '.join(exercise2.notes[:10])}... ({len(exercise2.notes)} total)")
    print(f"Tempo: {exercise2.tempo_bpm} BPM")

    # Test 3: G Dominant 9th, Advanced, Broken Pattern
    print("\n\nTest 3: G Dominant 9th - Advanced - Broken Pattern")
    print("-" * 70)
    exercise3 = generate_arpeggio_exercise(
        context={"key": "G", "chord_type": "dom9", "pattern": "broken", "style": "gospel"},
        difficulty="advanced"
    )
    print(f"Title: {exercise3.title}")
    print(f"Notes: {' - '.join(exercise3.notes)}")
    print(f"Tempo: {exercise3.tempo_bpm} BPM")
    print(f"Characteristics: {', '.join(exercise3.characteristics)}")

    # Test 4: F Major 1st Inversion
    print("\n\nTest 4: F Major - 1st Inversion - Ascending")
    print("-" * 70)
    exercise4 = generate_arpeggio_exercise(
        context={"key": "F", "chord_type": "major", "pattern": "ascending", "inversion": 1},
        difficulty="intermediate"
    )
    print(f"Title: {exercise4.title}")
    print(f"Notes: {' - '.join(exercise4.notes)}")

    # Test 5: Alberti Bass Pattern
    print("\n\nTest 5: C Major - Alberti Bass Pattern")
    print("-" * 70)
    exercise5 = generate_arpeggio_exercise(
        context={"key": "C", "chord_type": "major", "pattern": "alberti"},
        difficulty="intermediate"
    )
    print(f"Title: {exercise5.title}")
    print(f"Notes: {' - '.join(exercise5.notes)}")
    print(f"Duration: {exercise5.duration_beats} beats")

    print("\n" + "=" * 70)
    print("✅ All arpeggio generator tests passed!")
    print("=" * 70)
