/**
 * Substitution Explorer Component
 *
 * Explore all possible chord substitution options:
 * - Modal Interchange (borrowed chords)
 * - Negative Harmony
 * - Tritone Substitution
 * - Common Tone Diminished
 * - Functional Substitutes
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Shuffle, ChevronDown, ChevronUp, Volume2, Sparkles } from 'lucide-react';

interface Substitution {
    symbol: string;
    voicing: string[];
    category: string;
}

const NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
const CHORD_QUALITIES = [
    { value: '', label: 'Major' },
    { value: 'm', label: 'Minor' },
    { value: '7', label: 'Dom7' },
    { value: 'maj7', label: 'Maj7' },
    { value: 'm7', label: 'Min7' },
    { value: 'dim7', label: 'Dim7' },
];

const SUBSTITUTION_CATEGORIES = [
    {
        id: 'tritone',
        name: 'Tritone Substitution',
        description: 'Replace dominant chord with dominant 3 tritones away',
        color: 'from-blue-500 to-cyan-500',
        icon: '↔️'
    },
    {
        id: 'negative',
        name: 'Negative Harmony',
        description: 'Mirror-image harmonic relationship',
        color: 'from-purple-500 to-pink-500',
        icon: '✨'
    },
    {
        id: 'common_tone_dim',
        name: 'Common Tone Diminished',
        description: 'Diminished 7th sharing common tones',
        color: 'from-orange-500 to-red-500',
        icon: '🎯'
    },
];

export function SubstitutionExplorer() {
    const [chordRoot, setChordRoot] = useState('C');
    const [chordQuality, setChordQuality] = useState('7');
    const [keyRoot, setKeyRoot] = useState('C');
    const [keyQuality, setKeyQuality] = useState<'major' | 'minor'>('major');
    const [substitutions, setSubstitutions] = useState<Record<string, Substitution[]>>({});
    const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
    const [isLoading, setIsLoading] = useState(false);

    // Analyze substitutions
    const analyzeSubstitutions = async () => {
        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/theory-tools/substitutions/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chord_root: chordRoot,
                    quality: chordQuality,
                    key_root: keyRoot,
                    key_quality: keyQuality,
                    complexity_level: 'moderate'
                })
            });

            const data = await response.json();

            if (data.substitutions) {
                setSubstitutions(data.substitutions);
                // Auto-expand all categories
                setExpandedCategories(new Set(Object.keys(data.substitutions)));
            }

        } catch (error) {
            console.error('Substitution analysis failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Toggle category expansion
    const toggleCategory = (categoryId: string) => {
        const newExpanded = new Set(expandedCategories);
        if (newExpanded.has(categoryId)) {
            newExpanded.delete(categoryId);
        } else {
            newExpanded.add(categoryId);
        }
        setExpandedCategories(newExpanded);
    };

    return (
        <div className="space-y-6">
            {/* Input Section */}
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                <h3 className="text-white font-semibold mb-4">Chord & Key Selection</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Chord to Analyze */}
                    <div>
                        <label className="block text-sm text-gray-400 mb-3">Chord to Analyze</label>
                        <div className="flex gap-3">
                            <select
                                value={chordRoot}
                                onChange={(e) => setChordRoot(e.target.value)}
                                className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white font-medium"
                            >
                                {NOTE_NAMES.map(note => (
                                    <option key={note} value={note}>{note}</option>
                                ))}
                            </select>

                            <select
                                value={chordQuality}
                                onChange={(e) => setChordQuality(e.target.value)}
                                className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white font-medium"
                            >
                                {CHORD_QUALITIES.map(q => (
                                    <option key={q.value} value={q.value}>{q.label}</option>
                                ))}
                            </select>
                        </div>

                        {/* Display selected chord */}
                        <div className="mt-3 text-center">
                            <div className="inline-block px-6 py-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                                <span className="text-3xl font-bold text-blue-400">
                                    {chordRoot}{chordQuality}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Key Context */}
                    <div>
                        <label className="block text-sm text-gray-400 mb-3">Key Context</label>
                        <div className="flex gap-3">
                            <select
                                value={keyRoot}
                                onChange={(e) => setKeyRoot(e.target.value)}
                                className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white font-medium"
                            >
                                {NOTE_NAMES.map(note => (
                                    <option key={note} value={note}>{note}</option>
                                ))}
                            </select>

                            <select
                                value={keyQuality}
                                onChange={(e) => setKeyQuality(e.target.value as 'major' | 'minor')}
                                className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white font-medium"
                            >
                                <option value="major">Major</option>
                                <option value="minor">Minor</option>
                            </select>
                        </div>

                        <div className="mt-3 text-center text-sm text-gray-400">
                            Key: {keyRoot} {keyQuality}
                        </div>
                    </div>
                </div>

                {/* Analyze Button */}
                <button
                    onClick={analyzeSubstitutions}
                    disabled={isLoading}
                    className="w-full mt-6 flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 rounded-xl text-white text-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Shuffle className="w-6 h-6" />
                    {isLoading ? 'Analyzing...' : 'Find All Substitutions'}
                </button>
            </div>

            {/* Results */}
            {Object.keys(substitutions).length > 0 && (
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xl font-semibold text-white">
                            Substitution Options for {chordRoot}{chordQuality}
                        </h3>
                        <div className="px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-lg">
                            <span className="text-sm text-green-400">
                                {Object.values(substitutions).flat().length} options found
                            </span>
                        </div>
                    </div>

                    {/* Substitution Categories */}
                    <div className="space-y-3">
                        {Object.entries(substitutions).map(([category, subs]) => {
                            const isExpanded = expandedCategories.has(category);
                            const categoryInfo = SUBSTITUTION_CATEGORIES.find(c => c.id === category);

                            return (
                                <motion.div
                                    key={category}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
                                >
                                    {/* Category Header */}
                                    <button
                                        onClick={() => toggleCategory(category)}
                                        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">{categoryInfo?.icon || '🎵'}</span>
                                            <div className="text-left">
                                                <div className="text-white font-semibold">
                                                    {categoryInfo?.name || category}
                                                </div>
                                                {categoryInfo?.description && (
                                                    <div className="text-sm text-gray-400">
                                                        {categoryInfo.description}
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-3">
                                            <div className="px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full text-sm text-blue-400">
                                                {subs.length} {subs.length === 1 ? 'option' : 'options'}
                                            </div>
                                            {isExpanded ? (
                                                <ChevronUp className="w-5 h-5 text-gray-400" />
                                            ) : (
                                                <ChevronDown className="w-5 h-5 text-gray-400" />
                                            )}
                                        </div>
                                    </button>

                                    {/* Category Content */}
                                    <AnimatePresence>
                                        {isExpanded && (
                                            <motion.div
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: 'auto', opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                                transition={{ duration: 0.2 }}
                                                className="border-t border-gray-700"
                                            >
                                                <div className="p-6 space-y-3">
                                                    {subs.map((sub, index) => (
                                                        <div
                                                            key={index}
                                                            className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg hover:bg-gray-900/70 transition-colors"
                                                        >
                                                            <div className="flex items-center gap-4">
                                                                <div className="text-2xl font-bold text-white font-mono">
                                                                    {sub.symbol}
                                                                </div>
                                                                <div className="text-sm text-gray-400">
                                                                    {sub.voicing?.join(' - ') || 'Voicing available'}
                                                                </div>
                                                            </div>

                                                            <button className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-white text-sm font-medium transition-colors">
                                                                <Play className="w-4 h-4" />
                                                                Play
                                                            </button>
                                                        </div>
                                                    ))}
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </motion.div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Empty State */}
            {Object.keys(substitutions).length === 0 && !isLoading && (
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-12 text-center">
                    <Sparkles className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                    <h3 className="text-xl font-semibold text-white mb-2">
                        Discover Chord Substitutions
                    </h3>
                    <p className="text-gray-400 mb-6">
                        Select a chord and key, then click "Find All Substitutions" to explore your options
                    </p>
                    <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full" />
                            <span>Tritone Subs</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-purple-500 rounded-full" />
                            <span>Negative Harmony</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-orange-500 rounded-full" />
                            <span>Diminished</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Info Box */}
            <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-xl border border-blue-500/30 p-6">
                <div className="flex items-start gap-3">
                    <Volume2 className="w-5 h-5 text-blue-400 flex-shrink-0 mt-1" />
                    <div>
                        <h4 className="text-white font-semibold mb-2">About Chord Substitutions</h4>
                        <p className="text-gray-300 text-sm leading-relaxed">
                            Chord substitutions allow you to reharmonize progressions while maintaining harmonic function.
                            The options shown here preserve the voice leading and harmonic direction of the original chord,
                            but offer fresh colors and unexpected harmonic paths. Click any option to hear how it sounds!
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
