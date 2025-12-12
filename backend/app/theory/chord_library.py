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
    "6/9": SIX_NINE, "69": SIX_NINE,
    
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
