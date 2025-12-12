
import { BarChart2, Music, Zap } from 'lucide-react';
import { useMemo } from 'react';
import { type MidiNote } from '../hooks/useMidiPlayer';
import { motion } from 'framer-motion';

interface AnalysisTabProps {
    notes: MidiNote[];
}

// Basic music theory helper
const getNoteName = (pitch: number): string => {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    return notes[pitch % 12];
};

// Dummy analysis function (replace with real logic)
const analyzeChords = (notes: MidiNote[]) => {
    if (notes.length < 3) return [];

    const chords = [];
    let currentTime = -1;
    let currentChord: MidiNote[] = [];

    for (const note of notes) {
        if (note.startTime > currentTime) {
            if (currentChord.length >= 3) {
                chords.push({
                    time: currentTime,
                    notes: currentChord.map(n => getNoteName(n.pitch)).sort(),
                });
            }
            currentTime = note.startTime;
            currentChord = [note];
        } else if (note.startTime === currentTime) {
            currentChord.push(note);
        }
    }
    // Add the last chord
    if (currentChord.length >= 3) {
        chords.push({
            time: currentTime,
            notes: currentChord.map(n => getNoteName(n.pitch)).sort(),
        });
    }

    // Basic chord naming
    return chords.map(c => ({ ...c, name: `${c.notes[0]}maj` })); // Simplified
};

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

export function AnalysisTab({ notes }: AnalysisTabProps) {
    const detectedChords = useMemo(() => analyzeChords(notes), [notes]);
    const totalNotes = notes.length;
    const keyComplexity = new Set(notes.map(n => getNoteName(n.pitch))).size;

    return (
        <div className="p-6 overflow-y-auto h-full">
            <div className="max-w-5xl mx-auto space-y-8">
                <header>
                    <h2 className="text-2xl font-bold text-white mb-2">Song Analysis</h2>
                    <p className="text-slate-400">
                        Insights into the harmonic and melodic structure of the piece.
                    </p>
                </header>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card title="Total Notes" value={totalNotes} icon={Music} color="cyan" />
                    <Card title="Unique Notes" value={`${keyComplexity}`} icon={BarChart2} color="violet" />
                    <Card title="Detected Chords" value={detectedChords.length} icon={Zap} color="amber" />
                </div>

                {/* Chord Progression */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="card p-6"
                >
                    <h3 className="text-lg font-semibold text-white mb-4">Chord Progression</h3>
                    {detectedChords.length > 0 ? (
                        <div className="flex flex-wrap gap-4">
                            {detectedChords.map((chord, index) => (
                                <div key={index} className="flex flex-col items-center">
                                    <span className="text-xs text-slate-400 mb-1">
                                        {chord.time.toFixed(2)}s
                                    </span>
                                    <div className="px-4 py-2 bg-slate-800 rounded-lg">
                                        <span className="font-mono text-violet-400">{chord.name}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-500 text-center py-4">
                            Not enough notes to perform chord analysis.
                        </p>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
