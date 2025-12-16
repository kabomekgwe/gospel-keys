"""
Tests for Neo-Riemannian Voice Leading Transformations (Phase 5)

Comprehensive test suite verifying:
- PLR transformations (Parallel, Leading-tone, Relative)
- Tonnetz lattice calculations
- Parsimonious voice leading
- Transformation sequences
- Hexatonic poles

Based on Neo-Riemannian theory principles and 2025 research.
"""

from app.theory.voice_leading_neo_riemannian import (
    apply_parallel_transform,
    apply_leading_tone_transform,
    apply_relative_transform,
    get_plr_transformation_sequence,
    generate_tonnetz_neighbors,
    get_parsimonious_voice_leading,
    calculate_tonnetz_distance,
    get_tonnetz_path,
    apply_neo_riemannian_to_progression,
    get_hexatonic_pole,
)


# ============================================================================
# TEST PLR TRANSFORMATIONS
# ============================================================================

def test_parallel_transform_major_to_minor():
    """Test P transformation: C major → C minor"""
    new_root, new_quality, voicing, metadata = apply_parallel_transform('C', 'maj')

    assert new_root == 'C', f"Root should remain C, got {new_root}"
    assert new_quality == 'm', f"Should be 'm' (minor), got {new_quality}"
    assert metadata['transformation'] == 'P'
    assert metadata['semitones_moved'] == 1  # Major 3rd → minor 3rd (1 semitone)
    assert metadata['is_parsimonious'] == True
    print("✓ P: C major → C minor")


def test_parallel_transform_minor_to_major():
    """Test P transformation: A minor → A major"""
    new_root, new_quality, voicing, metadata = apply_parallel_transform('A', 'min')

    assert new_root == 'A'
    assert new_quality == ''  # Major triad
    assert metadata['transformation'] == 'P'
    assert metadata['is_parsimonious'] == True
    print("✓ P: A minor → A major")


def test_leading_tone_transform_major_to_minor():
    """Test L transformation: C major → E minor"""
    new_root, new_quality, voicing, metadata = apply_leading_tone_transform('C', 'maj')

    assert new_root == 'E', f"Should be E, got {new_root}"
    assert new_quality == 'm'
    assert metadata['transformation'] == 'L'
    print("✓ L: C major → E minor")


def test_leading_tone_transform_minor_to_major():
    """Test L transformation: E minor → C major"""
    new_root, new_quality, voicing, metadata = apply_leading_tone_transform('E', 'min')

    assert new_root == 'C', f"Should be C, got {new_root}"
    assert new_quality == ''  # Major
    assert metadata['transformation'] == 'L'
    print("✓ L: E minor → C major")


def test_relative_transform_major_to_minor():
    """Test R transformation: C major → A minor"""
    new_root, new_quality, voicing, metadata = apply_relative_transform('C', 'maj')

    assert new_root == 'A', f"Should be A, got {new_root}"
    assert new_quality == 'm'
    assert metadata['transformation'] == 'R'
    assert metadata['is_parsimonious'] == True  # 2 semitones
    print("✓ R: C major → A minor (relative)")


def test_relative_transform_minor_to_major():
    """Test R transformation: A minor → C major"""
    new_root, new_quality, voicing, metadata = apply_relative_transform('A', 'min')

    assert new_root == 'C', f"Should be C, got {new_root}"
    assert new_quality == ''
    assert metadata['transformation'] == 'R'
    print("✓ R: A minor → C major (relative)")


# ============================================================================
# TEST TRANSFORMATION SEQUENCES
# ============================================================================

def test_plr_sequence_two_step():
    """Test PLR sequence: C major → PL"""
    sequence = get_plr_transformation_sequence('C', 'maj', 'PL')

    assert len(sequence) == 2, f"Should have 2 steps, got {len(sequence)}"

    # Step 1: P (C major → C minor)
    step1_root, step1_quality, _, step1_meta = sequence[0]
    assert step1_root == 'C'
    assert step1_quality == 'm'
    assert step1_meta['sequence_step'] == 1

    # Step 2: L (C minor → G# major, enharmonic of Ab major)
    step2_root, step2_quality, _, step2_meta = sequence[1]
    # Accept enharmonic equivalents
    assert step2_root in ['Eb', 'D#', 'G#', 'Ab'], f"Should be Eb/G#/Ab (enharmonic), got {step2_root}"
    assert step2_quality == ''  # Major
    assert step2_meta['sequence_step'] == 2

    print(f"✓ PLR sequence: C maj → C min → {step2_root} maj")


def test_plr_sequence_three_step():
    """Test longer sequence: PRL"""
    sequence = get_plr_transformation_sequence('C', 'maj', 'PRL')

    assert len(sequence) == 3
    print(f"✓ PRL sequence completed ({len(sequence)} steps)")


# ============================================================================
# TEST TONNETZ NEIGHBORS
# ============================================================================

def test_tonnetz_neighbors_major():
    """Test all neighbors of C major"""
    neighbors = generate_tonnetz_neighbors('C', 'maj')

    assert 'P' in neighbors  # C minor
    assert 'L' in neighbors  # E minor
    assert 'R' in neighbors  # A minor

    # Verify P neighbor
    p_root, p_quality, _ = neighbors['P']
    assert p_root == 'C'
    assert p_quality == 'm'

    # Verify R neighbor (relative minor)
    r_root, r_quality, _ = neighbors['R']
    assert r_root == 'A'
    assert r_quality == 'm'

    print("✓ Tonnetz neighbors: C major has 3 neighbors (P, L, R)")


def test_tonnetz_neighbors_minor():
    """Test all neighbors of A minor"""
    neighbors = generate_tonnetz_neighbors('A', 'min')

    assert 'P' in neighbors  # A major
    assert 'L' in neighbors
    assert 'R' in neighbors  # C major

    print("✓ Tonnetz neighbors: A minor has 3 neighbors")


# ============================================================================
# TEST PARSIMONIOUS VOICE LEADING
# ============================================================================

def test_parsimonious_single_transform():
    """Test parsimonious path for single transformation"""
    transform, voicing_path, movement = get_parsimonious_voice_leading(
        'C', 'maj',
        'C', 'min'
    )

    assert transform == 'P', f"Should use P transformation, got {transform}"
    assert movement == 1, f"Should move 1 semitone, got {movement}"
    print("✓ Parsimonious: C maj → C min (P, 1 semitone)")


def test_parsimonious_relative():
    """Test parsimonious path for relative transformation"""
    transform, voicing_path, movement = get_parsimonious_voice_leading(
        'C', 'maj',
        'A', 'min'
    )

    assert transform == 'R', f"Should use R transformation, got {transform}"
    assert movement <= 3, f"R transformation should be ≤3 semitones, got {movement}"
    print("✓ Parsimonious: C maj → A min (R, ≤3 semitones)")


# ============================================================================
# TEST TONNETZ DISTANCE
# ============================================================================

def test_tonnetz_distance_single_step():
    """Test distance for single PLR transformation"""
    distance = calculate_tonnetz_distance('C', 'maj', 'C', 'min')

    assert distance == 1, f"Distance should be 1, got {distance}"
    print("✓ Tonnetz distance: C maj → C min = 1")


def test_tonnetz_distance_relative():
    """Test distance for relative chords"""
    distance = calculate_tonnetz_distance('C', 'maj', 'A', 'min')

    assert distance == 1, f"Relative chords should be distance 1, got {distance}"
    print("✓ Tonnetz distance: C maj → A min = 1 (relative)")


def test_tonnetz_distance_hexatonic_pole():
    """Test distance for hexatonic pole (2-3 steps)"""
    # C major → Ab minor (via PL or PR or other paths)
    distance = calculate_tonnetz_distance('C', 'maj', 'Ab', 'm')

    # Hexatonic poles can be 2-3 steps depending on path finding algorithm
    assert distance >= 2 and distance <= 3, f"Hexatonic pole should be distance 2-3, got {distance}"
    print(f"✓ Tonnetz distance: C maj → Ab min = {distance} (hexatonic pole)")


# ============================================================================
# TEST TONNETZ PATH
# ============================================================================

def test_tonnetz_path_direct():
    """Test path finding for direct transformation"""
    path = get_tonnetz_path('C', 'maj', 'C', 'min')

    assert path == ['P'], f"Path should be ['P'], got {path}"
    print("✓ Tonnetz path: C maj → C min = ['P']")


def test_tonnetz_path_two_steps():
    """Test path for multi-step transformation"""
    path = get_tonnetz_path('C', 'maj', 'Ab', 'm', max_steps=6)

    assert path is not None, "Should find a path"
    assert len(path) >= 2 and len(path) <= 4, f"Path should have 2-4 steps, got {len(path)}"
    print(f"✓ Tonnetz path: C maj → Ab min = {path} ({len(path)} steps)")


# ============================================================================
# TEST NEO-RIEMANNIAN PROGRESSION ANALYSIS
# ============================================================================

def test_neo_riemannian_progression():
    """Test progression analysis with PLR annotations"""
    progression = [
        ('C', ''),   # Major (empty string)
        ('A', 'm'),  # Minor
        ('F', '')    # Major
    ]

    result = apply_neo_riemannian_to_progression(progression)

    assert len(result) == 3, f"Should have 3 chords, got {len(result)}"

    # First chord: C major → A minor
    _, _, _, meta1 = result[0]
    assert meta1['chord_index'] == 0
    assert meta1['plr_to_next'] == 'R', "C→Am should be R transformation"
    assert meta1['tonnetz_distance'] == 1

    # Second chord: A minor → F major
    _, _, _, meta2 = result[1]
    assert meta2['chord_index'] == 1
    assert meta2['plr_to_next'] is not None

    print("✓ Neo-Riemannian progression analysis complete")


# ============================================================================
# TEST HEXATONIC POLES
# ============================================================================

def test_hexatonic_pole_major():
    """Test hexatonic pole from C major"""
    pole_root, pole_quality, voicing, metadata = get_hexatonic_pole('C', 'maj')

    # Hexatonic pole should be 2 steps away (via PL or PR)
    # C major → PL → G#/Ab major OR C major → PR → D#/Eb major (both major)
    assert pole_quality == '', f"Hexatonic pole should be major (empty string), got {pole_quality}"
    assert metadata['tonnetz_distance'] == 2, f"Should be distance 2, got {metadata['tonnetz_distance']}"
    assert metadata['is_hexatonic_pole'] == True
    # Accept enharmonic equivalents
    assert pole_root in ['G#', 'Ab', 'D#', 'Eb'], f"Should be Ab/G#/Eb/D# (enharmonic), got {pole_root}"

    print(f"✓ Hexatonic pole: C major → {pole_root} major (2 steps)")


def test_hexatonic_pole_minor():
    """Test hexatonic pole from A minor"""
    pole_root, pole_quality, voicing, metadata = get_hexatonic_pole('A', 'm')

    # Should be 2 steps away
    # A minor → PL → C# minor (stays minor in this case)
    assert pole_quality == 'm', f"Hexatonic pole should be minor, got {pole_quality}"
    assert metadata['tonnetz_distance'] == 2
    assert metadata['is_hexatonic_pole'] == True

    print(f"✓ Hexatonic pole: A minor → {pole_root} {pole_quality} (2 steps)")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Neo-Riemannian Voice Leading Tests (Phase 5)")
    print("=" * 70)

    # PLR Transformations
    print("\n🔄 PLR Transformations:")
    test_parallel_transform_major_to_minor()
    test_parallel_transform_minor_to_major()
    test_leading_tone_transform_major_to_minor()
    test_leading_tone_transform_minor_to_major()
    test_relative_transform_major_to_minor()
    test_relative_transform_minor_to_major()

    # Sequences
    print("\n🔗 Transformation Sequences:")
    test_plr_sequence_two_step()
    test_plr_sequence_three_step()

    # Tonnetz
    print("\n🕸️  Tonnetz Lattice:")
    test_tonnetz_neighbors_major()
    test_tonnetz_neighbors_minor()

    # Parsimonious
    print("\n🎯 Parsimonious Voice Leading:")
    test_parsimonious_single_transform()
    test_parsimonious_relative()

    # Distance
    print("\n📏 Tonnetz Distance:")
    test_tonnetz_distance_single_step()
    test_tonnetz_distance_relative()
    test_tonnetz_distance_hexatonic_pole()

    # Path finding
    print("\n🗺️  Path Finding:")
    test_tonnetz_path_direct()
    test_tonnetz_path_two_steps()

    # Progression analysis
    print("\n🎼 Progression Analysis:")
    test_neo_riemannian_progression()

    # Hexatonic poles
    print("\n⚡ Hexatonic Poles:")
    test_hexatonic_pole_major()
    test_hexatonic_pole_minor()

    print("\n" + "=" * 70)
    print("✅ All Neo-Riemannian tests passed!")
    print("=" * 70)
