"""Celery tasks for curriculum adaptation (Phase 2)

Analyzes user performance and adapts curricula weekly.
"""

import logging
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.celery_app import celery_app
from app.core.config import settings
from app.database.curriculum_models import Curriculum
from app.services.adaptive_curriculum_service import AdaptiveCurriculumService

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


@celery_app.task(name="app.tasks.curriculum_adaptation.weekly_curriculum_adaptation_task")
def weekly_curriculum_adaptation_task():
    """Weekly curriculum adaptation task (Phase 2)

    Scheduled to run every Monday at 2:00 AM.
    Analyzes user performance and adapts curriculum difficulty and load.
    """
    import asyncio

    async def _adapt():
        async with AsyncSessionLocal() as session:
            try:
                # Get all active curricula
                result = await session.execute(
                    select(Curriculum).where(Curriculum.status == 'active')
                )
                active_curricula = result.scalars().all()

                logger.info(f"Running weekly adaptation for {len(active_curricula)} active curricula")

                adapted_count = 0

                for curriculum in active_curricula:
                    try:
                        # Create service instance with session
                        adaptive_service = AdaptiveCurriculumService(session)

                        # Analyze performance (7-day lookback)
                        analysis = await adaptive_service.analyze_user_performance(
                            user_id=curriculum.user_id,
                            lookback_days=7
                        )

                        # Only adapt if there are recommendations
                        if analysis.recommended_actions:
                            await adaptive_service.apply_adaptations(
                                curriculum_id=curriculum.id,
                                analysis=analysis
                            )
                            adapted_count += 1

                            logger.info(
                                f"Adapted curriculum {curriculum.id}: "
                                f"{len(analysis.recommended_actions)} changes"
                            )

                    except Exception as e:
                        logger.error(f"Failed to adapt curriculum {curriculum.id}: {e}")
                        continue

                logger.info(f"Weekly adaptation complete: {adapted_count}/{len(active_curricula)} adapted")

                return {
                    "status": "success",
                    "total_curricula": len(active_curricula),
                    "adapted": adapted_count
                }

            except Exception as e:
                logger.error(f"Weekly adaptation task failed: {e}")
                return {"status": "error", "message": str(e)}

    return asyncio.run(_adapt())
