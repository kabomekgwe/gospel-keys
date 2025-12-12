# Gospel Keys Backend API

A FastAPI-based service for piano transcription from YouTube URLs or uploaded audio files.

## Features

- **YouTube Transcription**: Download and transcribe piano from YouTube videos
- **File Upload**: Upload audio/video files for transcription
- **Piano Isolation**: Use Demucs source separation to isolate piano from mixes
- **MIDI Output**: Generate MIDI files from audio transcription using Spotify's basic-pitch
- **Chord Detection**: Detect gospel chords using chromagram analysis
- **Job Management**: Track transcription progress with async job system

## Quick Start

### Prerequisites

Install system dependencies:

```bash
# macOS
brew install ffmpeg

# The Python packages (demucs, basic-pitch) will be installed via uv
```

### Installation

```bash
# Install dependencies
uv sync

# Copy environment template (optional)
cp .env.example .env
```

### Start the Development Server

```bash
uv run fastapi dev app/main.py
```

Visit:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

### Transcription

- `POST /api/v1/transcribe/url` - Start transcription from YouTube URL
- `POST /api/v1/transcribe/upload` - Start transcription from uploaded file
- `GET /api/v1/transcribe/{job_id}` - Get job status and progress
- `GET /api/v1/transcribe/{job_id}/result` - Get full transcription result

### Job Management

- `GET /api/v1/jobs` - List all jobs
- `DELETE /api/v1/jobs/{job_id}` - Cancel job
- `DELETE /api/v1/jobs/{job_id}/result` - Delete job and files

### Health

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system health

## Project Structure

```
app/
├── main.py                 # FastAPI application
├── core/
│   └── config.py          # Configuration and settings
├── api/routes/
│   ├── health.py          # Health check endpoints
│   ├── transcribe.py      # Transcription endpoints
│   └── jobs.py            # Job management endpoints
├── schemas/
│   └── transcription.py   # Pydantic data models
├── services/
│   └── transcription.py   # Business logic orchestration
└── pipeline/
    ├── downloader.py      # YouTube download (yt-dlp)
    ├── audio_extractor.py # Audio extraction (ffmpeg)
    ├── source_separator.py # Piano isolation (demucs)
    ├── midi_converter.py  # MIDI transcription (basic-pitch)
    └── chord_detector.py  # Chord detection (librosa)
```

## Example Usage

### Transcribe YouTube Video

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "options": {
      "isolate_piano": true,
      "detect_chords": true,
      "detect_tempo": true,
      "detect_key": true
    }
  }'
```

### Check Job Status

```bash
curl "http://localhost:8000/api/v1/transcribe/{job_id}"
```

### Download MIDI File

After job completes, use the `midi_url` from the result:
```bash
curl "http://localhost:8000/files/{job_id}/transcription.mid" -o output.mid
```

## Development

### Run Tests

```bash
uv run pytest tests/
```

### Code Quality

```bash
uv run ruff check .
uv run ruff format .
```

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Architecture Documentation](../architecture.md)
- [Flow Diagrams](../flow%20idagrams.md)

