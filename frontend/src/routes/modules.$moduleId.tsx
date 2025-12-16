import { createFileRoute, Link } from '@tanstack/react-router';
import { useModule } from '../hooks/useCurriculum';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ChevronLeft, BookOpen, Clock, CheckCircle, Play } from 'lucide-react';

export const Route = createFileRoute('/modules/$moduleId')({
  component: ModuleDetailPage,
});

function ModuleDetailPage() {
  const { moduleId } = Route.useParams();
  const { data: module, isLoading, error } = useModule(moduleId);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
          <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4"></div>
          <div className="grid gap-4 mt-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !module) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-16">
          <div className="text-6xl mb-4">📚</div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            Module Not Found
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mb-6">
            The module you're looking for doesn't exist or has been removed.
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

  const completedLessons = module.lessons.filter((l) => l.is_completed).length;
  const totalLessons = module.lessons.length;
  const progressPercent = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Back Navigation */}
      <Button asChild variant="ghost" className="mb-6 -ml-2">
        <Link to="/curriculum/$curriculumId" params={{ curriculumId: module.curriculum_id }}>
          <ChevronLeft className="size-4 mr-1" />
          Back to Curriculum
        </Link>
      </Button>

      {/* Module Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              {module.title}
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              {module.description}
            </p>
          </div>
          <Badge variant="outline" className="text-sm px-3 py-1">
            {module.theme}
          </Badge>
        </div>

        {/* Module Stats */}
        <div className="flex flex-wrap gap-4 text-sm text-slate-600 dark:text-slate-400 mb-6">
          <div className="flex items-center gap-1.5">
            <Clock className="size-4" />
            <span>Weeks {module.start_week} - {module.end_week}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <BookOpen className="size-4" />
            <span>{totalLessons} Lessons</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle className="size-4 text-green-500" />
            <span>{completedLessons} Completed</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-600 dark:text-slate-400">Module Progress</span>
            <span className="font-semibold text-slate-900 dark:text-white">{progressPercent}%</span>
          </div>
          <Progress value={progressPercent} className="h-2" />
        </div>
      </div>

      {/* Prerequisites & Outcomes */}
      {(module.prerequisites.length > 0 || module.outcomes.length > 0) && (
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {module.prerequisites.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Prerequisites</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {module.prerequisites.map((prereq, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <span className="text-purple-500">•</span>
                      {prereq}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
          {module.outcomes.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Learning Outcomes</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {module.outcomes.map((outcome, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <span className="text-green-500">✓</span>
                      {outcome}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Lessons List */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Lessons</h2>

        {module.lessons.length === 0 ? (
          <Card className="text-center py-8">
            <CardContent>
              <p className="text-slate-600 dark:text-slate-400">
                No lessons available yet for this module.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {module.lessons.map((lesson, idx) => (
              <Card
                key={lesson.id}
                className={`transition-all hover:shadow-md ${lesson.is_completed ? 'border-green-200 dark:border-green-800/50 bg-green-50/50 dark:bg-green-900/10' : ''
                  }`}
              >
                <CardContent className="py-4">
                  <div className="flex items-center gap-4">
                    {/* Lesson Number & Status Icon */}
                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${lesson.is_completed
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                      }`}>
                      {lesson.is_completed ? (
                        <CheckCircle className="size-5" />
                      ) : (
                        <span className="font-semibold">{idx + 1}</span>
                      )}
                    </div>

                    {/* Lesson Info */}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-slate-900 dark:text-white truncate">
                        {lesson.title}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                        <span>Week {lesson.week_number}</span>
                        <span>•</span>
                        <span>{lesson.exercise_count} exercises</span>
                        {lesson.completed_exercises > 0 && (
                          <>
                            <span>•</span>
                            <span className="text-green-600 dark:text-green-400">
                              {lesson.completed_exercises}/{lesson.exercise_count} done
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Action Button */}
                    <Button asChild variant={lesson.is_completed ? "outline" : "primary"} size="sm">
                      <Link to="/lessons/$lessonId" params={{ lessonId: lesson.id }}>
                        <Play className="size-4 mr-1" />
                        {lesson.is_completed ? 'Review' : 'Start'}
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
