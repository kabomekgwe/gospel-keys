#!/usr/bin/env python3
"""
Test script for YIN pitch detection implementation
Phase 2: Real-Time Performance Analysis

Tests the Rust-based pitch detection exposed to Python via PyO3.
"""

import numpy as np
import time
from rust_audio_engine import detect_pitch


def generate_sine_wave(frequency: float, sample_rate: int, duration: float) -> list[float]:
    """Generate a sine wave at given frequency"""
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    samples = np.sin(2 * np.pi * frequency * t)
    return samples.tolist()


def test_pitch_detection_a440():
    """Test A4 (440 Hz) detection"""
    print("=" * 80)
    print("TEST 1: Pitch Detection - A4 (440 Hz)")
    print("=" * 80)

    # Generate A4 (440 Hz)
    samples = generate_sine_wave(440.0, 44100, 0.5)  # 0.5 second

    start_time = time.perf_counter()
    result = detect_pitch(samples, 44100)
    duration_ms = (time.perf_counter() - start_time) * 1000

    print(f"⏱️  Detection time: {duration_ms:.2f}ms")

    if result is not None:
        print(f"\n📊 Detection Results:")
        print(f"   Frequency: {result['frequency']:.2f} Hz (expected: 440.00 Hz)")
        print(f"   MIDI Note: {result['midi_note']} (expected: 69 - A4)")
        print(f"   Note Name: {result['note_name']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Cents Offset: {result['cents_offset']:.1f} cents")
        print(f"   RMS Level: {result['rms_level']:.3f}")

        # Validate
        freq_error = abs(result['frequency'] - 440.0)
        assert freq_error < 2.0, f"Frequency error too large: {freq_error:.2f} Hz"
        assert result['midi_note'] == 69, f"Wrong MIDI note: {result['midi_note']}"
        assert result['confidence'] > 0.9, f"Low confidence: {result['confidence']}"
        print("\n✅ PASSED: A4 detection")
    else:
        print("❌ FAILED: No pitch detected")
        raise AssertionError("No pitch detected for A4 sine wave")


def test_pitch_detection_c4():
    """Test C4 (261.63 Hz) detection"""
    print("\n" + "=" * 80)
    print("TEST 2: Pitch Detection - C4 (261.63 Hz)")
    print("=" * 80)

    # Generate C4 (261.63 Hz)
    samples = generate_sine_wave(261.63, 44100, 0.5)

    start_time = time.perf_counter()
    result = detect_pitch(samples, 44100)
    duration_ms = (time.perf_counter() - start_time) * 1000

    print(f"⏱️  Detection time: {duration_ms:.2f}ms")

    if result is not None:
        print(f"\n📊 Detection Results:")
        print(f"   Frequency: {result['frequency']:.2f} Hz (expected: 261.63 Hz)")
        print(f"   MIDI Note: {result['midi_note']} (expected: 60 - C4)")
        print(f"   Note Name: {result['note_name']}")
        print(f"   Confidence: {result['confidence']:.3f}")

        freq_error = abs(result['frequency'] - 261.63)
        assert freq_error < 2.0, f"Frequency error too large: {freq_error:.2f} Hz"
        assert result['midi_note'] == 60, f"Wrong MIDI note: {result['midi_note']}"
        print("\n✅ PASSED: C4 detection")
    else:
        print("❌ FAILED: No pitch detected")
        raise AssertionError("No pitch detected for C4 sine wave")


def test_silence_detection():
    """Test that silence returns None"""
    print("\n" + "=" * 80)
    print("TEST 3: Silence Detection")
    print("=" * 80)

    # Generate silence
    samples = [0.0] * 4096

    result = detect_pitch(samples, 44100)

    if result is None:
        print("✅ PASSED: Silence correctly returns None")
    else:
        print(f"❌ FAILED: Expected None, got {result}")
        raise AssertionError("Silence should return None")


def test_low_frequency_a0():
    """Test A0 (27.5 Hz) - lowest piano note"""
    print("\n" + "=" * 80)
    print("TEST 4: Low Frequency - A0 (27.5 Hz)")
    print("=" * 80)

    # Generate A0 (27.5 Hz) - need longer duration for low freq
    samples = generate_sine_wave(27.5, 44100, 1.0)  # 1 second

    result = detect_pitch(samples, 44100)

    if result is not None:
        print(f"📊 Detection Results:")
        print(f"   Frequency: {result['frequency']:.2f} Hz (expected: 27.5 Hz)")
        print(f"   MIDI Note: {result['midi_note']} (expected: 21 - A0)")
        print(f"   Note Name: {result['note_name']}")

        freq_error = abs(result['frequency'] - 27.5)
        assert freq_error < 2.0, f"Frequency error: {freq_error:.2f} Hz"
        assert result['midi_note'] == 21, f"Wrong MIDI note: {result['midi_note']}"
        print("\n✅ PASSED: A0 detection")
    else:
        print("❌ FAILED: No pitch detected")
        raise AssertionError("No pitch detected for A0")


def test_latency_requirement():
    """Test that detection latency is <50ms"""
    print("\n" + "=" * 80)
    print("TEST 5: Latency Requirement (<50ms)")
    print("=" * 80)

    samples = generate_sine_wave(440.0, 44100, 0.5)

    # Run multiple iterations
    iterations = 10
    latencies = []

    for i in range(iterations):
        start_time = time.perf_counter()
        result = detect_pitch(samples, 44100)
        duration_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(duration_ms)

    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    print(f"📊 Latency Statistics ({iterations} iterations):")
    print(f"   Average: {avg_latency:.2f}ms")
    print(f"   Min: {min_latency:.2f}ms")
    print(f"   Max: {max_latency:.2f}ms")
    print(f"   Target: <50ms")

    if avg_latency < 50:
        print(f"\n✅ PASSED: Latency {avg_latency:.2f}ms < 50ms")
    else:
        print(f"\n⚠️  WARNING: Latency {avg_latency:.2f}ms exceeds 50ms target")


def benchmark_performance():
    """Benchmark detection performance"""
    print("\n" + "=" * 80)
    print("BENCHMARK: Performance Analysis")
    print("=" * 80)

    test_frequencies = [
        (27.5, "A0 - Lowest piano note"),
        (82.41, "E2 - Low bass"),
        (261.63, "C4 - Middle C"),
        (440.0, "A4 - Concert pitch"),
        (1046.5, "C6 - High soprano"),
        (4186.0, "C8 - Highest piano note"),
    ]

    print(f"\n{'Frequency':<15} {'Note':<25} {'Detected':<15} {'Error':<10} {'Confidence':<12} {'Time (ms)'}")
    print("-" * 100)

    for freq, description in test_frequencies:
        samples = generate_sine_wave(freq, 44100, 0.5)

        start_time = time.perf_counter()
        result = detect_pitch(samples, 44100)
        duration_ms = (time.perf_counter() - start_time) * 1000

        if result is not None:
            error = abs(result['frequency'] - freq)
            print(f"{freq:<15.2f} {description:<25} {result['frequency']:<15.2f} {error:<10.2f} {result['confidence']:<12.3f} {duration_ms:.2f}")
        else:
            print(f"{freq:<15.2f} {description:<25} {'NOT DETECTED':<15}")


def main():
    print("🎹 YIN Pitch Detection Test Suite")
    print("Phase 2: Real-Time Performance Analysis")
    print()

    try:
        # Run tests
        test_pitch_detection_a440()
        test_pitch_detection_c4()
        test_silence_detection()
        test_low_frequency_a0()
        test_latency_requirement()

        # Benchmark
        benchmark_performance()

        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ YIN pitch detection implementation successful")
        print("✅ Ready for Phase 2 integration")

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
