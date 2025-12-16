/**
 * Tonnetz Lattice Component
 *
 * Interactive visualization of Neo-Riemannian transformations.
 * Shows PLR (Parallel, Leading-tone, Relative) relationships between chords.
 */

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Play, Volume2, Info, RotateCw, Zap } from 'lucide-react';

interface ChordNode {
    root: string;
    quality: string;
    x: number;
    y: number;
    id: string;
}

interface PLRTransformation {
    type: 'P' | 'L' | 'R';
    from: ChordNode;
    to: ChordNode;
}

export function TonnetzLattice() {
    const [selectedChord, setSelectedChord] = useState<ChordNode | null>(null);
    const [transformation, setTransformation] = useState<'P' | 'L' | 'R' | null>(null);
    const [aiExplanation, setAiExplanation] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPath, setShowPath] = useState(false);
    const [pathTarget, setPathTarget] = useState<ChordNode | null>(null);

    // Generate Tonnetz lattice nodes
    // Major triads arranged in one layer, minor triads in another
    // This creates the classic Tonnetz geometry
    const generateLatticeNodes = useCallback((): ChordNode[] => {
        const nodes: ChordNode[] = [];
        const roots = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F'];

        // Position major chords
        roots.forEach((root, i) => {
            nodes.push({
                root,
                quality: '',
                x: (i % 6) * 120 + 60,
                y: Math.floor(i / 6) * 100 + 50,
                id: `${root}-maj`
            });
        });

        // Position minor chords (offset for visual clarity)
        roots.forEach((root, i) => {
            nodes.push({
                root,
                quality: 'm',
                x: (i % 6) * 120 + 120,
                y: Math.floor(i / 6) * 100 + 100,
                id: `${root}-min`
            });
        });

        return nodes;
    }, []);

    const nodes = generateLatticeNodes();

    // Apply PLR transformation
    const handleTransformation = async (type: 'P' | 'L' | 'R') => {
        if (!selectedChord) return;

        setIsLoading(true);
        setTransformation(type);

        try {
            const response = await fetch('/api/v1/theory-tools/neo-riemannian/transform', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chord_root: selectedChord.root,
                    chord_quality: selectedChord.quality,
                    transformation: type,
                    student_level: 'intermediate'
                })
            });

            const data = await response.json();

            if (data.ai_explanation) {
                setAiExplanation(data.ai_explanation);
            }

            // Find and select the target chord
            const targetNode = nodes.find(
                n => n.root === data.new_root && n.quality === data.new_quality
            );
            if (targetNode) {
                setSelectedChord(targetNode);
            }

        } catch (error) {
            console.error('PLR transformation failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Find shortest path between two chords
    const findPath = async () => {
        if (!selectedChord || !pathTarget) return;

        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/theory-tools/neo-riemannian/path', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_chord: {
                        root: selectedChord.root,
                        quality: selectedChord.quality
                    },
                    end_chord: {
                        root: pathTarget.root,
                        quality: pathTarget.quality
                    },
                    max_steps: 6,
                    student_level: 'intermediate'
                })
            });

            const data = await response.json();

            if (data.ai_explanation) {
                setAiExplanation(data.ai_explanation);
            }

        } catch (error) {
            console.error('Path finding failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Get Tonnetz neighbors (P, L, R)
    const getNeighbors = async (node: ChordNode) => {
        try {
            const response = await fetch('/api/v1/theory-tools/tonnetz/neighbors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chord_root: node.root,
                    chord_quality: node.quality
                })
            });

            return await response.json();
        } catch (error) {
            console.error('Failed to get neighbors:', error);
            return null;
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Lattice Visualization */}
            <div className="lg:col-span-2 bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold text-white">Tonnetz Lattice</h3>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowPath(!showPath)}
                            className={`
                                px-4 py-2 rounded-lg font-medium transition-all
                                ${showPath
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                }
                            `}
                        >
                            {showPath ? 'Finding Path...' : 'Find Path'}
                        </button>

                        <button
                            onClick={() => {
                                setSelectedChord(null);
                                setPathTarget(null);
                                setAiExplanation('');
                                setShowPath(false);
                            }}
                            className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
                        >
                            <RotateCw className="w-5 h-5 text-gray-300" />
                        </button>
                    </div>
                </div>

                {/* SVG Lattice */}
                <div className="bg-gray-900/50 rounded-lg border border-gray-700 overflow-auto" style={{ height: '500px' }}>
                    <svg width="800" height="600" className="w-full h-full">
                        {/* Draw connections (PLR edges) */}
                        {selectedChord && nodes.map((node) => {
                            // Draw P, L, R connections for selected chord
                            return null; // Simplified for now
                        })}

                        {/* Draw chord nodes */}
                        {nodes.map((node) => {
                            const isSelected = selectedChord?.id === node.id;
                            const isPathTarget = pathTarget?.id === node.id;
                            const isMajor = node.quality === '';

                            return (
                                <motion.g
                                    key={node.id}
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 0.01 * nodes.indexOf(node) }}
                                >
                                    <circle
                                        cx={node.x}
                                        cy={node.y}
                                        r={isSelected || isPathTarget ? 32 : 24}
                                        fill={
                                            isSelected ? '#3b82f6' :
                                            isPathTarget ? '#10b981' :
                                            isMajor ? '#6366f1' : '#8b5cf6'
                                        }
                                        stroke={isSelected || isPathTarget ? '#fff' : 'none'}
                                        strokeWidth={2}
                                        className="cursor-pointer hover:opacity-80 transition-opacity"
                                        onClick={() => {
                                            if (showPath) {
                                                if (!selectedChord) {
                                                    setSelectedChord(node);
                                                } else if (!pathTarget) {
                                                    setPathTarget(node);
                                                    findPath();
                                                }
                                            } else {
                                                setSelectedChord(node);
                                                setPathTarget(null);
                                            }
                                        }}
                                    />
                                    <text
                                        x={node.x}
                                        y={node.y + 5}
                                        textAnchor="middle"
                                        className="fill-white text-sm font-semibold pointer-events-none"
                                    >
                                        {node.root}{node.quality}
                                    </text>
                                </motion.g>
                            );
                        })}
                    </svg>
                </div>

                {/* Legend */}
                <div className="flex items-center gap-6 mt-4 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-indigo-500" />
                        <span>Major Triads</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-purple-500" />
                        <span>Minor Triads</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-blue-500 border-2 border-white" />
                        <span>Selected</span>
                    </div>
                </div>
            </div>

            {/* Control Panel */}
            <div className="space-y-6">
                {/* Selected Chord Info */}
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <h4 className="text-white font-semibold mb-4">Selected Chord</h4>

                    {selectedChord ? (
                        <div className="space-y-4">
                            <div className="text-center">
                                <div className="text-4xl font-bold text-white mb-2">
                                    {selectedChord.root}{selectedChord.quality || 'maj'}
                                </div>
                                <div className="text-sm text-gray-400">
                                    {selectedChord.quality === '' ? 'Major Triad' : 'Minor Triad'}
                                </div>
                            </div>

                            <button className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-500 rounded-lg text-white font-medium transition-colors">
                                <Play className="w-5 h-5" />
                                Play Chord
                            </button>
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <Info className="w-12 h-12 mx-auto mb-2 opacity-50" />
                            <p>Select a chord to begin</p>
                        </div>
                    )}
                </div>

                {/* PLR Transformations */}
                {selectedChord && !showPath && (
                    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                        <h4 className="text-white font-semibold mb-4">Apply Transformation</h4>

                        <div className="space-y-3">
                            <button
                                onClick={() => handleTransformation('P')}
                                disabled={isLoading}
                                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <div className="flex items-center justify-between">
                                    <span>P (Parallel)</span>
                                    <Zap className="w-5 h-5" />
                                </div>
                                <div className="text-xs text-blue-200 mt-1">Major ↔ Minor</div>
                            </button>

                            <button
                                onClick={() => handleTransformation('L')}
                                disabled={isLoading}
                                className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <div className="flex items-center justify-between">
                                    <span>L (Leading-tone)</span>
                                    <Zap className="w-5 h-5" />
                                </div>
                                <div className="text-xs text-purple-200 mt-1">Root moves</div>
                            </button>

                            <button
                                onClick={() => handleTransformation('R')}
                                disabled={isLoading}
                                className="w-full px-4 py-3 bg-green-600 hover:bg-green-500 rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <div className="flex items-center justify-between">
                                    <span>R (Relative)</span>
                                    <Zap className="w-5 h-5" />
                                </div>
                                <div className="text-xs text-green-200 mt-1">Relative maj/min</div>
                            </button>
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
            </div>
        </div>
    );
}
