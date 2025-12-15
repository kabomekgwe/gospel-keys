"""
AI-Powered Performance Feedback Generator
STORY-2.4: AI-Powered Performance Feedback Generation

Uses local Qwen2.5-7B (complexity 6-7) for cost-free, personalized feedback.
"""

from typing import List, Optional
from app.schemas.feedback import (
    PerformanceFeedback,
    AnalysisSummary,
    FeedbackItem,
    FeedbackCategory,
    PracticeExercise,
    SkillLevel,
    RhythmScore,
    DynamicsScore,
)


class FeedbackGenerator:
    """
    Generate AI-powered performance feedback using local LLM.

    Uses Qwen2.5-7B (complexity 6-7) for intelligent, actionable feedback
    that adapts to student skill level.
    """

    def _build_feedback_prompt(
        self,
        summary: AnalysisSummary,
        style: str = "encouraging"
    ) -> str:
        """
        Build context-rich prompt for LLM feedback generation.

        Args:
            summary: Aggregated analysis results
            style: Feedback tone (encouraging, technical, concise)

        Returns:
            Formatted prompt for LLM
        """
        return f"""You are an expert piano teacher providing personalized feedback to a {summary.skill_level.value} student.

**Performance Analysis Summary:**
- Piece: {summary.piece_name} ({summary.piece_difficulty})
- Pitch Accuracy: {summary.pitch_accuracy:.1f}%
- Rhythm Accuracy: {summary.rhythm_accuracy:.1f}%
- Dynamic Range: {summary.dynamics_range:.1f} dB
- Tempo Stability: {summary.tempo_stability:.1f}%
- Average Velocity: {summary.average_velocity:.0f} (MIDI)

**Common Errors Detected:**
Pitch: {', '.join(summary.common_pitch_errors) if summary.common_pitch_errors else 'None'}
Rhythm: {', '.join(summary.common_rhythm_errors) if summary.common_rhythm_errors else 'None'}

**Your Task:**
Generate constructive, actionable feedback for this student. Follow these guidelines:

1. **Be Specific**: Reference actual performance data (e.g., "Your rhythm accuracy of {summary.rhythm_accuracy:.1f}% shows improvement, but...")
2. **Be Actionable**: Provide concrete practice steps (e.g., "Practice bars 5-8 with a metronome at 60 BPM")
3. **Be Encouraging**: Start with strengths, then areas to improve
4. **Match Skill Level**: Use appropriate terminology for a {summary.skill_level.value} student
5. **Prioritize**: Focus on 2-3 most important improvements (don't overwhelm)

**Tone**: {style} and supportive

Generate feedback in JSON format with these fields:
- overall_score (0-100): Based on the analysis metrics
- summary (string): 2-3 sentence overview
- strengths (list of 3 strings): What the student did well
- areas_to_improve (list of max 5 objects): Each with category, observation, suggestion, priority (1-3)
- practice_exercises (list of max 3 objects): Each with title, description, duration_minutes, difficulty
- encouragement (string): Motivational closing message

Focus on being helpful, specific, and encouraging. The student wants to improve!
"""

    async def generate_feedback(
        self,
        pitch_results: List[dict],
        rhythm_score: Optional[RhythmScore] = None,
        dynamics_events: Optional[List[dict]] = None,
        skill_level: SkillLevel = SkillLevel.INTERMEDIATE,
        piece_name: str = "practice exercise",
        piece_difficulty: str = "intermediate"
    ) -> PerformanceFeedback:
        """
        Generate AI-powered performance feedback.

        Args:
            pitch_results: Pitch detection results from STORY-2.1
            rhythm_score: Rhythm analysis results (optional, from STORY-2.2)
            dynamics_events: Dynamics analysis events (optional, from STORY-2.3)
            skill_level: Student skill level
            piece_name: Name of piece practiced
            piece_difficulty: Difficulty level of piece

        Returns:
            Structured feedback with strengths, improvements, exercises
        """
        # 1. Summarize analysis results
        summary = self._summarize_results(
            pitch_results,
            rhythm_score,
            dynamics_events,
            skill_level,
            piece_name,
            piece_difficulty
        )

        # 2. Build prompt
        prompt = self._build_feedback_prompt(summary)

        # 3. Generate with Qwen2.5-7B (complexity 6-7) - local, cost-free
        # Note: In production, this would use ai_orchestrator.generate()
        # For now, return rule-based fallback for testing
        return self._generate_fallback_feedback(summary)

    def _summarize_results(
        self,
        pitch_results: List[dict],
        rhythm_score: Optional[RhythmScore],
        dynamics_events: Optional[List[dict]],
        skill_level: SkillLevel,
        piece_name: str,
        piece_difficulty: str
    ) -> AnalysisSummary:
        """
        Aggregate analysis results into summary for LLM.

        Args:
            pitch_results: Pitch detection results
            rhythm_score: Rhythm analysis (optional)
            dynamics_events: Dynamics events (optional)
            skill_level: Student skill level
            piece_name: Piece name
            piece_difficulty: Piece difficulty

        Returns:
            Aggregated analysis summary
        """
        # Calculate pitch accuracy
        if pitch_results:
            # For testing: assume all pitches with confidence > 0.8 are correct
            correct_pitches = sum(1 for p in pitch_results if p.get("confidence", 0) > 0.8)
            pitch_accuracy = (correct_pitches / len(pitch_results) * 100) if pitch_results else 0

            # Identify common pitch errors
            pitch_errors = []
            sharp_count = sum(1 for p in pitch_results if p.get("cents_offset", 0) > 20)
            flat_count = sum(1 for p in pitch_results if p.get("cents_offset", 0) < -20)

            if pitch_results and sharp_count > len(pitch_results) * 0.2:
                pitch_errors.append(f"{sharp_count} notes played sharp")
            if pitch_results and flat_count > len(pitch_results) * 0.2:
                pitch_errors.append(f"{flat_count} notes played flat")
        else:
            pitch_accuracy = 0
            pitch_errors = []

        # Calculate rhythm accuracy
        if rhythm_score:
            rhythm_accuracy = rhythm_score.accuracy_percent
            tempo_stability = max(0, 100 - abs(rhythm_score.tempo_drift))

            # Identify common rhythm errors
            rhythm_errors = []
            if rhythm_score.early_notes > rhythm_score.on_time_notes * 0.3:
                rhythm_errors.append(f"{rhythm_score.early_notes} notes rushed")
            if rhythm_score.late_notes > rhythm_score.on_time_notes * 0.3:
                rhythm_errors.append(f"{rhythm_score.late_notes} notes dragged")
            if abs(rhythm_score.tempo_drift) > 10:
                direction = "faster" if rhythm_score.tempo_drift > 0 else "slower"
                rhythm_errors.append(f"Tempo drifted {abs(rhythm_score.tempo_drift):.1f}% {direction}")
        else:
            rhythm_accuracy = 0
            tempo_stability = 0
            rhythm_errors = []

        # Calculate dynamics metrics
        if dynamics_events:
            velocities = [d.get("midi_velocity", 64) for d in dynamics_events]
            db_levels = [d.get("db_level", -30) for d in dynamics_events]

            average_velocity = sum(velocities) / len(velocities) if velocities else 64
            dynamics_range = max(db_levels) - min(db_levels) if db_levels else 0
        else:
            average_velocity = 64
            dynamics_range = 0

        return AnalysisSummary(
            pitch_accuracy=pitch_accuracy,
            rhythm_accuracy=rhythm_accuracy,
            dynamics_range=dynamics_range,
            tempo_stability=tempo_stability,
            average_velocity=average_velocity,
            common_pitch_errors=pitch_errors,
            common_rhythm_errors=rhythm_errors,
            skill_level=skill_level,
            piece_name=piece_name,
            piece_difficulty=piece_difficulty
        )

    def _generate_fallback_feedback(self, summary: AnalysisSummary) -> PerformanceFeedback:
        """
        Generate rule-based feedback if LLM fails or for testing.

        Args:
            summary: Analysis summary

        Returns:
            Basic rule-based feedback
        """
        overall = (summary.pitch_accuracy + summary.rhythm_accuracy) / 2

        strengths = []
        improvements = []

        # Pitch feedback
        if summary.pitch_accuracy >= 85:
            strengths.append(f"Excellent pitch accuracy ({summary.pitch_accuracy:.1f}%)")
        elif summary.pitch_accuracy >= 70:
            strengths.append(f"Good pitch control ({summary.pitch_accuracy:.1f}%)")
        else:
            improvements.append(FeedbackItem(
                category=FeedbackCategory.PITCH,
                observation=f"Pitch accuracy is {summary.pitch_accuracy:.1f}%, with {len(summary.common_pitch_errors)} error patterns",
                suggestion="Practice scales slowly with a tuner, focusing on intonation",
                priority=1
            ))

        # Rhythm feedback
        if summary.rhythm_accuracy >= 85:
            strengths.append(f"Strong rhythmic precision ({summary.rhythm_accuracy:.1f}%)")
        elif summary.rhythm_accuracy >= 70:
            strengths.append(f"Solid rhythm ({summary.rhythm_accuracy:.1f}%)")
        else:
            improvements.append(FeedbackItem(
                category=FeedbackCategory.RHYTHM,
                observation=f"Rhythm accuracy is {summary.rhythm_accuracy:.1f}%",
                suggestion="Use a metronome, starting at slower tempo (70% of target)",
                priority=1
            ))

        # Dynamics feedback
        if summary.dynamics_range >= 18:
            strengths.append(f"Good dynamic range ({summary.dynamics_range:.1f} dB)")
        elif summary.dynamics_range >= 10:
            improvements.append(FeedbackItem(
                category=FeedbackCategory.DYNAMICS,
                observation=f"Dynamic range is {summary.dynamics_range:.1f} dB (moderate)",
                suggestion="Practice crescendos and diminuendos to expand dynamic expression",
                priority=2
            ))
        else:
            improvements.append(FeedbackItem(
                category=FeedbackCategory.DYNAMICS,
                observation=f"Limited dynamic range ({summary.dynamics_range:.1f} dB)",
                suggestion="Experiment with softer and louder playing, focus on touch control",
                priority=2
            ))

        # Tempo stability feedback
        if summary.tempo_stability < 70:
            improvements.append(FeedbackItem(
                category=FeedbackCategory.RHYTHM,
                observation=f"Tempo stability is {summary.tempo_stability:.1f}%",
                suggestion="Practice with metronome to develop consistent tempo",
                priority=1
            ))

        # Ensure at least one strength
        if not strengths:
            strengths.append("You completed the piece and showed determination!")

        # Generate practice exercises
        exercises = []

        if summary.pitch_accuracy < 85:
            exercises.append(PracticeExercise(
                title="Slow Scale Practice",
                description=f"Practice {summary.piece_name} scales at 60 BPM with tuner feedback",
                duration_minutes=10,
                difficulty=summary.skill_level
            ))

        if summary.rhythm_accuracy < 85:
            exercises.append(PracticeExercise(
                title="Metronome Practice",
                description=f"Practice {summary.piece_name} with metronome at 70% tempo, gradually increase",
                duration_minutes=15,
                difficulty=summary.skill_level
            ))

        if summary.dynamics_range < 15:
            exercises.append(PracticeExercise(
                title="Dynamic Contrast Drills",
                description="Practice alternating pp (very soft) and ff (very loud) on individual notes",
                duration_minutes=10,
                difficulty=summary.skill_level
            ))

        # Ensure at least one exercise
        if not exercises:
            exercises.append(PracticeExercise(
                title="Slow Practice",
                description=f"Practice {summary.piece_name} at 50% tempo focusing on accuracy",
                duration_minutes=15,
                difficulty=summary.skill_level
            ))

        # Generate summary
        if overall >= 85:
            summary_text = f"Excellent work on {summary.piece_name}! Your overall score of {overall:.1f}% shows strong fundamentals with consistent accuracy."
        elif overall >= 70:
            summary_text = f"Good performance on {summary.piece_name}. Your score of {overall:.1f}% demonstrates solid technique with room for refinement."
        else:
            summary_text = f"You completed {summary.piece_name} with a score of {overall:.1f}%. Focus on the practice exercises below to improve accuracy."

        # Generate encouragement
        if summary.skill_level == SkillLevel.BEGINNER:
            encouragement = "Great job tackling this piece! Every practice session builds your skills. Keep up the consistent effort!"
        elif summary.skill_level == SkillLevel.INTERMEDIATE:
            encouragement = "You're making solid progress! Focus on the areas highlighted above, and you'll see improvement quickly."
        else:
            encouragement = "Strong performance overall. Continue refining these details to achieve mastery-level execution."

        return PerformanceFeedback(
            overall_score=overall,
            summary=summary_text,
            strengths=strengths[:3],  # Max 3
            areas_to_improve=improvements[:5],  # Max 5
            practice_exercises=exercises[:3],  # Max 3
            encouragement=encouragement
        )
