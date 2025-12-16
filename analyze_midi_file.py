import mido
import sys

def analyze_midi(file_path):
    print(f"Analyzing {file_path}")
    try:
        mid = mido.MidiFile(file_path)
        print(f"Type: {mid.type}, Ticks per beat: {mid.ticks_per_beat}, Tracks: {len(mid.tracks)}")
        
        for i, track in enumerate(mid.tracks):
            print(f"\nTrack {i}: {track.name}")
            note_count = 0
            msg_count = len(track)
            print(f"  Total messages: {msg_count}")
            
            # Print first 10 messages
            for j, msg in enumerate(track):
                if j < 10:
                    print(f"    {msg}")
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_count += 1
            
            print(f"  Note On events: {note_count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_midi(sys.argv[1])
    else:
        print("Usage: python analyze_midi_file.py <path_to_midi>")
