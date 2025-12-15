# EPIC-3: Integration & Infrastructure

**Epic**: Real-Time Integration & Production Infrastructure
**Status**: 📋 Planned
**Priority**: Must Have
**Total Effort**: 34 story points
**Timeline**: 6-8 weeks
**Dependencies**: Phase 2 (EPIC-2) complete

---

## Overview

Phase 3 integrates the performance analysis capabilities from Phase 2 with the music generation from Phase 1, creating a complete real-time practice experience. This epic focuses on:

1. **Real-time streaming** of audio analysis via WebSocket
2. **Database schema** for progress tracking and session management
3. **Frontend integration** of analysis visualizations
4. **API layer** connecting all components
5. **Production infrastructure** (authentication, deployment, monitoring)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| WebSocket latency | <100ms | Round-trip analysis result delivery |
| Database query time | <50ms | P95 for progress retrieval |
| Frontend update rate | 60 FPS | Smooth visualization updates |
| Session reliability | >99.9% | No dropped connections |
| API response time | <200ms | P95 for all endpoints |
| System uptime | >99.5% | Production availability |

---

## User Stories

### 🎯 STORY-3.1: WebSocket Real-Time Analysis (13 points)
**Priority**: Must Have
**Effort**: 13 story points
**Timeline**: Week 1-3

**As a** piano student practicing in real-time
**I want** immediate feedback on my performance as I play
**So that** I can adjust my technique during practice, not after

**Acceptance Criteria**:
- [ ] WebSocket server implemented (FastAPI + python-socketio)
- [ ] Audio streaming from frontend to backend
- [ ] Real-time analysis pipeline (pitch + onset + dynamics)
- [ ] Analysis results streamed back to frontend
- [ ] Latency <100ms (round-trip)
- [ ] Connection recovery on disconnect
- [ ] Session state management
- [ ] Error handling and logging
- [ ] Load testing (10 concurrent sessions)

**Technical Details**:
- FastAPI WebSocket endpoint
- Audio chunking (512-1024 samples)
- Async processing pipeline
- Redis for session state (optional)
- Connection pooling

---

### 🗄️ STORY-3.2: Database Schema & Progress Tracking (8 points)
**Priority**: Must Have
**Effort**: 8 story points
**Timeline**: Week 2-3

**As a** piano student
**I want** my practice history and progress tracked
**So that** I can see improvement over time

**Acceptance Criteria**:
- [ ] PostgreSQL schema for performance tracking
- [ ] Tables: users, sessions, performances, analysis_results
- [ ] Migrations with Alembic
- [ ] CRUD operations for all entities
- [ ] Query optimization (indexes)
- [ ] Data retention policy
- [ ] Analytics queries (progress charts)
- [ ] API endpoints for data access

**Schema Design**:
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    skill_level VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Practice sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    piece_name VARCHAR(255),
    genre VARCHAR(50),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER
);

-- Performance recordings
CREATE TABLE performances (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    audio_path VARCHAR(500),
    midi_path VARCHAR(500),
    created_at TIMESTAMP
);

-- Analysis results
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY,
    performance_id UUID REFERENCES performances(id),
    pitch_accuracy FLOAT,
    rhythm_accuracy FLOAT,
    dynamics_range FLOAT,
    overall_score FLOAT,
    feedback_json JSONB,
    created_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_performances_session_id ON performances(session_id);
CREATE INDEX idx_analysis_results_performance_id ON analysis_results(performance_id);
```

---

### 🎨 STORY-3.3: Frontend Visualization & Integration (8 points)
**Priority**: Must Have
**Effort**: 8 story points
**Timeline**: Week 3-5

**As a** piano student
**I want** to see real-time visualizations of my performance
**So that** I can understand my strengths and weaknesses visually

**Acceptance Criteria**:
- [ ] Real-time pitch display (note accuracy chart)
- [ ] Onset timing visualization (rhythm grid)
- [ ] Dynamics meter (velocity over time)
- [ ] Overall score display
- [ ] Feedback panel with AI suggestions
- [ ] Practice history charts
- [ ] Progress dashboard
- [ ] Responsive design (mobile + desktop)

**Components**:
```typescript
// Real-time analysis display
<PerformanceMonitor />
  ├── <PitchVisualization />     // Real-time pitch accuracy
  ├── <RhythmGrid />             // Onset timing visualization
  ├── <DynamicsMeter />          // Velocity over time
  └── <FeedbackPanel />          // AI-powered suggestions

// Progress dashboard
<ProgressDashboard />
  ├── <PracticeHistory />        // Session history timeline
  ├── <AccuracyTrends />         // Pitch/rhythm accuracy over time
  ├── <SkillLevelChart />        // Improvement metrics
  └── <GoalTracking />           // Practice goals and achievements
```

---

### 🔐 STORY-3.4: Authentication & User Management (3 points)
**Priority**: Should Have
**Effort**: 3 story points
**Timeline**: Week 4

**As a** user of the platform
**I want** secure authentication and profile management
**So that** my practice data is private and persistent

**Acceptance Criteria**:
- [ ] better-auth integration (OAuth2 + email/password)
- [ ] Session management (JWT tokens)
- [ ] User profile CRUD endpoints
- [ ] Password reset flow
- [ ] Email verification
- [ ] Protected API routes
- [ ] Frontend auth guards
- [ ] Logout and session cleanup

**Auth Stack**:
- better-auth v1 (backend)
- OAuth2 providers (Google, GitHub)
- Secure cookies (httpOnly, secure, sameSite)
- CSRF protection

---

### 🚀 STORY-3.5: Production Deployment & CI/CD (2 points)
**Priority**: Should Have
**Effort**: 2 story points
**Timeline**: Week 5-6

**As a** developer
**I want** automated deployment and monitoring
**So that** we can ship updates reliably

**Acceptance Criteria**:
- [ ] Docker containerization (frontend + backend + Rust)
- [ ] docker-compose for local development
- [ ] GitHub Actions CI/CD pipeline
- [ ] Automated testing on PR
- [ ] Staging environment
- [ ] Production deployment script
- [ ] Environment variable management
- [ ] Logging and monitoring (OpenTelemetry)

**Infrastructure**:
```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [postgres, redis]

  postgres:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Real-time Components                                     │   │
│  │  - <PerformanceMonitor /> (WebSocket)                     │   │
│  │  - <PitchVisualization />                                 │   │
│  │  - <RhythmGrid />                                         │   │
│  │  - <DynamicsMeter />                                      │   │
│  │  - <FeedbackPanel />                                      │   │
│  └───────────────────────────┬──────────────────────────────┘   │
└────────────────────────────┬─┘                                   │
                             │ WebSocket (bidirectional)
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  WebSocket Manager                                        │   │
│  │  - Audio stream receiver                                 │   │
│  │  - Analysis pipeline orchestrator                        │   │
│  │  - Result broadcaster                                    │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Analysis Pipeline (Async)                               │   │
│  │  - detect_pitch()                                        │   │
│  │  - detect_onsets_python()                                │   │
│  │  - analyze_dynamics_python()                             │   │
│  │  - feedback_generator.generate_feedback()                │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Database Service (PostgreSQL)                           │   │
│  │  - Store sessions, performances, analysis results        │   │
│  │  - Query progress data                                   │   │
│  │  - Generate analytics                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              Rust Audio Engine (PyO3 bindings)                  │
│  - detect_pitch()                                               │
│  - detect_onsets_python()                                       │
│  - analyze_dynamics_python()                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Sequence

### Week 1-2: WebSocket Infrastructure (STORY-3.1)
1. Set up WebSocket server (FastAPI)
2. Implement audio streaming (frontend → backend)
3. Create async analysis pipeline
4. Stream results back to frontend
5. Test latency and reliability

### Week 2-3: Database & API (STORY-3.2)
1. Design and implement PostgreSQL schema
2. Create Alembic migrations
3. Build CRUD endpoints
4. Add analytics queries
5. Test performance with realistic data

### Week 3-5: Frontend Integration (STORY-3.3)
1. Build real-time visualization components
2. Integrate WebSocket client
3. Create progress dashboard
4. Add practice history views
5. Implement responsive design

### Week 4: Authentication (STORY-3.4)
1. Integrate better-auth
2. Set up OAuth2 providers
3. Implement protected routes
4. Add user profile management
5. Test auth flows

### Week 5-6: Deployment (STORY-3.5)
1. Create Docker containers
2. Set up docker-compose
3. Configure CI/CD pipeline
4. Deploy to staging
5. Production deployment

---

## Risk Management

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| WebSocket performance issues | High | Medium | Load testing, connection pooling, Redis caching |
| Database query slow | Medium | Low | Proper indexing, query optimization, caching |
| Frontend visualization lag | High | Medium | RequestAnimationFrame, Web Workers, canvas optimization |
| Auth security vulnerabilities | Critical | Low | Security audit, better-auth best practices, OWASP compliance |
| Deployment complexity | Medium | Medium | Comprehensive documentation, staging environment testing |

---

## Dependencies

**External**:
- FastAPI WebSocket support (built-in)
- python-socketio (alternative)
- PostgreSQL 16
- Redis 7 (optional, for session state)
- better-auth v1
- Docker & docker-compose

**Internal**:
- Phase 2 analysis functions (COMPLETE)
- Phase 1 music generation (COMPLETE)
- Rust audio engine (COMPLETE)

---

## Testing Strategy

### Unit Tests
- WebSocket connection handlers
- Database CRUD operations
- Frontend components

### Integration Tests
- Full analysis pipeline (audio → results)
- Database queries with realistic data
- Auth flows (login, logout, password reset)

### E2E Tests (Playwright)
- Real-time practice session
- Progress tracking
- Dashboard navigation

### Performance Tests
- WebSocket load testing (10+ concurrent users)
- Database query benchmarks
- Frontend rendering performance

---

## Definition of Done

- [ ] All 5 stories completed
- [ ] All tests passing (unit + integration + E2E)
- [ ] Code reviewed and merged
- [ ] Documentation complete
- [ ] Staging deployment successful
- [ ] Performance metrics met
- [ ] Security audit passed
- [ ] Production deployment ready

---

**Created**: December 15, 2025
**Owner**: Full-Stack Team
**Next Review**: Week 2 (progress check)
