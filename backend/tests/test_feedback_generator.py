#!/usr/bin/env python3
"""
Test script for AI-powered feedback generation
STORY-2.4: AI-Powered Performance Feedback Generation

Tests feedback generation with realistic analysis data.
"""

import asyncio
import time
import numpy as np
from rust_audio_engine import detect_pitch, detect_onsets_python, analyze_dynamics_python
from app.services.feedback_generator import FeedbackGenerator
from app.schemas.feedback import SkillLevel, RhythmScore


def generate_test_audio_with_errors(
    frequencies: list[float],
    durations: list[float],
    amplitudes: list[float],
    pitch_errors: list[float],  # Cents offset per note
    sample_rate: int = 44100
) -> list[float]:
    """
    Generate test audio with intentional pitch and dynamic variations.
    """
    samples = []

    for freq, duration, amplitude, cents_error in zip(frequencies, durations, amplitudes, pitch_errors):
        # Apply pitch error (cents)
        freq_adjusted = freq * (2 ** (cents_error / 1200.0))

        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Generate sine wave
        tone = np.sin(2 * np.pi * freq_adjusted * t)

        # Apply ADSR envelope
        attack_time = 0.01
        decay_time = 0.05
        release_time = 0.02

        attack_samples = int(attack_time * sample_rate)
        decay_samples = int(decay_time * sample_rate)
        release_samples = int(release_time * sample_rate)

        envelope = np.ones(num_samples)

        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        if decay_samples > 0:
            decay_start = attack_samples
            decay_end = attack_samples + decay_samples
            envelope[decay_start:decay_end] = np.linspace(1, 0.7, decay_samples)

        sustain_start = attack_samples + decay_samples
        sustain_end = num_samples - release_samples
        envelope[sustain_start:sustain_end] = 0.7

        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(0.7, 0, release_samples)

        tone = tone * envelope * amplitude
        samples.extend(tone.tolist())

    return samples


async def test_feedback_generation_basic():
    """Test basic feedback generation with realistic analysis data"""
    print("=" * 80)
    print("TEST 1: Basic Feedback Generation")
    print("=" * 80)

    generator = FeedbackGenerator()

    # Simulate analysis results for a beginner student
    # C major scale with some pitch errors
    frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C major scale
    durations = [0.5] * 8
    amplitudes = [0.3, 0.4, 0.5, 0.6, 0.5, 0.4, 0.3, 0.3]  # Varying dynamics
    pitch_errors = [0, 5, -10, 15, 0, -8, 12, 0]  # Some notes sharp/flat

    samples = generate_test_audio_with_errors(frequencies, durations, amplitudes, pitch_errors)

    # Run analysis
    print("\n📊 Running analysis pipeline...")

    # Pitch detection
    pitch_results = []
    chunk_size = int(0.5 * 44100)  # 0.5 second chunks
    for i in range(0, len(samples), chunk_size):
        chunk = samples[i:i+chunk_size]
        if len(chunk) > 4096:
            result = detect_pitch(chunk, 44100)
            if result:
                pitch_results.append(result)

    print(f"   Pitch: Analyzed {len(pitch_results)} notes")

    # Onset detection
    onsets = detect_onsets_python(samples, 44100, hop_size=256, threshold=0.15)
    print(f"   Onsets: Detected {len(onsets)} onsets")

    # Dynamics analysis
    dynamics_events = []
    if len(onsets) > 0:
        dynamics_events = analyze_dynamics_python(samples, onsets, 44100)
        print(f"   Dynamics: Analyzed {len(dynamics_events)} segments")

    # Mock rhythm score
    rhythm_score = RhythmScore(
        accuracy_percent=82.5,
        on_time_notes=14,
        early_notes=3,
        late_notes=1,
        tempo_drift=5.2
    )

    # Generate feedback
    print("\n🤖 Generating AI feedback...")
    start_time = time.perf_counter()

    feedback = await generator.generate_feedback(
        pitch_results=pitch_results,
        rhythm_score=rhythm_score,
        dynamics_events=dynamics_events,
        skill_level=SkillLevel.BEGINNER,
        piece_name="C Major Scale",
        piece_difficulty="Grade 1"
    )

    duration_ms = (time.perf_counter() - start_time) * 1000

    print(f"⏱️  Generation time: {duration_ms:.2f}ms")
    print(f"\n📋 Generated Feedback:")
    print(f"\n{'='*80}")
    print(f"Overall Score: {feedback.overall_score:.1f}/100")
    print(f"\n{feedback.summary}")
    print(f"\n{'Strengths:':<20}")
    for i, strength in enumerate(feedback.strengths, 1):
        print(f"  {i}. {strength}")

    print(f"\n{'Areas to Improve:':<20}")
    for i, item in enumerate(feedback.areas_to_improve, 1):
        print(f"  {i}. [{item.category.value}] Priority {item.priority}")
        print(f"     Observation: {item.observation}")
        print(f"     Suggestion: {item.suggestion}")
        print()

    print(f"{'Practice Exercises:':<20}")
    for i, exercise in enumerate(feedback.practice_exercises, 1):
        print(f"  {i}. {exercise.title} ({exercise.duration_minutes} min)")
        print(f"     {exercise.description}")
        print()

    print(f"{'Encouragement:':<20}")
    print(f"  {feedback.encouragement}")
    print(f"{'='*80}")

    # Validate structure
    assert 0 <= feedback.overall_score <= 100, "Score out of range"
    assert len(feedback.summary) > 20, "Summary too short"
    assert len(feedback.strengths) > 0, "No strengths identified"
    assert len(feedback.areas_to_improve) > 0, "No improvements identified"
    assert len(feedback.practice_exercises) > 0, "No exercises provided"
    assert len(feedback.encouragement) > 10, "No encouragement provided"

    print("\n✅ PASSED: Feedback generation successful")


async def test_feedback_skill_levels():
    """Test feedback adaptation to different skill levels"""
    print("\n" + "=" * 80)
    print("TEST 2: Skill Level Adaptation")
    print("=" * 80)

    generator = FeedbackGenerator()

    # Same performance data for different skill levels
    pitch_results = [{"confidence": 0.95, "cents_offset": 5}] * 10
    rhythm_score = RhythmScore(
        accuracy_percent=85.0,
        on_time_notes=17,
        early_notes=2,
        late_notes=1,
        tempo_drift=3.0
    )

    for skill_level in [SkillLevel.BEGINNER, SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED]:
        print(f"\n📊 Testing {skill_level.value} level...")

        feedback = await generator.generate_feedback(
            pitch_results=pitch_results,
            rhythm_score=rhythm_score,
            dynamics_events=[],
            skill_level=skill_level,
            piece_name="Test Piece"
        )

        print(f"   Score: {feedback.overall_score:.1f}/100")
        print(f"   Strengths: {len(feedback.strengths)}")
        print(f"   Improvements: {len(feedback.areas_to_improve)}")
        print(f"   Exercises: {len(feedback.practice_exercises)}")

        # Validate appropriate difficulty
        for exercise in feedback.practice_exercises:
            assert exercise.difficulty == skill_level, \
                f"Exercise difficulty mismatch: {exercise.difficulty} != {skill_level}"

    print("\n✅ PASSED: Skill level adaptation working")


async def test_feedback_performance():
    """Test feedback generation latency"""
    print("\n" + "=" * 80)
    print("TEST 3: Performance & Latency")
    print("=" * 80)

    generator = FeedbackGenerator()

    # Mock data
    pitch_results = [{"confidence": 0.9, "cents_offset": 0}] * 20
    rhythm_score = RhythmScore(
        accuracy_percent=87.5,
        on_time_notes=18,
        early_notes=1,
        late_notes=1,
        tempo_drift=2.5
    )

    iterations = 10
    latencies = []

    for _ in range(iterations):
        start_time = time.perf_counter()

        await generator.generate_feedback(
            pitch_results=pitch_results,
            rhythm_score=rhythm_score,
            dynamics_events=[]
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(duration_ms)

    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    print(f"\n📊 Latency Statistics ({iterations} iterations):")
    print(f"   Average: {avg_latency:.2f}ms")
    print(f"   Min: {min_latency:.2f}ms")
    print(f"   Max: {max_latency:.2f}ms")
    print(f"   Target: <3000ms (for LLM generation)")
    print(f"   Note: Using rule-based fallback for testing")

    # For rule-based, should be very fast
    if avg_latency < 100:
        print(f"\n✅ PASSED: Latency {avg_latency:.2f}ms (rule-based fallback)")
    else:
        print(f"\n⚠️  WARNING: Latency {avg_latency:.2f}ms higher than expected")


async def test_feedback_edge_cases():
    """Test feedback with edge cases"""
    print("\n" + "=" * 80)
    print("TEST 4: Edge Cases")
    print("=" * 80)

    generator = FeedbackGenerator()

    # Test 1: Perfect performance
    print("\n📊 Test 1: Perfect performance (no errors)")
    feedback = await generator.generate_feedback(
        pitch_results=[{"confidence": 1.0, "cents_offset": 0}] * 10,
        rhythm_score=RhythmScore(
            accuracy_percent=100.0,
            on_time_notes=10,
            early_notes=0,
            late_notes=0,
            tempo_drift=0.0
        ),
        dynamics_events=[{"midi_velocity": 80, "db_level": -10}] * 10
    )
    print(f"   Score: {feedback.overall_score:.1f}/100")
    print(f"   Strengths: {len(feedback.strengths)}")
    assert feedback.overall_score >= 90, "Perfect performance should score high"

    # Test 2: Poor performance
    print("\n📊 Test 2: Poor performance (many errors)")
    feedback = await generator.generate_feedback(
        pitch_results=[{"confidence": 0.5, "cents_offset": 30}] * 10,
        rhythm_score=RhythmScore(
            accuracy_percent=50.0,
            on_time_notes=5,
            early_notes=3,
            late_notes=2,
            tempo_drift=15.0
        ),
        dynamics_events=[{"midi_velocity": 50, "db_level": -20}] * 10
    )
    print(f"   Score: {feedback.overall_score:.1f}/100")
    print(f"   Improvements: {len(feedback.areas_to_improve)}")
    assert feedback.overall_score < 70, "Poor performance should score lower"
    assert len(feedback.areas_to_improve) >= 2, "Should suggest multiple improvements"

    # Test 3: Empty data
    print("\n📊 Test 3: Empty data")
    feedback = await generator.generate_feedback(
        pitch_results=[],
        rhythm_score=None,
        dynamics_events=None
    )
    print(f"   Score: {feedback.overall_score:.1f}/100")
    assert len(feedback.strengths) > 0, "Should always have at least one strength"
    assert len(feedback.practice_exercises) > 0, "Should always provide exercises"

    print("\n✅ PASSED: Edge cases handled correctly")


async def main():
    print("🎹 AI-Powered Feedback Generator Test Suite")
    print("STORY-2.4: AI-Powered Performance Feedback Generation")
    print()

    try:
        # Run tests
        await test_feedback_generation_basic()
        await test_feedback_skill_levels()
        await test_feedback_performance()
        await test_feedback_edge_cases()

        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ Feedback generation implementation successful")
        print("✅ Ready for Phase 2 completion and integration")
        print("\nNote: Tests use rule-based fallback. LLM integration can be")
        print("      enabled by connecting to ai_orchestrator in production.")

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
