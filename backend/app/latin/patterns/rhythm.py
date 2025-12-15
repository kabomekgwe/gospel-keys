"""Latin Rhythm Transformations

Implements Latin/Afro-Cuban rhythm feel transformations:
- Clave patterns (son, rumba)
- Bossa nova
- Samba
- Salsa
- Afro-Cuban 6/8

Key Concepts:
- Clave: 2-bar pattern that drives Latin music
- Son clave: 3-2 or 2-3 pattern (most common)
- Rumba clave: Slightly different from son
- Cascara: Timbale pattern
- Montuno: Piano comp pattern
"""

from typing import List
from app.gospel import Note


def apply_son_clave_3_2(notes: List[Note]) -> List[Note]:
    """Apply 3-2 son clave rhythm emphasis.

    Son clave (3-2): Most common clave pattern
    Bar 1: 3 hits (beat 1, & of 2, 4)
    Bar 2: 2 hits (& of 2, 3)

    Args:
        notes: Notes to transform

    Returns:
        Notes with clave emphasis applied
    """
    clave_notes = []

    for note in notes:
        # Determine position in 2-bar phrase (8 beats total)
        phrase_position = note.time % 8.0

        # 3-2 Son Clave hits:
        # Bar 1 (0-4): 0, 2.5, 3.5
        # Bar 2 (4-8): 6.5, 7
        clave_hits = [0, 2.5, 3.5, 6.5, 7.0]

        # Check if note is near a clave hit (within 0.15 beats)
        is_clave_hit = any(abs(phrase_position - hit) < 0.15 for hit in clave_hits)

        if is_clave_hit:
            # Emphasize clave hits
            clave_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 0.9,  # Shorter for articulation
                velocity=min(note.velocity + 12, 127),  # Louder
                hand=note.hand
            )
        else:
            # De-emphasize non-clave notes
            clave_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(note.velocity - 8, 30),  # Softer
                hand=note.hand
            )

        clave_notes.append(clave_note)

    return clave_notes


def apply_rumba_clave_3_2(notes: List[Note]) -> List[Note]:
    """Apply 3-2 rumba clave rhythm emphasis.

    Rumba clave (3-2): Similar to son but third hit is delayed
    Bar 1: 3 hits (beat 1, & of 2, & of 4)
    Bar 2: 2 hits (& of 2, 3)

    Args:
        notes: Notes to transform

    Returns:
        Notes with rumba clave emphasis
    """
    clave_notes = []

    for note in notes:
        phrase_position = note.time % 8.0

        # 3-2 Rumba Clave hits:
        # Bar 1 (0-4): 0, 2.5, 4.5 (different from son)
        # Bar 2 (4-8): 6.5, 7.0
        clave_hits = [0, 2.5, 4.5, 6.5, 7.0]

        is_clave_hit = any(abs(phrase_position - hit) < 0.15 for hit in clave_hits)

        if is_clave_hit:
            clave_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 0.9,
                velocity=min(note.velocity + 12, 127),
                hand=note.hand
            )
        else:
            clave_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(note.velocity - 8, 30),
                hand=note.hand
            )

        clave_notes.append(clave_note)

    return clave_notes


def apply_bossa_nova(notes: List[Note]) -> List[Note]:
    """Apply bossa nova rhythm feel.

    Bossa nova: Brazilian style with syncopated bass pattern
    Typical pattern emphasizes: 1, & of 2, 4

    Args:
        notes: Notes to transform

    Returns:
        Notes with bossa nova feel
    """
    bossa_notes = []

    for note in notes:
        beat_position = note.time % 4.0

        # Bossa nova emphasis points: 0, 2.5, 3.0
        bossa_hits = [0, 2.5, 3.0]

        is_bossa_hit = any(abs(beat_position - hit) < 0.15 for hit in bossa_hits)

        if is_bossa_hit:
            # Emphasize bossa pattern
            bossa_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 0.85,  # Shorter, articulate
                velocity=min(note.velocity + 10, 127),
                hand=note.hand
            )
        else:
            # Softer on non-pattern notes
            bossa_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(note.velocity - 5, 35),
                hand=note.hand
            )

        bossa_notes.append(bossa_note)

    return bossa_notes


def apply_samba(notes: List[Note]) -> List[Note]:
    """Apply samba rhythm feel.

    Samba: Fast Brazilian 2/4 with continuous 16th notes
    Emphasizes certain 16th-note subdivisions

    Args:
        notes: Notes to transform

    Returns:
        Notes with samba feel
    """
    samba_notes = []

    for note in notes:
        # Quantize to 16th notes
        sixteenth_position = round(note.time * 4) / 4

        # Samba emphasis pattern (in 16ths per beat)
        # 1 e & a -> emphasize 1, &
        beat_in_sixteenths = (note.time * 4) % 4
        is_emphasized = beat_in_sixteenths in [0, 2]  # 1, &

        if is_emphasized:
            samba_note = Note(
                pitch=note.pitch,
                time=sixteenth_position,
                duration=note.duration * 0.75,
                velocity=min(note.velocity + 8, 127),
                hand=note.hand
            )
        else:
            samba_note = Note(
                pitch=note.pitch,
                time=sixteenth_position,
                duration=note.duration * 0.7,
                velocity=max(note.velocity - 5, 40),
                hand=note.hand
            )

        samba_notes.append(samba_note)

    return samba_notes


def apply_cascara(notes: List[Note]) -> List[Note]:
    """Apply cascara (timbale) rhythm pattern.

    Cascara: Salsa/Cuban timbale pattern
    2-bar pattern with specific rhythmic accents

    Args:
        notes: Notes to transform

    Returns:
        Notes with cascara pattern emphasis
    """
    cascara_notes = []

    for note in notes:
        phrase_position = note.time % 8.0

        # Cascara pattern hits (2-bar, 8-beat cycle)
        # Simplified version: 0, 1, 2.5, 3.5, 4, 5, 6.5, 7.5
        cascara_hits = [0, 1, 2.5, 3.5, 4, 5, 6.5, 7.5]

        is_cascara_hit = any(abs(phrase_position - hit) < 0.15 for hit in cascara_hits)

        if is_cascara_hit:
            cascara_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 0.8,
                velocity=min(note.velocity + 10, 127),
                hand=note.hand
            )
        else:
            cascara_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(note.velocity - 10, 30),
                hand=note.hand
            )

        cascara_notes.append(cascara_note)

    return cascara_notes


def apply_montuno(notes: List[Note]) -> List[Note]:
    """Apply montuno piano pattern.

    Montuno: Syncopated piano comp pattern in salsa/Cuban music
    Typically emphasizes off-beats and creates rhythmic drive

    Args:
        notes: Notes to transform

    Returns:
        Notes with montuno pattern
    """
    montuno_notes = []

    for note in notes:
        beat_position = note.time % 4.0

        # Montuno typically emphasizes: & of 1, & of 2, & of 3, 4
        # Positions: 0.5, 1.5, 2.5, 3.0
        montuno_hits = [0.5, 1.5, 2.5, 3.0]

        is_montuno_hit = any(abs(beat_position - hit) < 0.15 for hit in montuno_hits)

        if is_montuno_hit:
            montuno_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration * 0.85,
                velocity=min(note.velocity + 8, 127),
                hand=note.hand
            )
        else:
            montuno_note = Note(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=max(note.velocity - 6, 35),
                hand=note.hand
            )

        montuno_notes.append(montuno_note)

    return montuno_notes


def apply_afro_cuban_6_8(notes: List[Note]) -> List[Note]:
    """Apply Afro-Cuban 6/8 feel.

    6/8 Afro-Cuban: Compound meter common in rumba, bembe
    2 dotted-quarter pulses per bar

    Args:
        notes: Notes to transform

    Returns:
        Notes quantized to 6/8 grid
    """
    six_eight_notes = []

    for note in notes:
        # 6/8: 2 pulses per bar, each divided into 3
        # Subdivision: 1/3 beat (0.333...)
        subdivision = 1.0 / 3  # Each eighth note in 6/8

        # Quantize to nearest subdivision
        quantized_time = round(note.time / subdivision) * subdivision

        six_eight_note = Note(
            pitch=note.pitch,
            time=quantized_time,
            duration=note.duration,
            velocity=note.velocity,
            hand=note.hand
        )
        six_eight_notes.append(six_eight_note)

    return six_eight_notes


def apply_latin_rhythm_pattern(notes: List[Note], pattern_name: str) -> List[Note]:
    """Apply Latin rhythm pattern transformation.

    Args:
        notes: Notes to transform
        pattern_name: Name of rhythm pattern
                     - "son_clave": 3-2 son clave
                     - "rumba_clave": 3-2 rumba clave
                     - "bossa_nova": Brazilian bossa
                     - "samba": Brazilian samba
                     - "cascara": Salsa timbale pattern
                     - "montuno": Piano comp pattern
                     - "6_8": Afro-Cuban 6/8

    Returns:
        Transformed notes

    Raises:
        ValueError: If pattern name not found
    """
    if pattern_name == "son_clave":
        return apply_son_clave_3_2(notes)
    elif pattern_name == "rumba_clave":
        return apply_rumba_clave_3_2(notes)
    elif pattern_name == "bossa_nova":
        return apply_bossa_nova(notes)
    elif pattern_name == "samba":
        return apply_samba(notes)
    elif pattern_name == "cascara":
        return apply_cascara(notes)
    elif pattern_name == "montuno":
        return apply_montuno(notes)
    elif pattern_name == "6_8":
        return apply_afro_cuban_6_8(notes)
    else:
        raise ValueError(
            f"Unknown Latin rhythm pattern: {pattern_name}. "
            f"Available: son_clave, rumba_clave, bossa_nova, samba, cascara, montuno, 6_8"
        )


__all__ = [
    "apply_son_clave_3_2",
    "apply_rumba_clave_3_2",
    "apply_bossa_nova",
    "apply_samba",
    "apply_cascara",
    "apply_montuno",
    "apply_afro_cuban_6_8",
    "apply_latin_rhythm_pattern",
]
