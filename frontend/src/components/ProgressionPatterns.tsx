/**
 * Progression Patterns Component
 * 
 * Display detected chord progression patterns with:
 * - Pattern name and genre tags
 * - Example progressions
 * - Explanations and musical context
 */
import { motion } from 'framer-motion';
import { Info, Music, Sparkles, Tag } from 'lucide-react';

export interface ProgressionPattern {
    id: string;
    name: string;
    pattern: string[];        // e.g., ['I', 'V', 'vi', 'IV']
    chords: string[];         // e.g., ['C', 'G', 'Am', 'F']
    genre: string;
    confidence: number;       // 0-1
    start_time: number;
    end_time: number;
    description?: string;
    famousExamples?: string[];
}

export interface ProgressionPatternsProps {
    patterns: ProgressionPattern[];
    currentTime?: number;
    onPatternClick?: (pattern: ProgressionPattern) => void;
    selectedPatternId?: string;
}

// Genre badge colors
const GENRE_COLORS: Record<string, string> = {
    pop: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
    rock: 'bg-red-500/20 text-red-400 border-red-500/30',
    jazz: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
    blues: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    classical: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    country: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    folk: 'bg-green-500/20 text-green-400 border-green-500/30',
    default: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
};

function getGenreColor(genre: string): string {
    const normalizedGenre = genre.toLowerCase();
    return GENRE_COLORS[normalizedGenre] || GENRE_COLORS.default;
}

export function ProgressionPatterns({
    patterns,
    currentTime = 0,
    onPatternClick,
    selectedPatternId,
}: ProgressionPatternsProps) {
    // Find active pattern
    const activePattern = patterns.find(
        p => currentTime >= p.startTime && currentTime < p.endTime
    );

    if (patterns.length === 0) {
        return (
            <div className="card p-8 text-center">
                <Music className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400">No patterns detected</p>
                <p className="text-sm text-slate-500 mt-1">
                    This song may have a unique or complex progression
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Summary */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">
                    Detected Patterns
                    <span className="ml-2 text-sm font-normal text-slate-400">
                        ({patterns.length} found)
                    </span>
                </h3>

                {activePattern && (
                    <span className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/20 text-cyan-400 rounded-full text-sm">
                        <Sparkles className="w-4 h-4" />
                        Now: {activePattern.name}
                    </span>
                )}
            </div>

            {/* Pattern cards */}
            <div className="grid gap-4 md:grid-cols-2">
                {patterns.map((pattern, index) => {
                    const isActive = activePattern?.id === pattern.id;
                    const isSelected = selectedPatternId === pattern.id;

                    return (
                        <motion.div
                            key={pattern.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            onClick={() => onPatternClick?.(pattern)}
                            className={`
                card p-5 cursor-pointer transition-all
                ${isActive ? 'ring-2 ring-cyan-400' : ''}
                ${isSelected ? 'ring-2 ring-violet-400' : ''}
                hover:border-slate-600
              `}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-3">
                                <div>
                                    <h4 className="text-white font-medium">{pattern.name}</h4>
                                    <div className="flex items-center gap-2 mt-1">
                                        <span className={`px-2 py-0.5 rounded text-xs border ${getGenreColor(pattern.genre)}`}>
                                            {pattern.genre}
                                        </span>
                                        <span className="text-xs text-slate-500">
                                            {Math.round(pattern.confidence * 100)}% match
                                        </span>
                                    </div>
                                </div>

                                {isActive && (
                                    <span className="w-3 h-3 bg-cyan-400 rounded-full animate-pulse" />
                                )}
                            </div>

                            {/* Chord progression */}
                            <div className="flex items-center gap-2 mb-3 overflow-x-auto pb-1">
                                {pattern.pattern.map((numeral, i) => (
                                    <div key={i} className="flex items-center gap-1">
                                        <div className="flex flex-col items-center min-w-[40px]">
                                            <span className="text-sm font-bold text-cyan-400">
                                                {numeral}
                                            </span>
                                            <span className="text-xs text-slate-400">
                                                {pattern.chords[i]}
                                            </span>
                                        </div>
                                        {i < pattern.pattern.length - 1 && (
                                            <span className="text-slate-600">→</span>
                                        )}
                                    </div>
                                ))}
                            </div>

                            {/* Description */}
                            {pattern.description && (
                                <p className="text-sm text-slate-400 mb-3">
                                    {pattern.description}
                                </p>
                            )}

                            {/* Famous examples */}
                            {pattern.famousExamples && pattern.famousExamples.length > 0 && (
                                <div className="flex items-start gap-2 text-xs">
                                    <Tag className="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0" />
                                    <span className="text-slate-500">
                                        {pattern.famousExamples.slice(0, 3).join(' • ')}
                                    </span>
                                </div>
                            )}

                            {/* Time range */}
                            <div className="flex items-center gap-2 mt-3 pt-3 border-t border-slate-700/50 text-xs text-slate-500">
                                <span>
                                    {formatTime(pattern.start_time)} - {formatTime(pattern.end_time)}
                                </span>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Common progression presets for reference
export const COMMON_PROGRESSIONS = [
    {
        name: 'I–V–vi–IV (Axis of Awesome)',
        pattern: ['I', 'V', 'vi', 'IV'],
        genre: 'Pop',
        examples: ['Let It Be', 'No Woman No Cry', 'With or Without You'],
    },
    {
        name: '50s Progression',
        pattern: ['I', 'vi', 'IV', 'V'],
        genre: 'Pop',
        examples: ['Stand By Me', 'Earth Angel', 'Unchained Melody'],
    },
    {
        name: 'ii–V–I',
        pattern: ['ii', 'V', 'I'],
        genre: 'Jazz',
        examples: ['Autumn Leaves', 'All The Things You Are'],
    },
    {
        name: 'I–IV–V (12 Bar Blues)',
        pattern: ['I', 'I', 'I', 'I', 'IV', 'IV', 'I', 'I', 'V', 'IV', 'I', 'V'],
        genre: 'Blues',
        examples: ['Johnny B. Goode', 'Sweet Home Chicago'],
    },
    {
        name: 'Andalusian Cadence',
        pattern: ['i', 'VII', 'VI', 'V'],
        genre: 'Classical',
        examples: ['Hit The Road Jack', 'Smooth'],
    },
];
