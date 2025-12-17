"""
Shared utilities for all music generators.

This module consolidates duplicate logic found across multiple generator files,
following the DRY principle.
"""

import json
import re
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.core.config import settings
from app.gospel import Arrangement
from app.gospel.midi.enhanced_exporter import export_enhanced_midi
from app.schemas.gospel import MIDINoteInfo


def parse_json_from_response(text: str) -> Dict:
    """
    Extract JSON from LLM response text.

    Handles multiple formats:
    - JSON wrapped in markdown code blocks (```json ... ```)
    - Raw JSON text
    - JSON object within other text

    Args:
        text: Response text from LLM

    Returns:
        Parsed JSON dictionary

    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    # Try to find JSON block in markdown
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if json_match:
        return json.loads(json_match.group(1))

    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group(0))

    raise ValueError(f"Could not parse JSON from response: {text[:200]}")


def note_to_midi(note: str, octave: int = 4) -> int:
    """
    Convert note name to MIDI number.

    Supports formats:
    - 'C4', 'C#4', 'Db4' (with octave)
    - 'C', 'C#', 'Db' (uses default octave)

    Args:
        note: Note name (e.g., 'C4', 'C#', 'Db')
        octave: Default octave if not specified in note

    Returns:
        MIDI note number (0-127)
    """
    NOTE_TO_MIDI = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }

    # Parse note with optional octave
    match = re.match(r'^([A-G][#b]?)(\d)?$', note)
    if match:
        note_name = match.group(1)
        oct = int(match.group(2)) if match.group(2) else octave
        base = NOTE_TO_MIDI.get(note_name, 0)
        return 60 + base + (oct - 4) * 12  # Middle C (C4) = 60

    return 60  # Default to middle C


def export_to_midi(
    arrangement: Arrangement,
    output_subdir: str,
    filename_prefix: str
) -> Tuple[Path, str]:
    """
    Export arrangement to MIDI file with base64 encoding.

    Args:
        arrangement: Arrangement object to export
        output_subdir: Subdirectory under outputs/ (e.g., 'gospel_generated')
        filename_prefix: Prefix for filename (e.g., 'gospel')

    Returns:
        Tuple of (midi_path, midi_base64_string)
    """
    output_dir = settings.OUTPUTS_DIR / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    import time
    timestamp = int(time.time())
    filename = f"{filename_prefix}_{arrangement.key}_{arrangement.tempo}bpm_{timestamp}.mid"
    midi_path = output_dir / filename

    # Export to MIDI file
    export_enhanced_midi(arrangement, midi_path)

    # Read and encode as base64
    with open(midi_path, 'rb') as f:
        midi_bytes = f.read()
        midi_base64 = base64.b64encode(midi_bytes).decode('utf-8')

    return midi_path, midi_base64


def get_notes_preview(arrangement: Arrangement, bars: int = 4) -> List[Dict]:
    """
    Extract preview notes from first N bars of arrangement.

    Args:
        arrangement: Arrangement to preview
        bars: Number of bars to include (default 4)

    Returns:
        List of up to 100 note dictionaries from first N bars
    """
    beats_per_bar = arrangement.time_signature[0]
    max_time = bars * beats_per_bar

    # Get all notes within time range
    all_notes = arrangement.get_all_notes()
    preview_notes = [n for n in all_notes if n.time < max_time]

    # Convert to Dict and limit to 100 notes
    return [
        {
            "pitch": note.pitch,
            "time": note.time,
            "duration": note.duration,
            "velocity": note.velocity,
            "hand": note.hand
        }
        for note in preview_notes[:100]
    ]


def parse_description_fallback(
    description: str,
    key: Optional[str],
    tempo: Optional[int],
    default_chords: List[str],
    default_tempo: int = 120
) -> Tuple[List[str], str, int]:
    """
    Parse key and tempo from description text (fallback when LLM unavailable).

    Extracts:
    - Key signature (e.g., "C major", "Am", "D#")
    - Tempo (e.g., "120 bpm", "72bpm")

    Args:
        description: User's description text
        key: Explicit key override (optional)
        tempo: Explicit tempo override (optional)
        default_chords: Fallback chord progression for this genre
        default_tempo: Default tempo if not found (default 120)

    Returns:
        Tuple of (chords, key, tempo)
    """
    # Parse key from description
    key_match = re.search(
        r'\b([A-G][#b]?)\s*(major|minor|m)?\b',
        description,
        re.IGNORECASE
    )
    parsed_key = key or (key_match.group(1) if key_match else "C")

    # Parse tempo from description
    tempo_match = re.search(r'\b(\d{2,3})\s*bpm\b', description, re.IGNORECASE)
    parsed_tempo = tempo or (int(tempo_match.group(1)) if tempo_match else default_tempo)

    return default_chords, parsed_key, parsed_tempo
