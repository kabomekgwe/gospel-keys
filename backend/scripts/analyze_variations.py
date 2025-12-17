
import asyncio
import sys
import os
import json
import logging
import time
import statistics
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.gospel_generator import GospelGeneratorService
from app.services.jazz_generator import JazzGeneratorService
from app.services.blues_generator import BluesGeneratorService
from app.services.neosoul_generator import NeosoulGeneratorService
from app.services.rnb_generator import RnBGeneratorService
from app.services.latin_generator import LatinGeneratorService
from app.services.reggae_generator import ReggaeGeneratorService
from app.services.classical_generator import ClassicalGeneratorService

from app.services.base_genre_generator import BaseGenreGenerator
from app.services.generator_utils import export_to_midi
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("VariationAnalyzer")

# Mock classes for Request/Response to avoid Pydantic issues or API requirements
class MockRequest:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'include_progression'):
            self.include_progression = False
        if not hasattr(self, 'ai_percentage'):
            self.ai_percentage = 0.0

class MockApplication:
    def __init__(self, value):
        self.value = value

# Analysis Metrics
class MidiMetrics:
    def __init__(self, arrangement, midi_path):
        self.total_notes = len(arrangement.left_hand_notes) + len(arrangement.right_hand_notes)
        self.lh_notes = len(arrangement.left_hand_notes)
        self.rh_notes = len(arrangement.right_hand_notes)
        self.duration = arrangement.total_duration_seconds
        self.notes_per_second = self.total_notes / self.duration if self.duration > 0 else 0
        
        all_velocities = [n.velocity for n in arrangement.left_hand_notes + arrangement.right_hand_notes]
        self.velocity_mean = statistics.mean(all_velocities) if all_velocities else 0
        self.velocity_std = statistics.stdev(all_velocities) if len(all_velocities) > 1 else 0
        
        all_pitches = [n.pitch for n in arrangement.left_hand_notes + arrangement.right_hand_notes]
        self.pitch_unique = len(set(all_pitches))
        self.pitch_range = (max(all_pitches) - min(all_pitches)) if all_pitches else 0

    def to_dict(self):
        return {
            "total_notes": self.total_notes,
            "notes_per_sec": round(self.notes_per_second, 2),
            "velocity_mean": round(self.velocity_mean, 2),
            "velocity_std": round(self.velocity_std, 2),
            "pitch_unique": self.pitch_unique,
            "pitch_range": self.pitch_range
        }

# Test Configuration
GENRE_CONFIGS = {
    "Gospel": {
        "service": GospelGeneratorService,
        "styles": ["worship", "uptempo", "concert", "practice"],
    },
    "Jazz": {
        "service": JazzGeneratorService,
        "styles": ["ballad", "standard", "uptempo"],
    },
    "Blues": {
        "service": BluesGeneratorService,
        "styles": ["slow", "shuffle", "fast"],
    },
    "Neosoul": {
        "service": NeosoulGeneratorService,
        "styles": ["smooth", "uptempo"],
    },
    "RnB": {
        "service": RnBGeneratorService,
        "styles": ["ballad", "groove", "uptempo"],
    },
    "Latin": {
        "service": LatinGeneratorService,
        "styles": ["salsa", "ballad", "uptempo"],
    },
    "Reggae": {
        "service": ReggaeGeneratorService,
        "styles": ["roots", "dancehall", "dub"],
    },
    "Classical": {
        "service": ClassicalGeneratorService,
        "styles": ["baroque", "classical", "romantic"],
    }
}

COMPLEXITY_LEVELS = [3, 5, 8]  # Low, Med, High

async def run_analysis():
    results = []
    
    logger.info("Starting Variation Analysis...")
    logger.info("===============================")

    for genre_name, config in GENRE_CONFIGS.items():
        logger.info(f"\n--- Analyzing {genre_name} ---")
        
        try:
            # Initialize service
            service_class = config["service"]
            service = service_class()
            
            for style in config["styles"]:
                for complexity in COMPLEXITY_LEVELS:
                    logger.info(f"Generating {genre_name} | Style: {style} | Complexity: {complexity}")
                    
                    # Create request
                    desc = f"{style} {genre_name} song"
                    request = MockRequest(
                        description=desc,
                        key="C",
                        tempo=100, # Default tempo
                        num_bars=4,
                        complexity=complexity,
                        style=style,
                        application=MockApplication(style),
                        include_progression=False
                    )
                    
                    try:
                        # 1. Generate chords (fallback)
                        chords, key, tempo = service._parse_description_with_fallback(
                            request.description, request.key, request.tempo
                        )
                        
                        # 2. Arrange
                        arrangement = service._create_arrangement(
                            chords=chords,
                            key=key,
                            tempo=tempo,
                            request=request
                        )
                        
                        # 3. Export (to get file size if needed, but mainly for object validity)
                        midi_path, _ = export_to_midi(
                            arrangement, 
                            "test_variations", 
                            f"{genre_name.lower()}_{style}_{complexity}"
                        )
                        
                        # 4. Analyze
                        metrics = MidiMetrics(arrangement, midi_path)
                        
                        result = {
                            "genre": genre_name,
                            "style": style,
                            "complexity": complexity,
                            **metrics.to_dict()
                        }
                        results.append(result)
                        
                    except Exception as e:
                        logger.error(f"Failed to generate {genre_name}/{style}/{complexity}: {str(e)}")
                        # traceback.print_exc()

        except Exception as e:
            logger.error(f"Failed to initialize {genre_name}: {str(e)}")

    # Output Results
    print_results_table(results)
    save_results_json(results)

def print_results_table(results):
    print("\n" + "="*100)
    print(f"{'GENRE':<12} | {'STYLE':<12} | {'CMP LX':<6} | {'NOTES':<6} | {'N/SEC':<6} | {'VEL_STD':<8} | {'P_RNG':<6}")
    print("-" * 100)
    
    last_genre = ""
    for r in results:
        if r['genre'] != last_genre and last_genre != "":
            print("-" * 100)
        last_genre = r['genre']
        
        print(f"{r['genre']:<12} | {r['style']:<12} | {r['complexity']:<6} | "
              f"{r['total_notes']:<6} | {r['notes_per_sec']:<6} | "
              f"{r['velocity_std']:<8} | {r['pitch_range']:<6}")
    print("="*100)

def save_results_json(results):
    output_path = Path("variation_analysis_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {output_path.absolute()}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
