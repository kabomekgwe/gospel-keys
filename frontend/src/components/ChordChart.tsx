/**
 * Chord Chart Component
 * 
 * Timeline visualization of chord progressions with:
 * - Color-coded harmonic functions (T/S/D)
 * - Roman numeral notation
 * - Interactive chord selection
 */
import { useMemo } from 'react';
import { motion } from 'framer-motion';

export interface ChordData {
    id: string;
    root: string;
    quality: string;
    romanNumeral?: string;
    function?: 'tonic' | 'subdominant' | 'dominant' | 'secondary';
    startTime: number;
    endTime: number;
    extensions?: string[];
}

export interface ChordChartProps {
    chords: ChordData[];
    duration: number;
    currentTime?: number;
    onChordClick?: (chord: ChordData) => void;
    selectedChordId?: string;
    showRomanNumerals?: boolean;
    keySignature?: string;
}

// Function colors
const FUNCTION_COLORS = {
    tonic: {
        bg: 'bg-emerald-500/20',
        border: 'border-emerald-500/50',
        text: 'text-emerald-400',
        glow: 'shadow-emerald-500/20',
    },
    subdominant: {
        bg: 'bg-amber-500/20',
        border: 'border-amber-500/50',
        text: 'text-amber-400',
        glow: 'shadow-amber-500/20',
    },
    dominant: {
        bg: 'bg-rose-500/20',
        border: 'border-rose-500/50',
        text: 'text-rose-400',
        glow: 'shadow-rose-500/20',
    },
    secondary: {
        bg: 'bg-violet-500/20',
        border: 'border-violet-500/50',
        text: 'text-violet-400',
        glow: 'shadow-violet-500/20',
    },
};

function getChordLabel(chord: ChordData): string {
    let label = chord.root + chord.quality;
    if (chord.extensions && chord.extensions.length > 0) {
        label += chord.extensions.join('');
    }
    return label;
}

export function ChordChart({
    chords,
    duration,
    currentTime = 0,
    onChordClick,
    selectedChordId,
    showRomanNumerals = true,
    keySignature,
}: ChordChartProps) {
    // Group chords by measure for layout
    const measuresPerRow = 8;
    const beatsPerMeasure = 4;
    const tempo = 120; // BPM (should come from props)
    const secondsPerMeasure = (60 / tempo) * beatsPerMeasure;
    const totalMeasures = Math.ceil(duration / secondsPerMeasure);
    const rows = Math.ceil(totalMeasures / measuresPerRow);

    // Find current chord
    const currentChord = useMemo(() => {
        return chords.find(c => currentTime >= c.startTime && currentTime < c.endTime);
    }, [chords, currentTime]);

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    {keySignature && (
                        <span className="px-3 py-1.5 bg-slate-800 rounded-lg text-sm">
                            <span className="text-slate-400">Key: </span>
                            <span className="text-white font-medium">{keySignature}</span>
                        </span>
                    )}
                    <span className="text-sm text-slate-400">
                        {chords.length} chord changes
                    </span>
                </div>

                {/* Legend */}
                <div className="flex items-center gap-4 text-xs">
                    <span className="flex items-center gap-1.5">
                        <span className="w-3 h-3 rounded bg-emerald-500/50" />
                        Tonic (T)
                    </span>
                    <span className="flex items-center gap-1.5">
                        <span className="w-3 h-3 rounded bg-amber-500/50" />
                        Subdominant (S)
                    </span>
                    <span className="flex items-center gap-1.5">
                        <span className="w-3 h-3 rounded bg-rose-500/50" />
                        Dominant (D)
                    </span>
                    <span className="flex items-center gap-1.5">
                        <span className="w-3 h-3 rounded bg-violet-500/50" />
                        Secondary
                    </span>
                </div>
            </div>

            {/* Timeline view */}
            <div className="relative h-16 bg-slate-800/50 rounded-xl overflow-hidden">
                {/* Grid lines */}
                {Array.from({ length: Math.floor(duration / secondsPerMeasure) + 1 }).map((_, i) => (
                    <div
                        key={i}
                        className="absolute top-0 bottom-0 w-px bg-slate-700/50"
                        style={{ left: `${(i * secondsPerMeasure / duration) * 100}%` }}
                    />
                ))}

                {/* Chords */}
                {chords.map((chord) => {
                    const left = (chord.startTime / duration) * 100;
                    const width = ((chord.endTime - chord.startTime) / duration) * 100;
                    const colors = FUNCTION_COLORS[chord.function || 'tonic'];
                    const isSelected = selectedChordId === chord.id;
                    const isCurrent = currentChord?.id === chord.id;

                    return (
                        <motion.button
                            key={chord.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            onClick={() => onChordClick?.(chord)}
                            className={`
                absolute top-1 bottom-1 flex flex-col items-center justify-center
                rounded-lg border transition-all cursor-pointer
                ${colors.bg} ${colors.border}
                ${isSelected ? `ring-2 ring-white/50 ${colors.glow} shadow-lg` : ''}
                ${isCurrent ? 'ring-2 ring-cyan-400' : ''}
                hover:brightness-110
              `}
                            style={{
                                left: `${left}%`,
                                width: `${Math.max(width, 2)}%`,
                            }}
                        >
                            <span className={`text-sm font-bold ${colors.text}`}>
                                {getChordLabel(chord)}
                            </span>
                            {showRomanNumerals && chord.romanNumeral && (
                                <span className="text-xs text-slate-400">
                                    {chord.romanNumeral}
                                </span>
                            )}
                        </motion.button>
                    );
                })}

                {/* Playhead */}
                <motion.div
                    className="absolute top-0 bottom-0 w-0.5 bg-cyan-400 z-10"
                    style={{ left: `${(currentTime / duration) * 100}%` }}
                    initial={false}
                    animate={{ left: `${(currentTime / duration) * 100}%` }}
                />
            </div>

            {/* Grid view (for longer progressions) */}
            {chords.length > 16 && (
                <div className="grid grid-cols-8 gap-2">
                    {chords.map((chord) => {
                        const colors = FUNCTION_COLORS[chord.function || 'tonic'];
                        const isSelected = selectedChordId === chord.id;
                        const isCurrent = currentChord?.id === chord.id;

                        return (
                            <motion.button
                                key={chord.id}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => onChordClick?.(chord)}
                                className={`
                  p-3 rounded-lg border text-center transition-all
                  ${colors.bg} ${colors.border}
                  ${isSelected ? `ring-2 ring-white/50 ${colors.glow} shadow-lg` : ''}
                  ${isCurrent ? 'ring-2 ring-cyan-400' : ''}
                `}
                            >
                                <div className={`text-sm font-bold ${colors.text}`}>
                                    {getChordLabel(chord)}
                                </div>
                                {showRomanNumerals && chord.romanNumeral && (
                                    <div className="text-xs text-slate-400 mt-0.5">
                                        {chord.romanNumeral}
                                    </div>
                                )}
                            </motion.button>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

// Compact chord display for quick preview
export function ChordBadge({ chord }: { chord: ChordData }) {
    const colors = FUNCTION_COLORS[chord.function || 'tonic'];

    return (
        <span className={`
      inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium
      ${colors.bg} ${colors.text} ${colors.border} border
    `}>
            {getChordLabel(chord)}
            {chord.romanNumeral && (
                <span className="text-slate-400">({chord.romanNumeral})</span>
            )}
        </span>
    );
}
