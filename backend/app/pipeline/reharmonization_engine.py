"""
Reharmonization Engine

Suggests alternative chord harmonizations:
- Tritone substitution
- Diatonic substitutes
- Passing/approach chords
- Upper structure triads
- Backdoor progressions
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.theory.interval_utils import note_to_semitone, semitone_to_note, transpose
from app.theory.chord_library import get_chord_notes, get_chord_type


class ReharmonizationType(Enum):
    """Types of reharmonization"""
    TRITONE_SUB = "tritone_substitution"
    DIATONIC_SUB = "diatonic_substitution"
    PASSING_CHORD = "passing_chord"
    APPROACH_CHORD = "approach_chord"
    BACKDOOR = "backdoor"
    MODAL_INTERCHANGE = "modal_interchange"
    UPPER_STRUCTURE = "upper_structure"
    DIMINISHED = "diminished_passing"


@dataclass
class ReharmonizationSuggestion:
    """A single reharmonization suggestion"""
    original_chord: str
    suggested_chord: str
    reharmonization_type: ReharmonizationType
    explanation: str
    jazz_level: int  # 1-5, how "jazzy" the substitution is
    voice_leading_quality: str  # "smooth", "moderate", "dramatic"


def get_tritone_substitution(chord: Dict) -> Optional[ReharmonizationSuggestion]:
    """
    Get tritone substitution for a dominant 7th chord.
    
    Tritone sub replaces V7 with bII7 (6 semitones away).
    Example: G7 -> Db7 (both resolve to C)
    """
    root = chord.get('root', '')
    quality = chord.get('quality', '')
    
    # Only works for dominant 7th chords
    if '7' not in quality or 'maj' in quality or 'm' in quality:
        return None
    
    # Calculate tritone (6 semitones)
    original_semitone = note_to_semitone(root)
    tritone_semitone = (original_semitone + 6) % 12
    new_root = semitone_to_note(tritone_semitone, prefer_sharps=False)
    
    return ReharmonizationSuggestion(
        original_chord=f"{root}{quality}",
        suggested_chord=f"{new_root}7",
        reharmonization_type=ReharmonizationType.TRITONE_SUB,
        explanation=f"Tritone substitution: {root}7 and {new_root}7 share the same tritone (3rd and 7th swapped)",
        jazz_level=3,
        voice_leading_quality="smooth"
    )


def get_diatonic_substitutes(chord: Dict, key: str) -> List[ReharmonizationSuggestion]:
    """
    Get diatonic substitutions (chords with similar function).
    
    - I can be replaced by vi or iii (tonic function)
    - IV can be replaced by ii (subdominant function)
    - V can be replaced by vii° (dominant function)
    """
    root = chord.get('root', '')
    quality = chord.get('quality', '')
    chord_symbol = f"{root}{quality}"
    
    key_semitone = note_to_semitone(key)
    chord_semitone = note_to_semitone(root)
    interval = (chord_semitone - key_semitone) % 12
    
    suggestions = []
    
    # Tonic substitutes (I <-> vi <-> iii)
    if interval == 0:  # I chord
        suggestions.extend([
            ReharmonizationSuggestion(
                original_chord=chord_symbol,
                suggested_chord=f"{semitone_to_note((key_semitone + 9) % 12)}m7",
                reharmonization_type=ReharmonizationType.DIATONIC_SUB,
                explanation="vi is a common tonic substitute (relative minor)",
                jazz_level=1,
                voice_leading_quality="smooth"
            ),
            ReharmonizationSuggestion(
                original_chord=chord_symbol,
                suggested_chord=f"{semitone_to_note((key_semitone + 4) % 12)}m7",
                reharmonization_type=ReharmonizationType.DIATONIC_SUB,
                explanation="iii is a tonic substitute (mediant)",
                jazz_level=2,
                voice_leading_quality="moderate"
            ),
        ])
    
    # Subdominant substitutes (IV <-> ii)
    elif interval == 5:  # IV chord
        suggestions.append(ReharmonizationSuggestion(
            original_chord=chord_symbol,
            suggested_chord=f"{semitone_to_note((key_semitone + 2) % 12)}m7",
            reharmonization_type=ReharmonizationType.DIATONIC_SUB,
            explanation="ii is a common subdominant substitute",
            jazz_level=1,
            voice_leading_quality="smooth"
        ))
    elif interval == 2:  # ii chord
        suggestions.append(ReharmonizationSuggestion(
            original_chord=chord_symbol,
            suggested_chord=f"{semitone_to_note((key_semitone + 5) % 12)}maj7",
            reharmonization_type=ReharmonizationType.DIATONIC_SUB,
            explanation="IV is a common subdominant substitute",
            jazz_level=1,
            voice_leading_quality="smooth"
        ))
    
    # Dominant substitutes (V <-> vii°)
    elif interval == 7:  # V chord
        suggestions.append(ReharmonizationSuggestion(
            original_chord=chord_symbol,
            suggested_chord=f"{semitone_to_note((key_semitone + 11) % 12)}m7b5",
            reharmonization_type=ReharmonizationType.DIATONIC_SUB,
            explanation="vii° shares dominant function with V",
            jazz_level=2,
            voice_leading_quality="moderate"
        ))
    
    return suggestions


def get_passing_chords(chord1: Dict, chord2: Dict) -> List[ReharmonizationSuggestion]:
    """
    Suggest passing chords between two chords.
    
    Options:
    - Chromatic passing (half-step approach)
    - Diminished passing
    - Secondary dominant
    """
    root1 = chord1.get('root', '')
    root2 = chord2.get('root', '')
    quality2 = chord2.get('quality', '')
    
    s1 = note_to_semitone(root1)
    s2 = note_to_semitone(root2)
    interval = (s2 - s1) % 12
    
    suggestions = []
    chord1_symbol = f"{root1}{chord1.get('quality', '')}"
    chord2_symbol = f"{root2}{quality2}"
    
    # Chromatic approach from half step below
    approach_note = semitone_to_note((s2 - 1) % 12, prefer_sharps=False)
    suggestions.append(ReharmonizationSuggestion(
        original_chord=f"{chord1_symbol} → {chord2_symbol}",
        suggested_chord=f"{approach_note}7 → {chord2_symbol}",
        reharmonization_type=ReharmonizationType.APPROACH_CHORD,
        explanation=f"Chromatic approach: {approach_note}7 resolves up a half step",
        jazz_level=3,
        voice_leading_quality="smooth"
    ))
    
    # Diminished passing chord
    if interval == 2:  # Whole step apart
        passing_note = semitone_to_note((s1 + 1) % 12)
        suggestions.append(ReharmonizationSuggestion(
            original_chord=f"{chord1_symbol} → {chord2_symbol}",
            suggested_chord=f"{chord1_symbol} → {passing_note}dim7 → {chord2_symbol}",
            reharmonization_type=ReharmonizationType.DIMINISHED,
            explanation="Chromatic diminished passing chord",
            jazz_level=3,
            voice_leading_quality="smooth"
        ))
    
    # Secondary dominant approach
    secondary_dom_root = semitone_to_note((s2 + 7) % 12)
    suggestions.append(ReharmonizationSuggestion(
        original_chord=f"{chord1_symbol} → {chord2_symbol}",
        suggested_chord=f"{chord1_symbol} → {secondary_dom_root}7 → {chord2_symbol}",
        reharmonization_type=ReharmonizationType.APPROACH_CHORD,
        explanation=f"Secondary dominant: V7/{root2}",
        jazz_level=2,
        voice_leading_quality="moderate"
    ))
    
    return suggestions


def get_backdoor_substitution(chord: Dict, next_chord: Dict) -> Optional[ReharmonizationSuggestion]:
    """
    Suggest backdoor resolution (bVII7 -> I).
    
    Works when V7 resolves to I - can use bVII7 instead.
    """
    root = chord.get('root', '')
    quality = chord.get('quality', '')
    next_root = next_chord.get('root', '')
    
    # Check if this is V7 -> I motion
    if '7' not in quality or 'maj' in quality or 'm' in quality:
        return None
    
    interval = (note_to_semitone(next_root) - note_to_semitone(root)) % 12
    if interval != 5:  # Not a V-I motion
        return None
    
    # Calculate bVII (one whole step below I)
    backdoor_root = semitone_to_note((note_to_semitone(next_root) - 2) % 12, prefer_sharps=False)
    
    return ReharmonizationSuggestion(
        original_chord=f"{root}{quality}",
        suggested_chord=f"{backdoor_root}7",
        reharmonization_type=ReharmonizationType.BACKDOOR,
        explanation=f"Backdoor resolution: {backdoor_root}7 (bVII7) resolves to {next_root}",
        jazz_level=4,
        voice_leading_quality="smooth"
    )


def get_modal_interchange_options(chord: Dict, key: str) -> List[ReharmonizationSuggestion]:
    """
    Suggest borrowed chords from parallel modes.
    """
    chord_symbol = f"{chord.get('root', '')}{chord.get('quality', '')}"
    key_semitone = note_to_semitone(key)
    
    suggestions = []
    
    # Common borrowed chords from parallel minor
    borrowed = [
        (3, "♭III", "maj7", "Parallel minor - bright minor quality"),
        (8, "♭VI", "maj7", "Parallel minor - surprise major"),
        (10, "♭VII", "7", "Mixolydian/parallel minor - rock sound"),
        (5, "iv", "m7", "Minor subdominant - darker pre-dominant"),
    ]
    
    for interval, numeral, quality, desc in borrowed:
        root = semitone_to_note((key_semitone + interval) % 12, prefer_sharps=False)
        suggestions.append(ReharmonizationSuggestion(
            original_chord=chord_symbol,
            suggested_chord=f"{root}{quality}",
            reharmonization_type=ReharmonizationType.MODAL_INTERCHANGE,
            explanation=f"{numeral} borrowed chord: {desc}",
            jazz_level=2,
            voice_leading_quality="moderate"
        ))
    
    return suggestions


def reharmonize_progression(
    chords: List[Dict], 
    key: str,
    jazz_level: int = 3
) -> Dict:
    """
    Generate reharmonization suggestions for an entire progression.
    
    Args:
        chords: List of chord dicts
        key: Key center
        jazz_level: 1-5, how advanced the suggestions should be
    
    Returns:
        Dict with original progression and suggestions
    """
    if not chords:
        return {"error": "No chords provided"}
    
    all_suggestions = []
    
    for i, chord in enumerate(chords):
        chord_suggestions = []
        
        # Tritone subs (for dom7 chords)
        tritone = get_tritone_substitution(chord)
        if tritone and tritone.jazz_level <= jazz_level:
            chord_suggestions.append(tritone)
        
        # Diatonic substitutes
        diatonic = get_diatonic_substitutes(chord, key)
        chord_suggestions.extend([s for s in diatonic if s.jazz_level <= jazz_level])
        
        # Modal interchange
        if jazz_level >= 2:
            modal = get_modal_interchange_options(chord, key)
            chord_suggestions.extend([s for s in modal if s.jazz_level <= jazz_level])
        
        # Backdoor (needs next chord)
        if i < len(chords) - 1:
            backdoor = get_backdoor_substitution(chord, chords[i + 1])
            if backdoor and backdoor.jazz_level <= jazz_level:
                chord_suggestions.append(backdoor)
        
        # Passing chords (needs next chord)
        if i < len(chords) - 1 and jazz_level >= 3:
            passing = get_passing_chords(chord, chords[i + 1])
            chord_suggestions.extend([s for s in passing if s.jazz_level <= jazz_level])
        
        all_suggestions.append({
            "chord_index": i,
            "original": f"{chord.get('root', '')}{chord.get('quality', '')}",
            "suggestions": [
                {
                    "chord": s.suggested_chord,
                    "type": s.reharmonization_type.value,
                    "explanation": s.explanation,
                    "jazz_level": s.jazz_level,
                    "voice_leading": s.voice_leading_quality
                }
                for s in chord_suggestions
            ]
        })
    
    return {
        "key": key,
        "jazz_level": jazz_level,
        "original_progression": [
            f"{c.get('root', '')}{c.get('quality', '')}" for c in chords
        ],
        "reharmonization_options": all_suggestions,
        "total_suggestions": sum(len(s["suggestions"]) for s in all_suggestions)
    }


# ============================================================================
# ASYNC WRAPPERS FOR PIPELINE INTEGRATION
# ============================================================================

import asyncio


async def suggest_reharmonizations_async(chord_dict: Dict, key: str) -> List[ReharmonizationSuggestion]:
    """
    Async wrapper for generating reharmonization suggestions for a single chord.
    
    Args:
        chord_dict: Dict with 'root' and 'quality' keys
        key: Musical key context
        
    Returns:
        List of reharmonization suggestions
    """
    def _suggest():
        return get_all_reharmonizations_for_chord(chord_dict, key)
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _suggest)
