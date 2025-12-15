"""
Voicing Types and Styles

Defines voicing style enumerations and metadata classes for advanced
chord voicings used in jazz, classical, and contemporary music.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class VoicingStyle(Enum):
    """
    Voicing style definitions for chord generation.

    These styles represent different ways to voice the same chord,
    commonly used in jazz piano, arranging, and composition.
    """

    # ============================================================================
    # BASIC SPACING
    # ============================================================================

    CLOSE = "close"
    """All notes within one octave (dense voicing)"""

    OPEN = "open"
    """Notes spread across 1-2 octaves (wider spacing)"""

    SPREAD = "spread"
    """Wide spacing across 2+ octaves"""

    # ============================================================================
    # DROP VOICINGS
    # ============================================================================

    DROP_2 = "drop_2"
    """
    Drop-2 voicing: 2nd voice from top dropped one octave.

    Standard jazz voicing for horns and piano.
    Example: Cmaj7 close [C4, E4, G4, B4] → drop-2 [C4, G3, B4, E4]
    """

    DROP_3 = "drop_3"
    """
    Drop-3 voicing: 3rd voice from top dropped one octave.

    Creates wider spacing than drop-2.
    Example: Cmaj7 close [C4, E4, G4, B4] → drop-3 [C4, E3, B4, G4]
    """

    DROP_2_4 = "drop_2_4"
    """
    Drop-2-4 voicing: 2nd AND 4th voices from top dropped one octave.

    Very wide voicing, common in big band arranging.
    Example: Cmaj7 close [C4, E4, G4, B4] → drop-2-4 [C3, G3, B4, E4]
    """

    DROP_2_3 = "drop_2_3"
    """
    Drop-2-3 voicing: 2nd AND 3rd voices from top dropped one octave.

    Alternative wide voicing.
    """

    # ============================================================================
    # ROOTLESS VOICINGS (Bill Evans Style)
    # ============================================================================

    ROOTLESS_A = "rootless_a"
    """
    Rootless voicing Type A: 3-5-7-9 (3rd on bottom).

    Bill Evans style left-hand voicing.
    Bass player covers the root.
    Example: Cmaj7 → [E, G, B, D]
    """

    ROOTLESS_B = "rootless_b"
    """
    Rootless voicing Type B: 7-9-3-5 (7th on bottom).

    Bill Evans style left-hand voicing.
    Inverted form of Type A.
    Example: Cmaj7 → [B, D, E, G]
    """

    # ============================================================================
    # SHELL VOICINGS
    # ============================================================================

    SHELL = "shell"
    """
    Shell voicing: Root-3-7 only (no 5th).

    Essential tones for comping, commonly used in jazz guitar/piano.
    Example: Cmaj7 → [C, E, B]
    """

    SHELL_INVERTED = "shell_inv"
    """
    Shell voicing inverted: Root-7-3.

    Wider spacing variation of shell voicing.
    Example: Cmaj7 → [C, B, E]
    """

    GUIDE_TONES = "guide_tones"
    """
    Guide tones only: 3rd and 7th (no root).

    Minimal voicing for voice leading, used in walking bass context.
    Example: Cmaj7 → [E, B]
    """

    # ============================================================================
    # QUARTAL/QUINTAL
    # ============================================================================

    QUARTAL = "quartal"
    """
    Quartal voicing: Built on perfect 4ths.

    Modern/modal sound (McCoy Tyner style).
    Example: Dm11 → [D, G, C, F]
    """

    QUINTAL = "quintal"
    """
    Quintal voicing: Built on perfect 5ths.

    Open, modern sound.
    Example: Dm11 → [D, A, E, B]
    """

    SO_WHAT = "so_what"
    """
    So What voicing: Quartal stack + major 3rd (Bill Evans).

    Made famous by Miles Davis "So What".
    Example: Dm11 → [D, G, C, F, A] (4ths + M3)
    """

    # ============================================================================
    # BLOCK CHORDS
    # ============================================================================

    BLOCK_CHORD = "block"
    """
    Block chord / Locked hands: Melody doubled in both hands.

    George Shearing style.
    Right hand: melody + harmony
    Left hand: doubled melody (octave below) + bass
    """

    FOUR_WAY_CLOSE = "four_way"
    """
    Four-way close: 4-note close voicing with melody on top.

    Common in big band sax sections.
    All notes within an octave, melody note on top.
    """

    # ============================================================================
    # CLUSTER VOICINGS
    # ============================================================================

    CLUSTER_CLOSE = "cluster_close"
    """
    Close cluster: Adjacent semitones (minor 2nds).

    Dissonant, modern sound.
    Example: [C, C#, D]
    """

    CLUSTER_OPEN = "cluster_open"
    """
    Open cluster: Mix of minor 2nds and major 2nds.

    Less dense than close cluster.
    Example: [C, D, D#]
    """


@dataclass
class VoicingSpec:
    """
    Specification for a chord voicing.

    Used to configure advanced voicing generation with precise control
    over intervals, omissions, and doublings.
    """

    style: VoicingStyle
    inversion: int = 0
    omit: Optional[List[int]] = None  # Intervals to omit (e.g., [7] = no 5th)
    double: Optional[List[int]] = None  # Intervals to double
    octave: int = 4
    spread_factor: float = 1.0  # For open/spread voicings


@dataclass
class VoicingMetadata:
    """
    Metadata about a generated voicing.

    Provides analysis information about the voicing for educational purposes
    or voice leading analysis.
    """

    style: VoicingStyle
    num_notes: int
    range_semitones: int  # Range from lowest to highest note
    has_root: bool
    has_third: bool
    has_seventh: bool
    intervals_from_bass: List[int]
    description: str


def get_voicing_description(style: VoicingStyle) -> str:
    """Get human-readable description of a voicing style."""
    descriptions = {
        VoicingStyle.CLOSE: "Close position - all notes within one octave",
        VoicingStyle.OPEN: "Open position - spread across 1-2 octaves",
        VoicingStyle.SPREAD: "Spread voicing - wide spacing across 2+ octaves",
        VoicingStyle.DROP_2: "Drop-2 - second voice from top dropped an octave",
        VoicingStyle.DROP_3: "Drop-3 - third voice from top dropped an octave",
        VoicingStyle.DROP_2_4: "Drop-2-4 - second and fourth voices dropped",
        VoicingStyle.DROP_2_3: "Drop-2-3 - second and third voices dropped",
        VoicingStyle.ROOTLESS_A: "Rootless Type A - 3-5-7-9 (Bill Evans style)",
        VoicingStyle.ROOTLESS_B: "Rootless Type B - 7-9-3-5 (Bill Evans style)",
        VoicingStyle.SHELL: "Shell voicing - root-3-7 only",
        VoicingStyle.SHELL_INVERTED: "Shell inverted - root-7-3",
        VoicingStyle.GUIDE_TONES: "Guide tones - 3rd and 7th only",
        VoicingStyle.QUARTAL: "Quartal - built on perfect 4ths",
        VoicingStyle.QUINTAL: "Quintal - built on perfect 5ths",
        VoicingStyle.SO_WHAT: "So What voicing - quartal stack + major 3rd",
        VoicingStyle.BLOCK_CHORD: "Block chord - locked hands style (Shearing)",
        VoicingStyle.FOUR_WAY_CLOSE: "Four-way close - 4-note close with melody top",
        VoicingStyle.CLUSTER_CLOSE: "Close cluster - adjacent semitones",
        VoicingStyle.CLUSTER_OPEN: "Open cluster - mixed m2 and M2 intervals",
    }
    return descriptions.get(style, "Unknown voicing style")


__all__ = [
    "VoicingStyle",
    "VoicingSpec",
    "VoicingMetadata",
    "get_voicing_description",
]
