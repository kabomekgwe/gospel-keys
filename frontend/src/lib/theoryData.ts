/**
 * Theory Data Library
 * 
 * Static definitions for chords, scales, intervals, and music theory concepts
 */

// ============================================================================
// Note and Pitch Utilities
// ============================================================================

export const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] as const;
export const NOTE_NAMES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'] as const;

export type NoteName = typeof NOTE_NAMES[number];

export function noteNameToMidi(note: string, octave: number = 4): number {
    const baseName = note.replace(/[0-9]/g, '').toUpperCase();
    let index = NOTE_NAMES.indexOf(baseName as NoteName);
    if (index === -1) {
        index = NOTE_NAMES_FLAT.indexOf(baseName as any);
    }
    if (index === -1) return 60; // Default to middle C
    return index + (octave + 1) * 12;
}

export function midiToNoteName(midi: number, preferFlats = false): string {
    const octave = Math.floor(midi / 12) - 1;
    const noteIndex = midi % 12;
    const noteName = preferFlats ? NOTE_NAMES_FLAT[noteIndex] : NOTE_NAMES[noteIndex];
    return `${noteName}${octave}`;
}

// ============================================================================
// Interval Definitions
// ============================================================================

export interface IntervalInfo {
    semitones: number;
    name: string;
    shortName: string;
    quality: 'perfect' | 'major' | 'minor' | 'augmented' | 'diminished';
}

export const INTERVALS: Record<string, IntervalInfo> = {
    'P1': { semitones: 0, name: 'Unison', shortName: 'P1', quality: 'perfect' },
    'm2': { semitones: 1, name: 'Minor 2nd', shortName: 'm2', quality: 'minor' },
    'M2': { semitones: 2, name: 'Major 2nd', shortName: 'M2', quality: 'major' },
    'm3': { semitones: 3, name: 'Minor 3rd', shortName: 'm3', quality: 'minor' },
    'M3': { semitones: 4, name: 'Major 3rd', shortName: 'M3', quality: 'major' },
    'P4': { semitones: 5, name: 'Perfect 4th', shortName: 'P4', quality: 'perfect' },
    'A4': { semitones: 6, name: 'Tritone', shortName: 'TT', quality: 'augmented' },
    'd5': { semitones: 6, name: 'Tritone', shortName: 'TT', quality: 'diminished' },
    'P5': { semitones: 7, name: 'Perfect 5th', shortName: 'P5', quality: 'perfect' },
    'm6': { semitones: 8, name: 'Minor 6th', shortName: 'm6', quality: 'minor' },
    'M6': { semitones: 9, name: 'Major 6th', shortName: 'M6', quality: 'major' },
    'm7': { semitones: 10, name: 'Minor 7th', shortName: 'm7', quality: 'minor' },
    'M7': { semitones: 11, name: 'Major 7th', shortName: 'M7', quality: 'major' },
    'P8': { semitones: 12, name: 'Octave', shortName: 'P8', quality: 'perfect' },
};

// ============================================================================
// Chord Definitions
// ============================================================================

export interface ChordDefinition {
    intervals: number[];
    name: string;
    shortName: string;
    category: 'triad' | 'seventh' | 'extended' | 'altered' | 'power' | 'sus';
    notes?: string[]; // Optional: specific voicing
}

export const CHORD_TYPES: Record<string, ChordDefinition> = {
    // Triads
    'maj': { intervals: [0, 4, 7], name: 'Major', shortName: '', category: 'triad' },
    'min': { intervals: [0, 3, 7], name: 'Minor', shortName: 'm', category: 'triad' },
    'dim': { intervals: [0, 3, 6], name: 'Diminished', shortName: '°', category: 'triad' },
    'aug': { intervals: [0, 4, 8], name: 'Augmented', shortName: '+', category: 'triad' },

    // Seventh Chords
    'maj7': { intervals: [0, 4, 7, 11], name: 'Major 7th', shortName: 'maj7', category: 'seventh' },
    'min7': { intervals: [0, 3, 7, 10], name: 'Minor 7th', shortName: 'm7', category: 'seventh' },
    '7': { intervals: [0, 4, 7, 10], name: 'Dominant 7th', shortName: '7', category: 'seventh' },
    'dim7': { intervals: [0, 3, 6, 9], name: 'Diminished 7th', shortName: '°7', category: 'seventh' },
    'hdim7': { intervals: [0, 3, 6, 10], name: 'Half-Diminished', shortName: 'ø7', category: 'seventh' },
    'minmaj7': { intervals: [0, 3, 7, 11], name: 'Minor-Major 7th', shortName: 'mM7', category: 'seventh' },
    'aug7': { intervals: [0, 4, 8, 10], name: 'Augmented 7th', shortName: '+7', category: 'seventh' },

    // Extended Chords
    '9': { intervals: [0, 4, 7, 10, 14], name: 'Dominant 9th', shortName: '9', category: 'extended' },
    'maj9': { intervals: [0, 4, 7, 11, 14], name: 'Major 9th', shortName: 'maj9', category: 'extended' },
    'min9': { intervals: [0, 3, 7, 10, 14], name: 'Minor 9th', shortName: 'm9', category: 'extended' },
    '11': { intervals: [0, 4, 7, 10, 14, 17], name: 'Dominant 11th', shortName: '11', category: 'extended' },
    '13': { intervals: [0, 4, 7, 10, 14, 17, 21], name: 'Dominant 13th', shortName: '13', category: 'extended' },

    // Suspended Chords
    'sus2': { intervals: [0, 2, 7], name: 'Suspended 2nd', shortName: 'sus2', category: 'sus' },
    'sus4': { intervals: [0, 5, 7], name: 'Suspended 4th', shortName: 'sus4', category: 'sus' },
    '7sus4': { intervals: [0, 5, 7, 10], name: 'Dominant 7th sus4', shortName: '7sus4', category: 'sus' },

    // Added Tone Chords
    'add9': { intervals: [0, 4, 7, 14], name: 'Add 9', shortName: 'add9', category: 'extended' },
    'add11': { intervals: [0, 4, 7, 17], name: 'Add 11', shortName: 'add11', category: 'extended' },
    '6': { intervals: [0, 4, 7, 9], name: 'Major 6th', shortName: '6', category: 'extended' },
    'min6': { intervals: [0, 3, 7, 9], name: 'Minor 6th', shortName: 'm6', category: 'extended' },

    // Power Chord
    '5': { intervals: [0, 7], name: 'Power Chord', shortName: '5', category: 'power' },

    // Altered Chords
    '7b5': { intervals: [0, 4, 6, 10], name: 'Dominant 7th flat 5', shortName: '7♭5', category: 'altered' },
    '7#5': { intervals: [0, 4, 8, 10], name: 'Dominant 7th sharp 5', shortName: '7♯5', category: 'altered' },
    '7b9': { intervals: [0, 4, 7, 10, 13], name: 'Dominant 7th flat 9', shortName: '7♭9', category: 'altered' },
    '7#9': { intervals: [0, 4, 7, 10, 15], name: 'Dominant 7th sharp 9', shortName: '7♯9', category: 'altered' },
};

// ============================================================================
// Scale Definitions
// ============================================================================

export interface ScaleDefinition {
    intervals: number[];
    name: string;
    category: 'major' | 'minor' | 'modes' | 'pentatonic' | 'blues' | 'jazz' | 'exotic';
    degrees: string[];
    chordQualities?: string[]; // Chord qualities built on each degree
}

export const SCALES: Record<string, ScaleDefinition> = {
    // Major and Minor
    'major': {
        intervals: [0, 2, 4, 5, 7, 9, 11],
        name: 'Major (Ionian)',
        category: 'major',
        degrees: ['1', '2', '3', '4', '5', '6', '7'],
        chordQualities: ['maj7', 'min7', 'min7', 'maj7', '7', 'min7', 'hdim7'],
    },
    'natural_minor': {
        intervals: [0, 2, 3, 5, 7, 8, 10],
        name: 'Natural Minor (Aeolian)',
        category: 'minor',
        degrees: ['1', '2', '♭3', '4', '5', '♭6', '♭7'],
        chordQualities: ['min7', 'hdim7', 'maj7', 'min7', 'min7', 'maj7', '7'],
    },
    'harmonic_minor': {
        intervals: [0, 2, 3, 5, 7, 8, 11],
        name: 'Harmonic Minor',
        category: 'minor',
        degrees: ['1', '2', '♭3', '4', '5', '♭6', '7'],
    },
    'melodic_minor': {
        intervals: [0, 2, 3, 5, 7, 9, 11],
        name: 'Melodic Minor',
        category: 'minor',
        degrees: ['1', '2', '♭3', '4', '5', '6', '7'],
    },

    // Modes
    'dorian': {
        intervals: [0, 2, 3, 5, 7, 9, 10],
        name: 'Dorian',
        category: 'modes',
        degrees: ['1', '2', '♭3', '4', '5', '6', '♭7'],
    },
    'phrygian': {
        intervals: [0, 1, 3, 5, 7, 8, 10],
        name: 'Phrygian',
        category: 'modes',
        degrees: ['1', '♭2', '♭3', '4', '5', '♭6', '♭7'],
    },
    'lydian': {
        intervals: [0, 2, 4, 6, 7, 9, 11],
        name: 'Lydian',
        category: 'modes',
        degrees: ['1', '2', '3', '♯4', '5', '6', '7'],
    },
    'mixolydian': {
        intervals: [0, 2, 4, 5, 7, 9, 10],
        name: 'Mixolydian',
        category: 'modes',
        degrees: ['1', '2', '3', '4', '5', '6', '♭7'],
    },
    'locrian': {
        intervals: [0, 1, 3, 5, 6, 8, 10],
        name: 'Locrian',
        category: 'modes',
        degrees: ['1', '♭2', '♭3', '4', '♭5', '♭6', '♭7'],
    },

    // Pentatonic
    'major_pentatonic': {
        intervals: [0, 2, 4, 7, 9],
        name: 'Major Pentatonic',
        category: 'pentatonic',
        degrees: ['1', '2', '3', '5', '6'],
    },
    'minor_pentatonic': {
        intervals: [0, 3, 5, 7, 10],
        name: 'Minor Pentatonic',
        category: 'pentatonic',
        degrees: ['1', '♭3', '4', '5', '♭7'],
    },

    // Blues
    'blues': {
        intervals: [0, 3, 5, 6, 7, 10],
        name: 'Blues Scale',
        category: 'blues',
        degrees: ['1', '♭3', '4', '♭5', '5', '♭7'],
    },
    'major_blues': {
        intervals: [0, 2, 3, 4, 7, 9],
        name: 'Major Blues',
        category: 'blues',
        degrees: ['1', '2', '♭3', '3', '5', '6'],
    },

    // Jazz Scales
    'bebop_dominant': {
        intervals: [0, 2, 4, 5, 7, 9, 10, 11],
        name: 'Bebop Dominant',
        category: 'jazz',
        degrees: ['1', '2', '3', '4', '5', '6', '♭7', '7'],
    },
    'altered': {
        intervals: [0, 1, 3, 4, 6, 8, 10],
        name: 'Altered (Super Locrian)',
        category: 'jazz',
        degrees: ['1', '♭2', '♭3', '♭4', '♭5', '♭6', '♭7'],
    },
    'whole_tone': {
        intervals: [0, 2, 4, 6, 8, 10],
        name: 'Whole Tone',
        category: 'jazz',
        degrees: ['1', '2', '3', '♯4', '♯5', '♭7'],
    },
    'diminished': {
        intervals: [0, 2, 3, 5, 6, 8, 9, 11],
        name: 'Diminished (Whole-Half)',
        category: 'jazz',
        degrees: ['1', '2', '♭3', '4', '♭5', '♭6', '6', '7'],
    },

    // Exotic
    'chromatic': {
        intervals: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        name: 'Chromatic',
        category: 'exotic',
        degrees: ['1', '♭2', '2', '♭3', '3', '4', '♭5', '5', '♭6', '6', '♭7', '7'],
    },
};

// ============================================================================
// Key Signature Data
// ============================================================================

export interface KeySignature {
    root: string;
    mode: 'major' | 'minor';
    sharps: number;
    flats: number;
    accidentals: string[];
}

export const KEY_SIGNATURES: KeySignature[] = [
    // Major keys
    { root: 'C', mode: 'major', sharps: 0, flats: 0, accidentals: [] },
    { root: 'G', mode: 'major', sharps: 1, flats: 0, accidentals: ['F#'] },
    { root: 'D', mode: 'major', sharps: 2, flats: 0, accidentals: ['F#', 'C#'] },
    { root: 'A', mode: 'major', sharps: 3, flats: 0, accidentals: ['F#', 'C#', 'G#'] },
    { root: 'E', mode: 'major', sharps: 4, flats: 0, accidentals: ['F#', 'C#', 'G#', 'D#'] },
    { root: 'B', mode: 'major', sharps: 5, flats: 0, accidentals: ['F#', 'C#', 'G#', 'D#', 'A#'] },
    { root: 'F#', mode: 'major', sharps: 6, flats: 0, accidentals: ['F#', 'C#', 'G#', 'D#', 'A#', 'E#'] },
    { root: 'F', mode: 'major', sharps: 0, flats: 1, accidentals: ['Bb'] },
    { root: 'Bb', mode: 'major', sharps: 0, flats: 2, accidentals: ['Bb', 'Eb'] },
    { root: 'Eb', mode: 'major', sharps: 0, flats: 3, accidentals: ['Bb', 'Eb', 'Ab'] },
    { root: 'Ab', mode: 'major', sharps: 0, flats: 4, accidentals: ['Bb', 'Eb', 'Ab', 'Db'] },
    { root: 'Db', mode: 'major', sharps: 0, flats: 5, accidentals: ['Bb', 'Eb', 'Ab', 'Db', 'Gb'] },

    // Minor keys (relative minors)
    { root: 'A', mode: 'minor', sharps: 0, flats: 0, accidentals: [] },
    { root: 'E', mode: 'minor', sharps: 1, flats: 0, accidentals: ['F#'] },
    { root: 'B', mode: 'minor', sharps: 2, flats: 0, accidentals: ['F#', 'C#'] },
    { root: 'F#', mode: 'minor', sharps: 3, flats: 0, accidentals: ['F#', 'C#', 'G#'] },
    { root: 'C#', mode: 'minor', sharps: 4, flats: 0, accidentals: ['F#', 'C#', 'G#', 'D#'] },
    { root: 'D', mode: 'minor', sharps: 0, flats: 1, accidentals: ['Bb'] },
    { root: 'G', mode: 'minor', sharps: 0, flats: 2, accidentals: ['Bb', 'Eb'] },
    { root: 'C', mode: 'minor', sharps: 0, flats: 3, accidentals: ['Bb', 'Eb', 'Ab'] },
    { root: 'F', mode: 'minor', sharps: 0, flats: 4, accidentals: ['Bb', 'Eb', 'Ab', 'Db'] },
];

// ============================================================================
// Utility Functions
// ============================================================================

export function getChordNotes(root: string, chordType: string): string[] {
    const chord = CHORD_TYPES[chordType];
    if (!chord) return [];

    const rootIndex = NOTE_NAMES.indexOf(root as NoteName) ??
        NOTE_NAMES_FLAT.indexOf(root as any) ?? 0;

    return chord.intervals.map(interval => {
        const noteIndex = (rootIndex + interval) % 12;
        return NOTE_NAMES[noteIndex];
    });
}

export function getScaleNotes(root: string, scaleType: string): string[] {
    const scale = SCALES[scaleType];
    if (!scale) return [];

    const rootIndex = NOTE_NAMES.indexOf(root as NoteName) ??
        NOTE_NAMES_FLAT.indexOf(root as any) ?? 0;

    return scale.intervals.map(interval => {
        const noteIndex = (rootIndex + interval) % 12;
        return NOTE_NAMES[noteIndex];
    });
}

export function getChordMidiNotes(root: string, chordType: string, octave: number = 4): number[] {
    const chord = CHORD_TYPES[chordType];
    if (!chord) return [];

    const rootMidi = noteNameToMidi(root, octave);
    return chord.intervals.map(interval => rootMidi + interval);
}

export function getScaleMidiNotes(root: string, scaleType: string, octave: number = 4): number[] {
    const scale = SCALES[scaleType];
    if (!scale) return [];

    const rootMidi = noteNameToMidi(root, octave);
    return scale.intervals.map(interval => rootMidi + interval);
}
