# EPIC-2: Real-Time Performance Analysis System

**Status**: 📋 Planned
**Phase**: Phase 2
**Target Date**: January 2026
**Owner**: Development Team
**Priority**: Must Have (NFR-003)

---

## Epic Overview

Implement a comprehensive real-time performance analysis system that evaluates student piano playing across pitch accuracy, rhythm precision, and dynamic expression. The system will leverage GPU acceleration for low-latency audio processing and AI-powered feedback generation.

## Business Value

**Problem**: Students currently receive no real-time feedback on their practice sessions, leading to:
- Reinforcement of incorrect technique
- Slow skill progression
- Reduced engagement and motivation
- No objective measurement of improvement

**Solution**: Real-time analysis provides:
- Immediate corrective feedback (within 100ms)
- Objective skill assessment (>91% accuracy target)
- Personalized coaching recommendations
- Progress tracking over time

**Impact**:
- **User Retention**: Expected +25% increase (industry benchmark)
- **Practice Quality**: More effective practice sessions
- **Differentiation**: Key competitive advantage vs traditional platforms
- **Monetization**: Premium feature for conversion funnel

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Pitch Detection Accuracy** | >91% | % of correctly identified notes vs ground truth |
| **Rhythm Accuracy** | >91% | % of correctly timed note events (±50ms tolerance) |
| **Analysis Latency** | <100ms | Time from audio input to feedback display |
| **False Positive Rate** | <5% | Incorrect feedback instances per session |
| **User Satisfaction** | >4.2/5 | Post-practice survey rating |
| **Feature Adoption** | >60% | % of active users enabling analysis |

## Technical Requirements

### Non-Functional Requirements
- **NFR-003**: Performance analysis accuracy >91% (pitch/rhythm)
- **Latency**: <100ms end-to-end (audio → feedback)
- **GPU Utilization**: Metal API for FFT and signal processing
- **CPU Usage**: <25% on M4 (leave headroom for synthesis)
- **Memory**: <500MB for analysis buffers

### Functional Requirements
- Real-time pitch detection (fundamental frequency estimation)
- Note onset/offset detection for rhythm analysis
- Dynamic range analysis (pianissimo to fortissimo)
- Tempo/timing drift detection
- Practice session recording and playback
- AI-generated feedback with actionable tips

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Audio Input  │→ │  Visualizer  │  │  Feedback    │     │
│  │ (WebAudio)   │  │  (Waveform)  │  │  Display     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↓                                     ↑             │
└─────────┼─────────────────────────────────────┼─────────────┘
          │                                     │
          │ WebSocket (streaming audio)         │ WebSocket (feedback)
          ↓                                     │
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Performance Analysis Orchestrator             │  │
│  │  - Audio buffering                                    │  │
│  │  - Analysis coordination                              │  │
│  │  - Feedback generation                                │  │
│  └───┬──────────────────────────┬───────────────────┬───┘  │
│      ↓                          ↓                   ↓      │
│  ┌────────────┐          ┌────────────┐      ┌──────────┐ │
│  │   Pitch    │          │  Rhythm    │      │ Dynamics │ │
│  │  Analyzer  │          │  Analyzer  │      │ Analyzer │ │
│  └─────┬──────┘          └─────┬──────┘      └────┬─────┘ │
│        │                       │                   │       │
└────────┼───────────────────────┼───────────────────┼───────┘
         ↓                       ↓                   ↓
┌─────────────────────────────────────────────────────────────┐
│              Rust Audio Engine (GPU-Accelerated)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  GPU FFT     │  │  Onset       │  │  RMS/Peak    │     │
│  │  (Metal)     │  │  Detection   │  │  Analysis    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
         ↓                       ↓                   ↓
┌─────────────────────────────────────────────────────────────┐
│                   AI Feedback Service                       │
│  - Multi-model LLM (Qwen2.5-7B for complexity 6-7)         │
│  - Generate actionable coaching tips                        │
│  - Contextual feedback based on skill level                 │
└─────────────────────────────────────────────────────────────┘
```

## Stories Breakdown

| ID | Story | Priority | Effort | Dependencies |
|----|-------|----------|--------|--------------|
| **STORY-2.1** | Real-time pitch detection with GPU FFT | Must Have | 8 pts | None |
| **STORY-2.2** | Rhythm accuracy analysis | Must Have | 5 pts | STORY-2.1 |
| **STORY-2.3** | Dynamic expression analysis | Should Have | 3 pts | STORY-2.1 |
| **STORY-2.4** | AI-powered feedback generation | Must Have | 5 pts | STORY-2.1, 2.2 |
| **STORY-2.5** | WebSocket streaming infrastructure | Must Have | 5 pts | None |
| **STORY-2.6** | Frontend visualization (real-time waveform) | Should Have | 3 pts | STORY-2.5 |
| **STORY-2.7** | Practice session recording/playback | Nice to Have | 5 pts | STORY-2.1, 2.2 |

**Total Effort**: 34 story points (~4-5 weeks)

## Technical Decisions Required

1. **ADR-001**: Rust Audio Engine for GPU Processing (→ to be written)
2. **ADR-002**: WebSocket vs WebRTC for audio streaming
3. **ADR-003**: YIN vs PYIN vs Crepe for pitch detection
4. **ADR-004**: Local vs cloud-based feedback generation

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **GPU FFT latency too high** | Medium | High | Benchmark early, CPU fallback with larger buffer |
| **Pitch detection accuracy <91%** | Medium | High | Implement multiple algorithms, ensemble voting |
| **WebSocket audio quality degradation** | Low | Medium | Implement adaptive bitrate, lossless codec |
| **AI feedback too generic** | Medium | Medium | Fine-tune prompts, use student skill level context |
| **Browser microphone latency** | High | Medium | Document minimum requirements, provide diagnostic tool |

## Dependencies

### External
- **WebAudio API**: Browser audio capture
- **WebSocket**: Real-time communication
- **Metal API**: GPU compute shaders (already integrated)
- **MLX**: AI feedback generation (already integrated)

### Internal
- **Rust Audio Engine**: Extend with analysis functions
- **Multi-Model Service**: Use Qwen2.5-7B for feedback (complexity 6-7)
- **User Service**: Skill level context for personalized feedback

## Out of Scope (Phase 2)

- ❌ Video recording of performances
- ❌ Multi-user jam session analysis
- ❌ Automatic transcription (audio → sheet music) - deferred to Phase 4
- ❌ Mobile app support - web-only initially
- ❌ Offline analysis - requires real-time backend

## Acceptance Criteria (Epic Complete)

- [ ] Pitch detection achieves >91% accuracy on test dataset
- [ ] Rhythm analysis achieves >91% accuracy on test dataset
- [ ] End-to-end latency <100ms (p95)
- [ ] AI feedback generates contextual, actionable tips
- [ ] WebSocket streaming handles 100+ concurrent users
- [ ] Frontend displays real-time waveform and feedback
- [ ] Integration tests pass for all analysis components
- [ ] Performance benchmarks meet targets (GPU usage, latency, accuracy)
- [ ] User acceptance testing with 10+ beta testers (>4.2/5 satisfaction)
- [ ] Documentation updated (API endpoints, user guide)

## Timeline

**Week 1-2**: STORY-2.1 (Pitch Detection) + STORY-2.5 (WebSocket)
**Week 3**: STORY-2.2 (Rhythm Analysis)
**Week 4**: STORY-2.3 (Dynamics) + STORY-2.4 (AI Feedback)
**Week 5**: STORY-2.6 (Visualization), testing, refinement

## References

- PRD.md - FR-007 (Real-time performance analysis)
- ARCHITECTURE.md - Rust Audio Engine section
- NFR-003 - Accuracy target >91%
- [YIN Pitch Detection Paper](https://asa.scitation.org/doi/10.1121/1.1458024)
- [Aubio Onset Detection](https://aubio.org/manpages/latest/aubioonset.1.html)

---

**Next Steps**:
1. Write ADR-001 (Rust Audio Engine decision)
2. Create individual story files (STORY-2.1 through STORY-2.4)
3. Set up Epic tracking in project management tool
4. Schedule kickoff meeting with stakeholders

**Created**: 2025-12-15
**Last Updated**: 2025-12-15
