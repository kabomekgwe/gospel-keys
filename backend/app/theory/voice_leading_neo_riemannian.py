"""
Neo-Riemannian Voice Leading Transformations (Phase 5 - Category 1)

Implements Neo-Riemannian theory operations for parsimonious voice leading:
- PLR transformations (Parallel, Leading-tone, Relative)
- Tonnetz lattice geometry
- Minimal voice movement between chords
- Voice-leading path finding

Based on 2025 research:
- O'Hara: "Neo-Riemannian Theory as Voice Leading Pedagogy"
- Cohn: "Neo-Riemannian Operations, Parsimonious Trichords"
- Tonnetz lattice visualization principles

Neo-Riemannian theory provides a geometric approach to understanding harmonic
relationships through minimal voice-leading transformations. Each transformation
moves exactly ONE voice by at most 2 semitones.
"""

from typing import List, Tuple, Dict, Optional
from collections import deque
from app.theory.chord_types import get_chord_type, get_chord_notes
from app.theory.interval_utils import note_to_semitone, semitone_to_note


# ============================================================================
# CORE PLR TRANSFORMATIONS
# ============================================================================

def apply_parallel_transform(
    chord_root: str,
    chord_quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, str, List[str], Dict]:
    """
    Apply Parallel (P) transformation: Major ↔ Minor.
    Moves the 3rd by a semitone (major 3rd ↔ minor 3rd).

    The P transformation preserves the root and fifth, changing only the third.
    This is the simplest Neo-Riemannian operation.

    Args:
        chord_root: Root note (e.g., 'C', 'F#')
        chord_quality: Chord quality ('maj', 'min', '', 'm')
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (new_root, new_quality, voicing, metadata)

    Examples:
        >>> apply_parallel_transform('C', 'maj')
        ('C', 'min', ['C4', 'Eb4', 'G4'], {...})

        >>> apply_parallel_transform('A', 'min')
        ('A', 'maj', ['A4', 'C#4', 'E4'], {...})
    """
    # Normalize quality
    quality_normalized = _normalize_quality(chord_quality)

    # Determine transformation
    if quality_normalized == 'major':
        new_quality = 'm'  # Use 'm' not 'min' (chord_types uses 'm')
        new_quality_full = 'minor'
        voice_moved = 'third'
        movement = -1  # Major 3rd down to minor 3rd
    elif quality_normalized == 'minor':
        new_quality = ''  # Major triad
        new_quality_full = 'major'
        voice_moved = 'third'
        movement = +1  # Minor 3rd up to major 3rd
    else:
        raise ValueError(f"P transformation only works on major/minor triads, got: {chord_quality}")

    # Generate voicing (get_chord_notes doesn't take octave)
    voicing = get_chord_notes(chord_root, new_quality, prefer_sharps)

    # Metadata
    metadata = {
        'transformation': 'P',
        'description': f'Parallel: {chord_root} {quality_normalized} → {chord_root} {new_quality_full}',
        'voice_moved': voice_moved,
        'semitones_moved': abs(movement),
        'total_movement': abs(movement),  # Only 1 voice moves
        'is_parsimonious': True  # P is always parsimonious (≤2 semitones)
    }

    return (chord_root, new_quality, voicing, metadata)


def apply_leading_tone_transform(
    chord_root: str,
    chord_quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, str, List[str], Dict]:
    """
    Apply Leading-tone (L) transformation: Major ↔ Minor.
    Moves the root by a semitone (up for maj→min, down for min→maj).

    The L transformation changes the root while preserving common tones.
    Major chord: root moves UP a semitone to become the third of the minor chord.
    Minor chord: third moves DOWN a semitone to become the root of the major chord.

    Args:
        chord_root: Root note
        chord_quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (new_root, new_quality, voicing, metadata)

    Examples:
        >>> apply_leading_tone_transform('C', 'maj')
        ('E', 'min', ['E4', 'G4', 'B4'], {...})  # C→E (up m3)

        >>> apply_leading_tone_transform('E', 'min')
        ('C', 'maj', ['C4', 'E4', 'G4'], {...})  # E→C (down m3)
    """
    quality_normalized = _normalize_quality(chord_quality)

    root_semitone = note_to_semitone(chord_root)

    if quality_normalized == 'major':
        # Major → Minor: root moves UP m3 (4 semitones) to become third of minor
        # C major (C-E-G) → E minor (E-G-B)
        new_root_semitone = (root_semitone + 4) % 12
        new_root = semitone_to_note(new_root_semitone, prefer_sharps)
        new_quality = 'm'  # Use 'm' not 'min'
        new_quality_full = 'minor'
        voice_moved = 'root'
        movement = +4  # Up minor 3rd

    elif quality_normalized == 'minor':
        # Minor → Major: third moves DOWN m3 to become root of major
        # E minor (E-G-B) → C major (C-E-G)
        # Root moves DOWN m3 (4 semitones)
        new_root_semitone = (root_semitone - 4) % 12
        new_root = semitone_to_note(new_root_semitone, prefer_sharps)
        new_quality = ''  # Major
        new_quality_full = 'major'
        voice_moved = 'third'
        movement = -4  # Down minor 3rd

    else:
        raise ValueError(f"L transformation only works on major/minor triads, got: {chord_quality}")

    # Generate voicing (get_chord_notes doesn't take octave)
    voicing = get_chord_notes(new_root, new_quality, prefer_sharps)

    metadata = {
        'transformation': 'L',
        'description': f'Leading-tone: {chord_root} {quality_normalized} → {new_root} {new_quality_full}',
        'voice_moved': voice_moved,
        'semitones_moved': abs(movement),
        'total_movement': abs(movement),
        'is_parsimonious': False  # L moves by 4 semitones (not ≤2)
    }

    return (new_root, new_quality, voicing, metadata)


def apply_relative_transform(
    chord_root: str,
    chord_quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, str, List[str], Dict]:
    """
    Apply Relative (R) transformation: Major ↔ Minor.
    Moves the fifth by a whole tone (major→up 2, minor→down 2).

    The R transformation relates a major chord to its relative minor (or vice versa).
    Major chord: fifth moves UP a whole tone to become root of relative minor.
    Minor chord: root moves DOWN a whole tone to become fifth of relative major.

    Args:
        chord_root: Root note
        chord_quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (new_root, new_quality, voicing, metadata)

    Examples:
        >>> apply_relative_transform('C', 'maj')
        ('A', 'min', ['A4', 'C5', 'E5'], {...})  # C major → A minor (relative)

        >>> apply_relative_transform('A', 'min')
        ('C', 'maj', ['C4', 'E4', 'G4'], {...})  # A minor → C major (relative)
    """
    quality_normalized = _normalize_quality(chord_quality)

    root_semitone = note_to_semitone(chord_root)

    if quality_normalized == 'major':
        # Major → Minor: fifth moves UP whole tone (root moves DOWN m3)
        # C major (C-E-G) → A minor (A-C-E)
        new_root_semitone = (root_semitone - 3) % 12  # Down m3
        new_root = semitone_to_note(new_root_semitone, prefer_sharps)
        new_quality = 'm'  # Use 'm' not 'min'
        new_quality_full = 'minor'
        voice_moved = 'fifth'
        movement = +2  # Fifth moves up whole tone

    elif quality_normalized == 'minor':
        # Minor → Major: root moves UP m3 (fifth moves DOWN whole tone)
        # A minor (A-C-E) → C major (C-E-G)
        new_root_semitone = (root_semitone + 3) % 12  # Up m3
        new_root = semitone_to_note(new_root_semitone, prefer_sharps)
        new_quality = ''  # Major
        new_quality_full = 'major'
        voice_moved = 'root'
        movement = +3  # Root moves up m3

    else:
        raise ValueError(f"R transformation only works on major/minor triads, got: {chord_quality}")

    # Generate voicing (get_chord_notes doesn't take octave)
    voicing = get_chord_notes(new_root, new_quality, prefer_sharps)

    metadata = {
        'transformation': 'R',
        'description': f'Relative: {chord_root} {quality_normalized} → {new_root} {new_quality_full}',
        'voice_moved': voice_moved,
        'semitones_moved': abs(movement),
        'total_movement': abs(movement),
        'is_parsimonious': movement <= 2  # R is parsimonious (2 semitones)
    }

    return (new_root, new_quality, voicing, metadata)


# ============================================================================
# TRANSFORMATION SEQUENCES & COMBINATIONS
# ============================================================================

def get_plr_transformation_sequence(
    start_root: str,
    start_quality: str,
    plr_sequence: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, str, List[str], Dict]]:
    """
    Apply a sequence of PLR transformations.

    Allows complex harmonic progressions using multiple transformations.
    Each transformation is applied to the result of the previous one.

    Args:
        start_root: Starting chord root
        start_quality: Starting chord quality
        plr_sequence: String of transformations (e.g., "PLPR", "LRL")
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of (root, quality, voicing, metadata) for each step

    Examples:
        >>> get_plr_transformation_sequence('C', 'maj', 'PRL')
        [
            ('C', 'min', [...], {...}),   # P: C major → C minor
            ('Ab', 'maj', [...], {...}),  # R: C minor → Ab major
            ('F', 'min', [...], {...})    # L: Ab major → F minor
        ]
    """
    transformations = {
        'P': apply_parallel_transform,
        'L': apply_leading_tone_transform,
        'R': apply_relative_transform
    }

    results = []
    current_root = start_root
    current_quality = start_quality

    for operation in plr_sequence.upper():
        if operation not in transformations:
            raise ValueError(f"Invalid PLR operation: {operation}. Use P, L, or R.")

        transform_func = transformations[operation]
        new_root, new_quality, voicing, metadata = transform_func(
            current_root, current_quality, octave, prefer_sharps
        )

        # Add sequence information
        metadata['sequence_step'] = len(results) + 1
        metadata['from_chord'] = f"{current_root}{current_quality}"
        metadata['to_chord'] = f"{new_root}{new_quality}"

        results.append((new_root, new_quality, voicing, metadata))

        # Update for next iteration
        current_root = new_root
        current_quality = new_quality

    return results


def generate_tonnetz_neighbors(
    chord_root: str,
    chord_quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Dict[str, Tuple[str, str, List[str]]]:
    """
    Generate all Tonnetz neighbors (one PLR transformation away).

    The Tonnetz (tone network) is a lattice of pitch relationships.
    Each triad has exactly 3 neighbors, accessible via P, L, or R.

    Args:
        chord_root: Root note
        chord_quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Dictionary mapping transformation names to resulting chords

    Examples:
        >>> generate_tonnetz_neighbors('C', 'maj')
        {
            'P': ('C', 'min', ['C4', 'Eb4', 'G4']),
            'L': ('E', 'min', ['E4', 'G4', 'B4']),
            'R': ('A', 'min', ['A4', 'C5', 'E5'])
        }
    """
    neighbors = {}

    # Apply each transformation
    for name, func in [
        ('P', apply_parallel_transform),
        ('L', apply_leading_tone_transform),
        ('R', apply_relative_transform)
    ]:
        try:
            new_root, new_quality, voicing, _ = func(
                chord_root, chord_quality, octave, prefer_sharps
            )
            neighbors[name] = (new_root, new_quality, voicing)
        except ValueError:
            # Transformation not applicable (e.g., non-triad)
            pass

    return neighbors


# ============================================================================
# PARSIMONIOUS VOICE LEADING
# ============================================================================

def get_parsimonious_voice_leading(
    chord1_root: str,
    chord1_quality: str,
    chord2_root: str,
    chord2_quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[Optional[str], Optional[List], int]:
    """
    Find parsimonious (minimal motion) PLR path between two chords.

    Parsimonious voice leading moves voices by the smallest possible distance.
    In Neo-Riemannian theory, this typically means ≤2 semitones total movement.

    Args:
        chord1_root: Starting chord root
        chord1_quality: Starting chord quality
        chord2_root: Target chord root
        chord2_quality: Target chord quality
        octave: Octave for voicing
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (transformation_sequence, voicing_path, total_movement)
        Returns (None, None, inf) if no path found

    Examples:
        >>> get_parsimonious_voice_leading('C', 'maj', 'C', 'min')
        ('P', [...], 1)  # Single P transformation, 1 semitone

        >>> get_parsimonious_voice_leading('C', 'maj', 'A', 'min')
        ('R', [...], 2)  # Single R transformation, 2 semitones
    """
    # Check if direct single transformation exists
    for transform_name, transform_func in [
        ('P', apply_parallel_transform),
        ('L', apply_leading_tone_transform),
        ('R', apply_relative_transform)
    ]:
        try:
            new_root, new_quality, voicing, metadata = transform_func(
                chord1_root, chord1_quality, octave, prefer_sharps
            )

            # Check if this matches target
            if _chords_match(new_root, new_quality, chord2_root, chord2_quality):
                return (
                    transform_name,
                    [voicing],
                    metadata['total_movement']
                )
        except ValueError:
            continue

    # No direct parsimonious path found
    # For true parsimonious leading, only single transformations count
    return (None, None, float('inf'))


# ============================================================================
# TONNETZ LATTICE GEOMETRY
# ============================================================================

def calculate_tonnetz_distance(
    chord1_root: str,
    chord1_quality: str,
    chord2_root: str,
    chord2_quality: str
) -> int:
    """
    Calculate geometric distance on Tonnetz lattice (number of PLR steps).

    The Tonnetz distance represents the minimum number of PLR transformations
    needed to move from chord1 to chord2.

    Args:
        chord1_root: Starting chord root
        chord1_quality: Starting chord quality
        chord2_root: Target chord root
        chord2_quality: Target chord quality

    Returns:
        Integer distance (number of transformations)
        Returns -1 if no path exists

    Examples:
        >>> calculate_tonnetz_distance('C', 'maj', 'C', 'min')
        1  # One P transformation

        >>> calculate_tonnetz_distance('C', 'maj', 'E', 'min')
        1  # One L transformation

        >>> calculate_tonnetz_distance('C', 'maj', 'Ab', 'min')
        2  # Two transformations (hexatonic pole)
    """
    # BFS to find shortest path
    path = get_tonnetz_path(
        chord1_root, chord1_quality,
        chord2_root, chord2_quality,
        max_steps=10
    )

    if path is None:
        return -1

    return len(path)


def get_tonnetz_path(
    chord1_root: str,
    chord1_quality: str,
    chord2_root: str,
    chord2_quality: str,
    max_steps: int = 6
) -> Optional[List[str]]:
    """
    Find shortest PLR transformation path using BFS (breadth-first search).

    Uses graph traversal to find the optimal sequence of transformations
    connecting two chords on the Tonnetz lattice.

    Args:
        chord1_root: Starting chord root
        chord1_quality: Starting chord quality
        chord2_root: Target chord root
        chord2_quality: Target chord quality
        max_steps: Maximum path length to search

    Returns:
        List of transformation names (e.g., ['P', 'R', 'L'])
        Returns None if no path found within max_steps

    Examples:
        >>> get_tonnetz_path('C', 'maj', 'A', 'min')
        ['R']  # Single R transformation

        >>> get_tonnetz_path('C', 'maj', 'Ab', 'min')
        ['P', 'R']  # C major → C minor → Ab minor (hexatonic pole)
    """
    # Normalize chords
    start = _chord_signature(chord1_root, chord1_quality)
    target = _chord_signature(chord2_root, chord2_quality)

    if start == target:
        return []  # Already at target

    # BFS queue: (current_chord, path_taken)
    queue = deque([(start, [])])
    visited = {start}

    transformations = {
        'P': apply_parallel_transform,
        'L': apply_leading_tone_transform,
        'R': apply_relative_transform
    }

    while queue:
        current, path = queue.popleft()

        if len(path) >= max_steps:
            continue  # Max depth reached

        # Parse current chord
        current_root, current_quality = _parse_chord_signature(current)

        # Try each transformation
        for transform_name, transform_func in transformations.items():
            try:
                new_root, new_quality, _, _ = transform_func(current_root, current_quality)
                new_sig = _chord_signature(new_root, new_quality)

                if new_sig == target:
                    return path + [transform_name]  # Found target!

                if new_sig not in visited:
                    visited.add(new_sig)
                    queue.append((new_sig, path + [transform_name]))

            except ValueError:
                continue  # Transformation not applicable

    return None  # No path found


def apply_neo_riemannian_to_progression(
    progression: List[Tuple[str, str]],
    octave: int = 4,
    prefer_sharps: bool = True
) -> List[Tuple[str, str, List[str], Dict]]:
    """
    Optimize chord progression using Neo-Riemannian transformations.

    Analyzes a progression and provides PLR transformation analysis for each
    chord transition, helping to understand voice-leading relationships.

    Args:
        progression: List of (root, quality) tuples
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        List of (root, quality, voicing, metadata) with PLR analysis

    Example:
        >>> apply_neo_riemannian_to_progression([
        ...     ('C', 'maj'),
        ...     ('A', 'min'),
        ...     ('F', 'maj')
        ... ])
        [
            ('C', 'maj', [...], {'plr_to_next': 'R', 'tonnetz_distance': 1}),
            ('A', 'min', [...], {'plr_to_next': 'L', 'tonnetz_distance': 1}),
            ('F', 'maj', [...], {'plr_to_next': None})
        ]
    """
    results = []

    for i, (root, quality) in enumerate(progression):
        voicing = get_chord_notes(root, quality, prefer_sharps)

        metadata = {
            'chord_index': i,
            'chord': f"{root}{quality}"
        }

        # Analyze relationship to next chord
        if i < len(progression) - 1:
            next_root, next_quality = progression[i + 1]

            # Find PLR path
            path = get_tonnetz_path(root, quality, next_root, next_quality, max_steps=3)
            distance = calculate_tonnetz_distance(root, quality, next_root, next_quality)

            metadata['plr_to_next'] = path[0] if path and len(path) == 1 else path
            metadata['tonnetz_distance'] = distance
            metadata['is_parsimonious_transition'] = distance == 1
        else:
            metadata['plr_to_next'] = None
            metadata['tonnetz_distance'] = None

        results.append((root, quality, voicing, metadata))

    return results


def get_hexatonic_pole(
    chord_root: str,
    chord_quality: str,
    octave: int = 4,
    prefer_sharps: bool = True
) -> Tuple[str, str, List[str], Dict]:
    """
    Get hexatonic pole (two PLR transformations away).

    The hexatonic pole is a chord related by two specific transformations,
    creating maximal harmonic contrast while maintaining voice-leading economy.
    Most common: PL or PR combinations.

    Args:
        chord_root: Root note
        chord_quality: Chord quality
        octave: Starting octave
        prefer_sharps: Use sharps instead of flats

    Returns:
        Tuple of (pole_root, pole_quality, voicing, metadata)

    Examples:
        >>> get_hexatonic_pole('C', 'maj')
        ('Ab', 'min', [...], {...})  # C major → Ab minor (via PL or PR)

        >>> get_hexatonic_pole('A', 'min')
        ('C#', 'maj', [...], {...})  # A minor → C# major
    """
    # Hexatonic poles typically use PL or PR
    # Try PL first (most common)
    try:
        sequence = get_plr_transformation_sequence(
            chord_root, chord_quality, 'PL', octave, prefer_sharps
        )

        if len(sequence) == 2:
            pole_root, pole_quality, voicing, _ = sequence[-1]

            metadata = {
                'transformation': 'PL',
                'description': f'Hexatonic pole: {chord_root}{chord_quality} → {pole_root}{pole_quality}',
                'path': ['P', 'L'],
                'tonnetz_distance': 2,
                'is_hexatonic_pole': True
            }

            return (pole_root, pole_quality, voicing, metadata)
    except:
        pass

    # Fallback: try PR
    sequence = get_plr_transformation_sequence(
        chord_root, chord_quality, 'PR', octave, prefer_sharps
    )

    pole_root, pole_quality, voicing, _ = sequence[-1]

    metadata = {
        'transformation': 'PR',
        'description': f'Hexatonic pole: {chord_root}{chord_quality} → {pole_root}{pole_quality}',
        'path': ['P', 'R'],
        'tonnetz_distance': 2,
        'is_hexatonic_pole': True
    }

    return (pole_root, pole_quality, voicing, metadata)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _normalize_quality(quality: str) -> str:
    """Normalize chord quality to 'major' or 'minor'."""
    quality_lower = quality.lower().strip()

    if quality_lower in ['', 'maj', 'major', 'M']:
        return 'major'
    elif quality_lower in ['m', 'min', 'minor', '-']:
        return 'minor'
    else:
        # For other qualities, try to infer from chord library
        try:
            chord = get_chord_type(quality)
            # Check intervals for major/minor quality
            if 3 in chord.intervals:  # Minor 3rd
                return 'minor'
            elif 4 in chord.intervals:  # Major 3rd
                return 'major'
        except:
            pass

    raise ValueError(f"Cannot determine major/minor quality from: {quality}")


def _chords_match(root1: str, quality1: str, root2: str, quality2: str) -> bool:
    """Check if two chords are equivalent."""
    return (_chord_signature(root1, quality1) ==
            _chord_signature(root2, quality2))


def _chord_signature(root: str, quality: str) -> str:
    """Create unique signature for chord comparison."""
    quality_normalized = _normalize_quality(quality)
    root_semitone = note_to_semitone(root)
    return f"{root_semitone}_{quality_normalized}"


def _parse_chord_signature(signature: str) -> Tuple[str, str]:
    """Parse chord signature back to (root, quality)."""
    parts = signature.split('_')
    root_semitone = int(parts[0])
    quality_normalized = parts[1]

    root = semitone_to_note(root_semitone, prefer_sharps=True)
    quality = 'm' if quality_normalized == 'minor' else ''  # Use 'm' not 'min'

    return (root, quality)


__all__ = [
    # Core PLR transformations
    'apply_parallel_transform',
    'apply_leading_tone_transform',
    'apply_relative_transform',

    # Sequences and combinations
    'get_plr_transformation_sequence',
    'generate_tonnetz_neighbors',

    # Parsimonious voice leading
    'get_parsimonious_voice_leading',

    # Tonnetz lattice
    'calculate_tonnetz_distance',
    'get_tonnetz_path',
    'apply_neo_riemannian_to_progression',
    'get_hexatonic_pole',
]
