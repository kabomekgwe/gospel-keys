/**
 * Song Detail Page
 * 
 * Displays song information with tabbed interface:
 * - Overview: Song metadata, stats
 * - Piano Roll: Visual MIDI display with playback
 * - Analysis: Chord/pattern analysis (linked to next phase)
 * - Practice: Practice mode (linked to practice phase)
 */
import { createFileRoute, Link, useParams } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useState, useMemo } from 'react';
import {
    ArrowLeft,
    Clock,
    Music,
    Timer,
    Key,
    Heart,
    Star,
    Download,
    Share2,
    BarChart2,
    Dumbbell,
    Layers,
    FileMusic,
} from 'lucide-react';
import { type SongDetail, libraryApi, notesApi } from '../../lib/api';
import { PianoRoll } from '../../components/PianoRoll';
import { Piano, MiniPiano } from '../../components/Piano';
import { PlaybackControls } from '../../components/PlaybackControls';
import { useNewMidiPlayer, type MidiNote } from '../../hooks/useNewMidiPlayer';
import { SheetMusicRenderer } from '../../components/sheet-music';
import { AnalysisTab } from '../../components/AnalysisTab';
import { PracticeTab } from '../../components/PracticeTab';


export const Route = createFileRoute('/library/$songId')({
    component: SongDetailPage,
    validateSearch: (search: Record<string, unknown>): { tab?: TabId; snippetId?: string } => ({
        tab: (search.tab as TabId) || 'overview',
        snippetId: (search.snippetId as string) || undefined,
    }),
});


type TabId = 'overview' | 'piano-roll' | 'sheet-music' | 'analysis' | 'practice';

const tabs: { id: TabId; label: string; icon: typeof Music }[] = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'piano-roll', label: 'Piano Roll', icon: Music },
    { id: 'sheet-music', label: 'Sheet Music', icon: FileMusic },
    { id: 'analysis', label: 'Analysis', icon: BarChart2 },
    { id: 'practice', label: 'Practice', icon: Dumbbell },
];

function SongDetailPage() {
    const { songId } = useParams({ from: '/library/$songId' });
    const searchParams = Route.useSearch();
    const navigate = Route.useNavigate();

    // Sync tab with search params
    const activeTab = searchParams.tab || 'overview';
    const setActiveTab = (tab: TabId) => navigate({ search: { ...searchParams, tab } });

    const [isFavorite, setIsFavorite] = useState(false);

    // Fetch song data from real API
    const { data: song, isLoading, error } = useQuery({
        queryKey: ['song', songId],
        queryFn: () => libraryApi.getSong(songId),
    });

    // Fetch notes for piano roll
    const { data: notesData } = useQuery({
        queryKey: ['song', songId, 'notes'],
        queryFn: () => notesApi.getNotes(songId),
        enabled: !!song,
    });

    const { data: chordsData } = useQuery({
        queryKey: ['song', songId, 'chords'],
        queryFn: () => notesApi.getChords(songId),
        enabled: !!song,
    });

    // Convert API notes to MidiNote format
    const songNotes = useMemo<MidiNote[]>(() => {
        if (!notesData) {
            return [];
        }
        return notesData.map((note) => ({
            id: note.id,
            pitch: note.pitch,
            startTime: note.startTime,
            duration: note.duration,
            velocity: note.velocity,
            hand: note.hand || 'right',
        }));
    }, [notesData]);

    // MIDI player
    const [playerState, playerControls] = useNewMidiPlayer(
        songNotes,
        song?.duration || 0
    );

    if (isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-900">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-slate-400">Loading song...</p>
                </div>
            </div>
        );
    }
    if (error || !song) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-900">
                <div className="text-center">
                    <p className="text-red-400 mb-4">Failed to load song</p>
                    <Link
                        to="/library"
                        className="text-cyan-400 hover:text-cyan-300 underline"
                    >
                        Back to Library
                    </Link>
                </div>
            </div>
        );
    }
    return (
        <div className="flex-1 flex flex-col bg-slate-900 overflow-hidden">
            {/* Header */}
            <header className="flex-shrink-0 p-6 bg-gradient-to-b from-slate-800/80 to-transparent">
                <div className="flex items-start gap-4">
                    {/* Back button */}
                    <Link
                        to="/library"
                        className="p-2 rounded-lg bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Link>

                    {/* Song info */}
                    <div className="flex-1">
                        <h1 className="text-2xl font-bold text-white mb-1">{song.title}</h1>
                        {song.artist && (
                            <p className="text-slate-400 mb-3">{song.artist}</p>
                        )}

                        {/* Metadata badges */}
                        <div className="flex flex-wrap items-center gap-3">
                            <span className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 rounded-full text-sm text-slate-300">
                                <Clock className="w-4 h-4 text-cyan-400" />
                                {Math.floor(song.duration / 60)}:{(song.duration % 60).toString().padStart(2, '0')}
                            </span>

                            {song.tempo && (
                                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 rounded-full text-sm text-slate-300">
                                    <Timer className="w-4 h-4 text-violet-400" />
                                    {song.tempo} BPM
                                </span>
                            )}

                            {song.key_signature && (
                                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 rounded-full text-sm text-slate-300">
                                    <Key className="w-4 h-4 text-amber-400" />
                                    {song.key_signature}
                                </span>
                            )}

                            {song.difficulty && (
                                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-500/20 rounded-full text-sm text-cyan-300">
                                    <Star className="w-4 h-4" />
                                    {song.difficulty}
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setIsFavorite(!isFavorite)}
                            className={`p-3 rounded-xl transition-colors ${isFavorite
                                ? 'bg-red-500/20 text-red-400'
                                : 'bg-slate-800/50 text-slate-400 hover:text-white'
                                }`}
                        >
                            <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="p-3 rounded-xl bg-slate-800/50 text-slate-400 hover:text-white transition-colors"
                        >
                            <Share2 className="w-5 h-5" />
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="p-3 rounded-xl bg-slate-800/50 text-slate-400 hover:text-white transition-colors"
                        >
                            <Download className="w-5 h-5" />
                        </motion.button>
                    </div>
                </div>

                {/* Tabs */}
                <nav className="flex items-center gap-1 mt-6 p-1 bg-slate-800/50 rounded-xl w-fit">
                    {tabs.map((tab) => (
                        <motion.button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`
                flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${activeTab === tab.id
                                    ? 'bg-cyan-500 text-white'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                                }
              `}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                        </motion.button>
                    ))}
                </nav>
            </header>

            {/* Tab content */}
            <div className="flex-1 overflow-hidden">
                {activeTab === 'overview' && (
                    <OverviewTab song={song} onNavigateToAnalysis={() => setActiveTab('analysis')} />
                )}

                {activeTab === 'piano-roll' && (
                    <div className="h-full flex flex-col">
                        <div className="flex-1 p-4 overflow-hidden">
                            <PianoRoll
                                notes={songNotes.map((n: MidiNote) => ({
                                    id: n.id,
                                    pitch: n.pitch,
                                    startTime: n.startTime,
                                    duration: n.duration,
                                    velocity: n.velocity,
                                    hand: n.hand,
                                }))}
                                duration={song.duration}
                                currentTime={playerState.currentTime}
                                isPlaying={playerState.isPlaying}
                                highlightedNotes={playerState.activeNotes.map(p =>
                                    songNotes.find((n: MidiNote) => n.pitch === p &&
                                        n.startTime <= playerState.currentTime &&
                                        n.startTime + n.duration > playerState.currentTime
                                    )?.id || ''
                                ).filter(Boolean)}
                                onSeek={playerControls.seek}
                            />
                        </div>

                        {/* Piano keyboard */}
                        <div className="flex-shrink-0 p-4 bg-slate-800/50 border-t border-slate-700/50 overflow-x-auto">
                            <div className="flex justify-center">
                                <Piano
                                    minPitch={48}
                                    maxPitch={84}
                                    activeNotes={playerState.activeNotes}
                                    onNotePlay={(pitch) => playerControls.playNote(pitch, 80, 0.5)}
                                    keySize={32}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'sheet-music' && (
                    <div className="h-full p-6 overflow-auto">
                        <div className="max-w-5xl mx-auto space-y-6">
                            <SheetMusicRenderer
                                notes={songNotes}
                                currentTime={playerState.currentTime}
                                height={220}
                                showControls
                                tempo={song.tempo}
                                keySignature={song.key_signature ?? 'C'}
                                timeSignature={song.time_signature ?? '4/4'}
                            />

                            {/* Playback controls for sheet music view */}
                            <div className="card p-4">
                                <PlaybackControls
                                    isPlaying={playerState.isPlaying}
                                    currentTime={playerState.currentTime}
                                    duration={song.duration}
                                    tempo={playerState.tempo}
                                    onPlay={playerControls.play}
                                    onPause={playerControls.pause}
                                    onStop={playerControls.stop}
                                    onSeek={playerControls.seek}
                                    onTempoChange={playerControls.setTempo}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'analysis' && (
                    <AnalysisTab
                        songId={songId}
                        detectedChords={chordsData || []}
                        totalNotes={songNotes.length}
                    />
                )}

                {activeTab === 'practice' && (
                    <PracticeTab
                        playerControls={playerControls}
                        playerState={playerState}
                        notes={songNotes}
                        snippetId={searchParams.snippetId}
                    />
                )}
            </div>

            {/* Playback controls (show for piano-roll tab) */}
            {activeTab === 'piano-roll' && (
                <PlaybackControls
                    isPlaying={playerState.isPlaying}
                    currentTime={playerState.currentTime}
                    duration={playerState.duration}
                    tempo={playerState.tempo}
                    onPlay={playerControls.play}
                    onPause={playerControls.pause}
                    onStop={playerControls.stop}
                    onSeek={playerControls.seek}
                    onTempoChange={playerControls.setTempo}
                />
            )}
        </div>
    );
}

// Overview tab content
function OverviewTab({ song, onNavigateToAnalysis }: { song: SongDetail; onNavigateToAnalysis: () => void }) {
    // Demo data - would come from API in production
    const avgVoicingComplexity = 0.65; // 0-1 scale
    const detectedPatternsCount = 3;

    return (
        <div className="p-6 overflow-y-auto">
            <div className="max-w-4xl mx-auto grid gap-6 md:grid-cols-2">
                {/* Stats card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card p-6"
                >
                    <h3 className="text-lg font-semibold text-white mb-4">Statistics</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-slate-400">Total Notes</span>
                            <span className="text-xl font-bold text-cyan-400">{song.note_count || '—'}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-slate-400">Chord Changes</span>
                            <span className="text-xl font-bold text-violet-400">{song.chord_count || '—'}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-slate-400">Time Signature</span>
                            <span className="text-lg font-mono text-white">{song.time_signature || '4/4'}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-slate-400">Duration</span>
                            <span className="text-lg font-mono text-white">
                                {Math.floor(song.duration / 60)}:{(song.duration % 60).toString().padStart(2, '0')}
                            </span>
                        </div>
                    </div>
                </motion.div>

                {/* Quick preview card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="card p-6"
                >
                    <h3 className="text-lg font-semibold text-white mb-4">Preview</h3>
                    <p className="text-slate-400 text-sm mb-4">
                        Click on the piano keys to play notes
                    </p>
                    <div className="flex justify-center">
                        <MiniPiano minPitch={60} maxPitch={72} />
                    </div>
                </motion.div>

                {/* Quick Analysis card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="card p-6 md:col-span-2"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">Quick Analysis</h3>
                        <button
                            onClick={onNavigateToAnalysis}
                            className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1"
                        >
                            View Full Analysis
                            <BarChart2 className="w-4 h-4" />
                        </button>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <Layers className="w-5 h-5 text-violet-400" />
                                <span className="text-slate-400 text-sm">Voicing Complexity</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-emerald-500 to-violet-500 transition-all duration-500"
                                        style={{ width: `${avgVoicingComplexity * 100}%` }}
                                    />
                                </div>
                                <span className="text-lg font-bold text-white">
                                    {Math.round(avgVoicingComplexity * 100)}%
                                </span>
                            </div>
                            <p className="text-xs text-slate-500 mt-2">
                                {avgVoicingComplexity < 0.4 ? 'Simple voicings' :
                                    avgVoicingComplexity < 0.7 ? 'Moderate complexity' :
                                        'Advanced voicings'}
                            </p>
                        </div>

                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <BarChart2 className="w-5 h-5 text-cyan-400" />
                                <span className="text-slate-400 text-sm">Detected Patterns</span>
                            </div>
                            <div className="flex items-baseline gap-2">
                                <span className="text-3xl font-bold text-cyan-400">
                                    {detectedPatternsCount}
                                </span>
                                <span className="text-sm text-slate-500">progressions</span>
                            </div>
                            <p className="text-xs text-slate-500 mt-2">
                                Including jazz, pop, and classical patterns
                            </p>
                        </div>
                    </div>

                    <div className="mt-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                        <p className="text-xs text-slate-400 leading-relaxed">
                            <strong className="text-slate-300">Tip:</strong> Switch to the Analysis tab to explore
                            detailed chord voicings, reharmonization suggestions, and progression patterns with interactive
                            piano visualizations.
                        </p>
                    </div>
                </motion.div>

                {/* Source info */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="card p-6 md:col-span-2"
                >
                    <h3 className="text-lg font-semibold text-white mb-4">Source</h3>
                    <div className="space-y-3">
                        {song.source_url && (
                            <div className="flex items-center gap-3">
                                <span className="text-slate-400 text-sm">URL:</span>
                                <a
                                    href={song.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-cyan-400 hover:text-cyan-300 underline text-sm truncate max-w-md"
                                >
                                    {song.source_url}
                                </a>
                            </div>
                        )}
                        <div className="flex items-center gap-3">
                            <span className="text-slate-400 text-sm">Imported:</span>
                            <span className="text-white text-sm">
                                {new Date(song.created_at).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                })}
                            </span>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
