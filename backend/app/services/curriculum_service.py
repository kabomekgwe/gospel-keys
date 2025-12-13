"""Curriculum Service

Manages curriculum generation, CRUD operations, progress tracking, and adaptive learning.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.curriculum_models import (
    UserSkillProfile,
    Curriculum,
    CurriculumModule,
    CurriculumLesson,
    CurriculumExercise,
    Assessment,
)
from app.database.models import User
from app.services.ai_orchestrator import ai_orchestrator
from app.services.srs_service import SRSService


class CurriculumService:
    """
    Service for managing curriculum generation, tracking, and adaptation.
    
    Responsibilities:
    - Create/update user skill profiles
    - Generate personalized curricula using AI
    - Track progress through lessons and exercises
    - Apply SRS scheduling to exercises
    - Adapt curriculum based on user performance
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # =========================================================================
    # User Skill Profile Methods
    # =========================================================================
    
    async def get_or_create_skill_profile(self, user_id: int) -> UserSkillProfile:
        """Get user's skill profile, creating if it doesn't exist"""
        result = await self.db.execute(
            select(UserSkillProfile).where(UserSkillProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = UserSkillProfile(user_id=user_id)
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
        
        return profile
    
    async def update_skill_profile(
        self, 
        user_id: int, 
        assessment_data: Dict[str, Any]
    ) -> UserSkillProfile:
        """Update skill profile from assessment data"""
        profile = await self.get_or_create_skill_profile(user_id)
        
        # Update skill levels
        if 'skill_levels' in assessment_data:
            levels = assessment_data['skill_levels']
            profile.technical_ability = levels.get('technical_ability', profile.technical_ability)
            profile.theory_knowledge = levels.get('theory_knowledge', profile.theory_knowledge)
            profile.rhythm_competency = levels.get('rhythm_competency', profile.rhythm_competency)
            profile.ear_training = levels.get('ear_training', profile.ear_training)
            profile.improvisation = levels.get('improvisation', profile.improvisation)
        
        # Update style familiarity
        if 'style_familiarity' in assessment_data:
            profile.style_familiarity_json = json.dumps(assessment_data['style_familiarity'])
        
        # Update learning preferences
        if 'primary_goal' in assessment_data:
            profile.primary_goal = assessment_data['primary_goal']
        if 'interests' in assessment_data:
            profile.interests_json = json.dumps(assessment_data['interests'])
        if 'weekly_practice_hours' in assessment_data:
            profile.weekly_practice_hours = assessment_data['weekly_practice_hours']
        if 'learning_velocity' in assessment_data:
            profile.learning_velocity = assessment_data['learning_velocity']
        if 'preferred_style' in assessment_data:
            profile.preferred_style = assessment_data['preferred_style']
        
        profile.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile
    
    def _profile_to_dict(self, profile: UserSkillProfile) -> Dict[str, Any]:
        """Convert skill profile to dict for AI prompts"""
        return {
            'technical_ability': profile.technical_ability,
            'theory_knowledge': profile.theory_knowledge,
            'rhythm_competency': profile.rhythm_competency,
            'ear_training': profile.ear_training,
            'improvisation': profile.improvisation,
            'style_familiarity': json.loads(profile.style_familiarity_json or '{}'),
            'primary_goal': profile.primary_goal,
            'interests': json.loads(profile.interests_json or '[]'),
            'weekly_practice_hours': profile.weekly_practice_hours,
            'learning_velocity': profile.learning_velocity,
        }
    
    # =========================================================================
    # Curriculum Generation Methods
    # =========================================================================
    
    async def generate_curriculum(
        self, 
        user_id: int,
        title: Optional[str] = None,
        duration_weeks: int = 12
    ) -> Curriculum:
        """Generate a personalized curriculum for the user"""
        # Get user's skill profile
        profile = await self.get_or_create_skill_profile(user_id)
        profile_dict = self._profile_to_dict(profile)
        
        # Generate curriculum plan using AI
        plan = await ai_orchestrator.generate_curriculum_plan(profile_dict, duration_weeks)
        
        # Create curriculum record
        curriculum = Curriculum(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title or plan.get('title', 'Personalized Curriculum'),
            description=plan.get('description'),
            duration_weeks=duration_weeks,
            current_week=1,
            status='active',
            ai_model_used='gemini',
        )
        self.db.add(curriculum)
        
        # Create modules, lessons, and exercises from plan
        for module_idx, module_data in enumerate(plan.get('modules', [])):
            module = CurriculumModule(
                id=str(uuid.uuid4()),
                curriculum_id=curriculum.id,
                title=module_data.get('title', f'Module {module_idx + 1}'),
                description=module_data.get('description'),
                theme=module_data.get('theme', 'general'),
                order_index=module_idx,
                start_week=module_data.get('start_week', 1),
                end_week=module_data.get('end_week', 4),
                outcomes_json=json.dumps(module_data.get('outcomes', [])),
            )
            self.db.add(module)
            
            for lesson_data in module_data.get('lessons', []):
                lesson = CurriculumLesson(
                    id=str(uuid.uuid4()),
                    module_id=module.id,
                    title=lesson_data.get('title', 'Untitled Lesson'),
                    description=lesson_data.get('description'),
                    week_number=lesson_data.get('week_number', 1),
                    theory_content_json=json.dumps(lesson_data.get('theory_content', {})),
                    concepts_json=json.dumps(lesson_data.get('concepts', [])),
                    estimated_duration_minutes=lesson_data.get('estimated_duration_minutes', 60),
                )
                self.db.add(lesson)
                
                for ex_idx, exercise_data in enumerate(lesson_data.get('exercises', [])):
                    # Set initial review time
                    next_review = datetime.utcnow()
                    
                    exercise = CurriculumExercise(
                        id=str(uuid.uuid4()),
                        lesson_id=lesson.id,
                        title=exercise_data.get('title', f'Exercise {ex_idx + 1}'),
                        description=exercise_data.get('description'),
                        order_index=ex_idx,
                        exercise_type=exercise_data.get('exercise_type', 'progression'),
                        content_json=json.dumps(exercise_data.get('content', {})),
                        difficulty=exercise_data.get('difficulty', 'beginner'),
                        estimated_duration_minutes=exercise_data.get('estimated_duration_minutes', 10),
                        target_bpm=exercise_data.get('target_bpm'),
                        next_review_at=next_review,
                    )
                    self.db.add(exercise)
        
        await self.db.commit()
        await self.db.refresh(curriculum)
        
        return curriculum
    
    # =========================================================================
    # Curriculum Retrieval Methods
    # =========================================================================
    
    async def get_active_curriculum(self, user_id: int) -> Optional[Curriculum]:
        """Get user's active curriculum with modules"""
        result = await self.db.execute(
            select(Curriculum)
            .options(selectinload(Curriculum.modules))
            .where(
                and_(
                    Curriculum.user_id == user_id,
                    Curriculum.status == 'active'
                )
            )
            .order_by(Curriculum.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def get_curriculum_with_details(self, curriculum_id: str) -> Optional[Curriculum]:
        """Get curriculum with all modules, lessons, and exercises"""
        result = await self.db.execute(
            select(Curriculum)
            .options(
                selectinload(Curriculum.modules)
                .selectinload(CurriculumModule.lessons)
                .selectinload(CurriculumLesson.exercises)
            )
            .where(Curriculum.id == curriculum_id)
        )
        return result.scalar_one_or_none()
    
    async def get_module(self, module_id: str) -> Optional[CurriculumModule]:
        """Get a module with its lessons"""
        result = await self.db.execute(
            select(CurriculumModule)
            .options(
                selectinload(CurriculumModule.lessons)
                .selectinload(CurriculumLesson.exercises)
            )
            .where(CurriculumModule.id == module_id)
        )
        return result.scalar_one_or_none()
    
    async def get_lesson(self, lesson_id: str) -> Optional[CurriculumLesson]:
        """Get a lesson with its exercises"""
        result = await self.db.execute(
            select(CurriculumLesson)
            .options(selectinload(CurriculumLesson.exercises))
            .where(CurriculumLesson.id == lesson_id)
        )
        return result.scalar_one_or_none()
    
    # =========================================================================
    # Daily Practice Queue
    # =========================================================================
    
    async def get_daily_practice(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get today's practice exercises ordered by priority.
        
        Priority:
        1. Overdue exercises (past next_review_at)
        2. Due today exercises
        3. New exercises not yet practiced
        """
        curriculum = await self.get_active_curriculum(user_id)
        if not curriculum:
            return []
        
        now = datetime.utcnow()
        today_end = datetime.utcnow().replace(hour=23, minute=59, second=59)
        
        # Get exercises from active curriculum
        result = await self.db.execute(
            select(CurriculumExercise)
            .join(CurriculumLesson)
            .join(CurriculumModule)
            .where(CurriculumModule.curriculum_id == curriculum.id)
            .where(
                or_(
                    CurriculumExercise.next_review_at <= today_end,
                    CurriculumExercise.next_review_at.is_(None)
                )
            )
            .where(CurriculumExercise.is_mastered == False)  # noqa: E712
            .order_by(CurriculumExercise.next_review_at.asc().nullsfirst())
            .limit(limit)
        )
        exercises = result.scalars().all()
        
        # Build response with context
        practice_items = []
        for ex in exercises:
            # Get lesson and module for context
            lesson_result = await self.db.execute(
                select(CurriculumLesson)
                .options(selectinload(CurriculumLesson.module))
                .where(CurriculumLesson.id == ex.lesson_id)
            )
            lesson = lesson_result.scalar_one_or_none()
            
            if ex.next_review_at and ex.next_review_at < now:
                priority = 1  # Overdue
            elif ex.next_review_at and ex.next_review_at <= today_end:
                priority = 2  # Due today
            else:
                priority = 3  # New
            
            practice_items.append({
                'exercise': ex,
                'lesson_title': lesson.title if lesson else 'Unknown',
                'module_title': lesson.module.title if lesson and lesson.module else 'Unknown',
                'priority': priority,
            })
        
        # Sort by priority
        practice_items.sort(key=lambda x: x['priority'])
        
        return practice_items
    
    # =========================================================================
    # Progress Tracking
    # =========================================================================
    
    async def complete_exercise(
        self, 
        exercise_id: str, 
        quality: int,
        score: Optional[float] = None,
        duration_seconds: Optional[int] = None
    ) -> CurriculumExercise:
        """
        Mark exercise as practiced and update SRS scheduling.
        
        Args:
            exercise_id: UUID of the exercise
            quality: 0-5 rating (SM-2 algorithm)
            score: Optional accuracy percentage
            duration_seconds: Time spent practicing
        """
        result = await self.db.execute(
            select(CurriculumExercise).where(CurriculumExercise.id == exercise_id)
        )
        exercise = result.scalar_one_or_none()
        
        if not exercise:
            raise ValueError(f"Exercise not found: {exercise_id}")
        
        # Update practice count
        exercise.practice_count += 1
        exercise.last_reviewed_at = datetime.utcnow()
        
        # Update best score
        if score is not None:
            if exercise.best_score is None or score > exercise.best_score:
                exercise.best_score = score
        
        # Calculate next review using SRS
        new_interval, new_ef, new_reps = SRSService.calculate_next_review(
            quality=quality,
            prev_interval=exercise.interval_days,
            prev_ease_factor=exercise.ease_factor,
            repetition_count=exercise.repetition_count
        )
        
        exercise.interval_days = new_interval
        exercise.ease_factor = new_ef
        exercise.repetition_count = new_reps
        exercise.next_review_at = datetime.utcnow() + timedelta(days=new_interval)
        
        # Check for mastery (high quality multiple times)
        if quality >= 4 and exercise.repetition_count >= 5:
            exercise.is_mastered = True
            exercise.mastered_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(exercise)
        
        # Update lesson/module completion
        await self._update_completion_stats(exercise)
        
        return exercise
    
    async def _update_completion_stats(self, exercise: CurriculumExercise) -> None:
        """Update lesson and module completion percentages"""
        # Get lesson
        lesson_result = await self.db.execute(
            select(CurriculumLesson)
            .options(selectinload(CurriculumLesson.exercises))
            .where(CurriculumLesson.id == exercise.lesson_id)
        )
        lesson = lesson_result.scalar_one_or_none()
        
        if lesson:
            # Calculate lesson completion
            total_exercises = len(lesson.exercises)
            mastered_exercises = sum(1 for ex in lesson.exercises if ex.is_mastered)
            
            if mastered_exercises == total_exercises:
                lesson.is_completed = True
                lesson.completed_at = datetime.utcnow()
            
            # Get module and update completion
            module_result = await self.db.execute(
                select(CurriculumModule)
                .options(selectinload(CurriculumModule.lessons))
                .where(CurriculumModule.id == lesson.module_id)
            )
            module = module_result.scalar_one_or_none()
            
            if module:
                total_lessons = len(module.lessons)
                completed_lessons = sum(1 for l in module.lessons if l.is_completed)
                module.completion_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
            
            await self.db.commit()
    
    # =========================================================================
    # Assessment Methods
    # =========================================================================
    
    async def create_assessment(
        self,
        user_id: int,
        assessment_type: str,
        scores: Dict[str, Any],
        curriculum_id: Optional[str] = None
    ) -> Assessment:
        """Create a new assessment record"""
        overall_score = sum(scores.values()) / len(scores) if scores else None
        
        assessment = Assessment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            curriculum_id=curriculum_id,
            assessment_type=assessment_type,
            scores_json=json.dumps(scores),
            overall_score=overall_score,
        )
        
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        
        return assessment
