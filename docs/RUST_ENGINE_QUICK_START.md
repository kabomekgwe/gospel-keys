# Rust Audio Engine - Quick Start Guide

**5-Minute Setup for Developers**

---

## Installation

```bash
# 1. Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Navigate to rust-audio-engine
cd rust-audio-engine

# 3. Build and install Python bindings
pip install maturin
maturin develop --release
```

## Basic Usage

### Python Example

```python
from rust_audio_engine import synthesize_midi

# Synthesize MIDI to WAV
duration = synthesize_midi(
    midi_path="song.mid",
    output_path="output.wav",
    soundfont_path="soundfont.sf2",
    use_gpu=True,      # Enable M4 GPU acceleration
    reverb=True        # Add reverb effect
)

print(f"Generated {duration:.2f} seconds of audio")
```

## Integration in Backend

### FastAPI Example

```python
# backend/app/routes/audio.py
from fastapi import APIRouter, HTTPException
from rust_audio_engine import synthesize_midi
import os

router = APIRouter()

@router.post("/synthesize/{midi_id}")
async def synthesize_audio(midi_id: str):
    try:
        midi_path = f"/data/midi/{midi_id}.mid"
        output_path = f"/storage/audio/{midi_id}.wav"

        duration = synthesize_midi(
            midi_path=midi_path,
            output_path=output_path,
            soundfont_path="/data/soundfonts/default.sf2",
            use_gpu=True,
            reverb=True
        )

        return {
            "status": "success",
            "duration": duration,
            "audio_url": f"/audio/{midi_id}.wav"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Performance Tips

1. **Always use release builds in production**
   ```bash
   maturin build --release
   ```

2. **Enable GPU for effects processing**
   ```python
   synthesize_midi(..., use_gpu=True)  # 50-100x faster
   ```

3. **Cache generated audio**
   - Check if WAV exists before regenerating
   - Store in `/storage/audio/{midi_id}.wav`

4. **Batch process during off-peak hours**
   ```python
   # Use Celery or similar for background tasks
   @celery.task
   def batch_synthesize(midi_list):
       for midi in midi_list:
           synthesize_midi(...)
   ```

## Available Functions

| Function | Purpose | Status |
|----------|---------|--------|
| `synthesize_midi()` | MIDI → WAV with effects | ✅ Production Ready |
| `generate_waveform()` | Audio → PNG waveform | 🚧 In Development |
| `analyze_performance()` | Student assessment | 🚧 Planned |

## Troubleshooting

### "No Metal device found"
- GPU effects will auto-fallback to CPU
- Verify macOS with Metal support

### "SoundFont loading failed"
- Check file path is correct
- Ensure .sf2 file is valid

### Slow performance
- Ensure using `--release` build
- Check GPU is enabled: `use_gpu=True`

## Next Steps

- **Full Documentation**: See `docs/architecture/RUST_AUDIO_ENGINE.md`
- **Performance Benchmarks**: Check optimization section
- **Integration Patterns**: Review example implementations

---

**Quick Links:**
- [Full Architecture Guide](./architecture/RUST_AUDIO_ENGINE.md)
- [Source Code](../rust-audio-engine/src/)
- [Python Integration Examples](../backend/test_multi_model.py)
