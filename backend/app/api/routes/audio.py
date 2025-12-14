"""Audio API Routes for Exercise Audio Generation

Handles audio file retrieval, streaming, and generation requests.
"""

import json
import logging
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.database.curriculum_models import CurriculumExercise
from app.tasks.audio_generation import generate_exercise_audio_task
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audio", tags=["Audio"])


# === Request/Response Models ===

class AudioGenerationRequest(BaseModel):
    """Request to generate audio for an exercise"""
    method: Literal["fluidsynth", "stable_audio", "both"] = Field(
        default="both",
        description="Audio generation method"
    )


class AudioGenerationResponse(BaseModel):
    """Response for audio generation request"""
    status: str = Field(..., description="pending, generating, complete, failed")
    exercise_id: str
    task_id: str | None = None
    message: str | None = None


class AudioStatusResponse(BaseModel):
    """Audio generation status for an exercise"""
    exercise_id: str
    status: str = Field(..., description="pending, generating, complete, failed")
    midi_file: str | None = None
    audio_files: dict[str, str] = Field(default_factory=dict)
    generated_at: str | None = None


# === Endpoints ===

@router.get("/exercises/{exercise_id}/audio", response_class=FileResponse)
async def get_exercise_audio(
    exercise_id: str,
    method: Literal["fluidsynth", "stable_audio"] = "fluidsynth",
    session: AsyncSession = Depends(get_db)
):
    """Get audio file for an exercise

    Args:
        exercise_id: Exercise ID
        method: Which audio file to retrieve
        session: Database session

    Returns:
        Audio file (WAV format)
    """
    try:
        # Get exercise from database
        result = await session.execute(
            select(CurriculumExercise).where(CurriculumExercise.id == exercise_id)
        )
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Check if audio exists
        if exercise.audio_generation_status != "complete":
            raise HTTPException(
                status_code=404,
                detail=f"Audio not ready. Status: {exercise.audio_generation_status}"
            )

        # Get audio file path
        audio_files = json.loads(exercise.audio_files_json)
        audio_path = audio_files.get(method)

        if not audio_path:
            raise HTTPException(
                status_code=404,
                detail=f"Audio file not found for method: {method}"
            )

        # Check if file exists
        file_path = Path(audio_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found on disk")

        # Return audio file
        return FileResponse(
            path=str(file_path),
            media_type="audio/wav",
            filename=f"{exercise_id}_{method}.wav"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audio for {exercise_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises/{exercise_id}/midi", response_class=FileResponse)
async def get_exercise_midi(
    exercise_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get MIDI file for an exercise

    Args:
        exercise_id: Exercise ID
        session: Database session

    Returns:
        MIDI file
    """
    try:
        # Get exercise from database
        result = await session.execute(
            select(CurriculumExercise).where(CurriculumExercise.id == exercise_id)
        )
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if not exercise.midi_file_path:
            raise HTTPException(status_code=404, detail="MIDI file not generated yet")

        # Check if file exists
        file_path = Path(exercise.midi_file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="MIDI file not found on disk")

        # Return MIDI file
        return FileResponse(
            path=str(file_path),
            media_type="audio/midi",
            filename=f"{exercise_id}.mid"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MIDI for {exercise_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises/{exercise_id}/status", response_model=AudioStatusResponse)
async def get_audio_status(
    exercise_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get audio generation status for an exercise

    Args:
        exercise_id: Exercise ID
        session: Database session

    Returns:
        AudioStatusResponse with current status
    """
    try:
        # Get exercise from database
        result = await session.execute(
            select(CurriculumExercise).where(CurriculumExercise.id == exercise_id)
        )
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Parse audio files
        audio_files = {}
        if exercise.audio_files_json:
            try:
                audio_files = json.loads(exercise.audio_files_json)
            except json.JSONDecodeError:
                pass

        return AudioStatusResponse(
            exercise_id=exercise.id,
            status=exercise.audio_generation_status,
            midi_file=exercise.midi_file_path,
            audio_files=audio_files,
            generated_at=exercise.audio_generated_at.isoformat() if exercise.audio_generated_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get status for {exercise_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/generate", response_model=AudioGenerationResponse)
async def generate_audio(
    exercise_id: str,
    request: AudioGenerationRequest = AudioGenerationRequest(),
    session: AsyncSession = Depends(get_db)
):
    """Queue audio generation for an exercise

    Args:
        exercise_id: Exercise ID
        request: Generation request parameters
        session: Database session

    Returns:
        AudioGenerationResponse with task ID
    """
    try:
        # Verify exercise exists
        result = await session.execute(
            select(CurriculumExercise).where(CurriculumExercise.id == exercise_id)
        )
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Check if already generating
        if exercise.audio_generation_status == "generating":
            return AudioGenerationResponse(
                status="generating",
                exercise_id=exercise_id,
                message="Audio generation already in progress"
            )

        # Queue Celery task
        task = generate_exercise_audio_task.apply_async(
            args=[exercise_id, request.method],
            countdown=0
        )

        # Update status to generating
        exercise.audio_generation_status = "generating"
        await session.commit()

        logger.info(f"Queued audio generation for {exercise_id}: task {task.id}")

        return AudioGenerationResponse(
            status="generating",
            exercise_id=exercise_id,
            task_id=task.id,
            message="Audio generation queued successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue audio generation for {exercise_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/regenerate", response_model=AudioGenerationResponse)
async def regenerate_audio(
    exercise_id: str,
    request: AudioGenerationRequest = AudioGenerationRequest(),
    session: AsyncSession = Depends(get_db)
):
    """Regenerate audio for an exercise (overwrite existing)

    Args:
        exercise_id: Exercise ID
        request: Generation request parameters
        session: Database session

    Returns:
        AudioGenerationResponse with task ID
    """
    try:
        # Verify exercise exists
        result = await session.execute(
            select(CurriculumExercise).where(CurriculumExercise.id == exercise_id)
        )
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Reset status and queue task
        exercise.audio_generation_status = "pending"
        await session.commit()

        # Queue Celery task
        task = generate_exercise_audio_task.apply_async(
            args=[exercise_id, request.method],
            countdown=0
        )

        # Update status
        exercise.audio_generation_status = "generating"
        await session.commit()

        logger.info(f"Queued audio regeneration for {exercise_id}: task {task.id}")

        return AudioGenerationResponse(
            status="generating",
            exercise_id=exercise_id,
            task_id=task.id,
            message="Audio regeneration queued successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate audio for {exercise_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
