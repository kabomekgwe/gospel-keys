"""
Expanded Lick Pattern Database - Phase 7 Week 2

Curated collection of 125+ authentic licks across 6 musical styles:
- 35 Bebop patterns (Charlie Parker, Dizzy Gillespie, Bud Powell)
- 25 Gospel patterns (Kirk Franklin, James Cleveland, Richard Smallwood)
- 20 Blues patterns (B.B. King, Ray Charles, Oscar Peterson)
- 20 Neo-Soul patterns (Robert Glasper, D'Angelo, Erykah Badu)
- 15 Modern Jazz patterns (Brad Mehldau, Chick Corea, Herbie Hancock)
- 10 Classical patterns (Bach, Mozart, Chopin)

Each pattern includes:
- Interval sequence (semitones from root)
- Rhythm pattern (beat durations)
- Characteristics (tags for searching)
- Difficulty level
- Harmonic context (which chords work best)
- Source attribution
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class LickPattern:
    """Extended lick pattern with metadata"""
    name: str
    intervals: Tuple[int, ...]          # Interval pattern in semitones
    rhythm: Tuple[float, ...]           # Note durations in beats
    characteristics: List[str]          # Tags: "chromatic", "arpeggio", etc.
    style: str                          # "bebop", "gospel", "blues", etc.
    difficulty: str                     # "beginner", "intermediate", "advanced"

    # Context metadata
    harmonic_context: List[str]         # Chords this works over
    phrase_type: str                    # "approach", "turnaround", "resolution"
    source: Optional[str] = None        # Attribution (e.g., "Charlie Parker")
    tempo_range: Tuple[int, int] = (60, 200)  # BPM range

    def total_duration(self) -> float:
        """Calculate total duration in beats"""
        return sum(self.rhythm)


# ============================================================================
# BEBOP PATTERNS (35 patterns)
# ============================================================================
# Based on Charlie Parker, Dizzy Gillespie, Bud Powell transcriptions
# Source: BopLand.org database, Aebersold jazz patterns

BEBOP_PATTERNS = [
    # Classic bebop approaches (10 patterns)
    LickPattern(
        name="bebop_3_to_b9_classic",
        intervals=(4, 5, 7, 8, 7, 5, 4, 0),  # 3-4-5-b6-5-4-3-root
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["chromatic", "descending", "bebop_scale", "approach_tone"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["dom7", "7alt", "7b9"],
        phrase_type="approach",
        source="Charlie Parker",
        tempo_range=(120, 240)
    ),

    LickPattern(
        name="bebop_enclosure_below_above",
        intervals=(0, -1, 1, 0),  # Root-below-above-root
        rhythm=(0.25, 0.25, 0.25, 0.75),
        characteristics=["chromatic", "enclosure", "target_tone"],
        style="bebop",
        difficulty="beginner",
        harmonic_context=["maj7", "min7", "dom7"],
        phrase_type="approach",
        source="Bebop vocabulary",
        tempo_range=(100, 300)
    ),

    LickPattern(
        name="bebop_enclosure_above_below",
        intervals=(0, 1, -1, 0),  # Root-above-below-root
        rhythm=(0.25, 0.25, 0.25, 0.75),
        characteristics=["chromatic", "enclosure", "target_tone"],
        style="bebop",
        difficulty="beginner",
        harmonic_context=["maj7", "min7", "dom7"],
        phrase_type="approach",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_chromatic_walk_up",
        intervals=(0, 1, 2, 3, 4, 5, 6, 7),  # Chromatic ascent
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["chromatic", "ascending", "scalar"],
        style="bebop",
        difficulty="beginner",
        harmonic_context=["dom7", "min7", "half_dim"],
        phrase_type="approach",
        source="Dizzy Gillespie"
    ),

    LickPattern(
        name="bebop_dominant_resolution",
        intervals=(10, 9, 7, 5, 4, 2, 0),  # 7-6-5-4-3-2-root
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["descending", "resolution", "guide_tones"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["dom7", "V7"],
        phrase_type="resolution",
        source="Bud Powell"
    ),

    LickPattern(
        name="bebop_blues_inflection",
        intervals=(0, 3, 4, 5, 7, 10),  # Root-b3-3-4-5-b7
        rhythm=(0.5, 0.25, 0.25, 0.5, 0.5, 1.0),
        characteristics=["blues", "chromatic", "blue_notes"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["dom7", "7#9", "blues"],
        phrase_type="approach",
        source="Charlie Parker"
    ),

    LickPattern(
        name="bebop_parker_lick_1",
        intervals=(0, 4, 7, 11, 12, 11, 9, 7),  # Root-3-5-7-octave-7-6-5
        rhythm=(0.5, 0.5, 0.5, 0.25, 0.25, 0.5, 0.5, 0.5),
        characteristics=["arpeggio", "descending", "maj7"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["maj7", "Imaj7"],
        phrase_type="approach",
        source="Charlie Parker - Now's The Time"
    ),

    LickPattern(
        name="bebop_triplet_approach",
        intervals=(5, 6, 7),  # Chromatic triplet to 5th
        rhythm=(0.33, 0.33, 0.34),
        characteristics=["chromatic", "triplet", "approach_tone"],
        style="bebop",
        difficulty="beginner",
        harmonic_context=["dom7", "maj7", "min7"],
        phrase_type="approach",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_ii_v_line",
        intervals=(0, 2, 4, 5, 7, 9, 11, 12),  # Dorian scale
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["scalar", "dorian", "ii_chord"],
        style="bebop",
        difficulty="beginner",
        harmonic_context=["min7", "ii7"],
        phrase_type="approach",
        source="ii-V-I vocabulary"
    ),

    LickPattern(
        name="bebop_altered_dominant",
        intervals=(0, 1, 3, 4, 6, 8, 10),  # Altered scale
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["altered", "tension", "chromatic"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["7alt", "7b9", "7#9"],
        phrase_type="tension",
        source="Dizzy Gillespie"
    ),

    # Bebop arpeggios and sequences (10 patterns)
    LickPattern(
        name="bebop_maj7_arpeggio",
        intervals=(0, 4, 7, 11, 12, 11, 7, 4, 0),  # Maj7 up and down
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["arpeggio", "maj7", "symmetrical"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["maj7", "Imaj7"],
        phrase_type="approach",
        source="Bud Powell"
    ),

    LickPattern(
        name="bebop_min7_arpeggio",
        intervals=(0, 3, 7, 10, 12, 10, 7, 3, 0),  # Min7 up and down
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["arpeggio", "min7", "symmetrical"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["min7", "ii7", "vi7"],
        phrase_type="approach",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_dom7_arpeggio",
        intervals=(0, 4, 7, 10, 12, 10, 7, 4, 0),  # Dom7 up and down
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["arpeggio", "dom7", "symmetrical"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["dom7", "V7"],
        phrase_type="approach",
        source="Charlie Parker"
    ),

    LickPattern(
        name="bebop_dim7_arpeggio",
        intervals=(0, 3, 6, 9, 12, 9, 6, 3, 0),  # Dim7 up and down
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["arpeggio", "dim7", "symmetrical"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["dim7", "passing_dim"],
        phrase_type="passing",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_sequence_thirds",
        intervals=(0, 2, 4, 6, 7, 9, 11, 13),  # Ascending thirds
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["sequence", "thirds", "ascending"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["maj7", "dom7"],
        phrase_type="approach",
        source="Bud Powell"
    ),

    LickPattern(
        name="bebop_octave_displacement",
        intervals=(0, 4, 7, 12, 16, 19, 24),  # Octave jumps
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["wide_intervals", "arpeggio", "dramatic"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["maj7", "dom7"],
        phrase_type="approach",
        source="Dizzy Gillespie"
    ),

    LickPattern(
        name="bebop_upper_structure_triad",
        intervals=(5, 9, 12),  # Upper structure major triad (9-#11-13)
        rhythm=(0.5, 0.5, 1.0),
        characteristics=["upper_structure", "triad", "modern"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["dom7", "V7", "altered"],
        phrase_type="tension",
        source="Modern bebop"
    ),

    LickPattern(
        name="bebop_quartal_voicing",
        intervals=(0, 5, 10),  # Perfect fourths
        rhythm=(0.5, 0.5, 1.0),
        characteristics=["quartal", "modern", "open"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["min7", "sus4", "modal"],
        phrase_type="approach",
        source="McCoy Tyner influence"
    ),

    LickPattern(
        name="bebop_turn_ornament",
        intervals=(0, 2, 0, -2, 0),  # Classical turn
        rhythm=(0.25, 0.25, 0.25, 0.25, 1.0),
        characteristics=["ornament", "turn", "classical"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["maj7", "min7"],
        phrase_type="decoration",
        source="Classical ornament"
    ),

    LickPattern(
        name="bebop_trill_ornament",
        intervals=(0, 1, 0, 1, 0, 1, 0),  # Half-step trill
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5),
        characteristics=["ornament", "trill", "chromatic"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["maj7", "min7", "dom7"],
        phrase_type="decoration",
        source="Classical ornament"
    ),

    # Bebop turnarounds and resolutions (15 patterns)
    LickPattern(
        name="bebop_I_vi_ii_V_line",
        intervals=(0, 4, 7, 9, 11, 10, 7, 5, 2, 0),  # Classic turnaround
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5),
        characteristics=["turnaround", "descending", "chord_tones"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["I_vi_ii_V"],
        phrase_type="turnaround",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_tritone_substitution",
        intervals=(0, 1, 3, 4, 7),  # b9-9-3-#11-5 (tritone sub)
        rhythm=(0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["tritone_sub", "altered", "chromatic"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["dom7", "tritone_sub"],
        phrase_type="substitution",
        source="Dizzy Gillespie"
    ),

    LickPattern(
        name="bebop_rhythm_changes_A",
        intervals=(0, 4, 7, 11, 12, 10, 7, 5),  # I chord (Rhythm changes)
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["rhythm_changes", "arpeggio", "I_chord"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["Imaj7", "rhythm_changes"],
        phrase_type="head",
        source="Charlie Parker - Anthropology"
    ),

    LickPattern(
        name="bebop_diminished_passing",
        intervals=(0, 3, 6, 9, 10),  # Dim7 to dominant
        rhythm=(0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["diminished", "passing", "chromatic"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["dim7", "passing_dim"],
        phrase_type="passing",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_coltrane_substitution",
        intervals=(0, 4, 8, 11),  # Major thirds cycle (Coltrane changes)
        rhythm=(1.0, 1.0, 1.0, 1.0),
        characteristics=["coltrane_changes", "major_thirds", "advanced"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["maj7", "coltrane_changes"],
        phrase_type="substitution",
        source="John Coltrane"
    ),

    LickPattern(
        name="bebop_half_diminished_line",
        intervals=(0, 3, 5, 8, 10),  # m7b5 arpeggio
        rhythm=(0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["half_diminished", "arpeggio", "ii_chord_minor"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["m7b5", "iiø7"],
        phrase_type="approach",
        source="Minor ii-V-i vocabulary"
    ),

    LickPattern(
        name="bebop_dorian_scale_run",
        intervals=(0, 2, 3, 5, 7, 9, 10, 12),  # Dorian mode
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["scalar", "dorian", "modal"],
        style="bebop",
        difficulty="beginner",
        harmonic_context=["min7", "ii7", "modal"],
        phrase_type="approach",
        source="Modal jazz"
    ),

    LickPattern(
        name="bebop_mixolydian_run",
        intervals=(0, 2, 4, 5, 7, 9, 10, 12),  # Mixolydian mode
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["scalar", "mixolydian", "dominant"],
        style="bebop",
        difficulty="beginner",
        harmonic_context=["dom7", "V7", "mixolydian"],
        phrase_type="approach",
        source="Modal jazz"
    ),

    LickPattern(
        name="bebop_blue_note_bend",
        intervals=(3, 4, 3),  # b3 to 3 and back (blue note)
        rhythm=(0.5, 0.25, 0.25),
        characteristics=["blues", "blue_note", "bend"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["dom7", "blues", "min7"],
        phrase_type="decoration",
        source="Blues influence"
    ),

    LickPattern(
        name="bebop_parker_blues_head",
        intervals=(0, 3, 5, 6, 7, 10, 12),  # Parker blues lick
        rhythm=(0.5, 0.25, 0.25, 0.5, 0.5, 0.5, 1.0),
        characteristics=["blues", "chromatic", "signature"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["blues", "I7"],
        phrase_type="head",
        source="Charlie Parker - Blues for Alice"
    ),

    LickPattern(
        name="bebop_descending_arpeggios",
        intervals=(24, 19, 16, 12, 11, 7, 4, 0),  # Descending from high octave
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["descending", "arpeggio", "wide_range"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["maj7", "dom7"],
        phrase_type="resolution",
        source="Bud Powell"
    ),

    LickPattern(
        name="bebop_ii_V_resolution_classic",
        intervals=(0, 2, 4, 5, 7, 6, 4, 2, 0),  # ii-V-I line
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 2.0),
        characteristics=["ii_V_I", "resolution", "classic"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["ii_V_I"],
        phrase_type="resolution",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_chromatic_approach_maj7",
        intervals=(-1, 0, 1, 0, 4, 7, 11),  # Chromatic enclosure to maj7
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 1.0),
        characteristics=["chromatic", "enclosure", "maj7"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["maj7", "Imaj7"],
        phrase_type="approach",
        source="Bebop vocabulary"
    ),

    LickPattern(
        name="bebop_guide_tone_line",
        intervals=(4, 3, 2, 0),  # 3-7-3-root guide tones
        rhythm=(1.0, 1.0, 1.0, 1.0),
        characteristics=["guide_tones", "voice_leading", "sparse"],
        style="bebop",
        difficulty="advanced",
        harmonic_context=["ii_V_I"],
        phrase_type="voice_leading",
        source="Modern bebop"
    ),

    LickPattern(
        name="bebop_anticipation_rhythm",
        intervals=(0, 4, 7, 12),  # Rhythmic displacement
        rhythm=(0.75, 0.25, 0.5, 1.5),
        characteristics=["rhythmic", "anticipation", "syncopation"],
        style="bebop",
        difficulty="intermediate",
        harmonic_context=["maj7", "dom7"],
        phrase_type="rhythmic",
        source="Bebop phrasing"
    ),
]


# ============================================================================
# GOSPEL PATTERNS (25 patterns)
# ============================================================================
# Based on Kirk Franklin, James Cleveland, Richard Smallwood, Hezekiah Walker
# Gospel characteristics: Major blues scale, slip notes, chromatic passing

GOSPEL_PATTERNS = [
    # Gospel chromatic approaches (8 patterns)
    LickPattern(
        name="gospel_chromatic_walkup",
        intervals=(0, 1, 2, 3, 4),  # Chromatic ascent to 3rd
        rhythm=(0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["chromatic", "ascending", "approach_tone"],
        style="gospel",
        difficulty="beginner",
        harmonic_context=["maj", "dom7", "I"],
        phrase_type="approach",
        source="Gospel vocabulary",
        tempo_range=(60, 140)
    ),

    LickPattern(
        name="gospel_slip_note_classic",
        intervals=(4, 3, 4),  # 3 to b3 to 3 (slip note)
        rhythm=(0.25, 0.5, 0.25),
        characteristics=["slip_note", "blues", "ornament"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj", "I", "IV"],
        phrase_type="decoration",
        source="Kirk Franklin style"
    ),

    LickPattern(
        name="gospel_double_chromatic",
        intervals=(0, 1, 2, 1, 2, 3, 4),  # Double chromatic approach
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 1.0),
        characteristics=["chromatic", "intricate", "ascending"],
        style="gospel",
        difficulty="advanced",
        harmonic_context=["maj", "dom7"],
        phrase_type="approach",
        source="Kirk Franklin"
    ),

    LickPattern(
        name="gospel_punch_chord_prep",
        intervals=(0, 2, 4, 7, 12),  # Ascending to punch chord
        rhythm=(0.5, 0.5, 0.5, 0.5, 2.0),
        characteristics=["ascending", "preparation", "punch_chord"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj", "I", "IV"],
        phrase_type="approach",
        source="Gospel piano"
    ),

    LickPattern(
        name="gospel_9th_emphasis",
        intervals=(14, 12, 9, 7, 4, 2, 0),  # Descending from 9th
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["descending", "9th_chord", "rich"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj9", "add9", "I"],
        phrase_type="resolution",
        source="Richard Smallwood"
    ),

    LickPattern(
        name="gospel_backdoor_approach",
        intervals=(10, 9, 7, 5, 4, 0),  # bVII7 to I
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 2.0),
        characteristics=["backdoor", "chromatic", "resolution"],
        style="gospel",
        difficulty="advanced",
        harmonic_context=["bVII7", "backdoor"],
        phrase_type="resolution",
        source="Gospel harmony"
    ),

    LickPattern(
        name="gospel_major_blues_run",
        intervals=(0, 2, 3, 4, 7, 9),  # Major blues scale
        rhythm=(0.5, 0.5, 0.25, 0.25, 0.5, 1.0),
        characteristics=["blues", "major_blues", "scalar"],
        style="gospel",
        difficulty="beginner",
        harmonic_context=["maj", "I", "blues"],
        phrase_type="approach",
        source="Gospel blues"
    ),

    LickPattern(
        name="gospel_tritone_resolution",
        intervals=(6, 7, 4, 0),  # Tritone to root
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["tritone", "resolution", "tension"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["dom7", "V7"],
        phrase_type="resolution",
        source="Gospel vocabulary"
    ),

    # Gospel rhythmic patterns (8 patterns)
    LickPattern(
        name="gospel_syncopated_rhythm",
        intervals=(0, 4, 7, 12),  # Syncopated major triad
        rhythm=(0.75, 0.25, 0.5, 1.5),
        characteristics=["syncopation", "rhythmic", "triad"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj", "I"],
        phrase_type="rhythmic",
        source="Gospel rhythm"
    ),

    LickPattern(
        name="gospel_delayed_resolution",
        intervals=(2, 4, 2, 0),  # Suspended then resolved
        rhythm=(1.0, 0.5, 0.5, 2.0),
        characteristics=["suspension", "delayed", "resolution"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["sus4", "sus2"],
        phrase_type="resolution",
        source="Gospel phrasing"
    ),

    LickPattern(
        name="gospel_triplet_fill",
        intervals=(0, 2, 4, 5, 4, 2, 0),  # Triplet scalar fill
        rhythm=(0.33, 0.33, 0.34, 0.33, 0.33, 0.34, 1.0),
        characteristics=["triplet", "scalar", "fill"],
        style="gospel",
        difficulty="beginner",
        harmonic_context=["maj", "dom7"],
        phrase_type="fill",
        source="Gospel organ style"
    ),

    LickPattern(
        name="gospel_rhythmic_anticipation",
        intervals=(0, 7, 12),  # Anticipated root-5-octave
        rhythm=(0.5, 0.75, 0.75),
        characteristics=["anticipation", "rhythmic", "strong"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj", "I"],
        phrase_type="rhythmic",
        source="Gospel piano"
    ),

    LickPattern(
        name="gospel_call_response_pattern",
        intervals=(0, 4, 7, 0, 4, 7),  # Call and response
        rhythm=(0.5, 0.5, 1.0, 0.5, 0.5, 1.0),
        characteristics=["call_response", "repetition", "gospel"],
        style="gospel",
        difficulty="beginner",
        harmonic_context=["maj", "I"],
        phrase_type="call_response",
        source="Gospel tradition"
    ),

    LickPattern(
        name="gospel_shout_rhythm",
        intervals=(0, 0, 0, 0),  # Repeated notes (shout rhythm)
        rhythm=(0.5, 0.5, 0.5, 0.5),
        characteristics=["repetition", "shout", "percussive"],
        style="gospel",
        difficulty="beginner",
        harmonic_context=["maj", "min", "dom7"],
        phrase_type="rhythmic",
        source="Gospel shout"
    ),

    LickPattern(
        name="gospel_hemiola_pattern",
        intervals=(0, 4, 7, 0, 4, 7),  # 3 against 2 feel
        rhythm=(0.67, 0.67, 0.66, 0.67, 0.67, 0.66),
        characteristics=["hemiola", "polyrhythm", "advanced"],
        style="gospel",
        difficulty="advanced",
        harmonic_context=["maj", "I"],
        phrase_type="rhythmic",
        source="Modern gospel"
    ),

    LickPattern(
        name="gospel_grace_note_fill",
        intervals=(0, 1, 2, 4),  # Grace notes to chord tone
        rhythm=(0.125, 0.125, 0.25, 1.5),
        characteristics=["grace_notes", "ornament", "quick"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj", "min"],
        phrase_type="decoration",
        source="Gospel organ"
    ),

    # Gospel harmonic patterns (9 patterns)
    LickPattern(
        name="gospel_parallel_4ths",
        intervals=(0, 5, 10),  # Quartal harmony
        rhythm=(0.5, 0.5, 1.0),
        characteristics=["quartal", "parallel", "modern"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["sus4", "modal"],
        phrase_type="harmony",
        source="Modern gospel"
    ),

    LickPattern(
        name="gospel_secondary_dominant",
        intervals=(0, 4, 7, 10, 14),  # V/V approach
        rhythm=(0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["secondary_dominant", "chromatic", "tonicization"],
        style="gospel",
        difficulty="advanced",
        harmonic_context=["V/V", "secondary_dom"],
        phrase_type="approach",
        source="Gospel harmony"
    ),

    LickPattern(
        name="gospel_parallel_6ths",
        intervals=(0, 4, 9, 14),  # Parallel major 6ths
        rhythm=(0.5, 0.5, 0.5, 1.0),
        characteristics=["parallel", "6ths", "sweet"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj6", "add6"],
        phrase_type="harmony",
        source="Gospel piano"
    ),

    LickPattern(
        name="gospel_add2_voicing",
        intervals=(0, 2, 4, 7),  # Add2 chord
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["add2", "sus2", "open"],
        style="gospel",
        difficulty="beginner",
        harmonic_context=["add2", "sus2"],
        phrase_type="harmony",
        source="Gospel voicing"
    ),

    LickPattern(
        name="gospel_cluster_resolution",
        intervals=(0, 1, 2, 4),  # Cluster to triad
        rhythm=(0.25, 0.25, 0.5, 2.0),
        characteristics=["cluster", "tension", "resolution"],
        style="gospel",
        difficulty="advanced",
        harmonic_context=["maj", "cluster"],
        phrase_type="tension",
        source="Modern gospel"
    ),

    LickPattern(
        name="gospel_modal_interchange",
        intervals=(0, 3, 7, 10),  # Borrowed minor chord
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["modal_interchange", "minor", "borrowed"],
        style="gospel",
        difficulty="advanced",
        harmonic_context=["min", "borrowed"],
        phrase_type="harmony",
        source="Gospel harmony"
    ),

    LickPattern(
        name="gospel_plagal_amen",
        intervals=(5, 0),  # IV to I (Amen cadence)
        rhythm=(2.0, 2.0),
        characteristics=["plagal", "amen", "cadence"],
        style="gospel",
        difficulty="beginner",
        harmonic_context=["IV", "I"],
        phrase_type="cadence",
        source="Gospel tradition"
    ),

    LickPattern(
        name="gospel_chromatic_mediant",
        intervals=(0, 4, 8),  # Chromatic mediant relationship
        rhythm=(1.0, 1.0, 2.0),
        characteristics=["chromatic_mediant", "colorful", "advanced"],
        style="gospel",
        difficulty="advanced",
        harmonic_context=["maj", "chromatic"],
        phrase_type="harmony",
        source="Modern gospel"
    ),

    LickPattern(
        name="gospel_ascending_progression",
        intervals=(0, 2, 4, 7, 9, 12),  # Ascending stepwise
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 1.5),
        characteristics=["ascending", "stepwise", "building"],
        style="gospel",
        difficulty="intermediate",
        harmonic_context=["maj", "progression"],
        phrase_type="approach",
        source="Gospel progression"
    ),
]


# ============================================================================
# BLUES PATTERNS (20 patterns)
# ============================================================================
# Based on B.B. King, Ray Charles, Oscar Peterson, Blues Brothers
# Blues characteristics: Blue notes (b3, b5, b7), bends, call-response

BLUES_PATTERNS = [
    # Classic blues licks (10 patterns)
    LickPattern(
        name="blues_minor_pentatonic_classic",
        intervals=(0, 3, 5, 7, 10, 12),  # Minor pentatonic
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["pentatonic", "minor", "classic"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["min", "blues", "I7"],
        phrase_type="approach",
        source="Blues vocabulary",
        tempo_range=(60, 160)
    ),

    LickPattern(
        name="blues_bb_king_box",
        intervals=(0, 3, 5, 6, 5, 3, 0),  # B.B. King style
        rhythm=(0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 1.0),
        characteristics=["blues", "bb_king", "signature", "blue_note"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7"],
        phrase_type="signature",
        source="B.B. King"
    ),

    LickPattern(
        name="blues_turnaround_classic",
        intervals=(0, 3, 5, 6, 7, 6, 5, 3, 0),  # Classic turnaround
        rhythm=(0.5, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 1.0),
        characteristics=["turnaround", "chromatic", "ending"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["I7", "turnaround"],
        phrase_type="turnaround",
        source="Blues vocabulary"
    ),

    LickPattern(
        name="blues_b5_bend",
        intervals=(6, 7, 6),  # b5 to 5 bend (blue note)
        rhythm=(0.5, 0.25, 0.25),
        characteristics=["blue_note", "bend", "b5"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7", "IV7"],
        phrase_type="decoration",
        source="Blues guitar adapted"
    ),

    LickPattern(
        name="blues_call_phrase",
        intervals=(0, 3, 5, 7),  # Call phrase
        rhythm=(1.0, 1.0, 1.0, 1.0),
        characteristics=["call", "sparse", "expressive"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["blues", "I7"],
        phrase_type="call",
        source="Blues tradition"
    ),

    LickPattern(
        name="blues_response_phrase",
        intervals=(12, 10, 7, 5, 3, 0),  # Response phrase
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 2.0),
        characteristics=["response", "descending", "resolution"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["blues", "I7"],
        phrase_type="response",
        source="Blues tradition"
    ),

    LickPattern(
        name="blues_walking_bass",
        intervals=(0, 2, 4, 5, 7, 9, 11, 12),  # Walking bass line
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["walking_bass", "scalar", "steady"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["blues", "I7", "boogie"],
        phrase_type="bass_line",
        source="Boogie-woogie"
    ),

    LickPattern(
        name="blues_double_stop",
        intervals=(0, 7, 0, 7),  # Root-5th double stops
        rhythm=(0.5, 0.5, 0.5, 0.5),
        characteristics=["double_stop", "5ths", "power"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["blues", "I7", "V7"],
        phrase_type="rhythmic",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_shuffle_rhythm",
        intervals=(0, 4, 7, 4, 0, 4, 7, 4),  # Shuffle pattern
        rhythm=(0.67, 0.33, 0.67, 0.33, 0.67, 0.33, 0.67, 0.33),
        characteristics=["shuffle", "swing", "rhythmic"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7"],
        phrase_type="rhythmic",
        source="Blues shuffle"
    ),

    LickPattern(
        name="blues_chromatic_descent",
        intervals=(12, 11, 10, 9, 8, 7),  # Chromatic from octave
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["chromatic", "descending", "dramatic"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7", "V7"],
        phrase_type="approach",
        source="Blues vocabulary"
    ),

    # Blues piano specific (10 patterns)
    LickPattern(
        name="blues_boogie_woogie_bass",
        intervals=(0, 7, 10, 7, 12, 10, 7, 5),  # Classic boogie pattern
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["boogie_woogie", "bass", "rolling"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["I7", "boogie"],
        phrase_type="bass_line",
        source="Boogie-woogie piano"
    ),

    LickPattern(
        name="blues_triplet_feel",
        intervals=(0, 3, 5, 0, 3, 5),  # Triplet blues
        rhythm=(0.33, 0.33, 0.34, 0.33, 0.33, 0.34),
        characteristics=["triplet", "pentatonic", "shuffle"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["blues", "I7"],
        phrase_type="rhythmic",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_left_hand_comp",
        intervals=(0, 10, 0, 10),  # Left hand comp (root-b7)
        rhythm=(0.5, 0.5, 0.5, 0.5),
        characteristics=["comping", "left_hand", "steady"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["7", "blues"],
        phrase_type="comping",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_grace_note_run",
        intervals=(2, 3, 5, 7),  # Grace note approach
        rhythm=(0.125, 0.375, 0.5, 1.0),
        characteristics=["grace_note", "quick", "ornament"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7"],
        phrase_type="decoration",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_octave_run",
        intervals=(0, 12, 0, 12, 0),  # Octave displacement
        rhythm=(0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["octaves", "alternating", "dramatic"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7"],
        phrase_type="rhythmic",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_tremolo_effect",
        intervals=(0, 3, 0, 3, 0, 3),  # Rapid alternation
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.25, 0.25),
        characteristics=["tremolo", "rapid", "effect"],
        style="blues",
        difficulty="advanced",
        harmonic_context=["blues", "I7"],
        phrase_type="effect",
        source="Blues organ"
    ),

    LickPattern(
        name="blues_crushed_note",
        intervals=(2, 3),  # Crushed approach (grace to chord tone)
        rhythm=(0.125, 0.875),
        characteristics=["crushed_note", "grace", "quick"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7", "IV7"],
        phrase_type="decoration",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_glissando_effect",
        intervals=(0, 1, 2, 3, 4, 5, 6, 7),  # Gliss up
        rhythm=(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125),
        characteristics=["glissando", "chromatic", "showy"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["blues", "I7"],
        phrase_type="effect",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_roll_ending",
        intervals=(12, 10, 7, 5, 3, 0),  # Descending roll
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.5, 1.5),
        characteristics=["roll", "descending", "ending"],
        style="blues",
        difficulty="intermediate",
        harmonic_context=["blues", "I7"],
        phrase_type="ending",
        source="Blues piano"
    ),

    LickPattern(
        name="blues_major_pentatonic",
        intervals=(0, 2, 4, 7, 9, 12),  # Major pentatonic (country blues)
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["pentatonic", "major", "country"],
        style="blues",
        difficulty="beginner",
        harmonic_context=["maj", "I"],
        phrase_type="approach",
        source="Country blues"
    ),
]


# ============================================================================
# NEO-SOUL PATTERNS (20 patterns)
# ============================================================================
# Based on Robert Glasper, D'Angelo, Erykah Badu, Hiatus Kaiyote
# Neo-soul characteristics: Complex harmony, syncopation, chromaticism

NEO_SOUL_PATTERNS = [
    # Neo-soul harmonic patterns (10 patterns)
    LickPattern(
        name="neosoul_9th_voicing",
        intervals=(0, 2, 4, 7, 14),  # Add9 emphasis
        rhythm=(0.5, 0.5, 0.5, 0.5, 2.0),
        characteristics=["9th", "rich", "lush"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["maj9", "add9", "9"],
        phrase_type="harmony",
        source="Robert Glasper",
        tempo_range=(70, 110)
    ),

    LickPattern(
        name="neosoul_sus_resolution",
        intervals=(5, 7, 4, 0),  # Sus4 to major resolution
        rhythm=(0.5, 0.5, 0.5, 2.0),
        characteristics=["sus4", "resolution", "delayed"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["sus4", "maj"],
        phrase_type="resolution",
        source="D'Angelo"
    ),

    LickPattern(
        name="neosoul_chromatic_voice_leading",
        intervals=(4, 3, 2, 0),  # Chromatic descent 3-2-root
        rhythm=(1.0, 1.0, 1.0, 1.0),
        characteristics=["chromatic", "voice_leading", "smooth"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["progression"],
        phrase_type="voice_leading",
        source="Robert Glasper"
    ),

    LickPattern(
        name="neosoul_cluster_chord",
        intervals=(0, 1, 2, 5, 7),  # Modern cluster
        rhythm=(0.25, 0.25, 0.25, 0.25, 2.0),
        characteristics=["cluster", "dissonance", "modern"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["cluster", "modern"],
        phrase_type="harmony",
        source="Modern neo-soul"
    ),

    LickPattern(
        name="neosoul_upper_extension",
        intervals=(14, 16, 18, 21),  # 9-#11-13-b7 (upper structure)
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["upper_structure", "extensions", "colorful"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["13", "9#11", "altered"],
        phrase_type="harmony",
        source="Robert Glasper"
    ),

    LickPattern(
        name="neosoul_negative_harmony",
        intervals=(0, -2, -4, -7),  # Negative harmony reflection
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["negative_harmony", "mirror", "advanced"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["chromatic", "reharmonization"],
        phrase_type="harmony",
        source="Jacob Collier influence"
    ),

    LickPattern(
        name="neosoul_quartal_stack",
        intervals=(0, 5, 10, 15),  # Stacked fourths
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["quartal", "stacked", "open"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["sus4", "modal"],
        phrase_type="harmony",
        source="McCoy Tyner / Glasper"
    ),

    LickPattern(
        name="neosoul_chromatic_mediant",
        intervals=(0, 4, 8, 12),  # Major thirds (chromatic mediant)
        rhythm=(1.0, 1.0, 1.0, 1.0),
        characteristics=["chromatic_mediant", "major_thirds", "colorful"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["chromatic", "mediant"],
        phrase_type="harmony",
        source="Modern harmony"
    ),

    LickPattern(
        name="neosoul_added_6th",
        intervals=(0, 4, 7, 9),  # Major 6th chord
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["6th", "sweet", "jazzy"],
        style="neo_soul",
        difficulty="beginner",
        harmonic_context=["maj6", "6"],
        phrase_type="harmony",
        source="Neo-soul vocabulary"
    ),

    LickPattern(
        name="neosoul_modal_mixture",
        intervals=(0, 3, 7, 10, 14),  # Minor 9th borrowed
        rhythm=(0.5, 0.5, 0.5, 0.5, 2.0),
        characteristics=["modal_mixture", "borrowed", "dark"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["min9", "borrowed"],
        phrase_type="harmony",
        source="Modal interchange"
    ),

    # Neo-soul rhythmic patterns (10 patterns)
    LickPattern(
        name="neosoul_syncopated_comp",
        intervals=(0, 4, 7),  # Off-beat triad
        rhythm=(0.75, 0.25, 2.0),
        characteristics=["syncopation", "comp", "rhythmic"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["maj", "triad"],
        phrase_type="comping",
        source="D'Angelo style"
    ),

    LickPattern(
        name="neosoul_delayed_attack",
        intervals=(0, 2, 4, 7),  # Delayed entry
        rhythm=(1.5, 0.5, 0.5, 1.5),
        characteristics=["delayed", "laid_back", "groove"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["maj", "add2"],
        phrase_type="rhythmic",
        source="Neo-soul groove"
    ),

    LickPattern(
        name="neosoul_triplet_over_duple",
        intervals=(0, 2, 4, 7, 9, 12),  # Polyrhythm
        rhythm=(0.67, 0.67, 0.66, 0.67, 0.67, 0.66),
        characteristics=["polyrhythm", "triplet", "complex"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["maj", "progression"],
        phrase_type="rhythmic",
        source="Hiatus Kaiyote"
    ),

    LickPattern(
        name="neosoul_anticipation_pattern",
        intervals=(0, 4, 7, 12),  # Anticipated changes
        rhythm=(0.75, 0.25, 0.5, 2.5),
        characteristics=["anticipation", "groove", "syncopation"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["maj"],
        phrase_type="rhythmic",
        source="Neo-soul rhythm"
    ),

    LickPattern(
        name="neosoul_sparse_rhythm",
        intervals=(0, 7, 14),  # Minimal notes, maximal space
        rhythm=(2.0, 1.0, 1.0),
        characteristics=["sparse", "space", "minimal"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["maj", "min"],
        phrase_type="rhythmic",
        source="Robert Glasper"
    ),

    LickPattern(
        name="neosoul_ghost_note_pattern",
        intervals=(0, 0, 4, 0, 7),  # Repeated root with ghost notes
        rhythm=(0.5, 0.25, 0.25, 0.5, 1.5),
        characteristics=["ghost_notes", "subtle", "groove"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["maj", "min"],
        phrase_type="rhythmic",
        source="Neo-soul piano"
    ),

    LickPattern(
        name="neosoul_rubato_phrase",
        intervals=(0, 2, 4, 7),  # Loose timing
        rhythm=(1.2, 0.8, 0.7, 1.3),
        characteristics=["rubato", "loose", "expressive"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["maj"],
        phrase_type="expressive",
        source="Erykah Badu style"
    ),

    LickPattern(
        name="neosoul_sixteenth_groove",
        intervals=(0, 4, 7, 4, 0, 4, 7, 4),  # Sixteenth note groove
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25),
        characteristics=["sixteenth", "groove", "driving"],
        style="neo_soul",
        difficulty="intermediate",
        harmonic_context=["maj", "min"],
        phrase_type="rhythmic",
        source="Neo-soul groove"
    ),

    LickPattern(
        name="neosoul_grace_note_cluster",
        intervals=(0, 1, 2, 4),  # Clustered grace notes
        rhythm=(0.1, 0.1, 0.1, 1.7),
        characteristics=["grace_notes", "cluster", "quick"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["maj", "cluster"],
        phrase_type="decoration",
        source="Modern neo-soul"
    ),

    LickPattern(
        name="neosoul_metric_modulation",
        intervals=(0, 4, 7, 12),  # Metric shift feel
        rhythm=(0.5, 0.5, 1.0, 2.0),
        characteristics=["metric_modulation", "tempo_shift", "advanced"],
        style="neo_soul",
        difficulty="advanced",
        harmonic_context=["maj"],
        phrase_type="rhythmic",
        source="Complex neo-soul"
    ),
]


# ============================================================================
# MODERN JAZZ PATTERNS (15 patterns)
# ============================================================================
# Based on Brad Mehldau, Chick Corea, Herbie Hancock, Keith Jarrett
# Modern jazz: Modal harmony, complex rhythms, reharmonization

MODERN_JAZZ_PATTERNS = [
    LickPattern(
        name="modernjazz_dorian_modal",
        intervals=(0, 2, 3, 5, 7, 9, 10, 12),  # Pure Dorian
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["modal", "dorian", "scalar"],
        style="modern_jazz",
        difficulty="intermediate",
        harmonic_context=["min7", "dorian", "modal"],
        phrase_type="modal",
        source="Miles Davis - Kind of Blue",
        tempo_range=(60, 180)
    ),

    LickPattern(
        name="modernjazz_lydian_bright",
        intervals=(0, 2, 4, 6, 7, 9, 11, 12),  # Lydian mode
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["modal", "lydian", "#4", "bright"],
        style="modern_jazz",
        difficulty="intermediate",
        harmonic_context=["maj7", "lydian", "modal"],
        phrase_type="modal",
        source="Modal jazz"
    ),

    LickPattern(
        name="modernjazz_phrygian_dark",
        intervals=(0, 1, 3, 5, 7, 8, 10, 12),  # Phrygian mode
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["modal", "phrygian", "b2", "dark"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["min7", "phrygian", "modal"],
        phrase_type="modal",
        source="Modal jazz"
    ),

    LickPattern(
        name="modernjazz_superimposed_triad",
        intervals=(6, 10, 13),  # Triad from #11 (bII triad)
        rhythm=(0.5, 0.5, 1.0),
        characteristics=["superimposed", "upper_structure", "modern"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["dom7", "lydian_dom"],
        phrase_type="reharmonization",
        source="Brad Mehldau"
    ),

    LickPattern(
        name="modernjazz_pentatonic_over_changes",
        intervals=(0, 2, 5, 7, 10),  # Pentatonic displacement
        rhythm=(0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["pentatonic", "superimposed", "outside"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["any", "outside"],
        phrase_type="outside",
        source="Keith Jarrett"
    ),

    LickPattern(
        name="modernjazz_whole_tone_scale",
        intervals=(0, 2, 4, 6, 8, 10),  # Whole tone
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["whole_tone", "symmetrical", "floating"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["aug", "7#5", "altered"],
        phrase_type="color",
        source="Bill Evans"
    ),

    LickPattern(
        name="modernjazz_octatonic_scale",
        intervals=(0, 2, 3, 5, 6, 8, 9, 11),  # Half-whole diminished
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        characteristics=["octatonic", "diminished", "symmetrical"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["dim7", "7b9", "altered"],
        phrase_type="color",
        source="Modern jazz"
    ),

    LickPattern(
        name="modernjazz_chromatic_planing",
        intervals=(0, 4, 7, 1, 5, 8, 2, 6, 9),  # Parallel triads
        rhythm=(0.33, 0.33, 0.34, 0.33, 0.33, 0.34, 0.33, 0.33, 0.34),
        characteristics=["planing", "parallel", "chromatic"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["chromatic"],
        phrase_type="movement",
        source="Bill Evans"
    ),

    LickPattern(
        name="modernjazz_inner_voice_movement",
        intervals=(0, 4, 5, 7),  # Inner voice chromatic
        rhythm=(1.0, 0.5, 0.5, 2.0),
        characteristics=["inner_voice", "chromatic", "smooth"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["maj7", "voice_leading"],
        phrase_type="voice_leading",
        source="Bill Evans"
    ),

    LickPattern(
        name="modernjazz_rootless_voicing",
        intervals=(3, 6, 9, 13),  # Rootless A-type
        rhythm=(0.5, 0.5, 0.5, 1.5),
        characteristics=["rootless", "7-3", "modern"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["dom7", "min7"],
        phrase_type="voicing",
        source="Bill Evans"
    ),

    LickPattern(
        name="modernjazz_block_chord_melody",
        intervals=(0, 4, 7, 12),  # Locked hands style
        rhythm=(0.5, 0.5, 0.5, 0.5),
        characteristics=["block_chords", "melody", "locked_hands"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["maj"],
        phrase_type="melody",
        source="George Shearing"
    ),

    LickPattern(
        name="modernjazz_quartal_voicing_stack",
        intervals=(0, 5, 10, 15, 20),  # Stacked perfect fourths
        rhythm=(0.5, 0.5, 0.5, 0.5, 2.0),
        characteristics=["quartal", "stacked", "modern", "open"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["sus4", "modal"],
        phrase_type="voicing",
        source="McCoy Tyner"
    ),

    LickPattern(
        name="modernjazz_tritone_interval",
        intervals=(0, 6, 12),  # Tritone leap
        rhythm=(0.5, 0.5, 1.0),
        characteristics=["tritone", "interval", "dramatic"],
        style="modern_jazz",
        difficulty="intermediate",
        harmonic_context=["dom7", "altered"],
        phrase_type="interval",
        source="Thelonious Monk"
    ),

    LickPattern(
        name="modernjazz_polyrhythmic_phrase",
        intervals=(0, 2, 4, 7, 9, 12),  # 3 over 4
        rhythm=(0.75, 0.75, 0.75, 0.75, 0.75, 0.75),
        characteristics=["polyrhythm", "complex", "modern"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["any"],
        phrase_type="rhythmic",
        source="Modern jazz"
    ),

    LickPattern(
        name="modernjazz_side_slip",
        intervals=(0, 4, 7, 1, 5, 8, 0, 4, 7),  # Half-step side-slip
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["side_slip", "outside", "chromatic"],
        style="modern_jazz",
        difficulty="advanced",
        harmonic_context=["any", "outside"],
        phrase_type="outside",
        source="Modern jazz"
    ),
]


# ============================================================================
# CLASSICAL PATTERNS (10 patterns)
# ============================================================================
# Based on Bach, Mozart, Chopin, Debussy
# Classical: Ornaments, sequences, voice leading

CLASSICAL_PATTERNS = [
    LickPattern(
        name="classical_alberti_bass",
        intervals=(0, 7, 4, 7, 0, 7, 4, 7),  # Classic broken chord
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25),
        characteristics=["alberti_bass", "accompaniment", "broken_chord"],
        style="classical",
        difficulty="beginner",
        harmonic_context=["maj", "I"],
        phrase_type="accompaniment",
        source="Mozart",
        tempo_range=(60, 160)
    ),

    LickPattern(
        name="classical_mordent",
        intervals=(0, 2, 0),  # Upper mordent
        rhythm=(0.25, 0.25, 0.5),
        characteristics=["ornament", "mordent", "classical"],
        style="classical",
        difficulty="intermediate",
        harmonic_context=["maj", "min"],
        phrase_type="ornament",
        source="Baroque ornament"
    ),

    LickPattern(
        name="classical_turn",
        intervals=(0, 2, 0, -2, 0),  # Turn ornament
        rhythm=(0.2, 0.2, 0.2, 0.2, 0.2),
        characteristics=["ornament", "turn", "classical"],
        style="classical",
        difficulty="intermediate",
        harmonic_context=["maj", "min"],
        phrase_type="ornament",
        source="Classical period"
    ),

    LickPattern(
        name="classical_appoggiatura",
        intervals=(2, 0),  # Leaning note
        rhythm=(0.5, 0.5),
        characteristics=["ornament", "appoggiatura", "dissonance"],
        style="classical",
        difficulty="intermediate",
        harmonic_context=["maj", "min"],
        phrase_type="ornament",
        source="Classical ornament"
    ),

    LickPattern(
        name="classical_trill",
        intervals=(0, 2, 0, 2, 0, 2, 0),  # Whole-step trill
        rhythm=(0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5),
        characteristics=["ornament", "trill", "rapid"],
        style="classical",
        difficulty="intermediate",
        harmonic_context=["maj", "min"],
        phrase_type="ornament",
        source="Classical ornament"
    ),

    LickPattern(
        name="classical_scale_sequence",
        intervals=(0, 2, 4, 2, 4, 5, 4, 5, 7),  # Ascending sequence
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["sequence", "scalar", "ascending"],
        style="classical",
        difficulty="intermediate",
        harmonic_context=["maj"],
        phrase_type="sequence",
        source="Bach"
    ),

    LickPattern(
        name="classical_suspension",
        intervals=(5, 4),  # 4-3 suspension
        rhythm=(1.0, 1.0),
        characteristics=["suspension", "dissonance", "resolution"],
        style="classical",
        difficulty="intermediate",
        harmonic_context=["maj"],
        phrase_type="voice_leading",
        source="Classical harmony"
    ),

    LickPattern(
        name="classical_cadential_64",
        intervals=(7, 4, 0),  # I6/4 to V
        rhythm=(0.5, 0.5, 1.0),
        characteristics=["cadential", "6/4", "dominant_prep"],
        style="classical",
        difficulty="intermediate",
        harmonic_context=["V", "cadence"],
        phrase_type="cadence",
        source="Classical harmony"
    ),

    LickPattern(
        name="classical_chopin_rubato",
        intervals=(0, 4, 7, 11, 12),  # Romantic arpeggio
        rhythm=(0.8, 0.6, 0.7, 0.5, 1.4),
        characteristics=["rubato", "romantic", "expressive"],
        style="classical",
        difficulty="advanced",
        harmonic_context=["maj7"],
        phrase_type="romantic",
        source="Chopin"
    ),

    LickPattern(
        name="classical_debussy_whole_tone",
        intervals=(0, 2, 4, 6, 8, 10),  # Impressionist
        rhythm=(0.5, 0.5, 0.5, 0.5, 0.5, 1.0),
        characteristics=["whole_tone", "impressionist", "floating"],
        style="classical",
        difficulty="advanced",
        harmonic_context=["aug", "impressionist"],
        phrase_type="color",
        source="Debussy"
    ),
]


# ============================================================================
# DATABASE ACCESS
# ============================================================================

class LickDatabase:
    """Centralized access to all lick patterns"""

    def __init__(self):
        self.all_patterns: List[LickPattern] = (
            BEBOP_PATTERNS +
            GOSPEL_PATTERNS +
            BLUES_PATTERNS +
            NEO_SOUL_PATTERNS +
            MODERN_JAZZ_PATTERNS +
            CLASSICAL_PATTERNS
        )

        # Build indexes for fast lookup
        self._build_indexes()

    def _build_indexes(self):
        """Build indexes for efficient searching"""
        self.by_style: Dict[str, List[LickPattern]] = {}
        self.by_difficulty: Dict[str, List[LickPattern]] = {}
        self.by_harmonic_context: Dict[str, List[LickPattern]] = {}
        self.by_phrase_type: Dict[str, List[LickPattern]] = {}
        self.by_name: Dict[str, LickPattern] = {}

        for pattern in self.all_patterns:
            # Index by style
            if pattern.style not in self.by_style:
                self.by_style[pattern.style] = []
            self.by_style[pattern.style].append(pattern)

            # Index by difficulty
            if pattern.difficulty not in self.by_difficulty:
                self.by_difficulty[pattern.difficulty] = []
            self.by_difficulty[pattern.difficulty].append(pattern)

            # Index by harmonic context
            for context in pattern.harmonic_context:
                if context not in self.by_harmonic_context:
                    self.by_harmonic_context[context] = []
                self.by_harmonic_context[context].append(pattern)

            # Index by phrase type
            if pattern.phrase_type not in self.by_phrase_type:
                self.by_phrase_type[pattern.phrase_type] = []
            self.by_phrase_type[pattern.phrase_type].append(pattern)

            # Index by name
            self.by_name[pattern.name] = pattern

    def get_by_style(self, style: str) -> List[LickPattern]:
        """Get all patterns for a style"""
        return self.by_style.get(style, [])

    def get_by_difficulty(self, difficulty: str) -> List[LickPattern]:
        """Get all patterns for a difficulty level"""
        return self.by_difficulty.get(difficulty, [])

    def get_by_harmonic_context(self, context: str) -> List[LickPattern]:
        """Get patterns suitable for a harmonic context"""
        return self.by_harmonic_context.get(context, [])

    def get_by_phrase_type(self, phrase_type: str) -> List[LickPattern]:
        """Get patterns by phrase type"""
        return self.by_phrase_type.get(phrase_type, [])

    def get_by_name(self, name: str) -> Optional[LickPattern]:
        """Get specific pattern by name"""
        return self.by_name.get(name)

    def search(
        self,
        style: Optional[str] = None,
        difficulty: Optional[str] = None,
        harmonic_context: Optional[str] = None,
        phrase_type: Optional[str] = None,
        characteristics: Optional[List[str]] = None
    ) -> List[LickPattern]:
        """Search patterns by multiple criteria"""
        results = self.all_patterns.copy()

        if style:
            results = [p for p in results if p.style == style]

        if difficulty:
            results = [p for p in results if p.difficulty == difficulty]

        if harmonic_context:
            results = [p for p in results if harmonic_context in p.harmonic_context]

        if phrase_type:
            results = [p for p in results if p.phrase_type == phrase_type]

        if characteristics:
            results = [
                p for p in results
                if any(char in p.characteristics for char in characteristics)
            ]

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        return {
            'total_patterns': len(self.all_patterns),
            'bebop': len(BEBOP_PATTERNS),
            'gospel': len(GOSPEL_PATTERNS),
            'blues': len(BLUES_PATTERNS),
            'neo_soul': len(NEO_SOUL_PATTERNS),
            'modern_jazz': len(MODERN_JAZZ_PATTERNS),
            'classical': len(CLASSICAL_PATTERNS),
        }


# Global database instance
lick_database = LickDatabase()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == '__main__':
    db = lick_database

    print("=" * 70)
    print("LICK DATABASE STATISTICS")
    print("=" * 70)
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"{key:20} {value:5}")

    print("\n" + "=" * 70)
    print("SAMPLE QUERIES")
    print("=" * 70)

    # Example 1: Get all bebop patterns
    bebop = db.get_by_style("bebop")
    print(f"\n1. Bebop patterns: {len(bebop)}")
    for p in bebop[:3]:
        print(f"   - {p.name}: {p.characteristics[:3]}")

    # Example 2: Get intermediate gospel patterns
    gospel = db.search(style="gospel", difficulty="intermediate")
    print(f"\n2. Intermediate gospel patterns: {len(gospel)}")
    for p in gospel[:3]:
        print(f"   - {p.name}: {p.source}")

    # Example 3: Get patterns for dominant 7th chords
    dom7 = db.get_by_harmonic_context("dom7")
    print(f"\n3. Dominant 7th patterns: {len(dom7)}")
    for p in dom7[:3]:
        print(f"   - {p.name} ({p.style})")

    # Example 4: Get turnaround patterns
    turnarounds = db.get_by_phrase_type("turnaround")
    print(f"\n4. Turnaround patterns: {len(turnarounds)}")
    for p in turnarounds:
        print(f"   - {p.name} ({p.style})")

    # Example 5: Search by characteristics
    chromatic = db.search(characteristics=["chromatic", "ascending"])
    print(f"\n5. Chromatic ascending patterns: {len(chromatic)}")
    for p in chromatic[:5]:
        print(f"   - {p.name} ({p.style})")
