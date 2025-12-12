/**
 * Song Card Component
 * 
 * Thumbnail-style card for displaying song in library grid/list
 */
import { Link } from '@tanstack/react-router';
import { motion } from 'framer-motion';
import { Clock, Key, Timer, Heart, Music2, MoreVertical, Play } from 'lucide-react';
import { useState } from 'react';
import type { Song } from '../lib/api';

export interface SongCardProps {
    song: Song;
    viewMode?: 'grid' | 'list';
    onFavoriteToggle?: (songId: string) => void;
    onPlay?: (songId: string) => void;
}

function formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function SongCard({ song, viewMode = 'grid', onFavoriteToggle, onPlay }: SongCardProps) {
    const [isHovered, setIsHovered] = useState(false);

    if (viewMode === 'list') {
        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-colors group"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                {/* Play button / Icon */}
                <div className="relative w-12 h-12 flex-shrink-0">
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-violet-500/20 rounded-lg flex items-center justify-center">
                        <Music2 className="w-6 h-6 text-cyan-400" />
                    </div>
                    {isHovered && onPlay && (
                        <motion.button
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            onClick={(e) => {
                                e.preventDefault();
                                onPlay(song.id);
                            }}
                            className="absolute inset-0 bg-cyan-500 rounded-lg flex items-center justify-center"
                        >
                            <Play className="w-5 h-5 text-white ml-0.5" />
                        </motion.button>
                    )}
                </div>

                {/* Title & Artist */}
                <Link
                    to={`/library/${song.id}`}
                    className="flex-1 min-w-0"
                >
                    <h3 className="text-white font-medium truncate group-hover:text-cyan-400 transition-colors">
                        {song.title}
                    </h3>
                    {song.artist && (
                        <p className="text-slate-400 text-sm truncate">{song.artist}</p>
                    )}
                </Link>

                {/* Metadata */}
                <div className="flex items-center gap-4 text-sm text-slate-400">
                    {song.key_signature && (
                        <span className="hidden md:flex items-center gap-1">
                            <Key className="w-4 h-4" />
                            {song.key_signature}
                        </span>
                    )}

                    {song.tempo && (
                        <span className="hidden lg:flex items-center gap-1">
                            <Timer className="w-4 h-4" />
                            {song.tempo}
                        </span>
                    )}

                    <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatDuration(song.duration)}
                    </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={(e) => {
                            e.preventDefault();
                            onFavoriteToggle?.(song.id);
                        }}
                        className={`p-2 rounded-lg transition-colors ${song.favorite
                                ? 'text-red-400 bg-red-500/10'
                                : 'text-slate-400 hover:text-red-400 hover:bg-slate-700'
                            }`}
                    >
                        <Heart className={`w-4 h-4 ${song.favorite ? 'fill-current' : ''}`} />
                    </motion.button>

                    <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                        <MoreVertical className="w-4 h-4" />
                    </button>
                </div>
            </motion.div>
        );
    }

    // Grid view
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ y: -4 }}
            className="relative group"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <Link to={`/library/${song.id}`}>
                <div className="card overflow-hidden">
                    {/* Thumbnail area */}
                    <div className="relative aspect-video bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center overflow-hidden">
                        {/* Decorative piano keys */}
                        <div className="absolute inset-0 opacity-20">
                            <svg viewBox="0 0 100 60" className="w-full h-full">
                                {[0, 15, 30, 45, 60, 75, 90].map((x, i) => (
                                    <rect
                                        key={i}
                                        x={x}
                                        y="0"
                                        width="14"
                                        height="60"
                                        fill="white"
                                        stroke="#1e293b"
                                        strokeWidth="0.5"
                                    />
                                ))}
                                {[10, 25, 55, 70, 85].map((x, i) => (
                                    <rect
                                        key={i}
                                        x={x}
                                        y="0"
                                        width="9"
                                        height="35"
                                        fill="#1e293b"
                                    />
                                ))}
                            </svg>
                        </div>

                        {/* Center icon */}
                        <div className="relative z-10">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500/30 to-violet-500/30 flex items-center justify-center backdrop-blur-sm border border-white/10">
                                <Music2 className="w-8 h-8 text-cyan-400" />
                            </div>
                        </div>

                        {/* Play overlay on hover */}
                        {isHovered && onPlay && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="absolute inset-0 bg-black/50 flex items-center justify-center"
                            >
                                <motion.button
                                    initial={{ scale: 0.8 }}
                                    animate={{ scale: 1 }}
                                    onClick={(e) => {
                                        e.preventDefault();
                                        onPlay(song.id);
                                    }}
                                    className="w-14 h-14 rounded-full bg-cyan-500 flex items-center justify-center shadow-lg shadow-cyan-500/30"
                                >
                                    <Play className="w-6 h-6 text-white ml-1" />
                                </motion.button>
                            </motion.div>
                        )}

                        {/* Duration badge */}
                        <div className="absolute bottom-2 right-2 px-2 py-0.5 bg-black/60 rounded text-xs text-white font-mono">
                            {formatDuration(song.duration)}
                        </div>

                        {/* Favorite button */}
                        <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                                e.preventDefault();
                                onFavoriteToggle?.(song.id);
                            }}
                            className={`absolute top-2 right-2 p-2 rounded-full transition-colors ${song.favorite
                                    ? 'bg-red-500/80 text-white'
                                    : 'bg-black/40 text-white/70 hover:bg-red-500/80 hover:text-white opacity-0 group-hover:opacity-100'
                                }`}
                        >
                            <Heart className={`w-4 h-4 ${song.favorite ? 'fill-current' : ''}`} />
                        </motion.button>
                    </div>

                    {/* Info */}
                    <div className="p-4">
                        <h3 className="text-white font-medium truncate mb-1 group-hover:text-cyan-400 transition-colors">
                            {song.title}
                        </h3>
                        {song.artist && (
                            <p className="text-slate-400 text-sm truncate mb-3">{song.artist}</p>
                        )}

                        {/* Tags */}
                        <div className="flex items-center gap-2 flex-wrap">
                            {song.key_signature && (
                                <span className="flex items-center gap-1 px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-300">
                                    <Key className="w-3 h-3" />
                                    {song.key_signature}
                                </span>
                            )}
                            {song.tempo && (
                                <span className="flex items-center gap-1 px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-300">
                                    <Timer className="w-3 h-3" />
                                    {song.tempo}
                                </span>
                            )}
                            {song.difficulty && (
                                <span className="px-2 py-0.5 bg-cyan-500/20 rounded text-xs text-cyan-300">
                                    {song.difficulty}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            </Link>
        </motion.div>
    );
}
