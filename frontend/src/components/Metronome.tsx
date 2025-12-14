/**
 * Metronome Component
 * 
 * Visual and audio metronome for practice sessions.
 * Features:
 * - Audio click track via Web Audio API
 * - Visual beat indicator
 * - Accented downbeats
 * - Subdivision options
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface MetronomeProps {
    /** Tempo in BPM */
    tempo: number;
    /** Time signature [beats, noteValue] */
    timeSignature?: [number, number];
    /** Whether the metronome is playing */
    isPlaying: boolean;
    /** Volume (0-1) */
    volume?: number;
    /** Subdivision (1=quarter, 2=eighth, 4=sixteenth) */
    subdivision?: number;
    /** CSS classes */
    className?: string;
}

export function Metronome({
    tempo,
    timeSignature = [4, 4],
    isPlaying,
    volume = 0.5,
    subdivision = 1,
    className = '',
}: MetronomeProps) {
    const [currentBeat, setCurrentBeat] = useState(0);
    const audioContextRef = useRef<AudioContext | null>(null);
    const nextNoteTimeRef = useRef(0);
    const timerRef = useRef<number | null>(null);
    const beatCountRef = useRef(0);

    const [beatsPerMeasure] = timeSignature;

    // Initialize audio context
    useEffect(() => {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        return () => {
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, []);

    // Create click sound
    const playClick = useCallback((isAccent: boolean) => {
        const ctx = audioContextRef.current;
        if (!ctx) return;

        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        // Accent = higher pitch
        osc.frequency.value = isAccent ? 1000 : 800;
        gain.gain.value = volume * (isAccent ? 1.0 : 0.7);

        const now = ctx.currentTime;
        osc.start(now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
        osc.stop(now + 0.1);
    }, [volume]);

    // Scheduler
    const schedule = useCallback(() => {
        const ctx = audioContextRef.current;
        if (!ctx) return;

        const secondsPerBeat = 60.0 / tempo / subdivision;
        const scheduleAheadTime = 0.1;
        const lookahead = 25; // ms

        while (nextNoteTimeRef.current < ctx.currentTime + scheduleAheadTime) {
            const beatInMeasure = beatCountRef.current % (beatsPerMeasure * subdivision);
            const isDownbeat = beatInMeasure === 0;
            const isMainBeat = beatInMeasure % subdivision === 0;

            if (isMainBeat) {
                playClick(isDownbeat);
                setCurrentBeat(Math.floor(beatInMeasure / subdivision));
            }

            beatCountRef.current++;
            nextNoteTimeRef.current += secondsPerBeat;
        }

        timerRef.current = window.setTimeout(schedule, lookahead);
    }, [tempo, beatsPerMeasure, subdivision, playClick]);

    // Start/stop
    useEffect(() => {
        if (isPlaying) {
            const ctx = audioContextRef.current;
            if (ctx && ctx.state === 'suspended') {
                ctx.resume();
            }

            beatCountRef.current = 0;
            nextNoteTimeRef.current = ctx?.currentTime || 0;
            schedule();
        } else {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
                timerRef.current = null;
            }
            setCurrentBeat(0);
        }

        return () => {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        };
    }, [isPlaying, schedule]);

    return (
        <div className={`flex items-center gap-3 ${className}`}>
            {/* Beat indicators */}
            <div className="flex gap-1.5">
                {Array.from({ length: beatsPerMeasure }).map((_, i) => (
                    <motion.div
                        key={i}
                        className={`
              w-4 h-4 rounded-full transition-colors
              ${i === 0 ? 'border-2 border-violet-400' : ''}
            `}
                        animate={{
                            backgroundColor: isPlaying && i === currentBeat
                                ? i === 0 ? '#a78bfa' : '#6ee7b7'
                                : '#334155',
                            scale: isPlaying && i === currentBeat ? 1.3 : 1,
                        }}
                        transition={{ duration: 0.05 }}
                    />
                ))}
            </div>

            {/* Tempo display */}
            <div className="flex items-baseline gap-1 text-sm">
                <span className="font-mono font-bold text-slate-200">{tempo}</span>
                <span className="text-xs text-slate-500">BPM</span>
            </div>
        </div>
    );
}

// Compact metronome toggle button
export function MetronomeToggle({
    isActive,
    onToggle,
    tempo,
    className = '',
}: {
    isActive: boolean;
    onToggle: () => void;
    tempo: number;
    className?: string;
}) {
    return (
        <button
            onClick={onToggle}
            className={`
        flex items-center gap-2 px-3 py-2 rounded-lg
        transition-colors
        ${isActive
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }
        ${className}
      `}
        >
            <motion.div
                animate={{
                    scale: isActive ? [1, 1.2, 1] : 1,
                }}
                transition={{
                    repeat: isActive ? Infinity : 0,
                    duration: 60 / tempo,
                }}
            >
                🎵
            </motion.div>
            <span className="text-sm font-medium">
                {tempo} BPM
            </span>
        </button>
    );
}
