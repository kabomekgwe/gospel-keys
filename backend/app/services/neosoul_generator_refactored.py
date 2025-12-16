"""Neo-Soul Piano Generation Service - Refactored with Base Class

Reduced from 284 lines to ~95 lines by using BaseGenreGenerator.
"""

from typing import List

from app.services.base_genre_generator import BaseGenreGenerator
from app.schemas.neosoul import (
    GenerateNeosoulRequest,
    GenerateNeosoulResponse,
    NeosoulGeneratorStatus,
)
from app.neosoul.arrangement.arranger import NeosoulArranger


class NeosoulGeneratorService(BaseGenreGenerator):
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

    def _get_style_context(self) -> str:
        """Get neo-soul-specific style context for AI prompts."""
        return """Requirements:
- Rich, colorful harmony with 9ths, 11ths, 13ths
- Modal interchange and borrowed chords
- Jazzy, syncopated rhythms
- R&B/soul influenced voicings
- Lush chord progressions
- Contemporary urban feel
- Smooth voice leading
- Influences: D'Angelo, Erykah Badu, Robert Glasper"""

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
