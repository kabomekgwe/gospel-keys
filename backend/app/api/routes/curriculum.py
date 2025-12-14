"""Curriculum API Routes

Endpoints for curriculum management, assessments, and daily practice.
"""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models import User
from app.database.session import get_db
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
    CurriculumDefaultRequest,
    CurriculumResponse,
    CurriculumSummary,
    CurriculumModuleResponse,
    CurriculumLessonResponse,
    CurriculumExerciseResponse,
    ExerciseCompleteRequest,
    AddLickToPracticeRequest,
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
    db: AsyncSession = Depends(get_db)
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


@router.post("/default", response_model=CurriculumResponse)
async def create_default_curriculum(
    request: CurriculumDefaultRequest,
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Create a new curriculum from a default template"""
    try:
        curriculum = await service.create_default_curriculum(
            user_id=user_id,
            template_key=request.template_key
        )
        return await _curriculum_to_response(curriculum, service)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates", response_model=List[dict])
async def list_curriculum_templates():
    """List available default curriculum templates"""
    from app.services.curriculum_defaults import DEFAULT_CURRICULUMS
    return [
        {
            "key": key,
            "title": template["title"],
            "description": template["description"],
            "weeks": sum(
                (m.get('end_week', 4) - m.get('start_week', 1) + 1) 
                for m in template.get('modules', [])
            )
        }
        for key, template in DEFAULT_CURRICULUMS.items()
    ]




@router.get("/list", response_model=List[CurriculumSummary])
async def list_user_curriculums(
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """List all curriculums for the user"""
    curriculums = await service.get_user_curriculums(user_id)
    return [await _curriculum_to_summary(c, service) for c in curriculums]


@router.post("/{curriculum_id}/activate", response_model=CurriculumResponse)
async def activate_curriculum(
    curriculum_id: str,
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service)
):
    """Set a curriculum as active"""
    try:
        curriculum = await service.activate_curriculum(curriculum_id, user_id)
        # We need details for the response
        full_curriculum = await service.get_curriculum_with_details(curriculum.id)
        return await _curriculum_to_response(full_curriculum, service)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
    session: AsyncSession = Depends(get_db)
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
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
    responses: dict = Body(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
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

        if not updated_profile:
            raise HTTPException(status_code=404, detail="User skill profile not found")

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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
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


# =============================================================================
# AI Coach Endpoints
# =============================================================================

@router.post("/ai-coach/chat")
async def chat_with_ai_coach(
    message: dict,
    user_id: int = Depends(get_current_user_id),
    service: CurriculumService = Depends(get_curriculum_service),
    session: AsyncSession = Depends(get_db)
):
    """Chat with AI coach for personalized guidance

    Args:
        message: Dict with 'text' (user message) and optional 'context' (current exercise, lesson, etc.)
        user_id: Current user ID
        service: Curriculum service
        session: Database session

    Returns:
        AI coach response with personalized guidance
    """
    from app.services.ai_orchestrator import ai_orchestrator
    from app.services.adaptive_curriculum_service import AdaptiveCurriculumService
    from sqlalchemy import select
    import logging

    logger = logging.getLogger(__name__)

    try:
        user_message = message.get('text', '')
        context = message.get('context', {})

        if not user_message:
            raise HTTPException(status_code=400, detail="Message text required")

        # Get user's active curriculum for context
        result = await session.execute(
            select(Curriculum)
            .where(Curriculum.user_id == user_id)
            .where(Curriculum.status == 'active')
            .order_by(Curriculum.created_at.desc())
        )
        curriculum = result.scalar_one_or_none()

        # Get user's skill profile
        profile = await service.get_or_create_skill_profile(user_id)
        skill_levels = json.loads(profile.skill_levels_json or '{}')

        # Get recent performance data
        adaptive_service = AdaptiveCurriculumService(session)
        performance = await adaptive_service.analyze_user_performance(user_id, lookback_days=7)

        # Build context-aware prompt for AI coach
        coach_prompt = f"""You are a warm, encouraging piano coach having a conversation with a student.

## Student Context
**Skill Levels:**
- Technical Ability: {skill_levels.get('technical_ability', 5)}/10
- Theory Knowledge: {skill_levels.get('theory_knowledge', 5)}/10
- Rhythm: {skill_levels.get('rhythm_competency', 5)}/10
- Ear Training: {skill_levels.get('ear_training', 5)}/10
- Improvisation: {skill_levels.get('improvisation', 5)}/10

**Recent Performance:**
- Average Quality: {performance.avg_quality_score:.1f}/5.0
- Trend: {performance.recent_performance_trend}
- Completion Rate: {performance.completion_rate * 100:.0f}%
"""

        if curriculum:
            coach_prompt += f"""
**Current Curriculum:**
- Title: {curriculum.title}
- Week {curriculum.current_week} of {curriculum.duration_weeks}
"""

        if performance.weak_skill_areas:
            coach_prompt += f"\n**Areas to Support:** {', '.join(performance.weak_skill_areas)}"

        if performance.strong_skill_areas:
            coach_prompt += f"\n**Strengths to Celebrate:** {', '.join(performance.strong_skill_areas)}"

        if context.get('current_exercise'):
            coach_prompt += f"\n\n**Current Exercise:** {context['current_exercise']}"

        if context.get('current_lesson'):
            coach_prompt += f"\n**Current Lesson:** {context['current_lesson']}"

        coach_prompt += f"""

**Student's Question/Message:**
"{user_message}"

**Instructions:**
1. Respond warmly and personally, addressing their specific situation
2. Reference their actual skill levels and recent performance
3. If they're struggling, provide specific, actionable tips
4. If they're doing well, celebrate and suggest next challenges
5. Keep responses conversational (2-4 paragraphs)
6. Be encouraging but realistic
7. Provide concrete practice suggestions when relevant

Respond as if you're their personal piano coach who knows them well."""

        # Generate AI response using Gemini
        try:
            model = ai_orchestrator.gemini_models[ai_orchestrator.select_gemini_model(7)]
            gemini_response = await model.generate_content_async(
                coach_prompt,
                generation_config={
                    "temperature": 0.9,
                    "max_output_tokens": 512,
                }
            )
            response_text = gemini_response.text
        except Exception as e:
            logger.warning(f"Gemini generation failed, using fallback: {e}")
            # Fallback response
            response_text = "I'm here to help! Could you tell me more about what you're working on?"

        return {
            "response": response_text,
            "context_used": {
                "skill_level": skill_levels.get('technical_ability', 5),
                "recent_quality": performance.avg_quality_score,
                "trend": performance.recent_performance_trend
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI Coach error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Coach error: {str(e)}")


@router.post("/add-lick-to-practice", response_model=CurriculumExerciseResponse)
async def add_lick_to_practice(
    request: AddLickToPracticeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    """Add a generated lick to the user's practice queue"""
    from sqlalchemy import select

    try:
        # Get or create active curriculum
        result = await db.execute(
            select(Curriculum)
            .where(Curriculum.user_id == current_user.id)
            .where(Curriculum.status == "active")
        )
        curriculum = result.scalar_one_or_none()

        if not curriculum:
            # Create a default curriculum for practice queue
            curriculum = Curriculum(
                user_id=current_user.id,
                title="Practice Queue",
                description="Collection of licks and exercises for practice",
                duration_weeks=52,  # One year
                status="active"
            )
            db.add(curriculum)
            await db.flush()

        # Get or create "Practice Queue" module
        result = await db.execute(
            select(CurriculumModule)
            .where(CurriculumModule.curriculum_id == curriculum.id)
            .where(CurriculumModule.title == "Licks Practice")
        )
        module = result.scalar_one_or_none()

        if not module:
            module = CurriculumModule(
                curriculum_id=curriculum.id,
                title="Licks Practice",
                description="Jazz licks for practice",
                order_index=0,
                duration_weeks=52
            )
            db.add(module)
            await db.flush()

        # Get or create "Licks" lesson
        result = await db.execute(
            select(CurriculumLesson)
            .where(CurriculumLesson.module_id == module.id)
            .where(CurriculumLesson.title == "Jazz Licks")
        )
        lesson = result.scalar_one_or_none()

        if not lesson:
            lesson = CurriculumLesson(
                module_id=module.id,
                title="Jazz Licks",
                description="Generated jazz licks",
                week_number=1,
                theory_content_json="{}",
                concepts_json="[]",
                estimated_duration_minutes=30
            )
            db.add(lesson)
            await db.flush()

        # Create lick exercise
        lick_content = {
            "notes": request.notes,
            "midi_notes": request.midi_notes,
            "context": request.context,
            "style": request.style,
            "duration_beats": request.duration_beats
        }

        exercise = CurriculumExercise(
            lesson_id=lesson.id,
            title=request.lick_name,
            description=f"{request.style.title()} lick over {request.context}",
            order_index=0,
            exercise_type="lick",
            content_json=json.dumps(lick_content),
            difficulty=request.difficulty,
            estimated_duration_minutes=5,
            # Set for immediate practice (SRS defaults)
            next_review_at=datetime.utcnow(),
            interval_days=1.0,
            ease_factor=2.5,
            repetition_count=0
        )

        db.add(exercise)
        await db.commit()
        await db.refresh(exercise)

        # Convert to response format
        return CurriculumExerciseResponse(
            id=exercise.id,
            lesson_id=exercise.lesson_id,
            title=exercise.title,
            description=exercise.description,
            order_index=exercise.order_index,
            exercise_type=exercise.exercise_type,
            content=json.loads(exercise.content_json),
            difficulty=exercise.difficulty,
            estimated_duration_minutes=exercise.estimated_duration_minutes,
            target_bpm=exercise.target_bpm,
            practice_count=exercise.practice_count,
            best_score=exercise.best_score,
            is_mastered=exercise.is_mastered,
            mastered_at=exercise.mastered_at,
            next_review_at=exercise.next_review_at,
            last_reviewed_at=exercise.last_reviewed_at,
            interval_days=exercise.interval_days,
            ease_factor=exercise.ease_factor,
            repetition_count=exercise.repetition_count,
            created_at=exercise.created_at
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add lick to practice queue: {str(e)}")
