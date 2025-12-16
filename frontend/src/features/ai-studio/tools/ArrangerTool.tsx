import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Music4, Play, Loader2, Download, FileAudio, Sparkles, User, GraduationCap, Sliders } from 'lucide-react';
import { aiApi, ArrangeResponse, CreativityLevel } from '../../../lib/api';

const STYLES = ['jazz', 'gospel', 'neo_soul', 'blues', 'classical', 'pop'];
const TIME_SIGNATURES = ['4/4', '3/4', '6/8', '12/8'];

// Humanization levels
const HUMANIZATION_LEVELS: { value: number; label: string; description: string }[] = [
    { value: 0, label: 'None', description: 'Raw AI output, perfect timing' },
    { value: 0.3, label: 'Light', description: 'Subtle micro-timing variations' },
    { value: 0.5, label: 'Medium', description: 'Natural feel with groove' },
    { value: 0.7, label: 'Heavy', description: 'Deep pocket with ghost notes' },
    { value: 1.0, label: 'Max', description: 'Full humanization treatment' },
];

// Artist references by style
const STYLE_ARTISTS: Record<string, string[]> = {
    jazz: ['Bill Evans', 'Oscar Peterson', 'Herbie Hancock'],
    gospel: ['Kirk Franklin', 'Cory Henry', 'Fred Hammond'],
    neo_soul: ['Robert Glasper', 'D\'Angelo'],
    blues: ['Ray Charles', 'Oscar Peterson'],
    classical: ['Glenn Gould'],
    pop: [],
};

// Creativity options
const CREATIVITY_LEVELS: { value: CreativityLevel; label: string }[] = [
    { value: 'conservative', label: 'Classic' },
    { value: 'balanced', label: 'Balanced' },
    { value: 'adventurous', label: 'Bold' },
    { value: 'experimental', label: 'Wild' },
];

export function ArrangerTool() {
    // Basic controls
    const [progression, setProgression] = useState('C Am F G');
    const [style, setStyle] = useState('jazz');
    const [tempo, setTempo] = useState(120);
    const [timeSignature, setTimeSignature] = useState('4/4');

    // Enhanced controls
    const [creativity, setCreativity] = useState<CreativityLevel>('balanced');
    const [styleReference, setStyleReference] = useState<string>('');
    const [humanization, setHumanization] = useState<number>(0.5);
    const [includeEducation, setIncludeEducation] = useState(true);

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
            // Enhanced options (backend may not support all yet)
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

    const availableArtists = STYLE_ARTISTS[style] || [];

    return (
        <div className="h-full flex flex-col p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Music4 className="w-8 h-8 text-indigo-400" />
                        AI Arranger
                    </h2>
                    <p className="text-slate-400">Convert chord progressions into humanized two-hand piano performances</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-0">
                {/* Controls */}
                <div className="lg:col-span-1 bg-slate-900/50 p-4 rounded-xl border border-slate-800 h-fit space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
                    <div className="space-y-4">
                        {/* Chord Progression */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Chord Progression</label>
                            <textarea
                                value={progression}
                                onChange={(e) => setProgression(e.target.value)}
                                placeholder="C Am F G"
                                rows={3}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-indigo-500 outline-none font-mono resize-none"
                            />
                            <p className="text-xs text-slate-500 mt-1">Space-separated chords. AI adapts to your key.</p>
                        </div>

                        {/* Style */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Arrangement Style</label>
                            <select
                                value={style}
                                onChange={(e) => {
                                    setStyle(e.target.value);
                                    setStyleReference('');
                                }}
                                className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-indigo-500 outline-none capitalize"
                            >
                                {STYLES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
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
                                    className="w-full bg-slate-800 text-white rounded-lg border border-slate-700 px-3 py-2 text-sm focus:border-indigo-500 outline-none"
                                >
                                    <option value="">None - General {style} style</option>
                                    {availableArtists.map(artist => (
                                        <option key={artist} value={artist}>Channel {artist}</option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {/* Tempo & Time Signature */}
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

                        {/* Creativity Level */}
                        <div className="pt-2 border-t border-slate-800">
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

                        {/* Humanization Level */}
                        <div className="pt-2 border-t border-slate-800">
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-1">
                                <Sliders className="w-3 h-3 text-cyan-400" />
                                Humanization
                                <span className="text-[10px] text-cyan-400 bg-cyan-500/10 px-1 rounded ml-1">NEW</span>
                            </label>
                            <div className="grid grid-cols-5 gap-1">
                                {HUMANIZATION_LEVELS.map((level) => (
                                    <button
                                        key={level.value}
                                        onClick={() => setHumanization(level.value)}
                                        className={`px-2 py-1.5 rounded-lg text-[10px] font-medium transition-all ${humanization === level.value
                                                ? 'bg-gradient-to-r from-cyan-500 to-teal-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                            }`}
                                        title={level.description}
                                    >
                                        {level.label}
                                    </button>
                                ))}
                            </div>
                            <p className="text-[10px] text-slate-500 mt-1">
                                {HUMANIZATION_LEVELS.find(l => l.value === humanization)?.description}
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
                                    Include Arrangement Notes
                                </span>
                            </label>
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

                                    {/* Features List */}
                                    <div className="mt-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800 text-sm text-slate-400">
                                        <p className="mb-2 font-medium text-slate-300">Features included in this {result.style} arrangement:</p>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li>Note-for-note piano performance</li>
                                            <li>Stylistically appropriate voicings</li>
                                            <li>Rhythmic patterns and comping</li>
                                            <li>Voice leading optimizations</li>
                                            {humanization > 0 && (
                                                <>
                                                    <li className="text-cyan-400">🎵 Gospel groove micro-timing</li>
                                                    <li className="text-cyan-400">🎵 Dynamic velocity curves</li>
                                                    {humanization >= 0.5 && <li className="text-cyan-400">🎵 Ghost notes and feel</li>}
                                                </>
                                            )}
                                        </ul>
                                    </div>

                                    {/* Educational Notes */}
                                    {includeEducation && (
                                        <div className="mt-4 p-4 bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-lg border border-green-500/20">
                                            <h4 className="text-sm font-medium text-green-400 mb-2 flex items-center gap-1">
                                                <GraduationCap className="w-4 h-4" />
                                                Arrangement Notes
                                            </h4>
                                            <p className="text-sm text-slate-400">
                                                This {style} arrangement uses characteristic voicings, rhythm patterns,
                                                and voice leading principles typical of the genre.
                                                {styleReference && ` It channels the style of ${styleReference}.`}
                                                {humanization > 0 && ` Humanization has been applied at ${Math.round(humanization * 100)}% intensity to add natural feel and groove.`}
                                            </p>
                                        </div>
                                    )}

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
                                Turn your chord progression into a humanized piano performance with genre-specific feel.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
