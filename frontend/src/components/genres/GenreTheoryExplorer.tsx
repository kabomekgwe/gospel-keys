/**
 * Genre Theory Explorer Component
 *
 * Explore how advanced music theory applies to each genre:
 * - Gospel: Modal interchange, chromatic approaches, backdoor progressions
 * - Jazz: Coltrane changes, tritone substitutions, Barry Harris diminished
 * - Blues: 12-bar forms, diminished passing, blues scale
 * - Neo-Soul: Extended voicings, negative harmony, smooth voice leading
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Music,
    Sparkles,
    TrendingUp,
    Zap,
    BookOpen,
    Play,
    ChevronRight,
    Info
} from 'lucide-react';

type GenreType = 'gospel' | 'jazz' | 'blues' | 'neosoul';

interface TheoryTechnique {
    name: string;
    description: string;
    example: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced';
}

interface GenreTheoryInfo {
    name: string;
    icon: React.ReactNode;
    color: string;
    description: string;
    techniques: TheoryTechnique[];
    commonProgressions: string[];
}

const GENRE_THEORY: Record<GenreType, GenreTheoryInfo> = {
    gospel: {
        name: 'Gospel',
        icon: <Music className="w-6 h-6" />,
        color: 'purple',
        description: 'Gospel music uses rich harmonic colors through modal interchange and chromatic movement for emotional expression.',
        techniques: [
            {
                name: 'Modal Interchange',
                description: 'Borrowing chords from parallel minor for emotional color',
                example: 'In C major, use iv (Fm) instead of IV (F) for melancholic color',
                difficulty: 'intermediate'
            },
            {
                name: 'Chromatic Approach',
                description: 'Half-step approach to target chords',
                example: 'F#dim7 → G7 (approaching dominant)',
                difficulty: 'beginner'
            },
            {
                name: 'Backdoor Progression',
                description: 'bVII7 → I for smooth resolution instead of V7 → I',
                example: 'Bb7 → C (instead of G7 → C)',
                difficulty: 'intermediate'
            },
            {
                name: 'Negative Harmony',
                description: 'Alternative harmonic resolution using mirror-image relationships',
                example: 'G7 → Fm (negative harmony of V → I)',
                difficulty: 'advanced'
            }
        ],
        commonProgressions: [
            'I - vi - ii - V (Traditional)',
            'I - IV - bVII - I (Contemporary)',
            'I - V7sus4 - V7 - vi - IV (Praise & Worship)'
        ]
    },
    jazz: {
        name: 'Jazz',
        icon: <Sparkles className="w-6 h-6" />,
        color: 'blue',
        description: 'Jazz harmony features complex substitutions, rapid modulations, and sophisticated voice leading techniques.',
        techniques: [
            {
                name: 'Coltrane Changes',
                description: 'Rapid modulation through three tonal centers separated by major thirds',
                example: 'B - Eb - G (Giant Steps pattern)',
                difficulty: 'advanced'
            },
            {
                name: 'Tritone Substitution',
                description: 'Replace dominant 7th with another dominant a tritone away',
                example: 'G7 → Db7 (both resolve to C)',
                difficulty: 'intermediate'
            },
            {
                name: 'Barry Harris Diminished',
                description: 'Four dominant 7ths from single diminished chord',
                example: 'Cdim7 → C7, Eb7, F#7, A7',
                difficulty: 'advanced'
            },
            {
                name: 'Modal Jazz',
                description: 'Static harmony emphasizing modes over chord changes',
                example: 'Dm7 (Dorian) for extended periods',
                difficulty: 'intermediate'
            }
        ],
        commonProgressions: [
            'ii - V - I (Standard cadence)',
            'Giant Steps cycle (B - D - G - Bb - Eb - F# - B)',
            'Modal vamps (static ii7 or i7)'
        ]
    },
    blues: {
        name: 'Blues',
        icon: <TrendingUp className="w-6 h-6" />,
        color: 'indigo',
        description: 'Blues harmony centers on dominant 7th chords, blue notes, and the iconic 12-bar form.',
        techniques: [
            {
                name: '12-Bar Blues Form',
                description: 'Standard blues progression structure',
                example: 'I7-I7-I7-I7-IV7-IV7-I7-I7-V7-IV7-I7-V7',
                difficulty: 'beginner'
            },
            {
                name: 'Quick IV Change',
                description: 'Move to IV chord in bar 2 instead of bar 5',
                example: 'I7-IV7-I7-I7-IV7-IV7-I7-I7-V7-IV7-I7-V7',
                difficulty: 'beginner'
            },
            {
                name: 'Diminished Passing Chords',
                description: 'Chromatic connection between I and IV',
                example: '#Idim7 between C7 and F7',
                difficulty: 'intermediate'
            },
            {
                name: 'Jazz Blues',
                description: 'Enhanced blues with ii-V substitutions',
                example: 'Imaj7 - IV7 - I7 - #ivdim7 - IV7 - #ivdim7',
                difficulty: 'advanced'
            }
        ],
        commonProgressions: [
            'Basic 12-bar blues',
            'Quick four blues',
            'Jazz blues with ii-V\'s'
        ]
    },
    neosoul: {
        name: 'Neo-Soul',
        icon: <Zap className="w-6 h-6" />,
        color: 'pink',
        description: 'Neo-soul features extended chord voicings, sophisticated harmony, and smooth voice leading.',
        techniques: [
            {
                name: 'Extended Chord Voicings',
                description: 'Rich maj9, m11, and dom13 chords throughout',
                example: 'Cmaj9 (rootless: E-G-B-D)',
                difficulty: 'intermediate'
            },
            {
                name: 'Rootless Voicings',
                description: 'Omit root (bass plays it) for modern sound',
                example: 'Dm11 (F-A-C-E-G without D)',
                difficulty: 'intermediate'
            },
            {
                name: 'Modal Mixture',
                description: 'Borrow bVII from parallel minor',
                example: 'In C major, use Bb major for neo-soul color',
                difficulty: 'intermediate'
            },
            {
                name: 'Negative Harmony',
                description: 'Alternative endings with mirror-image chords',
                example: 'Transform V-I into bII-I for unexpected resolution',
                difficulty: 'advanced'
            }
        ],
        commonProgressions: [
            'Imaj9 - vim11 - iim9 - V13 (Classic)',
            'Imaj9 - bVIImaj7 - IVmaj9 - iim11 (Modern)',
            'iiim7 - VI7b9 - iim7 - V7#5 (Jazzy)'
        ]
    }
};

interface GenreTheoryExplorerProps {
    initialGenre?: GenreType;
}

export function GenreTheoryExplorer({ initialGenre = 'gospel' }: GenreTheoryExplorerProps) {
    const [selectedGenre, setSelectedGenre] = useState<GenreType>(initialGenre);
    const [selectedTechnique, setSelectedTechnique] = useState<TheoryTechnique | null>(null);

    const genreInfo = GENRE_THEORY[selectedGenre];

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner': return 'text-green-400 bg-green-500/20';
            case 'intermediate': return 'text-yellow-400 bg-yellow-500/20';
            case 'advanced': return 'text-red-400 bg-red-500/20';
            default: return 'text-gray-400 bg-gray-500/20';
        }
    };

    return (
        <div className="space-y-6">
            {/* Genre Selector */}
            <div className="flex items-center gap-4">
                <BookOpen className="w-6 h-6 text-purple-500" />
                <h2 className="text-2xl font-bold text-white">Genre Theory Explorer</h2>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {(Object.entries(GENRE_THEORY) as [GenreType, GenreTheoryInfo][]).map(([key, info]) => (
                    <button
                        key={key}
                        onClick={() => {
                            setSelectedGenre(key);
                            setSelectedTechnique(null);
                        }}
                        className={`
                            p-4 rounded-xl border-2 transition-all
                            ${selectedGenre === key
                                ? `bg-${info.color}-500/20 border-${info.color}-500 shadow-lg shadow-${info.color}-500/20`
                                : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                            }
                        `}
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <div className={`${selectedGenre === key ? `text-${info.color}-400` : 'text-gray-400'}`}>
                                {info.icon}
                            </div>
                            <span className="text-white font-semibold">{info.name}</span>
                        </div>
                    </button>
                ))}
            </div>

            {/* Genre Info */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={selectedGenre}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-6"
                >
                    {/* Description */}
                    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                        <div className="flex items-start gap-4">
                            <Info className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
                            <div>
                                <h3 className="text-xl font-bold text-white mb-2">
                                    {genreInfo.name} Music Theory
                                </h3>
                                <p className="text-gray-300 leading-relaxed">
                                    {genreInfo.description}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Theory Techniques */}
                    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                        <h3 className="text-lg font-bold text-white mb-4">Theory Techniques</h3>

                        <div className="space-y-3">
                            {genreInfo.techniques.map((technique, index) => (
                                <button
                                    key={index}
                                    onClick={() => setSelectedTechnique(
                                        selectedTechnique?.name === technique.name ? null : technique
                                    )}
                                    className="w-full p-4 rounded-lg bg-gray-900/50 border border-gray-700 hover:border-purple-500/50 transition-all text-left group"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-3">
                                            <span className="text-white font-semibold group-hover:text-purple-400 transition-colors">
                                                {technique.name}
                                            </span>
                                            <span className={`
                                                px-2 py-1 rounded-full text-xs font-medium
                                                ${getDifficultyColor(technique.difficulty)}
                                            `}>
                                                {technique.difficulty}
                                            </span>
                                        </div>
                                        <ChevronRight className={`
                                            w-5 h-5 text-gray-400 transition-transform
                                            ${selectedTechnique?.name === technique.name ? 'rotate-90' : ''}
                                        `} />
                                    </div>

                                    <p className="text-gray-400 text-sm">
                                        {technique.description}
                                    </p>

                                    <AnimatePresence>
                                        {selectedTechnique?.name === technique.name && (
                                            <motion.div
                                                initial={{ opacity: 0, height: 0 }}
                                                animate={{ opacity: 1, height: 'auto' }}
                                                exit={{ opacity: 0, height: 0 }}
                                                transition={{ duration: 0.2 }}
                                                className="mt-3 pt-3 border-t border-gray-700"
                                            >
                                                <div className="flex items-start gap-2">
                                                    <Play className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                                                    <div>
                                                        <p className="text-xs text-gray-500 mb-1">Example:</p>
                                                        <p className="text-sm text-green-400 font-mono">
                                                            {technique.example}
                                                        </p>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Common Progressions */}
                    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                        <h3 className="text-lg font-bold text-white mb-4">Common Progressions</h3>

                        <div className="space-y-2">
                            {genreInfo.commonProgressions.map((progression, index) => (
                                <div
                                    key={index}
                                    className="p-3 rounded-lg bg-gray-900/50 border border-gray-700"
                                >
                                    <p className="text-gray-300 font-mono text-sm">
                                        {progression}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Try It Section */}
                    <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-xl border border-purple-500/30 p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <Sparkles className="w-6 h-6 text-purple-400" />
                            <h3 className="text-lg font-bold text-white">Try It Yourself</h3>
                        </div>

                        <p className="text-gray-300 mb-4">
                            Generate {genreInfo.name.toLowerCase()} content using these theory concepts in the Theory Lab.
                        </p>

                        <button className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white font-semibold transition-all">
                            Open Theory Lab
                        </button>
                    </div>
                </motion.div>
            </AnimatePresence>
        </div>
    );
}
