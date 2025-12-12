/**
 * Chord Dictionary Component
 * 
 * Browse and explore chords with interactive visualization
 */
import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, Volume2, VolumeX } from 'lucide-react';
import { InteractivePiano } from './InteractivePiano';
import {
    CHORD_TYPES,
    NOTE_NAMES,
    getChordNotes,
    getChordMidiNotes,
    type ChordDefinition
} from '../../lib/theoryData';

interface ChordDictionaryProps {
    onPlayChord?: (midiNotes: number[]) => void;
}

export function ChordDictionary({ onPlayChord }: ChordDictionaryProps) {
    const [selectedRoot, setSelectedRoot] = useState('C');
    const [selectedType, setSelectedType] = useState('maj');
    const [search, setSearch] = useState('');
    const [isPlaying, setIsPlaying] = useState(false);

    // Filter chord types by search
    const filteredTypes = useMemo(() => {
        if (!search) return Object.entries(CHORD_TYPES);
        const lower = search.toLowerCase();
        return Object.entries(CHORD_TYPES).filter(([key, chord]) =>
            chord.name.toLowerCase().includes(lower) ||
            key.toLowerCase().includes(lower)
        );
    }, [search]);

    // Get current chord data
    const currentChord = CHORD_TYPES[selectedType];
    const chordNotes = getChordNotes(selectedRoot, selectedType);
    const midiNotes = getChordMidiNotes(selectedRoot, selectedType, 4);
    const rootMidi = midiNotes[0];

    // Group chord types by category
    const chordsByCategory = useMemo(() => {
        const categories: Record<string, [string, ChordDefinition][]> = {};
        filteredTypes.forEach(([key, chord]) => {
            if (!categories[chord.category]) {
                categories[chord.category] = [];
            }
            categories[chord.category].push([key, chord]);
        });
        return categories;
    }, [filteredTypes]);

    const handlePlayChord = () => {
        if (onPlayChord) {
            setIsPlaying(true);
            onPlayChord(midiNotes);
            setTimeout(() => setIsPlaying(false), 1000);
        }
    };

    return (
        <div className="space-y-6">
            {/* Root Note Selector */}
            <div>
                <label className="text-sm font-medium text-slate-400 mb-2 block">Root Note</label>
                <div className="flex flex-wrap gap-2">
                    {NOTE_NAMES.map((note) => (
                        <button
                            key={note}
                            onClick={() => setSelectedRoot(note)}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedRoot === note
                                    ? 'bg-violet-500 text-white'
                                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                }`}
                        >
                            {note}
                        </button>
                    ))}
                </div>
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search chord types..."
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 outline-none"
                />
            </div>

            {/* Chord Types by Category */}
            <div className="space-y-4">
                {Object.entries(chordsByCategory).map(([category, chords]) => (
                    <div key={category}>
                        <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-2">
                            {category}
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {chords.map(([key, chord]) => (
                                <button
                                    key={key}
                                    onClick={() => setSelectedType(key)}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedType === key
                                            ? 'bg-cyan-500 text-white'
                                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                        }`}
                                >
                                    {selectedRoot}{chord.shortName || ''}
                                </button>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Selected Chord Display */}
            {currentChord && (
                <motion.div
                    key={`${selectedRoot}-${selectedType}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card p-6"
                >
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-2xl font-bold text-white">
                                {selectedRoot}{currentChord.shortName}
                            </h2>
                            <p className="text-slate-400">{currentChord.name}</p>
                        </div>
                        <button
                            onClick={handlePlayChord}
                            disabled={!onPlayChord}
                            className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isPlaying ? (
                                <VolumeX className="w-5 h-5" />
                            ) : (
                                <Volume2 className="w-5 h-5" />
                            )}
                            Play
                        </button>
                    </div>

                    {/* Piano Visualization */}
                    <div className="flex justify-center mb-6 overflow-x-auto py-2">
                        <InteractivePiano
                            highlightedNotes={midiNotes}
                            rootNote={rootMidi}
                            octaves={2}
                            startOctave={4}
                            size="md"
                            showNoteNames
                        />
                    </div>

                    {/* Chord Details */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Notes</h4>
                            <div className="flex gap-2">
                                {chordNotes.map((note, i) => (
                                    <span
                                        key={i}
                                        className={`px-3 py-1 rounded-full text-sm font-medium ${i === 0 ? 'bg-violet-500/20 text-violet-400' : 'bg-cyan-500/20 text-cyan-400'
                                            }`}
                                    >
                                        {note}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Intervals</h4>
                            <div className="flex gap-2">
                                {currentChord.intervals.map((interval, i) => (
                                    <span
                                        key={i}
                                        className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300"
                                    >
                                        {interval === 0 ? 'R' : interval}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
