"""Tutorial Generation Service

Generates comprehensive AI-powered tutorials for curriculum lessons.
Now using enhanced prompt architecture with genre-authentic system prompts
and silent fallback tracking.
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


class TutorialService:
    """Service for generating AI-powered lesson tutorials with genre authenticity"""

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
                Example: {
                    "overall": "intermediate",
                    "technical_ability": 6,
                    "theory_knowledge": 5,
                    "rhythm_competency": 7,
                    "goals": ["Master gospel voicings", "Learn runs"]
                }
            genre: Musical genre (gospel, jazz, blues, classical, neosoul)
                If None, defaults to "gospel" for backward compatibility

        Returns:
            Tutorial content dictionary with genre-authentic content
        """
        try:
            # Check if tutorial already exists
            if not force_regenerate and lesson.tutorial_content_json:
                existing_tutorial = json.loads(lesson.tutorial_content_json)
                if existing_tutorial:
                    logger.info(f"Using cached tutorial for lesson {lesson.id}")
                    return existing_tutorial

            # Default to gospel if no genre specified (backward compatibility)
            if genre is None:
                genre = "gospel"
                logger.debug(f"No genre specified, defaulting to gospel for lesson {lesson.id}")

            logger.info(
                f"Generating tutorial for lesson: {lesson.title} (genre: {genre})",
                extra={"lesson_id": lesson.id, "genre": genre}
            )

            # Build genre-authentic prompt using new architecture
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
                return_metadata=False  # Users see only content (silent fallback)
            )

            # Validate structure
            validated_tutorial = self._validate_tutorial_structure(tutorial_data)

            logger.info(
                f"Successfully generated tutorial for lesson {lesson.id}",
                extra={"genre": genre, "complexity": 7}
            )
            return validated_tutorial

        except Exception as e:
            logger.error(
                f"Failed to generate tutorial for lesson {lesson.id}: {e}",
                extra={"genre": genre, "error_type": type(e).__name__}
            )
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
        genre-aware prompt builder that includes authentic cultural context.

        Args:
            lesson: CurriculumLesson model instance
            user_skill_levels: Optional skill level dict
            genre: Musical genre (gospel, jazz, blues, classical, neosoul)

        Returns:
            Complete prompt string with genre-authentic context
        """
        # Initialize builder with genre context (includes genre-specific system prompt)
        builder = TutorialPromptBuilder(genre=genre)

        # Parse lesson content
        theory_content = {}
        concepts = []

        try:
            if lesson.theory_content_json:
                theory_content = json.loads(lesson.theory_content_json)
            if lesson.concepts_json:
                concepts = json.loads(lesson.concepts_json)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse lesson content JSON for lesson {lesson.id}")

        # Add lesson content
        builder.add_lesson_content(
            title=lesson.title,
            description=lesson.description,
            concepts=concepts,
            week_number=lesson.week_number,
            duration_minutes=lesson.estimated_duration_minutes,
            difficulty="intermediate"  # Could be dynamic based on lesson
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

        # Add output format specification
        builder.add_output_format(
            "JSON",
            schema={
                "overview": "Learning objectives, outcomes, duration, difficulty",
                "theory": "Summary, key points, examples, notation tips",
                "demonstration": "Description, example progressions, exercises, visual aids",
                "practice_guide": "Warm-up, detailed steps, cool-down",
                "tips_and_tricks": "Category, tip, why it helps",
                "common_mistakes": "Mistake, why it happens, fix, prevention",
                "next_steps": "Preview, optional practice, resources"
            }
        )

        # Add genre-specific guidance
        if genre:
            genre_guidance = self._get_genre_specific_guidance(genre)
            if genre_guidance:
                builder.add_custom_section("Genre-Specific Tutorial Focus", genre_guidance)

        # Add theory content context if available
        if theory_content:
            theory_text = json.dumps(theory_content, indent=2)
            builder.add_custom_section(
                "Theory Content Context",
                f"Reference this theory content when creating the tutorial:\n{theory_text}"
            )

        # Build and return
        final_prompt = builder.build()

        # Log token estimate for monitoring
        token_estimate = builder.get_token_estimate()
        logger.debug(
            f"Built tutorial prompt",
            extra={
                "token_estimate": token_estimate,
                "lesson_id": lesson.id,
                "genre": genre,
                "has_user_profile": user_skill_levels is not None
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
- Emphasize the "feeling" and spiritual context
- Reference Sunday morning worship applications
- Explain voicings in terms of emotional impact
- Connect technique to congregational support
- Use authentic gospel terminology (runs, shouts, Sunday morning sound)
- Suggest listening to contemporary gospel artists
            """,
            "jazz": """
- Reference jazz standards and specific recordings
- Explain historical context (bebop, modal, contemporary)
- Connect to jazz tradition and lineage
- Use proper jazz terminology (comping, changes, guide tones)
- Include chord-scale relationships
- Suggest listening to classic jazz recordings
            """,
            "blues": """
- Emphasize feel, expression, and authenticity
- Reference blues legends and regional styles (Delta, Chicago, Texas)
- Explain "singing" on the piano
- Connect to emotion and personal expression
- Use blues terminology (blue note, shuffle, crushed note)
- Suggest listening to blues masters
            """,
            "classical": """
- Reference composers and period styles (Baroque, Classical, Romantic)
- Emphasize proper technique and interpretation
- Include historical performance practice
- Use Italian/German musical terminology
- Connect to music theory and analysis
- Suggest score study and listening examples
            """,
            "neosoul": """
- Reference modern artists (D'Angelo, Robert Glasper, Erykah Badu, H.E.R.)
- Explain contemporary production context
- Emphasize groove, pocket, and laid-back feel
- Connect to hip-hop and R&B influences
- Use modern terminology (vamp, texture, Rhodes sound)
- Suggest listening to contemporary neo-soul artists
            """
        }

        return guidance_map.get(genre.lower(), "")

    def _validate_tutorial_structure(self, tutorial_data: Dict) -> Dict:
        """Validate and ensure tutorial has required structure

        Args:
            tutorial_data: Raw tutorial data from AI

        Returns:
            Validated tutorial dictionary
        """
        required_sections = [
            "overview", "theory", "demonstration",
            "practice_guide", "tips_and_tricks",
            "common_mistakes", "next_steps"
        ]

        # Ensure all required sections exist
        for section in required_sections:
            if section not in tutorial_data:
                logger.warning(f"Missing section: {section}, adding default")
                tutorial_data[section] = self._get_default_section(section)

        # Validate overview
        if "what_you_will_learn" not in tutorial_data.get("overview", {}):
            tutorial_data.setdefault("overview", {})["what_you_will_learn"] = []
        if "learning_outcomes" not in tutorial_data.get("overview", {}):
            tutorial_data["overview"]["learning_outcomes"] = []

        # Validate theory
        if "summary" not in tutorial_data.get("theory", {}):
            tutorial_data.setdefault("theory", {})["summary"] = ""
        if "key_points" not in tutorial_data.get("theory", {}):
            tutorial_data["theory"]["key_points"] = []

        # Validate practice guide
        if "steps" not in tutorial_data.get("practice_guide", {}):
            tutorial_data.setdefault("practice_guide", {})["steps"] = []

        return tutorial_data

    def _get_default_section(self, section_name: str) -> Dict:
        """Get default content for a missing section

        Args:
            section_name: Name of the section

        Returns:
            Default section content
        """
        defaults = {
            "overview": {
                "what_you_will_learn": [],
                "learning_outcomes": [],
                "duration_minutes": 60,
                "difficulty": "intermediate"
            },
            "theory": {
                "summary": "",
                "key_points": [],
                "examples": [],
                "notation_tips": []
            },
            "demonstration": {
                "description": "",
                "example_progressions": [],
                "reference_exercises": [],
                "visual_aids": []
            },
            "practice_guide": {
                "warm_up": [],
                "steps": [],
                "cool_down": []
            },
            "tips_and_tricks": [],
            "common_mistakes": [],
            "next_steps": {
                "preview": "",
                "optional_practice": [],
                "resources": []
            }
        }

        return defaults.get(section_name, {})

    def _get_fallback_tutorial(self, lesson: CurriculumLesson) -> Dict:
        """Generate a basic fallback tutorial when AI fails

        Args:
            lesson: CurriculumLesson model instance

        Returns:
            Basic tutorial structure
        """
        return {
            "overview": {
                "what_you_will_learn": [f"Study {lesson.title}"],
                "learning_outcomes": ["Complete lesson exercises"],
                "duration_minutes": lesson.estimated_duration_minutes,
                "difficulty": "intermediate"
            },
            "theory": {
                "summary": lesson.description or f"This lesson covers {lesson.title}",
                "key_points": [],
                "examples": [],
                "notation_tips": []
            },
            "demonstration": {
                "description": "Practice the exercises provided",
                "example_progressions": [],
                "reference_exercises": [],
                "visual_aids": []
            },
            "practice_guide": {
                "warm_up": ["Scales and arpeggios in the lesson key"],
                "steps": [
                    {
                        "step": 1,
                        "title": "Review theory",
                        "instruction": "Study the lesson concepts",
                        "duration_minutes": 15,
                        "success_criteria": "Understand core concepts",
                        "common_challenges": "Complex theory"
                    },
                    {
                        "step": 2,
                        "title": "Practice exercises",
                        "instruction": "Work through each exercise slowly",
                        "duration_minutes": 30,
                        "success_criteria": "Play exercises correctly at slow tempo",
                        "common_challenges": "Technical difficulty"
                    }
                ],
                "cool_down": ["Play through exercises at comfortable tempo"]
            },
            "tips_and_tricks": [],
            "common_mistakes": [],
            "next_steps": {
                "preview": "Continue to the next lesson",
                "optional_practice": [],
                "resources": []
            }
        }


# Singleton instance
tutorial_service = TutorialService()
