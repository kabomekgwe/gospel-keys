# Product Requirements Document: Gospel Keys

**Version:** 1.0
**Last Updated:** December 15, 2025
**Status:** In Development
**Project Type:** Music Education Platform

---

## Overview

Gospel Keys is a comprehensive music education platform that combines AI-powered curriculum generation, GPU-accelerated MIDI synthesis, and real-time performance analysis for learning piano and music theory across multiple genres (Gospel, Jazz, Blues, Classical, Neo-Soul).

**Mission:** Democratize professional-level music education through AI-powered personalization and GPU-accelerated audio synthesis.

---

## Problem Statement

Traditional music education platforms face several limitations:
- **High Cost**: Cloud-based AI processing creates unsustainable costs at scale
- **Generic Content**: One-size-fits-all curriculum doesn't adapt to individual learning styles
- **Limited Feedback**: Students receive delayed or no feedback on practice sessions
- **Technical Quality**: Poor audio quality and slow rendering in web-based platforms
- **Genre Coverage**: Most platforms focus on classical/pop, ignoring gospel, jazz, blues, neo-soul

**Our Solution**: Local-first AI processing (90% cost reduction) + GPU-accelerated synthesis (100x real-time) + multi-genre expertise + real-time performance analysis.

---

## Goals

### Primary Goals
- ✅ **Launched**: Multi-genre MIDI generation (Gospel, Jazz, Blues, Classical, Neo-Soul)
- ✅ **Launched**: GPU-accelerated audio synthesis with M4 Metal API
- ✅ **Launched**: Local LLM integration (Phi-3.5 Mini + Qwen2.5-7B)
- 🚧 **In Progress**: Real-time performance analysis
- 📋 **Planned**: Personalized learning paths
- 📋 **Planned**: Interactive music theory lessons

### Secondary Goals
- 📋 AI-generated practice exercises
- 📋 Automatic music transcription
- 📋 Multi-format export (WAV, MP3, FLAC, PDF sheet music)
- 📋 Collaborative learning features (real-time jam sessions)

---

## User Stories

### Student Users
- As a **beginner student**, I want to **generate practice exercises at my level** so that **I can progress without feeling overwhelmed**.
- As an **intermediate student**, I want to **receive real-time feedback on my playing** so that **I can correct mistakes immediately**.
- As an **advanced student**, I want to **explore multiple musical genres** so that **I can diversify my skills**.

### Teacher Users
- As a **music teacher**, I want to **assign personalized practice material** so that **each student progresses at their optimal pace**.
- As a **music teacher**, I want to **track student progress automatically** so that **I can focus on teaching rather than administration**.

### Content Creator Users
- As a **composer**, I want to **quickly sketch musical ideas** so that **I can capture inspiration without manual MIDI entry**.
- As a **arranger**, I want to **generate genre-authentic arrangements** so that **I can explore different styles efficiently**.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| **FR-001** | Generate MIDI arrangements from natural language | Must Have | ✅ Complete |
| **FR-002** | Support 5 genres (Gospel, Jazz, Blues, Classical, Neo-Soul) | Must Have | ✅ Complete |
| **FR-003** | GPU-accelerated MIDI-to-audio synthesis | Must Have | ✅ Complete |
| **FR-004** | 32 musical scales available | Must Have | ✅ Complete |
| **FR-005** | 36 chord types available | Must Have | ✅ Complete |
| **FR-006** | Genre-specific rhythm patterns | Must Have | ✅ Complete |
| **FR-007** | Real-time performance analysis (pitch/rhythm accuracy) | Must Have | 🚧 In Progress |
| **FR-008** | Personalized learning path generation | Should Have | 📋 Planned |
| **FR-009** | Interactive music theory lessons with AI tutor | Should Have | 📋 Planned |
| **FR-010** | Automatic music transcription (audio → sheet music) | Should Have | 📋 Planned |
| **FR-011** | Multi-format export (WAV, MP3, FLAC, PDF) | Should Have | 📋 Planned |
| **FR-012** | Progress tracking dashboard | Should Have | 📋 Planned |
| **FR-013** | Real-time jam sessions (low-latency collaboration) | Nice to Have | 📋 Planned |
| **FR-014** | Composition assistant with AI | Nice to Have | 📋 Planned |

### Non-Functional Requirements

| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| **NFR-001** | MIDI generation latency | < 2.5s (end-to-end) | ✅ Achieved (1.4-2.8s) |
| **NFR-002** | Audio synthesis speed | 100x real-time | ✅ Achieved |
| **NFR-003** | Performance analysis accuracy | > 91% (pitch/rhythm) | 🚧 Target |
| **NFR-004** | System availability | 99.9% uptime | 🚧 Target |
| **NFR-005** | Concurrent users | 50+ simultaneous generations | ✅ Achieved |
| **NFR-006** | Local LLM response time (simple) | < 200ms | ✅ Achieved |
| **NFR-007** | Local LLM response time (complex) | < 3s | ✅ Achieved |
| **NFR-008** | GPU memory usage | < 2GB VRAM | ✅ Achieved |
| **NFR-009** | API response time (p95) | < 200ms | 🚧 Target |
| **NFR-010** | First Contentful Paint | < 1.5s | 🚧 Target |

---

## Out of Scope

### Explicitly Not Included
- ❌ **DAW functionality**: Not a full digital audio workstation (use Ableton, Logic, etc.)
- ❌ **Sample library**: Not a sample/loop library platform
- ❌ **Social network features**: Not a musician social network (focus on education)
- ❌ **Live streaming**: Not a live performance streaming platform
- ❌ **Music marketplace**: Not selling/licensing generated music
- ❌ **Mobile apps (v1)**: Web-first approach, mobile apps planned for v2
- ❌ **Video lessons (v1)**: Text + audio only initially, video in future phases

---

## Success Metrics

### Adoption Metrics
- **Target Users (Year 1)**: 10,000 registered users
- **Target Active Users (MAU)**: 3,000 monthly active users
- **Target Retention (30-day)**: 40% retention rate
- **Target Conversion (free→paid)**: 15% conversion rate

### Engagement Metrics
- **MIDI Generations per User**: Average 50 generations/month
- **Practice Time per User**: Average 5 hours/week
- **Lesson Completion Rate**: 60% completion of started lessons

### Quality Metrics
- **Performance Analysis Accuracy**: > 91% (industry standard)
- **User Satisfaction (NPS)**: > 50 (promoters)
- **Bug Rate**: < 1 critical bug per 1000 users per month

### Financial Metrics
- **Cost per User (AI processing)**: < $2/month (90% reduction vs cloud-only)
- **Gross Margin**: > 70% (due to local LLM usage)
- **LTV:CAC Ratio**: > 3:1

---

## Timeline

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| **Phase 1: Core Generator System** | Dec 2025 | ✅ Complete |
| ├─ Gospel/Jazz/Blues/Classical/Neo-Soul generators | Dec 2025 | ✅ Complete |
| ├─ 32 scales + 36 chords | Dec 2025 | ✅ Complete |
| ├─ Rust GPU synthesis engine | Dec 2025 | ✅ Complete |
| ├─ Local LLM integration (Phi-3.5 + Qwen2.5) | Dec 2025 | ✅ Complete |
| └─ Comprehensive documentation | Dec 2025 | ✅ Complete |
| **Phase 2: Performance Analysis** | Jan 2026 | 🚧 In Progress |
| ├─ Real-time pitch detection (GPU FFT) | Jan 2026 | 📋 Planned |
| ├─ Rhythm accuracy analysis | Jan 2026 | 📋 Planned |
| ├─ Dynamic expression analysis | Jan 2026 | 📋 Planned |
| └─ AI-powered feedback generation | Jan 2026 | 📋 Planned |
| **Phase 3: Personalized Learning** | Feb 2026 | 📋 Planned |
| ├─ Student profile system | Feb 2026 | 📋 Planned |
| ├─ AI curriculum generation | Feb 2026 | 📋 Planned |
| ├─ Adaptive difficulty system | Feb 2026 | 📋 Planned |
| └─ Progress tracking dashboard | Feb 2026 | 📋 Planned |
| **Phase 4: Content Expansion** | Mar 2026 | 📋 Planned |
| ├─ AI-generated practice exercises | Mar 2026 | 📋 Planned |
| ├─ Interactive theory lessons | Mar 2026 | 📋 Planned |
| ├─ Automatic transcription | Mar 2026 | 📋 Planned |
| └─ Composition assistant | Mar 2026 | 📋 Planned |
| **Phase 5: Collaboration & Export** | Apr 2026 | 📋 Planned |
| ├─ Real-time jam sessions (WebRTC) | Apr 2026 | 📋 Planned |
| ├─ Multi-format export | Apr 2026 | 📋 Planned |
| ├─ Sheet music generation | Apr 2026 | 📋 Planned |
| └─ Asynchronous collaboration | Apr 2026 | 📋 Planned |

---

## Dependencies

### External Dependencies
- **Gemini Pro API**: Chord progression generation (fallback for complexity 8-10 tasks)
- **SoundFont Library**: High-quality piano samples for synthesis
- **Metal API**: Apple Silicon GPU acceleration (M4 chip)
- **MLX Framework**: Local LLM inference (Apple optimized)

### Internal Dependencies
- **Rust Audio Engine**: Core synthesis and effects processing
- **FastAPI Backend**: API layer and orchestration
- **React Frontend**: TanStack Router + TanStack Query
- **PostgreSQL Database**: User data, progress tracking, content storage
- **Zustand**: Frontend state management

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Gemini API rate limits** | Medium | High | Cache responses aggressively, use local LLMs for 90% of tasks |
| **GPU compatibility issues** | Low | Medium | CPU fallback implemented, test on multiple Mac models |
| **LLM quality variance** | Medium | Medium | Qwen2.5-7B proven capable, fallback to Gemini for complex tasks |
| **Real-time latency challenges** | High | High | WebRTC + buffer optimization, target <20ms latency |
| **User adoption pace** | High | High | Freemium tier, viral features (composition assistant) |
| **Content licensing** | Medium | Medium | User-generated focus, royalty-free SoundFonts |
| **Transcription accuracy** | Medium | Medium | Hybrid AI + rule-based approach, target 86%+ accuracy |

---

## Stakeholders

- **Product Owner**: Development Team
- **Technical Lead**: Backend Team
- **Musical Consultants**: Professional pianists (Gospel, Jazz, Blues, Classical, Neo-Soul)
- **Beta Testers**: 50+ music students and teachers
- **End Users**: Music students (beginner to advanced), music teachers, composers

---

## Approval

| Role | Name | Approval Date | Signature |
|------|------|---------------|-----------|
| Product Owner | [To be filled] | | |
| Technical Lead | [To be filled] | | |
| Musical Director | [To be filled] | | |

---

**Document Owner**: Development Team
**Next Review Date**: January 15, 2026
**Version History**:
- v1.0 (Dec 15, 2025): Initial PRD based on Phase 1 completion
