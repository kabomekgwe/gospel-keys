import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Layers, Play, Loader2, Volume2, ArrowRight } from 'lucide-react';
import { aiApi, VoicingStyle, VoicingResponse, VoiceLeadingResponse } from '../../../lib/api';
import { VoicingVisualizer } from '../../../components/analysis/VoicingVisualizer';
import { convertToVoicingAnalysisInfo } from '../utils';

interface VoicingToolProps {
    onPlayChord: (midiNotes: number[]) => void;
}

const VOICING_STYLES: VoicingStyle[] = ['open', 'closed', 'drop2', 'drop3', 'rootless', 'spread', 'gospel'];

type Mode = 'voicing' | 'voice_leading';

export function VoicingTool({ onPlayChord }: VoicingToolProps) {
    const [mode, setMode] = useState<Mode>('voicing');

    // Voicing Form
    const [chord, setChord] = useState('Cmaj7');
    const [style, setStyle] = useState<VoicingStyle>('open');

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
            });
        } else {
            voiceLeadingMutation.mutate({
                chord1,
                chord2,
                style: 'jazz', // Default style for voice leading
            });
        }
    };

    const isLoading = voicingMutation.isPending || voiceLeadingMutation.isPending;

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Layers className="w-8 h-8 text-violet-400" />
                        Voicing Architect
                    </h2>
                    <p className="text-slate-400">Master chord voicings and voice leading</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-6">
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
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Voicing Style</label>
                                    <select
                                        value={style}
                                        onChange={(e) => setStyle(e.target.value as VoicingStyle)}
                                        className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-violet-500 outline-none capitalize"
                                    >
                                        {VOICING_STYLES.map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
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
                        </div>
                    )}

                    {!voicingResult && !voiceLeadingResult && (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Layers className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Explore Voicings</p>
                            <p className="text-sm">Generate beautiful chord voicings or optimize voice leading</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
