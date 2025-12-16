import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Zap, Play, Loader2, Search, Target, Sparkles, Music, User, GraduationCap } from 'lucide-react';
import { aiApi, LickStyle, Difficulty, LicksResponse, PhrasePosition, CreativityLevel } from '../../../lib/api';
import { usePiano } from '../../../hooks/usePiano';

const LICK_STYLES: LickStyle[] = ['bebop', 'blues', 'modern', 'gospel', 'swing', 'bossa'];
const DIFFICULTIES: Difficulty[] = ['beginner', 'intermediate', 'advanced'];

// Phrase positions with descriptions
const PHRASE_POSITIONS: { value: PhrasePosition; label: string; icon: string; description: string }[] = [
    { value: 'start', label: 'Start', icon: '🎬', description: 'Beginning of phrase - establish a motif' },
    { value: 'middle', label: 'Middle', icon: '🎵', description: 'Middle of phrase - develop the idea' },
    { value: 'end', label: 'End', icon: '🎯', description: 'End of phrase - resolve and conclude' },
    { value: 'turnaround', label: 'Turnaround', icon: '🔄', description: 'Transition back to the beginning' },
];

// Creativity levels
const CREATIVITY_LEVELS: { value: CreativityLevel; label: string }[] = [
    { value: 'conservative', label: 'Classic' },
    { value: 'balanced', label: 'Balanced' },
    { value: 'adventurous', label: 'Bold' },
    { value: 'experimental', label: 'Wild' },
];

// Artist references by lick style
const STYLE_ARTISTS: Record<LickStyle, string[]> = {
    bebop: ['Charlie Parker', 'Dizzy Gillespie', 'Bud Powell'],
    blues: ['Oscar Peterson', 'Ray Charles'],
    modern: ['Robert Glasper', 'Brad Mehldau'],
    gospel: ['Cory Henry', 'Kirk Franklin'],
    swing: ['Oscar Peterson', 'Count Basie'],
    bossa: ['Antonio Carlos Jobim', 'João Gilberto'],
};

export function LicksTool() {
    const piano = usePiano();

    // Basic controls
    const [style, setStyle] = useState<LickStyle>('bebop');
    const [contextType, setContextType] = useState<'chord' | 'progression'>('chord');
    const [context, setContext] = useState('Cm7');
    const [difficulty, setDifficulty] = useState<Difficulty>('intermediate');
    const [length, setLength] = useState(2);

    // Enhanced controls
    const [phrasePosition, setPhrasePosition] = useState<PhrasePosition>('middle');
    const [creativity, setCreativity] = useState<CreativityLevel>('balanced');
    const [styleReference, setStyleReference] = useState<string>('');
    const [generateVariations, setGenerateVariations] = useState(false);

    // Context inputs
    const [precedingChords, setPrecedingChords] = useState<string>('');
    const [followingChord, setFollowingChord] = useState<string>('');
    const [targetNote, setTargetNote] = useState<string>('');

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
            phrase_position: phrasePosition,
            creativity,
            style_reference: styleReference || undefined,
            generate_variations: generateVariations,
            preceding_chords: precedingChords ? precedingChords.split(' ').filter(Boolean) : undefined,
            following_chord: followingChord || undefined,
            target_note: targetNote || undefined,
        });
    };

    const handlePlayLick = async (midiNotes: number[]) => {
        await piano.playScale(midiNotes, 0.2, 0.0, 0.7);
    };

    const availableArtists = STYLE_ARTISTS[style] || [];

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Zap className="w-8 h-8 text-pink-400" />
                        Lick Generator
                    </h2>
                    <p className="text-slate-400">Context-aware phrases for authentic improvisation</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
                    <div className="space-y-4">
                        {/* Style & Difficulty */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Style</label>
                                <select
                                    value={style}
                                    onChange={(e) => {
                                        setStyle(e.target.value as LickStyle);
                                        setStyleReference('');
                                    }}
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
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-pink-500 outline-none"
                                >
                                    <option value="">None</option>
                                    {availableArtists.map(artist => (
                                        <option key={artist} value={artist}>Channel {artist}</option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {/* Context Type & Input */}
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

                        {/* Phrase Position */}
                        <div className="pt-2 border-t border-slate-800">
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                <Music className="w-3 h-3 text-pink-400" />
                                Phrase Position
                            </label>
                            <div className="grid grid-cols-4 gap-1">
                                {PHRASE_POSITIONS.map((pos) => (
                                    <button
                                        key={pos.value}
                                        onClick={() => setPhrasePosition(pos.value)}
                                        className={`px-2 py-1.5 rounded-lg text-xs transition-all ${phrasePosition === pos.value
                                                ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                            }`}
                                        title={pos.description}
                                    >
                                        {pos.icon}
                                    </button>
                                ))}
                            </div>
                            <p className="text-[10px] text-slate-500 mt-1">
                                {PHRASE_POSITIONS.find(p => p.value === phrasePosition)?.description}
                            </p>
                        </div>

                        {/* Creativity Level */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                <Sparkles className="w-3 h-3 text-amber-400" />
                                Creativity
                            </label>
                            <div className="grid grid-cols-4 gap-1">
                                {CREATIVITY_LEVELS.map((level) => (
                                    <button
                                        key={level.value}
                                        onClick={() => setCreativity(level.value)}
                                        className={`px-2 py-1.5 rounded-lg text-xs font-medium transition-all ${creativity === level.value
                                                ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                            }`}
                                    >
                                        {level.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Phrase Context */}
                        <div className="pt-2 border-t border-slate-800">
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                <Target className="w-3 h-3 text-cyan-400" />
                                Phrase Context (Optional)
                            </label>
                            <div className="space-y-2">
                                <div>
                                    <label className="block text-[10px] text-slate-500 mb-1">Preceding Chords</label>
                                    <input
                                        type="text"
                                        value={precedingChords}
                                        onChange={(e) => setPrecedingChords(e.target.value)}
                                        placeholder="Dm7 G7"
                                        className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-2 py-1.5 text-xs focus:border-pink-500 outline-none"
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <label className="block text-[10px] text-slate-500 mb-1">Next Chord</label>
                                        <input
                                            type="text"
                                            value={followingChord}
                                            onChange={(e) => setFollowingChord(e.target.value)}
                                            placeholder="Cmaj7"
                                            className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-2 py-1.5 text-xs focus:border-pink-500 outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] text-slate-500 mb-1">Target Note</label>
                                        <input
                                            type="text"
                                            value={targetNote}
                                            onChange={(e) => setTargetNote(e.target.value)}
                                            placeholder="C4"
                                            className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-2 py-1.5 text-xs focus:border-pink-500 outline-none"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Length */}
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

                        {/* Options */}
                        <div className="pt-2 border-t border-slate-800">
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
                            {/* Context Badge */}
                            {(precedingChords || followingChord || targetNote) && (
                                <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-lg px-4 py-2 flex items-center gap-2 text-sm flex-wrap">
                                    <Target className="w-4 h-4 text-cyan-400" />
                                    <span className="text-cyan-300">Context-aware:</span>
                                    {precedingChords && <span className="text-slate-400">{precedingChords} →</span>}
                                    <span className="text-white font-bold">{context}</span>
                                    {followingChord && <span className="text-slate-400">→ {followingChord}</span>}
                                    {targetNote && <span className="text-pink-400 ml-2">🎯 {targetNote}</span>}
                                </div>
                            )}

                            {result.licks.map((lick, idx) => (
                                <div key={idx} className="bg-slate-800 border border-slate-700 rounded-xl p-4 transition-all hover:border-pink-500/30">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="font-bold text-white text-lg">{lick.name}</h3>
                                            <div className="flex gap-2 mt-1 flex-wrap">
                                                {lick.style_tags.map((tag, i) => (
                                                    <span key={i} className="text-[10px] uppercase tracking-wider bg-slate-900 text-slate-400 px-1.5 py-0.5 rounded">
                                                        {tag}
                                                    </span>
                                                ))}
                                                <span className="text-[10px] uppercase tracking-wider bg-pink-500/10 text-pink-400 px-1.5 py-0.5 rounded">
                                                    {phrasePosition} phrase
                                                </span>
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

                                    {/* Visual Representation */}
                                    <div className="h-24 bg-slate-900/50 rounded-lg border border-slate-800 mb-4 relative overflow-hidden flex items-end px-4 pb-4 gap-1">
                                        {lick.midi_notes.map((note, i) => {
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
                                    <GraduationCap className="w-5 h-5 text-green-400" />
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
                            <p className="text-sm">Create context-aware phrases to expand your vocabulary</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
