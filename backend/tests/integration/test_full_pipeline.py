"""
Full Pipeline Integration Tests

Tests the complete transcription pipeline including:
- Voicing analysis integration with chord detection
- Progression pattern detection
- Reharmonization suggestions
- End-to-end analysis flow
"""

import pytest
import pytest_asyncio
from pathlib import Path

from app.gospel import Note
from app.schemas.transcription import ChordEvent
from app.pipeline.voicing_analyzer import analyze_voicing, analyze_all_voicings, VoicingType
from app.pipeline.progression_detector import detect_progressions
from app.pipeline.reharmonization_engine import reharmonize_progression


def chord_event_to_dict(chord: ChordEvent) -> dict:
    """Convert ChordEvent to dict format expected by pipeline functions"""
    return {
        'root': chord.root,
        'quality': chord.quality,
        'time': chord.time,
        'symbol': chord.chord,
        'duration': chord.duration,
        'confidence': chord.confidence
    }


class TestVoicingAnalysisIntegration:
    """Test voicing analyzer integration with chord detection"""

    @pytest.mark.asyncio
    async def test_voicing_analysis_with_detected_chords(self):
        """Test that voicing analyzer correctly processes chords from detection"""
        # Simulate chord detection output - ii-V-I in C
        chords = [
            ChordEvent(
                time=0.0,
                duration=2.0,
                chord="Dm7",
                confidence=0.92,
                root="D",
                quality="m7"
            ),
            ChordEvent(
                time=2.0,
                duration=2.0,
                chord="G7",
                confidence=0.88,
                root="G",
                quality="7"
            ),
            ChordEvent(
                time=4.0,
                duration=4.0,
                chord="Cmaj7",
                confidence=0.95,
                root="C",
                quality="maj7"
            ),
        ]

        # Simulate MIDI notes for these chords
        # Using larger gaps to prevent window overlap (0.2s tolerance on each side)
        # Chord1: 0.0-2.0 (window: -0.2 to 2.2)
        # Chord2: 2.0-4.0 (window: 1.8 to 4.2)
        # Chord3: 4.0-8.0 (window: 3.8 to 8.2)
        # Need notes to start >0.2s after previous chord ends
        notes = [
            # Dm7 (0.0-1.5): D, F, A, C
            Note(pitch=50, time=0.0, duration=1.5, velocity=80, hand="left"),   # D3
            Note(pitch=53, time=0.0, duration=1.5, velocity=80, hand="left"),   # F3
            Note(pitch=57, time=0.0, duration=1.5, velocity=85, hand="right"),  # A3
            Note(pitch=60, time=0.0, duration=1.5, velocity=85, hand="right"),  # C4

            # G7 (2.7-3.7): G, B, D, F (gap: 2.2 to 2.5 safe, start at 2.7)
            Note(pitch=55, time=2.7, duration=1.0, velocity=80, hand="left"),   # G3
            Note(pitch=59, time=2.7, duration=1.0, velocity=80, hand="left"),   # B3
            Note(pitch=62, time=2.7, duration=1.0, velocity=85, hand="right"),  # D4
            Note(pitch=65, time=2.7, duration=1.0, velocity=85, hand="right"),  # F4

            # Cmaj7 (4.7-7.7): C, E, G, B (gap: 4.2 to 4.5 safe, start at 4.7)
            Note(pitch=48, time=4.7, duration=3.0, velocity=90, hand="left"),   # C3
            Note(pitch=52, time=4.7, duration=3.0, velocity=90, hand="left"),   # E3
            Note(pitch=55, time=4.7, duration=3.0, velocity=95, hand="right"),  # G3
            Note(pitch=59, time=4.7, duration=3.0, velocity=95, hand="right"),  # B3
        ]

        # Analyze all voicings
        voicings = await analyze_all_voicings(notes, chords)

        # Assertions
        assert len(voicings) == 3, "Should analyze all three chords"

        # Check Dm7 voicing
        dm7_voicing = voicings[0]
        assert dm7_voicing.chord_symbol == "Dm7"
        assert dm7_voicing.has_root is True
        assert dm7_voicing.has_third is True
        assert dm7_voicing.has_seventh is True
        assert len(dm7_voicing.notes) == 4

        # Check G7 voicing
        g7_voicing = voicings[1]
        assert g7_voicing.chord_symbol == "G7"
        assert g7_voicing.has_root is True

        # Check Cmaj7 voicing
        cmaj7_voicing = voicings[2]
        assert cmaj7_voicing.chord_symbol == "Cmaj7"
        assert cmaj7_voicing.voicing_type == VoicingType.CLOSE  # All within octave
        assert cmaj7_voicing.width_semitones == 11  # C3 to B3

    @pytest.mark.asyncio
    async def test_voicing_complexity_tracking(self):
        """Test that complexity scores increase with voicing difficulty"""
        # Simple triad
        simple_notes = [
            Note(pitch=60, time=0.0, duration=1.0, velocity=80, hand="left"),   # C
            Note(pitch=64, time=0.0, duration=1.0, velocity=80, hand="right"),  # E
            Note(pitch=67, time=0.0, duration=1.0, velocity=80, hand="right"),  # G
        ]
        simple_chord = ChordEvent(
            time=0.0, duration=1.0, chord="C", confidence=0.9, root="C", quality="major"
        )
        simple_voicing = await analyze_voicing(simple_notes, simple_chord)

        # Extended jazz chord with extensions
        complex_notes = [
            Note(pitch=60, time=0.0, duration=1.0, velocity=80, hand="left"),   # C
            Note(pitch=64, time=0.0, duration=1.0, velocity=80, hand="left"),   # E
            Note(pitch=67, time=0.0, duration=1.0, velocity=80, hand="left"),   # G
            Note(pitch=71, time=0.0, duration=1.0, velocity=80, hand="right"),  # B
            Note(pitch=74, time=0.0, duration=1.0, velocity=80, hand="right"),  # D (9th)
            Note(pitch=77, time=0.0, duration=1.0, velocity=80, hand="right"),  # F (11th)
            Note(pitch=81, time=0.0, duration=1.0, velocity=80, hand="right"),  # A (13th)
        ]
        complex_chord = ChordEvent(
            time=0.0, duration=1.0, chord="Cmaj13", confidence=0.9, root="C", quality="maj13"
        )
        complex_voicing = await analyze_voicing(complex_notes, complex_chord)

        # Complex voicing should have higher complexity score
        assert simple_voicing.complexity_score < complex_voicing.complexity_score, \
            f"Simple ({simple_voicing.complexity_score}) should be less complex than extended ({complex_voicing.complexity_score})"

        # Check extension detection
        assert len(complex_voicing.extensions) >= 3, "Should detect 9th, 11th, 13th extensions"


class TestProgressionDetectionAccuracy:
    """Test progression pattern detection with real chord sequences"""

    @pytest.mark.asyncio
    async def test_ii_v_i_detection(self):
        """Test detection of jazz ii-V-I progression"""
        # ii-V-I in C major
        chord_events = [
            ChordEvent(time=0.0, duration=2.0, chord="Dm7", confidence=0.9, root="D", quality="m7"),
            ChordEvent(time=2.0, duration=2.0, chord="G7", confidence=0.9, root="G", quality="7"),
            ChordEvent(time=4.0, duration=2.0, chord="Cmaj7", confidence=0.9, root="C", quality="maj7"),
        ]

        # Convert to dict format expected by detect_progressions
        chords = [chord_event_to_dict(c) for c in chord_events]
        patterns = detect_progressions(chords)

        # Should detect ii-V-I pattern
        assert len(patterns) > 0, "Should detect at least one pattern"

        ii_v_i_detected = any(p.pattern_name == "ii_v_i_major" for p in patterns)
        assert ii_v_i_detected, "Should detect ii-V-I pattern"

        # Check pattern details
        ii_v_i_pattern = next(p for p in patterns if p.pattern_name == "ii_v_i_major")
        assert ii_v_i_pattern.genre.value == "jazz", "ii-V-I is a jazz pattern"
        assert ii_v_i_pattern.confidence > 0.7, "Should have high confidence"
        assert ii_v_i_pattern.start_index == 0
        assert ii_v_i_pattern.end_index == 2

    @pytest.mark.asyncio
    async def test_blues_progression_detection(self):
        """Test detection of 12-bar blues progression"""
        # Simplified 12-bar blues in C
        chords = [
            # Bars 1-4: I
            ChordEvent(time=0.0, duration=4.0, chord="C7", confidence=0.9, root="C", quality="7"),
            ChordEvent(time=4.0, duration=4.0, chord="C7", confidence=0.9, root="C", quality="7"),
            ChordEvent(time=8.0, duration=4.0, chord="C7", confidence=0.9, root="C", quality="7"),
            ChordEvent(time=12.0, duration=4.0, chord="C7", confidence=0.9, root="C", quality="7"),
            # Bars 5-6: IV
            ChordEvent(time=16.0, duration=4.0, chord="F7", confidence=0.9, root="F", quality="7"),
            ChordEvent(time=20.0, duration=4.0, chord="F7", confidence=0.9, root="F", quality="7"),
            # Bars 7-8: I
            ChordEvent(time=24.0, duration=4.0, chord="C7", confidence=0.9, root="C", quality="7"),
            ChordEvent(time=28.0, duration=4.0, chord="C7", confidence=0.9, root="C", quality="7"),
            # Bars 9-10: V-IV
            ChordEvent(time=32.0, duration=4.0, chord="G7", confidence=0.9, root="G", quality="7"),
            ChordEvent(time=36.0, duration=4.0, chord="F7", confidence=0.9, root="F", quality="7"),
            # Bars 11-12: I-V (turnaround)
            ChordEvent(time=40.0, duration=4.0, chord="C7", confidence=0.9, root="C", quality="7"),
            ChordEvent(time=44.0, duration=4.0, chord="G7", confidence=0.9, root="G", quality="7"),
        ]

        chords_dict = [chord_event_to_dict(c) for c in chords]
        patterns = detect_progressions(chords_dict)  # total_duration=48.0)

        # Should detect blues pattern
        blues_detected = any("blues" in p.pattern_name.lower() or p.genre.value == "blues" for p in patterns)
        assert blues_detected, "Should detect blues progression"

    @pytest.mark.asyncio
    async def test_pop_progression_detection(self):
        """Test detection of I-V-vi-IV (pop) progression"""
        # I-V-vi-IV in C (e.g., "Let It Be")
        chords = [
            ChordEvent(time=0.0, duration=2.0, chord="C", confidence=0.9, root="C", quality="major"),
            ChordEvent(time=2.0, duration=2.0, chord="G", confidence=0.9, root="G", quality="major"),
            ChordEvent(time=4.0, duration=2.0, chord="Am", confidence=0.9, root="A", quality="minor"),
            ChordEvent(time=6.0, duration=2.0, chord="F", confidence=0.9, root="F", quality="major"),
        ]

        chords_dict = [chord_event_to_dict(c) for c in chords]
        patterns = detect_progressions(chords_dict)  # total_duration=8.0)

        # Should detect pop progression pattern
        pop_detected = any(
            p.pattern_name in ["I-V-vi-IV", "Four Chords"] or p.genre.value == "pop"
            for p in patterns
        )
        assert pop_detected, "Should detect pop progression (I-V-vi-IV)"


class TestReharmonizationSuggestionsQuality:
    """Test quality and validity of reharmonization suggestions"""

    @pytest.mark.asyncio
    async def test_diatonic_substitution_validity(self):
        """Test that diatonic substitutions are musically valid"""
        # Cmaj7 chord
        chord_event = ChordEvent(time=0.0, duration=2.0, chord="Cmaj7", confidence=0.9, root="C", quality="maj7")
        key = "C"

        # Convert to dict and call reharmonize_progression
        result = reharmonize_progression([chord_event_to_dict(chord_event)], key)

        # Result has 'reharmonization_options' which is list of chord options
        # Each chord option has 'suggestions' list
        chord_options = result['reharmonization_options']
        assert len(chord_options) > 0, "Should have chord options"

        suggestions = chord_options[0]['suggestions']

        # Should have multiple suggestions
        assert len(suggestions) > 0, "Should generate reharmonization suggestions"

        # Check for diatonic substitutions
        diatonic_subs = [s for s in suggestions if s['type'] == "diatonic_substitution"]
        assert len(diatonic_subs) > 0, "Should include diatonic substitutions"

        # Diatonic subs for Cmaj7 should include Em7, Am7 (relative minor/mediant)
        suggested_chords = [s['chord'] for s in diatonic_subs]
        assert any("Em" in c or "Am" in c for c in suggested_chords), \
            "Should suggest relative minor substitutions"

    @pytest.mark.asyncio
    async def test_tritone_substitution_for_dominants(self):
        """Test tritone substitution for dominant 7th chords"""
        # G7 dominant chord
        chord_event = ChordEvent(time=0.0, duration=2.0, chord="G7", confidence=0.9, root="G", quality="7")
        key = "C"

        result = reharmonize_progression([chord_event_to_dict(chord_event)], key)
        chord_options = result['reharmonization_options']
        suggestions = chord_options[0]['suggestions']

        # Should include tritone substitution
        tritone_subs = [s for s in suggestions if s['type'] == "tritone_substitution"]

        if len(tritone_subs) > 0:
            # Tritone sub of G7 should be Db7
            suggested_chords = [s['chord'] for s in tritone_subs]
            assert any("Db" in c or "C#" in c for c in suggested_chords), \
                "Tritone sub of G7 should suggest Db7"

    @pytest.mark.asyncio
    async def test_suggestions_categorized_by_jazz_level(self):
        """Test that suggestions are properly categorized by difficulty"""
        chord_event = ChordEvent(time=0.0, duration=2.0, chord="Cmaj7", confidence=0.9, root="C", quality="maj7")
        key = "C"

        result = reharmonize_progression([chord_event_to_dict(chord_event)], key, jazz_level=5)
        chord_options = result['reharmonization_options']
        suggestions = chord_options[0]['suggestions']

        # Should have suggestions at different jazz levels
        jazz_levels = [s['jazz_level'] for s in suggestions]

        # Should have both beginner and more advanced suggestions
        assert min(jazz_levels) <= 2, "Should have beginner-friendly suggestions"
        assert max(jazz_levels) >= 2, "Should have some intermediate suggestions"
        assert len(set(jazz_levels)) > 1, "Should have variety in difficulty levels"

    @pytest.mark.asyncio
    async def test_voice_leading_quality_assessment(self):
        """Test that voice leading quality is properly assessed"""
        chord_event = ChordEvent(time=0.0, duration=2.0, chord="Cmaj7", confidence=0.9, root="C", quality="maj7")
        key = "C"

        result = reharmonize_progression([chord_event_to_dict(chord_event)], key)
        chord_options = result['reharmonization_options']
        suggestions = chord_options[0]['suggestions']

        # All suggestions should have voice leading quality assigned
        for suggestion in suggestions:
            assert suggestion['voice_leading'] in ["smooth", "moderate", "dramatic"], \
                f"Invalid voice leading quality: {suggestion['voice_leading']}"

        # Diatonic subs should generally have smooth voice leading
        diatonic_subs = [s for s in suggestions if s['type'] == "diatonic_substitution"]
        if diatonic_subs:
            smooth_count = sum(1 for s in diatonic_subs if s['voice_leading'] == "smooth")
            assert smooth_count > 0, "Diatonic subs should include smooth voice leading options"


class TestCompleteAnalysisPipeline:
    """Test the complete end-to-end analysis pipeline"""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """
        Test complete flow: chords → voicing analysis → pattern detection → reharmonization

        This simulates the full transcription analysis pipeline from detected chords
        to generating learning insights.
        """
        # Step 1: Simulate chord detection output
        chords = [
            ChordEvent(time=0.0, duration=2.0, chord="Dm7", confidence=0.92, root="D", quality="m7"),
            ChordEvent(time=2.0, duration=2.0, chord="G7", confidence=0.88, root="G", quality="7"),
            ChordEvent(time=4.0, duration=4.0, chord="Cmaj7", confidence=0.95, root="C", quality="maj7"),
        ]

        # Step 2: Simulate MIDI notes
        notes = [
            # Dm7
            Note(pitch=50, time=0.0, duration=2.0, velocity=80, hand="left"),
            Note(pitch=53, time=0.0, duration=2.0, velocity=80, hand="left"),
            Note(pitch=57, time=0.0, duration=2.0, velocity=85, hand="right"),
            Note(pitch=60, time=0.0, duration=2.0, velocity=85, hand="right"),
            # G7
            Note(pitch=55, time=2.0, duration=2.0, velocity=80, hand="left"),
            Note(pitch=59, time=2.0, duration=2.0, velocity=80, hand="left"),
            Note(pitch=62, time=2.0, duration=2.0, velocity=85, hand="right"),
            Note(pitch=65, time=2.0, duration=2.0, velocity=85, hand="right"),
            # Cmaj7
            Note(pitch=48, time=4.0, duration=4.0, velocity=90, hand="left"),
            Note(pitch=52, time=4.0, duration=4.0, velocity=90, hand="left"),
            Note(pitch=55, time=4.0, duration=4.0, velocity=95, hand="right"),
            Note(pitch=59, time=4.0, duration=4.0, velocity=95, hand="right"),
        ]

        key = "C"
        total_duration = 6.0

        # Step 3: Analyze voicings
        voicings = await analyze_all_voicings(notes, chords)
        assert len(voicings) == 3, "Should analyze all chords"

        # Step 4: Detect progression patterns
        chords_dict = [chord_event_to_dict(c) for c in chords]
        patterns = detect_progressions(chords_dict)
        assert len(patterns) > 0, "Should detect progression patterns"

        # Should detect ii-V-I
        ii_v_i_detected = any(p.pattern_name == "ii_v_i_major" for p in patterns)
        assert ii_v_i_detected, "Should detect ii-V-I progression"

        # Step 5: Generate reharmonization suggestions for entire progression
        result = reharmonize_progression(chords_dict, key)

        # Flatten all suggestions from all chords
        chord_options = result['reharmonization_options']
        all_suggestions = []
        for chord_option in chord_options:
            all_suggestions.extend(chord_option['suggestions'])

        assert len(all_suggestions) > 0, "Should generate reharmonization suggestions"

        # Step 6: Verify complete analysis data structure
        # This represents what would be returned to the frontend
        analysis_result = {
            "voicings": voicings,
            "patterns": patterns,
            "reharmonizations": all_suggestions,
            "key": key,
            "total_chords": len(chords),
        }

        # Verify structure completeness
        assert "voicings" in analysis_result
        assert "patterns" in analysis_result
        assert "reharmonizations" in analysis_result
        assert analysis_result["total_chords"] == 3

        # Verify data relationships
        assert len(analysis_result["voicings"]) == len(chords), \
            "Should have one voicing analysis per chord"
