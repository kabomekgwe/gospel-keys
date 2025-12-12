import pytest
from httpx import AsyncClient
import uuid
from unittest.mock import patch, MagicMock
from app.database.models import Song, SongChord
from app.main import app

# Mock Chords Data
MOCK_CHORDS = [
    {"root": "D", "quality": "m7", "start": 0.0, "end": 2.0},
    {"root": "G", "quality": "7", "start": 2.0, "end": 4.0},
    {"root": "C", "quality": "maj7", "start": 4.0, "end": 8.0}
]

import pytest_asyncio

@pytest_asyncio.fixture
async def analysis_song_id(async_client, db_session):
    """Create a mock song with chords for analysis testing"""
    song_id = str(uuid.uuid4())
    song = Song(
        id=song_id,
        title="Test Jazz Standard",
        duration=120.0,
        audio_file_path="/tmp/test_audio.wav",
        tempo=120.0
    )
    db_session.add(song)
    
    # Add chords (ii-V-I in C)
    for c in MOCK_CHORDS:
        chord = SongChord(
            song_id=song_id,
            root=c["root"],
            quality=c["quality"],
            chord=f"{c['root']}{c['quality']}",
            time=c["start"],
            duration=c["end"] - c["start"]
        )
        db_session.add(chord)
        
    await db_session.commit()
    return song_id

@pytest.mark.asyncio
async def test_jazz_patterns_endpoint(async_client, analysis_song_id):
    """Test ii-V-I pattern detection endpoint"""
    response = await async_client.post(
        f"/api/v1/analyze/jazz-patterns?song_id={analysis_song_id}"
    )
    if response.status_code != 200:
        print(f"\nDEBUG ERROR RESPONSE: {response.text}\n")
    assert response.status_code == 200
    data = response.json()
    
    assert "ii_v_i_progressions" in data
    # Should detect at least one ii-V-I
    assert len(data["ii_v_i_progressions"]) > 0
    assert data["ii_v_i_progressions"][0]["key"] == "C"

@pytest.mark.asyncio
async def test_blues_form_endpoint(async_client, analysis_song_id):
    """Test blues form detection endpoint"""
    response = await async_client.post(
        f"/api/v1/analyze/blues-form?song_id={analysis_song_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "form_detection" in data
    assert "rhythm_feel" in data

@pytest.mark.asyncio
async def test_classical_form_endpoint(async_client, analysis_song_id):
    """Test classical form analysis endpoint"""
    response = await async_client.post(
        f"/api/v1/analyze/classical-form?song_id={analysis_song_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "form_suggestion" in data

@pytest.mark.asyncio
async def test_chord_library_endpoint(async_client):
    """Test chord library retrieval"""
    response = await async_client.get("/api/v1/analyze/chord-library?genre=jazz")
    assert response.status_code == 200
    data = response.json()
    assert "chord_templates" in data
    assert "maj7#11" in data["chord_templates"]

@pytest.mark.asyncio
async def test_compare_transcription_endpoint(async_client, analysis_song_id):
    """Test transcription comparison endpoint (mocked)"""
    with patch("app.pipeline.transcription_comparison.compare_transcriptions") as mock_compare:
        mock_compare.return_value = {
            "engine_results": {"basic-pitch": {"note_count": 100}},
            "comparison_metrics": {"agreement_score": 0.85}
        }
        
        # Create dummy audio for validation check
        with open("/tmp/test_audio.wav", "wb") as f:
            f.write(b"dummy audio content")

        response = await async_client.post(
            f"/api/v1/analyze/compare?song_id={analysis_song_id}",
            json=["basic-pitch"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["comparison_metrics"]["agreement_score"] == 0.85

@pytest.mark.asyncio
async def test_pitch_tracking_endpoint_mock(async_client, analysis_song_id):
    """Test CREPE pitch tracking endpoint with mocks"""
    with patch("app.api.routes.analysis.extract_pitch_contour") as mock_crepe:
        # Mock CREPE output
        mock_crepe.return_value = {
            "time": [0.1, 0.2],
            "frequency": [440.0, 442.0],
            "confidence": [0.9, 0.8],
            "notes": ["A4", "A4"]
        }
        
        response = await async_client.post(
            f"/api/v1/analyze/pitch-tracking?song_id={analysis_song_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "pitch_contour" in data
        assert len(data["pitch_contour"]["frequency"]) == 2
