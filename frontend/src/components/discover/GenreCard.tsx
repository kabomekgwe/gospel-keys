/**
 * Genre Card Component
 * 
 * Card for displaying a genre with song count and featured songs
 */
import { motion } from 'framer-motion';
import { Link } from '@tanstack/react-router';
import { Music2, ChevronRight } from 'lucide-react';

interface GenreCardProps {
    genre: string;
    songCount: number;
    icon?: React.ReactNode;
    gradientFrom?: string;
    gradientTo?: string;
}

const GENRE_COLORS: Record<string, { from: string; to: string }> = {
    'Classical': { from: 'from-amber-500', to: 'to-orange-600' },
    'Jazz': { from: 'from-violet-500', to: 'to-purple-600' },
    'Blues': { from: 'from-blue-500', to: 'to-indigo-600' },
    'Pop': { from: 'from-pink-500', to: 'to-rose-600' },
    'Rock': { from: 'from-red-500', to: 'to-orange-600' },
    'Electronic': { from: 'from-cyan-500', to: 'to-blue-600' },
    'R&B': { from: 'from-fuchsia-500', to: 'to-pink-600' },
    'Gospel': { from: 'from-yellow-500', to: 'to-amber-600' },
    'default': { from: 'from-slate-500', to: 'to-slate-600' },
};

export function GenreCard({
    genre,
    songCount,
    icon,
    gradientFrom,
    gradientTo,
}: GenreCardProps) {
    const colors = GENRE_COLORS[genre] || GENRE_COLORS.default;
    const from = gradientFrom || colors.from;
    const to = gradientTo || colors.to;

    return (
        <Link to="/library" search={{ genre }} className="block">
            <motion.div
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                className="relative overflow-hidden rounded-xl cursor-pointer group"
            >
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${from} ${to} opacity-90`} />

                {/* Pattern Overlay */}
                <div className="absolute inset-0 opacity-10">
                    <svg width="100%" height="100%">
                        <defs>
                            <pattern id={`pattern-${genre}`} x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                                <circle cx="10" cy="10" r="1.5" fill="white" />
                            </pattern>
                        </defs>
                        <rect width="100%" height="100%" fill={`url(#pattern-${genre})`} />
                    </svg>
                </div>

                {/* Content */}
                <div className="relative p-6">
                    <div className="flex items-center justify-between mb-4">
                        {icon || <Music2 className="w-8 h-8 text-white/80" />}
                        <ChevronRight className="w-5 h-5 text-white/60 group-hover:translate-x-1 transition-transform" />
                    </div>

                    <h3 className="text-xl font-bold text-white mb-1">{genre}</h3>
                    <p className="text-white/70 text-sm">
                        {songCount} {songCount === 1 ? 'song' : 'songs'}
                    </p>
                </div>

                {/* Hover glow */}
                <div className="absolute inset-0 bg-white/0 group-hover:bg-white/10 transition-colors" />
            </motion.div>
        </Link>
    );
}
