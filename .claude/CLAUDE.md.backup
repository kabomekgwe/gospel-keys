# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gospel Keys / Piano Keys** - Multi-genre piano transcription and analysis platform supporting Gospel, Jazz, Blues, Classical, and Contemporary music. The system processes YouTube videos or uploaded audio files through a sophisticated pipeline to generate MIDI transcriptions, chord analysis, and music theory insights.

**Architecture**: Monorepo with Python FastAPI backend and React TanStack frontend, containerized with Docker.

## Tech Stack

- **Backend**: Python 3.10-3.13, FastAPI, SQLAlchemy, Alembic, uv package manager
- **Frontend**: React 19, TanStack Router (file-based), TanStack Query, Zustand, Tailwind CSS 4
- **Audio Pipeline**: yt-dlp, ffmpeg, Demucs, librosa, pretty-midi, music21
- **AI/ML**: Essentia, MusicPy, PyTorch, Gemini API (music theory analysis)
- **Gospel AI**: MLX (M4 Pro optimized), REMI tokenization, LoRA fine-tuning, Mistral-7B-Instruct
- **Database**: SQLite (dev), async via aiosqlite
- **Testing**: pytest + pytest-asyncio (backend), vitest (frontend), Playwright (e2e)
- **Containerization**: Docker + Docker Compose

## Common Commands

### Development

```bash
# Backend (from /backend)
~/.local/bin/uv sync              # Install/sync dependencies
~/.local/bin/uv run uvicorn app.main:app --reload  # Dev server (port 8000)
~/.local/bin/uv run pytest tests/                  # Run all tests
~/.local/bin/uv run pytest tests/test_*.py -v      # Run specific test
~/.local/bin/uv run ruff check .                   # Lint
~/.local/bin/uv run ruff format .                  # Format

# Frontend (from /frontend)
pnpm install                      # Install dependencies
pnpm dev                          # Dev server (port 3000)
pnpm build                        # Production build
pnpm test                         # Run vitest tests

# E2E Tests (from root)
pnpm test                         # Run Playwright tests (requires both servers running)

# Docker Development (from root)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build  # Dev with hot-reload
docker-compose down                                                         # Stop services

# Docker Production (from root)
docker-compose up --build -d      # Production mode
docker-compose logs -f            # View logs
```

### Gospel Piano AI Pipeline

```bash
# Interactive menu (recommended for full workflow)
./scripts/quickstart.sh

# Manual commands for specific tasks
~/.local/bin/uv run python scripts/build_gospel_dataset.py --limit 100  # Collect 100 gospel MIDIs
~/.local/bin/uv run python scripts/monitor_dataset_progress.py          # Monitor collection progress
~/.local/bin/uv run python scripts/validate_gospel_midis.py --input data/gospel_dataset/validated
~/.local/bin/uv run python scripts/train_mlx_gospel.py --epochs 10 --batch-size 8
~/.local/bin/uv run python scripts/generate_gospel_batch.py --count 10000
```

### Database Migrations (Alembic)

```bash
# From /backend
~/.local/bin/uv run alembic revision --autogenerate -m "description"  # Create migration
~/.local/bin/uv run alembic upgrade head                               # Apply migrations
~/.local/bin/uv run alembic downgrade -1                               # Rollback one migration
~/.local/bin/uv run alembic history                                    # View migration history
```

## Architecture Overview

### Request Flow

```
User → Frontend (React) → Backend API → Service Layer → Pipeline Modules → Audio Processing
                              ↓
                        SQLite Database
                              ↓
                        File Storage (uploads/, outputs/)
```

### Backend Pipeline (5 Stages)

1. **Acquire**: YouTube download (yt-dlp) or file upload
2. **Extract**: Video → Audio conversion (ffmpeg)
3. **Isolate**: Piano stem separation (Demucs) - optional
4. **Transcribe**: Audio → MIDI notes (basic-pitch or custom models)
5. **Analyze**: Chord detection, genre classification, pattern recognition (librosa, custom analyzers)

Job status flow: `queued → downloading → processing → analyzing → complete|failed|cancelled`

### Gospel AI System Architecture

The gospel piano generation system uses a hybrid AI + rules approach optimized for M4 Pro:

```
Input (Chord Progression, Key, Tempo, Application)
         ↓
MLXGospelGenerator (M4 Pro neural engine optimized)
         ↓
REMI Tokenization → Transformer (Mistral-7B + LoRA) → MIDI Tokens
         ↓
HybridGospelArranger (AI percentage: 0-100%)
         ├─ AI Path: MLX-generated patterns
         └─ Rules Path: Traditional pattern library
         ↓
Gospel Patterns (left_hand + right_hand)
         ├─ Left: Stride bass, walking bass, shell voicings
         └─ Right: Block chords, runs, polychords
         ↓
Rhythm Transformations (shuffle, backbeat, syncopation)
         ↓
Enhanced MIDI Export (humanization, sustain pedal)
```

**Core Data Structures** (`app/gospel/__init__.py`):
- `Note`: MIDI note with pitch, time, duration, velocity, hand
- `ChordContext`: Context for generation (chord, key, position, tempo, previous voicing for smooth voice leading)
- `HandPattern`: Named pattern with difficulty, tempo range, characteristics
- `Arrangement`: Final two-hand output ready for MIDI export

**Key Components**:
- `app/gospel/ai/mlx_music_generator.py`: M4 Pro optimized generator, REMI tokenization, LoRA fine-tuning
- `app/gospel/arrangement/hybrid_arranger.py`: Blends AI generation with rule-based patterns
- `app/gospel/patterns/`: Left hand, right hand, rhythm transformation modules
- `app/gospel/applications/`: Practice, Concert, Worship, Uptempo application variants

**Production Scripts** (`scripts/`):
- `quickstart.sh`: Interactive menu with 9 workflow options
- `build_gospel_dataset.py`: YouTube → MIDI dataset builder (automated)
- `musescore_scraper.py`: MuseScore download helper (manual)
- `monitor_dataset_progress.py`: Real-time collection stats with progress bar
- `validate_gospel_midis.py`: Gospel quality validation (extended harmony, rhythm, playability)
- `train_mlx_gospel.py`: MLX model fine-tuning (LoRA, batch size 8 for 24GB RAM)
- `generate_gospel_batch.py`: Batch MIDI generation (10K MIDIs in ~90 min)

**Workflow**: Collect 100+ MIDIs → Train MLX model (2-4 hours) → Generate 10K MIDIs (90 min)

### Backend Structure

```
backend/app/
├── main.py                    # FastAPI app, CORS, lifespan, routers
├── core/config.py             # Settings (env vars, paths, feature flags)
├── api/routes/                # API endpoints
│   ├── transcribe.py          # POST /transcribe/url|upload, GET /{id}/result
│   ├── jobs.py                # Job management (list, cancel, delete)
│   ├── library.py             # Song library CRUD
│   ├── practice.py            # Practice sessions, time-stretch
│   ├── export.py              # MusicXML, quantized MIDI export
│   ├── analysis.py            # Advanced analysis (patterns, functions)
│   ├── ai.py                  # Gemini API for theory explanations
│   └── curriculum.py          # SRS (Spaced Repetition System) for practice
├── schemas/                   # Pydantic models (request/response contracts)
├── services/                  # Business logic orchestration
│   └── transcription.py       # Coordinates pipeline execution
├── pipeline/                  # Audio processing modules
│   ├── downloader.py          # YouTube download
│   ├── midi_converter.py      # Audio → MIDI
│   ├── chord_detector.py      # Chord analysis
│   ├── progression_detector.py # Chord progression patterns
│   ├── genre_classifier.py    # Genre detection (Gospel/Jazz/Blues/Classical)
│   ├── blues_analyzer.py      # 12-bar form, blue notes
│   ├── harmonic_function_analyzer.py  # Roman numeral analysis
│   └── reharmonization_engine.py      # Suggest alternative voicings
├── database/
│   ├── models.py              # SQLAlchemy ORM models
│   └── session.py             # Async DB session management
├── gospel/                    # Gospel piano AI system (2,492 lines)
│   ├── __init__.py            # Core data structures (Note, ChordContext, HandPattern, Arrangement)
│   ├── ai/                    # MLX generator, REMI tokenizer
│   ├── arrangement/           # Arranger, hybrid AI+rules logic
│   ├── patterns/              # Left/right hand patterns, rhythm transformations
│   ├── applications/          # Application-specific variants (Practice, Concert, Worship, Uptempo)
│   ├── midi/                  # Enhanced MIDI export, humanization
│   └── validation/            # Gospel quality validation
└── theory/                    # Music theory utilities (scales, chords, voicings)
```

### Frontend Structure (File-Based Routing)

```
frontend/src/
├── router.tsx                 # TanStack Router setup
├── routeTree.gen.ts           # Auto-generated route tree
├── routes/                    # File-based routes
│   ├── __root.tsx             # Root layout, QueryProvider, global nav
│   ├── index.tsx              # Home page (/)
│   ├── transcribe.tsx         # Upload interface (/transcribe)
│   ├── result.$jobId.tsx      # Job status + results (/result/:jobId)
│   ├── library.tsx            # Song library list
│   └── practice.$songId.tsx   # Practice mode with playback controls
├── components/
│   ├── upload/                # UrlInput, FileUpload
│   ├── piano/                 # PianoRoll, ChordTimeline (visualizations)
│   ├── library/               # SongCard, LibraryGrid
│   └── practice/              # PlaybackControls, LoopSelector
├── hooks/
│   ├── useTranscription.ts    # Mutations + queries for transcription jobs
│   ├── useLibrary.ts          # Library CRUD operations
│   └── usePractice.ts         # Practice session tracking
└── lib/
    ├── api.ts                 # Axios client with typed endpoints
    └── utils.ts               # Helper functions (cn, formatters)
```

**Routing Pattern**: TanStack Router uses file-based routing. Files in `src/routes/` automatically become routes. Use `$param` syntax for dynamic segments (e.g., `result.$jobId.tsx` → `/result/:jobId`).

### Data Flow Patterns

**Backend Service Pattern**: Routes delegate to services → services orchestrate pipeline modules → results stored in DB + files.

**Frontend State Management**:
- **TanStack Query**: Server state (API data, caching, polling for job status)
  - Query keys: `["transcription", "job", jobId]`, `["library", "songs"]`
  - Auto-refetch on job status polling (every 1s while in-progress)
- **Zustand**: Client state (UI preferences, playback state)

**Job Polling**: Frontend polls `GET /api/v1/transcribe/{jobId}` every 1 second while status is `queued|downloading|processing|analyzing`. Polling stops on `complete|failed|cancelled`.

## Key Patterns & Conventions

### Backend

- **Dependency injection**: Services injected into route modules via `lifespan` event
- **Async everywhere**: All DB operations and pipeline I/O are async
- **Error handling**: Pydantic validation → 400, not found → 404, processing errors → job.error + status=failed
- **File organization**: Outputs in `outputs/{job_id}/`, uploads in `uploads/{job_id}/`
- **Settings**: All config via `app/core/config.py` reading from `.env` (never hardcode paths/URLs)

### Gospel AI System

- **Hybrid approach**: AI percentage (0-100%) controls blend between AI-generated and rule-based patterns
- **Voice leading**: Previous chord voicing passed in `ChordContext` for smooth transitions
- **Pattern selection**: Based on tempo suitability, difficulty level, application type
- **REMI tokenization**: 284 vocab tokens, max sequence length 2048 (~16 bars)
- **MLX optimization**: Batch size 8 optimal for 24GB RAM, leverages M4 Pro GPU acceleration
- **Validation**: Extended harmony detection (9ths, 11ths, 13ths), gospel rhythm patterns, playability checks (hand span ≤12 semitones)

### Frontend

- **API client**: All backend calls through `lib/api.ts` with TypeScript types matching backend schemas
- **Component co-location**: Components in `components/`, organized by feature (upload/, piano/, library/)
- **Query hooks**: Custom hooks wrap TanStack Query (e.g., `useTranscriptionJob()` handles polling logic)
- **Route data loading**: Use TanStack Router loaders for initial data, Query for mutations/polling

### Multi-Genre Analysis

The system detects and analyzes music across genres:
- **Gospel**: Extended jazz chords (9ths, 11ths, 13ths), chromatic passing chords
- **Jazz**: ii-V-I progressions, tritone substitutions, altered dominants
- **Blues**: 12-bar form, blue notes (b3, b5, b7), dominant 7th chains
- **Classical**: Functional harmony, cadences, modulations

Pipeline modules in `app/pipeline/*_analyzer.py` provide genre-specific insights stored in job results.

## Important Files

- **Backend entry**: `backend/app/main.py` (FastAPI app, router includes, CORS, lifespan)
- **Frontend entry**: `frontend/src/router.tsx` (TanStack Router setup)
- **Settings**: `backend/app/core/config.py` (all environment-based config)
- **API contracts**: `backend/app/schemas/` (Pydantic models) mirrored in frontend TypeScript types
- **Gospel core**: `backend/app/gospel/__init__.py` (Note, ChordContext, HandPattern, Arrangement data structures)
- **MLX generator**: `backend/app/gospel/ai/mlx_music_generator.py` (M4 Pro optimized generation)
- **Hybrid arranger**: `backend/app/gospel/arrangement/hybrid_arranger.py` (AI + rules blending)
- **Gospel production**: `backend/PRODUCTION_READY.md` (complete workflow guide for 10K MIDI generation)
- **Architecture docs**: `architecture.md` (detailed flow diagrams), `flow idagrams.md`
- **Backend README**: `backend/README.md` (Docker setup, API examples)

## Environment Setup

**Backend** requires `.env` file in `backend/` directory (copy from `.env.example`):
- Database path, upload/output directories
- CORS origins for frontend
- Gemini API key (for AI theory features)

**Frontend** requires `VITE_API_URL` environment variable (defaults to `http://localhost:8000` in dev).

## Docker Notes

- **Development mode**: Uses `docker-compose.dev.yml` overlay with volume mounts for hot-reload
- **Production mode**: Standard `docker-compose.yml` builds optimized images
- **Backend port**: 8009 (mapped from internal 8000)
- **Frontend port**: 3000
- **Volumes**: `uploads/` and `outputs/` persist between container restarts

## Dependencies & Installation

**Backend**: Uses `uv` (fast Python package manager). Dependencies in `pyproject.toml`.

**System Requirements**:
- ffmpeg (audio processing): `brew install ffmpeg` on macOS
- Python 3.10-3.13 (full support, including basic-pitch)
- MLX framework (M-series Macs only for gospel AI features)

**Frontend**: Uses `pnpm` (specified in `package.json` via packageManager field). Lock file is `pnpm-lock.yaml`.

## Testing Strategy

- **Backend unit tests**: `tests/test_*.py` cover services, pipeline modules, theory utilities
- **Backend integration tests**: `tests/integration/` test full API endpoints with test DB
- **Gospel validation**: `scripts/validate_gospel_midis.py` validates gospel characteristics (extended harmony, rhythm patterns, playability)
- **Frontend component tests**: `src/test/*.test.tsx` with vitest + @testing-library/react
- **E2E tests**: Root `tests/*.spec.ts` with Playwright (full user flows)

**Test data**: Backend uses sample audio files in `tests/fixtures/` for pipeline testing.

## Gospel AI Production Workflow

**Quick Start** (Interactive Menu):
```bash
cd backend
./scripts/quickstart.sh
```

**Menu Options**:
1. Test YouTube search (30 sec)
2. Collect 10 MIDIs (test, 15 min)
3. Collect 100 MIDIs (full dataset, 2-3 hours)
4. Monitor progress (real-time)
5. Validate MIDIs
6. Train MLX model (2-4 hours on M4 Pro)
7. Generate 100 test MIDIs
8. Generate 10,000 production MIDIs (90 min)
9. Complete pipeline (all steps, 6-8 hours)

**Manual Pipeline Steps**:
1. **Collect Dataset** (2-3 hours): `build_gospel_dataset.py --limit 100` - Downloads from YouTube, isolates piano, transcribes to MIDI
2. **Monitor Progress**: `monitor_dataset_progress.py` - Real-time stats, ETA, style distribution
3. **Validate Quality**: `validate_gospel_midis.py` - Checks extended harmony, rhythm, voice leading
4. **Train Model** (2-4 hours): `train_mlx_gospel.py --epochs 10 --batch-size 8` - Fine-tune Mistral-7B with LoRA on M4 Pro
5. **Generate MIDIs** (90 min): `generate_gospel_batch.py --count 10000` - Batch generation with automatic variation

**Training Configuration** (M4 Pro optimized):
- Model: Mistral-7B-Instruct-4bit
- LoRA rank: 8
- Batch size: 8 (optimal for 24GB RAM)
- Epochs: 10-20
- Max sequence: 2048 tokens (~16 bars)
- Dataset requirement: 100+ validated gospel MIDIs

**Generation Parameters**:
- Keys: All 24 major/minor
- Tempos: 60-160 BPM
- Applications: Practice, Concert, Worship, Uptempo
- Styles: Contemporary, Traditional, Jazz-gospel (auto-inferred)
- Output: `output/gospel_production_10k/{style}/gospel_{index}_{key}_{tempo}bpm_{application}.mid`

## Known Limitations

- Demucs piano isolation: Works best on clear piano recordings, may struggle with heavily layered mixes
- MIDI transcription: Polyphonic accuracy varies by audio quality and playing complexity
- MLX framework: M-series Macs only (no CUDA support for gospel AI features)
- Gospel AI training: Requires 100+ validated MIDIs for quality results
