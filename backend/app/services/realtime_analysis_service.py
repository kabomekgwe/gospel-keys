"""
Real-Time Analysis Service
STORY-3.2: Database Schema & Progress Tracking

Provides CRUD operations for Phase 3 real-time performance analysis:
- RealtimeSession management
- Performance recording storage
- AnalysisResult persistence
- ProgressMetric aggregation
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    RealtimeSession,
    Performance,
    AnalysisResult,
    ProgressMetric,
    User
)


class RealtimeAnalysisService:
    """Service for managing real-time analysis data."""

    # =============================================================================
    # Session Management
    # =============================================================================

    @staticmethod
    async def create_session(
        db: AsyncSession,
        user_id: int,
        piece_name: Optional[str] = None,
        genre: Optional[str] = None,
        target_tempo: Optional[int] = None,
        difficulty_level: Optional[str] = None,
        websocket_session_id: Optional[str] = None
    ) -> RealtimeSession:
        """
        Create a new real-time practice session.

        Args:
            db: Database session
            user_id: User ID
            piece_name: Name of the piece being practiced
            genre: Music genre
            target_tempo: Target tempo in BPM
            difficulty_level: beginner, intermediate, advanced
            websocket_session_id: WebSocket session UUID

        Returns:
            Created RealtimeSession
        """
        session = RealtimeSession(
            id=uuid.uuid4(),
            user_id=user_id,
            piece_name=piece_name,
            genre=genre,
            target_tempo=target_tempo,
            difficulty_level=difficulty_level,
            started_at=datetime.utcnow(),
            websocket_session_id=websocket_session_id,
            status="active"
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def end_session(
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> Optional[RealtimeSession]:
        """
        End a practice session and calculate duration.

        Args:
            db: Database session
            session_id: Session UUID

        Returns:
            Updated RealtimeSession or None if not found
        """
        result = await db.execute(
            select(RealtimeSession).where(RealtimeSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if session:
            session.ended_at = datetime.utcnow()
            session.duration_seconds = int(
                (session.ended_at - session.started_at).total_seconds()
            )
            session.status = "completed"
            await db.commit()
            await db.refresh(session)

        return session

    @staticmethod
    async def get_session(
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> Optional[RealtimeSession]:
        """Get session by ID."""
        result = await db.execute(
            select(RealtimeSession).where(RealtimeSession.id == session_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_sessions(
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[RealtimeSession]:
        """
        Get all sessions for a user.

        Args:
            db: Database session
            user_id: User ID
            limit: Max results
            offset: Pagination offset
            status: Filter by status (active, completed, abandoned)

        Returns:
            List of RealtimeSession
        """
        query = select(RealtimeSession).where(
            RealtimeSession.user_id == user_id
        )

        if status:
            query = query.where(RealtimeSession.status == status)

        query = query.order_by(desc(RealtimeSession.started_at)).limit(limit).offset(offset)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_chunks_processed(
        db: AsyncSession,
        session_id: uuid.UUID,
        chunks: int
    ) -> None:
        """Increment chunks processed counter."""
        result = await db.execute(
            select(RealtimeSession).where(RealtimeSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if session:
            session.chunks_processed += chunks
            await db.commit()

    # =============================================================================
    # Performance Management
    # =============================================================================

    @staticmethod
    async def create_performance(
        db: AsyncSession,
        session_id: uuid.UUID,
        audio_path: Optional[str] = None,
        midi_path: Optional[str] = None,
        sample_rate: int = 44100,
        audio_format: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Performance:
        """
        Create a performance recording.

        Args:
            db: Database session
            session_id: Parent session ID
            audio_path: Path to audio file
            midi_path: Path to MIDI file
            sample_rate: Sample rate in Hz
            audio_format: Audio format (wav, mp3, etc.)
            notes: User notes

        Returns:
            Created Performance
        """
        performance = Performance(
            id=uuid.uuid4(),
            session_id=session_id,
            recording_started_at=datetime.utcnow(),
            audio_path=audio_path,
            midi_path=midi_path,
            sample_rate=sample_rate,
            audio_format=audio_format,
            notes=notes
        )
        db.add(performance)
        await db.commit()
        await db.refresh(performance)
        return performance

    @staticmethod
    async def get_session_performances(
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> List[Performance]:
        """Get all performances for a session."""
        result = await db.execute(
            select(Performance).where(
                Performance.session_id == session_id
            ).order_by(Performance.recording_started_at)
        )
        return list(result.scalars().all())

    # =============================================================================
    # Analysis Result Management
    # =============================================================================

    @staticmethod
    async def create_analysis_result(
        db: AsyncSession,
        performance_id: uuid.UUID,
        pitch_accuracy: Optional[float] = None,
        rhythm_accuracy: Optional[float] = None,
        dynamics_range: Optional[float] = None,
        overall_score: Optional[float] = None,
        feedback_json: Optional[str] = None,
        **kwargs  # Additional metrics
    ) -> AnalysisResult:
        """
        Create analysis result for a performance.

        Args:
            db: Database session
            performance_id: Parent performance ID
            pitch_accuracy: 0.0-1.0 accuracy score
            rhythm_accuracy: 0.0-1.0 accuracy score
            dynamics_range: 0.0-1.0 range score
            overall_score: 0.0-1.0 overall score
            feedback_json: JSON feedback string
            **kwargs: Additional metrics (timing_consistency, etc.)

        Returns:
            Created AnalysisResult
        """
        result = AnalysisResult(
            id=uuid.uuid4(),
            performance_id=performance_id,
            pitch_accuracy=pitch_accuracy,
            rhythm_accuracy=rhythm_accuracy,
            dynamics_range=dynamics_range,
            overall_score=overall_score,
            feedback_json=feedback_json,
            **kwargs
        )
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result

    @staticmethod
    async def get_performance_analysis(
        db: AsyncSession,
        performance_id: uuid.UUID
    ) -> List[AnalysisResult]:
        """Get all analysis results for a performance."""
        result = await db.execute(
            select(AnalysisResult).where(
                AnalysisResult.performance_id == performance_id
            ).order_by(AnalysisResult.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_latest_analysis(
        db: AsyncSession,
        performance_id: uuid.UUID
    ) -> Optional[AnalysisResult]:
        """Get most recent analysis result for a performance."""
        result = await db.execute(
            select(AnalysisResult).where(
                AnalysisResult.performance_id == performance_id
            ).order_by(desc(AnalysisResult.created_at)).limit(1)
        )
        return result.scalar_one_or_none()

    # =============================================================================
    # Progress Metrics Management
    # =============================================================================

    @staticmethod
    async def create_or_update_progress_metric(
        db: AsyncSession,
        user_id: int,
        metric_date: datetime,
        period_type: str,  # daily, weekly, monthly
        **metrics
    ) -> ProgressMetric:
        """
        Create or update progress metric for a time period.

        Args:
            db: Database session
            user_id: User ID
            metric_date: Date for the metric
            period_type: daily, weekly, monthly
            **metrics: Metric values (total_sessions, avg_pitch_accuracy, etc.)

        Returns:
            Created or updated ProgressMetric
        """
        # Check if metric exists
        result = await db.execute(
            select(ProgressMetric).where(
                and_(
                    ProgressMetric.user_id == user_id,
                    ProgressMetric.metric_date == metric_date,
                    ProgressMetric.period_type == period_type
                )
            )
        )
        metric = result.scalar_one_or_none()

        if metric:
            # Update existing
            for key, value in metrics.items():
                if hasattr(metric, key):
                    setattr(metric, key, value)
            metric.updated_at = datetime.utcnow()
        else:
            # Create new
            metric = ProgressMetric(
                id=uuid.uuid4(),
                user_id=user_id,
                metric_date=metric_date,
                period_type=period_type,
                **metrics
            )
            db.add(metric)

        await db.commit()
        await db.refresh(metric)
        return metric

    @staticmethod
    async def get_user_progress(
        db: AsyncSession,
        user_id: int,
        period_type: str = "daily",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 30
    ) -> List[ProgressMetric]:
        """
        Get progress metrics for a user over time.

        Args:
            db: Database session
            user_id: User ID
            period_type: daily, weekly, monthly
            start_date: Filter from date
            end_date: Filter to date
            limit: Max results

        Returns:
            List of ProgressMetric ordered by date
        """
        query = select(ProgressMetric).where(
            and_(
                ProgressMetric.user_id == user_id,
                ProgressMetric.period_type == period_type
            )
        )

        if start_date:
            query = query.where(ProgressMetric.metric_date >= start_date)
        if end_date:
            query = query.where(ProgressMetric.metric_date <= end_date)

        query = query.order_by(desc(ProgressMetric.metric_date)).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    # =============================================================================
    # Analytics & Aggregations
    # =============================================================================

    @staticmethod
    async def calculate_user_stats(
        db: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate aggregate statistics for a user.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary with statistics
        """
        since_date = datetime.utcnow() - timedelta(days=days)

        # Get sessions
        sessions_result = await db.execute(
            select(RealtimeSession).where(
                and_(
                    RealtimeSession.user_id == user_id,
                    RealtimeSession.started_at >= since_date
                )
            )
        )
        sessions = list(sessions_result.scalars().all())

        # Calculate total practice time
        total_practice_seconds = sum(
            s.duration_seconds for s in sessions if s.duration_seconds
        )

        # Get all analysis results for user's sessions
        session_ids = [s.id for s in sessions]
        if session_ids:
            analysis_query = select(AnalysisResult).join(Performance).where(
                Performance.session_id.in_(session_ids)
            )
            analysis_result = await db.execute(analysis_query)
            analyses = list(analysis_result.scalars().all())

            # Calculate averages
            if analyses:
                avg_pitch = sum(
                    a.pitch_accuracy for a in analyses if a.pitch_accuracy
                ) / len(analyses)
                avg_rhythm = sum(
                    a.rhythm_accuracy for a in analyses if a.rhythm_accuracy
                ) / len(analyses)
                avg_overall = sum(
                    a.overall_score for a in analyses if a.overall_score
                ) / len(analyses)
            else:
                avg_pitch = avg_rhythm = avg_overall = 0.0
        else:
            analyses = []
            avg_pitch = avg_rhythm = avg_overall = 0.0

        return {
            "total_sessions": len(sessions),
            "total_practice_hours": round(total_practice_seconds / 3600, 2),
            "total_analyses": len(analyses),
            "avg_pitch_accuracy": round(avg_pitch, 3),
            "avg_rhythm_accuracy": round(avg_rhythm, 3),
            "avg_overall_score": round(avg_overall, 3),
            "period_days": days
        }
