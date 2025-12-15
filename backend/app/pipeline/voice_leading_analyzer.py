"""
Voice Leading Analyzer

Analyzes harmonic movement quality between chords:
- Motion types (parallel, contrary, oblique, similar)
- Voice leading smoothness scoring
- Guide tone line tracking (jazz)
- Common tone analysis
- Parallel 5ths/octaves detection
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.theory.interval_utils import note_to_semitone, get_interval
from app.theory.chord_library import get_chord_notes


class MotionType(Enum):
    """Types of voice motion between chords"""
    PARALLEL = "parallel"       # Same direction, same interval
    SIMILAR = "similar"         # Same direction, different interval
    CONTRARY = "contrary"       # Opposite directions
    OBLIQUE = "oblique"         # One voice stationary
    STATIC = "static"           # Both voices stationary


@dataclass
class VoiceLeadingMetrics:
    """Metrics for voice leading quality"""
    smoothness_score: float  # 0-1, higher = smoother
    total_movement: int      # Total semitones moved
    common_tones: int        # Notes retained between chords
    avg_movement: float      # Average movement per voice
    motion_types: Dict[str, int]  # Count of each motion type
    parallel_fifths: List[Tuple[int, int]] = field(default_factory=list)
    parallel_octaves: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class GuideToneLine:
    """Tracks 3rds and 7ths through a progression"""
    voice: str  # "third" or "seventh"
    notes: List[str]
    intervals: List[int]  # Movement between consecutive notes
    smoothness: float


def analyze_voice_leading(chord1: Dict, chord2: Dict) -> Dict:
    """
    Analyze voice leading between two chords.
    
    Args:
        chord1: First chord dict with 'root', 'quality'
        chord2: Second chord dict with 'root', 'quality'
    
    Returns:
        Dict with voice leading analysis
    """
    notes1 = get_chord_notes(chord1['root'], chord1.get('quality', ''))
    notes2 = get_chord_notes(chord2['root'], chord2.get('quality', ''))
    
    # Calculate movements
    movements = _calculate_voice_movements(notes1, notes2)
    motion_types = _classify_motions(movements)
    common = _find_common_tones(notes1, notes2)
    
    # Check for parallel 5ths/octaves
    parallels = _detect_parallel_intervals(notes1, notes2)
    
    # Calculate smoothness (lower movement = smoother)
    total_movement = sum(abs(m) for m in movements)
    avg_movement = total_movement / len(movements) if movements else 0
    smoothness = max(0, 1 - (avg_movement / 6))  # 6 semitones = half octave
    
    return {
        "from_chord": f"{chord1['root']}{chord1.get('quality', '')}",
        "to_chord": f"{chord2['root']}{chord2.get('quality', '')}",
        "smoothness_score": round(smoothness, 3),
        "total_movement": total_movement,
        "avg_movement": round(avg_movement, 2),
        "common_tones": len(common),
        "common_tone_notes": common,
        "motion_types": motion_types,
        "parallel_fifths": parallels.get("fifths", []),
        "parallel_octaves": parallels.get("octaves", []),
        "voice_movements": movements
    }


def _calculate_voice_movements(notes1: List[str], notes2: List[str]) -> List[int]:
    """
    Calculate minimal voice movements between two chords.
    Uses nearest-neighbor voice leading.
    """
    movements = []
    
    # For each note in chord1, find nearest note in chord2
    for n1 in notes1:
        s1 = note_to_semitone(n1)
        
        # Find closest note in chord2
        min_dist = 12
        for n2 in notes2:
            s2 = note_to_semitone(n2)
            # Calculate movement (allow both directions)
            dist = (s2 - s1 + 6) % 12 - 6  # Range: -6 to +5
            if abs(dist) < abs(min_dist):
                min_dist = dist
        
        movements.append(min_dist)
    
    return movements


def _classify_motions(movements: List[int]) -> Dict[str, int]:
    """Classify motion types from voice movements"""
    counts = {
        "parallel": 0,
        "similar": 0,
        "contrary": 0,
        "oblique": 0,
        "static": 0
    }
    
    for i, m1 in enumerate(movements):
        for m2 in movements[i+1:]:
            if m1 == 0 and m2 == 0:
                counts["static"] += 1
            elif m1 == 0 or m2 == 0:
                counts["oblique"] += 1
            elif m1 == m2:
                counts["parallel"] += 1
            elif (m1 > 0 and m2 > 0) or (m1 < 0 and m2 < 0):
                counts["similar"] += 1
            else:
                counts["contrary"] += 1
    
    return counts


def _find_common_tones(notes1: List[str], notes2: List[str]) -> List[str]:
    """Find notes that remain the same between chords (enharmonic aware)"""
    common = []
    s1 = {note_to_semitone(n) for n in notes1}
    
    for n2 in notes2:
        if note_to_semitone(n2) in s1:
            common.append(n2)
    
    return common


def _detect_parallel_intervals(notes1: List[str], notes2: List[str]) -> Dict:
    """Detect parallel 5ths and octaves (voice leading errors)"""
    parallels = {"fifths": [], "octaves": []}
    
    # Check all pairs of voice movements
    for i, n1a in enumerate(notes1):
        for j, n1b in enumerate(notes1):
            if i >= j:
                continue
            
            # Get corresponding notes in second chord
            if i >= len(notes2) or j >= len(notes2):
                continue
                
            n2a = notes2[i]
            n2b = notes2[j]
            
            # Calculate intervals
            int1 = get_interval(n1a, n1b)
            int2 = get_interval(n2a, n2b)
            
            # Check for parallel 5ths
            if int1 == 7 and int2 == 7:
                parallels["fifths"].append((i, j))
            
            # Check for parallel octaves
            if int1 == 0 and int2 == 0 and n1a != n1b:
                parallels["octaves"].append((i, j))
    
    return parallels


def analyze_progression_voice_leading(chords: List[Dict]) -> Dict:
    """
    Analyze voice leading through an entire chord progression.
    
    Args:
        chords: List of chord dicts with 'root', 'quality'
    
    Returns:
        Comprehensive voice leading analysis
    """
    if len(chords) < 2:
        return {
            "overall_smoothness": 1.0,
            "total_violations": 0,
            "transitions": [],
            "guide_tones": None
        }
    
    transitions = []
    total_smoothness = 0
    total_violations = 0
    
    for i in range(len(chords) - 1):
        analysis = analyze_voice_leading(chords[i], chords[i+1])
        transitions.append(analysis)
        total_smoothness += analysis["smoothness_score"]
        total_violations += len(analysis["parallel_fifths"]) + len(analysis["parallel_octaves"])
    
    avg_smoothness = total_smoothness / len(transitions) if transitions else 1.0
    
    # Extract guide tones if chords have 7ths
    guide_tones = _extract_guide_tones(chords)
    
    return {
        "overall_smoothness": round(avg_smoothness, 3),
        "total_transitions": len(transitions),
        "total_violations": total_violations,
        "transitions": transitions,
        "guide_tones": guide_tones,
        "smoothness_rating": _rate_smoothness(avg_smoothness)
    }


def _extract_guide_tones(chords: List[Dict]) -> Optional[Dict]:
    """
    Extract guide tone lines (3rds and 7ths) for jazz voice leading.
    Guide tones are the 3rd and 7th of each chord - they define the quality.
    """
    if not chords:
        return None
    
    thirds = []
    sevenths = []
    
    for chord in chords:
        root = chord.get('root', 'C')
        quality = chord.get('quality', '')
        
        try:
            notes = get_chord_notes(root, quality)
        except ValueError:
            notes = get_chord_notes(root, '')
        
        # 3rd is typically the 2nd note (index 1)
        if len(notes) >= 2:
            thirds.append(notes[1])
        
        # 7th is typically the 4th note (index 3) for 7th chords
        if len(notes) >= 4:
            sevenths.append(notes[3])
    
    # Calculate movements in guide tones
    third_movements = []
    for i in range(len(thirds) - 1):
        movement = get_interval(thirds[i], thirds[i+1])
        # Normalize to smallest movement
        if movement > 6:
            movement = movement - 12
        third_movements.append(movement)
    
    seventh_movements = []
    for i in range(len(sevenths) - 1):
        movement = get_interval(sevenths[i], sevenths[i+1])
        if movement > 6:
            movement = movement - 12
        seventh_movements.append(movement)
    
    return {
        "thirds": {
            "notes": thirds,
            "movements": third_movements,
            "avg_movement": sum(abs(m) for m in third_movements) / len(third_movements) if third_movements else 0
        },
        "sevenths": {
            "notes": sevenths,
            "movements": seventh_movements,
            "avg_movement": sum(abs(m) for m in seventh_movements) / len(seventh_movements) if seventh_movements else 0
        } if sevenths else None
    }


def _rate_smoothness(score: float) -> str:
    """Convert smoothness score to rating"""
    if score >= 0.9:
        return "excellent"
    elif score >= 0.7:
        return "good"
    elif score >= 0.5:
        return "moderate"
    elif score >= 0.3:
        return "rough"
    else:
        return "very_rough"


# ============================================================================
# PHASE 5 ENHANCEMENT: NEO-RIEMANNIAN ANALYSIS
# ============================================================================

def analyze_neo_riemannian_distance(
    chord1: Dict,
    chord2: Dict
) -> Dict:
    """
    Add Tonnetz distance and PLR path to existing voice leading analysis (Phase 5).

    Neo-Riemannian theory provides a geometric approach to understanding
    harmonic relationships through minimal voice-leading transformations.

    Args:
        chord1: First chord dict with 'root', 'quality'
        chord2: Second chord dict with 'root', 'quality'

    Returns:
        Dictionary with neo-Riemannian metrics:
        - tonnetz_distance: Number of PLR transformations
        - plr_path: List of transformation names (e.g., ['P', 'R'])
        - is_parsimonious: Whether ≤1 transformation (≤2 semitones movement)

    Example:
        >>> analyze_neo_riemannian_distance(
        ...     {'root': 'C', 'quality': 'maj'},
        ...     {'root': 'A', 'quality': 'min'}
        ... )
        {
            'tonnetz_distance': 1,
            'plr_path': ['R'],
            'is_parsimonious': True
        }
    """
    try:
        from app.theory.voice_leading_neo_riemannian import (
            calculate_tonnetz_distance,
            get_tonnetz_path
        )

        root1 = chord1.get('root', 'C')
        quality1 = chord1.get('quality', '')
        root2 = chord2.get('root', 'C')
        quality2 = chord2.get('quality', '')

        # Calculate Tonnetz metrics
        distance = calculate_tonnetz_distance(root1, quality1, root2, quality2)
        path = get_tonnetz_path(root1, quality1, root2, quality2, max_steps=6)

        return {
            'tonnetz_distance': distance,
            'plr_path': path,
            'is_parsimonious': distance == 1  # Single PLR transformation
        }

    except (ImportError, ValueError):
        # Neo-Riemannian module not available or chords incompatible
        return {
            'tonnetz_distance': None,
            'plr_path': None,
            'is_parsimonious': False
        }


def get_comprehensive_analysis(
    chord1: Dict,
    chord2: Dict
) -> Dict:
    """
    Comprehensive analysis combining traditional + neo-Riemannian metrics (Phase 5).

    Integrates:
    - Traditional voice leading analysis (smoothness, motion types, parallels)
    - Neo-Riemannian analysis (Tonnetz distance, PLR paths)

    Args:
        chord1: First chord dict with 'root', 'quality'
        chord2: Second chord dict with 'root', 'quality'

    Returns:
        Combined analysis dictionary

    Example:
        >>> get_comprehensive_analysis(
        ...     {'root': 'C', 'quality': 'maj'},
        ...     {'root': 'C', 'quality': 'min'}
        ... )
        {
            'from_chord': 'Cmaj',
            'to_chord': 'Cmin',
            'smoothness_score': 0.95,
            'total_movement': 1,
            'tonnetz_distance': 1,
            'plr_path': ['P'],
            'is_parsimonious': True,
            ...
        }
    """
    # Get traditional analysis
    basic_analysis = analyze_voice_leading(chord1, chord2)

    # Get neo-Riemannian analysis
    neo_analysis = analyze_neo_riemannian_distance(chord1, chord2)

    # Combine both
    return {**basic_analysis, **neo_analysis}
