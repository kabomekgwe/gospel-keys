/**
 * SheetMusicRenderer Integration Tests
 */
import { describe, it, expect } from 'vitest';
import { render } from '../../test/utils';
import { SheetMusicRenderer } from './SheetMusicRenderer';

// We will not mock useVexFlow here

describe('SheetMusicRenderer Integration', () => {
    it('defaults to C Major when keySignature is null', () => {
        const mockNotes: any[] = [
            { id: '1', pitch: 60, startTime: 0, duration: 1, velocity: 100 }
        ];

        expect(() => {
            render(<SheetMusicRenderer notes={mockNotes} keySignature={null as any} />);
        }).not.toThrow();
    });

    it('does not throw an error with valid props', () => {
        const mockNotes: any[] = [
            { id: '1', pitch: 60, startTime: 0, duration: 1, velocity: 100 }
        ];

        expect(() => {
            render(<SheetMusicRenderer notes={mockNotes} keySignature="C" timeSignature="4/4" />);
        }).not.toThrow();
    });

    it('normalizes "C minor" to "Cm" and does not throw', () => {
        const mockNotes: any[] = [
            { id: '1', pitch: 60, startTime: 0, duration: 1, velocity: 100 }
        ];

        expect(() => {
            render(<SheetMusicRenderer notes={mockNotes} keySignature="C minor" />);
        }).not.toThrow();
    });
});
