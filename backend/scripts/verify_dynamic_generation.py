
import sys
import os
import asyncio
import logging
import pretty_midi
import numpy as np
import time
from pathlib import Path
from typing import List, Any
from pydantic import BaseModel

# Setup Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DynamicVerify")

# Import Services and Schemas
from app.services.gospel_generator import gospel_generator_service
from app.schemas.gospel import GenerateGospelRequest
from app.services.jazz_generator import jazz_generator_service
from app.schemas.jazz import GenerateJazzRequest
from app.services.blues_generator import blues_generator_service
from app.schemas.blues import GenerateBluesRequest
from app.services.neosoul_generator import neosoul_generator_service
from app.schemas.neosoul import GenerateNeosoulRequest
from app.services.rnb_generator import rnb_generator_service
from app.schemas.rnb import GenerateRnBRequest
from app.services.latin_generator import latin_generator_service
from app.schemas.latin import GenerateLatinRequest
from app.services.reggae_generator import reggae_generator_service
from app.schemas.reggae import GenerateReggaeRequest
from app.services.classical_generator import classical_generator_service
from app.schemas.classical import GenerateClassicalRequest

OUTPUT_DIR = Path("test_outputs/dynamic_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def analyze_midi(file_path: Path):
    """Analyze a MIDI file and return metrics."""
    try:
        pm = pretty_midi.PrettyMIDI(str(file_path))
        
        total_notes = sum(len(inst.notes) for inst in pm.instruments)
        
        velocities = []
        durations = []
        pitches = set()
        
        for inst in pm.instruments:
            for note in inst.notes:
                velocities.append(note.velocity)
                durations.append(note.end - note.start)
                pitches.add(note.pitch)
        
        if not velocities:
            return {
                "notes": 0, "vel_mean": 0, "vel_std": 0, 
                "dur_mean": 0, "unique_pitches": 0
            }
            
        return {
            "notes": total_notes,
            "vel_mean": np.mean(velocities),
            "vel_std": np.std(velocities),
            "dur_mean": np.mean(durations),
            "unique_pitches": len(pitches)
        }
    except Exception as e:
        logger.error(f"Failed to analyze {file_path}: {e}")
        return None

async def run_test(service, request_class, genre_name, genre_style_low, genre_style_high):
    logger.info(f"--- Testing {genre_name} ---")
    
    # Identify Output Directory
    # We cheat a bit by inspecting the service instance attributes
    subdir = getattr(service, 'output_subdir', f"{genre_name.lower()}_generated")
    # Base path likely relative to backend root or defined in settings
    base_output = Path("outputs") # Default in many setups
    if not base_output.exists():
        base_output = Path("backend/outputs")
    
    target_dir = base_output / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    
    def get_latest_midi(d: Path):
        files = list(d.glob("*.mid"))
        if not files: return None
        return max(files, key=os.path.getmtime)

    # 1. Low Complexity Test
    logger.info(f"Generating Low Complexity {genre_name}...")
    req_low = request_class(
        description=f"Generate a {genre_style_low} {genre_name} piece",
        key="C",
        tempo=100,
        complexity=2,
        style=genre_style_low,
        length=4
    )
    
    # Construct method name dynamically
    method_name = f"generate_{genre_name.lower().replace('-', '').replace(' ', '')}_arrangement"
    if genre_name == "Neo-Soul": method_name = "generate_neosoul_arrangement"
    if genre_name == "R&B": method_name = "generate_rnb_arrangement"
    
    generate_method = getattr(service, method_name, None)
    if not generate_method:
            generate_method = service.generate_arrangement
    
    midi_low_path = None
    try:
        start_t = time.time()
        # Capture state before
        before_file = get_latest_midi(target_dir)
        
        await generate_method(req_low)
        
        # Check after
        after_file = get_latest_midi(target_dir)
        if after_file and after_file != before_file:
            midi_low_path = after_file
            logger.info(f"Low Output found: {midi_low_path.name}")
        else:
            logger.warning("No new file detected for Low complexity")

    except Exception as e:
        logger.error(f"Service call failed (Pydantic?): {e}")
        # Even if it failed, maybe file was written?
        after_file = get_latest_midi(target_dir)
        if after_file: # We can't be strictly sure it's the new one but let's assume
             if time.time() - os.path.getmtime(after_file) < 5: # Created in last 5 secs
                 midi_low_path = after_file
                 logger.info(f"Recovered Low Output: {midi_low_path.name}")

    # 2. High Complexity Test
    time.sleep(1.5) # ensure unique filename timestamp
    logger.info(f"Generating High Complexity {genre_name}...")
    req_high = request_class(
        description=f"Generate a {genre_style_high} {genre_name} piece",
        key="C",
        tempo=100,
        complexity=9,
        style=genre_style_high,
        length=4
    )
    
    midi_high_path = None
    try:
        start_t = time.time()
        before_file = get_latest_midi(target_dir)
        
        await generate_method(req_high)
        
        after_file = get_latest_midi(target_dir)
        if after_file and after_file != before_file:
            midi_high_path = after_file
            logger.info(f"High Output found: {midi_high_path.name}")
        else:
             logger.warning("No new file detected for High complexity")

    except Exception as e:
        logger.error(f"Service call failed (Pydantic?): {e}")
        after_file = get_latest_midi(target_dir)
        if after_file:
             if time.time() - os.path.getmtime(after_file) < 5:
                 midi_high_path = after_file
                 logger.info(f"Recovered High Output: {midi_high_path.name}")
    
    # Analyze
    metrics_low = {}
    if midi_low_path:
        metrics_low = await analyze_midi(midi_low_path) or {}

    metrics_high = {}
    if midi_high_path:
        metrics_high = await analyze_midi(midi_high_path) or {}
        
    return {
        "genre": genre_name,
        "low": metrics_low,
        "high": metrics_high
    }

async def main():
    results = []
    
    tests = [
        (gospel_generator_service, GenerateGospelRequest, "Gospel", "Traditional", "Contemporary Shout"),
        (jazz_generator_service, GenerateJazzRequest, "Jazz", "Swing Ballad", "Fusion Bebop"),
        (blues_generator_service, GenerateBluesRequest, "Blues", "Delta Blues", "Jazz Blues"),
        (neosoul_generator_service, GenerateNeosoulRequest, "Neo-Soul", "Laid back", "Dilla Style"),
        (rnb_generator_service, GenerateRnBRequest, "R&B", "Ballad", "Future Soul"),
        (latin_generator_service, GenerateLatinRequest, "Latin", "Bolero", "Timba Salsa"),
        (reggae_generator_service, GenerateReggaeRequest, "Reggae", "Roots", "Dub"),
        (classical_generator_service, GenerateClassicalRequest, "Classical", "Baroque Minuet", "Romantic Etude"),
    ]
    
    for service, req_class, name, low_style, high_style in tests:
        res = await run_test(service, req_class, name, low_style, high_style)
        if res:
            results.append(res)
            
    # Print Summary
    print("\n" + "="*80)
    print(f"{'GENRE':<12} | {'LC NOTES':<10} | {'HC NOTES':<10} | {'LC VEL STD':<10} | {'HC VEL STD':<10} | {'LC PITCHES':<10} | {'HC PITCHES':<10}")
    print("-" * 80)
    for r in results:
        low = r['low']
        high = r['high']
        print(f"{r['genre']:<12} | "
              f"{low.get('notes', 0):<10} | "
              f"{high.get('notes', 0):<10} | "
              f"{low.get('vel_std', 0):<10.2f} | "
              f"{high.get('vel_std', 0):<10.2f} | "
              f"{low.get('unique_pitches', 0):<10} | "
              f"{high.get('unique_pitches', 0):<10}")
    print("="*80)
    print("LC = Low Complexity (2), HC = High Complexity (9)")
    print("Higher Pitch Diversity and Note Count in HC typically indicates successful dynamic generation.")

if __name__ == "__main__":
    asyncio.run(main())
