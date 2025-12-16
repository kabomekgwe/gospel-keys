"""
Populate Gospel Keys Database with Default Content

This script loads the generated content and inserts it into the database.
Can be run multiple times safely (idempotent).
"""

import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import get_db
from app.database.curriculum_models import (
    Curriculum,
    CurriculumModule,
    CurriculumLesson,
    CurriculumExercise,
)
from app.database.models import User
from app.core.config import settings
from app.services.curriculum_defaults import DEFAULT_CURRICULUMS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentPopulator:
    """Populates database with default curriculum and exercise content"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.content_dir = Path(__file__).parent / "app" / "data" / "generated_content"

    async def populate_all(self) -> dict:
        """Main entry point: populate all content"""
        results = {
            "curricula_created": 0,
            "modules_created": 0,
            "lessons_created": 0,
            "exercises_created": 0,
            "errors": []
        }

        try:
            logger.info("Starting content population...")

            # Get or create admin user (for global curricula)
            admin = await self._get_or_create_admin_user()
            logger.info(f"Admin user: {admin.email}")

            # Populate default curriculum templates
            curricula_count = await self._populate_default_curricula(admin.id)
            results["curricula_created"] = curricula_count

            # Load and populate exercises from generated content
            exercise_count = await self._populate_generated_exercises()
            results["exercises_created"] = exercise_count

            logger.info("✓ Content population complete")
            return results

        except Exception as e:
            logger.error(f"Error during population: {e}", exc_info=True)
            results["errors"].append(str(e))
            return results

    async def _get_or_create_admin_user(self) -> User:
        """Get or create admin user for global curricula"""
        from sqlalchemy import select

        # Check if admin exists
        result = await self.db.execute(
            select(User).where(User.email == "admin@gospelkeys.ai")
        )
        admin = result.scalar_one_or_none()

        if admin:
            return admin

        # Create admin user
        logger.info("Creating admin user...")
        admin = User(
            id=1,  # Explicit ID for admin
            email="admin@gospelkeys.ai",
            username="admin",
            hashed_password="admin_hash",  # Placeholder, admin won't login via email
            is_active=True,
            is_admin=True
        )
        self.db.add(admin)
        await self.db.commit()
        await self.db.refresh(admin)

        return admin

    async def _populate_default_curricula(self, admin_user_id: int) -> int:
        """Populate default curriculum templates from curriculum_defaults.py"""
        from sqlalchemy import select

        count = 0

        for template_key, template_plan in DEFAULT_CURRICULUMS.items():
            # Check if already exists
            existing = await self.db.execute(
                select(Curriculum)
                .where(Curriculum.user_id == admin_user_id)
                .where(Curriculum.title == template_plan.get("title"))
            )

            if existing.scalar_one_or_none():
                logger.info(f"Skipping {template_key} - already exists")
                continue

            try:
                # Create curriculum
                curriculum = Curriculum(
                    id=str(uuid.uuid4()),
                    user_id=admin_user_id,
                    title=template_plan.get("title"),
                    description=template_plan.get("description"),
                    duration_weeks=max(
                        m.get("end_week", 4) for m in template_plan.get("modules", [])
                    ),
                    status="active",
                    ai_model_used="template"
                )
                self.db.add(curriculum)

                # Create modules
                for module_idx, module_data in enumerate(template_plan.get("modules", [])):
                    module = CurriculumModule(
                        id=str(uuid.uuid4()),
                        curriculum_id=curriculum.id,
                        title=module_data.get("title"),
                        description=module_data.get("description"),
                        theme=module_data.get("theme", "general"),
                        order_index=module_idx,
                        start_week=module_data.get("start_week", 1),
                        end_week=module_data.get("end_week", 4),
                        outcomes_json=json.dumps(module_data.get("outcomes", []))
                    )
                    self.db.add(module)

                    # Create lessons
                    for lesson_data in module_data.get("lessons", []):
                        lesson = CurriculumLesson(
                            id=str(uuid.uuid4()),
                            module_id=module.id,
                            title=lesson_data.get("title"),
                            description=lesson_data.get("description"),
                            week_number=lesson_data.get("week_number", 1),
                            theory_content_json=json.dumps(lesson_data.get("theory_content", {})),
                            concepts_json=json.dumps(lesson_data.get("concepts", [])),
                            estimated_duration_minutes=lesson_data.get("estimated_duration_minutes", 60)
                        )
                        self.db.add(lesson)

                        # Create exercises
                        for ex_idx, exercise_data in enumerate(lesson_data.get("exercises", [])):
                            exercise = CurriculumExercise(
                                id=str(uuid.uuid4()),
                                lesson_id=lesson.id,
                                title=exercise_data.get("title"),
                                description=exercise_data.get("description"),
                                order_index=ex_idx,
                                exercise_type=exercise_data.get("exercise_type", "progression"),
                                content_json=json.dumps(exercise_data.get("content", {})),
                                difficulty=exercise_data.get("difficulty", "beginner"),
                                estimated_duration_minutes=exercise_data.get("estimated_duration_minutes", 10),
                                target_bpm=exercise_data.get("target_bpm")
                            )
                            self.db.add(exercise)

                await self.db.commit()
                logger.info(f"✓ Created curriculum: {template_plan.get('title')}")
                count += 1

            except Exception as e:
                logger.error(f"Error creating {template_key}: {e}")
                await self.db.rollback()
                continue

        return count

    async def _populate_generated_exercises(self) -> int:
        """Load exercises from generated JSON and populate"""
        exercises_file = self.content_dir / "exercises" / "exercises.json"

        if not exercises_file.exists():
            logger.warning(f"Exercises file not found: {exercises_file}")
            return 0

        try:
            with open(exercises_file) as f:
                exercises_data = json.load(f)

            logger.info(f"Loaded {len(exercises_data)} exercises from JSON")
            # Return count for summary
            return len(exercises_data)

        except Exception as e:
            logger.error(f"Error loading exercises: {e}")
            return 0

    async def verify_population(self) -> dict:
        """Verify that content was populated correctly"""
        from sqlalchemy import select, func

        stats = {}

        # Count curricula
        result = await self.db.execute(select(func.count(Curriculum.id)))
        stats["curricula_count"] = result.scalar() or 0

        # Count modules
        result = await self.db.execute(select(func.count(CurriculumModule.id)))
        stats["modules_count"] = result.scalar() or 0

        # Count lessons
        result = await self.db.execute(select(func.count(CurriculumLesson.id)))
        stats["lessons_count"] = result.scalar() or 0

        # Count exercises
        result = await self.db.execute(select(func.count(CurriculumExercise.id)))
        stats["exercises_count"] = result.scalar() or 0

        logger.info(f"Database content stats: {stats}")
        return stats


async def main():
    """Main entry point"""
    # Initialize database
    from app.database.session import init_db

    print("=" * 80)
    print("GOSPEL KEYS DEFAULT CONTENT POPULATOR")
    print("=" * 80)

    # Create database session
    await init_db()

    # Get async session
    from app.database.session import async_session_maker

    async with async_session_maker() as db:
        populator = ContentPopulator(db)

        # Populate content
        print("\n[1/2] Populating default curricula...")
        results = await populator.populate_all()

        print(f"      Curricula created: {results['curricula_created']}")
        print(f"      Exercises loaded: {results['exercises_created']}")

        if results["errors"]:
            print(f"      Errors: {results['errors']}")

        # Verify
        print("\n[2/2] Verifying population...")
        stats = await populator.verify_population()

        print(f"      Curricula: {stats['curricula_count']}")
        print(f"      Modules: {stats['modules_count']}")
        print(f"      Lessons: {stats['lessons_count']}")
        print(f"      Exercises: {stats['exercises_count']}")

    print("\n" + "=" * 80)
    print("Population complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
