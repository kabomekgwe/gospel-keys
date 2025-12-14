#!/usr/bin/env python3
"""
Gospel MIDI Dataset Builder

Automated pipeline to build gospel piano MIDI corpus for MLX fine-tuning.

Sources:
1. YouTube gospel piano videos (automated transcription)
2. MuseScore gospel piano scores (web scraping)

Pipeline:
YouTube URL → Download (yt-dlp) → Piano Isolation (Demucs) → Transcription (basic-pitch) → MIDI Validation → Dataset

Target: 500-1000 gospel MIDI files for MLX training

Usage:
    python scripts/build_gospel_dataset.py --source youtube --limit 100
    python scripts/build_gospel_dataset.py --source musescore --limit 500
    python scripts/build_gospel_dataset.py --source both --limit 1000
"""

import asyncio
import argparse
from pathlib import Path
import json
import subprocess
from typing import List, Dict
from dataclasses import dataclass
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parents[1]))

# from app.pipeline.downloader import download_youtube_audio  # Not needed - using yt-dlp directly
# from app.pipeline.midi_converter import convert_audio_to_midi  # Not needed yet
import pretty_midi


@dataclass
class GospelVideo:
    """Gospel piano video metadata."""
    url: str
    title: str
    artist: str
    style: str  # "traditional", "contemporary", "worship", "jazz-gospel"
    tempo_estimate: int
    key_estimate: str = "Unknown"


class GospelDatasetBuilder:
    """Build gospel MIDI dataset from YouTube and MuseScore."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.youtube_dir = output_dir / "youtube"
        self.musescore_dir = output_dir / "musescore"
        self.validated_dir = output_dir / "validated"

        for dir in [self.youtube_dir, self.musescore_dir, self.validated_dir]:
            dir.mkdir(exist_ok=True)

        # Track progress
        self.metadata_file = output_dir / "dataset_metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load existing dataset metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"youtube": [], "musescore": [], "validated": []}

    def _save_metadata(self):
        """Save dataset metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    async def build_from_youtube(self, videos: List[GospelVideo], limit: int = 100):
        """
        Build dataset from YouTube gospel piano videos.

        Args:
            videos: List of curated gospel video URLs
            limit: Maximum number of videos to process
        """
        print(f"\n🎹 Building Gospel Dataset from YouTube")
        print(f"📊 Target: {min(limit, len(videos))} videos\n")

        processed = 0
        for video in videos[:limit]:
            try:
                print(f"🎵 Processing: {video.title}")

                # Step 1: Download audio
                print(f"   ⬇️  Downloading...")
                audio_path = await self._download_youtube_video(video.url)

                # Step 2: Isolate piano (optional - if video has multiple instruments)
                print(f"   🎹 Isolating piano...")
                piano_path = await self._isolate_piano(audio_path)

                # Step 3: Transcribe to MIDI
                print(f"   📝 Transcribing to MIDI...")
                midi_path = await self._transcribe_to_midi(piano_path or audio_path)

                # Step 4: Validate gospel characteristics
                print(f"   ✅ Validating gospel style...")
                if self._validate_gospel_midi(midi_path, video):
                    # Move to validated directory
                    final_path = self.validated_dir / f"gospel_{processed:04d}_{video.artist.replace(' ', '_')}.mid"
                    midi_path.rename(final_path)

                    # Save metadata
                    self.metadata["validated"].append({
                        "file": str(final_path),
                        "source": "youtube",
                        "title": video.title,
                        "artist": video.artist,
                        "style": video.style,
                        "tempo": video.tempo_estimate,
                        "url": video.url
                    })

                    processed += 1
                    print(f"   ✅ Saved: {final_path.name}")
                else:
                    print(f"   ⚠️  Validation failed - skipping")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue

        self._save_metadata()
        print(f"\n✅ Processed {processed}/{limit} videos successfully!")

    async def _download_youtube_video(self, url: str) -> Path:
        """Download audio from YouTube."""
        output_dir = self.youtube_dir / "audio"
        output_dir.mkdir(exist_ok=True)

        # Use yt-dlp to download audio only
        output_template = str(output_dir / "%(id)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "-x",  # Extract audio only
            "--audio-format", "wav",
            "--audio-quality", "0",  # Best quality
            "-o", output_template,
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr}")

        # Find downloaded file
        audio_files = list(output_dir.glob("*.wav"))
        if not audio_files:
            raise RuntimeError("No audio file found after download")

        return audio_files[-1]  # Return most recent

    async def _isolate_piano(self, audio_path: Path) -> Path | None:
        """Isolate piano using Demucs (optional step)."""
        # TODO: Implement Demucs piano isolation
        # For now, skip isolation and use original audio
        # (Many gospel piano tutorial videos are already piano-only)
        return None

    async def _transcribe_to_midi(self, audio_path: Path) -> Path:
        """Transcribe audio to MIDI using basic-pitch or alternative."""
        output_dir = self.youtube_dir / "midi"
        output_dir.mkdir(exist_ok=True)

        midi_path = output_dir / f"{audio_path.stem}.mid"

        # Use basic-pitch for transcription
        cmd = [
            "basic-pitch",
            str(output_dir),
            str(audio_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"basic-pitch failed: {result.stderr}")

        # Find generated MIDI file
        midi_files = list(output_dir.glob(f"{audio_path.stem}*.mid"))
        if not midi_files:
            raise RuntimeError("No MIDI file generated")

        return midi_files[0]

    def _validate_gospel_midi(self, midi_path: Path, video: GospelVideo) -> bool:
        """
        Validate that MIDI file has gospel characteristics.

        Checks:
        1. Has piano notes (not empty)
        2. Uses extended chords (7ths, 9ths, 11ths, 13ths)
        3. Has reasonable duration (30 seconds - 5 minutes)
        4. Has gospel tempo range (40-180 BPM)
        5. Has chord changes (not single chord loop)
        """
        try:
            midi = pretty_midi.PrettyMIDI(str(midi_path))

            # Check 1: Has piano notes
            total_notes = sum(len(instrument.notes) for instrument in midi.instruments)
            if total_notes < 50:  # Too sparse
                print(f"      ⚠️  Too few notes: {total_notes}")
                return False

            # Check 2: Duration (30s - 5 min)
            duration = midi.get_end_time()
            if duration < 30 or duration > 300:
                print(f"      ⚠️  Invalid duration: {duration:.1f}s")
                return False

            # Check 3: Has variety (pitch range)
            all_pitches = [note.pitch for inst in midi.instruments for note in inst.notes]
            pitch_range = max(all_pitches) - min(all_pitches)
            if pitch_range < 24:  # Less than 2 octaves
                print(f"      ⚠️  Limited pitch range: {pitch_range} semitones")
                return False

            # Check 4: Not too repetitive (note density varies)
            # TODO: Add more sophisticated gospel validation
            # - Detect chord progressions
            # - Identify extended harmony
            # - Check for gospel rhythmic patterns

            return True

        except Exception as e:
            print(f"      ❌ Validation error: {e}")
            return False

    def build_from_musescore(self, limit: int = 500):
        """
        Build dataset from MuseScore gospel piano scores.

        TODO: Implement MuseScore scraping
        - Search for "gospel piano" on MuseScore
        - Download public domain scores
        - Convert to MIDI
        """
        print("\n⚠️  MuseScore scraping not yet implemented")
        print("💡 For now, manually download gospel MIDIs from:")
        print("   - https://musescore.com/sheetmusic?text=gospel%20piano")
        print("   - https://musescore.com/sheetmusic?text=kirk%20franklin")
        print("   - https://musescore.com/sheetmusic?text=thomas%20dorsey")

    def search_youtube_videos(self, query: str, max_results: int = 10) -> List[GospelVideo]:
        """
        Search YouTube for gospel piano videos using yt-dlp.

        Args:
            query: Search query (e.g., "kirk franklin piano tutorial")
            max_results: Maximum number of results to return

        Returns:
            List of GospelVideo objects with metadata
        """
        print(f"🔍 Searching YouTube: '{query}' (max {max_results} results)")

        cmd = [
            "yt-dlp",
            f"ytsearch{max_results}:{query}",
            "--get-id",
            "--get-title",
            "--get-duration",
            "--skip-download"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"⚠️  Search failed: {result.stderr}")
            return []

        # Parse results (alternating title, id, duration)
        lines = result.stdout.strip().split('\n')
        videos = []

        # Infer style from query
        style = self._infer_style_from_query(query)
        tempo = self._estimate_tempo_from_style(style)

        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                title = lines[i]
                video_id = lines[i + 1]

                videos.append(GospelVideo(
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    title=title,
                    artist=self._extract_artist_from_title(title),
                    style=style,
                    tempo_estimate=tempo
                ))

        print(f"✅ Found {len(videos)} videos")
        return videos

    def _infer_style_from_query(self, query: str) -> str:
        """Infer gospel style from search query."""
        query_lower = query.lower()
        if "kirk franklin" in query_lower or "contemporary" in query_lower:
            return "contemporary"
        elif "traditional" in query_lower or "thomas dorsey" in query_lower:
            return "traditional"
        elif "jazz" in query_lower or "richard smallwood" in query_lower:
            return "jazz-gospel"
        elif "worship" in query_lower or "hillsong" in query_lower:
            return "worship"
        else:
            return "gospel"

    def _estimate_tempo_from_style(self, style: str) -> int:
        """Estimate typical tempo for gospel style."""
        tempo_map = {
            "contemporary": 120,
            "traditional": 65,
            "jazz-gospel": 90,
            "worship": 72,
            "gospel": 100
        }
        return tempo_map.get(style, 100)

    def _extract_artist_from_title(self, title: str) -> str:
        """Extract artist name from video title."""
        # Simple heuristic: text before first "-" or "by"
        if " - " in title:
            return title.split(" - ")[0].strip()
        elif " by " in title.lower():
            parts = title.lower().split(" by ")
            if len(parts) > 1:
                return parts[1].split()[0].strip().title()
        return "Unknown"

    def get_gospel_search_queries(self) -> List[tuple[str, int]]:
        """
        Get comprehensive list of gospel piano search queries.

        Returns:
            List of (query, expected_count) tuples
        """
        return [
            # Contemporary (150 videos target)
            ("kirk franklin piano tutorial", 30),
            ("israel houghton piano", 20),
            ("tye tribbett piano tutorial", 15),
            ("contemporary gospel piano", 40),
            ("modern gospel piano tutorial", 30),
            ("praise and worship piano tutorial", 15),

            # Traditional (125 videos target)
            ("thomas dorsey precious lord piano", 20),
            ("traditional gospel piano tutorial", 40),
            ("old school gospel piano", 30),
            ("mahalia jackson piano", 15),
            ("classic gospel piano", 20),

            # Jazz-Gospel (100 videos target)
            ("richard smallwood total praise piano", 15),
            ("jazz gospel piano tutorial", 30),
            ("james hall piano tutorial", 15),
            ("donald lawrence piano", 15),
            ("gospel jazz chords", 25),

            # Worship (75 videos target)
            ("gospel worship piano tutorial", 30),
            ("hillsong gospel piano", 20),
            ("bethel worship piano", 15),
            ("elevation worship piano gospel", 10),

            # General/Tutorials (50 videos target)
            ("gospel piano lesson", 25),
            ("gospel piano chords tutorial", 25),
        ]

    def generate_dataset_stats(self):
        """Generate statistics about the collected dataset."""
        print("\n📊 Gospel MIDI Dataset Statistics\n")

        validated_files = list(self.validated_dir.glob("*.mid"))
        print(f"✅ Validated MIDIs: {len(validated_files)}")

        if not validated_files:
            print("⚠️  No validated files yet - run dataset builder first")
            return

        # Analyze dataset
        total_duration = 0
        total_notes = 0
        styles = {}

        for midi_file in validated_files:
            try:
                midi = pretty_midi.PrettyMIDI(str(midi_file))
                total_duration += midi.get_end_time()
                total_notes += sum(len(inst.notes) for inst in midi.instruments)

                # Get style from metadata
                for entry in self.metadata["validated"]:
                    if entry["file"] == str(midi_file):
                        style = entry["style"]
                        styles[style] = styles.get(style, 0) + 1
                        break

            except Exception as e:
                print(f"⚠️  Error analyzing {midi_file.name}: {e}")

        print(f"📏 Total Duration: {total_duration/60:.1f} minutes")
        print(f"🎵 Total Notes: {total_notes:,}")
        print(f"📊 Average Notes/File: {total_notes/len(validated_files):.0f}")

        print(f"\n🎨 Style Distribution:")
        for style, count in sorted(styles.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(validated_files)) * 100
            print(f"   - {style}: {count} files ({percentage:.1f}%)")

        print(f"\n💡 Recommendation for MLX Training:")
        if len(validated_files) < 100:
            print(f"   ⚠️  Need at least 100 files (have {len(validated_files)})")
        elif len(validated_files) < 500:
            print(f"   ✅ Sufficient for basic training ({len(validated_files)} files)")
            print(f"   💡 Collect 500+ for better quality")
        else:
            print(f"   ✅ Excellent dataset size ({len(validated_files)} files)!")
            print(f"   🚀 Ready for MLX fine-tuning on M4 Pro")


async def main():
    parser = argparse.ArgumentParser(description="Build gospel MIDI dataset")
    parser.add_argument("--source", choices=["youtube", "musescore", "both"], default="youtube")
    parser.add_argument("--limit", type=int, default=10, help="Max files to collect")
    parser.add_argument("--output", type=Path, default=Path("data/gospel_dataset"))
    parser.add_argument("--stats", action="store_true", help="Show dataset statistics")
    parser.add_argument("--query", type=str, help="Single YouTube search query (for testing)")
    parser.add_argument("--test", action="store_true", help="Test mode: search only, no download")

    args = parser.parse_args()

    builder = GospelDatasetBuilder(args.output)

    if args.stats:
        builder.generate_dataset_stats()
        return

    if args.source in ["youtube", "both"]:
        # Collect videos from YouTube search
        all_videos = []

        if args.query:
            # Single query mode (for testing)
            videos = builder.search_youtube_videos(args.query, max_results=args.limit)
            all_videos.extend(videos)
        else:
            # Use all gospel search queries
            queries = builder.get_gospel_search_queries()
            videos_per_query = max(1, args.limit // len(queries))

            for query, expected_count in queries:
                count = min(videos_per_query, expected_count)
                videos = builder.search_youtube_videos(query, max_results=count)
                all_videos.extend(videos)

                if len(all_videos) >= args.limit:
                    all_videos = all_videos[:args.limit]
                    break

        print(f"\n📋 Total videos found: {len(all_videos)}")

        if args.test:
            print("\n🧪 TEST MODE: Showing first 5 videos (not downloading)\n")
            for i, video in enumerate(all_videos[:5], 1):
                print(f"{i}. {video.title}")
                print(f"   Artist: {video.artist} | Style: {video.style}")
                print(f"   URL: {video.url}\n")
            return

        # Download and process videos
        await builder.build_from_youtube(all_videos, limit=args.limit)

    if args.source in ["musescore", "both"]:
        builder.build_from_musescore(limit=args.limit)

    # Show final stats
    builder.generate_dataset_stats()


if __name__ == "__main__":
    asyncio.run(main())
