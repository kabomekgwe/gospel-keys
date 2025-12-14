"""
Universal Progression Detector

Detects and classifies chord progressions across all genres:
- Pop progressions (I-V-vi-IV, vi-IV-I-V, etc.)
- Blues progressions (12-bar, 8-bar, quick-change, etc.)
- Jazz progressions (ii-V-I, rhythm changes, Coltrane changes, etc.)
- Modal progressions (Dorian, Mixolydian, Lydian vamps, etc.)
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.theory.interval_utils import note_to_semitone, get_interval


class ProgressionGenre(Enum):
    """Genre classification for progressions"""
    POP = "pop"
    BLUES = "blues"
    JAZZ = "jazz"
    MODAL = "modal"
    ROCK = "rock"
    CLASSICAL = "classical"
    UNKNOWN = "unknown"


@dataclass
class ProgressionMatch:
    """A matched chord progression pattern"""
    pattern_name: str
    genre: ProgressionGenre
    roman_numerals: List[str]
    start_index: int
    end_index: int
    key: str
    confidence: float
    description: str = ""
    metadata: Dict = field(default_factory=dict)


# ============================================================================
# PROGRESSION PATTERNS DATABASE
# ============================================================================

# Pop progressions - defined by root intervals from tonic
POP_PROGRESSIONS = {
    "axis_of_awesome": {
        "intervals": [0, 7, 9, 5],  # I-V-vi-IV (C-G-Am-F)
        "roman": ["I", "V", "vi", "IV"],
        "description": "The most common pop progression. 'Axis of Awesome' progression."
    },
    "sensitive_female": {
        "intervals": [9, 5, 0, 7],  # vi-IV-I-V
        "roman": ["vi", "IV", "I", "V"],
        "description": "Emotional pop progression. Starting on vi."
    },
    "50s_progression": {
        "intervals": [0, 9, 5, 7],  # I-vi-IV-V
        "roman": ["I", "vi", "IV", "V"],
        "description": "Classic 50s doo-wop progression."
    },
    "pop_punk": {
        "intervals": [0, 5, 7, 0],  # I-IV-V-I
        "roman": ["I", "IV", "V", "I"],
        "description": "Simple pop/punk progression."
    },
    "four_chord_minor": {
        "intervals": [0, 10, 8, 10],  # i-bVII-bVI-bVII
        "roman": ["i", "♭VII", "♭VI", "♭VII"],
        "description": "Minor key pop/rock progression."
    },
    "andalusian_cadence": {
        "intervals": [0, 10, 8, 7],  # i-bVII-bVI-V
        "roman": ["i", "♭VII", "♭VI", "V"],
        "description": "Andalusian (flamenco) cadence."
    },
    "pachelbel": {
        "intervals": [0, 7, 9, 4, 5, 0, 5, 7],  # I-V-vi-iii-IV-I-IV-V
        "roman": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],
        "description": "Pachelbel's Canon progression."
    },
}

# Blues progressions
BLUES_PROGRESSIONS = {
    "12_bar_basic": {
        "intervals": [0, 0, 0, 0, 5, 5, 0, 0, 7, 5, 0, 7],
        "roman": ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"],
        "description": "Standard 12-bar blues."
    },
    "12_bar_quick_change": {
        "intervals": [0, 5, 0, 0, 5, 5, 0, 0, 7, 5, 0, 7],
        "roman": ["I", "IV", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"],
        "description": "12-bar blues with quick IV in bar 2."
    },
    "8_bar_blues": {
        "intervals": [0, 0, 5, 5, 0, 7, 0, 7],
        "roman": ["I", "I", "IV", "IV", "I", "V", "I", "V"],
        "description": "8-bar blues form."
    },
    "minor_blues": {
        "intervals": [0, 0, 0, 0, 5, 5, 0, 0, 8, 7, 0, 7],
        "roman": ["i", "i", "i", "i", "iv", "iv", "i", "i", "♭VI", "V", "i", "V"],
        "description": "Minor blues progression."
    },
}

# Jazz progressions
JAZZ_PROGRESSIONS = {
    "ii_v_i_major": {
        "intervals": [2, 7, 0],  # ii-V-I
        "roman": ["ii", "V", "I"],
        "description": "The most common jazz progression.",
        "chord_qualities": ["m7", "7", "maj7"]
    },
    "ii_v_i_minor": {
        "intervals": [2, 7, 0],
        "roman": ["ii°", "V", "i"],
        "description": "ii-V-i in minor key.",
        "chord_qualities": ["m7b5", "7", "m7"]
    },
    "turnaround": {
        "intervals": [0, 9, 2, 7],  # I-vi-ii-V
        "roman": ["I", "vi", "ii", "V"],
        "description": "Standard jazz turnaround."
    },
    "rhythm_changes_a": {
        "intervals": [0, 9, 2, 7, 0, 9, 2, 7],
        "roman": ["I", "vi", "ii", "V", "I", "vi", "ii", "V"],
        "description": "Rhythm changes A section."
    },
    "rhythm_changes_b": {
        "intervals": [4, 4, 0, 0, 9, 9, 2, 7],
        "roman": ["III7", "III7", "VI7", "VI7", "II7", "II7", "V7", "V7"],
        "description": "Rhythm changes B section (bridge)."
    },
    "coltrane_changes": {
        "intervals": [0, 8, 4, 0],  # Bmaj7-D7-Gmaj7-Bb7 pattern (Giant Steps)
        "roman": ["I", "V7/♭VI", "♭VI", "V7/♭III"],
        "description": "Coltrane substitution pattern (Giant Steps)."
    },
    "backdoor": {
        "intervals": [10, 0],  # bVII7-I
        "roman": ["♭VII7", "I"],
        "description": "Backdoor resolution (bVII7 to I)."
    },
    "tritone_sub": {
        "intervals": [1, 0],  # bII7-I (tritone sub for V7)
        "roman": ["♭II7", "I"],
        "description": "Tritone substitution resolution."
    },
    "iii_vi_ii_v": {
        "intervals": [4, 9, 2, 7],
        "roman": ["iii", "vi", "ii", "V"],
        "description": "Extended circle progression."
    },
}

# Modal progressions
MODAL_PROGRESSIONS = {
    "dorian_vamp": {
        "intervals": [0, 2],  # i-II (Dorian)
        "roman": ["i", "II"],
        "description": "Dorian vamp (So What, Impressions)."
    },
    "mixolydian_vamp": {
        "intervals": [0, 10],  # I-bVII
        "roman": ["I", "♭VII"],
        "description": "Mixolydian vamp (Sweet Home Alabama feel)."
    },
    "lydian_vamp": {
        "intervals": [0, 2],  # I-II (Lydian context)
        "roman": ["I", "II"],
        "description": "Lydian progression with floating quality."
    },
    "phrygian_vamp": {
        "intervals": [0, 1],  # i-bII (Phrygian)
        "roman": ["i", "♭II"],
        "description": "Phrygian vamp (Spanish/Flamenco)."
    },
    "aeolian_rock": {
        "intervals": [0, 10, 8],  # i-bVII-bVI
        "roman": ["i", "♭VII", "♭VI"],
        "description": "Aeolian rock progression."
    },
}


def _get_root_interval(root1: str, root2: str) -> int:
    """Calculate interval between two chord roots in semitones"""
    return get_interval(root1, root2)


def _match_intervals(chord_roots: List[str], pattern_intervals: List[int]) -> Tuple[bool, str, float]:
    """
    Check if chord roots match a pattern of intervals.
    
    Returns:
        Tuple of (matches, detected_key, confidence)
    """
    if len(chord_roots) < len(pattern_intervals):
        return False, "", 0.0
    
    # Calculate actual intervals from first chord
    first_root = chord_roots[0]
    actual_intervals = [0]  # First chord is the reference
    
    for i in range(1, len(pattern_intervals)):
        if i >= len(chord_roots):
            return False, "", 0.0
        interval = _get_root_interval(first_root, chord_roots[i])
        actual_intervals.append(interval)
    
    # Check if intervals match the pattern
    # Account for different starting points (key detection)
    for key_offset in range(12):
        adjusted_pattern = [(p + key_offset) % 12 for p in pattern_intervals]
        
        # Normalize both to start from 0
        if adjusted_pattern[0] != 0:
            offset = adjusted_pattern[0]
            adjusted_pattern = [(p - offset) % 12 for p in adjusted_pattern]
        
        if actual_intervals == adjusted_pattern:
            # Detected key is the first chord root transposed by offset
            key_semitone = (note_to_semitone(first_root) - key_offset) % 12
            from app.theory.interval_utils import semitone_to_note
            detected_key = semitone_to_note(key_semitone)
            return True, detected_key, 0.9
    
    # Partial match check (allow one mismatch)
    mismatches = sum(1 for a, p in zip(actual_intervals, pattern_intervals) if a != p)
    if mismatches == 1 and len(pattern_intervals) >= 4:
        return True, first_root, 0.7  # Lower confidence for partial match
    
    return False, "", 0.0


def detect_progressions(
    chords: List[Dict],
    genres: Optional[List[ProgressionGenre]] = None
) -> List[ProgressionMatch]:
    """
    Detect chord progression patterns in a list of chords.
    
    Args:
        chords: List of chord dicts with 'root', 'quality', 'time', 'symbol'
        genres: Optional list of genres to search (None = all)
    
    Returns:
        List of matched progressions
    """
    if not chords:
        return []
    
    matches = []
    chord_roots = [c['root'] for c in chords]
    
    # All pattern databases to search
    pattern_dbs = []
    
    if genres is None or ProgressionGenre.POP in genres:
        pattern_dbs.append((POP_PROGRESSIONS, ProgressionGenre.POP))
    if genres is None or ProgressionGenre.BLUES in genres:
        pattern_dbs.append((BLUES_PROGRESSIONS, ProgressionGenre.BLUES))
    if genres is None or ProgressionGenre.JAZZ in genres:
        pattern_dbs.append((JAZZ_PROGRESSIONS, ProgressionGenre.JAZZ))
    if genres is None or ProgressionGenre.MODAL in genres:
        pattern_dbs.append((MODAL_PROGRESSIONS, ProgressionGenre.MODAL))
    
    # Slide window through chord sequence
    for db, genre in pattern_dbs:
        for pattern_name, pattern_data in db.items():
            pattern_len = len(pattern_data["intervals"])
            
            # Search for pattern at each position
            for start_idx in range(len(chord_roots) - pattern_len + 1):
                window = chord_roots[start_idx:start_idx + pattern_len]
                
                matched, key, confidence = _match_intervals(
                    window, pattern_data["intervals"]
                )
                
                if matched and confidence > 0.6:
                    matches.append(ProgressionMatch(
                        pattern_name=pattern_name,
                        genre=genre,
                        roman_numerals=pattern_data["roman"],
                        start_index=start_idx,
                        end_index=start_idx + pattern_len - 1,
                        key=key,
                        confidence=confidence,
                        description=pattern_data.get("description", ""),
                        metadata={
                            "chord_symbols": [chords[i].get('symbol', '') 
                                            for i in range(start_idx, start_idx + pattern_len)]
                        }
                    ))
    
    # Sort by confidence and remove overlapping duplicates
    matches.sort(key=lambda m: (-m.confidence, m.start_index))
    
    return _filter_overlapping(matches)


def _filter_overlapping(matches: List[ProgressionMatch]) -> List[ProgressionMatch]:
    """Remove overlapping matches, keeping highest confidence ones"""
    if not matches:
        return []
    
    filtered = []
    covered = set()
    
    for match in matches:
        # Check if this range is already covered
        match_range = set(range(match.start_index, match.end_index + 1))
        if not match_range.intersection(covered):
            filtered.append(match)
            covered.update(match_range)
    
    return filtered


def analyze_chord_sequence(chords: List[Dict]) -> Dict:
    """
    Comprehensive chord sequence analysis.
    
    Returns:
        Dict with detected progressions, key analysis, and genre likelihood
    """
    matches = detect_progressions(chords)
    
    # Calculate genre distribution
    genre_counts = {}
    for match in matches:
        genre = match.genre.value
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    # Determine likely key from matches
    key_votes = {}
    for match in matches:
        key_votes[match.key] = key_votes.get(match.key, 0) + match.confidence
    
    likely_key = max(key_votes.items(), key=lambda x: x[1])[0] if key_votes else None
    
    # Determine primary genre
    primary_genre = max(genre_counts.items(), key=lambda x: x[1])[0] if genre_counts else "unknown"
    
    return {
        "progressions": [
            {
                "pattern": m.pattern_name,
                "genre": m.genre.value,
                "roman_numerals": m.roman_numerals,
                "key": m.key,
                "confidence": m.confidence,
                "start_chord": m.start_index,
                "end_chord": m.end_index,
                "description": m.description,
                "chords": m.metadata.get("chord_symbols", [])
            }
            for m in matches
        ],
        "detected_key": likely_key,
        "primary_genre": primary_genre,
        "genre_distribution": genre_counts,
        "total_patterns_found": len(matches)
    }


def get_progression_info(pattern_name: str) -> Optional[Dict]:
    """Get information about a named progression pattern"""
    all_patterns = {
        **POP_PROGRESSIONS,
        **BLUES_PROGRESSIONS,
        **JAZZ_PROGRESSIONS,
        **MODAL_PROGRESSIONS,
    }
    return all_patterns.get(pattern_name)


def list_all_patterns() -> Dict[str, List[str]]:
    """List all available progression patterns by genre"""
    return {
        "pop": list(POP_PROGRESSIONS.keys()),
        "blues": list(BLUES_PROGRESSIONS.keys()),
        "jazz": list(JAZZ_PROGRESSIONS.keys()),
        "modal": list(MODAL_PROGRESSIONS.keys()),
    }


# ============================================================================
# ASYNC WRAPPERS FOR PIPELINE INTEGRATION
# ============================================================================

import asyncio
from typing import List


async def detect_progressions_async(chords: List, key: str = None) -> List[ProgressionMatch]:
    """
    Async wrapper for progression detection.
    
    Args:
        chords: List of ChordEvent objects from transcription
        key: Optional key hint for better matching
        
    Returns:
        List of detected progression patterns
    """
    def _detect():
        # Convert ChordEvent objects to dicts for the detector
        chord_dicts = []
        for chord in chords:
            chord_dicts.append({
                'root': chord.root,
                'quality': chord.quality,
                'time': chord.time,
                'symbol': chord.chord
            })
        
        # Run detection
        return detect_progressions(chord_dicts)
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _detect)
