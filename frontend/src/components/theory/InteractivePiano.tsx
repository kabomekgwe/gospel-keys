/**
 * Interactive Piano for Theory Visualization
 * 
 * A lightweight piano component for showing chord and scale notes
 */
import { useMemo } from 'react';
import { motion } from 'framer-motion';

interface InteractivePianoProps {
    highlightedNotes?: number[];
    rootNote?: number;
    octaves?: number;
    startOctave?: number;
    onNoteClick?: (midi: number) => void;
    showNoteNames?: boolean;
    size?: 'sm' | 'md' | 'lg';
}

const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

function isBlackKey(noteIndex: number): boolean {
    return [1, 3, 6, 8, 10].includes(noteIndex % 12);
}

export function InteractivePiano({
    highlightedNotes = [],
    rootNote,
    octaves = 2,
    startOctave = 4,
    onNoteClick,
    showNoteNames = true,
    size = 'md',
}: InteractivePianoProps) {

    const sizes = {
        sm: { white: { width: 24, height: 80 }, black: { width: 16, height: 50 } },
        md: { white: { width: 36, height: 120 }, black: { width: 24, height: 75 } },
        lg: { white: { width: 48, height: 160 }, black: { width: 32, height: 100 } },
    };

    const { white, black } = sizes[size];

    // Generate keys for the specified octaves
    const keys = useMemo(() => {
        const result: { midi: number; isBlack: boolean; noteName: string }[] = [];
        const startMidi = (startOctave + 1) * 12;
        const totalNotes = octaves * 12;

        for (let i = 0; i < totalNotes; i++) {
            const midi = startMidi + i;
            const noteIndex = midi % 12;
            result.push({
                midi,
                isBlack: isBlackKey(noteIndex),
                noteName: NOTE_NAMES[noteIndex],
            });
        }

        return result;
    }, [octaves, startOctave]);

    // Count white keys for width calculation
    const whiteKeys = keys.filter(k => !k.isBlack);
    const totalWidth = whiteKeys.length * white.width;

    const getKeyStyle = (midi: number, keyIsBlack: boolean) => {
        const isHighlighted = highlightedNotes.includes(midi);
        const isRoot = rootNote === midi;

        if (keyIsBlack) {
            if (isRoot) return 'bg-violet-500 border-violet-400';
            if (isHighlighted) return 'bg-cyan-500 border-cyan-400';
            return 'bg-slate-900 border-slate-700 hover:bg-slate-800';
        }

        if (isRoot) return 'bg-violet-400 border-violet-500';
        if (isHighlighted) return 'bg-cyan-400 border-cyan-500';
        return 'bg-white border-slate-300 hover:bg-slate-100';
    };

    // Calculate positions
    let whiteKeyIndex = 0;

    return (
        <div
            className="relative inline-flex"
            style={{ width: totalWidth, height: white.height }}
        >
            {/* White keys first */}
            {keys.map((key) => {
                if (key.isBlack) return null;

                const index = whiteKeyIndex++;
                const left = index * white.width;
                const isHighlighted = highlightedNotes.includes(key.midi);
                const isRoot = rootNote === key.midi;

                return (
                    <motion.button
                        key={key.midi}
                        onClick={() => onNoteClick?.(key.midi)}
                        whileHover={{ y: 2 }}
                        whileTap={{ y: 4 }}
                        className={`absolute rounded-b-md border-2 transition-colors ${getKeyStyle(key.midi, false)}`}
                        style={{
                            left,
                            top: 0,
                            width: white.width,
                            height: white.height,
                            zIndex: 1,
                        }}
                    >
                        {showNoteNames && (
                            <span
                                className={`absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-medium ${isRoot || isHighlighted ? 'text-white' : 'text-slate-600'
                                    }`}
                            >
                                {key.noteName}
                            </span>
                        )}
                    </motion.button>
                );
            })}

            {/* Black keys on top */}
            {(() => {
                let whiteIdx = 0;
                return keys.map((key, i) => {
                    if (!key.isBlack) {
                        whiteIdx++;
                        return null;
                    }

                    // Black key position is between white keys
                    const left = whiteIdx * white.width - black.width / 2;
                    const isHighlighted = highlightedNotes.includes(key.midi);
                    const isRoot = rootNote === key.midi;

                    return (
                        <motion.button
                            key={key.midi}
                            onClick={() => onNoteClick?.(key.midi)}
                            whileHover={{ y: 2 }}
                            whileTap={{ y: 4 }}
                            className={`absolute rounded-b-md border-2 transition-colors ${getKeyStyle(key.midi, true)}`}
                            style={{
                                left,
                                top: 0,
                                width: black.width,
                                height: black.height,
                                zIndex: 2,
                            }}
                        >
                            {showNoteNames && (
                                <span
                                    className={`absolute bottom-1 left-1/2 -translate-x-1/2 text-[10px] font-medium ${isRoot || isHighlighted ? 'text-white' : 'text-slate-500'
                                        }`}
                                >
                                    {key.noteName}
                                </span>
                            )}
                        </motion.button>
                    );
                });
            })()}
        </div>
    );
}
