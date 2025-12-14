/**
 * Hands Practice Page
 * 
 * Practice page for two-hand piano with pattern selection and playback.
 * Features:
 * - Chord progression input
 * - Left/right hand pattern selection  
 * - MIDI generation and playback
 * - Tempo control
 */
import { useState, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Link } from '@tanstack/react-router';
import { createFileRoute } from '@tanstack/react-router';

import { HandsSelector, HandMode, Style } from '../../components/practice/HandsSelector';
import { VoicingKeyboard } from '../../components/VoicingKeyboard';

// API types
interface PatternsResponse {
    style: string;
    left_hand_patterns: string[];
    right_hand_patterns: string[];
}

interface HandsPracticeResponse {
    midi_url: string;
    left_notes_count: number;
    right_notes_count: number;
    total_bars: number;
    duration_seconds: number;
    patterns_used: {
        left: string;
        right: string;
    };
}

interface HandsPracticeRequest {
    chords: string[];
    key: string;
    tempo: number;
    left_pattern: string;
    right_pattern: string;
    style: string;
    active_hand: string;
    bars_per_chord: number;
}

// Default chord progressions
const PRESET_PROGRESSIONS = [
    { name: 'ii-V-I', chords: ['Dm9', 'G13', 'Cmaj9', 'Am7'] },
    { name: 'Neo-Soul Vamp', chords: ['Dm11', 'Gmaj7', 'Cmaj9', 'Fmaj7'] },
    { name: 'Gospel Turnaround', chords: ['Cmaj7', 'Am7', 'Dm7', 'G7'] },
    { name: 'Jazz Blues', chords: ['C7', 'F7', 'C7', 'G7'] },
    { name: 'Coltrane Changes', chords: ['Cmaj7', 'Ebmaj7', 'Gbmaj7', 'Amaj7'] },
];

export const Route = createFileRoute('/practice/hands')({
    component: HandsPracticePage,
});

function HandsPracticePage() {
    // State
    const [mode, setMode] = useState<HandMode>('both');
    const [style, setStyle] = useState<Style>('neosoul');
    const [leftPattern, setLeftPattern] = useState('syncopated_groove');
    const [rightPattern, setRightPattern] = useState('extended_chord_voicing');
    const [chords, setChords] = useState<string[]>(['Dm9', 'G13', 'Cmaj9', 'Am7']);
    const [chordInput, setChordInput] = useState('Dm9, G13, Cmaj9, Am7');
    const [tempo, setTempo] = useState(72);
    const [barsPerChord, setBarsPerChord] = useState(2);

    // Fetch available patterns
    const { data: patterns, isLoading: patternsLoading } = useQuery<PatternsResponse>({
        queryKey: ['patterns', style],
        queryFn: async () => {
            const res = await fetch(`/api/v1/practice/patterns/${style}`);
            if (!res.ok) throw new Error('Failed to fetch patterns');
            return res.json();
        },
    });

    // Generate hands practice
    const generateMutation = useMutation<HandsPracticeResponse, Error, HandsPracticeRequest>({
        mutationFn: async (request) => {
            const res = await fetch('/api/v1/practice/hands', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request),
            });
            if (!res.ok) throw new Error('Failed to generate practice');
            return res.json();
        },
    });

    // Handle chord input
    const handleChordsChange = useCallback((input: string) => {
        setChordInput(input);
        const parsed = input
            .split(/[,\s]+/)
            .map(c => c.trim())
            .filter(c => c.length > 0);
        if (parsed.length > 0) {
            setChords(parsed);
        }
    }, []);

    // Handle generation
    const handleGenerate = useCallback(() => {
        generateMutation.mutate({
            chords,
            key: 'C',
            tempo,
            left_pattern: leftPattern,
            right_pattern: rightPattern,
            style,
            active_hand: mode,
            bars_per_chord: barsPerChord,
        });
    }, [chords, tempo, leftPattern, rightPattern, style, mode, barsPerChord, generateMutation]);

    // Handle pattern change
    const handlePatternChange = useCallback((hand: 'left' | 'right', pattern: string) => {
        if (hand === 'left') {
            setLeftPattern(pattern);
        } else {
            setRightPattern(pattern);
        }
    }, []);

    // Apply preset progression
    const applyPreset = useCallback((preset: typeof PRESET_PROGRESSIONS[0]) => {
        setChords(preset.chords);
        setChordInput(preset.chords.join(', '));
    }, []);

    const leftPatterns = patterns?.left_hand_patterns || ['syncopated_groove'];
    const rightPatterns = patterns?.right_hand_patterns || ['extended_chord_voicing'];

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100">
            {/* Header */}
            <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
                <div className="max-w-6xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link
                                to="/practice"
                                className="text-slate-400 hover:text-slate-200 transition-colors"
                            >
                                ← Back
                            </Link>
                            <h1 className="text-xl font-bold">🎹 Two-Hand Practice</h1>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Settings Panel */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Hand Selector */}
                        <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700/50">
                            <h2 className="text-lg font-semibold mb-4">Practice Settings</h2>
                            <HandsSelector
                                mode={mode}
                                onModeChange={setMode}
                                leftPattern={leftPattern}
                                rightPattern={rightPattern}
                                leftPatterns={leftPatterns}
                                rightPatterns={rightPatterns}
                                onPatternChange={handlePatternChange}
                                style={style}
                                onStyleChange={setStyle}
                                isLoading={patternsLoading || generateMutation.isPending}
                            />
                        </div>

                        {/* Tempo Control */}
                        <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700/50">
                            <h3 className="text-sm font-medium text-slate-400 mb-3">Tempo</h3>
                            <div className="flex items-center gap-4">
                                <input
                                    type="range"
                                    min={40}
                                    max={200}
                                    value={tempo}
                                    onChange={(e) => setTempo(Number(e.target.value))}
                                    className="flex-1 accent-violet-500"
                                />
                                <span className="text-lg font-mono font-bold w-16 text-right">
                                    {tempo} <span className="text-sm text-slate-400">BPM</span>
                                </span>
                            </div>

                            <h3 className="text-sm font-medium text-slate-400 mt-4 mb-3">Bars Per Chord</h3>
                            <div className="flex gap-2">
                                {[1, 2, 4].map(b => (
                                    <button
                                        key={b}
                                        onClick={() => setBarsPerChord(b)}
                                        className={`
                      flex-1 py-2 px-3 rounded-lg text-sm font-medium
                      transition-colors
                      ${barsPerChord === b
                                                ? 'bg-violet-600 text-white'
                                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                            }
                    `}
                                    >
                                        {b} bar{b > 1 ? 's' : ''}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Chord Progression Input */}
                        <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700/50">
                            <h2 className="text-lg font-semibold mb-4">Chord Progression</h2>

                            {/* Preset buttons */}
                            <div className="flex flex-wrap gap-2 mb-4">
                                {PRESET_PROGRESSIONS.map(preset => (
                                    <button
                                        key={preset.name}
                                        onClick={() => applyPreset(preset)}
                                        className="px-3 py-1.5 text-sm bg-slate-700 hover:bg-slate-600 
                             rounded-lg transition-colors"
                                    >
                                        {preset.name}
                                    </button>
                                ))}
                            </div>

                            {/* Chord input */}
                            <input
                                type="text"
                                value={chordInput}
                                onChange={(e) => handleChordsChange(e.target.value)}
                                placeholder="Enter chords separated by commas (e.g., Dm7, G7, Cmaj7)"
                                className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg
                         text-slate-100 placeholder-slate-500
                         focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500"
                            />

                            {/* Chord chips */}
                            <div className="flex flex-wrap gap-2 mt-3">
                                {chords.map((chord, i) => (
                                    <span
                                        key={i}
                                        className="px-3 py-1.5 bg-violet-500/20 text-violet-300 
                             rounded-lg text-sm font-medium border border-violet-500/30"
                                    >
                                        {chord}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Generate Button */}
                        <motion.button
                            onClick={handleGenerate}
                            disabled={generateMutation.isPending || chords.length === 0}
                            className="w-full py-4 px-6 bg-gradient-to-r from-violet-600 to-indigo-600 
                       text-white font-semibold rounded-xl shadow-lg shadow-violet-500/25
                       hover:from-violet-500 hover:to-indigo-500
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-all"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            {generateMutation.isPending ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="animate-spin">⏳</span>
                                    Generating...
                                </span>
                            ) : (
                                <span className="flex items-center justify-center gap-2">
                                    🎹 Generate Practice MIDI
                                </span>
                            )}
                        </motion.button>

                        {/* Result */}
                        {generateMutation.data && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-6 bg-slate-800/50 rounded-xl border border-emerald-500/30"
                            >
                                <h3 className="text-lg font-semibold text-emerald-400 mb-4">
                                    ✅ Practice MIDI Generated!
                                </h3>

                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                                    <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                                        <div className="text-2xl font-bold text-slate-100">
                                            {generateMutation.data.left_notes_count}
                                        </div>
                                        <div className="text-xs text-blue-400">Left Hand Notes</div>
                                    </div>
                                    <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                                        <div className="text-2xl font-bold text-slate-100">
                                            {generateMutation.data.right_notes_count}
                                        </div>
                                        <div className="text-xs text-green-400">Right Hand Notes</div>
                                    </div>
                                    <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                                        <div className="text-2xl font-bold text-slate-100">
                                            {generateMutation.data.total_bars}
                                        </div>
                                        <div className="text-xs text-slate-400">Total Bars</div>
                                    </div>
                                    <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                                        <div className="text-2xl font-bold text-slate-100">
                                            {generateMutation.data.duration_seconds.toFixed(1)}s
                                        </div>
                                        <div className="text-xs text-slate-400">Duration</div>
                                    </div>
                                </div>

                                <a
                                    href={generateMutation.data.midi_url}
                                    download
                                    className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 
                           hover:bg-emerald-500 text-white rounded-lg transition-colors"
                                >
                                    📥 Download MIDI
                                </a>
                            </motion.div>
                        )}

                        {/* Error */}
                        {generateMutation.isError && (
                            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
                                Error: {generateMutation.error.message}
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}

export default HandsPracticePage;
