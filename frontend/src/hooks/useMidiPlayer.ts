/**
 * MIDI Player Hook
 * 
 * Custom hook for playing MIDI notes using Web Audio API
 * Features:
 * - Load SoundFont instruments
 * - Play/pause/stop playback
 * - Seek to position
 * - Tempo control
 * - Note scheduling with accurate timing
 */
import { useRef, useState, useCallback, useEffect } from 'react';

export interface MidiNote {
    id: string;
    pitch: number;      // MIDI pitch (0-127)
    startTime: number;  // In seconds (original tempo)
    duration: number;   // In seconds (original tempo)
    velocity: number;   // 0-127
    hand?: 'left' | 'right'; // Hand assignment for visualization
}

export interface MidiPlayerState {
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    tempo: number;      // Tempo multiplier (1.0 = 100%)
    isLoading: boolean;
    error: string | null;
    activeNotes: number[]; // Currently sounding pitches
}

export interface MidiPlayerControls {
    play: () => void;
    pause: () => void;
    stop: () => void;
    seek: (time: number) => void;
    setTempo: (tempo: number) => void;
    playNote: (pitch: number, velocity?: number, duration?: number) => void;
    stopNote: (pitch: number) => void;
}

// Simple synth using Web Audio API (fallback when no soundfont)
function createSimpleSynth(audioContext: AudioContext) {
    const activeOscillators = new Map<number, { osc: OscillatorNode; gain: GainNode }>();

    function midiToFrequency(pitch: number): number {
        return 440 * Math.pow(2, (pitch - 69) / 12);
    }

    function playNote(pitch: number, velocity = 80, duration?: number) {
        stopNote(pitch);

        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();

        // Use triangle wave for piano-like sound
        osc.type = 'triangle';
        osc.frequency.value = midiToFrequency(pitch);

        // Velocity to volume (with curve)
        const volume = Math.pow(velocity / 127, 2) * 0.3;

        // ADSR envelope
        const now = audioContext.currentTime;
        const attackTime = 0.02;
        const decayTime = 0.1;
        const sustainLevel = 0.6;

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(volume, now + attackTime);
        gain.gain.linearRampToValueAtTime(volume * sustainLevel, now + attackTime + decayTime);

        osc.connect(gain);
        gain.connect(audioContext.destination);
        osc.start(now);

        activeOscillators.set(pitch, { osc, gain });

        if (duration) {
            setTimeout(() => stopNote(pitch), duration * 1000);
        }
    }

    function stopNote(pitch: number) {
        const node = activeOscillators.get(pitch);
        if (node) {
            const now = audioContext.currentTime;
            const releaseTime = 0.1;

            node.gain.gain.cancelScheduledValues(now);
            node.gain.gain.setValueAtTime(node.gain.gain.value, now);
            node.gain.gain.linearRampToValueAtTime(0, now + releaseTime);

            setTimeout(() => {
                node.osc.stop();
                node.osc.disconnect();
                node.gain.disconnect();
                activeOscillators.delete(pitch);
            }, releaseTime * 1000 + 10);
        }
    }

    function stopAll() {
        activeOscillators.forEach((_, pitch) => stopNote(pitch));
    }

    return { playNote, stopNote, stopAll };
}

export function useMidiPlayer(notes: MidiNote[], duration: number): [MidiPlayerState, MidiPlayerControls] {
    const audioContextRef = useRef<AudioContext | null>(null);
    const synthRef = useRef<ReturnType<typeof createSimpleSynth> | null>(null);
    const animationFrameRef = useRef<number>(0);
    const startTimeRef = useRef<number>(0);
    const pausedAtRef = useRef<number>(0);
    const scheduledNotesRef = useRef<Set<string>>(new Set());

    const [state, setState] = useState<MidiPlayerState>({
        isPlaying: false,
        currentTime: 0,
        duration,
        tempo: 1.0,
        isLoading: false,
        error: null,
        activeNotes: [],
    });

    // Initialize audio context lazily
    const getAudioContext = useCallback(() => {
        if (!audioContextRef.current) {
            audioContextRef.current = new AudioContext();
            synthRef.current = createSimpleSynth(audioContextRef.current);
        }
        // Resume if suspended
        if (audioContextRef.current.state === 'suspended') {
            audioContextRef.current.resume();
        }
        return audioContextRef.current;
    }, []);

    // Update duration when notes change
    useEffect(() => {
        setState(prev => ({ ...prev, duration }));
    }, [duration]);

    // Playback loop
    const updatePlayback = useCallback(() => {
        if (!state.isPlaying) return;

        const elapsed = (performance.now() - startTimeRef.current) / 1000;
        const currentTime = pausedAtRef.current + elapsed * state.tempo;

        if (currentTime >= duration) {
            // End of playback
            setState(prev => ({
                ...prev,
                isPlaying: false,
                currentTime: 0,
                activeNotes: [],
            }));
            pausedAtRef.current = 0;
            scheduledNotesRef.current.clear();
            synthRef.current?.stopAll();
            return;
        }

        // Find notes to play
        const newActiveNotes: number[] = [];
        const lookAhead = 0.1; // Schedule notes 100ms ahead

        notes.forEach(note => {
            const noteStart = note.startTime / state.tempo;
            const noteEnd = (note.startTime + note.duration) / state.tempo;

            // Check if note is currently active
            if (currentTime >= noteStart && currentTime < noteEnd) {
                newActiveNotes.push(note.pitch);
            }

            // Schedule note if within look-ahead window
            if (noteStart >= currentTime && noteStart < currentTime + lookAhead) {
                if (!scheduledNotesRef.current.has(note.id)) {
                    scheduledNotesRef.current.add(note.id);
                    synthRef.current?.playNote(note.pitch, note.velocity, note.duration / state.tempo);
                }
            }
        });

        setState(prev => ({
            ...prev,
            currentTime,
            activeNotes: newActiveNotes,
        }));

        animationFrameRef.current = requestAnimationFrame(updatePlayback);
    }, [state.isPlaying, state.tempo, notes, duration]);

    // Start/stop animation frame
    useEffect(() => {
        if (state.isPlaying) {
            startTimeRef.current = performance.now();
            animationFrameRef.current = requestAnimationFrame(updatePlayback);
        }
        return () => {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
        };
    }, [state.isPlaying, updatePlayback]);

    // Controls
    const play = useCallback(() => {
        getAudioContext();
        setState(prev => ({ ...prev, isPlaying: true }));
    }, [getAudioContext]);

    const pause = useCallback(() => {
        const elapsed = (performance.now() - startTimeRef.current) / 1000;
        pausedAtRef.current += elapsed * state.tempo;
        synthRef.current?.stopAll();
        setState(prev => ({
            ...prev,
            isPlaying: false,
            activeNotes: [],
        }));
    }, [state.tempo]);

    const stop = useCallback(() => {
        pausedAtRef.current = 0;
        scheduledNotesRef.current.clear();
        synthRef.current?.stopAll();
        setState(prev => ({
            ...prev,
            isPlaying: false,
            currentTime: 0,
            activeNotes: [],
        }));
    }, []);

    const seek = useCallback((time: number) => {
        pausedAtRef.current = Math.max(0, Math.min(time, duration));
        scheduledNotesRef.current.clear();
        synthRef.current?.stopAll();

        if (state.isPlaying) {
            startTimeRef.current = performance.now();
        }

        setState(prev => ({
            ...prev,
            currentTime: pausedAtRef.current,
            activeNotes: [],
        }));
    }, [duration, state.isPlaying]);

    const setTempo = useCallback((tempo: number) => {
        // Clamp tempo between 0.25x and 2x
        const clampedTempo = Math.max(0.25, Math.min(2, tempo));

        if (state.isPlaying) {
            // Save current position and restart with new tempo
            const elapsed = (performance.now() - startTimeRef.current) / 1000;
            pausedAtRef.current += elapsed * state.tempo;
            startTimeRef.current = performance.now();
        }

        setState(prev => ({ ...prev, tempo: clampedTempo }));
    }, [state.isPlaying, state.tempo]);

    const playNote = useCallback((pitch: number, velocity = 80, noteDuration = 0.5) => {
        getAudioContext();
        synthRef.current?.playNote(pitch, velocity, noteDuration);
        setState(prev => ({
            ...prev,
            activeNotes: [...prev.activeNotes.filter(p => p !== pitch), pitch],
        }));

        // Remove from active after duration
        setTimeout(() => {
            setState(prev => ({
                ...prev,
                activeNotes: prev.activeNotes.filter(p => p !== pitch),
            }));
        }, noteDuration * 1000);
    }, [getAudioContext]);

    const stopNote = useCallback((pitch: number) => {
        synthRef.current?.stopNote(pitch);
        setState(prev => ({
            ...prev,
            activeNotes: prev.activeNotes.filter(p => p !== pitch),
        }));
    }, []);

    // Cleanup
    useEffect(() => {
        return () => {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
            synthRef.current?.stopAll();
            audioContextRef.current?.close();
        };
    }, []);

    return [
        state,
        { play, pause, stop, seek, setTempo, playNote, stopNote },
    ];
}
