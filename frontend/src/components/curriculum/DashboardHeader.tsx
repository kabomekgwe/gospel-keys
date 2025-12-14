import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { Activity, Trophy, FileText, Settings } from 'lucide-react';
import type { CurriculumResponse } from '../../lib/api';
import { CurriculumSettings } from './CurriculumSettings';

interface DashboardHeaderProps {
  curriculum: CurriculumResponse;
}

export function DashboardHeader({ curriculum }: DashboardHeaderProps) {
  const [showSettings, setShowSettings] = useState(false);
  const progressPercentage = Math.round((curriculum.current_week / curriculum.duration_weeks) * 100);

  return (
    <div className="mb-8">
      {/* Title and Description */}
      <div className="mb-6">
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">{curriculum.title}</h1>
        {curriculum.description && (
          <p className="text-gray-300 text-lg">{curriculum.description}</p>
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
