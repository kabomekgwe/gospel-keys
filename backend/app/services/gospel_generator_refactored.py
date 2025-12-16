"""Gospel Piano Generation Service - Refactored with Base Class

Significantly reduced from 382 lines to ~120 lines by using BaseGenreGenerator.
All duplicate logic eliminated through inheritance.
"""

from typing import List, Optional
from pathlib import Path

from app.services.base_genre_generator import BaseGenreGenerator
from app.schemas.gospel import (
    GenerateGospelRequest,
    GenerateGospelResponse,
    GospelGeneratorStatus,
)
from app.gospel.arrangement.hybrid_arranger import HybridGospelArranger
from app.gospel.arrangement.arranger import GospelArranger


class GospelGeneratorService(BaseGenreGenerator):
    """
    Gospel piano generation service using hybrid AI+rules approach.

    Pipeline:
    1. Gemini API generates chord progression from natural language
    2. HybridGospelArranger creates MIDI arrangement (MLX or rules)
    3. Export to MIDI file

    Falls back gracefully if any component unavailable.
    """

    def __init__(self):
        """Initialize gospel generation service."""
        # Call base class with gospel-specific configuration
        super().__init__(
            genre_name="Gospel",
            arranger_class=GospelArranger,  # Fallback arranger
            request_schema=GenerateGospelRequest,
            response_schema=GenerateGospelResponse,
            status_schema=GospelGeneratorStatus,
            default_tempo=72,  # Slower tempo for gospel
            output_subdir="gospel_generated"
        )

        # Gospel-specific: Hybrid arranger (optional MLX support)
        self.hybrid_arranger = None
        self.rule_arranger = self.arranger  # Keep reference for clarity

    # =====================================================================
    # ABSTRACT METHOD IMPLEMENTATIONS - Gospel-specific behavior
    # =====================================================================

    def _get_style_context(self) -> str:
        """Get gospel-specific style context for AI prompts."""
        context = """Requirements:
- Use extended gospel harmony (9ths, 11ths, 13ths)
- Include chromatic passing chords
- Authentic gospel voice leading
- Rich harmonic movement
- Consider gospel traditions: call-and-response, modulation, runs"""

        # Try to get additional context from knowledge base
        kb_context = self._get_gospel_style_context()
        if kb_context:
            context += f"\n\n{kb_context}"

        return context

    def _get_default_progression(self, key: str) -> List[str]:
        """Get fallback gospel chord progression."""
        # Classic gospel progression with extended harmony
        return [
            f"{key}maj7",
            f"{key}maj9",
            "Fmaj7",
            "G7",
            "Am7"
        ]

    def get_status(self) -> GospelGeneratorStatus:
        """Get current status of gospel generation system."""
        # Check if MLX is available
        mlx_available = False
        mlx_trained = False
        try:
            from app.gospel.ai.mlx_music_generator import MLXGospelGenerator
            mlx_available = True
            # Check for trained checkpoint
            checkpoint_path = Path("checkpoints/mlx-gospel/best")
            mlx_trained = checkpoint_path.exists()
        except Exception:
            pass

        # Check dataset size
        dataset_path = Path("data/gospel_dataset/validated")
        dataset_size = len(list(dataset_path.glob("*.mid"))) if dataset_path.exists() else 0

        # Determine recommended AI percentage
        if mlx_trained and dataset_size >= 100:
            recommended_ai = 0.8  # Highly trained
        elif mlx_trained and dataset_size >= 50:
            recommended_ai = 0.5  # Moderately trained
        elif mlx_available:
            recommended_ai = 0.2  # Pretrained only
        else:
            recommended_ai = 0.0  # Rules only

        return GospelGeneratorStatus(
            mlx_available=mlx_available,
            mlx_trained=mlx_trained,
            gemini_available=self.gemini_model is not None,
            recommended_ai_percentage=recommended_ai,
            dataset_size=dataset_size,
            ready_for_production=(mlx_trained and dataset_size >= 100)
        )

    # =====================================================================
    # GOSPEL-SPECIFIC OVERRIDES - Hybrid arranger support
    # =====================================================================

    def _create_arrangement(self, chords: List[str], key: str, tempo: int, request: Any):
        """
        Override to support hybrid AI+rules arrangement.

        Gospel generator uniquely supports blending MLX AI with rule-based
        arrangement through the HybridGospelArranger.
        """
        # Determine which arranger to use based on AI percentage
        arranger = self._get_arranger(request.ai_percentage)

        # Create arrangement
        return arranger.arrange_progression(
            chords=chords,
            key=key,
            bpm=tempo,
            application=request.application.value,
            time_signature=(4, 4)
        )

    def _get_arranger(self, ai_percentage: float):
        """
        Get appropriate arranger based on AI percentage.

        Returns:
            HybridGospelArranger if ai_percentage > 0, else GospelArranger
        """
        if ai_percentage > 0:
            # Try to initialize hybrid arranger if not already done
            if self.hybrid_arranger is None:
                try:
                    self.hybrid_arranger = HybridGospelArranger(
                        ai_percentage=ai_percentage,
                        fallback_to_rules=True
                    )
                except Exception as e:
                    print(f"⚠️  Hybrid arranger init failed: {e}, using rules")
                    return self.rule_arranger

            # Update AI percentage if arranger already exists
            self.hybrid_arranger.ai_percentage = ai_percentage
            return self.hybrid_arranger
        else:
            return self.rule_arranger

    def _determine_generation_method(self, request) -> str:
        """
        Override to include MLX hybrid info.

        Returns:
            Detailed generation method string
        """
        if self.gemini_model and request.include_progression:
            if request.ai_percentage == 0.0:
                return "gemini+rules"
            elif request.ai_percentage == 1.0:
                return "gemini+mlx"
            else:
                return "gemini+hybrid"
        elif request.ai_percentage > 0:
            return "mlx+rules"
        else:
            return "rules-only"

    # =====================================================================
    # GOSPEL-SPECIFIC HELPERS - Knowledge base integration
    # =====================================================================

    def _get_gospel_style_context(self) -> str:
        """
        Get gospel style context from knowledge base for prompt enhancement.

        Returns:
            Formatted string with gospel-specific guidelines, or empty if unavailable.
        """
        try:
            from app.main import music_knowledge_base

            if music_knowledge_base and music_knowledge_base.is_loaded():
                # Get traditional gospel guidelines
                gospel_guidelines = music_knowledge_base.format_style_guidelines_for_prompt(
                    "gospel",
                    "traditional"
                )

                # If we got comprehensive guidelines, format for prompt
                if gospel_guidelines and len(gospel_guidelines) > 50:
                    return f"\nGOSPEL STYLE GUIDELINES:\n{gospel_guidelines}\n"

        except Exception:
            # Knowledge base not available, return empty (will use base requirements)
            pass

        return ""

    # =====================================================================
    # PUBLIC API - Maintains backward compatibility
    # =====================================================================

    async def generate_gospel_arrangement(
        self,
        request: GenerateGospelRequest
    ) -> GenerateGospelResponse:
        """
        Generate complete gospel piano arrangement from natural language.

        This method maintains the original API for backward compatibility,
        delegating to the base class generate_arrangement method.

        Args:
            request: Generation parameters

        Returns:
            GenerateGospelResponse with MIDI file and metadata
        """
        return await self.generate_arrangement(request)


# Global service instance
gospel_generator_service = GospelGeneratorService()
