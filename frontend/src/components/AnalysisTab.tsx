import { BarChart2, Music, Zap, Info, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { analysisApi, type ChordRegion } from '../lib/api';

interface AnalysisTabProps {
    songId: string;
    detectedChords: ChordRegion[];
    totalNotes: number;
}


const Card = ({ title, value, icon: Icon, color }: { title: string, value: string | number, icon: React.ElementType, color: string }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-6 flex items-start gap-4"
    >
        <div className={`p-3 rounded-xl bg-${color}-500/20`}>
            <Icon className={`w-6 h-6 text-${color}-400`} />
        </div>
        <div>
            <h4 className="text-slate-400 mb-1">{title}</h4>
            <p className="text-2xl font-bold text-white">{value}</p>
        </div>
    </motion.div>
);

export function AnalysisTab({ songId, detectedChords, totalNotes }: AnalysisTabProps) {
    // Fetch genre analysis from API
    const { data: genreData, isLoading: genreLoading } = useQuery({
        queryKey: ['analysis', 'genre', songId],
        queryFn: () => analysisApi.getGenre(songId),
        enabled: !!songId,
    });

    // Fetch jazz patterns from API
    const { data: jazzData, isLoading: jazzLoading } = useQuery({
        queryKey: ['analysis', 'jazz', songId],
        queryFn: () => analysisApi.getJazzPatterns(songId),
        enabled: !!songId,
    });

    // Calculate unique notes from chords
    const uniqueNotes = new Set(
        detectedChords.flatMap(c => c.chord ? [c.chord] : [])
    ).size;

    return (
        <div className="p-6 overflow-y-auto h-full">
            <div className="max-w-5xl mx-auto space-y-8">
                <header>
                    <h2 className="text-2xl font-bold text-white mb-2">Song Analysis</h2>
                    <p className="text-slate-400 flex items-center gap-2">
                        <Info className="w-4 h-4" />
                        Advanced harmonic analysis powered by backend AI.
                    </p>
                </header>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card title="Total Notes" value={totalNotes} icon={Music} color="cyan" />
                    <Card title="Unique Pitch Classes" value={uniqueNotes} icon={BarChart2} color="violet" />
                    <Card title="Detected Chords" value={detectedChords.length} icon={Zap} color="amber" />
                </div>

                {/* Genre Analysis */}
                {genreLoading ? (
                    <div className="card p-6">
                        <div className="text-center py-8">
                            <div className="w-8 h-8 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4" />
                            <p className="text-slate-400">Analyzing genre...</p>
                        </div>
                    </div>
                ) : genreData ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="card p-6"
                    >
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-emerald-400" />
                            Genre Classification
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-slate-300 capitalize">{genreData.primary_genre}</span>
                                    <span className="text-emerald-400 font-bold">
                                        {(genreData.confidence * 100).toFixed(1)}%
                                    </span>
                                </div>
                                <div className="w-full bg-slate-700 rounded-full h-3">
                                    <div
                                        className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-3 rounded-full transition-all"
                                        style={{ width: `${genreData.confidence * 100}%` }}
                                    />
                                </div>
                            </div>
                            {genreData.subgenres && genreData.subgenres.length > 0 && (
                                <div className="flex flex-wrap gap-2 mt-4">
                                    {genreData.subgenres.map((sub: string, i: number) => (
                                        <span
                                            key={i}
                                            className="px-3 py-1 bg-slate-700 text-slate-300 rounded-full text-sm"
                                        >
                                            {sub}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </motion.div>
                ) : null}

                {/* Jazz Pattern Analysis */}
                {jazzLoading ? (
                    <div className="card p-6">
                        <div className="text-center py-8">
                            <div className="w-8 h-8 border-4 border-violet-500/30 border-t-violet-500 rounded-full animate-spin mx-auto mb-4" />
                            <p className="text-slate-400">Detecting jazz patterns...</p>
                        </div>
                    </div>
                ) : jazzData && jazzData.total_patterns > 0 ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="card p-6"
                    >
                        <h3 className="text-lg font-semibold text-white mb-4">Jazz Patterns Detected</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                            <div className="bg-slate-800/50 p-4 rounded-lg">
                                <p className="text-slate-400 text-sm mb-1">ii-V-I Progressions</p>
                                <p className="text-2xl font-bold text-cyan-400">
                                    {jazzData.ii_v_i_progressions?.length || 0}
                                </p>
                            </div>
                            <div className="bg-slate-800/50 p-4 rounded-lg">
                                <p className="text-slate-400 text-sm mb-1">Turnarounds</p>
                                <p className="text-2xl font-bold text-violet-400">
                                    {jazzData.turnarounds?.length || 0}
                                </p>
                            </div>
                            <div className="bg-slate-800/50 p-4 rounded-lg">
                                <p className="text-slate-400 text-sm mb-1">Jazz Complexity</p>
                                <p className="text-2xl font-bold text-amber-400">
                                    {(jazzData.jazz_complexity_score * 100).toFixed(0)}%
                                </p>
                            </div>
                        </div>

                        {/* Pattern Timeline */}
                        {jazzData.ii_v_i_progressions && jazzData.ii_v_i_progressions.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-slate-300 mb-3">ii-V-I Timeline</h4>
                                <div className="space-y-2">
                                    {jazzData.ii_v_i_progressions.map((pattern, i) => (
                                        <div
                                            key={i}
                                            className="flex items-center gap-3 bg-slate-800/30 p-3 rounded-lg hover:bg-slate-800/50 transition-colors"
                                        >
                                            <div className="flex-shrink-0 w-16 text-sm text-slate-400">
                                                {pattern.start_time?.toFixed(1)}s
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-cyan-400 font-mono text-sm">
                                                        {pattern.key || 'Unknown Key'}
                                                    </span>
                                                    <span className="text-slate-500">•</span>
                                                    <span className="text-slate-300 text-sm">
                                                        Duration: {pattern.duration?.toFixed(1)}s
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="flex-shrink-0">
                                                <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded">
                                                    {((pattern.confidence || 0.9) * 100).toFixed(0)}% confident
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </motion.div>
                ) : null}

                {/* Chord Progression Timeline */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="card p-6"
                >
                    <h3 className="text-lg font-semibold text-white mb-4">Chord Progression Timeline</h3>
                    {detectedChords.length > 0 ? (
                        <div className="relative pt-6 pb-2 overflow-x-auto">
                            <div className="flex gap-1 min-w-full">
                                {detectedChords.map((chord, index) => (
                                    <div
                                        key={index}
                                        className="flex-shrink-0 flex flex-col items-center group relative cursor-help"
                                        style={{ width: Math.max(60, (chord.endTime - chord.startTime) * 40) }}
                                    >
                                        <div className="w-full h-8 bg-slate-800 rounded-lg mb-2 overflow-hidden relative">
                                            <div className="absolute inset-0 bg-violet-500/20 group-hover:bg-violet-500/30 transition-colors" />
                                        </div>
                                        <span className="font-mono font-bold text-violet-400 text-sm whitespace-nowrap">
                                            {chord.chord}
                                        </span>
                                        <span className="text-[10px] text-slate-500 mt-1">
                                            {chord.startTime.toFixed(1)}s
                                        </span>

                                        {/* Tooltip */}
                                        <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block z-10 bg-black/90 text-xs p-2 rounded whitespace-nowrap border border-slate-700">
                                            {chord.romanNumeral && (
                                                <>
                                                    Roman: {chord.romanNumeral} <br />
                                                </>
                                            )}
                                            Duration: {(chord.endTime - chord.startTime).toFixed(2)}s
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-12 bg-slate-800/30 rounded-xl border border-dashed border-slate-700">
                            <p className="text-slate-400">
                                No chords detected. Try uploading a song with chord progression.
                            </p>
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
