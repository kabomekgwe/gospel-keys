"""Test hybrid local+AI reharmonization API endpoint"""

import asyncio
from app.schemas.ai import ReharmonizationRequest, ProgressionStyle
from app.services.ai_generator import ai_generator_service


async def test_simple_reharmonization():
    """Test simple reharmonization (should use local rules)"""
    print("=" * 70)
    print("Test 1: Simple Reharmonization (Jazz ii-V-I)")
    print("=" * 70)

    request = ReharmonizationRequest(
        original_progression=["Dm7", "G7", "Cmaj7"],
        key="C",
        style=ProgressionStyle.JAZZ
    )

    try:
        response = await ai_generator_service.generate_reharmonization(request)

        print(f"\nOriginal: {' - '.join(response.original)}")
        print(f"Reharmonized: {' - '.join([c.symbol for c in response.reharmonized])}")
        print(f"\nExplanation: {response.explanation}")
        print(f"\nTechniques used: {', '.join(response.techniques_used)}")
        print(f"Source: {response.source}")
        print(f"Complexity: {response.complexity}")

        # Assertions
        assert len(response.reharmonized) == 3, "Should have 3 reharmonized chords"
        assert response.source == "local_rules", "Simple progression should use local rules"
        assert response.complexity <= 7, "Should be simple complexity"
        assert len(response.techniques_used) > 0, "Should use at least one technique"

        print("\n✅ Test 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_complex_reharmonization():
    """Test complex reharmonization (should use hybrid approach)"""
    print("\n" + "=" * 70)
    print("Test 2: Complex Reharmonization (Long Neo-Soul Progression)")
    print("=" * 70)

    request = ReharmonizationRequest(
        original_progression=[
            "Cmaj7", "Am9", "Dm7", "G7",
            "Cmaj7", "A7", "Dm7", "Db7", "Cmaj9"
        ],
        key="C",
        style=ProgressionStyle.NEO_SOUL
    )

    try:
        response = await ai_generator_service.generate_reharmonization(request)

        print(f"\nOriginal ({len(response.original)} chords): {' - '.join(response.original)}")
        print(f"Reharmonized: {' - '.join([c.symbol for c in response.reharmonized])}")
        print(f"\nExplanation: {response.explanation}")
        print(f"\nTechniques used: {', '.join(response.techniques_used)}")
        print(f"Source: {response.source}")
        print(f"Complexity: {response.complexity}")

        # Assertions
        assert len(response.reharmonized) == len(response.original), "Should maintain progression length"
        # Complex neo-soul progression might trigger hybrid
        print(f"  Note: Complexity {response.complexity}, Source: {response.source}")
        assert response.complexity >= 7, "Should be higher complexity"

        print("\n✅ Test 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_gospel_reharmonization():
    """Test Gospel reharmonization"""
    print("\n" + "=" * 70)
    print("Test 3: Gospel Reharmonization")
    print("=" * 70)

    request = ReharmonizationRequest(
        original_progression=["C", "F", "G", "C"],
        key="C",
        style=ProgressionStyle.GOSPEL
    )

    try:
        response = await ai_generator_service.generate_reharmonization(request)

        print(f"\nOriginal: {' - '.join(response.original)}")
        print(f"Reharmonized: {' - '.join([c.symbol for c in response.reharmonized])}")
        print(f"\nExplanation: {response.explanation}")
        print(f"\nTechniques used: {', '.join(response.techniques_used)}")
        print(f"Source: {response.source}")
        print(f"Complexity: {response.complexity}")

        # Assertions
        assert len(response.reharmonized) == 4, "Should have 4 chords"
        assert len(response.techniques_used) > 0, "Should use gospel techniques"

        print("\n✅ Test 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_single_chord():
    """Test single chord reharmonization"""
    print("\n" + "=" * 70)
    print("Test 4: Single Chord Reharmonization")
    print("=" * 70)

    request = ReharmonizationRequest(
        original_progression=["C"],
        key="C",
        style=ProgressionStyle.JAZZ
    )

    try:
        response = await ai_generator_service.generate_reharmonization(request)

        print(f"\nOriginal: {' - '.join(response.original)}")
        print(f"Reharmonized: {' - '.join([c.symbol for c in response.reharmonized])}")
        print(f"\nExplanation: {response.explanation}")
        print(f"\nTechniques used: {', '.join(response.techniques_used)}")
        print(f"Source: {response.source}")
        print(f"Complexity: {response.complexity}")

        # Assertions
        assert len(response.reharmonized) >= 1, "Should have at least 1 chord"
        assert response.source == "local_rules", "Single chord should use local rules"

        print("\n✅ Test 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# RUN ALL TESTS
# ============================================================================

async def main():
    print("=" * 70)
    print("Hybrid Local+AI Reharmonization API Tests")
    print("=" * 70)

    results = []

    results.append(("Simple Jazz ii-V-I", await test_simple_reharmonization()))
    results.append(("Complex Neo-Soul", await test_complex_reharmonization()))
    results.append(("Gospel Progression", await test_gospel_reharmonization()))
    results.append(("Single Chord", await test_single_chord()))

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
        print("\n🎉 All hybrid API tests passed!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")


if __name__ == '__main__':
    asyncio.run(main())
