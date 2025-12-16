import { createFileRoute, Link } from '@tanstack/react-router';
import { useCurriculumList } from '../hooks/useCurriculum';

export const Route = createFileRoute('/curriculum/')({
  component: CurriculumOverview,
});

function CurriculumOverview() {
  const { data: curriculumList, isLoading } = useCurriculumList();

  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  if (!curriculumList || curriculumList.length === 0) {
    return null; // Empty state handled by parent layout
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">All Curriculums</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {curriculumList.map((curriculum) => (
          <Link
            key={curriculum.id}
            to="/curriculum/$curriculumId"
            params={{ curriculumId: curriculum.id }}
            className="block bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition"
          >
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold">{curriculum.title}</h3>
              <span
                className={`px-2 py-1 text-xs font-medium rounded ${
                  curriculum.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : curriculum.status === 'completed'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-800'
                }`}
              >
                {curriculum.status}
              </span>
            </div>
            <p className="text-gray-600 text-sm mb-4 line-clamp-2">
              {curriculum.description}
            </p>
            <div className="flex justify-between text-sm text-gray-500">
              <span>Week {curriculum.current_week}/{curriculum.duration_weeks}</span>
              <span>{curriculum.module_count} modules</span>
            </div>
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${curriculum.overall_progress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {Math.round(curriculum.overall_progress)}% complete
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
