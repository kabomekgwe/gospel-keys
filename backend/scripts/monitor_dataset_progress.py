#!/usr/bin/env python3
"""
Real-Time Dataset Collection Monitor

Live dashboard showing:
- MIDIs collected vs target
- Current download/transcription status
- Success/failure rate
- Estimated time remaining
- Storage usage

Usage:
    python scripts/monitor_dataset_progress.py --output data/gospel_dataset
    python scripts/monitor_dataset_progress.py --refresh 5  # Update every 5 seconds
"""

import time
import argparse
from pathlib import Path
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
import os


@dataclass
class DatasetStats:
    """Dataset collection statistics."""
    total_validated: int
    total_attempted: int
    success_rate: float
    avg_time_per_midi: float
    estimated_remaining: timedelta
    storage_mb: float
    styles: dict[str, int]


class DatasetMonitor:
    """Real-time monitor for gospel dataset collection."""

    def __init__(self, output_dir: Path, refresh_seconds: int = 2):
        self.output_dir = output_dir
        self.refresh_seconds = refresh_seconds
        self.start_time = None

    def get_stats(self) -> DatasetStats:
        """Get current dataset statistics."""
        validated_dir = self.output_dir / "validated"
        metadata_file = self.output_dir / "dataset_metadata.json"

        # Count validated MIDIs
        validated_midis = list(validated_dir.glob("*.mid")) if validated_dir.exists() else []
        total_validated = len(validated_midis)

        # Load metadata to get total attempted
        metadata = {"youtube": [], "validated": []}
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)

        total_attempted = len(metadata.get("youtube", []))
        success_rate = (total_validated / total_attempted * 100) if total_attempted > 0 else 0

        # Calculate storage
        storage_mb = sum(f.stat().st_size for f in validated_midis) / (1024 * 1024)

        # Calculate timing
        if self.start_time:
            elapsed = time.time() - self.start_time
            avg_time = elapsed / total_validated if total_validated > 0 else 0
        else:
            avg_time = 0

        # Style distribution
        styles = {}
        for entry in metadata.get("validated", []):
            style = entry.get("style", "unknown")
            styles[style] = styles.get(style, 0) + 1

        # Estimated remaining (if we know target)
        # Placeholder for now
        estimated_remaining = timedelta(seconds=0)

        return DatasetStats(
            total_validated=total_validated,
            total_attempted=total_attempted,
            success_rate=success_rate,
            avg_time_per_midi=avg_time,
            estimated_remaining=estimated_remaining,
            storage_mb=storage_mb,
            styles=styles
        )

    def display_stats(self, stats: DatasetStats, target: int = 500):
        """Display statistics in terminal."""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')

        print("=" * 70)
        print("🎹  GOSPEL MIDI DATASET COLLECTION - LIVE MONITOR")
        print("=" * 70)
        print()

        # Progress bar
        progress_pct = (stats.total_validated / target * 100) if target > 0 else 0
        bar_width = 50
        filled = int(bar_width * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        print(f"📊 Progress: {stats.total_validated}/{target} MIDIs")
        print(f"[{bar}] {progress_pct:.1f}%")
        print()

        # Statistics
        print(f"✅ Validated:        {stats.total_validated} files")
        print(f"🎯 Attempted:        {stats.total_attempted} downloads")
        print(f"📈 Success Rate:     {stats.success_rate:.1f}%")
        print(f"💾 Storage:          {stats.storage_mb:.1f} MB")
        print()

        # Timing
        if stats.avg_time_per_midi > 0:
            print(f"⏱️  Avg Time/MIDI:    {stats.avg_time_per_midi:.1f}s")
            remaining_midis = target - stats.total_validated
            eta_seconds = remaining_midis * stats.avg_time_per_midi
            eta = timedelta(seconds=int(eta_seconds))
            print(f"⏳ Estimated ETA:     {eta}")
            print()

        # Style distribution
        if stats.styles:
            print("🎨 Style Distribution:")
            for style, count in sorted(stats.styles.items(), key=lambda x: x[1], reverse=True):
                pct = (count / stats.total_validated * 100) if stats.total_validated > 0 else 0
                bar_small = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"   {style:15s} [{bar_small}] {count:3d} ({pct:5.1f}%)")
            print()

        # Recommendations
        print("💡 Recommendations:")
        if stats.total_validated < 100:
            print(f"   ⚠️  Need at least 100 MIDIs for training (have {stats.total_validated})")
        elif stats.total_validated < 500:
            print(f"   ✅ Sufficient for basic training ({stats.total_validated} MIDIs)")
            print(f"   💡 Collect 500+ for best quality")
        else:
            print(f"   ✅ Excellent dataset size ({stats.total_validated} MIDIs)!")
            print(f"   🚀 Ready for MLX fine-tuning on M4 Pro!")

        print()
        print(f"🔄 Refreshing every {self.refresh_seconds}s... (Ctrl+C to exit)")
        print("=" * 70)

    def monitor_live(self, target: int = 500):
        """Live monitoring loop."""
        self.start_time = time.time()

        try:
            while True:
                stats = self.get_stats()
                self.display_stats(stats, target)

                # Check if target reached
                if stats.total_validated >= target:
                    print(f"\n🎉 Target reached! {stats.total_validated}/{target} MIDIs collected!")
                    print(f"\n📋 Next step: Run training script")
                    print(f"   ~/.local/bin/uv run python scripts/train_mlx_gospel.py")
                    break

                time.sleep(self.refresh_seconds)

        except KeyboardInterrupt:
            print("\n\n✋ Monitor stopped by user")
            stats = self.get_stats()
            print(f"\n📊 Final Stats:")
            print(f"   Validated: {stats.total_validated} MIDIs")
            print(f"   Success Rate: {stats.success_rate:.1f}%")
            print(f"   Storage: {stats.storage_mb:.1f} MB")


def main():
    parser = argparse.ArgumentParser(description="Monitor gospel dataset collection")
    parser.add_argument("--output", type=Path, default=Path("data/gospel_dataset"))
    parser.add_argument("--target", type=int, default=500, help="Target MIDI count")
    parser.add_argument("--refresh", type=int, default=2, help="Refresh interval (seconds)")
    parser.add_argument("--once", action="store_true", help="Show stats once and exit")

    args = parser.parse_args()

    monitor = DatasetMonitor(args.output, args.refresh)

    if args.once:
        stats = monitor.get_stats()
        monitor.display_stats(stats, args.target)
    else:
        monitor.monitor_live(args.target)


if __name__ == "__main__":
    main()
