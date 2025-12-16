#!/bin/bash
# Check status of overnight generation

echo "══════════════════════════════════════════════════════════════"
echo "🌙 OVERNIGHT GENERATION STATUS"
echo "══════════════════════════════════════════════════════════════"
echo ""

# Check if download is running
if pgrep -f "download_overnight.sh" > /dev/null; then
    echo "📥 Download: RUNNING"
    echo "   Log: tail -f download_log.txt"
else
    echo "📥 Download: COMPLETED or STOPPED"
fi

# Check if generation is running
if pgrep -f "generate_all_overnight.py" > /dev/null; then
    echo "🎵 Generation: RUNNING"
    echo "   Log: tail -f generation_log.txt"
else
    echo "🎵 Generation: COMPLETED or STOPPED"
fi

echo ""
echo "Recent Download Activity:"
tail -5 download_log.txt 2>/dev/null || echo "  No log yet"

echo ""
echo "Recent Generation Activity:"
tail -5 generation_log.txt 2>/dev/null || echo "  Waiting for download..."

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "To monitor live:"
echo "  Download:   tail -f download_log.txt"
echo "  Generation: tail -f generation_log.txt"
echo "══════════════════════════════════════════════════════════════"
