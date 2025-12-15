"""
Reharmonization Strategies (Phase 6)

Genre-specific reharmonization patterns and high-level templates:
- Jazz: ii-V-I variations, Coltrane changes, tritone subs
- Gospel: Chromatic passing, backdoor, Kirk Franklin style
- Classical: Modal interchange, secondary dominants
- Neo-Soul: Negative harmony, chromatic mediants
- Blues: Turnarounds, passing diminished, blues scale

Provides complete progression templates and style-appropriate constraints.
"""

from typing import List, Tuple, Dict, Optional, Any
from app.theory.interval_utils import note_to_semitone, semitone_to_note


# ============================================================================
# JAZZ STRATEGIES
# ============================================================================

def reharmonize_ii_V_I_jazz(
    key: str,
    variation: str = 'standard',
    octave: int = 4
) -> List[Tuple[str, str]]:
    """
    Generate jazz ii-V-I reharmonizations.

    Variations:
    - 'standard': Dm7 - G7 - Cmaj7 (in C)
    - 'tritone_sub': Dm7 - Db7 - Cmaj7
    - 'coltrane': Dm7 - Eb7 - G7 - B7 - Cmaj7 (major thirds cycle)
    - 'backdoor': Dm7 - Bb7 - Cmaj7
    - 'negative_harmony': Am7 - Db7 - Cmaj7
    - 'extended': Dm7 - Db7b9 - Cmaj9#11

    Args:
        key: Tonic key (e.g., 'C')
        variation: Which variation to use
        octave: Octave for voicing (ignored in this version)

    Returns:
        List of (root, quality) tuples
    """
    key_sem = note_to_semitone(key)

    # Standard ii-V-I
    ii_root = semitone_to_note((key_sem + 2) % 12)
    V_root = semitone_to_note((key_sem + 7) % 12)
    I_root = key

    if variation == 'standard':
        return [
            (ii_root, 'm7'),
            (V_root, '7'),
            (I_root, 'maj7')
        ]

    elif variation == 'tritone_sub':
        # Tritone substitute V7
        tritone_root = semitone_to_note((key_sem + 1) % 12, prefer_sharps=False)
        return [
            (ii_root, 'm7'),
            (tritone_root, '7'),
            (I_root, 'maj7')
        ]

    elif variation == 'coltrane':
        # Coltrane changes: major thirds cycle before resolution
        try:
            from app.theory.chord_substitutions import apply_coltrane_changes
            coltrane_chords = apply_coltrane_changes(V_root, '7')
            return [(ii_root, 'm7')] + coltrane_chords + [(I_root, 'maj7')]
        except:
            # Fallback: manual major thirds cycle
            return [
                (ii_root, 'm7'),
                (semitone_to_note((key_sem + 3) % 12), '7'),  # Eb7
                (V_root, '7'),  # G7
                (semitone_to_note((key_sem + 11) % 12), '7'),  # B7
                (I_root, 'maj7')
            ]

    elif variation == 'backdoor':
        # Backdoor resolution: bVII7 → I
        backdoor_root = semitone_to_note((key_sem - 2) % 12, prefer_sharps=False)
        return [
            (ii_root, 'm7'),
            (backdoor_root, '7'),
            (I_root, 'maj7')
        ]

    elif variation == 'negative_harmony':
        # Negative harmony transformation
        try:
            from app.theory.chord_substitutions import get_negative_harmony_chord
            neg_ii = get_negative_harmony_chord(ii_root, 'm7', key)
            neg_V = get_negative_harmony_chord(V_root, '7', key)
            return [
                neg_ii if neg_ii else (ii_root, 'm7'),
                neg_V if neg_V else (V_root, '7'),
                (I_root, 'maj7')
            ]
        except:
            # Fallback: relative substitutes
            return [
                (semitone_to_note((key_sem + 9) % 12), 'm7'),  # vi instead of ii
                (semitone_to_note((key_sem + 1) % 12, prefer_sharps=False), '7'),  # bII7
                (I_root, 'maj7')
            ]

    elif variation == 'extended':
        # Extended with altered dominants and tensions
        tritone_root = semitone_to_note((key_sem + 1) % 12, prefer_sharps=False)
        return [
            (ii_root, 'm7'),
            (tritone_root, '7b9'),
            (I_root, 'maj9#11')
        ]

    # Default to standard
    return [(ii_root, 'm7'), (V_root, '7'), (I_root, 'maj7')]


# ============================================================================
# GOSPEL STRATEGIES
# ============================================================================

def reharmonize_gospel_progression(
    progression: List[Tuple[str, str]],
    intensity: str = 'medium',
    add_passing_chords: bool = True
) -> List[Tuple[str, str]]:
    """
    Apply Kirk Franklin-style gospel reharmonization.

    Intensity levels:
    - 'low': Occasional chromatic passing chords
    - 'medium': Backdoor progressions, modal interchange, frequent passing chords
    - 'high': Dense passing diminished, upper structure triads, chromatic bass lines

    Args:
        progression: Original chord progression as (root, quality) tuples
        intensity: 'low', 'medium', or 'high'
        add_passing_chords: Whether to add chromatic passing chords

    Returns:
        Reharmonized progression
    """
    result = []

    for i, (root, quality) in enumerate(progression):
        # Add original chord
        result.append((root, quality))

        # Add passing chords before next chord
        if i < len(progression) - 1 and add_passing_chords:
            next_root, next_quality = progression[i + 1]

            root_sem = note_to_semitone(root)
            next_sem = note_to_semitone(next_root)
            interval = (next_sem - root_sem) % 12

            # Chromatic approach (all intensities)
            if intensity in ['low', 'medium', 'high']:
                approach_sem = (next_sem - 1) % 12
                approach_root = semitone_to_note(approach_sem, prefer_sharps=False)
                result.append((approach_root, '7'))

            # Diminished passing (medium and high)
            if intensity in ['medium', 'high'] and interval == 2:
                passing_sem = (root_sem + 1) % 12
                passing_root = semitone_to_note(passing_sem)
                result.append((passing_root, 'dim7'))

            # Secondary dominant (high intensity)
            if intensity == 'high':
                secondary_dom_sem = (next_sem + 7) % 12
                secondary_dom_root = semitone_to_note(secondary_dom_sem)
                result.append((secondary_dom_root, '7'))

    return result


def optimize_for_singability(
    progression: List[Tuple[str, str]],
    vocal_range: Tuple[int, int] = (55, 76)  # G3 to E5
) -> List[Tuple[str, str]]:
    """
    Optimize reharmonization for vocal singability (gospel/worship).

    Args:
        progression: Chord progression
        vocal_range: (min_midi, max_midi) for comfortable singing

    Returns:
        Optimized progression (simplified if needed)
    """
    # For gospel, prefer:
    # - Stepwise bass motion
    # - Clear melodic line support
    # - Not too many chromatic changes

    # This is a simplified version - full implementation would analyze melody
    return progression


# ============================================================================
# CLASSICAL STRATEGIES
# ============================================================================

def reharmonize_classical_cadence(
    key: str,
    cadence_type: str = 'authentic',
    period: str = 'romantic'
) -> List[Tuple[str, str]]:
    """
    Generate classical cadence reharmonizations.

    Cadence types:
    - 'authentic': V - I
    - 'plagal': IV - I
    - 'half': I/ii/IV - V
    - 'deceptive': V - vi

    Periods:
    - 'baroque': Simpler harmony, less chromaticism
    - 'classical': Clear functional harmony
    - 'romantic': Modal interchange, chromatic mediants
    - 'late_romantic': Extended harmony, altered chords

    Args:
        key: Tonic key
        cadence_type: Type of cadence
        period: Historical period style

    Returns:
        Cadence progression
    """
    key_sem = note_to_semitone(key)

    I_root = key
    IV_root = semitone_to_note((key_sem + 5) % 12)
    V_root = semitone_to_note((key_sem + 7) % 12)
    vi_root = semitone_to_note((key_sem + 9) % 12)
    ii_root = semitone_to_note((key_sem + 2) % 12)

    if cadence_type == 'authentic':
        if period == 'baroque':
            return [(V_root, ''), (I_root, '')]
        elif period == 'classical':
            return [(V_root, '7'), (I_root, '')]
        elif period == 'romantic':
            # Add leading tone diminished
            vii_root = semitone_to_note((key_sem + 11) % 12)
            return [(vii_root, 'dim7'), (V_root, '7'), (I_root, '')]
        else:  # late_romantic
            # Altered dominant
            return [(V_root, '7b9'), (I_root, '')]

    elif cadence_type == 'plagal':
        if period in ['baroque', 'classical']:
            return [(IV_root, ''), (I_root, '')]
        else:  # romantic/late_romantic
            # Minor subdominant (modal interchange)
            return [(IV_root, 'm'), (I_root, '')]

    elif cadence_type == 'half':
        if period in ['baroque', 'classical']:
            return [(ii_root, ''), (V_root, '7')]
        else:  # romantic
            # Approach V with secondary dominant
            return [(ii_root, 'm7'), (V_root, '7')]

    elif cadence_type == 'deceptive':
        return [(V_root, '7'), (vi_root, 'm')]

    return [(V_root, '7'), (I_root, '')]


# ============================================================================
# NEO-SOUL STRATEGIES
# ============================================================================

def reharmonize_neosoul_progression(
    progression: List[Tuple[str, str]],
    key: str,
    use_negative_harmony: bool = True,
    use_chromatic_mediants: bool = True
) -> List[Dict[str, Any]]:
    """
    Apply neo-soul reharmonization techniques.

    Features:
    - Negative harmony transformations
    - Chromatic mediant relationships
    - Extended/altered chords
    - Unexpected modulations

    Args:
        progression: Original progression
        key: Tonic key
        use_negative_harmony: Apply negative harmony
        use_chromatic_mediants: Use chromatic mediant relationships

    Returns:
        List of chord options with metadata
    """
    result = []

    for root, quality in progression:
        options = [(root, quality)]  # Original

        # Negative harmony option
        if use_negative_harmony:
            try:
                from app.theory.chord_substitutions import get_negative_harmony_chord
                neg_chord = get_negative_harmony_chord(root, quality, key)
                if neg_chord:
                    options.append(neg_chord)
            except:
                pass

        # Chromatic mediant option
        if use_chromatic_mediants:
            mediants = _get_chromatic_mediants(root, quality)
            options.extend(mediants[:1])  # Add one mediant option

        result.append({
            'original': (root, quality),
            'options': options,
            'technique': 'neosoul'
        })

    return result


def _get_chromatic_mediants(root: str, quality: str) -> List[Tuple[str, str]]:
    """Get chromatic mediant chords"""
    root_sem = note_to_semitone(root)

    # Major/minor third relationships
    mediants = []

    # Up minor third (if major chord)
    if 'm' not in quality:
        mediant_up = semitone_to_note((root_sem + 3) % 12)
        mediants.append((mediant_up, ''))

    # Down major third (if minor chord)
    if 'm' in quality:
        mediant_down = semitone_to_note((root_sem - 4) % 12, prefer_sharps=False)
        mediants.append((mediant_down, ''))

    return mediants


# ============================================================================
# BLUES STRATEGIES
# ============================================================================

def reharmonize_blues_turnaround(
    key: str,
    style: str = 'traditional'
) -> List[Tuple[str, str]]:
    """
    Generate blues turnaround reharmonizations.

    Styles:
    - 'traditional': I - vi - ii - V
    - 'chromatic': I - I7/V - IV - #IVdim - I/V - V
    - 'jazz_blues': I - III7 - vi - VI7 - ii - V - I
    - 'gospel_blues': I - bVII7 - IV - iv - I

    Args:
        key: Tonic key
        style: Turnaround style

    Returns:
        Turnaround progression
    """
    key_sem = note_to_semitone(key)

    I_root = key
    IV_root = semitone_to_note((key_sem + 5) % 12)
    V_root = semitone_to_note((key_sem + 7) % 12)
    vi_root = semitone_to_note((key_sem + 9) % 12)
    ii_root = semitone_to_note((key_sem + 2) % 12)

    if style == 'traditional':
        return [
            (I_root, '7'),
            (vi_root, '7'),
            (ii_root, '7'),
            (V_root, '7')
        ]

    elif style == 'chromatic':
        # Chromatic bass line
        return [
            (I_root, '7'),
            (semitone_to_note((key_sem + 7) % 12), '7/5'),  # I7/V
            (IV_root, '7'),
            (semitone_to_note((key_sem + 6) % 12), 'dim7'),  # #IVdim
            (I_root, '7'),
            (V_root, '7')
        ]

    elif style == 'jazz_blues':
        III_root = semitone_to_note((key_sem + 4) % 12)
        VI_root = semitone_to_note((key_sem + 9) % 12)
        return [
            (I_root, '7'),
            (III_root, '7'),
            (vi_root, 'm7'),
            (VI_root, '7'),
            (ii_root, 'm7'),
            (V_root, '7'),
            (I_root, '7')
        ]

    elif style == 'gospel_blues':
        bVII_root = semitone_to_note((key_sem - 2) % 12, prefer_sharps=False)
        iv_root = semitone_to_note((key_sem + 5) % 12)
        return [
            (I_root, '7'),
            (bVII_root, '7'),
            (IV_root, '7'),
            (iv_root, 'm7'),
            (I_root, '7')
        ]

    return [(I_root, '7'), (vi_root, '7'), (ii_root, '7'), (V_root, '7')]


# ============================================================================
# GENRE-SPECIFIC CONSTRAINTS
# ============================================================================

def get_genre_specific_constraints(genre: str) -> Dict[str, Any]:
    """
    Get genre-specific constraints and preferences.

    Returns:
        Dict with:
        - allowed_techniques: List of technique names
        - max_chromatic_density: 0-1 (how chromatic)
        - prefer_smooth_voice_leading: bool
        - max_reharmonization_distance: int (Tonnetz distance)
    """
    constraints = {
        'jazz': {
            'allowed_techniques': [
                'modal_interchange', 'diatonic_substitution',
                'tritone_substitution', 'coltrane_changes',
                'negative_harmony', 'common_tone_diminished',
                'chromatic_approach', 'diminished_passing'
            ],
            'max_chromatic_density': 0.8,
            'prefer_smooth_voice_leading': True,
            'max_reharmonization_distance': 4,
        },
        'gospel': {
            'allowed_techniques': [
                'diatonic_substitution', 'chromatic_approach',
                'diminished_passing', 'backdoor', 'modal_interchange'
            ],
            'max_chromatic_density': 0.6,
            'prefer_smooth_voice_leading': True,
            'max_reharmonization_distance': 3,
        },
        'classical': {
            'allowed_techniques': [
                'modal_interchange', 'diatonic_substitution',
                'secondary_dominant'
            ],
            'max_chromatic_density': 0.4,
            'prefer_smooth_voice_leading': True,
            'max_reharmonization_distance': 2,
        },
        'neosoul': {
            'allowed_techniques': [
                'negative_harmony', 'modal_interchange',
                'chromatic_mediant', 'extended_chords'
            ],
            'max_chromatic_density': 0.7,
            'prefer_smooth_voice_leading': False,  # Can be surprising
            'max_reharmonization_distance': 5,
        },
        'blues': {
            'allowed_techniques': [
                'diatonic_substitution', 'chromatic_approach',
                'diminished_passing'
            ],
            'max_chromatic_density': 0.5,
            'prefer_smooth_voice_leading': False,  # Blues has character
            'max_reharmonization_distance': 2,
        },
    }

    return constraints.get(genre, constraints['jazz'])


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'reharmonize_ii_V_I_jazz',
    'reharmonize_gospel_progression',
    'reharmonize_classical_cadence',
    'reharmonize_neosoul_progression',
    'reharmonize_blues_turnaround',
    'get_genre_specific_constraints',
    'optimize_for_singability',
]
