/**
 * SkillLevelChart Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Radar/spider chart showing skill level across multiple dimensions:
 * - Pitch accuracy
 * - Rhythm accuracy
 * - Dynamics control
 * - Overall proficiency
 * - Progress indicators showing improvement
 */

import { useEffect, useRef, useState } from 'react';
import { realtimeAnalysisApi, type ProgressMetric } from '../../lib/api';

export interface SkillLevelChartProps {
  /** User ID to fetch metrics for */
  userId: number;
  /** Compare with previous period */
  showComparison?: boolean;
  /** Size of the chart in pixels */
  size?: number;
  /** Color theme */
  theme?: 'light' | 'dark';
}

interface SkillMetrics {
  pitch: number; // 0.0 - 1.0
  rhythm: number;
  dynamics: number;
  overall: number;
}

/**
 * Calculate skill metrics from progress data
 */
function calculateSkillMetrics(metrics: ProgressMetric[]): SkillMetrics {
  if (metrics.length === 0) {
    return { pitch: 0, rhythm: 0, dynamics: 0, overall: 0 };
  }

  // Use most recent metric
  const latest = metrics[metrics.length - 1];

  return {
    pitch: latest.pitch_avg,
    rhythm: latest.rhythm_avg,
    dynamics: latest.dynamics_avg,
    overall: latest.overall_avg,
  };
}

/**
 * Draw radar chart on canvas
 */
function drawRadarChart(
  ctx: CanvasRenderingContext2D,
  metrics: SkillMetrics,
  previousMetrics: SkillMetrics | null,
  size: number,
  theme: 'light' | 'dark'
) {
  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size * 0.35;
  const labels = ['Pitch', 'Rhythm', 'Dynamics', 'Overall'];
  const values = [metrics.pitch, metrics.rhythm, metrics.dynamics, metrics.overall];
  const previousValues = previousMetrics
    ? [previousMetrics.pitch, previousMetrics.rhythm, previousMetrics.dynamics, previousMetrics.overall]
    : null;
  const numAxes = labels.length;

  // Clear canvas
  ctx.fillStyle = theme === 'dark' ? '#1a1a1a' : '#ffffff';
  ctx.fillRect(0, 0, size, size);

  // Draw background grid circles
  ctx.strokeStyle = theme === 'dark' ? '#333' : '#e5e7eb';
  ctx.lineWidth = 1;

  for (let i = 1; i <= 5; i++) {
    const r = (radius / 5) * i;
    ctx.beginPath();
    ctx.arc(centerX, centerY, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Draw axes
  ctx.strokeStyle = theme === 'dark' ? '#555' : '#d1d5db';
  ctx.lineWidth = 1;

  for (let i = 0; i < numAxes; i++) {
    const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);

    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(x, y);
    ctx.stroke();

    // Draw labels
    const labelDist = radius + 30;
    const labelX = centerX + labelDist * Math.cos(angle);
    const labelY = centerY + labelDist * Math.sin(angle);

    ctx.fillStyle = theme === 'dark' ? '#888' : '#666';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(labels[i], labelX, labelY);

    // Draw percentage labels
    const valueLabelDist = radius + 15;
    const valueLabelX = centerX + valueLabelDist * Math.cos(angle);
    const valueLabelY = centerY + valueLabelDist * Math.sin(angle);

    ctx.fillStyle = theme === 'dark' ? '#aaa' : '#999';
    ctx.font = '10px sans-serif';
    ctx.fillText(`${(values[i] * 100).toFixed(0)}%`, valueLabelX, valueLabelY);
  }

  // Draw previous period data (if available)
  if (previousValues) {
    ctx.strokeStyle = theme === 'dark' ? 'rgba(156, 163, 175, 0.4)' : 'rgba(156, 163, 175, 0.6)';
    ctx.fillStyle = theme === 'dark' ? 'rgba(156, 163, 175, 0.1)' : 'rgba(156, 163, 175, 0.2)';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    ctx.beginPath();
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
      const value = previousValues[i];
      const x = centerX + radius * value * Math.cos(angle);
      const y = centerY + radius * value * Math.sin(angle);

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // Draw current data
  ctx.strokeStyle = theme === 'dark' ? '#60a5fa' : '#3b82f6';
  ctx.fillStyle = theme === 'dark' ? 'rgba(96, 165, 250, 0.2)' : 'rgba(59, 130, 246, 0.2)';
  ctx.lineWidth = 2;

  ctx.beginPath();
  for (let i = 0; i < numAxes; i++) {
    const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
    const value = values[i];
    const x = centerX + radius * value * Math.cos(angle);
    const y = centerY + radius * value * Math.sin(angle);

    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // Draw data points
  ctx.fillStyle = theme === 'dark' ? '#60a5fa' : '#3b82f6';
  for (let i = 0; i < numAxes; i++) {
    const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
    const value = values[i];
    const x = centerX + radius * value * Math.cos(angle);
    const y = centerY + radius * value * Math.sin(angle);

    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  }
}

export function SkillLevelChart({
  userId,
  showComparison = true,
  size = 400,
  theme = 'light',
}: SkillLevelChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [currentMetrics, setCurrentMetrics] = useState<SkillMetrics>({
    pitch: 0,
    rhythm: 0,
    dynamics: 0,
    overall: 0,
  });
  const [previousMetrics, setPreviousMetrics] = useState<SkillMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch progress metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      setError(null);

      try {
        // Get current period (last 30 days)
        const currentData = await realtimeAnalysisApi.getUserProgressMetrics({
          userId,
          days: 30,
        });

        if (currentData.length > 0) {
          setCurrentMetrics(calculateSkillMetrics(currentData));
        }

        // Get previous period (30-60 days ago) for comparison
        if (showComparison) {
          const previousData = await realtimeAnalysisApi.getUserProgressMetrics({
            userId,
            days: 60,
          });

          // Filter to get 30-60 day range
          const thirtyDaysAgo = new Date();
          thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

          const previousPeriod = previousData.filter((metric) => {
            const metricDate = new Date(metric.created_at);
            return metricDate < thirtyDaysAgo;
          });

          if (previousPeriod.length > 0) {
            setPreviousMetrics(calculateSkillMetrics(previousPeriod));
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [userId, showComparison]);

  // Canvas rendering
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || loading) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    drawRadarChart(ctx, currentMetrics, previousMetrics, size, theme);
  }, [currentMetrics, previousMetrics, size, theme, loading]);

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';

  if (loading) {
    return (
      <div className={`${bgColor} rounded-lg shadow-md p-6`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          <span className={`ml-3 ${mutedColor}`}>Loading skill levels...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${bgColor} rounded-lg shadow-md p-6`}>
        <div className="text-center py-12">
          <p className="text-red-600 mb-2">Error loading skill levels</p>
          <p className={`text-sm ${mutedColor}`}>{error}</p>
        </div>
      </div>
    );
  }

  // Calculate improvement
  const improvements = previousMetrics
    ? {
        pitch: ((currentMetrics.pitch - previousMetrics.pitch) * 100).toFixed(1),
        rhythm: ((currentMetrics.rhythm - previousMetrics.rhythm) * 100).toFixed(1),
        dynamics: ((currentMetrics.dynamics - previousMetrics.dynamics) * 100).toFixed(1),
        overall: ((currentMetrics.overall - previousMetrics.overall) * 100).toFixed(1),
      }
    : null;

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${textColor}`}>Skill Level</h3>
        <span className={`text-sm ${mutedColor}`}>Last 30 days</span>
      </div>

      {/* Chart */}
      <div className="flex justify-center">
        <canvas ref={canvasRef} width={size} height={size} />
      </div>

      {/* Legend */}
      {showComparison && previousMetrics && (
        <div className="flex items-center justify-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-blue-500" />
            <span className={mutedColor}>Current</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 border-t-2 border-dashed border-gray-400" />
            <span className={mutedColor}>Previous</span>
          </div>
        </div>
      )}

      {/* Improvement Indicators */}
      {improvements && (
        <div className="grid grid-cols-4 gap-2 pt-2 border-t" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
          {Object.entries(improvements).map(([key, value]) => {
            const improvement = parseFloat(value);
            const isPositive = improvement > 0;
            const isNeutral = improvement === 0;

            return (
              <div key={key} className="text-center">
                <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
                  {key}
                </div>
                <div
                  className={`text-sm font-semibold ${
                    isNeutral
                      ? mutedColor
                      : isPositive
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {isPositive ? '+' : ''}
                  {value}%
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* No data message */}
      {currentMetrics.overall === 0 && (
        <div className="text-center py-6">
          <p className={`text-sm ${mutedColor}`}>
            No skill data yet. Complete some practice sessions to see your skill level!
          </p>
        </div>
      )}
    </div>
  );
}
