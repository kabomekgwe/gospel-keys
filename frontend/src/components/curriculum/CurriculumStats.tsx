import { Link } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { Target, Calendar, TrendingUp, Star, Award, Clock } from 'lucide-react';
import { curriculumApi, api, type CurriculumResponse } from '../../lib/api';

interface CurriculumStatsProps {
  curriculum: CurriculumResponse;
}

export function CurriculumStats({ curriculum }: CurriculumStatsProps) {
  // Fetch real performance data from API
  const { data: performanceData } = useQuery({
    queryKey: ['performance', 'analysis', 7],
    queryFn: () => api.getPerformanceAnalysis(7),
  });

  // Fetch daily practice data for today's stats
  const { data: dailyData } = useQuery({
    queryKey: ['curriculum', 'daily'],
    queryFn: curriculumApi.getDailyPractice,
  });

  // Calculate stats from API data with fallbacks
  const completionPercentage = Math.round((curriculum.current_week / curriculum.duration_weeks) * 100);

  const stats = {
    overallProgress: {
      completionPercentage,
      exercisesCompleted: performanceData?.mastered_exercises?.length ?? 0,
      totalExercises: (performanceData?.mastered_exercises?.length ?? 0) + (performanceData?.struggling_exercises?.length ?? 0) + 10, // Estimate
      masteredExercises: performanceData?.mastered_exercises?.length ?? 0,
      currentStreak: 0, // Would need dedicated API endpoint for streak tracking
    },
    weekFocus: {
      moduleTitle: curriculum.modules[0]?.title || 'Getting Started',
      moduleTheme: curriculum.modules[0]?.theme || 'Foundation Building',
      currentLesson: dailyData?.items?.[0]?.lesson_title || 'No lessons due',
      exercisesDueToday: dailyData?.items?.length ?? 0,
      estimatedTime: dailyData?.total_estimated_minutes ?? 0,
    },
    performance: {
      avgQualityScore: performanceData?.avg_quality_score ?? 0,
      strongestArea: performanceData?.strong_skill_areas?.[0]?.replace(/_/g, ' ') || 'N/A',
      weakestArea: performanceData?.weak_skill_areas?.[0]?.replace(/_/g, ' ') || 'N/A',
    },
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {/* Card 1: Overall Progress */}
      <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 transition-all duration-300 hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <Target className="w-5 h-5 text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">Overall Progress</h3>
        </div>

        {/* Circular Progress */}
        <div className="flex items-center justify-center mb-4">
          <div className="relative w-32 h-32">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-gray-700"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - stats.overallProgress.completionPercentage / 100)}`}
                className="text-purple-500 transition-all duration-500"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-3xl font-bold text-white">
                {stats.overallProgress.completionPercentage}%
              </span>
            </div>
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between text-gray-400">
            <span>Exercises</span>
            <span className="text-white font-medium">
              {stats.overallProgress.exercisesCompleted} / {stats.overallProgress.totalExercises}
            </span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>Mastered</span>
            <span className="text-white font-medium flex items-center gap-1">
              <Award className="w-4 h-4 text-yellow-500" />
              {stats.overallProgress.masteredExercises}
            </span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>Current Streak</span>
            <span className="text-white font-medium">
              🔥 {stats.overallProgress.currentStreak} days
            </span>
          </div>
        </div>
      </div>

      {/* Card 2: This Week's Focus */}
      <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 transition-all duration-300 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
            <Calendar className="w-5 h-5 text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">This Week's Focus</h3>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-xs text-gray-500 uppercase mb-1">Current Module</p>
            <p className="text-white font-semibold">{stats.weekFocus.moduleTitle}</p>
            <p className="text-sm text-gray-400">{stats.weekFocus.moduleTheme}</p>
          </div>

          <div>
            <p className="text-xs text-gray-500 uppercase mb-1">Current Lesson</p>
            <p className="text-white font-medium">{stats.weekFocus.currentLesson}</p>
          </div>

          <div className="pt-4 border-t border-gray-700">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-400">Due Today</span>
              <span className="text-2xl font-bold text-white">
                {stats.weekFocus.exercisesDueToday}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Clock className="w-4 h-4" />
              <span>~{stats.weekFocus.estimatedTime} min practice time</span>
            </div>
          </div>
        </div>
      </div>

      {/* Card 3: Performance Insights */}
      <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 transition-all duration-300 hover:border-green-500/50 hover:shadow-lg hover:shadow-green-500/5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-green-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">Performance Insights</h3>
        </div>

        <div className="space-y-4">
          {/* Average Quality Score */}
          <div>
            <p className="text-xs text-gray-500 uppercase mb-2">Avg Quality Score</p>
            <div className="flex items-center gap-2 mb-1">
              <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`w-5 h-5 ${star <= Math.floor(stats.performance.avgQualityScore)
                      ? 'text-yellow-500 fill-yellow-500'
                      : star === Math.ceil(stats.performance.avgQualityScore)
                        ? 'text-yellow-500 fill-yellow-500/50'
                        : 'text-gray-600'
                      }`}
                  />
                ))}
              </div>
              <span className="text-white font-bold text-lg">
                {stats.performance.avgQualityScore.toFixed(1)}
              </span>
            </div>
            <p className="text-xs text-gray-400">out of 5.0</p>
          </div>

          {/* Strongest/Weakest Areas */}
          <div className="pt-4 border-t border-gray-700 space-y-3">
            <div>
              <p className="text-xs text-gray-500 uppercase mb-1">Strongest Area</p>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <p className="text-white font-medium">{stats.performance.strongestArea}</p>
              </div>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase mb-1">Needs Attention</p>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <p className="text-white font-medium">{stats.performance.weakestArea}</p>
              </div>
            </div>
          </div>

          {/* Link to Full Analysis */}
          <Link
            to="/curriculum/performance"
            className="block w-full px-4 py-2 bg-gray-700 text-white text-center font-medium rounded-lg hover:bg-gray-600 transition text-sm"
          >
            View Full Analysis
          </Link>
        </div>
      </div>
    </div>
  );
}
