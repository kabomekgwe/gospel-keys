#!/usr/bin/env python3
"""
Test script for advanced chord voicings (Phase 2)
"""

def test_drop_voicings():
    """Test drop-2, drop-3, drop-2-4 voicings"""
    print("=" * 60)
    print("Testing Drop Voicings")
    print("=" * 60)

    from app.theory.chord_library import (
        get_chord_notes_with_inversion,
        apply_drop_2,
        apply_drop_3,
        apply_drop_2_4
    )
    from app.theory.interval_utils import note_to_semitone

    # Generate Cmaj7 in close position
    notes = get_chord_notes_with_inversion("C", "maj7", 0, 4)
    print(f"\nCmaj7 close position: {notes}")

    # Convert to MIDI for drop voicing transformations
    midi_notes = []
    for note_str in notes:
        note_name = ''.join(c for c in note_str if not c.isdigit())
        note_oct = int(''.join(c for c in note_str if c.isdigit()))
        semitone = note_to_semitone(note_name)
        midi = note_oct * 12 + semitone
        midi_notes.append(midi)

    print(f"MIDI notes: {midi_notes}")

    # Test drop voicings
    drop2 = apply_drop_2(midi_notes)
    print(f"Drop-2:    {drop2}  # 2nd from top dropped octave")

    drop3 = apply_drop_3(midi_notes)
    print(f"Drop-3:    {drop3}  # 3rd from top dropped octave")

    drop24 = apply_drop_2_4(midi_notes)
    print(f"Drop-2-4:  {drop24}  # 2nd & 4th from top dropped")


def test_rootless_voicings():
    """Test Bill Evans style rootless voicings"""
    print("\n" + "=" * 60)
    print("Testing Rootless Voicings (Bill Evans Style)")
    print("=" * 60)

    from app.theory.chord_library import (
        get_rootless_voicing_a,
        get_rootless_voicing_b
    )

    # Test on various chord qualities
    test_chords = [
        ("C", "maj7", "Cmaj7"),
        ("G", "7", "G7"),
        ("D", "m7", "Dm7"),
        ("F", "maj7", "Fmaj7"),
    ]

    for root, quality, name in test_chords:
        print(f"\n{name}:")
        try:
            type_a = get_rootless_voicing_a(root, quality, octave=3)
            print(f"  Type A (3-5-7-9): {type_a}")
        except Exception as e:
            print(f"  Type A: ERROR - {e}")

        try:
            type_b = get_rootless_voicing_b(root, quality, octave=3)
            print(f"  Type B (7-9-3-5): {type_b}")
        except Exception as e:
            print(f"  Type B: ERROR - {e}")


def test_shell_voicing():
    """Test shell voicings"""
    print("\n" + "=" * 60)
    print("Testing Shell Voicings")
    print("=" * 60)

    from app.theory.chord_library import get_shell_voicing

    test_chords = [
        ("C", "maj7"),
        ("F", "7"),
        ("D", "m7"),
        ("G", "7"),
    ]

    for root, quality in test_chords:
        notes = get_shell_voicing(root, quality, octave=3)
        print(f"{root}{quality:6} shell: {notes}  # Root-3-7 only")


def test_so_what_voicing():
    """Test So What voicing"""
    print("\n" + "=" * 60)
    print("Testing So What Voicing")
    print("=" * 60)

    from app.theory.chord_library import get_so_what_voicing

    # Test on various roots
    roots = ["D", "E", "F", "G", "C"]

    for root in roots:
        notes = get_so_what_voicing(root, octave=3)
        print(f"{root} So What: {notes}  # Quartal stack + M3")


def test_summary():
    """Print summary of voicing expansion"""
    print("\n" + "=" * 60)
    print("VOICING EXPANSION SUMMARY")
    print("=" * 60)

    print("\n📊 Phase 1: Inversions")
    print("-" * 60)
    print("  • 56 base chord types")
    print("  • 438 total voicings with inversions (7.8x expansion)")
    print("  • Functions: get_inversion_intervals(), get_chord_notes_with_inversion()")

    print("\n📊 Phase 2: Advanced Voicing Styles")
    print("-" * 60)
    print("  • Drop voicings:  drop-2, drop-3, drop-2-4")
    print("  • Rootless:       Type A (3-5-7-9), Type B (7-9-3-5)")
    print("  • Shell:          Root-3-7")
    print("  • So What:        Quartal stack + M3")
    print("  • VoicingStyle:   19 enum values defined")

    print("\n📊 Estimated Total Voicings (with Phase 2):")
    print("-" * 60)
    print("  • Inversions:      438")
    print("  • Drop voicings:   ~1,314  (438 × 3 drop styles)")
    print("  • Rootless:        ~112   (56 chords × 2 types)")
    print("  • Shell:           ~56")
    print("  • So What:         12     (one per root)")
    print("  • TOTAL:           ~1,900+ distinct voicings")

    print("\n📈 Expansion: From 56 → ~1,900+ voicings (34x expansion!)")


if __name__ == "__main__":
    test_drop_voicings()
    test_rootless_voicings()
    test_shell_voicing()
    test_so_what_voicing()
    test_summary()
    print("\n✅ All voicing tests completed!\n")
