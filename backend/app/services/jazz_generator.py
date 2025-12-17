"""Jazz Piano Generation Service - Refactored with Base Class

Reduced from 284 lines to ~90 lines by using BaseGenreGenerator.
"""

from typing import List

from app.services.base_genre_generator import BaseGenreGenerator
from app.services.local_llm_generator_mixin import LocalLLMGeneratorMixin
from app.services.ml_progression_predictor_mixin import MLProgressionPredictorMixin
from app.services.user_preference_learning_mixin import UserPreferenceLearningMixin
from app.schemas.jazz import (
    GenerateJazzRequest,
    GenerateJazzResponse,
    JazzGeneratorStatus,
)
from app.jazz.arrangement.arranger import JazzArranger


class JazzGeneratorService(
    LocalLLMGeneratorMixin,
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    BaseGenreGenerator
):
    """
    Jazz piano generation service.

    Pipeline:
    1. Gemini API generates chord progression from natural language
    2. JazzArranger creates MIDI arrangement (rule-based)
    3. Export to MIDI file

    Falls back gracefully if any component unavailable.
    """

    def __init__(self):
        """Initialize jazz generation service."""
        super().__init__(
            genre_name="Jazz",
            arranger_class=JazzArranger,
            request_schema=GenerateJazzRequest,
            response_schema=GenerateJazzResponse,
            status_schema=JazzGeneratorStatus,
            default_tempo=120,  # Standard jazz tempo
            output_subdir="jazz_generated"
        )

    # =====================================================================
    # ABSTRACT METHOD IMPLEMENTATIONS - Jazz-specific behavior
    # =====================================================================

    def _get_style_context(self, complexity: int = 5, style: str = "") -> str:
        """Get jazz-specific style context for AI prompts."""
        
        # Harmonic Complexity
        if complexity <= 3:
            harmony = "Use basic ii-V-I progressions with 7th chords. Avoid excessive extensions."
        elif complexity <= 6:
            harmony = "Use standard jazz harmony (9ths, 11ths, 13ths) and rootless voicings."
        else:
            harmony = "Use advanced modern jazz harmony, altered dominants, tritone subs, and quartal voicings."

        # Style Nuances
        style_reqs = ""
        st = style.lower()
        if "bebop" in st:
            style_reqs = "- Fast harmonic rhythm, use chromatic approach chords"
        elif "modal" in st:
            style_reqs = "- Use modal interchange and static harmony (e.g., So What chords)"
        elif "ballad" in st:
            style_reqs = "- Lush, dense voicings with slow harmonic rhythm"
            
        return f"""Requirements:
- {harmony}
- Rootless voicings (drop-2, drop-3)
- Walking bass patterns in left hand
- Syncopated comping rhythms
- Consider bebop, modal jazz, and swing traditions
{style_reqs}"""

    def _get_default_progression(self, key: str) -> List[str]:
        """Get fallback jazz chord progression (ii-V-I in C)."""
        return ["Dm7", "G7", "Cmaj7", "Am7"]

    def get_status(self) -> JazzGeneratorStatus:
        """Get current status of jazz generation system."""
        return JazzGeneratorStatus(
            gemini_available=self.gemini_model is not None,
            rules_available=self.arranger is not None,
            ready_for_production=(
                self.gemini_model is not None and self.arranger is not None
            )
        )

    # =====================================================================
    # PUBLIC API - Maintains backward compatibility
    # =====================================================================

    async def generate_jazz_arrangement(
        self,
        request: GenerateJazzRequest
    ) -> GenerateJazzResponse:
        """
        Generate complete jazz piano arrangement from natural language.

        Args:
            request: Generation parameters

        Returns:
            GenerateJazzResponse with MIDI file and metadata
        """
        return await self.generate_arrangement(request)


# Global service instance
jazz_generator_service = JazzGeneratorService()
