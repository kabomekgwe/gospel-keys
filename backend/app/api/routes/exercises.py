"""Exercise Library API Endpoints

RESTful API for accessing and managing the exercise library.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.exercise_library_service import get_exercise_library_service, ExerciseLibraryService
from app.services.template_parser import template_parser
from app.schemas.curriculum import (
    TemplateExercise,
    ExerciseTypeEnum,
    DifficultyLevelEnum,
    GetExerciseRequest,
    GetExerciseResponse,
    GenerateExercisesFromTemplateRequest,
    GenerateExercisesFromTemplateResponse,
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/library", response_model=GetExerciseResponse)
async def list_exercises(
    exercise_type: Optional[ExerciseTypeEnum] = None,
    difficulty: Optional[DifficultyLevelEnum] = None,
    tags: Optional[List[str]] = Query(None),
    curriculum_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List exercises with optional filters

    Args:
        exercise_type: Filter by exercise type
        difficulty: Filter by difficulty level
        tags: Filter by tags (match any)
        curriculum_id: Filter by curriculum
        limit: Maximum results (1-200)
        offset: Pagination offset
        db: Database session

    Returns:
        Paginated list of exercises
    """
    service = get_exercise_library_service(db)

    request = GetExerciseRequest(
        exercise_type=exercise_type,
        difficulty=difficulty,
        tags=tags or [],
        curriculum_id=curriculum_id,
        limit=limit
    )

    exercises, total_count = await service.search_exercises(request)

    return GetExerciseResponse(
        exercises=exercises,
        total_count=total_count
    )


@router.get("/library/{exercise_id}")
async def get_exercise(
    exercise_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific exercise by ID

    Args:
        exercise_id: Unique exercise identifier
        db: Database session

    Returns:
        Exercise details including MIDI/audio paths
    """
    service = get_exercise_library_service(db)
    exercise = await service.get_exercise_by_id(exercise_id)

    if not exercise:
        raise HTTPException(status_code=404, detail=f"Exercise {exercise_id} not found")

    return exercise


@router.get("/library/random")
async def get_random_exercise(
    exercise_type: Optional[ExerciseTypeEnum] = None,
    difficulty: Optional[DifficultyLevelEnum] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get a random exercise with optional filters

    Args:
        exercise_type: Filter by type
        difficulty: Filter by difficulty
        db: Database session

    Returns:
        Random exercise
    """
    service = get_exercise_library_service(db)
    exercise = await service.get_random_exercise(
        exercise_type=exercise_type,
        difficulty=difficulty
    )

    if not exercise:
        raise HTTPException(status_code=404, detail="No exercises found matching criteria")

    return exercise


@router.get("/library/by-type/{exercise_type}")
async def get_exercises_by_type(
    exercise_type: ExerciseTypeEnum,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get exercises of a specific type

    Args:
        exercise_type: Type to filter by
        limit: Maximum results
        db: Database session

    Returns:
        List of exercises of specified type
    """
    service = get_exercise_library_service(db)
    exercises = await service.get_exercises_by_type(exercise_type, limit=limit)

    return {
        "exercise_type": exercise_type.value,
        "exercises": exercises,
        "count": len(exercises)
    }


@router.get("/library/by-difficulty/{difficulty}")
async def get_exercises_by_difficulty(
    difficulty: DifficultyLevelEnum,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get exercises of a specific difficulty

    Args:
        difficulty: Difficulty level to filter by
        limit: Maximum results
        db: Database session

    Returns:
        List of exercises at specified difficulty
    """
    service = get_exercise_library_service(db)
    exercises = await service.get_exercises_by_difficulty(difficulty, limit=limit)

    return {
        "difficulty": difficulty.value,
        "exercises": exercises,
        "count": len(exercises)
    }


@router.get("/library/by-curriculum/{curriculum_id}")
async def get_exercises_by_curriculum(
    curriculum_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get all exercises for a curriculum

    Args:
        curriculum_id: Curriculum identifier
        limit: Maximum results
        offset: Pagination offset
        db: Database session

    Returns:
        List of exercises in curriculum
    """
    service = get_exercise_library_service(db)
    exercises = await service.get_exercises_by_curriculum(
        curriculum_id,
        limit=limit,
        offset=offset
    )

    return {
        "curriculum_id": curriculum_id,
        "exercises": exercises,
        "count": len(exercises)
    }


@router.post("/generate-from-template", response_model=GenerateExercisesFromTemplateResponse)
async def generate_from_template(
    request: GenerateExercisesFromTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Batch generate exercises from a curriculum template

    Args:
        request: Template file path and generation options
        db: Database session

    Returns:
        Generation statistics (success, errors, etc.)
    """
    from pathlib import Path
    import time

    start_time = time.time()

    try:
        # Parse template file
        template_path = Path(request.template_file)
        if not template_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Template file not found: {request.template_file}"
            )

        curriculums = template_parser.parse_template_file(template_path)

        if not curriculums:
            raise HTTPException(
                status_code=400,
                detail="No valid curriculums found in template file"
            )

        # Filter if specific curriculum requested
        if request.curriculum_id:
            curriculums = [c for c in curriculums if c.id == request.curriculum_id]
            if not curriculums:
                raise HTTPException(
                    status_code=404,
                    detail=f"Curriculum {request.curriculum_id} not found in template"
                )

        # Import into database
        service = get_exercise_library_service(db)
        total_exercises = 0
        errors = []

        for curriculum in curriculums:
            stats = await service.import_from_template(curriculum)
            total_exercises += stats["exercises_imported"]
            errors.extend(stats["errors"])

        elapsed = time.time() - start_time

        return GenerateExercisesFromTemplateResponse(
            success=len(errors) == 0,
            template_file=request.template_file,
            curriculums_processed=len(curriculums),
            exercises_generated=total_exercises,
            midi_files_created=0,  # TODO: Track actual MIDI generation
            audio_files_created=0,  # TODO: Track actual audio generation
            errors=errors,
            exercise_ids=[],  # TODO: Return actual IDs
            generation_time_seconds=elapsed
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/library/{exercise_id}/complete")
async def mark_exercise_complete(
    exercise_id: str,
    completion_time: Optional[float] = None,
    success: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Mark an exercise as completed and update stats

    Args:
        exercise_id: Exercise identifier
        completion_time: Time taken (seconds)
        success: Whether successfully completed
        db: Database session

    Returns:
        Updated exercise statistics
    """
    service = get_exercise_library_service(db)
    await service.update_usage_stats(exercise_id, completion_time, success)

    return {
        "exercise_id": exercise_id,
        "recorded": True,
        "completion_time": completion_time,
        "success": success
    }


@router.get("/stats")
async def get_library_stats(db: AsyncSession = Depends(get_db)):
    """Get overall exercise library statistics

    Args:
        db: Database session

    Returns:
        Library statistics (total exercises, by type, by difficulty, etc.)
    """
    # TODO: Implement with database aggregation queries
    return {
        "total_exercises": 0,
        "total_curriculums": 0,
        "exercises_by_type": {},
        "exercises_by_difficulty": {},
        "exercises_with_midi": 0,
        "exercises_with_audio": 0,
    }
