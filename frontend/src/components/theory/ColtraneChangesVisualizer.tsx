/**
 * Coltrane Changes Visualizer
 *
 * Visualize Giant Steps harmonic movement through three tonal centers.
 * Shows major third cycles and dominant preparation.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, TrendingUp, Volume2, Sparkles } from 'lucide-react';

const NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];

export function ColtraneChangesVisualizer() {
    const [targetKey, setTargetKey] = useState('C');
    const [progression, setProgression] = useState<any[]>([]);
    const [aiExplanation, setAiExplanation] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [currentChordIndex, setCurrentChordIndex] = useState(-1);

    // Generate Coltrane Changes
    const generateColtraneChanges = async () => {
        setIsLoading(true);
        setCurrentChordIndex(-1);

        try {
            const response = await fetch('/api/v1/theory-tools/coltrane/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_key: targetKey,
                    student_level: 'advanced'
                })
            });

            const data = await response.json();

            if (data.progression) {
                setProgression(data.progression);
            }

            if (data.ai_explanation) {
                setAiExplanation(data.ai_explanation);
            }

        } catch (error) {
            console.error('Coltrane Changes generation failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Play progression
    const playProgression = () => {
        setCurrentChordIndex(0);
        const interval = setInterval(() => {
            setCurrentChordIndex(prev => {
                if (prev >= progression.length - 1) {
                    clearInterval(interval);
                    return -1;
                }
                return prev + 1;
            });
        }, 1000);
    };

    return (
        <div className="space-y-6">
            {/* Target Key Selection */}
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                <h3 className="text-white font-semibold mb-4">Target Key</h3>

                <div className="flex items-center gap-4">
                    <div className="flex-1">
                        <select
                            value={targetKey}
                            onChange={(e) => setTargetKey(e.target.value)}
                            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white text-lg font-medium"
                        >
                            {NOTE_NAMES.map(note => (
                                <option key={note} value={note}>{note} Major</option>
                            ))}
                        </select>
                    </div>

                    <button
                        onClick={generateColtraneChanges}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 rounded-lg text-white font-semibold transition-all disabled:opacity-50"
                    >
                        <TrendingUp className="w-5 h-5" />
                        {isLoading ? 'Generating...' : 'Generate'}
                    </button>
                </div>
            </div>

            {/* Circular Visualization */}
            {progression.length > 0 && (
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-semibold text-white">Harmonic Cycle</h3>

                        <button
                            onClick={playProgression}
                            disabled={currentChordIndex >= 0}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-white font-medium transition-colors disabled:opacity-50"
                        >
                            <Play className="w-4 h-4" />
                            Play Progression
                        </button>
                    </div>

                    {/* SVG Circle */}
                    <div className="flex justify-center">
                        <svg width="400" height="400" viewBox="0 0 400 400" className="max-w-full">
                            {/* Center circle */}
                            <circle
                                cx="200"
                                cy="200"
                                r="180"
                                fill="none"
                                stroke="#374151"
                                strokeWidth="2"
                                strokeDasharray="5,5"
                            />

                            {/* Chord positions */}
                            {progression.map((chord, index) => {
                                const angle = (index / progression.length) * 2 * Math.PI - Math.PI / 2;
                                const x = 200 + Math.cos(angle) * 150;
                                const y = 200 + Math.sin(angle) * 150;
                                const isActive = currentChordIndex === index;
                                const isPassed = currentChordIndex > index;

                                // Determine if it's a major center or dominant
                                const isMajorCenter = chord.symbol.includes('maj7');

                                return (
                                    <g key={index}>
                                        {/* Connection line to next chord */}
                                        {index < progression.length - 1 && (
                                            <line
                                                x1={x}
                                                y1={y}
                                                x2={200 + Math.cos((index + 1) / progression.length * 2 * Math.PI - Math.PI / 2) * 150}
                                                y2={200 + Math.sin((index + 1) / progression.length * 2 * Math.PI - Math.PI / 2) * 150}
                                                stroke={isPassed ? '#10b981' : '#4b5563'}
                                                strokeWidth={isPassed ? 3 : 2}
                                                opacity={isPassed ? 1 : 0.3}
                                            />
                                        )}

                                        {/* Chord circle */}
                                        <motion.circle
                                            cx={x}
                                            cy={y}
                                            r={isActive ? 35 : isMajorCenter ? 30 : 25}
                                            fill={isActive ? '#f59e0b' : isMajorCenter ? '#3b82f6' : '#8b5cf6'}
                                            stroke={isActive ? '#fff' : 'none'}
                                            strokeWidth={3}
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            transition={{ delay: index * 0.1 }}
                                        />

                                        {/* Chord label */}
                                        <text
                                            x={x}
                                            y={y + 5}
                                            textAnchor="middle"
                                            className={`${isActive ? 'text-lg font-bold' : 'text-sm'} fill-white pointer-events-none`}
                                        >
                                            {chord.symbol.replace('maj7', '').replace('7', '')}
                                        </text>

                                        {/* Chord quality below */}
                                        <text
                                            x={x}
                                            y={y + 50}
                                            textAnchor="middle"
                                            className="text-xs fill-gray-400 pointer-events-none"
                                        >
                                            {chord.symbol}
                                        </text>
                                    </g>
                                );
                            })}

                            {/* Center label */}
                            <text
                                x="200"
                                y="200"
                                textAnchor="middle"
                                className="text-sm fill-gray-500"
                            >
                                Giant Steps
                            </text>
                            <text
                                x="200"
                                y="220"
                                textAnchor="middle"
                                className="text-xs fill-gray-600"
                            >
                                Major 3rd Cycles
                            </text>
                        </svg>
                    </div>

                    {/* Legend */}
                    <div className="flex items-center justify-center gap-6 mt-6 text-sm">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-blue-500" />
                            <span className="text-gray-400">Tonal Center (Maj7)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-purple-500" />
                            <span className="text-gray-400">Dominant (7)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-orange-500 border-2 border-white" />
                            <span className="text-gray-400">Currently Playing</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Progression List */}
            {progression.length > 0 && (
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <h3 className="text-white font-semibold mb-4">Chord Progression</h3>

                    <div className="space-y-2">
                        {progression.map((chord, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className={`
                                    flex items-center justify-between p-4 rounded-lg transition-all
                                    ${currentChordIndex === index
                                        ? 'bg-orange-500/20 border-2 border-orange-500'
                                        : 'bg-gray-900/50 border border-gray-700'
                                    }
                                `}
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-8 h-8 flex items-center justify-center bg-gray-700 rounded-full text-gray-300 text-sm">
                                        {index + 1}
                                    </div>
                                    <div className="text-2xl font-bold text-white font-mono">
                                        {chord.symbol}
                                    </div>
                                    <div className="text-sm text-gray-400">
                                        {chord.voicing?.slice(0, 4).join(' - ') || ''}
                                    </div>
                                </div>

                                <button className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-white text-sm font-medium transition-colors">
                                    <Play className="w-4 h-4" />
                                    Play
                                </button>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

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

            {/* Empty State */}
            {progression.length === 0 && !isLoading && (
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-12 text-center">
                    <Sparkles className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                    <h3 className="text-xl font-semibold text-white mb-2">
                        Explore Coltrane Changes
                    </h3>
                    <p className="text-gray-400 mb-4">
                        Select a target key and generate the Giant Steps harmonic pattern
                    </p>
                    <div className="text-sm text-gray-500">
                        Named after John Coltrane's revolutionary composition "Giant Steps"
                    </div>
                </div>
            )}

            {/* Info */}
            <div className="bg-gradient-to-br from-orange-900/20 to-red-900/20 rounded-xl border border-orange-500/30 p-6">
                <div className="flex items-start gap-3">
                    <TrendingUp className="w-5 h-5 text-orange-400 flex-shrink-0 mt-1" />
                    <div>
                        <h4 className="text-white font-semibold mb-2">About Coltrane Changes</h4>
                        <p className="text-gray-300 text-sm leading-relaxed">
                            The "Coltrane Changes" create rapid harmonic movement through three tonal centers separated by major thirds.
                            Each tonal center is approached by its dominant chord, creating a sophisticated harmonic cycle.
                            This pattern revolutionized jazz harmony when John Coltrane introduced it in "Giant Steps" (1960).
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
