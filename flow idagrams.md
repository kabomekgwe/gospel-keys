# Gospel Keys - Flow Diagrams

## 1. High-Level System Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│    USER                    FRONTEND                   BACKEND                       │
│                                                                                     │
│  ┌───────┐              ┌───────────┐              ┌───────────┐                   │
│  │ Paste │              │           │   POST       │           │                   │
│  │  URL  │─────────────►│  React    │─────────────►│  FastAPI  │                   │
│  └───────┘              │    +      │              │           │                   │
│                         │  TanStack │◄─────────────│  Returns  │                   │
│                         │   Query   │   Job ID     │  Job ID   │                   │
│                         │           │              │           │                   │
│                         └─────┬─────┘              └─────┬─────┘                   │
│                               │                          │                         │
│                               │ Poll every 1s            │ Background              │
│                               │                          │ Processing              │
│                               ▼                          ▼                         │
│                         ┌───────────┐              ┌───────────┐                   │
│                         │  Update   │◄─────────────│  Pipeline │                   │
│                         │ Progress  │   Status     │           │                   │
│                         │   Bar     │   Updates    │ yt-dlp    │                   │
│                         └───────────┘              │ ffmpeg    │                   │
│                               │                    │ demucs    │                   │
│                               │                    │ basic-pitch                   │
│                               │                    │ librosa   │                   │
│  ┌───────┐              ┌─────▼─────┐              └─────┬─────┘                   │
│  │ View  │◄─────────────│  Render   │◄─────────────┐     │                         │
│  │Results│              │  Piano    │   Complete   │     │                         │
│  └───────┘              │  Roll +   │   + Result   │     │                         │
│                         │  Chords   │              │     │                         │
│                         └───────────┘              └─────┘                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Backend Pipeline Detail

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              TRANSCRIPTION PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   INPUT                    PROCESSING                           OUTPUT             │
│                                                                                     │
│   ┌─────────┐                                                                       │
│   │YouTube  │──┐                                                                    │
│   │  URL    │  │         ┌──────────────────────────────────────────────┐          │
│   └─────────┘  │         │                                              │          │
│                ├────────►│  1. DOWNLOAD        [yt-dlp]                 │          │
│   ┌─────────┐  │         │     └─► video.mp4                            │          │
│   │ File    │──┘         │                                              │          │
│   │ Upload  │            │  2. EXTRACT AUDIO   [ffmpeg]                 │          │
│   └─────────┘            │     └─► audio.wav (44.1kHz mono)             │          │
│                          │                                              │          │
│                          │  3. ISOLATE PIANO   [demucs]     (optional)  │          │
│                          │     └─► piano.wav                            │          │
│                          │                                              │          │
│                          │  4. TRANSCRIBE      [basic-pitch]            │          │
│                          │     └─► NoteEvent[]                          │          │
│                          │     └─► output.mid                           │          │
│                          │                                              │          │
│                          │  5. DETECT CHORDS   [librosa]                │          │
│                          │     └─► ChordEvent[]                         │          │
│                          │                                              │          │
│                          │  6. ANALYZE         [custom]     (Phase 2)   │          │
│                          │     └─► GospelPattern[]                      │──────┐   │
│                          │                                              │      │   │
│                          └──────────────────────────────────────────────┘      │   │
│                                                                                │   │
│                                                                                ▼   │
│                                                               ┌─────────────────┐  │
│                                                               │ Transcription   │  │
│                                                               │ Result          │  │
│                                                               │                 │  │
│                                                               │ • notes[]       │  │
│                                                               │ • chords[]      │  │
│                                                               │ • tempo         │  │
│                                                               │ • key           │  │
│                                                               │ • midi_url      │  │
│                                                               └─────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 3. Frontend Component Tree

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND STRUCTURE                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   App.tsx                                                                           │
│   │                                                                                 │
│   └─► <Routes>                                                                      │
│       │                                                                             │
│       ├─► <Layout>                    ← Header, Footer wrapper                      │
│       │   │                                                                         │
│       │   ├─► "/" ─────────────► <HomePage>                                         │
│       │   │                       │                                                 │
│       │   │                       ├─► Hero Section                                  │
│       │   │                       ├─► Feature Cards                                 │
│       │   │                       └─► CTA Section                                   │
│       │   │                                                                         │
│       │   ├─► "/transcribe" ───► <TranscribePage>                                   │
│       │   │                       │                                                 │
│       │   │                       ├─► Mode Tabs (URL | File)                        │
│       │   │                       │                                                 │
│       │   │                       ├─► <UrlInput>           ← YouTube URL entry      │
│       │   │                       │   └─► Validates URL                             │
│       │   │                       │   └─► Calls useTranscribeUrl()                  │
│       │   │                       │                                                 │
│       │   │                       ├─► <FileUpload>         ← Drag & drop            │
│       │   │                       │   └─► react-dropzone                            │
│       │   │                       │   └─► Calls useTranscribeFile()                 │
│       │   │                       │                                                 │
│       │   │                       └─► Options Panel                                 │
│       │   │                                                                         │
│       │   └─► "/result/:jobId" ─► <ResultPage>                                      │
│       │                           │                                                 │
│       │                           ├─► useTranscriptionJob(jobId)                    │
│       │                           │   └─► Polls until complete                      │
│       │                           │                                                 │
│       │                           ├─► Progress Bar (while processing)               │
│       │                           │                                                 │
│       │                           ├─► Metadata Cards                                │
│       │                           │   └─► Duration, Tempo, Key, Notes               │
│       │                           │                                                 │
│       │                           ├─► <PianoRoll>          ← MIDI visualization     │
│       │                           │   └─► notes: NoteEvent[]                        │
│       │                           │   └─► Clickable for seek                        │
│       │                           │                                                 │
│       │                           └─► <ChordTimeline>      ← Chord progression      │
│       │                               └─► chords: ChordEvent[]                      │
│       │                               └─► Color-coded by quality                    │
│       │                                                                             │
└───────┴─────────────────────────────────────────────────────────────────────────────┘
```

## 4. Data Flow Sequence

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         SEQUENCE: URL TRANSCRIPTION                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   User          TranscribePage       API Client        Backend         Pipeline     │
│    │                  │                  │                │                │        │
│    │  Enter URL       │                  │                │                │        │
│    │─────────────────►│                  │                │                │        │
│    │                  │                  │                │                │        │
│    │  Click Submit    │                  │                │                │        │
│    │─────────────────►│                  │                │                │        │
│    │                  │                  │                │                │        │
│    │                  │  transcribeUrl() │                │                │        │
│    │                  │─────────────────►│                │                │        │
│    │                  │                  │                │                │        │
│    │                  │                  │  POST /url     │                │        │
│    │                  │                  │───────────────►│                │        │
│    │                  │                  │                │                │        │
│    │                  │                  │                │  Start job     │        │
│    │                  │                  │                │───────────────►│        │
│    │                  │                  │                │                │        │
│    │                  │                  │  { id, status }│                │        │
│    │                  │                  │◄───────────────│                │        │
│    │                  │                  │                │                │        │
│    │                  │  Job created     │                │                │        │
│    │                  │◄─────────────────│                │                │        │
│    │                  │                  │                │                │        │
│    │  Navigate to     │                  │                │                │        │
│    │  /result/{id}    │                  │                │                │        │
│    │◄─────────────────│                  │                │                │        │
│    │                  │                  │                │                │        │
│    │                                                                       │        │
│    │                     ResultPage         TanStack Query                 │        │
│    │                         │                  │                          │        │
│    │                         │  useJob(id)      │                          │        │
│    │                         │─────────────────►│                          │        │
│    │                         │                  │                          │        │
│    │                         │                  │  GET /transcribe/{id}    │        │
│    │                         │                  │─────────────────────────►│        │
│    │                         │                  │                          │        │
│    │                         │                  │  { status: "processing", │        │
│    │                         │                  │    progress: 45 }        │        │
│    │                         │                  │◄─────────────────────────│        │
│    │                         │                  │                          │        │
│    │  Show progress   │◄─────────────────│                                 │        │
│    │◄─────────────────│                  │                                 │        │
│    │                  │                  │                                 │        │
│    │                  │      ... polling continues every 1s ...            │        │
│    │                  │                  │                                 │        │
│    │                  │                  │  GET /transcribe/{id}           │        │
│    │                  │                  │─────────────────────────────────►        │
│    │                  │                  │                                 │        │
│    │                  │                  │  { status: "complete",          │        │
│    │                  │                  │    result: {...} }              │        │
│    │                  │                  │◄─────────────────────────────────        │
│    │                  │                  │                                 │        │
│    │  Render results  │◄─────────────────│                                 │        │
│    │  (PianoRoll,     │                  │                                 │        │
│    │   ChordTimeline) │                  │                                 │        │
│    │◄─────────────────│                  │                                 │        │
│    │                  │                  │                                 │        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 5. State Management

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              STATE ARCHITECTURE                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                         SERVER STATE (TanStack Query)                        │  │
│   │                                                                             │  │
│   │   Cached & synced with backend:                                             │  │
│   │                                                                             │  │
│   │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │  │
│   │   │ Job Status      │  │ Job Result      │  │ Job List        │            │  │
│   │   │                 │  │                 │  │                 │            │  │
│   │   │ Key:            │  │ Key:            │  │ Key:            │            │  │
│   │   │ ["job", id]     │  │ ["result", id]  │  │ ["jobs"]        │            │  │
│   │   │                 │  │                 │  │                 │            │  │
│   │   │ Polls: Yes      │  │ Polls: No       │  │ Polls: No       │            │  │
│   │   │ (while active)  │  │ (fetched once)  │  │ (on demand)     │            │  │
│   │   └─────────────────┘  └─────────────────┘  └─────────────────┘            │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                         CLIENT STATE (React useState)                        │  │
│   │                                                                             │  │
│   │   Component-local, UI-only:                                                 │  │
│   │                                                                             │  │
│   │   TranscribePage:                                                           │  │
│   │   ┌─────────────────────────────────────────────────────┐                  │  │
│   │   │ mode: "url" | "file"        ← Tab selection         │                  │  │
│   │   │ showOptions: boolean        ← Options panel toggle  │                  │  │
│   │   │ options: TranscriptionOptions ← Form state          │                  │  │
│   │   └─────────────────────────────────────────────────────┘                  │  │
│   │                                                                             │  │
│   │   PianoRoll:                                                                │  │
│   │   ┌─────────────────────────────────────────────────────┐                  │  │
│   │   │ currentTime: number         ← Playhead position     │                  │  │
│   │   │ zoom: number                ← Zoom level            │                  │  │
│   │   └─────────────────────────────────────────────────────┘                  │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                         GLOBAL STATE (Zustand) [Future]                      │  │
│   │                                                                             │  │
│   │   Cross-component, persistent:                                              │  │
│   │                                                                             │  │
│   │   ┌─────────────────────────────────────────────────────┐                  │  │
│   │   │ playback: { isPlaying, currentTime, speed }         │ ← Audio player   │  │
│   │   │ user: { id, preferences }                           │ ← Auth state     │  │
│   │   │ ui: { sidebarOpen, theme }                          │ ← UI prefs       │  │
│   │   └─────────────────────────────────────────────────────┘                  │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 6. API Contract Summary

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               API ENDPOINTS                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   TRANSCRIPTION                                                                     │
│   ─────────────                                                                     │
│                                                                                     │
│   POST /api/v1/transcribe/url                                                       │
│   ├── Request:  { url: string, options: TranscriptionOptions }                      │
│   ├── Response: TranscriptionJob                                                    │
│   └── Action:   Creates job, starts background processing                           │
│                                                                                     │
│   POST /api/v1/transcribe/upload                                                    │
│   ├── Request:  multipart/form-data { file, isolate_piano, detect_chords }          │
│   ├── Response: TranscriptionJob                                                    │
│   └── Action:   Saves file, creates job, starts processing                          │
│                                                                                     │
│   GET /api/v1/transcribe/{job_id}                                                   │
│   ├── Response: TranscriptionJob (with progress)                                    │
│   └── Usage:    Poll this endpoint while status is in-progress                      │
│                                                                                     │
│   GET /api/v1/transcribe/{job_id}/result                                            │
│   ├── Response: TranscriptionResult                                                 │
│   └── Requires: Job status must be "complete"                                       │
│                                                                                     │
│   JOBS                                                                              │
│   ────                                                                              │
│                                                                                     │
│   GET /api/v1/jobs                                                                  │
│   ├── Params:   ?status=complete&limit=20&offset=0                                  │
│   └── Response: TranscriptionJob[]                                                  │
│                                                                                     │
│   DELETE /api/v1/jobs/{job_id}                                                      │
│   └── Action:   Cancel a running job                                                │
│                                                                                     │
│   DELETE /api/v1/jobs/{job_id}/result                                               │
│   └── Action:   Delete job and associated files                                     │
│                                                                                     │
│   HEALTH                                                                            │
│   ──────                                                                            │
│                                                                                     │
│   GET /health                                                                       │
│   └── Response: { status: "healthy", service: "gospel-keys-api" }                   │
│                                                                                     │
│   GET /health/detailed                                                              │
│   └── Response: { status, checks: { database, redis, celery, ffmpeg } }             │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 7. File Structure Summary

```
gospel-piano-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── core/
│   │   │   └── config.py        # Settings
│   │   ├── api/routes/
│   │   │   ├── health.py        # Health checks
│   │   │   ├── transcribe.py    # Core endpoints
│   │   │   └── jobs.py          # Job management
│   │   ├── schemas/
│   │   │   └── transcription.py # Pydantic models
│   │   ├── services/
│   │   │   └── transcription.py # Business logic
│   │   └── pipeline/
│   │       ├── downloader.py    # yt-dlp
│   │       ├── audio_extractor.py # ffmpeg
│   │       ├── source_separator.py # demucs
│   │       ├── midi_converter.py # basic-pitch
│   │       └── chord_detector.py # librosa
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # Entry point
│   │   ├── App.tsx              # Routes
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── TranscribePage.tsx
│   │   │   └── ResultPage.tsx
│   │   ├── components/
│   │   │   ├── ui/Layout.tsx
│   │   │   ├── upload/
│   │   │   │   ├── UrlInput.tsx
│   │   │   │   └── FileUpload.tsx
│   │   │   └── piano/
│   │   │       ├── PianoRoll.tsx
│   │   │       └── ChordTimeline.tsx
│   │   ├── hooks/
│   │   │   └── useTranscription.ts
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── transcription.ts
│   ├── biome.json
│   └── package.json
│
├── docker-compose.yml
└── docs/
    └── ARCHITECTURE.md          # This file
```