"""
Unit tests for Reharmonization Engine and Tension Analyzer (Phase 5E)
"""

import pytest
from app.pipeline.reharmonization_engine import (
    get_tritone_substitution,
    get_diatonic_substitutes,
    get_passing_chords,
    get_backdoor_substitution,
    reharmonize_progression,
    ReharmonizationType,
)
from app.pipeline.tension_analyzer import (
    calculate_chord_tension,
    analyze_tension_curve,
    get_tension_recommendations,
)


class TestReharmonizationEngine:
    """Tests for reharmonization suggestions"""

    def test_tritone_substitution_g7(self):
        """Test tritone sub for G7 (should be Db7)"""
        chord = {"root": "G", "quality": "7"}
        result = get_tritone_substitution(chord)
        
        assert result is not None
        assert "Db7" in result.suggested_chord or "C#7" in result.suggested_chord
        assert result.reharmonization_type == ReharmonizationType.TRITONE_SUB

    def test_tritone_sub_only_for_dominant(self):
        """Tritone sub should only work for dominant 7th chords"""
        # Major 7 - should not work
        chord = {"root": "C", "quality": "maj7"}
        assert get_tritone_substitution(chord) is None
        
        # Minor 7 - should not work
        chord = {"root": "D", "quality": "m7"}
        assert get_tritone_substitution(chord) is None

    def test_diatonic_substitutes_tonic(self):
        """Test diatonic subs for I chord (should include vi and iii)"""
        chord = {"root": "C", "quality": "maj7"}
        results = get_diatonic_substitutes(chord, "C")
        
        assert len(results) >= 2
        # Should suggest Am7 (vi) and Em7 (iii)
        suggested_roots = [r.suggested_chord for r in results]
        assert any("A" in s for s in suggested_roots)  # vi

    def test_diatonic_substitutes_subdominant(self):
        """Test diatonic subs for IV chord (should include ii)"""
        chord = {"root": "F", "quality": "maj7"}
        results = get_diatonic_substitutes(chord, "C")
        
        assert len(results) >= 1
        # Should suggest Dm7 (ii)
        assert any("D" in r.suggested_chord for r in results)

    def test_passing_chords(self):
        """Test passing chord suggestions"""
        chord1 = {"root": "C", "quality": "maj7"}
        chord2 = {"root": "D", "quality": "m7"}
        
        results = get_passing_chords(chord1, chord2)
        
        assert len(results) >= 1
        # Should include approach and/or diminished passing
        types = [r.reharmonization_type for r in results]
        assert ReharmonizationType.APPROACH_CHORD in types or ReharmonizationType.DIMINISHED in types

    def test_backdoor_substitution(self):
        """Test backdoor (bVII7) substitution for V-I"""
        chord = {"root": "G", "quality": "7"}
        next_chord = {"root": "C", "quality": "maj7"}
        
        result = get_backdoor_substitution(chord, next_chord)
        
        assert result is not None
        assert "Bb7" in result.suggested_chord or "A#7" in result.suggested_chord
        assert result.reharmonization_type == ReharmonizationType.BACKDOOR

    def test_full_progression_reharmonization(self):
        """Test reharmonizing an entire progression"""
        chords = [
            {"root": "D", "quality": "m7"},
            {"root": "G", "quality": "7"},
            {"root": "C", "quality": "maj7"},
        ]
        
        result = reharmonize_progression(chords, key="C", jazz_level=3)
        
        assert "reharmonization_options" in result
        assert len(result["reharmonization_options"]) == 3
        assert result["total_suggestions"] > 0

    def test_jazz_level_filtering(self):
        """Test that jazz level filters suggestions"""
        chords = [{"root": "G", "quality": "7"}]
        
        result_low = reharmonize_progression(chords, key="C", jazz_level=1)
        result_high = reharmonize_progression(chords, key="C", jazz_level=5)
        
        # Higher jazz level should have more suggestions
        assert result_high["total_suggestions"] >= result_low["total_suggestions"]


class TestTensionAnalyzer:
    """Tests for tension curve analysis"""

    def test_tonic_low_tension(self):
        """Tonic chord should have low tension"""
        chord = {"root": "C", "quality": "maj7"}
        result = calculate_chord_tension(chord, key="C")
        
        assert result.tension_level < 0.4
        assert result.distance_from_tonic == 0

    def test_dominant_high_tension(self):
        """Dominant 7th should have higher tension"""
        chord = {"root": "G", "quality": "7"}
        result = calculate_chord_tension(chord, key="C")
        
        assert result.tension_level > 0.3
        assert result.distance_from_tonic == 7

    def test_altered_dominant_highest_tension(self):
        """Altered dominant should have high tension"""
        chord = {"root": "G", "quality": "7alt"}
        result = calculate_chord_tension(chord, key="C")
        
        assert result.tension_level > 0.5

    def test_tension_curve_analysis(self):
        """Test full tension curve analysis"""
        chords = [
            {"root": "C", "quality": "maj7"},   # Low tension
            {"root": "A", "quality": "m7"},     # Low-medium
            {"root": "D", "quality": "m7"},     # Medium
            {"root": "G", "quality": "7"},      # High
            {"root": "C", "quality": "maj7"},   # Low (resolution)
        ]
        
        result = analyze_tension_curve(chords, key="C")
        
        assert "tension_curve" in result
        assert "summary" in result
        assert len(result["tension_curve"]) == 5
        
        # Should detect arch pattern (build and release)
        summary = result["summary"]
        assert "climax_position" in summary
        assert "arc_shape" in summary

    def test_tension_recommendations(self):
        """Test tension recommendations"""
        analysis = {
            "summary": {
                "average_tension": 0.7,
                "arc_shape": "rising",
                "resolution_count": 0
            }
        }
        
        recs = get_tension_recommendations(analysis)
        
        assert len(recs) > 0
        # Should recommend adding resolution
        rec_types = [r["type"] for r in recs]
        assert "reduce_tension" in rec_types or "no_resolution" in rec_types

    def test_low_tension_recommendation(self):
        """Test recommendation for very consonant progression"""
        analysis = {
            "summary": {
                "average_tension": 0.15,
                "arc_shape": "flat",
                "resolution_count": 2
            }
        }
        
        recs = get_tension_recommendations(analysis)
        
        # Should suggest adding interest
        rec_types = [r["type"] for r in recs]
        assert "increase_interest" in rec_types


class TestIntegration:
    """Integration tests for Phase 5E"""

    def test_reharmonization_with_tension(self):
        """Test that reharmonization affects tension"""
        from app.pipeline.tension_analyzer import calculate_chord_tension
        
        original = {"root": "G", "quality": "7"}
        
        # Get tritone sub
        tritone = get_tritone_substitution(original)
        assert tritone is not None
        
        # Parse the suggested chord
        suggested_root = tritone.suggested_chord.replace("7", "")
        substituted = {"root": suggested_root, "quality": "7"}
        
        # Both should have similar tension (both are dominant 7ths)
        orig_tension = calculate_chord_tension(original, key="C")
        sub_tension = calculate_chord_tension(substituted, key="C")
        
        # Tension should be in similar range (both dominant)
        assert abs(orig_tension.tension_level - sub_tension.tension_level) < 0.3
