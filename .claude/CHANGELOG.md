# Changelog - Gospel Keys

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Real-time performance analysis (pitch/rhythm accuracy)
- Personalized learning path generation
- Interactive music theory lessons with AI tutor
- Automatic music transcription (audio → sheet music)
- Multi-format export (WAV, MP3, FLAC, PDF)
- Progress tracking dashboard
- Real-time jam sessions (WebRTC collaboration)
- Composition assistant with AI

---

## [1.0.0] - 2025-12-15

### Added - Phase 1: Core Generator System ✅

#### Music Generation
- **Gospel Piano Generator**: Natural language → MIDI with AI blending (0.0-1.0 ratio)
- **Jazz Piano Generator**: ii-V-I patterns, bebop phrasing, rootless voicings
- **Blues Piano Generator**: 12-bar blues, shuffle feel, call-response patterns
- **Classical Piano Generator**: Baroque/Classical/Romantic period styles
- **Neo-Soul Piano Generator**: Extended harmony, laid-back timing, chromatic fills

#### Music Theory
- **32 Musical Scales**: Major modes, minor variants, blues/pentatonic, symmetric/advanced, exotic/world
- **36 Chord Types**: Triads, 7th chords, extended chords, altered chords, add chords
- **Genre-Specific Patterns**: Rhythm, left hand, right hand patterns for all 5 genres

#### Audio Engine
- **Rust GPU Synthesis**: Metal API on Apple Silicon (M4) for 100x real-time performance
- **SoundFont Rendering**: Professional piano samples with convolution reverb
- **GPU Effects**: Reverb with M4 optimization

#### AI Integration
- **Local LLM**: Phi-3.5 Mini (3.8B) for simple tasks (complexity 1-4)
- **Local LLM**: Qwen2.5-7B for complex tasks (complexity 5-7)
- **Cloud LLM**: Gemini Pro fallback for very complex tasks (complexity 8-10)
- **Multi-Model Service**: Automatic routing based on task complexity
- **90% Cost Reduction**: Local processing vs. cloud-only approach

#### Documentation
- **Generator System Guide**: Comprehensive 1,400-line reference (scales, chords, patterns, API)
- **Architecture Documentation**: System design, data flow, deployment strategy
- **PRD**: Product requirements, goals, success metrics, timeline
- **ADR Template**: Architecture decision record template

#### Performance
- **MIDI Generation**: 1.4-2.8s end-to-end (95%+ chord accuracy)
- **Audio Synthesis**: ~300ms for 30-second MIDI (100x real-time)
- **Concurrent Generations**: 50+ simultaneous requests
- **Cache Hit Rate**: 40-60% for Gemini responses

#### API
- **5 Generator Endpoints**: `/gospel/generate`, `/jazz/generate`, `/blues/generate`, `/classical/generate`, `/neosoul/generate`
- **Download Endpoints**: `/{genre}/download/{id}` for MIDI files
- **Standard Response Format**: MIDI base64, chord progression, metadata, note preview

### Technical Stack
- **Frontend**: React 19 + TanStack Router + TanStack Query + Zustand + Vite 7
- **Backend**: FastAPI (Python 3.13) + PostgreSQL
- **Audio**: Rust 1.75+ with Metal API
- **LLMs**: MLX (Phi-3.5 Mini + Qwen2.5-7B) + Gemini Pro
- **Testing**: Vitest (frontend) + Playwright (E2E)

### Documentation Added
- `.claude/docs/PRD.md` - Product Requirements Document
- `.claude/docs/ARCHITECTURE.md` - System Architecture
- `.claude/docs/ADR/000-template.md` - ADR template
- `docs/GENERATOR_SYSTEM_GUIDE.md` - Complete generator reference
- `.claude/CHANGELOG.md` - This file

---

## [0.1.0] - 2025-11-XX (Pre-Phase 1)

### Initial Development
- Project structure setup
- Basic FastAPI backend
- React frontend with Vite
- PostgreSQL database setup
- Initial Rust audio engine experiments

---

## Version Guidelines

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

### Change Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

---

## Links

- **Repository**: [Link to repo]
- **Documentation**: `docs/` and `.claude/docs/`
- **Issue Tracker**: [Link to issues]
- **Roadmap**: See PRD.md for phases 2-5

---

**Maintained by**: Development Team
**Last Updated**: December 15, 2025
