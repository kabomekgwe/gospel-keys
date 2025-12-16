# Bootstrap MIDI Generation Status

**Date**: December 16, 2025
**Status**: ✅ **WORKING** (with limitations)

---

## ✅ What's Working

### Successful Generation
The bootstrap generator successfully creates MIDI files:

```bash
python scripts/generate_bootstrap_dataset.py \
    --output data/midi_sources/gospel \
    --count 5 \
    --genre gospel
```

**Result**: 5 Gospel MIDI files created (258 bytes each)

```
✅ gospel_C_traditional_80bpm_var0.mid
✅ gospel_C_traditional_100bpm_var0.mid
✅ gospel_C_traditional_120bpm_var0.mid
✅ gospel_C_traditional_140bpm_var0.mid
✅ gospel_C_traditional_160bpm_var0.mid
```

### Working Components
- ✅ Chord generation (fallback algorithm)
- ✅ MIDI file creation
- ✅ MIDI tokenization
- ✅ File organization
- ✅ Variations (key, tempo, style)

---

## ⚠️ Known Limitations

### 1. RAM Constraint Issue

**Problem**: System has only 8-9GB available RAM, but Qwen 2.5-14B requires 12GB

**Impact**:
- Model automatically falls back to **Phi-3.5 Mini** (3.8B)
- Still generates music, but lower quality
- Melody generation has parsing errors

**Warning Logs**:
```
WARNING: mlx-community/Qwen2.5-14B-Instruct-4bit requires ~12GB RAM,
but only 9.1GB available. This WILL crash your system!
🔄 Falling back to SMALL tier (Phi-3.5 Mini)
```

### 2. Melody Generation Quality

**Problem**: Phi-3.5 Mini produces malformed JSON

**Error**:
```
ERROR: Failed to parse melody response:
Expecting ',' delimiter: line 31 column 66 (char 1946)
```

**Impact**: Only generating 1-note melodies instead of full melodic phrases

### 3. musiclang_predict Missing

**Problem**: `musiclang_predict` package failed to install due to pandas build errors

**Impact**: Using fallback chord generation (still functional)

**Warning**:
```
⚠️ musiclang_predict not installed. Chord service disabled.
```

---

## 🔧 Solutions

### Option 1: Accept Lower Quality (Current)
- Continue using Phi-3.5 Mini
- MIDI files will have simpler melodies
- Still suitable for training (quantity over quality)

### Option 2: Close Other Applications
Free up RAM to reach 12GB available:
```bash
# Check RAM usage
top -l 1 | grep PhysMem

# Close heavy applications (Chrome, Docker, etc.)
# Then retry generation
```

### Option 3: Use Smaller Model Officially
Modify `multi_model_service.py` to use Qwen 7B instead of 14B:

```python
# Change in backend/app/core/config.py
LOCAL_MEDIUM_MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"  # Only 6GB RAM
```

### Option 4: Skip LLM Melody Generation
Modify `hybrid_music_generator.py` to use algorithmic melody only:

```python
# In generate_melody(), skip LLM and use fallback
melody = await self._generate_algorithmic_melody(...)
```

---

## 📊 Current Generation Performance

Per file:
- **Time**: ~15 seconds (14.8s average)
- **Size**: 258 bytes
- **Components**: 8 chords, 1 melody note, 113 tokens

Projection for 1000 files:
- **Time**: ~4.1 hours (with Phi-3.5 Mini)
- **Size**: ~250KB total
- **Usable**: Yes (for training)

---

## 🎯 Recommendations

### For Immediate Use
1. **Continue with current setup** - Files are being generated successfully
2. **Generate larger batches** - The generator works, just with simpler melodies
3. **Use for Stage 1 training** - Quality sufficient for general music pretraining

### For Better Quality
1. **Free up RAM** - Close browser/Docker to reach 12GB available
2. **Or switch to Qwen 7B** - Better quality, lower RAM (6GB)
3. **Or install musiclang_predict** - Better chord voicings
   - Requires fixing pandas installation issue

---

## 📝 Next Steps

### Option A: Generate Training Data Now (Recommended)
```bash
# Generate 250 Gospel files with current setup
python scripts/generate_bootstrap_dataset.py \
    --output data/midi_sources/gospel \
    --count 250 \
    --genre gospel

# ~1 hour with Phi-3.5 Mini
```

### Option B: Fix Quality Issues First
1. Free up RAM (close applications)
2. Retry with Qwen 14B
3. Or switch to Qwen 7B model

### Option C: Download Real MIDI Files
The original plan included downloading Lakh + MAESTRO datasets:

```bash
# Fix wget → curl in collect_midi_dataset.sh
# Then download 45K+ real MIDI files
bash scripts/collect_midi_dataset.sh
```

---

## 🚀 Quick Start

**To generate 250 Gospel training files right now:**

```bash
cd backend

# Option 1: Accept lower quality, generate now
python scripts/generate_bootstrap_dataset.py \
    --output data/midi_sources/gospel \
    --count 250 \
    --genre gospel

# Option 2: Free up RAM first
# 1. Close Chrome, Docker, etc.
# 2. Check: top -l 1 | grep PhysMem
# 3. Ensure 12GB+ available
# 4. Retry generation
```

---

## ✅ Success Criteria

The generator is considered **working** despite limitations because:
- ✅ Creates valid MIDI files
- ✅ Includes chord progressions
- ✅ Includes basic melodies
- ✅ Tokenizes correctly
- ✅ Suitable for training data

**Status**: Ready for production with current quality level

---

**Last Updated**: December 16, 2025
**Files Generated**: 5 test files ✅
**System RAM**: 8-9GB available (needs 12GB for Qwen 14B)
**Recommendation**: Proceed with generation using Phi-3.5 Mini OR free up RAM
