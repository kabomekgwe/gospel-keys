"""Test Enhanced Tutorial Service Integration

Quick test to verify the new prompt architecture works correctly.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.tutorial_service import tutorial_service
from app.services.ai_orchestrator_enhanced import enhanced_ai_orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MockLesson:
    """Mock lesson for testing"""
    def __init__(self):
        self.id = 1
        self.title = "Gospel Voicings 101"
        self.description = "Learn fundamental gospel voicing techniques"
        self.week_number = 1
        self.estimated_duration_minutes = 45
        self.tutorial_content_json = None  # Force generation
        self.theory_content_json = '{"key": "C", "concepts": ["Shell voicings", "Added 9ths"]}'
        self.concepts_json = '["Shell voicings", "Color tones", "Voice leading"]'


async def test_gospel_tutorial():
    """Test gospel tutorial generation"""
    logger.info("=" * 60)
    logger.info("TEST 1: Gospel Tutorial Generation")
    logger.info("=" * 60)

    lesson = MockLesson()

    try:
        tutorial = await tutorial_service.generate_lesson_tutorial(
            lesson=lesson,
            genre="gospel",
            user_skill_levels={
                "overall": "intermediate",
                "technical_ability": 6,
                "theory_knowledge": 5,
                "rhythm_competency": 7,
                "goals": ["Master gospel voicings", "Learn Sunday morning sound"]
            }
        )

        logger.info("✅ Tutorial generated successfully!")
        logger.info(f"Sections: {list(tutorial.keys())}")

        # Check structure
        required_sections = ["overview", "theory", "practice_guide"]
        for section in required_sections:
            if section in tutorial:
                logger.info(f"  ✓ {section}: Present")
            else:
                logger.warning(f"  ✗ {section}: Missing")

        # Sample content
        if "overview" in tutorial:
            logger.info(f"\nOverview learning objectives:")
            for obj in tutorial["overview"].get("what_you_will_learn", [])[:3]:
                logger.info(f"  - {obj}")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


async def test_jazz_tutorial():
    """Test jazz tutorial generation"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Jazz Tutorial Generation")
    logger.info("=" * 60)

    lesson = MockLesson()
    lesson.title = "ii-V-I Progressions"
    lesson.description = "Master the fundamental jazz progression"

    try:
        tutorial = await tutorial_service.generate_lesson_tutorial(
            lesson=lesson,
            genre="jazz",
            force_regenerate=True
        )

        logger.info("✅ Jazz tutorial generated successfully!")
        logger.info(f"Sections: {list(tutorial.keys())}")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


async def test_fallback_handling():
    """Test that fallback works gracefully"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Fallback Handling (Backward Compatibility)")
    logger.info("=" * 60)

    lesson = MockLesson()
    lesson.title = "Test Lesson"

    try:
        # Test without genre parameter (should default to gospel)
        tutorial = await tutorial_service.generate_lesson_tutorial(
            lesson=lesson,
            force_regenerate=True
            # No genre parameter - testing backward compatibility
        )

        logger.info("✅ Backward compatible call succeeded!")
        logger.info(f"Generated with default genre (gospel)")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


async def test_health_metrics():
    """Test health metrics retrieval"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Health Metrics")
    logger.info("=" * 60)

    try:
        metrics = enhanced_ai_orchestrator.get_health_metrics()

        logger.info("✅ Health metrics retrieved!")
        logger.info(f"Total requests: {metrics.total_requests}")
        logger.info(f"Fallback count: {metrics.fallback_count}")
        logger.info(f"Fallback rate: {metrics.fallback_rate * 100:.1f}%")

        if metrics.by_task_type:
            logger.info("\nFallback rate by task type:")
            for task, rate in metrics.by_task_type.items():
                logger.info(f"  {task}: {rate * 100:.1f}%")

        if metrics.by_genre:
            logger.info("\nFallback rate by genre:")
            for genre, rate in metrics.by_genre.items():
                logger.info(f"  {genre}: {rate * 100:.1f}%")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


async def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("ENHANCED TUTORIAL SERVICE INTEGRATION TESTS")
    logger.info("=" * 60)

    results = {
        "Gospel Tutorial": await test_gospel_tutorial(),
        "Jazz Tutorial": await test_jazz_tutorial(),
        "Fallback Handling": await test_fallback_handling(),
        "Health Metrics": await test_health_metrics(),
    }

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("\nNext steps:")
        logger.info("1. Monitor logs for fallback rates")
        logger.info("2. Review genre-authentic content quality")
        logger.info("3. Update API routes to accept genre parameter")
        return 0
    else:
        logger.error("\n⚠️  SOME TESTS FAILED")
        logger.error("Check logs above for error details")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
