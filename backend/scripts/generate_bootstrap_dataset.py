"""
Bootstrap Dataset Generator - Generate Training MIDI with Phase 1

Uses the Phase 1 hybrid music generator to create synthetic training data
for Phase 2 fine-tuning. Generates diverse Gospel, Jazz, and Blues MIDI files
with variations in key, tempo, and style.

Usage:
    python scripts/generate_bootstrap_dataset.py \
        --output data/midi_sources/gospel \
        --count 250 \
        --genre gospel
"""

import argparse
import asyncio
import logging
import json
from pathlib import Path
import shutil
from typing import Optional, Dict, Any

from app.schemas.music_generation import (
    MusicGenerationRequest,
    MusicGenre,
    MusicKey,
)
from app.services.hybrid_music_generator import hybrid_music_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BootstrapDatasetGenerator:
    """Generate synthetic MIDI files using Phase 1 hybrid generator"""

    # Key variations for diversity
    KEYS = [
        MusicKey.C, MusicKey.F, MusicKey.G,
        MusicKey.B_FLAT, MusicKey.E_FLAT, MusicKey.D,
        MusicKey.A, MusicKey.E
    ]

    # Style variations by genre
    STYLES = {
        MusicGenre.GOSPEL: ["traditional", "contemporary", "jazz"],
        MusicGenre.JAZZ: ["bebop", "swing", "modal"],
        MusicGenre.BLUES: ["standard", "minor", "shuffle"],
    }

    # Tempo variations
    TEMPOS = [80, 100, 120, 140, 160]

    TEMPOS = [80, 100, 120, 140, 160]

    def __init__(self, output_dir: Path, genre: MusicGenre, template_path: Optional[Path] = None):
        self.output_dir = output_dir
        self.genre = genre
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_data = self._load_template(template_path) if template_path else None
        
        self.generated_count = 0

    def _load_template(self, template_path: Path) -> Optional[Dict[str, Any]]:
        """Load and find genre-specific template"""
        try:
            with open(template_path, 'r') as f:
                data = json.load(f)
            
            # Find template for current genre
            genres = data.get('genres', [])
            for g in genres:
                if g.get('genre', '').lower() == self.genre.value.lower():
                    logger.info(f"📄 Found {self.genre.value} template in {template_path.name}")
                    return g.get('musicSheetTemplate')
            
            logger.warning(f"⚠️ No matching template for {self.genre.value} in {template_path.name}")
            return None
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return None

    async def generate_variation(
        self,
        key: MusicKey,
        style: str,
        tempo: int,
        num_bars: int = 8
    ) -> str:
        """Generate single MIDI variation"""

        request = MusicGenerationRequest(
            genre=self.genre,
            key=key,
            tempo=tempo,
            num_bars=num_bars,
            time_signature="4/4",
            style=style,
            complexity=6,
            include_melody=True,
            include_bass=False,
            include_chords=True,
            synthesize_audio=False,  # MIDI only
            use_gpu_synthesis=False,
            add_reverb=False,
            template_data=self.template_data # Pass template if loaded
        )

        try:
            response = await hybrid_music_generator.generate(request)
            return response.midi_file

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None

    async def generate_dataset(self, target_count: int = 250, num_bars: int = 8):
        """Generate complete dataset with variations"""

        logger.info("🤖 Bootstrap Dataset Generator")
        logger.info("="*60)
        logger.info(f"Genre: {self.genre.value}")
        logger.info(f"Target: {target_count} files")
        logger.info(f"Bars: {num_bars}")
        logger.info(f"Output: {self.output_dir}")
        logger.info("")

        styles = self.STYLES.get(self.genre, ["traditional"])

        # Calculate variations needed
        variations_per_setting = max(1, target_count // (len(self.KEYS) * len(styles) * len(self.TEMPOS)))

        logger.info(f"Generating {variations_per_setting} variations per setting...")
        logger.info("")

        generated_files = []

        for key in self.KEYS:
            for style in styles:
                for tempo in self.TEMPOS:
                    for variation in range(variations_per_setting):
                        if self.generated_count >= target_count:
                            break

                        logger.info(
                            f"[{self.generated_count + 1}/{target_count}] "
                            f"Generating {self.genre.value} in {key.value}, "
                            f"style={style}, tempo={tempo}, var={variation}..."
                        )

                        midi_file = await self.generate_variation(
                            key=key,
                            style=style,
                            tempo=tempo,
                            num_bars=num_bars
                        )

                        if midi_file and Path(midi_file).exists():
                            # Copy to output directory with descriptive name
                            output_name = (
                                f"{self.genre.value}_{key.value}_"
                                f"{style}_{tempo}bpm_var{variation}.mid"
                            )
                            output_path = self.output_dir / output_name

                            shutil.copy2(midi_file, output_path)
                            generated_files.append(output_path)
                            self.generated_count += 1

                            logger.info(f"   ✓ Saved: {output_name}")
                        else:
                            logger.warning(f"   ✗ Generation failed")

                    if self.generated_count >= target_count:
                        break
                if self.generated_count >= target_count:
                    break
            if self.generated_count >= target_count:
                break

        logger.info("")
        logger.info(f"✅ Bootstrap generation complete!")
        logger.info(f"   Generated: {self.generated_count} files")
        logger.info(f"   Output: {self.output_dir}")

        return generated_files


async def main_async(args):
    """Async main function"""

    genre = MusicGenre(args.genre)
    output_dir = Path(args.output)

    generator = BootstrapDatasetGenerator(
        output_dir=output_dir,
        genre=genre,
        template_path=Path(args.template) if args.template else None
    )

    files = await generator.generate_dataset(
        target_count=args.count,
        num_bars=args.bars
    )

    logger.info("")
    logger.info(f"🎉 Generated {len(files)} {genre.value} MIDI files!")
    logger.info("   Ready for Phase 2 training")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic MIDI dataset with Phase 1"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output directory for generated MIDI files"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=250,
        help="Number of files to generate"
    )
    parser.add_argument(
        "--genre",
        type=str,
        default="gospel",
        choices=["gospel", "jazz", "blues", "classical", "neosoul"],
        help="Genre to generate"
    )

    parser.add_argument(
        "--bars",
        type=int,
        default=8,
        help="Number of bars per file"
    )

    parser.add_argument(
        "--template",
        type=str,
        help="Path to JSON template for World Class generation"
    )

    args = parser.parse_args()

    # Run async generator
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
