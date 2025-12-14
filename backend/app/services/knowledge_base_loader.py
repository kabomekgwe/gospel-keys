"""
Music Theory Knowledge Base Loader

Loads comprehensive music theory documentation at startup and provides
fast, in-memory access to style guidelines, validation rules, prompt templates,
dataset sources, and quality benchmarks.

Architecture: Documentation-first approach
- One-time research using Perplexity API → build comprehensive docs
- Load docs at startup → cache in memory
- Generation system references docs → 0ms latency, $0 ongoing cost

Usage:
    from app.services.knowledge_base_loader import knowledge_base

    # Get style guidelines
    guidelines = knowledge_base.get_style_guidelines("gospel", "traditional")

    # Get dataset sources
    sources = knowledge_base.get_dataset_sources("gospel", min_quality=8.0)

    # Get validation rules
    rules = knowledge_base.get_validation_rules("voicing_rules", "lydian")
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class MusicKnowledgeBase:
    """
    Singleton service for accessing music theory documentation.

    Loads all documentation modules at startup:
    - Module 1: Style Guidelines (gospel, jazz, neo-soul, classical, R&B)
    - Module 2: Dataset Sources (YouTube channels, MIDI repos)
    - Module 3: Validation Rules (voicing, voice leading, idioms)
    - Module 4: Prompt Templates (application contexts, difficulty)
    - Module 5: Quality Benchmarks (genre authentication, standards)
    """

    _instance: Optional['MusicKnowledgeBase'] = None

    def __new__(cls, docs_dir: Optional[str] = None):
        """Singleton pattern - only one instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, docs_dir: Optional[str] = None):
        """Initialize knowledge base loader"""
        if self._initialized:
            return

        self.docs_dir = Path(docs_dir) if docs_dir else Path("backend/docs/music_theory")
        self.style_guidelines: Dict[str, Any] = {}
        self.dataset_sources: Dict[str, Any] = {}
        self.validation_rules: Dict[str, Any] = {}
        self.prompt_templates: Dict[str, Any] = {}
        self.quality_benchmarks: Dict[str, Any] = {}

        self._load_all()
        self._initialized = True

        logger.info(f"Music knowledge base loaded from {self.docs_dir}")

    def _load_all(self):
        """Load all documentation modules into memory"""
        try:
            # Module 1: Style Guidelines
            self._load_style_guidelines()

            # Module 2: Dataset Sources
            self._load_dataset_sources()

            # Module 3: Validation Rules
            self._load_validation_rules()

            # Module 4: Prompt Templates
            self._load_prompt_templates()

            # Module 5: Quality Benchmarks
            self._load_quality_benchmarks()

        except Exception as e:
            logger.warning(f"Knowledge base not fully loaded: {e}")
            logger.warning("Some documentation may be missing. This is expected before research is executed.")

    def _load_json_safe(self, path: Path) -> Dict:
        """Safely load JSON file, return empty dict if not found"""
        try:
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                logger.debug(f"Documentation file not found (expected before research): {path}")
                return {}
        except Exception as e:
            logger.warning(f"Error loading {path}: {e}")
            return {}

    def _load_style_guidelines(self):
        """Load Module 1: Style Guidelines for all genres"""
        base_path = self.docs_dir / "style_guidelines"

        # Load individual genre files (will be created during Phase 2 curation)
        for genre in ["gospel", "jazz", "neo_soul", "classical", "rb_contemporary"]:
            genre_file = base_path / f"{genre}.json"
            self.style_guidelines[genre] = self._load_json_safe(genre_file)

        logger.debug(f"Loaded style guidelines for {len(self.style_guidelines)} genres")

    def _load_dataset_sources(self):
        """Load Module 2: Dataset source directory"""
        sources_file = self.docs_dir.parent / "datasets" / "sources.json"
        self.dataset_sources = self._load_json_safe(sources_file)

        youtube_count = len(self.dataset_sources.get("youtube_channels", []))
        midi_count = len(self.dataset_sources.get("midi_repositories", []))
        logger.debug(f"Loaded {youtube_count} YouTube channels, {midi_count} MIDI repositories")

    def _load_validation_rules(self):
        """Load Module 3: Theory validation rules"""
        rules_path = self.docs_dir / "validation_rules"

        # Load voicing rules
        voicing_file = rules_path / "voicing_rules.json"
        self.validation_rules["voicing_rules"] = self._load_json_safe(voicing_file)

        # Load voice leading rules
        voice_leading_file = rules_path / "voice_leading.json"
        self.validation_rules["voice_leading"] = self._load_json_safe(voice_leading_file)

        # Load idiomatic patterns
        idioms_file = rules_path / "idiomatic_patterns.json"
        self.validation_rules["idiomatic_patterns"] = self._load_json_safe(idioms_file)

        logger.debug(f"Loaded {len(self.validation_rules)} validation rule categories")

    def _load_prompt_templates(self):
        """Load Module 4: Prompt enhancement templates"""
        templates_path = self.docs_dir.parent / "prompts" / "enhancement_templates"

        # Load application context templates
        contexts_file = templates_path / "application_contexts.json"
        self.prompt_templates["application_contexts"] = self._load_json_safe(contexts_file)

        # Load difficulty calibration
        difficulty_file = templates_path / "difficulty_calibration.json"
        self.prompt_templates["difficulty"] = self._load_json_safe(difficulty_file)

        # Load tempo/mood templates
        tempo_file = templates_path / "tempo_mood.json"
        self.prompt_templates["tempo_mood"] = self._load_json_safe(tempo_file)

        logger.debug(f"Loaded {len(self.prompt_templates)} prompt template categories")

    def _load_quality_benchmarks(self):
        """Load Module 5: Quality benchmarks and metrics"""
        benchmarks_file = self.docs_dir.parent / "quality" / "benchmarks.json"
        self.quality_benchmarks = self._load_json_safe(benchmarks_file)

        genre_count = len([k for k in self.quality_benchmarks.keys() if k.endswith("_authenticity")])
        logger.debug(f"Loaded quality benchmarks for {genre_count} genres")

    # ==================== PUBLIC API METHODS ====================

    def get_style_guidelines(
        self,
        style: str,
        sub_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get style guidelines from documentation

        Args:
            style: Genre (gospel, jazz, neo_soul, classical, rb_contemporary)
            sub_style: Optional sub-style (traditional, contemporary, bebop, etc.)

        Returns:
            Dictionary with style guidelines including:
            - common_progressions: List of typical chord progressions
            - signature_voicings: Characteristic voicings
            - harmonic_devices: Style-specific techniques
            - rhythm_patterns: Typical rhythm approaches

        Example:
            >>> kb = MusicKnowledgeBase()
            >>> gospel = kb.get_style_guidelines("gospel", "traditional")
            >>> print(gospel["common_progressions"])
        """
        guidelines = self.style_guidelines.get(style, {})

        if sub_style and isinstance(guidelines, dict):
            return guidelines.get(sub_style, guidelines)

        return guidelines

    def get_dataset_sources(
        self,
        genre: Optional[str] = None,
        source_type: str = "youtube_channels",
        min_quality: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Get curated dataset sources for a genre

        Args:
            genre: Filter by genre (gospel, jazz, classical, etc.)
            source_type: Type of source (youtube_channels, midi_repositories, transcription_services)
            min_quality: Minimum quality rating (0.0-10.0)

        Returns:
            List of source dictionaries with metadata:
            - name: Source name/channel
            - genre: Genre specialty
            - quality_rating: Quality score (0-10)
            - content_type: Type of content
            - authority_reason: Why this source is authoritative

        Example:
            >>> kb = MusicKnowledgeBase()
            >>> sources = kb.get_dataset_sources("gospel", min_quality=8.0)
            >>> for s in sources:
            ...     print(f"{s['name']}: {s['quality_rating']}/10")
        """
        sources = self.dataset_sources.get(source_type, [])

        # Filter by genre if specified
        if genre:
            sources = [s for s in sources if s.get("genre") == genre]

        # Filter by minimum quality
        sources = [s for s in sources if s.get("quality_rating", 0) >= min_quality]

        return sources

    def get_validation_rules(
        self,
        rule_type: str,
        specific_rule: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get theory validation rules

        Args:
            rule_type: Type of rules (voicing_rules, voice_leading, idiomatic_patterns)
            specific_rule: Optional specific rule (lydian, drop2, etc.)

        Returns:
            Dictionary with validation criteria:
            - required_notes: Notes that must be present
            - optional_notes: Notes that can be included
            - forbidden_patterns: Patterns to avoid
            - common_mistakes: Typical errors

        Example:
            >>> kb = MusicKnowledgeBase()
            >>> lydian = kb.get_validation_rules("voicing_rules", "lydian")
            >>> print(lydian["required_notes"])
        """
        rules = self.validation_rules.get(rule_type, {})

        if specific_rule and isinstance(rules, dict):
            return rules.get(specific_rule, {})

        return rules

    def get_prompt_template(
        self,
        template_type: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get prompt enhancement template

        Args:
            template_type: Template category (application_contexts, difficulty, tempo_mood)
            context: Specific context (gospel_concert, jazz_practice, etc.)

        Returns:
            Dictionary with prompt enhancements:
            - prompt_enhancements: List of guidance strings
            - harmonic_guidance: Specific harmonic suggestions
            - rhythm_guidance: Rhythm/feel suggestions

        Example:
            >>> kb = MusicKnowledgeBase()
            >>> template = kb.get_prompt_template("application_contexts", "gospel_concert")
            >>> for enhancement in template["prompt_enhancements"]:
            ...     print(f"- {enhancement}")
        """
        templates = self.prompt_templates.get(template_type, {})

        if context and isinstance(templates, dict):
            return templates.get(context, {})

        return templates

    def get_quality_benchmarks(
        self,
        genre: str,
        benchmark_type: str = "authenticity"
    ) -> Dict[str, Any]:
        """
        Get quality benchmarks for genre

        Args:
            genre: Genre to get benchmarks for
            benchmark_type: Type of benchmark (authenticity, transcription, performance)

        Returns:
            Dictionary with quality criteria:
            - required_characteristics: Must-have features
            - disqualifying_patterns: Red flags
            - quality_thresholds: Numeric thresholds

        Example:
            >>> kb = MusicKnowledgeBase()
            >>> gospel_auth = kb.get_quality_benchmarks("gospel", "authenticity")
            >>> print(gospel_auth["required_characteristics"])
        """
        key = f"{genre}_{benchmark_type}"
        return self.quality_benchmarks.get(key, {})

    def format_style_guidelines_for_prompt(
        self,
        style: str,
        sub_style: Optional[str] = None
    ) -> str:
        """
        Format style guidelines as text for AI prompt inclusion

        Args:
            style: Genre (gospel, jazz, etc.)
            sub_style: Optional sub-style

        Returns:
            Formatted string ready for prompt insertion

        Example:
            >>> kb = MusicKnowledgeBase()
            >>> prompt_text = kb.format_style_guidelines_for_prompt("gospel", "traditional")
            >>> print(prompt_text)
        """
        doc = self.get_style_guidelines(style, sub_style)

        if not doc:
            return f"Style: {style.title()}\n(Documentation pending - use general knowledge)"

        sections = []
        sections.append(f"STYLE: {style.title()}" + (f" - {sub_style.title()}" if sub_style else ""))

        # Common progressions
        if "common_progressions" in doc:
            sections.append("\nCOMMON PROGRESSIONS:")
            for prog in doc["common_progressions"][:5]:  # Top 5
                pattern = prog.get("pattern", "")
                usage = prog.get("usage", "")
                sections.append(f"  - {pattern}: {usage}")

        # Signature voicings
        if "signature_voicings" in doc:
            sections.append("\nSIGNATURE VOICINGS:")
            for voicing in doc["signature_voicings"][:3]:  # Top 3
                name = voicing.get("name", "")
                context = voicing.get("context", "")
                sections.append(f"  - {name}: {context}")

        # Harmonic devices
        if "harmonic_devices" in doc:
            devices = ", ".join(doc["harmonic_devices"][:5])
            sections.append(f"\nHARMONIC DEVICES: {devices}")

        # Rhythm patterns
        if "rhythm_patterns" in doc:
            patterns = ", ".join(doc["rhythm_patterns"][:3])
            sections.append(f"\nRHYTHM PATTERNS: {patterns}")

        return "\n".join(sections)

    def is_loaded(self) -> bool:
        """Check if knowledge base has any documentation loaded"""
        return bool(
            self.style_guidelines or
            self.dataset_sources or
            self.validation_rules or
            self.prompt_templates or
            self.quality_benchmarks
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded documentation"""
        return {
            "style_guidelines_loaded": len(self.style_guidelines),
            "dataset_sources": {
                "youtube_channels": len(self.dataset_sources.get("youtube_channels", [])),
                "midi_repositories": len(self.dataset_sources.get("midi_repositories", [])),
                "transcription_services": len(self.dataset_sources.get("transcription_services", []))
            },
            "validation_rules_categories": len(self.validation_rules),
            "prompt_template_categories": len(self.prompt_templates),
            "quality_benchmarks": len(self.quality_benchmarks),
            "is_fully_loaded": self.is_loaded()
        }


# Global singleton instance
# Initialize once at startup in app/main.py
knowledge_base = MusicKnowledgeBase()
