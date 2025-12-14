/**
 * Library Index - Browse all transcribed songs
 */

import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
    Search,
    Grid,
    List,
    Star,
    Music2,
    Clock,
    Loader2,
    CheckCircle2,
    AlertCircle,
    Plus
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { libraryApi, Song } from '../../lib/api'
import { useJobsStore, StoredJob } from '../../lib/jobsStore'
import { useUIStore } from '../../lib/uiStore'

export const Route = createFileRoute('/library/')({ component: LibraryPage })

function LibraryPage() {
    const [search, setSearch] = useState('')
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
    const [favoritesOnly, setFavoritesOnly] = useState(false)
    const { openUploadModal } = useUIStore()

    const { data: songs, isLoading, error } = useQuery({
        queryKey: ['songs', { search, favoritesOnly }],
        queryFn: () => libraryApi.listSongs({
            search: search || undefined,
            favorites_only: favoritesOnly
        }),
    })

    // Active jobs
    const allJobs = useJobsStore((state) => state.jobs)
    const activeJobs = allJobs.filter(
        (j) => ['pending', 'downloading', 'processing', 'analyzing'].includes(j.status)
    );

    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = Math.round(seconds % 60)
        return `${mins}:${String(secs).padStart(2, '0')}`
    }

    return (
        <div className="min-h-screen p-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8 flex justify-between items-end"
            >
                <div>
                    <h1 className="text-3xl font-bold mb-2">Song Library</h1>
                    <p className="text-slate-400">
                        Browse and manage your transcribed songs
                    </p>
                </div>
                <button
                    onClick={openUploadModal}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white rounded-lg shadow-lg shadow-cyan-500/20 transition-all font-medium"
                >
                    <Plus className="w-4 h-4" />
                    New Song
                </button>
            </motion.div>

            {/* Toolbar */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col sm:flex-row gap-4 mb-6"
            >
                {/* Search */}
                <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search songs..."
                        className="w-full pl-12 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all"
                    />
                </div>

                {/* Filters */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setFavoritesOnly(!favoritesOnly)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${favoritesOnly
                            ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                            : 'text-slate-400 hover:text-white bg-slate-800 border border-slate-700'
                            }`}
                    >
                        <Star className={`w-4 h-4 ${favoritesOnly ? 'fill-yellow-400' : ''}`} />
                        Favorites
                    </button>

                    <div className="flex bg-slate-800 border border-slate-700 rounded-lg p-1">
                        <button
                            onClick={() => setViewMode('grid')}
                            className={`p-2 rounded ${viewMode === 'grid' ? 'bg-slate-700 text-white' : 'text-slate-400'}`}
                        >
                            <Grid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={`p-2 rounded ${viewMode === 'list' ? 'bg-slate-700 text-white' : 'text-slate-400'}`}
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </motion.div>

            {/* Content */}
            {isLoading ? (
                <div className="flex items-center justify-center py-20">
                    <div className="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full" />
                </div>
            ) : error ? (
                <div className="glass-card rounded-xl p-8 text-center">
                    <p className="text-red-400">Failed to load songs</p>
                </div>
            ) : (songs && songs.length > 0) || activeJobs.length > 0 ? (
                <AnimatePresence mode="wait">
                    {viewMode === 'grid' ? (
                        <motion.div
                            key="grid"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
                        >
                            {/* Active Jobs First */}
                            {activeJobs.map((job) => (
                                <JobCard key={job.job_id} job={job} />
                            ))}

                            {/* Songs */}
                            {songs?.map((song, index) => (
                                <SongCard key={song.id} song={song} index={index + activeJobs.length} />
                            ))}
                        </motion.div>
                    ) : (
                        <motion.div
                            key="list"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="space-y-2"
                        >
                            {/* Active Jobs First */}
                            {activeJobs.map((job) => (
                                <JobRow key={job.job_id} job={job} />
                            ))}

                            {/* Songs */}
                            {songs?.map((song, index) => (
                                <SongRow key={song.id} song={song} index={index + activeJobs.length} formatDuration={formatDuration} />
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>
            ) : (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="glass-card rounded-xl p-12 text-center"
                >
                    <Music2 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-400 mb-2">
                        {search ? 'No songs match your search' : 'No songs in library'}
                    </h3>
                    <p className="text-slate-500 mb-6">
                        {search ? 'Try a different search term' : 'Upload your first song to get started'}
                    </p>
                    {!search && (
                        <button
                            onClick={openUploadModal}
                            className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-medium rounded-lg transition-colors"
                        >
                            <Plus className="w-5 h-5" />
                            Upload Song
                        </button>
                    )}
                </motion.div>
            )}
        </div>
    )
}

function JobCard({ job }: { job: StoredJob }) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card rounded-xl p-5 border border-cyan-500/30 bg-cyan-500/5 relative overflow-hidden"
        >
            <div className="absolute inset-x-0 bottom-0 h-1 bg-slate-800">
                <div
                    className="h-full bg-cyan-400 transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                />
            </div>

            <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
                    <Loader2 className="w-6 h-6 text-cyan-400 animate-spin" />
                </div>
                <div className="px-2 py-1 rounded bg-cyan-500/20 text-cyan-300 text-xs font-medium">
                    {job.progress}%
                </div>
            </div>

            <h3 className="font-semibold text-white truncate mb-1">
                {job.title || 'Processing Song...'}
            </h3>
            <p className="text-sm text-cyan-300/70 truncate mb-3">
                {job.current_step || 'Initializing...'}
            </p>
        </motion.div>
    )
}

function JobRow({ job }: { job: StoredJob }) {
    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card rounded-lg p-4 flex items-center gap-4 border border-cyan-500/30 bg-cyan-500/5"
        >
            <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
            </div>

            <div className="flex-1 min-w-0">
                <h3 className="font-medium text-white truncate">
                    {job.title || 'Processing Song...'}
                </h3>
                <p className="text-sm text-cyan-300/70 truncate">
                    {job.current_step || 'Initializing...'} • {job.progress}%
                </p>
            </div>
        </motion.div>
    )
}

function SongCard({ song, index }: { song: Song; index: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
        >
            <Link to={`/library/${song.id}`}>
                <div className="glass-card rounded-xl p-5 hover:border-cyan-500/30 transition-all cursor-pointer group">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
                            <Music2 className="w-6 h-6 text-cyan-400" />
                        </div>
                        {song.favorite && (
                            <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                        )}
                    </div>

                    <h3 className="font-semibold text-white truncate group-hover:text-cyan-400 transition-colors mb-1">
                        {song.title}
                    </h3>
                    <p className="text-sm text-slate-500 truncate mb-3">
                        {song.artist || 'Unknown Artist'}
                    </p>

                    <div className="flex items-center gap-3 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {Math.floor(song.duration / 60)}:{String(Math.round(song.duration % 60)).padStart(2, '0')}
                        </span>
                        {song.tempo && <span>{Math.round(song.tempo)} BPM</span>}
                        {song.key_signature && <span>{song.key_signature}</span>}
                    </div>
                </div>
            </Link>
        </motion.div>
    )
}

function SongRow({ song, index, formatDuration }: { song: Song; index: number; formatDuration: (s: number) => string }) {
    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.03 }}
        >
            <Link to={`/library/${song.id}`}>
                <div className="glass-card rounded-lg p-4 flex items-center gap-4 hover:border-cyan-500/30 transition-all cursor-pointer group">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center flex-shrink-0">
                        <Music2 className="w-5 h-5 text-cyan-400" />
                    </div>

                    <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-white truncate group-hover:text-cyan-400 transition-colors">
                            {song.title}
                        </h3>
                        <p className="text-sm text-slate-500 truncate">
                            {song.artist || 'Unknown Artist'}
                        </p>
                    </div>

                    <div className="hidden sm:flex items-center gap-6 text-sm text-slate-500">
                        {song.key_signature && <span className="w-12">{song.key_signature}</span>}
                        {song.tempo && <span className="w-16">{Math.round(song.tempo)} BPM</span>}
                        <span className="w-12 text-right">{formatDuration(song.duration)}</span>
                    </div>

                    {song.favorite && (
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400 flex-shrink-0" />
                    )}
                </div>
            </Link>
        </motion.div>
    )
}
