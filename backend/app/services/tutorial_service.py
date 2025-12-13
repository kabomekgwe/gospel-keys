"""Tutorial Generation Service

Generates comprehensive AI-powered tutorials for curriculum lessons.
Uses Gemini Pro/Ultra for high-quality educational content.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional

from app.database.curriculum_models import CurriculumLesson
from app.services.ai_orchestrator import ai_orchestrator, TaskType
from app.core.config import settings

logger = logging.getLogger(__name__)


class TutorialService:
    """Service for generating AI-powered lesson tutorials"""

    def __init__(self):
        self.cache_ttl_hours = 720  # 30 days

    async def generate_lesson_tutorial(
        self,
        lesson: CurriculumLesson,
        force_regenerate: bool = False
    ) -> Dict:
        """Generate comprehensive tutorial for a lesson

        Args:
            lesson: CurriculumLesson model instance
            force_regenerate: Regenerate even if tutorial exists

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

            logger.info(f"Generating tutorial for lesson: {lesson.title}")

            # Build AI prompt
            prompt = self._build_tutorial_prompt(lesson)

            # Generate using AI orchestrator
            tutorial_data = await ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.TUTORIAL_GENERATION,
                generation_config={
                    "temperature": 0.7,  # Creative but structured
                    "max_output_tokens": 4096,
                },
                cache_ttl_hours=self.cache_ttl_hours
            )

            # Validate structure
            validated_tutorial = self._validate_tutorial_structure(tutorial_data)

            logger.info(f"Successfully generated tutorial for lesson {lesson.id}")
            return validated_tutorial

        except Exception as e:
            logger.error(f"Failed to generate tutorial for lesson {lesson.id}: {e}")
            # Return fallback template
            return self._get_fallback_tutorial(lesson)

    def _build_tutorial_prompt(self, lesson: CurriculumLesson) -> str:
        """Build AI prompt for tutorial generation

        Args:
            lesson: CurriculumLesson model instance

        Returns:
            Formatted prompt string
        """
        # Parse lesson content
        theory_content = {}
        concepts = []

        try:
            theory_content = json.loads(lesson.theory_content_json)
            concepts = json.loads(lesson.concepts_json)
        except json.JSONDecodeError:
            pass

        # Build prompt
        prompt = f"""Generate a comprehensive piano lesson tutorial in JSON format.

Lesson Information:
- Title: {lesson.title}
- Description: {lesson.description or 'Not provided'}
- Week Number: {lesson.week_number}
- Duration: {lesson.estimated_duration_minutes} minutes
- Theory Content: {json.dumps(theory_content, indent=2)}
- Key Concepts: {json.dumps(concepts, indent=2)}

Generate a detailed tutorial with the following JSON structure:

{{
  "overview": {{
    "what_you_will_learn": ["list of 3-5 learning objectives"],
    "learning_outcomes": ["list of 3-5 expected outcomes"],
    "duration_minutes": {lesson.estimated_duration_minutes},
    "difficulty": "beginner|intermediate|advanced"
  }},
  "theory": {{
    "summary": "2-3 paragraph explanation of the theory",
    "key_points": ["list of 5-7 key theoretical points"],
    "examples": ["list of 3-5 musical examples with explanations"],
    "notation_tips": ["list of 3-5 notation reading tips"]
  }},
  "demonstration": {{
    "description": "Detailed description of what to demonstrate",
    "example_progressions": ["list of 2-3 chord progressions to demonstrate"],
    "reference_exercises": ["list of exercise titles from this lesson"],
    "visual_aids": ["list of suggested diagrams or visual aids"]
  }},
  "practice_guide": {{
    "warm_up": ["list of 2-3 warm-up activities"],
    "steps": [
      {{
        "step": 1,
        "title": "Step title",
        "instruction": "Detailed instruction",
        "duration_minutes": 5,
        "success_criteria": "How to know you've mastered this step",
        "common_challenges": "Potential difficulties"
      }}
    ],
    "cool_down": ["list of 1-2 cool-down activities"]
  }},
  "tips_and_tricks": [
    {{
      "category": "technique|theory|practice|performance",
      "tip": "Specific actionable tip",
      "why_it_helps": "Explanation of benefit"
    }}
  ],
  "common_mistakes": [
    {{
      "mistake": "Description of common error",
      "why_it_happens": "Explanation of cause",
      "fix": "How to correct it",
      "prevention": "How to avoid it"
    }}
  ],
  "next_steps": {{
    "preview": "Preview of what comes next in the curriculum",
    "optional_practice": ["list of 2-3 optional exercises for advanced students"],
    "resources": ["list of 2-3 recommended resources"]
  }}
}}

Focus on Gospel piano style. Make instructions clear, actionable, and encouraging.
Ensure all JSON is valid and properly formatted.
"""

        return prompt

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
        if "what_you_will_learn" not in tutorial_data["overview"]:
            tutorial_data["overview"]["what_you_will_learn"] = []
        if "learning_outcomes" not in tutorial_data["overview"]:
            tutorial_data["overview"]["learning_outcomes"] = []

        # Validate theory
        if "summary" not in tutorial_data["theory"]:
            tutorial_data["theory"]["summary"] = ""
        if "key_points" not in tutorial_data["theory"]:
            tutorial_data["theory"]["key_points"] = []

        # Validate practice guide
        if "steps" not in tutorial_data["practice_guide"]:
            tutorial_data["practice_guide"]["steps"] = []

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
