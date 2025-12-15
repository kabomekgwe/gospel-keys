"""
Real-Time Analysis API Routes
STORY-3.2: Database Schema & Progress Tracking

Endpoints for Phase 3 real-time performance analysis:
- Session management (start, end, list)
- Performance recording
- Analysis results storage
- Progress metrics and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.database.session import get_db
from app.services.realtime_analysis_service import RealtimeAnalysisService
from app.schemas.realtime_analysis import (
    SessionCreate,
    SessionResponse,
    PerformanceCreate,
    PerformanceResponse,
    AnalysisResultCreate,
    AnalysisResultResponse,
    ProgressMetricResponse,
    UserStatsResponse
)

router = APIRouter(prefix="/realtime", tags=["realtime-analysis"])

# =============================================================================
# Session Endpoints
# =============================================================================

@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new real-time practice session.

    This marks the start of a practice session with WebSocket analysis.
    """
    session = await RealtimeAnalysisService.create_session(
        db=db,
        user_id=session_data.user_id,
        piece_name=session_data.piece_name,
        genre=session_data.genre,
        target_tempo=session_data.target_tempo,
        difficulty_level=session_data.difficulty_level,
        websocket_session_id=session_data.websocket_session_id
    )
    return session


@router.patch("/sessions/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    End a practice session and calculate duration.

    Marks the session as completed and computes total practice time.
    """
    session = await RealtimeAnalysisService.end_session(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get session details by ID."""
    session = await RealtimeAnalysisService.get_session(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.get("/users/{user_id}/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(active|completed|abandoned)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all practice sessions for a user.

    Supports pagination and filtering by status.
    """
    sessions = await RealtimeAnalysisService.get_user_sessions(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        status=status
    )
    return sessions


@router.patch("/sessions/{session_id}/chunks")
async def update_chunks_processed(
    session_id: uuid.UUID,
    chunks: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Update chunks processed counter for a session.

    Called periodically during WebSocket analysis to track progress.
    """
    await RealtimeAnalysisService.update_chunks_processed(db, session_id, chunks)
    return {"status": "success", "chunks_added": chunks}


# =============================================================================
# Performance Endpoints
# =============================================================================

@router.post("/performances", response_model=PerformanceResponse, status_code=201)
async def create_performance(
    performance_data: PerformanceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a performance recording.

    Stores metadata about an audio/MIDI recording within a session.
    """
    performance = await RealtimeAnalysisService.create_performance(
        db=db,
        session_id=performance_data.session_id,
        audio_path=performance_data.audio_path,
        midi_path=performance_data.midi_path,
        sample_rate=performance_data.sample_rate,
        audio_format=performance_data.audio_format,
        notes=performance_data.notes
    )
    return performance


@router.get("/sessions/{session_id}/performances", response_model=List[PerformanceResponse])
async def get_session_performances(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all performance recordings for a session."""
    performances = await RealtimeAnalysisService.get_session_performances(db, session_id)
    return performances


# =============================================================================
# Analysis Result Endpoints
# =============================================================================

@router.post("/analysis-results", response_model=AnalysisResultResponse, status_code=201)
async def create_analysis_result(
    analysis_data: AnalysisResultCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Store analysis results for a performance.

    Contains pitch/rhythm/dynamics accuracy scores and AI feedback.
    """
    result = await RealtimeAnalysisService.create_analysis_result(
        db=db,
        performance_id=analysis_data.performance_id,
        pitch_accuracy=analysis_data.pitch_accuracy,
        rhythm_accuracy=analysis_data.rhythm_accuracy,
        dynamics_range=analysis_data.dynamics_range,
        overall_score=analysis_data.overall_score,
        feedback_json=analysis_data.feedback_json,
        avg_pitch_deviation_cents=analysis_data.avg_pitch_deviation_cents,
        timing_consistency=analysis_data.timing_consistency,
        tempo_stability=analysis_data.tempo_stability,
        note_accuracy_rate=analysis_data.note_accuracy_rate,
        total_notes_detected=analysis_data.total_notes_detected,
        total_onsets_detected=analysis_data.total_onsets_detected,
        total_dynamics_events=analysis_data.total_dynamics_events,
        difficulty_estimate=analysis_data.difficulty_estimate,
        genre_match_score=analysis_data.genre_match_score,
        analysis_engine_version=analysis_data.analysis_engine_version,
        processing_time_ms=analysis_data.processing_time_ms
    )
    return result


@router.get("/performances/{performance_id}/analysis", response_model=List[AnalysisResultResponse])
async def get_performance_analysis(
    performance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all analysis results for a performance."""
    results = await RealtimeAnalysisService.get_performance_analysis(db, performance_id)
    return results


@router.get("/performances/{performance_id}/analysis/latest", response_model=AnalysisResultResponse)
async def get_latest_analysis(
    performance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent analysis result for a performance."""
    result = await RealtimeAnalysisService.get_latest_analysis(db, performance_id)

    if not result:
        raise HTTPException(status_code=404, detail="No analysis found for this performance")

    return result


# =============================================================================
# Progress Metrics & Analytics Endpoints
# =============================================================================

@router.get("/users/{user_id}/progress", response_model=List[ProgressMetricResponse])
async def get_user_progress(
    user_id: int,
    period_type: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get progress metrics for a user over time.

    Returns aggregated practice statistics by day, week, or month.
    """
    metrics = await RealtimeAnalysisService.get_user_progress(
        db=db,
        user_id=user_id,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return metrics


@router.get("/users/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregate statistics for a user.

    Calculates totals and averages for practice sessions and performance metrics.
    """
    stats = await RealtimeAnalysisService.calculate_user_stats(
        db=db,
        user_id=user_id,
        days=days
    )
    return stats


# =============================================================================
# Batch Operations (Optional - for efficiency)
# =============================================================================

@router.get("/sessions/{session_id}/complete-data")
async def get_session_complete_data(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete session data including all performances and analysis results.

    Useful for displaying a complete session summary in the UI.
    """
    # Get session
    session = await RealtimeAnalysisService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get performances
    performances = await RealtimeAnalysisService.get_session_performances(db, session_id)

    # Get analysis results for each performance
    performances_with_analysis = []
    for perf in performances:
        analyses = await RealtimeAnalysisService.get_performance_analysis(db, perf.id)
        performances_with_analysis.append({
            "performance": perf,
            "analysis_results": analyses
        })

    return {
        "session": session,
        "performances": performances_with_analysis,
        "total_performances": len(performances),
        "total_analyses": sum(len(p["analysis_results"]) for p in performances_with_analysis)
    }
