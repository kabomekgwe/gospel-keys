"""
Cadence Detector

Identifies cadence types in chord progressions:
- Perfect/Imperfect Authentic (V-I)
- Plagal (IV-I)
- Half (ending on V)
- Deceptive (V-vi)
- Phrygian Half Cadence
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from app.theory.interval_utils import note_to_semitone, get_interval


class CadenceType(Enum):
    """Types of musical cadences"""
    PERFECT_AUTHENTIC = "perfect_authentic"    # V-I with root position, soprano on tonic
    IMPERFECT_AUTHENTIC = "imperfect_authentic"  # V-I with inversion or soprano not on tonic
    PLAGAL = "plagal"                          # IV-I (Amen cadence)
    HALF = "half"                              # Ends on V
    DECEPTIVE = "deceptive"                    # V-vi
    PHRYGIAN_HALF = "phrygian_half"           # iv6-V in minor
    BACKDOOR = "backdoor"                      # bVII-I
    PLAGAL_MINOR = "plagal_minor"             # iv-I (minor plagal)


@dataclass
class DetectedCadence:
    """A detected cadence in a progression"""
    cadence_type: CadenceType
    start_index: int
    end_index: int
    chords: List[str]
    key: str
    strength: str  # "strong", "moderate", "weak"
    description: str


# Cadence patterns defined by interval from tonic and chord qualities
CADENCE_PATTERNS = {
    CadenceType.PERFECT_AUTHENTIC: {
        "intervals": [7, 0],  # V to I
        "qualities": [["7", "maj", ""], ["maj7", "maj", ""]],
        "description": "Perfect Authentic Cadence (V-I)"
    },
    CadenceType.PLAGAL: {
        "intervals": [5, 0],  # IV to I
        "qualities": [["maj7", "maj", ""], ["maj7", "maj", ""]],
        "description": "Plagal Cadence (IV-I, 'Amen')"
    },
    CadenceType.DECEPTIVE: {
        "intervals": [7, 9],  # V to vi
        "qualities": [["7", "maj", ""], ["m7", "m", "min"]],
        "description": "Deceptive Cadence (V-vi)"
    },
    CadenceType.HALF: {
        "intervals": [None, 7],  # anything to V
        "description": "Half Cadence (ending on V)"
    },
    CadenceType.BACKDOOR: {
        "intervals": [10, 0],  # bVII to I
        "qualities": [["7"], ["maj7", "maj", ""]],
        "description": "Backdoor Cadence (♭VII7-I)"
    },
    CadenceType.PLAGAL_MINOR: {
        "intervals": [5, 0],  # iv to I
        "qualities": [["m7", "m", "min"], ["maj7", "maj", ""]],
        "description": "Minor Plagal Cadence (iv-I)"
    },
}


def detect_cadences(chords: List[Dict], key: Optional[str] = None) -> List[DetectedCadence]:
    """
    Detect cadences in a chord progression.
    
    Args:
        chords: List of chord dicts with 'root', 'quality', 'time'
        key: Optional key context (if None, will attempt detection)
    
    Returns:
        List of detected cadences
    """
    if len(chords) < 2:
        return []
    
    # Attempt key detection if not provided
    if key is None:
        key = _estimate_key(chords)
    
    key_semitone = note_to_semitone(key)
    cadences = []
    
    # Check each pair of consecutive chords
    for i in range(len(chords) - 1):
        chord1 = chords[i]
        chord2 = chords[i + 1]
        
        # Calculate intervals from key
        root1 = note_to_semitone(chord1['root'])
        root2 = note_to_semitone(chord2['root'])
        
        interval1 = (root1 - key_semitone) % 12
        interval2 = (root2 - key_semitone) % 12
        
        quality1 = chord1.get('quality', '')
        quality2 = chord2.get('quality', '')
        
        # Check against each cadence pattern
        detected = _match_cadence_pattern(
            interval1, interval2, quality1, quality2, i
        )
        
        if detected:
            detected.chords = [
                f"{chord1['root']}{quality1}",
                f"{chord2['root']}{quality2}"
            ]
            detected.key = key
            cadences.append(detected)
    
    # Also check for half cadences (ending on V)
    if chords:
        last_chord = chords[-1]
        last_interval = (note_to_semitone(last_chord['root']) - key_semitone) % 12
        
        if last_interval == 7:  # Ends on V
            cadences.append(DetectedCadence(
                cadence_type=CadenceType.HALF,
                start_index=len(chords) - 2,
                end_index=len(chords) - 1,
                chords=[f"{last_chord['root']}{last_chord.get('quality', '')}"],
                key=key,
                strength="moderate",
                description="Half Cadence (ends on V)"
            ))
    
    return cadences


def _match_cadence_pattern(
    interval1: int, 
    interval2: int, 
    quality1: str, 
    quality2: str,
    index: int
) -> Optional[DetectedCadence]:
    """Check if intervals match a cadence pattern"""
    
    for cadence_type, pattern in CADENCE_PATTERNS.items():
        pattern_intervals = pattern["intervals"]
        
        # Check interval match
        if pattern_intervals[0] is not None and pattern_intervals[0] != interval1:
            continue
        if pattern_intervals[1] != interval2:
            continue
        
        # Check quality match if specified
        if "qualities" in pattern:
            q1_match = any(q in quality1 or quality1 in q for q in pattern["qualities"][0])
            q2_match = any(q in quality2 or quality2 in q for q in pattern["qualities"][1])
            
            if not (q1_match and q2_match):
                # Still count as weak cadence without quality match
                strength = "weak"
            else:
                strength = "strong"
        else:
            strength = "moderate"
        
        return DetectedCadence(
            cadence_type=cadence_type,
            start_index=index,
            end_index=index + 1,
            chords=[],  # Will be filled by caller
            key="",     # Will be filled by caller
            strength=strength,
            description=pattern["description"]
        )
    
    return None


def _estimate_key(chords: List[Dict]) -> str:
    """
    Estimate the key from chord progression.
    Uses multiple heuristics:
    1. Most common root
    2. Final chord root
    3. V-I motion detection
    """
    if not chords:
        return "C"
    
    # Heuristic 1: Last chord is often the tonic
    last_root = chords[-1]['root']
    
    # Heuristic 2: Look for V-I motion
    for i in range(len(chords) - 1):
        interval = get_interval(chords[i]['root'], chords[i+1]['root'])
        if interval == 5:  # Up a 4th (down a 5th = V-I)
            return chords[i+1]['root']
    
    # Heuristic 3: Most common root
    root_counts = {}
    for chord in chords:
        root = chord['root']
        root_counts[root] = root_counts.get(root, 0) + 1
    
    most_common = max(root_counts.items(), key=lambda x: x[1])[0]
    
    # Weight last chord heavily
    if root_counts.get(last_root, 0) >= root_counts[most_common] * 0.5:
        return last_root
    
    return most_common


def analyze_cadential_structure(chords: List[Dict]) -> Dict:
    """
    Comprehensive cadence analysis for a progression.
    
    Returns:
        Dict with cadence analysis, phrase structure hints, and harmonic closure
    """
    cadences = detect_cadences(chords)
    
    # Categorize cadences
    authentic_count = sum(1 for c in cadences if "authentic" in c.cadence_type.value)
    plagal_count = sum(1 for c in cadences if "plagal" in c.cadence_type.value)
    half_count = sum(1 for c in cadences if c.cadence_type == CadenceType.HALF)
    deceptive_count = sum(1 for c in cadences if c.cadence_type == CadenceType.DECEPTIVE)
    
    # Determine overall harmonic closure
    if cadences:
        final_cadence = cadences[-1] if cadences else None
        closure = _assess_closure(final_cadence)
    else:
        closure = "open"
    
    return {
        "cadences": [
            {
                "type": c.cadence_type.value,
                "position": c.start_index,
                "chords": c.chords,
                "strength": c.strength,
                "description": c.description
            }
            for c in cadences
        ],
        "summary": {
            "authentic_cadences": authentic_count,
            "plagal_cadences": plagal_count,
            "half_cadences": half_count,
            "deceptive_cadences": deceptive_count,
            "total_cadences": len(cadences)
        },
        "harmonic_closure": closure,
        "estimated_key": cadences[0].key if cadences else _estimate_key(chords),
        "phrase_count_estimate": max(1, len(cadences))
    }


def _assess_closure(final_cadence: Optional[DetectedCadence]) -> str:
    """Assess how resolved/closed the progression feels"""
    if final_cadence is None:
        return "open"
    
    if final_cadence.cadence_type in [CadenceType.PERFECT_AUTHENTIC, CadenceType.IMPERFECT_AUTHENTIC]:
        return "closed" if final_cadence.strength == "strong" else "mostly_closed"
    elif final_cadence.cadence_type == CadenceType.PLAGAL:
        return "closed"
    elif final_cadence.cadence_type == CadenceType.HALF:
        return "open"
    elif final_cadence.cadence_type == CadenceType.DECEPTIVE:
        return "suspended"
    else:
        return "ambiguous"
