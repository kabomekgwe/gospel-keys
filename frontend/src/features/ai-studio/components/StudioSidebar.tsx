import {
    Music,
    Layers,
    Dumbbell,
    Search,
    Zap,
    Mic2,
    Sparkles,
    Piano
} from 'lucide-react';
import { motion } from 'framer-motion';

export type ToolId = 'progression' | 'voicing' | 'exercise' | 'analysis' | 'licks' | 'arranger' | 'reharmonizer';

interface StudioSidebarProps {
    activeTool: ToolId;
    onSelectTool: (tool: ToolId) => void;
}

const TOOLS = [
    {
        id: 'progression',
        name: 'Progression',
        icon: <Music className="w-5 h-5" />,
        color: 'text-cyan-400',
        bg: 'bg-cyan-500/10',
        border: 'border-cyan-500/30'
    },
    {
        id: 'reharmonizer',
        name: 'Reharmonizer',
        icon: <Sparkles className="w-5 h-5" />,
        color: 'text-purple-400',
        bg: 'bg-purple-500/10',
        border: 'border-purple-500/30'
    },
    {
        id: 'voicing',
        name: 'Voicings',
        icon: <Layers className="w-5 h-5" />,
        color: 'text-violet-400',
        bg: 'bg-violet-500/10',
        border: 'border-violet-500/30'
    },
    {
        id: 'arranger',
        name: 'Arranger',
        icon: <Piano className="w-5 h-5" />,
        color: 'text-indigo-400',
        bg: 'bg-indigo-500/10',
        border: 'border-indigo-500/30'
    },
    {
        id: 'licks',
        name: 'Licks',
        icon: <Zap className="w-5 h-5" />,
        color: 'text-pink-400',
        bg: 'bg-pink-500/10',
        border: 'border-pink-500/30'
    },
    {
        id: 'exercise',
        name: 'Exercises',
        icon: <Dumbbell className="w-5 h-5" />,
        color: 'text-amber-400',
        bg: 'bg-amber-500/10',
        border: 'border-amber-500/30'
    },
    {
        id: 'analysis',
        name: 'Analysis',
        icon: <Search className="w-5 h-5" />,
        color: 'text-emerald-400',
        bg: 'bg-emerald-500/10',
        border: 'border-emerald-500/30'
    }
] as const;

export function StudioSidebar({ activeTool, onSelectTool }: StudioSidebarProps) {
    return (
        <div className="w-64 bg-slate-900 border-r border-slate-800 h-full flex flex-col">
            <div className="p-4 border-b border-slate-800">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Mic2 className="w-6 h-6 text-cyan-400" />
                    AI Studio
                </h2>
                <p className="text-xs text-slate-500 mt-1">Gospel Keys Intelligence</p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {TOOLS.map((tool) => {
                    const isActive = activeTool === tool.id;
                    return (
                        <button
                            key={tool.id}
                            onClick={() => onSelectTool(tool.id as ToolId)}
                            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 group text-left
                                ${isActive
                                    ? `bg-slate-800 border ${tool.border}`
                                    : 'hover:bg-slate-800/50 border border-transparent'
                                }`}
                        >
                            <div className={`p-2 rounded-lg ${isActive ? tool.bg : 'bg-slate-800'} ${tool.color} transition-colors`}>
                                {tool.icon}
                            </div>
                            <div className="flex-1">
                                <span className={`block font-medium ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-white'}`}>
                                    {tool.name}
                                </span>
                            </div>
                            {isActive && (
                                <motion.div
                                    layoutId="active-indicator"
                                    className={`w-1 h-8 rounded-full ${tool.color.replace('text-', 'bg-')}`}
                                />
                            )}
                        </button>
                    );
                })}
            </div>

            <div className="p-4 border-t border-slate-800">
                <div className="p-3 bg-slate-800/50 rounded-lg text-xs text-slate-400 text-center">
                    v2.0.0 • AI Powered
                </div>
            </div>
        </div>
    );
}
