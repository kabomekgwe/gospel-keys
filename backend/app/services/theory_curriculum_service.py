"""
Theory Curriculum Service

Generates progressive theory curriculum paths with:
- Structured learning progression (beginner → intermediate → advanced)
- Theory-specific modules and lessons
- AI-generated tutorial content
- Interactive exercises using theory library
- Genre-specific application examples
- Assessments to validate knowledge
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.ai_orchestrator import ai_orchestrator, TaskType
from app.theory import (
    chord_substitutions,
    voice_leading_neo_riemannian,
    voice_leading_optimization
)

logger = logging.getLogger(__name__)


class TheoryCurriculumService:
    """
    Generates theory-focused curriculum paths with progressive difficulty.

    Organizes theory education into:
    - Beginner: Fundamentals (intervals, scales, triads)
    - Intermediate: Extended harmony (7th chords, modes, voice leading)
    - Advanced: Complex theory (Neo-Riemannian, negative harmony, Coltrane changes)
    """

    # Theory progression map
    THEORY_PROGRESSION = {
        'beginner': [
            'intervals',
            'major_minor_scales',
            'triads',
            'basic_progressions',
            'chord_inversions',
            'simple_voice_leading'
        ],
        'intermediate': [
            'seventh_chords',
            'modes',
            'extended_chords',
            'modal_interchange',
            'diatonic_substitution',
            'voice_leading_rules'
        ],
        'advanced': [
            'neo_riemannian_theory',
            'negative_harmony',
            'coltrane_changes',
            'barry_harris_diminished',
            'advanced_substitutions',
            'voice_leading_optimization'
        ]
    }

    # Topic metadata
    TOPIC_METADATA = {
        'intervals': {
            'name': 'Intervals',
            'description': 'Understanding musical distances between notes',
            'prerequisites': [],
            'difficulty': 'beginner',
            'estimated_hours': 2
        },
        'major_minor_scales': {
            'name': 'Major and Minor Scales',
            'description': 'The foundation of Western music',
            'prerequisites': ['intervals'],
            'difficulty': 'beginner',
            'estimated_hours': 3
        },
        'triads': {
            'name': 'Triads',
            'description': 'Building three-note chords',
            'prerequisites': ['major_minor_scales', 'intervals'],
            'difficulty': 'beginner',
            'estimated_hours': 2
        },
        'basic_progressions': {
            'name': 'Basic Chord Progressions',
            'description': 'Common harmonic sequences (I-IV-V, ii-V-I)',
            'prerequisites': ['triads'],
            'difficulty': 'beginner',
            'estimated_hours': 3
        },
        'chord_inversions': {
            'name': 'Chord Inversions',
            'description': 'Different voicings of the same chord',
            'prerequisites': ['triads'],
            'difficulty': 'beginner',
            'estimated_hours': 2
        },
        'simple_voice_leading': {
            'name': 'Simple Voice Leading',
            'description': 'Smooth transitions between chords',
            'prerequisites': ['chord_inversions', 'basic_progressions'],
            'difficulty': 'beginner',
            'estimated_hours': 3
        },
        'seventh_chords': {
            'name': 'Seventh Chords',
            'description': 'Adding the 7th degree for richer harmony',
            'prerequisites': ['triads', 'basic_progressions'],
            'difficulty': 'intermediate',
            'estimated_hours': 3
        },
        'modes': {
            'name': 'Modes',
            'description': 'Seven modal scales from major scale',
            'prerequisites': ['major_minor_scales'],
            'difficulty': 'intermediate',
            'estimated_hours': 4
        },
        'extended_chords': {
            'name': 'Extended Chords',
            'description': '9th, 11th, 13th chord extensions',
            'prerequisites': ['seventh_chords'],
            'difficulty': 'intermediate',
            'estimated_hours': 3
        },
        'modal_interchange': {
            'name': 'Modal Interchange',
            'description': 'Borrowing chords from parallel modes',
            'prerequisites': ['modes', 'seventh_chords'],
            'difficulty': 'intermediate',
            'estimated_hours': 3
        },
        'diatonic_substitution': {
            'name': 'Diatonic Substitution',
            'description': 'Replacing chords with similar function',
            'prerequisites': ['basic_progressions', 'seventh_chords'],
            'difficulty': 'intermediate',
            'estimated_hours': 2
        },
        'voice_leading_rules': {
            'name': 'Voice Leading Rules',
            'description': 'Classical voice leading principles',
            'prerequisites': ['simple_voice_leading', 'seventh_chords'],
            'difficulty': 'intermediate',
            'estimated_hours': 4
        },
        'neo_riemannian_theory': {
            'name': 'Neo-Riemannian Theory',
            'description': 'PLR transformations and Tonnetz lattice',
            'prerequisites': ['voice_leading_rules', 'triads'],
            'difficulty': 'advanced',
            'estimated_hours': 5
        },
        'negative_harmony': {
            'name': 'Negative Harmony',
            'description': 'Mirror-image harmonic relationships',
            'prerequisites': ['modal_interchange', 'voice_leading_rules'],
            'difficulty': 'advanced',
            'estimated_hours': 4
        },
        'coltrane_changes': {
            'name': 'Coltrane Changes',
            'description': 'Giant Steps harmonic pattern',
            'prerequisites': ['seventh_chords', 'diatonic_substitution'],
            'difficulty': 'advanced',
            'estimated_hours': 5
        },
        'barry_harris_diminished': {
            'name': 'Barry Harris Diminished System',
            'description': '6th-diminished scale harmonization',
            'prerequisites': ['extended_chords', 'voice_leading_rules'],
            'difficulty': 'advanced',
            'estimated_hours': 4
        },
        'advanced_substitutions': {
            'name': 'Advanced Substitutions',
            'description': 'Tritone subs, diminished passing, reharmonization',
            'prerequisites': ['diatonic_substitution', 'extended_chords'],
            'difficulty': 'advanced',
            'estimated_hours': 4
        },
        'voice_leading_optimization': {
            'name': 'Voice Leading Optimization',
            'description': 'Computational approaches to smooth voice leading',
            'prerequisites': ['voice_leading_rules', 'neo_riemannian_theory'],
            'difficulty': 'advanced',
            'estimated_hours': 5
        }
    }

    async def generate_theory_module(
        self,
        theory_topic: str,
        student_level: str,
        genre_context: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate complete module for a theory topic.

        Module structure:
        1. Introduction Lesson (AI-generated tutorial)
        2. Concept Exploration (interactive exercises)
        3. Application in Genre Context
        4. Creative Practice (student improvisation)
        5. Assessment (theory quiz + performance test)

        Args:
            theory_topic: Topic ID from TOPIC_METADATA
            student_level: Current skill level
            genre_context: Genre for application examples

        Returns:
            Dict containing complete module structure
        """
        if theory_topic not in self.TOPIC_METADATA:
            raise ValueError(f"Unknown theory topic: {theory_topic}")

        metadata = self.TOPIC_METADATA[theory_topic]

        # Generate introduction lesson
        intro_lesson = await self._generate_intro_lesson(theory_topic, student_level)

        # Generate concept exploration exercises
        exercises = await self._generate_concept_exercises(theory_topic, student_level)

        # Generate genre-specific application
        genre_application = await self._generate_genre_application(
            theory_topic,
            genre_context,
            student_level
        )

        # Generate assessment questions
        assessment = await self._generate_assessment(theory_topic, student_level)

        return {
            "topic_id": theory_topic,
            "metadata": metadata,
            "lessons": [
                {
                    "type": "introduction",
                    "title": f"Introduction to {metadata['name']}",
                    "content": intro_lesson,
                    "estimated_time_minutes": 15
                },
                {
                    "type": "exploration",
                    "title": "Interactive Exploration",
                    "exercises": exercises,
                    "estimated_time_minutes": 30
                },
                {
                    "type": "application",
                    "title": f"{metadata['name']} in {genre_context.title()}",
                    "content": genre_application,
                    "estimated_time_minutes": 20
                },
                {
                    "type": "assessment",
                    "title": "Knowledge Check",
                    "questions": assessment,
                    "estimated_time_minutes": 15
                }
            ],
            "total_estimated_hours": metadata['estimated_hours'],
            "prerequisites": metadata['prerequisites'],
            "difficulty": metadata['difficulty']
        }

    async def _generate_intro_lesson(
        self,
        theory_topic: str,
        student_level: str
    ) -> str:
        """Generate AI-powered introduction lesson for a theory topic"""
        metadata = self.TOPIC_METADATA[theory_topic]

        prompt = f"""
        Create an educational tutorial for {student_level} level music students learning "{metadata['name']}".

        Topic description: {metadata['description']}
        Prerequisites: {', '.join(metadata['prerequisites']) if metadata['prerequisites'] else 'None'}

        Provide a comprehensive tutorial that includes:
        1. Clear definition of the concept (2-3 paragraphs)
        2. Why it's important in music (1 paragraph)
        3. Simple examples with musical notation descriptions
        4. Common use cases
        5. Tips for understanding and remembering

        Write in an engaging, accessible style appropriate for {student_level} students.
        Use analogies and real-world musical examples.
        Aim for approximately 500-600 words.
        """

        response = await ai_orchestrator.generate(
            task_type=TaskType.TUTORIAL_GENERATION,
            prompt=prompt,
            complexity=7,  # Qwen2.5-7B for quality tutorials
            max_tokens=1200
        )

        return response.get("text", "Tutorial generation failed")

    async def _generate_concept_exercises(
        self,
        theory_topic: str,
        student_level: str
    ) -> List[Dict[str, Any]]:
        """Generate interactive exercises for exploring the concept"""
        exercises = []

        # Generate 3-5 exercises using theory library
        if theory_topic == 'neo_riemannian_theory':
            # PLR transformation exercises
            tonnetz = voice_leading_neo_riemannian.TonnetzLattice()
            exercises.append({
                "type": "transformation",
                "instruction": "Apply the P (Parallel) transformation to C major",
                "start_chord": ("C", ""),
                "target_transformation": "P",
                "correct_answer": tonnetz.apply_transformation(("C", ""), "P")
            })
            exercises.append({
                "type": "path_finding",
                "instruction": "Find the shortest PLR path from C major to Ab major",
                "start_chord": ("C", ""),
                "end_chord": ("Ab", ""),
                "hint": "Consider using the R transformation"
            })

        elif theory_topic == 'negative_harmony':
            # Negative harmony exercises
            exercises.append({
                "type": "mirror_chord",
                "instruction": "Find the negative harmony version of Cmaj7 in the key of C",
                "original_chord": ("C", "maj7"),
                "key": "C",
                "correct_answer": chord_substitutions.get_negative_harmony_chord(
                    ("C", "maj7"), "C", "major"
                )
            })

        elif theory_topic == 'advanced_substitutions':
            # Substitution exercises
            exercises.append({
                "type": "find_substitutions",
                "instruction": "Find all valid substitutions for G7 in the key of C major",
                "target_chord": ("G", "7"),
                "key": "C"
            })

        else:
            # Generic theory exercises
            exercises.append({
                "type": "conceptual",
                "instruction": f"Practice identifying and using {self.TOPIC_METADATA[theory_topic]['name']}",
                "description": "Interactive exercises will be generated based on your progress"
            })

        return exercises

    async def _generate_genre_application(
        self,
        theory_topic: str,
        genre: str,
        student_level: str
    ) -> str:
        """Generate genre-specific application examples"""
        metadata = self.TOPIC_METADATA[theory_topic]

        prompt = f"""
        Explain how "{metadata['name']}" is used in {genre} music.

        Student level: {student_level}
        Concept: {metadata['description']}

        Provide:
        1. How this theory concept appears in {genre} (2-3 paragraphs)
        2. Specific song examples or famous uses
        3. Practical tips for applying it in {genre} playing/composition
        4. What makes this concept particularly effective in {genre}

        Keep language at {student_level} level, approximately 300-400 words.
        """

        response = await ai_orchestrator.generate(
            task_type=TaskType.TUTORIAL_GENERATION,
            prompt=prompt,
            complexity=6,  # Qwen2.5-7B
            max_tokens=800
        )

        return response.get("text", "Genre application generation failed")

    async def _generate_assessment(
        self,
        theory_topic: str,
        student_level: str
    ) -> List[Dict[str, Any]]:
        """Generate assessment questions for the theory topic"""
        metadata = self.TOPIC_METADATA[theory_topic]

        prompt = f"""
        Create 5 assessment questions for {student_level} students about "{metadata['name']}".

        Topic: {metadata['description']}

        For each question, provide:
        - Question text
        - 4 multiple choice options (A, B, C, D)
        - Correct answer (letter)
        - Brief explanation of why it's correct

        Make questions progressively harder (1 easy, 2 medium, 2 challenging).
        Focus on understanding, not just memorization.

        Format each question as:
        Q1: [question]
        A) [option]
        B) [option]
        C) [option]
        D) [option]
        Correct: [letter]
        Explanation: [explanation]
        """

        response = await ai_orchestrator.generate(
            task_type=TaskType.CONTENT_VALIDATION,
            prompt=prompt,
            complexity=5,  # Qwen2.5-7B
            max_tokens=1000
        )

        # Parse response into structured questions
        # For now, return raw text (would implement parsing in production)
        return [{
            "raw_content": response.get("text", ""),
            "format": "multiple_choice",
            "count": 5
        }]

    def get_learning_path(self, student_level: str) -> List[str]:
        """
        Get recommended learning path for a student level.

        Returns ordered list of topic IDs to study.
        """
        return self.THEORY_PROGRESSION.get(student_level, [])

    def get_next_topics(
        self,
        completed_topics: List[str],
        student_level: str
    ) -> List[str]:
        """
        Get next recommended topics based on what student has completed.

        Args:
            completed_topics: List of topic IDs already completed
            student_level: Current skill level

        Returns:
            List of topic IDs ready to study (prerequisites met)
        """
        all_topics = self.THEORY_PROGRESSION.get(student_level, [])
        available = []

        for topic in all_topics:
            if topic in completed_topics:
                continue

            # Check if prerequisites are met
            prerequisites = self.TOPIC_METADATA[topic]['prerequisites']
            if all(prereq in completed_topics for prereq in prerequisites):
                available.append(topic)

        return available


# Global instance
theory_curriculum_service = TheoryCurriculumService()
