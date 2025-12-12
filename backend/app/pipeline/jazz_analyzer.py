"""
Jazz Pattern Recognition Module

Detects common jazz patterns and progressions in transcribed music.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class JazzPattern:
    """Detected jazz pattern"""
    pattern_type: str
    start_time: float
    duration: float
    chords: List[str]
    key: str
    confidence: float
    metadata: Dict


# Extended jazz chord templates
JAZZ_CHORD_TEMPLATES = {
    # Major family
    "maj7": [0, 4, 7, 11],
    "maj9": [0, 4, 7, 11, 14],
    "maj7#11": [0, 4, 7, 11, 18],  # Lydian
    "6/9": [0, 4, 7, 9, 14],
    
    # Minor family
    "m7": [0, 3, 7, 10],
    "m9": [0, 3, 7, 10, 14],
    "m11": [0, 3, 7, 10, 14, 17],
    "m7b5": [0, 3, 6, 10],  # Half-diminished
    
    # Dominant family
    "7": [0, 4, 7, 10],
    "9": [0, 4, 7, 10, 14],
    "13": [0, 4, 7, 10, 14, 17, 21],
    "7#9": [0, 4, 7, 10, 15],  # Hendrix chord
    "7b9": [0, 4, 7, 10, 13],
    "7alt": [0, 4, 10, 13, 18],  # Altered dominant
    "7#11": [0, 4, 7, 10, 18],
    
    # Diminished
    "dim7": [0, 3, 6, 9],
    "dim": [0, 3, 6],
    
    # Augmented
    "aug": [0, 4, 8],
    "7#5": [0, 4, 8, 10],
}


def detect_ii_v_i_progressions(chords: List[Dict], key: str = "C") -> List[JazzPattern]:
    """
    Detect ii-V-I progressions (most common in jazz)
    
    Args:
        chords: List of chord dicts with 'root', 'quality', 'time'
        key: Key signature
    
    Returns:
        List of detected ii-V-I patterns
    """
    patterns = []
    
    # Define ii-V-I pattern in different keys
    # In C major: Dm7 - G7 - Cmaj7
    # In C minor: Dm7b5 - G7 - Cm7
    for i in range(len(chords) - 2):
        chord1 = chords[i]
        chord2 = chords[i + 1]
        chord3 = chords[i + 2]
        
        # Check if this matches ii-V-I pattern
        # Simplified check (can be enhanced with more music theory)
        if _is_ii_v_i_pattern(chord1, chord2, chord3, key):
            pattern = JazzPattern(
                pattern_type="ii-V-I",
                start_time=chord1['time'],
                duration=chord3['time'] + chord3.get('duration', 2.0) - chord1['time'],
                chords=[chord1['symbol'], chord2['symbol'], chord3['symbol']],
                key=key,
                confidence=0.95,
                metadata={
                    "progression_quality": "major" if "maj" in chord3['quality'] else "minor"
                }
            )
            patterns.append(pattern)
    
    return patterns


def _is_ii_v_i_pattern(chord1: Dict, chord2: Dict, chord3: Dict, key: str) -> bool:
    """Check if three chords form a ii-V-I pattern"""
    # Simplified implementation
    # In reality, would need full music theory analysis
    
    # Check root movement (up perfect 4th, up perfect 4th)
    # Example: D -> G -> C
    roots = [chord1['root'], chord2['root'], chord3['root']]
    
    # Common ii-V-I progressions
    major_progressions = [
        ["D", "G", "C"],
        ["A", "D", "G"],
        ["E", "A", "D"],
        ["B", "E", "A"],
        ["F#", "B", "E"],
        ["C#", "F#", "B"],
        ["G#", "C#", "F#"],
        ["Eb", "Ab", "Db"],
        ["Bb", "Eb", "Ab"],
        ["F", "Bb", "Eb"],
    ]
    
    return roots in major_progressions


def detect_turnarounds(chords: List[Dict]) -> List[JazzPattern]:
    """
    Detect turnaround progressions (I-VI-ii-V)
    
    Common in jazz endings and transitions.
    Example in C: Cmaj7 - Am7 - Dm7 - G7
    """
    patterns = []
    
    for i in range(len(chords) - 3):
        # Check 4-chord sequence
        sequence = chords[i:i+4]
        
        if _is_turnaround(sequence):
            pattern = JazzPattern(
                pattern_type="turnaround",
                start_time=sequence[0]['time'],
                duration=sequence[3]['time'] + sequence[3].get('duration', 1.0) - sequence[0]['time'],
                chords=[c['symbol'] for c in sequence],
                key="C",  # Detect actual key
                confidence=0.88,
                metadata={"variation": "standard"}
            )
            patterns.append(pattern)
    
    return patterns


def _is_turnaround(chords: List[Dict]) -> bool:
    """Check if 4 chords form a turnaround"""
    # Simplified check
    # I-VI-ii-V pattern
    turnaround_patterns = [
        ["C", "A", "D", "G"],
        ["G", "E", "A", "D"],
        ["F", "D", "G", "C"],
        ["Bb", "G", "C", "F"],
    ]
    
    roots = [c['root'] for c in chords]
    return roots in turnaround_patterns


def detect_tritone_substitutions(chords: List[Dict]) -> List[JazzPattern]:
    """
    Detect tritone substitutions
    
    Example: Instead of G7 -> Cmaj7, use Db7 -> Cmaj7
    The Db7 is a tritone away from G7
    """
    patterns = []
    
    for i in range(len(chords) - 1):
        chord1 = chords[i]
        chord2 = chords[i + 1]
        
        if _is_tritone_sub(chord1, chord2):
            pattern = JazzPattern(
                pattern_type="tritone_substitution",
                start_time=chord1['time'],
                duration=chord2['time'] + chord2.get('duration', 2.0) - chord1['time'],
                chords=[chord1['symbol'], chord2['symbol']],
                key="",  # Context-dependent
                confidence=0.85,
                metadata={
                    "original_dominant": _get_tritone_pair(chord1['root'])
                }
            )
            patterns.append(pattern)
    
    return patterns


def _is_tritone_sub(chord1: Dict, chord2: Dict) -> bool:
    """Check if chord1 is a tritone substitution"""
    # Check if chord1 is a dominant 7th
    if '7' not in chord1['quality'] or 'maj' in chord1['quality']:
        return False
    
    # Check interval to next chord (should resolve down half-step)
    # This is a simplified check
    return True  # Placeholder


def _get_tritone_pair(root: str) -> str:
    """Get the tritone (6 semitones away) of a root note"""
    tritone_pairs = {
        "C": "F#", "F#": "C",
        "Db": "G", "G": "Db",
        "D": "Ab", "Ab": "D",
        "Eb": "A", "A": "Eb",
        "E": "Bb", "Bb": "E",
        "F": "B", "B": "F",
    }
    return tritone_pairs.get(root, "")


def analyze_jazz_patterns(song_chords: List[Dict]) -> Dict:
    """
    Complete jazz pattern analysis
    
    Args:
        song_chords: List of chord dicts from transcription
    
    Returns:
        Dict with all detected patterns
    """
    results = {
        "ii_v_i_progressions": detect_ii_v_i_progressions(song_chords),
        "turnarounds": detect_turnarounds(song_chords),
        "tritone_substitutions": detect_tritone_substitutions(song_chords),
        "total_patterns": 0,
        "jazz_complexity_score": 0.0
    }
    
    # Calculate total patterns
    results["total_patterns"] = sum([
        len(results["ii_v_i_progressions"]),
        len(results["turnarounds"]),
        len(results["tritone_substitutions"])
    ])
    
    # Calculate jazz complexity (0-1 scale)
    # More patterns = more jazz-like
    if len(song_chords) > 0:
        results["jazz_complexity_score"] = min(1.0, results["total_patterns"] / (len(song_chords) / 4))
    
    return results
