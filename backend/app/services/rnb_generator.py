"""
R&B generator service using refactored base class.

Provides R&B-specific style context and default progressions.
"""

from typing import List
from app.services.base_genre_generator import BaseGenreGenerator
from app.services.local_llm_generator_mixin import LocalLLMGeneratorMixin
from app.services.ml_progression_predictor_mixin import MLProgressionPredictorMixin
from app.services.user_preference_learning_mixin import UserPreferenceLearningMixin
from app.rnb.arrangement.arranger import RnBArranger
from app.schemas.rnb import (
    GenerateRnBRequest,
    GenerateRnBResponse,
    RnBGeneratorStatus
)


class RnBGeneratorService(
    LocalLLMGeneratorMixin,
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    BaseGenreGenerator
):
    """
    R&B music generator.

    Features:
    - Smooth extended harmonies (7ths, 9ths, 11ths)
    - Contemporary soul voicings
    - Syncopated rhythms with groove emphasis
    - Lush chord progressions
    - Neo-soul influenced harmony
    """

    def __init__(self):
        super().__init__(
            genre_name="R&B",
            arranger_class=RnBArranger,
            request_schema=GenerateRnBRequest,
            response_schema=GenerateRnBResponse,
            status_schema=RnBGeneratorStatus,
            default_tempo=85,  # Smooth R&B tempo
            output_subdir="rnb_generated"
        )

    def _get_style_context(self, complexity: int = 5, style: str = "") -> str:
        """
        Get R&B-specific style context for AI prompts.

        Returns R&B harmony and rhythm characteristics.
        """
        if complexity <= 4:
            harmony_text = "- Use standard extension chords: maj7, maj9, 9th"
        elif complexity <= 7:
            harmony_text = "- Use rich extensions (11th, 13th) and sus chords"
        else:
            harmony_text = "- Use advanced neo-soul harmony: chromatic movement, altered dominants, dim7 passing chords"

        style_n = ""
        st = style.lower()
        if "90s" in st:
            style_n = "- 90s New Jack Swing feel"
        elif "trap" in st:
            style_n = "- Trap-soul influence"
        elif "ballad" in st:
            style_n = "- Slow jam ballad feel"

        return f"""Requirements for authentic R&B music:

        Harmony:
        {harmony_text}
        - Contemporary progressions: I-vi-IV-V with extensions
        - Add sus2/sus4 for smooth transitions
        - Use add9 chords for lush voicings (e.g., Cadd9)
        - Modal interchange (borrow chords from parallel minor)
        - Smooth voice leading with minimal movement

        Rhythm:
        - Syncopated groove with emphasis on backbeats
        - Laid-back "in the pocket" feel
        - 16th-note subdivisions for contemporary R&B
        - Anticipations and delayed resolutions
        - Subtle swing/shuffle feel (not straight)
        - Space and breathing room in arrangement
        {style_n}
        """

    def _get_default_progression(self, key: str) -> List[str]:
        """
        Get fallback R&B chord progression.

        Returns classic R&B progression with extended harmony.
        """
        # Map keys to R&B progressions (with extended harmony and neo-soul flavor)
        progressions = {
            "C": ["Cmaj9", "Am7", "Fmaj7", "G9"],      # I-vi-IV-V with extensions
            "D": ["Dmaj9", "Bm7", "Gmaj7", "A9"],
            "E": ["Emaj9", "C#m7", "Amaj7", "B9"],
            "F": ["Fmaj9", "Dm7", "Bbmaj7", "C9"],
            "G": ["Gmaj9", "Em7", "Cmaj7", "D9"],
            "A": ["Amaj9", "F#m7", "Dmaj7", "E9"],
            "B": ["Bmaj9", "G#m7", "Emaj7", "F#9"],
            "Am": ["Am9", "Fmaj7", "Dm9", "E7#9"],     # Minor with altered dominant
            "Dm": ["Dm9", "Bbmaj7", "Gm9", "A7#9"],
            "Em": ["Em9", "Cmaj7", "Am9", "B7#9"]
        }

        return progressions.get(key, ["Cmaj9", "Am7", "Fmaj7", "G9"])

    def get_status(self):
        """
        Get current status of R&B generator.

        Returns status information including model availability.
        """
        return self.status_schema(
            gemini_available=self.gemini_model is not None,
            ready=True
        )


# Singleton instance
rnb_generator_service = RnBGeneratorService()
