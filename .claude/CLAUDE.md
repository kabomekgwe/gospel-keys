# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Gospel Keys** (formerly "Piano Learning") is a full-stack music analysis and learning platform that transcribes YouTube videos/audio files to MIDI, performs deep music theory analysis, and provides AI-powered learning features.

**Core Capabilities:**
- YouTube/file → MIDI transcription with piano isolation
- Advanced music theory analysis (voicings, progressions, reharmonizations)
- Gospel-specific MIDI generation with hand-crafted patterns
- Jazz lick generation with theory analysis
- Adaptive curriculum with spaced repetition (SRS)
- AI-powered coaching using Gemini API

---

## Tech Stack

### Backend (Python)
- **Framework**: FastAPI (async)
- **Server**: Uvicorn
- **Database**: SQLAlchemy 2.0 (async), SQLite/PostgreSQL
- **Audio**: librosa, Demucs (source separation), yt-dlp, ffmpeg
- **MIDI**: basic-pitch (Spotify research), pretty-midi, music21
- **ML**: PyTorch (MPS for Apple Silicon), MLX (Apple M-series optimized)
- **AI**: google-generativeai (Gemini), anthropic
- **Tasks**: Celery + Redis (background jobs)
- **Python**: 3.10-3.13

### Frontend (TypeScript/React)
- **Framework**: React 19 + TypeScript
- **Routing**: TanStack Router v1 (file-based)
- **State**: TanStack Query v5 (server), Zustand (client)
- **UI**: Tailwind CSS 4, Framer Motion
- **Music**: Tone.js (synthesis), VexFlow (notation), Web Audio API
- **Build**: Vite 7
- **Testing**: Vitest, Playwright

### Package Manager
- **pnpm** 10.14.0 (strictly required - DO NOT use npm or yarn)

---

## Development Commands

### Backend

```bash
# Navigate to backend
cd backend

# Install dependencies (first time)
pip install -e ".[dev]"

# Run dev server (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Lint/format
ruff check .
ruff format .

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time)
pnpm install

# Run dev server (port 3000)
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Preview production build
pnpm preview
```

### Root-level E2E Tests

```bash
# Run Playwright tests
pnpm exec playwright test

# Run with UI
pnpm exec playwright test --ui
```

---

## Architecture Overview

### Monorepo Structure

```
youtube-transcript/
├── backend/           # Python FastAPI service
│   └── app/
│       ├── api/routes/       # HTTP endpoints (transcribe, library, curriculum, ai, gospel)
│       ├── schemas/          # Pydantic models (API contracts)
│       ├── services/         # Business logic orchestration
│       ├── pipeline/         # Audio processing modules (22 specialized processors)
│       ├── database/         # SQLAlchemy ORM models
│       ├── gospel/           # Gospel MIDI generation (patterns, arrangement)
│       ├── jazz/             # Jazz lick generation and analysis
│       ├── theory/           # Music theory utilities (chords, scales, intervals)
│       └── main.py           # FastAPI app factory
└── frontend/          # React + TanStack app
    └── src/
        ├── routes/           # File-based routing (TanStack Router)
        ├── components/       # React UI (analysis, curriculum, generator)
        ├── hooks/            # Custom hooks (useMidiPlayer, useChordPlayback, usePiano)
        ├── lib/              # Utilities and typed API client
        └── main.tsx          # Entry point
```

### Request Flow (Transcription Pipeline)

```
HTTP POST /api/v1/transcribe/url
    ↓
TranscriptionService.create_job()
    ↓
Background Task Chain (7 steps):
    1. Download (yt-dlp)          → 5-10% progress
    2. Extract Audio (ffmpeg)     → 15%
    3. Isolate Piano (Demucs)     → 30-50%
    4. Transcribe MIDI (basic-pitch) → 55%
    5. Detect Chords (librosa)    → 80%
    6. Theory Analysis (music21)  → 85%
    7. Advanced Analysis:
       - Voicing Classification   → 90%
       - Progression Detection    → 95%
       - Reharmonization Suggest  → 100%
    ↓
TranscriptionResult (JSON with MIDI notes, chords, patterns, analysis)
    ↓
Frontend polls GET /api/v1/transcribe/{job_id} every 1s
    ↓
When complete: fetch GET /api/v1/transcribe/{job_id}/result
    ↓
Display in AnalysisTab (piano roll, voicings, progressions, reharmonizations)
```

### Key Backend Services

**TranscriptionService** (`services/transcription.py`)
- Orchestrates 7-step pipeline from URL/file → MIDI
- Manages job lifecycle (QUEUED → DOWNLOADING → PROCESSING → ANALYZING → COMPLETE)
- Error handling with retries and cleanup

**GospelGeneratorService** (`services/gospel_generator.py`)
- Generates gospel-style MIDI from chord progressions
- Hand-crafted pattern libraries (left-hand bass, right-hand comping)
- Velocity curves for expressive playback

**AIGeneratorService** (`services/ai_generator.py`)
- Gemini API integration for music generation
- Generates: progressions, voicings, exercises, licks, reharmonizations
- Hybrid AI + rule-based validation

**CurriculumService** (`services/curriculum_service.py`)
- Adaptive learning paths with SRS (SuperMemo-2 algorithm)
- Skill assessment and progress tracking
- AI coach integration

### Key Pipeline Modules (22 total)

**Core Analysis:**
- `voicing_analyzer.py` - Classifies 9 voicing types (drop-2, rootless, shell, cluster, etc.)
- `progression_detector.py` - Matches against 30+ patterns (jazz, pop, blues, modal)
- `reharmonization_engine.py` - Suggests 8 alternative chord types per chord
- `voice_leading_analyzer.py` - Analyzes smooth voice transitions
- `chord_detector.py` - Detects chords using librosa + templates

**Genre-Specific:**
- `jazz_analyzer.py` - Jazz theory patterns (ii-V-I, rhythm changes, Coltrane changes)
- `blues_analyzer.py` - Blues-specific detection
- `classical_analyzer.py` - Classical form analysis

**Input/Processing:**
- `downloader.py` - yt-dlp wrapper
- `audio_extractor.py` - ffmpeg conversion to 44.1kHz mono WAV
- `source_separator.py` - Demucs model for piano isolation
- `midi_converter.py` - basic-pitch transcription

### Frontend Architecture

**Routing** (TanStack Router, file-based):
- `/` - Dashboard
- `/upload` - Transcription input
- `/library` - User's songs
- `/library/[id]` - Song analysis view
- `/curriculum` - Learning paths
- `/generator` - AI generation tools
- `/practice` - Practice exercises

**State Management:**
- **Server State**: TanStack Query (caching, polling, mutations)
- **Client State**: Zustand (global UI state)

**API Client Pattern** (`lib/api.ts`):
```typescript
export const transcriptionApi = {
  fromUrl: (url, options) => fetch(...),
  getStatus: (jobId) => fetch(...),
  getResult: (jobId) => fetch(...),
};

// Usage with TanStack Query:
const { data: job } = useQuery({
  queryKey: ['transcription', 'job', jobId],
  queryFn: () => transcriptionApi.getStatus(jobId),
  refetchInterval: 1000, // Poll every 1s
});
```

**Custom Hooks:**
- `useMidiPlayer.ts` - MIDI playback control
- `useChordPlayback.ts` - Chord audio synthesis with Tone.js
- `usePiano.ts` - Interactive piano keyboard
- `useVexFlow.ts` - Musical notation rendering

---

## Music Theory Domain

### Voicing Classification (9 types)

Algorithm groups MIDI notes by chord time, then classifies:
1. **Quartal** - All intervals are 4ths
2. **Cluster** - Adjacent semitones
3. **Rootless** - No root note
4. **Shell** - Root-3rd-7th only
5. **Close** - All notes within octave
6. **Drop-2/Drop-3** - Specific voicing patterns
7. **Open** - Spans >1 octave
8. **Spread** - Very wide spacing (>2 octaves)

Output: voicing type, MIDI notes, intervals, width, complexity score, hand span

### Progression Detection (30+ patterns)

**Pop** (5): Axis of Awesome (I-V-vi-IV), Sensitive Female, 50s, Pachelbel, Andalusian
**Jazz** (15+): ii-V-I, turnarounds, rhythm changes, Coltrane changes, backdoor, tritone subs
**Blues** (4): 12-bar (standard/quick-change), 8-bar, minor blues
**Modal** (3+): Dorian/Mixolydian/Lydian vamps

Detection: Convert to root intervals → match against templates → return with roman numerals

### Reharmonization (8 types)

1. Tritone Substitution (V7 → bII7)
2. Diatonic Substitutes (I→vi, IV→ii, V→iii)
3. Passing Chords (chromatic approach)
4. Approach Chords (half-step above)
5. Backdoor Progressions (bVII7 → I)
6. Modal Interchange (parallel minor/major)
7. Upper Structure Triads (complex extensions)
8. Diminished Passing Chords

Each suggestion includes: chord, explanation, jazz difficulty (1-5), voice-leading quality

---

## AI Integration (Gemini API)

### AI Generator Endpoints (`/api/v1/ai/*`)

- `POST /progressions` - Generate chord progressions (key, mode, style, mood, length)
- `POST /voicings` - Generate voicing options (chord, style, hand)
- `POST /exercises` - Generate practice exercises (type, key, difficulty)
- `POST /licks` - Generate jazz licks (style, context, difficulty) **NEW**
- `POST /reharmonization` - AI-powered reharmonization suggestions
- `POST /substitutions` - Chord substitution ideas

### Hybrid AI + Validation Pattern

**Jazz Licks Example** (`services/ai_generator.py`):
```python
async def generate_licks(request: LicksRequest):
    # 1. Get appropriate scales for context
    scales = lick_pattern_service.get_scales_for_context(chords, style)

    # 2. Build Gemini prompt with style guidelines
    prompt = self._build_licks_prompt(request, scales)

    # 3. Generate with Gemini
    response = self.model.generate_content(prompt)
    licks_data = parse_json_from_response(response.text)

    # 4. Validate each lick (scale conformance, playability)
    for lick in licks_data["licks"]:
        validation = lick_pattern_service.validate_lick(lick, ...)
        if validation.is_valid:
            validated_licks.append(lick)

    # 5. Retry if <3 valid licks
    return LicksResponse(licks=validated_licks, ...)
```

**Validation Rules** (`jazz/lick_patterns.py`):
- MIDI range: 48-84 (playable piano range)
- Scale conformance: 90-95% (allow chromatic passing tones)
- Difficulty-appropriate intervals (beginner: max 5th, advanced: any)
- Rhythm complexity matching difficulty level

---

## Gospel MIDI Generation

### Pattern-Based System (`gospel/`)

**Components:**
- `Note` class - MIDI note with hand/timing context
- `ChordContext` - Voicing/rhythm decision data
- `patterns/left_hand.py` - Bass patterns (walking bass, root-fifth, stride)
- `patterns/right_hand.py` - Comping patterns (block chords, rhythmic fills)
- `arrangement/arranger.py` - Full composition orchestration
- `midi/exporter.py` - Enhanced MIDI export with velocity curves

**Generation Flow:**
```
Chord Progression
    ↓
Select Application Type (worship, uptempo, practice)
    ↓
Choose Patterns (left-hand bass, right-hand rhythm)
    ↓
Arrange Hands (distribute notes, avoid collisions)
    ↓
Apply Velocity Curves (expression, dynamics)
    ↓
Export to MIDI
```

---

## Curriculum System (SRS)

### Database Models (`database/curriculum_models.py`)

- `Curriculum` - Master learning plan (duration_weeks, status)
- `CurriculumModule` - Themed blocks (4-8 weeks)
- `CurriculumLesson` - Weekly lessons
- `CurriculumExercise` - Practice items with SRS fields:
  - `next_review_at` - When to practice next
  - `interval_days` - Current review interval
  - `ease_factor` - Difficulty multiplier (2.5 default)
  - `repetition_count` - Total reviews

### SuperMemo-2 Algorithm (`services/srs_service.py`)

After practice, user rates quality (0-5):
- **0 (Blackout)** → Reset interval to 1 day
- **3 (Hesitant)** → Reduce ease factor
- **4 (Good)** → Increase interval by ease factor
- **5 (Perfect)** → Max interval increase

Formula: `new_interval = old_interval * ease_factor`

### Adding Content to Practice Queue

**Jazz Licks Integration** (`POST /curriculum/add-lick-to-practice`):
```python
# Auto-creates curriculum structure if missing
curriculum = get_or_create_curriculum(user_id)
module = get_or_create_module(curriculum, "Licks Practice")
lesson = get_or_create_lesson(module, "Jazz Licks")

# Create exercise with immediate review
exercise = CurriculumExercise(
    lesson_id=lesson.id,
    exercise_type="lick",
    content_json=json.dumps(lick_data),
    next_review_at=datetime.utcnow(),  # Immediate
    interval_days=1.0,
    ease_factor=2.5,
)
```

Frontend: "Add to Practice" button on each lick card → calls endpoint → lick appears in daily queue

---

## Key Patterns and Conventions

### Backend Patterns

**1. Service-Pipeline Pattern**
- Services orchestrate high-level workflows
- Pipeline modules are stateless processors
- Easy composition and testing

**2. Job-Based Async**
- Long tasks don't block HTTP
- Polling for status updates
- Job persistence across restarts

**3. Schema-Driven Development**
- Pydantic schemas define contracts
- Auto-validation on requests
- Frontend imports types from schemas

### Frontend Patterns

**1. TanStack Query for Server State**
```typescript
// Polling pattern
const { data, error } = useQuery({
  queryKey: ['job', jobId],
  queryFn: () => api.getStatus(jobId),
  refetchInterval: (query) => {
    return query.state.data?.status === 'complete' ? false : 1000;
  },
});
```

**2. Mutation Pattern**
```typescript
const mutation = useMutation({
  mutationFn: api.createJob,
  onSuccess: (job) => {
    navigate({ to: `/library/${job.job_id}` });
  },
});
```

**3. File-Based Routing**
- Routes auto-generated from `routes/` directory
- `[id]` for dynamic segments
- Type-safe navigation with TanStack Router

---

## Important Implementation Notes

### When Working with Music Theory Code

**Voicing Analyzer** (`pipeline/voicing_analyzer.py:182`):
- Groups notes by chord time window (±0.1s tolerance)
- Classification order matters (quartal → cluster → rootless → shell → drop voicings → close/open/spread)
- Returns `VoicingInfo` with complexity score (0-1) and hand span in inches

**Progression Detector** (`pipeline/progression_detector.py:47`):
- Patterns defined as interval sequences from tonic
- Requires at least 2 chords to match
- Returns confidence score (exact=1.0, fuzzy match=0.6-0.9)

**Reharmonization Engine** (`pipeline/reharmonization_engine.py:24`):
- 8 types with varying jazz difficulty levels
- Each suggestion includes explanation for learning
- Voice-leading quality: smooth (common tones) vs dramatic (large leaps)

### When Working with Gospel Generation

**Pattern Libraries** (`gospel/patterns/`):
- Left-hand: `WALKING_BASS`, `ROOT_FIFTH`, `STRIDE_BASS`
- Right-hand: `BLOCK_CHORDS`, `RHYTHMIC_FILLS`, `GOSPEL_RUNS`
- Patterns define: rhythm, note selection, velocity curves

**Arrangement** (`gospel/arrangement/arranger.py:89`):
- Distributes notes to hands based on register
- Avoids hand collisions (checks overlap)
- Applies application-specific styles (worship=sustained, uptempo=rhythmic)

### When Working with AI Generation

**Gemini Prompt Structure** (`services/ai_generator.py:469`):
```python
prompt = f"""
Generate {count} jazz licks in {style} style over {context}.

Requirements:
- Style: {_get_style_guidelines(style)}
- Difficulty: {_get_difficulty_guidelines(difficulty)}
- Scales: {scales}

Return JSON:
{{
  "licks": [
    {{
      "name": "...",
      "notes": ["C4", "D4", "E4"],
      "midi_notes": [60, 62, 64],
      "theory_analysis": {{ ... }}
    }}
  ]
}}
"""
```

**Validation After Generation** (`jazz/lick_patterns.py:156`):
- Check MIDI range (48-84)
- Verify scale conformance (90-95% accuracy)
- Validate interval jumps for difficulty
- Retry up to 2 times if <3 valid licks

### When Working with Curriculum

**SRS Scheduling** (`services/srs_service.py:23`):
```python
def schedule_next_review(exercise, quality: int):
    if quality < 3:
        # Reset on failure
        exercise.interval_days = 1.0
        exercise.repetition_count = 0
    else:
        # Increase interval
        exercise.interval_days *= exercise.ease_factor
        exercise.repetition_count += 1
        # Adjust ease factor based on quality
        exercise.ease_factor += (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    exercise.next_review_at = now + timedelta(days=exercise.interval_days)
```

**Auto-Create Structure** (`api/routes/curriculum.py:875`):
- GET/CREATE curriculum if missing
- GET/CREATE module "Licks Practice" if missing
- GET/CREATE lesson "Jazz Licks" if missing
- CREATE exercise with immediate review
- Zero user friction - all automatic

---

## Testing

### Backend Tests
```bash
cd backend
pytest                          # All tests
pytest tests/test_pipeline.py  # Specific module
pytest -v -s                    # Verbose with stdout
pytest -k "voicing"             # Match test names
```

### Frontend Tests
```bash
cd frontend
pnpm test                       # Run all Vitest tests
pnpm test -- --ui               # Interactive UI
pnpm test -- voicing            # Specific test files
```

### E2E Tests
```bash
pnpm exec playwright test       # Run all E2E
pnpm exec playwright test --ui  # Interactive mode
```

---

## Common Tasks

### Adding a New Pipeline Module

1. Create module in `backend/app/pipeline/your_analyzer.py`
2. Implement analysis function returning Pydantic model
3. Add to `TranscriptionService` pipeline chain
4. Update `TranscriptionResult` schema with new field
5. Add progress step (update percentage ranges)
6. Update frontend `AnalysisTab` to display results

### Adding a New AI Generator

1. Add request/response schemas in `backend/app/schemas/ai.py`
2. Implement generation method in `AIGeneratorService`
3. Add validation logic if using hybrid approach
4. Create endpoint in `api/routes/ai.py`
5. Add TypeScript types in `frontend/src/lib/api.ts`
6. Create UI in `components/generator/AIGenerator.tsx`

### Adding a New Gospel Pattern

1. Define pattern in `gospel/patterns/left_hand.py` or `right_hand.py`
2. Specify: rhythm, note selection logic, velocity profile
3. Register pattern in `PATTERN_LIBRARY`
4. Add to `arranger.py` pattern selection logic
5. Test with various chord progressions

---

## File Locations Reference

**Backend:**
- Schemas: `backend/app/schemas/*.py`
- Services: `backend/app/services/*.py`
- Pipeline: `backend/app/pipeline/*.py`
- Routes: `backend/app/api/routes/*.py`
- Database: `backend/app/database/*.py`

**Frontend:**
- Routes: `frontend/src/routes/**/*.tsx`
- Components: `frontend/src/components/**/*.tsx`
- API Client: `frontend/src/lib/api.ts`
- Hooks: `frontend/src/hooks/*.ts`

**Config:**
- Backend deps: `backend/pyproject.toml`
- Frontend deps: `frontend/package.json`
- Root E2E: `package.json`

---

## Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Add theory analysis fields"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

---

## Environment Variables

**Backend** (`.env` in `backend/`):
```bash
DATABASE_URL=postgresql://user:pass@localhost/gospel_keys
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
```

**Frontend** (`.env` in `frontend/`):
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## Known Issues / Gotchas

1. **Python 3.13 Compatibility**: Some packages (basic-pitch, audiocraft) require TensorFlow which doesn't support Python 3.13 yet. Use Python 3.10-3.12.

2. **Demucs Memory**: Source separation requires significant RAM (~4GB). May timeout on large files.

3. **MIDI Timing**: basic-pitch may quantize notes. For precise timing, use librosa onset detection.

4. **Voicing Classification**: Requires simultaneous notes within ±0.1s window. Single notes won't be classified.

5. **TanStack Router**: File-based routing requires restart when adding new route files.

6. **Gemini Rate Limits**: Free tier has limits. Implement retry with exponential backoff for production.

7. **MLX (Apple Silicon)**: Only works on M-series Macs. Gracefully falls back on other platforms.

---

## Project History

Originally **"youtube-transcript"** for MIDI transcription, evolved into **Gospel Keys** with:
- Phase 1: Basic transcription pipeline
- Phase 2: Gospel MIDI generation
- Phase 3: Jazz analysis and lick generation
- Phase 4: Curriculum system with SRS
- Phase 5: AI-powered learning features

Current focus: Completing jazz lick enhancements (variations, progression alignment) and expanding curriculum content.
