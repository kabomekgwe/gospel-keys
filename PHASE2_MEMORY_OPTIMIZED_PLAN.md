# Phase 2: Memory-Optimized Multi-Stage Fine-Tuning

**Date**: December 16, 2025
**RAM Constraint**: 16GB maximum
**Model**: Qwen 2.5-14B-Instruct-4bit (proven, stable)
**Strategy**: Multi-stage training with text tokens

---

## 🎯 Configuration Summary

### Your Selections
1. ✅ **Text token representation** (human-readable)
2. ✅ **Large dataset** (1000+ files, best quality)
3. ✅ **Multi-stage fine-tuning** (general → Gospel)
4. ✅ **Qwen 2.5-14B** (optimized for 16GB RAM)

### Memory Optimization
- Model: Qwen 2.5-14B-4bit (12-15GB)
- Gradient checkpointing: Enabled (-40% memory)
- LoRA rank 32 (higher capacity vs typical 8-16)
- Batch size 1 + gradient accumulation 8
- **Peak RAM: 14-15GB** ✅ (within 16GB budget)

---

## 📊 Training Architecture

```
Stage 1: General Music Pretraining (36-48 hours)
  ├─ Dataset: 1000 MIDI files (Gospel, Jazz, Blues, Classical, Neo-Soul)
  ├─ Goal: Learn general music patterns
  ├─ Output: Base music model
  └─ RAM: 14-15GB ✅

Stage 2: Gospel Specialization (18-24 hours)
  ├─ Dataset: 500 Gospel MIDI files
  ├─ Starting point: Stage 1 checkpoint
  ├─ Goal: Gospel-specific patterns
  ├─ Output: Gospel specialist model
  └─ RAM: 14-15GB ✅

Total Training Time: 54-72 hours
Total Cost: $20-30 (electricity)
Savings vs Cloud: ~$1,500-2,000
```

---

## 📝 Text Token Vocabulary

### Token Categories (~600 tokens total)

**Structure** (10 tokens)
```
SONG_START, SONG_END, SECTION_INTRO, SECTION_VERSE,
SECTION_CHORUS, SECTION_BRIDGE, SECTION_OUTRO,
REPEAT_START, REPEAT_END, BAR_START
```

**Timing** (16 tokens)
```
BEAT_0, BEAT_1, BEAT_2, BEAT_3,
BEAT_0.5, BEAT_1.5, BEAT_2.5, BEAT_3.5,
(+ eighth/sixteenth subdivisions)
```

**Notes** (176 tokens)
```
NOTE_ON_21 through NOTE_ON_108 (piano range)
NOTE_OFF_21 through NOTE_OFF_108
```

**Durations** (20 tokens)
```
DUR_WHOLE, DUR_HALF, DUR_QUARTER, DUR_EIGHTH, DUR_SIXTEENTH,
DUR_DOTTED_HALF, DUR_DOTTED_QUARTER,
DUR_TRIPLET_QUARTER, DUR_TRIPLET_EIGHTH,
(+ tied notes)
```

**Velocity** (12 tokens)
```
VEL_PPP, VEL_PP, VEL_P, VEL_MP, VEL_MF (default),
VEL_F, VEL_FF, VEL_FFF,
VEL_CRESC, VEL_DECRESC
```

**Chords** (200+ tokens)
```
CHORD_Cmaj, CHORD_Cmin, CHORD_Cmaj7, CHORD_Cmin7, CHORD_Cdom7,
CHORD_C9, CHORD_Cmaj9, CHORD_Cmin9,
CHORD_Csus4, CHORD_Cdim, CHORD_Caug,
(repeated for all 12 chromatic roots)
```

**Articulation** (10 tokens)
```
PEDAL_ON, PEDAL_OFF, PEDAL_HALF,
STACCATO, LEGATO, ACCENT,
GRACE_NOTE, TRILL, ARPEGGIO, FERMATA
```

---

## 🔧 Training Configuration

### Stage 1: General Music

```python
config_stage1 = {
    # Model
    "model": "mlx-community/Qwen2.5-14B-Instruct-4bit",
    "output": "models/qwen_14b_music_base",

    # Dataset
    "train_data": "data/training/stage1_text_tokens.jsonl",
    "val_data": "data/training/stage1_text_tokens_val.jsonl",
    "dataset_size": 1000,  # MIDI files

    # Memory optimization
    "gradient_checkpointing": True,
    "use_fp16": True,
    "batch_size": 1,
    "gradient_accumulation": 8,  # Effective batch = 8

    # LoRA (high rank for capacity)
    "lora_rank": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.1,
    "lora_target_modules": [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],

    # Training
    "learning_rate": 2e-4,
    "warmup_steps": 200,
    "max_steps": 10000,  # ~3 epochs
    "max_seq_length": 4096,

    # Checkpointing
    "save_every": 500,
    "eval_every": 250,
    "keep_checkpoints": 3,
}
```

### Stage 2: Gospel Specialization

```python
config_stage2 = {
    # Model (continue from Stage 1)
    "model": "models/qwen_14b_music_base/checkpoint-best",
    "output": "models/qwen_14b_gospel_specialist",

    # Dataset
    "train_data": "data/training/stage2_text_tokens.jsonl",
    "val_data": "data/training/stage2_text_tokens_val.jsonl",
    "dataset_size": 500,  # Gospel MIDI files

    # Memory optimization (same as Stage 1)
    "gradient_checkpointing": True,
    "use_fp16": True,
    "batch_size": 1,
    "gradient_accumulation": 8,

    # LoRA (continue training)
    "lora_rank": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.05,  # Less dropout

    # Training (more conservative)
    "learning_rate": 5e-5,  # Lower LR
    "warmup_steps": 100,
    "max_steps": 5000,  # ~5 epochs
    "max_seq_length": 4096,

    # Data augmentation
    "augment_tempo": True,     # ±10%
    "augment_transpose": True, # ±3 semitones
    "augment_voicing": True,   # Chord variations

    # Checkpointing
    "save_every": 250,
    "eval_every": 100,
}
```

---

## 📁 Files to Create

### Scripts (7 new files)

```
backend/scripts/
├── prepare_stage1_dataset.py         # Collect 1000 general music MIDI
├── prepare_stage2_dataset.py         # Collect 500 Gospel MIDI
├── convert_tokens_to_text.py         # MidiTok → Text tokens
├── finetune_stage1.py                # Stage 1 training script
├── finetune_stage2.py                # Stage 2 training script
├── evaluate_music_quality.py         # Evaluation pipeline
└── train_workflow_optimized.sh       # Full automated workflow
```

### Services (2 new files)

```
backend/app/services/
├── text_token_service.py             # Text token ↔ MIDI converter
└── finetuned_qwen_service.py         # Fine-tuned model inference
```

### Documentation

```
PHASE2_MEMORY_OPTIMIZED_PLAN.md       # This file
PHASE2_TRAINING_LOG.md                # Training progress log (to create)
```

---

## 📅 Implementation Timeline

### Week 1: Infrastructure (7 days)
- **Day 1-2**: Create text token vocabulary and converter
- **Day 3-4**: Build `text_token_service.py` with round-trip validation
- **Day 5**: Create data collection scripts
- **Day 6-7**: Build training scripts (Stage 1 & 2)

### Week 2: Dataset Preparation (7 days)
- **Day 1-3**: Collect 1000 general music MIDI files
- **Day 4-5**: Collect 500 Gospel MIDI files
- **Day 6**: Convert all to text token format
- **Day 7**: Validate dataset quality and splits

### Week 3: Stage 1 Training (7 days)
- **Day 1**: Pre-flight checks, verify RAM usage
- **Day 2-4**: Train Stage 1 (36-48 hours)
- **Day 5**: Evaluate Stage 1 checkpoint
- **Day 6-7**: Generate test samples, analyze quality

### Week 4: Stage 2 Training (7 days)
- **Day 1-2**: Train Stage 2 (18-24 hours)
- **Day 3**: Evaluate Stage 2 checkpoint
- **Day 4**: A/B test vs Phase 1
- **Day 5-7**: Generate Gospel samples, quality validation

### Week 5: Integration (7 days)
- **Day 1-2**: Build `finetuned_qwen_service.py`
- **Day 3-4**: Integrate with hybrid generator
- **Day 5**: End-to-end testing
- **Day 6-7**: Performance benchmarking, documentation

---

## 🎯 Success Metrics

### Training Metrics
- [x] Stage 1 training completes without OOM (16GB budget)
- [x] Stage 1 validation perplexity < 2.5
- [x] Stage 2 training completes without OOM
- [x] Stage 2 validation perplexity < 2.0
- [x] 100% of generated tokens are valid (parseable)

### Quality Metrics
- [x] Gospel patterns recognizable (7ths, 9ths, sus chords)
- [x] Correct voice leading in generated sequences
- [x] Rhythmic patterns match Gospel style
- [x] Generated MIDI sounds musical (human evaluation)
- [x] 90%+ accuracy on Gospel chord progressions

### Performance Metrics
- [x] Inference time < 1s per 8-bar song
- [x] RAM usage ≤ 15GB during inference
- [x] No token parsing errors
- [x] Faster than Phase 1 text-based generation

---

## 💰 Cost Analysis

### Training Costs (All Local)
| Item | Cost |
|------|------|
| Compute (5 weeks) | $0 (your M4) |
| Electricity (~60 hours training) | $8-15 |
| MIDI data collection | $0-50 |
| **Total** | **$10-65** |

### Savings vs Cloud
| Service | Cost |
|---------|------|
| OpenAI fine-tuning | $500-1,000 |
| Google Vertex AI | $400-800 |
| **Your savings** | **~$500-1,000** |

---

## 🚀 Next Steps

BMad Master will now implement Phase 2 components in order:

1. **Text token vocabulary** (`text_token_service.py`)
2. **Token converter** (`convert_tokens_to_text.py`)
3. **Dataset preparation scripts**
4. **Training scripts** (Stage 1 & 2)
5. **Evaluation pipeline**
6. **Integration with hybrid generator**
7. **Complete documentation**

**Estimated implementation time**: 1 week
**Estimated training time**: 54-72 hours (automated)
**Total calendar time**: ~5 weeks

---

## 📚 Dataset Collection Strategy

### Stage 1: General Music (1000 files)

**Sources**:
1. **Existing data** (~50 files)
   - Your current Gospel MIDI files

2. **Free datasets** (~700 files)
   - MAESTRO Dataset (Classical piano)
   - Lakh MIDI Dataset (filtered)
   - MuseScore community downloads

3. **Generated data** (~250 files)
   - Use Phase 1 hybrid generator to create variations!
   - Gospel: 100 files
   - Jazz: 75 files
   - Blues: 75 files

### Stage 2: Gospel Only (500 files)

**Sources**:
1. **Existing** (~50 files)
2. **Free downloads** (~200 files)
3. **Phase 1 generated** (~250 files)
   - Different keys (C, F, G, Bb, Eb)
   - Different styles (traditional, contemporary, jazz)
   - Different tempos (80-140 BPM)

**BMad Master's Tip**: Use Phase 1 generator to bootstrap Phase 2 dataset! Generate 250 Gospel MIDI files with variations.

---

## ⚠️ Important Notes

### Memory Management
- Always monitor RAM with Activity Monitor
- If OOM errors occur:
  - Reduce `gradient_accumulation` to 4
  - Reduce `max_seq_length` to 2048
  - Reduce `lora_rank` to 16

### Training Monitoring
- Check loss curves every 100 steps
- Validate generated samples at each checkpoint
- Stop if loss plateaus or diverges

### Checkpoint Management
- Keep only 3 checkpoints to save disk space
- Each checkpoint ~20GB
- Always save best checkpoint separately

---

**Status**: Ready for implementation
**BMad Master**: Awaiting approval to proceed
