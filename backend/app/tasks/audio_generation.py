"""Celery tasks for background audio generation

Handles async MIDI and audio file generation for curriculum exercises.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.celery_app import celery_app
from app.core.config import settings
from app.database.curriculum_models import CurriculumExercise
from app.services.midi_generation_service import midi_generation_service
from app.services.audio_pipeline_service import audio_pipeline_service

logger = logging.getLogger(__name__)

# Create async database engine for tasks
engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.BASE_DIR}/piano_keys.db",
    echo=False
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=__import__('sqlalchemy.ext.asyncio', fromlist=['AsyncSession']).AsyncSession
)


@celery_app.task(bind=True, name="app.tasks.audio_generation.generate_exercise_audio_task")
def generate_exercise_audio_task(self, exercise_id: str, method: str = "both") -> Dict:
    """Background task to generate audio for a curriculum exercise

    Args:
        exercise_id: Exercise ID
        method: Audio generation method ("fluidsynth", "stable_audio", "both")

    Returns:
        Dict with status and file paths
    """
    import asyncio

    async def _generate():
        async with AsyncSessionLocal() as session:
            try:
                # Update status to generating
                result = await session.execute(
                    select(CurriculumExercise).where(CurriculumExercise.id == exercise_id)
                )
                exercise = result.scalar_one_or_none()

                if not exercise:
                    logger.error(f"Exercise not found: {exercise_id}")
                    return {"status": "error", "message": "Exercise not found"}

                # Update status
                exercise.audio_generation_status = "generating"
                await session.commit()

                logger.info(f"Generating audio for exercise {exercise_id} using {method}")

                # Generate MIDI
                midi_path = await midi_generation_service.generate_exercise_midi(exercise)
                exercise.midi_file_path = str(midi_path)
                await session.commit()

                # Generate audio
                audio_paths = await audio_pipeline_service.generate_exercise_audio(
                    exercise=exercise,
                    method=method,
                    midi_path=midi_path
                )

                # Update exercise with audio paths
                audio_files = {}
                if audio_paths.get("fluidsynth"):
                    audio_files["fluidsynth"] = str(audio_paths["fluidsynth"])
                if audio_paths.get("stable_audio"):
                    audio_files["stable_audio"] = str(audio_paths["stable_audio"])

                exercise.audio_files_json = json.dumps(audio_files)
                exercise.audio_generation_status = "complete"
                exercise.audio_generated_at = datetime.utcnow()
                await session.commit()

                logger.info(f"Audio generation complete for exercise {exercise_id}")

                return {
                    "status": "success",
                    "exercise_id": exercise_id,
                    "midi_path": str(midi_path),
                    "audio_files": audio_files
                }

            except Exception as e:
                logger.error(f"Audio generation failed for {exercise_id}: {e}")

                # Update status to failed
                try:
                    exercise.audio_generation_status = "failed"
                    await session.commit()
                except Exception:
                    pass

                return {
                    "status": "error",
                    "exercise_id": exercise_id,
                    "message": str(e)
                }

    # Run async code
    return asyncio.run(_generate())


@celery_app.task(name="app.tasks.audio_generation.generate_batch_audio_task")
def generate_batch_audio_task(exercise_ids: list[str], method: str = "both") -> Dict:
    """Generate audio for multiple exercises in batch

    Args:
        exercise_ids: List of exercise IDs
        method: Audio generation method

    Returns:
        Dict with batch status
    """
    results = []

    for exercise_id in exercise_ids:
        result = generate_exercise_audio_task.apply_async(
            args=[exercise_id, method],
            countdown=0
        )
        results.append({
            "exercise_id": exercise_id,
            "task_id": result.id
        })

    return {
        "status": "batch_queued",
        "total": len(exercise_ids),
        "tasks": results
    }


@celery_app.task(name="app.tasks.audio_generation.cleanup_failed_audio_tasks")
def cleanup_failed_audio_tasks() -> Dict:
    """Cleanup task to retry failed audio generation

    Runs daily via Celery Beat to retry exercises stuck in 'generating' state
    for more than 1 hour.
    """
    import asyncio

    async def _cleanup():
        async with AsyncSessionLocal() as session:
            try:
                # Find exercises stuck in generating state
                from datetime import timedelta

                one_hour_ago = datetime.utcnow() - timedelta(hours=1)

                result = await session.execute(
                    select(CurriculumExercise).where(
                        CurriculumExercise.audio_generation_status == "generating",
                        CurriculumExercise.created_at < one_hour_ago
                    )
                )
                stuck_exercises = result.scalars().all()

                logger.info(f"Found {len(stuck_exercises)} stuck audio generation tasks")

                for exercise in stuck_exercises:
                    # Mark as failed
                    exercise.audio_generation_status = "failed"

                await session.commit()

                return {
                    "status": "cleanup_complete",
                    "cleaned": len(stuck_exercises)
                }

            except Exception as e:
                logger.error(f"Cleanup task failed: {e}")
                return {"status": "error", "message": str(e)}

    return asyncio.run(_cleanup())
