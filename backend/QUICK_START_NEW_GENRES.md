# Quick Start: New Genres (Reggae, Latin, R&B)

**5-Minute Guide to Testing the New Genres**

---

## TL;DR

Three new genres are now available:
- **Reggae**: `/api/v1/reggae/generate`
- **Latin**: `/api/v1/latin/generate`
- **R&B**: `/api/v1/rnb/generate`

All fully functional with AI generation, authentic patterns, and MIDI export.

---

## Quick Test (30 seconds)

### 1. Start Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Test Reggae

```bash
curl -X POST http://localhost:8000/api/v1/reggae/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Roots reggae in G", "tempo": 75, "num_bars": 4, "include_progression": false}'
```

### 3. Test Latin

```bash
curl -X POST http://localhost:8000/api/v1/latin/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Salsa in C", "tempo": 95, "num_bars": 4, "include_progression": false}'
```

### 4. Test R&B

```bash
curl -X POST http://localhost:8000/api/v1/rnb/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Neo-soul in F", "tempo": 85, "num_bars": 4, "include_progression": false}'
```

---

## Python Examples

### Reggae Generation

```python
import asyncio
from app.services.reggae_generator import reggae_generator_service
from app.schemas.reggae import GenerateReggaeRequest, ReggaeApplication

async def generate_reggae():
    request = GenerateReggaeRequest(
        description="Roots reggae with heavy dub bass",
        key="G",
        tempo=75,
        num_bars=8,
        application=ReggaeApplication.ROOTS,
        include_progression=False
    )

    response = await reggae_generator_service.generate_arrangement(request)

    if response.success:
        print(f"✅ Generated: {response.midi_file_path}")
        print(f"   Bars: {response.arrangement_info.total_bars}")
        print(f"   Notes: {response.arrangement_info.total_notes}")
        print(f"   Duration: {response.arrangement_info.duration_seconds}s")
    else:
        print(f"❌ Error: {response.error}")

asyncio.run(generate_reggae())
```

### Latin Generation

```python
from app.services.latin_generator import latin_generator_service
from app.schemas.latin import GenerateLatinRequest, LatinApplication

async def generate_latin():
    request = GenerateLatinRequest(
        description="Upbeat salsa with montuno patterns",
        key="C",
        tempo=95,
        num_bars=8,
        application=LatinApplication.SALSA,
        include_progression=False
    )

    response = await latin_generator_service.generate_arrangement(request)
    return response

# asyncio.run(generate_latin())
```

### R&B Generation

```python
from app.services.rnb_generator import rnb_generator_service
from app.schemas.rnb import GenerateRnBRequest, RnBApplication

async def generate_rnb():
    request = GenerateRnBRequest(
        description="Smooth neo-soul ballad",
        key="F",
        tempo=70,
        num_bars=8,
        application=RnBApplication.BALLAD,
        include_progression=False
    )

    response = await rnb_generator_service.generate_arrangement(request)
    return response

# asyncio.run(generate_rnb())
```

---

## API Endpoints Reference

### Reggae

**Status**: `GET /api/v1/reggae/status`

**Generate**: `POST /api/v1/reggae/generate`

**Applications**:
- `roots`: Classic 70-80 BPM, dub bass
- `dancehall`: Faster 90-110 BPM, energetic
- `dub`: Minimal 60-75 BPM, sparse

### Latin/Salsa

**Status**: `GET /api/v1/latin/status`

**Generate**: `POST /api/v1/latin/generate`

**Applications**:
- `salsa`: Classic 90-100 BPM, montuno
- `ballad`: Slow 60-80 BPM, romantic
- `uptempo`: Fast 110-140 BPM, mambo

### R&B

**Status**: `GET /api/v1/rnb/status`

**Generate**: `POST /api/v1/rnb/generate`

**Applications**:
- `ballad`: Slow 60-75 BPM, lush
- `groove`: Mid 80-95 BPM, syncopated
- `uptempo`: Fast 95-110 BPM, contemporary

---

## Request Parameters

All three genres share the same request structure:

```typescript
{
  description: string;        // Natural language description
  key?: string;               // Musical key (optional, e.g., "C", "Am")
  tempo?: number;             // BPM (optional, 50-180)
  num_bars: number;           // Number of bars (4-64)
  application: string;        // Application type (see above)
  include_progression: boolean; // Use AI or fallback
}
```

---

## Response Format

All three genres return the same response structure:

```typescript
{
  success: boolean;
  midi_file_path?: string;
  midi_base64?: string;
  arrangement_info?: {
    tempo: number;
    key: string;
    time_signature: [number, number];
    total_bars: number;
    total_notes: number;
    duration_seconds: number;
    application: string;
  };
  chord_analysis?: Array<{
    symbol: string;
    function: string;
    notes: string[];
    comment?: string;
  }>;
  notes_preview?: Array<{
    pitch: number;
    time: number;
    duration: number;
    velocity: number;
    hand: string;
  }>;
  generation_method?: string;
  error?: string;
}
```

---

## Musical Characteristics

### Reggae
- **Feel**: Laid-back, offbeat emphasis
- **Bass**: Heavy dub style, roots and fifths
- **Chords**: Skank rhythm, bubble, sustained
- **Rhythm**: One-drop, beats 2 & 4 emphasis

### Latin/Salsa
- **Feel**: Syncopated, danceable, energetic
- **Bass**: Tumbao pattern, clave-based
- **Chords**: Montuno patterns, guajeo voicings
- **Rhythm**: Clave (3-2 or 2-3), anticipations

### R&B
- **Feel**: Smooth, groovy, soulful
- **Bass**: Syncopated, walking, in-the-pocket
- **Chords**: Extended harmony (9ths, 11ths, 13ths)
- **Rhythm**: Backbeat emphasis, 16th subdivisions

---

## Common Use Cases

### Generate with AI (Gemini)

```json
{
  "description": "Uplifting roots reggae in G major with positive vibes",
  "num_bars": 16,
  "include_progression": true  // ← Use AI
}
```

Result: AI generates chord progression from description.

### Generate with Fallback

```json
{
  "description": "Reggae in G",
  "key": "G",
  "tempo": 75,
  "num_bars": 8,
  "include_progression": false  // ← Use fallback
}
```

Result: Uses genre's default progression for key G.

### Specify Everything

```json
{
  "description": "Custom reggae",
  "key": "D",
  "tempo": 80,
  "num_bars": 12,
  "application": "dancehall",
  "include_progression": false
}
```

Result: Uses exact parameters provided.

---

## Advanced Features

### ML Chord Prediction

```python
from app.services.advanced_generator_mixins import MLProgressionPredictorMixin

class MLReggaeGen(MLProgressionPredictorMixin, ReggaeGeneratorService):
    pass

gen = MLReggaeGen()
predictions = gen.predict_next_chord(["G", "C", "D"], "user_123", top_k=5)
# Returns: [("G", 0.45), ("Em", 0.25), ...]
```

### Real-Time Streaming

```python
from app.services.advanced_generator_mixins import StreamingGenerationMixin

class StreamingLatinGen(StreamingGenerationMixin, LatinGeneratorService):
    pass

gen = StreamingLatinGen()
async for event in gen.generate_streaming(request):
    if event["type"] == "bar":
        print(f"Bar {event['bar_number']} ready!")
        # Send to frontend immediately
```

### Genre Fusion

```python
# Blend Reggae (70%) + Latin (30%)
fusion = await reggae_gen.generate_fusion(
    request=request,
    secondary_genre_generator=latin_generator_service,
    primary_weight=0.7
)
```

See `docs/ADVANCED_FEATURES_GUIDE.md` for complete documentation.

---

## Troubleshooting

### Issue: "Module not found"

**Solution**: Make sure you're in the backend directory:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Issue: "Arranger not found"

**Solution**: Check that all directories were created:
```bash
ls -la app/reggae/arrangement/
ls -la app/latin/arrangement/
ls -la app/rnb/arrangement/
```

### Issue: "Gemini API not available"

**Solution**: Set environment variable:
```bash
export GOOGLE_API_KEY="your_key_here"
```

Or use `include_progression: false` to use fallback patterns.

### Issue: "Import error for schemas"

**Solution**: Check schemas exist:
```bash
ls -la app/schemas/reggae.py
ls -la app/schemas/latin.py
ls -la app/schemas/rnb.py
```

---

## Next Steps

1. **Test all three endpoints** (5 min)
2. **Try with AI** (`include_progression: true`) (5 min)
3. **Explore advanced features** (30 min)
4. **Read full documentation**:
   - `COMPLETE_GENRE_IMPLEMENTATION.md` - Complete overview
   - `docs/ADVANCED_FEATURES_GUIDE.md` - Advanced mixins
   - `examples/advanced_features_demo.py` - Working examples

---

## Documentation Index

| File | Purpose |
|------|---------|
| `QUICK_START_NEW_GENRES.md` | This file - 5-minute guide |
| `COMPLETE_GENRE_IMPLEMENTATION.md` | Complete infrastructure overview |
| `NEW_GENRES_AND_FEATURES_COMPLETE.md` | Initial implementation summary |
| `docs/ADVANCED_FEATURES_GUIDE.md` | Advanced mixins documentation |
| `examples/advanced_features_demo.py` | Working code examples |

---

**Happy Generating! 🎵**

*Questions? Check the documentation or test the demo: `python -m examples.advanced_features_demo`*
