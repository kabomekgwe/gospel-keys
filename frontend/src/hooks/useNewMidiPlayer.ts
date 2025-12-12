
import { useState, useEffect, useRef } from 'react';
import * as Tone from 'tone';
import Soundfont from 'soundfont-player';

// Define the shape of a MIDI note
export interface MidiNote {
    id: string;
    pitch: number;
    startTime: number;
    duration: number;
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
}

// Player controls
export interface PlayerControls {
    play: () => void;
    pause: () => void;
    stop: () => void;
    seek: (time: number) => void;
    setTempo: (tempo: number) => void;
    playNote: (pitch: number, velocity: number, duration: number) => void;
}

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

    const sampler = useRef<Soundfont.Player | null>(null);
    const scheduledEvents = useRef<Map<string, number>>(new Map());

    // Initialize the piano sampler
    useEffect(() => {
        const ac = new AudioContext();
        Soundfont.instrument(ac, 'acoustic_grand_piano', { soundfont: 'MusyngKite' })
            .then((piano) => {
                sampler.current = piano;
            })
            .catch((err) => {
                console.error('Failed to load piano soundfont', err);
            });

        return () => {
            if (sampler.current) {
                // sampler.current.disconnect();
            }
        };
    }, []);

    // Playback loop
    useEffect(() => {
        let animationFrameId: number;

        const loop = (now: number) => {
            if (isPlaying) {
                const newTime = Tone.Transport.seconds;
                setCurrentTime(newTime);
                animationFrameId = requestAnimationFrame(loop);
            }
        };

        if (isPlaying) {
            animationFrameId = requestAnimationFrame(loop);
        } else {
            cancelAnimationFrame(animationFrameId!);
        }

        return () => {
            cancelAnimationFrame(animationFrameId);
        };
    }, [isPlaying]);

    // Schedule MIDI notes
    useEffect(() => {
        if (!sampler.current || notes.length === 0) return;

        // Clear previous events
        scheduledEvents.current.forEach((eventId) => {
            Tone.Transport.clear(eventId);
        });
        scheduledEvents.current.clear();

        notes.forEach((note) => {
            const eventId = Tone.Transport.schedule(
                (time) => {
                    sampler.current?.play(note.pitch.toString(), time, {
                        duration: note.duration,
                        gain: note.velocity / 127,
                    });
                    setActiveNotes((prev) => [...prev, note.pitch]);
                    Tone.Transport.scheduleOnce(() => {
                        setActiveNotes((prev) => prev.filter((p) => p !== note.pitch));
                    }, `+${note.duration}`);
                },
                note.startTime
            );
            scheduledEvents.current.set(note.id, eventId as unknown as number);
        });
    }, [notes, sampler.current]);

    // Playback controls
    const play = () => {
        if (Tone.Transport.state !== 'started') {
            Tone.Transport.start();
        }
        setIsPlaying(true);
    };

    const pause = () => {
        Tone.Transport.pause();
        setIsPlaying(false);
    };

    const stop = () => {
        Tone.Transport.stop();
        setCurrentTime(0);
        setIsPlaying(false);
    };

    const seek = (time: number) => {
        Tone.Transport.seconds = time;
        setCurrentTime(time);
    };

    const playNote = (pitch: number, velocity: number, duration: number) => {
        if (sampler.current) {
            sampler.current.play(pitch.toString(), Tone.now(), {
                duration,
                gain: velocity / 127,
            });
        }
    };

    return [
        { isPlaying, currentTime, duration, tempo, activeNotes },
        { play, pause, stop, seek, setTempo, playNote },
    ];
}
