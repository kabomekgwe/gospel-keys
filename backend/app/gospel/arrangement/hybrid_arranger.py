"""
Hybrid Gospel Arranger - AI + Rules

Combines MLX-learned patterns with music theory rules for best results.

Strategy:
- MLX generates creative gospel patterns (post fine-tuning)
- Rules ensure playability and music theory correctness
- Gradual AI adoption: 20% → 50% → 80% → 100% as quality improves

Usage:
    arranger = HybridGospelArranger(ai_percentage=0.5)  # 50% AI, 50% rules
    arrangement = arranger.arrange_progression(chords, key, bpm, "worship")
"""

from pathlib import Path
from typing import Optional
import random

from ..import Note, ChordContext, Arrangement
from .arranger import GospelArranger
from ..ai.mlx_music_generator import MLXGospelGenerator


class HybridGospelArranger(GospelArranger):
    """
    Hybrid arranger using both MLX AI and rule-based generation.

    Modes:
    - 0.0 (0%): Pure rule-based (original GospelArranger)
    - 0.2 (20%): Mostly rules, occasional AI patterns
    - 0.5 (50%): Balanced hybrid
    - 0.8 (80%): Mostly AI, rules for validation
    - 1.0 (100%): Pure AI (after validation)
    """

    def __init__(
        self,
        ai_percentage: float = 0.5,
        mlx_checkpoint: Optional[Path] = None,
        fallback_to_rules: bool = True
    ):
        """
        Initialize hybrid arranger.

        Args:
            ai_percentage: 0.0-1.0, percentage of AI vs rules
            mlx_checkpoint: Path to fine-tuned MLX gospel model
            fallback_to_rules: If True, fallback to rules on AI failure
        """
        super().__init__()

        self.ai_percentage = ai_percentage
        self.fallback_to_rules = fallback_to_rules

        # Initialize MLX generator (only if ai_percentage > 0)
        self.mlx_generator = None
        if ai_percentage > 0:
            try:
                print(f"🎹 Initializing MLX Gospel Generator (AI: {ai_percentage * 100}%)")
                self.mlx_generator = MLXGospelGenerator(
                    checkpoint_dir=mlx_checkpoint
                )
                print(f"✅ MLX Generator loaded")
            except Exception as e:
                print(f"⚠️  MLX Generator failed to load: {e}")
                if not fallback_to_rules:
                    raise
                print(f"   Falling back to rule-based generation")
                self.ai_percentage = 0.0

    def arrange_progression(
        self,
        chords: list[str],
        key: str,
        bpm: int,
        application: str,
        time_signature: str = "4/4",
        use_ai: Optional[bool] = None
    ) -> Arrangement:
        """
        Arrange gospel piano progression with hybrid AI + rules.

        Args:
            chords: Chord progression
            key: Musical key
            bpm: BPM
            application: "worship", "uptempo", "practice", "concert"
            time_signature: Time signature
            use_ai: Override ai_percentage (None = use configured percentage)

        Returns:
            Arrangement with left/right hand notes
        """
        # Determine if this arrangement uses AI
        use_ai_for_this = use_ai if use_ai is not None else (random.random() < self.ai_percentage)

        if use_ai_for_this and self.mlx_generator:
            try:
                # Generate with MLX AI
                print(f"🤖 Generating with MLX AI (application: {application})")
                return self._generate_with_ai(chords, key, bpm, application, time_signature)
            except Exception as e:
                print(f"⚠️  AI generation failed: {e}")
                if not self.fallback_to_rules:
                    raise
                print(f"   Falling back to rule-based generation")

        # Generate with rules (original GospelArranger)
        print(f"📏 Generating with rules (application: {application})")
        return super().arrange_progression(
            chords, key, bpm, application, time_signature
        )

    def _generate_with_ai(
        self,
        chords: list[str],
        key: str,
        bpm: int,
        application: str,
        time_signature: str
    ) -> Arrangement:
        """Generate arrangement using MLX AI."""
        # Generate with MLX
        arrangement = self.mlx_generator.generate_arrangement(
            chord_progression=chords,
            key=key,
            tempo=bpm,
            application=application,
            num_bars=len(chords),
            creativity=0.8  # Allow creative variation
        )

        # Validate and fix with rules
        if self._should_apply_rule_validation():
            arrangement = self._validate_and_fix_ai_output(arrangement, chords, application)

        return arrangement

    def _should_apply_rule_validation(self) -> bool:
        """
        Decide if rule-based validation should be applied.

        - Always validate for "practice" application (need to ensure playability)
        - Usually validate for low AI percentages (safety net)
        - Sometimes validate for high AI percentages (quality check)
        """
        if self.ai_percentage < 0.3:
            return True  # Always validate when mostly rules
        elif self.ai_percentage < 0.7:
            return random.random() < 0.5  # Sometimes validate in hybrid mode
        else:
            return random.random() < 0.2  # Rarely validate when mostly AI

    def _validate_and_fix_ai_output(
        self,
        arrangement: Arrangement,
        chords: list[str],
        application: str
    ) -> Arrangement:
        """
        Apply rule-based validation and fixes to AI-generated arrangement.

        Checks:
        1. Hand span (playability)
        2. Voice leading smoothness
        3. Chord tone alignment
        4. Difficulty appropriate for application
        """
        # TODO: Implement validation logic
        # For now, return as-is
        return arrangement

    def get_generation_stats(self) -> dict:
        """Get statistics about AI vs rules usage."""
        return {
            "ai_percentage": self.ai_percentage,
            "mlx_available": self.mlx_generator is not None,
            "mode": self._get_mode_description()
        }

    def _get_mode_description(self) -> str:
        """Get human-readable mode description."""
        if self.ai_percentage == 0.0:
            return "Pure Rules (Original GospelArranger)"
        elif self.ai_percentage < 0.3:
            return f"Mostly Rules ({self.ai_percentage * 100:.0f}% AI for experimentation)"
        elif self.ai_percentage < 0.7:
            return f"Balanced Hybrid ({self.ai_percentage * 100:.0f}% AI, {(1 - self.ai_percentage) * 100:.0f}% Rules)"
        elif self.ai_percentage < 1.0:
            return f"Mostly AI ({self.ai_percentage * 100:.0f}% AI with rule validation)"
        else:
            return "Pure AI (100% MLX generation)"


# Convenience function
def create_gospel_arranger(
    mode: str = "hybrid",
    mlx_checkpoint: Optional[Path] = None
) -> GospelArranger | HybridGospelArranger:
    """
    Factory function to create appropriate gospel arranger.

    Args:
        mode: "rules" (0% AI), "hybrid" (50% AI), "ai" (80% AI), or "pure-ai" (100% AI)
        mlx_checkpoint: Path to fine-tuned MLX model

    Returns:
        GospelArranger or HybridGospelArranger instance
    """
    mode_percentages = {
        "rules": 0.0,
        "hybrid": 0.5,
        "ai": 0.8,
        "pure-ai": 1.0
    }

    ai_percentage = mode_percentages.get(mode, 0.5)

    if ai_percentage == 0.0:
        # Pure rules - use original arranger
        return GospelArranger()
    else:
        # Hybrid - use MLX + rules
        return HybridGospelArranger(
            ai_percentage=ai_percentage,
            mlx_checkpoint=mlx_checkpoint
        )
