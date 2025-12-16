import { createFileRoute, Link, Outlet } from '@tanstack/react-router';
import { useActiveCurriculum, useCurriculumList } from '../hooks/useCurriculum';

export const Route = createFileRoute('/curriculum')({
  component: CurriculumLayout,
});

function CurriculumLayout() {
  const { data: activeCurriculum, isLoading: activeLoading } = useActiveCurriculum();
  const { data: curriculumList, isLoading: listLoading } = useCurriculumList();

  if (activeLoading || listLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">My Curriculum</h1>
        <p className="text-gray-600">
          Personalized music education powered by AI
        </p>
      </header>

      {/* Active Curriculum Card */}
      {activeCurriculum && (
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 mb-8 text-white">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold mb-2">{activeCurriculum.title}</h2>
              <p className="text-blue-100 mb-4">{activeCurriculum.description}</p>
              <div className="flex gap-4 text-sm">
                <div>
                  <span className="opacity-75">Week:</span>{' '}
                  <span className="font-semibold">
                    {activeCurriculum.current_week}/{activeCurriculum.duration_weeks}
                  </span>
                </div>
                <div>
                  <span className="opacity-75">Modules:</span>{' '}
                  <span className="font-semibold">{activeCurriculum.modules.length}</span>
                </div>
              </div>
            </div>
            <Link
              to="/curriculum/$curriculumId"
              params={{ curriculumId: activeCurriculum.id }}
              className="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition"
            >
              View Details
            </Link>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex gap-4 mb-6 border-b border-gray-200">
        <Link
          to="/curriculum"
          className="px-4 py-2 border-b-2 border-transparent hover:border-blue-500 transition"
          activeProps={{ className: 'border-blue-500 text-blue-600' }}
        >
          Overview
        </Link>
        <Link
          to="/curriculum/daily"
          className="px-4 py-2 border-b-2 border-transparent hover:border-blue-500 transition"
          activeProps={{ className: 'border-blue-500 text-blue-600' }}
        >
          Daily Practice
        </Link>
        <Link
          to="/curriculum/new"
          className="px-4 py-2 border-b-2 border-transparent hover:border-blue-500 transition"
          activeProps={{ className: 'border-blue-500 text-blue-600' }}
        >
          Create New
        </Link>
      </nav>

      {/* Outlet for nested routes */}
      <Outlet />

      {/* Curriculum List */}
      {!activeCurriculum && curriculumList && curriculumList.length === 0 && (
        <div className="text-center py-12">
          <h3 className="text-xl font-semibold mb-2">No curriculum yet</h3>
          <p className="text-gray-600 mb-4">
            Get started by creating your personalized curriculum
          </p>
          <Link
            to="/curriculum/new"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Create Curriculum
          </Link>
        </div>
      )}
    </div>
  );
}
