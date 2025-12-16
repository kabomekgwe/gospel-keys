"""
Test Exercise Generator Engine - Phase 8 Week 1

Tests:
- Exercise generation for all types
- Variant generation (beginner/intermediate/advanced)
- Complexity routing
- Integration with type-specific generators
"""

from app.services.exercise_generator_engine import (
    exercise_generator_engine,
    generate_exercise,
    generate_exercise_variants,
    ExerciseType
)


def test_generate_scale_exercise():
    """Test 1: Scale exercise generation"""
    print("=" * 70)
    print("Test 1: Scale Exercise Generation")
    print("=" * 70)

    try:
        exercise = generate_exercise(
            exercise_type="scale",
            context={
                "key": "D",
                "scale_type": "major",
                "practice_pattern": "ascending"
            },
            difficulty="intermediate"
        )

        print(f"\nGenerated Exercise:")
        print(f"  Title: {exercise.title}")
        print(f"  Type: {exercise.exercise_type}")
        print(f"  Key: {exercise.key}")
        print(f"  Difficulty: {exercise.difficulty}")
        print(f"  Tempo: {exercise.tempo_bpm} BPM")
        print(f"  Duration: {exercise.duration_beats} beats")
        print(f"  Notes: {' - '.join(exercise.notes)}")
        print(f"  Complexity: {exercise.complexity}")
        print(f"  Generation: {exercise.generation_method}")
        print(f"  Characteristics: {', '.join(exercise.characteristics)}")

        # Assertions
        assert exercise.exercise_type == "scale", "Should be scale exercise"
        assert exercise.difficulty == "intermediate", "Should be intermediate"
        assert exercise.key == "D", "Should be in D"
        assert exercise.complexity == 1, "Scales should be complexity 1"
        assert exercise.generation_method == "local_pattern", "Should use local generation"
        assert len(exercise.notes) > 0, "Should have notes"
        assert len(exercise.midi_notes) > 0, "Should have MIDI notes"

        print("\n✅ Test 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_variants():
    """Test 2: Variant generation (beginner/intermediate/advanced)"""
    print("\n" + "=" * 70)
    print("Test 2: Variant Generation")
    print("=" * 70)

    try:
        # Generate base exercise
        base_exercise = generate_exercise(
            exercise_type="scale",
            context={
                "key": "C",
                "scale_type": "major",
                "practice_pattern": "ascending"
            },
            difficulty="intermediate"
        )

        print(f"\nBase Exercise: {base_exercise.title}")
        print(f"  Tempo: {base_exercise.tempo_bpm} BPM")
        print(f"  Difficulty: {base_exercise.difficulty}")

        # Generate variants
        variants = generate_exercise_variants(base_exercise, count=3)

        print(f"\nGenerated {len(variants)} variants:")
        for i, variant in enumerate(variants, 1):
            print(f"\n  Variant {i}:")
            print(f"    Difficulty: {variant.difficulty}")
            print(f"    Tempo: {variant.tempo_bpm} BPM")
            print(f"    Practice Tips Count: {len(variant.practice_tips)}")

        # Assertions
        assert len(variants) == 3, "Should generate 3 variants"
        assert variants[0].difficulty == "beginner", "First should be beginner"
        assert variants[1].difficulty == "intermediate", "Second should be intermediate"
        assert variants[2].difficulty == "advanced", "Third should be advanced"

        # Tempo should scale with difficulty
        assert variants[0].tempo_bpm < variants[1].tempo_bpm < variants[2].tempo_bpm, \
            "Tempo should increase with difficulty"

        print("\n✅ Test 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complexity_levels():
    """Test 3: Complexity level mapping"""
    print("\n" + "=" * 70)
    print("Test 3: Complexity Level Mapping")
    print("=" * 70)

    try:
        # Test each exercise type complexity
        expected_complexity = {
            "scale": 1,
            "arpeggio": 2,
            "rhythm": 3,
            "progression": 4,
            "pattern": 5,
            "voicing": 5,
            "voice_leading": 6,
            "lick": 6,
            "ear_training": 7
        }

        print("\nComplexity Levels:")
        for exercise_type, expected in expected_complexity.items():
            actual = exercise_generator_engine.get_complexity(exercise_type)
            is_local = exercise_generator_engine.is_local_generation(exercise_type)
            status = "✓" if actual == expected else "✗"

            print(f"  {status} {exercise_type:15} - Expected: {expected}, Got: {actual}, Local: {is_local}")

            assert actual == expected, f"{exercise_type} complexity mismatch"
            assert is_local is True, f"{exercise_type} should use local generation (complexity <= 7)"

        print("\n✅ Test 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_scale_types():
    """Test 4: Different scale types and patterns"""
    print("\n" + "=" * 70)
    print("Test 4: Different Scale Types and Patterns")
    print("=" * 70)

    try:
        test_cases = [
            {"key": "A", "scale_type": "natural_minor", "pattern": "ascending", "difficulty": "beginner"},
            {"key": "E", "scale_type": "harmonic_minor", "pattern": "ascending_descending", "difficulty": "intermediate"},
            {"key": "G", "scale_type": "dorian", "pattern": "thirds", "difficulty": "advanced"},
        ]

        print("\nGenerating various scale exercises:")
        for i, test_case in enumerate(test_cases, 1):
            exercise = generate_exercise(
                exercise_type="scale",
                context={
                    "key": test_case["key"],
                    "scale_type": test_case["scale_type"],
                    "practice_pattern": test_case["pattern"]
                },
                difficulty=test_case["difficulty"]
            )

            print(f"\n  {i}. {exercise.title}")
            print(f"     Notes: {len(exercise.notes)} total")
            print(f"     Duration: {exercise.duration_beats} beats")
            print(f"     Tempo: {exercise.tempo_bpm} BPM")

            # Assertions
            assert exercise.key == test_case["key"], f"Key mismatch for test {i}"
            assert exercise.difficulty == test_case["difficulty"], f"Difficulty mismatch for test {i}"
            assert len(exercise.notes) > 0, f"No notes for test {i}"

        print("\n✅ Test 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arpeggio_exercises():
    """Test 6: Arpeggio exercise generation"""
    print("\n" + "=" * 70)
    print("Test 6: Arpeggio Exercise Generation")
    print("=" * 70)

    try:
        # Test various arpeggio types
        test_cases = [
            {"key": "C", "chord_type": "major", "pattern": "ascending", "difficulty": "beginner"},
            {"key": "D", "chord_type": "min7", "pattern": "ascending_descending", "difficulty": "intermediate"},
            {"key": "G", "chord_type": "dom9", "pattern": "broken", "difficulty": "advanced", "style": "jazz"},
        ]

        print("\nGenerating various arpeggio exercises:")
        for i, test_case in enumerate(test_cases, 1):
            exercise = generate_exercise(
                exercise_type="arpeggio",
                context=test_case,
                difficulty=test_case["difficulty"]
            )

            print(f"\n  {i}. {exercise.title}")
            print(f"     Notes: {len(exercise.notes)} total")
            print(f"     Duration: {exercise.duration_beats} beats")
            print(f"     Tempo: {exercise.tempo_bpm} BPM")
            print(f"     Characteristics: {', '.join(exercise.characteristics[:3])}")

            # Assertions
            assert exercise.exercise_type == "arpeggio", f"Should be arpeggio for test {i}"
            assert exercise.key == test_case["key"], f"Key mismatch for test {i}"
            assert exercise.complexity == 2, f"Arpeggios should be complexity 2"
            assert len(exercise.notes) > 0, f"No notes for test {i}"

        print("\n✅ Test 6 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exercise_to_dict():
    """Test 5: Exercise serialization to dict"""
    print("\n" + "=" * 70)
    print("Test 5: Exercise Serialization")
    print("=" * 70)

    try:
        exercise = generate_exercise(
            exercise_type="scale",
            context={"key": "F", "scale_type": "major"},
            difficulty="beginner"
        )

        # Convert to dict
        exercise_dict = exercise.to_dict()

        print("\nExercise Dictionary Keys:")
        for key in sorted(exercise_dict.keys()):
            print(f"  - {key}")

        # Assertions
        required_keys = [
            'exercise_type', 'title', 'description', 'notes', 'midi_notes',
            'rhythm', 'duration_beats', 'key', 'tempo_bpm', 'difficulty',
            'characteristics', 'practice_tips', 'complexity', 'generation_method'
        ]

        for key in required_keys:
            assert key in exercise_dict, f"Missing key: {key}"

        assert isinstance(exercise_dict['notes'], list), "Notes should be list"
        assert isinstance(exercise_dict['midi_notes'], list), "MIDI notes should be list"
        assert isinstance(exercise_dict['tempo_bpm'], int), "Tempo should be int"

        print("\n✅ Test 5 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def main():
    print("=" * 70)
    print("EXERCISE GENERATOR ENGINE TESTS - Phase 8 Week 1")
    print("=" * 70)

    results = []

    results.append(("Scale exercise generation", test_generate_scale_exercise()))
    results.append(("Variant generation", test_generate_variants()))
    results.append(("Complexity level mapping", test_complexity_levels()))
    results.append(("Different scale types", test_different_scale_types()))
    results.append(("Exercise serialization", test_exercise_to_dict()))
    results.append(("Arpeggio exercises", test_arpeggio_exercises()))

    print("\n" + "=" * 70)
    print("TEST RESULTS:")
    print("=" * 70)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✅" if passed else "❌"
        print(f"{symbol} {test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print("\n" + "=" * 70)
    print(f"Total: {total_passed}/{total_tests} tests passed")
    print("=" * 70)

    if total_passed == total_tests:
        print("\n🎉 All tests passed! Exercise Generator Engine is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")

    return total_passed == total_tests


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
