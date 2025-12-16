import sys
import platform
import subprocess
import importlib.util

print("--- System Verification ---")
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")

# Verify PyTorch and MPS
try:
    import torch
    print(f"PyTorch Version: {torch.__version__}")
    if torch.backends.mps.is_available():
        print("✅ MPS (Metal Performance Shaders) is available! GPU acceleration enabled for PyTorch.")
    else:
        print("❌ MPS is NOT available. PyTorch will run on CPU (slower).")
except ImportError:
    print("❌ PyTorch is NOT installed.")

# Verify MLX
try:
    import mlx.core as mx
    print(f"MLX Version: {mx.__version__}")
    print("✅ MLX is installed.")
except ImportError:
    print("❌ MLX is NOT installed.")

print("\n--- MidiTok Verification ---")
try:
    from miditok import REMI, TokenizerConfig
    print("✅ MidiTok imported and tokenizer initialized successfully.")
except ImportError:
    print("❌ MidiTok is NOT installed.")
except Exception as e:
    print(f"❌ MidiTok initialization failed: {e}")

print("\n--- MusicLang Verification ---")
try:
    from musiclang_predict import MusicLangPredictor
    print("✅ MusicLang Predictor imported.")
    # Optional: Initialize to test weights loading (might be slow)
    # predictor = MusicLangPredictor("musiclang/musiclang-v2")
    # print("✅ MusicLang model loaded.")
except ImportError as e:
    print(f"❌ MusicLang verification failed: {e}")
except Exception as e:
    print(f"❌ MusicLang initialization failed: {e}")

print("\n--- MLX-LM Verification ---")
try:
    import mlx_lm
    print("✅ MLX-LM imported.")
except ImportError:
    print("❌ mlx-lm is NOT installed.")
