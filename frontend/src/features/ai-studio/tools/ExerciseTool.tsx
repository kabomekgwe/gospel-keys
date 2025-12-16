
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Dumbbell, Loader2, Target, Trophy, Timer, Flame, GraduationCap } from 'lucide-react';
import { aiApi, ExerciseType, Difficulty, ExerciseResponse, CreativityLevel } from '../../../lib/api';
import { PracticeButton } from '../components/PracticeButton';

const KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
const EXERCISE_TYPES: ExerciseType[] = ['scales', 'arpeggios', 'progressions', 'voice_leading', 'rhythm'];
const DIFFICULTIES: Difficulty[] = ['beginner', 'intermediate', 'advanced'];

// Session durations
const SESSION_DURATIONS = [
    { value: 5, label: '5 min', description: 'Quick warmup' },
    { value: 15, label: '15 min', description: 'Focused session' },
    { value: 30, label: '30 min', description: 'Deep practice' },
    { value: 60, label: '1 hour', description: 'Master session' },
];

// Creativity for exercise generation
const CREATIVITY_LEVELS: { value: CreativityLevel; label: string }[] = [
    { value: 'conservative', label: 'Traditional' },
    { value: 'balanced', label: 'Mixed' },
    { value: 'adventurous', label: 'Creative' },
];

export function ExerciseTool() {
    const [type, setType] = useState<ExerciseType>('scales');
    const [key, setKey] = useState('C');
    const [difficulty, setDifficulty] = useState<Difficulty>('intermediate');
    const [focus, setFocus] = useState('');

    // Enhanced options
    const [sessionDuration, setSessionDuration] = useState(15);
    const [creativity, setCreativity] = useState<CreativityLevel>('balanced');
    const [includeWarmup, setIncludeWarmup] = useState(true);

    const [result, setResult] = useState<ExerciseResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Practice mode state
    const [activeStep, setActiveStep] = useState<number | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.generateExercise,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
            setActiveStep(null);
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
                    <p className="text-slate-400">Custom exercises with built-in practice mode</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
                    <div className="space-y-4">
                        {/* Exercise Type */}
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

                        {/* Key & Difficulty */}
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

                        {/* Specific Focus */}
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

                        {/* Session Duration */}
                        <div className="pt-2 border-t border-slate-800">
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                <Timer className="w-3 h-3 text-amber-400" />
                                Session Duration
                            </label>
                            <div className="grid grid-cols-4 gap-1">
                                {SESSION_DURATIONS.map((duration) => (
                                    <button
                                        key={duration.value}
                                        onClick={() => setSessionDuration(duration.value)}
                                        className={`px-2 py-1.5 rounded-lg text-xs font-medium transition-all ${sessionDuration === duration.value
                                                ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                            }`}
                                        title={duration.description}
                                    >
                                        {duration.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Creativity */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                <Flame className="w-3 h-3 text-orange-400" />
                                Exercise Style
                            </label>
                            <div className="grid grid-cols-3 gap-1">
                                {CREATIVITY_LEVELS.map((level) => (
                                    <button
                                        key={level.value}
                                        onClick={() => setCreativity(level.value)}
                                        className={`px-2 py-1.5 rounded-lg text-xs font-medium transition-all ${creativity === level.value
                                                ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                            }`}
                                    >
                                        {level.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Options */}
                        <div className="pt-2 border-t border-slate-800">
                            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer p-2 hover:bg-slate-800/50 rounded-lg transition-colors">
                                <input
                                    type="checkbox"
                                    checked={includeWarmup}
                                    onChange={(e) => setIncludeWarmup(e.target.checked)}
                                    className="rounded border-slate-600 text-amber-500 focus:ring-offset-slate-900 focus:ring-amber-500"
                                />
                                <span>Include Warmup Routine</span>
                            </label>
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
                                    <div className="flex items-center gap-2">
                                        <span className="px-3 py-1 bg-amber-500/10 text-amber-500 text-xs rounded-full border border-amber-500/20 capitalize">
                                            {result.difficulty}
                                        </span>
                                        <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 text-xs rounded-full border border-cyan-500/20">
                                            ~{sessionDuration} min
                                        </span>
                                    </div>
                                </div>
                                <p className="text-slate-400 mb-6">{result.description}</p>

                                {/* Exercise Steps */}
                                <div className="space-y-4">
                                    {result.steps.map((step, idx) => (
                                        <div
                                            key={idx}
                                            className={`flex gap-4 p-4 rounded-lg border transition-all cursor-pointer ${activeStep === idx
                                                    ? 'bg-amber-500/10 border-amber-500/30'
                                                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                                                }`}
                                            onClick={() => setActiveStep(activeStep === idx ? null : idx)}
                                        >
                                            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold border ${activeStep === idx
                                                    ? 'bg-amber-500 text-white border-amber-400'
                                                    : 'bg-slate-800 text-slate-400 border-slate-700'
                                                }`}>
                                                {idx + 1}
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-slate-200 mb-2">{step.instruction}</p>
                                                {step.notes && (
                                                    <div className="text-sm font-mono text-cyan-400 bg-slate-950/50 p-2 rounded w-fit">
                                                        {step.notes.join(' - ')}
                                                    </div>
                                                )}
                                                {activeStep === idx && (
                                                    <div className="mt-3 pt-3 border-t border-slate-700">
                                                        <PracticeButton
                                                            label={`Step ${idx + 1}`}
                                                            defaultTempo={60}
                                                        />
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Challenge Variations */}
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

                                {/* Educational Tip */}
                                <div className="mt-6 p-4 bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-lg border border-green-500/20">
                                    <h4 className="text-sm font-medium text-green-400 mb-2 flex items-center gap-1">
                                        <GraduationCap className="w-4 h-4" />
                                        Practice Tip
                                    </h4>
                                    <p className="text-sm text-slate-400">
                                        Start each step slowly and focus on accuracy. Use the Practice button on any step
                                        to set up a looped practice session with metronome.
                                    </p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Dumbbell className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Start Practicing</p>
                            <p className="text-sm">Generate targeted exercises with built-in practice mode</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
