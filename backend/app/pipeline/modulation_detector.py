"""
Modulation Detector

Detects key changes/modulations in chord progressions:
- Pivot chord modulation
- Direct modulation
- Common-tone modulation
- Chromatic modulation
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.theory.interval_utils import note_to_semitone, get_interval, semitone_to_note
from app.pipeline.cadence_detector import detect_cadences, CadenceType


class ModulationType(Enum):
    """Types of modulation"""
    PIVOT = "pivot"           # Common chord between keys
    DIRECT = "direct"         # Abrupt key change
    COMMON_TONE = "common_tone"  # Shared note
    CHROMATIC = "chromatic"   # Chromatic voice leading
    SEQUENTIAL = "sequential" # Sequence moves to new key
    ENHARMONIC = "enharmonic" # Enharmonic reinterpretation


@dataclass
class ModulationEvent:
    """A detected modulation"""
    from_key: str
    to_key: str
    modulation_type: ModulationType
    pivot_chord: Optional[str]
    chord_index: int
    confidence: float
    relationship: str  # e.g., "up_5th", "relative_minor"


# Key relationships by interval
KEY_RELATIONSHIPS = {
    0: "same",
    1: "half_step_up",
    2: "whole_step_up",
    3: "minor_third_up",
    4: "major_third_up",
    5: "fourth_up",
    7: "fifth_up",
    8: "minor_sixth_up",
    9: "relative_minor/major",
    10: "minor_seventh_up",
    11: "half_step_down",
}


def detect_modulations(
    chords: List[Dict], 
    initial_key: Optional[str] = None
) -> List[ModulationEvent]:
    """
    Detect modulations in a chord progression.
    
    Args:
        chords: List of chord dicts with 'root', 'quality', 'time'
        initial_key: Starting key (auto-detected if None)
    
    Returns:
        List of detected modulation events
    """
    if len(chords) < 4:
        return []
    
    # Detect initial key
    if initial_key is None:
        initial_key = _estimate_initial_key(chords[:8])
    
    modulations = []
    current_key = initial_key
    
    # Sliding window analysis
    window_size = 4
    
    for i in range(len(chords) - window_size):
        window = chords[i:i + window_size + 1]
        
        # Check for cadence in different key
        cadences = detect_cadences(window)
        
        for cadence in cadences:
            if cadence.key != current_key:
                # Potential modulation detected
                mod_type, pivot = _classify_modulation(
                    chords[max(0, i-1):i+2],
                    current_key,
                    cadence.key
                )
                
                if mod_type:
                    interval = get_interval(current_key, cadence.key)
                    relationship = KEY_RELATIONSHIPS.get(interval, f"interval_{interval}")
                    
                    modulations.append(ModulationEvent(
                        from_key=current_key,
                        to_key=cadence.key,
                        modulation_type=mod_type,
                        pivot_chord=pivot,
                        chord_index=i,
                        confidence=cadence.confidence if hasattr(cadence, 'confidence') else 0.7,
                        relationship=relationship
                    ))
                    
                    current_key = cadence.key
    
    # Second pass: look for tonicization patterns (V-I in non-tonic key)
    tonicizations = _detect_tonicizations(chords, initial_key)
    
    # Filter overlapping modulations and tonicizations
    return _filter_modulations(modulations)


def _estimate_initial_key(chords: List[Dict]) -> str:
    """Estimate the initial key from first few chords"""
    if not chords:
        return "C"
    
    # Look for strong cadence
    cadences = detect_cadences(chords)
    if cadences:
        return cadences[0].key
    
    # Fallback to first chord root
    return chords[0]['root']


def _classify_modulation(
    chords: List[Dict],
    from_key: str,
    to_key: str
) -> Tuple[Optional[ModulationType], Optional[str]]:
    """
    Classify the type of modulation.
    
    Returns:
        Tuple of (modulation type, pivot chord if applicable)
    """
    if not chords:
        return None, None
    
    from_semitone = note_to_semitone(from_key)
    to_semitone = note_to_semitone(to_key)
    
    # Check each chord as potential pivot
    for chord in chords:
        root = chord['root']
        quality = chord.get('quality', '')
        chord_semitone = note_to_semitone(root)
        
        # Interval in old key
        old_interval = (chord_semitone - from_semitone) % 12
        # Interval in new key
        new_interval = (chord_semitone - to_semitone) % 12
        
        # Check if chord is diatonic in both keys (pivot chord)
        diatonic_old = old_interval in [0, 2, 4, 5, 7, 9, 11]
        diatonic_new = new_interval in [0, 2, 4, 5, 7, 9, 11]
        
        if diatonic_old and diatonic_new:
            return ModulationType.PIVOT, f"{root}{quality}"
    
    # Check for chromatic relationship
    key_interval = get_interval(from_key, to_key)
    if key_interval in [1, 11]:  # Half step
        return ModulationType.CHROMATIC, None
    
    # Check for common tone
    # (Simplified: same root note)
    for chord in chords:
        if chord['root'] == from_key or chord['root'] == to_key:
            return ModulationType.COMMON_TONE, f"{chord['root']}{chord.get('quality', '')}"
    
    # Default to direct modulation
    return ModulationType.DIRECT, None


def _detect_tonicizations(chords: List[Dict], key: str) -> List[Dict]:
    """
    Detect temporary tonicizations (brief touches of other keys).
    These are not full modulations but secondary dominant resolutions.
    """
    tonicizations = []
    key_semitone = note_to_semitone(key)
    
    for i in range(len(chords) - 1):
        chord1 = chords[i]
        chord2 = chords[i + 1]
        
        # Check for V-I motion to non-tonic chord
        quality1 = chord1.get('quality', '')
        
        if '7' in quality1 and 'maj' not in quality1:
            # Dominant seventh - check resolution
            interval = get_interval(chord1['root'], chord2['root'])
            
            if interval == 5:  # Up a P4 (down a P5)
                # This is a V-I motion
                target_interval = (note_to_semitone(chord2['root']) - key_semitone) % 12
                
                if target_interval != 0:  # Not resolving to tonic
                    tonicizations.append({
                        "index": i,
                        "secondary_dominant": f"{chord1['root']}{quality1}",
                        "target": f"{chord2['root']}{chord2.get('quality', '')}",
                        "target_degree": target_interval
                    })
    
    return tonicizations


def _filter_modulations(modulations: List[ModulationEvent]) -> List[ModulationEvent]:
    """Remove overlapping or low-confidence modulations"""
    if not modulations:
        return []
    
    # Sort by confidence
    sorted_mods = sorted(modulations, key=lambda m: -m.confidence)
    
    # Remove overlaps (keep higher confidence)
    filtered = []
    covered_indices = set()
    
    for mod in sorted_mods:
        if mod.chord_index not in covered_indices:
            filtered.append(mod)
            # Mark nearby indices as covered
            for j in range(mod.chord_index - 1, mod.chord_index + 3):
                covered_indices.add(j)
    
    # Sort by position
    return sorted(filtered, key=lambda m: m.chord_index)


def analyze_key_structure(chords: List[Dict]) -> Dict:
    """
    Comprehensive key and modulation analysis.
    
    Returns:
        Dict with key areas, modulations, and tonal structure
    """
    if not chords:
        return {"error": "No chords provided"}
    
    # Detect initial key
    initial_key = _estimate_initial_key(chords[:8])
    
    # Detect modulations
    modulations = detect_modulations(chords, initial_key)
    
    # Build key area map
    key_areas = []
    current_key = initial_key
    current_start = 0
    
    for mod in modulations:
        key_areas.append({
            "key": current_key,
            "start_chord": current_start,
            "end_chord": mod.chord_index - 1,
            "duration_chords": mod.chord_index - current_start
        })
        current_key = mod.to_key
        current_start = mod.chord_index
    
    # Add final key area
    key_areas.append({
        "key": current_key,
        "start_chord": current_start,
        "end_chord": len(chords) - 1,
        "duration_chords": len(chords) - current_start
    })
    
    return {
        "initial_key": initial_key,
        "final_key": current_key,
        "key_areas": key_areas,
        "modulations": [
            {
                "from": m.from_key,
                "to": m.to_key,
                "type": m.modulation_type.value,
                "pivot": m.pivot_chord,
                "at_chord": m.chord_index,
                "relationship": m.relationship
            }
            for m in modulations
        ],
        "total_modulations": len(modulations),
        "is_monotonal": len(modulations) == 0,
        "key_diversity": len(set(ka["key"] for ka in key_areas))
    }
