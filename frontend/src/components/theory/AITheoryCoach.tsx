/**
 * AI Theory Coach Component
 *
 * Chatbot-style interface for theory questions with:
 * - Natural language theory Q&A
 * - Explanations tailored to skill level
 * - Practice exercise requests
 * - Visual examples with interactive piano
 * - Audio demonstrations
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Volume2, User, Bot, Loader2, Music, Sparkles } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    examples?: {
        type: 'chord' | 'progression' | 'scale';
        data: any;
    }[];
}

interface AITheoryCoachProps {
    studentLevel?: 'beginner' | 'intermediate' | 'advanced';
    initialTopic?: string;
}

export function AITheoryCoach({
    studentLevel = 'intermediate',
    initialTopic
}: AITheoryCoachProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Add welcome message on mount
    useEffect(() => {
        if (messages.length === 0) {
            setMessages([{
                id: '1',
                role: 'assistant',
                content: `Hi! I'm your AI Theory Coach. I can help you understand music theory concepts, explain techniques, and suggest practice exercises. What would you like to learn about today?`,
                timestamp: new Date()
            }]);
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/theory-tools/ai-coach/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: userMessage.content,
                    student_level: studentLevel,
                    conversation_history: messages.slice(-5).map(m => ({
                        role: m.role,
                        content: m.content
                    }))
                })
            });

            const data = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.answer || 'Sorry, I could not process that question.',
                timestamp: new Date(),
                examples: data.examples
            };

            setMessages(prev => [...prev, assistantMessage]);

        } catch (error) {
            console.error('Failed to get AI response:', error);

            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const quickQuestions = [
        "What is a tritone substitution?",
        "Explain Neo-Riemannian transformations",
        "How does negative harmony work?",
        "What are Coltrane Changes?",
        "Explain voice leading rules"
    ];

    const handleQuickQuestion = (question: string) => {
        setInput(question);
    };

    return (
        <div className="flex flex-col h-full max-h-[800px] bg-gray-800/50 rounded-xl border border-gray-700">
            {/* Header */}
            <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-700">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                    <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h3 className="text-white font-semibold">AI Theory Coach</h3>
                    <p className="text-sm text-gray-400">
                        Ask me anything about music theory
                    </p>
                </div>
                <div className="ml-auto px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full text-sm text-blue-400">
                    {studentLevel} level
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <AnimatePresence initial={false}>
                    {messages.map((message) => (
                        <motion.div
                            key={message.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            {/* Avatar */}
                            <div className={`
                                w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
                                ${message.role === 'user'
                                    ? 'bg-cyan-500/20 text-cyan-400'
                                    : 'bg-purple-500/20 text-purple-400'}
                            `}>
                                {message.role === 'user' ? (
                                    <User className="w-5 h-5" />
                                ) : (
                                    <Bot className="w-5 h-5" />
                                )}
                            </div>

                            {/* Message Content */}
                            <div className={`
                                flex-1 max-w-[80%]
                                ${message.role === 'user' ? 'text-right' : ''}
                            `}>
                                <div className={`
                                    inline-block px-4 py-3 rounded-lg
                                    ${message.role === 'user'
                                        ? 'bg-cyan-500/20 border border-cyan-500/30 text-white'
                                        : 'bg-gray-900/50 border border-gray-700 text-gray-300'}
                                `}>
                                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                                        {message.content}
                                    </p>

                                    {/* Examples */}
                                    {message.examples && message.examples.length > 0 && (
                                        <div className="mt-3 space-y-2">
                                            {message.examples.map((example, idx) => (
                                                <div
                                                    key={idx}
                                                    className="p-3 bg-gray-800/50 rounded-lg border border-gray-600"
                                                >
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Music className="w-4 h-4 text-purple-400" />
                                                        <span className="text-xs text-gray-400 uppercase">
                                                            {example.type} Example
                                                        </span>
                                                    </div>
                                                    <pre className="text-xs text-gray-300 font-mono">
                                                        {JSON.stringify(example.data, null, 2)}
                                                    </pre>
                                                    <button className="mt-2 flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-500 rounded text-white text-xs transition-colors">
                                                        <Volume2 className="w-3 h-3" />
                                                        Play Example
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                <div className="mt-1 text-xs text-gray-500">
                                    {message.timestamp.toLocaleTimeString([], {
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </div>
                            </div>
                        </motion.div>
                    ))}

                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex gap-3"
                        >
                            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
                                <Bot className="w-5 h-5 text-purple-400" />
                            </div>
                            <div className="px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-lg">
                                <div className="flex items-center gap-2 text-gray-400">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span className="text-sm">Thinking...</span>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions (show if no messages yet) */}
            {messages.length <= 1 && (
                <div className="px-6 pb-4">
                    <p className="text-sm text-gray-400 mb-3">Quick questions:</p>
                    <div className="flex flex-wrap gap-2">
                        {quickQuestions.map((question, idx) => (
                            <button
                                key={idx}
                                onClick={() => handleQuickQuestion(question)}
                                className="px-3 py-2 bg-gray-700/50 hover:bg-gray-700 border border-gray-600 rounded-lg text-sm text-gray-300 transition-colors"
                            >
                                {question}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a theory question..."
                        disabled={isLoading}
                        className="flex-1 px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors disabled:opacity-50"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-lg text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Send className="w-5 h-5" />
                        )}
                        Send
                    </button>
                </div>

                <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                    <Sparkles className="w-4 h-4" />
                    <span>Powered by AI - explanations adapt to your {studentLevel} level</span>
                </div>
            </form>
        </div>
    );
}
