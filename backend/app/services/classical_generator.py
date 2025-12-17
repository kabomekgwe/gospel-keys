"""Classical Piano Generation Service - Refactored with Base Class

Reduced from 126 lines to ~95 lines by using BaseGenreGenerator.
"""

from typing import List

from app.services.base_genre_generator import BaseGenreGenerator
from app.services.local_llm_generator_mixin import LocalLLMGeneratorMixin
from app.services.ml_progression_predictor_mixin import MLProgressionPredictorMixin
from app.services.user_preference_learning_mixin import UserPreferenceLearningMixin
from app.schemas.classical import (
    GenerateClassicalRequest,
    GenerateClassicalResponse,
    ClassicalGeneratorStatus,
)
from app.classical.arrangement.arranger import ClassicalArranger


class ClassicalGeneratorService(
    LocalLLMGeneratorMixin,
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    BaseGenreGenerator
):
    """
    Classical piano generation service.

    Pipeline:
    1. Gemini API generates chord progression from natural language
    2. ClassicalArranger creates MIDI arrangement (rule-based)
    3. Export to MIDI file
    """

    def __init__(self):
        """Initialize classical generation service."""
        super().__init__(
            genre_name="Classical",
            arranger_class=ClassicalArranger,
            request_schema=GenerateClassicalRequest,
            response_schema=GenerateClassicalResponse,
            status_schema=ClassicalGeneratorStatus,
            default_tempo=120,  # Moderate classical tempo
            output_subdir="classical_generated"
        )

    def _get_style_context(self, complexity: int = 5, style: str = "") -> str:
        """Get classical-specific style context for AI prompts."""
        
        # Harmonic Complexity
        if complexity <= 4:
            harmony = "Use functional harmony (I-IV-V) and homophonic texture (melody + accompaniment)."
        elif complexity <= 7:
            harmony = "Use fully realized 4-part harmony, applied dominants, and modulation to related keys."
        else:
            harmony = "Use advanced chromaticism, remote modulations, and contrapuntal texture (fugue/canon)."

        # Style Nuances
        style_n = ""
        st = style.lower()
        if "baroque" in st or "bach" in st:
            style_n = "- Baroque style: imitation, ornamentation, terraced dynamics"
        elif "romantic" in st or "chopin" in st:
            style_n = "- Romantic style: rubato, wide spacing, dramatic dynamic contrast"
        elif "impressionist" in st or "debussy" in st:
            style_n = "- Impressionist style: parallel motion, extended chords, blurring tonality"

        return f"""Requirements:
- {harmony}
- Proper voice leading rules (avoid parallel 5ths/8ves)
- Cadences: authentic, plagal, deceptive, half
- Counterpoint and polyphonic texture
- Period-appropriate style
- Alberti bass, arpeggios, or contrapuntal left hand
{style_n}"""

    def _get_default_progression(self, key: str) -> List[str]:
        """Get fallback classical progression (I-IV-V-I)."""
        # Standard classical cadence
        return [f"{key}", "F", "G", f"{key}"]

    def get_status(self) -> ClassicalGeneratorStatus:
        """Get current status of classical generation system."""
        return ClassicalGeneratorStatus(
            gemini_available=self.gemini_model is not None,
            rules_available=self.arranger is not None,
            ready_for_production=(
                self.gemini_model is not None and self.arranger is not None
            )
        )

    async def generate_classical_arrangement(
        self,
        request: GenerateClassicalRequest
    ) -> GenerateClassicalResponse:
        """Generate classical piano arrangement."""
        return await self.generate_arrangement(request)


# Global service instance
classical_generator_service = ClassicalGeneratorService()
