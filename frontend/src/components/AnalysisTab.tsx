import { BarChart2, Music, Zap, Info } from 'lucide-react';
import { motion } from 'framer-motion';
import { type ChordRegion } from '../lib/api';
import { AnalysisOverview } from './analysis/AnalysisOverview';

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
    // Calculate unique notes from chords
    const uniqueNotes = new Set(
        detectedChords.flatMap(c => c.chord ? [c.chord] : [])
    ).size;

    return (
        <div className="p-6 overflow-y-auto h-full">
            <div className="max-w-6xl mx-auto space-y-8">
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

                {/* Main Analysis View */}
                <AnalysisOverview songId={songId} detectedChords={detectedChords} />
            </div>
        </div>
    );
}
