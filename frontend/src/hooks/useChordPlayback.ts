/**
 * Chord Playback Hook
 *
 * Provides audio playback capabilities using Tone.js
 * Features:
 * - Play individual notes
 * - Play chords (all notes together)
 * - Play arpeggios (notes sequentially)
 * - Play chord sequences
 * - Piano sampler with fallback to synth
 * - Proper cleanup on unmount
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import * as Tone from 'tone';

export interface UseChordPlaybackOptions {
  /** Instrument type */
  instrument?: 'piano' | 'synth';
  /** Default note duration in seconds */
  duration?: number;
  /** Volume in dB (-Infinity to 0) */
  volume?: number;
}

export interface ChordPlayback {
  /** Play a single note */
  playNote: (midiNote: number, duration?: number) => Promise<void>;
  /** Play multiple notes simultaneously */
  playChord: (midiNotes: number[], duration?: number) => Promise<void>;
  /** Play notes sequentially (arpeggio) */
  playArpeggio: (midiNotes: number[], delayMs?: number, duration?: number) => Promise<void>;
  /** Play a sequence of chords */
  playSequence: (chords: number[][], delayMs?: number) => Promise<void>;
  /** Stop all currently playing notes */
  stop: () => void;
  /** Whether audio is currently playing */
  isPlaying: boolean;
  /** Whether the instrument is ready */
  isReady: boolean;
  /** Loading state */
  isLoading: boolean;
  /** Error if instrument failed to load */
  error: string | null;
}

/**
 * Convert MIDI note number to note name with octave
 */
function midiToNoteName(midi: number): string {
  const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const octave = Math.floor(midi / 12) - 1;
  const noteName = noteNames[midi % 12];
  return `${noteName}${octave}`;
}

/**
 * Custom hook for chord playback with Tone.js
 */
export function useChordPlayback(options: UseChordPlaybackOptions = {}): ChordPlayback {
  const {
    instrument = 'synth',
    duration: defaultDuration = 1.0,
    volume = -6,
  } = options;

  const [isPlaying, setIsPlaying] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const instrumentRef = useRef<Tone.Sampler | Tone.PolySynth | null>(null);
  const playingNotesRef = useRef<Set<string>>(new Set());

  // Initialize instrument
  useEffect(() => {
    let mounted = true;
    let currentInstrument: Tone.Sampler | Tone.PolySynth | null = null;

    async function initInstrument() {
      try {
        setIsLoading(true);
        setError(null);

        if (instrument === 'piano') {
          // Use real piano samples via Tone.Sampler
          // Using Salamander Grand Piano samples (open source)
          const sampler = new Tone.Sampler({
            urls: {
              A0: "A0.mp3",
              C1: "C1.mp3",
              "D#1": "Ds1.mp3",
              "F#1": "Fs1.mp3",
              A1: "A1.mp3",
              C2: "C2.mp3",
              "D#2": "Ds2.mp3",
              "F#2": "Fs2.mp3",
              A2: "A2.mp3",
              C3: "C3.mp3",
              "D#3": "Ds3.mp3",
              "F#3": "Fs3.mp3",
              A3: "A3.mp3",
              C4: "C4.mp3",
              "D#4": "Ds4.mp3",
              "F#4": "Fs4.mp3",
              A4: "A4.mp3",
              C5: "C5.mp3",
              "D#5": "Ds5.mp3",
              "F#5": "Fs5.mp3",
              A5: "A5.mp3",
              C6: "C6.mp3",
              "D#6": "Ds6.mp3",
              "F#6": "Fs6.mp3",
              A6: "A6.mp3",
              C7: "C7.mp3",
              "D#7": "Ds7.mp3",
              "F#7": "Fs7.mp3",
              A7: "A7.mp3",
              C8: "C8.mp3"
            },
            baseUrl: "https://tonejs.github.io/audio/salamander/",
            onload: () => {
              if (mounted) {
                setIsReady(true);
                setIsLoading(false);
              }
            },
            onerror: (err) => {
              console.error('Failed to load piano samples:', err);
              if (mounted) {
                setError('Failed to load piano samples');
                setIsLoading(false);
              }
            }
          }).toDestination();

          sampler.volume.value = volume;
          currentInstrument = sampler;
        } else {
          // Default synth
          const synth = new Tone.PolySynth(Tone.Synth).toDestination();
          synth.volume.value = volume;
          currentInstrument = synth;

          if (mounted) {
            setIsReady(true);
            setIsLoading(false);
          }
        }

        if (mounted) {
          instrumentRef.current = currentInstrument;
        }
      } catch (err) {
        console.error('Failed to initialize instrument:', err);
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load instrument');
          setIsLoading(false);
        }
      }
    }

    initInstrument();

    return () => {
      mounted = false;
      if (currentInstrument) {
        currentInstrument.dispose();
      }
    };
  }, [instrument, volume]);

  // Play a single note
  const playNote = useCallback(
    async (midiNote: number, dur: number = defaultDuration): Promise<void> => {
      if (!instrumentRef.current || !isReady) {
        console.warn('Instrument not ready');
        return;
      }

      try {
        // Ensure audio context is started
        if (Tone.getContext().state !== 'running') {
          await Tone.start();
        }

        const noteName = midiToNoteName(midiNote);
        playingNotesRef.current.add(noteName);
        setIsPlaying(true);

        instrumentRef.current.triggerAttackRelease(noteName, dur);

        // Clear playing state after duration
        setTimeout(() => {
          playingNotesRef.current.delete(noteName);
          if (playingNotesRef.current.size === 0) {
            setIsPlaying(false);
          }
        }, dur * 1000);
      } catch (err) {
        console.error('Failed to play note:', err);
      }
    },
    [isReady, defaultDuration]
  );

  // Play multiple notes simultaneously
  const playChord = useCallback(
    async (midiNotes: number[], dur: number = defaultDuration): Promise<void> => {
      if (!instrumentRef.current || !isReady) {
        console.warn('Instrument not ready');
        return;
      }

      try {
        // Ensure audio context is started
        if (Tone.getContext().state !== 'running') {
          await Tone.start();
        }

        const noteNames = midiNotes.map(midiToNoteName);
        noteNames.forEach((name) => playingNotesRef.current.add(name));
        setIsPlaying(true);

        // Play all notes together
        instrumentRef.current.triggerAttackRelease(noteNames, dur);

        // Clear playing state after duration
        setTimeout(() => {
          noteNames.forEach((name) => playingNotesRef.current.delete(name));
          if (playingNotesRef.current.size === 0) {
            setIsPlaying(false);
          }
        }, dur * 1000);
      } catch (err) {
        console.error('Failed to play chord:', err);
      }
    },
    [isReady, defaultDuration]
  );

  // Play notes sequentially (arpeggio)
  const playArpeggio = useCallback(
    async (
      midiNotes: number[],
      delayMs: number = 150,
      dur: number = defaultDuration
    ): Promise<void> => {
      if (!instrumentRef.current || !isReady) {
        console.warn('Instrument not ready');
        return;
      }

      try {
        // Ensure audio context is started
        if (Tone.getContext().state !== 'running') {
          await Tone.start();
        }

        setIsPlaying(true);

        const now = Tone.now();
        const noteNames = midiNotes.map(midiToNoteName);

        noteNames.forEach((noteName, index) => {
          const time = now + (index * delayMs) / 1000;
          playingNotesRef.current.add(noteName);
          instrumentRef.current!.triggerAttackRelease(noteName, dur, time);
        });

        // Clear playing state after all notes finish
        const totalDuration = (noteNames.length * delayMs) / 1000 + dur;
        setTimeout(() => {
          noteNames.forEach((name) => playingNotesRef.current.delete(name));
          setIsPlaying(false);
        }, totalDuration * 1000);
      } catch (err) {
        console.error('Failed to play arpeggio:', err);
      }
    },
    [isReady, defaultDuration]
  );

  // Play a sequence of chords
  const playSequence = useCallback(
    async (chords: number[][], delayMs: number = 1000): Promise<void> => {
      if (!instrumentRef.current || !isReady) {
        console.warn('Instrument not ready');
        return;
      }

      try {
        // Ensure audio context is started
        if (Tone.getContext().state !== 'running') {
          await Tone.start();
        }

        setIsPlaying(true);

        const now = Tone.now();
        const dur = defaultDuration;

        chords.forEach((chord, index) => {
          const time = now + (index * delayMs) / 1000;
          const noteNames = chord.map(midiToNoteName);

          noteNames.forEach((name) => playingNotesRef.current.add(name));
          instrumentRef.current!.triggerAttackRelease(noteNames, dur, time);

          // Schedule cleanup for this chord
          setTimeout(() => {
            noteNames.forEach((name) => playingNotesRef.current.delete(name));
          }, (time - now + dur) * 1000);
        });

        // Clear playing state after all chords finish
        const totalDuration = (chords.length * delayMs) / 1000 + dur;
        setTimeout(() => {
          setIsPlaying(false);
        }, totalDuration * 1000);
      } catch (err) {
        console.error('Failed to play sequence:', err);
      }
    },
    [isReady, defaultDuration]
  );

  // Stop all playing notes
  const stop = useCallback(() => {
    if (instrumentRef.current) {
      instrumentRef.current.releaseAll();
      playingNotesRef.current.clear();
      setIsPlaying(false);
    }
  }, []);

  return {
    playNote,
    playChord,
    playArpeggio,
    playSequence,
    stop,
    isPlaying,
    isReady,
    isLoading,
    error,
  };
}
