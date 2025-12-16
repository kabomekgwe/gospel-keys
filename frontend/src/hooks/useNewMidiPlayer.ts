
import { useState, useEffect, useRef, useCallback } from 'react';
import * as Tone from 'tone';

// Define the shape of a MIDI note
// Define the shape of a MIDI note
export interface MidiNote {
    id: string;
    pitch: number;
    start_time: number;
    end_time: number;
    velocity: number;
    hand: 'left' | 'right';
}

// Player state
export interface PlayerState {
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    tempo: number;
    activeNotes: number[];
    mutedHands: { left: boolean; right: boolean };
    metronomeEnabled: boolean;
}

// Player controls
export interface PlayerControls {
    play: () => void;
    pause: () => void;
    stop: () => void;
    seek: (time: number) => void;
    setTempo: (tempo: number) => void;
    playNote: (pitch: number, velocity: number, duration: number) => void;
    toggleHandMute: (hand: 'left' | 'right') => void;
    toggleMetronome: () => void;
}

// Salamander Grand Piano samples (C major scale for demo, but better to map widely)
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

/**
 * Custom hook for a MIDI player with realistic piano sounds
 * @param notes - An array of MIDI notes
 * @param duration - The total duration of the song in seconds
 * @returns - The player state and controls
 */
export function useNewMidiPlayer(
    notes: MidiNote[],
    duration: number
): [PlayerState, PlayerControls] {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [tempo, setTempo] = useState(120);
    const [activeNotes, setActiveNotes] = useState<number[]>([]);

    // Practice features
    const [mutedHands, setMutedHands] = useState({ left: false, right: false });
    const [metronomeEnabled, setMetronomeEnabled] = useState(false);

    const sampler = useRef<Tone.Sampler | null>(null);
    const metronome = useRef<Tone.MembraneSynth | null>(null);
    const scheduledEvents = useRef<number[]>([]);
    const metronomeLoop = useRef<number | null>(null);

    // Initialize the piano sampler and metronome
    useEffect(() => {
        const piano = new Tone.Sampler({
            urls: SAMPLER_URLS,
            baseUrl: SAMPLER_BASE_URL,
            onload: () => {
                console.log('Piano samples loaded');
            }
        }).toDestination();

        // Reverb for more realism
        const reverb = new Tone.Reverb({
            decay: 2.5,
            preDelay: 0.1,
            wet: 0.3
        }).toDestination();
        piano.connect(reverb);

        sampler.current = piano;

        // Metronome synth
        metronome.current = new Tone.MembraneSynth({
            pitchDecay: 0.008,
            octaves: 2,
            envelope: {
                attack: 0.0006,
                decay: 0.3,
                sustain: 0
            }
        }).toDestination();
        metronome.current.volume.value = -10; // Lower volume

        return () => {
            piano.dispose();
            reverb.dispose();
            metronome.current?.dispose();
        };
    }, []);

    // Sync Tone.Transport loop
    useEffect(() => {
        let animationFrameId: number;

        const loop = () => {
            if (isPlaying) {
                // Ensure Tone.Transport is properly synced
                setCurrentTime(Tone.Transport.seconds);
                animationFrameId = requestAnimationFrame(loop);
            }
        };

        if (isPlaying) {
            animationFrameId = requestAnimationFrame(loop);
        } else {
            cancelAnimationFrame(animationFrameId!);
        }

        return () => cancelAnimationFrame(animationFrameId);
    }, [isPlaying]);

    // Cleanup scheduled events
    const clearScheduledEvents = useCallback(() => {
        scheduledEvents.current.forEach((eventId) => Tone.Transport.clear(eventId));
        scheduledEvents.current = [];
    }, []);

    // Schedule MIDI notes
    useEffect(() => {
        if (!sampler.current || notes.length === 0) return;

        clearScheduledEvents();

        // Sort notes just in case
        const sortedNotes = [...notes].sort((a, b) => a.start_time - b.start_time);

        sortedNotes.forEach((note) => {
            const duration = note.end_time - note.start_time;
            const eventId = Tone.Transport.schedule((time: number) => {
                // Check hand muting
                if ((note.hand === 'left' && mutedHands.left) ||
                    (note.hand === 'right' && mutedHands.right)) {
                    return;
                }

                sampler.current?.triggerAttackRelease(
                    Tone.Frequency(note.pitch, 'midi').toNote(),
                    duration,
                    time,
                    note.velocity / 127
                );

                // Visual feedback
                Tone.Draw.schedule(() => {
                    setActiveNotes((prev) => [...prev, note.pitch]);
                }, time);

                Tone.Draw.schedule(() => {
                    setActiveNotes((prev) => prev.filter((p) => p !== note.pitch));
                }, time + duration);

            }, note.start_time);

            scheduledEvents.current.push(eventId);
        });

    }, [notes, mutedHands, clearScheduledEvents]); // Re-schedule if hands are muted/unmuted

    // Metronome logic
    useEffect(() => {
        if (metronomeLoop.current !== null) {
            Tone.Transport.clear(metronomeLoop.current);
            metronomeLoop.current = null;
        }

        if (metronomeEnabled && metronome.current) {
            // Schedule metronome clicks
            const loopId = Tone.Transport.scheduleRepeat((time: number) => {
                metronome.current?.triggerAttackRelease("C5", "32n", time);
            }, "4n"); // Quarter note clicks
            metronomeLoop.current = loopId;
        }
    }, [metronomeEnabled, tempo]);

    // Handle Tempo
    useEffect(() => {
        Tone.Transport.bpm.value = tempo;
    }, [tempo]);

    // Controls
    const play = useCallback(async () => {
        if (Tone.context.state !== 'running') {
            await Tone.start();
        }

        if (Tone.Transport.state !== 'started') {
            Tone.Transport.start();
        }
        setIsPlaying(true);
    }, []);

    const pause = useCallback(() => {
        Tone.Transport.pause();
        setIsPlaying(false);
    }, []);

    const stop = useCallback(() => {
        Tone.Transport.stop();
        Tone.Transport.seconds = 0;
        setCurrentTime(0);
        setIsPlaying(false);
        setActiveNotes([]); // Clear active notes
    }, []);

    const seek = useCallback((time: number) => {
        Tone.Transport.seconds = time;
        setCurrentTime(time);
        // Clear active notes on seek just in case
        setActiveNotes([]);
    }, []);

    const playNote = useCallback((pitch: number, velocity: number, duration: number) => {
        if (sampler.current) {
            sampler.current.triggerAttackRelease(
                Tone.Frequency(pitch, 'midi').toNote(),
                duration,
                Tone.now(),
                velocity / 127
            );
        }
    }, []);

    const toggleHandMute = useCallback((hand: 'left' | 'right') => {
        setMutedHands(prev => ({ ...prev, [hand]: !prev[hand] }));
    }, []);

    const toggleMetronome = useCallback(() => {
        setMetronomeEnabled(prev => !prev);
    }, []);

    return [
        {
            isPlaying,
            currentTime,
            duration,
            tempo,
            activeNotes,
            mutedHands,
            metronomeEnabled
        },
        {
            play,
            pause,
            stop,
            seek,
            setTempo,
            playNote,
            toggleHandMute,
            toggleMetronome
        },
    ];
}
