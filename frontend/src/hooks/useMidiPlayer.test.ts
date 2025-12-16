/**
 * useMidiPlayer Tests
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMidiPlayer, type MidiNote } from './useMidiPlayer';

describe('useMidiPlayer', () => {
    const mockNotes: MidiNote[] = [
        { id: '1', pitch: 60, start_time: 0, end_time: 1, velocity: 100 },
        { id: '2', pitch: 64, start_time: 1, end_time: 2, velocity: 90 },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('initializes with default state', () => {
        const { result } = renderHook(() => useMidiPlayer(mockNotes, 10));

        const [state] = result.current;
        expect(state.isPlaying).toBe(false);
        expect(state.currentTime).toBe(0);
        expect(state.duration).toBe(10);
        expect(state.tempo).toBe(1.0);
    });

    it('controls playback', () => {
        const { result } = renderHook(() => useMidiPlayer(mockNotes, 10));

        const [, controls] = result.current;

        act(() => {
            controls.play();
        });

        expect(result.current[0].isPlaying).toBe(true);
        expect(global.AudioContext).toHaveBeenCalled(); // Should initialize audio context

        act(() => {
            controls.pause();
        });

        expect(result.current[0].isPlaying).toBe(false);
    });

    it('stops playback and resets', () => {
        const { result } = renderHook(() => useMidiPlayer(mockNotes, 10));
        const [, controls] = result.current;

        act(() => {
            controls.play();
        });

        act(() => {
            controls.stop();
        });

        const [state] = result.current;
        expect(state.isPlaying).toBe(false);
        expect(state.currentTime).toBe(0);
    });

    it('adjusts tempo limits', () => {
        const { result } = renderHook(() => useMidiPlayer(mockNotes, 10));
        const [, controls] = result.current;

        act(() => {
            controls.setTempo(3.0);
        });
        expect(result.current[0].tempo).toBe(2.0); // Clamped to 2x

        act(() => {
            controls.setTempo(0.1);
        });
        expect(result.current[0].tempo).toBe(0.25); // Clamped to 0.25x
    });
});
