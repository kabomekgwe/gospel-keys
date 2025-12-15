import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Music4, Play, Loader2, Download, FileAudio } from 'lucide-react';
import { aiApi, ArrangeResponse } from '../../../lib/api';

const STYLES = ['jazz', 'gospel', 'neo_soul', 'blues', 'classical', 'pop'];
const TIME_SIGNATURES = ['4/4', '3/4', '6/8', '12/8'];

export function ArrangerTool() {
    const [progression, setProgression] = useState('C Am F G');
    const [style, setStyle] = useState('jazz');
    const [tempo, setTempo] = useState(120);
    const [timeSignature, setTimeSignature] = useState('4/4');

    const [result, setResult] = useState<ArrangeResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: aiApi.arrangeProgression,
        onSuccess: (data) => {
            setResult(data);
            setError(null);
        },
        onError: (err) => setError(err.message),
    });

    const handleGenerate = () => {
        mutation.mutate({
            progression: progression.split(' ').filter(Boolean),
            style,
            tempo,
            time_signature: timeSignature,
        });
    };

    const handleDownloadMidi = () => {
        if (!result) return;

        // Convert base64 to blob and download
        const byteCharacters = atob(result.midi_data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'audio/midi' });

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `arrangement-${style}.mid`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Music4 className="w-8 h-8 text-indigo-400" />
                        AI Arranger
                    </h2>
                    <p className="text-slate-400">Convert chord progressions into full two-hand piano performances</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Chord Progression</label>
                            <textarea
                                value={progression}
                                onChange={(e) => setProgression(e.target.value)}
                                placeholder="C Am F G"
                                rows={3}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-indigo-500 outline-none font-mono resize-none"
                            />
                            <p className="text-xs text-slate-500 mt-1">Check your key signature. AI will adapt to the chords provided.</p>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Arrangement Style</label>
                            <select
                                value={style}
                                onChange={(e) => setStyle(e.target.value)}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-indigo-500 outline-none capitalize"
                            >
                                {STYLES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                            </select>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Tempo (BPM)</label>
                                <input
                                    type="number"
                                    value={tempo}
                                    onChange={(e) => setTempo(Number(e.target.value))}
                                    min={40}
                                    max={300}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-indigo-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Time Signature</label>
                                <select
                                    value={timeSignature}
                                    onChange={(e) => setTimeSignature(e.target.value)}
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-indigo-500 outline-none"
                                >
                                    {TIME_SIGNATURES.map(ts => <option key={ts} value={ts}>{ts}</option>)}
                                </select>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={mutation.isPending}
                        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-lg font-medium shadow-lg shadow-indigo-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
                    >
                        {mutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Arranging...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5 fill-current" />
                                Generate Arrangement
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
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-12 h-12 bg-indigo-500/20 rounded-full flex items-center justify-center text-indigo-400">
                                        <FileAudio className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-white">Arrangement Ready</h3>
                                        <p className="text-slate-400 text-sm">{result.description}</p>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-4">
                                    <button
                                        onClick={handleDownloadMidi}
                                        className="w-full sm:w-auto px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
                                    >
                                        <Download className="w-5 h-5" />
                                        Download MIDI File
                                    </button>

                                    <div className="mt-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800 text-sm text-slate-400">
                                        <p className="mb-2 font-medium text-slate-300">Features included in this {result.style} arrangement:</p>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li>Note-for-note piano performance</li>
                                            <li>Stylistically appropriate voicings</li>
                                            <li>Rhythmic patterns and comping</li>
                                            <li>Voice leading optimizations</li>
                                        </ul>
                                    </div>


                                    <div className="mt-2 text-xs text-slate-500 text-center">
                                        Import the downloaded MIDI file into your DAW (Logic, Ableton, GarageBand) to hear it played with high-quality instruments.
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-8">
                            <Music4 className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">Create Full Arrangements</p>
                            <p className="text-sm text-center max-w-md mt-2">
                                Turn your chord progression into a complete piano performance in seconds.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
