import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Zap, Play, Loader2, Search } from 'lucide-react';
import { aiApi, LickStyle, Difficulty, LicksResponse } from '../../../lib/api';
import { usePiano } from '../../../hooks/usePiano';

const LICK_STYLES: LickStyle[] = ['bebop', 'blues', 'modern', 'gospel', 'swing', 'bossa'];
const DIFFICULTIES: Difficulty[] = ['beginner', 'intermediate', 'advanced'];

export function LicksTool() {
    // We use local usePiano for playback here since we need finer control for licks (arpeggio/scale)
    // Or we could use the passed context if it exposes playArpeggio/Scale. 
    // The context in MusicAIStudio only exposes playChord. 
    // So we'll use usePiano directly here.
    const piano = usePiano();

    const [style, setStyle] = useState<LickStyle>('bebop');
    const [contextType, setContextType] = useState<'chord' | 'progression'>('chord');
    const [context, setContext] = useState('Cm7');
    const [difficulty, setDifficulty] = useState<Difficulty>('intermediate');
    const [length, setLength] = useState(2);

    const [result, setResult] = useState<LicksResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.generateLicks,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        mutation.mutate({
            style,
            context_type: contextType,
            context,
            difficulty,
            length_bars: length,
            direction: 'mixed',
        });
    };

    const handlePlayLick = async (midiNotes: number[]) => {
        // Play as a fast melodic line (lick)
        // 8th notes at 120bpm = 0.25s per note roughly. 
        // Licks usually played faster, say 0.2s or 0.15s
        await piano.playScale(midiNotes, 0.2, 0.0, 0.7);
    };

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Zap className="w-8 h-8 text-pink-400" />
                        Lick Generator
                    </h2>
                    <p className="text-slate-400">Generate idiomatic phrases for improvisation</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4">
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Style</label>
                                <select
                                    value={style}
                                    onChange={(e) => setStyle(e.target.value as LickStyle)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-pink-500 outline-none capitalize"
                                >
                                    {LICK_STYLES.map(s => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Difficulty</label>
                                <select
                                    value={difficulty}
                                    onChange={(e) => setDifficulty(e.target.value as Difficulty)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-pink-500 outline-none capitalize"
                                >
                                    {DIFFICULTIES.map(d => <option key={d} value={d}>{d}</option>)}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Context Type</label>
                            <div className="flex bg-slate-800 rounded-lg p-1">
                                <button
                                    onClick={() => setContextType('chord')}
                                    className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${contextType === 'chord' ? 'bg-pink-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                                >
                                    Single Chord
                                </button>
                                <button
                                    onClick={() => setContextType('progression')}
                                    className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${contextType === 'progression' ? 'bg-pink-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                                >
                                    Progression
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">
                                {contextType === 'chord' ? 'Chord Symbol' : 'Progression'}
                            </label>
                            <input
                                type="text"
                                value={context}
                                onChange={(e) => setContext(e.target.value)}
                                placeholder={contextType === 'chord' ? "Cm7" : "Cm7 F7 Bbmaj7"}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-pink-500 outline-none"
                            />
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Length (Bars)</label>
                            <input
                                type="range"
                                min={1}
                                max={4}
                                value={length}
                                onChange={(e) => setLength(Number(e.target.value))}
                                className="w-full accent-pink-500"
                            />
                            <div className="flex justify-between text-xs text-slate-500 mt-1">
                                <span>1</span>
                                <span>{length} bars</span>
                                <span>4</span>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={mutation.isPending}
                        className="w-full py-3 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-500 hover:to-rose-500 text-white rounded-lg font-medium shadow-lg shadow-pink-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
                    >
                        {mutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Composing...
                            </>
                        ) : (
                            <>
                                <Zap className="w-5 h-5 fill-current" />
                                Generate Licks
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
                            {result.licks.map((lick, idx) => (
                                <div key={idx} className="bg-slate-800 border border-slate-700 rounded-xl p-4 transition-all hover:border-pink-500/30">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="font-bold text-white text-lg">{lick.name}</h3>
                                            <div className="flex gap-2 mt-1">
                                                {lick.style_tags.map((tag, i) => (
                                                    <span key={i} className="text-[10px] uppercase tracking-wider bg-slate-900 text-slate-400 px-1.5 py-0.5 rounded">
                                                        {tag}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handlePlayLick(lick.midi_notes)}
                                            className="p-2 bg-pink-600/20 text-pink-400 rounded-lg hover:bg-pink-600 hover:text-white transition-colors flex items-center gap-2"
                                        >
                                            <Play className="w-4 h-4 fill-current" />
                                            <span>Play</span>
                                        </button>
                                    </div>

                                    {/* Visual Representation (Simple bar view) */}
                                    <div className="h-24 bg-slate-900/50 rounded-lg border border-slate-800 mb-4 relative overflow-hidden flex items-end px-4 pb-4 gap-1">
                                        {lick.midi_notes.map((note, i) => {
                                            // Normalize height for visualization
                                            const min = Math.min(...lick.midi_notes);
                                            const max = Math.max(...lick.midi_notes);
                                            const range = max - min || 1;
                                            const heightPct = 20 + ((note - min) / range) * 60;

                                            return (
                                                <div
                                                    key={i}
                                                    className="flex-1 bg-pink-500/40 hover:bg-pink-400 rounded-t-sm transition-all"
                                                    style={{ height: `${heightPct}%` }}
                                                    title={`Note: ${lick.notes[i]}`}
                                                />
                                            );
                                        })}
                                    </div>

                                    <div className="bg-slate-900/30 rounded p-3 text-sm text-slate-400 font-mono">
                                        {lick.notes.join(' - ')}
                                    </div>

                                    {lick.theory_analysis && (
                                        <div className="mt-4 pt-4 border-t border-slate-700/50">
                                            <p className="text-sm text-slate-300">
                                                <span className="font-medium text-pink-400">Analysis: </span>
                                                Uses {lick.theory_analysis.scale_degrees.join(', ')} scale degrees.
                                                {lick.theory_analysis.approach_tones.length > 0 && ` Features chromatic approach tones.`}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}

                            <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6">
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <Search className="w-5 h-5 text-pink-400" />
                                    Deep Dive
                                </h3>

                                <p className="text-sm text-slate-300 mb-4 leading-relaxed">
                                    {result.analysis}
                                </p>

                                <div>
                                    <h4 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider text-xs">Practice Tips</h4>
                                    <ul className="text-sm text-slate-400 space-y-2">
                                        {result.practice_tips.map((tip, i) => (
                                            <li key={i} className="flex items-start gap-2">
                                                <span className="mt-1.5 w-1 h-1 bg-pink-500 rounded-full shrink-0" />
                                                {tip}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Zap className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Generate Licks</p>
                            <p className="text-sm">Create jazz lines and phrases to expand your vocabulary</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
