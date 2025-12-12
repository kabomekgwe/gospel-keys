/**
 * Simple Audio Synth Hook
 * 
 * Lightweight hook for playing chords and scales in theory components
 */
import { useRef, useCallback, useEffect } from 'react';

interface UseSynthOptions {
    oscillatorType?: OscillatorType;
    attack?: number;
    decay?: number;
    sustain?: number;
    release?: number;
}

export function useSynth(options: UseSynthOptions = {}) {
    const {
        oscillatorType = 'triangle',
        attack = 0.02,
        decay = 0.1,
        sustain = 0.3,
        release = 0.5,
    } = options;

    const audioContextRef = useRef<AudioContext | null>(null);
    const activeNotesRef = useRef<Map<number, { oscillator: OscillatorNode; gainNode: GainNode }>>(new Map());

    // Initialize audio context on first use
    const getAudioContext = useCallback(() => {
        if (!audioContextRef.current) {
            audioContextRef.current = new AudioContext();
        }
        if (audioContextRef.current.state === 'suspended') {
            audioContextRef.current.resume();
        }
        return audioContextRef.current;
    }, []);

    // Convert MIDI pitch to frequency
    const midiToFrequency = useCallback((pitch: number): number => {
        return 440 * Math.pow(2, (pitch - 69) / 12);
    }, []);

    // Play a single note
    const playNote = useCallback((pitch: number, duration?: number, velocity = 0.5) => {
        const ctx = getAudioContext();
        const now = ctx.currentTime;

        // Create oscillator and gain node
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();

        oscillator.type = oscillatorType;
        oscillator.frequency.value = midiToFrequency(pitch);

        // ADSR envelope
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(velocity, now + attack);
        gainNode.gain.linearRampToValueAtTime(sustain * velocity, now + attack + decay);

        // Connect
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        oscillator.start(now);

        // Store reference
        activeNotesRef.current.set(pitch, { oscillator, gainNode });

        // Auto-stop if duration provided
        if (duration && duration > 0) {
            const stopTime = now + duration;
            gainNode.gain.setValueAtTime(sustain * velocity, stopTime - release);
            gainNode.gain.linearRampToValueAtTime(0, stopTime);
            oscillator.stop(stopTime);

            setTimeout(() => {
                activeNotesRef.current.delete(pitch);
            }, duration * 1000 + 100);
        }

        return { oscillator, gainNode };
    }, [getAudioContext, midiToFrequency, oscillatorType, attack, decay, sustain, release]);

    // Stop a specific note
    const stopNote = useCallback((pitch: number) => {
        const noteData = activeNotesRef.current.get(pitch);
        if (!noteData) return;

        const ctx = getAudioContext();
        const now = ctx.currentTime;
        const { oscillator, gainNode } = noteData;

        gainNode.gain.setValueAtTime(gainNode.gain.value, now);
        gainNode.gain.linearRampToValueAtTime(0, now + release);
        oscillator.stop(now + release);

        activeNotesRef.current.delete(pitch);
    }, [getAudioContext, release]);

    // Stop all notes
    const stopAll = useCallback(() => {
        activeNotesRef.current.forEach((_, pitch) => stopNote(pitch));
    }, [stopNote]);

    // Play a chord (multiple notes at once)
    const playChord = useCallback((pitches: number[], duration = 1, velocity = 0.4) => {
        pitches.forEach(pitch => {
            playNote(pitch, duration, velocity / Math.sqrt(pitches.length)); // Reduce volume for chords
        });
    }, [playNote]);

    // Play a scale (notes in sequence)
    const playScale = useCallback((pitches: number[], noteDuration = 0.3, gap = 0.05, velocity = 0.5) => {
        pitches.forEach((pitch, index) => {
            const delay = index * (noteDuration + gap) * 1000;
            setTimeout(() => {
                playNote(pitch, noteDuration, velocity);
            }, delay);
        });
    }, [playNote]);

    // Play arpeggio (notes in sequence, overlapping)
    const playArpeggio = useCallback((pitches: number[], noteDuration = 0.5, gap = 0.15, velocity = 0.4) => {
        pitches.forEach((pitch, index) => {
            const delay = index * gap * 1000;
            setTimeout(() => {
                playNote(pitch, noteDuration, velocity);
            }, delay);
        });
    }, [playNote]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopAll();
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, [stopAll]);

    return {
        playNote,
        stopNote,
        stopAll,
        playChord,
        playScale,
        playArpeggio,
    };
}
