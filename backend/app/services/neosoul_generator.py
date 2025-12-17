"""Neo-Soul Piano Generation Service - Refactored with Base Class

Reduced from 284 lines to ~95 lines by using BaseGenreGenerator.
"""

from typing import List

from app.services.base_genre_generator import BaseGenreGenerator
from app.services.local_llm_generator_mixin import LocalLLMGeneratorMixin
from app.services.ml_progression_predictor_mixin import MLProgressionPredictorMixin
from app.services.user_preference_learning_mixin import UserPreferenceLearningMixin
from app.schemas.neosoul import (
    GenerateNeosoulRequest,
    GenerateNeosoulResponse,
    NeosoulGeneratorStatus,
)
from app.neosoul.arrangement.arranger import NeosoulArranger


class NeosoulGeneratorService(
    LocalLLMGeneratorMixin,
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    BaseGenreGenerator
):
    """
    Neo-soul piano generation service.

    Pipeline:
    1. Gemini API generates chord progression from natural language
    2. NeosoulArranger creates MIDI arrangement (rule-based)
    3. Export to MIDI file
    """

    def __init__(self):
        """Initialize neo-soul generation service."""
        super().__init__(
            genre_name="Neo-Soul",
            arranger_class=NeosoulArranger,
            request_schema=GenerateNeosoulRequest,
            response_schema=GenerateNeosoulResponse,
            status_schema=NeosoulGeneratorStatus,
            default_tempo=85,  # Laid-back neo-soul tempo
            output_subdir="neosoul_generated"
        )

    def _get_style_context(self, complexity: int = 5, style: str = "") -> str:
        """Get neo-soul-specific style context for AI prompts."""
        
        # Harmonic Complexity
        if complexity <= 4:
            harmony = "Use lush maj9 and m9 chords. diatonic progressions."
        elif complexity <= 7:
            harmony = "Use extended harmony (11ths, 13ths), secondary dominants, and chromatic passing chords."
        else:
            harmony = "Use advanced non-functional harmony, altered chords (7#9, 7b13), polychords, and quartal voicings."

        # Style Nuances
        style_reqs = ""
        st = style.lower()
        if "dilla" in st or "swing" in st:
            style_reqs = "- Use 'drunk' swing feel (unquantized/laid back)"
        elif "gospel" in st:
            style_reqs = "- Incorporate gospel passing chords and plagal cadences"
            
        return f"""Requirements:
- {harmony}
- Modal interchange and borrowed chords
- Jazzy, syncopated rhythms
- R&B/soul influenced voicings
- Contemporary urban feel
- Smooth voice leading
- Influences: D'Angelo, Erykah Badu, Robert Glasper
{style_reqs}"""

    def _get_default_progression(self, key: str) -> List[str]:
        """Get fallback neo-soul progression."""
        # Colorful neo-soul progression with extensions
        return [f"{key}maj9", "Dm9", "Em11", "Fmaj9", "Am9"]

    def get_status(self) -> NeosoulGeneratorStatus:
        """Get current status of neo-soul generation system."""
        return NeosoulGeneratorStatus(
            gemini_available=self.gemini_model is not None,
            rules_available=self.arranger is not None,
            ready_for_production=(
                self.gemini_model is not None and self.arranger is not None
            )
        )

    async def generate_neosoul_arrangement(
        self,
        request: GenerateNeosoulRequest
    ) -> GenerateNeosoulResponse:
        """Generate neo-soul piano arrangement."""
        return await self.generate_arrangement(request)


# Global service instance
neosoul_generator_service = NeosoulGeneratorService()
