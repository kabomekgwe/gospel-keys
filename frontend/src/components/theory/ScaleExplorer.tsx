/**
 * Scale Explorer Component
 * 
 * Browse and explore scales with interactive visualization
 */
import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, Volume2 } from 'lucide-react';
import { InteractivePiano } from './InteractivePiano';
import {
    SCALES,
    NOTE_NAMES,
    getScaleNotes,
    getScaleMidiNotes,
    type ScaleDefinition
} from '../../lib/theoryData';

interface ScaleExplorerProps {
    onPlayScale?: (midiNotes: number[]) => void;
}

export function ScaleExplorer({ onPlayScale }: ScaleExplorerProps) {
    const [selectedRoot, setSelectedRoot] = useState('C');
    const [selectedScale, setSelectedScale] = useState('major');
    const [search, setSearch] = useState('');

    // Filter scales by search
    const filteredScales = useMemo(() => {
        if (!search) return Object.entries(SCALES);
        const lower = search.toLowerCase();
        return Object.entries(SCALES).filter(([key, scale]) =>
            scale.name.toLowerCase().includes(lower) ||
            key.toLowerCase().includes(lower)
        );
    }, [search]);

    // Get current scale data
    const currentScale = SCALES[selectedScale];
    const scaleNotes = getScaleNotes(selectedRoot, selectedScale);
    const midiNotes = getScaleMidiNotes(selectedRoot, selectedScale, 4);
    const rootMidi = midiNotes[0];

    // Group scales by category
    const scalesByCategory = useMemo(() => {
        const categories: Record<string, [string, ScaleDefinition][]> = {};
        filteredScales.forEach(([key, scale]) => {
            if (!categories[scale.category]) {
                categories[scale.category] = [];
            }
            categories[scale.category].push([key, scale]);
        });
        return categories;
    }, [filteredScales]);

    const handlePlayScale = () => {
        if (onPlayScale) {
            onPlayScale(midiNotes);
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
                    placeholder="Search scales..."
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 outline-none"
                />
            </div>

            {/* Scale Types by Category */}
            <div className="space-y-4">
                {Object.entries(scalesByCategory).map(([category, scales]) => (
                    <div key={category}>
                        <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-2">
                            {category}
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {scales.map(([key, scale]) => (
                                <button
                                    key={key}
                                    onClick={() => setSelectedScale(key)}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedScale === key
                                            ? 'bg-cyan-500 text-white'
                                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                        }`}
                                >
                                    {scale.name}
                                </button>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Selected Scale Display */}
            {currentScale && (
                <motion.div
                    key={`${selectedRoot}-${selectedScale}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card p-6"
                >
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-2xl font-bold text-white">
                                {selectedRoot} {currentScale.name}
                            </h2>
                            <p className="text-slate-400 capitalize">{currentScale.category} scale</p>
                        </div>
                        <button
                            onClick={handlePlayScale}
                            disabled={!onPlayScale}
                            className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Volume2 className="w-5 h-5" />
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

                    {/* Scale Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Notes</h4>
                            <div className="flex flex-wrap gap-2">
                                {scaleNotes.map((note, i) => (
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
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Scale Degrees</h4>
                            <div className="flex flex-wrap gap-2">
                                {currentScale.degrees.map((degree, i) => (
                                    <span
                                        key={i}
                                        className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300"
                                    >
                                        {degree}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Intervals</h4>
                            <div className="flex flex-wrap gap-2">
                                {currentScale.intervals.map((interval, i) => (
                                    <span
                                        key={i}
                                        className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300"
                                    >
                                        {interval === 0 ? 'R' : `+${interval}`}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {currentScale.chordQualities && (
                            <div className="p-4 bg-slate-800/50 rounded-lg">
                                <h4 className="text-sm font-medium text-slate-400 mb-2">Diatonic Chords</h4>
                                <div className="flex flex-wrap gap-2">
                                    {currentScale.chordQualities.map((quality, i) => {
                                        const chordRoot = scaleNotes[i] || '';
                                        return (
                                            <span
                                                key={i}
                                                className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300"
                                            >
                                                {chordRoot}{quality}
                                            </span>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>
                </motion.div>
            )}
        </div>
    );
}
