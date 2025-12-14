# Gospel MIDI Dataset for MLX Training

## Overview

This directory contains the gospel piano MIDI dataset for fine-tuning MLX models on M4 Pro.

**Target**: 500-1000 gospel piano MIDI files
**Purpose**: Train MLX transformer to generate authentic gospel piano arrangements
**Quality**: Extended harmony, gospel feel, various styles (traditional → contemporary)

---

## Quick Start

### Option 1: Automated YouTube Collection (Recommended)

```bash
# Collect 100 gospel piano MIDIs from YouTube
~/.local/bin/uv run python scripts/build_gospel_dataset.py \
    --source youtube \
    --limit 100 \
    --output data/gospel_dataset

# Check progress
~/.local/bin/uv run python scripts/build_gospel_dataset.py --stats
```

### Option 2: Manual MuseScore Collection

1. Visit https://musescore.com/sheetmusic?text=gospel%20piano
2. Download public domain gospel piano scores
3. Save MIDI files to `data/gospel_dataset/musescore/`
4. Run validator:
```bash
~/.local/bin/uv run python scripts/validate_gospel_midis.py
```

### Option 3: Both (Best Quality)

```bash
# Collect from both YouTube and MuseScore
~/.local/bin/uv run python scripts/build_gospel_dataset.py \
    --source both \
    --limit 500
```

---

## Dataset Structure

```
gospel_dataset/
├── youtube/              # YouTube-sourced MIDIs
│   ├── audio/            # Downloaded audio files
│   └── midi/             # Transcribed MIDIs
├── musescore/            # MuseScore downloads
├── validated/            # Validated gospel MIDIs (ready for training)
│   ├── gospel_0001_Kirk_Franklin.mid
│   ├── gospel_0002_Richard_Smallwood.mid
│   └── ...
└── dataset_metadata.json # Metadata (artist, style, tempo, etc.)
```

---

## Validation Criteria

Each MIDI file is validated for gospel characteristics:

✅ **Piano notes present** (minimum 50 notes)
✅ **Duration**: 30 seconds - 5 minutes
✅ **Pitch range**: At least 2 octaves (24 semitones)
✅ **Gospel tempo range**: 40-180 BPM
✅ **Variety**: Chord changes, not repetitive loops

Future enhancements:
- Extended chord detection (9ths, 11ths, 13ths)
- Gospel rhythm pattern matching
- Chromatic passing chord identification

---

## Style Distribution (Target)

| Style | Percentage | Count (of 500) | Characteristics |
|-------|------------|----------------|-----------------|
| **Contemporary** | 30% | 150 | Kirk Franklin, Israel Houghton, syncopated |
| **Traditional** | 25% | 125 | Thomas Dorsey, hymn-based, sustained |
| **Jazz-Gospel** | 20% | 100 | Richard Smallwood, extended harmony |
| **Worship** | 15% | 75 | Hillsong, atmospheric, modern |
| **Tutorials** | 10% | 50 | Instructional, covers various styles |

---

## YouTube Search Queries

The automated builder uses these search queries:

**Contemporary:**
- "kirk franklin piano tutorial"
- "israel houghton piano"
- "tye tribbett piano tutorial"

**Traditional:**
- "thomas dorsey precious lord piano"
- "traditional gospel piano tutorial"

**Jazz-Gospel:**
- "richard smallwood total praise piano"
- "jazz gospel piano tutorial"
- "james hall piano tutorial"

**Worship:**
- "gospel worship piano tutorial"
- "hillsong gospel piano"

**General:**
- "gospel piano lesson"
- "gospel piano chords tutorial"

---

## Training Timeline (M4 Pro)

| Phase | Duration | Task |
|-------|----------|------|
| **Week 1** | 2-3 days | Collect 100 MIDIs (YouTube) |
| **Week 2** | 3-4 days | Collect 400 MIDIs (YouTube + MuseScore) |
| **Week 3** | 2-4 hours | Fine-tune MLX model on M4 Pro |
| **Week 4** | Test | Generate 100 test MIDIs, validate quality |

---

## MLX Fine-Tuning Command

Once you have 500+ validated MIDIs:

```python
from app.gospel.ai.mlx_music_generator import MLXGospelGenerator

generator = MLXGospelGenerator()

# Fine-tune on gospel dataset (2-4 hours on M4 Pro)
generator.fine_tune_on_gospel_dataset(
    gospel_midi_dir=Path("data/gospel_dataset/validated"),
    output_dir=Path("backend/models/mlx-gospel-transformer"),
    num_epochs=10,
    batch_size=8,  # M4 Pro with 24GB RAM can handle this
    learning_rate=5e-5
)
```

---

## Cost Analysis

### YouTube Collection (Automated)
- **Cost**: $0 (all local processing)
- **Time**: ~5-7 days for 500 MIDIs (mostly automated)
- **Quality**: Variable (depends on transcription accuracy)

### MuseScore Collection (Manual)
- **Cost**: $0 (public domain scores)
- **Time**: ~10-15 hours manual download for 500 MIDIs
- **Quality**: High (human-created scores)

### Hybrid Approach (Recommended)
- **Cost**: $0
- **Time**: 7-10 days for 500 MIDIs
- **Quality**: Best (diverse sources, validated)

---

## Troubleshooting

### Issue: yt-dlp download fails
**Solution**: Update yt-dlp: `pip install --upgrade yt-dlp`

### Issue: basic-pitch transcription is slow
**Solution**: Use GPU acceleration or reduce audio quality

### Issue: Too many invalid MIDIs
**Solution**: Adjust validation criteria in `build_gospel_dataset.py`

### Issue: Dataset too small
**Solution**:
1. Lower validation strictness
2. Add more YouTube search queries
3. Manually curate from MuseScore

---

## Next Steps After Dataset Collection

1. **Train MLX Model** (2-4 hours on M4 Pro)
2. **Generate 100 test MIDIs** (<10 minutes)
3. **Validate gospel authenticity** (blind listening test)
4. **Iterate if needed** (adjust training params)
5. **Generate 10,000+ production MIDIs** (~3 hours total)

---

## Resources

- **MuseScore Gospel Piano**: https://musescore.com/sheetmusic?text=gospel%20piano
- **YouTube Gospel Piano Channels**: See `gospel_youtube_urls.json`
- **MIDI Tokenization**: miditok REMI+ format
- **MLX Documentation**: https://ml-explore.github.io/mlx/

---

## Questions?

Check the main project README or the implementation plan at:
`~/.claude/plans/quizzical-fluttering-quilt.md`
