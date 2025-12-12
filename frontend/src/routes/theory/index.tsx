/**
 * Theory Hub Page
 * 
 * Main page for music theory reference with:
 * - Chord dictionary
 * - Scale explorer
 * - Circle of fifths
 * - AI Generator
 */
import { createFileRoute } from '@tanstack/react-router';
import { motion } from 'framer-motion';
import { useState } from 'react';
import {
    BookOpen,
    Layers,
    Music,
    Circle,
    Sparkles,
} from 'lucide-react';
import { ChordDictionary, ScaleExplorer, CircleOfFifths } from '../../components/theory';
import { AIGenerator } from '../../components/theory/AIGenerator';
import { useSynth } from '../../hooks/useSynth';

export const Route = createFileRoute('/theory/')({
    component: TheoryHub,
});

type TabId = 'ai' | 'chords' | 'scales' | 'circle';

interface Tab {
    id: TabId;
    label: string;
    icon: React.ReactNode;
}

const TABS: Tab[] = [
    { id: 'ai', label: 'AI Generator', icon: <Sparkles className="w-5 h-5" /> },
    { id: 'chords', label: 'Chord Dictionary', icon: <Layers className="w-5 h-5" /> },
    { id: 'scales', label: 'Scale Explorer', icon: <Music className="w-5 h-5" /> },
    { id: 'circle', label: 'Circle of Fifths', icon: <Circle className="w-5 h-5" /> },
];

function TheoryHub() {
    const [activeTab, setActiveTab] = useState<TabId>('ai');
    const [selectedKey, setSelectedKey] = useState('C');

    // Audio synth for playing chords and scales
    const { playChord, playScale } = useSynth({ oscillatorType: 'triangle' });

    const handleKeySelect = (key: string, isMinor: boolean) => {
        setSelectedKey(key);
        // Could switch to scales tab and select minor scale
        if (isMinor) {
            setActiveTab('scales');
        }
    };

    const handlePlayChord = (midiNotes: number[]) => {
        playChord(midiNotes, 1.5, 0.4);
    };

    const handlePlayScale = (midiNotes: number[]) => {
        playScale(midiNotes, 0.35, 0.05, 0.5);
    };

    return (
        <div className="min-h-screen p-8 overflow-y-auto">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold text-white flex items-center gap-3 mb-2">
                    <BookOpen className="w-8 h-8 text-violet-400" />
                    Music Theory Reference
                </h1>
                <p className="text-slate-400">
                    Explore chords, scales, and harmonic relationships powered by AI
                </p>
            </motion.div>

            {/* Tab Navigation */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-2 mb-8 border-b border-slate-700 pb-4 overflow-x-auto"
            >
                {TABS.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all whitespace-nowrap ${activeTab === tab.id
                            ? tab.id === 'ai'
                                ? 'bg-gradient-to-r from-violet-500/20 to-cyan-500/20 text-violet-400 border border-violet-500/30'
                                : 'bg-violet-500/20 text-violet-400 border border-violet-500/30'
                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                            }`}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </motion.div>

            {/* Tab Content */}
            <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
            >
                {activeTab === 'ai' && (
                    <AIGenerator onPlayChord={handlePlayChord} />
                )}

                {activeTab === 'chords' && (
                    <ChordDictionary onPlayChord={handlePlayChord} />
                )}

                {activeTab === 'scales' && (
                    <ScaleExplorer onPlayScale={handlePlayScale} />
                )}

                {activeTab === 'circle' && (
                    <div className="flex flex-col items-center">
                        <div className="card p-8">
                            <CircleOfFifths
                                selectedKey={selectedKey}
                                onSelectKey={handleKeySelect}
                                showMinors
                            />
                        </div>

                        <div className="mt-8 max-w-2xl text-center">
                            <h3 className="text-lg font-semibold text-white mb-4">How to Use</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                                <div className="p-4 bg-slate-800/50 rounded-lg">
                                    <h4 className="font-medium text-cyan-400 mb-2">Key Relationships</h4>
                                    <p className="text-sm text-slate-400">
                                        Adjacent keys share similar notes. Moving clockwise adds sharps,
                                        counterclockwise adds flats.
                                    </p>
                                </div>
                                <div className="p-4 bg-slate-800/50 rounded-lg">
                                    <h4 className="font-medium text-violet-400 mb-2">Relative Minors</h4>
                                    <p className="text-sm text-slate-400">
                                        Inner ring shows relative minor keys. Each major key has a
                                        relative minor with the same key signature.
                                    </p>
                                </div>
                                <div className="p-4 bg-slate-800/50 rounded-lg">
                                    <h4 className="font-medium text-amber-400 mb-2">Common Progressions</h4>
                                    <p className="text-sm text-slate-400">
                                        Use adjacent keys for smooth chord progressions.
                                        I-IV-V chords are neighbors on the circle.
                                    </p>
                                </div>
                                <div className="p-4 bg-slate-800/50 rounded-lg">
                                    <h4 className="font-medium text-emerald-400 mb-2">Modulation</h4>
                                    <p className="text-sm text-slate-400">
                                        Modulate to nearby keys for smooth transitions.
                                        Opposite keys create maximum contrast.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </motion.div>
        </div>
    );
}
