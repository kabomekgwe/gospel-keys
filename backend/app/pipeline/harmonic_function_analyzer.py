"""
Harmonic Function Analyzer

Maps chords to their harmonic functions:
- Tonic (T): I, vi, iii
- Subdominant (S): IV, ii
- Dominant (D): V, vii°

Also detects:
- Secondary dominants (V/x)
- Modal mixture / borrowed chords
- Neapolitan and Augmented 6th chords
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.theory.interval_utils import note_to_semitone, get_interval, semitone_to_note


class HarmonicFunction(Enum):
    """Primary harmonic functions"""
    TONIC = "T"
    SUBDOMINANT = "S"
    DOMINANT = "D"
    SECONDARY_DOMINANT = "V/x"
    BORROWED = "borrowed"
    CHROMATIC = "chromatic"


@dataclass
class ChordFunction:
    """Analyzed chord with its harmonic function"""
    chord_symbol: str
    roman_numeral: str
    function: HarmonicFunction
    function_detail: str
    is_diatonic: bool
    applied_to: Optional[str] = None  # For secondary dominants


# Diatonic chord functions in major key
# Interval from tonic -> (roman numeral, function, quality)
MAJOR_KEY_FUNCTIONS = {
    0: ("I", HarmonicFunction.TONIC, ["", "maj", "maj7"]),
    2: ("ii", HarmonicFunction.SUBDOMINANT, ["m", "m7", "min"]),
    4: ("iii", HarmonicFunction.TONIC, ["m", "m7", "min"]),
    5: ("IV", HarmonicFunction.SUBDOMINANT, ["", "maj", "maj7"]),
    7: ("V", HarmonicFunction.DOMINANT, ["", "7", "maj"]),
    9: ("vi", HarmonicFunction.TONIC, ["m", "m7", "min"]),
    11: ("vii°", HarmonicFunction.DOMINANT, ["dim", "m7b5", "°"]),
}

# Diatonic chord functions in minor key
MINOR_KEY_FUNCTIONS = {
    0: ("i", HarmonicFunction.TONIC, ["m", "m7", "min"]),
    2: ("ii°", HarmonicFunction.SUBDOMINANT, ["dim", "m7b5", "°"]),
    3: ("III", HarmonicFunction.TONIC, ["", "maj", "maj7"]),
    5: ("iv", HarmonicFunction.SUBDOMINANT, ["m", "m7", "min"]),
    7: ("V", HarmonicFunction.DOMINANT, ["", "7", "maj"]),  # Harmonic minor
    8: ("VI", HarmonicFunction.SUBDOMINANT, ["", "maj", "maj7"]),
    10: ("VII", HarmonicFunction.DOMINANT, ["", "7", "maj"]),  # Natural minor
}

# Common borrowed chords (modal mixture)
BORROWED_CHORDS = {
    # From parallel minor to major
    3: ("♭III", "Parallel minor"),
    8: ("♭VI", "Parallel minor"),
    10: ("♭VII", "Parallel minor/Mixolydian"),
    # Neapolitan
    1: ("♭II", "Neapolitan"),
}


def analyze_chord_function(
    chord: Dict, 
    key: str, 
    mode: str = "major"
) -> ChordFunction:
    """
    Analyze the harmonic function of a single chord.
    
    Args:
        chord: Chord dict with 'root', 'quality'
        key: Key center (e.g., "C", "F#")
        mode: "major" or "minor"
    
    Returns:
        ChordFunction with analysis
    """
    root = chord.get('root', 'C')
    quality = chord.get('quality', '')
    
    key_semitone = note_to_semitone(key)
    chord_semitone = note_to_semitone(root)
    interval = (chord_semitone - key_semitone) % 12
    
    chord_symbol = f"{root}{quality}"
    
    # Check for secondary dominants FIRST (before diatonic)
    # This catches dom7 chords that would otherwise match diatonic chords
    if '7' in quality and 'maj' not in quality and 'm' not in quality:
        secondary = _detect_secondary_dominant(interval, quality)
        if secondary:
            return ChordFunction(
                chord_symbol=chord_symbol,
                roman_numeral=secondary["roman"],
                function=HarmonicFunction.SECONDARY_DOMINANT,
                function_detail=f"Secondary dominant to {secondary['target']}",
                is_diatonic=False,
                applied_to=secondary["target"]
            )
    
    # Check diatonic functions
    functions = MAJOR_KEY_FUNCTIONS if mode == "major" else MINOR_KEY_FUNCTIONS
    
    if interval in functions:
        roman, function, expected_qualities = functions[interval]
        
        # Check if quality matches expected
        is_diatonic = any(q in quality or quality in q for q in expected_qualities)
        
        if is_diatonic:
            return ChordFunction(
                chord_symbol=chord_symbol,
                roman_numeral=roman,
                function=function,
                function_detail=f"{function.value} function",
                is_diatonic=True
            )
    
    # Check for secondary dominants
    secondary = _detect_secondary_dominant(interval, quality)
    if secondary:
        return ChordFunction(
            chord_symbol=chord_symbol,
            roman_numeral=secondary["roman"],
            function=HarmonicFunction.SECONDARY_DOMINANT,
            function_detail=f"Secondary dominant to {secondary['target']}",
            is_diatonic=False,
            applied_to=secondary["target"]
        )
    
    # Check for borrowed chords
    if interval in BORROWED_CHORDS:
        roman, source = BORROWED_CHORDS[interval]
        return ChordFunction(
            chord_symbol=chord_symbol,
            roman_numeral=roman,
            function=HarmonicFunction.BORROWED,
            function_detail=f"Borrowed from {source}",
            is_diatonic=False
        )
    
    # Chromatic / unknown
    return ChordFunction(
        chord_symbol=chord_symbol,
        roman_numeral=_interval_to_roman(interval, quality),
        function=HarmonicFunction.CHROMATIC,
        function_detail="Chromatic chord",
        is_diatonic=False
    )


def _detect_secondary_dominant(interval: int, quality: str) -> Optional[Dict]:
    """
    Detect if chord is a secondary dominant.
    Secondary dominants are dominant 7th chords that resolve up a P4 to a diatonic chord.
    """
    # Must be a dominant-type chord
    if '7' not in quality or 'maj' in quality or 'm' in quality:
        return None
    
    # Secondary dominant targets (where they resolve)
    # The chord a P4 up from this one
    target_interval = (interval + 5) % 12
    
    targets = {
        2: "ii",   # V/ii
        4: "iii",  # V/iii
        5: "IV",   # V/IV
        7: "V",    # V/V
        9: "vi",   # V/vi
    }
    
    if target_interval in targets:
        return {
            "roman": f"V/{targets[target_interval]}",
            "target": targets[target_interval]
        }
    
    return None


def _interval_to_roman(interval: int, quality: str) -> str:
    """Convert interval to roman numeral with accidental"""
    base_numerals = ["I", "♭II", "II", "♭III", "III", "IV", "♯IV/♭V", 
                     "V", "♭VI", "VI", "♭VII", "VII"]
    
    numeral = base_numerals[interval]
    
    # Lowercase for minor
    if 'm' in quality and 'maj' not in quality:
        numeral = numeral.lower()
    
    return numeral


def analyze_progression_functions(
    chords: List[Dict], 
    key: Optional[str] = None,
    mode: str = "major"
) -> Dict:
    """
    Analyze harmonic functions for an entire progression.
    
    Args:
        chords: List of chord dicts
        key: Key center (auto-detected if None)
        mode: "major" or "minor"
    
    Returns:
        Comprehensive harmonic analysis
    """
    if not chords:
        return {"error": "No chords provided"}
    
    # Auto-detect key if not provided
    if key is None:
        key = _estimate_key_from_progression(chords)
    
    # Analyze each chord
    analyses = [analyze_chord_function(c, key, mode) for c in chords]
    
    # Count function distribution
    function_counts = {}
    for a in analyses:
        f = a.function.value
        function_counts[f] = function_counts.get(f, 0) + 1
    
    # Calculate diatonic percentage
    diatonic_count = sum(1 for a in analyses if a.is_diatonic)
    diatonic_pct = diatonic_count / len(analyses) if analyses else 0
    
    # Find secondary dominants
    secondary_doms = [a for a in analyses if a.function == HarmonicFunction.SECONDARY_DOMINANT]
    
    # Analyze harmonic rhythm (T-S-D patterns)
    function_sequence = [a.function.value for a in analyses]
    
    return {
        "key": key,
        "mode": mode,
        "chord_functions": [
            {
                "chord": a.chord_symbol,
                "roman": a.roman_numeral,
                "function": a.function.value,
                "detail": a.function_detail,
                "diatonic": a.is_diatonic,
                "applied_to": a.applied_to
            }
            for a in analyses
        ],
        "function_distribution": function_counts,
        "diatonic_percentage": round(diatonic_pct * 100, 1),
        "secondary_dominants": len(secondary_doms),
        "function_sequence": function_sequence,
        "harmonic_rhythm_pattern": _analyze_harmonic_rhythm(function_sequence)
    }


def _estimate_key_from_progression(chords: List[Dict]) -> str:
    """Estimate key from chord progression"""
    if not chords:
        return "C"
    
    # Weight last chord heavily
    last_root = chords[-1]['root']
    
    # Look for V-I motion
    for i in range(len(chords) - 1):
        interval = get_interval(chords[i]['root'], chords[i+1]['root'])
        if interval == 5:  # Down a 5th = V-I
            return chords[i+1]['root']
    
    # Fallback to most common root
    root_counts = {}
    for c in chords:
        r = c['root']
        root_counts[r] = root_counts.get(r, 0) + 1
    
    return max(root_counts.items(), key=lambda x: x[1])[0]


def _analyze_harmonic_rhythm(sequence: List[str]) -> str:
    """Analyze the T-S-D flow pattern"""
    if not sequence:
        return "empty"
    
    # Common patterns
    patterns = {
        ("T", "S", "D", "T"): "classical_cadence",
        ("T", "D", "T"): "simple_resolution",
        ("S", "D", "T"): "cadential",
        ("T", "S", "T"): "plagal_motion",
    }
    
    # Check for pattern matches
    seq_tuple = tuple(sequence[-4:]) if len(sequence) >= 4 else tuple(sequence)
    
    for pattern, name in patterns.items():
        if seq_tuple == pattern:
            return name
    
    # Count transitions
    t_to_s = sum(1 for i in range(len(sequence)-1) 
                 if sequence[i] == "T" and sequence[i+1] == "S")
    s_to_d = sum(1 for i in range(len(sequence)-1) 
                 if sequence[i] == "S" and sequence[i+1] == "D")
    d_to_t = sum(1 for i in range(len(sequence)-1) 
                 if sequence[i] == "D" and sequence[i+1] == "T")
    
    if d_to_t > 0:
        return "resolving"
    elif s_to_d > 0:
        return "building_tension"
    else:
        return "static"
