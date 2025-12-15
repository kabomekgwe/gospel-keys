# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gospel Keys** is a music education platform that combines AI-powered curriculum generation, GPU-accelerated MIDI synthesis, and real-time performance analysis for learning piano and music theory across multiple genres (Gospel, Jazz, Blues, Classical, Neo-Soul).

### Tech Stack

**Frontend**:
- React 19 with TanStack Router (file-based routing)
- TanStack Query for data fetching
- Zustand for state management
- Tailwind CSS 4 for styling
- Vite 7 as build tool
- Vitest for testing

**Backend**:
- FastAPI (Python 3.13)
- PostgreSQL database
- MLX for local LLM inference (Apple Silicon optimized)
- PyO3 for Rust-Python integration

**Rust Audio Engine**:
- GPU-accelerated MIDI synthesis using Metal API
- SoundFont-based audio generation
- Convolution reverb with M4 chip optimization

**AI/ML**:
- 3-tier local-first LLM strategy:
  - Tier 1: Phi-3.5 Mini (3.8B, complexity 1-4)
  - Tier 2: Qwen2.5-7B (complexity 5-7)
  - Tier 3: Gemini Pro fallback (complexity 8-10)
- Cost savings: ~90% reduction vs cloud-only

---

## Development Commands

### Backend Development

```bash
# Navigate to backend
cd backend

# Activate Python virtual environment
source .venv/bin/activate

# Run development server
python -m uvicorn app.main:app --reload --port 8000

# Run tests
python test_multi_model.py          # Test multi-model LLM service
python verify_integration.py        # Verify AI integration
python test_full_system.py          # Full system test

# Generate curriculum content
python generate_real_curriculum.py  # Generate with local LLM
python create_advanced_curriculum.py # Create advanced curriculum

# Database management
python reset_db_globals.py          # Reset database
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
pnpm install

# Run development server (with host binding for Docker)
pnpm dev
# Runs on http://localhost:3000

# Build for production
pnpm build

# Run tests
pnpm test
```

### Rust Audio Engine

```bash
# Navigate to Rust engine
cd rust-audio-engine

# Development build
cargo build

# Production build (optimized)
cargo build --release

# Run Rust tests
cargo test

# Install Python bindings
pip install maturin
maturin develop --release
```

Test integration:
```python
from rust_audio_engine import synthesize_midi

duration = synthesize_midi(
    midi_path="song.mid",
    output_path="output.wav",
    soundfont_path="soundfont.sf2",
    use_gpu=True,      # Enable M4 GPU
    reverb=True        # Add reverb effect
)
```

### E2E Testing

```bash
# Run Playwright tests from project root
npx playwright test

# Run with UI
npx playwright test --ui

# Run specific test
npx playwright test tests/example.spec.ts
```

---

## Architecture

### Request Flow

```
User → React Frontend → FastAPI Backend → Service Layer → Pipeline/Processing
                            ↓                    ↓              ↓
                        PostgreSQL      AI Orchestrator    Rust Engine
                                            ↓                    ↓
                                    Local LLM (MLX)      GPU Synthesis
```

### Key Architecture Concepts

**3-Layer Backend Structure**:
1. **API Routes** (`backend/app/api/routes/`): HTTP endpoints, request validation
2. **Service Layer** (`backend/app/services/`): Business logic orchestration
3. **Pipeline Layer** (`backend/app/pipeline/`): Heavy processing (audio, MIDI, AI)

**Genre-Specific Modules**: Each genre has dedicated generators
- `backend/app/gospel/` - Gospel-specific patterns
- `backend/app/jazz/` - Jazz voicings and progressions
- `backend/app/blues/` - Blues patterns
- `backend/app/classical/` - Classical techniques
- `backend/app/neosoul/` - Neo-soul harmonies

**AI Orchestration** (`backend/app/services/ai_orchestrator.py`):
- Routes tasks by complexity (1-10)
- Complexity 1-4 → Phi-3.5 Mini (local, fast)
- Complexity 5-7 → Qwen2.5-7B (local, higher quality)
- Complexity 8-10 → Gemini Pro (cloud fallback)
- Automatic model switching based on task complexity

**Rust Audio Engine** (`rust-audio-engine/src/`):
- `synthesizer.rs`: MIDI → WAV synthesis using SoundFont
- `metal_effects.rs`: GPU-accelerated audio effects (reverb, EQ)
- `waveform.rs`: Visual waveform generation (planned)
- `lib.rs`: PyO3 Python bindings

**Multi-Model Service** (`backend/app/services/multi_model_service.py`):
- Manages local LLM lifecycle
- Lazy loading (models load on first use)
- Automatic memory management
- Structured output with Pydantic schemas

### Data Flow Examples

**Curriculum Generation**:
```
User Request → curriculum_service.py → ai_orchestrator.py
                                            ↓
                      (Complexity 7: Qwen2.5-7B local generation)
                                            ↓
                      Generate lessons → genre_generator.py
                                            ↓
                      Generate MIDI → gpu_midi_generator.py
                                            ↓
                      Synthesize Audio → rust_audio_engine (GPU)
                                            ↓
                      Store in DB → Return to frontend
```

**MIDI Synthesis**:
```
MIDI File → Python Service → rust_audio_engine.synthesize_midi()
                                    ↓
                      Load SoundFont → rustysynth
                                    ↓
                      Render Audio → metal_effects.rs (GPU reverb)
                                    ↓
                      Write WAV → Return path
```

---

## Important Development Notes

### Apple Silicon (M4) Optimization

The project is heavily optimized for Apple Silicon:
- **MLX**: Apple's ML framework for local LLM inference
- **Metal API**: GPU compute shaders for audio processing
- **Neural Engine**: Automatic utilization for AI workloads

Performance characteristics:
- Phi-3.5 Mini: ~50 tokens/sec (M4)
- Qwen2.5-7B: ~30-40 tokens/sec (M4)
- GPU Reverb: 50-100x faster than CPU
- MIDI Synthesis: ~100x real-time

### Cost-Free AI Strategy

The platform uses local LLMs to eliminate API costs:
- 90% of tasks run locally (Phi-3.5 Mini + Qwen2.5-7B)
- Only complex tasks use Gemini Pro API
- Estimated savings: $120-276/year per user

**When adding AI features**:
1. Classify task complexity (1-10 scale)
2. Use `ai_orchestrator.py` for routing
3. Default to local models for reproducible content
4. Reserve Gemini for creative/complex tasks only

### Local LLM Usage

**Generate simple content** (complexity 1-4):
```python
from app.services.multi_model_service import multi_model_service

response = multi_model_service.generate(
    prompt="Generate a C major scale exercise",
    complexity=3,  # Routes to Phi-3.5 Mini
    max_tokens=512
)
```

**Generate complex content** (complexity 5-7):
```python
response = multi_model_service.generate(
    prompt="Create a comprehensive jazz tutorial on ii-V-I progressions",
    complexity=7,  # Routes to Qwen2.5-7B
    max_tokens=2048,
    response_format=TutorialSchema  # Structured output
)
```

### Rust-Python Integration

The Rust audio engine is exposed to Python via PyO3:
- Changes to Rust code require `maturin develop --release`
- Release builds are ~10x faster than debug builds
- GPU acceleration is automatic with fallback to CPU
- Python sees Rust functions as native Python functions

**After modifying Rust code**:
```bash
cd rust-audio-engine
maturin develop --release
# Now Python code sees updated functions
```

### Database Schema

Located in `backend/app/database/`:
- User profiles and progress tracking
- Curriculum and lesson storage
- Generated MIDI and audio file references
- Practice session analytics

### Frontend State Management

- **Zustand**: Global app state (user, settings)
- **TanStack Query**: Server state caching and sync
- **TanStack Router**: File-based routing with type safety

Key stores:
- `frontend/src/hooks/useUserStore.ts` - User state
- `frontend/src/hooks/useCurriculumStore.ts` - Curriculum state

---

## Testing Strategy

### Backend Testing
```bash
cd backend
python -m pytest tests/           # Unit tests
python test_multi_model.py        # LLM integration
python verify_integration.py      # AI orchestrator
```

### Frontend Testing
```bash
cd frontend
pnpm test                          # Vitest unit tests
```

### E2E Testing
```bash
npx playwright test               # Full user flows
```

### Rust Testing
```bash
cd rust-audio-engine
cargo test                         # Rust unit tests
cargo test -- --nocapture          # With output
```

---

## Documentation

### Key Documentation Files

- `docs/architecture/RUST_AUDIO_ENGINE.md` - Rust engine architecture
- `docs/RUST_ENGINE_QUICK_START.md` - 5-minute setup guide
- `docs/FEATURE_RECOMMENDATIONS_2025.md` - Feature roadmap
- `docs/PRIORITY_FEATURES_IMPLEMENTATION.md` - Implementation guides
- `AI_INTEGRATION.md` - Multi-model LLM strategy
- `architecture.md` - System architecture overview
- `PHASE1_COMPLETE.md` - Phase 1 completion summary

### Quick Reference

**Rust Engine Functions**:
- `synthesize_midi()` - MIDI → WAV with GPU effects ✅
- `generate_waveform()` - Audio → PNG waveform 🚧
- `analyze_performance()` - Student assessment 🚧

**AI Complexity Scale**:
- 1-4: Simple (Phi-3.5 Mini) - exercises, tips, validation
- 5-7: Moderate (Qwen2.5-7B) - tutorials, theory, coaching
- 8-10: Complex (Gemini Pro) - creative composition, advanced analysis

---

## Common Tasks

### Add a New Genre

1. Create generator: `backend/app/[genre]/generator.py`
2. Implement voicing patterns and chord progressions
3. Register in `ai_orchestrator.py`
4. Add API routes in `backend/app/api/routes/`
5. Create frontend components in `frontend/src/components/[genre]/`

### Add a New AI Feature

1. Determine complexity level (1-10)
2. Use `ai_orchestrator.generate()` with appropriate complexity
3. Define Pydantic schema for structured output
4. Test with local models first
5. Fallback to Gemini only if needed

### Optimize Audio Processing

1. Profile with Activity Monitor (GPU History)
2. Check if using release build: `cargo build --release`
3. Verify GPU usage: Metal shader compilation logs
4. Consider batch processing for multiple files

### Debug Local LLM Issues

1. Check model loading: `backend/app/services/multi_model_service.py`
2. Verify MLX installation: `python -c "import mlx; print(mlx.__version__)"`
3. Monitor memory: Models require 2-5GB RAM
4. Check logs: Model switching logged to console

---

## Performance Targets

- **First Contentful Audio**: < 500ms (30s MIDI)
- **LLM Response (Simple)**: < 200ms (Phi-3.5 Mini)
- **LLM Response (Complex)**: < 3s (Qwen2.5-7B)
- **MIDI Synthesis**: ~100x real-time
- **GPU Reverb**: 50-100x faster than CPU

---

## Notes

- All Python code uses Python 3.13
- Virtual environment required: `source .venv/bin/activate`
- Rust code optimized for Apple Silicon (M4)
- Always use `--release` for Rust builds in production
- Local LLMs download on first use (2-4GB each)
- GPU acceleration automatic with CPU fallback
