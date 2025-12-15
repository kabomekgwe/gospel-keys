/**
 * GoalTracking Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Goal setting and tracking interface:
 * - Set practice goals (sessions per week, accuracy targets)
 * - Track goal progress with visual indicators
 * - Achievement badges and milestones
 * - Weekly/monthly goal summaries
 */

import { useEffect, useState } from 'react';
import { realtimeAnalysisApi } from '../../lib/api';

export interface GoalTrackingProps {
  /** User ID for goal tracking */
  userId: number;
  /** Color theme */
  theme?: 'light' | 'dark';
}

interface Goal {
  id: string;
  type: 'sessions' | 'pitch' | 'rhythm' | 'overall';
  target: number;
  current: number;
  period: 'weekly' | 'monthly';
  label: string;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlockedAt?: string;
}

/**
 * Get achievement badge definitions
 */
function getAchievements(stats: any): Achievement[] {
  return [
    {
      id: 'first-session',
      title: 'Getting Started',
      description: 'Complete your first practice session',
      icon: '🎯',
      unlocked: stats.total_sessions >= 1,
      unlockedAt: stats.total_sessions >= 1 ? new Date().toISOString() : undefined,
    },
    {
      id: 'consistent-week',
      title: 'Consistent Learner',
      description: 'Practice 5 times in one week',
      icon: '📅',
      unlocked: stats.sessions_this_week >= 5,
    },
    {
      id: 'pitch-master',
      title: 'Pitch Perfect',
      description: 'Achieve 90% pitch accuracy',
      icon: '🎵',
      unlocked: stats.avg_pitch_accuracy >= 0.9,
    },
    {
      id: 'rhythm-master',
      title: 'Rhythm Keeper',
      description: 'Achieve 90% rhythm accuracy',
      icon: '🥁',
      unlocked: stats.avg_rhythm_accuracy >= 0.9,
    },
    {
      id: 'dedication',
      title: 'Dedicated Musician',
      description: 'Complete 50 practice sessions',
      icon: '🏆',
      unlocked: stats.total_sessions >= 50,
    },
    {
      id: 'marathon',
      title: 'Practice Marathon',
      description: 'Practice for 10 hours total',
      icon: '⏱️',
      unlocked: stats.total_practice_time >= 36000, // 10 hours in seconds
    },
  ];
}

export function GoalTracking({ userId, theme = 'light' }: GoalTrackingProps) {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  // Fetch user stats and calculate goals
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Get user stats
        const userStats = await realtimeAnalysisApi.getUserStats(userId, 30);
        setStats(userStats);

        // Calculate weekly goals
        const weeklyGoals: Goal[] = [
          {
            id: 'sessions-week',
            type: 'sessions',
            target: 5,
            current: userStats.sessions_this_week || 0,
            period: 'weekly',
            label: 'Practice Sessions',
          },
          {
            id: 'pitch-week',
            type: 'pitch',
            target: 0.8,
            current: userStats.avg_pitch_accuracy || 0,
            period: 'weekly',
            label: 'Pitch Accuracy',
          },
          {
            id: 'rhythm-week',
            type: 'rhythm',
            target: 0.8,
            current: userStats.avg_rhythm_accuracy || 0,
            period: 'weekly',
            label: 'Rhythm Accuracy',
          },
          {
            id: 'overall-week',
            type: 'overall',
            target: 0.75,
            current: userStats.avg_overall_score || 0,
            period: 'weekly',
            label: 'Overall Score',
          },
        ];

        setGoals(weeklyGoals);
        setAchievements(getAchievements(userStats));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';
  const borderColor = isDark ? 'border-gray-700' : 'border-gray-200';

  if (loading) {
    return (
      <div className={`${bgColor} rounded-lg shadow-md p-6`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          <span className={`ml-3 ${mutedColor}`}>Loading goals...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${bgColor} rounded-lg shadow-md p-6`}>
        <div className="text-center py-12">
          <p className="text-red-600 mb-2">Error loading goals</p>
          <p className={`text-sm ${mutedColor}`}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Weekly Goals */}
      <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
        <h3 className={`text-lg font-semibold ${textColor}`}>Weekly Goals</h3>

        <div className="space-y-3">
          {goals.map((goal) => {
            const isPercentage = goal.type !== 'sessions';
            const progress = isPercentage
              ? (goal.current / goal.target) * 100
              : (goal.current / goal.target) * 100;
            const isComplete = goal.current >= goal.target;

            return (
              <div key={goal.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium ${textColor}`}>
                    {goal.label}
                  </span>
                  <span className={`text-sm font-semibold ${isComplete ? 'text-green-600' : mutedColor}`}>
                    {isPercentage
                      ? `${(goal.current * 100).toFixed(0)}% / ${(goal.target * 100).toFixed(0)}%`
                      : `${goal.current} / ${goal.target}`}
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      isComplete
                        ? 'bg-green-500'
                        : progress >= 75
                        ? 'bg-blue-500'
                        : progress >= 50
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(100, progress)}%` }}
                  />
                </div>

                {/* Completion Message */}
                {isComplete && (
                  <div className="flex items-center gap-1 text-sm text-green-600">
                    <span>✓</span>
                    <span>Goal achieved!</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Overall Progress Summary */}
        {stats && (
          <div className="pt-3 border-t" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="text-center">
                <div className={`${mutedColor} text-xs uppercase tracking-wide mb-1`}>
                  This Week
                </div>
                <div className={`text-xl font-bold ${textColor}`}>
                  {stats.sessions_this_week || 0}
                </div>
                <div className={`text-xs ${mutedColor}`}>sessions</div>
              </div>

              <div className="text-center">
                <div className={`${mutedColor} text-xs uppercase tracking-wide mb-1`}>
                  Total Time
                </div>
                <div className={`text-xl font-bold ${textColor}`}>
                  {Math.floor((stats.total_practice_time || 0) / 3600)}h
                </div>
                <div className={`text-xs ${mutedColor}`}>practiced</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Achievements */}
      <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
        <h3 className={`text-lg font-semibold ${textColor}`}>Achievements</h3>

        <div className="grid grid-cols-2 gap-3">
          {achievements.map((achievement) => (
            <div
              key={achievement.id}
              className={`p-3 rounded-lg border ${borderColor} ${
                achievement.unlocked ? 'opacity-100' : 'opacity-40'
              } transition-opacity`}
            >
              <div className="text-center space-y-2">
                <div className="text-3xl">{achievement.icon}</div>
                <div>
                  <div className={`text-sm font-semibold ${textColor}`}>
                    {achievement.title}
                  </div>
                  <div className={`text-xs ${mutedColor} mt-1`}>
                    {achievement.description}
                  </div>
                </div>
                {achievement.unlocked && (
                  <div className="text-xs text-green-600 font-medium">
                    ✓ Unlocked
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Achievement Stats */}
        <div className="pt-2 border-t text-center" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
          <span className={`text-sm ${mutedColor}`}>
            {achievements.filter((a) => a.unlocked).length} of {achievements.length} achievements unlocked
          </span>
        </div>
      </div>
    </div>
  );
}
