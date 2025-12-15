import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Music2, Mic2, AlertCircle, Loader2, Zap, Layers } from 'lucide-react';
import { analysisApi, type GenreAnalysis, type JazzPatternsResult, type PitchAnalysisResult, type ChordRegion } from '../../lib/api';
import { GenreRadar } from './GenreRadar';
import { MelodyContour } from './MelodyContour';
import { VoicingsDisplay } from './VoicingsDisplay';

interface AnalysisOverviewProps {
    songId: string;
    detectedChords?: ChordRegion[];
}

export function AnalysisOverview({ songId, detectedChords = [] }: AnalysisOverviewProps) {
    const [selectedView, setSelectedView] = useState<'genre' | 'melody' | 'jazz' | 'chords' | 'voicings'>('genre');

    // Fetch Genre Analysis
    const {
        data: genreData,
        isLoading: isGenreLoading,
        error: genreError
    } = useQuery({
        queryKey: ['analysis', 'genre', songId],
        queryFn: () => analysisApi.getGenre(songId),
        retry: false
    });

    // Fetch Melody Analysis (Pitch Tracking)
    const {
        data: melodyData,
        isLoading: isMelodyLoading
    } = useQuery({
        queryKey: ['analysis', 'melody', songId],
        queryFn: () => analysisApi.getPitchTracking(songId),
        enabled: selectedView === 'melody',
        staleTime: Infinity
    });

    // Fetch Jazz Patterns
    const {
        data: jazzData,
        isLoading: isJazzLoading
    } = useQuery({
        queryKey: ['analysis', 'jazz', songId],
        queryFn: () => analysisApi.getJazzPatterns(songId),
        enabled: selectedView === 'jazz',
        staleTime: Infinity
    });

    return (
        <div className="space-y-6">
            {/* Navigation Tabs */}
            <div className="flex space-x-2 bg-slate-900/50 p-1 rounded-lg w-fit">
                <TabButton
                    active={selectedView === 'genre'}
                    onClick={() => setSelectedView('genre')}
                    icon={<Activity className="w-4 h-4" />}
                    label="Genre DNA"
                />
                <TabButton
                    active={selectedView === 'melody'}
                    onClick={() => setSelectedView('melody')}
                    icon={<Mic2 className="w-4 h-4" />}
                    label="Melody Contour"
                />
                <TabButton
                    active={selectedView === 'jazz'}
                    onClick={() => setSelectedView('jazz')}
                    icon={<Music2 className="w-4 h-4" />}
                    label="Jazz Patterns"
                />
                <TabButton
                    active={selectedView === 'chords'}
                    onClick={() => setSelectedView('chords')}
                    icon={<Zap className="w-4 h-4" />}
                    label="Chords"
                />
                <TabButton
                    active={selectedView === 'voicings'}
                    onClick={() => setSelectedView('voicings')}
                    icon={<Layers className="w-4 h-4" />}
                    label="Voicings"
                />
            </div>

            {/* Content Area */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6 min-h-[400px]">
                <AnimatePresence mode="wait">
                    {/* GENRE VIEW */}
                    {selectedView === 'genre' && (
                        <motion.div
                            key="genre"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="h-full"
                        >
                            {isGenreLoading ? (
                                <LoadingState message="Analyzing genre characteristics..." />
                            ) : genreError ? (
                                <ErrorState message="Could not load genre analysis. Ensure audio is processed." />
                            ) : genreData ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div>
                                        <h3 className="text-lg font-semibold text-white mb-2">Genre Classification</h3>
                                        <p className="text-slate-400 text-sm mb-6">
                                            Primary breakdown of detected musical styles and harmonic characteristics.
                                        </p>
                                        <GenreRadar analysis={genreData} />
                                    </div>
                                    <div className="space-y-6">
                                        <StatCard
                                            label="Primary Genre"
                                            value={genreData.primary_genre}
                                            subValue={`${(genreData.confidence * 100).toFixed(0)}% Confidence`}
                                            color="cyan"
                                        />
                                        <StatCard
                                            label="Tempo"
                                            value={`${Math.round(genreData.tempo)} BPM`}
                                            subValue="Estimated"
                                            color="emerald"
                                        />
                                        <div>
                                            <div className="text-sm text-slate-500 mb-2">Detected Subgenres</div>
                                            <div className="flex flex-wrap gap-2">
                                                {genreData.subgenres.map(s => (
                                                    <span key={s} className="px-3 py-1 bg-slate-700 rounded-full text-xs text-slate-300 border border-slate-600">
                                                        {s}
                                                    </span>
                                                ))}
                                                {genreData.subgenres.length === 0 && (
                                                    <span className="text-slate-500 text-sm italic">None detected</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ) : null}
                        </motion.div>
                    )}

                    {/* MELODY VIEW */}
                    {selectedView === 'melody' && (
                        <motion.div
                            key="melody"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                        >
                            {isMelodyLoading ? (
                                <LoadingState message="Extracting pitch contour..." />
                            ) : melodyData ? (
                                <div>
                                    <div className="flex justify-between items-end mb-6">
                                        <div>
                                            <h3 className="text-lg font-semibold text-white">Melody Analysis</h3>
                                            <p className="text-slate-400 text-sm">
                                                Pitch tracking using CREPE neural network.
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-2xl font-bold text-emerald-400">
                                                {melodyData.total_frames > 0 ? 'Active' : 'Silent'}
                                            </div>
                                            <div className="text-xs text-slate-500">Status</div>
                                        </div>
                                    </div>
                                    <MelodyContour analysis={melodyData} />
                                </div>
                            ) : (
                                <ErrorState message="Melody extraction unavailable." />
                            )}
                        </motion.div>
                    )}

                    {/* JAZZ VIEW */}
                    {selectedView === 'jazz' && (
                        <motion.div
                            key="jazz"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                        >
                            {isJazzLoading ? (
                                <LoadingState message="Detecting jazz patterns..." />
                            ) : jazzData ? (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-3 gap-4">
                                        <StatCard
                                            label="ii-V-I's"
                                            value={jazzData.ii_v_i_progressions.length}
                                            color="violet"
                                        />
                                        <StatCard
                                            label="Turnarounds"
                                            value={jazzData.turnarounds.length}
                                            color="pink"
                                        />
                                        <StatCard
                                            label="Tritone Subs"
                                            value={jazzData.tritone_substitutions.length}
                                            color="amber"
                                        />
                                    </div>

                                    <div className="space-y-4">
                                        <h4 className="text-sm font-medium text-slate-300 uppercase tracking-wider">Detected Progressions</h4>
                                        {jazzData.ii_v_i_progressions.length > 0 ? (
                                            <div className="bg-slate-900/50 rounded-lg overflow-hidden">
                                                {jazzData.ii_v_i_progressions.map((p, i) => (
                                                    <div key={i} className="flex items-center justify-between p-3 border-b border-slate-800 last:border-0 hover:bg-slate-800/50 transition-colors">
                                                        <div className="flex items-center gap-3">
                                                            <div className="w-8 h-8 rounded-full bg-violet-500/10 flex items-center justify-center text-violet-400 text-xs font-bold">
                                                                ii-V
                                                            </div>
                                                            <div>
                                                                <div className="text-white text-sm">Key of {p.key}</div>
                                                                <div className="text-xs text-slate-500">
                                                                    {p.start_time.toFixed(1)}s - {(p.start_time + p.duration).toFixed(1)}s
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <div className="text-xs font-mono text-slate-400">
                                                            {(p.confidence * 100).toFixed(0)}%
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="text-center py-8 text-slate-500 italic border border-dashed border-slate-700 rounded-lg">
                                                No standard ii-V-I progressions detected
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                <ErrorState message="Jazz analysis failed." />
                            )}
                        </motion.div>
                    )}

                    {/* CHORDS VIEW */}
                    {selectedView === 'chords' && (
                        <motion.div
                            key="chords"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">Chord Progression Timeline</h3>
                            {detectedChords.length > 0 ? (
                                <div className="relative pt-6 pb-2 overflow-x-auto">
                                    <div className="flex gap-1 min-w-full">
                                        <div className="flex gap-1 min-w-full">
                                            {detectedChords.map((chord, index) => (
                                                <div
                                                    key={index}
                                                    className="flex-shrink-0 flex flex-col items-center group relative cursor-help"
                                                    style={{ width: Math.max(60, chord.duration * 40) }}
                                                >
                                                    <div className="w-full h-8 bg-slate-800 rounded-lg mb-2 overflow-hidden relative">
                                                        <div className="absolute inset-0 bg-violet-500/20 group-hover:bg-violet-500/30 transition-colors" />
                                                    </div>
                                                    <span className="font-mono font-bold text-violet-400 text-sm whitespace-nowrap">
                                                        {chord.chord}
                                                    </span>
                                                    <span className="text-[10px] text-slate-500 mt-1">
                                                        {chord.time.toFixed(1)}s
                                                    </span>

                                                    {/* Tooltip */}
                                                    <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block z-10 bg-black/90 text-xs p-2 rounded whitespace-nowrap border border-slate-700 pointer-events-none">
                                                        {chord.romanNumeral && (
                                                            <>
                                                                Roman: {chord.romanNumeral} <br />
                                                            </>
                                                        )}
                                                        Duration: {chord.duration.toFixed(2)}s
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

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
                    )}

                    {/* VOICINGS VIEW */}
                    {selectedView === 'voicings' && (
                        <motion.div
                            key="voicings"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                        >
                            <VoicingsDisplay
                                chords={detectedChords}
                                songId={songId}
                                maxVisible={6}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

// Sub-components for cleaner file

function TabButton({ active, onClick, icon, label }: any) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${active
                ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
        >
            {icon}
            {label}
        </button>
    );
}

function StatCard({ label, value, subValue, color = 'slate' }: any) {
    const colors: any = {
        cyan: 'text-cyan-400',
        emerald: 'text-emerald-400',
        violet: 'text-violet-400',
        pink: 'text-pink-400',
        amber: 'text-amber-400',
        slate: 'text-slate-200'
    };

    return (
        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
            <div className="text-slate-500 text-xs uppercase tracking-wider mb-1">{label}</div>
            <div className={`text-2xl font-bold ${colors[color]}`}>{value}</div>
            {subValue && <div className="text-slate-400 text-xs mt-1">{subValue}</div>}
        </div>
    );
}

function LoadingState({ message }: { message: string }) {
    return (
        <div className="flex flex-col items-center justify-center h-64 text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-cyan-500" />
            <p>{message}</p>
        </div>
    );
}

function ErrorState({ message }: { message: string }) {
    return (
        <div className="flex flex-col items-center justify-center h-64 text-rose-400">
            <AlertCircle className="w-8 h-8 mb-3" />
            <p>{message}</p>
        </div>
    );
}
