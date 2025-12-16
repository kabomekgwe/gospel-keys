import { useState } from 'react';
import { Play, Target, Repeat, Timer, Gauge, Check, X } from 'lucide-react';

interface PracticeButtonProps {
    /** Text label for what's being practiced */
    label: string;
    /** MIDI notes to loop (for chord/voicing practice) */
    midiNotes?: number[];
    /** For melodic practice (licks, scales) */
    melodicNotes?: number[];
    /** Callback to play the content */
    onPlay?: () => void;
    /** Optional tempo for practice loop */
    defaultTempo?: number;
    /** Additional CSS classes */
    className?: string;
}

interface PracticeSettings {
    tempo: number;
    loop: boolean;
    loopCount: number;
    handsFree: boolean;
}

/**
 * PracticeButton - A reusable "Practice This" button that opens practice settings.
 * 
 * Features:
 * - Tempo adjustment slider
 * - Loop controls (count or infinite)
 * - Hands-free mode with countdown
 * - Quick play action
 */
export function PracticeButton({
    label,
    midiNotes: _midiNotes,
    melodicNotes: _melodicNotes,
    onPlay,
    defaultTempo = 80,
    className = '',
}: PracticeButtonProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isPracticing, setIsPracticing] = useState(false);
    const [settings, setSettings] = useState<PracticeSettings>({
        tempo: defaultTempo,
        loop: true,
        loopCount: 4,
        handsFree: false,
    });

    const handleStartPractice = () => {
        setIsPracticing(true);
        // In a real implementation, this would start a metronome/loop
        // For now, just trigger the onPlay callback
        onPlay?.();

        // Simulate practice session
        setTimeout(() => {
            setIsPracticing(false);
        }, 3000);
    };

    const handleQuickPlay = (e: React.MouseEvent) => {
        e.stopPropagation();
        onPlay?.();
    };

    return (
        <div className={`relative ${className}`}>
            {/* Main Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                    ${isPracticing
                        ? 'bg-green-500 text-white animate-pulse'
                        : 'bg-gradient-to-r from-emerald-500/20 to-green-500/20 text-emerald-400 hover:from-emerald-500/30 hover:to-green-500/30 border border-emerald-500/30'
                    }
                `}
            >
                <Target className="w-3 h-3" />
                {isPracticing ? 'Practicing...' : 'Practice This'}
            </button>

            {/* Practice Settings Popover */}
            {isOpen && !isPracticing && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Popover */}
                    <div className="absolute bottom-full left-0 mb-2 z-50 w-72 bg-slate-800 border border-slate-700 rounded-xl shadow-xl p-4">
                        <div className="flex items-center justify-between mb-4">
                            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                                <Target className="w-4 h-4 text-emerald-400" />
                                Practice: {label}
                            </h4>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="text-slate-400 hover:text-white"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            {/* Tempo Slider */}
                            <div>
                                <label className="flex items-center justify-between text-xs text-slate-400 mb-2">
                                    <span className="flex items-center gap-1">
                                        <Gauge className="w-3 h-3" />
                                        Tempo
                                    </span>
                                    <span className="text-white font-mono">{settings.tempo} BPM</span>
                                </label>
                                <input
                                    type="range"
                                    min={40}
                                    max={160}
                                    value={settings.tempo}
                                    onChange={(e) => setSettings(s => ({ ...s, tempo: Number(e.target.value) }))}
                                    className="w-full accent-emerald-500"
                                />
                                <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                                    <span>40</span>
                                    <span>Slow → Fast</span>
                                    <span>160</span>
                                </div>
                            </div>

                            {/* Loop Controls */}
                            <div>
                                <label className="flex items-center justify-between text-xs text-slate-400 mb-2">
                                    <span className="flex items-center gap-1">
                                        <Repeat className="w-3 h-3" />
                                        Loop
                                    </span>
                                </label>
                                <div className="flex gap-2">
                                    {[2, 4, 8, '∞'].map((count) => (
                                        <button
                                            key={count}
                                            onClick={() => setSettings(s => ({
                                                ...s,
                                                loopCount: count === '∞' ? -1 : Number(count),
                                                loop: true
                                            }))}
                                            className={`flex-1 py-1.5 rounded text-xs font-medium transition-all ${(count === '∞' && settings.loopCount === -1) || settings.loopCount === count
                                                ? 'bg-emerald-500 text-white'
                                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                                }`}
                                        >
                                            {count === '∞' ? '∞' : `${count}x`}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Hands-Free Toggle */}
                            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer p-2 bg-slate-900/50 rounded-lg">
                                <input
                                    type="checkbox"
                                    checked={settings.handsFree}
                                    onChange={(e) => setSettings(s => ({ ...s, handsFree: e.target.checked }))}
                                    className="rounded border-slate-600 text-emerald-500"
                                />
                                <span className="flex items-center gap-1">
                                    <Timer className="w-3 h-3" />
                                    Hands-free (3s countdown)
                                </span>
                            </label>

                            {/* Action Buttons */}
                            <div className="flex gap-2 pt-2 border-t border-slate-700">
                                <button
                                    onClick={handleQuickPlay}
                                    className="flex-1 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-colors"
                                >
                                    <Play className="w-4 h-4 fill-current" />
                                    Quick Play
                                </button>
                                <button
                                    onClick={handleStartPractice}
                                    className="flex-1 py-2 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-green-500 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-colors"
                                >
                                    <Check className="w-4 h-4" />
                                    Start
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

/**
 * Compact version for inline use in chord cards
 */
export function PracticeButtonCompact({ onPlay, className = '' }: { onPlay?: () => void; className?: string }) {
    return (
        <button
            onClick={onPlay}
            className={`
                flex items-center gap-1 px-2 py-1 rounded text-[10px] font-medium transition-all
                bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20
                ${className}
            `}
            title="Practice this"
        >
            <Target className="w-2.5 h-2.5" />
            Practice
        </button>
    );
}
