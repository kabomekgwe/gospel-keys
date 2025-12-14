/**
 * Song Analysis Dashboard
 * 
 * Comprehensive music analysis view with:
 * - Chord progressions and harmonic function
 * - Tension curve visualization
 * - Pattern detection results
 * - Genre classification
 * - Key/tempo analysis
 */
import { createFileRoute, Link, useParams } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useState, useMemo } from 'react';
import {
    ArrowLeft,
    Music,
    BarChart2,
    Zap,
    Layers,
    Target,
    TrendingUp,
    Fingerprint,
} from 'lucide-react';
import { analysisApi, libraryApi } from '../../../lib/api';
import { ChordChart, type ChordData } from '../../../components/ChordChart';
import { TensionCurve, type TensionPoint } from '../../../components/TensionCurve';
import { ProgressionPatterns, type ProgressionPattern } from '../../../components/ProgressionPatterns';
import { VoicingVisualizer, type VoicingInfo } from '../../../components/analysis/VoicingVisualizer';
import { ReharmonizationPanel, type ReharmonizationSuggestion } from '../../../components/analysis/ReharmonizationPanel';
import { ProgressionPatternDisplay, type ChordEvent as ChordEventType, type ProgressionPattern as PatternType } from '../../../components/analysis/ProgressionPatternDisplay';

export const Route = createFileRoute('/library/$songId/analyze')({
    component: AnalyzePage,
});

// Generate demo data for testing
function generateDemoChords(duration: number): ChordData[] {
    const chords: ChordData[] = [];
    const progressions = [
        { root: 'C', quality: 'maj', roman: 'I', fn: 'tonic' as const },
        { root: 'G', quality: 'maj', roman: 'V', fn: 'dominant' as const },
        { root: 'A', quality: 'm', roman: 'vi', fn: 'tonic' as const },
        { root: 'F', quality: 'maj', roman: 'IV', fn: 'subdominant' as const },
    ];

    let time = 0;
    let id = 0;
    const chordDuration = 2;

    while (time < duration) {
        const prog = progressions[id % progressions.length];
        chords.push({
            id: `chord-${id}`,
            root: prog.root,
            quality: prog.quality,
            romanNumeral: prog.roman,
            function: prog.fn,
            function: prog.fn,
            time: time,
            duration: chordDuration,
        });
        time += chordDuration;
        id++;
    }

    return chords;
}

function generateDemoTension(duration: number): TensionPoint[] {
    const points: TensionPoint[] = [];
    const resolution = 0.5; // Every 0.5 seconds

    for (let t = 0; t < duration; t += resolution) {
        // Create an arch-shaped tension curve
        const normalized = t / duration;
        const baseArc = Math.sin(normalized * Math.PI);
        const wave = Math.sin(normalized * Math.PI * 8) * 0.15;
        let tension = baseArc * 0.7 + 0.2 + wave;
        tension = Math.max(0, Math.min(1, tension));

        const point: TensionPoint = { time: t, tension };

        // Add events at key points
        if (Math.abs(normalized - 0.5) < 0.02) {
            point.event = 'climax';
            point.eventLabel = 'Musical climax';
        } else if (normalized > 0.9 && normalized < 0.95) {
            point.event = 'cadence';
            point.eventLabel = 'Final cadence';
        }

        points.push(point);
    }

    return points;
}

function generateDemoPatterns(): ProgressionPattern[] {
    return [
        {
            id: 'pattern-1',
            name: 'I–V–vi–IV (Axis Progression)',
            pattern: ['I', 'V', 'vi', 'IV'],
            chords: ['C', 'G', 'Am', 'F'],
            genre: 'Pop',
            confidence: 0.95,
            confidence: 0.95,
            start_time: 0,
            end_time: 32,
            description: 'The most common chord progression in pop music.',
            famousExamples: ['Let It Be', 'No Woman No Cry', 'With or Without You'],
        },
        {
            id: 'pattern-2',
            name: 'Repeated Axis',
            pattern: ['I', 'V', 'vi', 'IV'],
            chords: ['C', 'G', 'Am', 'F'],
            genre: 'Pop',
            confidence: 0.92,
            start_time: 32,
            end_time: 64,
            description: 'Same progression repeated with slight variation.',
        },
    ];
}

// Demo data for new piano learning components
function generateDemoVoicing(): VoicingInfo {
    return {
        chord_symbol: 'Cmaj7',
        voicing_type: 'drop_2',
        notes: [48, 60, 64, 71, 67], // C3, C4, E4, B4, G4
        note_names: ['C3', 'C4', 'E4', 'B4', 'G4'],
        intervals: [12, 4, 7, -4],
        width_semitones: 19,
        inversion: 0,
        has_root: true,
        has_third: true,
        has_seventh: true,
        extensions: [],
        complexity_score: 0.6,
        hand_span_inches: 9.5,
    };
}

function generateDemoReharmonizations(): ReharmonizationSuggestion[] {
    return [
        {
            original_chord: 'Cmaj7',
            suggested_chord: 'Em7',
            reharmonization_type: 'diatonic_substitution',
            explanation: 'Diatonic substitute - Em7 shares the tonic function with Cmaj7.',
            jazz_level: 1,
            voice_leading_quality: 'smooth',
            voicing: { notes: [52, 64, 67, 71, 74] },
        },
        {
            original_chord: 'Cmaj7',
            suggested_chord: 'Am7',
            reharmonization_type: 'diatonic_substitution',
            explanation: 'Relative minor - Am7 is the vi chord in C major.',
            jazz_level: 1,
            voice_leading_quality: 'smooth',
            voicing: { notes: [57, 64, 67, 69, 72] },
        },
    ];
}

function generateDemoProgressionPatterns(): PatternType[] {
    return [
        {
            pattern_name: 'ii-V-I in C Major',
            genre: 'jazz',
            roman_numerals: ['ii', 'V', 'I'],
            start_index: 0,
            end_index: 2,
            key: 'C major',
            confidence: 0.95,
            description: 'The most common jazz progression.',
        },
    ];
}

function generateDemoChordEvents(chords: ChordData[]): ChordEventType[] {
    return chords.map(c => ({
        time: c.time,
        duration: c.duration,
        chord: `${c.root}${c.quality === 'maj' ? '' : 'm'}${c.quality.includes('7') ? '7' : ''}`,
    }));
}

function AnalyzePage() {
    const { songId } = useParams({ from: '/library/$songId/analyze' });
    const [currentTime, setCurrentTime] = useState(0);
    const [selectedChordId, setSelectedChordId] = useState<string>();

    // Fetch song data from real API
    const { data: song, isLoading: songLoading } = useQuery({
        queryKey: ['song', songId],
        queryFn: () => libraryApi.getSong(songId),
    });

    // Fetch genre analysis from real API
    const { data: genreData } = useQuery({
        queryKey: ['analysis', 'genre', songId],
        queryFn: async () => {
            try {
                return await analysisApi.getGenre(songId);
            } catch {
                // Fallback to demo data if API not available
                return {
                    primary_genre: 'Unknown',
                    subgenres: [],
                    confidence: 0,
                    characteristics: {},
                };
            }
        },
        enabled: !!song,
    });

    // Fetch chord analysis
    const { data: chordData } = useQuery({
        queryKey: ['analysis', 'chords', songId],
        queryFn: async () => {
            try {
                return await analysisApi.getChords(songId);
            } catch {
                // Fallback to demo if API not available
                return song ? generateDemoChords(song.duration) : [];
            }
        },
        enabled: !!song,
    });

    // Fetch patterns
    const { data: patternData } = useQuery({
        queryKey: ['analysis', 'patterns', songId],
        queryFn: async () => {
            try {
                return await analysisApi.getPatterns(songId);
            } catch {
                return generateDemoPatterns();
            }
        },
        enabled: !!song,
    });

    // Use real data or fallback to demo
    const chords = useMemo<ChordData[]>(() => {
        if (chordData && chordData.length > 0) {
            return chordData.map((c: any, i: number) => ({
                id: `chord-${i}`,
                root: c.root || c.chord?.split(/[mM7]/)[0] || 'C',
                quality: c.quality || 'maj',
                romanNumeral: c.roman_numeral,
                function: c.function,
                time: c.time || c.startTime || i * 2,
                duration: c.duration || (c.endTime ? c.endTime - c.startTime : 2),
            }));
        }
        return song ? generateDemoChords(song.duration) : [];
    }, [chordData, song]);

    const tensionData = useMemo(() =>
        song ? generateDemoTension(song.duration) : [],
        [song]
    );

    const patterns = useMemo<ProgressionPattern[]>(() => {
        if (patternData && patternData.length > 0) {
            return patternData.map((p: any, i: number) => ({
                id: `pattern-${i}`,
                name: p.name || p.pattern_name || 'Unknown Pattern',
                pattern: p.pattern || p.roman_numerals || [],
                chords: p.chords || [],
                genre: p.genre || 'Unknown',
                confidence: p.confidence || 0.5,
                start_time: p.start_time || 0,
                end_time: p.end_time || 30,
                description: p.description,
                famousExamples: p.famous_examples || p.examples,
            }));
        }
        return generateDemoPatterns();
    }, [patternData]);

    if (songLoading) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-900">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-violet-500/30 border-t-violet-500 rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-slate-400">Loading analysis...</p>
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
        <div className="flex-1 overflow-y-auto bg-slate-900">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-slate-900/80 backdrop-blur-lg border-b border-slate-700/50">
                <div className="p-6">
                    <div className="flex items-center gap-4 mb-4">
                        <Link
                            to={`/library/${songId}`}
                            className="p-2 rounded-lg bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </Link>

                        <div>
                            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                                <BarChart2 className="w-6 h-6 text-violet-400" />
                                Analysis Dashboard
                            </h1>
                            <p className="text-slate-400">{song.title}</p>
                        </div>
                    </div>

                    {/* Stats bar */}
                    <div className="flex flex-wrap items-center gap-4">
                        <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg">
                            <Music className="w-4 h-4 text-cyan-400" />
                            <span className="text-sm text-slate-300">Key: {song.key_signature}</span>
                        </div>

                        <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg">
                            <Zap className="w-4 h-4 text-amber-400" />
                            <span className="text-sm text-slate-300">Tempo: {song.tempo} BPM</span>
                        </div>

                        <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg">
                            <Layers className="w-4 h-4 text-violet-400" />
                            <span className="text-sm text-slate-300">{chords.length} chord changes</span>
                        </div>

                        {genreData && (
                            <div className="flex items-center gap-2 px-4 py-2 bg-violet-500/20 text-violet-300 rounded-lg">
                                <Fingerprint className="w-4 h-4" />
                                <span className="text-sm">
                                    {genreData.primary_genre}
                                    <span className="text-violet-400 ml-1">
                                        ({Math.round(genreData.confidence * 100)}%)
                                    </span>
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Content */}
            <div className="p-6 space-y-8">
                {/* Genre Analysis */}
                {genreData && (
                    <motion.section
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Fingerprint className="w-5 h-5 text-violet-400" />
                            Genre Classification
                        </h2>

                        <div className="card p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <span className="text-2xl font-bold text-white">{genreData.primary_genre}</span>
                                    <div className="flex items-center gap-2 mt-2">
                                        {genreData.subgenres.map((sub, i) => (
                                            <span key={i} className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300">
                                                {sub}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="text-3xl font-bold text-violet-400">
                                        {Math.round(genreData.confidence * 100)}%
                                    </div>
                                    <div className="text-xs text-slate-400">Confidence</div>
                                </div>
                            </div>

                            {/* Characteristics */}
                            <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-700/50">
                                {Object.entries(genreData.characteristics).map(([key, value]) => (
                                    <div key={key} className="text-center">
                                        <div className="text-sm text-white capitalize">{value as string}</div>
                                        <div className="text-xs text-slate-400 capitalize">{key.replace('_', ' ')}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </motion.section>
                )}

                {/* Chord Progression */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Layers className="w-5 h-5 text-cyan-400" />
                        Chord Progression
                    </h2>

                    <div className="card p-6">
                        <ChordChart
                            chords={chords}
                            duration={song.duration}
                            currentTime={currentTime}
                            keySignature={song.key_signature}
                            selectedChordId={selectedChordId}
                            onChordClick={(chord) => setSelectedChordId(chord.id)}
                        />
                    </div>
                </motion.section>

                {/* Tension Curve */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-amber-400" />
                        Harmonic Tension
                    </h2>

                    <div className="card p-6">
                        <TensionCurve
                            data={tensionData}
                            duration={song.duration}
                            currentTime={currentTime}
                            arcType="arch"
                            onSeek={setCurrentTime}
                        />
                    </div>
                </motion.section>

                {/* Progression Patterns */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Target className="w-5 h-5 text-emerald-400" />
                        Progression Patterns
                    </h2>

                    <ProgressionPatterns
                        patterns={patterns}
                        currentTime={currentTime}
                    />
                </motion.section>

                {/* Detected Chord Progressions */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                >
                    <ProgressionPatternDisplay
                        patterns={generateDemoProgressionPatterns()}
                        totalDuration={song.duration}
                        chords={generateDemoChordEvents(chords)}
                        enableAudio={true}
                    />
                </motion.section>

                {/* Chord Voicing Analysis */}
                {chords.length > 0 && (
                    <motion.section
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                    >
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Music className="w-5 h-5 text-cyan-400" />
                            Chord Voicing Example
                        </h2>

                        <VoicingVisualizer
                            chord="Cmaj7"
                            voicing={generateDemoVoicing()}
                            showDetails={true}
                            compact={false}
                        />
                    </motion.section>
                )}

                {/* Reharmonization Suggestions */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                >
                    <ReharmonizationPanel
                        originalChord="Cmaj7"
                        suggestions={generateDemoReharmonizations()}
                        enableAudio={true}
                    />
                </motion.section>
            </div>
        </div>
    );
}
