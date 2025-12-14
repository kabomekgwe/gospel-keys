/**
 * Voicings Display Component
 * 
 * Displays interactive VoicingKeyboard for detected chords in a song.
 * Fetches voicing data from backend and shows visual representations.
 */
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { VoicingKeyboard, type VoicingInfo, type VoicingNote } from '../VoicingKeyboard';
import type { ChordRegion } from '../../lib/api';

interface VoicingsDisplayProps {
    /** Detected chords from the song */
    chords: ChordRegion[];
    /** Song ID for context */
    songId: string;
    /** Maximum chords to show at once */
    maxVisible?: number;
    /** Compact mode */
    compact?: boolean;
    /** Additional CSS classes */
    className?: string;
}

// Fetch voicing info from backend
async function fetchVoicing(chord: string): Promise<VoicingInfo | null> {
    try {
        const res = await fetch(`/api/v1/voicing/${encodeURIComponent(chord)}`);
        if (!res.ok) return null;
        const data = await res.json();

        // Transform API response to VoicingInfo format
        return {
            chord: data.chord,
            voicing_type: data.voicing_type,
            notes: data.notes.map((n: any): VoicingNote => ({
                pitch: n.pitch,
                hand: n.hand,
                finger: n.finger,
            })),
            intervals: data.intervals,
            width_semitones: data.width_semitones,
            complexity_score: data.complexity_score,
            hand_span_inches: data.hand_span_inches,
            has_root: data.has_root,
            has_third: data.has_third,
            has_seventh: data.has_seventh,
            extensions: data.extensions,
        };
    } catch (e) {
        console.error('Failed to fetch voicing:', e);
        return null;
    }
}

export function VoicingsDisplay({
    chords,
    songId,
    maxVisible = 4,
    compact = false,
    className = '',
}: VoicingsDisplayProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedChord, setSelectedChord] = useState<string | null>(null);

    // Get unique chord symbols
    const uniqueChords = useMemo(() => {
        const seen = new Set<string>();
        return chords.filter(c => {
            if (!c.chord || seen.has(c.chord)) return false;
            seen.add(c.chord);
            return true;
        });
    }, [chords]);

    // Visible chords slice
    const visibleChords = useMemo(() => {
        return uniqueChords.slice(currentIndex, currentIndex + maxVisible);
    }, [uniqueChords, currentIndex, maxVisible]);

    // Fetch voicing for selected chord
    const { data: selectedVoicing, isLoading: voicingLoading } = useQuery({
        queryKey: ['voicing', selectedChord],
        queryFn: () => selectedChord ? fetchVoicing(selectedChord) : null,
        enabled: !!selectedChord,
    });

    const canGoBack = currentIndex > 0;
    const canGoForward = currentIndex + maxVisible < uniqueChords.length;

    return (
        <div className={`space-y-4 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Layers className="w-5 h-5 text-violet-400" />
                    Chord Voicings
                </h3>

                <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-400">
                        {uniqueChords.length} unique chords
                    </span>

                    <div className="flex gap-1">
                        <button
                            onClick={() => setCurrentIndex(i => Math.max(0, i - maxVisible))}
                            disabled={!canGoBack}
                            className={`p-1.5 rounded-lg transition-colors ${canGoBack
                                    ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    : 'bg-slate-800/50 text-slate-600 cursor-not-allowed'
                                }`}
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setCurrentIndex(i => Math.min(uniqueChords.length - maxVisible, i + maxVisible))}
                            disabled={!canGoForward}
                            className={`p-1.5 rounded-lg transition-colors ${canGoForward
                                    ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    : 'bg-slate-800/50 text-slate-600 cursor-not-allowed'
                                }`}
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Chord buttons */}
            <div className="grid grid-cols-4 gap-2">
                {visibleChords.map((chord, i) => (
                    <motion.button
                        key={chord.chord}
                        onClick={() => setSelectedChord(chord.chord || null)}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.05 }}
                        className={`
              p-4 rounded-xl text-center transition-all
              ${selectedChord === chord.chord
                                ? 'bg-violet-600 text-white ring-2 ring-violet-400'
                                : 'bg-slate-800/50 text-slate-200 hover:bg-slate-700/50 border border-slate-700/50'
                            }
            `}
                    >
                        <div className="text-xl font-bold mb-1">{chord.chord}</div>
                        <div className="text-xs text-slate-400">
                            {chord.time.toFixed(1)}s
                        </div>
                    </motion.button>
                ))}
            </div>

            {/* Selected chord visualization */}
            <AnimatePresence mode="wait">
                {selectedChord && (
                    <motion.div
                        key={selectedChord}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-slate-800/30 rounded-xl p-6 border border-slate-700/50"
                    >
                        {voicingLoading ? (
                            <div className="flex items-center justify-center py-12">
                                <Loader2 className="w-8 h-8 animate-spin text-violet-400" />
                            </div>
                        ) : selectedVoicing ? (
                            <VoicingKeyboard
                                chord={selectedChord}
                                voicing={selectedVoicing}
                                showFingering={true}
                                showComplexity={true}
                                compact={compact}
                            />
                        ) : (
                            <div className="text-center py-8 text-slate-400">
                                <p>Unable to load voicing for {selectedChord}</p>
                                <p className="text-sm mt-1">Try restarting the backend server</p>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Instructions */}
            {!selectedChord && uniqueChords.length > 0 && (
                <div className="text-center py-8 text-slate-500">
                    <Layers className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>Click a chord to view its voicing</p>
                </div>
            )}

            {uniqueChords.length === 0 && (
                <div className="text-center py-8 text-slate-500">
                    <p>No chords detected in this song</p>
                </div>
            )}
        </div>
    );
}
