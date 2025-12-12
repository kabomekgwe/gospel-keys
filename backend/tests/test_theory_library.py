"""
Unit tests for Music Theory Library (Phase 5A)
"""

import pytest
from app.theory.interval_utils import (
    note_to_semitone,
    semitone_to_note,
    get_interval,
    get_interval_name,
    transpose,
    is_enharmonic,
    note_to_midi,
    midi_to_note,
)
from app.theory.scale_library import (
    get_scale,
    get_scale_notes,
    list_scales_by_category,
)
from app.theory.chord_library import (
    get_chord_type,
    get_chord_notes,
    parse_chord_symbol,
    list_chords_by_category,
)


class TestIntervalUtils:
    """Tests for interval_utils.py"""

    def test_note_to_semitone_naturals(self):
        assert note_to_semitone("C") == 0
        assert note_to_semitone("D") == 2
        assert note_to_semitone("E") == 4
        assert note_to_semitone("F") == 5
        assert note_to_semitone("G") == 7
        assert note_to_semitone("A") == 9
        assert note_to_semitone("B") == 11

    def test_note_to_semitone_accidentals(self):
        assert note_to_semitone("C#") == 1
        assert note_to_semitone("Db") == 1
        assert note_to_semitone("F#") == 6
        assert note_to_semitone("Gb") == 6
        assert note_to_semitone("Bb") == 10

    def test_note_to_semitone_with_octave(self):
        assert note_to_semitone("C4") == 0
        assert note_to_semitone("A4") == 9

    def test_semitone_to_note(self):
        assert semitone_to_note(0) == "C"
        assert semitone_to_note(1, prefer_sharps=True) == "C#"
        assert semitone_to_note(1, prefer_sharps=False) == "Db"

    def test_get_interval(self):
        # C to G is a perfect 5th (7 semitones)
        assert get_interval("C", "G") == 7
        # C to E is a major 3rd (4 semitones)
        assert get_interval("C", "E") == 4
        # E to C (going up) is a minor 6th (8 semitones)
        assert get_interval("E", "C") == 8

    def test_get_interval_name(self):
        assert get_interval_name(0) == "P1"
        assert get_interval_name(4) == "M3"
        assert get_interval_name(7) == "P5"
        assert get_interval_name(10) == "m7"
        assert get_interval_name(11) == "M7"

    def test_transpose(self):
        assert transpose("C", 7) == "G"  # Up a 5th
        assert transpose("G", -7) == "C"  # Down a 5th
        assert transpose("F#", 2) == "G#"
        assert transpose("Bb", 5, prefer_sharps=False) == "Eb"

    def test_is_enharmonic(self):
        assert is_enharmonic("C#", "Db")
        assert is_enharmonic("F#", "Gb")
        assert not is_enharmonic("C", "D")

    def test_note_to_midi(self):
        assert note_to_midi("C", 4) == 60  # Middle C
        assert note_to_midi("A", 4) == 69  # A440
        assert note_to_midi("C4") == 60

    def test_midi_to_note(self):
        assert midi_to_note(60) == "C4"
        assert midi_to_note(69) == "A4"


class TestScaleLibrary:
    """Tests for scale_library.py"""

    def test_get_scale(self):
        major = get_scale("major")
        assert major.name == "Ionian"
        assert major.intervals == (0, 2, 4, 5, 7, 9, 11)

        dorian = get_scale("dorian")
        assert dorian.intervals == (0, 2, 3, 5, 7, 9, 10)

    def test_get_scale_notes(self):
        c_major = get_scale_notes("C", "major")
        assert c_major == ["C", "D", "E", "F", "G", "A", "B"]

        a_minor = get_scale_notes("A", "minor")
        assert a_minor == ["A", "B", "C", "D", "E", "F", "G"]

    def test_get_scale_notes_with_sharps(self):
        g_major = get_scale_notes("G", "major")
        assert "F#" in g_major

    def test_blues_scale(self):
        c_blues = get_scale_notes("C", "blues")
        # C blues: C, Eb, F, F#/Gb, G, Bb
        assert len(c_blues) == 6
        assert "C" in c_blues

    def test_list_scales_by_category(self):
        modes = list_scales_by_category("mode")
        assert len(modes) >= 7  # At least 7 modes of major scale

    def test_invalid_scale(self):
        with pytest.raises(ValueError):
            get_scale("nonexistent_scale")


class TestChordLibrary:
    """Tests for chord_library.py"""

    def test_get_chord_type_major(self):
        major = get_chord_type("")
        assert major.name == "Major Triad"
        assert major.intervals == (0, 4, 7)

    def test_get_chord_type_seventh(self):
        maj7 = get_chord_type("maj7")
        assert maj7.intervals == (0, 4, 7, 11)

        m7 = get_chord_type("m7")
        assert m7.intervals == (0, 3, 7, 10)

        dom7 = get_chord_type("7")
        assert dom7.intervals == (0, 4, 7, 10)

    def test_get_chord_notes(self):
        c_major = get_chord_notes("C", "")
        assert c_major == ["C", "E", "G"]

        c_maj7 = get_chord_notes("C", "maj7")
        assert c_maj7 == ["C", "E", "G", "B"]

        d_m7 = get_chord_notes("D", "m7")
        assert d_m7 == ["D", "F", "A", "C"]

    def test_parse_chord_symbol(self):
        root, quality, bass = parse_chord_symbol("Cmaj7")
        assert root == "C"
        assert quality == "maj7"
        assert bass is None

        root, quality, bass = parse_chord_symbol("F#m7")
        assert root == "F#"
        assert quality == "m7"

        root, quality, bass = parse_chord_symbol("G/B")
        assert root == "G"
        assert quality == ""
        assert bass == "B"

    def test_list_chords_by_category(self):
        triads = list_chords_by_category("triad")
        assert len(triads) >= 6  # Major, minor, dim, aug, sus2, sus4

        sevenths = list_chords_by_category("seventh")
        assert len(sevenths) >= 7

    def test_altered_chords(self):
        hendrix = get_chord_type("7#9")
        assert hendrix.name == "Dominant 7 sharp 9"
        assert 15 in hendrix.intervals  # #9 is 15 semitones

    def test_invalid_chord(self):
        with pytest.raises(ValueError):
            get_chord_type("nonexistent")


class TestTheoryIntegration:
    """Integration tests combining multiple modules"""

    def test_ii_v_i_chord_notes(self):
        """Test that we can generate ii-V-I chords in C"""
        ii = get_chord_notes("D", "m7")   # Dm7
        v = get_chord_notes("G", "7")      # G7
        i = get_chord_notes("C", "maj7")   # Cmaj7

        assert ii == ["D", "F", "A", "C"]
        assert v == ["G", "B", "D", "F"]
        assert i == ["C", "E", "G", "B"]

    def test_scale_chord_relationship(self):
        """Verify that chord tones are in the parent scale"""
        c_major_scale = get_scale_notes("C", "major")
        c_major_chord = get_chord_notes("C", "")

        for note in c_major_chord:
            assert note in c_major_scale

    def test_transpose_chord_progression(self):
        """Test transposing a chord progression"""
        # ii-V-I roots in C: D, G, C
        roots_in_c = ["D", "G", "C"]
        # Transpose up a whole step to D
        roots_in_d = [transpose(r, 2) for r in roots_in_c]
        assert roots_in_d == ["E", "A", "D"]
