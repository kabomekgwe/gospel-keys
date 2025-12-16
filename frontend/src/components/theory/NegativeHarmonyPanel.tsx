/**
 * Negative Harmony Panel
 *
 * Side-by-side comparison of original vs negative harmony progressions.
 * Shows axis of reflection and voice movements.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Sparkles, ArrowRight, Volume2, Plus, X } from 'lucide-react';

interface ChordInput {
    root: string;
    quality: string;
}

const NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
const CHORD_QUALITIES = [
    { value: '', label: 'Major' },
    { value: 'm', label: 'Minor' },
    { value: '7', label: 'Dom7' },
    { value: 'maj7', label: 'Maj7' },
    { value: 'm7', label: 'Min7' },
];

export function NegativeHarmonyPanel() {
    const [keyRoot, setKeyRoot] = useState('C');
    const [keyQuality, setKeyQuality] = useState<'major' | 'minor'>('major');
    const [originalProgression, setOriginalProgression] = useState<ChordInput[]>([
        { root: 'C', quality: 'maj7' },
        { root: 'A', quality: 'm7' },
        { root: 'D', quality: 'm7' },
        { root: 'G', quality: '7' },
    ]);
    const [negativeProgression, setNegativeProgression] = useState<any[]>([]);
    const [aiExplanation, setAiExplanation] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Generate negative harmony
    const generateNegativeHarmony = async () => {
        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/theory-tools/negative-harmony/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    progression: originalProgression.map(c => [c.root, c.quality]),
                    key_root: keyRoot,
                    key_quality: keyQuality,
                    student_level: 'intermediate'
                })
            });

            const data = await response.json();

            if (data.negative_progression) {
                setNegativeProgression(data.negative_progression);
            }

            if (data.ai_explanation) {
                setAiExplanation(data.ai_explanation);
            }

        } catch (error) {
            console.error('Negative harmony generation failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Add chord to progression
    const addChord = () => {
        setOriginalProgression([...originalProgression, { root: 'C', quality: '' }]);
    };

    // Remove chord from progression
    const removeChord = (index: number) => {
        setOriginalProgression(originalProgression.filter((_, i) => i !== index));
    };

    // Update chord
    const updateChord = (index: number, field: 'root' | 'quality', value: string) => {
        const updated = [...originalProgression];
        updated[index] = { ...updated[index], [field]: value };
        setOriginalProgression(updated);
    };

    return (
        <div className="space-y-6">
            {/* Key Selection */}
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                <h3 className="text-white font-semibold mb-4">Key Center</h3>

                <div className="flex items-center gap-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-2">Root</label>
                        <select
                            value={keyRoot}
                            onChange={(e) => setKeyRoot(e.target.value)}
                            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                        >
                            {NOTE_NAMES.map(note => (
                                <option key={note} value={note}>{note}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-gray-400 mb-2">Quality</label>
                        <select
                            value={keyQuality}
                            onChange={(e) => setKeyQuality(e.target.value as 'major' | 'minor')}
                            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                        >
                            <option value="major">Major</option>
                            <option value="minor">Minor</option>
                        </select>
                    </div>

                    <div className="ml-auto">
                        <div className="text-sm text-gray-400 mb-2">Axis of Reflection</div>
                        <div className="px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-lg text-purple-400 font-mono">
                            Between I and IV
                        </div>
                    </div>
                </div>
            </div>

            {/* Side-by-Side Progressions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Original Progression */}
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-white font-semibold">Original Progression</h3>
                        <button
                            onClick={addChord}
                            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-sm transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            Add Chord
                        </button>
                    </div>

                    <div className="space-y-3">
                        {originalProgression.map((chord, index) => (
                            <div key={index} className="flex items-center gap-3">
                                <div className="flex-1 grid grid-cols-2 gap-2">
                                    <select
                                        value={chord.root}
                                        onChange={(e) => updateChord(index, 'root', e.target.value)}
                                        className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                    >
                                        {NOTE_NAMES.map(note => (
                                            <option key={note} value={note}>{note}</option>
                                        ))}
                                    </select>

                                    <select
                                        value={chord.quality}
                                        onChange={(e) => updateChord(index, 'quality', e.target.value)}
                                        className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                    >
                                        {CHORD_QUALITIES.map(q => (
                                            <option key={q.value} value={q.value}>{q.label}</option>
                                        ))}
                                    </select>
                                </div>

                                {originalProgression.length > 1 && (
                                    <button
                                        onClick={() => removeChord(index)}
                                        className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                                    >
                                        <X className="w-4 h-4 text-gray-400" />
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>

                    <button
                        className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-white font-medium transition-colors"
                    >
                        <Play className="w-4 h-4" />
                        Play Original
                    </button>
                </div>

                {/* Negative Harmony Progression */}
                <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 rounded-xl border border-purple-500/30 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-purple-400" />
                            <h3 className="text-white font-semibold">Negative Harmony</h3>
                        </div>
                    </div>

                    {negativeProgression.length > 0 ? (
                        <>
                            <div className="space-y-3">
                                {negativeProgression.map((chord, index) => (
                                    <div key={index} className="px-4 py-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                                        <div className="flex items-center justify-between">
                                            <span className="text-white font-mono text-lg">
                                                {chord.symbol}
                                            </span>
                                            <ArrowRight className="w-4 h-4 text-purple-400" />
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <button
                                className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg text-white font-medium transition-colors"
                            >
                                <Play className="w-4 h-4" />
                                Play Negative
                            </button>

                            <button
                                className="w-full mt-2 px-4 py-2 bg-pink-600 hover:bg-pink-500 rounded-lg text-white text-sm font-medium transition-colors"
                            >
                                Play Both (Alternating)
                            </button>
                        </>
                    ) : (
                        <div className="py-12 text-center text-gray-500">
                            <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
                            <p>Generate negative harmony to see result</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Generate Button */}
            <button
                onClick={generateNegativeHarmony}
                disabled={isLoading || originalProgression.length === 0}
                className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-xl text-white text-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Sparkles className="w-6 h-6" />
                {isLoading ? 'Generating...' : 'Generate Negative Harmony'}
            </button>

            {/* AI Explanation */}
            {aiExplanation && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-xl border border-blue-500/30 p-6"
                >
                    <div className="flex items-start gap-3">
                        <Volume2 className="w-5 h-5 text-blue-400 flex-shrink-0 mt-1" />
                        <div>
                            <h4 className="text-white font-semibold mb-2">AI Explanation</h4>
                            <p className="text-gray-300 text-sm leading-relaxed">
                                {aiExplanation}
                            </p>
                        </div>
                    </div>
                </motion.div>
            )}

            {/* Visual Axis Representation */}
            {negativeProgression.length > 0 && (
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <h4 className="text-white font-semibold mb-4">Axis of Reflection</h4>

                    <div className="relative py-8">
                        {/* Central axis */}
                        <div className="absolute top-1/2 left-0 right-0 h-px bg-purple-500/50 transform -translate-y-1/2" />

                        <div className="flex items-center justify-between">
                            {/* Original side */}
                            <div className="text-center">
                                <div className="text-sm text-gray-400 mb-2">Original</div>
                                <div className="space-y-1">
                                    {originalProgression.map((chord, i) => (
                                        <div key={i} className="px-3 py-1 bg-blue-500/20 rounded text-blue-400 text-sm">
                                            {chord.root}{chord.quality}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Axis label */}
                            <div className="px-4 py-2 bg-purple-500/20 border border-purple-500/30 rounded-lg">
                                <div className="text-purple-400 text-sm font-semibold">Reflection Axis</div>
                                <div className="text-purple-300 text-xs">Between I & IV</div>
                            </div>

                            {/* Negative side */}
                            <div className="text-center">
                                <div className="text-sm text-gray-400 mb-2">Negative</div>
                                <div className="space-y-1">
                                    {negativeProgression.map((chord, i) => (
                                        <div key={i} className="px-3 py-1 bg-purple-500/20 rounded text-purple-400 text-sm">
                                            {chord.symbol}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
