#!/usr/bin/env python3
"""
Quarterly Music Knowledge Update Script

Updates the music theory knowledge base with current trends and new sources.
Should be run every 3-4 months to keep documentation fresh.

Usage:
    export PERPLEXITY_API_KEY=pplx-xxxxx
    uv run python scripts/update_music_knowledge.py --module style_guidelines
    uv run python scripts/update_music_knowledge.py --module dataset_sources
    uv run python scripts/update_music_knowledge.py --all  # Update everything

Cost: ~$2-5 per module (~$10-15 for full update)
Duration: ~30-60 minutes per module
"""

import asyncio
import json
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import httpx


class MusicKnowledgeUpdater:
    """Updates music knowledge base documentation with current information"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "llama-3.1-sonar-large-128k-online"
        self.docs_dir = Path("backend/docs/music_theory")
        self.total_queries = 0

    async def query_perplexity(self, question: str, system_prompt: str = "") -> Dict:
        """Make a single query to Perplexity API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 4000,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

        self.total_queries += 1

        return {
            "question": question,
            "answer": result["choices"][0]["message"]["content"],
            "model": result["model"],
            "timestamp": datetime.now().isoformat(),
        }

    async def update_style_guidelines(self, specific_genre: str = None):
        """Update style guidelines with 2025 trends"""
        print("\\n=== UPDATING STYLE GUIDELINES ===")

        current_year = datetime.now().year
        system_prompt = f"""You are a professional music theorist and pianist with expertise in
        contemporary music trends. Provide updates on current ({current_year}) trends, techniques,
        and notable artists."""

        genres = [specific_genre] if specific_genre else ["gospel", "jazz", "neo_soul", "rb_contemporary"]

        for genre in genres:
            print(f"\\n  Updating {genre.upper()} guidelines...")

            queries = [
                f"What are the latest {genre} piano techniques and trends in {current_year}?",
                f"Which {genre} pianists emerged or gained prominence in {current_year-1}-{current_year}?",
                f"What chord progressions are most popular in {current_year} {genre} music?",
            ]

            results = []
            for query in queries:
                print(f"    - {query[:60]}...")
                result = await self.query_perplexity(query, system_prompt)
                results.append(result)
                await asyncio.sleep(1)

            # Save update
            update_file = self.docs_dir / "style_guidelines" / f"{genre}_update_{current_year}.json"
            update_file.parent.mkdir(parents=True, exist_ok=True)
            with open(update_file, "w") as f:
                json.dump({
                    "update_date": datetime.now().isoformat(),
                    "year": current_year,
                    "genre": genre,
                    "updates": results
                }, f, indent=2)

            print(f"  ✅ Saved to {update_file}")

    async def update_dataset_sources(self):
        """Update dataset source directory with new channels/sources"""
        print("\\n=== UPDATING DATASET SOURCES ===")

        current_year = datetime.now().year
        system_prompt = """You are a music data curator. Provide specific channel names,
        URLs, and quality assessments for recently discovered sources."""

        queries = [
            f"What new YouTube channels for gospel piano emerged in {current_year-1}-{current_year}? List channel names and why they're valuable.",
            f"What new YouTube channels for jazz piano emerged in {current_year-1}-{current_year}?",
            "What new MIDI datasets or creative commons libraries were released in the past year?",
        ]

        results = []
        for query in queries:
            print(f"  {query[:60]}...")
            result = await self.query_perplexity(query, system_prompt)
            results.append(result)
            await asyncio.sleep(1)

        # Save update
        update_file = self.docs_dir.parent / "datasets" / f"sources_update_{current_year}.json"
        update_file.parent.mkdir(parents=True, exist_ok=True)
        with open(update_file, "w") as f:
            json.dump({
                "update_date": datetime.now().isoformat(),
                "year": current_year,
                "new_sources": results
            }, f, indent=2)

        print(f"✅ Saved to {update_file}")

    async def update_validation_rules(self):
        """Update theory validation rules with current best practices"""
        print("\\n=== UPDATING VALIDATION RULES ===")

        current_year = datetime.now().year
        system_prompt = """You are a music theory professor. Provide updated perspectives
        on voice leading rules and contemporary harmonic practice."""

        queries = [
            f"What voice leading practices have evolved in modern ({current_year}) jazz and gospel piano?",
            f"What are common music theory errors in AI-generated music as of {current_year}?",
        ]

        results = []
        for query in queries:
            print(f"  {query[:60]}...")
            result = await self.query_perplexity(query, system_prompt)
            results.append(result)
            await asyncio.sleep(1)

        # Save update
        update_file = self.docs_dir / "validation_rules" / f"update_{current_year}.json"
        update_file.parent.mkdir(parents=True, exist_ok=True)
        with open(update_file, "w") as f:
            json.dump({
                "update_date": datetime.now().isoformat(),
                "year": current_year,
                "updates": results
            }, f, indent=2)

        print(f"✅ Saved to {update_file}")

    async def run_update(self, modules: List[str]):
        """Run updates for specified modules"""
        print("=" * 70)
        print("MUSIC KNOWLEDGE QUARTERLY UPDATE")
        print("=" * 70)
        print(f"Date: {datetime.now().isoformat()}")
        print(f"Modules: {', '.join(modules)}")
        print("=" * 70)

        if "style_guidelines" in modules or "all" in modules:
            await self.update_style_guidelines()

        if "dataset_sources" in modules or "all" in modules:
            await self.update_dataset_sources()

        if "validation_rules" in modules or "all" in modules:
            await self.update_validation_rules()

        print("\\n" + "=" * 70)
        print("UPDATE COMPLETE")
        print("=" * 70)
        print(f"Total queries: {self.total_queries}")
        print(f"Estimated cost: ${self.total_queries * 0.001:.2f}")
        print("\\nNEXT STEPS:")
        print("  1. Review update files in backend/docs/music_theory/")
        print("  2. Integrate new information into main documentation files")
        print("  3. Test knowledge base loader with updated docs")
        print("  4. Commit updated documentation to version control")
        print("=" * 70)


async def main():
    parser = argparse.ArgumentParser(description="Update music knowledge base documentation")
    parser.add_argument(
        "--module",
        choices=["style_guidelines", "dataset_sources", "validation_rules", "all"],
        default="all",
        help="Module to update (default: all)"
    )
    parser.add_argument(
        "--genre",
        choices=["gospel", "jazz", "neo_soul", "rb_contemporary"],
        help="Specific genre to update (only for style_guidelines module)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("ERROR: PERPLEXITY_API_KEY environment variable not set")
        print("\\nTo set:")
        print("  export PERPLEXITY_API_KEY=pplx-xxxxx")
        return

    updater = MusicKnowledgeUpdater(api_key)

    modules = [args.module] if args.module != "all" else ["style_guidelines", "dataset_sources", "validation_rules"]

    await updater.run_update(modules)


if __name__ == "__main__":
    asyncio.run(main())
