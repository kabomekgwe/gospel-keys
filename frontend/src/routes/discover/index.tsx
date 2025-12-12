/**
 * Discover Page
 * 
 * Browse songs by genre, difficulty, and popularity
 */
import { createFileRoute } from '@tanstack/react-router';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { Compass, Search, Sparkles, Clock, Star } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { libraryApi } from '../../lib/api';
import { GenreCard, DiscoverFilters, TrendingList, type FilterState } from '../../components/discover';
import { SongCard } from '../../components/SongCard';

export const Route = createFileRoute('/discover/')({
    component: DiscoverPage,
});

// Mock genre data (would come from API in production)
const GENRES = [
    { name: 'Classical', count: 24 },
    { name: 'Jazz', count: 18 },
    { name: 'Blues', count: 12 },
    { name: 'Pop', count: 36 },
    { name: 'Rock', count: 22 },
    { name: 'Electronic', count: 15 },
    { name: 'R&B', count: 10 },
    { name: 'Gospel', count: 8 },
];

function DiscoverPage() {
    const [search, setSearch] = useState('');
    const [filters, setFilters] = useState<FilterState>({
        genres: [],
        difficulty: [],
        sortBy: 'recent',
    });

    // Fetch songs from API
    const { data: songs = [], isLoading } = useQuery({
        queryKey: ['songs', 'discover'],
        queryFn: () => libraryApi.listSongs({ limit: 50 }),
    });

    // Filter songs based on search and filters
    const filteredSongs = songs.filter(song => {
        // Search filter
        if (search) {
            const searchLower = search.toLowerCase();
            if (
                !song.title.toLowerCase().includes(searchLower) &&
                !(song.artist || '').toLowerCase().includes(searchLower)
            ) {
                return false;
            }
        }

        // Genre filter (if we had genre data on songs)
        // if (filters.genres.length > 0 && !filters.genres.includes(song.genre)) {
        //   return false;
        // }

        return true;
    });

    // Sort songs
    const sortedSongs = [...filteredSongs].sort((a, b) => {
        switch (filters.sortBy) {
            case 'title':
                return a.title.localeCompare(b.title);
            case 'duration':
                return (b.duration || 0) - (a.duration || 0);
            case 'popular':
                return 0; // Would sort by play count
            case 'recent':
            default:
                return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
        }
    });

    return (
        <div className="min-h-screen p-8 overflow-y-auto">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold text-white flex items-center gap-3 mb-2">
                    <Compass className="w-8 h-8 text-cyan-400" />
                    Discover
                </h1>
                <p className="text-slate-400">
                    Find new songs to learn and practice
                </p>
            </motion.div>

            {/* Search Bar */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="mb-8"
            >
                <div className="relative max-w-xl">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search songs, artists..."
                        className="w-full pl-12 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-cyan-500 outline-none text-lg"
                    />
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column - Filters & Trending */}
                <div className="space-y-6">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <DiscoverFilters
                            genres={GENRES.map(g => g.name)}
                            onFilterChange={setFilters}
                            initialFilters={filters}
                        />
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <TrendingList
                            songs={songs.slice(0, 5)}
                            title="Trending Now"
                        />
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <TrendingList
                            songs={songs.slice(5, 10)}
                            title="Recently Added"
                            icon={<Clock className="w-5 h-5 text-emerald-400" />}
                        />
                    </motion.div>
                </div>

                {/* Right Column - Genres & Songs */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Genre Cards */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-amber-400" />
                            Browse by Genre
                        </h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {GENRES.map((genre, index) => (
                                <motion.div
                                    key={genre.name}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 0.1 + index * 0.05 }}
                                >
                                    <GenreCard
                                        genre={genre.name}
                                        songCount={genre.count}
                                    />
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>

                    {/* Filtered Songs */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                <Star className="w-5 h-5 text-violet-400" />
                                {search ? 'Search Results' : 'All Songs'}
                            </h2>
                            <span className="text-sm text-slate-500">
                                {sortedSongs.length} songs
                            </span>
                        </div>

                        {isLoading ? (
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {[...Array(6)].map((_, i) => (
                                    <div key={i} className="card p-4 animate-pulse">
                                        <div className="w-full aspect-video bg-slate-700 rounded-lg mb-3" />
                                        <div className="h-4 bg-slate-700 rounded w-3/4 mb-2" />
                                        <div className="h-3 bg-slate-700 rounded w-1/2" />
                                    </div>
                                ))}
                            </div>
                        ) : sortedSongs.length > 0 ? (
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {sortedSongs.slice(0, 12).map((song) => (
                                    <SongCard
                                        key={song.id}
                                        song={song}
                                        viewMode="grid"
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="card p-8 text-center">
                                <Search className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                                <p className="text-slate-400">No songs found</p>
                                <p className="text-sm text-slate-500">Try adjusting your filters</p>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
