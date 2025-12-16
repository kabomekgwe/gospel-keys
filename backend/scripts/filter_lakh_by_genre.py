"""
Filter Lakh MIDI Dataset by Genre

Extracts Gospel, Jazz, and Blues MIDI files from the Lakh MIDI Dataset
using filename and path heuristics.

Usage:
    python scripts/filter_lakh_by_genre.py \
        --input data/midi_sources/downloads/lmd_matched \
        --output-dir data/midi_sources \
        --gospel-count 200 \
        --jazz-count 150 \
        --blues-count 100
"""

import argparse
import logging
import shutil
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LakhGenreFilter:
    """Filter Lakh MIDI files by genre keywords"""

    # Genre keyword patterns (in filenames/paths)
    GENRE_KEYWORDS = {
        "gospel": [
            "gospel", "hymn", "spiritual", "praise", "worship",
            "church", "amen", "hallelujah", "blessed", "holy"
        ],
        "jazz": [
            "jazz", "bebop", "swing", "bossa", "samba",
            "coltrane", "davis", "monk", "parker", "dizzy",
            "blue note", "standard"
        ],
        "blues": [
            "blues", "b.b.", "muddy", "howlin", "robert johnson",
            "delta", "chicago blues", "twelve bar"
        ],
    }

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def matches_genre(self, filepath: Path, genre: str) -> bool:
        """Check if file matches genre keywords"""
        # Convert path to lowercase for matching
        path_str = str(filepath).lower()

        # Check against keywords
        keywords = self.GENRE_KEYWORDS.get(genre, [])
        return any(keyword in path_str for keyword in keywords)

    def filter_by_genre(
        self,
        genre: str,
        max_files: int = 200
    ) -> List[Path]:
        """Find MIDI files matching genre"""
        logger.info(f"🔍 Filtering for {genre} (max {max_files} files)...")

        matched_files = []

        # Search through Lakh directory
        midi_files = list(self.input_dir.rglob("*.mid")) + \
                     list(self.input_dir.rglob("*.midi"))

        logger.info(f"   Searching {len(midi_files)} MIDI files...")

        for midi_file in midi_files:
            if len(matched_files) >= max_files:
                break

            if self.matches_genre(midi_file, genre):
                matched_files.append(midi_file)

        logger.info(f"   ✓ Found {len(matched_files)} {genre} files")
        return matched_files

    def copy_files(self, files: List[Path], genre: str):
        """Copy files to genre-specific output directory"""
        genre_dir = self.output_dir / genre
        genre_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📁 Copying {len(files)} files to {genre_dir}...")

        for i, source_file in enumerate(files):
            dest_file = genre_dir / f"{genre}_{i:04d}.mid"
            shutil.copy2(source_file, dest_file)

        logger.info(f"   ✓ Copied {len(files)} {genre} files")

    def filter_all_genres(
        self,
        gospel_count: int = 200,
        jazz_count: int = 150,
        blues_count: int = 100
    ):
        """Filter all genres"""
        logger.info("🎵 Lakh MIDI Genre Filter")
        logger.info("="*60)
        logger.info(f"Input: {self.input_dir}")
        logger.info(f"Output: {self.output_dir}")
        logger.info("")

        results = {}

        # Filter Gospel
        gospel_files = self.filter_by_genre("gospel", gospel_count)
        self.copy_files(gospel_files, "gospel")
        results["gospel"] = len(gospel_files)

        # Filter Jazz
        jazz_files = self.filter_by_genre("jazz", jazz_count)
        self.copy_files(jazz_files, "jazz")
        results["jazz"] = len(jazz_files)

        # Filter Blues
        blues_files = self.filter_by_genre("blues", blues_count)
        self.copy_files(blues_files, "blues")
        results["blues"] = len(blues_files)

        logger.info("")
        logger.info("✅ Genre filtering complete!")
        logger.info(f"   Gospel: {results['gospel']} files")
        logger.info(f"   Jazz: {results['jazz']} files")
        logger.info(f"   Blues: {results['blues']} files")
        logger.info(f"   Total: {sum(results.values())} files")

        return results


def main():
    parser = argparse.ArgumentParser(description="Filter Lakh MIDI by genre")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input directory (Lakh lmd_matched)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory for genre folders"
    )
    parser.add_argument(
        "--gospel-count",
        type=int,
        default=200,
        help="Max Gospel files to extract"
    )
    parser.add_argument(
        "--jazz-count",
        type=int,
        default=150,
        help="Max Jazz files to extract"
    )
    parser.add_argument(
        "--blues-count",
        type=int,
        default=100,
        help="Max Blues files to extract"
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        logger.error(f"❌ Input directory not found: {input_dir}")
        return

    output_dir = Path(args.output_dir)

    # Run filter
    filter_tool = LakhGenreFilter(input_dir, output_dir)
    filter_tool.filter_all_genres(
        gospel_count=args.gospel_count,
        jazz_count=args.jazz_count,
        blues_count=args.blues_count
    )

    logger.info("🎉 Done!")


if __name__ == "__main__":
    main()
