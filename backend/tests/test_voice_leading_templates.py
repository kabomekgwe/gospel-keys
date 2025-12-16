"""
Tests for Jazz Voice Leading Templates (Phase 5)

Simplified test suite verifying core functionality of:
- Bill Evans rootless voicings
- Upper structure triads
- Drop voicings
- Jazz template database

Based on Bill Evans and 2025 jazz pedagogy research.
"""

from app.theory.voice_leading_templates import (
    get_bill_evans_voicing,
    get_rootless_left_hand,
    get_upper_structure_voicing,
    get_drop_2_voicing,
    get_so_what_voicing,
    BILL_EVANS_TEMPLATES,
    UPPER_STRUCTURE_PATTERNS,
)


# ============================================================================
# TEST BILL EVANS ROOTLESS VOICINGS
# ============================================================================

def test_bill_evans_a_form():
    """Test Bill Evans A-form voicing (3-5-7-9)"""
    voicing = get_bill_evans_voicing('D', 'm7', form='A', octave=3)

    assert len(voicing) == 4, f"Should have 4 notes, got {len(voicing)}"
    assert all(isinstance(note, str) for note in voicing), "All notes should be strings"

    print(f"✓ Bill Evans A-form: Dm7 = {voicing}")


def test_bill_evans_b_form():
    """Test Bill Evans B-form voicing (7-9-3-5)"""
    voicing = get_bill_evans_voicing('G', '7', form='B', octave=3)

    assert len(voicing) == 4, f"Should have 4 notes, got {len(voicing)}"
    assert all(isinstance(note, str) for note in voicing), "All notes should be strings"

    print(f"✓ Bill Evans B-form: G7 = {voicing}")


def test_rootless_left_hand():
    """Test rootless left hand voicings"""
    voicing_a = get_rootless_left_hand('D', 'm7', form='A', octave=3)
    voicing_b = get_rootless_left_hand('G', '7', form='B', octave=3)

    assert len(voicing_a) == 4
    assert len(voicing_b) == 4
    assert voicing_a != voicing_b, "A and B forms should be different"

    print(f"✓ Rootless left hand: A={len(voicing_a)} notes, B={len(voicing_b)} notes")


# ============================================================================
# TEST UPPER STRUCTURE TRIADS
# ============================================================================

def test_upper_structure_sharp11_dominant():
    """Test upper structure (#11 dominant)"""
    voicing = get_upper_structure_voicing('C', '7', 'sharp11_dominant', octave=3)

    assert len(voicing) > 0, "Should return voicing"
    assert all(isinstance(note, str) for note in voicing), "All notes should be strings"

    print(f"✓ Upper structure #11: C7 = {voicing}")


def test_upper_structure_database():
    """Test upper structure pattern database completeness"""
    assert len(UPPER_STRUCTURE_PATTERNS) >= 5, f"Should have ≥5 patterns, got {len(UPPER_STRUCTURE_PATTERNS)}"

    # Verify pattern structure
    for pattern_name, pattern_data in UPPER_STRUCTURE_PATTERNS.items():
        assert 'base_quality' in pattern_data, f"Pattern {pattern_name} missing 'base_quality'"
        assert 'upper_triad_interval' in pattern_data, f"Pattern {pattern_name} missing 'upper_triad_interval'"

    print(f"✓ Upper structure database: {len(UPPER_STRUCTURE_PATTERNS)} patterns")


# ============================================================================
# TEST DROP VOICINGS
# ============================================================================

def test_drop_2_voicing():
    """Test drop-2 voicing"""
    voicing = get_drop_2_voicing('B', 'C', 'maj7')  # melody_note, chord_root, chord_quality

    assert len(voicing) == 4, f"Drop-2 should have 4 notes, got {len(voicing)}"
    assert all(isinstance(note, str) for note in voicing), "All notes should be strings"

    print(f"✓ Drop-2 voicing: Cmaj7 = {voicing}")


# ============================================================================
# TEST SO WHAT VOICING
# ============================================================================

def test_so_what_voicing():
    """Test So What voicing (quartal)"""
    voicing = get_so_what_voicing('D', 'm', octave=3)

    assert len(voicing) >= 5, f"So What voicing should have ≥5 notes, got {len(voicing)}"
    assert all(isinstance(note, str) for note in voicing), "All notes should be strings"

    print(f"✓ So What voicing: Dm = {voicing} ({len(voicing)} notes)")


# ============================================================================
# TEST TEMPLATE DATABASE
# ============================================================================

def test_bill_evans_template_database():
    """Test Bill Evans template database completeness"""
    assert len(BILL_EVANS_TEMPLATES) >= 5, f"Should have ≥5 templates, got {len(BILL_EVANS_TEMPLATES)}"

    # Verify key templates exist
    key_templates = [
        'ii_V_I_major_form_A',
        'ii_V_I_major_form_B'
    ]

    for template in key_templates:
        assert template in BILL_EVANS_TEMPLATES, f"Missing template: {template}"

    print(f"✓ Bill Evans template database: {len(BILL_EVANS_TEMPLATES)} templates")


def test_template_structure():
    """Test template data structure validity"""
    template = BILL_EVANS_TEMPLATES['ii_V_I_major_form_A']

    # Required fields
    required_fields = ['progression', 'description', 'source', 'smoothness', 'genre']
    for field in required_fields:
        assert field in template, f"Template missing field: {field}"

    # Progression format
    progression = template['progression']
    assert len(progression) >= 2, "Progression should have ≥2 chords"
    assert isinstance(progression, list), "Progression should be a list"

    # Smoothness score
    assert 0 <= template['smoothness'] <= 1, f"Smoothness should be 0-1, got {template['smoothness']}"

    print(f"✓ Template structure valid: '{template['description']}'")


def test_template_metadata():
    """Test template metadata accuracy"""
    count_by_genre = {}

    for template_name, template_data in BILL_EVANS_TEMPLATES.items():
        genre = template_data.get('genre', 'unknown')
        count_by_genre[genre] = count_by_genre.get(genre, 0) + 1

    assert 'jazz' in count_by_genre, "Should have jazz templates"
    assert count_by_genre['jazz'] >= 3, f"Should have ≥3 jazz templates, got {count_by_genre.get('jazz', 0)}"

    print(f"✓ Template metadata: {count_by_genre}")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Jazz Voice Leading Templates Tests (Phase 5)")
    print("=" * 70)

    # Bill Evans voicings
    print("\n🎹 Bill Evans Rootless Voicings:")
    test_bill_evans_a_form()
    test_bill_evans_b_form()
    test_rootless_left_hand()

    # Upper structures
    print("\n🔺 Upper Structure Triads:")
    test_upper_structure_sharp11_dominant()
    test_upper_structure_database()

    # Drop voicings
    print("\n📐 Drop Voicings:")
    test_drop_2_voicing()

    # So What
    print("\n🎺 Quartal Voicings:")
    test_so_what_voicing()

    # Template database
    print("\n📚 Template Database:")
    test_bill_evans_template_database()
    test_template_structure()
    test_template_metadata()

    print("\n" + "=" * 70)
    print("✅ All Jazz Template tests passed!")
    print("=" * 70)
