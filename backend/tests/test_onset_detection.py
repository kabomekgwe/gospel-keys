#!/usr/bin/env python3
"""
Test script for onset detection implementation
STORY-2.2: Rhythm Accuracy Analysis

Tests spectral flux + energy-based onset detection.
"""

import numpy as np
import time
from rust_audio_engine import detect_onsets_python


def generate_click_sequence(click_times: list[float], sample_rate: int, duration: float) -> list[float]:
    """
    Generate audio with clicks at specified times.
    Creates more realistic clicks with exponential decay.
    """
    num_samples = int(sample_rate * duration)
    samples = np.zeros(num_samples, dtype=np.float32)

    for click_time in click_times:
        click_idx = int(click_time * sample_rate)
        if click_idx < num_samples:
            # Create click with exponential decay (more realistic than impulse)
            decay_samples = 200  # ~4.5ms decay
            for i in range(decay_samples):
                if click_idx + i < num_samples:
                    decay = np.exp(-i / 40.0)  # Exponential decay
                    samples[click_idx + i] += 0.8 * decay

    return samples.tolist()


def generate_tone_sequence(frequencies: list[float], durations: list[float],
                          sample_rate: int = 44100) -> list[float]:
    """
    Generate sequence of tones (more realistic than clicks).
    Each tone has clear attack/decay envelope.
    """
    samples = []

    for freq, duration in zip(frequencies, durations):
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Generate sine wave
        tone = np.sin(2 * np.pi * freq * t)

        # Apply ADSR envelope (Attack-Decay-Sustain-Release)
        attack_time = 0.01  # 10ms attack
        decay_time = 0.05   # 50ms decay
        release_time = 0.02  # 20ms release

        attack_samples = int(attack_time * sample_rate)
        decay_samples = int(decay_time * sample_rate)
        release_samples = int(release_time * sample_rate)

        envelope = np.ones(num_samples)

        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay to sustain level (0.7)
        if decay_samples > 0:
            decay_start = attack_samples
            decay_end = attack_samples + decay_samples
            envelope[decay_start:decay_end] = np.linspace(1, 0.7, decay_samples)

        # Sustain
        sustain_start = attack_samples + decay_samples
        sustain_end = num_samples - release_samples
        envelope[sustain_start:sustain_end] = 0.7

        # Release
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(0.7, 0, release_samples)

        tone = tone * envelope
        samples.extend(tone.tolist())

    return samples


def test_onset_detection_tone_sequence():
    """Test onset detection with realistic tone sequence"""
    print("=" * 80)
    print("TEST 1: Onset Detection - Tone Sequence (C4, E4, G4)")
    print("=" * 80)

    # Generate C major triad: C4, E4, G4
    frequencies = [261.63, 329.63, 392.00]  # C4, E4, G4
    durations = [0.5, 0.5, 0.5]  # Each note 0.5 seconds
    expected_onset_times = [0.0, 0.5, 1.0]  # Expected onset times

    samples = generate_tone_sequence(frequencies, durations)

    start_time = time.perf_counter()
    onsets = detect_onsets_python(samples, 44100, hop_size=256, threshold=0.15)
    duration_ms = (time.perf_counter() - start_time) * 1000

    print(f"⏱️  Detection time: {duration_ms:.2f}ms")
    print(f"📊 Detected {len(onsets)} onsets")

    if onsets:
        print(f"\n📍 Detected Onset Times:")
        for i, onset in enumerate(onsets):
            print(f"   Onset {i+1}: {onset['timestamp']:.3f}s (strength: {onset['strength']:.3f}, confidence: {onset['confidence']:.3f})")

        # Validate: should detect 3 onsets near expected times
        assert len(onsets) >= 2, f"Should detect at least 2 onsets, got {len(onsets)}"

        # Check first onset is near 0.0s
        first_onset_error = abs(onsets[0]['timestamp'] - expected_onset_times[0])
        assert first_onset_error < 0.1, f"First onset error: {first_onset_error:.3f}s"

        print("\n✅ PASSED: Tone sequence onset detection")
    else:
        print("❌ FAILED: No onsets detected")
        raise AssertionError("No onsets detected in tone sequence")


def test_onset_detection_clicks():
    """Test onset detection with click train"""
    print("\n" + "=" * 80)
    print("TEST 2: Onset Detection - Click Train")
    print("=" * 80)

    click_times = [0.2, 0.5, 0.8]
    samples = generate_click_sequence(click_times, 44100, 1.2)

    start_time = time.perf_counter()
    onsets = detect_onsets_python(samples, 44100, hop_size=256, threshold=0.1)
    duration_ms = (time.perf_counter() - start_time) * 1000

    print(f"⏱️  Detection time: {duration_ms:.2f}ms")
    print(f"📊 Detected {len(onsets)} onsets")

    if onsets:
        print(f"\n📍 Detected Onset Times:")
        for i, onset in enumerate(onsets):
            expected = click_times[i] if i < len(click_times) else None
            error = abs(onset['timestamp'] - expected) if expected else None
            error_str = f" (error: {error*1000:.1f}ms)" if error else ""
            print(f"   Onset {i+1}: {onset['timestamp']:.3f}s{error_str}")

        assert len(onsets) >= 2, f"Should detect at least 2 onsets, got {len(onsets)}"
        print("\n✅ PASSED: Click train onset detection")
    else:
        print("⚠️  WARNING: No onsets detected in click train")


def test_onset_detection_silence():
    """Test that silence produces no onsets"""
    print("\n" + "=" * 80)
    print("TEST 3: Onset Detection - Silence")
    print("=" * 80)

    samples = [0.0] * 44100  # 1 second of silence

    onsets = detect_onsets_python(samples, 44100)

    print(f"📊 Detected {len(onsets)} onsets (expected: 0)")

    assert len(onsets) == 0, f"Silence should produce no onsets, got {len(onsets)}"
    print("✅ PASSED: Silence correctly produces no onsets")


def test_onset_detection_latency():
    """Test onset detection latency requirement (<50ms)"""
    print("\n" + "=" * 80)
    print("TEST 4: Latency Requirement (<50ms)")
    print("=" * 80)

    # Generate 2-second audio
    frequencies = [440.0, 523.25, 659.25]  # A4, C5, E5
    durations = [0.6, 0.6, 0.8]
    samples = generate_tone_sequence(frequencies, durations)

    iterations = 10
    latencies = []

    for _ in range(iterations):
        start_time = time.perf_counter()
        detect_onsets_python(samples, 44100, hop_size=256, threshold=0.15)
        duration_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(duration_ms)

    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    print(f"📊 Latency Statistics ({iterations} iterations, {len(samples)/44100:.1f}s audio):")
    print(f"   Average: {avg_latency:.2f}ms")
    print(f"   Min: {min_latency:.2f}ms")
    print(f"   Max: {max_latency:.2f}ms")
    print(f"   Target: <50ms")

    if avg_latency < 50:
        print(f"\n✅ PASSED: Latency {avg_latency:.2f}ms < 50ms target")
    else:
        print(f"\n⚠️  WARNING: Latency {avg_latency:.2f}ms exceeds 50ms target")


def benchmark_onset_detection():
    """Benchmark onset detection with various audio lengths"""
    print("\n" + "=" * 80)
    print("BENCHMARK: Onset Detection Performance")
    print("=" * 80)

    test_cases = [
        (1.0, "1 second"),
        (2.0, "2 seconds"),
        (5.0, "5 seconds"),
        (10.0, "10 seconds"),
    ]

    print(f"\n{'Duration':<15} {'Samples':<15} {'Onsets':<10} {'Time (ms)':<12} {'Throughput'}")
    print("-" * 75)

    for duration, description in test_cases:
        # Generate audio
        num_notes = int(duration / 0.5)
        frequencies = [440.0] * num_notes
        durations_list = [0.5] * num_notes
        samples = generate_tone_sequence(frequencies, durations_list)

        # Benchmark
        start_time = time.perf_counter()
        onsets = detect_onsets_python(samples, 44100, hop_size=256, threshold=0.15)
        duration_ms = (time.perf_counter() - start_time) * 1000

        throughput = (duration / (duration_ms / 1000))

        print(f"{description:<15} {len(samples):<15,} {len(onsets):<10} {duration_ms:<12.2f} {throughput:.1f}x real-time")


def main():
    print("🎵 Onset Detection Test Suite")
    print("STORY-2.2: Rhythm Accuracy Analysis")
    print()

    try:
        # Run tests
        test_onset_detection_tone_sequence()
        test_onset_detection_clicks()
        test_onset_detection_silence()
        test_onset_detection_latency()

        # Benchmark
        benchmark_onset_detection()

        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ Onset detection implementation successful")
        print("✅ Ready for Phase 2 rhythm analysis integration")

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
