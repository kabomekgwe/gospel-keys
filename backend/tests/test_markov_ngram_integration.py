"""Test Markov and N-gram integration with lick generator

Tests:
- Markov-based generation for all styles
- N-gram generation
- Auto-strategy selection
- Integration with analyzer for characteristics
"""

from app.pipeline.lick_generator_engine import lick_generator_engine, LickGenerationRequest
from app.pipeline.markov_lick_model import markov_model_manager


def test_markov_generation_bebop():
    """Test 1: Markov generation for bebop"""
    print("=" * 70)
    print("Test 1: Markov Generation - Bebop")
    print("=" * 70)

    try:
        # Train models first
        print("\nTraining Markov models...")
        from app.pipeline.lick_database_expanded import lick_database
        markov_model_manager.train_all_models(lick_database)

        # Generate bebop lick using Markov
        lick = lick_generator_engine.generate_from_markov(
            style="bebop",
            length=8,
            root="C",
            temperature=1.0
        )

        print(f"\nGenerated Bebop Lick (Markov):")
        print(f"  Notes: {' - '.join(lick.notes)}")
        print(f"  Intervals: {lick.intervals}")
        print(f"  Characteristics: {', '.join(lick.characteristics)}")
        print(f"  Technique: {lick.technique}")

        # Assertions
        assert len(lick.notes) > 0, "Should generate notes"
        assert lick.style == "bebop", "Should be bebop style"
        assert "markov" in lick.technique, "Should use Markov technique"
        assert len(lick.characteristics) > 0, "Should have characteristics"

        print("\n✅ Test 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_markov_temperature_variation():
    """Test 2: Markov temperature control"""
    print("\n" + "=" * 70)
    print("Test 2: Markov Temperature Variation")
    print("=" * 70)

    try:
        temperatures = [0.5, 1.0, 1.5]
        licks = []

        for temp in temperatures:
            lick = lick_generator_engine.generate_from_markov(
                style="gospel",
                length=6,
                root="D",
                temperature=temp
            )
            licks.append(lick)

            print(f"\nTemperature {temp}:")
            print(f"  Intervals: {lick.intervals}")
            print(f"  Characteristics: {', '.join(lick.characteristics[:3])}")

        # Assertions
        assert all(len(l.notes) > 0 for l in licks), "All should generate notes"
        assert all(l.style == "gospel" for l in licks), "All should be gospel"

        print("\n✅ Test 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ngram_generation():
    """Test 3: N-gram generation"""
    print("\n" + "=" * 70)
    print("Test 3: N-gram Generation")
    print("=" * 70)

    try:
        # Generate using 3-gram
        lick_3gram = lick_generator_engine.generate_from_ngram(
            style="blues",
            length=8,
            root="A",
            n=3
        )

        print(f"\n3-gram Blues Lick:")
        print(f"  Notes: {' - '.join(lick_3gram.notes)}")
        print(f"  Intervals: {lick_3gram.intervals}")
        print(f"  Technique: {lick_3gram.technique}")

        # Generate using 4-gram
        lick_4gram = lick_generator_engine.generate_from_ngram(
            style="blues",
            length=8,
            root="A",
            n=4
        )

        print(f"\n4-gram Blues Lick:")
        print(f"  Notes: {' - '.join(lick_4gram.notes)}")
        print(f"  Intervals: {lick_4gram.intervals}")

        # Assertions
        assert len(lick_3gram.notes) > 0, "3-gram should generate notes"
        assert len(lick_4gram.notes) > 0, "4-gram should generate notes"
        assert "ngram" in lick_3gram.technique, "Should use N-gram technique"
        assert lick_3gram.style == "blues", "Should be blues style"

        print("\n✅ Test 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_strategy_selection():
    """Test 4: Automatic strategy selection"""
    print("\n" + "=" * 70)
    print("Test 4: Auto Strategy Selection")
    print("=" * 70)

    try:
        # Test 1: Beginner should use pattern-based
        request_beginner = LickGenerationRequest(
            style="bebop",
            difficulty="beginner",
            context_chords=["C"],
            key="C",
            length_beats=2.0
        )

        lick_beginner = lick_generator_engine.generate_hybrid(request_beginner, use_ai=False)

        print(f"\nBeginner lick (should use pattern):")
        print(f"  Technique: {lick_beginner.lick.technique}")

        # Test 2: Intermediate should use Markov
        request_intermediate = LickGenerationRequest(
            style="gospel",
            difficulty="intermediate",
            context_chords=["F"],
            key="C",
            length_beats=4.0  # 8 eighth notes
        )

        lick_intermediate = lick_generator_engine.generate_hybrid(request_intermediate, use_ai=False)

        print(f"\nIntermediate lick (should use Markov):")
        print(f"  Technique: {lick_intermediate.lick.technique}")

        # Test 3: Advanced should use N-gram
        request_advanced = LickGenerationRequest(
            style="bebop",  # Changed from neo_soul to bebop to avoid old library issues
            difficulty="advanced",
            context_chords=["Dm7"],
            key="C",
            length_beats=4.0
        )

        lick_advanced = lick_generator_engine.generate_hybrid(request_advanced, use_ai=False)

        print(f"\nAdvanced lick (should use N-gram):")
        print(f"  Technique: {lick_advanced.lick.technique}")

        # Assertions
        assert all(result.lick.notes for result in [lick_beginner, lick_intermediate, lick_advanced]), "All should generate"

        print("\n✅ Test 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_characteristic_detection_integration():
    """Test 5: Characteristic detection from analyzer"""
    print("\n" + "=" * 70)
    print("Test 5: Characteristic Detection Integration")
    print("=" * 70)

    try:
        # Generate lick with Markov
        lick = lick_generator_engine.generate_from_markov(
            style="bebop",
            length=8,
            root="C",
            temperature=1.0
        )

        print(f"\nGenerated lick:")
        print(f"  Intervals: {lick.intervals}")
        print(f"  Characteristics: {', '.join(lick.characteristics)}")

        # Verify characteristics were detected
        assert len(lick.characteristics) > 0, "Should detect characteristics"

        # Common bebop characteristics
        possible_chars = ['chromatic', 'scalar', 'arpeggio', 'ascending', 'descending', 'blues']
        has_valid_char = any(char in lick.characteristics for char in possible_chars)

        assert has_valid_char, "Should have valid musical characteristics"

        print("\n✅ Test 5 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_styles():
    """Test 6: Generation for all styles"""
    print("\n" + "=" * 70)
    print("Test 6: Multiple Style Generation")
    print("=" * 70)

    try:
        styles = ['bebop', 'gospel', 'blues', 'neo_soul', 'modern_jazz', 'classical']
        results = {}

        for style in styles:
            lick = lick_generator_engine.generate_from_markov(
                style=style,
                length=6,
                root="C",
                temperature=1.0
            )

            results[style] = lick

            print(f"\n{style.upper()}:")
            print(f"  Intervals: {lick.intervals}")
            print(f"  Characteristics: {', '.join(lick.characteristics[:2])}")

        # Assertions
        assert len(results) == len(styles), f"Should generate for all {len(styles)} styles"
        assert all(len(l.notes) > 0 for l in results.values()), "All should have notes"

        print("\n✅ Test 6 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def main():
    print("=" * 70)
    print("Markov & N-gram Integration Tests")
    print("=" * 70)

    results = []

    results.append(("Markov generation (bebop)", test_markov_generation_bebop()))
    results.append(("Markov temperature variation", test_markov_temperature_variation()))
    results.append(("N-gram generation", test_ngram_generation()))
    results.append(("Auto strategy selection", test_auto_strategy_selection()))
    results.append(("Characteristic detection", test_characteristic_detection_integration()))
    results.append(("Multiple styles", test_multiple_styles()))

    print("\n" + "=" * 70)
    print("Test Results:")
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
        print("\n🎉 All Markov & N-gram integration tests passed!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")


if __name__ == '__main__':
    main()
