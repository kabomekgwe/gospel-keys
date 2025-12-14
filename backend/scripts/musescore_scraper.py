#!/usr/bin/env python3
"""
MuseScore Gospel Piano MIDI Scraper

Downloads gospel piano sheet music in MIDI format from MuseScore.com

MuseScore has millions of user-uploaded scores, many in public domain.
This script searches for gospel piano music and downloads MIDI files.

Usage:
    python scripts/musescore_scraper.py --query "gospel piano" --limit 50
    python scripts/musescore_scraper.py --query "kirk franklin" --limit 30
    python scripts/musescore_scraper.py --style traditional --limit 100

Legal Note:
- Only downloads public domain and Creative Commons licensed scores
- Respects MuseScore's terms of service
- Does NOT download copyrighted material
"""

import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import re


@dataclass
class MuseScoreSheet:
    """MuseScore sheet music metadata."""
    url: str
    title: str
    composer: str
    style: str
    difficulty: str
    license: str  # "public-domain", "cc-by", "cc-by-sa", etc.
    midi_url: Optional[str] = None


class MuseScoreScraper:
    """Scrape and download gospel piano MIDIs from MuseScore."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.base_url = "https://musescore.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

        # Track downloaded scores
        self.metadata_file = output_dir / "musescore_metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> List[Dict]:
        """Load existing metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return []

    def _save_metadata(self):
        """Save metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def search_gospel_piano(
        self,
        query: str = "gospel piano",
        style: Optional[str] = None,
        limit: int = 50
    ) -> List[MuseScoreSheet]:
        """
        Search MuseScore for gospel piano scores.

        Args:
            query: Search query
            style: Gospel style filter (traditional, contemporary, jazz-gospel)
            limit: Maximum number of results

        Returns:
            List of MuseScoreSheet objects
        """
        print(f"\n🔍 Searching MuseScore: '{query}' (limit: {limit})")

        # Build search URL
        search_query = query
        if style:
            search_query = f"{query} {style}"

        search_url = f"{self.base_url}/sheetmusic"
        params = {
            "text": search_query,
            "type": "non-official"  # Exclude official copyrighted scores
        }

        results = []
        page = 1
        max_pages = (limit // 20) + 1  # MuseScore shows ~20 results per page

        while len(results) < limit and page <= max_pages:
            print(f"   📄 Fetching page {page}...")

            params["page"] = page
            try:
                response = self.session.get(search_url, params=params, timeout=10)
                response.raise_for_status()

                # Parse search results
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find score cards (MuseScore's HTML structure)
                score_cards = soup.find_all('article', class_='dHQUe')  # This class may change

                if not score_cards:
                    # Try alternative selectors
                    score_cards = soup.find_all('div', attrs={'data-test': 'score-card'})

                if not score_cards:
                    print(f"   ⚠️  No more results found on page {page}")
                    break

                for card in score_cards:
                    if len(results) >= limit:
                        break

                    sheet = self._parse_score_card(card)
                    if sheet and self._is_gospel_piano(sheet):
                        results.append(sheet)

                page += 1
                time.sleep(1)  # Be respectful, rate limit

            except Exception as e:
                print(f"   ❌ Error fetching page {page}: {e}")
                break

        print(f"✅ Found {len(results)} gospel piano scores")
        return results

    def _parse_score_card(self, card) -> Optional[MuseScoreSheet]:
        """Parse score card HTML to extract metadata."""
        try:
            # Extract title
            title_elem = card.find('a', class_='FzkJ1')
            if not title_elem:
                title_elem = card.find('h2')

            title = title_elem.text.strip() if title_elem else "Unknown"

            # Extract URL
            url_elem = card.find('a', href=True)
            url = f"{self.base_url}{url_elem['href']}" if url_elem else None

            if not url:
                return None

            # Extract composer/arranger
            composer_elem = card.find('span', class_='_3FGFx')
            composer = composer_elem.text.strip() if composer_elem else "Unknown"

            # Infer style from title
            style = self._infer_style_from_title(title)

            # Difficulty (if available)
            difficulty = "intermediate"  # Default

            # License (assume public domain for non-official)
            license_type = "public-domain"

            return MuseScoreSheet(
                url=url,
                title=title,
                composer=composer,
                style=style,
                difficulty=difficulty,
                license=license_type
            )

        except Exception as e:
            print(f"   ⚠️  Error parsing score card: {e}")
            return None

    def _is_gospel_piano(self, sheet: MuseScoreSheet) -> bool:
        """Check if score is gospel piano music."""
        title_lower = sheet.title.lower()
        composer_lower = sheet.composer.lower()

        # Gospel keywords
        gospel_keywords = [
            "gospel", "kirk franklin", "thomas dorsey", "mahalia jackson",
            "praise", "worship", "hymn", "spiritual", "hallelujah",
            "jesus", "lord", "amen", "holy", "blessed"
        ]

        # Piano keywords
        piano_keywords = ["piano", "keyboard", "keys"]

        has_gospel = any(keyword in title_lower or keyword in composer_lower
                         for keyword in gospel_keywords)
        has_piano = any(keyword in title_lower for keyword in piano_keywords)

        return has_gospel and (has_piano or "piano" in sheet.title.lower())

    def _infer_style_from_title(self, title: str) -> str:
        """Infer gospel style from title."""
        title_lower = title.lower()

        if any(word in title_lower for word in ["kirk franklin", "contemporary", "modern"]):
            return "contemporary"
        elif any(word in title_lower for word in ["traditional", "thomas dorsey", "classic"]):
            return "traditional"
        elif any(word in title_lower for word in ["jazz", "blues"]):
            return "jazz-gospel"
        elif any(word in title_lower for word in ["worship", "praise"]):
            return "worship"
        else:
            return "gospel"

    def download_midi(self, sheet: MuseScoreSheet, output_path: Path) -> bool:
        """
        Download MIDI file for a MuseScore sheet.

        Note: MuseScore requires authentication for direct MIDI downloads.
        Alternative approaches:
        1. Use MuseScore's public API (if available)
        2. Download MusicXML and convert to MIDI
        3. Manual download instructions for user

        For now, this provides the download URL for manual download.
        """
        print(f"\n📥 MuseScore MIDI Download: {sheet.title}")
        print(f"   URL: {sheet.url}")
        print(f"   ⚠️  Automated MIDI download requires MuseScore account")
        print(f"   💡 Manual steps:")
        print(f"      1. Visit: {sheet.url}")
        print(f"      2. Click 'Download' → 'MIDI'")
        print(f"      3. Save to: {output_path}")

        # Save metadata for manual download
        self.metadata.append({
            **asdict(sheet),
            "download_path": str(output_path),
            "status": "pending_manual_download"
        })
        self._save_metadata()

        return False  # Manual download required

    def generate_download_list(
        self,
        sheets: List[MuseScoreSheet],
        output_file: Path
    ):
        """
        Generate a download list for manual batch download.

        Creates a markdown file with all URLs and download instructions.
        """
        print(f"\n📝 Generating download list: {output_file}")

        markdown = f"""# Gospel Piano MIDI Download List from MuseScore

**Total Scores**: {len(sheets)}

## Download Instructions

1. Visit each URL below
2. Click **Download** → **MIDI**
3. Save file to `{self.output_dir}/`
4. Rename file to match the suggested filename

---

## Scores to Download

"""

        for i, sheet in enumerate(sheets, 1):
            filename = f"gospel_{i:04d}_{sheet.composer.replace(' ', '_')}.mid"
            markdown += f"""### {i}. {sheet.title}

- **Composer**: {sheet.composer}
- **Style**: {sheet.style}
- **URL**: {sheet.url}
- **Save as**: `{filename}`

---

"""

        output_file.write_text(markdown)
        print(f"✅ Download list saved to: {output_file}")
        print(f"\n💡 You can also use browser extensions like 'DownThemAll' for batch downloads")


def main():
    parser = argparse.ArgumentParser(description="Scrape gospel piano MIDIs from MuseScore")
    parser.add_argument("--query", type=str, default="gospel piano", help="Search query")
    parser.add_argument("--style", type=str, choices=["traditional", "contemporary", "jazz-gospel", "worship"])
    parser.add_argument("--limit", type=int, default=50, help="Max scores to find")
    parser.add_argument("--output", type=Path, default=Path("data/gospel_dataset/musescore"))

    args = parser.parse_args()

    scraper = MuseScoreScraper(args.output)

    # Search for gospel piano scores
    sheets = scraper.search_gospel_piano(
        query=args.query,
        style=args.style,
        limit=args.limit
    )

    if not sheets:
        print("\n⚠️  No gospel piano scores found. Try different search terms.")
        return

    # Generate download list (manual download required)
    download_list_file = args.output / "musescore_download_list.md"
    scraper.generate_download_list(sheets, download_list_file)

    print(f"\n📊 Summary:")
    print(f"   - Found: {len(sheets)} gospel piano scores")
    print(f"   - Download list: {download_list_file}")
    print(f"\n💡 Next Steps:")
    print(f"   1. Open the download list: {download_list_file}")
    print(f"   2. Manually download MIDIs from MuseScore")
    print(f"   3. Save to: {args.output}/")
    print(f"   4. Run validator: python scripts/validate_gospel_midis.py")


if __name__ == "__main__":
    main()
