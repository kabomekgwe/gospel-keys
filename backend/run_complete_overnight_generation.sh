#!/bin/bash
# Complete Overnight Generation: Download + Generate
# This script runs EVERYTHING overnight

set -e

echo "═══════════════════════════════════════════════════════════════════"
echo "🌙 COMPLETE OVERNIGHT GENERATION"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "This will:"
echo "  1️⃣  Download Llama 3.3 70B (37GB) - ~15-30 minutes"
echo "  2️⃣  Generate complete curriculum with GPT-4 quality - ~2-4 hours"
echo "  3️⃣  Create MIDI, MusicXML, theory files"
echo "  4️⃣  Structure for UI consumption"
echo ""
echo "⏱️  Total time: 2-5 hours"
echo "💡 Your Mac will stay awake the entire time"
echo ""
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

# Activate Python environment
echo "🐍 Activating Python virtual environment..."
source .venv/bin/activate

# Keep Mac awake while running
echo "☕ Starting caffeinate (prevents sleep)..."
echo ""

# Run the complete generation script with caffeinate
caffeinate -dim python generate_all_overnight.py

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "✅ COMPLETE OVERNIGHT GENERATION FINISHED!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Check these files:"
echo "  - backend/generation_log.txt (detailed log)"
echo "  - generated_curriculum/ (all generated content)"
echo ""
echo "Next: Start your backend and visit:"
echo "  - http://localhost:3000/curriculum"
echo "  - http://localhost:3000/practice"
echo ""
