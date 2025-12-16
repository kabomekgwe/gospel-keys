import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Layers, Play, Loader2, Volume2, ArrowRight, Heart, Zap, Music, GraduationCap, User } from 'lucide-react';
import { aiApi, VoicingStyle, VoicingResponse, VoiceLeadingResponse, Emotion } from '../../../lib/api';
import { VoicingVisualizer } from '../../../components/analysis/VoicingVisualizer';
import { convertToVoicingAnalysisInfo } from '../utils';

interface VoicingToolProps {
    onPlayChord: (midiNotes: number[]) => void;
}

const VOICING_STYLES: VoicingStyle[] = ['open', 'closed', 'drop2', 'drop3', 'rootless', 'spread', 'gospel'];

// Emotional colors for voicings
const EMOTIONS: { value: Emotion; label: string; icon: string; description: string }[] = [
    { value: 'neutral', label: 'Neutral', icon: '⚪', description: 'Balanced, standard voicing' },
    { value: 'warm', label: 'Warm', icon: '🔥', description: 'Rich, close intervals' },
    { value: 'bright', label: 'Bright', icon: '☀️', description: 'Open, upper extensions' },
    { value: 'dark', label: 'Dark', icon: '🌙', description: 'Low register, minor colors' },
    { value: 'tense', label: 'Tense', icon: '⚡', description: 'Dissonant, unresolved' },
    { value: 'ethereal', label: 'Ethereal', icon: '✨', description: 'Spacious, otherworldly' },
    { value: 'powerful', label: 'Powerful', icon: '💪', description: 'Full, dense voicing' },
    { value: 'intimate', label: 'Intimate', icon: '💜', description: 'Soft, close voicing' },
];

// Artist references by style
const STYLE_ARTISTS: Record<string, string[]> = {
    open: ['Bill Evans', 'Ahmad Jamal'],
    closed: ['Oscar Peterson', 'Red Garland'],
    drop2: ['Wes Montgomery', 'Joe Pass'],
    drop3: ['Barry Harris', 'Hank Jones'],
    rootless: ['Herbie Hancock', 'McCoy Tyner'],
    spread: ['Chick Corea', 'Keith Jarrett'],
    gospel: ['Cory Henry', 'Kirk Franklin'],
};

type Mode = 'voicing' | 'voice_leading';

export function VoicingTool({ onPlayChord }: VoicingToolProps) {
    const [mode, setMode] = useState<Mode>('voicing');

    // Voicing Form
    const [chord, setChord] = useState('Cmaj7');
    const [style, setStyle] = useState<VoicingStyle>('open');
    const [emotion, setEmotion] = useState<Emotion>('neutral');
    const [styleReference, setStyleReference] = useState<string>('');
    const [includeEducation, setIncludeEducation] = useState(true);

    // Context for voice leading
    const [previousChord, setPreviousChord] = useState<string>('');
    const [nextChord, setNextChord] = useState<string>('');

    // Voice Leading Form
    const [chord1, setChord1] = useState('Dm7');
    const [chord2, setChord2] = useState('G7');

    // Results
    const [voicingResult, setVoicingResult] = useState<VoicingResponse | null>(null);
    const [voiceLeadingResult, setVoiceLeadingResult] = useState<VoiceLeadingResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const voicingMutation = useMutation({
        mutationFn: aiApi.generateVoicing,
        onSuccess: (data) => {
            setVoicingResult(data);
            setVoiceLeadingResult(null);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const voiceLeadingMutation = useMutation({
        mutationFn: aiApi.optimizeVoiceLeading,
        onSuccess: (data) => {
            setVoiceLeadingResult(data);
            setVoicingResult(null);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        if (mode === 'voicing') {
            voicingMutation.mutate({
                chord,
                style,
                hand: 'both',
                include_fingering: true,
                emotion,
                previous_chord: previousChord || undefined,
                next_chord: nextChord || undefined,
                style_reference: styleReference || undefined,
                include_education: includeEducation,
            });
        } else {
            voiceLeadingMutation.mutate({
                chord1,
                chord2,
                style: 'jazz',
            });
        }
    };

    const isLoading = voicingMutation.isPending || voiceLeadingMutation.isPending;
    const availableArtists = STYLE_ARTISTS[style] || [];

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Layers className="w-8 h-8 text-violet-400" />
                        Voicing Architect
                    </h2>
                    <p className="text-slate-400">Context-aware chord voicings with emotional intelligence</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-6 overflow-y-auto max-h-[calc(100vh-200px)]">
                    {/* Mode Switch */}
                    <div className="flex bg-slate-800 rounded-lg p-1">
                        <button
                            onClick={() => setMode('voicing')}
                            className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${mode === 'voicing' ? 'bg-violet-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                        >
                            Chord Voicings
                        </button>
                        <button
                            onClick={() => setMode('voice_leading')}
                            className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${mode === 'voice_leading' ? 'bg-violet-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                        >
                            Voice Leading
                        </button>
                    </div>

                    <div className="space-y-4">
                        {mode === 'voicing' ? (
                            <>
                                {/* Chord Symbol */}
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Chord Symbol</label>
                                    <input
                                        type="text"
                                        value={chord}
                                        onChange={(e) => setChord(e.target.value)}
                                        placeholder="Cmaj7"
                                        className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-violet-500 outline-none"
                                    />
                                </div>

                                {/* Voicing Style */}
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Voicing Style</label>
                                    <select
                                        value={style}
                                        onChange={(e) => {
                                            setStyle(e.target.value as VoicingStyle);
                                            setStyleReference('');
                                        }}
                                        className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-violet-500 outline-none capitalize"
                                    >
                                        {VOICING_STYLES.map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
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
                                            className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-violet-500 outline-none"
                                        >
                                            <option value="">None</option>
                                            {availableArtists.map(artist => (
                                                <option key={artist} value={artist}>{artist}</option>
                                            ))}
                                        </select>
                                    </div>
                                )}

                                {/* Emotional Color */}
                                <div className="pt-2 border-t border-slate-800">
                                    <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                        <Heart className="w-3 h-3 text-pink-400" />
                                        Emotional Color
                                    </label>
                                    <div className="grid grid-cols-4 gap-1">
                                        {EMOTIONS.map((e) => (
                                            <button
                                                key={e.value}
                                                onClick={() => setEmotion(e.value)}
                                                className={`px-2 py-1.5 rounded-lg text-xs transition-all ${emotion === e.value
                                                    ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white'
                                                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                                    }`}
                                                title={e.description}
                                            >
                                                {e.icon}
                                            </button>
                                        ))}
                                    </div>
                                    <p className="text-[10px] text-slate-500 mt-1">
                                        {EMOTIONS.find(e => e.value === emotion)?.description}
                                    </p>
                                </div>

                                {/* Voice Leading Context */}
                                <div className="pt-2 border-t border-slate-800">
                                    <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                        <Zap className="w-3 h-3 text-amber-400" />
                                        Voice Leading Context (Optional)
                                    </label>
                                    <div className="grid grid-cols-2 gap-2">
                                        <div>
                                            <label className="block text-[10px] text-slate-500 mb-1">Previous Chord</label>
                                            <input
                                                type="text"
                                                value={previousChord}
                                                onChange={(e) => setPreviousChord(e.target.value)}
                                                placeholder="Am7"
                                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-2 py-1.5 text-xs focus:border-violet-500 outline-none"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-[10px] text-slate-500 mb-1">Next Chord</label>
                                            <input
                                                type="text"
                                                value={nextChord}
                                                onChange={(e) => setNextChord(e.target.value)}
                                                placeholder="G7"
                                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-2 py-1.5 text-xs focus:border-violet-500 outline-none"
                                            />
                                        </div>
                                    </div>
                                    <p className="text-[10px] text-slate-500 mt-1">
                                        Provide context for optimal voice leading
                                    </p>
                                </div>

                                {/* Options */}
                                <div className="pt-2 border-t border-slate-800">
                                    <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer p-2 hover:bg-slate-800/50 rounded-lg transition-colors">
                                        <input
                                            type="checkbox"
                                            checked={includeEducation}
                                            onChange={(e) => setIncludeEducation(e.target.checked)}
                                            className="rounded border-slate-600 text-green-500 focus:ring-offset-slate-900 focus:ring-green-500"
                                        />
                                        <span className="flex items-center gap-1">
                                            <GraduationCap className="w-3 h-3" />
                                            Include Voice Leading Analysis
                                        </span>
                                    </label>
                                </div>
                            </>
                        ) : (
                            <>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">From Chord</label>
                                    <input
                                        type="text"
                                        value={chord1}
                                        onChange={(e) => setChord1(e.target.value)}
                                        placeholder="Dm7"
                                        className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-violet-500 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">To Chord</label>
                                    <input
                                        type="text"
                                        value={chord2}
                                        onChange={(e) => setChord2(e.target.value)}
                                        placeholder="G7"
                                        className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-violet-500 outline-none"
                                    />
                                </div>
                            </>
                        )}
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={isLoading}
                        className="w-full py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white rounded-lg font-medium shadow-lg shadow-violet-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Calculating...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5 fill-current" />
                                {mode === 'voicing' ? 'Generate Voicings' : 'Optimize Leading'}
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
                    {mode === 'voicing' && voicingResult && (
                        <div className="space-y-6">
                            {/* Context Badge */}
                            {(previousChord || nextChord) && (
                                <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2 flex items-center gap-2 text-sm">
                                    <Zap className="w-4 h-4 text-amber-400" />
                                    <span className="text-amber-300">Context-aware voicing:</span>
                                    {previousChord && <span className="text-slate-400">{previousChord} →</span>}
                                    <span className="text-white font-bold">{chord}</span>
                                    {nextChord && <span className="text-slate-400">→ {nextChord}</span>}
                                </div>
                            )}

                            {/* Voicings Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {voicingResult.voicings.map((voicing, idx) => (
                                    <div key={idx} className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                                        <div className="flex justify-between items-center mb-4">
                                            <h3 className="font-semibold text-white">{voicing.name}</h3>
                                            <button
                                                onClick={() => onPlayChord(voicing.midi_notes)}
                                                className="p-2 bg-violet-600/20 text-violet-400 rounded hover:bg-violet-600 hover:text-white transition-colors"
                                            >
                                                <Volume2 className="w-4 h-4" />
                                            </button>
                                        </div>

                                        <div className="h-48">
                                            <VoicingVisualizer
                                                chord={voicingResult.chord}
                                                voicing={convertToVoicingAnalysisInfo(voicing, voicingResult.chord)}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Voice Leading Analysis */}
                            {voicingResult.voice_leading_analysis && (
                                <div className="bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 border border-violet-500/20 rounded-xl p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                        <Music className="w-5 h-5 text-violet-400" />
                                        Voice Leading Analysis
                                    </h3>
                                    <div className="space-y-3">
                                        {voicingResult.voice_leading_analysis.common_tones.length > 0 && (
                                            <div className="flex items-start gap-3">
                                                <span className="text-slate-400 text-sm w-28">Common Tones:</span>
                                                <span className="text-white text-sm">
                                                    {voicingResult.voice_leading_analysis.common_tones.join(', ')}
                                                </span>
                                            </div>
                                        )}
                                        {voicingResult.voice_leading_analysis.voice_movements.map((movement, i) => (
                                            <div key={i} className="flex items-start gap-3">
                                                <span className="text-slate-400 text-sm w-28">Voice {i + 1}:</span>
                                                <span className="text-slate-300 text-sm">{movement}</span>
                                            </div>
                                        ))}
                                        <div className="flex items-center gap-3 pt-2 border-t border-slate-700/50">
                                            <span className="text-slate-400 text-sm w-28">Smoothness:</span>
                                            <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500"
                                                    style={{ width: `${voicingResult.voice_leading_analysis.smoothness_score * 100}%` }}
                                                />
                                            </div>
                                            <span className="text-white text-sm font-medium">
                                                {Math.round(voicingResult.voice_leading_analysis.smoothness_score * 100)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Educational Content */}
                            {voicingResult.education && (
                                <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                        <GraduationCap className="w-5 h-5 text-green-400" />
                                        Learn About This Voicing
                                    </h3>

                                    {voicingResult.education.why_it_works && (
                                        <div className="mb-4">
                                            <p className="text-sm text-slate-300 leading-relaxed">
                                                {voicingResult.education.why_it_works}
                                            </p>
                                        </div>
                                    )}

                                    {voicingResult.education.theory_concepts && voicingResult.education.theory_concepts.length > 0 && (
                                        <div className="flex flex-wrap gap-2">
                                            {voicingResult.education.theory_concepts.map((concept, i) => (
                                                <span key={i} className="px-2 py-1 bg-green-500/10 text-green-300 text-xs rounded-full">
                                                    {concept}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Tips */}
                            {voicingResult.tips && voicingResult.tips.length > 0 && (
                                <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4">Performance Tips</h3>
                                    <ul className="grid gap-2">
                                        {voicingResult.tips.map((tip, i) => (
                                            <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                                                <span className="mt-1.5 w-1 h-1 bg-violet-500 rounded-full shrink-0" />
                                                {tip}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    {mode === 'voice_leading' && voiceLeadingResult && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-center gap-4 mb-8">
                                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 w-full max-w-sm">
                                    <div className="flex justify-between items-center mb-2">
                                        <div className="font-bold text-white">{chord1}</div>
                                        <button onClick={() => onPlayChord(voiceLeadingResult.chord1.midi_notes)}>
                                            <Volume2 className="w-4 h-4 text-violet-400" />
                                        </button>
                                    </div>
                                    <div className="text-sm text-slate-400 font-mono mb-2">
                                        {voiceLeadingResult.chord1.notes.join(' - ')}
                                    </div>
                                    <div className="h-32">
                                        <VoicingVisualizer
                                            chord={chord1}
                                            voicing={convertToVoicingAnalysisInfo(voiceLeadingResult.chord1, chord1)}
                                            compact
                                        />
                                    </div>
                                </div>

                                <ArrowRight className="w-8 h-8 text-slate-600 shrink-0" />

                                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 w-full max-w-sm">
                                    <div className="flex justify-between items-center mb-2">
                                        <div className="font-bold text-white">{chord2}</div>
                                        <button onClick={() => onPlayChord(voiceLeadingResult.chord2.midi_notes)}>
                                            <Volume2 className="w-4 h-4 text-violet-400" />
                                        </button>
                                    </div>
                                    <div className="text-sm text-slate-400 font-mono mb-2">
                                        {voiceLeadingResult.chord2.notes.join(' - ')}
                                    </div>
                                    <div className="h-32">
                                        <VoicingVisualizer
                                            chord={chord2}
                                            voicing={convertToVoicingAnalysisInfo(voiceLeadingResult.chord2, chord2)}
                                            compact
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6">
                                <h3 className="text-lg font-semibold text-white mb-4">Voice Leading Analysis</h3>
                                <div className="space-y-4">
                                    <div className="flex items-start gap-3">
                                        <div className="mt-1 w-1.5 h-1.5 bg-violet-500 rounded-full shrink-0" />
                                        <div>
                                            <span className="text-slate-300 font-medium">Movement: </span>
                                            <span className="text-slate-400">{voiceLeadingResult.movement}</span>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-3">
                                        <div className="mt-1 w-1.5 h-1.5 bg-violet-500 rounded-full shrink-0" />
                                        <div>
                                            <span className="text-slate-300 font-medium">Common Tones: </span>
                                            <span className="text-slate-400">
                                                {voiceLeadingResult.common_tones.length > 0
                                                    ? voiceLeadingResult.common_tones.join(', ')
                                                    : 'None'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Educational Content for Voice Leading */}
                            {voiceLeadingResult.education && (
                                <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-xl p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                        <GraduationCap className="w-5 h-5 text-green-400" />
                                        Why This Voice Leading Works
                                    </h3>
                                    <p className="text-sm text-slate-300 leading-relaxed">
                                        {voiceLeadingResult.education.why_it_works}
                                    </p>
                                </div>
                            )}
                        </div>
                    )}

                    {!voicingResult && !voiceLeadingResult && (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Layers className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Explore Voicings</p>
                            <p className="text-sm">Generate context-aware voicings or optimize voice leading</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
