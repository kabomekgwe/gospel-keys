/**
 * Theory Lab Tool - Neo-Riemannian Transformations & Voice Leading Optimization
 * 
 * Exposes advanced music theory algorithms:
 * - P, L, R transformations
 * - Tonnetz path finding
 * - CSP-optimized voice leading
 */
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
    ArrowRight,
    Play,
    Loader2,
    Sparkles,
    GitBranch,
    Zap,
    Music,
    ChevronRight
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8009';

interface TransformResult {
    original_chord: string;
    transformation: string;
    new_chord: string;
    voicing: string[];
    metadata: {
        description: string;
        voice_moved: string;
        semitones_moved: number;
        is_parsimonious: boolean;
    };
}

interface TonnetzPathResult {
    chord1: string;
    chord2: string;
    path: string[] | null;
    distance: number;
    path_description: string;
}

interface VoiceLeadingResult {
    progression: string[];
    voicings: number[][];
    total_movement: number;
    method: string;
}

interface NeighborsResult {
    original: string;
    neighbors: Record<string, { chord: string; voicing: string[] }>;
}

interface Props {
    onPlayChord?: (midiNotes: number[]) => void;
}

export function TheoryLabTool({ onPlayChord }: Props) {
    const [activeTab, setActiveTab] = useState<'transform' | 'path' | 'optimize'>('transform');

    // Transform state
    const [chord, setChord] = useState('C');
    const [transformResult, setTransformResult] = useState<TransformResult | null>(null);
    const [neighbors, setNeighbors] = useState<NeighborsResult | null>(null);

    // Path state
    const [chord1, setChord1] = useState('C');
    const [chord2, setChord2] = useState('Am');
    const [pathResult, setPathResult] = useState<TonnetzPathResult | null>(null);

    // Optimize state
    const [progression, setProgression] = useState('Cmaj7 Fmaj7 G7 Cmaj7');
    const [optimizeResult, setOptimizeResult] = useState<VoiceLeadingResult | null>(null);

    // Mutations
    const transformMutation = useMutation({
        mutationFn: async (transformation: string) => {
            const res = await fetch(`${API_BASE}/api/v1/theory/transform`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chord, transformation })
            });
            if (!res.ok) throw new Error('Transform failed');
            return res.json() as Promise<TransformResult>;
        },
        onSuccess: (data) => {
            setTransformResult(data);
            // Update chord to result for chaining
            setChord(data.new_chord);
        }
    });

    const neighborsMutation = useMutation({
        mutationFn: async () => {
            const res = await fetch(`${API_BASE}/api/v1/theory/neighbors`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chord })
            });
            if (!res.ok) throw new Error('Neighbors failed');
            return res.json() as Promise<NeighborsResult>;
        },
        onSuccess: setNeighbors
    });

    const pathMutation = useMutation({
        mutationFn: async () => {
            const res = await fetch(`${API_BASE}/api/v1/theory/tonnetz-path`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chord1, chord2 })
            });
            if (!res.ok) throw new Error('Path failed');
            return res.json() as Promise<TonnetzPathResult>;
        },
        onSuccess: setPathResult
    });

    const optimizeMutation = useMutation({
        mutationFn: async () => {
            const chords = progression.split(/\s+/).filter(Boolean);
            const res = await fetch(`${API_BASE}/api/v1/theory/optimize-voice-leading`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    progression: chords,
                    constraints: {
                        avoid_parallel_fifths: true,
                        max_movement: 7
                    }
                })
            });
            if (!res.ok) throw new Error('Optimization failed');
            return res.json() as Promise<VoiceLeadingResult>;
        },
        onSuccess: setOptimizeResult
    });

    const handlePlayVoicing = (voicing: number[]) => {
        if (onPlayChord) {
            onPlayChord(voicing);
        }
    };

    const tabs = [
        { id: 'transform' as const, label: 'Neo-Riemannian', icon: <Sparkles className="w-4 h-4" /> },
        { id: 'path' as const, label: 'Tonnetz Path', icon: <GitBranch className="w-4 h-4" /> },
        { id: 'optimize' as const, label: 'Voice Leading', icon: <Zap className="w-4 h-4" /> },
    ];

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/30">
                    <Music className="w-6 h-6 text-violet-400" />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">Theory Lab</h2>
                    <p className="text-sm text-slate-400">Neo-Riemannian Transformations & CSP Optimization</p>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 p-1 bg-slate-800/50 rounded-lg border border-slate-700/50">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === tab.id
                                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                            }`}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Transform Tab */}
            {activeTab === 'transform' && (
                <div className="space-y-6">
                    {/* Input */}
                    <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                        <label className="block text-sm text-slate-400 mb-2">Chord</label>
                        <input
                            type="text"
                            value={chord}
                            onChange={(e) => setChord(e.target.value)}
                            className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white text-lg font-mono focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                            placeholder="e.g., Cmaj, Am, F#m"
                        />

                        {/* PLR Buttons */}
                        <div className="flex gap-3 mt-4">
                            {['P', 'L', 'R'].map((t) => (
                                <button
                                    key={t}
                                    onClick={() => transformMutation.mutate(t)}
                                    disabled={transformMutation.isPending}
                                    className="flex-1 py-4 rounded-lg font-bold text-2xl transition-all bg-gradient-to-br from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white shadow-lg shadow-violet-500/25 disabled:opacity-50"
                                >
                                    {transformMutation.isPending ? (
                                        <Loader2 className="w-6 h-6 animate-spin mx-auto" />
                                    ) : (
                                        t
                                    )}
                                </button>
                            ))}
                        </div>

                        <div className="mt-3 text-xs text-slate-500 grid grid-cols-3 gap-2 text-center">
                            <span>Parallel</span>
                            <span>Leading-tone</span>
                            <span>Relative</span>
                        </div>
                    </div>

                    {/* Transform Result */}
                    {transformResult && (
                        <div className="p-4 bg-slate-800/50 rounded-xl border border-violet-500/30">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <span className="text-2xl font-mono text-white">{transformResult.original_chord}</span>
                                    <div className="flex items-center gap-2 px-3 py-1 bg-violet-500/20 rounded-full">
                                        <span className="text-violet-300 font-bold">{transformResult.transformation}</span>
                                        <ChevronRight className="w-4 h-4 text-violet-400" />
                                    </div>
                                    <span className="text-2xl font-mono text-violet-300">{transformResult.new_chord}</span>
                                </div>
                                <button
                                    onClick={() => {
                                        // Convert note names to MIDI (simplified)
                                        const noteToMidi: Record<string, number> = {
                                            'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
                                            'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
                                            'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
                                        };
                                        const midiNotes = transformResult.voicing.map(note => {
                                            const match = note.match(/^([A-G][#b]?)(\d)?$/);
                                            if (match) {
                                                const base = noteToMidi[match[1]] || 60;
                                                const octave = match[2] ? parseInt(match[2]) : 4;
                                                return base + (octave - 4) * 12;
                                            }
                                            return 60;
                                        });
                                        handlePlayVoicing(midiNotes);
                                    }}
                                    className="p-2 rounded-lg bg-violet-500/20 hover:bg-violet-500/30 text-violet-300"
                                >
                                    <Play className="w-5 h-5" />
                                </button>
                            </div>
                            <p className="mt-2 text-sm text-slate-400">{transformResult.metadata.description}</p>
                            <div className="mt-2 flex gap-2">
                                <span className={`px-2 py-1 rounded text-xs ${transformResult.metadata.is_parsimonious ? 'bg-green-500/20 text-green-300' : 'bg-amber-500/20 text-amber-300'}`}>
                                    {transformResult.metadata.is_parsimonious ? 'Parsimonious' : 'Non-parsimonious'}
                                </span>
                                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">
                                    {transformResult.metadata.semitones_moved} semitones
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Get All Neighbors */}
                    <button
                        onClick={() => neighborsMutation.mutate()}
                        disabled={neighborsMutation.isPending}
                        className="w-full py-3 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-colors flex items-center justify-center gap-2"
                    >
                        {neighborsMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <GitBranch className="w-4 h-4" />}
                        Show All Tonnetz Neighbors
                    </button>

                    {neighbors && (
                        <div className="grid grid-cols-3 gap-4">
                            {Object.entries(neighbors.neighbors).map(([t, data]) => (
                                <div key={t} className="p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 text-center">
                                    <span className="text-sm text-slate-400">{t}</span>
                                    <p className="text-xl font-mono text-white mt-1">{data.chord}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Path Tab */}
            {activeTab === 'path' && (
                <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                            <label className="block text-sm text-slate-400 mb-2">From Chord</label>
                            <input
                                type="text"
                                value={chord1}
                                onChange={(e) => setChord1(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white font-mono focus:ring-2 focus:ring-cyan-500"
                                placeholder="e.g., C"
                            />
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                            <label className="block text-sm text-slate-400 mb-2">To Chord</label>
                            <input
                                type="text"
                                value={chord2}
                                onChange={(e) => setChord2(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white font-mono focus:ring-2 focus:ring-cyan-500"
                                placeholder="e.g., Am"
                            />
                        </div>
                    </div>

                    <button
                        onClick={() => pathMutation.mutate()}
                        disabled={pathMutation.isPending}
                        className="w-full py-4 rounded-lg bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white font-medium flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/25"
                    >
                        {pathMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <ArrowRight className="w-5 h-5" />}
                        Find Shortest Path
                    </button>

                    {pathResult && (
                        <div className="p-4 bg-slate-800/50 rounded-xl border border-cyan-500/30">
                            <div className="flex items-center gap-4 text-xl font-mono">
                                <span className="text-white">{pathResult.chord1}</span>
                                {pathResult.path?.map((t, i) => (
                                    <span key={i} className="flex items-center gap-2">
                                        <span className="px-2 py-1 rounded bg-cyan-500/20 text-cyan-300 text-sm">{t}</span>
                                        <ChevronRight className="w-4 h-4 text-slate-500" />
                                    </span>
                                ))}
                                <span className="text-cyan-300">{pathResult.chord2}</span>
                            </div>
                            <p className="mt-3 text-slate-400">{pathResult.path_description}</p>
                            <p className="mt-1 text-sm text-slate-500">Tonnetz Distance: {pathResult.distance}</p>
                        </div>
                    )}
                </div>
            )}

            {/* Optimize Tab */}
            {activeTab === 'optimize' && (
                <div className="space-y-6">
                    <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                        <label className="block text-sm text-slate-400 mb-2">Chord Progression</label>
                        <input
                            type="text"
                            value={progression}
                            onChange={(e) => setProgression(e.target.value)}
                            className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white font-mono focus:ring-2 focus:ring-amber-500"
                            placeholder="e.g., Cmaj7 Fmaj7 G7 Cmaj7"
                        />
                        <p className="mt-2 text-xs text-slate-500">Space-separated chord symbols</p>
                    </div>

                    <button
                        onClick={() => optimizeMutation.mutate()}
                        disabled={optimizeMutation.isPending}
                        className="w-full py-4 rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-medium flex items-center justify-center gap-2 shadow-lg shadow-amber-500/25"
                    >
                        {optimizeMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                        Optimize Voice Leading (CSP)
                    </button>

                    {optimizeResult && (
                        <div className="p-4 bg-slate-800/50 rounded-xl border border-amber-500/30 space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-400">Method: <span className="text-amber-300">{optimizeResult.method}</span></span>
                                <span className="text-sm text-slate-400">Total Movement: <span className="text-amber-300">{optimizeResult.total_movement.toFixed(1)} semitones</span></span>
                            </div>

                            <div className="space-y-2">
                                {optimizeResult.voicings.map((voicing, i) => (
                                    <div key={i} className="flex items-center gap-4 p-3 bg-slate-900/50 rounded-lg">
                                        <span className="text-slate-400 font-mono text-sm w-20">{optimizeResult.progression[i]}</span>
                                        <div className="flex gap-2">
                                            {voicing.map((note, j) => (
                                                <span key={j} className="px-2 py-1 bg-amber-500/20 rounded text-amber-300 font-mono text-sm">
                                                    {note}
                                                </span>
                                            ))}
                                        </div>
                                        <button
                                            onClick={() => handlePlayVoicing(voicing)}
                                            className="ml-auto p-1.5 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-300"
                                        >
                                            <Play className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
