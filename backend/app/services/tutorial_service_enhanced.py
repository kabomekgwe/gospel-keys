"""Enhanced Tutorial Generation Service

Example of using the new prompt architecture with:
- Genre-authentic system prompts
- Rich context building
- Metadata tracking
- Silent fallback
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional

from app.database.curriculum_models import CurriculumLesson
from app.services.ai_orchestrator_enhanced import enhanced_ai_orchestrator, TaskType
from app.prompts.builders import TutorialPromptBuilder
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedTutorialService:
    """Service for generating AI-powered lesson tutorials with enhanced prompts"""

    def __init__(self):
        self.cache_ttl_hours = 720  # 30 days
        self.orchestrator = enhanced_ai_orchestrator

    async def generate_lesson_tutorial(
        self,
        lesson: CurriculumLesson,
        force_regenerate: bool = False,
        user_skill_levels: Optional[Dict[str, int]] = None,
        genre: Optional[str] = None
    ) -> Dict:
        """Generate comprehensive tutorial for a lesson

        Args:
            lesson: CurriculumLesson model instance
            force_regenerate: Regenerate even if tutorial exists
            user_skill_levels: Optional skill levels for personalization
            genre: Musical genre (gospel, jazz, blues, classical, neosoul)

        Returns:
            Tutorial content dictionary
        """
        try:
            # Check if tutorial already exists
            if not force_regenerate and lesson.tutorial_content_json:
                existing_tutorial = json.loads(lesson.tutorial_content_json)
                if existing_tutorial:
                    logger.info(f"Using cached tutorial for lesson {lesson.id}")
                    return existing_tutorial

            logger.info(f"Generating tutorial for lesson: {lesson.title} (genre: {genre or 'general'})")

            # Build rich, structured prompt using new architecture
            prompt = self._build_enhanced_tutorial_prompt(
                lesson,
                user_skill_levels,
                genre
            )

            # Generate using enhanced orchestrator with metadata tracking
            tutorial_data = await self.orchestrator.generate_with_metadata(
                prompt=prompt,
                task_type=TaskType.TUTORIAL_GENERATION,
                complexity=7,  # Tutorials are moderately complex (Llama 3.3 70B)
                generation_config={
                    "temperature": 0.7,  # Creative but structured
                    "max_output_tokens": 4096,
                },
                cache_ttl_hours=self.cache_ttl_hours,
                genre=genre,
                return_metadata=False  # Users see only content (no metadata)
            )

            # Validate structure
            validated_tutorial = self._validate_tutorial_structure(tutorial_data)

            logger.info(
                f"Successfully generated tutorial for lesson {lesson.id}",
                extra={"genre": genre, "complexity": 7}
            )
            return validated_tutorial

        except Exception as e:
            logger.error(f"Failed to generate tutorial for lesson {lesson.id}: {e}")
            # Return fallback template
            return self._get_fallback_tutorial(lesson)

    def _build_enhanced_tutorial_prompt(
        self,
        lesson: CurriculumLesson,
        user_skill_levels: Optional[Dict[str, int]] = None,
        genre: Optional[str] = None
    ) -> str:
        """Build enhanced tutorial prompt using new PromptBuilder

        This replaces the old string concatenation approach with a structured,
        genre-aware prompt builder.

        Args:
            lesson: CurriculumLesson model instance
            user_skill_levels: Optional skill level dict
            genre: Musical genre

        Returns:
            Complete prompt string with genre-authentic context
        """
        # Initialize builder with genre context (includes genre-specific system prompt)
        builder = TutorialPromptBuilder(genre=genre)

        # Add lesson content
        try:
            concepts = json.loads(lesson.concepts_json) if lesson.concepts_json else []
        except json.JSONDecodeError:
            concepts = []

        builder.add_lesson_content(
            title=lesson.title,
            description=lesson.description,
            concepts=concepts,
            week_number=lesson.week_number,
            duration_minutes=lesson.estimated_duration_minutes,
            difficulty=getattr(lesson, 'difficulty', 'intermediate')
        )

        # Add student profile if available
        if user_skill_levels:
            builder.add_student_profile(
                skill_level=user_skill_levels.get('overall', 'intermediate'),
                technical_ability=user_skill_levels.get('technical_ability'),
                theory_knowledge=user_skill_levels.get('theory_knowledge'),
                rhythm_competency=user_skill_levels.get('rhythm_competency'),
                goals=user_skill_levels.get('goals', [])
            )

        # Add genre-specific guidance
        if genre:
            genre_guidance = self._get_genre_specific_guidance(genre)
            if genre_guidance:
                builder.add_custom_section("Genre-Specific Context", genre_guidance)

        # Build and return
        final_prompt = builder.build()

        # Log token estimate for monitoring
        token_estimate = builder.get_token_estimate()
        logger.debug(
            f"Built tutorial prompt",
            extra={
                "token_estimate": token_estimate,
                "lesson_id": lesson.id,
                "genre": genre
            }
        )

        return final_prompt

    def _get_genre_specific_guidance(self, genre: str) -> str:
        """Get additional genre-specific guidance for tutorials

        Args:
            genre: Musical genre

        Returns:
            Genre-specific guidance text
        """
        guidance_map = {
            "gospel": """
**Gospel Tutorial Focus:**
- Emphasize the "feeling" and spiritual context
- Reference Sunday morning worship applications
- Explain voicings in terms of emotional impact
- Connect technique to congregational support
- Use authentic gospel terminology (runs, shouts, Sunday morning sound)
            """,
            "jazz": """
**Jazz Tutorial Focus:**
- Reference jazz standards and recordings
- Explain historical context (bebop, modal, etc.)
- Connect to jazz tradition and lineage
- Use proper jazz terminology (comping, changes, guide tones)
- Include chord-scale relationships
            """,
            "blues": """
**Blues Tutorial Focus:**
- Emphasize feel, expression, and authenticity
- Reference blues legends and regional styles
- Explain "singing" on the piano
- Connect to emotion and personal expression
- Use blues terminology (blue note, shuffle, crushed note)
            """,
            "classical": """
**Classical Tutorial Focus:**
- Reference composers and period styles
- Emphasize proper technique and interpretation
- Include historical performance practice
- Use Italian/German musical terminology
- Connect to music theory and analysis
            """,
            "neosoul": """
**Neo-Soul Tutorial Focus:**
- Reference modern artists (D'Angelo, Glasper, etc.)
- Explain contemporary production context
- Emphasize groove, pocket, and laid-back feel
- Connect to hip-hop and R&B influences
- Use modern terminology (vamp, texture, Rhodes sound)
            """
        }

        return guidance_map.get(genre.lower(), "")

    def _validate_tutorial_structure(self, tutorial_data: Dict) -> Dict:
        """Validate tutorial has required structure

        Args:
            tutorial_data: Raw tutorial data

        Returns:
            Validated tutorial data
        """
        required_fields = ["overview", "concepts", "practice_steps", "encouragement"]

        # Ensure all required fields exist
        for field in required_fields:
            if field not in tutorial_data:
                logger.warning(f"Tutorial missing field: {field}")
                tutorial_data[field] = f"[Content for {field}]"

        return tutorial_data

    def _get_fallback_tutorial(self, lesson: CurriculumLesson) -> Dict:
        """Generate fallback tutorial when AI fails

        Args:
            lesson: CurriculumLesson model instance

        Returns:
            Basic tutorial structure
        """
        return {
            "overview": f"Welcome to {lesson.title}! In this lesson, we'll explore {lesson.description or 'important concepts'}.",
            "concepts": [
                "This lesson introduces core concepts that build on previous material.",
                "Practice each exercise slowly at first, then gradually increase tempo.",
                "Focus on accuracy and consistency before speed."
            ],
            "practice_steps": [
                "Review the exercises in order",
                "Practice hands separately first",
                "Gradually increase tempo as comfort improves",
                "Record yourself to track progress"
            ],
            "encouragement": "Keep practicing! Consistent effort leads to mastery."
        }


# Example usage in an API endpoint:
"""
from app.services.tutorial_service_enhanced import EnhancedTutorialService

tutorial_service = EnhancedTutorialService()

# Generate gospel tutorial
tutorial = await tutorial_service.generate_lesson_tutorial(
    lesson=lesson_instance,
    genre="gospel",
    user_skill_levels={
        "overall": "intermediate",
        "technical_ability": 6,
        "theory_knowledge": 5,
        "rhythm_competency": 7,
        "goals": ["Master gospel voicings", "Learn to comp in church"]
    }
)

# Tutorial contains rich, genre-authentic content
# If AI fails, users see template seamlessly (no error messages)
# Developers see full error chain in logs
"""
