import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { curriculumApi } from '../../../lib/api';
import { useState } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Play,
  CheckCircle,
  Clock,
  Target,
  ChevronDown,
  ChevronUp,
  Plus,
} from 'lucide-react';

export const Route = createFileRoute('/curriculum/lessons/$lessonId')({
  component: LessonDetailPage,
});

function LessonDetailPage() {
  const { lessonId } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showTutorial, setShowTutorial] = useState(false);
  const [expandedExercises, setExpandedExercises] = useState<Set<string>>(new Set());

  // Fetch lesson data
  const { data: lesson, isLoading, error } = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => curriculumApi.getLesson(lessonId),
  });

  // Fetch tutorial (lazy load when expanded)
  const { data: tutorial, isLoading: tutorialLoading } = useQuery({
    queryKey: ['lesson', lessonId, 'tutorial'],
    queryFn: () => curriculumApi.getLessonTutorial(lessonId, false),
    enabled: showTutorial,
  });

  const toggleExercise = (exerciseId: string) => {
    setExpandedExercises((prev) => {
      const next = new Set(prev);
      if (next.has(exerciseId)) {
        next.delete(exerciseId);
      } else {
        next.add(exerciseId);
      }
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-400 text-lg">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6 flex items-center justify-center">
        <div className="bg-gray-800/50 p-8 rounded-xl border border-gray-700 text-center max-w-md">
          <h2 className="text-xl font-semibold text-white mb-4">Lesson Not Found</h2>
          <p className="text-gray-400 mb-6">This lesson doesn't exist or has been removed.</p>
          <Link
            to="/curriculum"
            className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-500 transition inline-block"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  // Mock data for demonstration
  const mockLesson = {
    ...lesson,
    title: lesson.title || 'Gospel Voicings Fundamentals',
    description: lesson.description || 'Learn the essential voicings used in gospel piano',
    week: 1,
    module_name: 'Gospel Foundations',
    completion_percentage: 40,
    total_exercises: 10,
    completed_exercises: 4,
    exercises: Array.from({ length: 10 }, (_, i) => ({
      id: `ex-${i + 1}`,
      title: `Exercise ${i + 1}: ${['Major 7th Voicings', 'Dominant 7th', 'Minor 7th', 'Half Diminished', '2-5-1 Progression', 'Gospel Turnarounds', 'Chromatic Approaches', 'Shell Voicings', 'Extended Chords', 'Voice Leading'][i]}`,
      type: ['chord_progression', 'scale', 'voicing', 'pattern'][i % 4] as any,
      status: i < 4 ? 'completed' : i === 4 ? 'due' : 'pending' as any,
      next_review: i < 4 ? new Date(Date.now() + (i + 1) * 86400000).toISOString() : null,
      quality_score: i < 4 ? 3 + Math.random() * 2 : null,
      repetition_count: i < 4 ? Math.floor(Math.random() * 5) + 1 : 0,
    })),
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-gray-400 mb-6">
          <Link to="/curriculum" className="hover:text-white transition">
            Dashboard
          </Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-500">{mockLesson.module_name}</span>
          <ChevronRight className="w-4 h-4" />
          <span className="text-white">{mockLesson.title}</span>
        </nav>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-white">{mockLesson.title}</h1>
                  <p className="text-gray-400 mt-1">{mockLesson.description}</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Week {mockLesson.week}</p>
              <p className="text-sm text-gray-500">{mockLesson.module_name}</p>
            </div>
          </div>

          {/* Progress */}
          <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Progress</span>
              <span className="text-sm text-white font-medium">
                {mockLesson.completed_exercises} / {mockLesson.total_exercises} exercises completed
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${mockLesson.completion_percentage}%` }}
              />
            </div>
          </div>
        </div>

        {/* Tutorial Section */}
        <div className="mb-8">
          <button
            onClick={() => setShowTutorial(!showTutorial)}
            className="w-full bg-gray-800/50 p-4 rounded-xl border border-gray-700 hover:border-gray-600 transition flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-semibold text-white">Lesson Tutorial</h3>
                <p className="text-sm text-gray-400">AI-generated learning guide</p>
              </div>
            </div>
            {showTutorial ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {showTutorial && (
            <div className="mt-4 bg-gray-800/50 p-6 rounded-xl border border-gray-700">
              {tutorialLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
                  <p className="text-gray-400">Loading tutorial...</p>
                </div>
              ) : tutorial ? (
                <div className="prose prose-invert max-w-none">
                  <div className="text-gray-300 whitespace-pre-wrap">{tutorial.content}</div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-400 mb-4">Tutorial not available</p>
                  <button
                    onClick={() => queryClient.invalidateQueries({ queryKey: ['lesson', lessonId, 'tutorial'] })}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition"
                  >
                    Generate Tutorial
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Exercise List */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Exercises</h2>
            <div className="flex gap-2">
              <button
                onClick={() => alert('Add all to Daily Practice - Coming soon!')}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition flex items-center gap-2 text-sm"
              >
                <Plus className="w-4 h-4" />
                Add All to Queue
              </button>
              <button
                onClick={() => alert('Complete All - Coming soon!')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition flex items-center gap-2 text-sm"
              >
                <CheckCircle className="w-4 h-4" />
                Complete All
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {mockLesson.exercises.map((exercise, index) => {
              const isExpanded = expandedExercises.has(exercise.id);
              const statusConfig = {
                completed: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10', border: 'border-green-500/30' },
                due: { icon: Target, color: 'text-purple-500', bg: 'bg-purple-500/20', border: 'border-purple-500/50' },
                pending: { icon: Clock, color: 'text-gray-500', bg: 'bg-gray-800/50', border: 'border-gray-700' },
              }[exercise.status];

              const StatusIcon = statusConfig.icon;

              return (
                <div
                  key={exercise.id}
                  className={`border rounded-xl overflow-hidden transition ${statusConfig.border} ${statusConfig.bg}`}
                >
                  <button
                    onClick={() => toggleExercise(exercise.id)}
                    className="w-full p-4 flex items-center gap-4 hover:bg-gray-900/30 transition text-left"
                  >
                    <StatusIcon className={`w-6 h-6 flex-shrink-0 ${statusConfig.color}`} />
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-medium mb-1">{exercise.title}</h3>
                      <div className="flex items-center gap-3 text-sm text-gray-400">
                        <span className="capitalize">{exercise.type.replace('_', ' ')}</span>
                        {exercise.status === 'completed' && exercise.quality_score && (
                          <>
                            <span>•</span>
                            <span>Quality: {exercise.quality_score.toFixed(1)}/5.0</span>
                            <span>•</span>
                            <span>{exercise.repetition_count} reps</span>
                          </>
                        )}
                        {exercise.next_review && (
                          <>
                            <span>•</span>
                            <span>Next: {new Date(exercise.next_review).toLocaleDateString()}</span>
                          </>
                        )}
                      </div>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="border-t border-gray-700 p-4 bg-gray-900/30">
                      <div className="mb-4">
                        <p className="text-gray-400 text-sm mb-3">
                          This exercise focuses on {exercise.title.toLowerCase()}. Practice slowly at first, then gradually increase tempo.
                        </p>
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            alert('Audio player integration - Coming in next update!');
                          }}
                          className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition flex items-center justify-center gap-2"
                        >
                          <Play className="w-4 h-4" />
                          Practice Now
                        </button>
                        {exercise.status !== 'completed' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              alert('Mark Complete - Coming soon!');
                            }}
                            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
                          >
                            Mark Complete
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Navigation Footer */}
        <div className="mt-8 flex justify-between items-center p-4 bg-gray-800/50 rounded-xl border border-gray-700">
          <button
            onClick={() => alert('Previous lesson - Coming soon!')}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition flex items-center gap-2"
            disabled={true}
          >
            <ChevronLeft className="w-4 h-4" />
            Previous Lesson
          </button>
          <Link
            to="/curriculum"
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            Back to Dashboard
          </Link>
          <button
            onClick={() => alert('Next lesson - Coming soon!')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition flex items-center gap-2"
          >
            Next Lesson
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
