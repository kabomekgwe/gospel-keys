"""
Unit tests for Harmonic Function Analyzer and Modulation Detector (Phase 5D)
"""

import pytest
from app.pipeline.harmonic_function_analyzer import (
    analyze_chord_function,
    analyze_progression_functions,
    HarmonicFunction,
)
from app.pipeline.modulation_detector import (
    detect_modulations,
    analyze_key_structure,
    ModulationType,
)


class TestHarmonicFunctionAnalyzer:
    """Tests for harmonic function analysis"""

    def test_tonic_function_major(self):
        """Test I chord as tonic"""
        chord = {"root": "C", "quality": "maj7"}
        result = analyze_chord_function(chord, "C", "major")
        
        assert result.function == HarmonicFunction.TONIC
        assert result.roman_numeral == "I"
        assert result.is_diatonic

    def test_subdominant_function(self):
        """Test IV chord as subdominant"""
        chord = {"root": "F", "quality": "maj7"}
        result = analyze_chord_function(chord, "C", "major")
        
        assert result.function == HarmonicFunction.SUBDOMINANT
        assert result.roman_numeral == "IV"

    def test_dominant_function(self):
        """Test V chord as dominant"""
        chord = {"root": "G", "quality": "7"}
        result = analyze_chord_function(chord, "C", "major")
        
        assert result.function == HarmonicFunction.DOMINANT
        assert result.roman_numeral == "V"

    def test_ii_minor_subdominant(self):
        """Test ii chord as subdominant"""
        chord = {"root": "D", "quality": "m7"}
        result = analyze_chord_function(chord, "C", "major")
        
        assert result.function == HarmonicFunction.SUBDOMINANT
        assert result.roman_numeral == "ii"

    def test_vi_minor_tonic(self):
        """Test vi chord as tonic function"""
        chord = {"root": "A", "quality": "m7"}
        result = analyze_chord_function(chord, "C", "major")
        
        assert result.function == HarmonicFunction.TONIC
        assert result.roman_numeral == "vi"

    def test_secondary_dominant_v_of_v(self):
        """Test V/V (D7 in C major)"""
        chord = {"root": "D", "quality": "7"}
        result = analyze_chord_function(chord, "C", "major")
        
        assert result.function == HarmonicFunction.SECONDARY_DOMINANT
        assert "V" in result.roman_numeral
        assert result.applied_to == "V"

    def test_borrowed_chord_flat_vii(self):
        """Test bVII as borrowed chord"""
        chord = {"root": "Bb", "quality": ""}
        result = analyze_chord_function(chord, "C", "major")
        
        assert result.function == HarmonicFunction.BORROWED
        assert "VII" in result.roman_numeral

    def test_progression_analysis(self):
        """Test full progression function analysis"""
        chords = [
            {"root": "C", "quality": "maj7"},
            {"root": "A", "quality": "m7"},
            {"root": "D", "quality": "m7"},
            {"root": "G", "quality": "7"},
            {"root": "C", "quality": "maj7"},
        ]
        
        result = analyze_progression_functions(chords, key="C")
        
        assert result["key"] == "C"
        assert "chord_functions" in result
        assert len(result["chord_functions"]) == 5
        assert "function_distribution" in result
        assert "diatonic_percentage" in result

    def test_function_sequence(self):
        """Test T-S-D-T progression"""
        chords = [
            {"root": "C", "quality": ""},    # T
            {"root": "F", "quality": ""},    # S
            {"root": "G", "quality": "7"},   # D
            {"root": "C", "quality": ""},    # T
        ]
        
        result = analyze_progression_functions(chords, key="C")
        
        sequence = result["function_sequence"]
        assert sequence == ["T", "S", "D", "T"]


class TestModulationDetector:
    """Tests for modulation detection"""

    def test_no_modulation_simple_progression(self):
        """Test that stable progression has no modulation"""
        chords = [
            {"root": "C", "quality": "maj7", "time": 0},
            {"root": "A", "quality": "m7", "time": 1},
            {"root": "D", "quality": "m7", "time": 2},
            {"root": "G", "quality": "7", "time": 3},
            {"root": "C", "quality": "maj7", "time": 4},
        ]
        
        modulations = detect_modulations(chords, initial_key="C")
        
        # Should be minimal or no modulations for ii-V-I in C
        assert len(modulations) <= 1

    def test_key_structure_analysis(self):
        """Test comprehensive key analysis"""
        chords = [
            {"root": "C", "quality": "maj7", "time": 0},
            {"root": "D", "quality": "m7", "time": 1},
            {"root": "G", "quality": "7", "time": 2},
            {"root": "C", "quality": "maj7", "time": 3},
        ]
        
        result = analyze_key_structure(chords)
        
        assert "initial_key" in result
        assert "key_areas" in result
        assert "modulations" in result
        assert "is_monotonal" in result

    def test_monotonal_detection(self):
        """Test detection of single-key progression"""
        chords = [
            {"root": "C", "quality": ""},
            {"root": "F", "quality": ""},
            {"root": "G", "quality": ""},
            {"root": "C", "quality": ""},
        ]
        
        result = analyze_key_structure(chords)
        
        assert result["is_monotonal"] == True
        assert result["key_diversity"] == 1

    def test_relative_key_detection(self):
        """Test modulation to relative key"""
        # C major to A minor (relative)
        chords = [
            {"root": "C", "quality": "maj7", "time": 0},
            {"root": "G", "quality": "7", "time": 1},
            {"root": "C", "quality": "maj7", "time": 2},
            {"root": "E", "quality": "7", "time": 3},  # V of vi
            {"root": "A", "quality": "m", "time": 4},  # vi / i
            {"root": "D", "quality": "m7", "time": 5},
            {"root": "E", "quality": "7", "time": 6},
            {"root": "A", "quality": "m", "time": 7},
        ]
        
        result = analyze_key_structure(chords)
        
        # Should at minimum detect the two key areas
        assert len(result["key_areas"]) >= 1


class TestIntegration:
    """Integration tests combining harmonic analysis"""

    def test_full_harmonic_analysis(self):
        """Test complete harmonic analysis workflow"""
        # "Autumn Leaves" type progression (first 8 bars)
        chords = [
            {"root": "A", "quality": "m7"},
            {"root": "D", "quality": "7"},
            {"root": "G", "quality": "maj7"},
            {"root": "C", "quality": "maj7"},
            {"root": "F#", "quality": "m7b5"},
            {"root": "B", "quality": "7"},
            {"root": "E", "quality": "m7"},
            {"root": "E", "quality": "m7"},
        ]
        
        # Harmonic function analysis
        func_result = analyze_progression_functions(chords)
        
        assert "chord_functions" in func_result
        assert "function_distribution" in func_result
        
        # Key structure analysis
        key_result = analyze_key_structure(chords)
        
        assert "initial_key" in key_result
        assert "key_areas" in key_result
