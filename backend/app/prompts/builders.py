"""Prompt Builder Utilities

Helper classes for constructing optimized prompts with rich context
while maintaining clarity and structure.
"""

from typing import Any, Dict, List, Optional
from .system_prompts import get_system_prompt


class PromptBuilder:
    """Fluent builder for constructing rich, structured prompts

    Supports quality-over-brevity approach with organized sections.
    """

    def __init__(self, task_type: str, genre: Optional[str] = None):
        """Initialize prompt builder

        Args:
            task_type: Type of task (tutorial, feedback, exercise, curriculum)
            genre: Musical genre for context
        """
        self.task_type = task_type
        self.genre = genre
        self.sections: List[str] = []

        # Add system prompt as foundation
        system_prompt = get_system_prompt(task_type, genre, include_genre=True)
        if system_prompt:
            self.sections.append(system_prompt)

    def add_context(self, title: str, content: Dict[str, Any]) -> "PromptBuilder":
        """Add contextual information section

        Args:
            title: Section title
            content: Dictionary of key-value pairs

        Returns:
            Self for chaining
        """
        section = f"## {title}\n"
        for key, value in content.items():
            # Format key nicely (snake_case -> Title Case)
            formatted_key = key.replace("_", " ").title()
            section += f"- **{formatted_key}**: {value}\n"

        self.sections.append(section)
        return self

    def add_student_profile(
        self,
        skill_level: str,
        technical_ability: Optional[int] = None,
        theory_knowledge: Optional[int] = None,
        rhythm_competency: Optional[int] = None,
        goals: Optional[List[str]] = None
    ) -> "PromptBuilder":
        """Add student profile context

        Args:
            skill_level: Beginner, intermediate, advanced
            technical_ability: 1-10 rating
            theory_knowledge: 1-10 rating
            rhythm_competency: 1-10 rating
            goals: List of learning goals

        Returns:
            Self for chaining
        """
        profile = f"## Student Profile\n"
        profile += f"- **Skill Level**: {skill_level}\n"

        if technical_ability is not None:
            profile += f"- **Technical Ability**: {technical_ability}/10\n"
        if theory_knowledge is not None:
            profile += f"- **Theory Knowledge**: {theory_knowledge}/10\n"
        if rhythm_competency is not None:
            profile += f"- **Rhythm Competency**: {rhythm_competency}/10\n"

        if goals:
            profile += f"\n**Learning Goals**:\n"
            for goal in goals:
                profile += f"- {goal}\n"

        self.sections.append(profile)
        return self

    def add_performance_data(
        self,
        pitch_accuracy: Optional[float] = None,
        rhythm_accuracy: Optional[float] = None,
        tempo_stability: Optional[float] = None,
        dynamics_range: Optional[float] = None,
        common_errors: Optional[Dict[str, List[str]]] = None
    ) -> "PromptBuilder":
        """Add performance analysis data

        Args:
            pitch_accuracy: Percentage (0-100)
            rhythm_accuracy: Percentage (0-100)
            tempo_stability: Percentage (0-100)
            dynamics_range: dB range
            common_errors: Dict of error categories and lists

        Returns:
            Self for chaining
        """
        section = f"## Performance Analysis\n"

        if pitch_accuracy is not None:
            section += f"- **Pitch Accuracy**: {pitch_accuracy:.1f}%\n"
        if rhythm_accuracy is not None:
            section += f"- **Rhythm Accuracy**: {rhythm_accuracy:.1f}%\n"
        if tempo_stability is not None:
            section += f"- **Tempo Stability**: {tempo_stability:.1f}%\n"
        if dynamics_range is not None:
            section += f"- **Dynamic Range**: {dynamics_range:.1f} dB\n"

        if common_errors:
            section += f"\n**Common Errors**:\n"
            for category, errors in common_errors.items():
                category_name = category.replace("_", " ").title()
                if errors:
                    section += f"- **{category_name}**: {', '.join(errors)}\n"
                else:
                    section += f"- **{category_name}**: None detected\n"

        self.sections.append(section)
        return self

    def add_lesson_content(
        self,
        title: str,
        description: Optional[str] = None,
        concepts: Optional[List[str]] = None,
        week_number: Optional[int] = None,
        duration_minutes: Optional[int] = None,
        difficulty: Optional[str] = None
    ) -> "PromptBuilder":
        """Add lesson content information

        Args:
            title: Lesson title
            description: Lesson description
            concepts: List of key concepts
            week_number: Week in curriculum
            duration_minutes: Estimated practice duration
            difficulty: Difficulty level

        Returns:
            Self for chaining
        """
        section = f"## Lesson Content\n"
        section += f"- **Title**: {title}\n"

        if description:
            section += f"- **Description**: {description}\n"
        if week_number is not None:
            section += f"- **Week**: {week_number}\n"
        if duration_minutes is not None:
            section += f"- **Duration**: {duration_minutes} minutes\n"
        if difficulty:
            section += f"- **Difficulty**: {difficulty}\n"

        if concepts:
            section += f"\n**Key Concepts**:\n"
            for concept in concepts:
                section += f"- {concept}\n"

        self.sections.append(section)
        return self

    def add_requirements(self, requirements: List[str]) -> "PromptBuilder":
        """Add specific requirements or constraints

        Args:
            requirements: List of requirement strings

        Returns:
            Self for chaining
        """
        section = f"## Requirements\n"
        for i, req in enumerate(requirements, 1):
            section += f"{i}. {req}\n"

        self.sections.append(section)
        return self

    def add_output_format(
        self,
        format_type: str,
        schema: Optional[Dict[str, str]] = None
    ) -> "PromptBuilder":
        """Add output format specification

        Args:
            format_type: "JSON", "Markdown", "Plain text"
            schema: Dictionary of field names and descriptions

        Returns:
            Self for chaining
        """
        section = f"## Output Format\n"
        section += f"Return response as **{format_type}**.\n"

        if schema:
            section += f"\n**Required fields**:\n"
            for field, description in schema.items():
                section += f"- `{field}`: {description}\n"

        self.sections.append(section)
        return self

    def add_examples(self, examples: List[Dict[str, str]]) -> "PromptBuilder":
        """Add example inputs and outputs

        Args:
            examples: List of dicts with 'input' and 'output' keys

        Returns:
            Self for chaining
        """
        section = f"## Examples\n"

        for i, example in enumerate(examples, 1):
            section += f"\n**Example {i}**:\n"
            if "input" in example:
                section += f"Input: {example['input']}\n"
            if "output" in example:
                section += f"Output: {example['output']}\n"

        self.sections.append(section)
        return self

    def add_custom_section(self, title: str, content: str) -> "PromptBuilder":
        """Add custom section with any content

        Args:
            title: Section title
            content: Section content (markdown supported)

        Returns:
            Self for chaining
        """
        section = f"## {title}\n{content}\n"
        self.sections.append(section)
        return self

    def build(self) -> str:
        """Build final prompt string

        Returns:
            Complete prompt with all sections joined
        """
        return "\n\n".join(self.sections)

    def get_token_estimate(self) -> int:
        """Estimate token count (rough approximation)

        Returns:
            Approximate token count (chars / 4)
        """
        full_prompt = self.build()
        # Rough estimate: 1 token ≈ 4 characters for English
        return len(full_prompt) // 4


# =============================================================================
# SPECIALIZED BUILDERS (Convenience Factories)
# =============================================================================

class TutorialPromptBuilder(PromptBuilder):
    """Specialized builder for tutorial generation"""

    def __init__(self, genre: Optional[str] = None):
        super().__init__(task_type="tutorial", genre=genre)

        # Add tutorial-specific requirements by default
        self.add_requirements([
            "Structure: Welcome → Core Concepts → Practice Guidance → Encouragement",
            "Length: 400-600 words (comprehensive but focused)",
            "Tone: Warm, encouraging, specific (no generic praise)",
            "Include: Why concepts matter, specific practice tips",
            "Avoid: Condescending language, overwhelming detail"
        ])


class FeedbackPromptBuilder(PromptBuilder):
    """Specialized builder for feedback generation"""

    def __init__(self, genre: Optional[str] = None):
        super().__init__(task_type="feedback", genre=genre)

        # Add feedback-specific output format
        self.add_output_format(
            "JSON",
            schema={
                "overall_score": "0-100 performance score",
                "summary": "2-3 sentence overview",
                "strengths": "List of 2-3 specific strengths",
                "areas_to_improve": "List of 2-3 prioritized improvements with suggestions",
                "practice_exercises": "List of 1-3 targeted exercises",
                "encouragement": "Motivational closing message"
            }
        )


class ExercisePromptBuilder(PromptBuilder):
    """Specialized builder for exercise generation"""

    def __init__(self, genre: Optional[str] = None):
        super().__init__(task_type="exercise", genre=genre)

        # Add exercise-specific requirements
        self.add_requirements([
            "Must be playable at target skill level",
            "Genre-authentic (use proper voicings and feel)",
            "Include tempo guidance (start slow, build speed)",
            "Provide specific practice tips",
            "Balance technical challenge with musicality"
        ])


class CurriculumPromptBuilder(PromptBuilder):
    """Specialized builder for curriculum planning"""

    def __init__(self, genre: Optional[str] = None):
        super().__init__(task_type="curriculum", genre=genre)

        # Add curriculum-specific structure
        self.add_requirements([
            "Progressive skill building (start where student is)",
            "Comprehensive development (technique, theory, rhythm, ear, expression)",
            "Structure: Modules (3-6 weeks) → Lessons (1 week) → Exercises (3-7 per lesson)",
            "Exercise distribution: 40% technical, 30% musical, 20% ear, 10% creative",
            "Realistic time commitments and clear success metrics"
        ])
