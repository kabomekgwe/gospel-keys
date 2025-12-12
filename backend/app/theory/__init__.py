"""
Music Theory Library Package

Core data structures and utilities for comprehensive music theory analysis.
"""

from app.theory.interval_utils import (
    note_to_semitone,
    semitone_to_note,
    get_interval,
    get_interval_name,
    transpose,
    is_enharmonic,
    note_to_midi,
    midi_to_note,
    frequency_to_midi,
    midi_to_frequency,
)

from app.theory.scale_library import (
    Scale,
    get_scale,
    get_scale_notes,
    list_scales_by_category,
    SCALE_LIBRARY,
)

from app.theory.chord_library import (
    ChordType,
    get_chord_type,
    get_chord_notes,
    parse_chord_symbol,
    list_chords_by_category,
    CHORD_LIBRARY,
)

__all__ = [
    # Interval utilities
    "note_to_semitone",
    "semitone_to_note",
    "get_interval",
    "get_interval_name",
    "transpose",
    "is_enharmonic",
    "note_to_midi",
    "midi_to_note",
    "frequency_to_midi",
    "midi_to_frequency",
    # Scales
    "Scale",
    "get_scale",
    "get_scale_notes",
    "list_scales_by_category",
    "SCALE_LIBRARY",
    # Chords
    "ChordType",
    "get_chord_type",
    "get_chord_notes",
    "parse_chord_symbol",
    "list_chords_by_category",
    "CHORD_LIBRARY",
]
