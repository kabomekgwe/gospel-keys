/**
 * Playback Controls Component
 * 
 * Audio/MIDI playback control bar with play/pause, seek, tempo, and volume
 */
import { motion } from 'framer-motion';
import {
    Play,
    Pause,
    Square,
    SkipBack,
    SkipForward,
    Repeat,
    Volume2,
    VolumeX,
} from 'lucide-react';
import { useState } from 'react';

export interface PlaybackControlsProps {
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    tempo: number;
    onPlay: () => void;
    onPause: () => void;
    onStop: () => void;
    onSeek: (time: number) => void;
    onTempoChange: (tempo: number) => void;
    isLooping?: boolean;
    onLoopToggle?: () => void;
    loopStart?: number;
    loopEnd?: number;
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function PlaybackControls({
    isPlaying,
    currentTime,
    duration,
    tempo,
    onPlay,
    onPause,
    onStop,
    onSeek,
    onTempoChange,
    isLooping = false,
    onLoopToggle,
    loopStart,
    loopEnd,
}: PlaybackControlsProps) {
    const [isMuted, setIsMuted] = useState(false);
    const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

    const tempoPresets = [0.5, 0.75, 1.0, 1.25, 1.5];

    // Handle seek on timeline click
    const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percent = x / rect.width;
        onSeek(percent * duration);
    };

    // Skip forward/backward
    const skipAmount = 5; // seconds
    const skipForward = () => onSeek(Math.min(currentTime + skipAmount, duration));
    const skipBackward = () => onSeek(Math.max(currentTime - skipAmount, 0));

    return (
        <div className="bg-slate-800/80 backdrop-blur-lg border-t border-slate-700/50 p-4">
            {/* Timeline */}
            <div className="mb-4">
                <div
                    className="relative h-2 bg-slate-700 rounded-full cursor-pointer group"
                    onClick={handleTimelineClick}
                >
                    {/* Loop region indicator */}
                    {isLooping && loopStart !== undefined && loopEnd !== undefined && (
                        <div
                            className="absolute h-full bg-violet-500/30 rounded-full"
                            style={{
                                left: `${(loopStart / duration) * 100}%`,
                                width: `${((loopEnd - loopStart) / duration) * 100}%`,
                            }}
                        />
                    )}

                    {/* Progress bar */}
                    <motion.div
                        className="absolute h-full bg-gradient-to-r from-cyan-500 to-cyan-400 rounded-full"
                        style={{ width: `${progress}%` }}
                        initial={false}
                    />

                    {/* Playhead */}
                    <motion.div
                        className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ left: `calc(${progress}% - 8px)` }}
                        initial={false}
                    />
                </div>

                {/* Time display */}
                <div className="flex justify-between mt-1.5 text-xs text-slate-400 font-mono">
                    <span>{formatTime(currentTime)}</span>
                    <span>{formatTime(duration)}</span>
                </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
                {/* Left: Tempo control */}
                <div className="flex items-center gap-2 min-w-[160px]">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">Tempo</span>
                    <div className="flex items-center gap-1">
                        {tempoPresets.map((preset) => (
                            <motion.button
                                key={preset}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => onTempoChange(preset)}
                                className={`
                  px-2 py-1 text-xs rounded-md transition-colors
                  ${tempo === preset
                                        ? 'bg-cyan-500 text-white'
                                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    }
                `}
                            >
                                {preset}x
                            </motion.button>
                        ))}
                    </div>
                </div>

                {/* Center: Playback buttons */}
                <div className="flex items-center gap-2">
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={skipBackward}
                        className="p-2 text-slate-300 hover:text-white transition-colors"
                        title="Skip back 5s"
                    >
                        <SkipBack className="w-5 h-5" />
                    </motion.button>

                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={onStop}
                        className="p-2 text-slate-300 hover:text-white transition-colors"
                        title="Stop"
                    >
                        <Square className="w-5 h-5" />
                    </motion.button>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={isPlaying ? onPause : onPlay}
                        className="w-14 h-14 flex items-center justify-center bg-gradient-to-r from-cyan-500 to-cyan-400 rounded-full text-white shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-shadow"
                        title={isPlaying ? 'Pause' : 'Play'}
                    >
                        {isPlaying ? (
                            <Pause className="w-6 h-6 ml-0.5" />
                        ) : (
                            <Play className="w-6 h-6 ml-1" />
                        )}
                    </motion.button>

                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={skipForward}
                        className="p-2 text-slate-300 hover:text-white transition-colors"
                        title="Skip forward 5s"
                    >
                        <SkipForward className="w-5 h-5" />
                    </motion.button>

                    {onLoopToggle && (
                        <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={onLoopToggle}
                            className={`p-2 transition-colors ${isLooping ? 'text-violet-400' : 'text-slate-300 hover:text-white'
                                }`}
                            title="Toggle loop"
                        >
                            <Repeat className="w-5 h-5" />
                        </motion.button>
                    )}
                </div>

                {/* Right: Volume */}
                <div className="flex items-center gap-2 min-w-[160px] justify-end">
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setIsMuted(!isMuted)}
                        className={`p-2 transition-colors ${isMuted ? 'text-red-400' : 'text-slate-300 hover:text-white'
                            }`}
                    >
                        {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                    </motion.button>

                    <div className="w-24 h-2 bg-slate-700 rounded-full">
                        <motion.div
                            className="h-full bg-slate-400 rounded-full"
                            style={{ width: isMuted ? '0%' : '80%' }}
                            initial={false}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
