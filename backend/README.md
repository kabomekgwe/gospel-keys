# Gospel Keys Backend API

A FastAPI-based service for piano transcription from YouTube URLs or uploaded audio files.

## Features

- **YouTube Transcription**: Download and transcribe piano from YouTube videos
- **File Upload**: Upload audio/video files for transcription
- **Piano Isolation**: Use Demucs source separation to isolate piano from mixes
- **MIDI Output**: Generate MIDI files from audio transcription using Spotify's basic-pitch
- **Chord Detection**: Detect gospel chords using chromagram analysis
- 🎹 Piano transcription from YouTube URLs or uploaded files
- 🎵 MIDI generation with note detection
- 🎼 Chord detection and analysis  
- 📚 Song library with SQLite database
- ⏱️ Practice mode with time-stretching
- ✂️ Snippet extraction for practice sections
- 📝 Annotation system for theory notes
- 📤 Export to MusicXML and quantized MIDI
- 🐳 Docker support for easy deployment

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd youtube-transcript/backend

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Option 2: Local Development

**Requirements:**
- Python 3.10 or 3.11 (NOT 3.12 due to tensorflow dependency)
- ffmpeg installed (`brew install ffmpeg` on macOS)
- uv package manager

```bash
# Install dependencies
~/.local/bin/uv sync

# Run development server
~/.local/bin/uv run uvicorn app.main:app --reload

# API available at http://localhost:8000
```

## Docker Commands

```bash
# Development (with hot-reload)
docker-compose up

# Production (with monitoring)
docker-compose -f docker-compose.prod.yml up -d

# Build image
docker build -t gospel-keys-api .

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Clean up volumes
docker-compose down -v
```

## Monitoring (Production)

When using `docker-compose.prod.yml`:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
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

