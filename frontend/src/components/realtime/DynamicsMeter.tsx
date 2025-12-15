/**
 * DynamicsMeter Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Real-time dynamics/velocity visualization showing:
 * - Current volume level (RMS/dB)
 * - MIDI velocity range
 * - Dynamic markings (pp, p, mp, mf, f, ff)
 * - Dynamics consistency over time
 */

import { useEffect, useRef, useState } from 'react';
import type { AnalysisResult } from '../../hooks/useWebSocketAnalysis';

export interface DynamicsMeterProps {
  /** Current analysis result from real-time WebSocket */
  latestResult: AnalysisResult | null;
  /** Height of the component in pixels */
  height?: number;
  /** Color theme */
  theme?: 'light' | 'dark';
}

interface DynamicsPoint {
  timestamp: number;
  rms: number;
  db: number;
  velocity: number;
}

/**
 * Get dynamic marking from MIDI velocity
 */
function getDynamicMarking(velocity: number): string {
  if (velocity < 20) return 'pp';
  if (velocity < 40) return 'p';
  if (velocity < 60) return 'mp';
  if (velocity < 80) return 'mf';
  if (velocity < 100) return 'f';
  return 'ff';
}

/**
 * Get dynamic marking color
 */
function getDynamicsColor(velocity: number): string {
  if (velocity < 40) return '#3b82f6'; // Blue for quiet
  if (velocity < 80) return '#10b981'; // Green for moderate
  return '#ef4444'; // Red for loud
}

export function DynamicsMeter({
  latestResult,
  height = 180,
  theme = 'light',
}: DynamicsMeterProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [dynamicsHistory, setDynamicsHistory] = useState<DynamicsPoint[]>([]);
  const [currentVelocity, setCurrentVelocity] = useState<number>(0);
  const [currentRMS, setCurrentRMS] = useState<number>(0);
  const [currentDB, setCurrentDB] = useState<number>(-Infinity);
  const [avgVelocity, setAvgVelocity] = useState<number>(0);
  const animationFrameRef = useRef<number>();

  // Process latest dynamics data
  useEffect(() => {
    if (!latestResult?.dynamics) return;

    const { dynamics } = latestResult;

    // Update current values
    setCurrentVelocity(dynamics.midi_velocity);
    setCurrentRMS(dynamics.rms);
    setCurrentDB(dynamics.db);

    // Update running average
    setAvgVelocity((prev) => {
      const alpha = 0.2; // Smoothing factor
      return prev * (1 - alpha) + dynamics.midi_velocity * alpha;
    });

    // Add to history (keep last 100 points)
    setDynamicsHistory((prev) => {
      const newPoint: DynamicsPoint = {
        timestamp: Date.now(),
        rms: dynamics.rms,
        db: dynamics.db,
        velocity: dynamics.midi_velocity,
      };
      return [...prev, newPoint].slice(-100);
    });
  }, [latestResult]);

  // Canvas rendering (60 FPS)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;

      // Clear canvas
      ctx.fillStyle = theme === 'dark' ? '#1a1a1a' : '#ffffff';
      ctx.fillRect(0, 0, width, height);

      const now = Date.now();
      const timeWindow = 5000; // 5 seconds
      const recentPoints = dynamicsHistory.filter((p) => now - p.timestamp < timeWindow);

      if (recentPoints.length === 0) {
        // No data - show placeholder
        ctx.fillStyle = theme === 'dark' ? '#666' : '#ccc';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No dynamics data yet...', width / 2, height / 2);
        animationFrameRef.current = requestAnimationFrame(render);
        return;
      }

      // Draw dynamic level zones
      const zones = [
        { label: 'ff', max: 127, color: 'rgba(239, 68, 68, 0.1)' },
        { label: 'f', max: 100, color: 'rgba(249, 115, 22, 0.1)' },
        { label: 'mf', max: 80, color: 'rgba(16, 185, 129, 0.1)' },
        { label: 'mp', max: 60, color: 'rgba(59, 130, 246, 0.1)' },
        { label: 'p', max: 40, color: 'rgba(99, 102, 241, 0.1)' },
        { label: 'pp', max: 20, color: 'rgba(139, 92, 246, 0.1)' },
      ];

      zones.forEach((zone) => {
        const zoneHeight = (zone.max / 127) * height;
        ctx.fillStyle = zone.color;
        ctx.fillRect(0, height - zoneHeight, width, zoneHeight);
      });

      // Draw grid lines
      ctx.strokeStyle = theme === 'dark' ? '#333' : '#e5e7eb';
      ctx.lineWidth = 1;
      zones.forEach((zone) => {
        const y = height - (zone.max / 127) * height;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      });

      // Draw velocity line
      if (recentPoints.length > 1) {
        ctx.strokeStyle = theme === 'dark' ? '#60a5fa' : '#3b82f6';
        ctx.lineWidth = 2;
        ctx.beginPath();

        recentPoints.forEach((point, i) => {
          const x = (i / (recentPoints.length - 1)) * width;
          const y = height - (point.velocity / 127) * height;

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });

        ctx.stroke();

        // Draw current point
        const latestPoint = recentPoints[recentPoints.length - 1];
        const x = width;
        const y = height - (latestPoint.velocity / 127) * height;

        ctx.fillStyle = getDynamicsColor(latestPoint.velocity);
        ctx.beginPath();
        ctx.arc(x - 10, y, 5, 0, Math.PI * 2);
        ctx.fill();
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    animationFrameRef.current = requestAnimationFrame(render);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [dynamicsHistory, theme, height]);

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';

  const currentMarking = getDynamicMarking(currentVelocity);
  const avgMarking = getDynamicMarking(avgVelocity);

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${textColor}`}>Dynamics</h3>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className={mutedColor}>Current:</span>
            <span
              className="font-bold text-lg"
              style={{ color: getDynamicsColor(currentVelocity) }}
            >
              {currentMarking}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className={mutedColor}>Average:</span>
            <span
              className="font-semibold"
              style={{ color: getDynamicsColor(avgVelocity) }}
            >
              {avgMarking}
            </span>
          </div>
        </div>
      </div>

      {/* Velocity Meters */}
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center">
          <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
            MIDI Velocity
          </div>
          <div className={`text-2xl font-bold ${textColor}`}>
            {currentVelocity}
          </div>
          <div className={`text-xs ${mutedColor}`}>0-127</div>
        </div>

        <div className="text-center">
          <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
            RMS Level
          </div>
          <div className={`text-2xl font-bold ${textColor}`}>
            {currentRMS.toFixed(3)}
          </div>
          <div className={`text-xs ${mutedColor}`}>0.0-1.0</div>
        </div>

        <div className="text-center">
          <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
            Decibels
          </div>
          <div className={`text-2xl font-bold ${textColor}`}>
            {currentDB === -Infinity ? '-∞' : currentDB.toFixed(1)}
          </div>
          <div className={`text-xs ${mutedColor}`}>dB</div>
        </div>
      </div>

      {/* Dynamics Graph */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={600}
          height={height}
          className="w-full rounded border"
          style={{ border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}` }}
        />

        {/* Y-axis labels */}
        <div className="absolute left-2 top-0 h-full flex flex-col justify-between py-2 text-xs" style={{ color: mutedColor }}>
          <span className="font-semibold">ff (127)</span>
          <span>f (100)</span>
          <span>mf (80)</span>
          <span>mp (60)</span>
          <span>p (40)</span>
          <span>pp (20)</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
        <div className={`text-xs ${mutedColor}`}>
          Last 5 seconds • Blue line shows velocity changes
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className={mutedColor}>Dynamic Range:</span>
          <span className={`font-semibold ${textColor}`}>
            pp to {getDynamicMarking(Math.max(...dynamicsHistory.map((p) => p.velocity)))}
          </span>
        </div>
      </div>
    </div>
  );
}
