"""Adaptive Curriculum Service

Analyzes user performance and dynamically adapts curriculum difficulty,
load, and content based on practice data and SRS metrics.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.curriculum_models import (
    Curriculum, CurriculumModule, CurriculumLesson, CurriculumExercise
)
from app.services.ai_orchestrator import ai_orchestrator, TaskType

logger = logging.getLogger(__name__)


@dataclass
class PerformanceAnalysis:
    """Performance analysis for a user's curriculum progress"""
    completion_rate: float  # 0-1
    avg_quality_score: float  # 0-5 (from SRS ease_factor)
    struggling_exercises: List[str]  # Exercise IDs with low ease_factor
    mastered_exercises: List[str]  # Exercise IDs marked as mastered
    weak_skill_areas: List[str]  # Exercise types with low performance
    strong_skill_areas: List[str]  # Exercise types with high performance
    recommended_actions: List[str]  # List of recommended adaptations
    total_exercises: int
    reviewed_exercises: int
    recent_performance_trend: str  # 'improving', 'declining', 'stable'
    consecutive_struggles: int  # Number of consecutive low-quality completions
    skill_area_trends: Dict[str, float]  # Skill area -> trend score (-1 to 1)


@dataclass
class RealTimePerformance:
    """Real-time performance metrics from recent completions"""
    last_5_quality_scores: List[float]
    avg_recent_quality: float
    trend: str  # 'improving', 'declining', 'stable'
    needs_difficulty_adjustment: bool
    recommended_difficulty_change: Optional[str]  # 'increase', 'decrease', None


class AdaptiveCurriculumService:
    """Service for analyzing performance and adapting curricula"""

    def __init__(self, db: AsyncSession):
        self.db = db

        # Performance thresholds
        self.STRUGGLING_EASE_THRESHOLD = 2.0  # Below this = struggling
        self.MASTERY_EASE_THRESHOLD = 2.8  # Above this + mastered = strong
        self.LOW_COMPLETION_THRESHOLD = 0.6  # Below 60% = overloaded
        self.HIGH_COMPLETION_THRESHOLD = 0.95  # Above 95% = under-challenged

    async def analyze_user_performance(
        self,
        user_id: int,
        lookback_days: int = 7
    ) -> PerformanceAnalysis:
        """Analyze user's recent performance across their active curriculum

        Args:
            user_id: User ID
            lookback_days: Days to look back for practice data

        Returns:
            PerformanceAnalysis dataclass
        """
        try:
            # Get user's active curriculum
            result = await self.db.execute(
                select(Curriculum)
                .where(and_(
                    Curriculum.user_id == user_id,
                    Curriculum.status == 'active'
                ))
                .order_by(Curriculum.created_at.desc())
            )
            curriculum = result.scalar_one_or_none()

            if not curriculum:
                logger.warning(f"No active curriculum for user {user_id}")
                return self._get_default_analysis()

            # Get all exercises in the curriculum
            result = await self.db.execute(
                select(CurriculumExercise)
                .join(CurriculumLesson)
                .join(CurriculumModule)
                .where(CurriculumModule.curriculum_id == curriculum.id)
            )
            exercises = result.scalars().all()

            if not exercises:
                return self._get_default_analysis()

            # Analyze exercises
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

            total_exercises = len(exercises)
            reviewed_exercises = sum(
                1 for ex in exercises
                if ex.last_reviewed_at and ex.last_reviewed_at >= cutoff_date
            )

            completion_rate = reviewed_exercises / total_exercises if total_exercises > 0 else 0.0

            # Calculate average quality score from ease_factor
            ease_factors = [ex.ease_factor for ex in exercises if ex.ease_factor]
            avg_quality_score = sum(ease_factors) / len(ease_factors) if ease_factors else 2.5

            # Identify struggling exercises
            struggling_exercises = [
                ex.id for ex in exercises
                if ex.ease_factor < self.STRUGGLING_EASE_THRESHOLD
            ]

            # Identify mastered exercises
            mastered_exercises = [
                ex.id for ex in exercises
                if ex.is_mastered or (ex.ease_factor > self.MASTERY_EASE_THRESHOLD and ex.repetition_count > 3)
            ]

            # Analyze by exercise type
            skill_performance = {}
            for ex in exercises:
                if ex.exercise_type not in skill_performance:
                    skill_performance[ex.exercise_type] = []
                skill_performance[ex.exercise_type].append(ex.ease_factor)

            weak_skill_areas = []
            strong_skill_areas = []
            skill_area_trends = {}

            for skill_type, scores in skill_performance.items():
                avg_score = sum(scores) / len(scores) if scores else 2.5
                if avg_score < self.STRUGGLING_EASE_THRESHOLD:
                    weak_skill_areas.append(skill_type)
                elif avg_score > self.MASTERY_EASE_THRESHOLD:
                    strong_skill_areas.append(skill_type)

                # Calculate trend for this skill area (if enough data)
                if len(scores) >= 3:
                    mid = len(scores) // 2
                    first_half = sum(scores[:mid]) / mid
                    second_half = sum(scores[mid:]) / (len(scores) - mid)
                    trend_score = (second_half - first_half) / 5.0  # Normalize to -1 to 1
                    skill_area_trends[skill_type] = min(1.0, max(-1.0, trend_score))

            # Calculate recent performance trend and consecutive struggles
            recent_exercises = [ex for ex in exercises if ex.last_reviewed_at and ex.last_reviewed_at >= cutoff_date]
            recent_exercises.sort(key=lambda x: x.last_reviewed_at)

            recent_performance_trend = 'stable'
            consecutive_struggles = 0

            if len(recent_exercises) >= 3:
                recent_scores = [ex.ease_factor for ex in recent_exercises]
                mid = len(recent_scores) // 2
                first_half_avg = sum(recent_scores[:mid]) / mid if mid > 0 else 2.5
                second_half_avg = sum(recent_scores[mid:]) / (len(recent_scores) - mid)

                if second_half_avg - first_half_avg > 0.3:
                    recent_performance_trend = 'improving'
                elif second_half_avg - first_half_avg < -0.3:
                    recent_performance_trend = 'declining'

                # Count consecutive low-quality completions
                for ex in reversed(recent_exercises):
                    if ex.ease_factor < self.STRUGGLING_EASE_THRESHOLD:
                        consecutive_struggles += 1
                    else:
                        break

            # Generate recommendations
            recommended_actions = self._generate_recommendations(
                completion_rate=completion_rate,
                avg_quality_score=avg_quality_score,
                weak_skill_areas=weak_skill_areas,
                struggling_count=len(struggling_exercises),
                mastered_count=len(mastered_exercises)
            )

            return PerformanceAnalysis(
                completion_rate=completion_rate,
                avg_quality_score=avg_quality_score,
                struggling_exercises=struggling_exercises,
                mastered_exercises=mastered_exercises,
                weak_skill_areas=weak_skill_areas,
                strong_skill_areas=strong_skill_areas,
                recommended_actions=recommended_actions,
                total_exercises=total_exercises,
                reviewed_exercises=reviewed_exercises,
                recent_performance_trend=recent_performance_trend,
                consecutive_struggles=consecutive_struggles,
                skill_area_trends=skill_area_trends
            )

        except Exception as e:
            logger.error(f"Failed to analyze performance for user {user_id}: {e}")
            return self._get_default_analysis()

    def _generate_recommendations(
        self,
        completion_rate: float,
        avg_quality_score: float,
        weak_skill_areas: List[str],
        struggling_count: int,
        mastered_count: int
    ) -> List[str]:
        """Generate adaptive recommendations based on performance metrics

        Args:
            completion_rate: Percentage of exercises completed
            avg_quality_score: Average ease factor
            weak_skill_areas: List of weak exercise types
            struggling_count: Number of struggling exercises
            mastered_count: Number of mastered exercises

        Returns:
            List of recommended actions
        """
        recommendations = []

        # Load adjustments
        if completion_rate < self.LOW_COMPLETION_THRESHOLD:
            recommendations.append("reduce_daily_load")
        elif completion_rate > self.HIGH_COMPLETION_THRESHOLD and avg_quality_score > 2.5:
            recommendations.append("increase_daily_load")

        # Difficulty adjustments
        if avg_quality_score < 2.0:
            recommendations.append("reduce_difficulty")
        elif avg_quality_score > 3.5 and completion_rate > 0.8:
            recommendations.append("increase_difficulty")

        # Remedial content
        if weak_skill_areas:
            recommendations.append(f"add_remedial_{weak_skill_areas[0]}")

        # Progress recognition
        if mastered_count > struggling_count * 2:
            recommendations.append("unlock_advanced_content")

        return recommendations

    async def apply_adaptations(
        self,
        curriculum_id: str,
        analysis: PerformanceAnalysis
    ) -> Dict:
        """Apply recommended adaptations to the curriculum

        Args:
            curriculum_id: Curriculum ID
            analysis: PerformanceAnalysis from analyze_user_performance

        Returns:
            Dict with applied changes
        """
        try:
            # Get curriculum
            result = await self.db.execute(
                select(Curriculum).where(Curriculum.id == curriculum_id)
            )
            curriculum = result.scalar_one_or_none()

            if not curriculum:
                raise ValueError(f"Curriculum not found: {curriculum_id}")

            changes = []

            for action in analysis.recommended_actions:
                if action == "reduce_daily_load":
                    await self._adjust_srs_intervals(curriculum_id, factor=1.2)
                    changes.append("Reduced daily exercise load by 20%")

                elif action == "increase_daily_load":
                    await self._adjust_srs_intervals(curriculum_id, factor=0.8)
                    changes.append("Increased daily exercise load by 20%")

                elif action == "reduce_difficulty":
                    # This would require regenerating exercises - log for now
                    changes.append("Recommended: Reduce exercise difficulty")

                elif action == "increase_difficulty":
                    changes.append("Recommended: Increase exercise difficulty")

                elif action.startswith("add_remedial_"):
                    skill_area = action.replace("add_remedial_", "")
                    # This would generate new exercises - log for now
                    changes.append(f"Recommended: Add remedial exercises for {skill_area}")

                elif action == "unlock_advanced_content":
                    changes.append("Recommended: Unlock advanced content")

            # Log adaptation
            adaptation_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": asdict(analysis),
                "changes": changes
            }

            # Update curriculum
            history = json.loads(curriculum.adaptation_history_json)
            history.append(adaptation_log)
            curriculum.adaptation_history_json = json.dumps(history)
            curriculum.last_adapted_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Applied {len(changes)} adaptations to curriculum {curriculum_id}")

            return {
                "curriculum_id": curriculum_id,
                "changes_applied": changes,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to apply adaptations to curriculum {curriculum_id}: {e}")
            raise e

    async def _adjust_srs_intervals(self, curriculum_id: str, factor: float):
        """Adjust SRS review intervals for all exercises

        Args:
            curriculum_id: Curriculum ID
            factor: Multiplier for intervals (>1 = slower, <1 = faster)
        """
        try:
            # Get all exercises
            result = await self.db.execute(
                select(CurriculumExercise)
                .join(CurriculumLesson)
                .join(CurriculumModule)
                .where(CurriculumModule.curriculum_id == curriculum_id)
            )
            exercises = result.scalars().all()

            # Adjust intervals
            for exercise in exercises:
                exercise.interval_days *= factor

                # Recalculate next_review_at if it exists
                if exercise.last_reviewed_at:
                    exercise.next_review_at = exercise.last_reviewed_at + timedelta(days=exercise.interval_days)

            await self.db.commit()

            logger.info(f"Adjusted SRS intervals by {factor}x for {len(exercises)} exercises")

        except Exception as e:
            logger.error(f"Failed to adjust SRS intervals: {e}")
            raise e

    def _get_default_analysis(self) -> PerformanceAnalysis:
        """Get default analysis when data is insufficient"""
        return PerformanceAnalysis(
            completion_rate=0.0,
            avg_quality_score=2.5,
            struggling_exercises=[],
            mastered_exercises=[],
            weak_skill_areas=[],
            strong_skill_areas=[],
            recommended_actions=[],
            total_exercises=0,
            reviewed_exercises=0,
            recent_performance_trend='stable',
            consecutive_struggles=0,
            skill_area_trends={}
        )

    async def get_real_time_performance(
        self,
        user_id: int,
        exercise_count: int = 5
    ) -> RealTimePerformance:
        """Analyze user's most recent exercise completions for real-time difficulty adjustment

        Args:
            user_id: User ID
            exercise_count: Number of recent exercises to analyze (default 5)

        Returns:
            RealTimePerformance with trend analysis and recommendations
        """
        try:
            # Get user's active curriculum
            result = await self.db.execute(
                select(Curriculum)
                .where(and_(
                    Curriculum.user_id == user_id,
                    Curriculum.status == 'active'
                ))
                .order_by(Curriculum.created_at.desc())
            )
            curriculum = result.scalar_one_or_none()

            if not curriculum:
                return self._get_default_real_time_performance()

            # Get last N completed exercises ordered by completion time
            result = await self.db.execute(
                select(CurriculumExercise)
                .join(CurriculumLesson)
                .join(CurriculumModule)
                .where(and_(
                    CurriculumModule.curriculum_id == curriculum.id,
                    CurriculumExercise.last_reviewed_at.isnot(None)
                ))
                .order_by(CurriculumExercise.last_reviewed_at.desc())
                .limit(exercise_count)
            )
            recent_exercises = result.scalars().all()

            if len(recent_exercises) < 3:  # Need at least 3 for trend analysis
                return self._get_default_real_time_performance()

            # Extract quality scores (using ease_factor as proxy: 2.5 = baseline, convert to 0-5 scale)
            quality_scores = [
                min(5.0, max(0.0, (ex.ease_factor - 1.0) * 2.0))  # Convert ease_factor to 0-5 scale
                for ex in recent_exercises
            ]
            quality_scores.reverse()  # Chronological order

            avg_recent_quality = sum(quality_scores) / len(quality_scores)

            # Determine trend (comparing first half vs second half)
            mid_point = len(quality_scores) // 2
            first_half_avg = sum(quality_scores[:mid_point]) / mid_point if mid_point > 0 else avg_recent_quality
            second_half_avg = sum(quality_scores[mid_point:]) / (len(quality_scores) - mid_point)

            trend_diff = second_half_avg - first_half_avg

            if trend_diff > 0.3:
                trend = 'improving'
            elif trend_diff < -0.3:
                trend = 'declining'
            else:
                trend = 'stable'

            # Determine if difficulty adjustment is needed
            needs_adjustment = False
            recommended_change = None

            if avg_recent_quality < 2.5 and trend in ['declining', 'stable']:
                needs_adjustment = True
                recommended_change = 'decrease'
            elif avg_recent_quality > 4.2 and trend in ['improving', 'stable']:
                needs_adjustment = True
                recommended_change = 'increase'

            return RealTimePerformance(
                last_5_quality_scores=quality_scores,
                avg_recent_quality=avg_recent_quality,
                trend=trend,
                needs_difficulty_adjustment=needs_adjustment,
                recommended_difficulty_change=recommended_change
            )

        except Exception as e:
            logger.error(f"Failed to get real-time performance for user {user_id}: {e}")
            return self._get_default_real_time_performance()

    def _get_default_real_time_performance(self) -> RealTimePerformance:
        """Get default real-time performance when data is insufficient"""
        return RealTimePerformance(
            last_5_quality_scores=[],
            avg_recent_quality=2.5,
            trend='stable',
            needs_difficulty_adjustment=False,
            recommended_difficulty_change=None
        )

    async def auto_adjust_difficulty(
        self,
        user_id: int,
        real_time_perf: RealTimePerformance
    ) -> Dict:
        """Automatically adjust curriculum difficulty based on real-time performance

        Args:
            user_id: User ID
            real_time_perf: Real-time performance analysis

        Returns:
            Dict with adjustment details
        """
        try:
            if not real_time_perf.needs_difficulty_adjustment:
                return {
                    "adjusted": False,
                    "reason": "Performance within acceptable range"
                }

            # Get user's active curriculum
            result = await self.db.execute(
                select(Curriculum)
                .where(and_(
                    Curriculum.user_id == user_id,
                    Curriculum.status == 'active'
                ))
                .order_by(Curriculum.created_at.desc())
            )
            curriculum = result.scalar_one_or_none()

            if not curriculum:
                return {"adjusted": False, "reason": "No active curriculum"}

            changes = []

            if real_time_perf.recommended_difficulty_change == 'decrease':
                # Reduce difficulty: increase SRS intervals (more time to practice)
                await self._adjust_srs_intervals(curriculum.id, factor=1.3)
                changes.append("Increased practice intervals by 30% to allow more time for mastery")

                # Log the adjustment
                adaptation_log = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "auto_difficulty_decrease",
                    "trigger": f"Recent avg quality: {real_time_perf.avg_recent_quality:.2f}",
                    "changes": changes
                }

            elif real_time_perf.recommended_difficulty_change == 'increase':
                # Increase difficulty: decrease SRS intervals (faster progression)
                await self._adjust_srs_intervals(curriculum.id, factor=0.7)
                changes.append("Decreased practice intervals by 30% to accelerate progression")

                adaptation_log = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "auto_difficulty_increase",
                    "trigger": f"Recent avg quality: {real_time_perf.avg_recent_quality:.2f}",
                    "changes": changes
                }

            # Update curriculum adaptation history
            history = json.loads(curriculum.adaptation_history_json)
            history.append(adaptation_log)
            curriculum.adaptation_history_json = json.dumps(history)
            curriculum.last_adapted_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Auto-adjusted difficulty for user {user_id}: {real_time_perf.recommended_difficulty_change}")

            return {
                "adjusted": True,
                "change_type": real_time_perf.recommended_difficulty_change,
                "changes_applied": changes,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to auto-adjust difficulty for user {user_id}: {e}")
            return {"adjusted": False, "reason": str(e)}
