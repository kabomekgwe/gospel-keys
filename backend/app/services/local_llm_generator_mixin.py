"""Local LLM Generator Mixin

Adds local LLM integration to any generator, replacing Gemini API calls
with zero-cost local inference using MLX framework.

Features:
- Automatic routing by complexity (simple → Phi-3.5, medium → Llama 3.3 70B)
- Graceful fallback to Gemini for complex tasks
- Cost tracking and savings reporting
- GPT-4 quality output from Llama 3.3 70B
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Import multi-model service
try:
    from app.services.multi_model_service import multi_model_service, MLX_AVAILABLE
    LOCAL_LLM_ENABLED = MLX_AVAILABLE and multi_model_service.is_available()
except ImportError:
    multi_model_service = None
    LOCAL_LLM_ENABLED = False
    logger.warning("⚠️ Local LLM not available, will use Gemini fallback")


class LocalLLMGeneratorMixin:
    """
    Mixin to add local LLM capabilities to any generator.

    Replaces Gemini API calls with local inference using MLX framework.

    Usage:
        class MyGenerator(LocalLLMGeneratorMixin, BaseGenreGenerator):
            pass

        # Now has:
        response = generator.generate_with_local_llm(...)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._local_llm_enabled = LOCAL_LLM_ENABLED
        self._generation_stats = {
            "local_count": 0,
            "gemini_count": 0,
            "local_cost_saved": 0.0  # Estimated savings in USD
        }

    def _estimate_complexity(self, description: str, num_bars: int) -> int:
        """
        Estimate task complexity for routing (1-10 scale).

        Complexity factors:
        - Description length and keywords
        - Number of bars (more bars = more complex)
        - Request features (include_progression, etc.)

        Returns:
            1-4: Simple (Phi-3.5 Mini) - basic progressions, short descriptions
            5-7: Medium (Llama 3.3 70B) - detailed descriptions, longer pieces
            8-10: Complex (Gemini) - very creative, experimental requests
        """
        complexity = 3  # Base complexity

        # Description analysis
        desc_lower = description.lower()

        # Simple indicators (-1 complexity)
        simple_keywords = ["simple", "basic", "easy", "standard"]
        if any(kw in desc_lower for kw in simple_keywords):
            complexity -= 1

        # Complex indicators (+2 complexity)
        complex_keywords = [
            "experimental", "avant-garde", "unusual", "innovative",
            "unique", "creative", "original", "fusion"
        ]
        if any(kw in desc_lower for kw in complex_keywords):
            complexity += 2

        # Medium complexity indicators (+1)
        medium_keywords = [
            "sophisticated", "advanced", "professional",
            "detailed", "rich", "elaborate"
        ]
        if any(kw in desc_lower for kw in medium_keywords):
            complexity += 1

        # Bars factor
        if num_bars > 16:
            complexity += 1
        if num_bars > 32:
            complexity += 1

        # Description length factor
        if len(description) > 100:
            complexity += 1

        # Clamp to 1-10
        return max(1, min(10, complexity))

    async def _generate_progression_with_local_llm(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int],
        num_bars: int
    ) -> tuple:
        """
        Generate chord progression using local LLM.

        Automatically routes to best model based on complexity.
        Falls back to Gemini for complex tasks (complexity 8-10).

        Returns:
            (chords, key, tempo, analysis) tuple
        """
        # Estimate complexity
        complexity = self._estimate_complexity(description, num_bars)

        # Build prompt
        prompt = self._build_progression_prompt(description, key, tempo, num_bars)

        # Try local LLM first (if complexity <= 7)
        if self._local_llm_enabled and complexity <= 7:
            try:
                logger.info(f"🤖 Using local LLM (complexity {complexity}) for progression generation")

                response = multi_model_service.generate(
                    prompt=prompt,
                    complexity=complexity,
                    max_tokens=1024,
                    temperature=0.7
                )

                # Parse response
                result = self._parse_llm_response(response, key, tempo)

                # Track stats
                self._generation_stats["local_count"] += 1
                self._generation_stats["local_cost_saved"] += 0.001  # ~$0.001 saved per generation

                logger.info(f"✅ Local LLM generation successful (total saved: ${self._generation_stats['local_cost_saved']:.3f})")
                return result

            except Exception as e:
                logger.warning(f"⚠️ Local LLM failed: {e}, falling back to Gemini")
                # Fall through to Gemini

        # Use Gemini (for complex tasks or if local LLM unavailable)
        if self.gemini_model:
            logger.info(f"☁️ Using Gemini (complexity {complexity})")
            self._generation_stats["gemini_count"] += 1

            # Use existing Gemini implementation
            return await self._generate_progression_with_gemini(
                description, key, tempo, num_bars
            )
        else:
            # No AI available, use fallback
            logger.warning("⚠️ No AI available, using rule-based fallback")
            chords, key_result, tempo_result = self._parse_description_with_fallback(
                description, key, tempo
            )
            return (chords, key_result, tempo_result, [])

    def _build_progression_prompt(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int],
        num_bars: int
    ) -> str:
        """Build prompt for progression generation."""
        # Get genre-specific style context
        style_context = self._get_style_context()

        prompt = f"""You are a {self.genre_name} music expert. Generate a chord progression.

{style_context}

User Request: {description}
Number of bars: {num_bars}
"""

        if key:
            prompt += f"Key: {key}\n"
        if tempo:
            prompt += f"Tempo: {tempo} BPM\n"

        prompt += """
Return ONLY valid JSON in this exact format:
{
  "key": "C",
  "tempo": 120,
  "chords": [
    {
      "symbol": "Cmaj7",
      "function": "I",
      "notes": ["C", "E", "G", "B"],
      "comment": "Tonic with jazz color"
    }
  ]
}"""

        return prompt

    def _parse_llm_response(
        self,
        response: str,
        key: Optional[str],
        tempo: Optional[int]
    ) -> tuple:
        """Parse LLM response into (chords, key, tempo, analysis) tuple."""
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            raise ValueError("No JSON found in LLM response")

        data = json.loads(json_match.group(0))

        # Extract data
        key_result = data.get("key", key or "C")
        tempo_result = data.get("tempo", tempo or self.default_tempo)

        chord_list = data.get("chords", [])
        chords = [c.get("symbol", "C") for c in chord_list]

        # Build analysis
        analysis = [
            {
                "symbol": c.get("symbol", ""),
                "function": c.get("function", ""),
                "notes": c.get("notes", []),
                "comment": c.get("comment", "")
            }
            for c in chord_list
        ]

        return (chords, key_result, tempo_result, analysis)

    def get_llm_stats(self) -> Dict[str, Any]:
        """Get local LLM usage statistics."""
        total = self._generation_stats["local_count"] + self._generation_stats["gemini_count"]
        local_percentage = (
            (self._generation_stats["local_count"] / total * 100)
            if total > 0 else 0
        )

        return {
            "local_llm_enabled": self._local_llm_enabled,
            "local_generations": self._generation_stats["local_count"],
            "gemini_generations": self._generation_stats["gemini_count"],
            "total_generations": total,
            "local_percentage": local_percentage,
            "estimated_cost_saved_usd": self._generation_stats["local_cost_saved"],
            "estimated_monthly_savings_usd": self._generation_stats["local_cost_saved"] * 30  # Rough estimate
        }

    def reset_llm_stats(self):
        """Reset statistics counters."""
        self._generation_stats = {
            "local_count": 0,
            "gemini_count": 0,
            "local_cost_saved": 0.0
        }
        logger.info("📊 LLM statistics reset")
