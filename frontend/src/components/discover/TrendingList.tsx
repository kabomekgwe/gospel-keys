/**
 * Trending List Component
 * 
 * Display trending/popular songs
 */
import { motion } from 'framer-motion';
import { Link } from '@tanstack/react-router';
import { TrendingUp, Clock, Play, Music2 } from 'lucide-react';
import type { Song } from '../../lib/api';

interface TrendingListProps {
    songs: Song[];
    title?: string;
    icon?: React.ReactNode;
    maxItems?: number;
}

export function TrendingList({
    songs,
    title = 'Trending Now',
    icon = <TrendingUp className="w-5 h-5 text-cyan-400" />,
    maxItems = 5,
}: TrendingListProps) {
    const displaySongs = songs.slice(0, maxItems);

    if (displaySongs.length === 0) {
        return (
            <div className="card p-6 text-center">
                <Music2 className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                <p className="text-slate-500">No songs available</p>
            </div>
        );
    }

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                {icon}
                {title}
            </h3>

            <div className="space-y-3">
                {displaySongs.map((song, index) => (
                    <motion.div
                        key={song.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <Link
                            to="/library/$songId"
                            params={{ songId: song.id }}
                            className="flex items-center gap-4 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors group"
                        >
                            {/* Rank */}
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold ${index === 0 ? 'bg-amber-500/20 text-amber-400' :
                                    index === 1 ? 'bg-slate-400/20 text-slate-300' :
                                        index === 2 ? 'bg-orange-600/20 text-orange-400' :
                                            'bg-slate-700 text-slate-400'
                                }`}>
                                {index + 1}
                            </div>

                            {/* Thumbnail placeholder */}
                            <div className="w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center relative overflow-hidden">
                                <Music2 className="w-6 h-6 text-slate-500" />
                                <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Play className="w-5 h-5 text-white" />
                                </div>
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0">
                                <p className="font-medium text-white truncate group-hover:text-cyan-400 transition-colors">
                                    {song.title}
                                </p>
                                <p className="text-sm text-slate-500 truncate">
                                    {song.artist || 'Unknown Artist'}
                                </p>
                            </div>

                            {/* Duration */}
                            {song.duration && (
                                <div className="flex items-center gap-1 text-sm text-slate-500">
                                    <Clock className="w-4 h-4" />
                                    {Math.floor(song.duration / 60)}:{String(song.duration % 60).padStart(2, '0')}
                                </div>
                            )}
                        </Link>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
