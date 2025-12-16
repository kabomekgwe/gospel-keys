import { createFileRoute, Link } from '@tanstack/react-router';
import { useLesson, useCompleteExercise } from '../hooks/useCurriculum';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
    ChevronLeft,
    Clock,
    CheckCircle,
    Play,
    BookOpen,
    Music,
    Target,
    Star,
    Repeat
} from 'lucide-react';
import type { CurriculumExercise } from '../types/curriculum';

export const Route = createFileRoute('/lessons/$lessonId')({
    component: LessonDetailPage,
});

function LessonDetailPage() {
    const { lessonId } = Route.useParams();
    const { data: lesson, isLoading, error } = useLesson(lessonId);
    const completeExercise = useCompleteExercise();

    if (isLoading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="animate-pulse space-y-6">
                    <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
                    <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
                    <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4"></div>
                    <div className="grid gap-4 mt-8">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-32 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error || !lesson) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center py-16">
                    <div className="text-6xl mb-4">📖</div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                        Lesson Not Found
                    </h2>
                    <p className="text-slate-600 dark:text-slate-400 mb-6">
                        The lesson you're looking for doesn't exist or has been removed.
                    </p>
                    <Button asChild variant="outline">
                        <Link to="/curriculum">
                            <ChevronLeft className="size-4 mr-2" />
                            Back to Curriculums
                        </Link>
                    </Button>
                </div>
            </div>
        );
    }

    const completedExercises = lesson.exercises.filter((e) => e.is_mastered).length;
    const totalExercises = lesson.exercises.length;
    const progressPercent = totalExercises > 0 ? Math.round((completedExercises / totalExercises) * 100) : 0;

    const handleCompleteExercise = async (exerciseId: string, quality: number) => {
        try {
            await completeExercise.mutateAsync({
                exerciseId,
                request: { quality }
            });
        } catch (err) {
            console.error('Failed to complete exercise:', err);
        }
    };

    const getExerciseTypeIcon = (type: string) => {
        switch (type) {
            case 'scale':
            case 'chord':
            case 'voicing':
                return <Music className="size-4" />;
            case 'progression':
            case 'lick':
                return <Play className="size-4" />;
            case 'ear_training':
                return <Target className="size-4" />;
            case 'rhythm':
                return <Repeat className="size-4" />;
            default:
                return <BookOpen className="size-4" />;
        }
    };

    const getDifficultyColor = (difficulty: number) => {
        if (difficulty <= 3) return 'text-green-600 dark:text-green-400';
        if (difficulty <= 6) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-red-600 dark:text-red-400';
    };

    return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
            {/* Back Navigation */}
            <Button asChild variant="ghost" className="mb-6 -ml-2">
                <Link to="/modules/$moduleId" params={{ moduleId: lesson.module_id }}>
                    <ChevronLeft className="size-4 mr-1" />
                    Back to Module
                </Link>
            </Button>

            {/* Lesson Header */}
            <div className="mb-8">
                <div className="flex items-start justify-between gap-4 mb-4">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline">Week {lesson.week_number}</Badge>
                            {lesson.is_completed && (
                                <Badge variant="completed">
                                    <CheckCircle className="size-3 mr-1" />
                                    Completed
                                </Badge>
                            )}
                        </div>
                        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                            {lesson.title}
                        </h1>
                        <p className="text-lg text-slate-600 dark:text-slate-400">
                            {lesson.description}
                        </p>
                    </div>
                </div>

                {/* Lesson Stats */}
                <div className="flex flex-wrap gap-4 text-sm text-slate-600 dark:text-slate-400 mb-6">
                    <div className="flex items-center gap-1.5">
                        <Clock className="size-4" />
                        <span>{lesson.estimated_duration_minutes} min</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <Target className="size-4" />
                        <span>{totalExercises} Exercises</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <CheckCircle className="size-4 text-green-500" />
                        <span>{completedExercises} Mastered</span>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-600 dark:text-slate-400">Lesson Progress</span>
                        <span className="font-semibold text-slate-900 dark:text-white">{progressPercent}%</span>
                    </div>
                    <Progress value={progressPercent} className="h-2" />
                </div>
            </div>

            {/* Concepts/Theory Section */}
            {lesson.concepts && lesson.concepts.length > 0 && (
                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <BookOpen className="size-5 text-purple-500" />
                            Key Concepts
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-wrap gap-2">
                            {lesson.concepts.map((concept, idx) => (
                                <Badge key={idx} variant="default" className="text-sm">
                                    {concept}
                                </Badge>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Theory Content */}
            {lesson.theory_content && Object.keys(lesson.theory_content).length > 0 && (
                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle className="text-lg">Theory</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="prose dark:prose-invert max-w-none">
                            {lesson.theory_content.explanation && (
                                <p>{lesson.theory_content.explanation}</p>
                            )}
                            {lesson.theory_content.examples && (
                                <div className="mt-4">
                                    <h4 className="font-semibold">Examples:</h4>
                                    <ul className="list-disc pl-5">
                                        {lesson.theory_content.examples.map((example: string, idx: number) => (
                                            <li key={idx}>{example}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Exercises List */}
            <div className="space-y-4">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">Exercises</h2>

                {lesson.exercises.length === 0 ? (
                    <Card className="text-center py-8">
                        <CardContent>
                            <p className="text-slate-600 dark:text-slate-400">
                                No exercises available yet for this lesson.
                            </p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {lesson.exercises.map((exercise, idx) => (
                            <ExerciseCard
                                key={exercise.id}
                                exercise={exercise}
                                index={idx}
                                onComplete={handleCompleteExercise}
                                isCompleting={completeExercise.isPending}
                                getTypeIcon={getExerciseTypeIcon}
                                getDifficultyColor={getDifficultyColor}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

interface ExerciseCardProps {
    exercise: CurriculumExercise;
    index: number;
    onComplete: (exerciseId: string, quality: number) => void;
    isCompleting: boolean;
    getTypeIcon: (type: string) => React.ReactNode;
    getDifficultyColor: (difficulty: number) => string;
}

function ExerciseCard({
    exercise,
    index,
    onComplete,
    isCompleting,
    getTypeIcon,
    getDifficultyColor
}: ExerciseCardProps) {
    return (
        <Card className={`transition-all hover:shadow-md ${exercise.is_mastered ? 'border-green-200 dark:border-green-800/50 bg-green-50/30 dark:bg-green-900/10' : ''
            }`}>
            <CardContent className="py-5">
                <div className="flex items-start gap-4">
                    {/* Exercise Number & Status */}
                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${exercise.is_mastered
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                        : 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
                        }`}>
                        {exercise.is_mastered ? (
                            <CheckCircle className="size-5" />
                        ) : (
                            <span className="font-semibold">{index + 1}</span>
                        )}
                    </div>

                    {/* Exercise Info */}
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-slate-900 dark:text-white">
                                {exercise.title}
                            </h3>
                            {exercise.is_mastered && (
                                <Badge variant="completed" className="text-xs">
                                    Mastered
                                </Badge>
                            )}
                        </div>

                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                            {exercise.description}
                        </p>

                        {/* Exercise Meta */}
                        <div className="flex flex-wrap items-center gap-3 text-xs">
                            <Badge variant="outline" className="gap-1">
                                {getTypeIcon(exercise.exercise_type)}
                                {exercise.exercise_type.replace('_', ' ')}
                            </Badge>
                            <span className={`font-medium ${getDifficultyColor(exercise.difficulty)}`}>
                                Difficulty: {exercise.difficulty}/10
                            </span>
                            <span className="text-slate-500 dark:text-slate-400">
                                ~{exercise.estimated_duration_minutes} min
                            </span>
                            {exercise.target_bpm && (
                                <span className="text-slate-500 dark:text-slate-400">
                                    {exercise.target_bpm} BPM
                                </span>
                            )}
                            {exercise.practice_count > 0 && (
                                <span className="text-slate-500 dark:text-slate-400">
                                    Practiced {exercise.practice_count}x
                                </span>
                            )}
                            {exercise.best_score !== undefined && exercise.best_score !== null && (
                                <span className="flex items-center gap-1 text-yellow-600 dark:text-yellow-400">
                                    <Star className="size-3" />
                                    Best: {exercise.best_score}%
                                </span>
                            )}
                        </div>

                        {/* Exercise Content Preview */}
                        {exercise.content?.instructions && (
                            <div className="mt-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                                <p className="text-sm text-slate-700 dark:text-slate-300">
                                    {exercise.content.instructions}
                                </p>
                            </div>
                        )}

                        {exercise.content?.tips && exercise.content.tips.length > 0 && (
                            <div className="mt-2">
                                <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Tips:</p>
                                <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-1">
                                    {exercise.content.tips.slice(0, 2).map((tip, idx) => (
                                        <li key={idx} className="flex items-start gap-1">
                                            <span className="text-purple-500">•</span>
                                            {tip}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col gap-2">
                        {!exercise.is_mastered ? (
                            <>
                                <Button
                                    size="sm"
                                    variant="primary"
                                    onClick={() => onComplete(exercise.id, 5)}
                                    disabled={isCompleting}
                                >
                                    <CheckCircle className="size-4 mr-1" />
                                    Complete
                                </Button>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => onComplete(exercise.id, 3)}
                                    disabled={isCompleting}
                                >
                                    <Repeat className="size-4 mr-1" />
                                    Needs Work
                                </Button>
                            </>
                        ) : (
                            <Button
                                size="sm"
                                variant="outline"
                                onClick={() => onComplete(exercise.id, 5)}
                                disabled={isCompleting}
                            >
                                <Repeat className="size-4 mr-1" />
                                Review
                            </Button>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
