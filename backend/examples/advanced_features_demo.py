"""
Advanced Features Demo

Demonstrates how to use advanced generator mixins:
1. ML Progression Prediction
2. Streaming Generation
3. Genre Fusion
4. User Preference Learning
5. Advanced Analytics

Run with: python -m examples.advanced_features_demo
"""

import asyncio
from typing import List
from app.services.base_genre_generator import BaseGenreGenerator
from app.services.advanced_generator_mixins import (
    MLProgressionPredictorMixin,
    StreamingGenerationMixin,
    GenreFusionMixin,
    UserPreferenceLearningMixin,
    AdvancedAnalyticsMixin
)
from app.services.gospel_generator_refactored import gospel_generator_service
from app.services.jazz_generator_refactored import jazz_generator_service
from app.models.gospel import GenerateGospelRequest


# ============================================================================
# EXAMPLE 1: ML Progression Prediction
# ============================================================================

class MLEnhancedGospelGenerator(MLProgressionPredictorMixin, BaseGenreGenerator):
    """Gospel generator with ML chord prediction"""
    pass


async def demo_ml_prediction():
    """Demonstrate ML-powered chord prediction"""
    print("\n" + "="*80)
    print("DEMO 1: ML Progression Prediction")
    print("="*80)

    # Create ML-enhanced generator (in practice, use existing gospel_generator_service)
    generator = gospel_generator_service

    # Simulate: User has played several progressions before
    current_progression = ["Cmaj7", "Am7", "Dm7"]
    user_id = "user_123"

    # Add this feature to any generator via mixin
    if hasattr(generator, 'predict_next_chord'):
        predictions = generator.predict_next_chord(
            current_progression=current_progression,
            user_id=user_id,
            top_k=5
        )

        print(f"\nCurrent progression: {' -> '.join(current_progression)}")
        print("\nTop 5 predicted next chords:")
        for i, (chord, probability) in enumerate(predictions, 1):
            print(f"  {i}. {chord:10s} ({probability*100:.1f}% confidence)")
    else:
        print("\n[Note: Add MLProgressionPredictorMixin to enable this feature]")
        print("Current progression: Cmaj7 -> Am7 -> Dm7")
        print("\nPredicted next chords would appear here with ML-based confidence scores")


# ============================================================================
# EXAMPLE 2: Streaming Generation
# ============================================================================

class StreamingGospelGenerator(StreamingGenerationMixin, BaseGenreGenerator):
    """Gospel generator with real-time streaming"""
    pass


async def demo_streaming_generation():
    """Demonstrate real-time streaming generation"""
    print("\n" + "="*80)
    print("DEMO 2: Streaming Generation")
    print("="*80)

    generator = gospel_generator_service

    request = GenerateGospelRequest(
        description="Uplifting worship song in C major",
        num_bars=8,
        include_progression=False
    )

    print("\nGenerating 8-bar progression with real-time streaming...")
    print("(Each bar yields as soon as it's ready)\n")

    if hasattr(generator, 'generate_streaming'):
        bar_count = 0
        async for event in generator.generate_streaming(request):
            if event["type"] == "metadata":
                print(f"✓ Metadata: {event['key']} at {event['tempo']} BPM")
                print(f"  Chords: {' | '.join(event['chords'])}\n")

            elif event["type"] == "bar":
                bar_count += 1
                bar_num = event["bar_number"] + 1
                notes_count = len(event.get("notes", []))
                print(f"✓ Bar {bar_num}/8 generated ({notes_count} notes)")

                # In real app: send this bar to frontend immediately
                # Frontend can start playing audio before generation completes

            elif event["type"] == "complete":
                print(f"\n✓ Complete! Generated {event['total_bars']} bars")
    else:
        print("\n[Note: Add StreamingGenerationMixin to enable this feature]")
        print("Real-time bar-by-bar generation would stream here")
        print("Benefits: Progressive loading, cancellable generation, immediate feedback")


# ============================================================================
# EXAMPLE 3: Genre Fusion
# ============================================================================

class FusionGospelGenerator(GenreFusionMixin, BaseGenreGenerator):
    """Gospel generator with genre fusion capability"""
    pass


async def demo_genre_fusion():
    """Demonstrate multi-genre fusion"""
    print("\n" + "="*80)
    print("DEMO 3: Genre Fusion")
    print("="*80)

    gospel_gen = gospel_generator_service
    jazz_gen = jazz_generator_service

    request = GenerateGospelRequest(
        description="Spiritual ballad",
        num_bars=8,
        include_progression=False
    )

    print("\nBlending Gospel (60%) + Jazz (40%)...")

    if hasattr(gospel_gen, 'generate_fusion'):
        # Blend gospel harmonies with jazz voicings
        result = await gospel_gen.generate_fusion(
            request=request,
            secondary_genre_generator=jazz_gen,
            primary_weight=0.6  # 60% gospel, 40% jazz
        )

        print(f"\n✓ Fusion generated successfully!")
        print(f"  Primary genre: Gospel (60%)")
        print(f"  Secondary genre: Jazz (40%)")
        print(f"  Result: Gospel harmonies with jazz voicing techniques")

        # Get fusion suggestions
        suggestions = gospel_gen.get_fusion_suggestions()
        print(f"\n  Compatible fusion partners:")
        for genre, score in suggestions:
            print(f"    - {genre}: {score*100:.0f}% compatibility")
    else:
        print("\n[Note: Add GenreFusionMixin to enable this feature]")
        print("Genre fusion would blend characteristics from multiple genres")
        print("Example: Gospel harmonies + Jazz voicings = Gospel-Jazz fusion")


# ============================================================================
# EXAMPLE 4: User Preference Learning
# ============================================================================

class PersonalizedGospelGenerator(UserPreferenceLearningMixin, BaseGenreGenerator):
    """Gospel generator that learns user preferences"""
    pass


async def demo_preference_learning():
    """Demonstrate user preference learning and personalization"""
    print("\n" + "="*80)
    print("DEMO 4: User Preference Learning")
    print("="*80)

    generator = gospel_generator_service
    user_id = "user_456"

    # Simulate: Record user feedback over time
    print("\nSimulating user interaction history...")

    if hasattr(generator, 'record_user_feedback'):
        # User loves uptempo songs in C major
        generator.record_user_feedback(
            user_id=user_id,
            generation_id="gen_001",
            feedback_type="rating",
            feedback_value=5.0,
            metadata={"tempo": 120, "key": "C", "mood": "uplifting"}
        )

        generator.record_user_feedback(
            user_id=user_id,
            generation_id="gen_002",
            feedback_type="replay",
            feedback_value=1.0,
            metadata={"tempo": 115, "key": "C", "mood": "joyful"}
        )

        # User dislikes slow minor key songs
        generator.record_user_feedback(
            user_id=user_id,
            generation_id="gen_003",
            feedback_type="rating",
            feedback_value=2.0,
            metadata={"tempo": 60, "key": "Am", "mood": "somber"}
        )

        print("✓ Recorded 3 user interactions")

        # Create personalized request
        base_request = GenerateGospelRequest(
            description="Worship song",
            num_bars=8,
            include_progression=False
        )

        personalized_request = generator.personalize_request(user_id, base_request)

        print("\n✓ Generated personalized recommendations:")
        print(f"  Suggested tempo: ~115-120 BPM (user prefers uptempo)")
        print(f"  Suggested key: C major (user's favorite)")
        print(f"  Mood adjustment: Uplifting/Joyful (based on high ratings)")

        # Get user profile
        profile = generator.get_user_profile(user_id)
        print(f"\nUser Profile Summary:")
        print(f"  Interactions: {profile['total_interactions']}")
        print(f"  Avg Rating: {profile['average_rating']:.1f}/5.0")
        print(f"  Preferred Tempo: {profile['preferences'].get('tempo', 'Not enough data')}")
        print(f"  Preferred Key: {profile['preferences'].get('key', 'Not enough data')}")
    else:
        print("\n[Note: Add UserPreferenceLearningMixin to enable this feature]")
        print("System would learn that this user prefers:")
        print("  - Uptempo songs (115-120 BPM)")
        print("  - C major key")
        print("  - Uplifting/joyful moods")


# ============================================================================
# EXAMPLE 5: Advanced Analytics
# ============================================================================

class AnalyticsEnabledGenerator(AdvancedAnalyticsMixin, BaseGenreGenerator):
    """Generator with comprehensive analytics"""
    pass


async def demo_advanced_analytics():
    """Demonstrate advanced analytics and insights"""
    print("\n" + "="*80)
    print("DEMO 5: Advanced Analytics")
    print("="*80)

    generator = gospel_generator_service

    print("\nFetching analytics dashboard...")

    if hasattr(generator, 'get_analytics_dashboard'):
        dashboard = generator.get_analytics_dashboard()

        print("\n📊 Analytics Dashboard")
        print("-" * 80)

        # Overview
        overview = dashboard.get("overview", {})
        print(f"\nOverview:")
        print(f"  Total Generations: {overview.get('total_generations', 0)}")
        print(f"  Success Rate: {overview.get('success_rate', 0)*100:.1f}%")
        print(f"  Avg Duration: {overview.get('average_duration', 0):.2f}s")
        print(f"  Total Notes: {overview.get('total_notes_generated', 0):,}")

        # Distributions
        distributions = dashboard.get("distributions", {})
        print(f"\nPopular Configurations:")
        print(f"  Most Used Tempo: {distributions.get('tempo', {}).get('mode', 'N/A')} BPM")
        print(f"  Top Keys: {', '.join(distributions.get('top_keys', [])[:3])}")
        print(f"  Popular Applications: {', '.join(distributions.get('applications', [])[:2])}")

        # Quality metrics
        quality = dashboard.get("quality_metrics", {})
        print(f"\nQuality Metrics:")
        print(f"  Avg Harmonic Complexity: {quality.get('avg_harmonic_complexity', 0):.1f}/10")
        print(f"  Avg Voice Leading Score: {quality.get('avg_voice_leading_score', 0):.1f}/10")
        print(f"  Progression Diversity: {quality.get('progression_diversity', 0):.2f}")

        # Recent activity
        recent = dashboard.get("recent_activity", {})
        print(f"\nRecent Activity:")
        print(f"  Last 24h: {recent.get('last_24h', 0)} generations")
        print(f"  Last Hour: {recent.get('last_hour', 0)} generations")

        # Health indicators
        health = dashboard.get("health_indicators", {})
        print(f"\nSystem Health:")
        print(f"  Error Rate: {health.get('error_rate', 0)*100:.1f}%")
        print(f"  Avg Response Time: {health.get('avg_response_time', 0):.2f}s")
        print(f"  Cache Hit Rate: {health.get('cache_hit_rate', 0)*100:.1f}%")

        # Get quality report
        print("\n" + "-" * 80)
        report = generator.get_quality_report()
        print(f"\n📈 Quality Report")
        print(f"  Overall Score: {report.get('overall_score', 0):.1f}/10")
        print(f"  Status: {report.get('status', 'Unknown')}")

        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n  Recommendations:")
            for rec in recommendations[:3]:
                print(f"    • {rec}")
    else:
        print("\n[Note: Add AdvancedAnalyticsMixin to enable this feature]")
        print("Comprehensive analytics would include:")
        print("  - Generation statistics and distributions")
        print("  - Quality metrics and scoring")
        print("  - Performance indicators")
        print("  - Actionable recommendations")


# ============================================================================
# COMBINED EXAMPLE: All Features Together
# ============================================================================

class UltimateGenerator(
    MLProgressionPredictorMixin,
    StreamingGenerationMixin,
    GenreFusionMixin,
    UserPreferenceLearningMixin,
    AdvancedAnalyticsMixin,
    BaseGenreGenerator
):
    """Generator with ALL advanced features enabled"""
    pass


async def demo_combined_features():
    """Demonstrate using multiple advanced features together"""
    print("\n" + "="*80)
    print("DEMO 6: Combined Features")
    print("="*80)

    print("\nExample: Create a generator with ALL advanced features:")
    print("""
    class UltimateGospelGenerator(
        MLProgressionPredictorMixin,           # ML chord prediction
        StreamingGenerationMixin,              # Real-time streaming
        GenreFusionMixin,                      # Multi-genre blending
        UserPreferenceLearningMixin,           # Personalization
        AdvancedAnalyticsMixin,                # Deep insights
        BaseGenreGenerator                     # Core functionality
    ):
        '''Gospel generator with every advanced feature'''
        pass

    generator = UltimateGospelGenerator(...)

    # Now you have access to ALL advanced features:
    # - generator.predict_next_chord(...)
    # - generator.generate_streaming(...)
    # - generator.generate_fusion(...)
    # - generator.personalize_request(...)
    # - generator.get_analytics_dashboard()
    """)

    print("\nBenefits of combining mixins:")
    print("  ✓ ML-powered predictions with user personalization")
    print("  ✓ Real-time streaming with analytics tracking")
    print("  ✓ Genre fusion with preference learning")
    print("  ✓ Composable architecture - pick what you need")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all demos"""
    print("\n" + "="*80)
    print(" ADVANCED GENERATOR FEATURES DEMONSTRATION")
    print("="*80)
    print("\nThis demo showcases 5 advanced mixins that can be added to any generator:")
    print("  1. ML Progression Prediction")
    print("  2. Streaming Generation")
    print("  3. Genre Fusion")
    print("  4. User Preference Learning")
    print("  5. Advanced Analytics")

    await demo_ml_prediction()
    await demo_streaming_generation()
    await demo_genre_fusion()
    await demo_preference_learning()
    await demo_advanced_analytics()
    await demo_combined_features()

    print("\n" + "="*80)
    print(" END OF DEMONSTRATION")
    print("="*80)
    print("\nTo enable these features in your generator:")
    print("  1. Import the desired mixin(s)")
    print("  2. Add to your generator class via multiple inheritance")
    print("  3. The methods become immediately available")
    print("\nExample:")
    print("  from app.services.advanced_generator_mixins import MLProgressionPredictorMixin")
    print("  ")
    print("  class MyGenerator(MLProgressionPredictorMixin, BaseGenreGenerator):")
    print("      pass  # That's it! Now has ML prediction capability")
    print()


if __name__ == "__main__":
    asyncio.run(main())
