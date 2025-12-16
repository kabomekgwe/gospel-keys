"""Blues Piano Generation Service - Refactored with Base Class

Reduced from 115 lines to ~85 lines by using BaseGenreGenerator.
"""

from typing import List

from app.services.base_genre_generator import BaseGenreGenerator
from app.schemas.blues import (
    GenerateBluesRequest,
    GenerateBluesResponse,
    BluesGeneratorStatus,
)
from app.blues.arrangement.arranger import BluesArranger


class BluesGeneratorService(BaseGenreGenerator):
    """Blues piano generation service."""

    def __init__(self):
        """Initialize blues generation service."""
        super().__init__(
            genre_name="Blues",
            arranger_class=BluesArranger,
            request_schema=GenerateBluesRequest,
            response_schema=GenerateBluesResponse,
            status_schema=BluesGeneratorStatus,
            default_tempo=90,  # Medium swing tempo
            output_subdir="blues_generated"
        )

    def _get_style_context(self) -> str:
        """Get blues-specific style context for AI prompts."""
        return """Requirements:
- 12-bar blues form (I-I-I-I-IV-IV-I-I-V-IV-I-I/V)
- Blues scale with blue notes (♭3, ♭5, ♭7)
- Dominant 7th chords (I7, IV7, V7)
- Shuffle/swing rhythm (triplet feel)
- Call-and-response patterns
- Blues riffs and licks"""

    def _get_default_progression(self, key: str) -> List[str]:
        """Get fallback blues progression (12-bar blues)."""
        # Standard 12-bar blues in I-IV-V
        return [f"{key}7", f"{key}7", "F7", f"{key}7", "G7"]

    def get_status(self) -> BluesGeneratorStatus:
        """Get current status of blues generation system."""
        return BluesGeneratorStatus(
            gemini_available=self.gemini_model is not None,
            rules_available=self.arranger is not None,
            ready_for_production=(
                self.gemini_model is not None and self.arranger is not None
            )
        )

    async def generate_blues_arrangement(
        self,
        request: GenerateBluesRequest
    ) -> GenerateBluesResponse:
        """Generate blues piano arrangement."""
        return await self.generate_arrangement(request)


# Global service instance
blues_generator_service = BluesGeneratorService()
