#!/usr/bin/env python3
"""Analyze MIDI to show chord progression variety."""
import sys
sys.path.insert(0, 'backend')

import asyncio
from app.services.hybrid_music_generator import hybrid_music_generator
from app.schemas.music_generation import MusicGenerationRequest, MusicGenre, MusicKey

async def test_chord_variety():
    """Generate and show chord progression variety."""
    
    print("\n🎹 Testing Dynamic Jazz Progression Generation")
    print("=" * 60)
    
    request = MusicGenerationRequest(
        genre=MusicGenre.JAZZ,
        key=MusicKey.C,
        tempo=120,
        num_bars=12,  # 12 bars
        complexity=7,
        style="bebop",
        include_melody=True,
        include_chords=True,
        synthesize_audio=False
    )
    
    result = await hybrid_music_generator.generate(request)
    
    print(f"\n📊 Generated Chord Progression ({len(result.chord_progression.chords)} chords):")
    print("-" * 60)
    
    for i, chord in enumerate(result.chord_progression.chords):
        bar = i + 1
        print(f"  Bar {bar:2d}: {chord}")
    
    print("\n" + "=" * 60)
    
    # Count unique chords
    unique_chords = set(result.chord_progression.chords)
    print(f"✅ Unique chord symbols: {len(unique_chords)}")
    print(f"   Chords: {', '.join(sorted(unique_chords))}")
    
    if len(unique_chords) >= 4:
        print("🎉 SUCCESS: Dynamic progression with varied chords!")
    else:
        print("⚠️  Still needs more variety")
    
    print(f"\n🎵 MIDI saved to: {result.midi_file}")

if __name__ == "__main__":
    asyncio.run(test_chord_variety())
