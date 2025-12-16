import { createFileRoute } from '@tanstack/react-router';
import { useDailyPractice, useCompleteExercise } from '../hooks/useCurriculum';
import { useState } from 'react';

export const Route = createFileRoute('/curriculum/daily')({
  component: DailyPracticePage,
});

function DailyPracticePage() {
  const { data: practice, isLoading } = useDailyPractice();
  const completeExercise = useCompleteExercise();
  const [expandedExercise, setExpandedExercise] = useState<string | null>(null);

  if (isLoading) {
    return <div className="text-center py-8">Loading today's practice...</div>;
  }

  if (!practice || practice.items.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <h3 className="text-xl font-semibold mb-2">No exercises due today</h3>
        <p className="text-gray-600">
          Check back tomorrow or explore new lessons in your curriculum
        </p>
      </div>
    );
  }

  const handleComplete = async (exerciseId: string, quality: number) => {
    await completeExercise.mutateAsync({
      exerciseId,
      request: { quality },
    });
  };

  return (
    <div>
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-bold mb-2">Today's Practice Queue</h2>
        <div className="flex gap-6 text-sm text-gray-600">
          <div>
            <span className="font-medium">{practice.items.length}</span> exercises
          </div>
          <div>
            <span className="font-medium">{practice.total_estimated_minutes}</span> minutes
          </div>
          {practice.overdue_count > 0 && (
            <div className="text-red-600">
              <span className="font-medium">{practice.overdue_count}</span> overdue
            </div>
          )}
          {practice.new_count > 0 && (
            <div className="text-green-600">
              <span className="font-medium">{practice.new_count}</span> new
            </div>
          )}
        </div>
      </div>

      <div className="space-y-4">
        {practice.items.map((item) => (
          <div
            key={item.exercise.id}
            className="bg-white border border-gray-200 rounded-lg overflow-hidden"
          >
            <div
              className="p-6 cursor-pointer hover:bg-gray-50"
              onClick={() =>
                setExpandedExercise(
                  expandedExercise === item.exercise.id ? null : item.exercise.id,
                )
              }
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-lg font-semibold">{item.exercise.title}</h3>
                    {item.priority === 1 && (
                      <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                        Overdue
                      </span>
                    )}
                    {item.priority === 3 && (
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                        New
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600 text-sm mb-2">
                    {item.exercise.description}
                  </p>
                  <div className="flex gap-4 text-xs text-gray-500">
                    <span>{item.module_title}</span>
                    <span>•</span>
                    <span>{item.lesson_title}</span>
                    <span>•</span>
                    <span>{item.exercise.estimated_duration_minutes} min</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium mb-1">
                    Difficulty: {item.exercise.difficulty}/10
                  </div>
                  <div className="text-xs text-gray-500">
                    Practiced {item.exercise.practice_count}x
                  </div>
                </div>
              </div>
            </div>

            {expandedExercise === item.exercise.id && (
              <div className="border-t border-gray-200 p-6 bg-gray-50">
                <div className="mb-4">
                  <h4 className="font-medium mb-2">Exercise Content</h4>
                  {item.exercise.content.instructions && (
                    <p className="text-gray-700 mb-2">
                      {item.exercise.content.instructions}
                    </p>
                  )}
                  {item.exercise.content.tips && (
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {item.exercise.content.tips.map((tip, idx) => (
                        <li key={idx}>{tip}</li>
                      ))}
                    </ul>
                  )}
                </div>

                <div>
                  <h4 className="font-medium mb-2">Mark as Complete</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    How well did you perform this exercise?
                  </p>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((quality) => (
                      <button
                        key={quality}
                        onClick={() => handleComplete(item.exercise.id, quality)}
                        disabled={completeExercise.isPending}
                        className={`px-4 py-2 rounded-lg font-medium transition ${
                          quality <= 2
                            ? 'bg-red-100 text-red-800 hover:bg-red-200'
                            : quality === 3
                              ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                              : 'bg-green-100 text-green-800 hover:bg-green-200'
                        } disabled:opacity-50`}
                      >
                        {quality}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    1 = Struggled, 3 = OK, 5 = Mastered
                  </p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
