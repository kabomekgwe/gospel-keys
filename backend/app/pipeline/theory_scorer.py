"""
Theory-Based Performance Scorer

Advanced scoring using music theory analysis:
- Voice leading quality with Neo-Riemannian metrics
- Chord substitution creativity detection
- Tonnetz distance analysis
- Harmonic coherence scoring
"""

import logging
from typing import Dict, List, Any, Tuple, Optional

from app.pipeline.voice_leading_analyzer import analyze_voice_leading
from app.theory import voice_leading_neo_riemannian, chord_substitutions
from app.services.ai_orchestrator import ai_orchestrator, TaskType

logger = logging.getLogger(__name__)


class TheoryScorer:
    """
    Advanced performance scoring using theory analysis.

    Analyzes student performances with music theory knowledge to provide:
    - Voice leading quality scores
    - Substitution creativity assessment
    - Harmonic journey analysis via Tonnetz
    - AI-generated improvement suggestions
    """

    def __init__(self):
        self.tonnetz = voice_leading_neo_riemannian.TonnetzLattice()

    async def score_voice_leading(
        self,
        student_progression: List[Tuple[str, str]],
        expected_progression: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Analyze and score voice leading quality.

        Metrics:
        - Common tone retention (0-100)
        - Total voice movement (semitones)
        - Parallel motion detection (-points)
        - Smooth voice leading bonus (+points)
        - Parsimonious transitions bonus (+points)

        Args:
            student_progression: List of (root, quality) tuples played by student
            expected_progression: Expected progression

        Returns:
            Dict with detailed voice leading breakdown and overall score
        """
        if len(student_progression) < 2:
            return {
                "score": 0,
                "error": "Need at least 2 chords to analyze voice leading"
            }

        total_smoothness = 0
        total_movement = 0
        common_tones_total = 0
        parallel_fifths_count = 0
        parallel_octaves_count = 0
        parsimonious_count = 0

        analyses = []

        # Analyze each chord transition
        for i in range(len(student_progression) - 1):
            chord1 = {"root": student_progression[i][0], "quality": student_progression[i][1]}
            chord2 = {"root": student_progression[i + 1][0], "quality": student_progression[i + 1][1]}

            analysis = analyze_voice_leading(chord1, chord2)
            analyses.append(analysis)

            total_smoothness += analysis["smoothness_score"]
            total_movement += analysis["total_movement"]
            common_tones_total += analysis["common_tones"]
            parallel_fifths_count += len(analysis["parallel_fifths"])
            parallel_octaves_count += len(analysis["parallel_octaves"])

            # Check if transition is parsimonious (minimal voice movement)
            if analysis["avg_movement"] <= 2:  # 2 semitones or less average
                parsimonious_count += 1

        num_transitions = len(student_progression) - 1
        avg_smoothness = total_smoothness / num_transitions
        avg_common_tones = common_tones_total / num_transitions

        # Calculate score (0-100)
        score = 0

        # Base score from smoothness (40 points)
        score += avg_smoothness * 40

        # Common tone retention bonus (20 points)
        score += (avg_common_tones / 3) * 20  # Assuming triads (3 notes)

        # Parsimonious voice leading bonus (20 points)
        parsimonious_ratio = parsimonious_count / num_transitions
        score += parsimonious_ratio * 20

        # Penalties
        # Parallel fifths penalty (-5 points each, max -20)
        score -= min(parallel_fifths_count * 5, 20)

        # Parallel octaves penalty (-3 points each, max -10)
        score -= min(parallel_octaves_count * 3, 10)

        # Additional bonus: efficient movement (20 points)
        # Less than 10 semitones total per transition is excellent
        avg_movement = total_movement / num_transitions
        if avg_movement <= 10:
            efficiency_bonus = (10 - avg_movement) / 10 * 20
            score += efficiency_bonus

        score = max(0, min(100, score))  # Clamp to 0-100

        return {
            "score": round(score, 1),
            "metrics": {
                "avg_smoothness": round(avg_smoothness, 3),
                "avg_common_tones": round(avg_common_tones, 2),
                "total_movement_semitones": total_movement,
                "avg_movement_per_transition": round(avg_movement, 2),
                "parsimonious_transitions": parsimonious_count,
                "parsimonious_ratio": round(parsimonious_ratio, 2),
                "parallel_fifths_detected": parallel_fifths_count,
                "parallel_octaves_detected": parallel_octaves_count
            },
            "transition_analyses": analyses,
            "grade": self._get_grade(score),
            "feedback": self._generate_voice_leading_feedback(score, avg_smoothness, parsimonious_ratio, parallel_fifths_count)
        }

    async def score_substitution_creativity(
        self,
        student_progression: List[Tuple[str, str]],
        original_progression: List[Tuple[str, str]],
        key: str
    ) -> Dict[str, Any]:
        """
        Score creative substitution use.

        Checks:
        - Valid substitutions? (functional analysis)
        - Harmonic coherence? (Tonnetz distance)
        - Genre appropriateness?
        - Complexity level?

        Args:
            student_progression: Chords played by student
            original_progression: Expected/original progression
            key: Musical key

        Returns:
            Dict with creativity score and explanation
        """
        if len(student_progression) != len(original_progression):
            return {
                "score": 0,
                "error": "Progression lengths don't match"
            }

        detected_subs = []
        total_coherence = 0

        # Analyze each chord pair
        for i, (student_chord, original_chord) in enumerate(zip(student_progression, original_progression)):
            if student_chord != original_chord:
                # Student used a different chord - check if it's a valid substitution
                sub_analysis = chord_substitutions.find_substitutions(
                    original_chord,
                    key,
                    "major",
                    complexity_level="moderate"
                )

                # Check if student's chord is in the valid substitutions
                is_valid = any(
                    student_chord == (sub["symbol"].split(":")[0], sub["symbol"].split(":")[-1])
                    for category_subs in sub_analysis.values()
                    for sub in category_subs
                )

                if is_valid:
                    detected_subs.append({
                        "position": i,
                        "original": original_chord,
                        "substitution": student_chord,
                        "valid": True,
                        "category": self._identify_substitution_type(original_chord, student_chord)
                    })
                else:
                    detected_subs.append({
                        "position": i,
                        "original": original_chord,
                        "substitution": student_chord,
                        "valid": False,
                        "category": "unknown"
                    })

        # Calculate creativity score
        valid_subs = [s for s in detected_subs if s["valid"]]
        invalid_subs = [s for s in detected_subs if not s["valid"]]

        creativity_score = 0

        # Valid substitutions earn points (max 70)
        creativity_score += min(len(valid_subs) * 20, 70)

        # Invalid substitutions lose points
        creativity_score -= len(invalid_subs) * 15

        # Bonus for variety (using different substitution types)
        unique_categories = set(s["category"] for s in valid_subs if s["category"] != "unknown")
        creativity_score += len(unique_categories) * 10

        creativity_score = max(0, min(100, creativity_score))

        # Generate AI explanation
        explanation = await self._generate_substitution_explanation(
            detected_subs,
            valid_subs,
            creativity_score
        )

        return {
            "score": round(creativity_score, 1),
            "detected_substitutions": detected_subs,
            "valid_count": len(valid_subs),
            "invalid_count": len(invalid_subs),
            "creativity_level": self._get_creativity_level(creativity_score),
            "ai_explanation": explanation,
            "grade": self._get_grade(creativity_score)
        }

    async def analyze_harmonic_movement(
        self,
        progression: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Comprehensive harmonic analysis using Neo-Riemannian theory.

        Uses:
        - Neo-Riemannian distance (PLR transformations)
        - Functional harmony analysis
        - Common tone analysis
        - Voice leading efficiency

        Args:
            progression: List of (root, quality) chord tuples

        Returns:
            Dict with detailed harmonic metrics
        """
        if len(progression) < 2:
            return {"error": "Need at least 2 chords"}

        tonnetz_distances = []
        plr_paths = []

        # Analyze each transition with Tonnetz
        for i in range(len(progression) - 1):
            from_chord = progression[i]
            to_chord = progression[i + 1]

            # Find shortest PLR path
            path = self.tonnetz.find_shortest_path(from_chord, to_chord, max_steps=6)

            if path:
                distance = len(path.get("transformations", []))
                tonnetz_distances.append(distance)
                plr_paths.append({
                    "from": from_chord,
                    "to": to_chord,
                    "distance": distance,
                    "transformations": path.get("transformations", [])
                })

        avg_tonnetz_distance = sum(tonnetz_distances) / len(tonnetz_distances) if tonnetz_distances else 0

        # Calculate efficiency score
        # Lower Tonnetz distance = more efficient/parsimonious
        efficiency_score = 100
        if avg_tonnetz_distance > 0:
            efficiency_score = max(0, 100 - (avg_tonnetz_distance * 15))

        return {
            "avg_tonnetz_distance": round(avg_tonnetz_distance, 2),
            "efficiency_score": round(efficiency_score, 1),
            "plr_paths": plr_paths,
            "parsimonious_transitions": sum(1 for d in tonnetz_distances if d <= 1),
            "harmonic_complexity": self._get_harmonic_complexity(avg_tonnetz_distance),
            "metrics": {
                "total_transitions": len(progression) - 1,
                "analyzed_transitions": len(tonnetz_distances),
                "min_distance": min(tonnetz_distances) if tonnetz_distances else 0,
                "max_distance": max(tonnetz_distances) if tonnetz_distances else 0
            }
        }

    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _get_creativity_level(self, score: float) -> str:
        """Get creativity level description"""
        if score >= 80:
            return "Highly Creative"
        elif score >= 60:
            return "Creative"
        elif score >= 40:
            return "Somewhat Creative"
        else:
            return "Standard"

    def _get_harmonic_complexity(self, avg_distance: float) -> str:
        """Get harmonic complexity level"""
        if avg_distance <= 1:
            return "Simple/Diatonic"
        elif avg_distance <= 2:
            return "Moderate"
        elif avg_distance <= 3:
            return "Complex"
        else:
            return "Very Complex"

    def _identify_substitution_type(
        self,
        original: Tuple[str, str],
        substitution: Tuple[str, str]
    ) -> str:
        """Identify what type of substitution was used"""
        # Simplified - in practice would use chord_substitutions module
        orig_root, orig_qual = original
        sub_root, sub_qual = substitution

        # Check for tritone substitution (dom7 chords)
        if "7" in orig_qual and "7" in sub_qual:
            return "tritone_substitution"

        # Check for parallel major/minor
        if orig_root == sub_root and orig_qual != sub_qual:
            return "parallel"

        return "other"

    def _generate_voice_leading_feedback(
        self,
        score: float,
        smoothness: float,
        parsimonious_ratio: float,
        parallel_fifths: int
    ) -> str:
        """Generate human-readable feedback for voice leading"""
        feedback = []

        if score >= 90:
            feedback.append("Excellent voice leading! Very smooth and efficient.")
        elif score >= 70:
            feedback.append("Good voice leading with room for improvement.")
        else:
            feedback.append("Voice leading needs work. Focus on smoother transitions.")

        if parsimonious_ratio < 0.5:
            feedback.append("Try to minimize voice movement - keep common tones when possible.")

        if parallel_fifths > 0:
            feedback.append(f"Watch out for parallel fifths ({parallel_fifths} detected) - avoid in classical styles.")

        return " ".join(feedback)

    async def _generate_substitution_explanation(
        self,
        all_subs: List[Dict],
        valid_subs: List[Dict],
        score: float
    ) -> str:
        """Generate AI explanation of substitution choices"""
        if not all_subs:
            return "No substitutions detected - played progression as written."

        prompt = f"""
        Analyze this student's chord substitution choices:

        Valid substitutions: {len(valid_subs)}
        Invalid substitutions: {len([s for s in all_subs if not s['valid']])}
        Creativity score: {score}/100

        Provide 2-3 sentences explaining:
        1. What substitutions they used effectively
        2. Any substitutions that didn't work harmonically
        3. One specific suggestion for improvement

        Keep language encouraging and educational.
        """

        try:
            response = await ai_orchestrator.generate(
                task_type=TaskType.SUBSTITUTION_ANALYSIS,
                prompt=prompt,
                complexity=6,  # Qwen2.5-7B
                max_tokens=300
            )
            return response.get("text", "Unable to generate explanation")
        except Exception as e:
            logger.error(f"Failed to generate substitution explanation: {e}")
            return "Substitution analysis completed. See metrics for details."


# Global instance
theory_scorer = TheoryScorer()
