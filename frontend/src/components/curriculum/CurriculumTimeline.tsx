import { CheckCircle, Target, Lock, Calendar } from 'lucide-react';
import type { CurriculumResponse } from '../../lib/api';

interface CurriculumTimelineProps {
  curriculum: CurriculumResponse;
}

export function CurriculumTimeline({ curriculum }: CurriculumTimelineProps) {
  const weeks = Array.from({ length: curriculum.duration_weeks }, (_, i) => i + 1);
  const currentWeek = curriculum.current_week;

  // Milestone weeks (e.g., 4, 8, 12 for assessments)
  const milestones = [
    Math.floor(curriculum.duration_weeks * 0.33),
    Math.floor(curriculum.duration_weeks * 0.67),
    curriculum.duration_weeks,
  ];

  const getWeekStatus = (week: number): 'completed' | 'current' | 'upcoming' | 'future' => {
    if (week < currentWeek) return 'completed';
    if (week === currentWeek) return 'current';
    if (week === currentWeek + 1) return 'upcoming';
    return 'future';
  };

  const getWeekColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'current':
        return 'bg-purple-500 ring-4 ring-purple-500/30 animate-pulse';
      case 'upcoming':
        return 'bg-purple-400';
      default:
        return 'bg-gray-700';
    }
  };

  const isMilestone = (week: number) => milestones.includes(week);

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-white">Learning Journey</h2>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Calendar className="w-4 h-4" />
          <span>{curriculum.duration_weeks} weeks total</span>
        </div>
      </div>

      <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
        {/* Timeline Container */}
        <div className="relative">
          {/* Background Line */}
          <div className="absolute left-0 right-0 top-4 h-1 bg-gray-700" />

          {/* Progress Line */}
          <div
            className="absolute left-0 top-4 h-1 bg-gradient-to-r from-green-500 via-purple-500 to-purple-500 transition-all duration-500"
            style={{ width: `${((currentWeek - 1) / (curriculum.duration_weeks - 1)) * 100}%` }}
          />

          {/* Week Markers */}
          <div className="relative flex justify-between items-start">
            {weeks.map((week) => {
              const status = getWeekStatus(week);
              const milestone = isMilestone(week);

              return (
                <div
                  key={week}
                  className="flex flex-col items-center"
                  style={{ width: `${100 / curriculum.duration_weeks}%` }}
                >
                  {/* Marker Dot */}
                  <div
                    className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${getWeekColor(
                      status
                    )} ${milestone ? 'w-10 h-10' : ''}`}
                  >
                    {status === 'completed' && !milestone && (
                      <CheckCircle className="w-4 h-4 text-white" />
                    )}
                    {status === 'current' && <Target className="w-4 h-4 text-white" />}
                    {status === 'future' && <Lock className="w-3 h-3 text-gray-500" />}
                    {milestone && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full border-2 border-gray-900" />
                    )}
                  </div>

                  {/* Week Label */}
                  <div className="mt-2 text-center">
                    <p
                      className={`text-xs font-medium ${
                        status === 'current'
                          ? 'text-purple-400'
                          : status === 'completed'
                          ? 'text-green-400'
                          : 'text-gray-500'
                      }`}
                    >
                      {week}
                    </p>
                    {milestone && (
                      <p className="text-xs text-yellow-500 mt-1">Assessment</p>
                    )}
                    {status === 'current' && (
                      <p className="text-xs text-purple-400 mt-1 font-semibold">Current</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="mt-8 pt-6 border-t border-gray-700 flex flex-wrap gap-4 justify-center text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500" />
            <span className="text-gray-400">Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-purple-500" />
            <span className="text-gray-400">Current Week</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-purple-400" />
            <span className="text-gray-400">Next Week</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gray-700" />
            <span className="text-gray-400">Future</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-purple-500 relative">
              <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-yellow-500 rounded-full" />
            </div>
            <span className="text-gray-400">Milestone</span>
          </div>
        </div>

        {/* Progress Stats */}
        <div className="mt-6 pt-6 border-t border-gray-700 grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-green-400">{currentWeek - 1}</p>
            <p className="text-sm text-gray-400 mt-1">Weeks Completed</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-purple-400">{currentWeek}</p>
            <p className="text-sm text-gray-400 mt-1">Current Week</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-400">
              {curriculum.duration_weeks - currentWeek}
            </p>
            <p className="text-sm text-gray-400 mt-1">Weeks Remaining</p>
          </div>
        </div>
      </div>
    </div>
  );
}
