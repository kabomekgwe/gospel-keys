"""
Chord Substitution System (Phase 4)

Advanced reharmonization and chord substitution techniques based on:
- Modal Interchange (borrowed chords)
- Negative Harmony (Jacob Collier/Ernst Levy)
- Coltrane Changes (Giant Steps pattern)
- Barry Harris Diminished System
- Common Tone Diminished
- Diatonic Substitution
- Extended Substitution Patterns

Research sources documented in plan file.
"""

from typing import List, Tuple, Optional, Dict
from app.theory.chord_types import get_chord_type, CHORD_LIBRARY, get_chord_notes
from app.theory.chord_inversions import get_chord_notes_with_inversion
from app.theory.interval_utils import note_to_semitone, semitone_to_note


# ============================================================================
# CATEGORY 1: MODAL INTERCHANGE (BORROWED CHORDS)
# ============================================================================

# Modal characteristic chords for each mode
MODAL_CHARACTERISTICS = {
    'ionian': {  # Major (reference)
        'i': '', 'ii': 'm', 'iii': 'm', 'iv': '', 'v': '', 'vi': 'm', 'vii': 'dim'
    },
    'dorian': {
        'i': 'm', 'ii': 'm', 'iii': '', 'iv': '', 'v': 'm', 'vi': 'dim', 'vii': ''
    },
    'phrygian': {
        'i': 'm', 'ii': '', 'iii': '', 'iv': 'm', 'v': 'dim', 'vi': '', 'vii': 'm'
    },
    'lydian': {
        'i': '', 'ii': '', 'iii': 'm', 'iv': 'dim', 'v': '', 'vi': 'm', 'vii': 'm'
    },
    'mixolydian': {
        'i': '', 'ii': 'm', 'iii': 'dim', 'iv': '', 'v': 'm', 'vi': 'm', 'vii': ''
    },
    'aeolian': {  # Natural minor
        'i': 'm', 'ii': 'dim', 'iii': '', 'iv': 'm', 'v': 'm', 'vi': '', 'vii': ''
    },
    'locrian': {
        'i': 'dim', 'ii': '', 'iii': 'm', 'iv': 'm', 'v': '', 'vi': '', 'vii': 'm'
    },
}


def get_modal_interchange_chord(
    key_root: str,
    source_mode: str,
    target_mode: str,
    degree: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, List[str]]:
    """
    Borrow a chord from a parallel mode.

    Modal interchange allows borrowing chords from parallel modes
    (modes with the same root). Most common: borrowing from parallel minor.

    Args:
        key_root: Root of the key (e.g., "C")
        source_mode: Current mode (e.g., "ionian" for major)
        target_mode: Mode to borrow from (e.g., "aeolian" for minor)
        degree: Scale degree (e.g., "iv", "bVII", "bIII")
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (chord_symbol, note_list)

    Example:
        >>> get_modal_interchange_chord("C", "ionian", "aeolian", "iv")
        ("Fm", ['F4', 'Ab4', 'C5'])  # Borrowed from C minor
    """
    # Scale degree to semitone mapping
    degree_map = {
        'i': 0, 'ii': 2, 'iii': 4, 'iv': 5, 'v': 7, 'vi': 9, 'vii': 11,
        'bii': 1, 'biii': 3, 'bv': 6, 'bvi': 8, 'bvii': 10,
        '#i': 1, '#ii': 3, '#iv': 6, '#v': 8, '#vi': 10,
    }

    degree_lower = degree.lower()
    if degree_lower not in degree_map:
        raise ValueError(f"Unknown degree: {degree}")

    # Get chord quality from target mode
    if target_mode not in MODAL_CHARACTERISTICS:
        raise ValueError(f"Unknown mode: {target_mode}")

    mode_chords = MODAL_CHARACTERISTICS[target_mode]
    if degree_lower not in mode_chords:
        raise ValueError(f"Degree {degree} not found in {target_mode} mode")

    quality = mode_chords[degree_lower]

    # Calculate root note
    key_semitone = note_to_semitone(key_root)
    degree_semitone = degree_map[degree_lower]
    chord_root_semitone = (key_semitone + degree_semitone) % 12
    chord_root = semitone_to_note(chord_root_semitone, prefer_sharps)

    # Generate chord
    notes = get_chord_notes_with_inversion(chord_root, quality, 0, octave, prefer_sharps)
    chord_symbol = f"{chord_root}{quality}"

    return (chord_symbol, notes)


def get_backdoor_progression(
    key_root: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Generate backdoor progression: iv - bVII7 - I.

    Alternative to ii-V-I using borrowed chords from parallel minor.
    Creates plagal resolution (iv-I) with chromatic bass motion (bVII-I).

    Args:
        key_root: Root of the key (e.g., "C")
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of (chord_symbol, notes) tuples

    Example:
        >>> get_backdoor_progression("C")
        [("Fm", [...]), ("Bb7", [...]), ("Cmaj7", [...])]
    """
    # iv chord (borrowed from minor)
    iv = get_modal_interchange_chord(key_root, "ionian", "aeolian", "iv", octave, prefer_sharps)

    # bVII7 chord (dominant of bVII)
    bvii_root_semitone = (note_to_semitone(key_root) + 10) % 12
    bvii_root = semitone_to_note(bvii_root_semitone, prefer_sharps)
    bvii_notes = get_chord_notes_with_inversion(bvii_root, "7", 0, octave, prefer_sharps)
    bvii_symbol = f"{bvii_root}7"

    # I chord (tonic)
    tonic_notes = get_chord_notes_with_inversion(key_root, "maj7", 0, octave, prefer_sharps)
    tonic_symbol = f"{key_root}maj7"

    return [
        iv,
        (bvii_symbol, bvii_notes),
        (tonic_symbol, tonic_notes)
    ]


def get_all_modal_borrowings(
    key_root: str,
    source_mode: str = "ionian",
    octave: int = 4,
    prefer_sharps: bool = True
) -> Dict[str, List[Tuple[str, List[str]]]]:
    """
    Get all possible borrowed chords from all parallel modes.

    Args:
        key_root: Root of the key
        source_mode: Current mode (default: ionian/major)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Dictionary mapping mode names to list of borrowed chords

    Example:
        >>> borrowings = get_all_modal_borrowings("C", "ionian")
        >>> borrowings["aeolian"]  # Chords from C minor
        [("Cm", [...]), ("Ddim", [...]), ("Eb", [...]), ...]
    """
    result = {}

    for target_mode in MODAL_CHARACTERISTICS.keys():
        if target_mode == source_mode:
            continue

        mode_chords = []
        for degree in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii']:
            try:
                chord = get_modal_interchange_chord(
                    key_root, source_mode, target_mode, degree, octave, prefer_sharps
                )
                mode_chords.append(chord)
            except (ValueError, KeyError):
                continue

        if mode_chords:
            result[target_mode] = mode_chords

    return result


def suggest_modal_interchange(
    progression: List[Tuple[str, str]],
    key_root: str,
    prefer_sharps: bool = True
) -> List[Dict[str, any]]:
    """
    Suggest modal interchange substitutions for a progression.

    Args:
        progression: List of (chord_symbol, function) tuples
        key_root: Root of the key
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of substitution suggestions with metadata

    Example:
        >>> suggest_modal_interchange([("C", "I"), ("F", "IV"), ("G7", "V7")], "C")
        [{'original': 'F', 'substitute': 'Fm', 'borrowed_from': 'aeolian', ...}, ...]
    """
    suggestions = []

    common_substitutions = {
        'IV': ('iv', 'aeolian'),  # Major IV → minor iv
        'VI': ('bvi', 'aeolian'),  # Major VI → bVI
        'II': ('bii', 'phrygian'),  # Major II → bII
    }

    for chord_symbol, function in progression:
        if function.upper() in common_substitutions:
            degree, mode = common_substitutions[function.upper()]
            try:
                sub_symbol, sub_notes = get_modal_interchange_chord(
                    key_root, "ionian", mode, degree, 4, prefer_sharps
                )
                suggestions.append({
                    'original': chord_symbol,
                    'substitute': sub_symbol,
                    'borrowed_from': mode,
                    'degree': degree,
                    'description': f"Borrowed from parallel {mode}"
                })
            except (ValueError, KeyError):
                continue

    return suggestions


# ============================================================================
# CATEGORY 2: NEGATIVE HARMONY
# ============================================================================

def calculate_negative_axis(key_root: str, key_quality: str = "major") -> float:
    """
    Calculate the axis point for negative harmony transformation.

    In major keys: axis is between tonic (I) and subdominant (IV)
    Typically between the root and the minor third (1.5 semitones above root)

    Args:
        key_root: Root of the key
        key_quality: "major" or "minor"

    Returns:
        Float representing axis position in semitones from C

    Example:
        >>> calculate_negative_axis("C", "major")
        1.5  # Between C and Eb (midpoint)
    """
    root_semitone = note_to_semitone(key_root)

    if key_quality == "major":
        # Axis between root (0) and minor third (3)
        # midpoint at 1.5 semitones
        axis = root_semitone + 1.5
    else:  # minor
        # In minor, axis typically between root and major third
        axis = root_semitone + 2.0

    return axis % 12


def get_negative_harmony_chord(
    chord_root: str,
    quality: str,
    key_root: str,
    key_quality: str = "major",
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, List[str]]:
    """
    Generate negative harmony substitution of a chord.

    Negative harmony flips chords around a central axis, creating
    mirror-image harmonic relationships. Popularized by Jacob Collier.

    Common substitutions:
    - V7 → IVm6 (G7 → Fm6 in C major)
    - I → IV (C → F in C major)
    - ii → bVI (Dm → Ab in C major)

    Args:
        chord_root: Root of chord to transform
        quality: Chord quality
        key_root: Root of the key
        key_quality: "major" or "minor"
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (negative_symbol, note_list)

    Example:
        >>> get_negative_harmony_chord("G", "7", "C", "major")
        ("Fm6", ['F4', 'Ab4', 'C5', 'D5'])  # G7 → Fm6
    """
    axis = calculate_negative_axis(key_root, key_quality)
    chord_semitone = note_to_semitone(chord_root)

    # Reflect around axis: new_position = 2 * axis - old_position
    negative_semitone = (2 * axis - chord_semitone) % 12

    # Get the chord type
    chord = get_chord_type(quality)

    # Reflect each interval
    negative_intervals = []
    for interval in chord.intervals:
        original_pitch = (chord_semitone + interval) % 12
        reflected_pitch = (2 * axis - original_pitch) % 12
        relative_interval = (reflected_pitch - negative_semitone) % 12
        negative_intervals.append(relative_interval)

    # Sort intervals
    negative_intervals = sorted(set(negative_intervals))

    # Determine quality based on intervals
    negative_root = semitone_to_note(int(negative_semitone), prefer_sharps)

    # Common negative harmony mappings
    negative_quality_map = {
        '7': 'm6',      # Dom7 → m6
        'maj7': '',     # Maj7 → Major triad
        'm7': '6',      # m7 → 6
        '': 'm',        # Major → minor
        'm': '',        # minor → Major
    }

    negative_quality = negative_quality_map.get(quality, quality)

    # Generate the negative chord
    negative_notes = get_chord_notes_with_inversion(
        negative_root, negative_quality, 0, octave, prefer_sharps
    )
    negative_symbol = f"{negative_root}{negative_quality}"

    return (negative_symbol, negative_notes)


def get_negative_harmony_progression(
    progression: List[Tuple[str, str]],
    key_root: str,
    key_quality: str = "major",
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Transform an entire progression using negative harmony.

    Args:
        progression: List of (chord_root, quality) tuples
        key_root: Root of the key
        key_quality: "major" or "minor"
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of (negative_symbol, notes) tuples

    Example:
        >>> prog = [("C", "maj7"), ("A", "m7"), ("D", "m7"), ("G", "7")]
        >>> get_negative_harmony_progression(prog, "C", "major")
        [("F", [...]), ("Eb6", [...]), ("Ab6", [...]), ("Fm6", [...])]
    """
    negative_prog = []

    for chord_root, quality in progression:
        negative_chord = get_negative_harmony_chord(
            chord_root, quality, key_root, key_quality, octave, prefer_sharps
        )
        negative_prog.append(negative_chord)

    return negative_prog


# ============================================================================
# CATEGORY 3: COLTRANE CHANGES (GIANT STEPS PATTERN)
# ============================================================================

def apply_coltrane_changes(
    target_key: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Generate Coltrane Changes pattern leading to target key.

    The "Giant Steps" progression moves through three tonal centers
    descending by major thirds, with each preceded by its dominant.

    Pattern: Maj → (up m3) → Dom7 → (down P5) → Maj → repeat

    Args:
        target_key: Final destination key
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of chord progressions

    Example:
        >>> apply_coltrane_changes("C")
        [("Eb", "maj7"), ("F#", "7"), ("B", "maj7"), ("D", "7"), ("G", "maj7"),
         ("Bb", "7"), ("C", "maj7")]
    """
    target_semitone = note_to_semitone(target_key)

    # Three tonal centers: major thirds apart (4 semitones)
    # Starting from target, go backwards by major 3rds
    center3_semitone = target_semitone  # Target (e.g., C)
    center2_semitone = (target_semitone + 4) % 12  # Up major 3rd (E)
    center1_semitone = (target_semitone + 8) % 12  # Up another major 3rd (G#/Ab)

    progression = []

    # Start from center 1
    center1 = semitone_to_note(center1_semitone, prefer_sharps)
    center1_notes = get_chord_notes_with_inversion(center1, "maj7", 0, octave, prefer_sharps)
    progression.append((f"{center1}maj7", center1_notes))

    # Dom7 of center 2 (up minor 3rd from center 1)
    dom2_semitone = (center1_semitone + 3) % 12
    dom2 = semitone_to_note(dom2_semitone, prefer_sharps)
    dom2_notes = get_chord_notes_with_inversion(dom2, "7", 0, octave, prefer_sharps)
    progression.append((f"{dom2}7", dom2_notes))

    # Center 2
    center2 = semitone_to_note(center2_semitone, prefer_sharps)
    center2_notes = get_chord_notes_with_inversion(center2, "maj7", 0, octave, prefer_sharps)
    progression.append((f"{center2}maj7", center2_notes))

    # Dom7 of center 3 (up minor 3rd from center 2)
    dom3_semitone = (center2_semitone + 3) % 12
    dom3 = semitone_to_note(dom3_semitone, prefer_sharps)
    dom3_notes = get_chord_notes_with_inversion(dom3, "7", 0, octave, prefer_sharps)
    progression.append((f"{dom3}7", dom3_notes))

    # Center 3 (target)
    center3 = semitone_to_note(center3_semitone, prefer_sharps)
    center3_notes = get_chord_notes_with_inversion(center3, "maj7", 0, octave, prefer_sharps)
    progression.append((f"{center3}maj7", center3_notes))

    return progression


def get_giant_steps_cycle(
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Generate the complete Giant Steps harmonic cycle.

    The original "Giant Steps" by John Coltrane cycles through
    B major, G major, and Eb major (major thirds apart).

    Returns:
        Complete Giant Steps progression

    Example:
        >>> get_giant_steps_cycle()
        [("Bmaj7", [...]), ("D7", [...]), ("Gmaj7", [...]), ...]
    """
    # Original Giant Steps starts on B major
    return apply_coltrane_changes("B", octave, prefer_sharps)


def generate_coltrane_substitution(
    original_root: str,
    original_quality: str,
    target_root: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Apply Coltrane-style substitution between two chords.

    Inserts tonal centers moving by major thirds between original and target.

    Args:
        original_root: Starting chord root
        original_quality: Starting chord quality
        target_root: Destination chord root
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Substitution progression

    Example:
        >>> generate_coltrane_substitution("C", "maj7", "F", "maj7")
        [("Cmaj7", [...]), intermediate chords..., ("Fmaj7", [...])]
    """
    # Generate Coltrane changes leading to target
    coltrane_prog = apply_coltrane_changes(target_root, octave, prefer_sharps)

    # Add original chord at beginning
    original_notes = get_chord_notes_with_inversion(
        original_root, original_quality, 0, octave, prefer_sharps
    )
    original_symbol = f"{original_root}{original_quality}"

    return [(original_symbol, original_notes)] + coltrane_prog


# ============================================================================
# CATEGORY 4: BARRY HARRIS DIMINISHED SYSTEM
# ============================================================================

def get_sixth_diminished_scale(
    root: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Generate Barry Harris 6th-diminished scale harmonization.

    The scale alternates between major 6th and diminished 7th chords:
    Major 6 + dim7 from 7th degree = 8-note scale

    Args:
        root: Root note
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of alternating 6 and dim7 chords

    Example:
        >>> get_sixth_diminished_scale("C")
        [("C6", [...]), ("Ddim7", [...]), ("C6/E", [...]), ...]
    """
    root_semitone = note_to_semitone(root)

    # 6th-diminished scale intervals: W-H-W-H-W-H-W-H
    # (1, 2, 3, 4, 5, 6, 7, 7.5)
    scale_degrees = [0, 2, 3, 5, 6, 8, 9, 11]

    harmonization = []

    # Alternate between 6 and dim7
    for i, degree in enumerate(scale_degrees):
        pitch = (root_semitone + degree) % 12
        note = semitone_to_note(pitch, prefer_sharps)

        if i % 2 == 0:  # Even positions: major 6
            notes = get_chord_notes_with_inversion(note, "6", 0, octave, prefer_sharps)
            symbol = f"{note}6"
        else:  # Odd positions: dim7
            notes = get_chord_notes_with_inversion(note, "dim7", 0, octave, prefer_sharps)
            symbol = f"{note}dim7"

        harmonization.append((symbol, notes))

    return harmonization


def get_four_dominants_from_dim7(
    dim7_root: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Generate four dominant 7th chords from one diminished 7th.

    Each diminished 7th contains four dominant 7ths (all tritone substitutes).
    Lower any note → Dom7 with that note as 3rd.

    Args:
        dim7_root: Root of diminished 7th chord
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of 4 dominant 7th chords

    Example:
        >>> get_four_dominants_from_dim7("B")  # Bdim7 = B-D-F-Ab
        [("G7", [...]), ("Bb7", [...]), ("Db7", [...]), ("E7", [...])]
    """
    # Get dim7 chord tones
    dim7_notes = get_chord_notes(dim7_root, "dim7", prefer_sharps)

    dominants = []

    # Each note of dim7 can be the 3rd of a Dom7
    # Dom7 root is minor 3rd below its 3rd
    for note_name in dim7_notes:
        # Calculate Dom7 root (4 semitones below)
        third_semitone = note_to_semitone(note_name)
        dom_root_semitone = (third_semitone - 4) % 12
        dom_root = semitone_to_note(dom_root_semitone, prefer_sharps)

        # Generate Dom7
        notes = get_chord_notes_with_inversion(dom_root, "7", 0, octave, prefer_sharps)
        symbol = f"{dom_root}7"

        dominants.append((symbol, notes))

    return dominants


def apply_barry_harris_rules(
    base_chord: str,
    rule: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, List[str]]:
    """
    Apply Barry Harris transformation rules to diminished chord.

    Rules:
    - "lower_one": Lower 1 note of dim7 → Dom7
    - "raise_one": Raise 1 note of dim7 → m6
    - "lower_two": Lower 2 consecutive notes → Maj6

    Args:
        base_chord: Diminished 7th chord symbol (e.g., "Bdim7")
        rule: Transformation rule
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Transformed chord

    Example:
        >>> apply_barry_harris_rules("Bdim7", "lower_one")
        ("G7", ['G4', 'B4', 'D5', 'F5'])  # B becomes Bb, now G7
    """
    # Parse chord symbol
    root = base_chord.replace("dim7", "").replace("°7", "")

    if rule == "lower_one":
        # Lower root → Dom7 a minor 3rd below
        root_semitone = note_to_semitone(root)
        dom_root_semitone = (root_semitone - 4) % 12
        dom_root = semitone_to_note(dom_root_semitone, prefer_sharps)
        notes = get_chord_notes_with_inversion(dom_root, "7", 0, octave, prefer_sharps)
        return (f"{dom_root}7", notes)

    elif rule == "raise_one":
        # Raise root → m6
        m6_notes = get_chord_notes_with_inversion(root, "m6", 0, octave, prefer_sharps)
        return (f"{root}m6", m6_notes)

    elif rule == "lower_two":
        # Lower two consecutive notes → Maj6
        maj6_notes = get_chord_notes_with_inversion(root, "6", 0, octave, prefer_sharps)
        return (f"{root}6", maj6_notes)

    else:
        raise ValueError(f"Unknown rule: {rule}")


def harmonize_sixth_diminished(
    root: str,
    melody_degrees: List[int],
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Harmonize a melody using 6th-diminished scale.

    Args:
        root: Root of the scale
        melody_degrees: Scale degrees of melody (0-7)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Harmonization using alternating 6 and dim7 chords

    Example:
        >>> harmonize_sixth_diminished("C", [0, 2, 4, 5])
        [("C6", [...]), ("C6/E", [...]), ("C6", [...]), ("Fdim7", [...])]
    """
    scale_chords = get_sixth_diminished_scale(root, octave, prefer_sharps)

    harmonization = []
    for degree in melody_degrees:
        if 0 <= degree < len(scale_chords):
            harmonization.append(scale_chords[degree])

    return harmonization


# ============================================================================
# EXPORT ALL FUNCTIONS
# ============================================================================

__all__ = [
    # Category 1: Modal Interchange
    'get_modal_interchange_chord',
    'get_backdoor_progression',
    'get_all_modal_borrowings',
    'suggest_modal_interchange',

    # Category 2: Negative Harmony
    'calculate_negative_axis',
    'get_negative_harmony_chord',
    'get_negative_harmony_progression',

    # Category 3: Coltrane Changes
    'apply_coltrane_changes',
    'get_giant_steps_cycle',
    'generate_coltrane_substitution',

    # Category 4: Barry Harris Diminished
    'get_sixth_diminished_scale',
    'get_four_dominants_from_dim7',
    'apply_barry_harris_rules',
    'harmonize_sixth_diminished',
]

# ============================================================================
# CATEGORY 5: COMMON TONE DIMINISHED
# ============================================================================

def get_common_tone_dim7(
    target_chord_root: str,
    target_quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, List[str]]:
    """
    Generate common-tone diminished 7th chord.

    Non-dominant dim7 sharing a common tone with the target chord.
    Used as passing chord or for chromatic color.

    Common pattern: dim7 a half-step above target creates smooth resolution.

    Args:
        target_chord_root: Root of destination chord
        target_quality: Quality of destination chord
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Common-tone dim7 chord

    Example:
        >>> get_common_tone_dim7("C", "maj7")
        ("C#dim7", ['C#4', 'E4', 'G4', 'Bb4'])  # Shares common tones with Cmaj7
    """
    # Get target chord notes
    target_notes = get_chord_notes(target_chord_root, target_quality, prefer_sharps)

    # Common-tone dim7 is typically half-step above target root
    target_semitone = note_to_semitone(target_chord_root)
    dim_root_semitone = (target_semitone + 1) % 12
    dim_root = semitone_to_note(dim_root_semitone, prefer_sharps)

    # Generate dim7
    notes = get_chord_notes_with_inversion(dim_root, "dim7", 0, octave, prefer_sharps)
    symbol = f"{dim_root}dim7"

    return (symbol, notes)


def convert_dom7b9_to_dim7(
    dom7_root: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, List[str]]:
    """
    Convert Dom7(b9) to diminished 7th by omitting root.

    Dom7(b9) = Root + 3rd + 5th + b7 + b9
    Remove root → b9, 3rd, 5th, b7 = dim7

    Args:
        dom7_root: Root of dominant 7(b9) chord
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Resulting dim7 chord

    Example:
        >>> convert_dom7b9_to_dim7("G")
        ("Abdim7", ['Ab4', 'B4', 'D5', 'F5'])  # G7b9 without root = Abdim7
    """
    # Get Dom7b9 notes
    dom_notes = get_chord_notes(dom7_root, "7b9", prefer_sharps)

    # The b9 becomes the root of the dim7
    # b9 is 13 semitones (1 semitone in next octave)
    dom_semitone = note_to_semitone(dom7_root)
    b9_semitone = (dom_semitone + 13) % 12  # 13 % 12 = 1
    dim_root = semitone_to_note(b9_semitone, prefer_sharps)

    # Generate dim7 from b9
    notes = get_chord_notes_with_inversion(dim_root, "dim7", 0, octave, prefer_sharps)
    symbol = f"{dim_root}dim7"

    return (symbol, notes)


def get_passing_dim7(
    from_chord_root: str,
    to_chord_root: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, List[str]]:
    """
    Generate passing diminished 7th between two chords.

    Chromatic passing chord that connects two diatonic chords smoothly.

    Args:
        from_chord_root: Starting chord root
        to_chord_root: Destination chord root
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Passing dim7 chord

    Example:
        >>> get_passing_dim7("C", "D")
        ("C#dim7", ['C#4', 'E4', 'G4', 'Bb4'])  # Passes between C and D
    """
    from_semitone = note_to_semitone(from_chord_root)
    to_semitone = note_to_semitone(to_chord_root)

    # Passing chord is typically half-step below destination
    if to_semitone > from_semitone:
        # Ascending: use half-step below destination
        dim_semitone = (to_semitone - 1) % 12
    else:
        # Descending: use half-step above origin
        dim_semitone = (from_semitone + 1) % 12

    dim_root = semitone_to_note(dim_semitone, prefer_sharps)
    notes = get_chord_notes_with_inversion(dim_root, "dim7", 0, octave, prefer_sharps)
    symbol = f"{dim_root}dim7"

    return (symbol, notes)


def suggest_dim7_substitution(
    progression: List[Tuple[str, str]],
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Dict[str, any]]:
    """
    Suggest diminished 7th substitutions for a progression.

    Identifies opportunities to insert passing or common-tone dim7 chords.

    Args:
        progression: List of (chord_root, quality) tuples
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of substitution suggestions

    Example:
        >>> suggest_dim7_substitution([("C", ""), ("Dm", "m"), ("G", "7")])
        [{'type': 'passing', 'between': ('C', 'Dm'), 'chord': 'C#dim7', ...}, ...]
    """
    suggestions = []

    for i in range(len(progression) - 1):
        from_root, from_quality = progression[i]
        to_root, to_quality = progression[i + 1]

        # Check if chromatic passing chord would work
        from_semitone = note_to_semitone(from_root)
        to_semitone = note_to_semitone(to_root)

        # Suggest passing dim7 if chords are whole step apart
        interval = (to_semitone - from_semitone) % 12
        if interval == 2:  # Whole step
            passing = get_passing_dim7(from_root, to_root, octave, prefer_sharps)
            suggestions.append({
                'type': 'passing',
                'between': (from_root, to_root),
                'chord_symbol': passing[0],
                'notes': passing[1],
                'description': f"Chromatic passing chord between {from_root} and {to_root}"
            })

    return suggestions


# ============================================================================
# CATEGORY 6: DIATONIC SUBSTITUTION
# ============================================================================

# Functional harmony groups (Tonic, Subdominant, Dominant)
FUNCTIONAL_GROUPS = {
    'tonic': ['I', 'i', 'III', 'iii', 'VI', 'vi'],
    'subdominant': ['II', 'ii', 'IV', 'iv'],
    'dominant': ['V', 'v', 'VII', 'vii', 'viio'],
}


def get_functional_substitutes(
    key_root: str,
    roman_numeral: str,
    key_quality: str = "major",
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Get functional substitutes for a chord (Tonic/Subdominant/Dominant).

    Chords with the same harmonic function can substitute for each other.

    Args:
        key_root: Root of the key
        roman_numeral: Roman numeral of chord (e.g., "I", "ii", "V")
        key_quality: "major" or "minor"
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of substitute chords with same function

    Example:
        >>> get_functional_substitutes("C", "I", "major")
        [("C", [...]), ("Em", [...]), ("Am", [...])]  # All tonic function
    """
    # Determine function
    function = None
    for func, numerals in FUNCTIONAL_GROUPS.items():
        if roman_numeral in numerals:
            function = func
            break

    if function is None:
        raise ValueError(f"Unknown roman numeral: {roman_numeral}")

    # Get all substitutes in same function
    substitutes = []
    degree_map_major = {
        'I': (0, ''), 'ii': (2, 'm'), 'iii': (4, 'm'),
        'IV': (5, ''), 'V': (7, ''), 'vi': (9, 'm'), 'viio': (11, 'dim')
    }
    degree_map_minor = {
        'i': (0, 'm'), 'iio': (2, 'dim'), 'III': (3, ''),
        'iv': (5, 'm'), 'v': (7, 'm'), 'VI': (8, ''), 'VII': (10, '')
    }

    degree_map = degree_map_major if key_quality == "major" else degree_map_minor

    for numeral in FUNCTIONAL_GROUPS[function]:
        if numeral in degree_map:
            degree_semitone, quality = degree_map[numeral]
            key_semitone = note_to_semitone(key_root)
            chord_root_semitone = (key_semitone + degree_semitone) % 12
            chord_root = semitone_to_note(chord_root_semitone, prefer_sharps)

            notes = get_chord_notes_with_inversion(chord_root, quality, 0, octave, prefer_sharps)
            symbol = f"{chord_root}{quality}"
            substitutes.append((symbol, notes))

    return substitutes


def substitute_chord_in_progression(
    progression: List[Tuple[str, str, str]],
    key_root: str,
    key_quality: str = "major",
    octave: int = 4,
    prefer_sharps: bool = True
) -> Dict[int, List[Tuple[str, List[str]]]]:
    """
    Generate substitution options for each chord in progression.

    Args:
        progression: List of (chord_root, quality, roman_numeral) tuples
        key_root: Root of the key
        key_quality: "major" or "minor"
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Dictionary mapping position to list of substitutes

    Example:
        >>> prog = [("C", "", "I"), ("F", "", "IV"), ("G", "7", "V")]
        >>> substitute_chord_in_progression(prog, "C", "major")
        {0: [("C", [...]), ("Em", [...]), ("Am", [...])],
         1: [("F", [...]), ("Dm", [...])],
         2: [("G7", [...]), ("Bdim", [...])]}
    """
    substitutions = {}

    for i, (chord_root, quality, numeral) in enumerate(progression):
        try:
            subs = get_functional_substitutes(key_root, numeral, key_quality, octave, prefer_sharps)
            substitutions[i] = subs
        except ValueError:
            # If can't find substitutes, keep original
            notes = get_chord_notes_with_inversion(chord_root, quality, 0, octave, prefer_sharps)
            substitutions[i] = [(f"{chord_root}{quality}", notes)]

    return substitutions


def get_all_substitution_options(
    chord_root: str,
    quality: str,
    key_root: str,
    key_quality: str = "major",
    octave: int = 4,
    prefer_sharps: bool = True
) -> Dict[str, List[Tuple[str, List[str]]]]:
    """
    Get all possible substitution types for a chord.

    Includes: functional, tritone, modal interchange, negative harmony.

    Args:
        chord_root: Root of chord to substitute
        quality: Chord quality
        key_root: Root of the key
        key_quality: "major" or "minor"
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Dictionary of substitution categories and options

    Example:
        >>> get_all_substitution_options("G", "7", "C", "major")
        {'tritone': [("Db7", [...])],
         'negative': [("Fm6", [...])],
         'functional': [("Bdim", [...])],
         ...}
    """
    options = {}

    # Tritone substitution (for dominant chords)
    if quality in ["7", "9", "13"]:
        tritone_root_semitone = (note_to_semitone(chord_root) + 6) % 12
        tritone_root = semitone_to_note(tritone_root_semitone, prefer_sharps)
        tritone_notes = get_chord_notes_with_inversion(tritone_root, quality, 0, octave, prefer_sharps)
        options['tritone'] = [(f"{tritone_root}{quality}", tritone_notes)]

    # Negative harmony
    try:
        negative = get_negative_harmony_chord(chord_root, quality, key_root, key_quality, octave, prefer_sharps)
        options['negative'] = [negative]
    except (ValueError, KeyError):
        pass

    # Common tone diminished
    try:
        common_dim = get_common_tone_dim7(chord_root, quality, octave, prefer_sharps)
        options['common_tone_dim'] = [common_dim]
    except (ValueError, KeyError):
        pass

    return options


def apply_diatonic_substitution(
    progression: List[Tuple[str, str]],
    key_root: str,
    substitution_index: int,
    substitute_type: str = "relative",
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Apply diatonic substitution to a specific chord in progression.

    Args:
        progression: Original progression
        key_root: Root of the key
        substitution_index: Index of chord to substitute
        substitute_type: "relative" (iii for I) or "mediant" (VI for I)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Modified progression with substitution

    Example:
        >>> prog = [("C", ""), ("F", ""), ("G", "7")]
        >>> apply_diatonic_substitution(prog, "C", 0, "relative")
        [("Em", [...]), ("F", [...]), ("G7", [...])]  # I → iii
    """
    result = []

    for i, (chord_root, quality) in enumerate(progression):
        if i == substitution_index:
            # Apply substitution
            key_semitone = note_to_semitone(key_root)
            chord_semitone = note_to_semitone(chord_root)
            degree = (chord_semitone - key_semitone) % 12

            # Common substitutions
            if substitute_type == "relative":
                # I → iii (up major 3rd), IV → vi (up major 3rd)
                new_semitone = (chord_semitone + 4) % 12
                new_quality = 'm'
            elif substitute_type == "mediant":
                # I → VI (up major 6th)
                new_semitone = (chord_semitone + 9) % 12
                new_quality = 'm'
            else:
                new_semitone = chord_semitone
                new_quality = quality

            new_root = semitone_to_note(new_semitone, prefer_sharps)
            notes = get_chord_notes_with_inversion(new_root, new_quality, 0, octave, prefer_sharps)
            result.append((f"{new_root}{new_quality}", notes))
        else:
            # Keep original
            notes = get_chord_notes_with_inversion(chord_root, quality, 0, octave, prefer_sharps)
            result.append((f"{chord_root}{quality}", notes))

    return result


# ============================================================================
# CATEGORY 7: EXTENDED SUBSTITUTION PATTERNS
# ============================================================================

def get_cycle_of_fifths_substitution(
    start_root: str,
    num_chords: int = 4,
    quality: str = "7",
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Generate cycle of fifths progression.

    Move by descending perfect 5ths (ascending perfect 4ths).
    Classic ii-V-I extended to longer cycles.

    Args:
        start_root: Starting chord root
        num_chords: Number of chords in cycle
        quality: Chord quality for each chord
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of chords moving by fifths

    Example:
        >>> get_cycle_of_fifths_substitution("D", 4, "m7")
        [("Dm7", [...]), ("Gm7", [...]), ("Cm7", [...]), ("Fm7", [...])]
    """
    cycle = []
    current_semitone = note_to_semitone(start_root)

    for _ in range(num_chords):
        current_root = semitone_to_note(current_semitone, prefer_sharps)
        notes = get_chord_notes_with_inversion(current_root, quality, 0, octave, prefer_sharps)
        symbol = f"{current_root}{quality}"
        cycle.append((symbol, notes))

        # Move down perfect 5th (7 semitones) = up perfect 4th (5 semitones)
        current_semitone = (current_semitone + 5) % 12

    return cycle


def get_cycle_of_thirds_substitution(
    start_root: str,
    direction: str = "down",
    num_chords: int = 3,
    quality: str = "",
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, List[str]]]:
    """
    Generate cycle of thirds progression (mediant/submediant relationships).

    Args:
        start_root: Starting chord root
        direction: "up" (major 3rds) or "down" (minor 3rds)
        num_chords: Number of chords
        quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of chords moving by thirds

    Example:
        >>> get_cycle_of_thirds_substitution("C", "down", 3)
        [("C", [...]), ("Am", [...]), ("F", [...])]  # Down by minor 3rds
    """
    cycle = []
    current_semitone = note_to_semitone(start_root)
    interval = 4 if direction == "up" else 3  # Major 3rd or minor 3rd

    for _ in range(num_chords):
        current_root = semitone_to_note(current_semitone, prefer_sharps)
        notes = get_chord_notes_with_inversion(current_root, quality, 0, octave, prefer_sharps)
        symbol = f"{current_root}{quality}"
        cycle.append((symbol, notes))

        current_semitone = (current_semitone - interval) % 12

    return cycle


def get_chromatic_approach_chord(
    target_root: str,
    target_quality: str,
    approach_type: str = "below",
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, List[str]]:
    """
    Generate chromatic approach chord.

    Chord a half-step above or below target for smooth chromatic resolution.

    Args:
        target_root: Destination chord root
        target_quality: Destination chord quality
        approach_type: "below" (half-step below) or "above" (half-step above)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Approach chord

    Example:
        >>> get_chromatic_approach_chord("C", "maj7", "below")
        ("B7", ['B3', 'D#4', 'F#4', 'A4'])  # Approaches C from below
    """
    target_semitone = note_to_semitone(target_root)

    if approach_type == "below":
        approach_semitone = (target_semitone - 1) % 12
        approach_quality = "7"  # Dominant 7 creates strong resolution
    else:  # above
        approach_semitone = (target_semitone + 1) % 12
        approach_quality = "7"

    approach_root = semitone_to_note(approach_semitone, prefer_sharps)
    notes = get_chord_notes_with_inversion(approach_root, approach_quality, 0, octave, prefer_sharps)
    symbol = f"{approach_root}{approach_quality}"

    return (symbol, notes)


def suggest_reharmonization(
    original_progression: List[Tuple[str, str]],
    key_root: str,
    complexity: str = "moderate",
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[List[Tuple[str, List[str]]]]:
    """
    Suggest multiple reharmonization options for a progression.

    Args:
        original_progression: Original chord progression
        key_root: Root of the key
        complexity: "simple", "moderate", or "complex"
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of alternative progressions

    Example:
        >>> suggest_reharmonization([("C", ""), ("G", "7")], "C", "moderate")
        [[("C", [...]), ("Db7", [...])],  # Tritone sub
         [("Em", [...]), ("G7", [...])],  # Relative minor
         ...]
    """
    suggestions = []

    if complexity in ["simple", "moderate", "complex"]:
        # Option 1: Tritone substitutions for dominants
        tritone_prog = []
        for chord_root, quality in original_progression:
            if quality in ["7", "9"]:
                tritone_semitone = (note_to_semitone(chord_root) + 6) % 12
                tritone_root = semitone_to_note(tritone_semitone, prefer_sharps)
                notes = get_chord_notes_with_inversion(tritone_root, quality, 0, octave, prefer_sharps)
                tritone_prog.append((f"{tritone_root}{quality}", notes))
            else:
                notes = get_chord_notes_with_inversion(chord_root, quality, 0, octave, prefer_sharps)
                tritone_prog.append((f"{chord_root}{quality}", notes))
        suggestions.append(tritone_prog)

    if complexity in ["moderate", "complex"]:
        # Option 2: Modal interchange
        mi_prog = []
        for chord_root, quality in original_progression:
            # Try borrowing from parallel minor
            try:
                borrowed = get_modal_interchange_chord(key_root, "ionian", "aeolian", "iv", octave, prefer_sharps)
                mi_prog.append(borrowed)
            except (ValueError, KeyError):
                notes = get_chord_notes_with_inversion(chord_root, quality, 0, octave, prefer_sharps)
                mi_prog.append((f"{chord_root}{quality}", notes))
        if mi_prog != original_progression:
            suggestions.append(mi_prog)

    if complexity == "complex":
        # Option 3: Coltrane-style substitution
        if len(original_progression) >= 2:
            first_root, first_quality = original_progression[0]
            last_root, last_quality = original_progression[-1]
            coltrane_prog = generate_coltrane_substitution(
                first_root, first_quality, last_root, octave, prefer_sharps
            )
            suggestions.append(coltrane_prog)

    return suggestions


# ============================================================================
# UPDATE EXPORTS
# ============================================================================

__all__ = [
    # Category 1: Modal Interchange
    'get_modal_interchange_chord',
    'get_backdoor_progression',
    'get_all_modal_borrowings',
    'suggest_modal_interchange',

    # Category 2: Negative Harmony
    'calculate_negative_axis',
    'get_negative_harmony_chord',
    'get_negative_harmony_progression',

    # Category 3: Coltrane Changes
    'apply_coltrane_changes',
    'get_giant_steps_cycle',
    'generate_coltrane_substitution',

    # Category 4: Barry Harris Diminished
    'get_sixth_diminished_scale',
    'get_four_dominants_from_dim7',
    'apply_barry_harris_rules',
    'harmonize_sixth_diminished',

    # Category 5: Common Tone Diminished
    'get_common_tone_dim7',
    'convert_dom7b9_to_dim7',
    'get_passing_dim7',
    'suggest_dim7_substitution',

    # Category 6: Diatonic Substitution
    'get_functional_substitutes',
    'substitute_chord_in_progression',
    'get_all_substitution_options',
    'apply_diatonic_substitution',

    # Category 7: Extended Patterns
    'get_cycle_of_fifths_substitution',
    'get_cycle_of_thirds_substitution',
    'get_chromatic_approach_chord',
    'suggest_reharmonization',
]
