
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Music, Play, Loader2, Volume2 } from 'lucide-react';
import { aiApi, ProgressionStyle, Mood, ProgressionResponse } from '../../../lib/api';

interface ProgressionToolProps {
    onPlayChord: (midiNotes: number[]) => void;
}

const KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
const MODES = ['major', 'minor', 'dorian', 'mixolydian', 'lydian', 'phrygian', 'locrian'];
const STYLES: ProgressionStyle[] = ['jazz', 'gospel', 'pop', 'classical', 'neo_soul', 'rnb', 'blues'];
const MOODS: Mood[] = ['happy', 'sad', 'tense', 'peaceful', 'energetic', 'mysterious', 'romantic'];

export function ProgressionTool({ onPlayChord }: ProgressionToolProps) {
    // Form State
    const [key, setKey] = useState('C');
    const [mode, setMode] = useState('major');
    const [style, setStyle] = useState<ProgressionStyle>('jazz');
    const [mood, setMood] = useState<Mood | ''>('');
    const [length, setLength] = useState(4);
    const [includeExtensions, setIncludeExtensions] = useState(true);

    // Results State
    const [result, setResult] = useState<ProgressionResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.generateProgression,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        mutation.mutate({
            key,
            mode,
            style,
            mood: mood || undefined,
            length,
            include_extensions: includeExtensions,
        });
    };

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Music className="w-8 h-8 text-cyan-400" />
                        Chord Progression Generator
                    </h2>
                    <p className="text-slate-400">Generate creative progressions in any style</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4">
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Key</label>
                                <select
                                    value={key}
                                    onChange={(e) => setKey(e.target.value)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-cyan-500 outline-none"
                                >
                                    {KEYS.map(k => <option key={k} value={k}>{k}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Mode</label>
                                <select
                                    value={mode}
                                    onChange={(e) => setMode(e.target.value)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-cyan-500 outline-none capitalize"
                                >
                                    {MODES.map(m => <option key={m} value={m}>{m}</option>)}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Style</label>
                            <select
                                value={style}
                                onChange={(e) => setStyle(e.target.value as ProgressionStyle)}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-cyan-500 outline-none capitalize"
                            >
                                {STYLES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Mood (Optional)</label>
                            <select
                                value={mood}
                                onChange={(e) => setMood(e.target.value as Mood)}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-cyan-500 outline-none capitalize"
                            >
                                <option value="">Any</option>
                                {MOODS.map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Length (Chords)</label>
                            <input
                                type="range"
                                min={2}
                                max={16}
                                value={length}
                                onChange={(e) => setLength(Number(e.target.value))}
                                className="w-full accent-cyan-500"
                            />
                            <div className="flex justify-between text-xs text-slate-500 mt-1">
                                <span>2</span>
                                <span>{length} chords</span>
                                <span>16</span>
                            </div>
                        </div>

                        <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer p-2 hover:bg-slate-800/50 rounded-lg transition-colors">
                            <input
                                type="checkbox"
                                checked={includeExtensions}
                                onChange={(e) => setIncludeExtensions(e.target.checked)}
                                className="rounded border-slate-600 text-cyan-500 focus:ring-offset-slate-900 focus:ring-cyan-500"
                            />
                            Include Extended Chords (7th, 9th, etc.)
                        </label>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={mutation.isPending}
                        className="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg font-medium shadow-lg shadow-cyan-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
                    >
                        {mutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5 fill-current" />
                                Generate Progression
                            </>
                        )}
                    </button>

                    {error && (
                        <div className="p-3 bg-red-500/10 text-red-400 text-sm rounded-lg border border-red-500/20">
                            {error}
                        </div>
                    )}
                </div>

                {/* Results Display */}
                <div className="lg:col-span-2 space-y-6 overflow-y-auto pr-2 custom-scrollbar">
                    {result ? (
                        <div className="space-y-6">
                            {/* Chords Grid */}
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                                {result.progression.map((chord, idx) => (
                                    <div
                                        key={idx}
                                        className="group relative bg-slate-800 border border-slate-700 hover:border-cyan-500/50 rounded-xl p-4 transition-all hover:bg-slate-800/80"
                                    >
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">
                                                {chord.symbol}
                                            </span>
                                            {chord.function && (
                                                <span className="text-[10px] uppercase tracking-wider text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded">
                                                    {chord.function}
                                                </span>
                                            )}
                                        </div>

                                        <div className="space-y-2">
                                            <div className="text-xs text-slate-400 font-mono">
                                                {chord.notes.join(' - ')}
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => onPlayChord(chord.midi_notes)}
                                            className="mt-3 w-full py-1.5 bg-slate-700/50 hover:bg-cyan-500/20 text-slate-300 hover:text-cyan-400 rounded text-xs flex items-center justify-center gap-1.5 transition-colors"
                                        >
                                            <Volume2 className="w-3 h-3" /> Play
                                        </button>
                                    </div>
                                ))}
                            </div>

                            {/* Analysis Card */}
                            <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6">
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <Volume2 className="w-5 h-5 text-indigo-400" />
                                    Analysis & Tips
                                </h3>

                                {result.analysis && (
                                    <div className="mb-4">
                                        <h4 className="text-sm font-medium text-slate-300 mb-2">Theoretical Analysis</h4>
                                        <p className="text-sm text-slate-400 leading-relaxed">
                                            {result.analysis}
                                        </p>
                                    </div>
                                )}

                                {result.tips && result.tips.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-medium text-slate-300 mb-2">Playing Tips</h4>
                                        <ul className="grid gap-2">
                                            {result.tips.map((tip, i) => (
                                                <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                                                    <span className="mt-1.5 w-1 h-1 bg-cyan-500 rounded-full shrink-0" />
                                                    {tip}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Music className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Ready to Create</p>
                            <p className="text-sm">Adjust settings and click Generate to start</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
