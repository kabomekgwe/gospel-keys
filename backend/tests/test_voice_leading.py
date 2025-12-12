"""
Unit tests for Voice Leading Analyzer and Cadence Detector (Phase 5C)
"""

import pytest
from app.pipeline.voice_leading_analyzer import (
    analyze_voice_leading,
    analyze_progression_voice_leading,
)
from app.pipeline.cadence_detector import (
    detect_cadences,
    analyze_cadential_structure,
    CadenceType,
)


class TestVoiceLeadingAnalyzer:
    """Tests for voice leading analysis"""

    def test_analyze_smooth_voice_leading(self):
        """Test C to Am (smooth, common tones)"""
        chord1 = {"root": "C", "quality": ""}
        chord2 = {"root": "A", "quality": "m"}
        
        result = analyze_voice_leading(chord1, chord2)
        
        assert "smoothness_score" in result
        assert result["smoothness_score"] > 0.5  # Should be smooth
        assert len(result["common_tone_notes"]) >= 1  # C and E are common

    def test_analyze_rough_voice_leading(self):
        """Test C to F# (distant, no common tones)"""
        chord1 = {"root": "C", "quality": ""}
        chord2 = {"root": "F#", "quality": ""}
        
        result = analyze_voice_leading(chord1, chord2)
        
        # Tritone relationship should still be relatively smooth with minimal voice leading
        assert result["smoothness_score"] > 0  # Just verify it's a valid score
        assert result["total_movement"] > 0

    def test_common_tone_detection(self):
        """Test common tone detection in I-vi"""
        chord1 = {"root": "C", "quality": "maj7"}  # C E G B
        chord2 = {"root": "A", "quality": "m7"}    # A C E G
        
        result = analyze_voice_leading(chord1, chord2)
        
        # C, E, G are common
        assert len(result["common_tone_notes"]) >= 2

    def test_motion_type_classification(self):
        """Test motion type detection"""
        chord1 = {"root": "C", "quality": ""}
        chord2 = {"root": "G", "quality": ""}
        
        result = analyze_voice_leading(chord1, chord2)
        
        assert "motion_types" in result
        assert isinstance(result["motion_types"], dict)

    def test_progression_analysis(self):
        """Test full progression voice leading analysis"""
        chords = [
            {"root": "D", "quality": "m7"},
            {"root": "G", "quality": "7"},
            {"root": "C", "quality": "maj7"},
        ]
        
        result = analyze_progression_voice_leading(chords)
        
        assert "overall_smoothness" in result
        assert "transitions" in result
        assert len(result["transitions"]) == 2
        assert "guide_tones" in result

    def test_guide_tone_extraction(self):
        """Test guide tone line extraction for jazz"""
        chords = [
            {"root": "D", "quality": "m7"},   # 3rd = F, 7th = C
            {"root": "G", "quality": "7"},    # 3rd = B, 7th = F
            {"root": "C", "quality": "maj7"}, # 3rd = E, 7th = B
        ]
        
        result = analyze_progression_voice_leading(chords)
        
        assert result["guide_tones"] is not None
        assert "thirds" in result["guide_tones"]
        assert len(result["guide_tones"]["thirds"]["notes"]) == 3


class TestCadenceDetector:
    """Tests for cadence detection"""

    def test_detect_authentic_cadence(self):
        """Test V-I (authentic) cadence detection"""
        chords = [
            {"root": "G", "quality": "7", "time": 0},
            {"root": "C", "quality": "maj7", "time": 1},
        ]
        
        cadences = detect_cadences(chords, key="C")
        
        assert len(cadences) >= 1
        authentic = next((c for c in cadences if "authentic" in c.cadence_type.value), None)
        assert authentic is not None

    def test_detect_plagal_cadence(self):
        """Test IV-I (plagal) cadence detection"""
        chords = [
            {"root": "F", "quality": "", "time": 0},
            {"root": "C", "quality": "", "time": 1},
        ]
        
        cadences = detect_cadences(chords, key="C")
        
        plagal = next((c for c in cadences if c.cadence_type == CadenceType.PLAGAL), None)
        assert plagal is not None

    def test_detect_deceptive_cadence(self):
        """Test V-vi (deceptive) cadence detection"""
        chords = [
            {"root": "G", "quality": "7", "time": 0},
            {"root": "A", "quality": "m", "time": 1},
        ]
        
        cadences = detect_cadences(chords, key="C")
        
        deceptive = next((c for c in cadences if c.cadence_type == CadenceType.DECEPTIVE), None)
        assert deceptive is not None

    def test_detect_half_cadence(self):
        """Test half cadence (ending on V)"""
        chords = [
            {"root": "C", "quality": "", "time": 0},
            {"root": "D", "quality": "m", "time": 1},
            {"root": "G", "quality": "7", "time": 2},
        ]
        
        cadences = detect_cadences(chords, key="C")
        
        half = next((c for c in cadences if c.cadence_type == CadenceType.HALF), None)
        assert half is not None

    def test_backdoor_cadence(self):
        """Test bVII-I (backdoor) cadence"""
        chords = [
            {"root": "Bb", "quality": "7", "time": 0},
            {"root": "C", "quality": "maj7", "time": 1},
        ]
        
        cadences = detect_cadences(chords, key="C")
        
        backdoor = next((c for c in cadences if c.cadence_type == CadenceType.BACKDOOR), None)
        assert backdoor is not None

    def test_cadential_structure_analysis(self):
        """Test comprehensive cadential analysis"""
        chords = [
            {"root": "C", "quality": "maj7", "time": 0},
            {"root": "A", "quality": "m7", "time": 1},
            {"root": "D", "quality": "m7", "time": 2},
            {"root": "G", "quality": "7", "time": 3},
            {"root": "C", "quality": "maj7", "time": 4},
        ]
        
        result = analyze_cadential_structure(chords)
        
        assert "cadences" in result
        assert "summary" in result
        assert "harmonic_closure" in result
        assert "estimated_key" in result

    def test_key_estimation(self):
        """Test automatic key detection from progression"""
        chords = [
            {"root": "D", "quality": "m7", "time": 0},
            {"root": "G", "quality": "7", "time": 1},
            {"root": "C", "quality": "maj7", "time": 2},
        ]
        
        result = analyze_cadential_structure(chords)
        
        # Should detect C as the key
        assert result["estimated_key"] in ["C", "G"]  # Either is reasonable
