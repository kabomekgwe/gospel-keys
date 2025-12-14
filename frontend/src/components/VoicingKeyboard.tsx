/**
 * Voicing Keyboard Component
 * 
 * Interactive piano keyboard specialized for displaying chord voicings.
 * Features:
 * - Left/right hand color coding (blue/green)
 * - Fingering number overlays (1-5)
 * - Hand span indicator
 * - Complexity badge
 * - Interval display
 */
import { useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Piano } from './Piano';

export interface VoicingNote {
    pitch: number;
    hand: 'left' | 'right';
    finger?: number; // 1-5 fingering (thumb=1)
}

export interface VoicingInfo {
    chord: string;
    voicing_type: string;
    notes: VoicingNote[];
    intervals?: number[];
    width_semitones?: number;
    complexity_score?: number;
    hand_span_inches?: number;
    has_root?: boolean;
    has_third?: boolean;
    has_seventh?: boolean;
    extensions?: string[];
}

export interface VoicingKeyboardProps {
    /** Chord symbol being displayed */
    chord: string;
    /** Voicing information */
    voicing: VoicingInfo;
    /** Optional: show only one hand */
    showHand?: 'left' | 'right' | 'both';
    /** Callback when a note is clicked */
    onNotePlay?: (pitch: number) => void;
    /** Show fingering numbers */
    showFingering?: boolean;
    /** Show intervals between notes */
    showIntervals?: boolean;
    /** Show complexity badge */
    showComplexity?: boolean;
    /** Compact mode for smaller displays */
    compact?: boolean;
    /** Additional CSS classes */
    className?: string;
}

const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

function getNoteName(pitch: number): string {
    const octave = Math.floor(pitch / 12) - 1;
    const name = NOTE_NAMES[pitch % 12];
    return `${name}${octave}`;
}

function getComplexityLabel(score: number): { label: string; color: string } {
    if (score < 0.3) return { label: 'Beginner', color: 'bg-green-500' };
    if (score < 0.5) return { label: 'Easy', color: 'bg-emerald-500' };
    if (score < 0.7) return { label: 'Intermediate', color: 'bg-amber-500' };
    if (score < 0.85) return { label: 'Advanced', color: 'bg-orange-500' };
    return { label: 'Expert', color: 'bg-red-500' };
}

export function VoicingKeyboard({
    chord,
    voicing,
    showHand = 'both',
    onNotePlay,
    showFingering = true,
    showIntervals = false,
    showComplexity = true,
    compact = false,
    className = '',
}: VoicingKeyboardProps) {
    // Filter notes by hand selection
    const visibleNotes = useMemo(() => {
        if (showHand === 'both') return voicing.notes;
        return voicing.notes.filter(n => n.hand === showHand);
    }, [voicing.notes, showHand]);

    // Create color map for left/right hand differentiation
    const noteColors = useMemo(() => {
        const colors = new Map<number, string>();
        visibleNotes.forEach(note => {
            // Left hand = blue, Right hand = green
            colors.set(note.pitch, note.hand === 'left' ? 'blue' : 'green');
        });
        return colors;
    }, [visibleNotes]);

    // Calculate pitch range with padding
    const { minPitch, maxPitch } = useMemo(() => {
        if (visibleNotes.length === 0) return { minPitch: 48, maxPitch: 72 };

        const pitches = visibleNotes.map(n => n.pitch);
        const min = Math.min(...pitches);
        const max = Math.max(...pitches);

        // Ensure we start on a C and have some padding
        const paddedMin = Math.floor((min - 5) / 12) * 12;
        const paddedMax = Math.ceil((max + 5) / 12) * 12;

        return {
            minPitch: Math.max(21, paddedMin), // A0 minimum
            maxPitch: Math.min(108, paddedMax), // C8 maximum
        };
    }, [visibleNotes]);

    const activeNotes = useMemo(() =>
        visibleNotes.map(n => n.pitch),
        [visibleNotes]
    );

    // Group notes by hand
    const { leftNotes, rightNotes } = useMemo(() => ({
        leftNotes: voicing.notes.filter(n => n.hand === 'left'),
        rightNotes: voicing.notes.filter(n => n.hand === 'right'),
    }), [voicing.notes]);

    const complexity = useMemo(() => {
        if (voicing.complexity_score === undefined) return null;
        return getComplexityLabel(voicing.complexity_score);
    }, [voicing.complexity_score]);

    const keySize = compact ? 28 : 40;

    return (
        <div className={`flex flex-col gap-4 ${className}`}>
            {/* Header with chord info */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h3 className="text-2xl font-bold text-slate-100">{chord}</h3>
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-slate-700 text-slate-300">
                        {voicing.voicing_type.replace(/_/g, ' ')}
                    </span>
                </div>

                {showComplexity && complexity && (
                    <div className={`px-3 py-1 text-xs font-semibold rounded-full text-white ${complexity.color}`}>
                        {complexity.label}
                    </div>
                )}
            </div>

            {/* Hand legend */}
            <div className="flex items-center gap-4 text-sm">
                {(showHand === 'both' || showHand === 'left') && leftNotes.length > 0 && (
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-blue-500" />
                        <span className="text-slate-400">
                            Left Hand ({leftNotes.length} notes)
                        </span>
                    </div>
                )}
                {(showHand === 'both' || showHand === 'right') && rightNotes.length > 0 && (
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-green-500" />
                        <span className="text-slate-400">
                            Right Hand ({rightNotes.length} notes)
                        </span>
                    </div>
                )}
            </div>

            {/* Piano keyboard with overlays */}
            <div className="relative">
                <Piano
                    minPitch={minPitch}
                    maxPitch={maxPitch}
                    activeNotes={activeNotes}
                    noteColors={noteColors}
                    onNotePlay={onNotePlay}
                    showLabels={!compact}
                    keySize={keySize}
                />

                {/* Fingering overlays */}
                {showFingering && (
                    <FingeringOverlay
                        notes={visibleNotes}
                        minPitch={minPitch}
                        keySize={keySize}
                        compact={compact}
                    />
                )}
            </div>

            {/* Note details */}
            <div className="flex flex-wrap gap-2">
                {visibleNotes.map(note => (
                    <motion.button
                        key={note.pitch}
                        onClick={() => onNotePlay?.(note.pitch)}
                        className={`
              px-3 py-1.5 rounded-lg text-sm font-medium
              transition-colors cursor-pointer
              ${note.hand === 'left'
                                ? 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30 border border-blue-500/30'
                                : 'bg-green-500/20 text-green-300 hover:bg-green-500/30 border border-green-500/30'
                            }
            `}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        {getNoteName(note.pitch)}
                        {note.finger && <span className="ml-1 opacity-60">({note.finger})</span>}
                    </motion.button>
                ))}
            </div>

            {/* Additional info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                {voicing.width_semitones !== undefined && (
                    <InfoBadge label="Span" value={`${voicing.width_semitones} semitones`} />
                )}
                {voicing.hand_span_inches !== undefined && (
                    <InfoBadge label="Hand Span" value={`${voicing.hand_span_inches.toFixed(1)}"`} />
                )}
                {voicing.has_root !== undefined && (
                    <InfoBadge
                        label="Chord Tones"
                        value={[
                            voicing.has_root && 'R',
                            voicing.has_third && '3',
                            voicing.has_seventh && '7',
                        ].filter(Boolean).join(', ') || 'None'}
                    />
                )}
                {voicing.extensions && voicing.extensions.length > 0 && (
                    <InfoBadge label="Extensions" value={voicing.extensions.join(', ')} />
                )}
            </div>

            {/* Intervals display */}
            {showIntervals && voicing.intervals && voicing.intervals.length > 0 && (
                <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span>Intervals:</span>
                    {voicing.intervals.map((interval, i) => (
                        <span
                            key={i}
                            className="px-2 py-0.5 rounded bg-slate-700 font-mono"
                        >
                            {interval}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}

function InfoBadge({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex flex-col gap-0.5 p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
            <span className="text-xs text-slate-500">{label}</span>
            <span className="font-medium text-slate-200">{value}</span>
        </div>
    );
}

interface FingeringOverlayProps {
    notes: VoicingNote[];
    minPitch: number;
    keySize: number;
    compact: boolean;
}

function FingeringOverlay({ notes, minPitch, keySize, compact }: FingeringOverlayProps) {
    const BLACK_KEY_INDICES = [1, 3, 6, 8, 10];

    const isBlackKey = (pitch: number) => BLACK_KEY_INDICES.includes(pitch % 12);

    // Calculate position for each fingering indicator
    const getPosition = useCallback((pitch: number) => {
        let whiteKeyCount = 0;
        for (let p = minPitch; p < pitch; p++) {
            if (!isBlackKey(p)) whiteKeyCount++;
        }

        const isBlack = isBlackKey(pitch);
        const x = whiteKeyCount * keySize + (isBlack ? keySize * 0.3 : keySize * 0.5);
        const y = isBlack ? keySize * 1.8 : keySize * 3.2;

        return { x, y, isBlack };
    }, [minPitch, keySize]);

    return (
        <div className="absolute inset-0 pointer-events-none">
            <AnimatePresence>
                {notes.map(note => {
                    if (!note.finger) return null;

                    const { x, y, isBlack } = getPosition(note.pitch);

                    return (
                        <motion.div
                            key={note.pitch}
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0 }}
                            className={`
                absolute flex items-center justify-center
                rounded-full font-bold text-xs
                ${compact ? 'w-4 h-4' : 'w-5 h-5'}
                ${note.hand === 'left'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-green-500 text-white'
                                }
                shadow-lg
              `}
                            style={{
                                left: x - (compact ? 8 : 10),
                                top: y - (compact ? 8 : 10),
                            }}
                        >
                            {note.finger}
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
}

// Standalone mini version for chord charts
export function MiniVoicingKeyboard({
    voicing,
    className = '',
}: {
    voicing: VoicingInfo;
    className?: string;
}) {
    const noteColors = useMemo(() => {
        const colors = new Map<number, string>();
        voicing.notes.forEach(note => {
            colors.set(note.pitch, note.hand === 'left' ? 'blue' : 'green');
        });
        return colors;
    }, [voicing.notes]);

    const pitches = voicing.notes.map(n => n.pitch);
    const minPitch = Math.min(...pitches) - 2;
    const maxPitch = Math.max(...pitches) + 2;

    return (
        <div className={`inline-block ${className}`}>
            <Piano
                minPitch={Math.floor(minPitch / 12) * 12}
                maxPitch={Math.ceil(maxPitch / 12) * 12}
                activeNotes={pitches}
                noteColors={noteColors}
                showLabels={false}
                keySize={16}
            />
        </div>
    );
}
