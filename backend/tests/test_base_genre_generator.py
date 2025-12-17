"""
Unit tests for base_genre_generator.py

Tests the BaseGenreGenerator abstract class and template method pattern.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from app.services.base_genre_generator import BaseGenreGenerator


# Concrete implementation for testing
class TestGenreGenerator(BaseGenreGenerator):
    """Concrete test implementation of BaseGenreGenerator."""

    def _get_style_context(self, complexity: int = 5, style: str = "") -> str:
        return f"Test genre style context (complexity={complexity}, style={style})"

    def _get_default_progression(self, key: str):
        return [f"{key}maj7", f"{key}7"]

    def get_status(self):
        return {
            "gemini_available": self.gemini_model is not None,
            "ready": True
        }


class TestBaseGenreGeneratorInit:
    """Test initialization of BaseGenreGenerator."""

    @patch('app.services.base_genre_generator.settings')
    def test_init_without_gemini(self, mock_settings):
        """Should initialize without Gemini if API key missing."""
        mock_settings.google_api_key = None

        mock_arranger_class = Mock()
        mock_arranger_class.return_value = Mock()

        generator = TestGenreGenerator(
            genre_name="Test",
            arranger_class=mock_arranger_class,
            request_schema=Mock,
            response_schema=Mock,
            status_schema=Mock,
            default_tempo=120,
            output_subdir="test_output"
        )

        assert generator.gemini_model is None
        assert generator.genre_name == "Test"
        assert generator.default_tempo == 120
        assert generator.output_subdir == "test_output"

    @patch('app.services.base_genre_generator.genai.GenerativeModel')
    @patch('app.services.base_genre_generator.settings')
    def test_init_with_gemini(self, mock_settings, mock_gemini_model):
        """Should initialize Gemini if API key present."""
        mock_settings.google_api_key = "test_key"

        mock_arranger_class = Mock()
        mock_arranger_class.return_value = Mock()

        generator = TestGenreGenerator(
            genre_name="Test",
            arranger_class=mock_arranger_class,
            request_schema=Mock,
            response_schema=Mock,
            status_schema=Mock
        )

        assert generator.gemini_model is not None
        mock_gemini_model.assert_called_once_with('gemini-1.5-flash')

    @patch('app.services.base_genre_generator.settings')
    def test_init_arranger_failure_raises(self, mock_settings):
        """Should raise if arranger initialization fails."""
        mock_settings.google_api_key = None

        mock_arranger_class = Mock()
        mock_arranger_class.side_effect = Exception("Arranger failed")

        with pytest.raises(Exception, match="Arranger failed"):
            TestGenreGenerator(
                genre_name="Test",
                arranger_class=mock_arranger_class,
                request_schema=Mock,
                response_schema=Mock,
                status_schema=Mock
            )


class TestGenerationPipeline:
    """Test the main generation pipeline (template method)."""

    @pytest.fixture
    def generator(self):
        """Create test generator with mocked dependencies."""
        with patch('app.services.base_genre_generator.settings') as mock_settings:
            mock_settings.google_api_key = None

            mock_arranger_class = Mock()
            mock_arranger = Mock()
            mock_arranger.arrange_progression.return_value = self._create_mock_arrangement()
            mock_arranger_class.return_value = mock_arranger

            gen = TestGenreGenerator(
                genre_name="Test",
                arranger_class=mock_arranger_class,
                request_schema=Mock,
                response_schema=Mock,
                status_schema=Mock
            )

            return gen

    def _create_mock_arrangement(self):
        """Create a mock arrangement object."""
        arrangement = Mock()
        arrangement.tempo = 120
        arrangement.key = "C"
        arrangement.time_signature = (4, 4)
        arrangement.total_bars = 4
        arrangement.left_hand_notes = [Mock()]
        arrangement.right_hand_notes = [Mock()]
        arrangement.total_duration_seconds = 10.0
        arrangement.application = "standard"
        arrangement.get_all_notes.return_value = []
        return arrangement

    @pytest.mark.asyncio
    @patch('app.services.base_genre_generator.export_to_midi')
    async def test_generate_without_gemini(self, mock_export, generator):
        """Should generate using fallback when Gemini unavailable."""
        mock_export.return_value = (Path("/tmp/test.mid"), "base64data")

        request = Mock()
        request.include_progression = True
        request.description = "Test in C major at 120 bpm"
        request.key = None
        request.tempo = None
        request.num_bars = 4
        request.complexity = 5
        request.style = "test"
        request.ai_percentage = 0.0

        response = await generator.generate_arrangement(request)

        assert response.success is True
        assert response.midi_file_path == "/tmp/test.mid"
        assert response.midi_base64 == "base64data"

    @pytest.mark.asyncio
    @patch('app.services.base_genre_generator.export_to_midi')
    @patch('app.services.base_genre_generator.parse_json_from_response')
    async def test_generate_with_gemini(self, mock_parse_json, mock_export, generator):
        """Should generate using Gemini when available."""
        # Mock Gemini model
        generator.gemini_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"key": "C", "tempo": 120, "chords": []}'
        generator.gemini_model.generate_content = Mock(return_value=mock_response)

        mock_parse_json.return_value = {
            "key": "C",
            "tempo": 120,
            "chords": [
                {"symbol": "Cmaj7", "function": "I", "notes": ["C", "E", "G", "B"], "comment": "Tonic"}
            ]
        }

        mock_export.return_value = (Path("/tmp/test.mid"), "base64data")

        request = Mock()
        request.include_progression = True
        request.description = "Happy song"
        request.key = None
        request.tempo = None
        request.num_bars = 4
        request.complexity = 5
        request.style = "test"
        request.ai_percentage = 0.0

        response = await generator.generate_arrangement(request)

        assert response.success is True
        generator.gemini_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_handles_errors_gracefully(self, generator):
        """Should return error response on failure."""
        # Force an error
        generator.arranger.arrange_progression.side_effect = Exception("Test error")

        request = Mock()
        request.include_progression = False
        request.description = "Test"
        request.key = "C"
        request.tempo = 120
        request.complexity = 5
        request.style = "test"
        request.ai_percentage = 0.0

        response = await generator.generate_arrangement(request)

        assert response.success is False
        assert "Test error" in response.error
        assert response.generation_method == "failed"


class TestProgressionGeneration:
    """Test chord progression generation."""

    @pytest.fixture
    def generator_with_gemini(self):
        """Create generator with mocked Gemini."""
        with patch('app.services.base_genre_generator.settings') as mock_settings:
            mock_settings.google_api_key = "test_key"

            with patch('app.services.base_genre_generator.genai.GenerativeModel') as mock_model:
                mock_arranger_class = Mock()
                mock_arranger_class.return_value = Mock()

                gen = TestGenreGenerator(
                    genre_name="Test",
                    arranger_class=mock_arranger_class,
                    request_schema=Mock,
                    response_schema=Mock,
                    status_schema=Mock,
                    default_tempo=90
                )

                return gen

    @pytest.mark.asyncio
    @patch('app.services.base_genre_generator.parse_json_from_response')
    async def test_gemini_progression_generation(self, mock_parse_json, generator_with_gemini):
        """Should generate progression using Gemini."""
        mock_response = Mock()
        mock_response.text = '{"key": "D", "tempo": 100, "chords": []}'
        generator_with_gemini.gemini_model.generate_content = Mock(return_value=mock_response)

        mock_parse_json.return_value = {
            "key": "D",
            "tempo": 100,
            "chords": [
                {"symbol": "Dmaj7", "function": "I", "notes": ["D", "F#", "A", "C#"], "comment": "Tonic"}
            ]
        }

        chords, key, tempo, analysis = await generator_with_gemini._generate_progression_with_gemini(
            "Happy song in D",
            None,
            None,
            4
        )

        assert key == "D"
        assert tempo == 100
        assert chords == ["Dmaj7"]
        assert len(analysis) == 1

    @pytest.mark.asyncio
    async def test_gemini_uses_genre_context(self, generator_with_gemini):
        """Should include genre-specific context in prompt."""
        mock_response = Mock()
        mock_response.text = '{"key": "C", "tempo": 120, "chords": []}'
        generator_with_gemini.gemini_model.generate_content = Mock(return_value=mock_response)

        with patch('app.services.base_genre_generator.parse_json_from_response') as mock_parse:
            mock_parse.return_value = {"key": "C", "tempo": 120, "chords": []}

            await generator_with_gemini._generate_progression_with_gemini(
                "Test song",
                None,
                None,
                4
            )

            # Check that style context was included
            call_args = generator_with_gemini.gemini_model.generate_content.call_args
            prompt = call_args[0][0]
            assert "Test genre style context" in prompt


class TestFallbackParsing:
    """Test fallback description parsing."""

    @pytest.fixture
    def generator(self):
        """Create test generator."""
        with patch('app.services.base_genre_generator.settings') as mock_settings:
            mock_settings.google_api_key = None

            mock_arranger_class = Mock()
            mock_arranger_class.return_value = Mock()

            return TestGenreGenerator(
                genre_name="Test",
                arranger_class=mock_arranger_class,
                request_schema=Mock,
                response_schema=Mock,
                status_schema=Mock,
                default_tempo=100
            )

    @patch('app.services.base_genre_generator.parse_description_fallback')
    def test_fallback_uses_genre_defaults(self, mock_fallback, generator):
        """Should use genre-specific default progression."""
        mock_fallback.return_value = (["Cmaj7", "C7"], "C", 120)

        chords, key, tempo = generator._parse_description_with_fallback(
            "Test song",
            None,
            None
        )

        # Check that genre's default progression was passed
        call_args = mock_fallback.call_args
        assert call_args[0][3] == ["Cmaj7", "C7"]  # From _get_default_progression
        assert call_args[0][4] == 100  # default_tempo


class TestArrangementCreation:
    """Test arrangement creation with genre arrangers."""

    @pytest.fixture
    def generator(self):
        """Create test generator with mock arranger."""
        with patch('app.services.base_genre_generator.settings') as mock_settings:
            mock_settings.google_api_key = None

            mock_arranger_class = Mock()
            mock_arranger = Mock()
            mock_arranger_class.return_value = mock_arranger

            gen = TestGenreGenerator(
                genre_name="Test",
                arranger_class=mock_arranger_class,
                request_schema=Mock,
                response_schema=Mock,
                status_schema=Mock
            )

            return gen

    def test_arrangement_calls_arranger(self, generator):
        """Should call arranger with correct parameters."""
        request = Mock()
        request.application = Mock()
        request.application.value = "worship"

        generator._create_arrangement(
            chords=["Cmaj7", "Dm7"],
            key="C",
            tempo=120,
            request=request
        )

        generator.arranger.arrange_progression.assert_called_once()
        call_kwargs = generator.arranger.arrange_progression.call_args[1]
        assert call_kwargs["chords"] == ["Cmaj7", "Dm7"]
        assert call_kwargs["key"] == "C"
        assert call_kwargs["bpm"] == 120
        assert call_kwargs["application"] == "worship"


class TestResponseBuilding:
    """Test response construction."""

    @pytest.fixture
    def generator(self):
        """Create test generator."""
        with patch('app.services.base_genre_generator.settings') as mock_settings:
            mock_settings.google_api_key = None

            mock_arranger_class = Mock()
            mock_arranger_class.return_value = Mock()

            return TestGenreGenerator(
                genre_name="Test",
                arranger_class=mock_arranger_class,
                request_schema=Mock,
                response_schema=Mock,
                status_schema=Mock
            )

    @patch('app.services.base_genre_generator.get_notes_preview')
    def test_success_response_structure(self, mock_preview, generator):
        """Should build proper success response."""
        mock_preview.return_value = []

        arrangement = Mock()
        arrangement.tempo = 120
        arrangement.key = "C"
        arrangement.time_signature = (4, 4)
        arrangement.total_bars = 4
        arrangement.left_hand_notes = [1, 2]
        arrangement.right_hand_notes = [3, 4, 5]
        arrangement.total_duration_seconds = 10.5
        arrangement.application = "standard"

        request = Mock()
        request.include_progression = True
        request.complexity = 5
        request.style = "test"
        request.ai_percentage = 0.0

        response = generator._build_success_response(
            midi_path=Path("/tmp/test.mid"),
            midi_base64="base64data",
            arrangement=arrangement,
            analysis=[],
            request=request
        )

        assert response.success is True
        assert response.midi_file_path == "/tmp/test.mid"
        assert response.midi_base64 == "base64data"
        assert response.arrangement_info["tempo"] == 120
        assert response.arrangement_info["key"] == "C"
        assert response.arrangement_info["total_notes"] == 5

    def test_error_response_structure(self, generator):
        """Should build proper error response."""
        response = generator._build_error_response("Test error message")

        assert response.success is False
        assert response.error == "Test error message"
        assert response.generation_method == "failed"


class TestGenerationMethod:
    """Test generation method determination."""

    @pytest.fixture
    def generator(self):
        """Create test generator."""
        with patch('app.services.base_genre_generator.settings') as mock_settings:
            mock_settings.google_api_key = None

            mock_arranger_class = Mock()
            mock_arranger_class.return_value = Mock()

            return TestGenreGenerator(
                genre_name="Test",
                arranger_class=mock_arranger_class,
                request_schema=Mock,
                response_schema=Mock,
                status_schema=Mock
            )

    def test_gemini_and_rules(self, generator):
        """Should return 'gemini+rules' when both used."""
        generator.gemini_model = Mock()

        request = Mock()
        request = Mock()
        request.include_progression = True
        request.complexity = 5
        request.style = "test"
        request.ai_percentage = 0.0

        method = generator._determine_generation_method(request)
        assert method == "gemini+rules"

    def test_rules_only(self, generator):
        """Should return 'rules-only' when no AI."""
        generator.gemini_model = None

        request = Mock()
        request = Mock()
        request.include_progression = False
        request.complexity = 5
        request.style = "test"
        request.ai_percentage = 0.0

        method = generator._determine_generation_method(request)
        assert method == "rules-only"


# Integration test
class TestBaseGeneratorIntegration:
    """Test base generator with realistic scenarios."""

    @pytest.mark.asyncio
    @patch('app.services.base_genre_generator.export_to_midi')
    @patch('app.services.base_genre_generator.settings')
    async def test_full_generation_flow(self, mock_settings, mock_export):
        """Test complete generation from request to response."""
        mock_settings.google_api_key = None

        # Create mock arranger
        mock_arranger_class = Mock()
        mock_arranger = Mock()
        mock_arrangement = Mock()
        mock_arrangement.tempo = 120
        mock_arrangement.key = "C"
        mock_arrangement.time_signature = (4, 4)
        mock_arrangement.total_bars = 4
        mock_arrangement.left_hand_notes = []
        mock_arrangement.right_hand_notes = []
        mock_arrangement.total_duration_seconds = 10.0
        mock_arrangement.application = "standard"
        mock_arrangement.get_all_notes.return_value = []

        mock_arranger.arrange_progression.return_value = mock_arrangement
        mock_arranger_class.return_value = mock_arranger

        mock_export.return_value = (Path("/tmp/test.mid"), "YmFzZTY0ZGF0YQ==")

        # Create generator
        generator = TestGenreGenerator(
            genre_name="Test",
            arranger_class=mock_arranger_class,
            request_schema=Mock,
            response_schema=Mock,
            status_schema=Mock
        )

        # Create request
        request = Mock()
        request.include_progression = False
        request.description = "Calm song in C at 120 bpm"
        request.key = "C"
        request.tempo = 120
        request.num_bars = 4
        request.application = Mock()
        request.application.value = "standard"
        request.complexity = 5
        request.style = "test"
        request.ai_percentage = 0.0

        # Generate
        response = await generator.generate_arrangement(request)

        # Verify
        assert response.success is True
        assert response.midi_file_path == "/tmp/test.mid"
        assert response.midi_base64 == "YmFzZTY0ZGF0YQ=="
        assert mock_arranger.arrange_progression.called
