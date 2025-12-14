#!/usr/bin/env python3
"""
One-Time Music Knowledge Research Script

Uses Perplexity API to research and build comprehensive music theory documentation.
This script should be run ONCE to build the initial knowledge base, then periodically
(quarterly) to refresh with current trends.

Cost: ~$5-10 for initial research (~150 queries)
Duration: ~2-3 hours

Usage:
    export PERPLEXITY_API_KEY=pplx-xxxxx
    uv run python scripts/research_music_knowledge.py
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List
import httpx
from datetime import datetime


class MusicKnowledgeResearcher:
    """Research music theory knowledge using Perplexity API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "llama-3.1-sonar-large-128k-online"  # Best model for research
        self.output_dir = Path("backend/docs/music_theory")
        self.total_queries = 0
        self.total_cost_estimate = 0.0

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
            "temperature": 0.2,  # Lower for more factual, consistent responses
            "max_tokens": 4000,  # Comprehensive responses
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
        # Estimate cost: ~$0.001 per request with Sonar Large
        self.total_cost_estimate += 0.001

        return {
            "question": question,
            "answer": result["choices"][0]["message"]["content"],
            "model": result["model"],
            "timestamp": datetime.now().isoformat(),
            "usage": result.get("usage", {})
        }

    async def research_style_guidelines(self):
        """Module 1: Research style guidelines for all genres"""
        print("\n=== MODULE 1: STYLE GUIDELINES ENCYCLOPEDIA ===")

        system_prompt = """You are a professional music theorist and pianist with expertise in
        gospel, jazz, classical, blues, neo-soul, and R&B piano. Provide detailed, technical
        answers with specific chord symbols, progressions, and voicing techniques."""

        # Gospel Piano Queries
        gospel_queries = [
            "What are the 10 most common chord progressions in traditional gospel piano (Thomas Dorsey era, 1930s-1960s)? List them in Roman numeral notation with typical usage context.",
            "What are Kirk Franklin's signature chord progressions and harmonic techniques used in his contemporary gospel style (1990s-2025)?",
            "What are the characteristic voicings used in gospel piano? Describe specific voicing types (open, closed, rootless, etc.) with note examples.",
            "What harmonic devices define the gospel piano sound? (secondary dominants, passing chords, chromatic movement, etc.)",
            "What rhythm patterns and articulation styles are typical in traditional vs contemporary gospel piano?",
            "What defines beginner, intermediate, and advanced gospel piano technique? List specific skills for each level.",
            "What are the differences between traditional gospel, contemporary gospel, and modern worship/praise music in terms of harmony and rhythm?",
        ]

        # Jazz Piano Queries
        jazz_queries = [
            "What are the defining characteristics of bebop piano style? Include typical chord progressions, voicings, and lick patterns.",
            "What are chromatic approach patterns used in bebop and modern jazz piano? Provide specific examples of half-step approaches (above/below target notes).",
            "What are the most common jazz piano voicings? (rootless, drop-2, drop-3, shell voicings) Provide note examples for C7, Dm7, and Cmaj7.",
            "What are standard jazz blues progressions and turnarounds? List 5-10 common variations.",
            "What are common reharmonization techniques in modern jazz piano? (tritone substitution, modal interchange, etc.)",
            "What voice leading principles are essential for jazz piano? Include rules for parallel motion and chromatic voice leading.",
        ]

        # Neo-Soul Queries
        neo_soul_queries = [
            "What chord progressions and harmonic devices are characteristic of neo-soul piano (D'Angelo, Erykah Badu, Robert Glasper)?",
            "What rhythm feels and articulation styles define neo-soul piano? How does it differ from traditional R&B?",
            "What extended harmony (9ths, 11ths, 13ths) is commonly used in neo-soul? Provide specific voicing examples.",
        ]

        # Classical Queries
        classical_queries = [
            "What are the fundamental voice leading rules in classical piano harmony? (parallel 5ths/octaves, contrary motion, etc.)",
            "What are standard cadential formulas in classical piano? (authentic, plagal, half, deceptive cadences)",
            "What are prohibited parallels in classical harmony, and when do these rules apply vs when can they be broken?",
        ]

        # R&B/Contemporary Queries
        rb_queries = [
            "What chord progressions are most popular in contemporary R&B piano (2020-2025)?",
            "What harmonic trends define modern R&B piano production? How has it evolved from 1990s R&B?",
        ]

        # Execute all queries
        all_queries = {
            "gospel": gospel_queries,
            "jazz": jazz_queries,
            "neo_soul": neo_soul_queries,
            "classical": classical_queries,
            "rb_contemporary": rb_queries,
        }

        results = {}
        for category, queries in all_queries.items():
            print(f"\n  Researching {category.upper()}... ({len(queries)} queries)")
            results[category] = []
            for i, query in enumerate(queries, 1):
                print(f"    [{i}/{len(queries)}] {query[:80]}...")
                result = await self.query_perplexity(query, system_prompt)
                results[category].append(result)
                await asyncio.sleep(1)  # Rate limiting

        # Save raw results
        output_file = self.output_dir / "style_guidelines" / "research_raw.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n  ✅ Saved to {output_file}")
        return results

    async def research_dataset_sources(self):
        """Module 2: Research dataset sources (YouTube, MIDI repos, transcription services)"""
        print("\n=== MODULE 2: DATASET SOURCE DIRECTORY ===")

        system_prompt = """You are a music data curator with expertise in finding high-quality
        piano performance recordings and MIDI datasets. Provide specific channel names, URLs,
        and quality assessments."""

        queries = [
            "What are the top 20 YouTube channels for high-quality gospel piano performances and tutorials? List channel names and why they are authoritative (pianist credentials, audio quality, consistency).",
            "What are the top 15 YouTube channels for high-quality jazz piano performances? Include bebop, modern jazz, and blues specialists.",
            "What are the top 10 YouTube channels for classical piano performances with excellent audio quality?",
            "What are reputable public domain MIDI file repositories for piano music? List URLs and what genres they specialize in.",
            "What are creative commons or open-source music libraries that include piano MIDI files for machine learning training?",
            "What academic or research MIDI datasets exist for piano music? (e.g., MAESTRO, MAPS, Lakh MIDI)",
            "What professional piano transcription services are known for high accuracy? List companies and their reputation in the music industry.",
            "What community-driven piano transcription projects exist? (MuseScore community, IMSLP, etc.)",
        ]

        results = []
        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] {query[:80]}...")
            result = await self.query_perplexity(query, system_prompt)
            results.append(result)
            await asyncio.sleep(1)

        # Save raw results
        output_file = self.output_dir / "datasets" / "sources_research_raw.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"  ✅ Saved to {output_file}")
        return results

    async def research_validation_rules(self):
        """Module 3: Research music theory validation rules"""
        print("\n=== MODULE 3: THEORY VALIDATION RULES ===")

        system_prompt = """You are a music theory professor specializing in piano harmony and
        voice leading. Provide precise, technical answers about correct vs incorrect voicings,
        voice leading, and idiomatic patterns."""

        queries = [
            # Voicing Correctness
            "What defines a correct lydian mode voicing on piano? What notes are essential vs optional? Provide examples for C lydian.",
            "What are the characteristic notes for each of the 7 modal scales in piano voicings? (Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian)",
            "What are the rules for rootless jazz piano voicings? What notes can be omitted and which must be present?",
            "What are drop-2 and drop-3 voicings in jazz piano? Provide specific note constructions for Cmaj7, Dm7, and G7.",
            "What makes a gospel piano voicing sound authentic vs generic? What intervallic structures are characteristic?",

            # Voice Leading
            "When do parallel 5ths and octaves matter in voice leading, and when can they be ignored? Provide specific contexts for each.",
            "What are the principles of smooth voice leading in jazz and gospel piano? What constitutes good vs bad voice leading?",
            "In bebop piano, should chromatic approach tones be a half-step above or below the target note? Are there rules or is it context-dependent?",
            "What are common voice leading mistakes pianists make when moving from Dm7 to G7 to Cmaj7? How should this progression be voiced?",

            # Idiomatic Patterns
            "What harmonic patterns are acceptable in gospel piano that would be incorrect in classical harmony?",
            "What distinguishes historically authentic baroque/classical voice leading from modern piano harmony?",
            "What are common music theory errors that AI models make when generating piano music? What rules are most frequently violated?",
        ]

        results = []
        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] {query[:80]}...")
            result = await self.query_perplexity(query, system_prompt)
            results.append(result)
            await asyncio.sleep(1)

        # Save raw results
        output_file = self.output_dir / "validation_rules" / "research_raw.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"  ✅ Saved to {output_file}")
        return results

    async def research_prompt_templates(self):
        """Module 4: Research context-aware prompt enhancement templates"""
        print("\n=== MODULE 4: PROMPT ENHANCEMENT TEMPLATES ===")

        system_prompt = """You are a professional pianist and music educator who understands
        the differences between performance contexts, difficulty levels, and musical applications."""

        queries = [
            # Application Contexts
            "What are the key differences between concert gospel piano performance vs church accompaniment? (arrangement style, voicing complexity, improvisation, rhythm)",
            "How does a practice arrangement differ from a performance arrangement for gospel/jazz piano? What should be simplified or emphasized?",
            "What are the differences between recording studio piano arrangement vs live performance arrangement?",
            "How do uptempo vs ballad gospel arrangements differ in harmonic approach, rhythm, and voicing?",

            # Difficulty Calibration
            "What defines beginner, intermediate, and advanced piano technique for gospel music? List specific skills and progression complexity for each level.",
            "What defines beginner, intermediate, and advanced piano technique for jazz improvisation? What makes a jazz lick or voicing advanced vs intermediate?",
            "What chord progression complexity indicates beginner vs intermediate vs advanced piano difficulty across genres?",
            "What technical skills (hand independence, voicing spread, rhythm complexity) distinguish difficulty levels in piano music?",

            # Tempo/Mood Relationships
            "What are typical tempo ranges (BPM) for gospel ballads, mid-tempo, and uptempo arrangements?",
            "What harmonic devices are appropriate for reflective/ballad gospel vs energetic/uptempo gospel?",
            "How do contemporary vs traditional gospel styles differ in tempo, rhythm, and harmonic approach?",
            "What mood-specific voicing choices are common in jazz piano? (bright vs dark, tense vs relaxed harmonies)",
        ]

        results = []
        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] {query[:80]}...")
            result = await self.query_perplexity(query, system_prompt)
            results.append(result)
            await asyncio.sleep(1)

        # Save raw results
        output_file = self.output_dir / "prompts" / "enhancement_templates_research_raw.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"  ✅ Saved to {output_file}")
        return results

    async def research_quality_benchmarks(self):
        """Module 5: Research professional quality benchmarks"""
        print("\n=== MODULE 5: QUALITY BENCHMARKS & METRICS ===")

        system_prompt = """You are a professional music producer and MIDI programming expert
        who understands what makes piano music sound authentic vs synthetic/programmed."""

        queries = [
            # Genre Authentication
            "What harmonic characteristics distinguish authentic gospel piano from generic jazz or pop piano?",
            "What specific harmonic markers indicate authentic jazz piano vs jazz-influenced pop?",
            "What rhythm and timing characteristics distinguish authentic blues piano from blues-influenced styles?",
            "What makes a MIDI piano performance sound realistic vs obviously programmed? List specific humanization factors.",

            # Transcription Quality
            "What quality standards do professional piano transcription services use? What metrics indicate high vs low accuracy?",
            "What are common errors in automated piano transcription (basic-pitch, Omnizart, etc.)? What should be filtered out?",
            "What note density (notes per second) is typical for different piano genres? (classical, jazz, gospel, contemporary)",
            "What pitch range is typical for different piano performance contexts? (solo, accompaniment, ensemble)",

            # Performance Realism
            "What timing humanization parameters make MIDI piano sound realistic? (timing deviation, groove, swing)",
            "What velocity variation patterns create realistic piano dynamics? What ranges are typical for different styles?",
            "What voicing spread (hand span, octave ranges) is realistic for human piano performance vs programmed?",
            "What articulation patterns (staccato, legato, pedaling) are characteristic of different piano genres?",
        ]

        results = []
        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] {query[:80]}...")
            result = await self.query_perplexity(query, system_prompt)
            results.append(result)
            await asyncio.sleep(1)

        # Save raw results
        output_file = self.output_dir / "quality" / "benchmarks_research_raw.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"  ✅ Saved to {output_file}")
        return results

    async def research_all_modules(self):
        """Execute all research modules"""
        print("\n" + "=" * 70)
        print("MUSIC KNOWLEDGE RESEARCH - PERPLEXITY API")
        print("=" * 70)
        print(f"Model: {self.model}")
        print(f"Output directory: {self.output_dir}")
        print("=" * 70)

        results = {}

        # Module 1: Style Guidelines (30+ queries)
        results["style_guidelines"] = await self.research_style_guidelines()

        # Module 2: Dataset Sources (8 queries)
        results["dataset_sources"] = await self.research_dataset_sources()

        # Module 3: Validation Rules (12 queries)
        results["validation_rules"] = await self.research_validation_rules()

        # Module 4: Prompt Templates (13 queries)
        results["prompt_templates"] = await self.research_prompt_templates()

        # Module 5: Quality Benchmarks (12 queries)
        results["quality_benchmarks"] = await self.research_quality_benchmarks()

        # Summary
        print("\n" + "=" * 70)
        print("RESEARCH COMPLETE")
        print("=" * 70)
        print(f"Total queries: {self.total_queries}")
        print(f"Estimated cost: ${self.total_cost_estimate:.2f}")
        print(f"\nAll raw research saved to: {self.output_dir}")
        print("\nNEXT STEPS:")
        print("  1. Review raw research files in backend/docs/music_theory/")
        print("  2. Curate and structure into clean JSON/Markdown (1-2 days manual work)")
        print("  3. Build knowledge_base_loader.py to load structured docs")
        print("  4. Integrate into gospel_generator, ai_generator, dataset_builder")
        print("=" * 70)

        return results


async def main():
    """Main entry point"""
    # Get API key from environment
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("ERROR: PERPLEXITY_API_KEY environment variable not set")
        print("\nTo set:")
        print("  export PERPLEXITY_API_KEY=pplx-xxxxx")
        print("\nGet API key from: https://www.perplexity.ai/settings/api")
        return

    researcher = MusicKnowledgeResearcher(api_key)
    await researcher.research_all_modules()


if __name__ == "__main__":
    asyncio.run(main())
