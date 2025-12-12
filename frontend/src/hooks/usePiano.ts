/**
 * Real Piano Hook
 * 
 * Uses sampled piano audio (Salamander via Tone.js) for high-quality playback
 * Compatible with useSynth API for easy replacement
 */
import { useRef, useEffect, useCallback } from 'react';
import * as Tone from 'tone';

// Salamander Grand Piano samples
const SAMPLER_URLS = {
    'A0': 'A0.mp3', 'C1': 'C1.mp3', 'D#1': 'Ds1.mp3', 'F#1': 'Fs1.mp3',
    'A1': 'A1.mp3', 'C2': 'C2.mp3', 'D#2': 'Ds2.mp3', 'F#2': 'Fs2.mp3',
    'A2': 'A2.mp3', 'C3': 'C3.mp3', 'D#3': 'Ds3.mp3', 'F#3': 'Fs3.mp3',
    'A3': 'A3.mp3', 'C4': 'C4.mp3', 'D#4': 'Ds4.mp3', 'F#4': 'Fs4.mp3',
    'A4': 'A4.mp3', 'C5': 'C5.mp3', 'D#5': 'Ds5.mp3', 'F#5': 'Fs5.mp3',
    'A5': 'A5.mp3', 'C6': 'C6.mp3', 'D#6': 'Ds6.mp3', 'F#6': 'Fs6.mp3',
    'A6': 'A6.mp3', 'C7': 'C7.mp3', 'D#7': 'Ds7.mp3', 'F#7': 'Fs7.mp3',
    'A7': 'A7.mp3', 'C8': 'C8.mp3'
};
const SAMPLER_BASE_URL = 'https://tonejs.github.io/audio/salamander/';

export function usePiano() {
    const samplerRef = useRef<Tone.Sampler | null>(null);
    const reverbRef = useRef<Tone.Reverb | null>(null);

    // Initialize sampler
    useEffect(() => {
        const piano = new Tone.Sampler({
            urls: SAMPLER_URLS,
            baseUrl: SAMPLER_BASE_URL,
            onload: () => {
                console.log('Piano samples loaded (Theory)');
            }
        }).toDestination();

        // Add some reverb for nicer sound
        const reverb = new Tone.Reverb({
            decay: 2.0,
            preDelay: 0.1,
            wet: 0.2
        }).toDestination();
        piano.connect(reverb);

        samplerRef.current = piano;
        reverbRef.current = reverb;

        return () => {
            piano.dispose();
            reverb.dispose();
        };
    }, []);

    // Ensure audio context is running
    const ensureContext = useCallback(async () => {
        if (Tone.context.state !== 'running') {
            await Tone.start();
        }
    }, []);

    // Play a single note
    const playNote = useCallback(async (pitch: number, duration = 1, velocity = 0.6) => {
        await ensureContext();
        if (samplerRef.current) {
            samplerRef.current.triggerAttackRelease(
                Tone.Frequency(pitch, 'midi').toNote(),
                duration,
                Tone.now(),
                velocity
            );
        }
    }, [ensureContext]);

    // Play a chord (multiple notes at once)
    const playChord = useCallback(async (pitches: number[], duration = 2, velocity = 0.5) => {
        await ensureContext();
        if (samplerRef.current) {
            const now = Tone.now();
            pitches.forEach(pitch => {
                samplerRef.current?.triggerAttackRelease(
                    Tone.Frequency(pitch, 'midi').toNote(),
                    duration,
                    now,
                    velocity
                );
            });
        }
    }, [ensureContext]);

    // Play a scale (notes in sequence)
    const playScale = useCallback(async (pitches: number[], noteDuration = 0.4, gap = 0.0, velocity = 0.6) => {
        await ensureContext();
        if (samplerRef.current) {
            const now = Tone.now();
            pitches.forEach((pitch, index) => {
                samplerRef.current?.triggerAttackRelease(
                    Tone.Frequency(pitch, 'midi').toNote(),
                    noteDuration,
                    now + index * (noteDuration + gap),
                    velocity
                );
            });
        }
    }, [ensureContext]);

    // Play arpeggio
    const playArpeggio = useCallback(async (pitches: number[], noteDuration = 0.4, gap = 0.2, velocity = 0.6) => {
        await ensureContext();
        if (samplerRef.current) {
            const now = Tone.now();
            pitches.forEach((pitch, index) => {
                samplerRef.current?.triggerAttackRelease(
                    Tone.Frequency(pitch, 'midi').toNote(),
                    noteDuration,
                    now + index * gap,
                    velocity
                );
            });
        }
    }, [ensureContext]);

    const stopAll = useCallback(() => {
        if (samplerRef.current) {
            samplerRef.current.releaseAll();
        }
    }, []);

    return {
        playNote,
        playChord,
        playScale,
        playArpeggio,
        stopAll
    };
}
