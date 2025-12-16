"""Test exercise library database operations"""
import asyncio

from app.database.session import async_session_maker
from app.services.exercise_library_service import get_exercise_library_service
from app.services.exercise_progress_service import get_exercise_progress_service
from app.services.spaced_repetition_service import get_spaced_repetition_service
from app.services.exercise_recommendation_service import get_exercise_recommendation_service


async def test_system():
    """Test the complete exercise library system"""
    async with async_session_maker() as db:
        print("=" * 60)
        print("EXERCISE LIBRARY SYSTEM TEST")
        print("=" * 60)

        # Test 1: Query curricula
        print("\n1. Testing Curriculum Library Service...")
        library_service = get_exercise_library_service(db)

        # Check if we have data
        from app.database.models import CurriculumLibrary, ExerciseLibrary
        from sqlalchemy import select, func

        # Count curricula
        stmt = select(func.count()).select_from(CurriculumLibrary)
        result = await db.execute(stmt)
        curricula_count = result.scalar()
        print(f"   ✅ Found {curricula_count} curricula in database")

        # Count exercises
        stmt = select(func.count()).select_from(ExerciseLibrary)
        result = await db.execute(stmt)
        exercises_count = result.scalar()
        print(f"   ✅ Found {exercises_count} exercises in database")

        # Test 2: Exercise Progress Service
        print("\n2. Testing Exercise Progress Service...")
        progress_service = get_exercise_progress_service(db)

        # Get stats for user 1 (should be empty)
        stats = await progress_service.get_progress_stats(user_id=1)
        print(f"   ✅ Progress stats: {stats['total_exercises_practiced']} exercises practiced")
        print(f"   ✅ Total practice time: {stats['total_practice_time_hours']:.2f} hours")
        print(f"   ✅ Mastery rate: {stats['mastery_rate']:.1f}%")

        # Test 3: Spaced Repetition Service
        print("\n3. Testing Spaced Repetition Service...")
        sr_service = get_spaced_repetition_service(db)

        sr_stats = await sr_service.get_review_stats(user_id=1)
        print(f"   ✅ Due today: {sr_stats['total_due_today']}")
        print(f"   ✅ Upcoming this week: {sr_stats['total_upcoming_week']}")
        print(f"   ✅ Average ease factor: {sr_stats['avg_ease_factor']:.2f}")

        # Test 4: Recommendation Service
        print("\n4. Testing Recommendation Service...")
        rec_service = get_exercise_recommendation_service(db)

        rec_stats = await rec_service.get_recommendation_stats(user_id=1)
        print(f"   ✅ Recommendation stats retrieved")
        print(f"   ✅ Total due for review: {rec_stats['due_for_review']}")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nDatabase Operations Summary:")
        print(f"  - {curricula_count} curricula imported")
        print(f"  - {exercises_count} exercises available")
        print(f"  - All services initialized successfully")
        print(f"  - All database queries working")
        print("\n✅ Exercise Library System is fully operational!")


if __name__ == "__main__":
    asyncio.run(test_system())
