/**
 * Practice Dashboard Page
 * 
 * Main practice hub with:
 * - Daily streak tracking
 * - Practice goals and progress
 * - Session history charts
 * - XP and level progression
 */
import { createFileRoute, Link } from '@tanstack/react-router';
import { motion } from 'framer-motion';
import {
    Dumbbell,
    Play,
    Music2,
    ChevronRight,
    Flame,
    Calendar,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { usePracticeStore } from '../../lib/practiceStore';
import { libraryApi } from '../../lib/api';
import { StreakCounter, PracticeGoals, PracticeStats, SessionHistoryChart } from '../../components/practice';

export const Route = createFileRoute('/practice/')({
    component: PracticeDashboard,
});

function PracticeDashboard() {
    const { sessions, currentStreak, todayPracticeSeconds, goal } = usePracticeStore();

    // Get recent songs for quick access
    const { data: recentSongs } = useQuery({
        queryKey: ['songs', 'recent'],
        queryFn: () => libraryApi.listSongs({ limit: 5 }),
    });

    // Get recent practice sessions
    const recentSessions = sessions.slice(0, 5);

    return (
        <div className="min-h-screen p-8 overflow-y-auto">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold text-white flex items-center gap-3 mb-2">
                    <Dumbbell className="w-8 h-8 text-cyan-400" />
                    Practice Dashboard
                </h1>
                <p className="text-slate-400">
                    Track your progress and build your skills
                </p>
            </motion.div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Streak and Goals */}
                <div className="space-y-6">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <StreakCounter size="md" showDetails />
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <PracticeGoals size="md" showEdit />
                    </motion.div>

                    {/* Quick Start */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="card p-6"
                    >
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Play className="w-5 h-5 text-emerald-400" />
                            Quick Start
                        </h3>

                        {recentSongs && recentSongs.length > 0 ? (
                            <div className="space-y-2">
                                {recentSongs.slice(0, 3).map((song) => (
                                    <Link
                                        key={song.id}
                                        to="/library/$songId/practice"
                                        params={{ songId: song.id }}
                                        className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors group"
                                    >
                                        <div className="w-10 h-10 rounded-lg bg-slate-700 flex items-center justify-center">
                                            <Music2 className="w-5 h-5 text-cyan-400" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-white truncate group-hover:text-cyan-400 transition-colors">
                                                {song.title}
                                            </p>
                                            <p className="text-sm text-slate-500 truncate">
                                                {song.artist || 'Unknown Artist'}
                                            </p>
                                        </div>
                                        <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
                                    </Link>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-4">
                                <Music2 className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                                <p className="text-slate-500 text-sm">No songs yet</p>
                                <Link
                                    to="/upload"
                                    className="text-cyan-400 text-sm hover:underline"
                                >
                                    Upload a song
                                </Link>
                            </div>
                        )}
                    </motion.div>
                </div>

                {/* Right Column - Charts and Stats */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Stats */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <PracticeStats layout="grid" />
                    </motion.div>

                    {/* History Chart */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <SessionHistoryChart defaultView="bar" defaultRange="week" />
                    </motion.div>

                    {/* Recent Sessions */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="card p-6"
                    >
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Calendar className="w-5 h-5 text-violet-400" />
                            Recent Sessions
                        </h3>

                        {recentSessions.length > 0 ? (
                            <div className="space-y-3">
                                {recentSessions.map((session) => (
                                    <div
                                        key={session.id}
                                        className="flex items-center gap-4 p-3 rounded-lg bg-slate-800/50"
                                    >
                                        <div className="w-10 h-10 rounded-lg bg-slate-700 flex items-center justify-center">
                                            <Music2 className="w-5 h-5 text-cyan-400" />
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-medium text-white">
                                                {session.songTitle || 'Practice Session'}
                                            </p>
                                            <p className="text-sm text-slate-500">
                                                {new Date(session.startTime).toLocaleDateString()} •{' '}
                                                {Math.floor(session.durationSeconds / 60)} min
                                            </p>
                                        </div>
                                        {session.tempoMultiplier !== 1 && (
                                            <span className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-400">
                                                {session.tempoMultiplier}× speed
                                            </span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8">
                                <Dumbbell className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                                <p className="text-slate-500">No practice sessions yet</p>
                                <p className="text-slate-600 text-sm">Start practicing to see your history</p>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>

            {/* Motivation Banner */}
            {currentStreak === 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="mt-8 card p-6 bg-gradient-to-r from-cyan-500/10 to-violet-500/10 border-cyan-500/30"
                >
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-cyan-500/20 rounded-xl">
                            <Flame className="w-8 h-8 text-cyan-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white">Start Your Streak Today! 🔥</h3>
                            <p className="text-slate-400">
                                Practice just {Math.max(0, Math.ceil((goal.dailyMinutes * 60 - todayPracticeSeconds) / 60))} more minutes to reach your daily goal and start building your streak.
                            </p>
                        </div>
                        <Link
                            to="/library"
                            className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-medium rounded-lg transition-colors"
                        >
                            Start Practice
                        </Link>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
