"""
Reharmonization Quality Metrics (Phase 6)

Multi-criteria evaluation system for reharmonization options:
- Voice leading quality (smoothness, common tones, movement)
- Harmonic function compatibility (T-S-D preservation)
- Neo-Riemannian parsimony (Tonnetz distance)
- Genre appropriateness
- Complexity/accessibility

Provides detailed scoring and human-readable explanations.
"""

from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from app.theory.interval_utils import note_to_semitone, semitone_to_note


# ============================================================================
# SCORING WEIGHTS
# ============================================================================

GENRE_WEIGHTS = {
    'jazz': {
        'voice_leading': 0.30,
        'harmonic_function': 0.25,
        'neo_riemannian': 0.25,
        'genre_appropriateness': 0.15,
        'complexity': 0.05,
    },
    'gospel': {
        'voice_leading': 0.40,
        'harmonic_function': 0.30,
        'neo_riemannian': 0.15,
        'genre_appropriateness': 0.10,
        'complexity': 0.05,
    },
    'classical': {
        'voice_leading': 0.40,
        'harmonic_function': 0.35,
        'neo_riemannian': 0.15,
        'genre_appropriateness': 0.05,
        'complexity': 0.05,
    },
    'neosoul': {
        'voice_leading': 0.25,
        'harmonic_function': 0.20,
        'neo_riemannian': 0.30,
        'genre_appropriateness': 0.20,
        'complexity': 0.05,
    },
    'blues': {
        'voice_leading': 0.35,
        'harmonic_function': 0.25,
        'neo_riemannian': 0.15,
        'genre_appropriateness': 0.20,
        'complexity': 0.05,
    },
}


# ============================================================================
# VOICE LEADING QUALITY SCORING
# ============================================================================

def calculate_voice_leading_score(
    original: Tuple[str, str],
    new_chord: Tuple[str, str],
    previous_chord: Optional[Tuple[str, str]] = None,
    next_chord: Optional[Tuple[str, str]] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive voice leading quality score.

    Returns:
        Dict with:
        - score: 0-1 (1 = smoothest)
        - smoothness: 0-1
        - common_tones: int
        - total_movement: int (semitones)
        - has_parallel_fifths: bool
        - has_parallel_octaves: bool
        - explanation: str
    """
    try:
        from app.pipeline.voice_leading_analyzer import analyze_voice_leading

        # Analyze transitions
        analyses = []

        if previous_chord:
            prev_analysis = analyze_voice_leading(
                previous_chord[0], previous_chord[1],
                new_chord[0], new_chord[1]
            )
            if prev_analysis:
                analyses.append(prev_analysis)

        if next_chord:
            next_analysis = analyze_voice_leading(
                new_chord[0], new_chord[1],
                next_chord[0], next_chord[1]
            )
            if next_analysis:
                analyses.append(next_analysis)

        # If no context, analyze original → new
        if not analyses:
            orig_analysis = analyze_voice_leading(
                original[0], original[1],
                new_chord[0], new_chord[1]
            )
            if orig_analysis:
                analyses.append(orig_analysis)

        if analyses:
            # Average smoothness
            smoothness = sum(a.get('smoothness', 0.5) for a in analyses) / len(analyses)
            common_tones = int(sum(a.get('common_tones', 0) for a in analyses) / len(analyses))
            total_movement = int(sum(a.get('total_movement', 0) for a in analyses) / len(analyses))

            # Check for parallel motion issues
            has_parallel_fifths = any(a.get('parallel_fifths', False) for a in analyses)
            has_parallel_octaves = any(a.get('parallel_octaves', False) for a in analyses)

            # Penalty for parallel motion
            penalty = 0.0
            if has_parallel_fifths:
                penalty += 0.2
            if has_parallel_octaves:
                penalty += 0.1

            score = max(0.0, smoothness - penalty)

            explanation = _generate_voice_leading_explanation(
                smoothness, common_tones, total_movement,
                has_parallel_fifths, has_parallel_octaves
            )

            return {
                'score': score,
                'smoothness': smoothness,
                'common_tones': common_tones,
                'total_movement': total_movement,
                'has_parallel_fifths': has_parallel_fifths,
                'has_parallel_octaves': has_parallel_octaves,
                'explanation': explanation
            }

    except (ImportError, Exception):
        pass

    # Fallback: simple semitone distance analysis
    return _calculate_simple_voice_leading(original, new_chord)


def _calculate_simple_voice_leading(
    original: Tuple[str, str],
    new_chord: Tuple[str, str]
) -> Dict[str, Any]:
    """Simple voice leading analysis based on root movement"""
    root1_sem = note_to_semitone(original[0])
    root2_sem = note_to_semitone(new_chord[0])

    distance = min(abs(root2_sem - root1_sem), 12 - abs(root2_sem - root1_sem))

    # Closer roots = smoother
    smoothness = max(0.0, 1.0 - (distance / 12.0))

    return {
        'score': smoothness,
        'smoothness': smoothness,
        'common_tones': 0,
        'total_movement': distance,
        'has_parallel_fifths': False,
        'has_parallel_octaves': False,
        'explanation': f"Root movement: {distance} semitones"
    }


def _generate_voice_leading_explanation(
    smoothness: float,
    common_tones: int,
    total_movement: int,
    has_parallel_fifths: bool,
    has_parallel_octaves: bool
) -> str:
    """Generate human-readable voice leading explanation"""
    parts = []

    if smoothness >= 0.8:
        parts.append("Very smooth voice leading")
    elif smoothness >= 0.6:
        parts.append("Moderately smooth voice leading")
    else:
        parts.append("Dramatic voice leading")

    if common_tones > 0:
        parts.append(f"{common_tones} common tone{'s' if common_tones > 1 else ''}")

    parts.append(f"{total_movement} semitones total movement")

    if has_parallel_fifths:
        parts.append("⚠️ parallel fifths")
    if has_parallel_octaves:
        parts.append("⚠️ parallel octaves")

    return ", ".join(parts)


# ============================================================================
# HARMONIC FUNCTION SCORING
# ============================================================================

def calculate_harmonic_function_score(
    original: Tuple[str, str],
    new_chord: Tuple[str, str],
    key: str
) -> Dict[str, Any]:
    """
    Calculate harmonic function compatibility score.

    Returns:
        Dict with:
        - score: 0-1
        - original_function: 'T', 'S', or 'D'
        - new_function: 'T', 'S', or 'D'
        - preserves_function: bool
        - explanation: str
    """
    try:
        from app.pipeline.harmonic_function_analyzer import analyze_chord_function

        orig_function = analyze_chord_function(original[0], original[1], key)
        new_function = analyze_chord_function(new_chord[0], new_chord[1], key)

        preserves_function = (orig_function == new_function)

        # Scoring rules
        if preserves_function:
            score = 1.0
            explanation = f"Preserves {orig_function} function"
        elif _is_valid_progression(orig_function, new_function):
            score = 0.7
            explanation = f"Valid progression: {orig_function} → {new_function}"
        else:
            score = 0.4
            explanation = f"Weak progression: {orig_function} → {new_function}"

        return {
            'score': score,
            'original_function': orig_function,
            'new_function': new_function,
            'preserves_function': preserves_function,
            'explanation': explanation
        }

    except (ImportError, Exception):
        # Fallback
        return {
            'score': 0.6,
            'original_function': 'Unknown',
            'new_function': 'Unknown',
            'preserves_function': False,
            'explanation': 'Function analysis unavailable'
        }


def _is_valid_progression(from_func: str, to_func: str) -> bool:
    """Check if harmonic function progression is valid"""
    valid_progressions = [
        ('T', 'S'),  # Tonic to Subdominant
        ('S', 'D'),  # Subdominant to Dominant
        ('D', 'T'),  # Dominant to Tonic (resolution)
        ('T', 'D'),  # Tonic to Dominant (acceptable)
    ]
    return (from_func, to_func) in valid_progressions


# ============================================================================
# NEO-RIEMANNIAN SCORING
# ============================================================================

def calculate_neo_riemannian_score(
    original: Tuple[str, str],
    new_chord: Tuple[str, str]
) -> Dict[str, Any]:
    """
    Calculate Neo-Riemannian parsimony score.

    Returns:
        Dict with:
        - score: 0-1 (1 = most parsimonious)
        - tonnetz_distance: int
        - plr_path: List[str] (if available)
        - is_parsimonious: bool (distance ≤ 2)
        - explanation: str
    """
    try:
        from app.theory.voice_leading_neo_riemannian import (
            calculate_tonnetz_distance,
            get_tonnetz_path
        )

        distance = calculate_tonnetz_distance(
            original[0], original[1],
            new_chord[0], new_chord[1]
        )

        try:
            path = get_tonnetz_path(
                original[0], original[1],
                new_chord[0], new_chord[1],
                max_steps=4
            )
        except:
            path = []

        # Scoring: exponential decay based on distance
        # Distance 1 = 1.0, Distance 2 = 0.8, Distance 3 = 0.5, Distance 4+ = 0.3
        if distance == 1:
            score = 1.0
        elif distance == 2:
            score = 0.8
        elif distance == 3:
            score = 0.5
        else:
            score = max(0.0, 0.3 - (distance - 4) * 0.1)

        is_parsimonious = (distance <= 2)

        explanation = _generate_neo_riemannian_explanation(distance, path, is_parsimonious)

        return {
            'score': score,
            'tonnetz_distance': distance,
            'plr_path': path if path else [],
            'is_parsimonious': is_parsimonious,
            'explanation': explanation
        }

    except (ImportError, Exception):
        # Fallback: assume moderate parsimony
        return {
            'score': 0.5,
            'tonnetz_distance': 0,
            'plr_path': [],
            'is_parsimonious': False,
            'explanation': 'Neo-Riemannian analysis unavailable'
        }


def _generate_neo_riemannian_explanation(
    distance: int,
    path: list,
    is_parsimonious: bool
) -> str:
    """Generate explanation for Neo-Riemannian analysis"""
    if is_parsimonious:
        if distance == 1:
            transformation = path[0] if path else "single"
            return f"Highly parsimonious ({transformation} transformation, ≤2 semitones)"
        else:
            return f"Parsimonious (Tonnetz distance: {distance})"
    else:
        return f"Moderate parsimony (Tonnetz distance: {distance})"


# ============================================================================
# GENRE APPROPRIATENESS SCORING
# ============================================================================

def calculate_genre_appropriateness_score(
    technique: str,
    genre: str
) -> Dict[str, Any]:
    """
    Calculate genre appropriateness score.

    Returns:
        Dict with:
        - score: 0-1
        - explanation: str
    """
    genre_preferences = {
        'jazz': {
            'modal_interchange': (0.9, "Common in modern jazz"),
            'diatonic_substitution': (0.8, "Standard jazz practice"),
            'negative_harmony': (0.7, "Contemporary jazz harmony"),
            'tritone_substitution': (1.0, "Classic jazz technique"),
            'coltrane_changes': (1.0, "Advanced jazz harmony"),
            'common_tone_diminished': (0.8, "Jazz passing chord"),
            'chromatic_approach': (0.9, "Essential jazz technique"),
            'diminished_passing': (0.9, "Jazz chromaticism"),
        },
        'gospel': {
            'modal_interchange': (0.7, "Used in contemporary gospel"),
            'diatonic_substitution': (0.9, "Gospel standard"),
            'chromatic_approach': (1.0, "Gospel signature sound"),
            'diminished_passing': (0.9, "Gospel passing chord"),
            'backdoor': (0.8, "Gospel resolution"),
        },
        'classical': {
            'modal_interchange': (1.0, "Romantic era technique"),
            'diatonic_substitution': (1.0, "Classical harmony"),
            'secondary_dominant': (0.9, "Classical chromaticism"),
        },
        'neosoul': {
            'negative_harmony': (1.0, "Neo-soul signature"),
            'modal_interchange': (0.9, "Modern harmonic color"),
            'chromatic_mediant': (0.9, "Neo-soul progression"),
        },
        'blues': {
            'diatonic_substitution': (0.8, "Blues standard"),
            'chromatic_approach': (0.9, "Blues walk-up"),
            'diminished_passing': (0.8, "Blues passing chord"),
        },
    }

    preferences = genre_preferences.get(genre, {})
    score, explanation = preferences.get(technique, (0.5, "Moderately appropriate"))

    return {
        'score': score,
        'explanation': explanation
    }


# ============================================================================
# COMPLEXITY SCORING
# ============================================================================

def calculate_complexity_score(technique: str) -> Dict[str, Any]:
    """
    Calculate complexity/accessibility score.

    Simpler = higher score (more accessible to listeners).

    Returns:
        Dict with:
        - score: 0-1 (1 = simplest)
        - complexity_level: str
        - explanation: str
    """
    complexity_levels = {
        # Simple (1.0)
        'diatonic_substitution': (1.0, 'simple', 'Easy to hear and understand'),

        # Moderate (0.7-0.9)
        'modal_interchange': (0.8, 'moderate', 'Familiar but colorful'),
        'chromatic_approach': (0.8, 'moderate', 'Common passing chord'),
        'tritone_substitution': (0.7, 'moderate', 'Classic substitution'),
        'diminished_passing': (0.7, 'moderate', 'Chromatic passing'),

        # Advanced (0.5-0.6)
        'common_tone_diminished': (0.6, 'advanced', 'Sophisticated harmony'),
        'negative_harmony': (0.5, 'advanced', 'Abstract transformation'),

        # Very Advanced (0.3-0.4)
        'coltrane_changes': (0.4, 'very_advanced', 'Complex modulation'),
    }

    score, level, explanation = complexity_levels.get(
        technique,
        (0.5, 'moderate', 'Moderate complexity')
    )

    return {
        'score': score,
        'complexity_level': level,
        'explanation': explanation
    }


# ============================================================================
# COMBINED SCORING
# ============================================================================

def calculate_combined_score(
    voice_leading_score: float,
    harmonic_function_score: float,
    neo_riemannian_score: float,
    genre_score: float,
    complexity_score: float,
    genre: str = 'jazz'
) -> Dict[str, Any]:
    """
    Calculate weighted combined score.

    Returns:
        Dict with:
        - combined_score: 0-1
        - weights: Dict of weights used
        - breakdown: Dict of individual scores
        - explanation: str
    """
    weights = GENRE_WEIGHTS.get(genre, GENRE_WEIGHTS['jazz'])

    combined = (
        weights['voice_leading'] * voice_leading_score +
        weights['harmonic_function'] * harmonic_function_score +
        weights['neo_riemannian'] * neo_riemannian_score +
        weights['genre_appropriateness'] * genre_score +
        weights['complexity'] * complexity_score
    )

    # Find strongest and weakest aspects
    scores_dict = {
        'voice_leading': voice_leading_score,
        'harmonic_function': harmonic_function_score,
        'neo_riemannian': neo_riemannian_score,
        'genre': genre_score,
        'complexity': complexity_score,
    }

    strongest = max(scores_dict.items(), key=lambda x: x[1])
    weakest = min(scores_dict.items(), key=lambda x: x[1])

    explanation = f"Combined score: {combined:.2f}. Strongest: {strongest[0]} ({strongest[1]:.2f}). Weakest: {weakest[0]} ({weakest[1]:.2f})"

    return {
        'combined_score': combined,
        'weights': weights,
        'breakdown': scores_dict,
        'strongest_aspect': strongest[0],
        'weakest_aspect': weakest[0],
        'explanation': explanation
    }


# ============================================================================
# SCORE EXPLANATION
# ============================================================================

def get_score_explanation(
    voice_leading: Dict,
    harmonic_function: Dict,
    neo_riemannian: Dict,
    genre: Dict,
    complexity: Dict,
    combined: Dict
) -> str:
    """
    Generate comprehensive human-readable explanation of scores.

    Args:
        voice_leading: Voice leading score dict
        harmonic_function: Harmonic function score dict
        neo_riemannian: Neo-Riemannian score dict
        genre: Genre score dict
        complexity: Complexity score dict
        combined: Combined score dict

    Returns:
        Formatted explanation string
    """
    lines = []

    # Overall
    lines.append(f"Overall Quality: {combined['combined_score']:.1%}")
    lines.append("")

    # Voice leading
    lines.append(f"Voice Leading ({voice_leading['score']:.1%}): {voice_leading.get('explanation', '')}")

    # Harmonic function
    lines.append(f"Harmonic Function ({harmonic_function['score']:.1%}): {harmonic_function.get('explanation', '')}")

    # Neo-Riemannian
    lines.append(f"Neo-Riemannian ({neo_riemannian['score']:.1%}): {neo_riemannian.get('explanation', '')}")

    # Genre
    lines.append(f"Genre Fit ({genre['score']:.1%}): {genre.get('explanation', '')}")

    # Complexity
    lines.append(f"Accessibility ({complexity['score']:.1%}): {complexity.get('explanation', '')}")

    return "\n".join(lines)


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'calculate_voice_leading_score',
    'calculate_harmonic_function_score',
    'calculate_neo_riemannian_score',
    'calculate_genre_appropriateness_score',
    'calculate_complexity_score',
    'calculate_combined_score',
    'get_score_explanation',
    'GENRE_WEIGHTS',
]
