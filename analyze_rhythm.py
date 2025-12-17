#!/usr/bin/env python3
"""Analyze MIDI rhythm to show note events per beat."""
import sys
sys.path.insert(0, 'backend')

from mido import MidiFile
import glob

def analyze_rhythm(midi_path: str):
    """Analyze MIDI file rhythm patterns."""
    mid = MidiFile(midi_path)
    ticks_per_beat = mid.ticks_per_beat
    
    # Collect note-on events with their timing
    events = []
    
    for track in mid.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                beat = tick / ticks_per_beat
                bar = int(beat // 4)
                beat_in_bar = beat % 4
                events.append({
                    'tick': tick,
                    'bar': bar,
                    'beat': beat_in_bar,
                    'note': msg.note,
                    'vel': msg.velocity
                })
    
    print(f"\n🎹 Rhythm Analysis: {midi_path}")
    print(f"{'='*70}")
    print(f"Ticks per beat: {ticks_per_beat}")
    print(f"Total note events: {len(events)}")
    
    # Group by bar
    bars = {}
    for e in events:
        bar = e['bar']
        if bar not in bars:
            bars[bar] = []
        bars[bar].append(e)
    
    print(f"\n📊 Rhythm breakdown per bar:")
    print(f"{'-'*70}")
    
    for bar_num in sorted(bars.keys())[:8]:  # First 8 bars
        bar_events = bars[bar_num]
        # Group by beat position
        beat_hits = {}
        for e in bar_events:
            beat_pos = round(e['beat'] * 2) / 2  # Round to 8th notes
            if beat_pos not in beat_hits:
                beat_hits[beat_pos] = 0
            beat_hits[beat_pos] += 1
        
        # Create rhythm visualization
        rhythm_vis = ""
        for half_beat in range(8):  # 8 eighth notes per bar
            beat_pos = half_beat / 2
            if beat_pos in beat_hits:
                count = beat_hits[beat_pos]
                rhythm_vis += f"[{count:2d}]"
            else:
                rhythm_vis += "  . "
        
        print(f"Bar {bar_num:2d}: {rhythm_vis}  ({len(bar_events)} notes)")
    
    # Count events per beat position across all bars
    all_beat_positions = {}
    for e in events:
        beat_pos = round(e['beat'] * 2) / 2
        if beat_pos not in all_beat_positions:
            all_beat_positions[beat_pos] = 0
        all_beat_positions[beat_pos] += 1
    
    print(f"\n📈 Overall rhythm distribution:")
    print(f"{'-'*70}")
    for pos in sorted(all_beat_positions.keys()):
        count = all_beat_positions[pos]
        bar_chart = "█" * (count // 5)
        beat_name = f"{int(pos) + 1}" + ("-and" if pos % 1 else "")
        print(f"  {beat_name:8s}: {bar_chart} ({count})")
    
    # Check variety
    total_positions = len([p for p in all_beat_positions if all_beat_positions[p] > 0])
    print(f"\n{'='*70}")
    if total_positions >= 6:
        print("🎉 GREAT: Varied rhythm across multiple beat positions!")
    elif total_positions >= 4:
        print("👍 GOOD: Some rhythmic variety")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Rhythm too static")

if __name__ == "__main__":
    midi_files = sorted(glob.glob("backend/output/hybrid_generation/midi/*.mid"))
    if midi_files:
        analyze_rhythm(midi_files[-1])
    else:
        print("No MIDI files found")
