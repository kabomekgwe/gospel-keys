"""
Basic Phase 6 Integration Test

Quick smoke test to verify:
- All modules import successfully
- Critical missing function exists
- Basic orchestration works
"""

def test_imports():
    """Test that all Phase 6 modules import successfully"""
    print("Testing imports...")

    try:
        from app.pipeline.reharmonization_orchestrator import get_all_reharmonizations_for_chord
        print("✓ reharmonization_orchestrator imports")
    except ImportError as e:
        print(f"✗ reharmonization_orchestrator import failed: {e}")
        return False

    try:
        from app.pipeline.reharmonization_quality_metrics import calculate_voice_leading_score
        print("✓ reharmonization_quality_metrics imports")
    except ImportError as e:
        print(f"✗ reharmonization_quality_metrics import failed: {e}")
        return False

    try:
        from app.pipeline.reharmonization_strategies import reharmonize_ii_V_I_jazz
        print("✓ reharmonization_strategies imports")
    except ImportError as e:
        print(f"✗ reharmonization_strategies import failed: {e}")
        return False

    try:
        from app.pipeline.reharmonization_engine import get_all_reharmonizations_for_chord as engine_func
        print("✓ reharmonization_engine imports (with missing function)")
    except ImportError as e:
        print(f"✗ reharmonization_engine import failed: {e}")
        return False

    return True


def test_missing_function_exists():
    """Test that the critical missing function now exists"""
    print("\nTesting critical missing function...")

    try:
        from app.pipeline.reharmonization_engine import get_all_reharmonizations_for_chord

        # Verify function exists and is callable
        assert callable(get_all_reharmonizations_for_chord), "Function is not callable"
        print("✓ get_all_reharmonizations_for_chord exists and is callable")
        return True

    except (ImportError, AssertionError) as e:
        print(f"✗ Missing function test failed: {e}")
        return False


def test_basic_orchestration():
    """Test basic orchestration functionality"""
    print("\nTesting basic orchestration...")

    try:
        from app.pipeline.reharmonization_orchestrator import get_all_reharmonizations_for_chord

        # Test with simple C major chord
        chord_dict = {'root': 'C', 'quality': ''}
        options = get_all_reharmonizations_for_chord(
            chord_dict=chord_dict,
            key='C',
            genre='jazz',
            max_options=5
        )

        assert isinstance(options, list), "Should return a list"
        print(f"✓ Orchestration works: Got {len(options)} options for C major")

        # Check structure of first option if available
        if options:
            first = options[0]
            assert 'new_root' in first, "Option missing 'new_root'"
            assert 'new_quality' in first, "Option missing 'new_quality'"
            assert 'technique' in first, "Option missing 'technique'"
            assert 'score' in first, "Option missing 'score'"
            print(f"✓ First option structure valid: {first['technique']} (score: {first['score']:.2f})")

        return True

    except Exception as e:
        print(f"✗ Basic orchestration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_jazz_strategy():
    """Test jazz ii-V-I strategy"""
    print("\nTesting jazz strategies...")

    try:
        from app.pipeline.reharmonization_strategies import reharmonize_ii_V_I_jazz

        # Test standard ii-V-I in C
        progression = reharmonize_ii_V_I_jazz('C', variation='standard')

        assert len(progression) == 3, f"Should have 3 chords, got {len(progression)}"
        assert progression[0] == ('D', 'm7'), "ii chord should be Dm7"
        assert progression[1] == ('G', '7'), "V chord should be G7"
        assert progression[2] == ('C', 'maj7'), "I chord should be Cmaj7"

        print(f"✓ Jazz ii-V-I standard: {progression}")

        # Test tritone substitution variant
        tritone_prog = reharmonize_ii_V_I_jazz('C', variation='tritone_sub')
        assert len(tritone_prog) == 3, "Tritone sub should have 3 chords"
        assert tritone_prog[1][0] in ['Db', 'C#'], f"Should have tritone sub, got {tritone_prog[1]}"

        print(f"✓ Jazz ii-V-I tritone sub: {tritone_prog}")

        return True

    except Exception as e:
        print(f"✗ Jazz strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_metrics():
    """Test quality metrics module"""
    print("\nTesting quality metrics...")

    try:
        from app.pipeline.reharmonization_quality_metrics import (
            calculate_genre_appropriateness_score,
            calculate_complexity_score,
            GENRE_WEIGHTS
        )

        # Test genre score
        genre_result = calculate_genre_appropriateness_score('tritone_substitution', 'jazz')
        assert 'score' in genre_result, "Genre score missing 'score'"
        assert 0.0 <= genre_result['score'] <= 1.0, "Score out of range"
        print(f"✓ Genre score (tritone/jazz): {genre_result['score']:.2f}")

        # Test complexity score
        complexity_result = calculate_complexity_score('diatonic_substitution')
        assert 'score' in complexity_result, "Complexity score missing 'score'"
        print(f"✓ Complexity score (diatonic): {complexity_result['score']:.2f}")

        # Test genre weights exist
        assert 'jazz' in GENRE_WEIGHTS, "Jazz weights missing"
        assert 'gospel' in GENRE_WEIGHTS, "Gospel weights missing"
        print(f"✓ Genre weights defined for {len(GENRE_WEIGHTS)} genres")

        return True

    except Exception as e:
        print(f"✗ Quality metrics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Phase 6 Basic Integration Tests")
    print("=" * 70)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Missing Function", test_missing_function_exists()))
    results.append(("Basic Orchestration", test_basic_orchestration()))
    results.append(("Jazz Strategy", test_jazz_strategy()))
    results.append(("Quality Metrics", test_quality_metrics()))

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
        print("\n🎉 All Phase 6 basic tests passed!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
