/**
 * Piano Keyboard Component
 * 
 * Interactive piano keyboard with visual note highlighting
 * Features:
 * - Full 88-key layout (or custom range)
 * - Active note highlighting with colors
 * - Click-to-play functionality
 * - Responsive sizing
 */
import { useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface PianoProps {
    /** MIDI pitch range (default: 21-108 for full 88 keys) */
    minPitch?: number;
    maxPitch?: number;
    /** Currently active/pressed notes (MIDI pitches) */
    activeNotes?: number[];
    /** Notes highlighted for learning (MIDI pitches) */
    targetNotes?: number[];
    /** Custom colors for specific notes (MIDI pitch → color) */
    noteColors?: Map<number, string>;
    /** Callback when a key is clicked */
    onNotePlay?: (pitch: number) => void;
    /** Callback when a key is released */
    onNoteStop?: (pitch: number) => void;
    /** Show note labels on keys */
    showLabels?: boolean;
    /** Vertical or horizontal orientation */
    orientation?: 'horizontal' | 'vertical';
    /** Key height/width in pixels */
    keySize?: number;
    /** Additional CSS classes */
    className?: string;
}

const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const BLACK_KEY_INDICES = [1, 3, 6, 8, 10];

function isBlackKey(pitch: number): boolean {
    return BLACK_KEY_INDICES.includes(pitch % 12);
}

function getNoteName(pitch: number, includeOctave = true): string {
    const octave = Math.floor(pitch / 12) - 1;
    const name = NOTE_NAMES[pitch % 12];
    return includeOctave ? `${name}${octave}` : name;
}

// Black key offsets relative to white keys (percentage from left edge of adjacent white key)
function getBlackKeyOffset(noteIndex: number): number {
    const offsets: Record<number, number> = {
        1: 0.65,  // C#
        3: 0.75,  // D#
        6: 0.60,  // F#
        8: 0.67,  // G#
        10: 0.75, // A#
    };
    return offsets[noteIndex] || 0.7;
}

export function Piano({
    minPitch = 48, // C3
    maxPitch = 84, // C6
    activeNotes = [],
    targetNotes = [],
    noteColors,
    onNotePlay,
    onNoteStop,
    showLabels = true,
    orientation = 'horizontal',
    keySize = 40,
    className = '',
}: PianoProps) {
    // Build key data
    const keys = useMemo(() => {
        const whiteKeys: number[] = [];
        const blackKeys: number[] = [];

        for (let pitch = minPitch; pitch <= maxPitch; pitch++) {
            if (isBlackKey(pitch)) {
                blackKeys.push(pitch);
            } else {
                whiteKeys.push(pitch);
            }
        }

        return { whiteKeys, blackKeys };
    }, [minPitch, maxPitch]);

    // Calculate dimensions
    const whiteKeyWidth = keySize;
    const whiteKeyHeight = keySize * 4;
    const blackKeyWidth = keySize * 0.6;
    const blackKeyHeight = keySize * 2.4;

    const totalWidth = keys.whiteKeys.length * whiteKeyWidth;
    const isVertical = orientation === 'vertical';

    // Handle mouse events
    const handleMouseDown = useCallback((pitch: number) => {
        onNotePlay?.(pitch);
    }, [onNotePlay]);

    const handleMouseUp = useCallback((pitch: number) => {
        onNoteStop?.(pitch);
    }, [onNoteStop]);

    // Get key color based on state
    const getKeyStyle = useCallback((pitch: number, isWhite: boolean) => {
        const isActive = activeNotes.includes(pitch);
        const isTarget = targetNotes.includes(pitch);
        const customColor = noteColors?.get(pitch);

        // Custom color takes precedence
        if (customColor) {
            return isWhite
                ? `bg-gradient-to-b from-${customColor}-300 to-${customColor}-400 shadow-md shadow-${customColor}-400/30`
                : `bg-gradient-to-b from-${customColor}-500 to-${customColor}-600`;
        }

        if (isActive) {
            return isWhite
                ? 'bg-gradient-to-b from-cyan-400 to-cyan-500 shadow-lg shadow-cyan-500/50'
                : 'bg-gradient-to-b from-cyan-500 to-cyan-600';
        }
        if (isTarget) {
            return isWhite
                ? 'bg-gradient-to-b from-violet-300 to-violet-400 shadow-md shadow-violet-400/30'
                : 'bg-gradient-to-b from-violet-500 to-violet-600';
        }
        return isWhite
            ? 'bg-gradient-to-b from-slate-100 to-slate-200 hover:from-slate-50 hover:to-slate-100'
            : 'bg-gradient-to-b from-slate-800 to-slate-900 hover:from-slate-700 hover:to-slate-800';
    }, [activeNotes, targetNotes, noteColors]);

    // Calculate black key positions
    const getBlackKeyPosition = useCallback((pitch: number): number => {
        // Find the white key to the left
        let whiteKeyIndex = 0;
        for (let p = minPitch; p < pitch; p++) {
            if (!isBlackKey(p)) whiteKeyIndex++;
        }

        const noteIndex = pitch % 12;
        const offset = getBlackKeyOffset(noteIndex);
        return whiteKeyIndex * whiteKeyWidth - blackKeyWidth * offset;
    }, [minPitch, whiteKeyWidth, blackKeyWidth]);

    // Handle keyboard events for accessibility
    const handleKeyDown = useCallback((event: React.KeyboardEvent, pitch: number) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            onNotePlay?.(pitch);
        }
    }, [onNotePlay]);

    const handleKeyUp = useCallback((event: React.KeyboardEvent, pitch: number) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            onNoteStop?.(pitch);
        }
    }, [onNoteStop]);

    return (
        <div
            className={`relative select-none ${isVertical ? 'flex flex-col' : ''} ${className}`}
            role="application"
            aria-label="Piano Keyboard"
            style={{
                width: isVertical ? whiteKeyHeight : totalWidth,
                height: isVertical ? totalWidth : whiteKeyHeight,
            }}
        >
            {/* White keys */}
            <div
                className={`absolute inset-0 flex ${isVertical ? 'flex-col' : ''}`}
                style={{ zIndex: 1 }}
            >
                {keys.whiteKeys.map((pitch, index) => {
                    const isActive = activeNotes.includes(pitch);
                    const isC = pitch % 12 === 0;

                    return (
                        <motion.button
                            key={pitch}
                            type="button"
                            className={`
                relative flex items-end justify-center pb-2
                border border-slate-300
                rounded-b-md
                transition-colors duration-75
                focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2
                ${getKeyStyle(pitch, true)}
              `}
                            style={{
                                width: isVertical ? whiteKeyHeight : whiteKeyWidth,
                                height: isVertical ? whiteKeyWidth : whiteKeyHeight,
                            }}
                            onMouseDown={() => handleMouseDown(pitch)}
                            onMouseUp={() => handleMouseUp(pitch)}
                            onMouseLeave={() => handleMouseUp(pitch)}
                            onKeyDown={(e) => handleKeyDown(e, pitch)}
                            onKeyUp={(e) => handleKeyUp(e, pitch)}
                            aria-label={`${getNoteName(pitch)} key${isActive ? ', active' : ''}`}
                            aria-pressed={isActive}
                            tabIndex={0}
                            whileTap={{ scale: 0.98 }}
                        >
                            {showLabels && isC && (
                                <span className={`
                  text-xs font-medium
                  ${isActive ? 'text-slate-900' : 'text-slate-500'}
                `}>
                                    {getNoteName(pitch)}
                                </span>
                            )}

                            {/* Active indicator glow */}
                            <AnimatePresence>
                                {isActive && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.8 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.8 }}
                                        className="absolute inset-0 rounded-b-md bg-cyan-400/30 blur-sm"
                                    />
                                )}
                            </AnimatePresence>
                        </motion.button>
                    );
                })}
            </div>

            {/* Black keys */}
            <div
                className="absolute top-0 left-0"
                style={{ zIndex: 2 }}
            >
                {keys.blackKeys.map((pitch) => {
                    const position = getBlackKeyPosition(pitch);
                    const isActive = activeNotes.includes(pitch);

                    return (
                        <motion.button
                            key={pitch}
                            type="button"
                            className={`
                absolute flex items-end justify-center pb-1
                rounded-b-md
                shadow-md
                transition-colors duration-75
                focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2
                ${getKeyStyle(pitch, false)}
              `}
                            style={{
                                left: isVertical ? 0 : position,
                                top: isVertical ? position : 0,
                                width: isVertical ? blackKeyHeight : blackKeyWidth,
                                height: isVertical ? blackKeyWidth : blackKeyHeight,
                            }}
                            onMouseDown={() => handleMouseDown(pitch)}
                            onMouseUp={() => handleMouseUp(pitch)}
                            onMouseLeave={() => handleMouseUp(pitch)}
                            onKeyDown={(e) => handleKeyDown(e, pitch)}
                            onKeyUp={(e) => handleKeyUp(e, pitch)}
                            aria-label={`${getNoteName(pitch)} key${isActive ? ', active' : ''}`}
                            aria-pressed={isActive}
                            tabIndex={0}
                            whileTap={{ scale: 0.95 }}
                        >
                            {/* Active indicator glow */}
                            <AnimatePresence>
                                {isActive && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.8 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.8 }}
                                        className="absolute inset-0 rounded-b-md bg-cyan-500/40 blur-sm"
                                    />
                                )}
                            </AnimatePresence>
                        </motion.button>
                    );
                })}
            </div>
        </div>
    );
}

// Compact piano for smaller areas
export function MiniPiano({
    activeNotes = [],
    targetNotes = [],
    minPitch = 60,
    maxPitch = 72,
}: Pick<PianoProps, 'activeNotes' | 'targetNotes' | 'minPitch' | 'maxPitch'>) {
    return (
        <div className="inline-flex items-center gap-0.5 p-2 bg-slate-800/50 rounded-lg">
            {Array.from({ length: maxPitch - minPitch + 1 }, (_, i) => {
                const pitch = minPitch + i;
                const isBlack = isBlackKey(pitch);
                const isActive = activeNotes.includes(pitch);
                const isTarget = targetNotes.includes(pitch);

                return (
                    <div
                        key={pitch}
                        className={`
              transition-all duration-75 rounded-sm
              ${isBlack ? 'h-4 w-2 -mx-1 z-10' : 'h-6 w-3'}
              ${isActive
                                ? 'bg-cyan-400 shadow-sm shadow-cyan-500/50'
                                : isTarget
                                    ? 'bg-violet-400/80'
                                    : isBlack
                                        ? 'bg-slate-700'
                                        : 'bg-slate-300'
                            }
            `}
                    />
                );
            })}
        </div>
    );
}
