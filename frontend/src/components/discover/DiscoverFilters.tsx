/**
 * Discover Filters Component
 * 
 * Filters for browsing songs by genre, difficulty, duration, etc.
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Filter, X, ChevronDown } from 'lucide-react';

interface DiscoverFiltersProps {
    genres: string[];
    onFilterChange: (filters: FilterState) => void;
    initialFilters?: Partial<FilterState>;
}

export interface FilterState {
    genres: string[];
    difficulty: string[];
    durationMin?: number;
    durationMax?: number;
    sortBy: 'recent' | 'popular' | 'title' | 'duration';
}

const DIFFICULTIES = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];
const SORT_OPTIONS = [
    { value: 'recent', label: 'Recently Added' },
    { value: 'popular', label: 'Most Popular' },
    { value: 'title', label: 'Title A-Z' },
    { value: 'duration', label: 'Duration' },
] as const;

export function DiscoverFilters({
    genres,
    onFilterChange,
    initialFilters,
}: DiscoverFiltersProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [filters, setFilters] = useState<FilterState>({
        genres: [],
        difficulty: [],
        sortBy: 'recent',
        ...initialFilters,
    });

    const updateFilters = (newFilters: Partial<FilterState>) => {
        const updated = { ...filters, ...newFilters };
        setFilters(updated);
        onFilterChange(updated);
    };

    const toggleGenre = (genre: string) => {
        const newGenres = filters.genres.includes(genre)
            ? filters.genres.filter(g => g !== genre)
            : [...filters.genres, genre];
        updateFilters({ genres: newGenres });
    };

    const toggleDifficulty = (diff: string) => {
        const newDiff = filters.difficulty.includes(diff)
            ? filters.difficulty.filter(d => d !== diff)
            : [...filters.difficulty, diff];
        updateFilters({ difficulty: newDiff });
    };

    const clearFilters = () => {
        const cleared: FilterState = {
            genres: [],
            difficulty: [],
            sortBy: 'recent',
        };
        setFilters(cleared);
        onFilterChange(cleared);
    };

    const activeFilterCount = filters.genres.length + filters.difficulty.length;

    return (
        <div className="card p-4">
            {/* Toggle Button */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between text-white"
            >
                <div className="flex items-center gap-2">
                    <Filter className="w-5 h-5 text-cyan-400" />
                    <span className="font-medium">Filters</span>
                    {activeFilterCount > 0 && (
                        <span className="px-2 py-0.5 bg-cyan-500 rounded-full text-xs">
                            {activeFilterCount}
                        </span>
                    )}
                </div>
                <ChevronDown
                    className={`w-5 h-5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''
                        }`}
                />
            </button>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                    >
                        <div className="pt-4 space-y-6">
                            {/* Sort By */}
                            <div>
                                <label className="text-sm font-medium text-slate-400 mb-2 block">
                                    Sort By
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {SORT_OPTIONS.map(option => (
                                        <button
                                            key={option.value}
                                            onClick={() => updateFilters({ sortBy: option.value })}
                                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filters.sortBy === option.value
                                                    ? 'bg-cyan-500 text-white'
                                                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                                }`}
                                        >
                                            {option.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Genres */}
                            <div>
                                <label className="text-sm font-medium text-slate-400 mb-2 block">
                                    Genre
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {genres.map(genre => (
                                        <button
                                            key={genre}
                                            onClick={() => toggleGenre(genre)}
                                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filters.genres.includes(genre)
                                                    ? 'bg-violet-500 text-white'
                                                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                                }`}
                                        >
                                            {genre}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Difficulty */}
                            <div>
                                <label className="text-sm font-medium text-slate-400 mb-2 block">
                                    Difficulty
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {DIFFICULTIES.map(diff => (
                                        <button
                                            key={diff}
                                            onClick={() => toggleDifficulty(diff)}
                                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filters.difficulty.includes(diff)
                                                    ? 'bg-emerald-500 text-white'
                                                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                                }`}
                                        >
                                            {diff}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Clear Filters */}
                            {activeFilterCount > 0 && (
                                <button
                                    onClick={clearFilters}
                                    className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                    Clear all filters
                                </button>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
