import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { curriculumApi, type DailyPracticeItem, type CurriculumExercise, type PerformanceAnalysis } from '../../lib/api';
import { useState } from 'react';
import { ExerciseAudioPlayer } from '../../components/curriculum/ExerciseAudioPlayer';
import { TrendingUp, BookOpen, Lightbulb, X } from 'lucide-react';

export const Route = createFileRoute('/curriculum/daily')({
    component: DailyPracticePage,
});

function DailyPracticePage() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
    const [showCompletionDialog, setShowCompletionDialog] = useState(false);
    const [selectedExercise, setSelectedExercise] = useState<CurriculumExercise | null>(null);
    const [showPerformanceInsights, setShowPerformanceInsights] = useState(true);

    const { data: practiceQueue, isLoading, error } = useQuery({
        queryKey: ['curriculum', 'daily'],
        queryFn: curriculumApi.getDailyPractice,
    });

    // Load performance analysis for insights banner
    const { data: performanceAnalysis } = useQuery<PerformanceAnalysis>({
        queryKey: ['performance', 'analysis', 7],
        queryFn: () => curriculumApi.getPerformanceAnalysis(7),
        enabled: !!practiceQueue,
    });

    const completeExerciseMutation = useMutation({
        mutationFn: ({ exerciseId, quality }: { exerciseId: string; quality: number }) =>
            curriculumApi.completeExercise(exerciseId, { quality }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['curriculum', 'daily'] });
            setShowCompletionDialog(false);
            setSelectedExercise(null);
            // Move to next exercise
            if (practiceQueue && currentExerciseIndex < practiceQueue.items.length - 1) {
                setCurrentExerciseIndex(currentExerciseIndex + 1);
            }
        },
    });

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6 flex items-center justify-center">
                <div className="bg-gray-800/50 p-8 rounded-xl border border-gray-700 text-center">
                    <h2 className="text-xl font-semibold text-white mb-4">No Active Curriculum</h2>
                    <p className="text-gray-400 mb-6">Create a curriculum to start your daily practice.</p>
                    <button
                        onClick={() => navigate({ to: '/curriculum' })}
                        className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-500 transition"
                    >
                        Create Curriculum
                    </button>
                </div>
            </div>
        );
    }

    if (!practiceQueue || practiceQueue.items.length === 0) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6 flex items-center justify-center">
                <div className="bg-gray-800/50 p-8 rounded-xl border border-gray-700 text-center">
                    <div className="text-6xl mb-4">🎉</div>
                    <h2 className="text-2xl font-semibold text-white mb-4">All Caught Up!</h2>
                    <p className="text-gray-400 mb-6">You've completed all exercises for today.</p>
                    <button
                        onClick={() => navigate({ to: '/curriculum' })}
                        className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-500 transition"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const currentItem = practiceQueue.items[currentExerciseIndex];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <button
                        onClick={() => navigate({ to: '/curriculum' })}
                        className="text-gray-400 hover:text-white transition flex items-center gap-2"
                    >
                        ← Back to Dashboard
                    </button>
                    <div className="text-right">
                        <p className="text-white font-medium">{practiceQueue.curriculum_title}</p>
                        <p className="text-gray-400 text-sm">Week {practiceQueue.current_week}</p>
                    </div>
                </div>

                {/* Performance Insights Banner */}
                {showPerformanceInsights && performanceAnalysis && (
                    <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border border-purple-500/30 rounded-xl p-6 mb-6">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-3">
                                <TrendingUp className="w-6 h-6 text-purple-400" />
                                <h3 className="text-xl font-semibold text-white">Your Progress</h3>
                            </div>
                            <button
                                onClick={() => setShowPerformanceInsights(false)}
                                className="text-gray-400 hover:text-white transition"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <p className="text-gray-400 text-sm mb-1">Completion Rate</p>
                                <p className="text-3xl font-bold text-white">
                                    {Math.round(performanceAnalysis.completion_rate * 100)}%
                                </p>
                                <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                                    <div
                                        className={`h-2 rounded-full ${
                                            performanceAnalysis.completion_rate >= 0.8
                                                ? 'bg-green-500'
                                                : performanceAnalysis.completion_rate >= 0.6
                                                ? 'bg-yellow-500'
                                                : 'bg-orange-500'
                                        }`}
                                        style={{ width: `${performanceAnalysis.completion_rate * 100}%` }}
                                    />
                                </div>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <p className="text-gray-400 text-sm mb-1">Avg Quality Score</p>
                                <p className="text-3xl font-bold text-white">
                                    {performanceAnalysis.avg_quality_score.toFixed(1)}
                                </p>
                                <p className="text-sm text-gray-400 mt-1">out of 5.0</p>
                            </div>

                            <div className="bg-gray-900/50 rounded-lg p-4">
                                <p className="text-gray-400 text-sm mb-1">Mastered</p>
                                <p className="text-3xl font-bold text-white">
                                    {performanceAnalysis.mastered_exercises.length}
                                </p>
                                <p className="text-sm text-gray-400 mt-1">exercises</p>
                            </div>
                        </div>

                        {/* Adaptive Recommendations */}
                        {performanceAnalysis.recommended_actions.length > 0 && (
                            <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4">
                                <div className="flex items-start gap-3">
                                    <Lightbulb className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                                    <div className="flex-1">
                                        <p className="text-white font-medium mb-2">
                                            Curriculum Adapted Based on Your Performance
                                        </p>
                                        <p className="text-gray-300 text-sm">
                                            Your practice load and difficulty have been adjusted to optimize your learning.
                                            View details on the{' '}
                                            <button
                                                onClick={() => navigate({ to: '/curriculum/performance' })}
                                                className="text-blue-400 hover:text-blue-300 underline"
                                            >
                                                Performance Dashboard
                                            </button>
                                            .
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Stats Bar */}
                <div className="grid grid-cols-4 gap-4 mb-8">
                    <StatCard
                        label="Exercises"
                        value={practiceQueue.items.length.toString()}
                        icon="📚"
                    />
                    <StatCard
                        label="Overdue"
                        value={practiceQueue.overdue_count.toString()}
                        icon="⚠️"
                        highlight={practiceQueue.overdue_count > 0}
                    />
                    <StatCard
                        label="New"
                        value={practiceQueue.new_count.toString()}
                        icon="✨"
                    />
                    <StatCard
                        label="Est. Time"
                        value={`${practiceQueue.total_estimated_minutes} min`}
                        icon="⏱️"
                    />
                </div>

                {/* Exercise Queue */}
                <div className="grid md:grid-cols-3 gap-6">
                    {/* Exercise List */}
                    <div className="md:col-span-1 bg-gray-800/50 rounded-xl border border-gray-700 p-4 h-fit">
                        <h3 className="text-white font-semibold mb-4">Practice Queue</h3>
                        <div className="space-y-2">
                            {practiceQueue.items.map((item, index) => (
                                <button
                                    key={item.exercise.id}
                                    onClick={() => setCurrentExerciseIndex(index)}
                                    className={`w-full text-left p-3 rounded-lg transition ${index === currentExerciseIndex
                                            ? 'bg-purple-600/30 border border-purple-500'
                                            : 'bg-gray-700/30 hover:bg-gray-700/50'
                                        }`}
                                >
                                    <div className="flex items-center gap-2">
                                        <PriorityBadge priority={item.priority} />
                                        <span className="text-white text-sm truncate">{item.exercise.title}</span>
                                    </div>
                                    <p className="text-gray-400 text-xs mt-1">{item.module_title}</p>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Current Exercise */}
                    <div className="md:col-span-2">
                        <ExerciseCard
                            item={currentItem}
                            onComplete={() => {
                                setSelectedExercise(currentItem.exercise);
                                setShowCompletionDialog(true);
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Completion Dialog */}
            {showCompletionDialog && selectedExercise && (
                <CompletionDialog
                    exercise={selectedExercise}
                    onClose={() => setShowCompletionDialog(false)}
                    onSubmit={(quality) => {
                        completeExerciseMutation.mutate({
                            exerciseId: selectedExercise.id,
                            quality,
                        });
                    }}
                    isSubmitting={completeExerciseMutation.isPending}
                />
            )}
        </div>
    );
}

function StatCard({ label, value, icon, highlight }: {
    label: string;
    value: string;
    icon: string;
    highlight?: boolean;
}) {
    return (
        <div className={`p-4 rounded-xl border ${highlight ? 'bg-orange-900/30 border-orange-500' : 'bg-gray-800/50 border-gray-700'
            }`}>
            <div className="flex items-center gap-2 mb-1">
                <span className="text-xl">{icon}</span>
                <span className={`text-2xl font-bold ${highlight ? 'text-orange-400' : 'text-white'}`}>{value}</span>
            </div>
            <p className="text-gray-400 text-sm">{label}</p>
        </div>
    );
}

function PriorityBadge({ priority }: { priority: number }) {
    const config = {
        1: { bg: 'bg-red-500', label: '!' },
        2: { bg: 'bg-yellow-500', label: '•' },
        3: { bg: 'bg-green-500', label: '+' },
    }[priority] || { bg: 'bg-gray-500', label: '?' };

    return (
        <span className={`w-5 h-5 flex items-center justify-center rounded-full text-white text-xs ${config.bg}`}>
            {config.label}
        </span>
    );
}

function ExerciseCard({ item, onComplete }: { item: DailyPracticeItem; onComplete: () => void }) {
    const { exercise } = item;

    return (
        <div className="space-y-4">
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
                {/* Header */}
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <span className="text-purple-400 text-sm">{item.module_title} → {item.lesson_title}</span>
                        <h2 className="text-2xl font-bold text-white mt-1">{exercise.title}</h2>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-sm ${exercise.difficulty === 'beginner' ? 'bg-green-900/50 text-green-400' :
                                exercise.difficulty === 'intermediate' ? 'bg-yellow-900/50 text-yellow-400' :
                                    'bg-red-900/50 text-red-400'
                            }`}>
                            {exercise.difficulty}
                        </span>
                    </div>
                </div>

                {/* View Tutorial Button */}
                {item.lesson_id && (
                    <button
                        onClick={() => window.open(`/curriculum/tutorial/${item.lesson_id}`, '_blank')}
                        className="w-full mb-4 flex items-center justify-center gap-2 px-4 py-3 bg-blue-900/50 border border-blue-500/30 text-blue-300 rounded-lg hover:bg-blue-900/70 transition"
                    >
                        <BookOpen className="w-5 h-5" />
                        View Lesson Tutorial
                    </button>
                )}

            {/* Description */}
            {exercise.description && (
                <p className="text-gray-300 mb-6">{exercise.description}</p>
            )}

            {/* Exercise Content */}
            <div className="bg-gray-900/50 rounded-lg p-4 mb-6">
                <h3 className="text-white font-medium mb-3">Exercise Content</h3>
                <ExerciseContentDisplay content={exercise.content} type={exercise.exercise_type} />
            </div>

            {/* Meta Info */}
            <div className="flex gap-4 text-gray-400 text-sm mb-6">
                <span>⏱️ {exercise.estimated_duration_minutes} min</span>
                {exercise.target_bpm && <span>🎵 {exercise.target_bpm} BPM</span>}
                <span>📊 Practiced {exercise.practice_count} times</span>
            </div>

                {/* Action Button */}
                <button
                    onClick={onComplete}
                    className="w-full py-4 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-500 transition"
                >
                    Mark as Completed
                </button>
            </div>

            {/* Audio Player */}
            <ExerciseAudioPlayer
                exerciseId={exercise.id}
                exerciseTitle={exercise.title}
            />
        </div>
    );
}

function ExerciseContentDisplay({ content, type }: { content: CurriculumExercise['content']; type: string }) {
    if (type === 'progression' && content.chords) {
        return (
            <div>
                <div className="flex gap-2 flex-wrap mb-3">
                    {content.chords.map((chord, i) => (
                        <span key={i} className="px-4 py-2 bg-purple-900/50 text-purple-300 rounded-lg font-mono text-lg">
                            {chord}
                        </span>
                    ))}
                </div>
                {content.roman_numerals && (
                    <div className="flex gap-2 flex-wrap text-gray-400">
                        {content.roman_numerals.map((num, i) => (
                            <span key={i} className="px-4 py-1 bg-gray-700/50 rounded text-sm">
                                {num}
                            </span>
                        ))}
                    </div>
                )}
                {content.key && <p className="text-gray-400 mt-2">Key: {content.key}</p>}
            </div>
        );
    }

    if (type === 'scale' && content.scale) {
        return (
            <div className="text-gray-300">
                <p><strong>Scale:</strong> {content.scale}</p>
                {content.key && <p><strong>Key:</strong> {content.key}</p>}
                {content.octaves && <p><strong>Octaves:</strong> {content.octaves}</p>}
            </div>
        );
    }

    if (type === 'voicing' && content.chord) {
        return (
            <div>
                <span className="px-4 py-2 bg-purple-900/50 text-purple-300 rounded-lg font-mono text-lg inline-block mb-2">
                    {content.chord}
                </span>
                {content.voicing_type && <p className="text-gray-400">Type: {content.voicing_type}</p>}
                {content.notes && (
                    <div className="mt-2">
                        <span className="text-gray-400">Notes: </span>
                        {content.notes.map((note, i) => (
                            <span key={i} className="px-2 py-1 bg-gray-700 text-white rounded mx-1">
                                {note}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        );
    }

    // Default display
    return (
        <pre className="text-gray-300 text-sm overflow-auto">
            {JSON.stringify(content, null, 2)}
        </pre>
    );
}

function CompletionDialog({
    exercise,
    onClose,
    onSubmit,
    isSubmitting
}: {
    exercise: CurriculumExercise;
    onClose: () => void;
    onSubmit: (quality: number) => void;
    isSubmitting: boolean;
}) {
    const qualityOptions = [
        { value: 0, label: 'Blackout', description: 'Complete failure', color: 'bg-red-600' },
        { value: 1, label: 'Wrong', description: 'Incorrect but remembered something', color: 'bg-red-500' },
        { value: 2, label: 'Difficult', description: 'Got it with serious difficulty', color: 'bg-orange-500' },
        { value: 3, label: 'Hard', description: 'Got it with hesitation', color: 'bg-yellow-500' },
        { value: 4, label: 'Good', description: 'Got it after brief thinking', color: 'bg-green-500' },
        { value: 5, label: 'Perfect', description: 'Instant recall', color: 'bg-green-600' },
    ];

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 max-w-md w-full">
                <h3 className="text-xl font-semibold text-white mb-2">Rate Your Practice</h3>
                <p className="text-gray-400 mb-6">{exercise.title}</p>

                <div className="space-y-2 mb-6">
                    {qualityOptions.map(({ value, label, description, color }) => (
                        <button
                            key={value}
                            onClick={() => !isSubmitting && onSubmit(value)}
                            disabled={isSubmitting}
                            className={`w-full flex items-center gap-4 p-3 rounded-lg border border-gray-600 hover:border-purple-500 transition disabled:opacity-50`}
                        >
                            <span className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${color}`}>
                                {value}
                            </span>
                            <div className="text-left">
                                <span className="text-white font-medium">{label}</span>
                                <p className="text-gray-400 text-sm">{description}</p>
                            </div>
                        </button>
                    ))}
                </div>

                <button
                    onClick={onClose}
                    disabled={isSubmitting}
                    className="w-full py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition disabled:opacity-50"
                >
                    Cancel
                </button>
            </div>
        </div>
    );
}
