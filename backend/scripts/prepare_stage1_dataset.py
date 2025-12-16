"""
Stage 1 Dataset Preparation - General Music Collection

Collects and prepares 1000 MIDI files across multiple genres for general
music pretraining. Creates a diverse dataset for foundational music patterns.

Target genres: Gospel (30%), Jazz (25%), Blues (20%), Classical (15%), Neo-Soul (10%)

Usage:
    python scripts/prepare_stage1_dataset.py \
        --output data/training/stage1_general_music \
        --target-files 1000
"""

import argparse
import logging
from pathlib import Path
import shutil
from typing import List
import json
from datetime import datetime

from app.schemas.music_generation import MusicGenre

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Stage1DatasetPreparator:
    """Prepare Stage 1 general music dataset"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Genre distribution targets
        self.genre_targets = {
            MusicGenre.GOSPEL: 300,
            MusicGenre.JAZZ: 250,
            MusicGenre.BLUES: 200,
            MusicGenre.CLASSICAL: 150,
            MusicGenre.NEOSOUL: 100,
        }

    def collect_from_sources(self):
        """Collect MIDI files from various sources"""
        logger.info("📂 Collecting MIDI files from sources...")

        collected = {}

        # Source 1: Existing project data
        logger.info("  Source 1: Checking existing project data...")
        existing_dir = Path("backend/data/gospel_midi")
        if existing_dir.exists():
            gospel_files = list(existing_dir.glob("*.mid")) + list(existing_dir.glob("*.midi"))
            collected[MusicGenre.GOSPEL] = gospel_files[:50]
            logger.info(f"    Found {len(collected[MusicGenre.GOSPEL])} Gospel files")

        # Source 2: User-provided directories
        # Users should place MIDI files in these directories:
        source_dirs = {
            MusicGenre.JAZZ: Path("backend/data/midi_sources/jazz"),
            MusicGenre.BLUES: Path("backend/data/midi_sources/blues"),
            MusicGenre.CLASSICAL: Path("backend/data/midi_sources/classical"),
            MusicGenre.NEOSOUL: Path("backend/data/midi_sources/neosoul"),
        }

        for genre, source_dir in source_dirs.items():
            if source_dir.exists():
                files = list(source_dir.glob("*.mid")) + list(source_dir.glob("*.midi"))
                collected[genre] = files
                logger.info(f"    Found {len(files)} {genre.value} files")
            else:
                logger.warning(f"    ⚠️  {source_dir} not found - create and add MIDI files")
                collected[genre] = []

        return collected

    def generate_synthetic_data(self, genre: MusicGenre, count: int) -> List[Path]:
        """Generate synthetic MIDI files using Phase 1 hybrid generator"""
        logger.info(f"  🤖 Generating {count} synthetic {genre.value} files...")

        # This would use the hybrid generator from Phase 1
        # For now, return empty list (implement after Phase 1 testing)
        logger.warning("    Synthetic generation not yet implemented")
        logger.warning("    Please provide real MIDI files or implement generator")
        return []

    def prepare_dataset(self):
        """Prepare complete Stage 1 dataset"""
        logger.info("🎵 Stage 1 Dataset Preparation")
        logger.info("="*60)
        logger.info(f"Target: {sum(self.genre_targets.values())} files")
        logger.info(f"Output: {self.output_dir}")
        logger.info("")

        # Collect existing files
        collected = self.collect_from_sources()

        # Copy files to output directory
        total_copied = 0
        for genre, target_count in self.genre_targets.items():
            genre_dir = self.output_dir / genre.value
            genre_dir.mkdir(exist_ok=True)

            files = collected.get(genre, [])
            actual_count = min(len(files), target_count)

            logger.info(f"📁 {genre.value}: copying {actual_count}/{target_count} files")

            for i, source_file in enumerate(files[:target_count]):
                dest_file = genre_dir / f"{genre.value}_{i:04d}.mid"
                shutil.copy2(source_file, dest_file)
                total_copied += 1

            # Note shortfall
            if actual_count < target_count:
                shortfall = target_count - actual_count
                logger.warning(f"  ⚠️  Short by {shortfall} files - add more or generate synthetic")

        # Save metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "total_files": total_copied,
            "genre_distribution": {
                genre.value: len(list((self.output_dir / genre.value).glob("*.mid")))
                for genre in self.genre_targets.keys()
            },
            "target_distribution": {k.value: v for k, v in self.genre_targets.items()},
        }

        with open(self.output_dir / "dataset_info.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info("")
        logger.info(f"✅ Stage 1 dataset prepared: {total_copied} files")
        logger.info(f"   Metadata: {self.output_dir / 'dataset_info.json'}")

        return total_copied


def main():
    parser = argparse.ArgumentParser(description="Prepare Stage 1 general music dataset")
    parser.add_argument(
        "--output",
        type=str,
        default="backend/data/training/stage1_general_music",
        help="Output directory"
    )
    parser.add_argument(
        "--target-files",
        type=int,
        default=1000,
        help="Target number of files (distributed across genres)"
    )

    args = parser.parse_args()

    preparator = Stage1DatasetPreparator(output_dir=Path(args.output))
    total = preparator.prepare_dataset()

    if total < args.target_files:
        logger.warning("")
        logger.warning(f"⚠️  Only collected {total}/{args.target_files} files")
        logger.warning("   To reach target:")
        logger.warning("   1. Add MIDI files to backend/data/midi_sources/<genre>/")
        logger.warning("   2. Use Phase 1 hybrid generator to create synthetic data")
        logger.warning("   3. Download free MIDI datasets (MAESTRO, Lakh, etc.)")

    logger.info("🎉 Done!")


if __name__ == "__main__":
    main()
