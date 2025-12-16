
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Sparkles, Loader2, ArrowRight, Volume2, Gauge, GraduationCap, User, Lightbulb } from 'lucide-react';
import { aiApi, ProgressionStyle, ReharmonizationResponse, CreativityLevel } from '../../../lib/api';

interface ReharmonizerToolProps {
    onPlayChord: (midiNotes: number[]) => void;
}

const KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
const STYLES: ProgressionStyle[] = ['jazz', 'gospel', 'pop', 'classical', 'neo_soul', 'rnb', 'blues'];

// Boldness levels for reharmonization
const BOLDNESS_LEVELS: { value: CreativityLevel; label: string; description: string; examples: string }[] = [
    {
        value: 'conservative',
        label: 'Gentle',
        description: 'Subtle enhancements only',
        examples: 'Add 7ths, smooth voice leading'
    },
    {
        value: 'balanced',
        label: 'Tasteful',
        description: 'Modern but recognizable',
        examples: 'Tritone subs, passing chords'
    },
    {
        value: 'adventurous',
        label: 'Bold',
        description: 'Significant transformation',
        examples: 'Modal interchange, borrowed chords'
    },
    {
        value: 'experimental',
        label: 'Radical',
        description: 'Complete reimagining',
        examples: 'Reharmonization chains, shock value'
    },
];

// Artist references for reharmonization style
const STYLE_ARTISTS: Record<ProgressionStyle, string[]> = {
    jazz: ['Bill Evans', 'Herbie Hancock', 'Brad Mehldau'],
    gospel: ['Kirk Franklin', 'Fred Hammond'],
    neo_soul: ['Robert Glasper', 'D\'Angelo'],
    pop: ['Jacob Collier'],
    classical: [],
    rnb: [],
    blues: [],
};

export function ReharmonizerTool({ onPlayChord }: ReharmonizerToolProps) {
    const [originalProgression, setOriginalProgression] = useState('C Am F G');
    const [key, setKey] = useState('C');
    const [style, setStyle] = useState<ProgressionStyle>('jazz');

    // Enhanced options
    const [boldness, setBoldness] = useState<CreativityLevel>('balanced');
    const [styleReference, setStyleReference] = useState<string>('');
    const [generateVariations, setGenerateVariations] = useState(false);
    const [includeEducation, setIncludeEducation] = useState(true);

    // Display state
    const [activeVariation, setActiveVariation] = useState<number>(-1);

    const [result, setResult] = useState<ReharmonizationResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.generateReharmonization,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
            setActiveVariation(-1);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        mutation.mutate({
            original_progression: originalProgression.split(' ').filter(Boolean),
            key,
            style,
            creativity: boldness,
            style_reference: styleReference || undefined,
            generate_variations: generateVariations,
            include_education: includeEducation,
        });
    };

    // Get displayed progression (primary or variation)
    const displayedReharmonization =
        activeVariation >= 0 && result?.variations_data?.[activeVariation]
            ? result.variations_data[activeVariation]
            : result?.reharmonized ?? [];

    const availableArtists = STYLE_ARTISTS[style] || [];

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Sparkles className="w-8 h-8 text-purple-400" />
                        AI Reharmonizer
                    </h2>
                    <p className="text-slate-400">Transform simple progressions with controllable boldness</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
                    <div className="space-y-4">
                        {/* Original Progression */}
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

                        {/* Key & Style */}
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
                                    onChange={(e) => {
                                        setStyle(e.target.value as ProgressionStyle);
                                        setStyleReference('');
                                    }}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-purple-500 outline-none capitalize"
                                >
                                    {STYLES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                                </select>
                            </div>
                        </div>

                        {/* Artist Reference */}
                        {availableArtists.length > 0 && (
                            <div>
                                <label className="block text-xs text-slate-400 mb-1 flex items-center gap-1">
                                    <User className="w-3 h-3" />
                                    Style Reference
                                </label>
                                <select
                                    value={styleReference}
                                    onChange={(e) => setStyleReference(e.target.value)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-purple-500 outline-none"
                                >
                                    <option value="">None</option>
                                    {availableArtists.map(artist => (
                                        <option key={artist} value={artist}>Channel {artist}</option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {/* Boldness Level - Key Feature */}
                        <div className="pt-2 border-t border-slate-800">
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                <Gauge className="w-3 h-3 text-purple-400" />
                                Boldness Level
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                {BOLDNESS_LEVELS.map((level) => (
                                    <button
                                        key={level.value}
                                        onClick={() => setBoldness(level.value)}
                                        className={`px-3 py-2 rounded-lg text-xs transition-all text-left ${boldness === level.value
                                                ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                            }`}
                                    >
                                        <div className="font-medium">{level.label}</div>
                                        <div className="text-[10px] opacity-70 mt-0.5">{level.description}</div>
                                    </button>
                                ))}
                            </div>
                            <p className="text-[10px] text-slate-500 mt-2 flex items-start gap-1">
                                <Lightbulb className="w-3 h-3 shrink-0 mt-0.5" />
                                {BOLDNESS_LEVELS.find(l => l.value === boldness)?.examples}
                            </p>
                        </div>

                        {/* Options */}
                        <div className="pt-2 border-t border-slate-800 space-y-2">
                            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer p-2 hover:bg-slate-800/50 rounded-lg transition-colors">
                                <input
                                    type="checkbox"
                                    checked={generateVariations}
                                    onChange={(e) => setGenerateVariations(e.target.checked)}
                                    className="rounded border-slate-600 text-amber-500 focus:ring-offset-slate-900 focus:ring-amber-500"
                                />
                                <span className="flex items-center gap-1">
                                    Generate Variations
                                    <span className="text-[10px] text-amber-400 bg-amber-500/10 px-1 rounded">NEW</span>
                                </span>
                            </label>

                            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer p-2 hover:bg-slate-800/50 rounded-lg transition-colors">
                                <input
                                    type="checkbox"
                                    checked={includeEducation}
                                    onChange={(e) => setIncludeEducation(e.target.checked)}
                                    className="rounded border-slate-600 text-green-500 focus:ring-offset-slate-900 focus:ring-green-500"
                                />
                                <span className="flex items-center gap-1">
                                    <GraduationCap className="w-3 h-3" />
                                    Include Theory Explanation
                                </span>
                            </label>
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
                            {/* Variation Selector */}
                            {result.variations && result.variations.length > 0 && (
                                <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-xl p-4">
                                    <h3 className="text-sm font-medium text-amber-400 mb-3 flex items-center gap-2">
                                        <Sparkles className="w-4 h-4" />
                                        Reharmonization Variations
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        <button
                                            onClick={() => setActiveVariation(-1)}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeVariation === -1
                                                    ? 'bg-purple-500 text-white'
                                                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                                }`}
                                        >
                                            Primary
                                        </button>
                                        {result.variations.map((variation, idx) => (
                                            <button
                                                key={idx}
                                                onClick={() => setActiveVariation(idx)}
                                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeVariation === idx
                                                        ? 'bg-amber-500 text-white'
                                                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                                    }`}
                                                title={variation.description}
                                            >
                                                {variation.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

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
                                                {displayedReharmonization.map((chord, i) => (
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

                            {/* Educational Content */}
                            {result.education && (
                                <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                        <GraduationCap className="w-5 h-5 text-green-400" />
                                        Why This Reharmonization Works
                                    </h3>

                                    <p className="text-sm text-slate-300 leading-relaxed mb-4">
                                        {result.education.why_it_works}
                                    </p>

                                    {result.education.theory_concepts && result.education.theory_concepts.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mb-4">
                                            {result.education.theory_concepts.map((concept, i) => (
                                                <span key={i} className="px-2 py-1 bg-green-500/10 text-green-300 text-xs rounded-full">
                                                    {concept}
                                                </span>
                                            ))}
                                        </div>
                                    )}

                                    {result.education.alternatives && result.education.alternatives.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-green-300 mb-2">Other Approaches</h4>
                                            <ul className="text-sm text-slate-400 space-y-1">
                                                {result.education.alternatives.map((alt, i) => (
                                                    <li key={i} className="flex items-start gap-2">
                                                        <span className="mt-1.5 w-1 h-1 bg-green-500 rounded-full shrink-0" />
                                                        {alt}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}

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
