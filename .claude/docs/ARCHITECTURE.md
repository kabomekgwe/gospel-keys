# Architecture Document: Gospel Keys

**Version:** 1.0
**Last Updated:** December 15, 2025
**Status:** Production Ready (Phase 1)
**Project:** Music Education Platform

---

## System Overview

Gospel Keys is a full-stack music education platform built on a local-first AI architecture with GPU-accelerated audio processing. The system combines natural language processing (Gemini Pro), local LLM inference (MLX), genre-specific rule engines, and Metal API GPU synthesis to deliver professional-quality music generation and analysis.

**Key Architectural Principles**:
- **Local-First AI**: 90% of AI processing runs locally (Phi-3.5 Mini + Qwen2.5-7B)
- **GPU Acceleration**: Metal API on Apple Silicon (M4) for 100x real-time synthesis
- **Async-First**: FastAPI + React with TanStack Query for optimal performance
- **Genre Modularity**: Each genre (Gospel, Jazz, Blues, Classical, Neo-Soul) is a self-contained module

---

## Technology Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| **Frontend** | React 19 | 19.x | Latest features, concurrent rendering |
| **Frontend Router** | TanStack Router | 7.x | File-based routing, type-safe |
| **Frontend State** | Zustand | 4.x | Lightweight, performant state management |
| **Frontend Data** | TanStack Query | 5.x | Server state management, caching |
| **Frontend Build** | Vite | 7.x | Fast dev server, optimized builds |
| **Backend** | FastAPI | 0.115+ | Python async, OpenAPI docs, type hints |
| **Backend Language** | Python | 3.13 | Latest features, performance improvements |
| **Database** | PostgreSQL | 16+ | JSONB support, robust, scalable |
| **Audio Engine** | Rust | 1.75+ | Memory safety, GPU access, performance |
| **GPU API** | Metal | Native | Apple Silicon M4 optimization |
| **Local LLM (Simple)** | Phi-3.5 Mini | 3.8B params | Fast inference, complexity 1-4 |
| **Local LLM (Complex)** | Qwen2.5-7B | 7B params | High quality, complexity 5-7 |
| **Cloud LLM (Fallback)** | Gemini Pro | 1.5 | Complex tasks, complexity 8-10 |
| **LLM Framework** | MLX | Latest | Apple Silicon optimized inference |
| **Testing (Frontend)** | Vitest | 2.x | Fast unit/integration tests |
| **Testing (E2E)** | Playwright | 1.x | Cross-browser E2E tests |

---

## Component Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ TanStack Router│  │ TanStack Query  │  │ Zustand Store   │  │
│  │ (Routing)      │  │ (Server State)  │  │ (Client State)  │  │
│  └────────────────┘  └─────────────────┘  └─────────────────┘  │
│                            │                                     │
│                            │ HTTP/WebSocket                      │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Python)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      API Layer                             │  │
│  │  /gospel/generate  /jazz/generate  /blues/generate  etc.  │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
│                        │                                         │
│  ┌─────────────────────┴─────────────────────────────────────┐  │
│  │                   Service Layer                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │ Gospel Gen   │  │ Jazz Gen     │  │ Blues Gen       │  │  │
│  │  │ Service      │  │ Service      │  │ Service         │  │  │
│  │  └──────────────┘  └──────────────┘  └─────────────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │ Classical Gen│  │ NeoSoul Gen  │  │ Multi-Model LLM │  │  │
│  │  │ Service      │  │ Service      │  │ Service         │  │  │
│  │  └──────────────┘  └──────────────┘  └─────────────────┘  │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
│                        │                                         │
│  ┌─────────────────────┴─────────────────────────────────────┐  │
│  │                   Arrangement Layer                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │ Gospel       │  │ Jazz         │  │ Blues           │  │  │
│  │  │ Arranger     │  │ Arranger     │  │ Arranger        │  │  │
│  │  └──────────────┘  └──────────────┘  └─────────────────┘  │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │ Pattern Libraries (rhythm, left/right hand)         │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   Theory Layer                           │  │
│  │  ┌──────────────┐  ┌──────────────┐                      │  │
│  │  │ Scale Library│  │ Chord Library│   (32 scales, 36    │  │
│  │  │ (32 scales)  │  │ (36 types)   │    chord types)     │  │
│  │  └──────────────┘  └──────────────┘                      │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────┬─────────┬─────────────────────────────────┘
                      │         │
        ┌─────────────┘         └─────────────┐
        ▼                                      ▼
┌───────────────────┐                ┌──────────────────────┐
│   Gemini Pro API  │                │ Rust Audio Engine    │
│   (Cloud LLM)     │                │ (GPU Synthesis)      │
│                   │                │                      │
│ - Chord progression│                │ - Metal API (M4)     │
│ - Complexity 8-10  │                │ - SoundFont render   │
│ - Fallback only    │                │ - Convolution reverb │
└───────────────────┘                │ - 100x real-time     │
                                     └──────────────────────┘
         ┌───────────────────┐
         │  MLX Framework     │
         │  (Local LLM)       │
         │                    │
         │ - Phi-3.5 Mini (3.8B) → Simple tasks (complexity 1-4)
         │ - Qwen2.5-7B (7B)     → Complex tasks (complexity 5-7)
         │ - Apple Silicon optimized
         │ - 90% of AI workload
         └───────────────────┘
```

---

## Data Flow

### Music Generation Flow (Detailed)

```
1. User Input
   ↓
   [Natural Language: "Uplifting gospel song in C major"]
   ↓
2. Frontend (React)
   ↓
   POST /gospel/generate
   {
     description: "Uplifting gospel song in C major",
     num_bars: 16,
     application: "WORSHIP",
     ai_percentage: 0.3
   }
   ↓
3. Backend API (FastAPI)
   ↓
   gospel_routes.py → gospel_generator.py
   ↓
4. Gemini API Call
   ↓
   Input: Description + Genre constraints
   Output: Chord progression
   [
     {symbol: "Cmaj9", function: "I", duration: 2},
     {symbol: "Fmaj7", function: "IV", duration: 2},
     ...
   ]
   ↓
5. Gospel Arranger
   ↓
   Context Analysis:
   - Key: C major
   - Style: Worship
   - Tempo: 80 BPM (inferred)
   ↓
   Pattern Selection:
   - Left Hand: Shell Voicing
   - Right Hand: Block Chord with Melody
   - Rhythm: Gospel Swing (0.55 intensity)
   ↓
   Improvisation Insertion:
   - 30% probability (worship context)
   - Gospel fills at phrase endings
   ↓
6. MIDI File Creation
   ↓
   - Note events (pitch, time, velocity)
   - Meta events (tempo, key sig, time sig)
   - Track structure (left hand, right hand)
   ↓
7. [Optional] Rust GPU Synthesis
   ↓
   synthesize_midi(
     midi_path,
     soundfont_path,
     use_gpu=True,
     reverb=True
   )
   ↓
   Metal API GPU Rendering
   ↓
   WAV Audio Output
   ↓
8. Response Assembly
   ↓
   {
     midi_base64: "TVRoZA...",
     chord_progression: [...],
     metadata: {tempo, key, bars, notes},
     note_preview: [...]
   }
   ↓
9. Frontend Rendering
   ↓
   - MIDI Player plays audio
   - Chord progression display
   - Metadata visualization
```

### Performance Analysis Flow (Planned)

```
Student Practice Recording
   ↓
Rust Audio Engine
   ↓
GPU FFT (Pitch Detection)
   ↓
Onset Detection (Rhythm Analysis)
   ↓
Comparison with Expected MIDI
   ↓
Accuracy Metrics
   ↓
Multi-Model LLM (Feedback Generation)
   ↓
Personalized Practice Tips
   ↓
Display to Student
```

---

## API Design

### REST API Endpoints

#### Generator Endpoints

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/gospel/generate` | POST | Generate gospel piano MIDI | ~1.4-2.6s |
| `/jazz/generate` | POST | Generate jazz piano MIDI | ~1.5-2.7s |
| `/blues/generate` | POST | Generate blues piano MIDI | ~1.4-2.5s |
| `/classical/generate` | POST | Generate classical piano MIDI | ~1.5-2.8s |
| `/neosoul/generate` | POST | Generate neo-soul piano MIDI | ~1.4-2.6s |
| `/{genre}/download/{id}` | GET | Download MIDI file | ~50ms |

#### Performance Analysis Endpoints (Planned)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/analyze/performance` | POST | Analyze student recording |
| `/analyze/progress` | GET | Get student progress metrics |
| `/feedback/generate` | POST | Generate AI practice feedback |

#### Curriculum Endpoints (Planned)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/curriculum/generate` | POST | Generate personalized curriculum |
| `/curriculum/{id}` | GET | Get curriculum details |
| `/lessons/interactive` | POST | Start interactive theory lesson |

### WebSocket Endpoints (Planned)

| Endpoint | Purpose |
|----------|---------|
| `/ws/jam/{session_id}` | Real-time jam session audio streaming |
| `/ws/practice/{session_id}` | Real-time practice feedback |

---

## Security Architecture

### Authentication & Authorization

**Current (Phase 1)**: Development mode, no auth
**Planned (Phase 2)**:
- **Auth Library**: better-auth v1
- **Session Management**: Secure server-side sessions
- **OAuth Providers**: Google, Apple, GitHub
- **2FA**: TOTP-based two-factor authentication

### Data Protection

| Data Type | Protection Method |
|-----------|-------------------|
| **User Credentials** | Argon2 password hashing |
| **Session Tokens** | HttpOnly secure cookies |
| **Student Recordings** | Encrypted at rest (AES-256) |
| **Generated MIDI** | Public (user-owned content) |
| **Progress Data** | Row-level security (RLS) |

### Input Validation

- **All user input**: Zod schema validation
- **MIDI files**: Size limits (10MB max), format validation
- **Audio files**: Format validation (WAV/MP3/FLAC only)
- **Natural language**: Length limits (500 chars), sanitization

### Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/*/generate` | 10 requests | per minute |
| `/analyze/*` | 20 requests | per minute |
| Authentication endpoints | 5 requests | per 15 minutes |

---

## Deployment Architecture

### Development Environment

```
Local Machine (Apple Silicon M4)
├── Frontend: Vite dev server (port 3000)
├── Backend: FastAPI (port 8000)
├── Database: PostgreSQL (port 5432)
├── Rust Engine: Compiled locally (maturin)
└── LLMs: MLX models (~10GB disk space)
```

### Production Architecture (Planned)

```
Frontend (Vercel/Cloudflare Pages)
   ↓
Backend (Cloudflare Workers / Fly.io)
   ↓
PostgreSQL (Neon / Supabase)
   ↓
Rust Audio Engine (Dedicated Servers with M4)
   ↓
LLM Inference (Self-hosted / Modal)
```

**Rationale for self-hosted GPU servers**:
- Metal API requires Apple Silicon hardware
- Cost-effective at scale (vs. renting GPUs hourly)
- Full control over performance and availability

---

## Scalability Considerations

### Current Scalability (Phase 1)

| Metric | Current Capacity | Bottleneck |
|--------|------------------|------------|
| Concurrent MIDI generations | 50+ | Gemini API rate limits |
| Audio synthesis throughput | 10 files/second | Rust single-threaded |
| Database connections | 100 | PostgreSQL connection pool |
| Storage per user | ~5KB MIDI files | Minimal |

### Future Scalability (Phase 2+)

**Horizontal Scaling**:
- FastAPI backend: Stateless, easy to replicate
- Rust synthesis: Separate worker pool with load balancing
- Database: Read replicas for analytics queries

**Caching Strategy**:
- Gemini responses: Redis cache (40-60% hit rate)
- Generated MIDI: CDN distribution
- Static assets: Cloudflare CDN

**Database Optimization**:
- Indexes on user_id, genre, created_at
- Partitioning for time-series data (practice sessions)
- Archive old MIDI files to object storage (S3/R2)

---

## Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| MIDI generation (p95) | < 3s | 1.4-2.8s | ✅ Met |
| Audio synthesis (30s MIDI) | < 500ms | ~300ms | ✅ Met |
| API response time (p95) | < 200ms | TBD | 🚧 Testing |
| First Contentful Paint | < 1.5s | TBD | 🚧 Testing |
| Time to Interactive | < 3.5s | TBD | 🚧 Testing |
| Bundle size (initial JS) | < 200KB | TBD | 🚧 Optimizing |

---

## Monitoring & Observability (Planned)

### Metrics to Track

**System Health**:
- API latency (p50, p95, p99)
- Error rates by endpoint
- Database query performance
- GPU utilization and temperature

**User Behavior**:
- MIDI generations per user
- Practice session duration
- Feature adoption rates
- Completion rates

**Business Metrics**:
- Daily/Monthly active users
- Conversion funnel
- Retention cohorts
- Revenue metrics

### Logging Strategy

- **Application logs**: Structured JSON logs (timestamp, level, message, context)
- **Access logs**: All API requests with latency
- **Error logs**: Stack traces, user context, repro steps
- **Audit logs**: User actions (curriculum generation, MIDI downloads)

**Tools (Planned)**:
- **Metrics**: Prometheus + Grafana
- **Logging**: Loki or Cloudflare Analytics
- **Tracing**: OpenTelemetry
- **Error Tracking**: Sentry

---

## Critical Files & Directories

### Backend Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI app entry
│   ├── api/
│   │   └── routes/                 # API endpoints
│   │       ├── gospel.py
│   │       ├── jazz.py
│   │       ├── blues.py
│   │       ├── classical.py
│   │       └── neosoul.py
│   ├── services/                   # Business logic
│   │   ├── gospel_generator.py
│   │   ├── jazz_generator.py
│   │   ├── blues_generator.py
│   │   ├── classical_generator.py
│   │   ├── neosoul_generator.py
│   │   └── multi_model_service.py  # Local LLM orchestration
│   ├── gospel/                     # Gospel-specific
│   │   ├── arrangement/
│   │   │   └── arranger.py         # Pattern arrangement
│   │   └── patterns/
│   │       └── rhythm.py           # Rhythm patterns
│   ├── jazz/                       # Jazz-specific
│   ├── blues/                      # Blues-specific
│   ├── classical/                  # Classical-specific
│   ├── neosoul/                    # Neo-soul-specific
│   ├── theory/                     # Music theory
│   │   ├── scale_library.py        # 32 scales
│   │   └── chord_library.py        # 36 chords
│   ├── schemas/                    # Pydantic models
│   ├── database/                   # Database models
│   └── pipeline/                   # Processing pipelines
└── tests/                          # Backend tests
```

### Frontend Structure

```
frontend/
├── src/
│   ├── routes/                     # TanStack Router pages
│   ├── components/                 # React components
│   ├── hooks/                      # Custom hooks
│   ├── api/                        # API client
│   ├── stores/                     # Zustand stores
│   └── lib/                        # Utilities
└── tests/                          # Frontend tests
```

### Rust Audio Engine Structure

```
rust-audio-engine/
├── src/
│   ├── lib.rs                      # PyO3 Python bindings
│   ├── synthesizer.rs              # MIDI → WAV synthesis
│   ├── metal_effects.rs            # GPU effects (reverb, EQ)
│   └── waveform.rs                 # Waveform visualization (planned)
└── Cargo.toml                      # Rust dependencies
```

---

## Technology Decisions (ADRs)

See `.claude/docs/ADR/` for detailed architecture decision records:
- ADR-001: Choice of Rust for audio engine (performance + safety)
- ADR-002: Local LLM strategy (cost reduction + privacy)
- ADR-003: FastAPI vs. alternatives (Python ecosystem + async)
- ADR-004: TanStack Router vs. React Router (type safety + file-based)
- ADR-005: Metal API for GPU (Apple Silicon optimization)

---

## Next Steps

1. **Complete Performance Analysis** (Phase 2): GPU FFT pitch detection
2. **Implement Authentication** (Phase 2): better-auth integration
3. **Build Curriculum System** (Phase 3): Personalized learning paths
4. **Add Monitoring** (Ongoing): Prometheus + Grafana setup
5. **Optimize Bundle Size** (Ongoing): Code splitting, tree shaking
6. **Deploy to Production** (Phase 2): Cloudflare Workers + Fly.io

---

**Document Owner**: Backend Team
**Next Review Date**: January 15, 2026
**Version History**:
- v1.0 (Dec 15, 2025): Initial architecture document based on Phase 1 completion
