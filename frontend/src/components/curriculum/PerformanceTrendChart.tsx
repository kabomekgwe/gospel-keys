import { useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface PerformanceTrendChartProps {
  weeklyData: {
    week: number;
    avgQualityScore: number;
    exercisesCompleted: number;
    completionRate: number;
  }[];
  milestoneWeeks?: number[];
}

export function PerformanceTrendChart({
  weeklyData,
  milestoneWeeks = [],
}: PerformanceTrendChartProps) {
  const stats = useMemo(() => {
    if (weeklyData.length === 0) return null;

    const latestWeek = weeklyData[weeklyData.length - 1];
    const previousWeek = weeklyData.length > 1 ? weeklyData[weeklyData.length - 2] : null;

    const qualityTrend = previousWeek
      ? latestWeek.avgQualityScore - previousWeek.avgQualityScore
      : 0;

    const avgQuality =
      weeklyData.reduce((sum, w) => sum + w.avgQualityScore, 0) / weeklyData.length;
    const avgCompletion =
      weeklyData.reduce((sum, w) => sum + w.completionRate, 0) / weeklyData.length;

    return {
      latestQuality: latestWeek.avgQualityScore,
      qualityTrend,
      avgQuality,
      avgCompletion,
      totalExercises: weeklyData.reduce((sum, w) => sum + w.exercisesCompleted, 0),
    };
  }, [weeklyData]);

  // Chart dimensions
  const width = 700;
  const height = 300;
  const padding = { top: 40, right: 40, bottom: 40, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Data ranges
  const maxWeek = Math.max(...weeklyData.map((d) => d.week));
  const minWeek = Math.min(...weeklyData.map((d) => d.week));
  const maxQuality = 5;
  const minQuality = 0;

  // Scale functions
  const scaleX = (week: number) => {
    return padding.left + ((week - minWeek) / (maxWeek - minWeek)) * chartWidth;
  };

  const scaleY = (quality: number) => {
    return padding.top + chartHeight - ((quality - minQuality) / (maxQuality - minQuality)) * chartHeight;
  };

  // Create line path
  const linePath = useMemo(() => {
    if (weeklyData.length === 0) return '';

    const points = weeklyData.map((d) => `${scaleX(d.week)},${scaleY(d.avgQualityScore)}`);
    return `M ${points.join(' L ')}`;
  }, [weeklyData]);

  // Create area path (for gradient fill)
  const areaPath = useMemo(() => {
    if (weeklyData.length === 0) return '';

    const points = weeklyData.map((d) => `${scaleX(d.week)},${scaleY(d.avgQualityScore)}`);
    const firstX = scaleX(weeklyData[0].week);
    const lastX = scaleX(weeklyData[weeklyData.length - 1].week);
    const bottomY = scaleY(0);

    return `M ${firstX},${bottomY} L ${points.join(' L ')} L ${lastX},${bottomY} Z`;
  }, [weeklyData]);

  const getTrendIcon = (trend: number) => {
    if (trend > 0.1) return <TrendingUp className="w-4 h-4 text-green-400" />;
    if (trend < -0.1) return <TrendingDown className="w-4 h-4 text-red-400" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  const getTrendColor = (trend: number) => {
    if (trend > 0.1) return 'text-green-400';
    if (trend < -0.1) return 'text-red-400';
    return 'text-gray-400';
  };

  const getTrendText = (trend: number) => {
    if (trend > 0.1) return `+${trend.toFixed(2)}`;
    if (trend < -0.1) return trend.toFixed(2);
    return 'Stable';
  };

  if (!stats) {
    return (
      <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-4">Performance Trends</h3>
        <div className="text-center py-12">
          <p className="text-gray-400">No performance data available yet</p>
          <p className="text-sm text-gray-500 mt-2">Complete some exercises to see your progress</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-white">Performance Trends</h3>
        <div className="flex items-center gap-2">
          {getTrendIcon(stats.qualityTrend)}
          <span className={`text-sm font-medium ${getTrendColor(stats.qualityTrend)}`}>
            {getTrendText(stats.qualityTrend)}
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-900/50 p-3 rounded-lg">
          <p className="text-xs text-gray-400 mb-1">Current Quality</p>
          <p className="text-2xl font-bold text-white">{stats.latestQuality.toFixed(1)}</p>
          <p className="text-xs text-gray-500">out of 5.0</p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded-lg">
          <p className="text-xs text-gray-400 mb-1">Avg Quality</p>
          <p className="text-2xl font-bold text-purple-400">{stats.avgQuality.toFixed(1)}</p>
          <p className="text-xs text-gray-500">all weeks</p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded-lg">
          <p className="text-xs text-gray-400 mb-1">Completion Rate</p>
          <p className="text-2xl font-bold text-blue-400">{stats.avgCompletion.toFixed(0)}%</p>
          <p className="text-xs text-gray-500">average</p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded-lg">
          <p className="text-xs text-gray-400 mb-1">Total Exercises</p>
          <p className="text-2xl font-bold text-green-400">{stats.totalExercises}</p>
          <p className="text-xs text-gray-500">completed</p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-900/30 p-4 rounded-lg overflow-x-auto">
        <svg width={width} height={height} className="mx-auto">
          <defs>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgb(139, 92, 246)" stopOpacity="0.3" />
              <stop offset="100%" stopColor="rgb(139, 92, 246)" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 1, 2, 3, 4, 5].map((value) => {
            const y = scaleY(value);
            return (
              <g key={value}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-gray-700"
                  opacity={0.3}
                />
                <text
                  x={padding.left - 10}
                  y={y}
                  textAnchor="end"
                  alignmentBaseline="middle"
                  className="text-xs fill-gray-400"
                >
                  {value}
                </text>
              </g>
            );
          })}

          {/* X-axis labels */}
          {weeklyData.map((d, i) => {
            const x = scaleX(d.week);
            const isMilestone = milestoneWeeks.includes(d.week);
            return (
              <g key={i}>
                {/* Milestone marker */}
                {isMilestone && (
                  <rect
                    x={x - 1}
                    y={padding.top}
                    width="2"
                    height={chartHeight}
                    fill="rgb(234, 179, 8)"
                    opacity="0.3"
                  />
                )}
                <text
                  x={x}
                  y={height - padding.bottom + 20}
                  textAnchor="middle"
                  className={`text-xs ${isMilestone ? 'fill-yellow-500 font-semibold' : 'fill-gray-400'}`}
                >
                  W{d.week}
                </text>
              </g>
            );
          })}

          {/* Area fill */}
          <path d={areaPath} fill="url(#areaGradient)" />

          {/* Line */}
          <path
            d={linePath}
            fill="none"
            stroke="rgb(139, 92, 246)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {weeklyData.map((d, i) => {
            const x = scaleX(d.week);
            const y = scaleY(d.avgQualityScore);
            const isLatest = i === weeklyData.length - 1;

            return (
              <g key={i}>
                <circle
                  cx={x}
                  cy={y}
                  r={isLatest ? 6 : 4}
                  fill="rgb(139, 92, 246)"
                  className="drop-shadow-lg"
                />
                {isLatest && (
                  <circle
                    cx={x}
                    cy={y}
                    r={8}
                    fill="none"
                    stroke="rgb(139, 92, 246)"
                    strokeWidth="2"
                    opacity="0.5"
                  />
                )}
              </g>
            );
          })}

          {/* Chart labels */}
          <text
            x={padding.left - 35}
            y={padding.top + chartHeight / 2}
            textAnchor="middle"
            className="text-xs fill-gray-400"
            transform={`rotate(-90, ${padding.left - 35}, ${padding.top + chartHeight / 2})`}
          >
            Quality Score
          </text>
          <text
            x={padding.left + chartWidth / 2}
            y={height - 5}
            textAnchor="middle"
            className="text-xs fill-gray-400"
          >
            Week
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-1 bg-purple-500 rounded" />
          <span className="text-gray-400">Quality Score</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500/30 rounded" />
          <span className="text-gray-400">Milestone Week</span>
        </div>
      </div>
    </div>
  );
}
