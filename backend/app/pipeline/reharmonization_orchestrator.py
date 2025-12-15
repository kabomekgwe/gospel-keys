"""
Reharmonization Orchestrator (Phase 6)

Intelligent orchestration layer that integrates:
- Phase 4: All 7 chord substitution categories
- Phase 5: Voice leading analysis and Neo-Riemannian filtering
- Multi-criteria scoring and ranking
- Genre-specific constraints

This module completes the missing `get_all_reharmonizations_for_chord()` function
that reharmonization_engine.py's async wrapper calls.
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import asyncio
from functools import lru_cache

from app.theory.interval_utils import note_to_semitone, semitone_to_note


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ReharmonizationOption:
    """A single reharmonization option with metadata"""
    new_root: str
    new_quality: str
    technique: str  # Which Phase 4 category
    score: float = 0.0  # Combined quality score (0-1)

    # Metadata
    source_mode: Optional[str] = None  # For modal interchange
    explanation: str = ""

    # Scoring breakdown
    voice_leading_score: float = 0.0
    harmonic_function_score: float = 0.0
    neo_riemannian_score: float = 0.0
    genre_score: float = 0.0
    complexity_score: float = 0.0

    # Voice leading details
    voice_leading_smoothness: float = 0.0
    common_tones: int = 0
    total_movement: int = 0
    neo_riemannian_distance: int = 0

    # Harmonic function
    harmonic_function: str = ""  # T, S, or D
    preserves_function: bool = False


# ============================================================================
# CORE ORCHESTRATION
# ============================================================================

def get_all_reharmonizations_for_chord(
    chord_dict: Dict,
    key: str,
    previous_chord: Optional[Tuple[str, str]] = None,
    next_chord: Optional[Tuple[str, str]] = None,
    genre: str = "jazz",
    max_options: int = 10,
    min_score: float = 0.5
) -> List[Dict[str, Any]]:
    """
    CRITICAL MISSING FUNCTION - Main orchestration entry point.

    Gathers reharmonization options from all 7 Phase 4 categories,
    scores them using Phase 5 analysis, and returns ranked results.

    Args:
        chord_dict: Dict with 'root' and 'quality' keys
        key: Musical key context
        previous_chord: Optional (root, quality) tuple for voice leading analysis
        next_chord: Optional (root, quality) tuple for voice leading analysis
        genre: Musical genre for style constraints
        max_options: Maximum number of options to return
        min_score: Minimum quality score threshold (0-1)

    Returns:
        List of dicts with reharmonization options, sorted by score
    """
    root = chord_dict.get('root', '')
    quality = chord_dict.get('quality', '')

    if not root:
        return []

    # Collect options from all Phase 4 categories
    options = []

    # 1. Modal Interchange
    options.extend(_get_modal_interchange_options(root, quality, key, genre))

    # 2. Diatonic Substitution
    options.extend(_get_diatonic_substitution_options(root, quality, key))

    # 3. Negative Harmony (if genre allows)
    if genre in ['jazz', 'neosoul']:
        options.extend(_get_negative_harmony_options(root, quality, key))

    # 4. Tritone Substitution (for dominant 7th chords)
    options.extend(_get_tritone_substitution_options(root, quality))

    # 5. Common Tone Diminished
    options.extend(_get_common_tone_diminished_options(root, quality))

    # 6. Passing/Approach Chords (if next_chord provided)
    if next_chord:
        options.extend(_get_passing_chord_options(root, quality, next_chord, genre))

    # 7. Coltrane Changes (for jazz genre)
    if genre == 'jazz':
        options.extend(_get_coltrane_changes_options(root, quality))

    # Score all options
    for option in options:
        _score_reharmonization_option(
            option,
            original=(root, quality),
            previous_chord=previous_chord,
            next_chord=next_chord,
            key=key,
            genre=genre
        )

    # Filter by minimum score
    options = [opt for opt in options if opt.score >= min_score]

    # Rank by score (descending)
    options.sort(key=lambda x: x.score, reverse=True)

    # Limit results
    options = options[:max_options]

    # Convert to dict format for API
    return [_option_to_dict(opt) for opt in options]


def _option_to_dict(option: ReharmonizationOption) -> Dict[str, Any]:
    """Convert ReharmonizationOption to API-friendly dict"""
    return {
        'new_root': option.new_root,
        'new_quality': option.new_quality,
        'technique': option.technique,
        'score': round(option.score, 3),
        'explanation': option.explanation,
        'source_mode': option.source_mode,

        # Scoring breakdown
        'scores': {
            'voice_leading': round(option.voice_leading_score, 3),
            'harmonic_function': round(option.harmonic_function_score, 3),
            'neo_riemannian': round(option.neo_riemannian_score, 3),
            'genre': round(option.genre_score, 3),
            'complexity': round(option.complexity_score, 3),
        },

        # Voice leading details
        'voice_leading': {
            'smoothness': round(option.voice_leading_smoothness, 3),
            'common_tones': option.common_tones,
            'total_movement': option.total_movement,
        },

        # Neo-Riemannian details
        'neo_riemannian_distance': option.neo_riemannian_distance,

        # Harmonic function
        'harmonic_function': option.harmonic_function,
        'preserves_function': option.preserves_function,
    }


# ============================================================================
# PHASE 4 INTEGRATION - GATHER OPTIONS FROM ALL 7 CATEGORIES
# ============================================================================

def _get_modal_interchange_options(
    root: str,
    quality: str,
    key: str,
    genre: str
) -> List[ReharmonizationOption]:
    """Get modal interchange options from Phase 4"""
    options = []

    try:
        from app.theory.chord_substitutions import get_all_modal_borrowings

        borrowed = get_all_modal_borrowings(key, include_modes=['dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian'])

        for mode, chords in borrowed.items():
            for chord_data in chords[:2]:  # Limit to 2 per mode
                # Handle both dict format and tuple format
                if isinstance(chord_data, dict):
                    new_root = chord_data.get('root', '')
                    new_quality = chord_data.get('quality', '')
                elif isinstance(chord_data, (tuple, list)) and len(chord_data) >= 2:
                    new_root, new_quality = chord_data[0], chord_data[1]
                else:
                    continue

                # Skip empty roots
                if not new_root:
                    continue

                options.append(ReharmonizationOption(
                    new_root=new_root,
                    new_quality=new_quality,
                    technique='modal_interchange',
                    source_mode=mode,
                    explanation=f"Borrowed from {mode} mode"
                ))
    except (ImportError, Exception) as e:
        # Phase 4 not available yet, use basic implementation
        pass

    return options


def _get_diatonic_substitution_options(
    root: str,
    quality: str,
    key: str
) -> List[ReharmonizationOption]:
    """Get diatonic substitution options from Phase 4"""
    options = []

    try:
        from app.theory.chord_substitutions import get_functional_substitutes

        substitutes = get_functional_substitutes(root, quality, key)

        for sub in substitutes:
            # Handle tuple format
            if isinstance(sub, (tuple, list)) and len(sub) >= 2:
                new_root, new_quality = sub[0], sub[1]
            else:
                continue

            options.append(ReharmonizationOption(
                new_root=new_root,
                new_quality=new_quality,
                technique='diatonic_substitution',
                explanation=f"Functional substitute: same harmonic role"
            ))
    except (ImportError, Exception):
        # Fallback: basic diatonic substitutes
        key_sem = note_to_semitone(key)
        root_sem = note_to_semitone(root)
        interval = (root_sem - key_sem) % 12

        # I ↔ vi
        if interval == 0:
            options.append(ReharmonizationOption(
                new_root=semitone_to_note((key_sem + 9) % 12),
                new_quality='m7',
                technique='diatonic_substitution',
                explanation="vi chord (relative minor)"
            ))

    return options


def _get_negative_harmony_options(
    root: str,
    quality: str,
    key: str
) -> List[ReharmonizationOption]:
    """Get negative harmony options from Phase 4"""
    options = []

    try:
        from app.theory.chord_substitutions import get_negative_harmony_chord

        neg_chord = get_negative_harmony_chord(root, quality, key)

        if neg_chord and isinstance(neg_chord, (tuple, list)) and len(neg_chord) >= 2:
            options.append(ReharmonizationOption(
                new_root=neg_chord[0],
                new_quality=neg_chord[1],
                technique='negative_harmony',
                explanation="Negative harmony transformation"
            ))
    except (ImportError, Exception):
        pass

    return options


def _get_tritone_substitution_options(
    root: str,
    quality: str
) -> List[ReharmonizationOption]:
    """Get tritone substitution for dominant 7th chords"""
    options = []

    # Only for dominant 7th chords
    if '7' in quality and 'maj' not in quality and 'm' not in quality:
        tritone_sem = (note_to_semitone(root) + 6) % 12
        tritone_root = semitone_to_note(tritone_sem, prefer_sharps=False)

        options.append(ReharmonizationOption(
            new_root=tritone_root,
            new_quality='7',
            technique='tritone_substitution',
            explanation=f"Tritone sub: {root}7 and {tritone_root}7 share the same tritone"
        ))

    return options


def _get_common_tone_diminished_options(
    root: str,
    quality: str
) -> List[ReharmonizationOption]:
    """Get common tone diminished options from Phase 4"""
    options = []

    try:
        from app.theory.chord_substitutions import get_common_tone_dim7

        dim_chord = get_common_tone_dim7(root, quality)

        if dim_chord and isinstance(dim_chord, (tuple, list)) and len(dim_chord) >= 2:
            options.append(ReharmonizationOption(
                new_root=dim_chord[0],
                new_quality=dim_chord[1],
                technique='common_tone_diminished',
                explanation="Common tone diminished 7th"
            ))
    except (ImportError, Exception):
        pass

    return options


def _get_passing_chord_options(
    root: str,
    quality: str,
    next_chord: Tuple[str, str],
    genre: str
) -> List[ReharmonizationOption]:
    """Get passing/approach chord options"""
    options = []
    next_root, next_quality = next_chord

    # Chromatic approach
    approach_sem = (note_to_semitone(next_root) - 1) % 12
    approach_root = semitone_to_note(approach_sem, prefer_sharps=False)

    options.append(ReharmonizationOption(
        new_root=approach_root,
        new_quality='7',
        technique='chromatic_approach',
        explanation=f"Chromatic approach to {next_root}"
    ))

    # Diminished passing (if appropriate)
    root_sem = note_to_semitone(root)
    next_sem = note_to_semitone(next_root)
    interval = (next_sem - root_sem) % 12

    if interval == 2:  # Whole step apart
        passing_sem = (root_sem + 1) % 12
        passing_root = semitone_to_note(passing_sem)

        options.append(ReharmonizationOption(
            new_root=passing_root,
            new_quality='dim7',
            technique='diminished_passing',
            explanation="Chromatic diminished passing chord"
        ))

    return options


def _get_coltrane_changes_options(
    root: str,
    quality: str
) -> List[ReharmonizationOption]:
    """Get Coltrane changes options from Phase 4"""
    options = []

    try:
        from app.theory.chord_substitutions import apply_coltrane_changes

        coltrane_chords = apply_coltrane_changes(root, quality)

        for chord in coltrane_chords[:2]:  # Limit to prevent overwhelming
            if isinstance(chord, (tuple, list)) and len(chord) >= 2:
                options.append(ReharmonizationOption(
                    new_root=chord[0],
                    new_quality=chord[1],
                    technique='coltrane_changes',
                    explanation="Coltrane changes (major thirds cycle)"
                ))
    except (ImportError, Exception):
        pass

    return options


# ============================================================================
# SCORING SYSTEM - PHASE 5 INTEGRATION
# ============================================================================

def _score_reharmonization_option(
    option: ReharmonizationOption,
    original: Tuple[str, str],
    previous_chord: Optional[Tuple[str, str]],
    next_chord: Optional[Tuple[str, str]],
    key: str,
    genre: str
) -> None:
    """
    Score a reharmonization option using multi-criteria analysis.

    Modifies option in-place with scores.
    """
    # Weight configuration (can be genre-specific)
    weights = {
        'voice_leading': 0.35,
        'harmonic_function': 0.25,
        'neo_riemannian': 0.20,
        'genre': 0.15,
        'complexity': 0.05
    }

    # 1. Voice leading score (Phase 5 integration)
    option.voice_leading_score = _calculate_voice_leading_score(
        original,
        (option.new_root, option.new_quality),
        previous_chord,
        next_chord
    )

    # 2. Harmonic function score
    option.harmonic_function_score = _calculate_harmonic_function_score(
        original,
        (option.new_root, option.new_quality),
        key
    )

    # 3. Neo-Riemannian score (Phase 5 integration)
    option.neo_riemannian_score = _calculate_neo_riemannian_score(
        original,
        (option.new_root, option.new_quality)
    )

    # 4. Genre appropriateness score
    option.genre_score = _calculate_genre_score(option.technique, genre)

    # 5. Complexity score (simpler is better for most contexts)
    option.complexity_score = _calculate_complexity_score(option.technique)

    # Combined weighted score
    option.score = (
        weights['voice_leading'] * option.voice_leading_score +
        weights['harmonic_function'] * option.harmonic_function_score +
        weights['neo_riemannian'] * option.neo_riemannian_score +
        weights['genre'] * option.genre_score +
        weights['complexity'] * option.complexity_score
    )


def _calculate_voice_leading_score(
    original: Tuple[str, str],
    new_chord: Tuple[str, str],
    previous_chord: Optional[Tuple[str, str]],
    next_chord: Optional[Tuple[str, str]]
) -> float:
    """
    Calculate voice leading quality score (0-1).

    Uses Phase 5 voice_leading_analyzer if available.
    """
    try:
        from app.pipeline.voice_leading_analyzer import analyze_voice_leading

        scores = []

        # Analyze transition from previous chord to new chord
        if previous_chord:
            analysis = analyze_voice_leading(
                previous_chord[0], previous_chord[1],
                new_chord[0], new_chord[1]
            )
            if analysis and 'smoothness' in analysis:
                scores.append(analysis['smoothness'])

        # Analyze transition from new chord to next chord
        if next_chord:
            analysis = analyze_voice_leading(
                new_chord[0], new_chord[1],
                next_chord[0], next_chord[1]
            )
            if analysis and 'smoothness' in analysis:
                scores.append(analysis['smoothness'])

        # If no context, analyze original to new
        if not scores:
            analysis = analyze_voice_leading(
                original[0], original[1],
                new_chord[0], new_chord[1]
            )
            if analysis and 'smoothness' in analysis:
                return analysis['smoothness']

        return sum(scores) / len(scores) if scores else 0.5

    except (ImportError, Exception):
        # Fallback: simple common tone analysis
        return _calculate_simple_voice_leading_score(original, new_chord)


def _calculate_simple_voice_leading_score(
    original: Tuple[str, str],
    new_chord: Tuple[str, str]
) -> float:
    """Simple voice leading score based on semitone distance"""
    # Defensive: Extract root from potentially malformed data
    def extract_root(root_str: str) -> str:
        """Extract just the note name from a string like 'D#m' or 'D#'"""
        # If root contains quality markers (m, M, maj, min, dim, aug, 7, etc), strip them
        import re
        # Match note name: letter + optional accidental (# or b)
        match = re.match(r'^([A-G][#b]?)', root_str)
        if match:
            return match.group(1)
        return root_str

    root1 = extract_root(original[0])
    root2 = extract_root(new_chord[0])

    root1_sem = note_to_semitone(root1)
    root2_sem = note_to_semitone(root2)

    distance = min(abs(root2_sem - root1_sem), 12 - abs(root2_sem - root1_sem))

    # Closer = better (exponential decay)
    return max(0.0, 1.0 - (distance / 12.0))


def _calculate_harmonic_function_score(
    original: Tuple[str, str],
    new_chord: Tuple[str, str],
    key: str
) -> float:
    """
    Calculate harmonic function compatibility score (0-1).

    Uses harmonic_function_analyzer if available.
    """
    try:
        from app.pipeline.harmonic_function_analyzer import analyze_chord_function

        orig_function = analyze_chord_function(original[0], original[1], key)
        new_function = analyze_chord_function(new_chord[0], new_chord[1], key)

        # Same function = highest score
        if orig_function == new_function:
            return 1.0

        # T-S or S-D transitions are good
        if (orig_function == 'T' and new_function == 'S') or \
           (orig_function == 'S' and new_function == 'D'):
            return 0.7

        # Other transitions less ideal
        return 0.4

    except (ImportError, Exception):
        # Fallback: assume moderate compatibility
        return 0.6


def _calculate_neo_riemannian_score(
    original: Tuple[str, str],
    new_chord: Tuple[str, str]
) -> float:
    """
    Calculate Neo-Riemannian parsimony score (0-1).

    Uses Phase 5 voice_leading_neo_riemannian if available.
    """
    try:
        from app.theory.voice_leading_neo_riemannian import calculate_tonnetz_distance

        distance = calculate_tonnetz_distance(
            original[0], original[1],
            new_chord[0], new_chord[1]
        )

        # Exponential decay: distance 1 = 1.0, distance 2 = 0.8, distance 3 = 0.5
        return max(0.0, 1.0 - (distance - 1) * 0.3)

    except (ImportError, Exception):
        # Fallback: use simple semitone distance
        return 0.5


def _calculate_genre_score(technique: str, genre: str) -> float:
    """Calculate genre appropriateness score (0-1)"""
    genre_preferences = {
        'jazz': {
            'modal_interchange': 0.9,
            'diatonic_substitution': 0.8,
            'negative_harmony': 0.7,
            'tritone_substitution': 1.0,
            'coltrane_changes': 1.0,
            'common_tone_diminished': 0.8,
            'chromatic_approach': 0.9,
            'diminished_passing': 0.9,
        },
        'gospel': {
            'modal_interchange': 0.7,
            'diatonic_substitution': 0.9,
            'chromatic_approach': 1.0,
            'diminished_passing': 0.9,
            'backdoor': 0.8,
        },
        'classical': {
            'modal_interchange': 1.0,
            'diatonic_substitution': 1.0,
            'secondary_dominant': 0.9,
        },
        'neosoul': {
            'negative_harmony': 1.0,
            'modal_interchange': 0.9,
            'chromatic_mediant': 0.9,
        },
    }

    preferences = genre_preferences.get(genre, {})
    return preferences.get(technique, 0.5)


def _calculate_complexity_score(technique: str) -> float:
    """
    Calculate complexity score (0-1).

    Simpler techniques score higher (more accessible).
    """
    complexity_levels = {
        'diatonic_substitution': 1.0,
        'modal_interchange': 0.8,
        'tritone_substitution': 0.7,
        'chromatic_approach': 0.8,
        'diminished_passing': 0.7,
        'negative_harmony': 0.5,
        'coltrane_changes': 0.4,
        'common_tone_diminished': 0.6,
    }

    return complexity_levels.get(technique, 0.5)


# ============================================================================
# CACHING
# ============================================================================

@lru_cache(maxsize=128)
def _cached_analysis(root: str, quality: str, key: str, context: str) -> Dict:
    """Cache expensive analysis operations"""
    # Placeholder for caching layer
    return {}


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'get_all_reharmonizations_for_chord',
    'ReharmonizationOption',
]
