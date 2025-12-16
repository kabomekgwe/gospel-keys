/**
 * Theory Curriculum Dashboard
 *
 * Progressive theory learning path with:
 * - Visual progress tree
 * - Prerequisite enforcement
 * - Skill-based unlocking
 * - Integration with Theory Lab
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    CheckCircle2,
    Circle,
    Lock,
    Play,
    BookOpen,
    Award,
    TrendingUp,
    Clock,
    ChevronRight
} from 'lucide-react';

interface TheoryTopic {
    id: string;
    name: string;
    description: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    prerequisites: string[];
    estimated_hours: number;
    completed: boolean;
    locked: boolean;
    progress: number; // 0-100
}

interface TheoryCurriculumProps {
    studentLevel?: 'beginner' | 'intermediate' | 'advanced';
}

const DIFFICULTY_COLORS = {
    beginner: 'from-green-500 to-emerald-500',
    intermediate: 'from-blue-500 to-cyan-500',
    advanced: 'from-purple-500 to-pink-500'
};

const DIFFICULTY_LABELS = {
    beginner: 'Beginner',
    intermediate: 'Intermediate',
    advanced: 'Advanced'
};

export function TheoryCurriculum({ studentLevel = 'beginner' }: TheoryCurriculumProps) {
    const [topics, setTopics] = useState<TheoryTopic[]>([]);
    const [selectedTopic, setSelectedTopic] = useState<TheoryTopic | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [completedCount, setCompletedCount] = useState(0);

    // Fetch curriculum data
    useEffect(() => {
        fetchCurriculum();
    }, [studentLevel]);

    const fetchCurriculum = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`/api/v1/theory-curriculum/path?level=${studentLevel}`);
            const data = await response.json();

            if (data.topics) {
                setTopics(data.topics);
                setCompletedCount(data.topics.filter((t: TheoryTopic) => t.completed).length);
            }
        } catch (error) {
            console.error('Failed to fetch curriculum:', error);
            // Use mock data for now
            setTopics(getMockTopics(studentLevel));
        } finally {
            setIsLoading(false);
        }
    };

    const getMockTopics = (level: string): TheoryTopic[] => {
        const beginner: TheoryTopic[] = [
            {
                id: 'intervals',
                name: 'Intervals',
                description: 'Understanding musical distances between notes',
                difficulty: 'beginner',
                prerequisites: [],
                estimated_hours: 2,
                completed: false,
                locked: false,
                progress: 0
            },
            {
                id: 'major_minor_scales',
                name: 'Major and Minor Scales',
                description: 'The foundation of Western music',
                difficulty: 'beginner',
                prerequisites: ['intervals'],
                estimated_hours: 3,
                completed: false,
                locked: true,
                progress: 0
            },
            {
                id: 'triads',
                name: 'Triads',
                description: 'Building three-note chords',
                difficulty: 'beginner',
                prerequisites: ['major_minor_scales', 'intervals'],
                estimated_hours: 2,
                completed: false,
                locked: true,
                progress: 0
            },
            {
                id: 'basic_progressions',
                name: 'Basic Chord Progressions',
                description: 'Common harmonic sequences',
                difficulty: 'beginner',
                prerequisites: ['triads'],
                estimated_hours: 3,
                completed: false,
                locked: true,
                progress: 0
            }
        ];

        const intermediate: TheoryTopic[] = [
            {
                id: 'seventh_chords',
                name: 'Seventh Chords',
                description: 'Adding the 7th degree for richer harmony',
                difficulty: 'intermediate',
                prerequisites: ['triads', 'basic_progressions'],
                estimated_hours: 3,
                completed: false,
                locked: false,
                progress: 0
            },
            {
                id: 'modes',
                name: 'Modes',
                description: 'Seven modal scales from major scale',
                difficulty: 'intermediate',
                prerequisites: ['major_minor_scales'],
                estimated_hours: 4,
                completed: false,
                locked: true,
                progress: 0
            }
        ];

        const advanced: TheoryTopic[] = [
            {
                id: 'neo_riemannian_theory',
                name: 'Neo-Riemannian Theory',
                description: 'PLR transformations and Tonnetz lattice',
                difficulty: 'advanced',
                prerequisites: ['voice_leading_rules', 'triads'],
                estimated_hours: 5,
                completed: false,
                locked: false,
                progress: 0
            },
            {
                id: 'negative_harmony',
                name: 'Negative Harmony',
                description: 'Mirror-image harmonic relationships',
                difficulty: 'advanced',
                prerequisites: ['modal_interchange', 'voice_leading_rules'],
                estimated_hours: 4,
                completed: false,
                locked: true,
                progress: 0
            }
        ];

        if (level === 'beginner') return beginner;
        if (level === 'intermediate') return intermediate;
        return advanced;
    };

    const handleStartTopic = (topic: TheoryTopic) => {
        if (topic.locked) return;
        setSelectedTopic(topic);
    };

    const totalHours = topics.reduce((sum, t) => sum + t.estimated_hours, 0);
    const completedHours = topics
        .filter(t => t.completed)
        .reduce((sum, t) => sum + t.estimated_hours, 0);
    const progressPercentage = topics.length > 0
        ? Math.round((completedCount / topics.length) * 100)
        : 0;

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-gray-400">Loading curriculum...</div>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Sidebar - Progress Overview */}
            <div className="space-y-6">
                {/* Overall Progress */}
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-purple-400" />
                        Your Progress
                    </h3>

                    <div className="space-y-4">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-gray-400">Completion</span>
                                <span className="text-sm font-medium text-white">
                                    {progressPercentage}%
                                </span>
                            </div>
                            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progressPercentage}%` }}
                                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
                            <div>
                                <div className="text-2xl font-bold text-white">
                                    {completedCount}
                                </div>
                                <div className="text-xs text-gray-400">Topics Completed</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">
                                    {completedHours}h
                                </div>
                                <div className="text-xs text-gray-400">
                                    of {totalHours}h total
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Level Badge */}
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <Award className="w-5 h-5 text-cyan-400" />
                        Current Level
                    </h3>

                    <div className={`
                        inline-flex items-center gap-2 px-4 py-2 rounded-lg
                        bg-gradient-to-r ${DIFFICULTY_COLORS[studentLevel]}
                        bg-opacity-20 border border-current text-white
                    `}>
                        <span className="font-medium">
                            {DIFFICULTY_LABELS[studentLevel]}
                        </span>
                    </div>

                    <p className="mt-4 text-sm text-gray-400">
                        Complete topics to unlock new ones and advance your theory knowledge.
                    </p>
                </div>
            </div>

            {/* Main Content - Topic Tree */}
            <div className="lg:col-span-2 space-y-6">
                <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                    <h2 className="text-2xl font-bold text-white mb-2">
                        Theory Learning Path
                    </h2>
                    <p className="text-gray-400 mb-6">
                        Follow the structured path to master music theory concepts
                    </p>

                    {/* Topic List */}
                    <div className="space-y-3">
                        {topics.map((topic, index) => (
                            <motion.div
                                key={topic.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                            >
                                <button
                                    onClick={() => handleStartTopic(topic)}
                                    disabled={topic.locked}
                                    className={`
                                        w-full p-5 rounded-xl border-2 transition-all text-left
                                        ${topic.completed
                                            ? 'bg-green-500/10 border-green-500/30'
                                            : topic.locked
                                                ? 'bg-gray-900/50 border-gray-700 opacity-50 cursor-not-allowed'
                                                : 'bg-gray-900/50 border-gray-700 hover:border-purple-500/50 hover:bg-purple-500/5'
                                        }
                                    `}
                                >
                                    <div className="flex items-start gap-4">
                                        {/* Status Icon */}
                                        <div className="flex-shrink-0 mt-1">
                                            {topic.completed ? (
                                                <CheckCircle2 className="w-6 h-6 text-green-500" />
                                            ) : topic.locked ? (
                                                <Lock className="w-6 h-6 text-gray-600" />
                                            ) : (
                                                <Circle className="w-6 h-6 text-purple-500" />
                                            )}
                                        </div>

                                        {/* Topic Info */}
                                        <div className="flex-1">
                                            <div className="flex items-start justify-between mb-2">
                                                <div>
                                                    <h3 className="text-white font-semibold">
                                                        {topic.name}
                                                    </h3>
                                                    <p className="text-sm text-gray-400 mt-1">
                                                        {topic.description}
                                                    </p>
                                                </div>

                                                {!topic.locked && !topic.completed && (
                                                    <ChevronRight className="w-5 h-5 text-gray-400" />
                                                )}
                                            </div>

                                            {/* Progress Bar (if in progress) */}
                                            {!topic.completed && topic.progress > 0 && (
                                                <div className="mb-3">
                                                    <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                                        <div
                                                            style={{ width: `${topic.progress}%` }}
                                                            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                                        />
                                                    </div>
                                                </div>
                                            )}

                                            {/* Meta Info */}
                                            <div className="flex items-center gap-4 text-xs text-gray-500">
                                                <div className="flex items-center gap-1">
                                                    <Clock className="w-3 h-3" />
                                                    <span>{topic.estimated_hours}h</span>
                                                </div>

                                                {topic.prerequisites.length > 0 && (
                                                    <div className="flex items-center gap-1">
                                                        <BookOpen className="w-3 h-3" />
                                                        <span>
                                                            Requires {topic.prerequisites.length} prerequisite{topic.prerequisites.length > 1 ? 's' : ''}
                                                        </span>
                                                    </div>
                                                )}

                                                {!topic.locked && !topic.completed && (
                                                    <div className="ml-auto flex items-center gap-1 text-purple-400">
                                                        <Play className="w-3 h-3" />
                                                        <span>Start Learning</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </button>
                            </motion.div>
                        ))}
                    </div>

                    {topics.length === 0 && (
                        <div className="text-center py-12 text-gray-500">
                            <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
                            <p>No topics available for this level</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Topic Detail Modal (placeholder) */}
            <AnimatePresence>
                {selectedTopic && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6"
                        onClick={() => setSelectedTopic(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-gray-800 rounded-xl border border-gray-700 p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
                        >
                            <h2 className="text-2xl font-bold text-white mb-4">
                                {selectedTopic.name}
                            </h2>
                            <p className="text-gray-400 mb-6">
                                {selectedTopic.description}
                            </p>

                            <div className="space-y-4">
                                <div className="flex items-center gap-4 text-sm text-gray-400">
                                    <div className="flex items-center gap-2">
                                        <Clock className="w-4 h-4" />
                                        <span>{selectedTopic.estimated_hours} hours</span>
                                    </div>
                                    <div className={`
                                        px-3 py-1 rounded-full text-xs font-medium
                                        bg-gradient-to-r ${DIFFICULTY_COLORS[selectedTopic.difficulty]}
                                        bg-opacity-20 text-white
                                    `}>
                                        {DIFFICULTY_LABELS[selectedTopic.difficulty]}
                                    </div>
                                </div>

                                <button className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white font-semibold transition-all">
                                    Start Learning
                                </button>

                                <button
                                    onClick={() => setSelectedTopic(null)}
                                    className="w-full px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
                                >
                                    Close
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
