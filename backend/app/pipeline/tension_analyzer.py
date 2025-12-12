"""
Tension Curve Analyzer

Analyzes harmonic tension throughout a progression:
- Calculates tension level for each chord
- Tracks tension build-up and release
- Identifies climax points
- Maps dissonance levels
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass

from app.theory.interval_utils import note_to_semitone, get_interval
from app.theory.chord_library import get_chord_notes


@dataclass
class TensionPoint:
    """Tension level at a specific point"""
    chord_index: int
    chord_symbol: str
    tension_level: float  # 0.0 (resolved) to 1.0 (maximum tension)
    dissonance_score: float
    distance_from_tonic: int
    contributing_factors: List[str]


# Chord quality tension ratings (0-1)
QUALITY_TENSION = {
    "": 0.1,           # Major triad - stable
    "maj": 0.1,
    "m": 0.15,         # Minor triad - slight tension
    "min": 0.15,
    "maj7": 0.2,       # Major 7 - slight dissonance
    "m7": 0.25,        # Minor 7
    "7": 0.4,          # Dominant 7 - wants to resolve
    "m7b5": 0.5,       # Half-diminished
    "dim": 0.55,       # Diminished
    "dim7": 0.6,       # Fully diminished
    "aug": 0.5,        # Augmented
    "7b9": 0.7,        # Altered dominant
    "7#9": 0.7,
    "7alt": 0.8,       # Fully altered
    "7#5": 0.6,
    "7b5": 0.6,
    "sus4": 0.35,      # Suspended - unresolved
    "sus2": 0.3,
}

# Interval tension from tonic (scale degrees)
INTERVAL_TENSION = {
    0: 0.0,   # Tonic - no tension
    1: 0.8,   # Half step - high tension (bII, vii)
    2: 0.4,   # Whole step (ii)
    3: 0.3,   # Minor 3rd (bIII, iii)
    4: 0.35,  # Major 3rd (III)
    5: 0.2,   # Perfect 4th (IV) - stable subdominant
    6: 0.9,   # Tritone - maximum tension
    7: 0.5,   # Perfect 5th (V) - dominant tension
    8: 0.4,   # Minor 6th (bVI)
    9: 0.25,  # Major 6th (vi) - relative minor
    10: 0.45, # Minor 7th (bVII)
    11: 0.7,  # Major 7th (leading tone area)
}


def calculate_chord_tension(
    chord: Dict, 
    key: str,
    prev_chord: Dict = None
) -> TensionPoint:
    """
    Calculate tension level for a single chord.
    
    Factors considered:
    1. Chord quality (dissonance)
    2. Distance from tonic
    3. Direction of previous motion
    4. Unresolved tendencies
    """
    root = chord.get('root', 'C')
    quality = chord.get('quality', '')
    chord_symbol = f"{root}{quality}"
    
    factors = []
    
    # Factor 1: Chord quality tension
    quality_tension = QUALITY_TENSION.get(quality, 0.4)
    factors.append(f"quality_tension: {quality_tension:.2f}")
    
    # Factor 2: Distance from tonic
    key_semitone = note_to_semitone(key)
    chord_semitone = note_to_semitone(root)
    interval = (chord_semitone - key_semitone) % 12
    interval_tension = INTERVAL_TENSION.get(interval, 0.5)
    factors.append(f"tonic_distance: {interval_tension:.2f}")
    
    # Factor 3: Dissonance within chord
    try:
        notes = get_chord_notes(root, quality)
        dissonance = _calculate_dissonance(notes)
    except:
        dissonance = 0.3
    factors.append(f"internal_dissonance: {dissonance:.2f}")
    
    # Factor 4: Motion tension (if previous chord exists)
    motion_tension = 0.0
    if prev_chord:
        prev_interval = get_interval(prev_chord.get('root', 'C'), root)
        if prev_interval in [1, 11]:  # Half step motion
            motion_tension = 0.2
            factors.append("chromatic_motion")
        elif prev_interval == 6:  # Tritone motion
            motion_tension = 0.3
            factors.append("tritone_motion")
    
    # Weighted combination
    tension_level = (
        quality_tension * 0.35 +
        interval_tension * 0.35 +
        dissonance * 0.2 +
        motion_tension * 0.1
    )
    
    return TensionPoint(
        chord_index=0,  # Will be set by caller
        chord_symbol=chord_symbol,
        tension_level=round(min(1.0, tension_level), 3),
        dissonance_score=round(dissonance, 3),
        distance_from_tonic=interval,
        contributing_factors=factors
    )


def _calculate_dissonance(notes: List[str]) -> float:
    """
    Calculate internal dissonance of a chord based on intervals.
    
    Dissonant intervals: m2/M7 (1, 11), tritone (6)
    """
    if len(notes) < 2:
        return 0.0
    
    dissonance = 0.0
    interval_count = 0
    
    for i, n1 in enumerate(notes):
        for n2 in notes[i+1:]:
            interval = get_interval(n1, n2)
            
            # Score dissonant intervals
            if interval in [1, 11]:  # Minor 2nd / Major 7th
                dissonance += 0.8
            elif interval == 6:  # Tritone
                dissonance += 0.6
            elif interval in [2, 10]:  # Major 2nd / Minor 7th
                dissonance += 0.3
            else:  # Consonant
                dissonance += 0.1
            
            interval_count += 1
    
    return dissonance / interval_count if interval_count > 0 else 0.0


def analyze_tension_curve(chords: List[Dict], key: str) -> Dict:
    """
    Analyze tension throughout an entire progression.
    
    Returns:
        Dict with tension curve data and analysis
    """
    if not chords:
        return {"error": "No chords provided"}
    
    tension_points = []
    prev_chord = None
    
    for i, chord in enumerate(chords):
        point = calculate_chord_tension(chord, key, prev_chord)
        point.chord_index = i
        tension_points.append(point)
        prev_chord = chord
    
    # Extract tension values
    tension_values = [p.tension_level for p in tension_points]
    
    # Find climax (highest tension)
    max_tension = max(tension_values)
    climax_index = tension_values.index(max_tension)
    
    # Find resolution points (local minima after peaks)
    resolutions = []
    for i in range(1, len(tension_values) - 1):
        if tension_values[i] < tension_values[i-1] and tension_values[i] <= tension_values[i+1]:
            resolutions.append(i)
    
    # Calculate tension arc shape
    arc_shape = _classify_tension_arc(tension_values)
    
    # Average tension
    avg_tension = sum(tension_values) / len(tension_values)
    
    return {
        "key": key,
        "tension_curve": [
            {
                "chord": p.chord_symbol,
                "tension": p.tension_level,
                "dissonance": p.dissonance_score,
                "tonic_distance": p.distance_from_tonic,
                "factors": p.contributing_factors
            }
            for p in tension_points
        ],
        "summary": {
            "average_tension": round(avg_tension, 3),
            "max_tension": max_tension,
            "min_tension": min(tension_values),
            "climax_position": climax_index,
            "climax_chord": tension_points[climax_index].chord_symbol,
            "resolution_count": len(resolutions),
            "arc_shape": arc_shape
        },
        "interpretation": _interpret_tension_curve(avg_tension, arc_shape)
    }


def _classify_tension_arc(values: List[float]) -> str:
    """Classify the overall shape of the tension curve"""
    if len(values) < 3:
        return "flat"
    
    # Check for rising, falling, or arch patterns
    first_third = sum(values[:len(values)//3]) / (len(values)//3 + 1)
    middle_third = sum(values[len(values)//3:2*len(values)//3]) / (len(values)//3 + 1)
    last_third = sum(values[2*len(values)//3:]) / (len(values)//3 + 1)
    
    if middle_third > first_third and middle_third > last_third:
        return "arch"  # Build and release
    elif first_third < middle_third < last_third:
        return "rising"  # Continuous build
    elif first_third > middle_third > last_third:
        return "falling"  # Continuous release
    elif abs(first_third - last_third) < 0.1:
        return "cyclic"  # Returns to start
    else:
        return "complex"


def _interpret_tension_curve(avg_tension: float, arc_shape: str) -> str:
    """Provide human-readable interpretation"""
    tension_desc = ""
    if avg_tension < 0.25:
        tension_desc = "very stable, consonant"
    elif avg_tension < 0.4:
        tension_desc = "moderately stable"
    elif avg_tension < 0.55:
        tension_desc = "balanced tension/release"
    elif avg_tension < 0.7:
        tension_desc = "tension-forward, dramatic"
    else:
        tension_desc = "highly dissonant, unresolved"
    
    arc_desc = {
        "arch": "Classic tension arc with build and release",
        "rising": "Builds tension toward the end",
        "falling": "Resolves tension over time",
        "cyclic": "Returns to starting tension level",
        "complex": "Complex tension pattern",
        "flat": "Steady tension level throughout"
    }
    
    return f"{tension_desc.capitalize()}. {arc_desc.get(arc_shape, 'No pattern detected')}."


def get_tension_recommendations(
    tension_analysis: Dict
) -> List[Dict]:
    """
    Provide recommendations based on tension analysis.
    """
    recommendations = []
    summary = tension_analysis.get("summary", {})
    
    avg = summary.get("average_tension", 0.5)
    arc = summary.get("arc_shape", "")
    
    if avg > 0.6:
        recommendations.append({
            "type": "reduce_tension",
            "suggestion": "Consider adding more resolution points with tonic or dominant chords",
            "priority": "high"
        })
    
    if arc == "rising":
        recommendations.append({
            "type": "add_resolution",
            "suggestion": "The progression lacks resolution. Consider ending with V-I or IV-I cadence",
            "priority": "medium"
        })
    
    if summary.get("resolution_count", 0) == 0:
        recommendations.append({
            "type": "no_resolution",
            "suggestion": "No clear resolution points found. Consider adding authentic or plagal cadences",
            "priority": "high"
        })
    
    if avg < 0.25:
        recommendations.append({
            "type": "increase_interest",
            "suggestion": "Progression is very consonant. Consider adding secondary dominants or borrowed chords for interest",
            "priority": "low"
        })
    
    return recommendations
