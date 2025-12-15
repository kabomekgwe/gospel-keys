"""
Comprehensive Chord Library

All chord types, voicings, and structures for music theory analysis.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from app.theory.interval_utils import semitone_to_note, note_to_semitone


@dataclass
class ChordType:
    """Chord type definition with intervals and metadata"""
    name: str
    intervals: Tuple[int, ...]  # Semitones from root
    symbol: str  # Common notation (e.g., "maj7", "m7", "7")
    category: str
    aliases: Tuple[str, ...] = ()
    description: str = ""


# ============================================================================
# TRIADS
# ============================================================================

MAJOR_TRIAD = ChordType(
    name="Major Triad",
    intervals=(0, 4, 7),
    symbol="",
    category="triad",
    aliases=("maj", "M"),
    description="Root, major 3rd, perfect 5th"
)

MINOR_TRIAD = ChordType(
    name="Minor Triad",
    intervals=(0, 3, 7),
    symbol="m",
    category="triad",
    aliases=("min", "-"),
    description="Root, minor 3rd, perfect 5th"
)

DIMINISHED_TRIAD = ChordType(
    name="Diminished Triad",
    intervals=(0, 3, 6),
    symbol="dim",
    category="triad",
    aliases=("°", "o"),
    description="Root, minor 3rd, diminished 5th"
)

AUGMENTED_TRIAD = ChordType(
    name="Augmented Triad",
    intervals=(0, 4, 8),
    symbol="aug",
    category="triad",
    aliases=("+",),
    description="Root, major 3rd, augmented 5th"
)

SUS2 = ChordType(
    name="Suspended 2nd",
    intervals=(0, 2, 7),
    symbol="sus2",
    category="triad",
    aliases=(),
    description="Root, major 2nd, perfect 5th"
)

SUS4 = ChordType(
    name="Suspended 4th",
    intervals=(0, 5, 7),
    symbol="sus4",
    category="triad",
    aliases=("sus",),
    description="Root, perfect 4th, perfect 5th"
)

# ============================================================================
# SEVENTH CHORDS
# ============================================================================

MAJOR_7 = ChordType(
    name="Major 7th",
    intervals=(0, 4, 7, 11),
    symbol="maj7",
    category="seventh",
    aliases=("Δ7", "M7", "ma7"),
    description="Major triad + major 7th"
)

MINOR_7 = ChordType(
    name="Minor 7th",
    intervals=(0, 3, 7, 10),
    symbol="m7",
    category="seventh",
    aliases=("min7", "-7"),
    description="Minor triad + minor 7th"
)

DOMINANT_7 = ChordType(
    name="Dominant 7th",
    intervals=(0, 4, 7, 10),
    symbol="7",
    category="seventh",
    aliases=("dom7",),
    description="Major triad + minor 7th. Primary chord of tension."
)

MINOR_MAJOR_7 = ChordType(
    name="Minor-Major 7th",
    intervals=(0, 3, 7, 11),
    symbol="mMaj7",
    category="seventh",
    aliases=("m(M7)", "minMaj7"),
    description="Minor triad + major 7th"
)

HALF_DIMINISHED_7 = ChordType(
    name="Half-Diminished 7th",
    intervals=(0, 3, 6, 10),
    symbol="m7b5",
    category="seventh",
    aliases=("ø7", "ø"),
    description="Diminished triad + minor 7th. ii chord in minor keys."
)

DIMINISHED_7 = ChordType(
    name="Fully Diminished 7th",
    intervals=(0, 3, 6, 9),
    symbol="dim7",
    category="seventh",
    aliases=("°7",),
    description="Diminished triad + diminished 7th. Symmetric chord."
)

AUGMENTED_MAJOR_7 = ChordType(
    name="Augmented Major 7th",
    intervals=(0, 4, 8, 11),
    symbol="augMaj7",
    category="seventh",
    aliases=("Maj7#5",),
    description="Augmented triad + major 7th"
)

AUGMENTED_7 = ChordType(
    name="Augmented 7th",
    intervals=(0, 4, 8, 10),
    symbol="7#5",
    category="seventh",
    aliases=("aug7", "+7"),
    description="Augmented triad + minor 7th"
)

# ============================================================================
# EXTENDED CHORDS (9ths, 11ths, 13ths)
# ============================================================================

MAJOR_9 = ChordType(
    name="Major 9th",
    intervals=(0, 4, 7, 11, 14),
    symbol="maj9",
    category="extended",
    aliases=("Δ9", "M9"),
    description="Major 7th + major 9th"
)

MINOR_9 = ChordType(
    name="Minor 9th",
    intervals=(0, 3, 7, 10, 14),
    symbol="m9",
    category="extended",
    aliases=("min9", "-9"),
    description="Minor 7th + major 9th"
)

DOMINANT_9 = ChordType(
    name="Dominant 9th",
    intervals=(0, 4, 7, 10, 14),
    symbol="9",
    category="extended",
    aliases=("dom9",),
    description="Dominant 7th + major 9th"
)

MAJOR_11 = ChordType(
    name="Major 11th",
    intervals=(0, 4, 7, 11, 14, 17),
    symbol="maj11",
    category="extended",
    aliases=("Δ11",),
    description="Major 9th + perfect 11th (often omit 3rd)"
)

MINOR_11 = ChordType(
    name="Minor 11th",
    intervals=(0, 3, 7, 10, 14, 17),
    symbol="m11",
    category="extended",
    aliases=("min11", "-11"),
    description="Minor 9th + perfect 11th"
)

DOMINANT_11 = ChordType(
    name="Dominant 11th",
    intervals=(0, 4, 7, 10, 14, 17),
    symbol="11",
    category="extended",
    aliases=(),
    description="Dominant 9th + perfect 11th (often omit 3rd)"
)

MAJOR_13 = ChordType(
    name="Major 13th",
    intervals=(0, 4, 7, 11, 14, 21),
    symbol="maj13",
    category="extended",
    aliases=("Δ13",),
    description="Major 9th + major 13th"
)

MINOR_13 = ChordType(
    name="Minor 13th",
    intervals=(0, 3, 7, 10, 14, 21),
    symbol="m13",
    category="extended",
    aliases=("min13", "-13"),
    description="Minor 9th + major 13th"
)

DOMINANT_13 = ChordType(
    name="Dominant 13th",
    intervals=(0, 4, 7, 10, 14, 21),
    symbol="13",
    category="extended",
    aliases=(),
    description="Dominant 9th + major 13th"
)

# ============================================================================
# ALTERED CHORDS
# ============================================================================

DOMINANT_7_FLAT_9 = ChordType(
    name="Dominant 7 flat 9",
    intervals=(0, 4, 7, 10, 13),
    symbol="7b9",
    category="altered",
    aliases=(),
    description="Dominant with b9. Tension chord resolving to minor."
)

DOMINANT_7_SHARP_9 = ChordType(
    name="Dominant 7 sharp 9",
    intervals=(0, 4, 7, 10, 15),
    symbol="7#9",
    category="altered",
    aliases=("Hendrix chord",),
    description="Dominant with #9. Purple Haze sound."
)

DOMINANT_7_FLAT_5 = ChordType(
    name="Dominant 7 flat 5",
    intervals=(0, 4, 6, 10),
    symbol="7b5",
    category="altered",
    aliases=(),
    description="Dominant with b5. French augmented 6th equivalent."
)

DOMINANT_7_SHARP_5 = ChordType(
    name="Dominant 7 sharp 5",
    intervals=(0, 4, 8, 10),
    symbol="7#5",
    category="altered",
    aliases=("7+", "aug7"),
    description="Dominant with #5."
)

DOMINANT_7_SHARP_11 = ChordType(
    name="Dominant 7 sharp 11",
    intervals=(0, 4, 7, 10, 18),
    symbol="7#11",
    category="altered",
    aliases=(),
    description="Dominant with #11 (Lydian dominant sound)"
)

ALTERED_DOMINANT = ChordType(
    name="Altered Dominant",
    intervals=(0, 4, 6, 8, 10, 13, 15),  # Root, 3, b5, #5, b7, b9, #9
    symbol="7alt",
    category="altered",
    aliases=("alt",),
    description="All alterations: b5, #5, b9, #9"
)

DOMINANT_13_FLAT_9 = ChordType(
    name="Dominant 13 flat 9",
    intervals=(0, 4, 7, 10, 13, 21),
    symbol="13b9",
    category="altered",
    aliases=(),
    description="13th chord with b9 tension"
)

DOMINANT_13_SHARP_11 = ChordType(
    name="Dominant 13 sharp 11",
    intervals=(0, 4, 7, 10, 14, 18, 21),
    symbol="13#11",
    category="altered",
    aliases=(),
    description="13th chord with #11 (Lydian dominant)"
)

# ============================================================================
# ADD CHORDS
# ============================================================================

ADD_9 = ChordType(
    name="Add 9",
    intervals=(0, 4, 7, 14),
    symbol="add9",
    category="add",
    aliases=("add2",),
    description="Major triad + 9th (no 7th)"
)

ADD_11 = ChordType(
    name="Add 11",
    intervals=(0, 4, 7, 17),
    symbol="add11",
    category="add",
    aliases=("add4",),
    description="Major triad + 11th (no 7th or 9th)"
)

MINOR_ADD_9 = ChordType(
    name="Minor Add 9",
    intervals=(0, 3, 7, 14),
    symbol="madd9",
    category="add",
    aliases=(),
    description="Minor triad + 9th"
)

SIX_NINE = ChordType(
    name="6/9",
    intervals=(0, 4, 7, 9, 14),
    symbol="6/9",
    category="add",
    aliases=("69",),
    description="Major triad + 6th + 9th. Jazz ending chord."
)

# ============================================================================
# SIXTH CHORDS
# ============================================================================

MAJOR_6 = ChordType(
    name="Major 6th",
    intervals=(0, 4, 7, 9),
    symbol="6",
    category="sixth",
    aliases=("M6",),
    description="Major triad + major 6th. Common jazz ending chord."
)

MINOR_6 = ChordType(
    name="Minor 6th",
    intervals=(0, 3, 7, 9),
    symbol="m6",
    category="sixth",
    aliases=("min6", "-6"),
    description="Minor triad + major 6th. Jazz minor tonic chord."
)

# ============================================================================
# SUSPENDED SEVENTH CHORDS
# ============================================================================

DOMINANT_7_SUS4 = ChordType(
    name="Dominant 7 sus4",
    intervals=(0, 5, 7, 10),
    symbol="7sus4",
    category="suspended",
    aliases=("7sus",),
    description="Sus4 + minor 7th. Resolves to dominant 7."
)

DOMINANT_9_SUS4 = ChordType(
    name="Dominant 9 sus4",
    intervals=(0, 5, 7, 10, 14),
    symbol="9sus",
    category="suspended",
    aliases=("9sus4",),
    description="7sus4 + 9th. Extended suspended sound."
)

# ============================================================================
# LYDIAN CHORDS (with #11)
# ============================================================================

MAJOR_7_SHARP_11 = ChordType(
    name="Major 7 sharp 11",
    intervals=(0, 4, 7, 11, 18),
    symbol="maj7#11",
    category="lydian",
    aliases=("Δ7#11", "Maj7#11"),
    description="Maj7 + #11. Lydian color, modern jazz sound."
)

MAJOR_9_SHARP_11 = ChordType(
    name="Major 9 sharp 11",
    intervals=(0, 4, 7, 11, 14, 18),
    symbol="maj9#11",
    category="lydian",
    aliases=("Δ9#11",),
    description="Maj9 + #11. Extended Lydian voicing."
)

# ============================================================================
# ADD 13 CHORDS
# ============================================================================

ADD_13 = ChordType(
    name="Add 13",
    intervals=(0, 4, 7, 21),
    symbol="add13",
    category="add",
    aliases=("add6",),
    description="Major triad + 13th (no 7th, 9th, or 11th)"
)

MINOR_ADD_13 = ChordType(
    name="Minor Add 13",
    intervals=(0, 3, 7, 21),
    symbol="madd13",
    category="add",
    aliases=(),
    description="Minor triad + 13th"
)

# ============================================================================
# COMPLEX ALTERED CHORDS
# ============================================================================

DOMINANT_7_FLAT_9_SHARP_9 = ChordType(
    name="Dominant 7 flat 9 sharp 9",
    intervals=(0, 4, 7, 10, 13, 15),
    symbol="7b9#9",
    category="altered",
    aliases=("7alt2",),
    description="Dominant with both b9 and #9. Ultimate tension chord."
)

DOMINANT_7_FLAT_9_SHARP_5 = ChordType(
    name="Dominant 7 flat 9 sharp 5",
    intervals=(0, 4, 8, 10, 13),
    symbol="7b9#5",
    category="altered",
    aliases=(),
    description="Dominant with b9 and #5 alterations"
)

DOMINANT_7_SHARP_9_SHARP_5 = ChordType(
    name="Dominant 7 sharp 9 sharp 5",
    intervals=(0, 4, 8, 10, 15),
    symbol="7#9#5",
    category="altered",
    aliases=(),
    description="Dominant with #9 and #5 alterations"
)

AUGMENTED_9 = ChordType(
    name="Augmented 9th",
    intervals=(0, 4, 8, 14),
    symbol="aug9",
    category="altered",
    aliases=("+9",),
    description="Augmented triad + 9th"
)

# ============================================================================
# MINOR 11 VARIATIONS
# ============================================================================

MINOR_11_FLAT_5 = ChordType(
    name="Minor 11 flat 5",
    intervals=(0, 3, 6, 10, 14, 17),
    symbol="m11b5",
    category="extended",
    aliases=("ø11",),
    description="Half-diminished + 11th. Extended ii chord in minor."
)

# ============================================================================
# QUARTAL/QUINTAL CHORDS
# ============================================================================

QUARTAL_CHORD = ChordType(
    name="Quartal Chord",
    intervals=(0, 5, 10),
    symbol="quartal",
    category="quartal",
    aliases=(),
    description="Built from perfect 4ths. Modern/modal sound."
)

QUINTAL_CHORD = ChordType(
    name="Quintal Chord",
    intervals=(0, 7, 14),
    symbol="quintal",
    category="quintal",
    aliases=("5stacked",),
    description="Stacked perfect 5ths. Open, hollow sound."
)

# ============================================================================
# CLUSTER CHORDS
# ============================================================================

MINOR_CLUSTER = ChordType(
    name="Minor 2nd Cluster",
    intervals=(0, 1, 7),
    symbol="cluster",
    category="cluster",
    aliases=(),
    description="Root + minor 2nd + 5th. Dissonant, modern jazz."
)

# ============================================================================
# SPECIAL CHORDS
# ============================================================================

POWER_CHORD = ChordType(
    name="Power Chord",
    intervals=(0, 7),
    symbol="5",
    category="special",
    aliases=("no3",),
    description="Root + 5th only. No 3rd = ambiguous quality."
)

# ============================================================================
# CHORD LIBRARY
# ============================================================================

CHORD_LIBRARY: Dict[str, ChordType] = {
    # Triads
    "major": MAJOR_TRIAD, "": MAJOR_TRIAD, "M": MAJOR_TRIAD,
    "minor": MINOR_TRIAD, "m": MINOR_TRIAD, "-": MINOR_TRIAD,
    "dim": DIMINISHED_TRIAD, "°": DIMINISHED_TRIAD,
    "aug": AUGMENTED_TRIAD, "+": AUGMENTED_TRIAD,
    "sus2": SUS2,
    "sus4": SUS4, "sus": SUS4,
    
    # Sevenths
    "maj7": MAJOR_7, "Δ7": MAJOR_7, "M7": MAJOR_7,
    "m7": MINOR_7, "min7": MINOR_7, "-7": MINOR_7,
    "7": DOMINANT_7, "dom7": DOMINANT_7,
    "mMaj7": MINOR_MAJOR_7, "m(M7)": MINOR_MAJOR_7,
    "m7b5": HALF_DIMINISHED_7, "ø7": HALF_DIMINISHED_7, "ø": HALF_DIMINISHED_7,
    "dim7": DIMINISHED_7, "°7": DIMINISHED_7,
    "augMaj7": AUGMENTED_MAJOR_7, "Maj7#5": AUGMENTED_MAJOR_7,
    "7#5": AUGMENTED_7, "aug7": AUGMENTED_7,
    
    # Extended
    "maj9": MAJOR_9, "Δ9": MAJOR_9, "M9": MAJOR_9,
    "m9": MINOR_9, "min9": MINOR_9, "-9": MINOR_9,
    "9": DOMINANT_9, "dom9": DOMINANT_9,
    "maj11": MAJOR_11, "Δ11": MAJOR_11,
    "m11": MINOR_11, "min11": MINOR_11, "-11": MINOR_11,
    "11": DOMINANT_11,
    "maj13": MAJOR_13, "Δ13": MAJOR_13,
    "m13": MINOR_13, "min13": MINOR_13, "-13": MINOR_13,
    "13": DOMINANT_13,
    
    # Altered
    "7b9": DOMINANT_7_FLAT_9,
    "7#9": DOMINANT_7_SHARP_9,
    "7b5": DOMINANT_7_FLAT_5,
    "7#11": DOMINANT_7_SHARP_11,
    "7alt": ALTERED_DOMINANT, "alt": ALTERED_DOMINANT,
    "13b9": DOMINANT_13_FLAT_9,
    "13#11": DOMINANT_13_SHARP_11,
    
    # Add
    "add9": ADD_9, "add2": ADD_9,
    "add11": ADD_11, "add4": ADD_11,
    "madd9": MINOR_ADD_9,
    "add13": ADD_13, "add6": ADD_13,
    "madd13": MINOR_ADD_13,
    "6/9": SIX_NINE, "69": SIX_NINE,

    # Sixth
    "6": MAJOR_6, "M6": MAJOR_6,
    "m6": MINOR_6, "min6": MINOR_6, "-6": MINOR_6,

    # Suspended Seventh
    "7sus4": DOMINANT_7_SUS4, "7sus": DOMINANT_7_SUS4,
    "9sus": DOMINANT_9_SUS4, "9sus4": DOMINANT_9_SUS4,

    # Lydian
    "maj7#11": MAJOR_7_SHARP_11, "Δ7#11": MAJOR_7_SHARP_11, "Maj7#11": MAJOR_7_SHARP_11,
    "maj9#11": MAJOR_9_SHARP_11, "Δ9#11": MAJOR_9_SHARP_11,

    # Complex Altered
    "7b9#9": DOMINANT_7_FLAT_9_SHARP_9, "7alt2": DOMINANT_7_FLAT_9_SHARP_9,
    "7b9#5": DOMINANT_7_FLAT_9_SHARP_5,
    "7#9#5": DOMINANT_7_SHARP_9_SHARP_5,
    "aug9": AUGMENTED_9, "+9": AUGMENTED_9,

    # Extended Variations
    "m11b5": MINOR_11_FLAT_5, "ø11": MINOR_11_FLAT_5,

    # Quartal/Quintal
    "quartal": QUARTAL_CHORD,
    "quintal": QUINTAL_CHORD, "5stacked": QUINTAL_CHORD,

    # Cluster
    "cluster": MINOR_CLUSTER,

    # Special
    "5": POWER_CHORD, "no3": POWER_CHORD,
}


def get_chord_type(quality: str) -> ChordType:
    """Get chord type by quality symbol (case-sensitive for symbols)."""
    if quality not in CHORD_LIBRARY:
        # Try lowercase
        if quality.lower() in CHORD_LIBRARY:
            return CHORD_LIBRARY[quality.lower()]
        raise ValueError(f"Unknown chord quality: {quality}")
    return CHORD_LIBRARY[quality]


def get_chord_notes(root: str, quality: str, prefer_sharps: bool = True) -> List[str]:
    """
    Get all notes in a chord.
    
    Args:
        root: Root note (e.g., "C", "F#")
        quality: Chord quality (e.g., "maj7", "m7", "7")
        prefer_sharps: Use sharps instead of flats
    
    Returns:
        List of note names
    """
    chord = get_chord_type(quality)
    root_semitone = note_to_semitone(root)
    
    return [
        semitone_to_note((root_semitone + interval) % 12, prefer_sharps)
        for interval in chord.intervals
    ]


def parse_chord_symbol(symbol: str) -> Tuple[str, str, Optional[str]]:
    """
    Parse a chord symbol into root, quality, and bass note (if slash chord).
    
    Args:
        symbol: Chord symbol (e.g., "Cmaj7", "F#m7", "G/B")
    
    Returns:
        Tuple of (root, quality, bass_note or None)
    """
    # Handle slash chords first
    bass_note = None
    if "/" in symbol:
        parts = symbol.split("/")
        symbol = parts[0]
        bass_note = parts[1] if len(parts) > 1 else None
    
    # Extract root note
    if len(symbol) < 1:
        raise ValueError("Empty chord symbol")
    
    root = symbol[0].upper()
    idx = 1
    
    # Check for accidentals
    while idx < len(symbol) and symbol[idx] in "#b":
        root += symbol[idx]
        idx += 1
    
    # Rest is quality
    quality = symbol[idx:] if idx < len(symbol) else ""
    
    return root, quality, bass_note


def list_chords_by_category(category: str) -> List[ChordType]:
    """Get all chords in a category."""
    seen = set()
    result = []
    for chord in CHORD_LIBRARY.values():
        if chord.category == category and chord.name not in seen:
            result.append(chord)
            seen.add(chord.name)
    return result


def get_all_categories() -> List[str]:
    """Get list of all chord categories."""
    return list(set(c.category for c in CHORD_LIBRARY.values()))


# ============================================================================
# CHORD INVERSIONS
# ============================================================================

def get_inversion_intervals(intervals: Tuple[int, ...], inversion: int) -> List[int]:
    """
    Calculate intervals for a specific inversion.

    Inversions rotate chord tones so a different note becomes the bass.
    Notes below the new bass are raised by an octave (12 semitones).

    Args:
        intervals: Original chord intervals (semitones from root)
        inversion: Inversion number (0=root, 1=1st, 2=2nd, 3=3rd, 4=4th)

    Returns:
        List of intervals for the inversion (from new bass note)

    Examples:
        Cmaj7 root position:  (0, 4, 7, 11) → [0, 4, 7, 11]   # C E G B
        Cmaj7 1st inversion:  (0, 4, 7, 11) → [0, 3, 7, 12]   # E G B C (bass E)
        Cmaj7 2nd inversion:  (0, 4, 7, 11) → [0, 4, 5, 9]    # G B C E (bass G)
        Cmaj7 3rd inversion:  (0, 4, 7, 11) → [0, 1, 5, 8]    # B C E G (bass B)
    """
    if inversion == 0:
        return list(intervals)

    if inversion < 0 or inversion >= len(intervals):
        raise ValueError(
            f"Invalid inversion {inversion} for chord with {len(intervals)} notes. "
            f"Valid inversions: 0 to {len(intervals) - 1}"
        )

    # Get the interval of the new bass note
    bass_interval = intervals[inversion]

    # Calculate new intervals relative to the new bass
    result = []
    for i, interval in enumerate(intervals):
        if i == inversion:
            # This is the new bass note
            result.append(0)
        elif i > inversion:
            # Notes that were above the new bass stay above
            distance = interval - bass_interval
            result.append(distance)
        else:
            # Notes that were below the new bass go up an octave
            distance = (12 - bass_interval) + interval
            result.append(distance)

    return result


def get_chord_notes_with_inversion(
    root: str,
    quality: str,
    inversion: int = 0,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Get chord notes in specified inversion with octave numbers.

    Uses MIDI note number approach for clarity and correctness.

    Args:
        root: Root note (e.g., "C", "F#")
        quality: Chord quality (e.g., "maj7", "m7", "7")
        inversion: 0=root, 1=1st, 2=2nd, 3=3rd, 4=4th (for 9/11/13)
        octave: Starting octave for bass note
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves (e.g., ["E4", "G4", "B4", "C5"])

    Examples:
        >>> get_chord_notes_with_inversion("C", "maj7", 0, 4)
        ["C4", "E4", "G4", "B4"]  # Root position

        >>> get_chord_notes_with_inversion("C", "maj7", 1, 4)
        ["E4", "G4", "B4", "C5"]  # 1st inversion (E on bass)

        >>> get_chord_notes_with_inversion("C", "maj7", 2, 4)
        ["G4", "B4", "C5", "E5"]  # 2nd inversion (G on bass)
    """
    chord = get_chord_type(quality)

    if inversion < 0 or inversion >= len(chord.intervals):
        raise ValueError(
            f"Invalid inversion {inversion} for chord with {len(chord.intervals)} notes"
        )

    # Calculate MIDI note numbers for root position
    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone  # MIDI note for root in given octave

    # Create list of MIDI notes in root position
    midi_notes = [base_midi + interval for interval in chord.intervals]

    if inversion > 0:
        # Move the first 'inversion' notes up an octave
        for i in range(inversion):
            midi_notes[i] += 12

        # Sort to maintain ascending order
        midi_notes.sort()

    # Convert MIDI notes to note names with octaves
    notes_with_octaves = []
    for midi_note in midi_notes:
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes_with_octaves.append(f"{note_name}{note_octave}")

    return notes_with_octaves


# ============================================================================
# VOICING TRANSFORMATIONS
# ============================================================================

def apply_drop_2(midi_notes: List[int]) -> List[int]:
    """
    Apply drop-2 voicing: drop 2nd voice from top down an octave.

    Args:
        midi_notes: List of MIDI note numbers in close position (ascending)

    Returns:
        List of MIDI notes with drop-2 voicing

    Example:
        Cmaj7 close: [60, 64, 67, 71] (C4, E4, G4, B4)
        Drop-2:      [60, 55, 64, 71] (C4, G3, E4, B4)
    """
    if len(midi_notes) < 4:
        return midi_notes  # Need at least 4 notes for drop-2

    result = midi_notes.copy()
    # Drop 2nd from top (index -2) down an octave
    result[-2] -= 12
    return sorted(result)


def apply_drop_3(midi_notes: List[int]) -> List[int]:
    """
    Apply drop-3 voicing: drop 3rd voice from top down an octave.

    Args:
        midi_notes: List of MIDI note numbers in close position

    Returns:
        List of MIDI notes with drop-3 voicing
    """
    if len(midi_notes) < 4:
        return midi_notes

    result = midi_notes.copy()
    # Drop 3rd from top (index -3) down an octave
    result[-3] -= 12
    return sorted(result)


def apply_drop_2_4(midi_notes: List[int]) -> List[int]:
    """
    Apply drop-2-4 voicing: drop 2nd AND 4th voices down an octave.

    Creates very wide voicing, common in big band arranging.

    Args:
        midi_notes: List of MIDI note numbers in close position

    Returns:
        List of MIDI notes with drop-2-4 voicing
    """
    if len(midi_notes) < 4:
        return midi_notes

    result = midi_notes.copy()
    # Drop 2nd from top (index -2)
    result[-2] -= 12
    # Drop 4th from top (index -4)
    result[-4] -= 12
    return sorted(result)


def get_rootless_voicing_a(
    root: str,
    quality: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate rootless voicing Type A: 3-5-7-9.

    Bill Evans style left-hand voicing.
    3rd on bottom, assumes bass player covers root.

    Args:
        root: Root note
        quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        Cmaj7 → [E3, G3, B3, D4] (3-5-7-9)
    """
    chord = get_chord_type(quality)

    # Find intervals for 3, 5, 7, 9
    intervals = list(chord.intervals)

    # Identify chord tones
    third_idx = None
    fifth_idx = None
    seventh_idx = None
    ninth_interval = None

    # Common interval patterns
    for i, interval in enumerate(intervals):
        if interval in (3, 4):  # m3 or M3
            third_idx = i
        elif interval == 7:  # P5
            fifth_idx = i
        elif interval in (10, 11):  # m7 or M7
            seventh_idx = i
        elif interval == 14:  # 9th
            ninth_interval = interval

    # Build rootless voicing
    voicing_intervals = []
    if third_idx is not None:
        voicing_intervals.append(intervals[third_idx])
    if fifth_idx is not None:
        voicing_intervals.append(intervals[fifth_idx])
    if seventh_idx is not None:
        voicing_intervals.append(intervals[seventh_idx])
    if ninth_interval is not None:
        voicing_intervals.append(ninth_interval)

    # Generate notes
    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in voicing_intervals:
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


def get_rootless_voicing_b(
    root: str,
    quality: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate rootless voicing Type B: 7-9-3-5.

    Bill Evans style left-hand voicing.
    7th on bottom (inverted form of Type A).

    Args:
        root: Root note
        quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        Cmaj7 → [B3, D4, E4, G4] (7-9-3-5)
    """
    # Get Type A voicing
    type_a = get_rootless_voicing_a(root, quality, octave, prefer_sharps)

    if len(type_a) < 4:
        return type_a

    # Convert to MIDI, rotate, convert back
    # Type A: [3, 5, 7, 9] → Type B: [7, 9, 3, 5]
    # This is essentially moving first two notes up an octave
    midi_notes = []
    for note_str in type_a:
        # Parse note name and octave
        note_name = ''.join(c for c in note_str if not c.isdigit())
        note_oct = int(''.join(c for c in note_str if c.isdigit()))
        semitone = note_to_semitone(note_name)
        midi = note_oct * 12 + semitone
        midi_notes.append(midi)

    # Rotate: move first two up an octave
    if len(midi_notes) >= 2:
        midi_notes[0] += 12
        midi_notes[1] += 12
        midi_notes.sort()

    # Convert back to note names
    notes = []
    for midi_note in midi_notes:
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


def get_shell_voicing(
    root: str,
    quality: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate shell voicing: Root-3-7 only.

    Essential tones for jazz comping.
    Omits the 5th.

    Args:
        root: Root note
        quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves (3 notes)

    Example:
        Cmaj7 → [C3, E3, B3]
    """
    chord = get_chord_type(quality)
    intervals = list(chord.intervals)

    # Always include root (0)
    # Find 3rd and 7th
    third_idx = None
    seventh_idx = None

    for i, interval in enumerate(intervals):
        if interval in (3, 4):  # m3 or M3
            third_idx = i
        elif interval in (10, 11):  # m7 or M7
            seventh_idx = i

    # Build shell voicing
    shell_intervals = [0]  # Root
    if third_idx is not None:
        shell_intervals.append(intervals[third_idx])
    if seventh_idx is not None:
        shell_intervals.append(intervals[seventh_idx])

    # Generate notes
    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in shell_intervals:
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


def get_so_what_voicing(
    root: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate So What voicing: Quartal stack + major 3rd.

    Bill Evans voicing from Miles Davis "So What".
    Structure: 4ths stacked, then major 3rd on top.

    Args:
        root: Root note
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of 5 note names

    Example:
        D So What → [D3, G3, C4, F4, A4]
                     (P4, P4, P4, M3)
    """
    # So What voicing intervals: 0, 5, 10, 15, 19
    # (root, +P4, +P4, +P4, +M3)
    intervals = [0, 5, 10, 15, 19]

    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in intervals:
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes
