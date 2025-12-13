/**
 * AI Generator Page
 * 
 * Standalone page for AI-powered music theory generation
 */
import { createFileRoute } from '@tanstack/react-router';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { AIGenerator } from '../../components/generator/AIGenerator';
import { usePiano } from '../../hooks/usePiano';

export const Route = createFileRoute('/generator/')({
    component: GeneratorPage,
});

function GeneratorPage() {
    // Real piano audio for playing chords and scales
    const { playChord } = usePiano();

    const handlePlayChord = (midiNotes: number[]) => {
        playChord(midiNotes, 2.0, 0.5);
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
                    <Sparkles className="w-8 h-8 text-cyan-400" />
                    AI Music Generator
                </h1>
                <p className="text-slate-400">
                    Generate progressions, voicings, and exercises powered by AI
                </p>
            </motion.div>

            {/* Content */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
            >
                <AIGenerator onPlayChord={handlePlayChord} />
            </motion.div>
        </div>
    );
}
