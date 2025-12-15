/**
 * AccuracyTrends Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Line chart showing accuracy trends over time:
 * - Pitch accuracy progression
 * - Rhythm accuracy progression
 * - Overall score trend
 * - Configurable time range (7d, 30d, 90d, all)
 * - Canvas-based rendering for performance
 */

import { useEffect, useRef, useState } from 'react';
import { realtimeAnalysisApi, type AnalysisResult } from '../../lib/api';

export interface AccuracyTrendsProps {
  /** User ID to fetch data for */
  userId: number;
  /** Time range for analysis */
  timeRange?: '7d' | '30d' | '90d' | 'all';
  /** Height of the chart in pixels */
  height?: number;
  /** Color theme */
  theme?: 'light' | 'dark';
}

interface DataPoint {
  date: Date;
  pitchAccuracy: number;
  rhythmAccuracy: number;
  overallScore: number;
}

/**
 * Aggregate analysis results by day
 */
function aggregateByDay(results: AnalysisResult[]): DataPoint[] {
  const dayMap = new Map<string, { pitch: number[]; rhythm: number[]; overall: number[] }>();

  results.forEach((result) => {
    const date = new Date(result.created_at);
    const dayKey = date.toISOString().split('T')[0]; // YYYY-MM-DD

    if (!dayMap.has(dayKey)) {
      dayMap.set(dayKey, { pitch: [], rhythm: [], overall: [] });
    }

    const day = dayMap.get(dayKey)!;

    if (result.pitch_accuracy !== undefined) {
      day.pitch.push(result.pitch_accuracy);
    }
    if (result.rhythm_accuracy !== undefined) {
      day.rhythm.push(result.rhythm_accuracy);
    }
    if (result.overall_score !== undefined) {
      day.overall.push(result.overall_score);
    }
  });

  // Calculate averages for each day
  const dataPoints: DataPoint[] = [];
  dayMap.forEach((values, dayKey) => {
    const avgPitch = values.pitch.length > 0
      ? values.pitch.reduce((a, b) => a + b, 0) / values.pitch.length
      : 0;
    const avgRhythm = values.rhythm.length > 0
      ? values.rhythm.reduce((a, b) => a + b, 0) / values.rhythm.length
      : 0;
    const avgOverall = values.overall.length > 0
      ? values.overall.reduce((a, b) => a + b, 0) / values.overall.length
      : 0;

    dataPoints.push({
      date: new Date(dayKey),
      pitchAccuracy: avgPitch,
      rhythmAccuracy: avgRhythm,
      overallScore: avgOverall,
    });
  });

  return dataPoints.sort((a, b) => a.date.getTime() - b.date.getTime());
}

export function AccuracyTrends({
  userId,
  timeRange = '30d',
  height = 300,
  theme = 'light',
}: AccuracyTrendsProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [dataPoints, setDataPoints] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRange, setSelectedRange] = useState<'7d' | '30d' | '90d' | 'all'>(timeRange);
  const [showPitch, setShowPitch] = useState<boolean>(true);
  const [showRhythm, setShowRhythm] = useState<boolean>(true);
  const [showOverall, setShowOverall] = useState<boolean>(true);

  // Fetch analysis results
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const days = selectedRange === 'all' ? 365 : parseInt(selectedRange);
        const results = await realtimeAnalysisApi.getUserAnalysisHistory({
          userId,
          days,
        });

        const aggregated = aggregateByDay(results);
        setDataPoints(aggregated);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId, selectedRange]);

  // Canvas rendering
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || dataPoints.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const padding = { top: 20, right: 20, bottom: 40, left: 50 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Clear canvas
    ctx.fillStyle = theme === 'dark' ? '#1a1a1a' : '#ffffff';
    ctx.fillRect(0, 0, width, height);

    if (dataPoints.length === 0) {
      ctx.fillStyle = theme === 'dark' ? '#666' : '#ccc';
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No data available', width / 2, height / 2);
      return;
    }

    // Draw grid
    ctx.strokeStyle = theme === 'dark' ? '#333' : '#e5e7eb';
    ctx.lineWidth = 1;

    // Horizontal grid lines (10%, 20%, ..., 100%)
    for (let i = 0; i <= 10; i++) {
      const y = padding.top + (chartHeight * (10 - i)) / 10;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartWidth, y);
      ctx.stroke();

      // Y-axis labels
      ctx.fillStyle = theme === 'dark' ? '#888' : '#666';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(`${i * 10}%`, padding.left - 10, y + 4);
    }

    // Vertical grid lines (dates)
    const dateStep = Math.max(1, Math.floor(dataPoints.length / 5));
    dataPoints.forEach((point, i) => {
      if (i % dateStep === 0) {
        const x = padding.left + (i / (dataPoints.length - 1)) * chartWidth;
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, padding.top + chartHeight);
        ctx.stroke();

        // X-axis labels
        ctx.save();
        ctx.translate(x, padding.top + chartHeight + 15);
        ctx.rotate(-Math.PI / 4);
        ctx.fillStyle = theme === 'dark' ? '#888' : '#666';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(point.date.toLocaleDateString(), 0, 0);
        ctx.restore();
      }
    });

    // Draw data lines
    const drawLine = (
      data: number[],
      color: string,
      label: string,
      visible: boolean
    ) => {
      if (!visible) return;

      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();

      data.forEach((value, i) => {
        const x = padding.left + (i / (data.length - 1)) * chartWidth;
        const y = padding.top + chartHeight - (value * chartHeight);

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();

      // Draw points
      ctx.fillStyle = color;
      data.forEach((value, i) => {
        const x = padding.left + (i / (data.length - 1)) * chartWidth;
        const y = padding.top + chartHeight - (value * chartHeight);
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
      });
    };

    // Plot lines
    if (showPitch) {
      drawLine(
        dataPoints.map((d) => d.pitchAccuracy),
        '#3b82f6',
        'Pitch',
        true
      );
    }

    if (showRhythm) {
      drawLine(
        dataPoints.map((d) => d.rhythmAccuracy),
        '#10b981',
        'Rhythm',
        true
      );
    }

    if (showOverall) {
      drawLine(
        dataPoints.map((d) => d.overallScore),
        '#8b5cf6',
        'Overall',
        true
      );
    }
  }, [dataPoints, theme, showPitch, showRhythm, showOverall]);

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
          <span className={`ml-3 ${mutedColor}`}>Loading trends...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${bgColor} rounded-lg shadow-md p-6`}>
        <div className="text-center py-12">
          <p className="text-red-600 mb-2">Error loading trends</p>
          <p className={`text-sm ${mutedColor}`}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${textColor}`}>Accuracy Trends</h3>

        {/* Time Range Selector */}
        <div className="flex gap-2">
          {(['7d', '30d', '90d', 'all'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setSelectedRange(range)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                selectedRange === range
                  ? 'bg-blue-500 text-white'
                  : `${mutedColor} hover:bg-gray-100 dark:hover:bg-gray-700`
              }`}
            >
              {range === 'all' ? 'All' : range.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Legend / Toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setShowPitch(!showPitch)}
          className="flex items-center gap-2 text-sm"
        >
          <div
            className={`w-3 h-3 rounded-full transition-opacity ${
              showPitch ? 'opacity-100' : 'opacity-30'
            }`}
            style={{ backgroundColor: '#3b82f6' }}
          />
          <span className={showPitch ? textColor : mutedColor}>Pitch</span>
        </button>

        <button
          onClick={() => setShowRhythm(!showRhythm)}
          className="flex items-center gap-2 text-sm"
        >
          <div
            className={`w-3 h-3 rounded-full transition-opacity ${
              showRhythm ? 'opacity-100' : 'opacity-30'
            }`}
            style={{ backgroundColor: '#10b981' }}
          />
          <span className={showRhythm ? textColor : mutedColor}>Rhythm</span>
        </button>

        <button
          onClick={() => setShowOverall(!showOverall)}
          className="flex items-center gap-2 text-sm"
        >
          <div
            className={`w-3 h-3 rounded-full transition-opacity ${
              showOverall ? 'opacity-100' : 'opacity-30'
            }`}
            style={{ backgroundColor: '#8b5cf6' }}
          />
          <span className={showOverall ? textColor : mutedColor}>Overall</span>
        </button>
      </div>

      {/* Chart */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={800}
          height={height}
          className="w-full rounded border"
          style={{ border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}` }}
        />
      </div>

      {/* Stats Summary */}
      {dataPoints.length > 0 && (
        <div className="grid grid-cols-3 gap-3 pt-2 border-t" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
          <div className="text-center">
            <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
              Avg Pitch
            </div>
            <div className={`text-xl font-bold ${textColor}`}>
              {(
                (dataPoints.reduce((sum, d) => sum + d.pitchAccuracy, 0) /
                  dataPoints.length) *
                100
              ).toFixed(0)}
              %
            </div>
          </div>

          <div className="text-center">
            <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
              Avg Rhythm
            </div>
            <div className={`text-xl font-bold ${textColor}`}>
              {(
                (dataPoints.reduce((sum, d) => sum + d.rhythmAccuracy, 0) /
                  dataPoints.length) *
                100
              ).toFixed(0)}
              %
            </div>
          </div>

          <div className="text-center">
            <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
              Avg Overall
            </div>
            <div className={`text-xl font-bold ${textColor}`}>
              {(
                (dataPoints.reduce((sum, d) => sum + d.overallScore, 0) /
                  dataPoints.length) *
                100
              ).toFixed(0)}
              %
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
