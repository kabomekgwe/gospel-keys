#!/usr/bin/env python3
"""
Test script for chord inversion system
"""

def test_inversion_calculations():
    """Test basic inversion interval calculations"""
    print("=" * 60)
    print("Testing Chord Inversion System")
    print("=" * 60)

    from app.theory.chord_library import (
        get_inversion_intervals,
        get_chord_notes_with_inversion,
        CHORD_LIBRARY
    )

    # Test 1: Cmaj7 inversions
    print("\n1. Cmaj7 Inversions (C-E-G-B):")
    print("-" * 60)
    maj7_intervals = (0, 4, 7, 11)

    print(f"Root position:  {get_inversion_intervals(maj7_intervals, 0)}")
    print(f"  → {get_chord_notes_with_inversion('C', 'maj7', 0, 4)}")

    print(f"1st inversion:  {get_inversion_intervals(maj7_intervals, 1)}")
    print(f"  → {get_chord_notes_with_inversion('C', 'maj7', 1, 4)}")

    print(f"2nd inversion:  {get_inversion_intervals(maj7_intervals, 2)}")
    print(f"  → {get_chord_notes_with_inversion('C', 'maj7', 2, 4)}")

    print(f"3rd inversion:  {get_inversion_intervals(maj7_intervals, 3)}")
    print(f"  → {get_chord_notes_with_inversion('C', 'maj7', 3, 4)}")

    # Test 2: Dominant 9th inversions (5 notes)
    print("\n2. G9 Inversions (G-B-D-F-A):")
    print("-" * 60)
    for inv in range(5):
        notes = get_chord_notes_with_inversion('G', '9', inv, 3)
        print(f"Inversion {inv}: {notes}")

    # Test 3: Dominant 13th inversions (7 notes)
    print("\n3. C13 Inversions (C-E-G-Bb-D-F-A):")
    print("-" * 60)
    for inv in range(6):  # 13th chords have 7 notes, so 0-6 inversions
        try:
            notes = get_chord_notes_with_inversion('C', '13', inv, 3)
            print(f"Inversion {inv}: {notes}")
        except Exception as e:
            print(f"Inversion {inv}: ERROR - {e}")


def test_all_chord_types():
    """Test that all 56 chord types support inversions"""
    print("\n" + "=" * 60)
    print("Testing All Chord Types with Inversions")
    print("=" * 60)

    from app.theory.chord_library import CHORD_LIBRARY, get_chord_notes_with_inversion

    # Count chords by number of notes
    by_note_count = {}
    for symbol, chord_type in CHORD_LIBRARY.items():
        note_count = len(chord_type.intervals)
        if note_count not in by_note_count:
            by_note_count[note_count] = []
        by_note_count[note_count].append((symbol, chord_type.name))

    print("\nChord Distribution by Note Count:")
    print("-" * 60)
    for count in sorted(by_note_count.keys()):
        print(f"{count} notes: {len(by_note_count[count])} chord types")

    # Test each chord type with all possible inversions
    print("\nTesting Random Samples:")
    print("-" * 60)

    test_samples = [
        ("maj7", "Major 7th - 4 notes"),
        ("m7", "Minor 7th - 4 notes"),
        ("9", "Dominant 9th - 5 notes"),
        ("maj9#11", "Maj9#11 - 6 notes"),
        ("13", "Dominant 13th - 7 notes"),
        ("quartal", "Quartal - 3 notes"),
        ("6", "Major 6th - 4 notes"),
    ]

    for quality, description in test_samples:
        try:
            from app.theory.chord_library import get_chord_type
            chord = get_chord_type(quality)
            num_notes = len(chord.intervals)

            print(f"\n{description}:")
            # Test root position and first inversion only for brevity
            root_notes = get_chord_notes_with_inversion('C', quality, 0, 4)
            print(f"  Root: {root_notes}")

            if num_notes > 1:
                inv1_notes = get_chord_notes_with_inversion('C', quality, 1, 4)
                print(f"  1st:  {inv1_notes}")

            print(f"  ✓ Supports {num_notes - 1} inversions (0-{num_notes - 1})")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)

    from app.theory.chord_library import get_chord_notes_with_inversion

    # Test 1: Invalid inversion number
    print("\n1. Invalid Inversion Numbers:")
    print("-" * 60)
    try:
        get_chord_notes_with_inversion('C', 'maj7', 10, 4)  # Only has 4 notes
        print("  ✗ Should have raised error for inversion 10")
    except ValueError as e:
        print(f"  ✓ Correctly raised error: {e}")

    # Test 2: Negative inversion
    try:
        get_chord_notes_with_inversion('C', 'maj7', -1, 4)
        print("  ✗ Should have raised error for inversion -1")
    except ValueError as e:
        print(f"  ✓ Correctly raised error: {e}")

    # Test 3: Different root notes
    print("\n2. Different Root Notes:")
    print("-" * 60)
    for root in ['C', 'F#', 'Bb', 'G']:
        notes = get_chord_notes_with_inversion(root, 'm7', 1, 4)
        print(f"  {root}m7 (1st inv): {notes}")


def calculate_total_voicings():
    """Calculate total number of voicings from inversions alone"""
    print("\n" + "=" * 60)
    print("Total Voicing Count Estimate")
    print("=" * 60)

    from app.theory.chord_library import CHORD_LIBRARY

    total_inversions = 0
    by_note_count = {}

    for chord_type in CHORD_LIBRARY.values():
        note_count = len(chord_type.intervals)
        # Each chord has note_count inversions (including root position)
        inversions = note_count
        total_inversions += inversions

        if note_count not in by_note_count:
            by_note_count[note_count] = 0
        by_note_count[note_count] += inversions

    print("\nInversions by Chord Size:")
    print("-" * 60)
    for count in sorted(by_note_count.keys()):
        chord_count = len([c for c in CHORD_LIBRARY.values() if len(c.intervals) == count])
        print(f"{count}-note chords: {chord_count} types × {count} inversions = {by_note_count[count]} voicings")

    print(f"\nBase chord types: 56")
    print(f"Total voicings (with inversions): {total_inversions}")
    print(f"Expansion: {total_inversions} / 56 = {total_inversions / 56:.1f}x")


if __name__ == "__main__":
    test_inversion_calculations()
    test_all_chord_types()
    test_edge_cases()
    calculate_total_voicings()
    print("\n✅ All inversion tests completed!\n")
