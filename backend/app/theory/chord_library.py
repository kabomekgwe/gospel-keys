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


# ============================================================================
# CATEGORY 1: QUARTAL/QUINTAL HARMONY (McCoy Tyner, Chick Corea)
# ============================================================================

def get_quartal_voicing(
    root: str,
    num_notes: int = 4,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate quartal voicing: stacked perfect 4ths.

    McCoy Tyner / Chick Corea style modern jazz voicing.
    Creates open, modal sound commonly used in modal jazz.

    Args:
        root: Root note
        num_notes: Number of notes (3-6)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        get_quartal_voicing('D', 4, 3) → ['D3', 'G3', 'C4', 'F4']
        (4ths: D-G-C-F)
    """
    if num_notes < 3 or num_notes > 6:
        raise ValueError("num_notes must be between 3 and 6")

    # Stack perfect 4ths (5 semitones each)
    intervals = [i * 5 for i in range(num_notes)]

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


def get_quintal_voicing(
    root: str,
    num_notes: int = 4,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate quintal voicing: stacked perfect 5ths.

    Open, modern sound. Creates wide spacing.
    Used in contemporary jazz and film scores.

    Args:
        root: Root note
        num_notes: Number of notes (3-5)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        get_quintal_voicing('C', 3, 3) → ['C3', 'G3', 'D4']
        (5ths: C-G-D)
    """
    if num_notes < 3 or num_notes > 5:
        raise ValueError("num_notes must be between 3 and 5")

    # Stack perfect 5ths (7 semitones each)
    intervals = [i * 7 for i in range(num_notes)]

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


def get_kenny_barron_voicing(
    root: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate Kenny Barron style open minor 11th voicing.

    Beautiful open-sounding voicing ideal for minor chords.
    Structure: root, b3, P4, b7, 9

    Args:
        root: Root note (minor chord root)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of 5 note names

    Example:
        get_kenny_barron_voicing('D', 3) → ['D3', 'F3', 'G3', 'C4', 'E4']
        (Dm11 voicing: root, m3, P4, m7, 9)
    """
    # Kenny Barron minor 11th intervals: 0, 3, 5, 10, 14
    # (root, m3, P4, m7, M9)
    intervals = [0, 3, 5, 10, 14]

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


def get_quartal_tertian_hybrid(
    root: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate hybrid voicing mixing 4ths and 3rds.

    Combines quartal (4ths) and tertian (3rds) harmony.
    Creates rich, contemporary sound.

    Args:
        root: Root note
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of 5 note names

    Example:
        get_quartal_tertian_hybrid('C', 3) → ['C3', 'F3', 'Bb3', 'D4', 'G4']
        (P4, P4, M3, P4)
    """
    # Hybrid intervals: 0, 5, 10, 14, 19
    # (root, +P4, +P4, +M3, +P4)
    intervals = [0, 5, 10, 14, 19]

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


# ============================================================================
# CATEGORY 2: CLUSTER VOICINGS (Contemporary/Modern)
# ============================================================================

def get_close_cluster(
    root: str,
    num_notes: int = 3,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate close cluster: adjacent semitones (minor 2nds).

    Dissonant, modern sound. All notes within semitone distance.
    Used in contemporary classical and avant-garde jazz.

    Args:
        root: Root note
        num_notes: Number of notes (3-5)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        get_close_cluster('C', 3, 4) → ['C4', 'C#4', 'D4']
        (adjacent semitones)
    """
    if num_notes < 3 or num_notes > 5:
        raise ValueError("num_notes must be between 3 and 5")

    # Stack minor 2nds (1 semitone each)
    intervals = [i for i in range(num_notes)]

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


def get_open_cluster(
    root: str,
    num_notes: int = 4,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate open cluster: mix of minor 2nds and major 2nds.

    Less dense than close cluster but still dissonant.
    Creates textural effect in modern harmony.

    Args:
        root: Root note
        num_notes: Number of notes (3-5)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with octaves

    Example:
        get_open_cluster('C', 4, 4) → ['C4', 'D4', 'D#4', 'F4']
        (M2, m2, M2)
    """
    if num_notes < 3 or num_notes > 5:
        raise ValueError("num_notes must be between 3 and 5")

    # Alternate M2 (2 semitones) and m2 (1 semitone)
    intervals = [0]
    current = 0
    for i in range(1, num_notes):
        if i % 2 == 1:
            current += 2  # Major 2nd
        else:
            current += 1  # Minor 2nd
        intervals.append(current)

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


def get_tone_cluster_chord(
    root: str,
    quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate tone cluster by filling all semitones between chord tones.

    Takes a standard chord and fills in all chromatic notes
    between lowest and highest tones.

    Args:
        root: Root note
        quality: Chord quality (from CHORD_LIBRARY)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with chromatic fill

    Example:
        get_tone_cluster_chord('C', 'maj', 4) → ['C4', 'C#4', 'D4', 'D#4', 'E4']
        (fills C-E with all semitones)
    """
    chord = get_chord_type(quality)

    # Get the range from lowest to highest chord tone
    min_interval = 0
    max_interval = max(chord.intervals)

    # Fill all semitones in this range
    intervals = list(range(min_interval, max_interval + 1))

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


# ============================================================================
# CATEGORY 3: SPREAD & ORCHESTRAL VOICINGS
# ============================================================================

def apply_spread_voicing(
    midi_notes: List[int],
    spread_factor: float = 2.0
) -> List[int]:
    """
    Apply spread voicing transformation: widen intervals by factor.

    Takes a close voicing and spreads it across wider range.
    Creates orchestral sound.

    Args:
        midi_notes: List of MIDI note numbers
        spread_factor: Multiplier for intervals (1.0 = no change, 2.0 = double)

    Returns:
        List of MIDI notes with widened spacing

    Example:
        apply_spread_voicing([60, 64, 67], 2.0) → [60, 68, 74]
        (intervals doubled)
    """
    if len(midi_notes) < 2:
        return midi_notes

    bass = midi_notes[0]
    result = [bass]

    for i in range(1, len(midi_notes)):
        original_interval = midi_notes[i] - bass
        new_interval = int(original_interval * spread_factor)
        result.append(bass + new_interval)

    return result


def get_split_bass_voicing(
    root: str,
    quality: str,
    bass_octave: int = 2,
    upper_octave: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate split bass voicing: 2+ octave gap between bass and upper.

    Orchestral spacing with wide gap between bass note and harmony.
    Creates huge, cinematic sound.

    Args:
        root: Root note
        quality: Chord quality
        bass_octave: Octave for bass note
        upper_octave: Octave for upper structure (must be >= bass_octave + 2)
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with split bass

    Example:
        get_split_bass_voicing('C', 'maj7', 2, 5)
        → ['C2', 'E5', 'G5', 'B5']
    """
    if upper_octave < bass_octave + 2:
        raise ValueError("upper_octave must be at least 2 octaves above bass_octave")

    chord = get_chord_type(quality)
    root_semitone = note_to_semitone(root)

    # Bass note
    bass_midi = bass_octave * 12 + root_semitone
    bass_note = f"{root}{bass_octave}"

    # Upper structure (all other chord tones)
    upper_base_midi = upper_octave * 12 + root_semitone

    notes = [bass_note]
    for interval in chord.intervals[1:]:  # Skip root (already have bass)
        midi_note = upper_base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


def get_wide_spread_voicing(
    root: str,
    quality: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate wide spread voicing for orchestral sound.

    Applies automatic spreading based on chord size.
    2-3 octave spread for full, orchestral texture.

    Args:
        root: Root note
        quality: Chord quality
        octave: Base octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with wide spacing
    """
    # Get close voicing first
    close_notes = get_chord_notes_with_inversion(root, quality, 0, octave, prefer_sharps)

    # Convert to MIDI
    midi_notes = []
    for note_str in close_notes:
        note_name = ''.join(c for c in note_str if not c.isdigit())
        note_oct = int(''.join(c for c in note_str if c.isdigit()))
        semitone = note_to_semitone(note_name)
        midi = note_oct * 12 + semitone
        midi_notes.append(midi)

    # Apply spread
    spread_midi = apply_spread_voicing(midi_notes, spread_factor=2.5)

    # Convert back to note names
    result = []
    for midi_note in spread_midi:
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        result.append(f"{note_name}{note_octave}")

    return result


# ============================================================================
# CATEGORY 4: PARALLEL & CHROMATIC MOTION
# ============================================================================

def get_parallel_voicing(
    root: str,
    quality: str,
    steps: int = 4,
    step_interval: int = 2,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[List[str]]:
    """
    Generate parallel voicing motion: same voicing moved in parallel steps.

    Creates smooth, modern sound by moving entire voicing structure
    chromatically or diatonically.

    Args:
        root: Starting root note
        quality: Chord quality
        steps: Number of parallel steps
        step_interval: Semitones per step (1=chromatic, 2=whole-tone, etc.)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of voicings, each as List[str]

    Example:
        get_parallel_voicing('C', 'maj7', 3, 2)
        → [['C3', 'E3', 'G3', 'B3'],
           ['D3', 'F#3', 'A3', 'C#4'],
           ['E3', 'G#3', 'B3', 'D#4']]
    """
    result = []

    for step in range(steps):
        # Calculate new root
        root_semitone = note_to_semitone(root)
        new_semitone = (root_semitone + step * step_interval) % 12
        new_root = semitone_to_note(new_semitone, prefer_sharps)

        # Generate voicing at new root
        voicing = get_chord_notes_with_inversion(new_root, quality, 0, octave, prefer_sharps)
        result.append(voicing)

    return result


def get_chromatic_voice_leading(
    root1: str,
    quality1: str,
    root2: str,
    quality2: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[List[str]]:
    """
    Generate chromatic voice leading between two chords.

    Creates smooth chromatic interpolation with passing chords
    between two target chords.

    Args:
        root1: First chord root
        quality1: First chord quality
        root2: Second chord root
        quality2: Second chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of voicings including chromatic passing chords

    Example:
        get_chromatic_voice_leading('C', 'maj7', 'F', 'maj7')
        → Smooth chromatic motion from Cmaj7 to Fmaj7
    """
    # Get starting and ending voicings
    start_voicing = get_chord_notes_with_inversion(root1, quality1, 0, octave, prefer_sharps)
    end_voicing = get_chord_notes_with_inversion(root2, quality2, 0, octave, prefer_sharps)

    # Convert to MIDI for interpolation
    def note_to_midi(note_str: str) -> int:
        note_name = ''.join(c for c in note_str if not c.isdigit())
        note_oct = int(''.join(c for c in note_str if c.isdigit()))
        semitone = note_to_semitone(note_name)
        return note_oct * 12 + semitone

    start_midi = [note_to_midi(n) for n in start_voicing]
    end_midi = [note_to_midi(n) for n in end_voicing]

    # Ensure same number of voices
    if len(start_midi) != len(end_midi):
        # Pad shorter voicing (simple approach)
        while len(start_midi) < len(end_midi):
            start_midi.append(start_midi[-1] + 12)
        while len(end_midi) < len(start_midi):
            end_midi.append(end_midi[-1] + 12)

    # Calculate distance and generate passing chords
    max_distance = max(abs(end_midi[i] - start_midi[i]) for i in range(len(start_midi)))
    num_steps = max_distance + 1

    result = []
    for step in range(num_steps):
        t = step / (num_steps - 1) if num_steps > 1 else 1.0

        # Interpolate each voice
        midi_notes = []
        for i in range(len(start_midi)):
            interpolated = start_midi[i] + int((end_midi[i] - start_midi[i]) * t)
            midi_notes.append(interpolated)

        # Convert back to note names
        notes = []
        for midi_note in midi_notes:
            pitch_class = midi_note % 12
            note_octave = midi_note // 12
            note_name = semitone_to_note(pitch_class, prefer_sharps)
            notes.append(f"{note_name}{note_octave}")

        result.append(notes)

    return result


def get_chromatic_neighbor_voicing(
    root: str,
    quality: str,
    neighbor_type: str = "upper",
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate chromatic neighbor chord (passing chord).

    Creates tension chord a semitone above or below target chord.
    Used in chromatic voice leading and jazz harmony.

    Args:
        root: Root note
        quality: Chord quality
        neighbor_type: "upper" (semitone above) or "lower" (semitone below)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names for neighbor chord

    Example:
        get_chromatic_neighbor_voicing('C', 'maj7', 'upper')
        → Chromatic neighbor a semitone above Cmaj7
    """
    root_semitone = note_to_semitone(root)

    if neighbor_type == "upper":
        neighbor_semitone = (root_semitone + 1) % 12
    elif neighbor_type == "lower":
        neighbor_semitone = (root_semitone - 1) % 12
    else:
        raise ValueError("neighbor_type must be 'upper' or 'lower'")

    neighbor_root = semitone_to_note(neighbor_semitone, prefer_sharps)
    return get_chord_notes_with_inversion(neighbor_root, quality, 0, octave, prefer_sharps)


# ============================================================================
# CATEGORY 5: TRITONE SUBSTITUTION
# ============================================================================

def get_tritone_substitute_voicing(
    root: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate tritone substitution voicing.

    Substitutes dominant 7 chord with another dominant 7 a tritone away.
    Creates chromatic bass motion in ii-V-I progressions.

    Args:
        root: Original dominant 7 root
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names for tritone substitute

    Example:
        get_tritone_substitute_voicing('G', 3)  # G7 → Db7
        → ['C#3', 'F3', 'G#3', 'B3']  (Db7)
    """
    root_semitone = note_to_semitone(root)
    tritone_semitone = (root_semitone + 6) % 12  # Tritone = 6 semitones
    tritone_root = semitone_to_note(tritone_semitone, prefer_sharps)

    return get_chord_notes_with_inversion(tritone_root, '7', 0, octave, prefer_sharps)


def get_tritone_sub_progression(
    key_root: str = 'C',
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[tuple]:
    """
    Generate ii-bII-I progression with tritone substitution.

    Classic jazz progression: ii-V-I becomes ii-bII-I with tritone sub.
    Creates smooth chromatic bass motion.

    Args:
        key_root: Key center (for I chord)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of (chord_name, voicing) tuples

    Example:
        get_tritone_sub_progression('C', 3)
        → [('Dm7', [...]), ('Db7', [...]), ('Cmaj7', [...])]
    """
    # Calculate ii and I chords
    root_semitone = note_to_semitone(key_root)
    ii_semitone = (root_semitone + 2) % 12  # ii is whole step above I
    ii_root = semitone_to_note(ii_semitone, prefer_sharps)

    # ii chord (minor 7)
    ii_voicing = get_chord_notes_with_inversion(ii_root, 'm7', 0, octave, prefer_sharps)

    # bII chord (tritone sub for V7)
    v_semitone = (root_semitone + 7) % 12  # V is perfect 5th above I
    tritone_semitone = (v_semitone + 6) % 12  # Tritone away
    tritone_root = semitone_to_note(tritone_semitone, prefer_sharps)
    tritone_voicing = get_chord_notes_with_inversion(tritone_root, '7', 0, octave, prefer_sharps)

    # I chord (major 7)
    i_voicing = get_chord_notes_with_inversion(key_root, 'maj7', 0, octave, prefer_sharps)

    return [
        (f"{ii_root}m7", ii_voicing),
        (f"{tritone_root}7", tritone_voicing),
        (f"{key_root}maj7", i_voicing)
    ]


# ============================================================================
# CATEGORY 6: UPPER EXTENSION STACKS
# ============================================================================

def get_upper_structure_stack(
    root: str,
    quality: str,
    extensions: List[int],
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate voicing with upper structure extensions stacked.

    Adds 9th, 11th, 13th, and altered extensions to chord.
    Creates rich, colorful harmony.

    Args:
        root: Root note
        quality: Base chord quality
        extensions: List of extension intervals (e.g., [9, 11, 13])
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with extensions

    Example:
        get_upper_structure_stack('C', '7', [9, 11, 13], 3)
        → C13 with all extensions: C-E-G-Bb-D-F-A
    """
    chord = get_chord_type(quality)
    intervals = list(chord.intervals)

    # Add extensions (convert scale degrees to intervals)
    extension_intervals = {
        9: 14,   # Major 9th (octave + M2)
        11: 17,  # Perfect 11th (octave + P4)
        13: 21,  # Major 13th (octave + M6)
        '#9': 15,  # Sharp 9 (augmented 9th)
        'b9': 13,  # Flat 9 (minor 9th)
        '#11': 18, # Sharp 11 (augmented 11th)
        'b13': 20  # Flat 13 (minor 13th)
    }

    for ext in extensions:
        if ext in extension_intervals:
            interval = extension_intervals[ext]
            if interval not in intervals:
                intervals.append(interval)

    # Generate notes
    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in sorted(intervals):
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


def get_stacked_extensions(
    root: str,
    max_extension: int = 13,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate chord with all extensions up to specified degree.

    Stacks 9th, 11th, 13th systematically.
    Creates dense, colorful jazz harmony.

    Args:
        root: Root note
        max_extension: Maximum extension (9, 11, or 13)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with stacked extensions

    Example:
        get_stacked_extensions('C', 13, 3)
        → C-E-G-Bb-D-F-A (C13 with all extensions)
    """
    # Start with dominant 7 base
    intervals = [0, 4, 7, 10]  # Root, M3, P5, m7

    # Add extensions based on max_extension
    if max_extension >= 9:
        intervals.append(14)  # Major 9th
    if max_extension >= 11:
        intervals.append(17)  # Perfect 11th
    if max_extension >= 13:
        intervals.append(21)  # Major 13th

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


def get_altered_upper_structure(
    root: str,
    alterations: List[str],
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate altered dominant voicing (#9, b9, #11, b13).

    Creates tension-filled altered dominant sound.
    Common in bebop and modern jazz.

    Args:
        root: Root note
        alterations: List of alterations (e.g., ['b9', '#9', '#11'])
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with alterations

    Example:
        get_altered_upper_structure('G', ['b9', '#11', 'b13'], 3)
        → G7alt with b9, #11, b13
    """
    # Start with dominant 7 base (root, 3, 5, b7)
    intervals = [0, 4, 7, 10]

    # Add alterations
    alteration_intervals = {
        'b9': 13,   # Flat 9 (minor 9th)
        '#9': 15,   # Sharp 9 (augmented 9th)
        '#11': 18,  # Sharp 11 (augmented 11th)
        'b13': 20   # Flat 13 (minor 13th)
    }

    for alt in alterations:
        if alt in alteration_intervals:
            intervals.append(alteration_intervals[alt])

    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in sorted(intervals):
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


# ============================================================================
# CATEGORY 7: SLASH CHORDS & POLYCHORDS
# ============================================================================

def parse_slash_chord_symbol(symbol: str) -> tuple:
    """
    Parse slash chord notation (e.g., "D/C", "Am7/G").

    Args:
        symbol: Slash chord symbol

    Returns:
        Tuple of (upper_root, upper_quality, bass_note)

    Example:
        parse_slash_chord_symbol("D/C") → ('D', '', 'C')
        parse_slash_chord_symbol("Am7/G") → ('A', 'm7', 'G')
    """
    if '/' not in symbol:
        raise ValueError("Symbol must contain '/' for slash chord")

    upper, bass = symbol.split('/')

    # Parse upper chord (find where quality starts)
    upper_root = upper[0]
    if len(upper) > 1 and upper[1] in ['#', 'b']:
        upper_root = upper[:2]
        upper_quality = upper[2:]
    else:
        upper_quality = upper[1:]

    return (upper_root, upper_quality if upper_quality else '', bass)


def get_slash_chord_voicing(
    upper_root: str,
    upper_quality: str,
    bass_note: str,
    upper_octave: int = 4,
    bass_octave: int = 2,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate slash chord voicing: upper chord over bass note.

    Creates polychord effect by placing specific bass note
    under upper harmony.

    Args:
        upper_root: Upper chord root
        upper_quality: Upper chord quality
        bass_note: Bass note (can differ from upper root)
        upper_octave: Octave for upper structure
        bass_octave: Octave for bass note
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names [bass, ...upper_chord]

    Example:
        get_slash_chord_voicing('D', '', 'C', 4, 2)
        → ['C2', 'D4', 'F#4', 'A4']  (D/C)
    """
    # Generate bass note
    bass_semitone = note_to_semitone(bass_note)
    bass_midi = bass_octave * 12 + bass_semitone
    bass_note_str = f"{bass_note}{bass_octave}"

    # Generate upper chord
    upper_voicing = get_chord_notes_with_inversion(
        upper_root, upper_quality, 0, upper_octave, prefer_sharps
    )

    return [bass_note_str] + upper_voicing


def get_polychord_voicing(
    lower_root: str,
    lower_quality: str,
    upper_root: str,
    upper_quality: str,
    lower_octave: int = 3,
    upper_octave: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate polychord voicing: two independent chords stacked.

    Creates complex, modern harmony by superimposing two chords.
    Used in contemporary jazz and film scores.

    Args:
        lower_root: Lower chord root
        lower_quality: Lower chord quality
        upper_root: Upper chord root
        upper_quality: Upper chord quality
        lower_octave: Octave for lower chord
        upper_octave: Octave for upper chord
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names [lower_chord, upper_chord]

    Example:
        get_polychord_voicing('C', '', 'D', '', 3, 4)
        → C major over D major polychord
    """
    lower_voicing = get_chord_notes_with_inversion(
        lower_root, lower_quality, 0, lower_octave, prefer_sharps
    )
    upper_voicing = get_chord_notes_with_inversion(
        upper_root, upper_quality, 0, upper_octave, prefer_sharps
    )

    return lower_voicing + upper_voicing


# ============================================================================
# CATEGORY 8: BLOCK CHORDS & LOCKED HANDS
# ============================================================================

def get_block_chord_voicing(
    melody_notes: List[str],
    harmony_interval: int = 7,
    bass_octave: int = 2
) -> List[str]:
    """
    Generate George Shearing style block chord (locked hands).

    Melody doubled in both hands with harmony fill.
    Right hand: melody + close harmony
    Left hand: doubled melody (octave below) + bass

    Args:
        melody_notes: List of melody note names with octaves
        harmony_interval: Interval below melody for harmony (7=P5, 4=M3, etc.)
        bass_octave: Octave for bass note

    Returns:
        List of note names for full block chord texture

    Example:
        get_block_chord_voicing(['C5', 'D5', 'E5'])
        → Block chord harmonization of melody
    """
    result = []

    for melody_note_str in melody_notes:
        # Parse melody note
        note_name = ''.join(c for c in melody_note_str if not c.isdigit())
        note_oct = int(''.join(c for c in melody_note_str if c.isdigit()))
        semitone = note_to_semitone(note_name)
        melody_midi = note_oct * 12 + semitone

        # Add bass note (melody note in lower octave)
        bass_midi = bass_octave * 12 + semitone
        bass_pitch = bass_midi % 12
        bass_note = semitone_to_note(bass_pitch)
        result.append(f"{bass_note}{bass_octave}")

        # Add harmony note (interval below melody)
        harmony_midi = melody_midi - harmony_interval
        harmony_pitch = harmony_midi % 12
        harmony_oct = harmony_midi // 12
        harmony_note = semitone_to_note(harmony_pitch)
        result.append(f"{harmony_note}{harmony_oct}")

        # Add melody note
        result.append(melody_note_str)

    return result


def get_four_way_close(
    melody_note: str,
    chord_root: str,
    chord_quality: str,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate four-way close voicing (big band style).

    4-note close voicing with melody on top.
    All notes within an octave, melody note on top.
    Common in big band sax sections.

    Args:
        melody_note: Melody note with octave (e.g., 'E5')
        chord_root: Chord root
        chord_quality: Chord quality
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of 4 note names in close position with melody on top

    Example:
        get_four_way_close('E5', 'C', 'maj7')
        → ['C5', 'E5', 'G5', 'B5'] with E on top
    """
    # Get chord tones
    chord = get_chord_type(chord_quality)

    # Parse melody note
    melody_name = ''.join(c for c in melody_note if not c.isdigit())
    melody_oct = int(''.join(c for c in melody_note if c.isdigit()))
    melody_semitone = note_to_semitone(melody_name)
    melody_midi = melody_oct * 12 + melody_semitone

    # Find chord tone closest to melody
    root_semitone = note_to_semitone(chord_root)
    chord_pitch_classes = [(root_semitone + interval) % 12 for interval in chord.intervals]

    # Build voicing with melody on top
    melody_pitch_class = melody_midi % 12

    # If melody is a chord tone, use it. Otherwise, pick closest chord tone
    if melody_pitch_class in chord_pitch_classes:
        # Use melody note and add 3 more chord tones below
        voicing_midi = [melody_midi]

        # Add 3 more chord tones below melody within an octave
        base_oct = melody_oct - 1
        for interval in reversed(chord.intervals[-3:]):
            midi = base_oct * 12 + root_semitone + interval
            if midi < melody_midi - 12:
                midi += 12
            voicing_midi.insert(0, midi)
    else:
        # Use closest 4 chord tones around melody
        voicing_midi = []
        for i in range(4):
            midi = melody_oct * 12 + root_semitone + chord.intervals[i % len(chord.intervals)]
            voicing_midi.append(midi)

    # Convert to note names
    notes = []
    for midi_note in sorted(voicing_midi)[:4]:  # Ensure only 4 notes
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


# ============================================================================
# CATEGORY 9: HYBRID & CONTEMPORARY VOICINGS
# ============================================================================

def get_seconds_voicing(
    root: str,
    num_notes: int = 4,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate voicing built on stacked 2nds.

    Modern, ambiguous sound. Creates texture without clear tonality.
    Used in contemporary jazz and classical music.

    Args:
        root: Root note
        num_notes: Number of notes (3-5)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with stacked 2nds

    Example:
        get_seconds_voicing('C', 4, 3)
        → ['C3', 'D3', 'E3', 'F#3']  (stacked M2s)
    """
    if num_notes < 3 or num_notes > 5:
        raise ValueError("num_notes must be between 3 and 5")

    # Stack major 2nds (2 semitones each)
    intervals = [i * 2 for i in range(num_notes)]

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


def get_mixed_interval_stack(
    root: str,
    intervals: List[int],
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate voicing with custom interval stack.

    Mix of 2nds, 3rds, 4ths as desired.
    Maximum flexibility for contemporary harmony.

    Args:
        root: Root note
        intervals: List of interval sizes (e.g., [2, 3, 5] for M2, m3, P4)
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names with mixed intervals

    Example:
        get_mixed_interval_stack('C', [2, 3, 5], 3)
        → ['C3', 'D3', 'F3', 'Bb3']  (M2 + m3 + P4)
    """
    # Build cumulative intervals
    cumulative_intervals = [0]
    current = 0
    for interval_size in intervals:
        current += interval_size
        cumulative_intervals.append(current)

    root_semitone = note_to_semitone(root)
    base_midi = octave * 12 + root_semitone

    notes = []
    for interval in cumulative_intervals:
        midi_note = base_midi + interval
        pitch_class = midi_note % 12
        note_octave = midi_note // 12
        note_name = semitone_to_note(pitch_class, prefer_sharps)
        notes.append(f"{note_name}{note_octave}")

    return notes


def get_bi_tonal_voicing(
    root1: str,
    root2: str,
    octave1: int = 3,
    octave2: int = 4,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate bi-tonal voicing: two keys simultaneously.

    Creates polytonal effect by superimposing two major triads.
    Avant-garde sound, used in contemporary classical and jazz.

    Args:
        root1: First key root
        root2: Second key root (should be different from root1)
        octave1: Octave for first triad
        octave2: Octave for second triad
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names from both keys

    Example:
        get_bi_tonal_voicing('C', 'F#', 3, 4)
        → C major + F# major superimposed
    """
    triad1 = get_chord_notes_with_inversion(root1, '', 0, octave1, prefer_sharps)
    triad2 = get_chord_notes_with_inversion(root2, '', 0, octave2, prefer_sharps)

    return triad1 + triad2


def get_modal_voicing(
    root: str,
    mode: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate modal voicing emphasizing mode color tones.

    Creates characteristic sound of each mode.
    Useful for modal jazz and contemporary harmony.

    Args:
        root: Root note
        mode: Mode name ('dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian')
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names emphasizing mode character

    Example:
        get_modal_voicing('D', 'dorian', 3)
        → Voicing emphasizing Dorian mode (raised 6th)
    """
    # Define characteristic intervals for each mode
    modal_structures = {
        'dorian': [0, 3, 5, 10, 14],      # m3, P4, m7, M9 (emphasize M6)
        'phrygian': [0, 1, 7, 10],        # m2, P5, m7 (emphasize b2)
        'lydian': [0, 4, 7, 11, 18],      # M3, P5, M7, #11 (emphasize #4)
        'mixolydian': [0, 4, 7, 10, 14],  # M3, P5, m7, M9 (emphasize m7)
        'aeolian': [0, 3, 7, 10],         # m3, P5, m7 (natural minor)
        'locrian': [0, 3, 6, 10]          # m3, b5, m7 (emphasize b5)
    }

    if mode.lower() not in modal_structures:
        raise ValueError(f"Unknown mode: {mode}. Must be one of {list(modal_structures.keys())}")

    intervals = modal_structures[mode.lower()]

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


# ============================================================================
# CATEGORY 10: VOICE LEADING OPTIMIZATIONS
# ============================================================================

def get_minimal_motion_voicing(
    root1: str,
    quality1: str,
    root2: str,
    quality2: str,
    octave: int = 3,
    prefer_sharps: bool = True
) -> tuple:
    """
    Find voicing with minimal voice leading motion between two chords.

    Optimizes voice leading by testing different inversions
    and selecting the combination with least total motion.

    Args:
        root1: First chord root
        quality1: First chord quality
        root2: Second chord root
        quality2: Second chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (voicing1, voicing2, total_motion)

    Example:
        get_minimal_motion_voicing('C', 'maj7', 'F', 'maj7', 3)
        → Best voice leading from Cmaj7 to Fmaj7
    """
    def note_to_midi(note_str: str) -> int:
        note_name = ''.join(c for c in note_str if not c.isdigit())
        note_oct = int(''.join(c for c in note_str if c.isdigit()))
        semitone = note_to_semitone(note_name)
        return note_oct * 12 + semitone

    def calculate_motion(voicing1: List[str], voicing2: List[str]) -> int:
        midi1 = [note_to_midi(n) for n in voicing1]
        midi2 = [note_to_midi(n) for n in voicing2]

        # Ensure same length
        min_len = min(len(midi1), len(midi2))
        return sum(abs(midi2[i] - midi1[i]) for i in range(min_len))

    # Get chord types to determine number of inversions
    chord1 = get_chord_type(quality1)
    chord2 = get_chord_type(quality2)
    num_inv1 = len(chord1.intervals)
    num_inv2 = len(chord2.intervals)

    # Try all inversion combinations
    best_motion = float('inf')
    best_voicing1 = None
    best_voicing2 = None

    for inv1 in range(num_inv1):
        for inv2 in range(num_inv2):
            v1 = get_chord_notes_with_inversion(root1, quality1, inv1, octave, prefer_sharps)
            v2 = get_chord_notes_with_inversion(root2, quality2, inv2, octave, prefer_sharps)

            motion = calculate_motion(v1, v2)
            if motion < best_motion:
                best_motion = motion
                best_voicing1 = v1
                best_voicing2 = v2

    return (best_voicing1, best_voicing2, best_motion)


def get_smooth_voice_leading_path(
    progression: List[tuple],
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[List[str]]:
    """
    Generate smooth voice leading for chord progression.

    Optimizes voice leading across entire progression
    by selecting best inversions at each step.

    Args:
        progression: List of (root, quality) tuples
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of voicings with optimized voice leading

    Example:
        get_smooth_voice_leading_path([('C', 'maj7'), ('F', 'maj7'), ('G', '7')])
        → Smooth voice leading ii-V-I
    """
    if not progression:
        return []

    # Start with root position for first chord
    root1, quality1 = progression[0]
    voicings = [get_chord_notes_with_inversion(root1, quality1, 0, octave, prefer_sharps)]

    # Optimize each subsequent chord
    for i in range(1, len(progression)):
        root_prev, quality_prev = progression[i-1]
        root_curr, quality_curr = progression[i]

        # Find best voicing for current chord given previous
        _, best_voicing, _ = get_minimal_motion_voicing(
            root_prev, quality_prev, root_curr, quality_curr, octave, prefer_sharps
        )
        voicings.append(best_voicing)

    return voicings


def get_contrary_motion_voicing(
    root: str,
    quality: str,
    inversion: int,
    octave: int = 3,
    prefer_sharps: bool = True
) -> List[str]:
    """
    Generate voicing with contrary motion emphasis.

    Arranges voices to move in opposite directions.
    Creates balanced, classical sound.

    Args:
        root: Root note
        quality: Chord quality
        inversion: Inversion number
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of note names arranged for contrary motion

    Example:
        get_contrary_motion_voicing('C', 'maj7', 1, 3)
        → 1st inversion with voices arranged for contrary motion
    """
    # Get standard inversion
    voicing = get_chord_notes_with_inversion(root, quality, inversion, octave, prefer_sharps)

    # For contrary motion, we want outer voices to move opposite directions
    # This is more about the progression, but we can prepare the voicing
    # by ensuring wide spacing
    if len(voicing) >= 4:
        # Convert to MIDI for manipulation
        def note_to_midi(note_str: str) -> int:
            note_name = ''.join(c for c in note_str if not c.isdigit())
            note_oct = int(''.join(c for c in note_str if c.isdigit()))
            semitone = note_to_semitone(note_name)
            return note_oct * 12 + semitone

        midi_notes = [note_to_midi(n) for n in voicing]

        # Spread outer voices wider
        midi_notes[0] -= 12  # Lower bass
        midi_notes[-1] += 12  # Raise soprano

        # Convert back
        result = []
        for midi_note in midi_notes:
            pitch_class = midi_note % 12
            note_octave = midi_note // 12
            note_name = semitone_to_note(pitch_class, prefer_sharps)
            result.append(f"{note_name}{note_octave}")

        return result

    return voicing
