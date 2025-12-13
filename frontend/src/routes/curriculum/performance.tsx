/**
 * Performance Dashboard Page
 *
 * Displays user performance analytics, weak/strong areas,
 * recommended adaptations, and progress trends
 */

import { useState, useEffect } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { api } from '@/lib/api';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Award,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  BarChart3,
  Activity,
  RefreshCw,
} from 'lucide-react';

export const Route = createFileRoute('/curriculum/performance')({
  component: PerformanceDashboard,
});

interface PerformanceAnalysis {
  completion_rate: number;
  avg_quality_score: number;
  struggling_exercises: string[];
  mastered_exercises: string[];
  weak_skill_areas: string[];
  strong_skill_areas: string[];
  recommended_actions: string[];
}

function PerformanceDashboard() {
  const [analysis, setAnalysis] = useState<PerformanceAnalysis | null>(null);
  const [lookbackDays, setLookbackDays] = useState(7);
  const [isLoading, setIsLoading] = useState(true);
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPerformanceData();
  }, [lookbackDays]);

  const loadPerformanceData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await api.getPerformanceAnalysis(lookbackDays);
      setAnalysis(data);
      setIsLoading(false);
    } catch (err) {
      setError('Failed to load performance data');
      setIsLoading(false);
    }
  };

  const handleApplyAdaptations = async () => {
    setIsApplying(true);

    try {
      await api.applyCurriculumAdaptations();
      // Reload data after applying
      await loadPerformanceData();
      setIsApplying(false);
    } catch (err) {
      setError('Failed to apply adaptations');
      setIsApplying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading performance data...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          {error || 'Performance data not available'}
        </div>
      </div>
    );
  }

  const completionPercentage = Math.round(analysis.completion_rate * 100);
  const qualityScore = analysis.avg_quality_score.toFixed(1);
  const hasRecommendations = analysis.recommended_actions.length > 0;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Performance Dashboard</h1>
            <p className="text-gray-600">Track your progress and get personalized recommendations</p>
          </div>

          {/* Lookback Period Selector */}
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            <select
              value={lookbackDays}
              onChange={(e) => setLookbackDays(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
            </select>
            <button
              onClick={loadPerformanceData}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
            >
              <RefreshCw className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Completion Rate */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Target className="w-6 h-6 text-blue-600" />
              <h3 className="font-semibold text-gray-900">Completion Rate</h3>
            </div>
            {completionPercentage >= 80 ? (
              <TrendingUp className="w-5 h-5 text-green-600" />
            ) : (
              <TrendingDown className="w-5 h-5 text-orange-600" />
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-gray-900">{completionPercentage}%</span>
          </div>
          <div className="mt-4 w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${
                completionPercentage >= 80
                  ? 'bg-green-600'
                  : completionPercentage >= 60
                  ? 'bg-blue-600'
                  : 'bg-orange-600'
              }`}
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {completionPercentage >= 80
              ? 'Excellent consistency!'
              : completionPercentage >= 60
              ? 'Good progress'
              : 'Try to practice more regularly'}
          </p>
        </div>

        {/* Quality Score */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Award className="w-6 h-6 text-purple-600" />
              <h3 className="font-semibold text-gray-900">Avg Quality Score</h3>
            </div>
            <BarChart3 className="w-5 h-5 text-purple-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-gray-900">{qualityScore}</span>
            <span className="text-lg text-gray-500">/ 5.0</span>
          </div>
          <div className="mt-4 flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <div
                key={star}
                className={`flex-1 h-3 rounded ${
                  star <= Math.round(analysis.avg_quality_score)
                    ? 'bg-yellow-400'
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {analysis.avg_quality_score >= 3.5
              ? 'Great performance!'
              : analysis.avg_quality_score >= 2.5
              ? 'Keep improving'
              : 'Focus on fundamentals'}
          </p>
        </div>

        {/* Mastered Exercises */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
              <h3 className="font-semibold text-gray-900">Mastered</h3>
            </div>
            <Activity className="w-5 h-5 text-green-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-gray-900">{analysis.mastered_exercises.length}</span>
            <span className="text-lg text-gray-500">exercises</span>
          </div>
          <p className="text-sm text-gray-600 mt-6">
            {analysis.mastered_exercises.length > 0
              ? `${analysis.mastered_exercises.length} exercises mastered`
              : 'Keep practicing to master exercises'}
          </p>
        </div>
      </div>

      {/* Weak Areas & Strong Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Weak Areas */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200 px-6 py-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
              <h2 className="text-xl font-bold text-gray-900">Areas to Improve</h2>
            </div>
          </div>
          <div className="p-6">
            {analysis.weak_skill_areas.length > 0 ? (
              <div className="space-y-3">
                {analysis.weak_skill_areas.map((area) => (
                  <div key={area} className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold text-gray-900 capitalize">
                          {area.replace(/_/g, ' ')}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">
                          Focus on exercises in this skill area
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {analysis.struggling_exercises.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-semibold text-gray-700 mb-2">
                      Struggling Exercises: {analysis.struggling_exercises.length}
                    </p>
                    <p className="text-xs text-gray-600">
                      These exercises need more practice time
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-2" />
                <p className="text-gray-600">No weak areas detected!</p>
                <p className="text-sm text-gray-500">Keep up the great work</p>
              </div>
            )}
          </div>
        </div>

        {/* Strong Areas */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200 px-6 py-4">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-green-600" />
              <h2 className="text-xl font-bold text-gray-900">Your Strengths</h2>
            </div>
          </div>
          <div className="p-6">
            {analysis.strong_skill_areas.length > 0 ? (
              <div className="space-y-3">
                {analysis.strong_skill_areas.map((area) => (
                  <div key={area} className="bg-green-50 border-l-4 border-green-400 p-4 rounded">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold text-gray-900 capitalize">
                          {area.replace(/_/g, ' ')}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">
                          Excellent performance in this area!
                        </p>
                      </div>
                      <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                    </div>
                  </div>
                ))}
                {analysis.mastered_exercises.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-semibold text-gray-700 mb-2">
                      Mastered Exercises: {analysis.mastered_exercises.length}
                    </p>
                    <p className="text-xs text-gray-600">
                      These exercises are ready for review cycles
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600">Keep practicing!</p>
                <p className="text-sm text-gray-500">Strengths will appear as you progress</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recommended Adaptations */}
      {hasRecommendations && (
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-600" />
                <h2 className="text-xl font-bold text-gray-900">Recommended Adaptations</h2>
              </div>
              <button
                onClick={handleApplyAdaptations}
                disabled={isApplying}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg disabled:opacity-50 flex items-center gap-2"
              >
                {isApplying ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Applying...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    Apply All
                  </>
                )}
              </button>
            </div>
          </div>
          <div className="p-6">
            <p className="text-gray-600 mb-4">
              Based on your performance, we recommend the following adjustments to optimize your learning:
            </p>
            <div className="space-y-3">
              {analysis.recommended_actions.map((action, index) => (
                <div key={index} className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    <p className="text-gray-900 capitalize">{action.replace(/_/g, ' ')}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> These adaptations will adjust your curriculum difficulty, daily load,
                or add remedial exercises based on your performance patterns.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Progress Trends Placeholder */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-bold text-gray-900">Progress Trends</h2>
          </div>
        </div>
        <div className="p-6">
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Progress Charts Coming Soon</h3>
            <p className="text-gray-600">
              Week-over-week trends and detailed performance charts will be available here.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
