/**
 * RhythmGrid Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Real-time rhythm/onset visualization showing:
 * - Onset detection events over time
 * - Timing consistency grid
 * - Tempo stability indicator
 * - Visual metronome alignment
 */

import { useEffect, useRef, useState } from 'react';
import type { AnalysisResult } from '../../hooks/useWebSocketAnalysis';

export interface RhythmGridProps {
  /** Current analysis result from real-time WebSocket */
  latestResult: AnalysisResult | null;
  /** Target tempo in BPM (for metronome grid) */
  targetTempo?: number;
  /** Height of the component in pixels */
  height?: number;
  /** Color theme */
  theme?: 'light' | 'dark';
}

interface OnsetEvent {
  timestamp: number;
  strength: number; // 0.0-1.0
  relativeTime: number; // Relative to window start
}

export function RhythmGrid({
  latestResult,
  targetTempo = 120,
  height = 150,
  theme = 'light',
}: RhythmGridProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [onsetHistory, setOnsetHistory] = useState<OnsetEvent[]>([]);
  const [onsetCount, setOnsetCount] = useState<number>(0);
  const [avgOnsetStrength, setAvgOnsetStrength] = useState<number>(0);
  const animationFrameRef = useRef<number>();

  // Process latest onset data
  useEffect(() => {
    if (!latestResult?.onsets) return;

    const { onsets } = latestResult;

    if (onsets.count > 0) {
      // Add new onset to history
      const newOnset: OnsetEvent = {
        timestamp: Date.now(),
        strength: onsets.max_strength,
        relativeTime: 0,
      };

      setOnsetHistory((prev) => {
        const updated = [...prev, newOnset].slice(-50); // Keep last 50 onsets
        return updated;
      });

      setOnsetCount((prev) => prev + 1);

      // Update average onset strength
      setAvgOnsetStrength((prev) => {
        const alpha = 0.1; // Smoothing factor
        return prev * (1 - alpha) + onsets.max_strength * alpha;
      });
    }
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
      const recentOnsets = onsetHistory.filter((o) => now - o.timestamp < timeWindow);

      // Draw tempo grid (metronome beats)
      if (targetTempo > 0) {
        const beatInterval = (60 / targetTempo) * 1000; // ms per beat
        const beatsInWindow = Math.ceil(timeWindow / beatInterval);

        ctx.strokeStyle = theme === 'dark' ? '#333' : '#e5e7eb';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);

        for (let i = 0; i <= beatsInWindow; i++) {
          const x = (i / beatsInWindow) * width;
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
          ctx.stroke();
        }

        ctx.setLineDash([]);
      }

      // Draw onset events
      if (recentOnsets.length > 0) {
        recentOnsets.forEach((onset) => {
          const age = now - onset.timestamp;
          const x = ((timeWindow - age) / timeWindow) * width;
          const barHeight = onset.strength * height * 0.8;
          const y = height - barHeight;

          // Color based on strength
          const alpha = Math.max(0.3, 1 - age / timeWindow);
          if (onset.strength > 0.7) {
            ctx.fillStyle = `rgba(239, 68, 68, ${alpha})`; // Strong - red
          } else if (onset.strength > 0.4) {
            ctx.fillStyle = `rgba(59, 130, 246, ${alpha})`; // Medium - blue
          } else {
            ctx.fillStyle = `rgba(156, 163, 175, ${alpha})`; // Weak - gray
          }

          // Draw onset bar
          ctx.fillRect(x - 2, y, 4, barHeight);

          // Draw onset marker at top
          ctx.beginPath();
          ctx.arc(x, 10, 3, 0, Math.PI * 2);
          ctx.fill();
        });
      } else {
        // No data - show placeholder
        ctx.fillStyle = theme === 'dark' ? '#666' : '#ccc';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No onset data yet...', width / 2, height / 2);
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    animationFrameRef.current = requestAnimationFrame(render);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [onsetHistory, targetTempo, theme, height]);

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${textColor}`}>Rhythm & Timing</h3>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className={mutedColor}>Tempo:</span>
            <span className={`font-semibold ${textColor}`}>{targetTempo} BPM</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={mutedColor}>Onsets:</span>
            <span className={`font-semibold ${textColor}`}>{onsetCount}</span>
          </div>
        </div>
      </div>

      {/* Onset Strength Meter */}
      <div className="flex items-center gap-3">
        <span className={`text-sm ${mutedColor}`}>Avg Strength:</span>
        <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-300"
            style={{
              width: `${avgOnsetStrength * 100}%`,
              backgroundColor:
                avgOnsetStrength > 0.7
                  ? '#ef4444'
                  : avgOnsetStrength > 0.4
                  ? '#3b82f6'
                  : '#9ca3af',
            }}
          />
        </div>
        <span className={`text-sm font-medium ${textColor} w-12 text-right`}>
          {(avgOnsetStrength * 100).toFixed(0)}%
        </span>
      </div>

      {/* Rhythm Grid Canvas */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={600}
          height={height}
          className="w-full rounded border"
          style={{ border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}` }}
        />

        {/* Time axis label */}
        <div className="flex justify-between text-xs mt-1" style={{ color: mutedColor }}>
          <span>5s ago</span>
          <span>Now</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
        <div className={`text-xs ${mutedColor}`}>
          Vertical lines = metronome beats • Bars = onset events
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className={mutedColor}>Strong</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className={mutedColor}>Medium</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-gray-400" />
            <span className={mutedColor}>Weak</span>
          </div>
        </div>
      </div>
    </div>
  );
}
