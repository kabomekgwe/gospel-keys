"""
Comprehensive Scale Library

All scales and modes for music theory analysis and education.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from app.theory.interval_utils import semitone_to_note, note_to_semitone


@dataclass
class Scale:
    """Scale definition with intervals and metadata"""
    name: str
    intervals: Tuple[int, ...]  # Semitone intervals from root
    category: str
    aliases: Tuple[str, ...] = ()
    description: str = ""


# ============================================================================
# MAJOR SCALE MODES
# ============================================================================

IONIAN = Scale(
    name="Ionian",
    intervals=(0, 2, 4, 5, 7, 9, 11),
    category="mode",
    aliases=("Major", "Major Scale"),
    description="The major scale. Bright and happy."
)

DORIAN = Scale(
    name="Dorian",
    intervals=(0, 2, 3, 5, 7, 9, 10),
    category="mode",
    aliases=("Dorian Minor",),
    description="Minor mode with raised 6th. Jazz and folk favorite."
)

PHRYGIAN = Scale(
    name="Phrygian",
    intervals=(0, 1, 3, 5, 7, 8, 10),
    category="mode",
    aliases=(),
    description="Minor mode with b2. Spanish/Flamenco sound."
)

LYDIAN = Scale(
    name="Lydian",
    intervals=(0, 2, 4, 6, 7, 9, 11),
    category="mode",
    aliases=(),
    description="Major mode with #4. Dreamy, floating quality."
)

MIXOLYDIAN = Scale(
    name="Mixolydian",
    intervals=(0, 2, 4, 5, 7, 9, 10),
    category="mode",
    aliases=("Dominant Scale",),
    description="Major with b7. Blues, rock, and dominant 7th chords."
)

AEOLIAN = Scale(
    name="Aeolian",
    intervals=(0, 2, 3, 5, 7, 8, 10),
    category="mode",
    aliases=("Natural Minor", "Minor Scale"),
    description="The natural minor scale."
)

LOCRIAN = Scale(
    name="Locrian",
    intervals=(0, 1, 3, 5, 6, 8, 10),
    category="mode",
    aliases=(),
    description="Diminished mode with b2 and b5. Rarely used melodically."
)

# ============================================================================
# MINOR SCALE VARIANTS
# ============================================================================

HARMONIC_MINOR = Scale(
    name="Harmonic Minor",
    intervals=(0, 2, 3, 5, 7, 8, 11),
    category="minor",
    aliases=(),
    description="Natural minor with raised 7th. Creates V7 chord in minor."
)

MELODIC_MINOR = Scale(
    name="Melodic Minor",
    intervals=(0, 2, 3, 5, 7, 9, 11),
    category="minor",
    aliases=("Jazz Minor", "Ascending Melodic Minor"),
    description="Minor with raised 6th and 7th. Foundation for many jazz scales."
)

# ============================================================================
# JAZZ / MODERN SCALES
# ============================================================================

BLUES_SCALE = Scale(
    name="Blues Scale",
    intervals=(0, 3, 5, 6, 7, 10),
    category="blues",
    aliases=("Minor Blues",),
    description="Minor pentatonic with added b5 (blue note)."
)

MAJOR_BLUES = Scale(
    name="Major Blues",
    intervals=(0, 2, 3, 4, 7, 9),
    category="blues",
    aliases=(),
    description="Major pentatonic with added b3."
)

PENTATONIC_MAJOR = Scale(
    name="Major Pentatonic",
    intervals=(0, 2, 4, 7, 9),
    category="pentatonic",
    aliases=(),
    description="Five-note major scale. Universal across cultures."
)

PENTATONIC_MINOR = Scale(
    name="Minor Pentatonic",
    intervals=(0, 3, 5, 7, 10),
    category="pentatonic",
    aliases=(),
    description="Five-note minor scale. Rock and blues staple."
)

WHOLE_TONE = Scale(
    name="Whole Tone",
    intervals=(0, 2, 4, 6, 8, 10),
    category="symmetric",
    aliases=(),
    description="All whole steps. Augmented, dreamy sound."
)

DIMINISHED_WHOLE_HALF = Scale(
    name="Diminished (Whole-Half)",
    intervals=(0, 2, 3, 5, 6, 8, 9, 11),
    category="symmetric",
    aliases=("Octatonic W-H", "Diminished Scale"),
    description="Alternating W-H pattern. Over diminished chords."
)

DIMINISHED_HALF_WHOLE = Scale(
    name="Diminished (Half-Whole)",
    intervals=(0, 1, 3, 4, 6, 7, 9, 10),
    category="symmetric",
    aliases=("Octatonic H-W", "Dominant Diminished"),
    description="Alternating H-W pattern. Over dominant 7b9 chords."
)

ALTERED_SCALE = Scale(
    name="Altered Scale",
    intervals=(0, 1, 3, 4, 6, 8, 10),
    category="jazz",
    aliases=("Super Locrian", "Diminished Whole Tone"),
    description="7th mode of melodic minor. Over altered dominant chords."
)

LYDIAN_DOMINANT = Scale(
    name="Lydian Dominant",
    intervals=(0, 2, 4, 6, 7, 9, 10),
    category="jazz",
    aliases=("Lydian b7", "Overtone Scale"),
    description="4th mode of melodic minor. Over 7#11 chords."
)

BEBOP_DOMINANT = Scale(
    name="Bebop Dominant",
    intervals=(0, 2, 4, 5, 7, 9, 10, 11),
    category="bebop",
    aliases=(),
    description="Mixolydian with added M7. 8-note scale for smooth lines."
)

BEBOP_MAJOR = Scale(
    name="Bebop Major",
    intervals=(0, 2, 4, 5, 7, 8, 9, 11),
    category="bebop",
    aliases=(),
    description="Major scale with added #5."
)

BEBOP_MINOR = Scale(
    name="Bebop Minor",
    intervals=(0, 2, 3, 5, 7, 8, 9, 10),
    category="bebop",
    aliases=("Bebop Dorian",),
    description="Dorian with added M3. Smooth minor lines."
)

# ============================================================================
# EXOTIC / WORLD SCALES
# ============================================================================

PHRYGIAN_DOMINANT = Scale(
    name="Phrygian Dominant",
    intervals=(0, 1, 4, 5, 7, 8, 10),
    category="exotic",
    aliases=("Spanish Phrygian", "Jewish Scale", "Freygish"),
    description="5th mode of harmonic minor. Middle Eastern/Spanish sound."
)

HUNGARIAN_MINOR = Scale(
    name="Hungarian Minor",
    intervals=(0, 2, 3, 6, 7, 8, 11),
    category="exotic",
    aliases=("Double Harmonic Minor", "Gypsy Minor"),
    description="Harmonic minor with #4. Eastern European flavor."
)

DOUBLE_HARMONIC_MAJOR = Scale(
    name="Double Harmonic Major",
    intervals=(0, 1, 4, 5, 7, 8, 11),
    category="exotic",
    aliases=("Arabic Major", "Byzantine Scale"),
    description="Major with b2 and b6. Arabic/Byzantine sound."
)

HIRAJOSHI = Scale(
    name="Hirajoshi",
    intervals=(0, 2, 3, 7, 8),
    category="exotic",
    aliases=(),
    description="Japanese pentatonic scale."
)

IWATO = Scale(
    name="Iwato",
    intervals=(0, 1, 5, 6, 10),
    category="exotic",
    aliases=(),
    description="Japanese scale with dark, unsettling quality."
)

YO_SCALE = Scale(
    name="Yo Scale",
    intervals=(0, 2, 5, 7, 9),
    category="exotic",
    aliases=("Japanese Pentatonic",),
    description="Traditional Japanese pentatonic."
)


# ============================================================================
# SCALE LIBRARY
# ============================================================================

SCALE_LIBRARY: Dict[str, Scale] = {
    # Modes
    "ionian": IONIAN,
    "major": IONIAN,
    "dorian": DORIAN,
    "phrygian": PHRYGIAN,
    "lydian": LYDIAN,
    "mixolydian": MIXOLYDIAN,
    "aeolian": AEOLIAN,
    "natural_minor": AEOLIAN,
    "minor": AEOLIAN,
    "locrian": LOCRIAN,
    
    # Minor variants
    "harmonic_minor": HARMONIC_MINOR,
    "melodic_minor": MELODIC_MINOR,
    "jazz_minor": MELODIC_MINOR,
    
    # Blues/Pentatonic
    "blues": BLUES_SCALE,
    "minor_blues": BLUES_SCALE,
    "major_blues": MAJOR_BLUES,
    "pentatonic_major": PENTATONIC_MAJOR,
    "pentatonic_minor": PENTATONIC_MINOR,
    
    # Symmetric
    "whole_tone": WHOLE_TONE,
    "diminished_wh": DIMINISHED_WHOLE_HALF,
    "diminished_hw": DIMINISHED_HALF_WHOLE,
    
    # Jazz
    "altered": ALTERED_SCALE,
    "super_locrian": ALTERED_SCALE,
    "lydian_dominant": LYDIAN_DOMINANT,
    "bebop_dominant": BEBOP_DOMINANT,
    "bebop_major": BEBOP_MAJOR,
    "bebop_minor": BEBOP_MINOR,
    
    # Exotic
    "phrygian_dominant": PHRYGIAN_DOMINANT,
    "hungarian_minor": HUNGARIAN_MINOR,
    "double_harmonic_major": DOUBLE_HARMONIC_MAJOR,
    "hirajoshi": HIRAJOSHI,
    "iwato": IWATO,
    "yo": YO_SCALE,
}


def get_scale(name: str) -> Scale:
    """Get scale by name (case-insensitive)."""
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key not in SCALE_LIBRARY:
        raise ValueError(f"Unknown scale: {name}")
    return SCALE_LIBRARY[key]


def get_scale_notes(root: str, scale_name: str, prefer_sharps: bool = True) -> List[str]:
    """
    Get all notes in a scale starting from a root.
    
    Args:
        root: Root note (e.g., "C", "F#")
        scale_name: Scale name (e.g., "major", "dorian")
        prefer_sharps: Use sharps instead of flats
    
    Returns:
        List of note names
    """
    scale = get_scale(scale_name)
    root_semitone = note_to_semitone(root)
    
    return [
        semitone_to_note((root_semitone + interval) % 12, prefer_sharps)
        for interval in scale.intervals
    ]


def list_scales_by_category(category: str) -> List[Scale]:
    """Get all scales in a category."""
    return [s for s in SCALE_LIBRARY.values() if s.category == category]


def get_all_categories() -> List[str]:
    """Get list of all scale categories."""
    return list(set(s.category for s in SCALE_LIBRARY.values()))
