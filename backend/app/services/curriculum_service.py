"""Curriculum Service

Manages curriculum generation, CRUD operations, progress tracking, and adaptive learning.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

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
from app.services.curriculum_defaults import DEFAULT_CURRICULUMS
from app.services.srs_service import SRSService

logger = logging.getLogger(__name__)


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

        # Generate curriculum plan with error handling
        try:
            # Check if AI is available before calling
            if not ai_orchestrator.is_available():
                raise ValueError(
                    "AI curriculum generation is unavailable. "
                    "Initialization errors: " + ", ".join(ai_orchestrator.initialization_errors)
                )

            plan = await ai_orchestrator.generate_curriculum_plan(profile_dict, duration_weeks)

        except Exception as e:
            # Log detailed error for debugging
            logger.error(
                "AI curriculum generation failed",
                extra={
                    "user_id": user_id,
                    "duration_weeks": duration_weeks,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                exc_info=True
            )

            # Provide user-friendly error message
            raise ValueError(
                "AI curriculum generation failed. Please ensure GEMINI_API_KEY is set correctly. "
                f"Error: {str(e)}"
            ) from e

        return await self._create_curriculum_from_plan(
            user_id=user_id,
            plan=plan,
            title=title,
            duration_weeks=duration_weeks,
            ai_model=f"gemini-{ai_orchestrator.budget_mode.value}"
        )

    async def create_default_curriculum(
        self,
        user_id: int,
        template_key: str = "gospel_essentials"
    ) -> Curriculum:
        """Create a curriculum from a default template"""
        if template_key not in DEFAULT_CURRICULUMS:
            raise ValueError(f"Unknown template: {template_key}")
            
        plan = DEFAULT_CURRICULUMS[template_key]
        
        # Calculate duration from modules (approx 4 weeks per module)
        duration_weeks = sum(
            (m.get('end_week', 4) - m.get('start_week', 1) + 1) 
            for m in plan.get('modules', [])
        )
        # Or just use max end_week
        last_module = plan['modules'][-1] if plan['modules'] else {}
        duration_weeks = last_module.get('end_week', 12)
        
        return await self._create_curriculum_from_plan(
            user_id=user_id,
            plan=plan,
            title=plan.get('title'),
            duration_weeks=duration_weeks,
            ai_model="template"
        )

    async def _create_curriculum_from_plan(
        self,
        user_id: int,
        plan: Dict[str, Any],
        title: Optional[str] = None,
        duration_weeks: int = 12,
        ai_model: str = "gemini"
    ) -> Curriculum:
        """Helper to save curriculum plan to database"""
        
        # Create curriculum record
        curriculum = Curriculum(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title or plan.get('title', 'Personalized Curriculum'),
            description=plan.get('description'),
            duration_weeks=duration_weeks,
            current_week=1,
            status='active',
            ai_model_used=ai_model,
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

        # Queue audio generation for all exercises (Phase 1)
        await self._queue_curriculum_audio_generation(curriculum.id)

        return curriculum

    async def _queue_curriculum_audio_generation(self, curriculum_id: str):
        """Queue background audio generation for all exercises in a curriculum

        Args:
            curriculum_id: Curriculum ID
        """
        try:
            from app.tasks.audio_generation import generate_exercise_audio_task

            # Get all exercises in the curriculum
            result = await self.db.execute(
                select(CurriculumExercise)
                .join(CurriculumLesson)
                .join(CurriculumModule)
                .join(Curriculum)
                .where(Curriculum.id == curriculum_id)
            )
            exercises = result.scalars().all()

            logger.info(f"Queueing audio generation for {len(exercises)} exercises in curriculum {curriculum_id}")

            # Queue a task for each exercise with staggered countdown
            for idx, exercise in enumerate(exercises):
                # Stagger tasks every 10 seconds to avoid overwhelming the system
                countdown_seconds = idx * 10

                generate_exercise_audio_task.apply_async(
                    args=[exercise.id, "both"],  # Generate both FluidSynth and Stable Audio
                    countdown=countdown_seconds
                )

            logger.info(f"Successfully queued {len(exercises)} audio generation tasks")

        except Exception as e:
            logger.error(f"Failed to queue audio generation for curriculum {curriculum_id}: {e}")
            # Don't raise - audio generation is non-critical, curriculum should still be created

    async def generate_theory_focused_exercise(
        self,
        theory_concept: str,
        difficulty: str,
        key: str,
        genre: str = "any"
    ) -> Dict[str, Any]:
        """
        Generate exercise specifically teaching a theory concept.

        Uses theory library for correct transformations and AI for student-friendly instructions.

        Args:
            theory_concept: One of "neo_riemannian", "negative_harmony", "substitutions",
                           "voice_leading", "coltrane_changes"
            difficulty: "beginner", "intermediate", "advanced"
            key: Musical key (e.g., "C", "Dm")
            genre: Genre context for application

        Returns:
            Dict containing exercise data, MIDI, and instructions
        """
        from app.services.ai_orchestrator import ai_orchestrator, TaskType
        from app.theory import chord_substitutions, voice_leading_neo_riemannian

        # Generate theory-correct content using theory library
        theory_data = {}

        if theory_concept == "neo_riemannian":
            # Use PLR transformations from theory library
            tonnetz = voice_leading_neo_riemannian.TonnetzLattice()
            start_chord = ("C", "")  # C major
            transformations = ["P", "L", "R"]

            progression = [start_chord]
            for trans in transformations:
                next_chord = tonnetz.apply_transformation(progression[-1], trans)
                progression.append(next_chord)

            theory_data = {
                "progression": progression,
                "transformations": transformations,
                "concept": "PLR Transformations"
            }

        elif theory_concept == "negative_harmony":
            # Use negative harmony from theory library
            original = [("C", "maj7"), ("A", "m7"), ("D", "m7"), ("G", "7")]
            negative = chord_substitutions.generate_negative_harmony(original, key, "major")

            theory_data = {
                "original_progression": original,
                "negative_progression": negative,
                "concept": "Negative Harmony Mirror"
            }

        elif theory_concept == "substitutions":
            # Use chord substitutions
            target_chord = (key, "7")
            subs = chord_substitutions.find_substitutions(
                target_chord,
                key,
                "major",
                complexity_level="moderate"
            )

            theory_data = {
                "original_chord": target_chord,
                "substitutions": subs,
                "concept": "Chord Substitutions"
            }

        # Generate student-friendly instructions using AI
        prompt = f"""
        Create practice instructions for a {difficulty} level music student learning {theory_concept}.

        Theory content: {json.dumps(theory_data)}
        Key: {key}
        Genre context: {genre}

        Provide:
        1. Brief explanation (2-3 sentences) of the concept
        2. Step-by-step practice instructions (numbered list)
        3. What to listen for when playing
        4. Common mistakes to avoid

        Keep language accessible for {difficulty} students.
        """

        ai_response = await ai_orchestrator.generate(
            task_type=TaskType.THEORY_EXERCISE_GEN,
            prompt=prompt,
            complexity=4,  # Use Phi-3.5 Mini (local, fast)
            max_tokens=800
        )

        return {
            "theory_concept": theory_concept,
            "difficulty": difficulty,
            "key": key,
            "genre": genre,
            "theory_data": theory_data,
            "instructions": ai_response.get("text", ""),
            "metadata": {
                "concept_complexity": difficulty,
                "estimated_practice_time": "10-15 minutes",
                "prerequisite_concepts": self._get_prerequisites(theory_concept)
            }
        }

    def _get_prerequisites(self, theory_concept: str) -> List[str]:
        """Get prerequisite concepts for a theory topic"""
        prerequisites = {
            "neo_riemannian": ["triads", "chord_inversions", "voice_leading_basics"],
            "negative_harmony": ["major_minor_scales", "chord_progressions", "functional_harmony"],
            "substitutions": ["seventh_chords", "chord_functions", "voice_leading_basics"],
            "voice_leading": ["triads", "chord_inversions"],
            "coltrane_changes": ["ii_v_i_progressions", "modulation", "extended_chords"]
        }
        return prerequisites.get(theory_concept, [])

    # =========================================================================
    # Curriculum Retrieval Methods
    # =========================================================================
    
    async def get_active_curriculum(self, user_id: int) -> Optional[Curriculum]:
        """Get user's active curriculum with modules (returns most recent if multiple exist)"""
        result = await self.db.execute(
            select(Curriculum)
            .options(
                selectinload(Curriculum.modules).selectinload(CurriculumModule.lessons)
            )
            .where(
                and_(
                    Curriculum.user_id == user_id,
                    Curriculum.status.in_(['active', 'completed'])
                )
            )
            .order_by(Curriculum.updated_at.desc())
            .limit(1)
        )
        return result.unique().scalars().first()
    
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
    
    async def get_user_curriculums(self, user_id: int) -> List[Curriculum]:
        """Get all curriculums for a user, PLUS global curriculums owned by admin"""

        # 1. Get user's personal curriculums
        result = await self.db.execute(
            select(Curriculum)
            .where(Curriculum.user_id == user_id)
            .order_by(Curriculum.updated_at.desc())
        )
        user_curriculums = result.scalars().all()

        # 2. Get global curriculums (from admin) - gracefully handle if admin doesn't exist
        try:
            admin_result = await self.db.execute(
                select(User.id).where(User.email == "admin@gospelkeys.ai")
            )
            admin_id = admin_result.scalar_one_or_none()

            if admin_id and admin_id != user_id:
                global_result = await self.db.execute(
                    select(Curriculum)
                    .where(Curriculum.user_id == admin_id)
                    .order_by(Curriculum.title)
                )
                global_curriculums = global_result.scalars().all()

                # Combine: User's first, then Globals
                return list(user_curriculums) + list(global_curriculums)
        except Exception as e:
            logger.warning(f"Could not fetch admin curriculums: {e}")
            # Continue without admin curriculums

        return user_curriculums

    async def activate_curriculum(self, curriculum_id: str, user_id: int) -> Curriculum:
        """
        Make a curriculum active. 
        If it belongs to another user (Global Admin), CLONE it first.
        """
        # Get the curriculum provided
        result = await self.db.execute(
            select(Curriculum)
            .options(
                selectinload(Curriculum.modules)
                .selectinload(CurriculumModule.lessons)
                .selectinload(CurriculumLesson.exercises)
            )
            .where(Curriculum.id == curriculum_id)
        )
        target = result.scalar_one_or_none()
        
        if not target:
            raise ValueError("Curriculum not found")
        
        # Case 1: Curriculum belongs to user -> Just activate
        if target.user_id == user_id:
            target.updated_at = datetime.utcnow()
            target.status = 'active'
            await self.db.commit()
            await self.db.refresh(target)
            return target
            
        # Case 2: Curriculum is Global (belongs to admin/other) -> Clone it
        # Verify it is indeed global (optional check, but good for security)
        # For now, if it exists and not ours, we assume we can clone it if we can see it.
        
        return await self._clone_curriculum(target, user_id)

    async def _clone_curriculum(self, source: Curriculum, new_owner_id: int) -> Curriculum:
        """Deep clone a curriculum for a new owner"""
        logger.info(f"Cloning curriculum {source.id} for user {new_owner_id}")
        
        # 1. Clone Curriculum Root
        new_curriculum = Curriculum(
            id=str(uuid.uuid4()),
            user_id=new_owner_id,
            title=source.title, # Keep name or add (Copy)? Keep name for standard paths.
            description=source.description,
            duration_weeks=source.duration_weeks,
            current_week=1,
            status='active', # Activate immediately
            ai_model_used=source.ai_model_used,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(new_curriculum)
        
        # 2. Clone Modules
        # Ensure we sort by order_index
        sorted_modules = sorted(source.modules, key=lambda m: m.order_index)
        
        for mod in sorted_modules:
            new_mod = CurriculumModule(
                id=str(uuid.uuid4()),
                curriculum_id=new_curriculum.id,
                title=mod.title,
                description=mod.description,
                theme=mod.theme,
                order_index=mod.order_index,
                start_week=mod.start_week,
                end_week=mod.end_week,
                # JSON fields might need parsing/serializing loop but simple assign works
                prerequisites_json=mod.prerequisites_json,
                outcomes_json=mod.outcomes_json,
                completion_percentage=0.0
            )
            self.db.add(new_mod)
            
            # 3. Clone Lessons
            sorted_lessons = sorted(mod.lessons, key=lambda l: l.week_number)
            for lesson in sorted_lessons:
                new_lesson = CurriculumLesson(
                    id=str(uuid.uuid4()),
                    module_id=new_mod.id,
                    title=lesson.title,
                    description=lesson.description,
                    week_number=lesson.week_number,
                    theory_content_json=lesson.theory_content_json,
                    concepts_json=lesson.concepts_json,
                    estimated_duration_minutes=lesson.estimated_duration_minutes,
                    is_completed=False
                )
                self.db.add(new_lesson)
                
                # 4. Clone Exercises
                sorted_exercises = sorted(lesson.exercises, key=lambda e: e.order_index)
                for ex in sorted_exercises:
                    new_ex = CurriculumExercise(
                        id=str(uuid.uuid4()),
                        lesson_id=new_lesson.id,
                        title=ex.title,
                        description=ex.description,
                        order_index=ex.order_index,
                        exercise_type=ex.exercise_type,
                        content_json=ex.content_json,
                        difficulty=ex.difficulty,
                        estimated_duration_minutes=ex.estimated_duration_minutes,
                        target_bpm=ex.target_bpm,
                        # Reset Tracking
                        practice_count=0,
                        is_mastered=False,
                        # Reset Stats
                        next_review_at=datetime.utcnow(), # Start fresh
                        # Copy Audio Data?
                        # Crucial decision: Do we re-generate audio or point to same files?
                        # Since audio files are static (midi_file_path), we can copy the path!
                        # This saves massive re-generation time.
                        midi_file_path=ex.midi_file_path,
                        audio_files_json=ex.audio_files_json,
                        audio_generation_status=ex.audio_generation_status,
                    )
                    self.db.add(new_ex)
        
        await self.db.commit()
        await self.db.refresh(new_curriculum)
        return new_curriculum
    
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

    # =========================================================================
    # Assessment Milestone Triggers (Phase 3)
    # =========================================================================

    async def check_and_trigger_milestone_assessments(
        self,
        curriculum_id: str
    ) -> List[str]:
        """Check if milestone assessments should be triggered

        Args:
            curriculum_id: Curriculum ID

        Returns:
            List of triggered assessment IDs
        """
        from app.services.assessment_service import AssessmentService
        from app.database.curriculum_models import Assessment

        try:
            # Get curriculum
            result = await self.db.execute(
                select(Curriculum).where(Curriculum.id == curriculum_id)
            )
            curriculum = result.scalar_one_or_none()

            if not curriculum:
                return []

            current_week = curriculum.current_week
            triggered_assessments = []

            # Check for existing assessments this week
            result = await self.db.execute(
                select(Assessment).where(
                    and_(
                        Assessment.curriculum_id == curriculum_id,
                        Assessment.assessment_type == 'milestone'
                    )
                )
            )
            existing_assessments = result.scalars().all()
            existing_weeks = set()

            for assessment in existing_assessments:
                # Parse assessment content to get week
                try:
                    content = json.loads(assessment.ai_feedback_json)
                    if 'week' in content:
                        existing_weeks.add(content['week'])
                except:
                    pass

            # Week 4 milestone
            if current_week >= 4 and 4 not in existing_weeks:
                assessment_service = AssessmentService(self.db)
                assessment = await assessment_service.generate_milestone_assessment(
                    curriculum=curriculum,
                    week=4
                )
                triggered_assessments.append(assessment.id)
                logger.info(f"Triggered week 4 milestone assessment for curriculum {curriculum_id}")

            # Week 8 milestone
            if current_week >= 8 and 8 not in existing_weeks:
                assessment_service = AssessmentService(self.db)
                assessment = await assessment_service.generate_milestone_assessment(
                    curriculum=curriculum,
                    week=8
                )
                triggered_assessments.append(assessment.id)
                logger.info(f"Triggered week 8 milestone assessment for curriculum {curriculum_id}")

            # Final assessment (curriculum complete)
            if curriculum.status == 'completed' and 'final' not in [a.assessment_type for a in existing_assessments]:
                assessment_service = AssessmentService(self.db)
                assessment = await assessment_service.generate_milestone_assessment(
                    curriculum=curriculum,
                    week=curriculum.duration_weeks
                )
                assessment.assessment_type = 'final'
                await self.db.commit()
                triggered_assessments.append(assessment.id)
                logger.info(f"Triggered final assessment for curriculum {curriculum_id}")

            return triggered_assessments

        except Exception as e:
            logger.error(f"Failed to check milestone triggers for curriculum {curriculum_id}: {e}")
            return []

    async def complete_assessment_feedback_loop(
        self,
        assessment_id: str,
        evaluation: Dict
    ):
        """Complete the feedback loop after assessment evaluation

        Workflow:
        1. Get assessment and user
        2. Update skill profile with new scores
        3. Trigger curriculum adaptation
        4. Log changes

        Args:
            assessment_id: Assessment ID
            evaluation: Evaluation results from assessment_service.evaluate_assessment
        """
        from app.services.assessment_service import AssessmentService
        from app.services.adaptive_curriculum_service import AdaptiveCurriculumService

        try:
            # Get assessment
            result = await self.db.execute(
                select(Assessment).where(Assessment.id == assessment_id)
            )
            assessment = result.scalar_one_or_none()

            if not assessment:
                raise ValueError(f"Assessment not found: {assessment_id}")

            # Update skill profile
            assessment_service = AssessmentService(self.db)
            updated_profile = await assessment_service.update_skill_profile_from_assessment(
                user_id=assessment.user_id,
                scores=evaluation["scores"]
            )

            logger.info(f"Updated skill profile for user {assessment.user_id} from assessment {assessment_id}")

            # If assessment is linked to a curriculum, trigger adaptation
            if assessment.curriculum_id:
                adaptive_service = AdaptiveCurriculumService(self.db)

                # Analyze performance
                analysis = await adaptive_service.analyze_user_performance(
                    user_id=assessment.user_id,
                    lookback_days=14  # Longer lookback after assessment
                )

                # Apply adaptations
                if analysis.recommended_actions:
                    await adaptive_service.apply_adaptations(
                        curriculum_id=assessment.curriculum_id,
                        analysis=analysis
                    )

                    logger.info(
                        f"Applied {len(analysis.recommended_actions)} adaptations "
                        f"to curriculum {assessment.curriculum_id} after assessment"
                    )

        except Exception as e:
            logger.error(f"Failed to complete feedback loop for assessment {assessment_id}: {e}")
            raise e
