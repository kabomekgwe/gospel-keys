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

# === Phase 2: Tutorial & Performance Endpoints ===

@router.get("/lessons/{lesson_id}/tutorial")
async def get_lesson_tutorial(
    lesson_id: str,
    force_regenerate: bool = False,
    session: AsyncSession = Depends(get_async_session)
):
    """Get or generate tutorial for a lesson

    Args:
        lesson_id: Lesson ID
        force_regenerate: Force regeneration even if exists
        session: Database session

    Returns:
        Tutorial content JSON
    """
    from app.services.tutorial_service import tutorial_service

    try:
        # Get lesson
        result = await session.execute(
            select(CurriculumLesson).where(CurriculumLesson.id == lesson_id)
        )
        lesson = result.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # Check if tutorial exists
        if not force_regenerate and lesson.tutorial_content_json:
            tutorial = json.loads(lesson.tutorial_content_json)
            if tutorial:
                return tutorial

        # Generate tutorial
        tutorial = await tutorial_service.generate_lesson_tutorial(lesson, force_regenerate)

        # Save to database
        lesson.tutorial_content_json = json.dumps(tutorial)
        lesson.tutorial_generated_at = datetime.utcnow()
        await session.commit()

        return tutorial

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-analysis")
async def get_performance_analysis(
    lookback_days: int = 7,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get performance analysis for current user

    Args:
        lookback_days: Days to analyze (default: 7)
        current_user: Current authenticated user
        session: Database session

    Returns:
        Performance analysis data
    """
    from app.services.adaptive_curriculum_service import AdaptiveCurriculumService

    try:
        adaptive_service = AdaptiveCurriculumService(session)

        analysis = await adaptive_service.analyze_user_performance(
            user_id=current_user.id,
            lookback_days=lookback_days
        )

        return {
            "completion_rate": analysis.completion_rate,
            "avg_quality_score": analysis.avg_quality_score,
            "total_exercises": analysis.total_exercises,
            "reviewed_exercises": analysis.reviewed_exercises,
            "struggling_exercises_count": len(analysis.struggling_exercises),
            "mastered_exercises_count": len(analysis.mastered_exercises),
            "weak_skill_areas": analysis.weak_skill_areas,
            "strong_skill_areas": analysis.strong_skill_areas,
            "recommended_actions": analysis.recommended_actions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-adaptations")
async def apply_curriculum_adaptations(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Apply recommended adaptations to user's active curriculum

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        Applied changes
    """
    from app.services.adaptive_curriculum_service import AdaptiveCurriculumService

    try:
        # Get active curriculum
        result = await session.execute(
            select(Curriculum).where(
                and_(
                    Curriculum.user_id == current_user.id,
                    Curriculum.status == 'active'
                )
            ).order_by(Curriculum.created_at.desc())
        )
        curriculum = result.scalar_one_or_none()

        if not curriculum:
            raise HTTPException(status_code=404, detail="No active curriculum found")

        # Analyze and apply
        adaptive_service = AdaptiveCurriculumService(session)

        analysis = await adaptive_service.analyze_user_performance(
            user_id=current_user.id,
            lookback_days=7
        )

        if not analysis.recommended_actions:
            return {
                "message": "No adaptations needed at this time",
                "changes_applied": []
            }

        result = await adaptive_service.apply_adaptations(
            curriculum_id=curriculum.id,
            analysis=analysis
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Phase 3: Assessment Endpoints ===

@router.get("/assessments/current")
async def get_current_assessment(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get current active assessment for user

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        Active assessment or None
    """
    from app.database.curriculum_models import Assessment

    try:
        # Get most recent assessment without scores (not completed yet)
        result = await session.execute(
            select(Assessment)
            .where(
                and_(
                    Assessment.user_id == current_user.id,
                    Assessment.overall_score == None
                )
            )
            .order_by(Assessment.created_at.desc())
        )
        assessment = result.scalar_one_or_none()

        if not assessment:
            return None

        # Parse assessment content
        content = json.loads(assessment.ai_feedback_json)

        return {
            "id": assessment.id,
            "assessment_type": assessment.assessment_type,
            "curriculum_id": assessment.curriculum_id,
            "created_at": assessment.created_at.isoformat(),
            "content": content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assessments/{assessment_id}/submit")
async def submit_assessment(
    assessment_id: str,
    responses: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Submit assessment responses and trigger evaluation + feedback loop

    Args:
        assessment_id: Assessment ID
        responses: User responses dict
        current_user: Current authenticated user
        session: Database session

    Returns:
        Evaluation results with updated skill profile
    """
    from app.services.assessment_service import AssessmentService
    from app.services.curriculum_service import CurriculumService

    try:
        # Verify assessment belongs to user
        result = await session.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        if assessment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Evaluate assessment
        assessment_service = AssessmentService(session)
        evaluation = await assessment_service.evaluate_assessment(
            assessment_id=assessment_id,
            responses=responses
        )

        # Complete feedback loop (update profile + trigger adaptation)
        curriculum_service = CurriculumService(session)
        await curriculum_service.complete_assessment_feedback_loop(
            assessment_id=assessment_id,
            evaluation=evaluation
        )

        # Get updated skill profile
        result = await session.execute(
            select(UserSkillProfile).where(UserSkillProfile.user_id == current_user.id)
        )
        updated_profile = result.scalar_one_or_none()

        return {
            "evaluation": evaluation,
            "skill_profile": {
                "technical_ability": updated_profile.technical_ability,
                "theory_knowledge": updated_profile.theory_knowledge,
                "rhythm_competency": updated_profile.rhythm_competency,
                "ear_training": updated_profile.ear_training,
                "improvisation": updated_profile.improvisation,
                "updated_at": updated_profile.updated_at.isoformat()
            },
            "message": "Assessment evaluated and curriculum adapted"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-diagnostic-assessment")
async def generate_diagnostic_assessment(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Generate initial diagnostic assessment for user

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        Generated assessment
    """
    from app.services.assessment_service import AssessmentService

    try:
        assessment_service = AssessmentService(session)
        assessment = await assessment_service.generate_diagnostic_assessment(
            user_id=current_user.id
        )

        # Parse content
        content = json.loads(assessment.ai_feedback_json)

        return {
            "id": assessment.id,
            "assessment_type": assessment.assessment_type,
            "created_at": assessment.created_at.isoformat(),
            "content": content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/curricula/{curriculum_id}/check-milestones")
async def check_milestone_assessments(
    curriculum_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Check and trigger milestone assessments for a curriculum

    Args:
        curriculum_id: Curriculum ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        List of triggered assessment IDs
    """
    from app.services.curriculum_service import CurriculumService

    try:
        # Verify curriculum belongs to user
        result = await session.execute(
            select(Curriculum).where(Curriculum.id == curriculum_id)
        )
        curriculum = result.scalar_one_or_none()

        if not curriculum:
            raise HTTPException(status_code=404, detail="Curriculum not found")

        if curriculum.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Check and trigger milestones
        curriculum_service = CurriculumService(session)
        triggered = await curriculum_service.check_and_trigger_milestone_assessments(
            curriculum_id=curriculum_id
        )

        return {
            "curriculum_id": curriculum_id,
            "triggered_assessments": triggered,
            "count": len(triggered)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
