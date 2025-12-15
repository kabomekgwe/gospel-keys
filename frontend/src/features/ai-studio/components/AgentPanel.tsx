import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Sparkles, User } from 'lucide-react';
import { useState, useEffect } from 'react';

interface AgentMessage {
    id: string;
    agentName: string;
    role: string;
    message: string;
    timestamp: Date;
    type: 'insight' | 'suggestion' | 'critique';
}

interface Agent {
    name: string;
    role: string;
    avatar: string; // Emoji
    color: string;
}

const AGENTS: Agent[] = [
    { name: 'Claude', role: 'Music Theorist', avatar: '🎼', color: 'text-violet-400' },
    { name: 'Gemini', role: 'Creative Director', avatar: '🎨', color: 'text-cyan-400' },
    { name: 'GospelBot', role: 'Genre Specialist', avatar: '🎹', color: 'text-amber-400' },
];

export function AgentPanel() {
    const [messages, setMessages] = useState<AgentMessage[]>([]);

    useEffect(() => {
        // Simulate initial greeting
        const timer = setTimeout(() => {
            setMessages([
                {
                    id: '1',
                    agentName: 'Claude',
                    role: 'Music Theorist',
                    message: "Welcome to the studio! I'm here to help with jazz theory usage.",
                    timestamp: new Date(),
                    type: 'insight'
                }
            ]);
        }, 1000);
        return () => clearTimeout(timer);
    }, []);

    // Simulate "Typing" or "Thinking" occasionally? 
    // For now, just a static list.

    return (
        <div className="w-80 bg-slate-900 border-l border-slate-800 h-full flex flex-col">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <User className="w-5 h-5 text-indigo-400" />
                        Party Mode
                    </h2>
                    <p className="text-xs text-slate-500">AI Agents Active</p>
                </div>
                <div className="flex -space-x-2">
                    {AGENTS.map((agent) => (
                        <div key={agent.name} className="w-8 h-8 rounded-full bg-slate-800 border-2 border-slate-900 flex items-center justify-center text-sm" title={agent.name}>
                            {agent.avatar}
                        </div>
                    ))}
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <AnimatePresence>
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/50"
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg bg-slate-800 rounded-full w-8 h-8 flex items-center justify-center">
                                    {AGENTS.find(a => a.name === msg.agentName)?.avatar || '🤖'}
                                </span>
                                <div>
                                    <span className={`font-semibold text-sm ${AGENTS.find(a => a.name === msg.agentName)?.color || 'text-white'}`}>
                                        {msg.agentName}
                                    </span>
                                    <span className="block text-xs text-slate-500">{msg.role}</span>
                                </div>
                                <span className="ml-auto text-[10px] text-slate-600">
                                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                            <p className="text-sm text-slate-300 leading-relaxed">
                                {msg.message}
                            </p>
                            {msg.type === 'suggestion' && (
                                <div className="mt-2 text-xs bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded inline-flex items-center gap-1">
                                    <Sparkles className="w-3 h-3" />
                                    Suggestion
                                </div>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            <div className="p-4 border-t border-slate-800">
                <button className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm transition-colors flex items-center justify-center gap-2">
                    <MessageSquare className="w-4 h-4" />
                    Ask the Team
                </button>
            </div>
        </div>
    );
}
