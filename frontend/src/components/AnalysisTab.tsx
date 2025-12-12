
import { BarChart2, Music, Zap, Info } from 'lucide-react';
import { useMemo } from 'react';
import { type MidiNote } from '../hooks/useNewMidiPlayer';
import { motion } from 'framer-motion';
import { Chord, Note } from '@tonaljs/tonal';

interface AnalysisTabProps {
    notes: MidiNote[];
}

// Helper to get note name from MIDI pitch
// const getNoteName = (pitch: number): string => {
//     return Note.fromMidi(pitch);
// };

interface DetectedChord {
    time: number;
    duration: number;
    notes: string[];
    name: string;
    symbol: string;
}

const analyzeChords = (notes: MidiNote[]): DetectedChord[] => {
    if (notes.length < 3) return [];

    // Event-based approach
    const events: { time: number; type: 'on' | 'off'; pitch: number }[] = [];
    notes.forEach(n => {
        events.push({ time: n.startTime, type: 'on', pitch: n.pitch });
        events.push({ time: n.startTime + n.duration, type: 'off', pitch: n.pitch });
    });
    events.sort((a, b) => a.time - b.time);

    const chords: DetectedChord[] = [];
    const currentNotes = new Set<number>();
    let lastTime = 0;

    events.forEach(event => {
        if (event.time > lastTime + 0.1) { // Threshold to ignore tiny gaps
            // Analyze previous segment
            if (currentNotes.size >= 3) {
                const noteNames = Array.from(currentNotes).map(p => Note.pitchClass(Note.fromMidi(p)));
                const detected = Chord.detect(noteNames);
                if (detected.length > 0) {
                    const chordName = detected[0];
                    // Simplify: if multiple candidates, take first
                    chords.push({
                        time: lastTime,
                        duration: event.time - lastTime,
                        notes: noteNames,
                        name: chordName,
                        symbol: chordName // Tonal returns symbols like "CMaj7"
                    });
                }
            }
        }

        if (event.type === 'on') {
            currentNotes.add(event.pitch);
        } else {
            currentNotes.delete(event.pitch);
        }
        lastTime = event.time;
    });

    // Merge adjacent identical chords
    const mergedChords: DetectedChord[] = [];
    if (chords.length > 0) {
        let current = chords[0];
        for (let i = 1; i < chords.length; i++) {
            const next = chords[i];
            if (next.name === current.name && Math.abs(next.time - (current.time + current.duration)) < 0.2) {
                current.duration += next.duration + (next.time - (current.time + current.duration));
            } else {
                mergedChords.push(current);
                current = next;
            }
        }
        mergedChords.push(current);
    }

    return mergedChords;
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
    // Calculate key complexity based on accidentals?
    // Simple unique notes count
    const uniqueNotes = new Set(notes.map(n => n.pitch % 12)).size;

    return (
        <div className="p-6 overflow-y-auto h-full">
            <div className="max-w-5xl mx-auto space-y-8">
                <header>
                    <h2 className="text-2xl font-bold text-white mb-2">Song Analysis</h2>
                    <p className="text-slate-400 flex items-center gap-2">
                        <Info className="w-4 h-4" />
                        Automated harmonic analysis based on note content.
                    </p>
                </header>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card title="Total Notes" value={totalNotes} icon={Music} color="cyan" />
                    <Card title="Unique Pitch Classes" value={uniqueNotes} icon={BarChart2} color="violet" />
                    <Card title="Detected Chords" value={detectedChords.length} icon={Zap} color="amber" />
                </div>

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
                                        style={{ width: Math.max(60, chord.duration * 40) }} // Scale width by duration
                                    >
                                        <div className="w-full h-8 bg-slate-800 rounded-lg mb-2 overflow-hidden relative">
                                            <div className="absolute inset-0 bg-violet-500/20 group-hover:bg-violet-500/30 transition-colors" />
                                            {/* Duration bar */}
                                        </div>
                                        <span className="font-mono font-bold text-violet-400 text-sm whitespace-nowrap">
                                            {chord.symbol}
                                        </span>
                                        <span className="text-[10px] text-slate-500 mt-1">
                                            {chord.time.toFixed(1)}s
                                        </span>

                                        {/* Tooltip */}
                                        <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block z-10 bg-black/90 text-xs p-2 rounded whitespace-nowrap border border-slate-700">
                                            Notes: {chord.notes.join(', ')} <br />
                                            Duration: {chord.duration.toFixed(2)}s
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-12 bg-slate-800/30 rounded-xl border border-dashed border-slate-700">
                            <p className="text-slate-400">
                                No clear chords detected. Try adding more notes or checking the transcription.
                            </p>
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
