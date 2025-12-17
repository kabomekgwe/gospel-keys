#!/usr/bin/env python3
"""Analyze MIDI to verify bar variation in jazz generation."""
import sys
sys.path.insert(0, 'backend')

from mido import MidiFile

def analyze_midi_bars(midi_path: str):
    """Analyze MIDI file to show note distribution per bar."""
    mid = MidiFile(midi_path)
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_bar = ticks_per_beat * 4  # Assuming 4/4
    
    # Collect notes by bar
    bars = {}
    current_tick = 0
    
    for track in mid.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                bar_num = tick // ticks_per_bar
                if bar_num not in bars:
                    bars[bar_num] = set()
                bars[bar_num].add(msg.note)
    
    print(f"\\n🎹 MIDI Analysis: {midi_path}")
    print(f"{'='*60}")
    print(f"Ticks per beat: {ticks_per_beat}")
    print(f"Total bars with notes: {len(bars)}")
    print(f"\\n📊 Notes per bar (MIDI pitch numbers):")
    print(f"{'-'*60}")
    
    # Check for identical bars
    unique_patterns = set()
    for bar, notes in sorted(bars.items()):
        pattern = tuple(sorted(notes))
        unique_patterns.add(pattern)
        
        # Convert MIDI to note names
        note_names = []
        for n in sorted(notes):
            octave = (n // 12) - 1
            pitch_class = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][n % 12]
            note_names.append(f"{pitch_class}{octave}")
        
        print(f"Bar {bar:2d}: {', '.join(note_names)}")
    
    print(f"\\n{'='*60}")
    print(f"✅ Unique note patterns: {len(unique_patterns)} / {len(bars)} bars")
    
    if len(unique_patterns) == len(bars):
        print("🎉 PERFECT: Every bar has a unique voicing!")
    elif len(unique_patterns) >= len(bars) * 0.8:
        print("👍 GOOD: Most bars have distinct voicings")
    elif len(unique_patterns) >= len(bars) * 0.5:
        print("⚠️  FAIR: Some variation present, could be better")
    else:
        print("❌ POOR: Too many identical bars - needs improvement")

if __name__ == "__main__":
    import glob
    # Find most recent MIDI
    midi_files = sorted(glob.glob("backend/output/hybrid_generation/midi/*.mid"))
    if midi_files:
        analyze_midi_bars(midi_files[-1])
    else:
        print("No MIDI files found")
