
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Sparkles, Loader2, ArrowRight, Volume2 } from 'lucide-react';
import { aiApi, ProgressionStyle, ReharmonizationResponse } from '../../../lib/api';

interface ReharmonizerToolProps {
    onPlayChord: (midiNotes: number[]) => void;
}

const KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
const STYLES: ProgressionStyle[] = ['jazz', 'gospel', 'pop', 'classical', 'neo_soul', 'rnb', 'blues'];

export function ReharmonizerTool({ onPlayChord }: ReharmonizerToolProps) {
    const [originalProgression, setOriginalProgression] = useState('C Am F G');
    const [key, setKey] = useState('C');
    const [style, setStyle] = useState<ProgressionStyle>('jazz');

    const [result, setResult] = useState<ReharmonizationResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.generateReharmonization,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        mutation.mutate({
            original_progression: originalProgression.split(' ').filter(Boolean),
            key,
            style,
        });
    };

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Sparkles className="w-8 h-8 text-purple-400" />
                        AI Reharmonizer
                    </h2>
                    <p className="text-slate-400">Transform simple progressions into sophisticated arrangements</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Original Progression</label>
                            <input
                                type="text"
                                value={originalProgression}
                                onChange={(e) => setOriginalProgression(e.target.value)}
                                placeholder="C Am F G"
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-purple-500 outline-none font-mono"
                            />
                            <p className="text-xs text-slate-500 mt-1">Separate chords with spaces (e.g. Dm7 G7 Cmaj7)</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Key</label>
                                <select
                                    value={key}
                                    onChange={(e) => setKey(e.target.value)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-purple-500 outline-none"
                                >
                                    {KEYS.map(k => <option key={k} value={k}>{k}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Target Style</label>
                                <select
                                    value={style}
                                    onChange={(e) => setStyle(e.target.value as ProgressionStyle)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-purple-500 outline-none capitalize"
                                >
                                    {STYLES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                                </select>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={mutation.isPending}
                        className="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg font-medium shadow-lg shadow-purple-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
                    >
                        {mutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Reharmonizing...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5" />
                                Reharmonize It
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
                            {/* Comparison View */}
                            <div className="grid gap-4">
                                <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                    <h3 className="text-xs uppercase tracking-wider text-slate-500 mb-3">Transformation</h3>

                                    <div className="space-y-4">
                                        <div className="flex items-center gap-4">
                                            <div className="w-24 text-sm text-slate-400">Original</div>
                                            <div className="flex flex-wrap gap-2">
                                                {result.original.map((chord, i) => (
                                                    <div key={i} className="bg-slate-900 px-3 py-1.5 rounded text-slate-300 font-mono text-sm border border-slate-800">
                                                        {chord}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="flex justify-center">
                                            <ArrowRight className="text-purple-500/50 w-6 h-6 rotate-90 md:rotate-0" />
                                        </div>

                                        <div className="flex items-center gap-4">
                                            <div className="w-24 text-sm text-purple-400 font-medium">Reharmonized</div>
                                            <div className="flex flex-wrap gap-2">
                                                {result.reharmonized.map((chord, i) => (
                                                    <div key={i} className="bg-purple-500/10 px-3 py-1.5 rounded text-purple-300 font-mono text-sm border border-purple-500/30 flex items-center gap-2">
                                                        <span>{chord.symbol}</span>
                                                        <button
                                                            onClick={() => onPlayChord && onPlayChord(chord.midi_notes)}
                                                            className="hover:text-white transition-colors"
                                                        >
                                                            <Volume2 className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Analysis Card */}
                            <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6">
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <Sparkles className="w-5 h-5 text-purple-400" />
                                    Analysis
                                </h3>

                                <div className="mb-6">
                                    <p className="text-sm text-slate-300 leading-relaxed">
                                        {result.explanation}
                                    </p>
                                </div>

                                {result.techniques_used && result.techniques_used.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-medium text-slate-400 mb-3 uppercase tracking-wider text-xs">Techniques Applied</h4>
                                        <div className="flex flex-wrap gap-2">
                                            {result.techniques_used.map((tech, i) => (
                                                <span key={i} className="px-3 py-1 bg-slate-700/50 text-slate-300 text-xs rounded-full border border-slate-600">
                                                    {tech}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Sparkles className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Reharmonize Your Chords</p>
                            <p className="text-sm text-center max-w-md mt-2">
                                Enter a simple chord progression (e.g., "C F G C") and let the AI transform it with advanced jazz, gospel, or neo-soul harmonies.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
