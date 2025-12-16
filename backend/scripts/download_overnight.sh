#!/bin/bash
# Overnight Download Script with Mac Sleep Prevention
# This keeps your Mac awake while downloading Llama 3.3 70B

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════════════"
echo "🌙 OVERNIGHT LLAMA 3.3 70B DOWNLOAD WITH SLEEP PREVENTION"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "This script will:"
echo "  ✅ Prevent your Mac from sleeping"
echo "  ✅ Keep display on (optional - press Ctrl+Shift+Eject to turn off)"
echo "  ✅ Download Llama 3.3 70B (37GB)"
echo "  ✅ Log everything to download_log.txt"
echo "  ✅ Play a sound when complete"
echo ""
echo "⏱️  Estimated time: 15-30 minutes"
echo "💾 Download size: 37GB"
echo ""
echo "💡 TIP: You can close this terminal, but keep Terminal.app running"
echo ""

# Check if Python virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "❌ ERROR: Python virtual environment not found!"
    echo "   Please run from the backend directory with .venv activated"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source .venv/bin/activate

# Check if caffeinate exists (it should on macOS)
if ! command -v caffeinate &> /dev/null; then
    echo "⚠️  WARNING: caffeinate command not found (are you on macOS?)"
    echo "   Download will run but Mac may sleep"
    python download_llama_overnight.py
else
    echo "☕ Starting caffeinate (prevents sleep during download)..."
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔒 YOUR MAC WILL NOT SLEEP UNTIL DOWNLOAD COMPLETES"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Run Python script with caffeinate
    # -d: prevent display from sleeping
    # -i: prevent system from idle sleeping
    # -m: prevent disk from idle sleeping
    caffeinate -dim python download_llama_overnight.py

    echo ""
    echo "✅ Download complete! Your Mac can sleep again."
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🎉 ALL DONE!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Check download_log.txt for details"
echo "  2. Your app now uses Llama 3.3 70B for tutorials!"
echo "  3. Run your backend to start using GPT-4 quality AI"
echo ""
