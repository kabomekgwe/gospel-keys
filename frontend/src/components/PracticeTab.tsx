
import { Dumbbell, Repeat, Play, Pause, CheckCircle, Hand, Timer } from 'lucide-react';
import { useState } from 'react';
import { type MidiNote } from '../hooks/useNewMidiPlayer';
import { motion } from 'framer-motion';
import { PracticeFeedback } from './practice/PracticeFeedback';
import { practiceApi } from '../lib/api';

interface PracticeTabProps {
    notes: MidiNote[];
    snippetId?: string; // Optional, if practicing a specific snippet
    playerControls: {
        play: () => void;
        pause: () => void;
        setTempo: (tempo: number) => void;
        seek: (time: number) => void;
        toggleHandMute: (hand: 'left' | 'right') => void;
        toggleMetronome: () => void;
    };
    playerState: {
        isPlaying: boolean;
        tempo: number;
        currentTime: number;
        mutedHands: { left: boolean; right: boolean };
        metronomeEnabled: boolean;
    };
}

const ControlButton = ({ onClick, children, active = false, variant = 'default', disabled = false }: { onClick: () => void, children: React.ReactNode, active?: boolean, variant?: 'default' | 'success', disabled?: boolean }) => (
    <motion.button
        whileHover={!disabled ? { scale: 1.05 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
        onClick={onClick}
        disabled={disabled}
        className={`px-4 py-2 flex items-center gap-2 rounded-lg transition-colors border border-transparent
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            ${variant === 'success'
                ? 'bg-emerald-500 hover:bg-emerald-600 text-white'
                : active
                    ? 'bg-cyan-500 text-white border-cyan-400'
                    : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
            }`}
    >
        {children}
    </motion.button>
);

export function PracticeTab({ playerControls, playerState, snippetId }: PracticeTabProps) {
    const [loop, setLoop] = useState<{ start: number, end: number } | null>(null);
    const [isLooping, setIsLooping] = useState(false);
    const [showFeedback, setShowFeedback] = useState(false);

    const handleSetLoop = () => {
        if (isLooping) {
            setIsLooping(false);
            setLoop(null);
        } else {
            const start = Math.max(0, playerState.currentTime - 5);
            const end = playerState.currentTime;
            setLoop({ start, end });
            setIsLooping(true);
            playerControls.seek(start);
        }
    };

    // This effect would ideally be in the player hook, but checking here for UI sync
    if (isLooping && loop && playerState.currentTime >= loop.end) {
        playerControls.seek(loop.start);
    }

    const handleRate = async (quality: number) => {
        if (snippetId) {
            try {
                await practiceApi.reviewSnippet(snippetId, quality);
                // Maybe show a toast or something?
            } catch (error) {
                console.error('Failed to submit review:', error);
            }
        }
        setShowFeedback(false);
    };

    return (
        <div className="p-6 overflow-y-auto h-full relative">
            {showFeedback && (
                <PracticeFeedback
                    onRate={handleRate}
                    onCancel={() => setShowFeedback(false)}
                />
            )}

            <div className="max-w-5xl mx-auto space-y-8">
                <header>
                    <h2 className="text-2xl font-bold text-white mb-2">Practice Mode</h2>
                    <p className="text-slate-400">
                        Hone your skills with focused practice tools.
                    </p>
                </header>

                <div className="card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Practice Tools</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                        {/* Tempo Control */}
                        <div className="space-y-3">
                            <label className="text-slate-300 font-medium">Tempo</label>
                            <div className="flex items-center gap-4">
                                <input
                                    type="range"
                                    min="50"
                                    max="200"
                                    value={playerState.tempo}
                                    onChange={(e) => playerControls.setTempo(Number(e.target.value))}
                                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                                />
                                <span className="font-mono text-cyan-400 w-16 text-center">{playerState.tempo} BPM</span>
                            </div>
                        </div>

                        {/* Hands Separate */}
                        <div className="space-y-3">
                            <label className="text-slate-300 font-medium">Hands</label>
                            <div className="flex items-center gap-2">
                                <ControlButton
                                    onClick={() => playerControls.toggleHandMute('left')}
                                    active={!playerState.mutedHands.left}
                                >
                                    <Hand className="w-4 h-4 scale-x-[-1]" />
                                    Left
                                </ControlButton>
                                <ControlButton
                                    onClick={() => playerControls.toggleHandMute('right')}
                                    active={!playerState.mutedHands.right}
                                >
                                    <Hand className="w-4 h-4" />
                                    Right
                                </ControlButton>
                            </div>
                        </div>

                        {/* Metronome & Loop */}
                        <div className="space-y-3">
                            <label className="text-slate-300 font-medium">Tools</label>
                            <div className="flex items-center gap-2 flex-wrap">
                                <ControlButton
                                    onClick={playerControls.toggleMetronome}
                                    active={playerState.metronomeEnabled}
                                >
                                    <Timer className="w-4 h-4" />
                                    Metronome
                                </ControlButton>

                                <ControlButton onClick={handleSetLoop} active={isLooping}>
                                    <Repeat className="w-4 h-4" />
                                    {isLooping ? 'Loop' : 'Loop 5s'}
                                </ControlButton>
                            </div>
                        </div>

                        {/* Playback Actions */}
                        <div className="space-y-3 md:col-span-2 lg:col-span-3 pt-4 border-t border-slate-700">
                            <div className="flex items-center gap-4">
                                <ControlButton onClick={playerControls.play} active={playerState.isPlaying}>
                                    <Play className="w-4 h-4" />
                                    Play
                                </ControlButton>
                                <ControlButton onClick={playerControls.pause} active={!playerState.isPlaying}>
                                    <Pause className="w-4 h-4" />
                                    Pause
                                </ControlButton>

                                {snippetId && (
                                    <div className="ml-auto">
                                        <ControlButton onClick={() => setShowFeedback(true)} variant="success">
                                            <CheckCircle className="w-4 h-4" />
                                            Finish & Rate
                                        </ControlButton>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="card p-8 text-center"
                >
                    <Dumbbell className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">Practice makes perfect!</h3>
                    <p className="text-slate-400 max-w-md mx-auto">
                        Isolate hands, slow down the tempo, and use the metronome to master difficult sections.
                    </p>
                </motion.div>
            </div>
        </div>
    );
}
