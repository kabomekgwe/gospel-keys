/**
 * Streak Counter Component
 * 
 * Displays current practice streak with fire animation
 */
import { motion } from 'framer-motion';
import { Flame, Trophy, Target } from 'lucide-react';
import { usePracticeStore } from '../../lib/practiceStore';

interface StreakCounterProps {
    size?: 'sm' | 'md' | 'lg';
    showDetails?: boolean;
}

export function StreakCounter({ size = 'md', showDetails = true }: StreakCounterProps) {
    const { currentStreak, longestStreak } = usePracticeStore();

    const sizeClasses = {
        sm: 'text-2xl',
        md: 'text-4xl',
        lg: 'text-6xl',
    };

    const iconSizes = {
        sm: 'w-6 h-6',
        md: 'w-10 h-10',
        lg: 'w-16 h-16',
    };

    const isOnFire = currentStreak >= 3;
    const isMilestone = [7, 14, 30, 60, 100, 365].includes(currentStreak);

    return (
        <div className="card p-6 text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
                <motion.div
                    animate={isOnFire ? { scale: [1, 1.1, 1] } : {}}
                    transition={{ duration: 0.5, repeat: Infinity }}
                    className={`relative ${iconSizes[size]}`}
                >
                    <Flame
                        className={`${iconSizes[size]} ${isOnFire ? 'text-orange-500' : 'text-slate-500'
                            }`}
                    />
                    {isOnFire && (
                        <motion.div
                            className="absolute inset-0 blur-md bg-orange-500/30 rounded-full"
                            animate={{ opacity: [0.5, 0.8, 0.5] }}
                            transition={{ duration: 1, repeat: Infinity }}
                        />
                    )}
                </motion.div>

                <motion.span
                    key={currentStreak}
                    initial={{ scale: 1.2, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className={`font-bold text-white ${sizeClasses[size]}`}
                >
                    {currentStreak}
                </motion.span>
            </div>

            <p className="text-slate-400 text-sm mb-1">
                {currentStreak === 0
                    ? 'Start your streak today!'
                    : currentStreak === 1
                        ? '1 day streak'
                        : `${currentStreak} day streak`}
            </p>

            {isMilestone && (
                <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="mt-3 inline-flex items-center gap-2 px-3 py-1 bg-amber-500/20 text-amber-400 rounded-full text-xs"
                >
                    <Trophy className="w-3 h-3" />
                    Milestone reached!
                </motion.div>
            )}

            {showDetails && (
                <div className="mt-4 pt-4 border-t border-slate-700/50 flex items-center justify-center gap-6">
                    <div className="text-center">
                        <div className="text-lg font-bold text-white">{longestStreak}</div>
                        <div className="text-xs text-slate-500">Longest streak</div>
                    </div>
                    <div className="h-8 w-px bg-slate-700" />
                    <div className="text-center">
                        <Target className="w-4 h-4 text-cyan-400 mx-auto mb-1" />
                        <div className="text-xs text-slate-500">Keep going!</div>
                    </div>
                </div>
            )}
        </div>
    );
}
