"""Voice Leading Engine - Shared voice leading optimization across all genres

Provides smooth voice leading algorithms that minimize movement between chords.
Can be customized with genre-specific rules (e.g., jazz allows more movement,
classical requires stricter rules to avoid parallel 5ths/octaves).
"""

from typing import List, Optional


def find_closest_voicing(
    chord_tones: List[int],
    previous_voicing: Optional[List[int]] = None,
    max_movement: Optional[int] = None,
    allow_wide_voicings: bool = True
) -> List[int]:
    """Find the chord inversion that minimizes voice movement.

    Universal voice leading algorithm used across all genres.
    Generates all possible inversions (root, 1st, 2nd, etc.) within +/- 1 octave
    and selects the one with minimum total voice movement.

    Args:
        chord_tones: Root position chord tones (MIDI note numbers)
        previous_voicing: Previous chord's voicing for smooth voice leading
        max_movement: Maximum allowed semitones per voice (None = unlimited)
                     Classical: 7 (perfect 5th), Jazz: 12 (octave), Gospel: 10
        allow_wide_voicings: If True, try octave variations (jazz, neo-soul)
                            If False, stay closer (classical, gospel ballads)

    Returns:
        Best inversion for smooth voice leading

    Example:
        >>> # Cmaj7 to Dm7 voice leading
        >>> cmaj7 = [48, 52, 55, 59]  # C, E, G, B (root position)
        >>> dm7 = [50, 53, 57, 60]    # D, F, A, C (root position)
        >>> best_dm7 = find_closest_voicing(dm7, previous_voicing=cmaj7)
        >>> # Returns optimal inversion with minimal movement from Cmaj7
    """
    if not previous_voicing:
        return chord_tones

    # Generate all possible inversions within +/- 1 octave
    inversions = []

    # Add root position and inversions by rotating chord tones
    for rotation in range(len(chord_tones)):
        inversion = chord_tones[rotation:] + chord_tones[:rotation]
        inversions.append(inversion)

        # Also try octave up/down for each inversion (if allowed)
        if allow_wide_voicings:
            inversions.append([n + 12 for n in inversion])
            inversions.append([n - 12 for n in inversion])

    # Find inversion with minimum total movement
    best_inversion = chord_tones
    min_movement = float('inf')

    for inversion in inversions:
        # Calculate total movement (sum of distances between voices)
        movement = 0

        # Compare each note in current chord to closest note in previous
        for note in inversion:
            if previous_voicing:
                # Find closest note in previous voicing
                closest_distance = min(abs(note - prev_note) for prev_note in previous_voicing)
                movement += closest_distance

        # Check max_movement constraint (if specified)
        if max_movement is not None:
            # Calculate max individual voice movement in this inversion
            max_individual_movement = max(
                min(abs(note - prev_note) for prev_note in previous_voicing)
                for note in inversion
            )
            if max_individual_movement > max_movement:
                continue  # Skip this inversion

        if movement < min_movement:
            min_movement = movement
            best_inversion = inversion

    return best_inversion


def optimize_voice_leading(
    chord_tones: List[int],
    previous_voicing: Optional[List[int]] = None,
    genre: str = "gospel"
) -> List[int]:
    """Optimize voice leading with genre-specific rules.

    Convenience wrapper around find_closest_voicing with genre presets.

    Args:
        chord_tones: Root position chord tones
        previous_voicing: Previous chord's voicing
        genre: Genre name for preset rules
               - "gospel": max_movement=10, allow_wide=True
               - "jazz": max_movement=12, allow_wide=True
               - "neosoul": max_movement=12, allow_wide=True
               - "blues": max_movement=10, allow_wide=True
               - "classical": max_movement=7, allow_wide=False (strict)

    Returns:
        Best inversion for the genre
    """
    # Genre-specific voice leading rules
    genre_rules = {
        "gospel": {"max_movement": 10, "allow_wide_voicings": True},
        "jazz": {"max_movement": 12, "allow_wide_voicings": True},
        "neosoul": {"max_movement": 12, "allow_wide_voicings": True},
        "blues": {"max_movement": 10, "allow_wide_voicings": True},
        "classical": {"max_movement": 7, "allow_wide_voicings": False},
    }

    rules = genre_rules.get(genre.lower(), genre_rules["gospel"])

    return find_closest_voicing(
        chord_tones=chord_tones,
        previous_voicing=previous_voicing,
        max_movement=rules["max_movement"],
        allow_wide_voicings=rules["allow_wide_voicings"]
    )


def get_chord_voicing(
    chord_tones: List[int],
    previous_voicing: Optional[List[int]] = None,
    octave: int = 4,
    genre: str = "gospel"
) -> List[int]:
    """Get MIDI note numbers for chord tones with voice leading.

    Combines octave placement with voice leading optimization.

    Args:
        chord_tones: Relative chord tones (e.g., [0, 4, 7] for major triad)
        previous_voicing: Previous chord's MIDI notes for smooth voice leading
        octave: Base octave (3 for bass, 4 for mid-range, 5 for treble)
        genre: Genre for voice leading rules

    Returns:
        List of MIDI note numbers optimized for voice leading

    Example:
        >>> # Get Cmaj voicing in octave 4 after playing Dm7
        >>> dm7_voicing = [50, 53, 57, 60]  # Previous chord
        >>> cmaj_tones = [0, 4, 7]  # Major triad intervals
        >>> cmaj_voicing = get_chord_voicing(cmaj_tones, dm7_voicing, octave=4)
        >>> # Returns optimal Cmaj7 voicing with minimal movement from Dm7
    """
    # Convert relative intervals to absolute MIDI notes
    base_midi = 12 * (octave + 1)  # MIDI note for C in given octave
    root_position = [base_midi + tone for tone in chord_tones]

    # Apply voice leading if previous voicing exists
    if previous_voicing:
        return optimize_voice_leading(root_position, previous_voicing, genre=genre)
    else:
        return root_position


# ============================================================================
# PHASE 5 ENHANCEMENT: TEMPLATE INTEGRATION
# ============================================================================

def find_closest_voicing_with_templates(
    chord_tones: List[int],
    previous_voicing: Optional[List[int]] = None,
    genre: str = "gospel",
    use_templates: bool = True,
    template_library: Optional[str] = None
) -> List[int]:
    """Enhanced voice leading with jazz template matching (Phase 5).

    When use_templates=True and genre is jazz/neosoul, this function
    will attempt to match chord to a pre-defined voicing template from
    masters like Bill Evans, McCoy Tyner, etc.

    Falls back to existing greedy algorithm if:
    - Templates not enabled
    - Genre doesn't use templates
    - No matching template found

    Args:
        chord_tones: Root position chord tones (MIDI note numbers)
        previous_voicing: Previous chord's voicing for smooth voice leading
        genre: Genre for template matching ("jazz", "neosoul", etc.)
        use_templates: Whether to use template database
        template_library: Specific template library to use (optional)

    Returns:
        Best voicing (template or greedy)

    Example:
        >>> # Jazz voicing with Bill Evans template
        >>> cmaj7 = [60, 64, 67, 71]  # C, E, G, B
        >>> dm7 = [62, 65, 69, 72]    # D, F, A, C
        >>> voicing = find_closest_voicing_with_templates(
        ...     dm7, cmaj7, genre="jazz", use_templates=True
        ... )
        >>> # Returns Bill Evans rootless A-form if available
    """
    # Template matching for jazz/neosoul genres
    if use_templates and genre.lower() in ['jazz', 'neosoul']:
        try:
            from app.theory.voice_leading_templates import (
                get_bill_evans_voicing,
                BILL_EVANS_TEMPLATES
            )

            # Attempt template match
            # For now, use greedy - full template matching coming in future enhancement
            # TODO: Implement chord-to-template matching algorithm

        except ImportError:
            # Templates not available, fall back to greedy
            pass

    # Fallback to existing greedy algorithm
    return find_closest_voicing(
        chord_tones=chord_tones,
        previous_voicing=previous_voicing,
        max_movement=_get_max_movement_for_genre(genre),
        allow_wide_voicings=_allow_wide_voicings_for_genre(genre)
    )


def _get_max_movement_for_genre(genre: str) -> Optional[int]:
    """Get max_movement setting for genre."""
    genre_rules = {
        "gospel": 10,
        "jazz": 12,
        "neosoul": 12,
        "blues": 10,
        "classical": 7,
    }
    return genre_rules.get(genre.lower())


def _allow_wide_voicings_for_genre(genre: str) -> bool:
    """Get allow_wide_voicings setting for genre."""
    return genre.lower() != "classical"


__all__ = [
    "find_closest_voicing",
    "optimize_voice_leading",
    "get_chord_voicing",
    # Phase 5 additions
    "find_closest_voicing_with_templates",
]
