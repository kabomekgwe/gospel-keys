"""Jazz Piano Generation Service - Refactored with Base Class

Reduced from 284 lines to ~90 lines by using BaseGenreGenerator.
"""

from typing import List

from app.services.base_genre_generator import BaseGenreGenerator
from app.schemas.jazz import (
    GenerateJazzRequest,
    GenerateJazzResponse,
    JazzGeneratorStatus,
)
from app.jazz.arrangement.arranger import JazzArranger


class JazzGeneratorService(BaseGenreGenerator):
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

    def _get_style_context(self) -> str:
        """Get jazz-specific style context for AI prompts."""
        return """Requirements:
- Use jazz harmony with ii-V-I progressions
- Rootless voicings (drop-2, drop-3)
- Extensions: 9ths, 11ths, 13ths, altered dominants
- Walking bass patterns in left hand
- Syncopated comping rhythms
- Consider bebop, modal jazz, and swing traditions"""

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
