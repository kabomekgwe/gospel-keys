"""
Prepare training data for fine-tuning Qwen 2.5-14B on music generation.

Pipeline:
1. Load Gospel MIDI files from dataset
2. Tokenize using MidiTok REMI
3. Extract metadata (key, tempo, genre)
4. Create train/validation splits
5. Save as JSONL for MLX fine-tuning

Usage:
    python scripts/prepare_training_data.py --input data/gospel_midi --output data/training
"""

import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import random

from app.services.ai.midi_service import midi_service
from app.schemas.music_generation import (
    TrainingDataSample,
    TrainingDataset,
    MusicGenre,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingDataPreparator:
    """Prepare MIDI dataset for LLM fine-tuning"""

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.midi_service = midi_service

    def prepare_dataset(
        self,
        genre: MusicGenre = MusicGenre.GOSPEL,
        val_split: float = 0.1,
        max_files: int = None
    ) -> TrainingDataset:
        """
        Prepare complete training dataset from MIDI files.

        Args:
            genre: Musical genre for the dataset
            val_split: Validation split ratio (0.0-1.0)
            max_files: Maximum files to process (None = all)

        Returns:
            Training dataset with metadata
        """
        logger.info(f"📂 Scanning {self.input_dir} for MIDI files...")

        # Find all MIDI files
        midi_files = list(self.input_dir.glob("**/*.mid")) + list(self.input_dir.glob("**/*.midi"))

        if max_files:
            midi_files = midi_files[:max_files]

        logger.info(f"Found {len(midi_files)} MIDI files")

        # Process each file
        samples: List[TrainingDataSample] = []
        total_tokens = 0

        for i, midi_file in enumerate(midi_files, 1):
            logger.info(f"[{i}/{len(midi_files)}] Processing {midi_file.name}...")

            try:
                sample = self._process_midi_file(midi_file, genre)
                samples.append(sample)
                total_tokens += len(sample.tokens)

                if i % 10 == 0:
                    logger.info(f"Processed {i} files, {total_tokens} tokens so far")

            except Exception as e:
                logger.error(f"Failed to process {midi_file}: {e}")
                continue

        logger.info(f"✅ Processed {len(samples)} files successfully")

        # Split into train/val
        random.shuffle(samples)
        val_size = int(len(samples) * val_split)
        train_samples = samples[val_size:]
        val_samples = samples[:val_size]

        logger.info(f"Train samples: {len(train_samples)}")
        logger.info(f"Val samples: {len(val_samples)}")

        # Create dataset
        dataset = TrainingDataset(
            samples=samples,
            vocab_size=self.midi_service.tokenizer.vocab_size,
            total_tokens=total_tokens,
            train_samples=len(train_samples),
            val_samples=len(val_samples),
            tokenizer_config=self._get_tokenizer_config(),
            created_at=datetime.now().isoformat(),
        )

        # Save datasets
        self._save_splits(train_samples, val_samples)
        self._save_metadata(dataset)

        logger.info(f"💾 Dataset saved to {self.output_dir}")

        return dataset

    def _process_midi_file(
        self,
        midi_file: Path,
        genre: MusicGenre
    ) -> TrainingDataSample:
        """Process single MIDI file into training sample"""

        # Tokenize MIDI
        tokens = self.midi_service.tokenize_midi_file(str(midi_file))

        # Extract metadata from filename and MIDI
        metadata = self._extract_metadata(midi_file, genre)

        # Create prompt from metadata
        prompt = self._create_prompt(metadata)

        # Create training sample
        sample = TrainingDataSample(
            prompt=prompt,
            tokens=tokens,
            metadata=metadata,
            source_file=str(midi_file),
            genre=genre,
            key=metadata.get("key"),
            tempo=metadata.get("tempo"),
            num_bars=metadata.get("num_bars"),
        )

        return sample

    def _extract_metadata(self, midi_file: Path, genre: MusicGenre) -> Dict[str, Any]:
        """Extract metadata from MIDI file"""
        import mido

        try:
            mid = mido.MidiFile(midi_file)

            # Extract tempo
            tempo = 120  # Default
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        tempo = int(mido.tempo2bpm(msg.tempo))
                        break

            # Estimate number of bars (simplified)
            ticks_per_beat = mid.ticks_per_beat
            total_ticks = sum(msg.time for track in mid.tracks for msg in track)
            total_beats = total_ticks / ticks_per_beat
            num_bars = int(total_beats / 4)  # Assume 4/4 time

            metadata = {
                "genre": genre.value,
                "tempo": tempo,
                "num_bars": num_bars,
                "filename": midi_file.name,
            }

            # Try to extract key from filename (e.g., "song_C_major.mid")
            stem = midi_file.stem.lower()
            if '_c_' in stem or stem.startswith('c_'):
                metadata["key"] = "C"
            elif '_g_' in stem or stem.startswith('g_'):
                metadata["key"] = "G"
            # Add more key detection logic as needed

            return metadata

        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {"genre": genre.value, "tempo": 120, "num_bars": 8}

    def _create_prompt(self, metadata: Dict[str, Any]) -> str:
        """Create text prompt from metadata for fine-tuning"""

        genre = metadata.get("genre", "gospel")
        key = metadata.get("key", "C")
        tempo = metadata.get("tempo", 120)
        num_bars = metadata.get("num_bars", 8)

        prompt = f"Generate a {genre} piano arrangement in {key} major at {tempo} BPM with {num_bars} bars."

        return prompt

    def _get_tokenizer_config(self) -> Dict[str, Any]:
        """Get MidiTok tokenizer configuration"""
        config = self.midi_service.tokenizer.config

        return {
            "tokenization": "REMI",
            "pitch_range": list(config.pitch_range),
            "beat_res": config.beat_res,
            "num_velocities": config.num_velocities,
            "special_tokens": config.special_tokens,
        }

    def _save_splits(
        self,
        train_samples: List[TrainingDataSample],
        val_samples: List[TrainingDataSample]
    ):
        """Save train/val splits as JSONL"""

        # Save train split
        train_file = self.output_dir / "train.jsonl"
        with open(train_file, 'w') as f:
            for sample in train_samples:
                json_line = json.dumps({
                    "prompt": sample.prompt,
                    "tokens": sample.tokens,
                    "metadata": sample.metadata,
                })
                f.write(json_line + '\n')

        logger.info(f"Saved {len(train_samples)} train samples to {train_file}")

        # Save val split
        val_file = self.output_dir / "val.jsonl"
        with open(val_file, 'w') as f:
            for sample in val_samples:
                json_line = json.dumps({
                    "prompt": sample.prompt,
                    "tokens": sample.tokens,
                    "metadata": sample.metadata,
                })
                f.write(json_line + '\n')

        logger.info(f"Saved {len(val_samples)} val samples to {val_file}")

    def _save_metadata(self, dataset: TrainingDataset):
        """Save dataset metadata"""
        metadata_file = self.output_dir / "dataset_info.json"

        with open(metadata_file, 'w') as f:
            json.dump(dataset.dict(), f, indent=2, default=str)

        logger.info(f"Saved metadata to {metadata_file}")


def main():
    parser = argparse.ArgumentParser(description="Prepare training data from MIDI files")
    parser.add_argument(
        "--input",
        type=str,
        default="backend/data/gospel_midi",
        help="Input directory with MIDI files"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="backend/data/training",
        help="Output directory for training data"
    )
    parser.add_argument(
        "--genre",
        type=str,
        default="gospel",
        choices=["gospel", "jazz", "blues", "classical"],
        help="Musical genre"
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.1,
        help="Validation split ratio (0.0-1.0)"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum files to process (None = all)"
    )

    args = parser.parse_args()

    logger.info("🎼 Starting training data preparation...")
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Genre: {args.genre}")

    # Create preparator
    preparator = TrainingDataPreparator(
        input_dir=Path(args.input),
        output_dir=Path(args.output)
    )

    # Prepare dataset
    dataset = preparator.prepare_dataset(
        genre=MusicGenre(args.genre),
        val_split=args.val_split,
        max_files=args.max_files
    )

    logger.info("✅ Training data preparation complete!")
    logger.info(f"Total samples: {len(dataset.samples)}")
    logger.info(f"Total tokens: {dataset.total_tokens}")
    logger.info(f"Vocab size: {dataset.vocab_size}")


if __name__ == "__main__":
    main()
