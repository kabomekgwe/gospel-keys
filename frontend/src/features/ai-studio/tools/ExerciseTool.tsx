
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Dumbbell, Loader2, Target, Trophy } from 'lucide-react';
import { aiApi, ExerciseType, Difficulty, ExerciseResponse } from '../../../lib/api';

const KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
const EXERCISE_TYPES: ExerciseType[] = ['scales', 'arpeggios', 'progressions', 'voice_leading', 'rhythm'];
const DIFFICULTIES: Difficulty[] = ['beginner', 'intermediate', 'advanced'];

export function ExerciseTool() {
    const [type, setType] = useState<ExerciseType>('scales');
    const [key, setKey] = useState('C');
    const [difficulty, setDifficulty] = useState<Difficulty>('intermediate');
    const [focus, setFocus] = useState('');

    const [result, setResult] = useState<ExerciseResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.generateExercise,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        mutation.mutate({
            type,
            key,
            difficulty,
            focus: focus || undefined,
        });
    };

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Dumbbell className="w-8 h-8 text-amber-400" />
                        Practice Generator
                    </h2>
                    <p className="text-slate-400">Custom exercises tailored to your needs</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Exercise Type</label>
                            <select
                                value={type}
                                onChange={(e) => setType(e.target.value as ExerciseType)}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-amber-500 outline-none capitalize"
                            >
                                {EXERCISE_TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
                            </select>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Key</label>
                                <select
                                    value={key}
                                    onChange={(e) => setKey(e.target.value)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-amber-500 outline-none"
                                >
                                    {KEYS.map(k => <option key={k} value={k}>{k}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Difficulty</label>
                                <select
                                    value={difficulty}
                                    onChange={(e) => setDifficulty(e.target.value as Difficulty)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-amber-500 outline-none capitalize"
                                >
                                    {DIFFICULTIES.map(d => <option key={d} value={d}>{d}</option>)}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Specific Focus (Optional)</label>
                            <input
                                type="text"
                                value={focus}
                                onChange={(e) => setFocus(e.target.value)}
                                placeholder="e.g. thumb cross-under, speed"
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-amber-500 outline-none"
                            />
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={mutation.isPending}
                        className="w-full py-3 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white rounded-lg font-medium shadow-lg shadow-amber-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
                    >
                        {mutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Target className="w-5 h-5" />
                                Generate Exercise
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
                            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-xl font-bold text-white">{result.title}</h3>
                                    <span className="px-3 py-1 bg-amber-500/10 text-amber-500 text-xs rounded-full border border-amber-500/20 capitalize">
                                        {result.difficulty}
                                    </span>
                                </div>
                                <p className="text-slate-400 mb-6">{result.description}</p>

                                <div className="space-y-4">
                                    {result.steps.map((step, idx) => (
                                        <div key={idx} className="flex gap-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800">
                                            <div className="flex-shrink-0 w-8 h-8 bg-slate-800 rounded-full flex items-center justify-center text-slate-400 font-bold border border-slate-700">
                                                {idx + 1}
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-slate-200 mb-2">{step.instruction}</p>
                                                {step.notes && (
                                                    <div className="text-sm font-mono text-cyan-400 bg-slate-950/50 p-2 rounded w-fit">
                                                        {step.notes.join(' - ')}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {result.variations && result.variations.length > 0 && (
                                    <div className="mt-8 pt-6 border-t border-slate-700">
                                        <h4 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-2">
                                            <Trophy className="w-4 h-4 text-yellow-500" />
                                            Challenge Variations
                                        </h4>
                                        <ul className="grid gap-2">
                                            {result.variations.map((v, i) => (
                                                <li key={i} className="text-sm text-slate-400 flex items-start gap-2">
                                                    <span className="mt-1.5 w-1 h-1 bg-amber-500 rounded-full shrink-0" />
                                                    {v}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Dumbbell className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Start Practicing</p>
                            <p className="text-sm">Generate targeted exercises to improve your skills</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
