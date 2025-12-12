
import React from 'react';
import { motion } from 'framer-motion';
import { Frown, Meh, Smile, Zap } from 'lucide-react';

interface PracticeFeedbackProps {
    onRate: (quality: number) => void;
    onCancel: () => void;
}

export function PracticeFeedback({ onRate, onCancel }: PracticeFeedbackProps) {
    const ratings = [
        { value: 1, label: 'Again', icon: Frown, color: 'text-red-400', bg: 'bg-red-500/20', border: 'border-red-500/50' },
        { value: 3, label: 'Hard', icon: Meh, color: 'text-amber-400', bg: 'bg-amber-500/20', border: 'border-amber-500/50' },
        { value: 4, label: 'Good', icon: Smile, color: 'text-emerald-400', bg: 'bg-emerald-500/20', border: 'border-emerald-500/50' },
        { value: 5, label: 'Easy', icon: Zap, color: 'text-blue-400', bg: 'bg-blue-500/20', border: 'border-blue-500/50' },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
        >
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-md w-full shadow-2xl">
                <h3 className="text-xl font-bold text-white text-center mb-2">
                    How was that?
                </h3>
                <p className="text-slate-400 text-center mb-6 text-sm">
                    Rate your performance to schedule the next review.
                </p>

                <div className="grid grid-cols-2 gap-3 mb-6">
                    {ratings.map((rating) => (
                        <button
                            key={rating.value}
                            onClick={() => onRate(rating.value)}
                            className={`flex flex-col items-center justify-center p-4 rounded-lg border transition-all hover:scale-105 active:scale-95 ${rating.bg} ${rating.border}`}
                        >
                            <rating.icon className={`w-8 h-8 mb-2 ${rating.color}`} />
                            <span className={`font-medium ${rating.color}`}>{rating.label}</span>
                        </button>
                    ))}
                </div>

                <div className="text-center">
                    <button
                        onClick={onCancel}
                        className="text-slate-500 hover:text-white text-sm underline"
                    >
                        Skip Feedback
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
