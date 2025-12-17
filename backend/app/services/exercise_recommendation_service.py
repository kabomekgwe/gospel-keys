"""Exercise Recommendation Engine

Intelligent recommendation system that suggests exercises based on:
- User progress and weak areas
- Spaced repetition schedule
- Learning goals and preferences
- Progressive difficulty
- Genre/style preferences
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserExerciseProgress, ExerciseLibrary, CurriculumLibrary
from app.schemas.curriculum import ExerciseTypeEnum, DifficultyLevelEnum


class ExerciseRecommendationService:
    """Service for generating personalized exercise recommendations"""

    def __init__(self, db: AsyncSession):
        self.db = db

        # Recommendation weights (sum to 1.0)
        self.weight_spaced_repetition = 0.4  # Prioritize due reviews
        self.weight_weak_areas = 0.3          # Focus on struggling areas
        self.weight_new_content = 0.2         # Introduce new exercises
        self.weight_variety = 0.1             # Ensure diverse practice

    async def get_recommended_exercises(
        self,
        user_id: int,
        limit: int = 10,
        genre: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get personalized exercise recommendations

        Args:
            user_id: User ID
            limit: Maximum recommendations
            genre: Optional genre filter

        Returns:
            List of recommended exercises with reasoning
        """
        recommendations = []

        # 1. Spaced repetition recommendations (40%)
        sr_limit = int(limit * self.weight_spaced_repetition)
        sr_recommendations = await self._get_spaced_repetition_recommendations(
            user_id, sr_limit
        )
        recommendations.extend(sr_recommendations)

        # 2. Weak area recommendations (30%)
        weak_limit = int(limit * self.weight_weak_areas)
        weak_recommendations = await self._get_weak_area_recommendations(
            user_id, weak_limit
        )
        recommendations.extend(weak_recommendations)

        # 3. New content recommendations (20%)
        new_limit = int(limit * self.weight_new_content)
        new_recommendations = await self._get_new_content_recommendations(
            user_id, new_limit, genre
        )
        recommendations.extend(new_recommendations)

        # 4. Variety recommendations (10%)
        variety_limit = max(1, limit - len(recommendations))
        variety_recommendations = await self._get_variety_recommendations(
            user_id, variety_limit
        )
        recommendations.extend(variety_recommendations)

        # Deduplicate and limit
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            exercise_id = rec["exercise_id"]
            if exercise_id not in seen:
                seen.add(exercise_id)
                unique_recommendations.append(rec)

        return unique_recommendations[:limit]

    async def _get_spaced_repetition_recommendations(
        self,
        user_id: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get exercises due for review

        Args:
            user_id: User ID
            limit: Maximum recommendations

        Returns:
            List of due exercises with reasoning
        """
        now = datetime.utcnow()

        stmt = (
            select(UserExerciseProgress, ExerciseLibrary)
            .join(ExerciseLibrary, UserExerciseProgress.exercise_id == ExerciseLibrary.id)
            .where(
                and_(
                    UserExerciseProgress.user_id == user_id,
                    UserExerciseProgress.next_review <= now
                )
            )
            .order_by(UserExerciseProgress.next_review.asc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        due_exercises = result.all()

        recommendations = []
        for progress, exercise in due_exercises:
            overdue_days = (now - progress.next_review).days if progress.next_review else 0
            recommendations.append({
                "exercise_id": exercise.id,
                "exercise_type": exercise.exercise_type,
                "difficulty": exercise.difficulty,
                "reason": f"Due for review ({overdue_days} days overdue)" if overdue_days > 0 else "Due for review today",
                "priority": "urgent" if overdue_days > 3 else "high",
                "next_review": progress.next_review,
                "repetitions": progress.repetitions
            })

        return recommendations

    async def _get_weak_area_recommendations(
        self,
        user_id: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get exercises in areas where user is struggling

        Args:
            user_id: User ID
            limit: Maximum recommendations

        Returns:
            List of exercises targeting weak areas
        """
        # Get weak areas from progress service
        from app.services.exercise_progress_service import get_exercise_progress_service
        progress_service = get_exercise_progress_service(self.db)
        weak_areas = await progress_service.get_weak_areas(user_id, min_attempts=2)

        return weak_areas[:limit]

    async def _get_new_content_recommendations(
        self,
        user_id: int,
        limit: int,
        genre: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get new exercises user hasn't tried

        Args:
            user_id: User ID
            limit: Maximum recommendations
            genre: Optional genre filter

        Returns:
            List of new exercises with appropriate difficulty
        """
        # Get exercises user hasn't practiced
        stmt = (
            select(ExerciseLibrary)
            .outerjoin(
                UserExerciseProgress,
                and_(
                    UserExerciseProgress.exercise_id == ExerciseLibrary.id,
                    UserExerciseProgress.user_id == user_id
                )
            )
            .where(UserExerciseProgress.user_id.is_(None))  # Not practiced
            .limit(limit * 2)  # Get more for filtering
        )

        result = await self.db.execute(stmt)
        new_exercises = result.scalars().all()

        recommendations = []
        for exercise in new_exercises[:limit]:
            recommendations.append({
                "exercise_id": exercise.id,
                "exercise_type": exercise.exercise_type,
                "difficulty": exercise.difficulty,
                "reason": "New content to explore",
                "priority": "medium"
            })

        return recommendations

    async def _get_variety_recommendations(
        self,
        user_id: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get exercises to ensure practice variety

        Args:
            user_id: User ID
            limit: Maximum recommendations

        Returns:
            List of exercises for variety
        """
        # Get exercises from underrepresented types
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        # Find exercise types not practiced recently
        stmt = (
            select(ExerciseLibrary)
            .outerjoin(
                UserExerciseProgress,
                and_(
                    UserExerciseProgress.exercise_id == ExerciseLibrary.id,
                    UserExerciseProgress.user_id == user_id,
                    UserExerciseProgress.last_reviewed >= cutoff_date
                )
            )
            .where(UserExerciseProgress.user_id.is_(None))  # Not practiced recently
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        variety_exercises = result.scalars().all()

        recommendations = []
        for exercise in variety_exercises:
            recommendations.append({
                "exercise_id": exercise.id,
                "exercise_type": exercise.exercise_type,
                "difficulty": exercise.difficulty,
                "reason": "Practice variety - not done recently",
                "priority": "low"
            })

        return recommendations

    async def recommend_by_genre(
        self,
        user_id: int,
        genre: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recommendations for a specific genre

        Args:
            user_id: User ID
            genre: Genre to filter by
            limit: Maximum recommendations

        Returns:
            Genre-specific recommendations
        """
        stmt = (
            select(ExerciseLibrary)
            .join(CurriculumLibrary, ExerciseLibrary.curriculum_id == CurriculumLibrary.id)
            .outerjoin(
                UserExerciseProgress,
                and_(
                    UserExerciseProgress.exercise_id == ExerciseLibrary.id,
                    UserExerciseProgress.user_id == user_id
                )
            )
            .where(
                and_(
                    CurriculumLibrary.genre.ilike(f"%{genre}%"),
                    UserExerciseProgress.user_id.is_(None) # Not practiced yet
                )
            )
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        exercises = result.scalars().all()

        return [
            {
                "exercise_id": ex.id,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "reason": f"Popular in {genre}",
                "priority": "medium",
                "genre": genre
            }
            for ex in exercises
        ]

    async def recommend_for_weak_areas(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recommendations specifically targeting weaknesses

        Args:
            user_id: User ID
            limit: Maximum recommendations

        Returns:
            Exercises targeting weak areas
        """
        from app.services.exercise_progress_service import get_exercise_progress_service

        progress_service = get_exercise_progress_service(self.db)

        # Get weak areas
        weak_exercises = await progress_service.get_weak_areas(user_id)

        # Enhance with recommendations
        recommendations = []
        for exercise in weak_exercises[:limit]:
            recommendations.append({
                "exercise_id": exercise["exercise_id"],
                "exercise_type": exercise["exercise_type"],
                "difficulty": exercise["difficulty"],
                "reason": f"Struggling area - {exercise['avg_score']:.0f}% success rate",
                "priority": "high",
                "current_score": exercise["avg_score"]
            })

        return recommendations

    async def get_next_difficulty_exercises(
        self,
        user_id: int,
        exercise_type: ExerciseTypeEnum,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Suggest exercises at the next difficulty level

        Args:
            user_id: User ID
            exercise_type: Type of exercise
            limit: Maximum recommendations

        Returns:
            Exercises at next difficulty level
        """
        difficulty_levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4
        }
        
        # 1. Determine user's current level for this exercise type
        stmt = (
            select(UserExerciseProgress, ExerciseLibrary)
            .join(ExerciseLibrary, UserExerciseProgress.exercise_id == ExerciseLibrary.id)
            .where(
                and_(
                    UserExerciseProgress.user_id == user_id,
                    ExerciseLibrary.exercise_type == exercise_type,
                    UserExerciseProgress.is_mastered == True
                )
            )
        )
        result = await self.db.execute(stmt)
        mastered = result.all()
        
        current_max_level = 0
        for progress, exercise in mastered:
            level = difficulty_levels.get(exercise.difficulty.lower(), 1)
            current_max_level = max(current_max_level, level)
            
        next_level = current_max_level + 1
        
        # 2. Find exercises at next difficulty level
        target_difficulties = [k for k, v in difficulty_levels.items() if v == next_level]
        
        if not target_difficulties:
            target_difficulties = ["advanced"] # Fallback
            
        stmt = (
            select(ExerciseLibrary)
            .where(
                and_(
                    ExerciseLibrary.exercise_type == exercise_type,
                    ExerciseLibrary.difficulty.in_(target_difficulties)
                )
            )
            .limit(limit)
        )
        
        ex_result = await self.db.execute(stmt)
        exercises = ex_result.scalars().all()
        
        return [
            {
                "exercise_id": ex.id,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "reason": "Next difficulty level challenge",
                "priority": "high"
            }
            for ex in exercises
        ]

    async def get_complementary_exercises(
        self,
        user_id: int,
        exercise_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get exercises that complement a given exercise

        Args:
            user_id: User ID
            exercise_id: Reference exercise
            limit: Maximum recommendations

        Returns:
            Complementary exercises
        """
        # 1. Get exercise details
        stmt = select(ExerciseLibrary).where(ExerciseLibrary.id == exercise_id)
        result = await self.db.execute(stmt)
        ref_exercise = result.scalar_one_or_none()
        
        if not ref_exercise:
            return []
            
        # 2. Find related exercises (same key, similar concepts)
        stmt = (
            select(ExerciseLibrary)
            .where(
                and_(
                    ExerciseLibrary.id != exercise_id,
                    ExerciseLibrary.key == ref_exercise.key,
                    ExerciseLibrary.difficulty == ref_exercise.difficulty
                )
            )
            .limit(limit)
        )
        
        rel_result = await self.db.execute(stmt)
        related = rel_result.scalars().all()
        
        return [
            {
                "exercise_id": ex.id,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "reason": f"Complementary practice in {ref_exercise.key}",
                "priority": "medium"
            }
            for ex in related
        ]

    async def get_recommendation_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get statistics about recommendations

        Args:
            user_id: User ID

        Returns:
            Recommendation statistics
        """
        from app.services.spaced_repetition_service import get_spaced_repetition_service
        from app.services.exercise_progress_service import get_exercise_progress_service

        sr_service = get_spaced_repetition_service(self.db)
        progress_service = get_exercise_progress_service(self.db)

        sr_stats = await sr_service.get_review_stats(user_id)
        progress_stats = await progress_service.get_progress_stats(user_id)
        weak_areas = await progress_service.get_weak_areas(user_id)

        return {
            "due_for_review": sr_stats["total_due_today"],
            "overdue_reviews": sr_stats["total_overdue"],
            "weak_areas_count": len(weak_areas),
            "exercises_practiced": progress_stats["total_exercises_practiced"],
            "mastery_rate": progress_stats["mastery_rate"],
            "recommendation_balance": {
                "review": self.weight_spaced_repetition,
                "weak_areas": self.weight_weak_areas,
                "new_content": self.weight_new_content,
                "variety": self.weight_variety
            }
        }


def get_exercise_recommendation_service(db: AsyncSession) -> ExerciseRecommendationService:
    """Factory function for exercise recommendation service

    Args:
        db: Database session

    Returns:
        ExerciseRecommendationService instance
    """
    return ExerciseRecommendationService(db)
