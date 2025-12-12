/**
 * Practice Goals Component
 * 
 * Progress ring showing daily practice goal completion
 */
import { motion } from 'framer-motion';
import { Pencil, Check } from 'lucide-react';
import { useState } from 'react';
import { usePracticeStore } from '../../lib/practiceStore';

interface PracticeGoalsProps {
    size?: 'sm' | 'md' | 'lg';
    showEdit?: boolean;
}

const GOAL_OPTIONS = [15, 20, 30, 45, 60, 90, 120];

export function PracticeGoals({ size = 'md', showEdit = true }: PracticeGoalsProps) {
    const { todayPracticeSeconds, goal, setGoal, getTodayProgress } = usePracticeStore();
    const [isEditing, setIsEditing] = useState(false);

    const progress = getTodayProgress();
    const isComplete = progress >= 100;
    const todayMinutes = Math.floor(todayPracticeSeconds / 60);
    const todaySeconds = todayPracticeSeconds % 60;

    const sizes = {
        sm: { ring: 80, stroke: 6 },
        md: { ring: 120, stroke: 8 },
        lg: { ring: 160, stroke: 10 },
    };

    const { ring, stroke } = sizes[size];
    const radius = (ring - stroke) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (progress / 100) * circumference;

    return (
        <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-slate-400">Daily Goal</h3>
                {showEdit && (
                    <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                    >
                        <Pencil className="w-4 h-4" />
                    </button>
                )}
            </div>

            {isEditing ? (
                <div className="space-y-3">
                    <p className="text-sm text-slate-400">Set your daily goal:</p>
                    <div className="flex flex-wrap gap-2">
                        {GOAL_OPTIONS.map((mins) => (
                            <button
                                key={mins}
                                onClick={() => {
                                    setGoal({ dailyMinutes: mins });
                                    setIsEditing(false);
                                }}
                                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${goal.dailyMinutes === mins
                                    ? 'bg-cyan-500 text-white'
                                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    }`}
                            >
                                {mins} min
                            </button>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="flex items-center gap-6">
                    {/* Progress Ring */}
                    <div className="relative" style={{ width: ring, height: ring }}>
                        <svg width={ring} height={ring} className="transform -rotate-90">
                            {/* Background ring */}
                            <circle
                                cx={ring / 2}
                                cy={ring / 2}
                                r={radius}
                                fill="none"
                                stroke="currentColor"
                                strokeWidth={stroke}
                                className="text-slate-700"
                            />
                            {/* Progress ring */}
                            <motion.circle
                                cx={ring / 2}
                                cy={ring / 2}
                                r={radius}
                                fill="none"
                                stroke="currentColor"
                                strokeWidth={stroke}
                                strokeLinecap="round"
                                strokeDasharray={circumference}
                                initial={{ strokeDashoffset: circumference }}
                                animate={{ strokeDashoffset }}
                                transition={{ duration: 1, ease: 'easeOut' }}
                                className={isComplete ? 'text-emerald-500' : 'text-cyan-500'}
                            />
                        </svg>

                        {/* Center content */}
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            {isComplete ? (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="text-emerald-500"
                                >
                                    <Check className="w-8 h-8" />
                                </motion.div>
                            ) : (
                                <>
                                    <span className="text-2xl font-bold text-white">{progress}%</span>
                                    <span className="text-xs text-slate-500">complete</span>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="flex-1">
                        <div className="mb-2">
                            <span className="text-2xl font-bold text-white">
                                {todayMinutes}:{String(todaySeconds).padStart(2, '0')}
                            </span>
                            <span className="text-slate-500 text-sm ml-2">
                                / {goal.dailyMinutes} min
                            </span>
                        </div>

                        {isComplete ? (
                            <p className="text-emerald-400 text-sm flex items-center gap-1">
                                <Check className="w-4 h-4" />
                                Goal achieved!
                            </p>
                        ) : (
                            <p className="text-slate-400 text-sm">
                                {Math.max(0, goal.dailyMinutes - todayMinutes)} min left
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
