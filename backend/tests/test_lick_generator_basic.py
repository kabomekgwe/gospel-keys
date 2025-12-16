"""Basic tests for Phase 7: Advanced Lick Generation Engine

Tests the core lick_generator_engine.py module functionality:
- Pattern-based generation with variation types
- Motif variation engine
- Context-aware generation
- Hybrid orchestration
"""

import asyncio
from app.pipeline.lick_generator_engine import (
    lick_generator_engine,
    LickGenerationRequest,
    GenerationStrategy,
    VariationType
)


def test_pattern_generation_standard():
    """Test 1: Pattern-based generation with standard variation"""
    print("=" * 70)
    print("Test 1: Pattern-based generation (Bebop 3-to-b9)")
    print("=" * 70)

    try:
        lick = lick_generator_engine.generate_from_pattern(
            pattern_name="bebop_3_to_b9",
            root="C",
            style="bebop",
            variation=VariationType.STANDARD
        )

        print(f"\nGenerated lick:")
        print(f"  Notes: {' - '.join(lick.notes)}")
        print(f"  MIDI: {lick.midi_notes}")
        print(f"  Intervals: {lick.intervals}")
        print(f"  Rhythm: {lick.rhythm}")
        print(f"  Duration: {lick.duration_beats} beats")
        print(f"  Style: {lick.style}")
        print(f"  Characteristics: {', '.join(lick.characteristics)}")

        # Assertions
        assert len(lick.notes) > 0, "Should have notes"
        assert len(lick.midi_notes) == len(lick.notes), "MIDI count should match notes"
        assert len(lick.intervals) == len(lick.notes), "Intervals count should match notes"
        assert lick.style == "bebop", "Style should be bebop"
        assert lick.duration_beats > 0, "Duration should be positive"

        print("\n✅ Test 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pattern_generation_inversion():
    """Test 2: Pattern-based generation with inversion"""
    print("\n" + "=" * 70)
    print("Test 2: Pattern variation (Inversion)")
    print("=" * 70)

    try:
        # Generate standard version
        standard = lick_generator_engine.generate_from_pattern(
            pattern_name="bebop_3_to_b9",
            root="C",
            style="bebop",
            variation=VariationType.STANDARD
        )

        # Generate inverted version
        inverted = lick_generator_engine.generate_from_pattern(
            pattern_name="bebop_3_to_b9",
            root="C",
            style="bebop",
            variation=VariationType.INVERSION
        )

        print(f"\nStandard lick intervals: {standard.intervals}")
        print(f"Inverted lick intervals: {inverted.intervals}")

        # Assertions
        assert standard.intervals != inverted.intervals, "Inverted should differ from standard"
        assert len(standard.notes) == len(inverted.notes), "Should have same length"

        print("\n✅ Test 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pattern_generation_retrograde():
    """Test 3: Pattern-based generation with retrograde"""
    print("\n" + "=" * 70)
    print("Test 3: Pattern variation (Retrograde)")
    print("=" * 70)

    try:
        # Generate standard version
        standard = lick_generator_engine.generate_from_pattern(
            pattern_name="blues_minor_pentatonic",
            root="A",
            style="blues",
            variation=VariationType.STANDARD
        )

        # Generate retrograde version
        retrograde = lick_generator_engine.generate_from_pattern(
            pattern_name="blues_minor_pentatonic",
            root="A",
            style="blues",
            variation=VariationType.RETROGRADE
        )

        print(f"\nStandard lick notes: {' - '.join(standard.notes)}")
        print(f"Retrograde lick notes: {' - '.join(retrograde.notes)}")

        # Assertions
        assert standard.notes != retrograde.notes, "Retrograde should differ from standard"
        assert len(standard.notes) == len(retrograde.notes), "Should have same length"
        # Retrograde should be reversed
        assert retrograde.notes == list(reversed(standard.notes)), "Should be reversed"

        print("\n✅ Test 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_motif_variation():
    """Test 4: Motif variation engine"""
    print("\n" + "=" * 70)
    print("Test 4: Motif variation")
    print("=" * 70)

    try:
        # Create source lick first
        source_lick = lick_generator_engine.generate_from_pattern(
            pattern_name="bebop_3_to_b9",
            root="C",
            style="bebop",
            variation=VariationType.STANDARD
        )

        print(f"\nSource lick: {' - '.join(source_lick.notes)}")

        # Generate variations
        variations = []
        for var_type in [VariationType.INVERSION, VariationType.RETROGRADE, VariationType.AUGMENTATION]:
            variation = lick_generator_engine.generate_motif_variation(
                source_lick=source_lick,
                variation_type=var_type,
                preserve=None
            )
            variations.append(variation)

        print(f"\nGenerated {len(variations)} variations:")

        for i, lick in enumerate(variations, 1):
            print(f"\nVariation {i}:")
            print(f"  Notes: {' - '.join(lick.notes)}")
            print(f"  Rhythm: {lick.rhythm}")
            print(f"  Technique: {lick.technique}")

        # Assertions
        assert len(variations) == 3, "Should generate 3 variations"
        assert all(len(v.notes) > 0 for v in variations), "All variations should have notes"

        print("\n✅ Test 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_aware_generation():
    """Test 5: Context-aware generation"""
    print("\n" + "=" * 70)
    print("Test 5: Context-aware generation")
    print("=" * 70)

    try:
        # Generate for ii-V-I progression
        lick = lick_generator_engine.generate_context_aware(
            chord_progression=["Dm7", "G7", "Cmaj7"],
            phrase_position="middle",
            previous_licks=[],
            style="jazz",
            difficulty="intermediate"
        )

        print(f"\nGenerated lick for ii-V-I progression:")
        print(f"  Notes: {' - '.join(lick.notes)}")
        print(f"  Harmonic function: {lick.harmonic_function}")
        print(f"  Characteristics: {', '.join(lick.characteristics)}")

        # Assertions
        assert len(lick.notes) > 0, "Should have notes"

        print("\n✅ Test 5 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hybrid_orchestration_local():
    """Test 6: Hybrid orchestration (local route - complexity ≤ 7)"""
    print("\n" + "=" * 70)
    print("Test 6: Hybrid orchestration (Local generation)")
    print("=" * 70)

    try:
        request = LickGenerationRequest(
            style="bebop",
            key="C",
            context_chords=["Dm7", "G7", "Cmaj7"],
            difficulty="intermediate",
            generation_strategy=GenerationStrategy.AUTO,
            use_ai_enhancement=False
        )

        result = lick_generator_engine.generate_hybrid(request, use_ai=False)

        print(f"\nGeneration result:")
        print(f"  Source: {result.source}")
        print(f"  Complexity: {result.complexity}")
        print(f"  Confidence: {result.confidence}")
        print(f"\nLick details:")
        print(f"  Notes: {' - '.join(result.lick.notes)}")
        print(f"  Duration: {result.lick.duration_beats} beats")

        # Assertions
        assert result.source in ["local_rules", "hybrid"], "Should use local or hybrid"
        assert 1 <= result.complexity <= 10, "Complexity should be 1-10"
        assert result.confidence > 0, "Should have confidence score"
        assert len(result.lick.notes) > 0, "Should generate lick"

        print(f"\n  Note: Complexity {result.complexity} determined as {result.source}")

        print("\n✅ Test 6 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_transposition():
    """Test 7: Transposition to different keys"""
    print("\n" + "=" * 70)
    print("Test 7: Transposition")
    print("=" * 70)

    try:
        # Generate in C
        lick_c = lick_generator_engine.generate_from_pattern(
            pattern_name="bebop_3_to_b9",
            root="C",
            style="bebop",
            variation=VariationType.STANDARD
        )

        # Generate in F# (6 semitones up)
        lick_f_sharp = lick_generator_engine.generate_from_pattern(
            pattern_name="bebop_3_to_b9",
            root="F#",
            style="bebop",
            variation=VariationType.STANDARD
        )

        print(f"\nLick in C: {' - '.join(lick_c.notes)}")
        print(f"  MIDI: {lick_c.midi_notes}")
        print(f"\nLick in F#: {' - '.join(lick_f_sharp.notes)}")
        print(f"  MIDI: {lick_f_sharp.midi_notes}")

        # Check transposition
        if len(lick_c.midi_notes) == len(lick_f_sharp.midi_notes):
            transposition = lick_f_sharp.midi_notes[0] - lick_c.midi_notes[0]
            print(f"\nTransposition: {transposition} semitones")

            # Verify all notes transposed by same amount
            all_correct = all(
                lick_f_sharp.midi_notes[i] - lick_c.midi_notes[i] == transposition
                for i in range(len(lick_c.midi_notes))
            )

            assert all_correct, "All notes should be transposed by same amount"

        # Assertions
        assert len(lick_c.notes) == len(lick_f_sharp.notes), "Should have same length"
        assert lick_c.notes != lick_f_sharp.notes, "Notes should differ"

        print("\n✅ Test 7 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 7 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# RUN ALL TESTS
# ============================================================================

async def main():
    print("=" * 70)
    print("Phase 7: Advanced Lick Generation - Basic Tests")
    print("=" * 70)

    results = []

    # Sync tests
    results.append(("Pattern generation (standard)", test_pattern_generation_standard()))
    results.append(("Pattern variation (inversion)", test_pattern_generation_inversion()))
    results.append(("Pattern variation (retrograde)", test_pattern_generation_retrograde()))
    results.append(("Motif variation", test_motif_variation()))
    results.append(("Context-aware generation", test_context_aware_generation()))
    results.append(("Transposition", test_transposition()))

    # Async tests
    results.append(("Hybrid orchestration (local)", await test_hybrid_orchestration_local()))

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
        print("\n🎉 All basic lick generator tests passed!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")


if __name__ == '__main__':
    asyncio.run(main())
