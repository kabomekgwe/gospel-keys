/**
 * ProgressDashboard Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Parent dashboard combining all progress visualization components:
 * - PracticeHistory - Session timeline
 * - AccuracyTrends - Progress over time
 * - SkillLevelChart - Radar chart of skills
 * - GoalTracking - Goals and achievements
 *
 * Integrates with:
 * - STORY-3.2: Database API for historical data
 * - Provides comprehensive progress overview
 */

import { useState } from 'react';
import { PracticeHistory } from './PracticeHistory';
import { AccuracyTrends } from './AccuracyTrends';
import { SkillLevelChart } from './SkillLevelChart';
import { GoalTracking } from './GoalTracking';
import type { RealtimeSession } from '../../lib/api';

export interface ProgressDashboardProps {
  /** User ID for progress tracking */
  userId: number;
  /** Color theme */
  theme?: 'light' | 'dark';
  /** Default view */
  defaultView?: 'overview' | 'history' | 'trends' | 'goals';
  /** Callback when session is selected */
  onSessionSelect?: (session: RealtimeSession) => void;
}

type View = 'overview' | 'history' | 'trends' | 'goals';

export function ProgressDashboard({
  userId,
  theme = 'light',
  defaultView = 'overview',
  onSessionSelect,
}: ProgressDashboardProps) {
  const [currentView, setCurrentView] = useState<View>(defaultView);

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-900' : 'bg-gray-50';
  const cardBg = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';
  const borderColor = isDark ? 'border-gray-700' : 'border-gray-200';

  const tabs: { id: View; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'history', label: 'History', icon: '📝' },
    { id: 'trends', label: 'Trends', icon: '📈' },
    { id: 'goals', label: 'Goals', icon: '🎯' },
  ];

  return (
    <div className={`${bgColor} min-h-screen p-6`}>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className={`${cardBg} rounded-lg shadow-md p-6`}>
          <h1 className={`text-3xl font-bold ${textColor}`}>Progress Dashboard</h1>
          <p className={`text-lg ${mutedColor} mt-1`}>
            Track your practice sessions and improvement over time
          </p>
        </div>

        {/* Tab Navigation */}
        <div className={`${cardBg} rounded-lg shadow-md p-2`}>
          <div className="flex gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setCurrentView(tab.id)}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                  currentView === tab.id
                    ? 'bg-blue-500 text-white shadow-md'
                    : `${mutedColor} hover:bg-gray-100 dark:hover:bg-gray-700`
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* View Content */}
        <div className="space-y-6">
          {/* Overview */}
          {currentView === 'overview' && (
            <>
              {/* Top Row - Stats */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SkillLevelChart userId={userId} theme={theme} showComparison />
                <GoalTracking userId={userId} theme={theme} />
              </div>

              {/* Bottom Row - Charts */}
              <div className="grid grid-cols-1 gap-6">
                <AccuracyTrends userId={userId} timeRange="30d" theme={theme} />
              </div>

              {/* Recent Sessions Preview */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className={`text-xl font-semibold ${textColor}`}>
                    Recent Sessions
                  </h2>
                  <button
                    onClick={() => setCurrentView('history')}
                    className={`text-sm font-medium text-blue-500 hover:underline`}
                  >
                    View All →
                  </button>
                </div>
                <PracticeHistory
                  userId={userId}
                  pageSize={5}
                  theme={theme}
                  onSessionSelect={onSessionSelect}
                />
              </div>
            </>
          )}

          {/* History View */}
          {currentView === 'history' && (
            <PracticeHistory
              userId={userId}
              pageSize={20}
              statusFilter="all"
              theme={theme}
              onSessionSelect={onSessionSelect}
            />
          )}

          {/* Trends View */}
          {currentView === 'trends' && (
            <div className="space-y-6">
              <AccuracyTrends userId={userId} timeRange="30d" height={400} theme={theme} />
              <SkillLevelChart userId={userId} theme={theme} showComparison size={500} />
            </div>
          )}

          {/* Goals View */}
          {currentView === 'goals' && <GoalTracking userId={userId} theme={theme} />}
        </div>

        {/* Quick Stats Footer */}
        <div className={`${cardBg} rounded-lg shadow-md p-4`}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
                Current View
              </div>
              <div className={`text-lg font-bold ${textColor}`}>
                {tabs.find((t) => t.id === currentView)?.label || 'Overview'}
              </div>
            </div>

            <div>
              <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
                User ID
              </div>
              <div className={`text-lg font-bold ${textColor}`}>{userId}</div>
            </div>

            <div>
              <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
                Theme
              </div>
              <div className={`text-lg font-bold ${textColor} capitalize`}>
                {theme}
              </div>
            </div>

            <div>
              <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
                Data Range
              </div>
              <div className={`text-lg font-bold ${textColor}`}>
                {currentView === 'trends' ? '30 Days' : 'All Time'}
              </div>
            </div>
          </div>
        </div>

        {/* Help Text */}
        <div className={`${cardBg} rounded-lg shadow-md p-4`}>
          <div className="text-sm">
            <h4 className={`font-semibold ${textColor} mb-2`}>Quick Tips:</h4>
            <ul className={`space-y-1 ${mutedColor}`}>
              <li>• <strong>Overview:</strong> See your overall progress, skills, and recent sessions at a glance</li>
              <li>• <strong>History:</strong> Browse all your practice sessions with detailed information</li>
              <li>• <strong>Trends:</strong> Visualize your improvement over time with interactive charts</li>
              <li>• <strong>Goals:</strong> Track your weekly goals and unlock achievements</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
