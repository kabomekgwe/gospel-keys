import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Lightbulb,
    BookOpen,
    Send
} from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    type?: 'text' | 'card';
    relatedConcept?: {
        title: string;
        description: string;
    };
}

interface TutorToolProps {
    onPlayChord?: (notes: number[]) => void;
}

export function TutorTool({ }: TutorToolProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Hi! I'm your AI Music Tutor. I can explain music theory concepts, analyze chord progressions, or answer your questions about the song. Try selecting a chord or asking me something!",
            type: 'text'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = () => {
        if (!inputValue.trim()) return;

        const newUserMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            type: 'text'
        };

        setMessages(prev => [...prev, newUserMessage]);
        setInputValue('');

        // Mock AI response for now
        setTimeout(() => {
            const response: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "That's a great question! In gospel music, we often use secondary dominants to create tension. For example, a V/V chord pulls strongly to the V chord.",
                type: 'text',
                relatedConcept: {
                    title: 'Secondary Dominants',
                    description: 'A major triad or dominant 7th chord built on the 5th degree of another chord.'
                }
            };
            setMessages(prev => [...prev, response]);
        }, 1000);
    };

    const suggestedTopics = [
        "Why does this ii-V-I work?",
        "Explain the Tritone Substitution",
        "What scale can I solo with?",
        "How to voice this for spread?"
    ];

    return (
        <div className="h-full flex flex-col bg-slate-900/50">
            {/* Header / Context Panel */}
            <div className="p-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-indigo-500/20 rounded-lg">
                        <BookOpen className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-white">Music Theory Tutor</h2>
                        <p className="text-sm text-slate-400">Interactive explanations & insights</p>
                    </div>
                </div>

                {/* Suggested Topics Chips */}
                <div className="flex flex-wrap gap-2">
                    {suggestedTopics.map((topic, i) => (
                        <button
                            key={i}
                            onClick={() => setInputValue(topic)}
                            className="text-xs px-3 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
                        >
                            {topic}
                        </button>
                    ))}
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                <AnimatePresence initial={false}>
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
                                {/* Message Bubble */}
                                <div
                                    className={`
                                        p-3 rounded-2xl text-sm leading-relaxed
                                        ${msg.role === 'user'
                                            ? 'bg-cyan-600 text-white rounded-tr-sm'
                                            : 'bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700'
                                        }
                                    `}
                                >
                                    {msg.content}
                                </div>

                                {/* Concept Card (if applicable) */}
                                {msg.relatedConcept && (
                                    <div className="bg-slate-800/80 border border-indigo-500/30 rounded-xl p-3 w-full backdrop-blur-sm">
                                        <div className="flex items-center gap-2 mb-1">
                                            <Lightbulb className="w-4 h-4 text-amber-400" />
                                            <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider">Concept</span>
                                        </div>
                                        <h4 className="font-semibold text-white mb-1">{msg.relatedConcept.title}</h4>
                                        <p className="text-xs text-slate-400">{msg.relatedConcept.description}</p>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-slate-900 border-t border-slate-800">
                <div className="relative">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Ask about harmony, scales, or theory..."
                        className="w-full bg-slate-800 text-white placeholder-slate-500 rounded-xl py-3 pl-4 pr-12 border border-slate-700 focus:border-cyan-500 focus:outline-none transition-colors"
                    />
                    <button
                        onClick={handleSendMessage}
                        disabled={!inputValue.trim()}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-cyan-600 rounded-lg text-white hover:bg-cyan-500 disabled:opacity-50 disabled:hover:bg-cyan-600 transition-colors"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
