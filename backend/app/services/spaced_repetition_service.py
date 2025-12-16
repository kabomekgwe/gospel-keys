"""Spaced Repetition Service

Implements the SM-2 (SuperMemo 2) algorithm for optimal exercise review scheduling.
Calculates when users should review exercises based on their performance.

Algorithm: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserExerciseProgress


class SpacedRepetitionService:
    """Service for spaced repetition scheduling using SM-2 algorithm"""

    def __init__(self, db: AsyncSession):
        self.db = db

        # SM-2 algorithm constants
        self.initial_ease_factor = 2.5
        self.initial_interval = 1  # 1 day
        self.ease_factor_min = 1.3
        self.ease_factor_max = 2.5

    async def calculate_next_review(
        self,
        user_id: int,
        exercise_id: str,
        quality: int
    ) -> Dict[str, Any]:
        """Calculate next review date using SM-2 algorithm

        Args:
            user_id: User ID
            exercise_id: Exercise ID
            quality: Quality rating (0-5)
                0: Complete blackout
                1: Incorrect, but recognized
                2: Incorrect, but close
                3: Correct with difficulty
                4: Correct with hesitation
                5: Perfect recall

        Returns:
            Updated spaced repetition data
        """
        # Get current progress
        progress = await self._get_progress(user_id, exercise_id)

        # Get current values or defaults
        ease_factor = progress.get("ease_factor", self.initial_ease_factor)
        interval = progress.get("interval", self.initial_interval)
        repetitions = progress.get("repetitions", 0)

        # SM-2 algorithm
        if quality < 3:
            # Failed review - reset
            repetitions = 0
            interval = 1
        else:
            # Successful review
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = round(interval * ease_factor)

            repetitions += 1

        # Update ease factor
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        # Constrain ease factor
        ease_factor = max(self.ease_factor_min, min(self.ease_factor_max, ease_factor))

        # Calculate next review date
        next_review = datetime.utcnow() + timedelta(days=interval)

        # Update database
        await self._update_progress(
            user_id=user_id,
            exercise_id=exercise_id,
            ease_factor=ease_factor,
            interval=interval,
            repetitions=repetitions,
            last_reviewed=datetime.utcnow(),
            next_review=next_review
        )

        return {
            "ease_factor": ease_factor,
            "interval": interval,
            "repetitions": repetitions,
            "next_review": next_review,
            "quality": quality
        }

    async def get_due_exercises(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get exercises due for review today

        Args:
            user_id: User ID
            limit: Maximum number of exercises

        Returns:
            List of exercises due for review, sorted by most overdue first
        """
        now = datetime.utcnow()

        stmt = (
            select(UserExerciseProgress)
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
        due_exercises = result.scalars().all()

        return [
            {
                "exercise_id": ex.exercise_id,
                "next_review": ex.next_review,
                "interval": ex.interval,
                "ease_factor": ex.ease_factor,
                "repetitions": ex.repetitions,
                "overdue_days": (now - ex.next_review).days if ex.next_review else 0
            }
            for ex in due_exercises
        ]

    async def get_upcoming_reviews(
        self,
        user_id: int,
        days_ahead: int = 7
    ) -> Dict[str, int]:
        """Get review schedule for upcoming days

        Args:
            user_id: User ID
            days_ahead: Number of days to look ahead

        Returns:
            Dictionary of {date: count} for each day
        """
        now = datetime.utcnow()
        end_date = now + timedelta(days=days_ahead)

        stmt = (
            select(
                func.date(UserExerciseProgress.next_review).label('review_date'),
                func.count().label('count')
            )
            .where(
                and_(
                    UserExerciseProgress.user_id == user_id,
                    UserExerciseProgress.next_review.between(now, end_date)
                )
            )
            .group_by(func.date(UserExerciseProgress.next_review))
        )

        result = await self.db.execute(stmt)
        upcoming = result.all()

        return {
            str(row.review_date): row.count
            for row in upcoming
        }

    async def get_review_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get spaced repetition statistics

        Args:
            user_id: User ID

        Returns:
            Statistics about review schedule
        """
        now = datetime.utcnow()
        week_from_now = now + timedelta(days=7)

        # Get all progress records
        stmt = select(UserExerciseProgress).where(UserExerciseProgress.user_id == user_id)
        result = await self.db.execute(stmt)
        all_progress = result.scalars().all()

        if not all_progress:
            return {
                "total_due_today": 0,
                "total_upcoming_week": 0,
                "total_overdue": 0,
                "avg_ease_factor": 0.0,
                "avg_interval": 0.0,
                "total_repetitions": 0,
            }

        total_due_today = sum(1 for p in all_progress if p.next_review and p.next_review <= now)
        total_upcoming_week = sum(1 for p in all_progress if p.next_review and now < p.next_review <= week_from_now)
        total_overdue = sum(1 for p in all_progress if p.next_review and p.next_review < now)

        ease_factors = [p.ease_factor for p in all_progress if p.ease_factor]
        avg_ease_factor = sum(ease_factors) / len(ease_factors) if ease_factors else 0.0

        intervals = [p.interval for p in all_progress if p.interval]
        avg_interval = sum(intervals) / len(intervals) if intervals else 0.0

        total_repetitions = sum(p.repetitions for p in all_progress)

        return {
            "total_due_today": total_due_today,
            "total_upcoming_week": total_upcoming_week,
            "total_overdue": total_overdue,
            "avg_ease_factor": avg_ease_factor,
            "avg_interval": avg_interval,
            "total_repetitions": total_repetitions,
        }

    async def mark_as_reviewed(
        self,
        user_id: int,
        exercise_id: str,
        quality: int
    ) -> Dict[str, Any]:
        """Mark an exercise as reviewed with quality rating

        This is the main method to call after a practice session.

        Args:
            user_id: User ID
            exercise_id: Exercise ID
            quality: Quality rating (0-5)

        Returns:
            Updated scheduling information
        """
        # Calculate next review
        schedule = await self.calculate_next_review(user_id, exercise_id, quality)

        # Also update general progress
        from app.services.exercise_progress_service import get_exercise_progress_service
        progress_service = get_exercise_progress_service(self.db)

        # Record practice session (assuming quality maps roughly to score)
        score = (quality / 5.0) * 100  # Convert 0-5 to 0-100
        await progress_service.record_practice_session(
            user_id=user_id,
            exercise_id=exercise_id,
            duration_seconds=0,  # Unknown from review
            score=score,
            quality_rating=quality
        )

        return schedule

    async def reset_exercise(
        self,
        user_id: int,
        exercise_id: str
    ) -> None:
        """Reset an exercise to initial spaced repetition state

        Args:
            user_id: User ID
            exercise_id: Exercise ID
        """
        await self._update_progress(
            user_id=user_id,
            exercise_id=exercise_id,
            ease_factor=self.initial_ease_factor,
            interval=self.initial_interval,
            repetitions=0,
            last_reviewed=None,
            next_review=datetime.utcnow()
        )

    async def _get_progress(
        self,
        user_id: int,
        exercise_id: str
    ) -> Dict[str, Any]:
        """Get spaced repetition progress for an exercise

        Args:
            user_id: User ID
            exercise_id: Exercise ID

        Returns:
            Progress data or defaults
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
            return {
                "ease_factor": self.initial_ease_factor,
                "interval": self.initial_interval,
                "repetitions": 0,
                "last_reviewed": None,
                "next_review": datetime.utcnow()
            }

        return {
            "ease_factor": progress.ease_factor,
            "interval": progress.interval,
            "repetitions": progress.repetitions,
            "last_reviewed": progress.last_reviewed,
            "next_review": progress.next_review
        }

    async def _update_progress(
        self,
        user_id: int,
        exercise_id: str,
        ease_factor: float,
        interval: int,
        repetitions: int,
        last_reviewed: Optional[datetime],
        next_review: datetime
    ) -> None:
        """Update spaced repetition progress in database

        Args:
            user_id: User ID
            exercise_id: Exercise ID
            ease_factor: New ease factor
            interval: New interval (days)
            repetitions: New repetition count
            last_reviewed: Last review timestamp
            next_review: Next review date
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
            # Create new progress record
            progress = UserExerciseProgress(
                user_id=user_id,
                exercise_id=exercise_id,
                times_practiced=0,
                total_practice_time_seconds=0,
                ease_factor=ease_factor,
                interval=interval,
                repetitions=repetitions,
                last_reviewed=last_reviewed,
                next_review=next_review
            )
            self.db.add(progress)
        else:
            # Update existing record
            progress.ease_factor = ease_factor
            progress.interval = interval
            progress.repetitions = repetitions
            progress.last_reviewed = last_reviewed
            progress.next_review = next_review

        await self.db.commit()

    def get_quality_description(self, quality: int) -> str:
        """Get human-readable description of quality rating

        Args:
            quality: Quality rating (0-5)

        Returns:
            Description string
        """
        descriptions = {
            0: "Complete blackout - No recall whatsoever",
            1: "Incorrect - But you recognized it when shown",
            2: "Incorrect - But it felt familiar/close",
            3: "Correct - But required significant effort",
            4: "Correct - With slight hesitation",
            5: "Perfect - Instant and confident recall"
        }
        return descriptions.get(quality, "Unknown quality level")


def get_spaced_repetition_service(db: AsyncSession) -> SpacedRepetitionService:
    """Factory function for spaced repetition service

    Args:
        db: Database session

    Returns:
        SpacedRepetitionService instance
    """
    return SpacedRepetitionService(db)
