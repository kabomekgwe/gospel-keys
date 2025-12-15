"""Simple chord symbol parser for Phase 6 integration"""

import re
from typing import Dict, Optional


def parse_chord_symbol(chord_symbol: str) -> Dict[str, str]:
    """Parse a chord symbol into root and quality components

    Args:
        chord_symbol: Chord symbol like "Cmaj7", "Dm7", "G7", "C"

    Returns:
        Dict with 'root' and 'quality' keys

    Examples:
        >>> parse_chord_symbol("Cmaj7")
        {'root': 'C', 'quality': 'maj7'}
        >>> parse_chord_symbol("Dm7")
        {'root': 'D', 'quality': 'm7'}
        >>> parse_chord_symbol("G7")
        {'root': 'G', 'quality': '7'}
        >>> parse_chord_symbol("C")
        {'root': 'C', 'quality': ''}
    """
    if not chord_symbol:
        return {'root': 'C', 'quality': ''}

    # Match root note (letter + optional accidental)
    match = re.match(r'^([A-G][#b]?)', chord_symbol)
    if not match:
        # Fallback
        return {'root': chord_symbol, 'quality': ''}

    root = match.group(1)
    quality = chord_symbol[len(root):]

    return {
        'root': root,
        'quality': quality
    }
