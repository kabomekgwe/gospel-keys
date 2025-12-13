"""Curriculum API Routes

Endpoints for curriculum management, assessments, and daily practice.
"""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.database.curriculum_models import (
    UserSkillProfile,
    Curriculum,
    CurriculumModule,
    CurriculumLesson,
    CurriculumExercise,
)
from app.services.curriculum_service import CurriculumService
from app.schemas.curriculum import (
    AssessmentSubmission,
    UserSkillProfileResponse,
    CurriculumGenerateRequest,
    CurriculumResponse,
    CurriculumSummary,
    CurriculumModuleResponse,
    CurriculumLessonResponse,
    CurriculumExerciseResponse,
    ExerciseCompleteRequest,
    DailyPracticeQueue,
    DailyPracticeItem,
    SkillLevels,
    StyleFamiliarity,
    LessonSummary,
    ModuleSummary,
    ExerciseContent,
)

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])


# Dependency to get curriculum service
async def get_curriculum_service(
    db: AsyncSession = Depends(get_async_session)
) -> CurriculumService:
    return CurriculumService(db)


# Helper to get current user ID (simplified - in production, use auth)
def get_current_user_id() -> int:
    # TODO: Integrate with real auth system
    return 1


# =============================================================================
# User Skill Profile Endpoints
# =============================================================================

@router.get("/profile", response_model=UserSkillProfileResponse)
async def get_skill_profile(
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Get user's skill profile"""
    profile = await service.get_or_create_skill_profile(user_id)
    return _profile_to_response(profile)


@router.post("/assessment", response_model=UserSkillProfileResponse)
async def submit_assessment(
    assessment: AssessmentSubmission,
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Submit user assessment and update skill profile"""
    assessment_data = {
        'skill_levels': assessment.skill_levels.model_dump(),
        'style_familiarity': assessment.style_familiarity.model_dump(),
        'primary_goal': assessment.primary_goal,
        'interests': assessment.interests,
        'weekly_practice_hours': assessment.weekly_practice_hours,
        'learning_velocity': assessment.learning_velocity,
        'preferred_style': assessment.preferred_style,
    }
    
    profile = await service.update_skill_profile(user_id, assessment_data)
    return _profile_to_response(profile)


def _profile_to_response(profile: UserSkillProfile) -> UserSkillProfileResponse:
    """Convert profile model to response schema"""
    style_fam = json.loads(profile.style_familiarity_json or '{}')
    interests = json.loads(profile.interests_json or '[]')
    
    return UserSkillProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        skill_levels=SkillLevels(
            technical_ability=profile.technical_ability,
            theory_knowledge=profile.theory_knowledge,
            rhythm_competency=profile.rhythm_competency,
            ear_training=profile.ear_training,
            improvisation=profile.improvisation,
        ),
        style_familiarity=StyleFamiliarity(**style_fam),
        primary_goal=profile.primary_goal,
        interests=interests,
        weekly_practice_hours=profile.weekly_practice_hours,
        learning_velocity=profile.learning_velocity,
        preferred_style=profile.preferred_style,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


# =============================================================================
# Curriculum CRUD Endpoints
# =============================================================================

@router.post("/generate", response_model=CurriculumResponse)
async def generate_curriculum(
    request: CurriculumGenerateRequest,
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Generate a new personalized curriculum"""
    curriculum = await service.generate_curriculum(
        user_id=user_id,
        title=request.title,
        duration_weeks=request.duration_weeks,
    )
    return await _curriculum_to_response(curriculum, service)


@router.get("/", response_model=Optional[CurriculumResponse])
async def get_active_curriculum(
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Get user's active curriculum"""
    curriculum = await service.get_active_curriculum(user_id)
    if not curriculum:
        return None
    return await _curriculum_to_response(curriculum, service)


@router.get("/{curriculum_id}", response_model=CurriculumResponse)
async def get_curriculum(
    curriculum_id: str,
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Get curriculum by ID with full details"""
    curriculum = await service.get_curriculum_with_details(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return await _curriculum_to_response(curriculum, service)


async def _curriculum_to_response(
    curriculum: Curriculum, 
    service: CurriculumService
) -> CurriculumResponse:
    """Convert curriculum model to response schema"""
    # Load full curriculum if modules not loaded
    if not curriculum.modules:
        curriculum = await service.get_curriculum_with_details(curriculum.id)
    
    module_summaries = []
    for module in curriculum.modules:
        lesson_count = len(module.lessons) if module.lessons else 0
        module_summaries.append(ModuleSummary(
            id=module.id,
            title=module.title,
            theme=module.theme,
            start_week=module.start_week,
            end_week=module.end_week,
            completion_percentage=module.completion_percentage,
            lesson_count=lesson_count,
        ))
    
    return CurriculumResponse(
        id=curriculum.id,
        user_id=curriculum.user_id,
        title=curriculum.title,
        description=curriculum.description,
        duration_weeks=curriculum.duration_weeks,
        current_week=curriculum.current_week,
        status=curriculum.status,
        ai_model_used=curriculum.ai_model_used,
        modules=module_summaries,
        created_at=curriculum.created_at,
        updated_at=curriculum.updated_at,
    )


# =============================================================================
# Module & Lesson Endpoints
# =============================================================================

@router.get("/modules/{module_id}", response_model=CurriculumModuleResponse)
async def get_module(
    module_id: str,
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Get module with lessons"""
    module = await service.get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return _module_to_response(module)


def _module_to_response(module: CurriculumModule) -> CurriculumModuleResponse:
    """Convert module model to response schema"""
    lesson_summaries = []
    for lesson in module.lessons:
        exercise_count = len(lesson.exercises) if lesson.exercises else 0
        completed_count = sum(1 for ex in lesson.exercises if ex.is_mastered) if lesson.exercises else 0
        lesson_summaries.append(LessonSummary(
            id=lesson.id,
            title=lesson.title,
            week_number=lesson.week_number,
            is_completed=lesson.is_completed,
            exercise_count=exercise_count,
            completed_exercises=completed_count,
        ))
    
    return CurriculumModuleResponse(
        id=module.id,
        curriculum_id=module.curriculum_id,
        title=module.title,
        description=module.description,
        theme=module.theme,
        order_index=module.order_index,
        start_week=module.start_week,
        end_week=module.end_week,
        prerequisites=json.loads(module.prerequisites_json or '[]'),
        outcomes=json.loads(module.outcomes_json or '[]'),
        completion_percentage=module.completion_percentage,
        lessons=lesson_summaries,
        created_at=module.created_at,
    )


@router.get("/lessons/{lesson_id}", response_model=CurriculumLessonResponse)
async def get_lesson(
    lesson_id: str,
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Get lesson with exercises"""
    lesson = await service.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return _lesson_to_response(lesson)


def _lesson_to_response(lesson: CurriculumLesson) -> CurriculumLessonResponse:
    """Convert lesson model to response schema"""
    exercises = [_exercise_to_response(ex) for ex in lesson.exercises]
    
    return CurriculumLessonResponse(
        id=lesson.id,
        module_id=lesson.module_id,
        title=lesson.title,
        description=lesson.description,
        week_number=lesson.week_number,
        theory_content=json.loads(lesson.theory_content_json or '{}'),
        concepts=json.loads(lesson.concepts_json or '[]'),
        estimated_duration_minutes=lesson.estimated_duration_minutes,
        is_completed=lesson.is_completed,
        completed_at=lesson.completed_at,
        exercises=exercises,
        created_at=lesson.created_at,
    )


# =============================================================================
# Exercise Endpoints
# =============================================================================

def _exercise_to_response(exercise: CurriculumExercise) -> CurriculumExerciseResponse:
    """Convert exercise model to response schema"""
    content_dict = json.loads(exercise.content_json or '{}')
    
    return CurriculumExerciseResponse(
        id=exercise.id,
        lesson_id=exercise.lesson_id,
        title=exercise.title,
        description=exercise.description,
        order_index=exercise.order_index,
        exercise_type=exercise.exercise_type,
        content=ExerciseContent(**content_dict),
        difficulty=exercise.difficulty,
        estimated_duration_minutes=exercise.estimated_duration_minutes,
        target_bpm=exercise.target_bpm,
        practice_count=exercise.practice_count,
        best_score=exercise.best_score,
        is_mastered=exercise.is_mastered,
        mastered_at=exercise.mastered_at,
        next_review_at=exercise.next_review_at,
        last_reviewed_at=exercise.last_reviewed_at,
        created_at=exercise.created_at,
    )


@router.post("/exercises/{exercise_id}/complete", response_model=CurriculumExerciseResponse)
async def complete_exercise(
    exercise_id: str,
    request: ExerciseCompleteRequest,
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Mark exercise as completed with quality rating"""
    try:
        exercise = await service.complete_exercise(
            exercise_id=exercise_id,
            quality=request.quality,
            score=request.score,
            duration_seconds=request.duration_seconds,
        )
        return _exercise_to_response(exercise)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# Daily Practice Endpoints
# =============================================================================

@router.get("/daily", response_model=DailyPracticeQueue)
async def get_daily_practice(
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Get today's practice queue"""
    curriculum = await service.get_active_curriculum(user_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="No active curriculum found")
    
    practice_items = await service.get_daily_practice(user_id)
    
    items = []
    total_minutes = 0
    overdue_count = 0
    new_count = 0
    
    for item in practice_items:
        ex = item['exercise']
        total_minutes += ex.estimated_duration_minutes
        
        if item['priority'] == 1:
            overdue_count += 1
        elif item['priority'] == 3:
            new_count += 1
        
        items.append(DailyPracticeItem(
            exercise=_exercise_to_response(ex),
            lesson_title=item['lesson_title'],
            module_title=item['module_title'],
            priority=item['priority'],
        ))
    
    return DailyPracticeQueue(
        date=datetime.utcnow(),
        curriculum_id=curriculum.id,
        curriculum_title=curriculum.title,
        current_week=curriculum.current_week,
        items=items,
        total_estimated_minutes=total_minutes,
        overdue_count=overdue_count,
        new_count=new_count,
    )
