#!/usr/bin/env python3
"""
Test script for Phase 3 advanced voicings
"""

def test_category_1_quartal_quintal():
    """Test quartal/quintal harmony functions"""
    print("=" * 60)
    print("CATEGORY 1: Quartal/Quintal Harmony")
    print("=" * 60)

    from app.theory.chord_library import (
        get_quartal_voicing,
        get_quintal_voicing,
        get_kenny_barron_voicing,
        get_quartal_tertian_hybrid
    )

    # Test quartal voicing
    print("\n1. Quartal Voicings (stacked 4ths):")
    print("-" * 60)
    for num_notes in [3, 4, 5]:
        notes = get_quartal_voicing('D', num_notes, 3)
        print(f"  D quartal ({num_notes} notes): {notes}")

    # Test quintal voicing
    print("\n2. Quintal Voicings (stacked 5ths):")
    print("-" * 60)
    for num_notes in [3, 4, 5]:
        notes = get_quintal_voicing('C', num_notes, 3)
        print(f"  C quintal ({num_notes} notes): {notes}")

    # Test Kenny Barron voicing
    print("\n3. Kenny Barron Voicing (minor 11th):")
    print("-" * 60)
    for root in ['D', 'A', 'E']:
        notes = get_kenny_barron_voicing(root, 3)
        print(f"  {root} Kenny Barron: {notes}")

    # Test quartal-tertian hybrid
    print("\n4. Quartal-Tertian Hybrid:")
    print("-" * 60)
    for root in ['C', 'F', 'G']:
        notes = get_quartal_tertian_hybrid(root, 3)
        print(f"  {root} hybrid: {notes}")


def test_category_2_cluster():
    """Test cluster voicings"""
    print("\n" + "=" * 60)
    print("CATEGORY 2: Cluster Voicings")
    print("=" * 60)

    from app.theory.chord_library import (
        get_close_cluster,
        get_open_cluster,
        get_tone_cluster_chord
    )

    # Test close cluster
    print("\n1. Close Cluster (adjacent semitones):")
    print("-" * 60)
    for num_notes in [3, 4, 5]:
        notes = get_close_cluster('C', num_notes, 4)
        print(f"  C close cluster ({num_notes} notes): {notes}")

    # Test open cluster
    print("\n2. Open Cluster (mixed m2 and M2):")
    print("-" * 60)
    for num_notes in [3, 4, 5]:
        notes = get_open_cluster('C', num_notes, 4)
        print(f"  C open cluster ({num_notes} notes): {notes}")

    # Test tone cluster chord
    print("\n3. Tone Cluster Chord (chromatic fill):")
    print("-" * 60)
    for quality, display in [('', 'C'), ('maj7', 'Cmaj7'), ('9', 'C9')]:
        notes = get_tone_cluster_chord('C', quality, 4)
        print(f"  {display} tone cluster: {notes}")


def test_category_3_spread():
    """Test spread and orchestral voicings"""
    print("\n" + "=" * 60)
    print("CATEGORY 3: Spread & Orchestral Voicings")
    print("=" * 60)

    from app.theory.chord_library import (
        apply_spread_voicing,
        get_split_bass_voicing,
        get_wide_spread_voicing
    )

    # Test spread voicing transformation
    print("\n1. Spread Voicing Transformation:")
    print("-" * 60)
    close_voicing = [60, 64, 67, 71]  # Cmaj7 in MIDI
    spread_2x = apply_spread_voicing(close_voicing, 2.0)
    spread_3x = apply_spread_voicing(close_voicing, 3.0)
    print(f"  Original:  {close_voicing}")
    print(f"  2x spread: {spread_2x}")
    print(f"  3x spread: {spread_3x}")

    # Test split bass voicing
    print("\n2. Split Bass Voicing (2+ octave gap):")
    print("-" * 60)
    for quality in ['maj7', 'm7', '7']:
        notes = get_split_bass_voicing('C', quality, bass_octave=2, upper_octave=5)
        print(f"  C{quality} split bass: {notes}")

    # Test wide spread voicing
    print("\n3. Wide Spread Voicing (orchestral):")
    print("-" * 60)
    for quality in ['maj7', 'm7', '9']:
        notes = get_wide_spread_voicing('C', quality, 3)
        print(f"  C{quality} wide spread: {notes}")


def test_summary():
    """Print summary of Phase 3 progress"""
    print("\n" + "=" * 60)
    print("PHASE 3 PROGRESS SUMMARY")
    print("=" * 60)

    print("\n✅ Category 1: Quartal/Quintal Harmony (4 functions)")
    print("  • get_quartal_voicing()")
    print("  • get_quintal_voicing()")
    print("  • get_kenny_barron_voicing()")
    print("  • get_quartal_tertian_hybrid()")

    print("\n✅ Category 2: Cluster Voicings (3 functions)")
    print("  • get_close_cluster()")
    print("  • get_open_cluster()")
    print("  • get_tone_cluster_chord()")

    print("\n✅ Category 3: Spread & Orchestral (3 functions)")
    print("  • apply_spread_voicing()")
    print("  • get_split_bass_voicing()")
    print("  • get_wide_spread_voicing()")

    print("\n📊 Phase 3 Functions Added So Far: 10/30+")
    print("📊 Estimated New Voicings: ~550 (of ~5,000 target)")

    print("\n🚧 Categories Remaining:")
    print("  • Category 4: Parallel & Chromatic Motion")
    print("  • Category 5: Tritone Substitution")
    print("  • Category 6: Upper Extension Stacks")
    print("  • Category 7: Slash Chords & Polychords")
    print("  • Category 8: Block Chords & Locked Hands")
    print("  • Category 9: Hybrid & Contemporary")
    print("  • Category 10: Voice Leading Optimizations")


if __name__ == "__main__":
    test_category_1_quartal_quintal()
    test_category_2_cluster()
    test_category_3_spread()
    test_summary()
    print("\n✅ Phase 3 (partial) tests completed!\n")
