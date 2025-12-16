# Phase 2 Implementation Status

**Date**: December 16, 2025
**Status**: 33% Complete (3/9 files implemented)
**RAM Constraint**: 16GB maximum

---

## ✅ **COMPLETED FILES (3/9)**

### 1. **text_token_service.py** ✅ (370 lines)
**Location**: `backend/app/services/text_token_service.py`

**Features**:
- Complete 600+ token vocabulary
- Bidirectional REMI ↔ Text conversion
- Round-trip validation
- Human-readable tokens

**Usage**:
```python
from app.services.text_token_service import text_token_service

# Convert REMI → Text
remi_tokens = [0, 30, 210, 240]
text_tokens = text_token_service.remi_to_text_tokens(remi_tokens)
# Result: ["SONG_START", "NOTE_ON_21", "DUR_WHOLE", "VEL_SILENT"]

# Validate round-trip
assert text_token_service.validate_round_trip(remi_tokens)
```

---

### 2. **convert_tokens_to_text.py** ✅ (280 lines)
**Location**: `backend/scripts/convert_tokens_to_text.py`

**Features**:
- Converts Phase 1 REMI data → Phase 2 text format
- Multiple output formats (MLX, Alpaca, ChatML)
- Built-in validation
- Progress tracking

**Usage**:
```bash
python backend/scripts/convert_tokens_to_text.py \
    --input data/training/train.jsonl \
    --output data/training/mlx_train.jsonl \
    --format mlx \
    --validate
```

---

### 3. **prepare_stage1_dataset.py** ✅ (150 lines)
**Location**: `backend/scripts/prepare_stage1_dataset.py`

**Features**:
- Collects 1000 general music MIDI files
- Genre distribution management
- Metadata tracking

**Usage**:
```bash
python backend/scripts/prepare_stage1_dataset.py \
    --output data/training/stage1_general_music \
    --target-files 1000
```

**Note**: Requires MIDI files in `backend/data/midi_sources/<genre>/`

---

## 📋 **REMAINING FILES (6/9) - Implementation Guide**

### 4. **prepare_stage2_dataset.py** (Similar to Stage 1)
**Purpose**: Collect 500 Gospel-only MIDI files

**Key differences from Stage 1**:
```python
self.genre_targets = {
    "traditional_gospel": 200,
    "contemporary_gospel": 150,
    "gospel_jazz": 100,
    "worship": 50,
}
```

**Implementation**: Copy `prepare_stage1_dataset.py` and modify genre targets

---

### 5. **finetune_stage1.py** (MLX LoRA Training)
**Purpose**: Train Qwen 2.5-14B on general music (Stage 1)

**Key configuration**:
```python
config = {
    "model": "mlx-community/Qwen2.5-14B-Instruct-4bit",
    "train_data": "data/training/stage1_text_tokens.jsonl",
    "output": "models/qwen_14b_music_base",

    # Memory optimization (16GB constraint)
    "gradient_checkpointing": True,
    "use_fp16": True,
    "batch_size": 1,
    "gradient_accumulation": 8,

    # LoRA settings
    "lora_rank": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.1,

    # Training
    "learning_rate": 2e-4,
    "max_steps": 10000,
    "max_seq_length": 4096,
}
```

**MLX LoRA Command**:
```bash
mlx_lm.lora \
    --model mlx-community/Qwen2.5-14B-Instruct-4bit \
    --train \
    --data data/training/stage1_text_tokens.jsonl \
    --iters 10000 \
    --lora-layers 32 \
    --batch-size 1 \
    --grad-checkpoint
```

---

### 6. **finetune_stage2.py** (Gospel Specialization)
**Purpose**: Fine-tune Stage 1 checkpoint on Gospel-only data

**Key differences**:
```python
config = {
    "model": "models/qwen_14b_music_base/checkpoint-best",  # Start from Stage 1
    "train_data": "data/training/stage2_text_tokens.jsonl",
    "learning_rate": 5e-5,  # Lower LR for specialization
    "max_steps": 5000,      # Fewer steps
}
```

---

### 7. **evaluate_music_quality.py**
**Purpose**: Evaluate fine-tuned model quality

**Metrics to implement**:
```python
def evaluate_model(model_path, test_data):
    metrics = {
        "perplexity": compute_perplexity(model, test_data),
        "token_accuracy": compute_token_accuracy(model, test_data),
        "midi_validity": check_midi_parseability(generated_tokens),
        "musical_coherence": human_evaluation_score(),
    }
    return metrics
```

**Success criteria**:
- Perplexity < 2.0
- Token accuracy > 95%
- 100% valid MIDI
- Musical coherence > 7/10

---

### 8. **finetuned_qwen_service.py**
**Purpose**: Production inference wrapper for fine-tuned model

**Implementation**:
```python
class FinetunedQwenService:
    def __init__(self):
        # Load fine-tuned model with LoRA adapters
        self.model, self.tokenizer = load(
            "models/qwen_14b_gospel_specialist"
        )

    async def generate_music_tokens(
        self,
        prompt: str,
        max_tokens: int = 2048
    ) -> List[str]:
        # Generate text tokens
        response = generate(self.model, self.tokenizer, prompt, max_tokens)

        # Parse text tokens from response
        text_tokens = parse_token_response(response)

        return text_tokens
```

**Integration with Phase 1**:
Replace `music_theory_generator.generate_melody()` with fine-tuned model

---

### 9. **train_workflow_optimized.sh**
**Purpose**: Automated end-to-end training workflow

**Complete workflow**:
```bash
#!/bin/bash

# Stage 0: Prepare datasets
python scripts/prepare_stage1_dataset.py
python scripts/prepare_stage2_dataset.py
python scripts/convert_tokens_to_text.py --input stage1 --output mlx_stage1
python scripts/convert_tokens_to_text.py --input stage2 --output mlx_stage2

# Stage 1: General music training (36-48 hours)
python scripts/finetune_stage1.py

# Stage 2: Gospel specialization (18-24 hours)
python scripts/finetune_stage2.py

# Evaluation
python scripts/evaluate_music_quality.py

echo "✅ Phase 2 training complete!"
```

---

## 🎯 **QUICK IMPLEMENTATION CHECKLIST**

- [x] ✅ Text token service
- [x] ✅ Token converter
- [x] ✅ Stage 1 dataset prep
- [ ] ⏳ Stage 2 dataset prep (copy Stage 1, modify targets)
- [ ] ⏳ MLX LoRA training scripts (use `mlx_lm.lora`)
- [ ] ⏳ Evaluation pipeline
- [ ] ⏳ Inference wrapper
- [ ] ⏳ Workflow orchestrator

**Estimated time to complete**: 8-12 hours coding + 54-72 hours training

---

## 💡 **IMPLEMENTATION TIPS**

### Using MLX for Fine-Tuning

MLX provides built-in LoRA fine-tuning:
```bash
# Install MLX LM tools
pip install mlx-lm

# Fine-tune with LoRA
mlx_lm.lora \
    --model mlx-community/Qwen2.5-14B-Instruct-4bit \
    --train \
    --data data/training/stage1_text_tokens.jsonl \
    --iters 10000 \
    --batch-size 1 \
    --lora-layers 32 \
    --grad-checkpoint \
    --learning-rate 2e-4 \
    --save-every 500

# Merge LoRA adapters (optional)
mlx_lm.fuse --model models/qwen_14b_music_base
```

### Dataset Format for MLX

MLX expects JSONL with `text` field:
```json
{"text": "<|im_start|>user\nGenerate Gospel in C major<|im_end|>\n<|im_start|>assistant\nSONG_START BAR_START CHORD_Cmaj7 ...<|im_end|>"}
```

This is exactly what `convert_tokens_to_text.py --format mlx` produces!

---

## 🚀 **NEXT STEPS**

### Option 1: Implement Remaining Files
Continue building the 6 remaining scripts using templates above

### Option 2: Use MLX CLI Directly
Skip custom training scripts and use MLX CLI:
```bash
# Prepare data
python scripts/convert_tokens_to_text.py --input train.jsonl --output mlx_train.jsonl

# Train with MLX CLI
mlx_lm.lora --model Qwen2.5-14B-Instruct-4bit --train --data mlx_train.jsonl

# Evaluate
mlx_lm.eval --model models/lora_fused

# Use in production
python -c "from mlx_lm import load, generate; model, tokenizer = load('models/lora_fused'); ..."
```

### Option 3: Test Current Implementation
Validate text token system works before full training:
```bash
# Test text tokens
python -c "from app.services.text_token_service import text_token_service; print(text_token_service.get_vocab_info())"

# Test converter
python scripts/convert_tokens_to_text.py --input sample.jsonl --output test.jsonl --validate
```

---

## 📊 **CURRENT STATUS**

| Component | Status | Lines | Progress |
|-----------|--------|-------|----------|
| **Phase 1** | ✅ Complete | 2,446 | 100% |
| **Phase 2 (3/9)** | 🔨 In Progress | 800 | 33% |
| **Total** | 🔨 Building | 3,246 | 76% |

**Remaining work**: ~1,200 lines (training scripts + evaluation)

---

## 🎉 **SUMMARY**

**What's Ready**:
- ✅ Complete text token vocabulary (600+ tokens)
- ✅ Bidirectional REMI ↔ Text conversion
- ✅ Data preparation infrastructure
- ✅ All documentation and plans

**What's Needed**:
- MLX LoRA training scripts (or use MLX CLI directly)
- Evaluation pipeline
- Production inference wrapper

**Recommendation**: Use **MLX CLI directly** for training (simpler, proven) and focus on evaluation + integration.

---

**BMad Master Status**: Core infrastructure complete. Training can begin once datasets are collected.
