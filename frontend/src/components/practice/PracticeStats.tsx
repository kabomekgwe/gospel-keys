/**
 * Practice Stats Component
 * 
 * Displays user stats: XP, level, total time, etc.
 */
import { motion } from 'framer-motion';
import { Clock, Music2, Star, TrendingUp } from 'lucide-react';
import { usePracticeStore } from '../../lib/practiceStore';

interface PracticeStatsProps {
    layout?: 'horizontal' | 'vertical' | 'grid';
}

export function PracticeStats({ layout = 'grid' }: PracticeStatsProps) {
    const { xp, level, sessions, dailyHistory } = usePracticeStore();

    // Calculate stats
    const totalPracticeSeconds = dailyHistory.reduce((acc, d) => acc + d.totalSeconds, 0);
    const totalHours = Math.floor(totalPracticeSeconds / 3600);
    const totalMinutes = Math.floor((totalPracticeSeconds % 3600) / 60);
    const totalSessions = sessions.length;
    const uniqueSongs = new Set(sessions.filter((s) => s.songId).map((s) => s.songId)).size;

    // XP to next level (exponential formula)
    const xpToNextLevel = Math.floor(100 * Math.pow(1.5, level - 1));
    const xpProgress = Math.round((xp / xpToNextLevel) * 100);

    const stats = [
        {
            label: 'Level',
            value: level,
            icon: Star,
            color: 'text-amber-400',
            subValue: `${xp}/${xpToNextLevel} XP`,
            progress: xpProgress,
        },
        {
            label: 'Practice Time',
            value: totalHours > 0 ? `${totalHours}h ${totalMinutes}m` : `${totalMinutes}m`,
            icon: Clock,
            color: 'text-cyan-400',
        },
        {
            label: 'Sessions',
            value: totalSessions,
            icon: TrendingUp,
            color: 'text-violet-400',
        },
        {
            label: 'Songs Practiced',
            value: uniqueSongs,
            icon: Music2,
            color: 'text-emerald-400',
        },
    ];

    if (layout === 'horizontal') {
        return (
            <div className="flex items-center gap-6">
                {stats.map((stat) => (
                    <div key={stat.label} className="flex items-center gap-3">
                        <stat.icon className={`w-5 h-5 ${stat.color}`} />
                        <div>
                            <div className="text-lg font-bold text-white">{stat.value}</div>
                            <div className="text-xs text-slate-500">{stat.label}</div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className={`grid ${layout === 'grid' ? 'grid-cols-2 md:grid-cols-4' : 'grid-cols-1'} gap-4`}>
            {stats.map((stat, index) => (
                <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="card p-4"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <div className={`p-2 rounded-lg bg-slate-800 ${stat.color}`}>
                            <stat.icon className="w-5 h-5" />
                        </div>
                        <span className="text-sm text-slate-400">{stat.label}</span>
                    </div>

                    <div className="text-2xl font-bold text-white">{stat.value}</div>

                    {stat.subValue && (
                        <div className="mt-2">
                            <div className="text-xs text-slate-500 mb-1">{stat.subValue}</div>
                            {stat.progress !== undefined && (
                                <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-amber-500 to-yellow-400"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${stat.progress}%` }}
                                        transition={{ duration: 0.5, delay: 0.3 }}
                                    />
                                </div>
                            )}
                        </div>
                    )}
                </motion.div>
            ))}
        </div>
    );
}
