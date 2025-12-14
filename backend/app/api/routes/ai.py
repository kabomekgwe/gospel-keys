"""AI Generator API Routes"""

from datetime import datetime, timedelta
from typing import Dict
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import (
    ProgressionRequest, ProgressionResponse,
    ReharmonizationRequest, ReharmonizationResponse,
    VoicingRequest, VoicingResponse,
    VoiceLeadingRequest, VoiceLeadingResponse,
    ExerciseRequest, ExerciseResponse,
    SubstitutionRequest, SubstitutionResponse,
    GeneratorsListResponse,
    UsageStatsResponse, ModelUsageStats, TaskTypeStats,
)
from app.services.ai_generator import ai_generator_service
from app.database.session import get_db
from app.database.models import ModelUsageLog


router = APIRouter(prefix="/ai", tags=["AI Generator"])


@router.get("/generators", response_model=GeneratorsListResponse)
async def list_generators():
    """Get list of all available AI generators by category"""
    return ai_generator_service.get_available_generators()


@router.post("/progression", response_model=ProgressionResponse)
async def generate_progression(request: ProgressionRequest):
    """Generate a chord progression based on style, mood, and key"""
    try:
        return await ai_generator_service.generate_progression(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/reharmonization", response_model=ReharmonizationResponse)
async def generate_reharmonization(request: ReharmonizationRequest):
    """Get reharmonization suggestions for an existing progression"""
    try:
        return await ai_generator_service.generate_reharmonization(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reharmonization failed: {str(e)}")


@router.post("/voicing", response_model=VoicingResponse)
async def generate_voicings(request: VoicingRequest):
    """Generate multiple voicing options for a chord"""
    try:
        return await ai_generator_service.generate_voicings(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voicing generation failed: {str(e)}")


@router.post("/voice-leading", response_model=VoiceLeadingResponse)
async def optimize_voice_leading(request: VoiceLeadingRequest):
    """Find optimal voice leading between two chords"""
    try:
        return await ai_generator_service.optimize_voice_leading(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice leading failed: {str(e)}")


@router.post("/exercise", response_model=ExerciseResponse)
async def generate_exercise(request: ExerciseRequest):
    """Generate a practice exercise"""
    try:
        return await ai_generator_service.generate_exercise(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exercise generation failed: {str(e)}")


@router.post("/substitution", response_model=SubstitutionResponse)
async def get_substitutions(request: SubstitutionRequest):
    """Get chord substitution suggestions"""
    try:
        return await ai_generator_service.get_substitutions(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Substitution lookup failed: {str(e)}")


@router.get("/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    days: int = 7,
    session: AsyncSession = Depends(get_db)
):
    """Get AI usage statistics for the last N days

    Args:
        days: Number of days to look back (default: 7)
        session: Database session

    Returns:
        UsageStatsResponse with aggregated statistics by model and task type
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Query all logs in the date range
        query = select(ModelUsageLog).where(
            ModelUsageLog.created_at >= start_date,
            ModelUsageLog.created_at <= end_date
        )
        result = await session.execute(query)
        logs = result.scalars().all()

        # Aggregate by model
        model_stats: Dict[str, Dict] = {}
        for log in logs:
            if log.model not in model_stats:
                model_stats[log.model] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'total_input_tokens': 0,
                    'total_output_tokens': 0,
                    'total_cost_usd': Decimal('0'),
                    'total_latency_ms': 0,
                }

            stats = model_stats[log.model]
            stats['total_requests'] += 1
            stats['successful_requests'] += 1 if log.success else 0
            stats['failed_requests'] += 0 if log.success else 1
            stats['total_input_tokens'] += log.input_tokens
            stats['total_output_tokens'] += log.output_tokens
            stats['total_cost_usd'] += log.cost_usd
            stats['total_latency_ms'] += log.latency_ms

        # Aggregate by task type
        task_stats: Dict[str, Dict] = {}
        for log in logs:
            if log.task_type not in task_stats:
                task_stats[log.task_type] = {
                    'total_requests': 0,
                    'total_cost_usd': Decimal('0'),
                }

            task_stats[log.task_type]['total_requests'] += 1
            task_stats[log.task_type]['total_cost_usd'] += log.cost_usd

        # Build response models
        models_list = [
            ModelUsageStats(
                model=model,
                total_requests=stats['total_requests'],
                successful_requests=stats['successful_requests'],
                failed_requests=stats['failed_requests'],
                total_input_tokens=stats['total_input_tokens'],
                total_output_tokens=stats['total_output_tokens'],
                total_cost_usd=float(stats['total_cost_usd']),
                avg_latency_ms=stats['total_latency_ms'] / stats['total_requests'] if stats['total_requests'] > 0 else 0.0
            )
            for model, stats in model_stats.items()
        ]

        task_types_list = [
            TaskTypeStats(
                task_type=task_type,
                total_requests=stats['total_requests'],
                total_cost_usd=float(stats['total_cost_usd'])
            )
            for task_type, stats in task_stats.items()
        ]

        # Calculate totals
        total_requests = sum(stats['total_requests'] for stats in model_stats.values())
        total_cost_usd = float(sum(stats['total_cost_usd'] for stats in model_stats.values()))

        return UsageStatsResponse(
            period_days=days,
            total_requests=total_requests,
            total_cost_usd=total_cost_usd,
            models=models_list,
            task_types=task_types_list,
            date_range={
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")
