/**
 * Practice Mode Page
 * 
 * Interactive practice view with:
 * - Tempo control (slow down practice)
 * - Loop section selection
 * - Follow-along piano roll
 * - Practice session tracking
 */
import { createFileRoute, Link, useParams } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useState, useMemo, useCallback } from 'react';
import {
    ArrowLeft,
    Dumbbell,
    Play,
    Pause,
    RotateCcw,
    Repeat,
    ChevronDown,
    Target,
    Clock,
    Trophy,
    Zap,
    Eye,
    EyeOff,
} from 'lucide-react';
import { PianoRoll } from '../../../components/PianoRoll';
import { Piano } from '../../../components/Piano';
import { useMidiPlayer, type MidiNote } from '../../../hooks/useMidiPlayer';
import { VoicingVisualizer, type VoicingInfo } from '../../../components/analysis/VoicingVisualizer';

export const Route = createFileRoute('/library/$songId/practice')({
    component: PracticePage,
});

// Generate demo notes
function generateDemoNotes(duration: number): MidiNote[] {
    const notes: MidiNote[] = [];
    const scale = [60, 62, 64, 65, 67, 69, 71, 72];

    let time = 0;
    let noteId = 0;

    while (time < duration) {
        const pitch = scale[Math.floor(Math.random() * scale.length)];
        const noteDuration = 0.3 + Math.random() * 0.4;
        notes.push({
            id: `note-${noteId++}`,
            pitch,
            start_time: time,
            end_time: time + noteDuration,
            velocity: 60 + Math.floor(Math.random() * 40),
        });
        time += 0.4 + Math.random() * 0.4;
    }

    return notes;
}

// Tempo presets
const TEMPO_PRESETS = [
    { value: 0.25, label: '0.25×', description: 'Ultra slow' },
    { value: 0.5, label: '0.5×', description: 'Half speed' },
    { value: 0.75, label: '0.75×', description: 'Slow' },
    { value: 1.0, label: '1×', description: 'Normal' },
    { value: 1.25, label: '1.25×', description: 'Fast' },
    { value: 1.5, label: '1.5×', description: 'Very fast' },
];

// Generate demo voicing for practice
function generateDemoVoicing(currentTime: number): { chord: string; voicing: VoicingInfo } {
    // Simple progression that cycles every 8 seconds
    const chords = [
        { symbol: 'Cmaj7', notes: [48, 60, 64, 71, 67], noteNames: ['C3', 'C4', 'E4', 'B4', 'G4'] },
        { symbol: 'Dm7', notes: [50, 62, 65, 69, 72], noteNames: ['D3', 'D4', 'F4', 'A4', 'C5'] },
        { symbol: 'G7', notes: [43, 55, 59, 62, 65], noteNames: ['G2', 'G3', 'B3', 'D4', 'F4'] },
        { symbol: 'Cmaj7', notes: [48, 60, 64, 71, 67], noteNames: ['C3', 'C4', 'E4', 'B4', 'G4'] },
    ];

    const index = Math.floor(currentTime / 2) % chords.length;
    const current = chords[index];

    return {
        chord: current.symbol,
        voicing: {
            chord_symbol: current.symbol,
            voicing_type: 'drop_2',
            notes: current.notes,
            note_names: current.noteNames,
            intervals: [12, 4, 7, -4],
            width_semitones: current.notes[current.notes.length - 1] - current.notes[0],
            inversion: 0,
            has_root: true,
            has_third: true,
            has_seventh: true,
            extensions: [],
            complexity_score: 0.6,
            hand_span_inches: 9.5,
        },
    };
}

function PracticePage() {
    const { songId } = useParams({ from: '/library/$songId/practice' });

    // Practice state
    const [loopEnabled, setLoopEnabled] = useState(false);
    const [loopStart, setLoopStart] = useState(0);
    const [loopEnd, setLoopEnd] = useState(30);
    const [showTempoMenu, setShowTempoMenu] = useState(false);
    const [showVoicing, setShowVoicing] = useState(false);

    // Fetch song data
    const { data: song, isLoading } = useQuery({
        queryKey: ['song', songId],
        queryFn: async () => {
            await new Promise(r => setTimeout(r, 300));
            return {
                id: songId,
                title: 'Nocturne Op. 9 No. 2',
                artist: 'Frédéric Chopin',
                duration: 120,
                tempo: 72,
                key_signature: 'E♭ major',
            };
        },
    });

    // Fetch practice sessions
    const { data: sessions } = useQuery({
        queryKey: ['practice-sessions', songId],
        queryFn: async () => {
            await new Promise(r => setTimeout(r, 200));
            return [
                { id: 1, duration_seconds: 1200, tempo_multiplier: 0.75, created_at: new Date().toISOString() },
                { id: 2, duration_seconds: 900, tempo_multiplier: 0.5, created_at: new Date(Date.now() - 86400000).toISOString() },
            ];
        },
    });

    // Generate demo notes
    const demoNotes = useMemo(() =>
        song ? generateDemoNotes(song.duration) : [],
        [song]
    );

    // Filter notes for loop region
    const loopNotes = useMemo(() => {
        if (!loopEnabled) return demoNotes;
        return demoNotes.filter(
            note => note.start_time >= loopStart && note.start_time < loopEnd
        );
    }, [demoNotes, loopEnabled, loopStart, loopEnd]);

    // MIDI player
    const [playerState, playerControls] = useMidiPlayer(
        loopNotes,
        loopEnabled ? loopEnd - loopStart : song?.duration || 0
    );

    // Handle loop toggle
    const toggleLoop = useCallback(() => {
        setLoopEnabled(prev => !prev);
        if (!loopEnabled && song) {
            // Set default loop to first 30 seconds
            setLoopStart(0);
            setLoopEnd(Math.min(30, song.duration));
        }
    }, [loopEnabled, song]);

    // Calculate total practice time
    const totalPracticeTime = useMemo(() => {
        if (!sessions) return 0;
        return sessions.reduce((acc, s) => acc + s.duration_seconds, 0);
    }, [sessions]);

    // Get current voicing based on playback time
    const currentVoicing = useMemo(() => {
        return generateDemoVoicing(playerState.currentTime);
    }, [playerState.currentTime]);

    if (isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-900">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-slate-400">Loading practice mode...</p>
                </div>
            </div>
        );
    }

    if (!song) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-900">
                <div className="text-center">
                    <p className="text-red-400 mb-4">Song not found</p>
                    <Link to="/library" className="text-cyan-400 hover:underline">
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
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link
                            to="/library/$songId"
                            params={{ songId }}
                            className="p-2 rounded-lg bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </Link>

                        <div>
                            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                                <Dumbbell className="w-6 h-6 text-cyan-400" />
                                Practice Mode
                            </h1>
                            <p className="text-slate-400">{song.title}</p>
                        </div>
                    </div>

                    {/* Practice stats */}
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg">
                            <Clock className="w-4 h-4 text-amber-400" />
                            <span className="text-sm text-slate-300">
                                {Math.floor(totalPracticeTime / 60)} min practiced
                            </span>
                        </div>

                        <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg">
                            <Trophy className="w-4 h-4 text-yellow-400" />
                            <span className="text-sm text-slate-300">
                                {sessions?.length || 0} sessions
                            </span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Controls */}
            <div className="flex-shrink-0 px-6 pb-4">
                <div className="flex items-center justify-between gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                    {/* Playback controls */}
                    <div className="flex items-center gap-3">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={playerState.isPlaying ? playerControls.pause : playerControls.play}
                            className="w-12 h-12 flex items-center justify-center bg-gradient-to-r from-cyan-500 to-cyan-400 rounded-full text-white shadow-lg shadow-cyan-500/30"
                        >
                            {playerState.isPlaying ? (
                                <Pause className="w-5 h-5" />
                            ) : (
                                <Play className="w-5 h-5 ml-0.5" />
                            )}
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={playerControls.stop}
                            className="p-3 rounded-lg bg-slate-700/50 text-slate-300 hover:text-white transition-colors"
                        >
                            <RotateCcw className="w-5 h-5" />
                        </motion.button>
                    </div>

                    {/* Tempo control */}
                    <div className="relative">
                        <button
                            onClick={() => setShowTempoMenu(!showTempoMenu)}
                            className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 rounded-lg text-slate-300 hover:text-white transition-colors"
                        >
                            <Zap className="w-4 h-4 text-amber-400" />
                            <span className="text-sm font-medium">{playerState.tempo}× Speed</span>
                            <ChevronDown className={`w-4 h-4 transition-transform ${showTempoMenu ? 'rotate-180' : ''}`} />
                        </button>

                        {showTempoMenu && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="absolute top-full left-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-20 p-2"
                            >
                                {TEMPO_PRESETS.map((preset) => (
                                    <button
                                        key={preset.value}
                                        onClick={() => {
                                            playerControls.setTempo(preset.value);
                                            setShowTempoMenu(false);
                                        }}
                                        className={`
                      w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors
                      ${playerState.tempo === preset.value
                                                ? 'bg-cyan-500/20 text-cyan-400'
                                                : 'text-slate-300 hover:bg-slate-700/50'
                                            }
                    `}
                                    >
                                        <span className="font-medium">{preset.label}</span>
                                        <span className="text-xs text-slate-500">{preset.description}</span>
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </div>

                    {/* Loop control */}
                    <div className="flex items-center gap-3">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={toggleLoop}
                            className={`
                flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
                ${loopEnabled
                                    ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30'
                                    : 'bg-slate-700/50 text-slate-300 hover:text-white'
                                }
              `}
                        >
                            <Repeat className="w-4 h-4" />
                            <span className="text-sm">Loop</span>
                        </motion.button>

                        {loopEnabled && (
                            <div className="flex items-center gap-2 text-sm text-slate-400">
                                <input
                                    type="number"
                                    value={loopStart}
                                    onChange={(e) => setLoopStart(Number(e.target.value))}
                                    className="w-16 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-center"
                                    min={0}
                                    max={song.duration - 1}
                                />
                                <span>→</span>
                                <input
                                    type="number"
                                    value={loopEnd}
                                    onChange={(e) => setLoopEnd(Number(e.target.value))}
                                    className="w-16 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-center"
                                    min={loopStart + 1}
                                    max={song.duration}
                                />
                                <span className="text-xs">seconds</span>
                            </div>
                        )}
                    </div>

                    {/* Show Voicing toggle */}
                    <div className="flex items-center gap-3">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setShowVoicing(!showVoicing)}
                            className={`
                flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
                ${showVoicing
                                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                                    : 'bg-slate-700/50 text-slate-300 hover:text-white'
                                }
              `}
                        >
                            {showVoicing ? (
                                <Eye className="w-4 h-4" />
                            ) : (
                                <EyeOff className="w-4 h-4" />
                            )}
                            <span className="text-sm">Show Voicing</span>
                        </motion.button>
                    </div>

                    {/* Progress */}
                    <div className="flex items-center gap-3">
                        <span className="text-sm font-mono text-slate-300">
                            {formatTime(playerState.currentTime)} / {formatTime(playerState.duration)}
                        </span>
                    </div>
                </div>
            </div>

            {/* Piano Roll area */}
            <div className="flex-1 p-6 pt-0 overflow-hidden">
                <div className="h-full flex flex-col gap-4">
                    <div className="flex-1 min-h-0">
                        <PianoRoll
                            notes={loopNotes.map(n => {
                                const adjustedStart = loopEnabled ? n.start_time - loopStart : n.start_time;
                                const adjustedEnd = loopEnabled ? n.end_time - loopStart : n.end_time;
                                return {
                                    id: n.id,
                                    pitch: n.pitch,
                                    start_time: adjustedStart,
                                    end_time: adjustedEnd,
                                    velocity: n.velocity,
                                };
                            })}
                            duration={playerState.duration}
                            currentTime={playerState.currentTime}
                            isPlaying={playerState.isPlaying}
                            onSeek={playerControls.seek}
                            highlightedNotes={playerState.activeNotes.map(p =>
                                loopNotes.find(n => n.pitch === p)?.id || ''
                            ).filter(Boolean)}
                        />
                    </div>

                    {/* Voicing Helper (when enabled) */}
                    {showVoicing && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex-shrink-0"
                        >
                            <div className="mb-2 flex items-center gap-2">
                                <div className="h-px flex-1 bg-slate-700" />
                                <span className="text-xs text-slate-500 uppercase tracking-wide">
                                    Current Chord: {currentVoicing.chord}
                                </span>
                                <div className="h-px flex-1 bg-slate-700" />
                            </div>
                            <VoicingVisualizer
                                chord={currentVoicing.chord}
                                voicing={currentVoicing.voicing}
                                showDetails={true}
                                compact={true}
                            />
                        </motion.div>
                    )}

                    {/* Interactive piano */}
                    <div className="flex-shrink-0 p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-x-auto">
                        <div className="flex justify-center">
                            <Piano
                                minPitch={48}
                                maxPitch={84}
                                activeNotes={playerState.activeNotes}
                                onNotePlay={(pitch) => playerControls.playNote(pitch, 80, 0.3)}
                                keySize={28}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Practice tips */}
            <div className="flex-shrink-0 p-6 pt-0">
                <div className="grid grid-cols-3 gap-4">
                    <div className="card p-4 flex items-start gap-3">
                        <div className="p-2 bg-cyan-500/20 rounded-lg">
                            <Target className="w-5 h-5 text-cyan-400" />
                        </div>
                        <div>
                            <h4 className="font-medium text-white text-sm">Slow Practice</h4>
                            <p className="text-xs text-slate-400 mt-1">
                                Start at 0.5× speed and gradually increase as you improve.
                            </p>
                        </div>
                    </div>

                    <div className="card p-4 flex items-start gap-3">
                        <div className="p-2 bg-violet-500/20 rounded-lg">
                            <Repeat className="w-5 h-5 text-violet-400" />
                        </div>
                        <div>
                            <h4 className="font-medium text-white text-sm">Loop Sections</h4>
                            <p className="text-xs text-slate-400 mt-1">
                                Focus on difficult passages by looping small sections.
                            </p>
                        </div>
                    </div>

                    <div className="card p-4 flex items-start gap-3">
                        <div className="p-2 bg-amber-500/20 rounded-lg">
                            <Trophy className="w-5 h-5 text-amber-400" />
                        </div>
                        <div>
                            <h4 className="font-medium text-white text-sm">Track Progress</h4>
                            <p className="text-xs text-slate-400 mt-1">
                                Each practice session is logged to track your improvement.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}
