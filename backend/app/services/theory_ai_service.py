"""
Theory AI Service

AI-powered theory explanations using multi-model LLM.
Integrates theory library with AI orchestrator for intelligent,
student-friendly music theory explanations.

Complexity Routing:
- Simple explanations (4-5): Phi-3.5 Mini
- Detailed theory explanations (5-6): Qwen2.5-7B
- Complex analysis (7-8): Qwen2.5-7B or Gemini Pro
"""

import logging
from typing import Any, Dict, List, Optional

from app.services.ai_orchestrator import ai_orchestrator, TaskType
from app.services.multi_model_service import multi_model_service

logger = logging.getLogger(__name__)


class TheoryAIService:
    """
    AI service for music theory explanations and analysis.

    Uses multi-model LLM with complexity routing for:
    - Student-friendly theory explanations
    - Practice exercise generation
    - Substitution analysis
    - Voice leading feedback
    """

    def __init__(self):
        self.ai_orchestrator = ai_orchestrator
        self.multi_llm = multi_model_service

    async def explain_neo_riemannian(
        self,
        transformation: str,
        from_chord: str,
        to_chord: str,
        student_level: str = "intermediate",
        voice_moved: str = "",
        semitones_moved: int = 0
    ) -> Dict[str, Any]:
        """
        Generate student-friendly PLR transformation explanation.

        Complexity 5-6: Routes to Qwen2.5-7B for detailed music theory

        Args:
            transformation: 'P', 'L', or 'R'
            from_chord: Starting chord (e.g., "Cmaj")
            to_chord: Resulting chord (e.g., "Cmin")
            student_level: "beginner", "intermediate", or "advanced"
            voice_moved: Which voice moved (e.g., "third")
            semitones_moved: How many semitones

        Returns:
            Dict with explanation text and key points
        """
        transformation_names = {
            'P': 'Parallel',
            'L': 'Leading-tone',
            'R': 'Relative'
        }

        transformation_name = transformation_names.get(transformation.upper(), transformation)

        prompt = f"""You are an expert music theory teacher. Explain the {transformation_name} ({transformation}) transformation to a {student_level} music student.

**Transformation:** {from_chord} → {to_chord}
**Voice Moved:** {voice_moved} (moved {semitones_moved} semitones)

Provide a clear, educational explanation that includes:

1. **What Changed**: Describe which note in the chord changed
2. **Voice Leading**: Explain why this creates smooth voice leading
3. **Musical Context**: Give 1-2 examples of where this transformation appears in real music
4. **Practice Tip**: One actionable practice suggestion

Keep your tone conversational and encouraging. Use analogies if helpful.
Write 3-4 sentences total."""

        try:
            response = await self.ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.THEORY_ANALYSIS,  # Complexity 5
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 512,
                    "response_mime_type": "text/plain",
                },
                cache_ttl_hours=24
            )

            explanation = response if isinstance(response, str) else response.get("text", "")

            return {
                "explanation": explanation,
                "transformation": transformation_name,
                "from_chord": from_chord,
                "to_chord": to_chord,
                "key_points": [
                    f"{voice_moved.title()} moves {semitones_moved} semitones",
                    "Creates parsimonious voice leading" if semitones_moved <= 2 else "Non-parsimonious transformation",
                    f"Common in {student_level} level repertoire"
                ]
            }

        except Exception as e:
            logger.error(f"Neo-Riemannian explanation failed: {e}")
            return {
                "explanation": f"The {transformation_name} transformation changes the {voice_moved} by {semitones_moved} semitones, creating smooth voice leading between {from_chord} and {to_chord}.",
                "transformation": transformation_name,
                "from_chord": from_chord,
                "to_chord": to_chord,
                "key_points": []
            }

    async def explain_negative_harmony(
        self,
        original_progression: List[str],
        negative_progression: List[str],
        key: str,
        student_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Explain negative harmony concept with musical context.

        Complexity 6-7: Routes to Qwen2.5-7B for detailed explanation

        Args:
            original_progression: Original chord progression
            negative_progression: Negative harmony version
            key: Key center
            student_level: Student proficiency level

        Returns:
            Dict with explanation and examples
        """
        original_str = " → ".join(original_progression)
        negative_str = " → ".join(negative_progression)

        prompt = f"""You are an expert music theory teacher explaining negative harmony to a {student_level} student.

**Key:** {key}
**Original Progression:** {original_str}
**Negative Harmony:** {negative_str}

Explain negative harmony in a way that:

1. **Core Concept**: What negative harmony is (axis of reflection between tonic and subdominant)
2. **Why These Chords**: Why these specific chords are the negative equivalents
3. **Musical Effect**: How it creates a similar yet fresh harmonic feeling
4. **Famous Example**: Mention Jacob Collier or other artist who uses this technique

Keep it educational, conversational, and inspiring.
Write 4-5 sentences."""

        try:
            response = await self.ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.THEORY_ANALYSIS,  # Complexity 5
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                    "response_mime_type": "text/plain",
                },
                cache_ttl_hours=24
            )

            explanation = response if isinstance(response, str) else response.get("text", "")

            return {
                "explanation": explanation,
                "original_progression": original_progression,
                "negative_progression": negative_progression,
                "key": key,
                "concepts": [
                    "Axis of reflection",
                    "Mirror-image harmonic relationships",
                    "Popularized by Jacob Collier"
                ]
            }

        except Exception as e:
            logger.error(f"Negative harmony explanation failed: {e}")
            return {
                "explanation": f"Negative harmony creates mirror-image chord relationships around a central axis in {key}. The progression {original_str} becomes {negative_str}, maintaining similar harmonic function with a fresh sound.",
                "original_progression": original_progression,
                "negative_progression": negative_progression,
                "key": key,
                "concepts": []
            }

    async def explain_coltrane_changes(
        self,
        progression: List[str],
        target_key: str,
        student_level: str = "advanced"
    ) -> Dict[str, Any]:
        """
        Explain Giant Steps harmonic movement (Coltrane Changes).

        Complexity 7-8: Routes to Qwen2.5-7B or Gemini Pro

        Args:
            progression: The Coltrane changes progression
            target_key: Target key
            student_level: Student proficiency level

        Returns:
            Dict with detailed explanation
        """
        progression_str = " → ".join(progression)

        prompt = f"""You are an expert jazz theory teacher explaining Coltrane Changes to an {student_level} student.

**Progression:** {progression_str}
**Target Key:** {target_key}

Provide a comprehensive explanation that covers:

1. **What It Is**: Definition of Coltrane Changes (Giant Steps pattern)
2. **Harmonic Structure**: How it moves through three tonal centers separated by major thirds
3. **Why It's Complex**: What makes this progression challenging
4. **Practice Strategy**: One specific practice approach for mastering this progression
5. **Historical Context**: John Coltrane's "Giant Steps" and why it was revolutionary

Be detailed but clear. Use technical terms but explain them.
Write 5-6 sentences."""

        try:
            response = await self.ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.THEORY_ANALYSIS,  # Complexity 5 (will route appropriately)
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                    "response_mime_type": "text/plain",
                },
                cache_ttl_hours=24
            )

            explanation = response if isinstance(response, str) else response.get("text", "")

            return {
                "explanation": explanation,
                "progression": progression,
                "target_key": target_key,
                "concepts": [
                    "Three tonal centers (major thirds apart)",
                    "Dominant preparation for each center",
                    "Rapid harmonic movement",
                    "John Coltrane's innovation"
                ]
            }

        except Exception as e:
            logger.error(f"Coltrane Changes explanation failed: {e}")
            return {
                "explanation": f"Coltrane Changes move through three tonal centers separated by major thirds, creating rapid harmonic movement. The progression {progression_str} demonstrates this technique, targeting {target_key}.",
                "progression": progression,
                "target_key": target_key,
                "concepts": []
            }

    async def suggest_practice_exercises(
        self,
        theory_concept: str,
        current_skill_level: float,
        student_goals: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate practice exercises for a theory concept.

        Complexity 5: Routes to Qwen2.5-7B

        Args:
            theory_concept: Theory concept to practice (e.g., "neo_riemannian", "negative_harmony")
            current_skill_level: Student's current skill (0-10)
            student_goals: List of student goals

        Returns:
            List of practice exercises with instructions
        """
        goals_str = ", ".join(student_goals)

        prompt = f"""You are a music pedagogy expert creating practice exercises.

**Theory Concept:** {theory_concept}
**Student Skill Level:** {current_skill_level}/10
**Student Goals:** {goals_str}

Generate 3 progressive practice exercises that:
1. Start at the student's current level
2. Build toward their goals
3. Are specific and actionable
4. Include success criteria

For each exercise, provide:
- Title
- Description (1-2 sentences)
- Time estimate (minutes)
- Success criteria

Return as JSON:
{{
  "exercises": [
    {{
      "title": "Exercise title",
      "description": "What to practice",
      "duration_minutes": 10,
      "success_criteria": "How to know you've mastered it"
    }}
  ]
}}"""

        try:
            response = await self.ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.EXERCISE_GENERATION,  # Complexity 4
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 1024,
                    "response_mime_type": "application/json",
                },
                cache_ttl_hours=1  # Short cache for personalized content
            )

            if isinstance(response, dict) and "exercises" in response:
                return response["exercises"]
            else:
                return []

        except Exception as e:
            logger.error(f"Practice exercise generation failed: {e}")
            return [
                {
                    "title": f"Explore {theory_concept}",
                    "description": "Practice applying this concept in different keys",
                    "duration_minutes": 15,
                    "success_criteria": "Comfortable using concept in at least 3 different keys"
                }
            ]

    async def analyze_student_substitution(
        self,
        student_chord: str,
        expected_chord: str,
        progression_context: List[str],
        key: str
    ) -> Dict[str, Any]:
        """
        Analyze if student used a valid substitution.

        Complexity 4-5: Routes to Qwen2.5-7B

        Args:
            student_chord: What the student played
            expected_chord: What was expected
            progression_context: Surrounding chords
            key: Key center

        Returns:
            Analysis of the substitution validity and creativity
        """
        context_str = " → ".join(progression_context)

        prompt = f"""You are a music theory expert analyzing a student's chord choice.

**Expected Chord:** {expected_chord}
**Student Played:** {student_chord}
**Progression Context:** {context_str}
**Key:** {key}

Analyze whether the student's substitution is:
1. **Valid**: Does it fit harmonically?
2. **Creative**: Is it an interesting choice?
3. **Appropriate**: Does it fit the style?

Provide:
- Validity score (0-10)
- Creativity score (0-10)
- Brief explanation (2-3 sentences)
- Substitution type if applicable (e.g., "tritone substitution", "modal interchange")

Return as JSON:
{{
  "is_valid": true/false,
  "validity_score": 0-10,
  "creativity_score": 0-10,
  "substitution_type": "type name or null",
  "explanation": "Brief explanation"
}}"""

        try:
            response = await self.ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.CONTENT_VALIDATION,  # Complexity 3
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": 512,
                    "response_mime_type": "application/json",
                },
                cache_ttl_hours=0  # No cache for performance analysis
            )

            if isinstance(response, dict):
                return response
            else:
                return {
                    "is_valid": True,
                    "validity_score": 5,
                    "creativity_score": 5,
                    "substitution_type": None,
                    "explanation": "Analyzing substitution..."
                }

        except Exception as e:
            logger.error(f"Substitution analysis failed: {e}")
            return {
                "is_valid": True,
                "validity_score": 5,
                "creativity_score": 5,
                "substitution_type": None,
                "explanation": "Unable to analyze substitution at this time."
            }

    async def generate_theory_tutorial(
        self,
        theory_topic: str,
        student_level: str,
        learning_goals: List[str]
    ) -> str:
        """
        Generate comprehensive tutorial on a theory topic.

        Complexity 6-7: Routes to Qwen2.5-7B

        Args:
            theory_topic: Theory topic to explain
            student_level: Student proficiency level
            learning_goals: What student wants to achieve

        Returns:
            Tutorial text (markdown formatted)
        """
        goals_str = "\n".join([f"- {goal}" for goal in learning_goals])

        prompt = f"""You are an expert music theory educator writing a tutorial.

**Topic:** {theory_topic}
**Student Level:** {student_level}
**Learning Goals:**
{goals_str}

Write a comprehensive tutorial (400-600 words) that:

1. **Introduction**: Hook the student with why this topic matters
2. **Core Concepts**: Explain the fundamental concepts clearly
3. **Examples**: Provide 2-3 concrete musical examples
4. **Practice Application**: How to apply this in practice
5. **Next Steps**: What to explore next

Use:
- Clear, conversational language
- Analogies where helpful
- Encouraging tone
- Markdown formatting for structure

Write the tutorial now:"""

        try:
            response = await self.ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.TUTORIAL_GENERATION,  # Complexity 7
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 2048,
                    "response_mime_type": "text/plain",
                },
                cache_ttl_hours=168  # 1 week cache for tutorials
            )

            return response if isinstance(response, str) else response.get("text", "Tutorial generation in progress...")

        except Exception as e:
            logger.error(f"Tutorial generation failed: {e}")
            return f"# {theory_topic}\n\nWelcome to this lesson on {theory_topic}! This is an advanced music theory concept that will expand your harmonic understanding.\n\nLet's explore this concept together through practice and experimentation."


# Global service instance
theory_ai_service = TheoryAIService()
