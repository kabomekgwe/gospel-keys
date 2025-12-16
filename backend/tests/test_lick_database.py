"""Test expanded lick database access and integration

Tests:
- Database statistics (125+ patterns)
- Pattern lookup by style, difficulty, harmonic context
- Search functionality
- Integration with lick generator engine
"""

from app.pipeline.lick_database_expanded import lick_database
from app.pipeline.lick_generator_engine import lick_generator_engine, VariationType


def test_database_stats():
    """Test 1: Database statistics"""
    print("=" * 70)
    print("Test 1: Database Statistics")
    print("=" * 70)

    try:
        stats = lick_database.get_stats()

        print(f"\nTotal patterns: {stats['total_patterns']}")
        print(f"  Bebop: {stats['bebop']}")
        print(f"  Gospel: {stats['gospel']}")
        print(f"  Blues: {stats['blues']}")
        print(f"  Neo-Soul: {stats['neo_soul']}")
        print(f"  Modern Jazz: {stats['modern_jazz']}")
        print(f"  Classical: {stats['classical']}")

        # Assertions
        assert stats['total_patterns'] == 125, f"Should have 125 patterns, got {stats['total_patterns']}"
        assert stats['bebop'] == 35, "Should have 35 bebop patterns"
        assert stats['gospel'] == 25, "Should have 25 gospel patterns"
        assert stats['blues'] == 20, "Should have 20 blues patterns"
        assert stats['neo_soul'] == 20, "Should have 20 neo-soul patterns"
        assert stats['modern_jazz'] == 15, "Should have 15 modern jazz patterns"
        assert stats['classical'] == 10, "Should have 10 classical patterns"

        print("\n✅ Test 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lookup_by_style():
    """Test 2: Lookup patterns by style"""
    print("\n" + "=" * 70)
    print("Test 2: Lookup by Style")
    print("=" * 70)

    try:
        bebop_patterns = lick_database.get_by_style("bebop")
        gospel_patterns = lick_database.get_by_style("gospel")

        print(f"\nBebop patterns: {len(bebop_patterns)}")
        print(f"  Example: {bebop_patterns[0].name}")
        print(f"  Source: {bebop_patterns[0].source}")

        print(f"\nGospel patterns: {len(gospel_patterns)}")
        print(f"  Example: {gospel_patterns[0].name}")
        print(f"  Source: {gospel_patterns[0].source}")

        # Assertions
        assert len(bebop_patterns) == 35, "Should have 35 bebop patterns"
        assert len(gospel_patterns) == 25, "Should have 25 gospel patterns"

        print("\n✅ Test 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lookup_by_difficulty():
    """Test 3: Lookup patterns by difficulty"""
    print("\n" + "=" * 70)
    print("Test 3: Lookup by Difficulty")
    print("=" * 70)

    try:
        beginner = lick_database.get_by_difficulty("beginner")
        intermediate = lick_database.get_by_difficulty("intermediate")
        advanced = lick_database.get_by_difficulty("advanced")

        print(f"\nBeginner patterns: {len(beginner)}")
        print(f"Intermediate patterns: {len(intermediate)}")
        print(f"Advanced patterns: {len(advanced)}")

        # Assertions
        total = len(beginner) + len(intermediate) + len(advanced)
        assert total == 125, f"Total should be 125, got {total}"
        assert len(beginner) > 0, "Should have beginner patterns"
        assert len(intermediate) > 0, "Should have intermediate patterns"
        assert len(advanced) > 0, "Should have advanced patterns"

        print("\n✅ Test 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lookup_by_harmonic_context():
    """Test 4: Lookup patterns by harmonic context"""
    print("\n" + "=" * 70)
    print("Test 4: Lookup by Harmonic Context")
    print("=" * 70)

    try:
        dom7_patterns = lick_database.get_by_harmonic_context("dom7")
        maj7_patterns = lick_database.get_by_harmonic_context("maj7")

        print(f"\nDominant 7th patterns: {len(dom7_patterns)}")
        print(f"  Examples:")
        for p in dom7_patterns[:3]:
            print(f"    - {p.name} ({p.style})")

        print(f"\nMajor 7th patterns: {len(maj7_patterns)}")
        print(f"  Examples:")
        for p in maj7_patterns[:3]:
            print(f"    - {p.name} ({p.style})")

        # Assertions
        assert len(dom7_patterns) > 0, "Should have dominant 7th patterns"
        assert len(maj7_patterns) > 0, "Should have major 7th patterns"

        print("\n✅ Test 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_multiple_criteria():
    """Test 5: Search with multiple criteria"""
    print("\n" + "=" * 70)
    print("Test 5: Search with Multiple Criteria")
    print("=" * 70)

    try:
        # Search for intermediate gospel patterns with chromatic characteristics
        results = lick_database.search(
            style="gospel",
            difficulty="intermediate",
            characteristics=["chromatic"]
        )

        print(f"\nIntermediate gospel chromatic patterns: {len(results)}")
        for p in results[:5]:
            print(f"  - {p.name}: {p.characteristics[:3]}")

        # Assertions
        assert all(p.style == "gospel" for p in results), "All should be gospel"
        assert all(p.difficulty == "intermediate" for p in results), "All should be intermediate"
        assert all("chromatic" in p.characteristics for p in results), "All should be chromatic"

        print("\n✅ Test 5 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_generator():
    """Test 6: Integration with lick generator engine"""
    print("\n" + "=" * 70)
    print("Test 6: Integration with Generator Engine")
    print("=" * 70)

    try:
        # Generate lick using a new pattern from expanded database
        lick = lick_generator_engine.generate_from_pattern(
            pattern_name="bebop_chromatic_walk_up",  # New pattern
            root="C",
            style="bebop",
            variation=VariationType.STANDARD
        )

        print(f"\nGenerated lick from new database:")
        print(f"  Pattern: bebop_chromatic_walk_up")
        print(f"  Notes: {' - '.join(lick.notes)}")
        print(f"  Characteristics: {', '.join(lick.characteristics)}")

        # Assertions
        assert len(lick.notes) > 0, "Should generate notes"
        assert "chromatic" in lick.characteristics, "Should be chromatic"

        print("\n✅ Test 6 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gospel_patterns():
    """Test 7: Gospel-specific patterns"""
    print("\n" + "=" * 70)
    print("Test 7: Gospel-Specific Patterns")
    print("=" * 70)

    try:
        # Test gospel slip note pattern
        lick = lick_generator_engine.generate_from_pattern(
            pattern_name="gospel_slip_note_classic",
            root="C",
            style="gospel",
            variation=VariationType.STANDARD
        )

        print(f"\nGenerated gospel slip note:")
        print(f"  Notes: {' - '.join(lick.notes)}")
        print(f"  Characteristics: {', '.join(lick.characteristics)}")

        # Assertions
        assert "slip_note" in lick.characteristics, "Should have slip_note characteristic"
        assert lick.style == "gospel", "Should be gospel style"

        print("\n✅ Test 7 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 7 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_neosoul_patterns():
    """Test 8: Neo-soul patterns"""
    print("\n" + "=" * 70)
    print("Test 8: Neo-Soul Patterns")
    print("=" * 70)

    try:
        # Test neo-soul 9th voicing
        lick = lick_generator_engine.generate_from_pattern(
            pattern_name="neosoul_9th_voicing",
            root="D",
            style="neo_soul",
            variation=VariationType.STANDARD
        )

        print(f"\nGenerated neo-soul 9th voicing:")
        print(f"  Notes: {' - '.join(lick.notes)}")
        print(f"  Characteristics: {', '.join(lick.characteristics)}")

        # Assertions
        assert "9th" in lick.characteristics, "Should emphasize 9th"
        assert lick.style == "neo_soul", "Should be neo-soul style"

        print("\n✅ Test 8 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 8 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def main():
    print("=" * 70)
    print("Expanded Lick Database Tests")
    print("=" * 70)

    results = []

    results.append(("Database statistics", test_database_stats()))
    results.append(("Lookup by style", test_lookup_by_style()))
    results.append(("Lookup by difficulty", test_lookup_by_difficulty()))
    results.append(("Lookup by harmonic context", test_lookup_by_harmonic_context()))
    results.append(("Search multiple criteria", test_search_multiple_criteria()))
    results.append(("Integration with generator", test_integration_with_generator()))
    results.append(("Gospel patterns", test_gospel_patterns()))
    results.append(("Neo-soul patterns", test_neosoul_patterns()))

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
        print("\n🎉 All database tests passed!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")


if __name__ == '__main__':
    main()
