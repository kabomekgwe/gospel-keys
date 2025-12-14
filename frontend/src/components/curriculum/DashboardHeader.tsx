import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { Activity, Trophy, FileText, Settings, ChevronDown, Check } from 'lucide-react';
import { type CurriculumResponse, curriculumApi } from '../../lib/api';
import { CurriculumSettings } from './CurriculumSettings';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface DashboardHeaderProps {
  curriculum: CurriculumResponse;
}

export function DashboardHeader({ curriculum }: DashboardHeaderProps) {
  const [showSettings, setShowSettings] = useState(false);
  const [showSelector, setShowSelector] = useState(false);
  const queryClient = useQueryClient();

  const progressPercentage = Math.round((curriculum.current_week / curriculum.duration_weeks) * 100);

  // Fetch all user curriculums
  const { data: allCurriculums } = useQuery({
    queryKey: ['curriculum', 'list'],
    queryFn: curriculumApi.listCurriculums,
  });

  // Switch curriculum mutation
  const switchMutation = useMutation({
    mutationFn: curriculumApi.activateCurriculum,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curriculum'] });
      setShowSelector(false);
    },
  });

  const handleSwitch = (id: string) => {
    switchMutation.mutate(id);
  };

  return (
    <div className="mb-8 relative">
      {/* Title and Description */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl md:text-4xl font-bold text-white">{curriculum.title}</h1>

          {allCurriculums && allCurriculums.length > 1 && (
            <div className="relative">
              <button
                onClick={() => setShowSelector(!showSelector)}
                className="p-1 hover:bg-gray-700 rounded-full transition text-gray-400 hover:text-white"
                title="Switch Curriculum"
              >
                <ChevronDown className="w-6 h-6" />
              </button>

              {showSelector && (
                <div className="absolute top-10 left-0 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 w-72 max-h-96 overflow-y-auto">
                  <div className="p-2">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">Your Curriculums</h3>
                    {allCurriculums.map(c => (
                      <button
                        key={c.id}
                        onClick={() => handleSwitch(c.id)}
                        className={`w-full text-left px-3 py-2 rounded-md flex items-center justify-between text-sm ${c.id === curriculum.id
                            ? 'bg-purple-600/20 text-purple-400'
                            : 'text-gray-300 hover:bg-gray-700'
                          }`}
                      >
                        <span className="truncate">{c.title}</span>
                        {c.id === curriculum.id && <Check className="w-4 h-4" />}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {curriculum.description && (
          <p className="text-gray-300 text-lg max-w-3xl">{curriculum.description}</p>
        )}
      </div>

      {/* Week Indicator and Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span className="text-white font-medium">
              Week {curriculum.current_week} of {curriculum.duration_weeks}
            </span>
            <span>•</span>
            <span className="capitalize">{curriculum.status}</span>
            <span>•</span>
            <span>{curriculum.modules.length} modules</span>
          </div>
          <span className="text-white font-semibold">{progressPercentage}% Complete</span>
        </div>
        {/* Progress Bar */}
        <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Quick Actions Toolbar */}
      <div className="flex flex-wrap gap-3">
        <Link
          to="/curriculum/daily"
          className="px-4 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-500 transition inline-flex items-center gap-2"
        >
          <Activity className="w-4 h-4" />
          Daily Practice
        </Link>
        <Link
          to="/curriculum/performance"
          className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-500 transition inline-flex items-center gap-2"
        >
          <Trophy className="w-4 h-4" />
          Performance
        </Link>
        <Link
          to="/curriculum/assessment"
          className="px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-500 transition inline-flex items-center gap-2"
        >
          <FileText className="w-4 h-4" />
          Assessments
        </Link>
        <button
          className="px-4 py-2 bg-gray-700 text-white font-medium rounded-lg hover:bg-gray-600 transition inline-flex items-center gap-2"
          onClick={() => setShowSettings(true)}
        >
          <Settings className="w-4 h-4" />
          Settings
        </button>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <CurriculumSettings curriculum={curriculum} onClose={() => setShowSettings(false)} />
      )}
    </div>
  );
}
