"""Exercise Progress Tracking Service

Tracks user progress on individual exercises including:
- Practice session history
- Performance metrics (scores, completion times)
- Mastery status
- Preparation for spaced repetition
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserExerciseProgress, ExerciseLibrary


class ExerciseProgressService:
    """Service for tracking user exercise progress"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mastery_threshold = 3  # Consecutive perfect completions to master
        self.mastery_score = 0.90  # 90% accuracy to count as perfect

    async def record_practice_session(
        self,
        user_id: int,
        exercise_id: str,
        duration_seconds: int,
        score: Optional[float] = None,
        quality_rating: Optional[int] = None
    ) -> Dict[str, Any]:
        """Record a completed practice session

        Args:
            user_id: User who practiced
            exercise_id: Exercise that was practiced
            duration_seconds: Time spent practicing
            score: Performance score (0-100)
            quality_rating: Spaced repetition quality (0-5)

        Returns:
            Updated progress data including mastery status
        """
        # 1. Get or create user_exercise_progress record
        stmt = select(UserExerciseProgress).where(
            and_(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.exercise_id == exercise_id
            )
        )
        result = await self.db.execute(stmt)
        progress = result.scalar_one_or_none()

        if not progress:
            # Create new progress record
            progress = UserExerciseProgress(
                user_id=user_id,
                exercise_id=exercise_id,
                times_practiced=0,
                total_practice_time_seconds=0,
                quality_ratings_json=json.dumps([])
            )
            self.db.add(progress)

        # 2-3. Increment times_practiced and add to total_practice_time
        progress.times_practiced += 1
        progress.total_practice_time_seconds += duration_seconds

        # 4-5. Update scores if provided
        if score is not None:
            if progress.best_score is None or score > progress.best_score:
                progress.best_score = score

            if progress.avg_score is None:
                progress.avg_score = score
            else:
                # Running average
                total_score = progress.avg_score * (progress.times_practiced - 1)
                progress.avg_score = (total_score + score) / progress.times_practiced

        # 6. Append quality_rating to quality_ratings_json
        if quality_rating is not None:
            ratings = json.loads(progress.quality_ratings_json) if progress.quality_ratings_json else []
            ratings.append(quality_rating)
            progress.quality_ratings_json = json.dumps(ratings)

            # 7. Check for mastery
            if not progress.is_mastered:
                is_mastered = await self.check_for_mastery(user_id, exercise_id, ratings)
                if is_mastered:
                    progress.is_mastered = True
                    progress.mastered_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(progress)

        return {
            "user_id": progress.user_id,
            "exercise_id": progress.exercise_id,
            "times_practiced": progress.times_practiced,
            "total_practice_time": progress.total_practice_time_seconds,
            "best_score": progress.best_score,
            "avg_score": progress.avg_score,
            "is_mastered": progress.is_mastered,
            "mastered_at": progress.mastered_at,
            "updated_at": progress.updated_at
        }

    async def get_user_progress(
        self,
        user_id: int,
        exercise_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get progress data for a specific exercise

        Args:
            user_id: User ID
            exercise_id: Exercise ID

        Returns:
            Progress data or None if never practiced
        """
        stmt = select(UserExerciseProgress).where(
            and_(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.exercise_id == exercise_id
            )
        )
        result = await self.db.execute(stmt)
        progress = result.scalar_one_or_none()

        if not progress:
            return None

        return {
            "user_id": progress.user_id,
            "exercise_id": progress.exercise_id,
            "times_practiced": progress.times_practiced,
            "total_practice_time_seconds": progress.total_practice_time_seconds,
            "best_score": progress.best_score,
            "avg_score": progress.avg_score,
            "is_mastered": progress.is_mastered,
            "mastered_at": progress.mastered_at,
            "ease_factor": progress.ease_factor,
            "interval": progress.interval,
            "next_review": progress.next_review,
        }

    async def get_all_progress(
        self,
        user_id: int,
        include_mastered: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all exercise progress for a user

        Args:
            user_id: User ID
            include_mastered: Include mastered exercises

        Returns:
            List of progress records
        """
        stmt = select(UserExerciseProgress).where(UserExerciseProgress.user_id == user_id)

        if not include_mastered:
            stmt = stmt.where(UserExerciseProgress.is_mastered == False)

        result = await self.db.execute(stmt)
        progress_list = result.scalars().all()

        return [
            {
                "exercise_id": p.exercise_id,
                "times_practiced": p.times_practiced,
                "total_practice_time_seconds": p.total_practice_time_seconds,
                "best_score": p.best_score,
                "avg_score": p.avg_score,
                "is_mastered": p.is_mastered,
                "mastered_at": p.mastered_at,
                "next_review": p.next_review,
            }
            for p in progress_list
        ]

    async def get_mastered_exercises(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all exercises user has mastered

        Args:
            user_id: User ID

        Returns:
            List of mastered exercises with mastery dates
        """
        stmt = select(UserExerciseProgress).where(
            and_(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.is_mastered == True
            )
        )

        result = await self.db.execute(stmt)
        mastered_list = result.scalars().all()

        return [
            {
                "exercise_id": p.exercise_id,
                "times_practiced": p.times_practiced,
                "mastered_at": p.mastered_at,
                "best_score": p.best_score,
            }
            for p in mastered_list
        ]

    async def check_for_mastery(
        self,
        user_id: int,
        exercise_id: str,
        recent_quality_ratings: List[int]
    ) -> bool:
        """Check if user has mastered the exercise

        Mastery criteria:
        - 3 consecutive perfect completions (quality 5)
        - OR 5 completions with quality 4-5
        - OR avg_score >= 90% over last 5 attempts

        Args:
            user_id: User ID
            exercise_id: Exercise ID
            recent_quality_ratings: Recent quality ratings (most recent first)

        Returns:
            True if mastered
        """
        if not recent_quality_ratings:
            return False

        # Check consecutive perfect completions
        if len(recent_quality_ratings) >= self.mastery_threshold:
            recent = recent_quality_ratings[:self.mastery_threshold]
            if all(rating == 5 for rating in recent):
                return True

        # Check 5 high-quality completions
        if len(recent_quality_ratings) >= 5:
            recent = recent_quality_ratings[:5]
            if all(rating >= 4 for rating in recent):
                return True

        # Check average score (would need score data)
        # TODO: Implement score-based mastery check

        return False

    async def mark_as_mastered(
        self,
        user_id: int,
        exercise_id: str
    ) -> None:
        """Mark an exercise as mastered

        Args:
            user_id: User ID
            exercise_id: Exercise ID
        """
        await self.db.execute(
            update(UserExerciseProgress)
            .where(
                and_(
                    UserExerciseProgress.user_id == user_id,
                    UserExerciseProgress.exercise_id == exercise_id
                )
            )
            .values(
                is_mastered=True,
                mastered_at=datetime.utcnow()
            )
        )
        await self.db.commit()

    async def get_progress_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get overall progress statistics for a user

        Args:
            user_id: User ID

        Returns:
            Aggregated statistics
        """
        # Get all progress records for user
        stmt = select(UserExerciseProgress).where(UserExerciseProgress.user_id == user_id)
        result = await self.db.execute(stmt)
        all_progress = result.scalars().all()

        if not all_progress:
            return {
                "total_exercises_practiced": 0,
                "total_practice_time_seconds": 0,
                "total_practice_time_hours": 0.0,
                "exercises_mastered": 0,
                "exercises_in_progress": 0,
                "avg_score_overall": 0.0,
                "exercises_by_type": {},
                "mastery_rate": 0.0,
            }

        total_exercises = len(all_progress)
        total_time = sum(p.total_practice_time_seconds for p in all_progress)
        exercises_mastered = sum(1 for p in all_progress if p.is_mastered)
        exercises_in_progress = total_exercises - exercises_mastered

        # Calculate average score
        scores = [p.avg_score for p in all_progress if p.avg_score is not None]
        avg_score_overall = sum(scores) / len(scores) if scores else 0.0

        mastery_rate = (exercises_mastered / total_exercises * 100) if total_exercises > 0 else 0.0

        # Get exercise types (join with ExerciseLibrary)
        exercises_by_type = {}
        for progress in all_progress:
            ex_stmt = select(ExerciseLibrary).where(ExerciseLibrary.id == progress.exercise_id)
            ex_result = await self.db.execute(ex_stmt)
            exercise = ex_result.scalar_one_or_none()
            if exercise:
                ex_type = exercise.exercise_type
                if ex_type not in exercises_by_type:
                    exercises_by_type[ex_type] = 0
                exercises_by_type[ex_type] += 1

        return {
            "total_exercises_practiced": total_exercises,
            "total_practice_time_seconds": total_time,
            "total_practice_time_hours": total_time / 3600,
            "exercises_mastered": exercises_mastered,
            "exercises_in_progress": exercises_in_progress,
            "avg_score_overall": avg_score_overall,
            "exercises_by_type": exercises_by_type,
            "mastery_rate": mastery_rate,
        }

    async def get_weak_areas(
        self,
        user_id: int,
        min_attempts: int = 3
    ) -> List[Dict[str, Any]]:
        """Identify exercises where user is struggling

        Args:
            user_id: User ID
            min_attempts: Minimum attempts before considering weak

        Returns:
            List of exercises with low success rates, sorted by worst first
        """
        stmt = (
            select(UserExerciseProgress, ExerciseLibrary)
            .join(ExerciseLibrary, UserExerciseProgress.exercise_id == ExerciseLibrary.id)
            .where(
                and_(
                    UserExerciseProgress.user_id == user_id,
                    UserExerciseProgress.times_practiced >= min_attempts,
                    UserExerciseProgress.is_mastered == False
                )
            )
            .order_by(UserExerciseProgress.avg_score.asc())
        )

        result = await self.db.execute(stmt)
        weak_areas = result.all()

        return [
            {
                "exercise_id": progress.exercise_id,
                "exercise_type": exercise.exercise_type,
                "difficulty": exercise.difficulty,
                "times_practiced": progress.times_practiced,
                "avg_score": progress.avg_score or 0,
                "best_score": progress.best_score or 0,
            }
            for progress, exercise in weak_areas
        ]

    async def get_recent_practice(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent practice sessions

        Args:
            user_id: User ID
            days: Look back this many days
            limit: Maximum results

        Returns:
            Recent practice sessions with timestamps
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = (
            select(UserExerciseProgress)
            .where(
                and_(
                    UserExerciseProgress.user_id == user_id,
                    UserExerciseProgress.last_reviewed >= cutoff_date
                )
            )
            .order_by(UserExerciseProgress.last_reviewed.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        recent_practice = result.scalars().all()

        return [
            {
                "exercise_id": p.exercise_id,
                "last_reviewed": p.last_reviewed,
                "times_practiced": p.times_practiced,
                "avg_score": p.avg_score,
                "is_mastered": p.is_mastered,
            }
            for p in recent_practice
        ]


def get_exercise_progress_service(db: AsyncSession) -> ExerciseProgressService:
    """Factory function for exercise progress service

    Args:
        db: Database session

    Returns:
        ExerciseProgressService instance
    """
    return ExerciseProgressService(db)
