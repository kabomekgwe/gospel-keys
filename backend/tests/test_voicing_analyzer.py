"""
Comprehensive tests for voicing analyzer module

Tests cover:
- Voicing type classification (close, open, drop-2, rootless, etc.)
- Chord tone identification (root, 3rd, 7th, extensions)
- Complexity calculation
- Hand span measurement
- Edge cases and error handling
"""

import pytest
from app.pipeline.voicing_analyzer import (
    VoicingInfo,
    VoicingType,
    analyze_voicing,
    analyze_all_voicings,
    classify_voicing_type,
    identify_chord_tones,
    calculate_complexity_score,
    estimate_hand_span,
)
from app.gospel import Note
from app.schemas.transcription import ChordEvent


class TestVoicingTypeClassification:
    """Test voicing type classification accuracy"""

    def test_close_voicing_detection(self):
        """Test close voicing (all notes within an octave, 4+ notes)"""
        # Cmaj7: C3, E3, G3, B3 (all within one octave, 4 notes)
        intervals = [4, 3, 4]  # C to E (4), E to G (3), G to B (4)
        width = 11  # Total span: 11 semitones (within octave)
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.CLOSE, "Should classify as close voicing"

    def test_open_voicing_detection(self):
        """Test open voicing (spanning more than an octave, no drop pattern)"""
        # Open voicing with mixed intervals, width > 12 but intervals don't match quartal or drop patterns
        intervals = [4, 6, 6]  # Mixed intervals (not all 5 or 6), all <= 7
        width = 16  # Total span: 16 semitones (> octave)
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.OPEN, "Should classify as open voicing"

    def test_drop_2_voicing_detection(self):
        """Test drop-2 voicing (second voice dropped an octave)"""
        # Cmaj7 drop-2: C3, B3, E4, G4
        # intervals[1] or intervals[2] > 7 triggers drop-2
        intervals = [11, 5, 3]  # intervals[0]=11 > 7, but need to check intervals[1] or [2]
        width = 19
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        # Actually, intervals[0]=11 > 7, so this will be DROP_3, not DROP_2
        # Let me use a proper drop-2 pattern: small, large, small
        intervals = [3, 9, 4]  # Small, large (9 > 7), small - this is drop-2
        width = 16

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.DROP_2, "Should classify as drop-2 voicing"

    def test_drop_3_voicing_detection(self):
        """Test drop-3 voicing (first interval large)"""
        # Drop-3: intervals[0] > 7
        intervals = [10, 3, 4]  # Large first interval (10 > 7)
        width = 17
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.DROP_3, "Should classify as drop-3 voicing"

    def test_rootless_voicing_detection(self):
        """Test rootless voicing (no root present) - common in jazz"""
        # Em7 rootless: G, B, D, F# (no E)
        intervals = [4, 3, 4]
        width = 11
        has_root = False  # No root!

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.ROOTLESS, "Should classify as rootless voicing"

    def test_shell_voicing_detection(self):
        """Test shell voicing (root-3rd-7th only)"""
        # Cmaj7 shell: C, E, B (3 notes, spans < 14 semitones)
        intervals = [4, 7]  # C to E, E to B
        width = 11
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.SHELL, "Should classify as shell voicing"

    def test_quartal_voicing_detection(self):
        """Test quartal voicing (built on 4ths)"""
        # Quartal: C, F, Bb (all perfect 4ths)
        intervals = [5, 5]  # Perfect 4ths (5 semitones each)
        width = 10
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.QUARTAL, "Should classify as quartal voicing"

    def test_cluster_voicing_detection(self):
        """Test cluster voicing (adjacent semitones)"""
        # Cluster: C, Db, D, Eb (chromatic cluster)
        intervals = [1, 1, 1]  # All semitones
        width = 3
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.CLUSTER, "Should classify as cluster voicing"

    def test_spread_voicing_detection(self):
        """Test spread voicing (very wide spacing)"""
        # Very wide voicing: C2, E4, G5
        intervals = [16, 15]  # Very large intervals
        width = 31  # Spans over 2 octaves
        has_root = True

        voicing_type = classify_voicing_type(intervals, width, has_root)
        assert voicing_type == VoicingType.SPREAD, "Should classify as spread voicing"


class TestChordToneIdentification:
    """Test chord tone identification (root, 3rd, 7th, extensions)"""

    def test_root_detection_in_cmaj7(self):
        """Test root note detection in Cmaj7"""
        # Cmaj7: C (root), E (3rd), G (5th), B (7th)
        notes = [60, 64, 67, 71]  # C4, E4, G4, B4
        chord_root = "C"
        chord_quality = "maj7"

        has_root, has_third, has_seventh, extensions = identify_chord_tones(notes, chord_root, chord_quality)

        assert has_root is True, "Should detect root C"
        assert has_third is True, "Should detect 3rd E"
        assert has_seventh is True, "Should detect 7th B"

    def test_missing_root_detection(self):
        """Test detection when root is missing (rootless voicing)"""
        # Cmaj7 rootless: E, G, B (no C)
        notes = [64, 67, 71]  # E4, G4, B4
        chord_root = "C"
        chord_quality = "maj7"

        has_root, has_third, has_seventh, extensions = identify_chord_tones(notes, chord_root, chord_quality)

        assert has_root is False, "Should detect missing root"
        assert has_third is True, "Should detect 3rd E"
        assert has_seventh is True, "Should detect 7th B"

    def test_ninth_extension_detection(self):
        """Test detection of 9th extension"""
        # Cmaj9: C, E, G, B, D (9th)
        notes = [60, 64, 67, 71, 74]  # C4, E4, G4, B4, D5
        chord_root = "C"
        chord_quality = "maj9"

        has_root, has_third, has_seventh, extensions = identify_chord_tones(notes, chord_root, chord_quality)

        assert "9" in extensions, "Should detect 9th extension"

    def test_eleventh_extension_detection(self):
        """Test detection of 11th extension"""
        # C11: C, E, G, Bb, D, F (11th)
        notes = [60, 64, 67, 70, 74, 77]  # C4, E4, G4, Bb4, D5, F5
        chord_root = "C"
        chord_quality = "11"

        has_root, has_third, has_seventh, extensions = identify_chord_tones(notes, chord_root, chord_quality)

        assert "11" in extensions, "Should detect 11th extension"

    def test_thirteenth_extension_detection(self):
        """Test detection of 13th extension"""
        # C13: C, E, G, Bb, D, F, A (13th)
        notes = [60, 64, 67, 70, 74, 77, 81]  # C4, E4, G4, Bb4, D5, F5, A5
        chord_root = "C"
        chord_quality = "13"

        has_root, has_third, has_seventh, extensions = identify_chord_tones(notes, chord_root, chord_quality)

        assert "13" in extensions, "Should detect 13th extension"

    def test_altered_extensions(self):
        """Test detection of altered extensions (b9, #9, #11, b13)"""
        # C7alt with b9: C, E, G, Bb, Db (b9)
        notes = [60, 64, 67, 70, 73]  # C4, E4, G4, Bb4, Db5
        chord_root = "C"
        chord_quality = "7b9"

        has_root, has_third, has_seventh, extensions = identify_chord_tones(notes, chord_root, chord_quality)

        assert "b9" in extensions or "altered" in str(extensions), \
            "Should detect altered extension"


class TestComplexityCalculation:
    """Test voicing complexity scoring (0.0 = simple, 1.0 = advanced)"""

    def test_simple_triad_complexity(self):
        """Test that simple triads get low complexity score"""
        # C major triad: C, E, G
        notes = [60, 64, 67]
        voicing_type = VoicingType.CLOSE
        extensions = []
        width_semitones = 7

        complexity = calculate_complexity_score(
            voicing_type=voicing_type,
            num_notes=len(notes),
            extensions=extensions,
            width=width_semitones
        )

        assert 0.0 <= complexity <= 0.4, f"Simple triad should be low complexity, got {complexity}"

    def test_extended_chord_complexity(self):
        """Test that extended chords get higher complexity score"""
        # C13: C, E, G, Bb, D, F, A (7 notes with extensions)
        notes = [60, 64, 67, 70, 74, 77, 81]
        voicing_type = VoicingType.OPEN
        extensions = ["9", "11", "13"]  # List of extensions
        width_semitones = 21

        complexity = calculate_complexity_score(
            voicing_type=voicing_type,
            num_notes=len(notes),
            extensions=extensions,
            width=width_semitones
        )

        assert 0.6 <= complexity <= 1.0, f"Extended chord should be high complexity, got {complexity}"

    def test_drop2_complexity_moderate(self):
        """Test that drop-2 voicings get moderate complexity"""
        # Cmaj7 drop-2: C, B, E, G (4 notes, common jazz voicing)
        notes = [48, 59, 64, 67]
        voicing_type = VoicingType.DROP_2
        extensions = []
        width_semitones = 19

        complexity = calculate_complexity_score(
            voicing_type=voicing_type,
            num_notes=len(notes),
            extensions=extensions,
            width=width_semitones
        )

        assert 0.4 <= complexity <= 0.7, f"Drop-2 should be moderate complexity, got {complexity}"

    def test_cluster_voicing_high_complexity(self):
        """Test that cluster voicings get high complexity (modern/dissonant)"""
        # Chromatic cluster: C, Db, D, Eb
        notes = [60, 61, 62, 63]
        voicing_type = VoicingType.CLUSTER
        extensions = []
        width_semitones = 3

        complexity = calculate_complexity_score(
            voicing_type=voicing_type,
            num_notes=len(notes),
            extensions=extensions,
            width=width_semitones
        )

        assert 0.7 <= complexity <= 1.0, f"Cluster voicing should be high complexity, got {complexity}"


class TestHandSpanMeasurement:
    """Test hand span calculation in inches"""

    def test_octave_hand_span(self):
        """Test hand span for perfect octave (C to C)"""
        # C3 to C4 (12 semitones = octave)
        width_semitones = 12

        hand_span = estimate_hand_span(width_semitones)

        # Approximate octave span is ~7-8 inches on piano
        assert 6.5 <= hand_span <= 9.0, f"Octave span should be ~7-8 inches, got {hand_span}"

    def test_small_chord_hand_span(self):
        """Test hand span for small chord (triad within octave)"""
        # C major: C, E, G (7 semitones)
        width_semitones = 7

        hand_span = estimate_hand_span(width_semitones)

        # Should be less than octave
        assert hand_span < 7.0, f"Triad span should be < 7 inches, got {hand_span}"

    def test_large_chord_hand_span(self):
        """Test hand span for wide chord"""
        # Very wide voicing: 2 octaves (24 semitones)
        width_semitones = 24

        hand_span = estimate_hand_span(width_semitones)

        # Two octaves ~ 14-16 inches (difficult for most hands)
        assert hand_span > 12.0, f"Two octave span should be > 12 inches, got {hand_span}"

    def test_playability_threshold(self):
        """Test that playability threshold is around 9-10 inches for octave + sixth"""
        # 18 semitones (octave + sixth)
        width_semitones = 18

        hand_span = estimate_hand_span(width_semitones)

        # Formula: 18 * 0.54167 = 9.75 inches
        # Should be challenging but playable for average hands
        assert 9.0 <= hand_span <= 10.5, \
            f"Octave + sixth should be 9-10.5 inches, got {hand_span}"


class TestVoicingAnalysisIntegration:
    """Test complete voicing analysis with real MIDI notes and chords"""

    @pytest.mark.asyncio
    async def test_analyze_voicing_with_cmaj7(self):
        """Test analyzing Cmaj7 voicing from MIDI notes"""
        # Cmaj7 drop-3: C3, B3, E4, G4 (intervals: 11, 5, 3)
        # First interval > 7, so classified as DROP_3
        notes = [
            Note(pitch=48, time=0.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=59, time=0.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=64, time=0.0, duration=1.0, velocity=80, hand="right"),
            Note(pitch=67, time=0.0, duration=1.0, velocity=80, hand="right"),
        ]

        chord = ChordEvent(
            time=0.0,
            duration=1.0,
            chord="Cmaj7",
            confidence=0.9,
            root="C",
            quality="maj7"
        )

        voicing = await analyze_voicing(notes, chord)

        assert voicing is not None, "Should return voicing analysis"
        assert voicing.voicing_type == VoicingType.DROP_3, "Should classify as drop-3 (large first interval)"
        assert voicing.has_root is True, "Should have root C"
        assert voicing.has_third is True, "Should have 3rd E"
        assert voicing.has_seventh is True, "Should have 7th B"
        assert len(voicing.notes) == 4, "Should have 4 notes"

    @pytest.mark.asyncio
    async def test_analyze_chord_sequence(self):
        """Test analyzing multiple chords in sequence"""
        # ii-V-I in C: Dm7, G7, Cmaj7
        notes = [
            # Dm7 at t=0
            Note(pitch=50, time=0.0, duration=1.0, velocity=80, hand="left"),  # D
            Note(pitch=53, time=0.0, duration=1.0, velocity=80, hand="left"),  # F
            Note(pitch=57, time=0.0, duration=1.0, velocity=80, hand="right"),  # A
            Note(pitch=60, time=0.0, duration=1.0, velocity=80, hand="right"),  # C
            # G7 at t=1
            Note(pitch=55, time=1.0, duration=1.0, velocity=80, hand="left"),  # G
            Note(pitch=59, time=1.0, duration=1.0, velocity=80, hand="left"),  # B
            Note(pitch=62, time=1.0, duration=1.0, velocity=80, hand="right"),  # D
            Note(pitch=65, time=1.0, duration=1.0, velocity=80, hand="right"),  # F
            # Cmaj7 at t=2
            Note(pitch=48, time=2.0, duration=1.0, velocity=80, hand="left"),  # C
            Note(pitch=52, time=2.0, duration=1.0, velocity=80, hand="left"),  # E
            Note(pitch=55, time=2.0, duration=1.0, velocity=80, hand="right"),  # G
            Note(pitch=59, time=2.0, duration=1.0, velocity=80, hand="right"),  # B
        ]

        chords = [
            ChordEvent(time=0.0, duration=1.0, chord="Dm7", confidence=0.9, root="D", quality="m7"),
            ChordEvent(time=1.0, duration=1.0, chord="G7", confidence=0.9, root="G", quality="7"),
            ChordEvent(time=2.0, duration=1.0, chord="Cmaj7", confidence=0.9, root="C", quality="maj7"),
        ]

        voicings = await analyze_all_voicings(notes, chords)

        assert len(voicings) == 3, "Should analyze all 3 chords"
        assert all(v is not None for v in voicings), "All voicings should be analyzed"

        # Check that voicings are different (voice leading)
        assert voicings[0].notes != voicings[1].notes, "Dm7 and G7 should have different voicings"
        assert voicings[1].notes != voicings[2].notes, "G7 and Cmaj7 should have different voicings"

    @pytest.mark.asyncio
    async def test_empty_notes_graceful_handling(self):
        """Test that empty notes list is handled gracefully"""
        notes = []
        chord = ChordEvent(
            time=0.0,
            duration=1.0,
            chord="Cmaj7",
            confidence=0.9,
            root="C",
            quality="maj7"
        )

        voicing = await analyze_voicing(notes, chord)

        # Should return None or handle gracefully (not crash)
        assert voicing is None or len(voicing.notes) == 0, \
            "Empty notes should return None or empty voicing"

    @pytest.mark.asyncio
    async def test_single_note_handling(self):
        """Test handling of single note (edge case)"""
        notes = [
            Note(pitch=60, time=0.0, duration=1.0, velocity=80, hand="left"),
        ]
        chord = ChordEvent(
            time=0.0,
            duration=1.0,
            chord="C",
            confidence=0.9,
            root="C",
            quality="major"
        )

        voicing = await analyze_voicing(notes, chord)

        # Single note should be low complexity
        if voicing:
            assert voicing.complexity_score < 0.3, \
                f"Single note should be very low complexity, got {voicing.complexity_score}"

    @pytest.mark.asyncio
    async def test_octaves_only_handling(self):
        """Test handling of octaves (two notes, same pitch class)"""
        notes = [
            Note(pitch=60, time=0.0, duration=1.0, velocity=80, hand="left"),  # C4
            Note(pitch=72, time=0.0, duration=1.0, velocity=80, hand="right"),  # C5
        ]
        chord = ChordEvent(
            time=0.0,
            duration=1.0,
            chord="C",
            confidence=0.9,
            root="C",
            quality="major"
        )

        voicing = await analyze_voicing(notes, chord)

        if voicing:
            assert voicing.width_semitones == 12, "Octave should span 12 semitones"
            assert voicing.complexity_score < 0.4, \
                "Octaves should be relatively simple, got {voicing.complexity_score}"


class TestVoiceLeadingAnalysis:
    """Test voice leading analysis across chord progressions"""

    @pytest.mark.asyncio
    async def test_smooth_voice_leading(self):
        """Test detection of smooth voice leading (minimal voice movement)"""
        # Cmaj7 to Dm7: Smooth voice leading
        # Cmaj7: C, E, G, B → Dm7: D, F, A, C
        # Voice movement: C→D (2), E→F (1), G→A (2), B→C (1) = average 1.5 semitones

        notes = [
            # Cmaj7
            Note(pitch=60, time=0.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=64, time=0.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=67, time=0.0, duration=1.0, velocity=80, hand="right"),
            Note(pitch=71, time=0.0, duration=1.0, velocity=80, hand="right"),
            # Dm7
            Note(pitch=62, time=1.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=65, time=1.0, duration=1.0, velocity=80, hand="left"),
            Note(pitch=69, time=1.0, duration=1.0, velocity=80, hand="right"),
            Note(pitch=72, time=1.0, duration=1.0, velocity=80, hand="right"),
        ]

        chords = [
            ChordEvent(time=0.0, duration=1.0, chord="Cmaj7", confidence=0.9, root="C", quality="maj7"),
            ChordEvent(time=1.0, duration=1.0, chord="Dm7", confidence=0.9, root="D", quality="m7"),
        ]

        voicings = await analyze_all_voicings(notes, chords)

        # Voice leading should be smooth (small intervals between voices)
        assert len(voicings) == 2, "Should analyze both chords"

        # Check that voicings are close in register (good voice leading)
        avg_pitch_1 = sum(voicings[0].notes) / len(voicings[0].notes)
        avg_pitch_2 = sum(voicings[1].notes) / len(voicings[1].notes)

        assert abs(avg_pitch_1 - avg_pitch_2) < 5, \
            f"Voice leading should be smooth, average pitch change: {abs(avg_pitch_1 - avg_pitch_2)}"
