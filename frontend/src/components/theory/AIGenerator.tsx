/**
 * AI Generator Component
 * 
 * Categorized UI for AI-powered music theory generation
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation } from '@tanstack/react-query';
import {
    Sparkles,
    Music,
    Layers,
    Dumbbell,
    Search,
    Play,
    Loader2,
    ChevronDown,
    ChevronRight,
    Volume2,
} from 'lucide-react';
import {
    aiApi,
    type ProgressionStyle,
    type Mood,
    type VoicingStyle,
    type ExerciseType,
    type Difficulty,
    type ProgressionResponse,
    type VoicingResponse,
    type ExerciseResponse,
    type SubstitutionResponse,
    type ChordInfo,
    type VoicingInfo,
} from '../../lib/api';

// ============================================================================
// Types & Constants
// ============================================================================

interface CategoryConfig {
    id: string;
    name: string;
    icon: React.ReactNode;
    color: string;
    generators: GeneratorConfig[];
}

interface GeneratorConfig {
    id: string;
    name: string;
    description: string;
}

const CATEGORIES: CategoryConfig[] = [
    {
        id: 'progressions',
        name: 'Progressions',
        icon: <Music className="w-5 h-5" />,
        color: 'cyan',
        generators: [
            { id: 'progression', name: 'Chord Progression', description: 'Generate progressions in any style' },
            { id: 'reharmonization', name: 'Reharmonization', description: 'Transform existing progressions' },
        ],
    },
    {
        id: 'voicings',
        name: 'Voicings',
        icon: <Layers className="w-5 h-5" />,
        color: 'violet',
        generators: [
            { id: 'voicing', name: 'Chord Voicings', description: 'Get multiple voicing options' },
            { id: 'voice_leading', name: 'Voice Leading', description: 'Optimize transitions between chords' },
        ],
    },
    {
        id: 'exercises',
        name: 'Exercises',
        icon: <Dumbbell className="w-5 h-5" />,
        color: 'amber',
        generators: [
            { id: 'exercise', name: 'Practice Exercises', description: 'Custom exercises for any skill' },
        ],
    },
    {
        id: 'analysis',
        name: 'Analysis',
        icon: <Search className="w-5 h-5" />,
        color: 'emerald',
        generators: [
            { id: 'substitution', name: 'Chord Substitutions', description: 'Find substitute chords' },
        ],
    },
];

const KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
const MODES = ['major', 'minor', 'dorian', 'mixolydian', 'lydian', 'phrygian', 'locrian'];
const STYLES: ProgressionStyle[] = ['jazz', 'gospel', 'pop', 'classical', 'neo_soul', 'rnb', 'blues'];
const MOODS: Mood[] = ['happy', 'sad', 'tense', 'peaceful', 'energetic', 'mysterious', 'romantic'];
const VOICING_STYLES: VoicingStyle[] = ['open', 'closed', 'drop2', 'drop3', 'rootless', 'spread', 'gospel'];
const EXERCISE_TYPES: ExerciseType[] = ['scales', 'arpeggios', 'progressions', 'voice_leading', 'rhythm'];
const DIFFICULTIES: Difficulty[] = ['beginner', 'intermediate', 'advanced'];

// ============================================================================
// Sub-components
// ============================================================================

interface ChordDisplayProps {
    chord: ChordInfo;
    onPlay?: (midiNotes: number[]) => void;
}

function ChordDisplay({ chord, onPlay }: ChordDisplayProps) {
    return (
        <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
                <span className="text-lg font-semibold text-white">{chord.symbol}</span>
                {chord.function && (
                    <span className="text-sm px-2 py-0.5 bg-cyan-500/20 text-cyan-400 rounded">
                        {chord.function}
                    </span>
                )}
            </div>
            <div className="flex items-center gap-2 mb-2">
                <span className="text-xs text-slate-500">Notes:</span>
                <span className="text-sm text-slate-300">{chord.notes.join(' - ')}</span>
            </div>
            {chord.comment && (
                <p className="text-xs text-slate-400 italic">{chord.comment}</p>
            )}
            {onPlay && (
                <button
                    onClick={() => onPlay(chord.midi_notes)}
                    className="mt-2 flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300"
                >
                    <Volume2 className="w-3 h-3" /> Play
                </button>
            )}
        </div>
    );
}

interface VoicingDisplayProps {
    voicing: VoicingInfo;
    onPlay?: (midiNotes: number[]) => void;
}

function VoicingDisplay({ voicing, onPlay }: VoicingDisplayProps) {
    return (
        <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">{voicing.name}</span>
                <span className="text-xs px-2 py-0.5 bg-violet-500/20 text-violet-400 rounded">
                    {voicing.hand}
                </span>
            </div>
            <div className="text-sm text-slate-300 mb-1">
                Notes: {voicing.notes.join(' - ')}
            </div>
            {voicing.fingering && (
                <div className="text-xs text-slate-400">
                    Fingering: {voicing.fingering.join(' - ')}
                </div>
            )}
            {onPlay && (
                <button
                    onClick={() => onPlay(voicing.midi_notes)}
                    className="mt-2 flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300"
                >
                    <Volume2 className="w-3 h-3" /> Play
                </button>
            )}
        </div>
    );
}

// ============================================================================
// Main Component
// ============================================================================

interface AIGeneratorProps {
    onPlayChord?: (midiNotes: number[]) => void;
}

export function AIGenerator({ onPlayChord }: AIGeneratorProps) {
    const [expandedCategory, setExpandedCategory] = useState<string | null>('progressions');
    const [activeGenerator, setActiveGenerator] = useState<string>('progression');

    // Form states
    const [key, setKey] = useState('C');
    const [mode, setMode] = useState('major');
    const [style, setStyle] = useState<ProgressionStyle>('jazz');
    const [mood, setMood] = useState<Mood | ''>('');
    const [length, setLength] = useState(4);
    const [includeExtensions, setIncludeExtensions] = useState(true);
    const [chord, setChord] = useState('Cmaj7');
    const [voicingStyle, setVoicingStyle] = useState<VoicingStyle>('open');
    const [chord1, setChord1] = useState('Dm7');
    const [chord2, setChord2] = useState('G7');
    const [exerciseType, setExerciseType] = useState<ExerciseType>('scales');
    const [difficulty, setDifficulty] = useState<Difficulty>('intermediate');
    const [originalProgression, setOriginalProgression] = useState('C Am F G');

    // Results
    const [progressionResult, setProgressionResult] = useState<ProgressionResponse | null>(null);
    const [voicingResult, setVoicingResult] = useState<VoicingResponse | null>(null);
    const [exerciseResult, setExerciseResult] = useState<ExerciseResponse | null>(null);
    const [substitutionResult, setSubstitutionResult] = useState<SubstitutionResponse | null>(null);

    // Mutations
    const progressionMutation = useMutation({
        mutationFn: aiApi.generateProgression,
        onSuccess: setProgressionResult,
    });

    const reharmonizationMutation = useMutation({
        mutationFn: aiApi.generateReharmonization,
        onSuccess: (data) => {
            setProgressionResult({
                progression: data.reharmonized,
                key,
                style,
                analysis: data.explanation,
                tips: data.techniques_used,
            });
        },
    });

    const voicingMutation = useMutation({
        mutationFn: aiApi.generateVoicing,
        onSuccess: setVoicingResult,
    });

    const voiceLeadingMutation = useMutation({
        mutationFn: aiApi.optimizeVoiceLeading,
        onSuccess: (data) => {
            setVoicingResult({
                chord: `${chord1} → ${chord2}`,
                voicings: [data.chord1, data.chord2],
                tips: [data.movement, ...(data.tips || [])],
            });
        },
    });

    const exerciseMutation = useMutation({
        mutationFn: aiApi.generateExercise,
        onSuccess: setExerciseResult,
    });

    const substitutionMutation = useMutation({
        mutationFn: aiApi.getSubstitutions,
        onSuccess: setSubstitutionResult,
    });

    const isLoading = progressionMutation.isPending || reharmonizationMutation.isPending ||
        voicingMutation.isPending || voiceLeadingMutation.isPending ||
        exerciseMutation.isPending || substitutionMutation.isPending;

    const handleGenerate = () => {
        switch (activeGenerator) {
            case 'progression':
                progressionMutation.mutate({
                    key,
                    mode,
                    style,
                    mood: mood || undefined,
                    length,
                    include_extensions: includeExtensions,
                });
                break;
            case 'reharmonization':
                reharmonizationMutation.mutate({
                    original_progression: originalProgression.split(' ').filter(Boolean),
                    key,
                    style,
                });
                break;
            case 'voicing':
                voicingMutation.mutate({
                    chord,
                    style: voicingStyle,
                    hand: 'both',
                    include_fingering: true,
                });
                break;
            case 'voice_leading':
                voiceLeadingMutation.mutate({
                    chord1,
                    chord2,
                    style,
                });
                break;
            case 'exercise':
                exerciseMutation.mutate({
                    type: exerciseType,
                    key,
                    difficulty,
                });
                break;
            case 'substitution':
                substitutionMutation.mutate({
                    chord,
                    style,
                });
                break;
        }
    };

    const toggleCategory = (categoryId: string) => {
        setExpandedCategory(expandedCategory === categoryId ? null : categoryId);
    };

    const colorClasses: Record<string, string> = {
        cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
        violet: 'text-violet-400 bg-violet-500/10 border-violet-500/30',
        amber: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
        emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Categories & Generators */}
            <div className="lg:col-span-1 space-y-4">
                <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-5 h-5 text-violet-400" />
                    <h3 className="text-lg font-semibold text-white">AI Generators</h3>
                </div>

                {CATEGORIES.map((category) => (
                    <div key={category.id} className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
                        <button
                            onClick={() => toggleCategory(category.id)}
                            className={`w-full flex items-center justify-between p-3 hover:bg-slate-700/50 transition-colors ${expandedCategory === category.id ? 'bg-slate-700/30' : ''
                                }`}
                        >
                            <div className="flex items-center gap-2">
                                <span className={colorClasses[category.color]?.split(' ')[0]}>
                                    {category.icon}
                                </span>
                                <span className="font-medium text-white">{category.name}</span>
                            </div>
                            {expandedCategory === category.id ? (
                                <ChevronDown className="w-4 h-4 text-slate-400" />
                            ) : (
                                <ChevronRight className="w-4 h-4 text-slate-400" />
                            )}
                        </button>

                        <AnimatePresence>
                            {expandedCategory === category.id && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="overflow-hidden"
                                >
                                    <div className="p-2 space-y-1 border-t border-slate-700">
                                        {category.generators.map((gen) => (
                                            <button
                                                key={gen.id}
                                                onClick={() => setActiveGenerator(gen.id)}
                                                className={`w-full text-left p-2 rounded-md transition-colors ${activeGenerator === gen.id
                                                        ? `${colorClasses[category.color]} border`
                                                        : 'text-slate-300 hover:bg-slate-700/50'
                                                    }`}
                                            >
                                                <div className="font-medium text-sm">{gen.name}</div>
                                                <div className="text-xs text-slate-400">{gen.description}</div>
                                            </button>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                ))}
            </div>

            {/* Right Column - Generator Form & Results */}
            <div className="lg:col-span-2 space-y-6">
                {/* Generator Form */}
                <motion.div
                    key={activeGenerator}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-800/50 rounded-lg border border-slate-700 p-4"
                >
                    <h4 className="text-lg font-semibold text-white mb-4">
                        {CATEGORIES.flatMap(c => c.generators).find(g => g.id === activeGenerator)?.name}
                    </h4>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                        {/* Common fields */}
                        {['progression', 'reharmonization', 'exercise', 'substitution'].includes(activeGenerator) && (
                            <>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Key</label>
                                    <select
                                        value={key}
                                        onChange={(e) => setKey(e.target.value)}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                                    >
                                        {KEYS.map((k) => (
                                            <option key={k} value={k}>{k}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Style</label>
                                    <select
                                        value={style}
                                        onChange={(e) => setStyle(e.target.value as ProgressionStyle)}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm capitalize"
                                    >
                                        {STYLES.map((s) => (
                                            <option key={s} value={s}>{s.replace('_', ' ')}</option>
                                        ))}
                                    </select>
                                </div>
                            </>
                        )}

                        {/* Progression-specific */}
                        {activeGenerator === 'progression' && (
                            <>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Mode</label>
                                    <select
                                        value={mode}
                                        onChange={(e) => setMode(e.target.value)}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm capitalize"
                                    >
                                        {MODES.map((m) => (
                                            <option key={m} value={m}>{m}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Mood</label>
                                    <select
                                        value={mood}
                                        onChange={(e) => setMood(e.target.value as Mood)}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm capitalize"
                                    >
                                        <option value="">Any</option>
                                        {MOODS.map((m) => (
                                            <option key={m} value={m}>{m}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Length</label>
                                    <input
                                        type="number"
                                        min={2}
                                        max={16}
                                        value={length}
                                        onChange={(e) => setLength(Number(e.target.value))}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                                    />
                                </div>

                                <div className="flex items-center">
                                    <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={includeExtensions}
                                            onChange={(e) => setIncludeExtensions(e.target.checked)}
                                            className="rounded"
                                        />
                                        Extended chords
                                    </label>
                                </div>
                            </>
                        )}

                        {/* Reharmonization-specific */}
                        {activeGenerator === 'reharmonization' && (
                            <div className="col-span-full">
                                <label className="block text-xs text-slate-400 mb-1">Original Progression</label>
                                <input
                                    type="text"
                                    value={originalProgression}
                                    onChange={(e) => setOriginalProgression(e.target.value)}
                                    placeholder="C Am F G"
                                    className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                                />
                                <p className="text-xs text-slate-500 mt-1">Separate chords with spaces</p>
                            </div>
                        )}

                        {/* Voicing-specific */}
                        {activeGenerator === 'voicing' && (
                            <>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Chord</label>
                                    <input
                                        type="text"
                                        value={chord}
                                        onChange={(e) => setChord(e.target.value)}
                                        placeholder="Cmaj7"
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Voicing Style</label>
                                    <select
                                        value={voicingStyle}
                                        onChange={(e) => setVoicingStyle(e.target.value as VoicingStyle)}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm capitalize"
                                    >
                                        {VOICING_STYLES.map((v) => (
                                            <option key={v} value={v}>{v}</option>
                                        ))}
                                    </select>
                                </div>
                            </>
                        )}

                        {/* Voice Leading-specific */}
                        {activeGenerator === 'voice_leading' && (
                            <>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">From Chord</label>
                                    <input
                                        type="text"
                                        value={chord1}
                                        onChange={(e) => setChord1(e.target.value)}
                                        placeholder="Dm7"
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">To Chord</label>
                                    <input
                                        type="text"
                                        value={chord2}
                                        onChange={(e) => setChord2(e.target.value)}
                                        placeholder="G7"
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                                    />
                                </div>
                            </>
                        )}

                        {/* Exercise-specific */}
                        {activeGenerator === 'exercise' && (
                            <>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Exercise Type</label>
                                    <select
                                        value={exerciseType}
                                        onChange={(e) => setExerciseType(e.target.value as ExerciseType)}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm capitalize"
                                    >
                                        {EXERCISE_TYPES.map((t) => (
                                            <option key={t} value={t}>{t.replace('_', ' ')}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Difficulty</label>
                                    <select
                                        value={difficulty}
                                        onChange={(e) => setDifficulty(e.target.value as Difficulty)}
                                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm capitalize"
                                    >
                                        {DIFFICULTIES.map((d) => (
                                            <option key={d} value={d}>{d}</option>
                                        ))}
                                    </select>
                                </div>
                            </>
                        )}

                        {/* Substitution-specific */}
                        {activeGenerator === 'substitution' && (
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Chord to Substitute</label>
                                <input
                                    type="text"
                                    value={chord}
                                    onChange={(e) => setChord(e.target.value)}
                                    placeholder="G7"
                                    className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                                />
                            </div>
                        )}
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={isLoading}
                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-violet-600 to-cyan-600 text-white font-medium rounded-lg hover:from-violet-500 hover:to-cyan-500 transition-all disabled:opacity-50"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5" />
                                Generate with AI
                            </>
                        )}
                    </button>
                </motion.div>

                {/* Results */}
                <AnimatePresence mode="wait">
                    {/* Progression Results */}
                    {progressionResult && ['progression', 'reharmonization'].includes(activeGenerator) && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="bg-slate-800/50 rounded-lg border border-slate-700 p-4"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h4 className="font-semibold text-white">
                                    {progressionResult.key} {progressionResult.style} Progression
                                </h4>
                                <button
                                    onClick={() => {
                                        if (onPlayChord) {
                                            progressionResult.progression.forEach((chord, i) => {
                                                setTimeout(() => onPlayChord(chord.midi_notes), i * 1500);
                                            });
                                        }
                                    }}
                                    className="flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-300"
                                >
                                    <Play className="w-4 h-4" /> Play All
                                </button>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                                {progressionResult.progression.map((chord, i) => (
                                    <ChordDisplay key={i} chord={chord} onPlay={onPlayChord} />
                                ))}
                            </div>

                            {progressionResult.analysis && (
                                <div className="p-3 bg-slate-900/50 rounded-lg mb-3">
                                    <h5 className="text-sm font-medium text-slate-300 mb-1">Analysis</h5>
                                    <p className="text-sm text-slate-400">{progressionResult.analysis}</p>
                                </div>
                            )}

                            {progressionResult.tips && progressionResult.tips.length > 0 && (
                                <div className="p-3 bg-slate-900/50 rounded-lg">
                                    <h5 className="text-sm font-medium text-slate-300 mb-1">Tips</h5>
                                    <ul className="text-sm text-slate-400 list-disc list-inside">
                                        {progressionResult.tips.map((tip, i) => (
                                            <li key={i}>{tip}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Voicing Results */}
                    {voicingResult && ['voicing', 'voice_leading'].includes(activeGenerator) && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="bg-slate-800/50 rounded-lg border border-slate-700 p-4"
                        >
                            <h4 className="font-semibold text-white mb-4">
                                Voicings for {voicingResult.chord}
                            </h4>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                                {voicingResult.voicings.map((voicing, i) => (
                                    <VoicingDisplay key={i} voicing={voicing} onPlay={onPlayChord} />
                                ))}
                            </div>

                            {voicingResult.tips && voicingResult.tips.length > 0 && (
                                <div className="p-3 bg-slate-900/50 rounded-lg">
                                    <h5 className="text-sm font-medium text-slate-300 mb-1">Tips</h5>
                                    <ul className="text-sm text-slate-400 list-disc list-inside">
                                        {voicingResult.tips.map((tip, i) => (
                                            <li key={i}>{tip}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Exercise Results */}
                    {exerciseResult && activeGenerator === 'exercise' && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="bg-slate-800/50 rounded-lg border border-slate-700 p-4"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h4 className="font-semibold text-white">{exerciseResult.title}</h4>
                                <span className="text-xs px-2 py-1 bg-amber-500/20 text-amber-400 rounded capitalize">
                                    {exerciseResult.difficulty}
                                </span>
                            </div>

                            <p className="text-sm text-slate-400 mb-4">{exerciseResult.description}</p>

                            <div className="space-y-3 mb-4">
                                {exerciseResult.steps.map((step, i) => (
                                    <div key={i} className="flex gap-3 p-3 bg-slate-900/50 rounded-lg">
                                        <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-amber-500/20 text-amber-400 rounded-full text-sm font-medium">
                                            {i + 1}
                                        </span>
                                        <div className="flex-1">
                                            <p className="text-sm text-slate-300">{step.instruction}</p>
                                            {step.notes && (
                                                <p className="text-xs text-slate-500 mt-1">
                                                    Notes: {step.notes.join(' - ')}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {exerciseResult.variations && exerciseResult.variations.length > 0 && (
                                <div className="p-3 bg-slate-900/50 rounded-lg">
                                    <h5 className="text-sm font-medium text-slate-300 mb-1">Variations</h5>
                                    <ul className="text-sm text-slate-400 list-disc list-inside">
                                        {exerciseResult.variations.map((v, i) => (
                                            <li key={i}>{v}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Substitution Results */}
                    {substitutionResult && activeGenerator === 'substitution' && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="bg-slate-800/50 rounded-lg border border-slate-700 p-4"
                        >
                            <h4 className="font-semibold text-white mb-4">
                                Substitutions for {substitutionResult.original}
                            </h4>

                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                {substitutionResult.substitutions.map((sub, i) => (
                                    <ChordDisplay key={i} chord={sub} onPlay={onPlayChord} />
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

export default AIGenerator;
