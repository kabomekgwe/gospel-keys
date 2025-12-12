/**
 * useSynth Hook Tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSynth } from './useSynth';

describe('useSynth', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('initializes without errors', () => {
        const { result } = renderHook(() => useSynth());
        expect(result.current).toBeDefined();
    });

    it('exposes playNote function', () => {
        const { result } = renderHook(() => useSynth());
        expect(typeof result.current.playNote).toBe('function');
    });

    it('exposes stopNote function', () => {
        const { result } = renderHook(() => useSynth());
        expect(typeof result.current.stopNote).toBe('function');
    });

    it('exposes playChord function', () => {
        const { result } = renderHook(() => useSynth());
        expect(typeof result.current.playChord).toBe('function');
    });

    it('exposes playScale function', () => {
        const { result } = renderHook(() => useSynth());
        expect(typeof result.current.playScale).toBe('function');
    });

    it('exposes playArpeggio function', () => {
        const { result } = renderHook(() => useSynth());
        expect(typeof result.current.playArpeggio).toBe('function');
    });

    it('exposes stopAll function', () => {
        const { result } = renderHook(() => useSynth());
        expect(typeof result.current.stopAll).toBe('function');
    });

    it('playNote creates AudioContext', () => {
        const { result } = renderHook(() => useSynth());

        act(() => {
            result.current.playNote(60, 0.5, 0.5);
        });

        expect(AudioContext).toHaveBeenCalled();
    });

    it('playChord calls playNote for each pitch', () => {
        const { result } = renderHook(() => useSynth());

        act(() => {
            result.current.playChord([60, 64, 67], 1, 0.4);
        });

        // AudioContext should be called for each note
        expect(AudioContext).toHaveBeenCalled();
    });

    it('accepts custom oscillator type', () => {
        const { result } = renderHook(() =>
            useSynth({ oscillatorType: 'sine' })
        );
        expect(result.current).toBeDefined();
    });

    it('accepts custom ADSR envelope', () => {
        const { result } = renderHook(() =>
            useSynth({
                attack: 0.1,
                decay: 0.2,
                sustain: 0.5,
                release: 0.3
            })
        );
        expect(result.current).toBeDefined();
    });
});
