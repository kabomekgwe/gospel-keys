# MIDI Dataset Collection Guide

**Goal**: Collect 1000+ MIDI files for Phase 2 multi-stage training
**Time**: 1-2 hours (automated) + 6-12 hours (downloads)
**Cost**: Free

---

## 🚀 **QUICK START (Automated)**

```bash
# Run automated collection script
bash backend/scripts/collect_midi_dataset.sh

# This will:
# 1. Download Lakh MIDI Dataset (2GB, 45K files)
# 2. Download MAESTRO Dataset (4GB, 1.2K files)
# 3. Filter Lakh by genre (Gospel, Jazz, Blues)
# 4. Organize MAESTRO (Classical)
# 5. Generate 250 synthetic Gospel files
#
# Total time: 6-12 hours (mostly downloading)
# Total size: ~8GB downloaded, ~2GB after filtering
# Result: 1000+ MIDI files ready for training
```

---

## 📊 **EXPECTED RESULTS**

After running the automated script:

| Genre | Source | Files | Quality |
|-------|--------|-------|---------|
| **Gospel** | Generated + Lakh | 450 | Excellent |
| **Jazz** | Lakh filtered | 150 | Good |
| **Blues** | Lakh filtered | 100 | Good |
| **Classical** | MAESTRO | 200 | Excellent |
| **Neo-Soul** | Manual/Generated | 100 | Good |
| **Total** | **Mixed** | **1000+** | **High** |

---

## 📁 **CREATED STRUCTURE**

```
backend/data/midi_sources/
├── downloads/                    # Raw downloads (can delete after)
│   ├── lmd_matched.tar.gz       # 2GB
│   ├── lmd_matched/             # 4GB extracted
│   ├── maestro-v3.0.0-midi.zip  # 4GB
│   └── maestro-v3.0.0/          # 4GB extracted
│
├── gospel/                       # 450 Gospel MIDI files
│   ├── gospel_0000.mid
│   ├── gospel_C_traditional_120bpm_var0.mid
│   └── ...
│
├── jazz/                         # 150 Jazz MIDI files
├── blues/                        # 100 Blues MIDI files
├── classical/                    # 200 Classical MIDI files
└── neosoul/                      # 100 Neo-Soul MIDI files
```

---

## 🛠️ **MANUAL STEPS (If Script Fails)**

### **Step 1: Download Datasets**

```bash
# Create directories
mkdir -p backend/data/midi_sources/downloads
cd backend/data/midi_sources/downloads

# Download Lakh (2GB)
wget http://hog.ee.columbia.edu/craftel/lmd/lmd_matched.tar.gz
tar -xzf lmd_matched.tar.gz

# Download MAESTRO (4GB)
wget https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip
unzip maestro-v3.0.0-midi.zip

cd ../../..
```

### **Step 2: Filter by Genre**

```bash
cd backend

# Filter Lakh for Gospel, Jazz, Blues
python scripts/filter_lakh_by_genre.py \
    --input data/midi_sources/downloads/lmd_matched \
    --output-dir data/midi_sources \
    --gospel-count 200 \
    --jazz-count 150 \
    --blues-count 100
```

### **Step 3: Copy Classical**

```bash
# Copy 200 MAESTRO files to classical directory
mkdir -p data/midi_sources/classical

find data/midi_sources/downloads/maestro-v3.0.0 -name "*.mid*" | \
    head -200 | \
    xargs -I {} cp {} data/midi_sources/classical/
```

### **Step 4: Generate Gospel Data**

```bash
# Generate 250 synthetic Gospel MIDI files
python scripts/generate_bootstrap_dataset.py \
    --output data/midi_sources/gospel \
    --count 250 \
    --genre gospel
```

---

## 🎯 **VERIFICATION**

Check collection results:

```bash
# Count files by genre
echo "Gospel: $(find backend/data/midi_sources/gospel -name '*.mid*' | wc -l)"
echo "Jazz: $(find backend/data/midi_sources/jazz -name '*.mid*' | wc -l)"
echo "Blues: $(find backend/data/midi_sources/blues -name '*.mid*' | wc -l)"
echo "Classical: $(find backend/data/midi_sources/classical -name '*.mid*' | wc -l)"
echo "Neo-Soul: $(find backend/data/midi_sources/neosoul -name '*.mid*' | wc -l)"

# Total
echo "Total: $(find backend/data/midi_sources -name '*.mid*' -not -path '*/downloads/*' | wc -l)"
```

**Expected output**:
```
Gospel: 450
Jazz: 150
Blues: 100
Classical: 200
Neo-Soul: 100
Total: 1000
```

---

## 🔧 **TROUBLESHOOTING**

### **Problem: Downloads fail**

**Solution**: Manual download
1. Visit https://colinraffel.com/projects/lmd/
2. Download `lmd_matched.tar.gz` manually
3. Visit https://magenta.tensorflow.org/datasets/maestro
4. Download `maestro-v3.0.0-midi.zip` manually
5. Extract to `backend/data/midi_sources/downloads/`

### **Problem: Low file counts**

**Solution**: Generate more synthetic data
```bash
# Generate additional files for any genre
python scripts/generate_bootstrap_dataset.py \
    --output data/midi_sources/gospel \
    --count 500 \
    --genre gospel
```

### **Problem: Genre filter finds few files**

**Solution**: Lakh has limited Gospel/Jazz/Blues. Supplement with:
1. FreeMIDI.org - Manual download
2. BitMIDI.com - Manual download
3. Generate more synthetic files

---

## 📚 **ALTERNATIVE SOURCES (Manual)**

If automated collection doesn't reach 1000 files:

### **FreeMIDI.org**
```bash
# Browse and download manually
# Gospel: https://freemidi.org/genre-gospel
# Jazz: https://freemidi.org/genre-jazz
# Blues: https://freemidi.org/genre-blues

# Save to:
# backend/data/midi_sources/gospel/freemidi_*.mid
```

### **BitMIDI**
```bash
# Download category archives
# Gospel: https://bitmidi.com/genre/gospel
# Jazz: https://bitmidi.com/genre/jazz

# Or use wget (respectfully):
wget -r -l1 -nd -A.mid https://bitmidi.com/genre/gospel
```

### **MuseScore** (Requires Account)
1. Create free account at musescore.com
2. Search "gospel piano", "jazz piano", etc.
3. Download as MIDI (individually)
4. Save to appropriate genre folder

---

## ✅ **NEXT STEPS AFTER COLLECTION**

Once you have 1000+ files:

```bash
# 1. Prepare Stage 1 dataset (general music)
python backend/scripts/prepare_stage1_dataset.py \
    --output backend/data/training/stage1_general_music \
    --target-files 1000

# 2. Prepare Stage 2 dataset (Gospel only)
python backend/scripts/prepare_stage2_dataset.py \
    --output backend/data/training/stage2_gospel_only \
    --target-files 500

# 3. Tokenize MIDI files
python backend/scripts/prepare_training_data.py \
    --input backend/data/training/stage1_general_music \
    --output backend/data/training \
    --genre mixed

# 4. Convert to text tokens
python backend/scripts/convert_tokens_to_text.py \
    --input backend/data/training/train.jsonl \
    --output backend/data/training/mlx_train.jsonl \
    --format mlx \
    --validate

# 5. Begin training!
bash backend/scripts/train_workflow_optimized.sh
```

---

## 💡 **RECOMMENDED APPROACH**

**BMad Master's recommendation for fastest results**:

```bash
# Option 1: Automated (6-12 hours, hands-off)
bash backend/scripts/collect_midi_dataset.sh

# Option 2: Generate-only (2-4 hours, no downloads)
python backend/scripts/generate_bootstrap_dataset.py --count 600 --genre gospel
python backend/scripts/generate_bootstrap_dataset.py --count 250 --genre jazz
python backend/scripts/generate_bootstrap_dataset.py --count 150 --genre blues

# Option 3: Hybrid (best quality)
# 1. Run automated script (gets 500-700 files)
bash backend/scripts/collect_midi_dataset.sh

# 2. Generate to fill gaps
python backend/scripts/generate_bootstrap_dataset.py --count 300 --genre gospel
```

---

## 📊 **DATASET QUALITY TIPS**

### **Validate MIDI Files**
```python
# Check if MIDI files are valid
python -c "
import mido
from pathlib import Path

midi_files = Path('backend/data/midi_sources/gospel').glob('*.mid*')
valid = 0
invalid = []

for f in midi_files:
    try:
        mid = mido.MidiFile(f)
        valid += 1
    except Exception as e:
        invalid.append(f.name)

print(f'Valid: {valid}')
print(f'Invalid: {len(invalid)}')
if invalid:
    print('Invalid files:', invalid[:10])
"
```

### **Remove Duplicates**
```bash
# Find and remove duplicate MIDI files
fdupes -r -d -N backend/data/midi_sources/
```

---

## 🎉 **SUCCESS CRITERIA**

You're ready for Phase 2 training when:

- [x] ✅ 1000+ MIDI files collected
- [x] ✅ At least 400+ Gospel files
- [x] ✅ Files distributed across genres
- [x] ✅ All MIDI files valid (parseable)
- [x] ✅ Organized in genre directories

**Current status**: Run `bash backend/scripts/collect_midi_dataset.sh` to begin!

---

**Estimated collection time**:
- Automated script: 6-12 hours (mostly downloading)
- Generate-only: 2-4 hours (no downloads)
- Manual collection: 1-2 days (browsing + downloading)

**Recommended**: Start automated script before bed, wake up to 1000+ files! 🎵
