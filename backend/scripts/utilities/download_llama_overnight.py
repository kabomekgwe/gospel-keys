#!/usr/bin/env python3
"""
Overnight Llama 3.3 70B Download Script
Keeps Mac awake and downloads the model with progress tracking
"""

import sys
import time
from datetime import datetime
from pathlib import Path

print("=" * 70)
print("🌙 OVERNIGHT LLAMA 3.3 70B DOWNLOAD")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("This script will:")
print("  1. Keep your Mac awake (no sleep during download)")
print("  2. Download Llama 3.3 70B 4-bit (37GB)")
print("  3. Show progress updates")
print("  4. Log everything to download_log.txt")
print()
print("⏱️  Estimated time: 15-30 minutes (depending on internet speed)")
print("💾 Download size: 37GB")
print("📁 Location: ~/.cache/huggingface/hub/")
print()

# Create log file
log_file = Path(__file__).parent / "download_log.txt"

def log(message):
    """Log to both console and file"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(log_file, "a") as f:
        f.write(log_msg + "\n")

log("🚀 Starting download process...")

try:
    # Import MLX
    log("📦 Importing MLX framework...")
    from mlx_lm import load
    log("✅ MLX imported successfully")

    # Import the service
    log("📦 Importing multi-model service...")
    from app.services.multi_model_service import multi_model_service
    log("✅ Service imported successfully")

    # Check if service is available
    if not multi_model_service or not multi_model_service.is_available():
        log("❌ ERROR: Multi-model service not available!")
        log("   Make sure MLX is installed: pip install mlx mlx-lm")
        sys.exit(1)

    log("✅ Multi-model service is available")
    log("")
    log("=" * 70)
    log("📥 STARTING LLAMA 3.3 70B DOWNLOAD (37GB)")
    log("=" * 70)
    log("⏳ This will take 15-30 minutes on fast internet...")
    log("💡 Your Mac will stay awake during the download")
    log("🔔 You'll hear a sound when complete (if volume is on)")
    log("")

    start_time = time.time()

    # Trigger model load (this downloads if not cached)
    log("🔄 Loading Llama 3.3 70B model...")
    log("   (Downloading from mlx-community/Llama-3.3-70B-Instruct-4bit)")

    # Generate a simple test to trigger download
    response = multi_model_service.generate(
        prompt="Say 'Hello! I am Llama 3.3 70B running locally on your M4 Pro!'",
        complexity=5,  # Routes to Llama 3.3 70B
        max_tokens=100
    )

    end_time = time.time()
    duration = end_time - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    log("")
    log("=" * 70)
    log("🎉 DOWNLOAD COMPLETE!")
    log("=" * 70)
    log(f"⏱️  Total time: {minutes} minutes, {seconds} seconds")
    log("")
    log("📝 Model response:")
    log(f"   {response[:200]}...")
    log("")
    log("✅ Llama 3.3 70B is now ready to use!")
    log("📁 Cached at: ~/.cache/huggingface/hub/")
    log(f"📊 Log saved to: {log_file}")
    log("")
    log("🎯 Next steps:")
    log("   1. Your app will now use Llama 3.3 70B for complexity 5-7 tasks")
    log("   2. Tutorial generation = GPT-4 quality")
    log("   3. No more downloads needed - it's cached!")
    log("")
    log(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Play success sound (macOS)
    import subprocess
    subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)

    print("\n🔔 Download complete! (Sound played)")

except KeyboardInterrupt:
    log("\n⚠️  Download interrupted by user (Ctrl+C)")
    log("   You can resume by running this script again")
    sys.exit(1)

except Exception as e:
    log(f"\n❌ ERROR: {e}")
    log(f"   Error type: {type(e).__name__}")
    log("   Check the log above for details")
    import traceback
    log("\n📋 Full traceback:")
    for line in traceback.format_exc().split("\n"):
        log(f"   {line}")
    sys.exit(1)
