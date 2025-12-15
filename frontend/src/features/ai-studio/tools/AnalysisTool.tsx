import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Search, Volume2, ArrowRightLeft, Loader2 } from 'lucide-react';
import { aiApi, ProgressionStyle, SubstitutionResponse } from '../../../lib/api';

interface AnalysisToolProps {
    onPlayChord: (midiNotes: number[]) => void;
}

const STYLES: ProgressionStyle[] = ['jazz', 'gospel', 'neo_soul', 'rnb'];

export function AnalysisTool({ onPlayChord }: AnalysisToolProps) {
    const [chord, setChord] = useState('CMaj7');
    const [style, setStyle] = useState<ProgressionStyle>('jazz');

    // Optional context (previous/next chords) could be added here

    const [result, setResult] = useState<SubstitutionResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.getSubstitutions,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        mutation.mutate({
            chord,
            style,
        });
    };

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Search className="w-8 h-8 text-emerald-400" />
                        Chord Analysis & Substitution
                    </h2>
                    <p className="text-slate-400">Discover harmonic possibilities and reharmonization options</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Target Chord</label>
                            <input
                                type="text"
                                value={chord}
                                onChange={(e) => setChord(e.target.value)}
                                placeholder="Cmaj7"
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-emerald-500 outline-none"
                            />
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Style Context</label>
                            <select
                                value={style}
                                onChange={(e) => setStyle(e.target.value as ProgressionStyle)}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-emerald-500 outline-none capitalize"
                            >
                                {STYLES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                            </select>
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={mutation.isPending}
                        className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg font-medium shadow-lg shadow-emerald-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
                    >
                        {mutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Search className="w-5 h-5" />
                                Find Substitutions
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
                        <div className="space-y-4">
                            <h3 className="text-lg font-semibold text-white">Substitutions for {result.original}</h3>
                            <div className="grid gap-4">
                                {result.substitutions.map((sub, idx) => {
                                    const explanation = result.explanations[sub.symbol];
                                    return (
                                        <div key={idx} className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex gap-4 transition-all hover:bg-slate-800/80">
                                            <div className="flex-shrink-0 w-12 h-12 bg-slate-900 rounded-lg flex items-center justify-center border border-slate-700">
                                                <ArrowRightLeft className="w-6 h-6 text-emerald-500/50" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <h4 className="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors">
                                                            {sub.symbol}
                                                        </h4>
                                                        <div className="text-sm font-mono text-slate-500 mt-1">
                                                            {sub.notes.join(' - ')}
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => onPlayChord(sub.midi_notes)}
                                                        className="p-2 bg-slate-700/50 hover:bg-emerald-500/20 text-slate-300 hover:text-emerald-400 rounded-lg transition-colors"
                                                    >
                                                        <Volume2 className="w-4 h-4" />
                                                    </button>
                                                </div>

                                                {explanation && (
                                                    <div className="mt-3 text-sm text-slate-300 bg-slate-900/50 rounded p-2 border border-slate-800/50">
                                                        {explanation}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Search className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Explore Substitutions</p>
                            <p className="text-sm">Find tritone substitutions, secondary dominants, and more</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
