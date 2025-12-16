"""Exercise Library Service

Service layer for managing the exercise library from curriculum templates.
Handles CRUD operations, search, filtering, and MIDI generation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import CurriculumLibrary, ExerciseLibrary, UserExerciseProgress
from app.schemas.curriculum import (
    TemplateCurriculum,
    TemplateExercise,
    ExerciseTypeEnum,
    DifficultyLevelEnum,
    GetExerciseRequest,
)


class ExerciseLibraryService:
    """Service for exercise library operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_exercise_by_id(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        """Get a single exercise by ID

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            Exercise data dictionary or None if not found
        """
        stmt = select(ExerciseLibrary).where(ExerciseLibrary.id == exercise_id)
        result = await self.db.execute(stmt)
        exercise = result.scalar_one_or_none()

        if not exercise:
            return None

        # Update access count
        await self.db.execute(
            update(ExerciseLibrary)
            .where(ExerciseLibrary.id == exercise_id)
            .values(times_accessed=ExerciseLibrary.times_accessed + 1)
        )
        await self.db.commit()

        return {
            "exercise_id": exercise.id,
            "curriculum_id": exercise.curriculum_id,
            "title": exercise.title,
            "description": exercise.description,
            "exercise_type": exercise.exercise_type,
            "difficulty": exercise.difficulty,
            "instructions": exercise.instructions,
            "midi_prompt": exercise.midi_prompt,
            "midi_file_path": exercise.midi_file_path,
            "audio_file_path": exercise.audio_file_path,
            "key": exercise.key,
            "time_signature": exercise.time_signature,
            "tempo_bpm": exercise.tempo_bpm,
            "tags": json.loads(exercise.tags_json) if exercise.tags_json else [],
            "content": json.loads(exercise.content_json) if exercise.content_json else {},
            "times_accessed": exercise.times_accessed,
            "avg_completion_time": exercise.avg_completion_time,
            "avg_score": exercise.avg_score,
        }

    async def search_exercises(self, request: GetExerciseRequest) -> Tuple[List[Dict[str, Any]], int]:
        """Search exercises with filters

        Args:
            request: Search parameters (type, difficulty, tags, etc.)

        Returns:
            Tuple of (exercises list, total count)
        """
        # Build base query
        stmt = select(ExerciseLibrary)

        # Apply filters
        conditions = []
        if request.exercise_type:
            conditions.append(ExerciseLibrary.exercise_type == request.exercise_type.value)
        if request.difficulty:
            conditions.append(ExerciseLibrary.difficulty == request.difficulty.value)
        if request.curriculum_id:
            conditions.append(ExerciseLibrary.curriculum_id == request.curriculum_id)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Tag filtering (check if JSON array contains any of the requested tags)
        if request.tags:
            tag_conditions = [
                ExerciseLibrary.tags_json.contains(json.dumps(tag))
                for tag in request.tags
            ]
            stmt = stmt.where(or_(*tag_conditions))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count_result = await self.db.execute(count_stmt)
        total_count = total_count_result.scalar()

        # Apply pagination
        stmt = stmt.limit(request.limit).offset(0)

        # Execute query
        result = await self.db.execute(stmt)
        exercises = result.scalars().all()

        # Convert to dictionaries
        return [
            {
                "exercise_id": ex.id,
                "curriculum_id": ex.curriculum_id,
                "title": ex.title,
                "description": ex.description,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "instructions": ex.instructions,
                "midi_file_path": ex.midi_file_path,
                "audio_file_path": ex.audio_file_path,
                "key": ex.key,
                "tags": json.loads(ex.tags_json) if ex.tags_json else [],
            }
            for ex in exercises
        ], total_count

    async def get_random_exercise(
        self,
        exercise_type: Optional[ExerciseTypeEnum] = None,
        difficulty: Optional[DifficultyLevelEnum] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a random exercise with optional filters

        Args:
            exercise_type: Filter by exercise type
            difficulty: Filter by difficulty level

        Returns:
            Random exercise or None if no matches
        """
        stmt = select(ExerciseLibrary).order_by(func.random())

        # Apply filters
        conditions = []
        if exercise_type:
            conditions.append(ExerciseLibrary.exercise_type == exercise_type.value)
        if difficulty:
            conditions.append(ExerciseLibrary.difficulty == difficulty.value)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.limit(1)

        result = await self.db.execute(stmt)
        exercise = result.scalar_one_or_none()

        if not exercise:
            return None

        return {
            "exercise_id": exercise.id,
            "curriculum_id": exercise.curriculum_id,
            "title": exercise.title,
            "description": exercise.description,
            "exercise_type": exercise.exercise_type,
            "difficulty": exercise.difficulty,
            "instructions": exercise.instructions,
            "midi_file_path": exercise.midi_file_path,
            "audio_file_path": exercise.audio_file_path,
            "key": exercise.key,
            "tags": json.loads(exercise.tags_json) if exercise.tags_json else [],
        }

    async def import_from_template(
        self,
        curriculum: TemplateCurriculum
    ) -> Dict[str, Any]:
        """Import a curriculum template into the exercise library

        Args:
            curriculum: Parsed curriculum template

        Returns:
            Import statistics (curricula created, exercises imported, etc.)
        """
        stats = {
            "curriculum_id": curriculum.id,
            "title": curriculum.title,
            "exercises_imported": 0,
            "exercises_with_midi": 0,
            "errors": []
        }

        try:
            # 1. Create/Update curriculum entry
            curriculum_entry = CurriculumLibrary(
                id=curriculum.id,
                title=curriculum.title,
                description=curriculum.description,
                genre=getattr(curriculum, 'genre', None),
                difficulty_level=getattr(curriculum, 'difficulty_level', None),
                estimated_duration_weeks=getattr(curriculum, 'estimated_duration_weeks', None),
                source_file=curriculum.source_file,
                ai_provider=curriculum.ai_provider,
                tags_json=json.dumps(getattr(curriculum, 'tags', [])),
                prerequisites_json=json.dumps(getattr(curriculum, 'prerequisites', [])),
                learning_objectives_json=json.dumps(getattr(curriculum, 'learning_objectives', [])),
                modules_json=json.dumps([
                    {
                        "id": module.id,
                        "title": module.title,
                        "lessons": [
                            {
                                "id": lesson.id,
                                "title": lesson.title,
                                "exercises": [ex.dict() for ex in lesson.exercises]
                            }
                            for lesson in module.lessons
                        ]
                    }
                    for module in curriculum.modules
                ])
            )

            # Merge (upsert) curriculum
            await self.db.merge(curriculum_entry)

            # 2. Import exercises
            for module in curriculum.modules:
                for lesson in module.lessons:
                    for exercise in lesson.exercises:
                        try:
                            exercise_id = f"{curriculum.id}_{module.id}_{lesson.id}_{exercise.id}"

                            exercise_entry = ExerciseLibrary(
                                id=exercise_id,
                                curriculum_id=curriculum.id,
                                title=exercise.title,
                                description=getattr(exercise, 'description', None),
                                exercise_type=exercise.exercise_type.value if hasattr(exercise.exercise_type, 'value') else exercise.exercise_type,
                                difficulty=exercise.difficulty.value if hasattr(exercise.difficulty, 'value') else exercise.difficulty,
                                instructions=getattr(exercise, 'instructions', None),
                                midi_prompt=getattr(exercise, 'midi_prompt', None),
                                key=getattr(exercise.content, 'key', None) if exercise.content else None,
                                time_signature=getattr(exercise.content, 'time_signature', None) if exercise.content else None,
                                tempo_bpm=getattr(exercise.content, 'tempo_bpm', None) if exercise.content else None,
                                tags_json=json.dumps(getattr(exercise, 'tags', [])),
                                content_json=json.dumps(exercise.content.dict() if exercise.content else {})
                            )

                            await self.db.merge(exercise_entry)
                            stats["exercises_imported"] += 1

                            if exercise.midi_prompt:
                                stats["exercises_with_midi"] += 1

                        except Exception as ex_error:
                            stats["errors"].append(f"Exercise {exercise.id}: {str(ex_error)}")

            await self.db.commit()

        except Exception as e:
            stats["errors"].append(str(e))
            await self.db.rollback()

        return stats

    async def get_exercises_by_curriculum(
        self,
        curriculum_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all exercises for a curriculum

        Args:
            curriculum_id: Curriculum identifier
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of exercises
        """
        stmt = (
            select(ExerciseLibrary)
            .where(ExerciseLibrary.curriculum_id == curriculum_id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        exercises = result.scalars().all()

        return [
            {
                "exercise_id": ex.id,
                "curriculum_id": ex.curriculum_id,
                "title": ex.title,
                "description": ex.description,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "midi_file_path": ex.midi_file_path,
                "audio_file_path": ex.audio_file_path,
            }
            for ex in exercises
        ]

    async def get_exercises_by_type(
        self,
        exercise_type: ExerciseTypeEnum,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get exercises of a specific type

        Args:
            exercise_type: Type to filter by
            limit: Maximum number of results

        Returns:
            List of exercises
        """
        stmt = (
            select(ExerciseLibrary)
            .where(ExerciseLibrary.exercise_type == exercise_type.value)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        exercises = result.scalars().all()

        return [
            {
                "exercise_id": ex.id,
                "title": ex.title,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "midi_file_path": ex.midi_file_path,
            }
            for ex in exercises
        ]

    async def get_exercises_by_difficulty(
        self,
        difficulty: DifficultyLevelEnum,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get exercises of a specific difficulty

        Args:
            difficulty: Difficulty level to filter by
            limit: Maximum number of results

        Returns:
            List of exercises
        """
        stmt = (
            select(ExerciseLibrary)
            .where(ExerciseLibrary.difficulty == difficulty.value)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        exercises = result.scalars().all()

        return [
            {
                "exercise_id": ex.id,
                "title": ex.title,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "midi_file_path": ex.midi_file_path,
            }
            for ex in exercises
        ]

    async def update_usage_stats(
        self,
        exercise_id: str,
        completion_time: Optional[float] = None,
        success: bool = True
    ) -> None:
        """Update exercise usage statistics

        Args:
            exercise_id: Exercise to update
            completion_time: Time taken to complete (seconds)
            success: Whether exercise was completed successfully
        """
        # Get current exercise stats
        stmt = select(ExerciseLibrary).where(ExerciseLibrary.id == exercise_id)
        result = await self.db.execute(stmt)
        exercise = result.scalar_one_or_none()

        if not exercise:
            return

        # Update access count
        exercise.times_accessed += 1

        # Update average completion time if provided
        if completion_time is not None:
            if exercise.avg_completion_time is None:
                exercise.avg_completion_time = completion_time
            else:
                # Running average
                total_time = exercise.avg_completion_time * (exercise.times_accessed - 1)
                exercise.avg_completion_time = (total_time + completion_time) / exercise.times_accessed

        await self.db.commit()


def get_exercise_library_service(db: AsyncSession) -> ExerciseLibraryService:
    """Factory function for exercise library service

    Args:
        db: Database session

    Returns:
        ExerciseLibraryService instance
    """
    return ExerciseLibraryService(db)
