"""
Blues Analysis Module (Enhanced)

Features:
- 12-bar blues form detection
- Shuffle rhythm detection
- Blue note analysis
- Multiple blues form variants (quick-change, minor blues, 8-bar)
"""

from typing import List, Dict, Optional
from app.theory.interval_utils import note_to_semitone, get_interval
from app.pipeline.progression_detector import (
    detect_progressions,
    ProgressionGenre,
    BLUES_PROGRESSIONS
)


def analyze_blues_structure(chords: List[Dict], tempo: float = 120.0) -> Dict:
    """
    Analyze song for blues characteristics.
    
    Args:
        chords: List of chord dictionaries with 'root', 'quality', 'time'
        tempo: Song tempo in BPM
        
    Returns:
        Dictionary of blues analysis results
    """
    form_result = detect_blues_form(chords)
    
    return {
        "form_detection": form_result,
        "rhythm_feel": detect_shuffle_feel(tempo),
        "blue_notes_analysis": analyze_blue_notes_context(chords),
        "blues_indicators": calculate_blues_indicators(chords)
    }


def detect_blues_form(chords: List[Dict]) -> Dict:
    """
    Detect if the chord progression follows a blues form.
    
    Supports:
    - Standard 12-bar blues
    - Quick-change 12-bar
    - 8-bar blues
    - Minor blues
    - Jazz blues
    """
    if not chords or len(chords) < 8:
        return {
            "is_blues": False,
            "form_type": None,
            "confidence": 0.0,
            "key": None
        }
    
    # Use progression detector
    matches = detect_progressions(chords, genres=[ProgressionGenre.BLUES])
    
    if matches:
        best_match = max(matches, key=lambda m: m.confidence)
        return {
            "is_blues": True,
            "form_type": best_match.pattern_name,
            "confidence": best_match.confidence,
            "key": best_match.key,
            "roman_numerals": best_match.roman_numerals
        }
    
    # Fallback: heuristic detection
    blues_indicators = _detect_blues_heuristics(chords)
    
    return {
        "is_blues": blues_indicators["score"] > 0.5,
        "form_type": "blues_influenced" if blues_indicators["score"] > 0.5 else None,
        "confidence": blues_indicators["score"],
        "key": blues_indicators.get("likely_key"),
        "indicators": blues_indicators
    }


def _detect_blues_heuristics(chords: List[Dict]) -> Dict:
    """
    Heuristic blues detection based on chord characteristics.
    """
    if not chords:
        return {"score": 0.0, "indicators": []}
    
    indicators = []
    score = 0.0
    
    # Get unique roots
    roots = [c['root'] for c in chords]
    unique_roots = list(set(roots))
    
    # Indicator 1: Three-chord structure (I, IV, V relationships)
    if len(unique_roots) <= 4:
        score += 0.2
        indicators.append("limited_harmony")
    
    # Indicator 2: Dominant 7th chords throughout
    dom7_count = sum(1 for c in chords if c.get('quality', '') == '7')
    if dom7_count / len(chords) > 0.5:
        score += 0.3
        indicators.append("dominant_heavy")
    
    # Indicator 3: Check for I-IV-V movement
    for i in range(len(chords) - 1):
        interval = get_interval(chords[i]['root'], chords[i+1]['root'])
        if interval in [5, 7]:  # P4 or P5
            score += 0.05
            
    score = min(score, 1.0)
    
    # Attempt key detection from most common root
    root_counts = {}
    for r in roots:
        root_counts[r] = root_counts.get(r, 0) + 1
    likely_key = max(root_counts.items(), key=lambda x: x[1])[0] if root_counts else None
    
    return {
        "score": score,
        "indicators": indicators,
        "likely_key": likely_key
    }


def detect_shuffle_feel(tempo: float) -> Dict:
    """
    Estimate rhythmic feel based on tempo.
    Real shuffle detection requires audio onset analysis (swing ratio).
    
    Returns:
        Dict with feel analysis
    """
    feel = "straight"
    confidence = 0.5
    
    if 80 <= tempo <= 140:
        feel = "potential_shuffle"
        confidence = 0.6
    elif 50 <= tempo <= 80:
        feel = "slow_blues"
        confidence = 0.7
    elif tempo > 140:
        feel = "uptempo_swing"
        confidence = 0.5
        
    return {
        "feel": feel,
        "tempo": tempo,
        "confidence": confidence,
        "note": "Full shuffle detection requires audio analysis"
    }


def analyze_blue_notes_context(chords: List[Dict]) -> Dict:
    """
    Analyze where blue notes would typically appear relative to chord changes.
    
    Blue notes in context of a chord:
    - ♭3 over major/dominant chord
    - ♭5 (passing tone)
    - ♭7 over major chord
    """
    if not chords:
        return {"blue_note_zones": [], "total_zones": 0}
    
    blue_zones = []
    
    for i, chord in enumerate(chords):
        root = chord.get('root', 'C')
        quality = chord.get('quality', '')
        time = chord.get('time', 0)
        duration = chord.get('duration', 1.0)
        
        # Major or dominant chords are prime blue note targets
        if quality in ['', 'maj', 'maj7', '7', '9', '13']:
            root_semitone = note_to_semitone(root)
            
            blue_zones.append({
                "time_start": time,
                "time_end": time + duration,
                "chord": f"{root}{quality}",
                "blue_notes": [
                    {"note": _semitone_to_blue_note(root_semitone, 3), "type": "flat_3"},
                    {"note": _semitone_to_blue_note(root_semitone, 6), "type": "flat_5"},
                    {"note": _semitone_to_blue_note(root_semitone, 10), "type": "flat_7"}
                ]
            })
    
    return {
        "blue_note_zones": blue_zones[:10],  # Limit output
        "total_zones": len(blue_zones)
    }


def _semitone_to_blue_note(root_semitone: int, offset: int) -> str:
    """Get note name for a blue note offset from root"""
    from app.theory.interval_utils import semitone_to_note
    return semitone_to_note((root_semitone + offset) % 12, prefer_sharps=False)


def calculate_blues_indicators(chords: List[Dict]) -> Dict:
    """
    Calculate overall blues characteristics score.
    """
    if not chords:
        return {"blues_score": 0.0, "factors": {}}
    
    factors = {}
    
    # Factor 1: Dominant 7th prevalence
    dom7 = sum(1 for c in chords if '7' in c.get('quality', '') and 'maj' not in c.get('quality', ''))
    factors["dominant_prevalence"] = min(dom7 / len(chords), 1.0)
    
    # Factor 2: Harmonic simplicity (few unique chords)
    unique_chords = len(set(f"{c['root']}{c.get('quality', '')}" for c in chords))
    factors["harmonic_simplicity"] = max(0, 1 - (unique_chords - 3) / 10)
    
    # Factor 3: I-IV-V coverage
    # (would need key context for accuracy)
    factors["primary_chord_focus"] = 0.5  # Placeholder
    
    # Weighted score
    blues_score = (
        factors["dominant_prevalence"] * 0.4 +
        factors["harmonic_simplicity"] * 0.3 +
        factors["primary_chord_focus"] * 0.3
    )
    
    return {
        "blues_score": round(blues_score, 3),
        "factors": factors,
        "interpretation": _interpret_blues_score(blues_score)
    }


def _interpret_blues_score(score: float) -> str:
    """Interpret blues score as text"""
    if score >= 0.8:
        return "Strong blues characteristics"
    elif score >= 0.6:
        return "Moderate blues influence"
    elif score >= 0.4:
        return "Some blues elements"
    else:
        return "Minimal blues characteristics"
