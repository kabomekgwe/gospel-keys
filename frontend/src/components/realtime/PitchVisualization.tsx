/**
 * PitchVisualization Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Real-time pitch accuracy visualization showing:
 * - Current note being played
 * - Pitch accuracy (cents deviation from target)
 * - Confidence meter
 * - Visual pitch tracking over time
 */

import { useEffect, useRef, useState } from 'react';
import type { AnalysisResult } from '../../hooks/useWebSocketAnalysis';

export interface PitchVisualizationProps {
  /** Current analysis result from real-time WebSocket */
  latestResult: AnalysisResult | null;
  /** Show detailed pitch deviation in cents */
  showDeviation?: boolean;
  /** Height of the component in pixels */
  height?: number;
  /** Color theme */
  theme?: 'light' | 'dark';
}

interface PitchHistoryPoint {
  timestamp: number;
  frequency: number;
  noteName: string;
  confidence: number;
  centsDeviation: number;
}

/**
 * Calculate cents deviation from target frequency
 * 1 semitone = 100 cents
 */
function calculateCents(actualFreq: number, targetFreq: number): number {
  if (targetFreq === 0) return 0;
  return 1200 * Math.log2(actualFreq / targetFreq);
}

/**
 * Get MIDI note number from frequency
 */
function frequencyToMidi(frequency: number): number {
  return Math.round(12 * Math.log2(frequency / 440) + 69);
}

/**
 * Get target frequency for a MIDI note
 */
function midiToFrequency(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

export function PitchVisualization({
  latestResult,
  showDeviation = true,
  height = 200,
  theme = 'light',
}: PitchVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [pitchHistory, setPitchHistory] = useState<PitchHistoryPoint[]>([]);
  const [currentNote, setCurrentNote] = useState<string>('---');
  const [currentDeviation, setCurrentDeviation] = useState<number>(0);
  const [currentConfidence, setCurrentConfidence] = useState<number>(0);
  const animationFrameRef = useRef<number>();

  // Process latest pitch data
  useEffect(() => {
    if (!latestResult?.pitch) return;

    const { pitch } = latestResult;

    if (pitch.is_voiced && pitch.frequency > 0) {
      // Calculate target frequency and deviation
      const midiNote = frequencyToMidi(pitch.frequency);
      const targetFreq = midiToFrequency(midiNote);
      const centsDeviation = calculateCents(pitch.frequency, targetFreq);

      // Update state
      setCurrentNote(pitch.note_name || '---');
      setCurrentDeviation(centsDeviation);
      setCurrentConfidence(pitch.confidence);

      // Add to history (keep last 100 points)
      setPitchHistory((prev) => {
        const newPoint: PitchHistoryPoint = {
          timestamp: Date.now(),
          frequency: pitch.frequency,
          noteName: pitch.note_name || '---',
          confidence: pitch.confidence,
          centsDeviation,
        };
        const updated = [...prev, newPoint].slice(-100);
        return updated;
      });
    } else {
      // No pitch detected
      setCurrentNote('---');
      setCurrentDeviation(0);
      setCurrentConfidence(0);
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

      if (pitchHistory.length === 0) {
        // No data - show placeholder
        ctx.fillStyle = theme === 'dark' ? '#666' : '#ccc';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No pitch data yet...', width / 2, height / 2);
        animationFrameRef.current = requestAnimationFrame(render);
        return;
      }

      // Draw pitch history graph
      const now = Date.now();
      const timeWindow = 5000; // 5 seconds
      const recentPoints = pitchHistory.filter((p) => now - p.timestamp < timeWindow);

      if (recentPoints.length > 1) {
        // Draw grid lines (cents deviation)
        ctx.strokeStyle = theme === 'dark' ? '#333' : '#eee';
        ctx.lineWidth = 1;

        // Center line (0 cents)
        const centerY = height / 2;
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(width, centerY);
        ctx.stroke();

        // +/- 25 cents lines
        const centsScale = height / 100; // 50 cents = half height
        [-25, 25].forEach((cents) => {
          const y = centerY - cents * centsScale;
          ctx.beginPath();
          ctx.setLineDash([5, 5]);
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
          ctx.stroke();
          ctx.setLineDash([]);
        });

        // Draw pitch deviation line
        ctx.strokeStyle = theme === 'dark' ? '#60a5fa' : '#3b82f6';
        ctx.lineWidth = 2;
        ctx.beginPath();

        recentPoints.forEach((point, i) => {
          const x = (i / (recentPoints.length - 1)) * width;
          const y = centerY - point.centsDeviation * centsScale;

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });

        ctx.stroke();

        // Draw confidence as opacity overlay
        const latestPoint = recentPoints[recentPoints.length - 1];
        if (latestPoint) {
          const x = width;
          const y = centerY - latestPoint.centsDeviation * centsScale;

          // Draw current point
          ctx.fillStyle = theme === 'dark' ? '#60a5fa' : '#3b82f6';
          ctx.globalAlpha = latestPoint.confidence;
          ctx.beginPath();
          ctx.arc(x - 10, y, 6, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1;
        }
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    animationFrameRef.current = requestAnimationFrame(render);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [pitchHistory, theme, height]);

  // Get accuracy color based on cents deviation
  const getAccuracyColor = (cents: number): string => {
    const absCents = Math.abs(cents);
    if (absCents < 10) return 'text-green-600';
    if (absCents < 25) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get accuracy label
  const getAccuracyLabel = (cents: number): string => {
    const absCents = Math.abs(cents);
    if (absCents < 10) return 'Excellent';
    if (absCents < 25) return 'Good';
    if (absCents < 50) return 'Fair';
    return 'Needs Work';
  };

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${textColor}`}>Pitch Accuracy</h3>
        <div className="flex items-center gap-2">
          <span className={`text-xs ${mutedColor}`}>Confidence:</span>
          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-150"
              style={{ width: `${currentConfidence * 100}%` }}
            />
          </div>
          <span className={`text-xs ${mutedColor} w-10 text-right`}>
            {(currentConfidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Current Note Display */}
      <div className="flex items-center justify-center gap-6 py-3">
        <div className="text-center">
          <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
            Current Note
          </div>
          <div className={`text-4xl font-bold ${textColor}`}>{currentNote}</div>
        </div>

        {showDeviation && currentNote !== '---' && (
          <>
            <div className="text-center">
              <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
                Deviation
              </div>
              <div className={`text-2xl font-semibold ${getAccuracyColor(currentDeviation)}`}>
                {currentDeviation > 0 ? '+' : ''}
                {currentDeviation.toFixed(1)}¢
              </div>
            </div>

            <div className="text-center">
              <div className={`text-xs uppercase tracking-wide ${mutedColor} mb-1`}>
                Accuracy
              </div>
              <div className={`text-lg font-medium ${getAccuracyColor(currentDeviation)}`}>
                {getAccuracyLabel(currentDeviation)}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Pitch Deviation Graph */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={600}
          height={height}
          className="w-full rounded border"
          style={{ border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}` }}
        />

        {/* Y-axis labels */}
        <div className="absolute left-2 top-0 h-full flex flex-col justify-between py-2">
          <span className={`text-xs ${mutedColor}`}>+50¢</span>
          <span className={`text-xs ${mutedColor}`}>+25¢</span>
          <span className={`text-xs ${mutedColor} font-semibold`}>0¢</span>
          <span className={`text-xs ${mutedColor}`}>-25¢</span>
          <span className={`text-xs ${mutedColor}`}>-50¢</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
        <div className={`text-xs ${mutedColor}`}>
          Last 5 seconds • Blue line shows pitch deviation
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className={mutedColor}>±10¢</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className={mutedColor}>±25¢</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className={mutedColor}>&gt;25¢</span>
          </div>
        </div>
      </div>
    </div>
  );
}
