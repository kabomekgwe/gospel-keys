import { useState } from 'react';
import { Bot } from 'lucide-react';
import { StudioSidebar, ToolId } from './components/StudioSidebar';
import { AgentPanel } from './components/AgentPanel';
import { motion, AnimatePresence } from 'framer-motion';
import { usePiano } from '../../hooks/usePiano';
import { ProgressionTool } from './tools/ProgressionTool';
import { ReharmonizerTool } from './tools/ReharmonizerTool';
import { VoicingTool } from './tools/VoicingTool';
import { ExerciseTool } from './tools/ExerciseTool';
import { LicksTool } from './tools/LicksTool';
import { ArrangerTool } from './tools/ArrangerTool';
import { AnalysisTool } from './tools/AnalysisTool';
import { TutorTool } from './tools/TutorTool';

// Placeholder tools
// Removed placeholders

export function MusicAIStudio() {
    const [activeTool, setActiveTool] = useState<ToolId>('progression');
    const [showAgentPanel, setShowAgentPanel] = useState(true);

    // Joint audio context for the studio
    const { playChord } = usePiano();

    const handlePlayChord = (midiNotes: number[]) => {
        playChord(midiNotes, 2.0, 0.5);
    };

    const renderTool = () => {
        switch (activeTool) {
            case 'progression': return <ProgressionTool onPlayChord={handlePlayChord} />;
            case 'voicing': return <VoicingTool onPlayChord={handlePlayChord} />;
            case 'exercise': return <ExerciseTool />;
            case 'licks': return <LicksTool />;
            case 'analysis': return <AnalysisTool onPlayChord={handlePlayChord} />;
            case 'arranger': return <ArrangerTool />;
            case 'tutor': return <TutorTool onPlayChord={handlePlayChord} />;
            case 'reharmonizer': return <ReharmonizerTool onPlayChord={handlePlayChord} />;
            default: return <ProgressionTool onPlayChord={handlePlayChord} />;
        }
    };

    return (
        <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black">
            {/* Sidebar */}
            <StudioSidebar activeTool={activeTool} onSelectTool={setActiveTool} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 bg-transparent relative overflow-hidden">
                <header className="flex items-center justify-between px-6 py-4 bg-slate-900/50 border-b border-slate-800">
                    <h1 className="text-xl font-bold text-white capitalize">{activeTool.replace('_', ' ')} Tool</h1>
                    <button
                        onClick={() => setShowAgentPanel(!showAgentPanel)}
                        className={`p-2 rounded-lg transition-colors ${showAgentPanel ? 'bg-cyan-500/20 text-cyan-400' : 'hover:bg-slate-800 text-slate-400'}`}
                        title="Toggle AI Agents"
                    >
                        <Bot className="w-5 h-5" />
                    </button>
                </header>
                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeTool}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.2 }}
                            className="h-full"
                        >
                            {renderTool()}
                        </motion.div>
                    </AnimatePresence>
                </div>
            </div>

            {/* Agent Panel (Right Sidebar) */}
            {showAgentPanel && <AgentPanel />}
        </div>
    );
}
