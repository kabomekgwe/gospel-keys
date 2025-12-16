"""
Latin/Salsa generator service using refactored base class.

Provides Latin music style context and default progressions.
"""

from typing import List
from app.services.base_genre_generator import BaseGenreGenerator
from app.services.local_llm_generator_mixin import LocalLLMGeneratorMixin
from app.services.ml_progression_predictor_mixin import MLProgressionPredictorMixin
from app.services.user_preference_learning_mixin import UserPreferenceLearningMixin
from app.latin.arrangement.arranger import LatinArranger
from app.schemas.latin import (
    GenerateLatinRequest,
    GenerateLatinResponse,
    LatinGeneratorStatus
)


class LatinGeneratorService(
    LocalLLMGeneratorMixin,
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    BaseGenreGenerator
):
    """
    Latin/Salsa music generator.

    Features:
    - Montuno piano patterns (repetitive syncopated figures)
    - Clave rhythm foundation (3-2 or 2-3 son clave)
    - Tumbao bass patterns
    - Cuban harmony with characteristic voicings
    - Syncopated, danceable groove
    """

    def __init__(self):
        super().__init__(
            genre_name="Latin",
            arranger_class=LatinArranger,
            request_schema=GenerateLatinRequest,
            response_schema=GenerateLatinResponse,
            status_schema=LatinGeneratorStatus,
            default_tempo=95,  # Typical salsa tempo
            output_subdir="latin_generated"
        )

    def _get_style_context(self) -> str:
        """
        Get Latin/Salsa-specific style context for AI prompts.

        Returns Latin harmony and rhythm characteristics.
        """
        return """Requirements for authentic Latin/Salsa music:

        Harmony:
        - Use ii-V-I progressions common in Cuban music
        - Minor chord progressions: i-iv-V7 (e.g., Am-Dm-E7)
        - Dominant 7th chords with tensions (9ths, 13ths)
        - Montuno patterns: repetitive 2-bar syncopated figures
        - Guajeo voicings: characteristic Cuban piano patterns
        - Modal harmony (Dorian, Mixolydian for improvisation)

        Rhythm:
        - Clave rhythm as foundation (3-2 or 2-3 son clave)
        - Tumbao bass pattern (syncopated roots and 5ths)
        - Montuno piano with cascara-style syncopation
        - Anticipations on beat 4+ ("and" of 4)
        - Polyrhythmic layering (cross-rhythms)

        Style:
        - Danceable groove at 90-100 BPM
        - High energy with driving rhythm section
        - Syncopated chord comping (piano montuno)
        - Call-and-response patterns
        - Authentic Cuban salsa feel
        """

    def _get_default_progression(self, key: str) -> List[str]:
        """
        Get fallback Latin/Salsa chord progression.

        Returns classic Latin progression with characteristic harmony.
        """
        # Map keys to Latin progressions (with dominant 7ths and minor variations)
        progressions = {
            "C": ["Cmaj7", "A7", "Dm7", "G7"],      # I-VI7-ii-V
            "D": ["Dmaj7", "B7", "Em7", "A7"],
            "E": ["Emaj7", "C#7", "F#m7", "B7"],
            "F": ["Fmaj7", "D7", "Gm7", "C7"],
            "G": ["Gmaj7", "E7", "Am7", "D7"],
            "A": ["Amaj7", "F#7", "Bm7", "E7"],
            "B": ["Bmaj7", "G#7", "C#m7", "F#7"],
            "Am": ["Am7", "Dm7", "E7", "Am7"],      # i-iv-V7-i
            "Dm": ["Dm7", "Gm7", "A7", "Dm7"],
            "Em": ["Em7", "Am7", "B7", "Em7"]
        }

        return progressions.get(key, ["Cmaj7", "A7", "Dm7", "G7"])

    def get_status(self):
        """
        Get current status of Latin generator.

        Returns status information including model availability.
        """
        return self.status_schema(
            gemini_available=self.gemini_model is not None,
            ready=True
        )


# Singleton instance
latin_generator_service = LatinGeneratorService()
