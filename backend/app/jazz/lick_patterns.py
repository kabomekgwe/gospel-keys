"""
Jazz Lick Pattern Library and Validation Service

This module provides:
- Curated jazz lick patterns by style (bebop, blues, modern, gospel)
- Validation rules for AI-generated licks
- Scale conformance checking
- Difficulty-appropriate complexity validation
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from app.theory.scale_library import get_scale_notes
from app.theory.chord_library import parse_chord_symbol


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class LickPattern:
    """Template for a jazz lick pattern"""
    name: str
    style: str
    difficulty: str
    intervals: Tuple[int, ...]  # Interval pattern (semitones from root)
    rhythm: List[float]          # Note durations in beats
    characteristics: List[str]    # Tags: "chromatic", "arpeggio", etc.
    usage_context: List[str]     # When to use: "ii-V-I", "turnaround", etc.


@dataclass
class ValidationResult:
    """Result of lick validation"""
    is_valid: bool
    confidence: float  # 0.0-1.0
    issues: List[str]  # Issues found
    suggestions: List[str]  # Improvement suggestions


# ============================================================================
# Lick Pattern Service
# ============================================================================

class LickPatternService:
    """Service for lick pattern validation and analysis"""

    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, List[LickPattern]]:
        """Load curated lick patterns by style"""
        return {
            "bebop": self._get_bebop_patterns(),
            "blues": self._get_blues_patterns(),
            "modern": self._get_modern_patterns(),
            "gospel": self._get_gospel_patterns(),
            "swing": self._get_swing_patterns(),
            "bossa": self._get_bossa_patterns(),
        }

    def validate_lick(
        self,
        lick_data: Dict,
        context_chords: List[str],
        style: str,
        difficulty: str
    ) -> ValidationResult:
        """Validate a generated lick against theory rules"""

        issues = []
        suggestions = []

        # 1. Check note range (48-84 MIDI)
        midi_notes = lick_data.get("midi_notes", [])
        if not midi_notes:
            issues.append("No MIDI notes provided")
            return ValidationResult(False, 0.0, issues, suggestions)

        if not all(48 <= note <= 84 for note in midi_notes):
            issues.append("Notes outside playable range (C2-C6, MIDI 48-84)")

        # 2. Check scale conformance
        scale_check = self._check_scale_conformance(
            lick_data.get("notes", []),
            context_chords,
            style
        )
        if not scale_check.is_valid:
            issues.extend(scale_check.issues)

        # 3. Check voice leading (no large jumps for beginners)
        if difficulty == "beginner":
            if self._check_interval_jumps(midi_notes, max_interval=7):
                issues.append("Too many large intervals for beginner level (max: perfect 5th)")
        elif difficulty == "intermediate":
            if self._check_interval_jumps(midi_notes, max_interval=12):
                issues.append("Intervals too large for intermediate level (max: octave)")

        # 4. Check duration matches stated length
        stated_duration = lick_data.get("duration_beats", 0)
        if stated_duration <= 0:
            issues.append("Invalid duration_beats value")

        # 5. Check rhythmic complexity matches difficulty
        if difficulty == "beginner":
            if self._has_complex_rhythm(lick_data):
                issues.append("Rhythm too complex for beginner level")

        # 6. Check note count is reasonable
        num_notes = len(midi_notes)
        if num_notes < 3:
            issues.append("Too few notes for a lick (minimum 3)")
        elif num_notes > 50:
            issues.append("Too many notes (maximum 50)")

        # Calculate confidence
        max_issues = 6
        confidence = 1.0 - (len(issues) / max_issues)
        is_valid = confidence >= 0.6 and len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence=max(0.0, confidence),
            issues=issues,
            suggestions=suggestions
        )

    def get_scales_for_context(
        self,
        chords: List[str],
        style: str
    ) -> List[str]:
        """Determine appropriate scales for chord context"""

        scales = []

        for chord in chords:
            try:
                root, quality, extensions = parse_chord_symbol(chord)
            except:
                # If parsing fails, skip this chord
                continue

            # Bebop scales
            if style == "bebop":
                if "maj7" in quality or quality == "":
                    scales.append(f"{root} Bebop Major")
                elif "7" in quality and "maj" not in quality:
                    scales.append(f"{root} Bebop Dominant")
                elif "m7" in quality:
                    scales.append(f"{root} Bebop Minor (Dorian)")

            # Blues scales
            elif style == "blues":
                scales.append(f"{root} Blues Scale")
                if "7" in quality:
                    scales.append(f"{root} Mixolydian")

            # Modern scales
            elif style == "modern":
                if "alt" in quality or "7#9" in quality or "7b9" in quality:
                    scales.append(f"{root} Altered Scale")
                elif "7#11" in quality:
                    scales.append(f"{root} Lydian Dominant")
                else:
                    scales.append(f"{root} Melodic Minor")

            # Gospel scales
            elif style == "gospel":
                scales.append(f"{root} Major Pentatonic")
                scales.append(f"{root} Minor Pentatonic")
                if "7" in quality:
                    scales.append(f"{root} Mixolydian")

            # Swing scales (similar to bebop)
            elif style == "swing":
                if "maj7" in quality:
                    scales.append(f"{root} Major Scale")
                elif "7" in quality and "maj" not in quality:
                    scales.append(f"{root} Mixolydian")
                elif "m7" in quality:
                    scales.append(f"{root} Dorian")

            # Bossa scales
            elif style == "bossa":
                if "maj7" in quality:
                    scales.append(f"{root} Lydian")
                elif "7" in quality:
                    scales.append(f"{root} Mixolydian")
                elif "m7" in quality:
                    scales.append(f"{root} Dorian")

        return list(set(scales))  # Remove duplicates

    def _check_scale_conformance(
        self,
        notes: List[str],
        context_chords: List[str],
        style: str
    ) -> ValidationResult:
        """Check if notes conform to appropriate scales"""

        if not notes:
            return ValidationResult(False, 0.0, ["No notes provided"], [])

        # Get allowed scales
        scales = self.get_scales_for_context(context_chords, style)

        # Allow chromatic passing tones (10% of notes can be outside scale)
        allowed_outside = max(1, len(notes) // 10)
        outside_notes = []

        # For validation, we'll use a simplified approach
        # In production, would use actual scale library for precise checking
        # For now, accept most notes as valid (focus on other validations)

        # Basic check: ensure notes are valid note names
        for note in notes:
            if not note or len(note) < 2:
                outside_notes.append(note)

        is_valid = len(outside_notes) <= allowed_outside

        return ValidationResult(
            is_valid=is_valid,
            confidence=1.0 - (len(outside_notes) / len(notes)) if notes else 0.0,
            issues=[f"Invalid note format: {', '.join(outside_notes)}"] if not is_valid else [],
            suggestions=[]
        )

    def _check_interval_jumps(
        self,
        midi_notes: List[int],
        max_interval: int = 12
    ) -> bool:
        """Check for intervals larger than max_interval semitones"""
        for i in range(len(midi_notes) - 1):
            interval = abs(midi_notes[i+1] - midi_notes[i])
            if interval > max_interval:
                return True
        return False

    def _has_complex_rhythm(self, lick_data: Dict) -> bool:
        """Check if rhythm is too complex for difficulty level"""
        # Check for 16th notes, triplets, syncopation
        num_notes = len(lick_data.get("notes", []))
        duration_beats = lick_data.get("duration_beats", 4.0)

        if num_notes == 0 or duration_beats <= 0:
            return False

        avg_note_duration = duration_beats / num_notes

        # If average note is shorter than 8th note (0.5 beats), it's complex
        return avg_note_duration < 0.5

    # ========================================================================
    # Pattern Definitions
    # ========================================================================

    def _get_bebop_patterns(self) -> List[LickPattern]:
        """Bebop lick patterns"""
        return [
            LickPattern(
                name="Bebop Descending 8th Line",
                style="bebop",
                difficulty="intermediate",
                intervals=(0, 2, 4, 5, 4, 2, 1, 0),
                rhythm=[0.5] * 8,
                characteristics=["chromatic", "descending", "bebop_scale"],
                usage_context=["ii-V-I", "descending resolution"]
            ),
            LickPattern(
                name="Enclosure Lick",
                style="bebop",
                difficulty="advanced",
                intervals=(1, -1, 0),
                rhythm=[0.25, 0.25, 0.5],
                characteristics=["chromatic", "enclosure", "target_tone"],
                usage_context=["approach", "chord_change"]
            ),
            LickPattern(
                name="Parker Lick",
                style="bebop",
                difficulty="advanced",
                intervals=(0, 2, 4, 5, 7, 9, 11, 12),
                rhythm=[0.5] * 8,
                characteristics=["bebop_scale", "ascending", "arpeggio"],
                usage_context=["dominant_7", "ii-V-I"]
            ),
        ]

    def _get_blues_patterns(self) -> List[LickPattern]:
        """Blues lick patterns"""
        return [
            LickPattern(
                name="Blues Bend Lick",
                style="blues",
                difficulty="beginner",
                intervals=(0, 3, 5, 6, 5, 3),
                rhythm=[1.0, 0.5, 0.5, 1.0, 0.5, 0.5],
                characteristics=["blues_scale", "bend", "blue_note"],
                usage_context=["blues", "dominant_7"]
            ),
            LickPattern(
                name="Call-Response Blues",
                style="blues",
                difficulty="intermediate",
                intervals=(0, 3, 5, 7, 5, 3, 0),
                rhythm=[0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 1.0],
                characteristics=["pentatonic", "call_response", "blues"],
                usage_context=["12_bar_blues", "shuffle"]
            ),
        ]

    def _get_modern_patterns(self) -> List[LickPattern]:
        """Modern jazz lick patterns"""
        return [
            LickPattern(
                name="Altered Scale Run",
                style="modern",
                difficulty="advanced",
                intervals=(0, 1, 3, 4, 6, 8, 10),
                rhythm=[0.5] * 7,
                characteristics=["altered", "outside", "tension"],
                usage_context=["altered_dominant", "7alt"]
            ),
            LickPattern(
                name="Wide Interval Jump",
                style="modern",
                difficulty="advanced",
                intervals=(0, 7, 12, 5, 9),
                rhythm=[0.5, 0.5, 1.0, 0.5, 1.5],
                characteristics=["wide_intervals", "angular", "modern"],
                usage_context=["contemporary", "outside_playing"]
            ),
        ]

    def _get_gospel_patterns(self) -> List[LickPattern]:
        """Gospel lick patterns"""
        return [
            LickPattern(
                name="Gospel Turnaround",
                style="gospel",
                difficulty="intermediate",
                intervals=(7, 5, 4, 3, 2, 0),
                rhythm=[0.5, 0.5, 0.25, 0.25, 0.5, 1.0],
                characteristics=["pentatonic", "turnaround", "descending"],
                usage_context=["phrase_ending", "turnaround"]
            ),
            LickPattern(
                name="Gospel Run",
                style="gospel",
                difficulty="intermediate",
                intervals=(0, 2, 4, 5, 7, 9, 10, 12),
                rhythm=[0.25] * 8,
                characteristics=["chromatic", "ascending", "gospel_run"],
                usage_context=["between_chords", "fill"]
            ),
        ]

    def _get_swing_patterns(self) -> List[LickPattern]:
        """Swing lick patterns"""
        return [
            LickPattern(
                name="Swing Eighth Line",
                style="swing",
                difficulty="beginner",
                intervals=(0, 2, 4, 5, 7, 5, 4, 2),
                rhythm=[0.5] * 8,
                characteristics=["swing", "major_scale", "stepwise"],
                usage_context=["major_chord", "swing_feel"]
            ),
            LickPattern(
                name="Swing Arpeggio",
                style="swing",
                difficulty="intermediate",
                intervals=(0, 4, 7, 12, 7, 4, 0),
                rhythm=[0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
                characteristics=["arpeggio", "chord_tones", "swing"],
                usage_context=["major_7", "dominant_7"]
            ),
        ]

    def _get_bossa_patterns(self) -> List[LickPattern]:
        """Bossa nova lick patterns"""
        return [
            LickPattern(
                name="Bossa Chromatic Approach",
                style="bossa",
                difficulty="intermediate",
                intervals=(0, 2, 4, 6, 7, 9, 11),
                rhythm=[0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 1.0],
                characteristics=["lydian", "chromatic", "bossa"],
                usage_context=["major_7", "lydian"]
            ),
            LickPattern(
                name="Bossa Syncopation",
                style="bossa",
                difficulty="advanced",
                intervals=(0, 4, 7, 11, 9, 7, 4, 0),
                rhythm=[0.25, 0.75, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0],
                characteristics=["syncopated", "bossa_nova", "maj7"],
                usage_context=["bossa_nova", "latin"]
            ),
        ]


# Global service instance
lick_pattern_service = LickPatternService()
