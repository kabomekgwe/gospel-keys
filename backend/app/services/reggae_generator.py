"""
Reggae generator service using refactored base class.

Provides reggae-specific style context and default progressions.
"""

from typing import List
from app.services.base_genre_generator import BaseGenreGenerator
from app.services.local_llm_generator_mixin import LocalLLMGeneratorMixin
from app.services.ml_progression_predictor_mixin import MLProgressionPredictorMixin
from app.services.user_preference_learning_mixin import UserPreferenceLearningMixin
from app.reggae.arrangement.arranger import ReggaeArranger
from app.schemas.reggae import (
    GenerateReggaeRequest,
    GenerateReggaeResponse,
    ReggaeGeneratorStatus
)


class ReggaeGeneratorService(
    LocalLLMGeneratorMixin,
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    BaseGenreGenerator
):
    """
    Reggae music generator.

    Features:
    - Offbeat emphasis (skank rhythm on upbeats)
    - Dub bass lines with heavy low-end
    - One-drop drum pattern
    - Characteristic chord voicings (major triads, sus chords)
    - Laid-back groove with syncopation
    """

    def __init__(self):
        super().__init__(
            genre_name="Reggae",
            arranger_class=ReggaeArranger,
            request_schema=GenerateReggaeRequest,
            response_schema=GenerateReggaeResponse,
            status_schema=ReggaeGeneratorStatus,
            default_tempo=75,  # Laid-back reggae tempo
            output_subdir="reggae_generated"
        )

    def _get_style_context(self, complexity: int = 5, style: str = "") -> str:
        """
        Get reggae-specific style context for AI prompts.

        Returns reggae harmony and rhythm characteristics.
        """
        if complexity <= 4:
            harmony_text = "- Use simple major triads and minimal progressions."
        elif complexity <= 7:
            harmony_text = "- Use added 7ths and sus chords for color."
        else:
            harmony_text = "- Use Dub-style minor 9ths, bi-tonal chords, and complex voice leading."

        style_n = ""
        st = style.lower()
        if "dub" in st:
            style_n = "- Dub style: heavy bass, sparse chords, echo effects"
        elif "rocksteady" in st:
            style_n = "- Rocksteady: smoother, melodic bass lines"
        elif "dancehall" in st:
            style_n = "- Dancehall: digital, sparse, rhythmic"

        return f"""Requirements for authentic reggae music:

        Harmony:
        {harmony_text}
        - I-IV-V progressions are common (e.g., C-F-G in C major)
        - Minor chord progressions: i-VI-III-VII (e.g., Am-F-C-G)
        - Add occasional diminished passing chords
        - Keep voicings simple and open

        Rhythm:
        - Emphasize offbeats (2 and 4) - the "skank" rhythm
        - One-drop drum pattern (kick on beat 3)
        - Bass plays roots with characteristic walking patterns
        - Syncopated rhythms with laid-back feel
        - Staccato chord stabs on upbeats

        Style:
        - Laid-back groove at 70-80 BPM
        - Heavy low-end bass presence
        {style_n}
        """

    def _get_default_progression(self, key: str) -> List[str]:
        """
        Get fallback reggae chord progression.

        Returns classic I-IV-V reggae progression with characteristic voicings.
        """
        # Map keys to reggae progressions (I-IV-V with sus variations)
        progressions = {
            "C": ["C", "F", "G", "F"],
            "D": ["D", "G", "A", "G"],
            "E": ["E", "A", "B", "A"],
            "F": ["F", "Bb", "C", "Bb"],
            "G": ["G", "C", "D", "C"],
            "A": ["A", "D", "E", "D"],
            "B": ["B", "E", "F#", "E"],
            "Am": ["Am", "F", "C", "G"],
            "Dm": ["Dm", "Bb", "F", "C"],
            "Em": ["Em", "C", "G", "D"]
        }

        return progressions.get(key, ["C", "F", "G", "F"])

    def get_status(self):
        """
        Get current status of reggae generator.

        Returns status information including model availability.
        """
        return self.status_schema(
            gemini_available=self.gemini_model is not None,
            ready=True
        )


# Singleton instance
reggae_generator_service = ReggaeGeneratorService()
