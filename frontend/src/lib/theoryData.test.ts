/**
 * Theory Data Library Tests
 */
import { describe, it, expect } from 'vitest';
import {
    NOTE_NAMES,
    CHORD_TYPES,
    SCALES,
    getChordNotes,
    getScaleNotes,
    getChordMidiNotes,
    getScaleMidiNotes,
    noteNameToMidi,
    midiToNoteName,
} from './theoryData';

describe('theoryData', () => {
    describe('NOTE_NAMES', () => {
        it('has 12 notes', () => {
            expect(NOTE_NAMES).toHaveLength(12);
        });

        it('starts with C', () => {
            expect(NOTE_NAMES[0]).toBe('C');
        });

        it('includes all chromatic notes', () => {
            expect(NOTE_NAMES).toContain('C');
            expect(NOTE_NAMES).toContain('D');
            expect(NOTE_NAMES).toContain('E');
            expect(NOTE_NAMES).toContain('F');
            expect(NOTE_NAMES).toContain('G');
            expect(NOTE_NAMES).toContain('A');
            expect(NOTE_NAMES).toContain('B');
        });
    });

    describe('CHORD_TYPES', () => {
        it('includes major chord', () => {
            expect(CHORD_TYPES.maj).toBeDefined();
            expect(CHORD_TYPES.maj.intervals).toEqual([0, 4, 7]);
        });

        it('includes minor chord', () => {
            expect(CHORD_TYPES.min).toBeDefined();
            expect(CHORD_TYPES.min.intervals).toEqual([0, 3, 7]);
        });

        it('includes seventh chords', () => {
            expect(CHORD_TYPES.maj7).toBeDefined();
            expect(CHORD_TYPES.min7).toBeDefined();
            expect(CHORD_TYPES['7']).toBeDefined();
        });

        it('has correct categories', () => {
            expect(CHORD_TYPES.maj.category).toBe('triad');
            expect(CHORD_TYPES.maj7.category).toBe('seventh');
            expect(CHORD_TYPES['9'].category).toBe('extended');
        });
    });

    describe('SCALES', () => {
        it('includes major scale', () => {
            expect(SCALES.major).toBeDefined();
            expect(SCALES.major.intervals).toEqual([0, 2, 4, 5, 7, 9, 11]);
        });

        it('includes natural minor scale', () => {
            expect(SCALES.natural_minor).toBeDefined();
            expect(SCALES.natural_minor.intervals).toEqual([0, 2, 3, 5, 7, 8, 10]);
        });

        it('includes pentatonic scales', () => {
            expect(SCALES.major_pentatonic).toBeDefined();
            expect(SCALES.minor_pentatonic).toBeDefined();
        });

        it('includes blues scale', () => {
            expect(SCALES.blues).toBeDefined();
            expect(SCALES.blues.intervals).toContain(6); // Blue note
        });
    });

    describe('getChordNotes', () => {
        it('returns correct notes for C major', () => {
            const notes = getChordNotes('C', 'maj');
            expect(notes).toEqual(['C', 'E', 'G']);
        });

        it('returns correct notes for A minor', () => {
            const notes = getChordNotes('A', 'min');
            expect(notes).toEqual(['A', 'C', 'E']);
        });

        it('returns correct notes for G7', () => {
            const notes = getChordNotes('G', '7');
            expect(notes).toEqual(['G', 'B', 'D', 'F']);
        });

        it('handles invalid chord type', () => {
            const notes = getChordNotes('C', 'invalid');
            expect(notes).toEqual([]);
        });
    });

    describe('getScaleNotes', () => {
        it('returns correct notes for C major', () => {
            const notes = getScaleNotes('C', 'major');
            expect(notes).toEqual(['C', 'D', 'E', 'F', 'G', 'A', 'B']);
        });

        it('returns correct notes for A minor pentatonic', () => {
            const notes = getScaleNotes('A', 'minor_pentatonic');
            expect(notes).toHaveLength(5);
        });

        it('handles invalid scale type', () => {
            const notes = getScaleNotes('C', 'invalid');
            expect(notes).toEqual([]);
        });
    });

    describe('noteNameToMidi', () => {
        it('converts C4 to 60', () => {
            expect(noteNameToMidi('C', 4)).toBe(60);
        });

        it('converts A4 to 69', () => {
            expect(noteNameToMidi('A', 4)).toBe(69);
        });

        it('converts C5 to 72', () => {
            expect(noteNameToMidi('C', 5)).toBe(72);
        });
    });

    describe('midiToNoteName', () => {
        it('converts 60 to C4', () => {
            expect(midiToNoteName(60)).toBe('C4');
        });

        it('converts 69 to A4', () => {
            expect(midiToNoteName(69)).toBe('A4');
        });

        it('handles sharps', () => {
            expect(midiToNoteName(61)).toBe('C#4');
        });
    });

    describe('getChordMidiNotes', () => {
        it('returns correct MIDI notes for C major at octave 4', () => {
            const notes = getChordMidiNotes('C', 'maj', 4);
            expect(notes).toEqual([60, 64, 67]); // C4, E4, G4
        });

        it('respects octave parameter', () => {
            const notes = getChordMidiNotes('C', 'maj', 5);
            expect(notes).toEqual([72, 76, 79]); // C5, E5, G5
        });
    });

    describe('getScaleMidiNotes', () => {
        it('returns correct MIDI notes for C major scale', () => {
            const notes = getScaleMidiNotes('C', 'major', 4);
            expect(notes).toEqual([60, 62, 64, 65, 67, 69, 71]);
        });

        it('has correct number of notes for pentatonic', () => {
            const notes = getScaleMidiNotes('C', 'major_pentatonic', 4);
            expect(notes).toHaveLength(5);
        });
    });
});
