
import asyncio
from app.services.hybrid_music_generator import hybrid_music_generator
from app.schemas.music_generation import MusicGenerationRequest, MusicGenre, MusicKey

async def main():
    print("Testing Hybrid Generator...")
    req = MusicGenerationRequest(
        genre=MusicGenre.JAZZ,
        key=MusicKey.C,
        tempo=120,
        num_bars=8,
        complexity=5,
        include_melody=True,
        include_chords=True,
        include_bass=True,
        synthesize_audio=False,
        use_gpu_synthesis=False,
        add_reverb=False
    )
    
    try:
        res = await hybrid_music_generator.generate(req)
        print("Success!")
        print(f"MIDI: {res.midi_file}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
