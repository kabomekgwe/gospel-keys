"""
Unit tests for generator_utils.py

Tests all shared utility functions used across genre generators.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from app.services.generator_utils import (
    parse_json_from_response,
    note_to_midi,
    export_to_midi,
    get_notes_preview,
    parse_description_fallback
)


class TestParseJsonFromResponse:
    """Test JSON parsing from LLM responses."""

    def test_parse_json_in_code_block(self):
        """Should extract JSON from markdown code blocks."""
        response = '''Here's the result:
        ```json
        {"key": "C", "tempo": 120}
        ```
        '''
        result = parse_json_from_response(response)
        assert result == {"key": "C", "tempo": 120}

    def test_parse_raw_json(self):
        """Should parse raw JSON without code blocks."""
        response = '{"key": "D", "tempo": 90}'
        result = parse_json_from_response(response)
        assert result == {"key": "D", "tempo": 90}

    def test_parse_json_embedded_in_text(self):
        """Should extract JSON object from surrounding text."""
        response = 'Here is the data: {"key": "E", "tempo": 110} and that\'s it.'
        result = parse_json_from_response(response)
        assert result == {"key": "E", "tempo": 110}

    def test_parse_json_with_newlines(self):
        """Should handle JSON with internal newlines."""
        response = '''```json
        {
          "key": "F",
          "tempo": 100,
          "chords": ["Fmaj7", "Gm7"]
        }
        ```'''
        result = parse_json_from_response(response)
        assert result["key"] == "F"
        assert result["tempo"] == 100
        assert len(result["chords"]) == 2

    def test_invalid_json_raises_error(self):
        """Should raise ValueError for invalid JSON."""
        response = "This is not JSON at all"
        with pytest.raises(ValueError, match="Could not parse JSON"):
            parse_json_from_response(response)

    def test_empty_response_raises_error(self):
        """Should raise ValueError for empty response."""
        with pytest.raises(ValueError):
            parse_json_from_response("")


class TestNoteToMidi:
    """Test note name to MIDI number conversion."""

    def test_middle_c(self):
        """C4 should be MIDI 60."""
        assert note_to_midi("C", 4) == 60
        assert note_to_midi("C4") == 60

    def test_sharps(self):
        """Sharp notes should work correctly."""
        assert note_to_midi("C#", 4) == 61
        assert note_to_midi("C#4") == 61
        assert note_to_midi("F#", 4) == 66

    def test_flats(self):
        """Flat notes should map to same as sharps."""
        assert note_to_midi("Db", 4) == 61  # Same as C#
        assert note_to_midi("Eb", 4) == 63  # Same as D#
        assert note_to_midi("Bb", 4) == 70  # Same as A#

    def test_octaves(self):
        """Different octaves should be 12 semitones apart."""
        assert note_to_midi("C", 3) == 48
        assert note_to_midi("C", 4) == 60
        assert note_to_midi("C", 5) == 72
        assert note_to_midi("C5") == 72

    def test_all_notes(self):
        """All 12 chromatic notes should work."""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        expected = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]

        for note, expected_midi in zip(notes, expected):
            assert note_to_midi(note, 4) == expected_midi

    def test_default_octave(self):
        """Should use default octave when not specified."""
        assert note_to_midi("C") == 60  # Default octave 4
        assert note_to_midi("A", 5) == 81  # Explicit octave

    def test_invalid_note_returns_default(self):
        """Invalid note should return middle C (60)."""
        assert note_to_midi("X") == 60
        assert note_to_midi("Z9") == 60


class TestExportToMidi:
    """Test MIDI export with base64 encoding."""

    @patch('app.services.generator_utils.export_enhanced_midi')
    @patch('builtins.open', new_callable=mock_open, read_data=b'MIDI_DATA')
    @patch('app.services.generator_utils.settings')
    def test_export_creates_directory(self, mock_settings, mock_file, mock_export):
        """Should create output directory if it doesn't exist."""
        mock_settings.OUTPUTS_DIR = Path("/tmp/outputs")

        # Mock arrangement
        arrangement = Mock()
        arrangement.key = "C"
        arrangement.tempo = 120

        with patch('pathlib.Path.mkdir') as mock_mkdir:
            export_to_midi(arrangement, "test_subdir", "test")
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('app.services.generator_utils.export_enhanced_midi')
    @patch('builtins.open', new_callable=mock_open, read_data=b'MIDI_DATA')
    @patch('app.services.generator_utils.settings')
    def test_export_returns_path_and_base64(self, mock_settings, mock_file, mock_export):
        """Should return MIDI path and base64-encoded data."""
        mock_settings.OUTPUTS_DIR = Path("/tmp/outputs")

        arrangement = Mock()
        arrangement.key = "C"
        arrangement.tempo = 120

        midi_path, midi_base64 = export_to_midi(arrangement, "test", "prefix")

        assert isinstance(midi_path, Path)
        assert isinstance(midi_base64, str)
        assert midi_base64  # Should not be empty

    @patch('app.services.generator_utils.export_enhanced_midi')
    @patch('app.services.generator_utils.settings')
    def test_export_filename_format(self, mock_settings, mock_export):
        """Should generate filename with correct format."""
        mock_settings.OUTPUTS_DIR = Path("/tmp/outputs")

        arrangement = Mock()
        arrangement.key = "Dm"
        arrangement.tempo = 90

        with patch('builtins.open', mock_open(read_data=b'test')):
            midi_path, _ = export_to_midi(arrangement, "blues", "blues")

            filename = midi_path.name
            assert "blues" in filename
            assert "Dm" in filename
            assert "90bpm" in filename
            assert filename.endswith(".mid")


class TestGetNotesPreview:
    """Test notes preview extraction."""

    def test_extracts_first_bars(self):
        """Should extract notes from first N bars only."""
        # Mock arrangement
        arrangement = Mock()
        arrangement.time_signature = (4, 4)

        # Create notes at different times
        notes = []
        for i in range(20):
            note = Mock()
            note.time = i * 0.5  # Notes every half beat
            note.pitch = 60 + i
            note.duration = 0.5
            note.velocity = 100
            note.hand = "right"
            notes.append(note)

        arrangement.get_all_notes.return_value = notes

        # Get 2 bars (8 beats in 4/4)
        preview = get_notes_preview(arrangement, bars=2)

        # Should only include notes before time 8
        assert len(preview) <= 16  # 8 beats * 2 notes per beat

    def test_limits_to_100_notes(self):
        """Should limit preview to 100 notes max."""
        arrangement = Mock()
        arrangement.time_signature = (4, 4)

        # Create 200 notes in first bar
        notes = []
        for i in range(200):
            note = Mock()
            note.time = 0.1 * i  # All within first bar
            note.pitch = 60
            note.duration = 0.1
            note.velocity = 100
            note.hand = "right"
            notes.append(note)

        arrangement.get_all_notes.return_value = notes

        preview = get_notes_preview(arrangement, bars=4)

        # Should be limited to 100
        assert len(preview) == 100

    def test_creates_midi_note_info_objects(self):
        """Should create proper MIDINoteInfo objects."""
        arrangement = Mock()
        arrangement.time_signature = (4, 4)

        note = Mock()
        note.time = 0.0
        note.pitch = 60
        note.duration = 1.0
        note.velocity = 100
        note.hand = "left"

        arrangement.get_all_notes.return_value = [note]

        preview = get_notes_preview(arrangement, bars=4)

        assert len(preview) == 1
        preview_note = preview[0]
        assert preview_note.pitch == 60
        assert preview_note.time == 0.0
        assert preview_note.duration == 1.0
        assert preview_note.velocity == 100
        assert preview_note.hand == "left"


class TestParseDescriptionFallback:
    """Test fallback description parsing."""

    def test_extracts_key_from_description(self):
        """Should extract key from text."""
        chords, key, tempo = parse_description_fallback(
            "Play something in D major at 120 bpm",
            None,
            None,
            ["Dmaj7", "Em7"],
            120
        )

        assert key == "D"

    def test_extracts_tempo_from_description(self):
        """Should extract tempo from text."""
        chords, key, tempo = parse_description_fallback(
            "A slow ballad in C at 72bpm",
            None,
            None,
            ["Cmaj7"],
            120
        )

        assert tempo == 72

    def test_uses_explicit_key_override(self):
        """Explicit key should override parsed key."""
        chords, key, tempo = parse_description_fallback(
            "Play something in D major",
            "G",  # Explicit override
            None,
            ["Gmaj7"],
            120
        )

        assert key == "G"

    def test_uses_explicit_tempo_override(self):
        """Explicit tempo should override parsed tempo."""
        chords, key, tempo = parse_description_fallback(
            "Fast jazz at 180 bpm",
            None,
            90,  # Explicit override
            ["Cmaj7"],
            120
        )

        assert tempo == 90

    def test_returns_default_chords(self):
        """Should return provided default chords."""
        default_chords = ["Cmaj7", "Dm7", "G7", "Cmaj7"]
        chords, key, tempo = parse_description_fallback(
            "Play something nice",
            None,
            None,
            default_chords,
            120
        )

        assert chords == default_chords

    def test_defaults_when_nothing_found(self):
        """Should use defaults when no key/tempo in description."""
        chords, key, tempo = parse_description_fallback(
            "Just play something",
            None,
            None,
            ["Cmaj7"],
            90
        )

        assert key == "C"  # Default
        assert tempo == 90  # From default_tempo parameter

    def test_handles_sharp_and_flat_keys(self):
        """Should recognize sharp and flat keys."""
        # Sharp key
        _, key, _ = parse_description_fallback(
            "Something in F# major",
            None, None, ["F#maj7"], 120
        )
        assert key == "F#"

        # Flat key
        _, key, _ = parse_description_fallback(
            "Something in Bb minor",
            None, None, ["Bbm7"], 120
        )
        assert key == "Bb"

    def test_handles_minor_keys(self):
        """Should recognize minor key indicators."""
        _, key, _ = parse_description_fallback(
            "A sad song in A minor",
            None, None, ["Am7"], 120
        )
        assert key == "A"


# Integration test
class TestUtilsIntegration:
    """Test utilities working together."""

    def test_full_pipeline(self):
        """Test a realistic usage scenario."""
        # 1. Parse JSON from LLM
        llm_response = '''```json
        {
            "key": "C",
            "tempo": 120,
            "chords": [
                {"symbol": "Cmaj7", "notes": ["C", "E", "G", "B"]}
            ]
        }
        ```'''

        data = parse_json_from_response(llm_response)
        assert data["key"] == "C"
        assert data["tempo"] == 120

        # 2. Convert notes to MIDI
        notes = data["chords"][0]["notes"]
        midi_notes = [note_to_midi(note, 4) for note in notes]
        assert midi_notes == [60, 64, 67, 71]  # C, E, G, B

        # 3. Fallback parsing would work too
        chords, key, tempo = parse_description_fallback(
            "Blues in C at 90 bpm",
            None, None,
            ["C7", "F7", "G7"],
            120
        )
        assert key == "C"
        assert tempo == 90
