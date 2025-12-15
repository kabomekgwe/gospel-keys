/**
 * FeedbackPanel Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Real-time AI-powered performance feedback showing:
 * - Actionable practice suggestions
 * - Strengths and areas for improvement
 * - Technical tips based on current performance
 * - Progressive feedback based on session analysis
 */

import { useEffect, useState } from 'react';
import type { AnalysisResult } from '../../hooks/useWebSocketAnalysis';

export interface FeedbackPanelProps {
  /** Current analysis result from real-time WebSocket */
  latestResult: AnalysisResult | null;
  /** Analysis result from database (for AI feedback) */
  analysisResult?: {
    pitch_accuracy?: number;
    rhythm_accuracy?: number;
    dynamics_range?: number;
    overall_score?: number;
    feedback_json?: string;
  } | null;
  /** Color theme */
  theme?: 'light' | 'dark';
}

interface Feedback {
  type: 'strength' | 'improvement' | 'tip';
  message: string;
  priority: number; // 1-3, higher is more important
}

/**
 * Generate real-time feedback based on analysis
 */
function generateRealtimeFeedback(result: AnalysisResult): Feedback[] {
  const feedback: Feedback[] = [];

  // Pitch feedback
  if (result.pitch) {
    if (result.pitch.is_voiced) {
      if (result.pitch.confidence > 0.8) {
        feedback.push({
          type: 'strength',
          message: `Great pitch clarity on ${result.pitch.note_name}!`,
          priority: 2,
        });
      } else if (result.pitch.confidence < 0.5) {
        feedback.push({
          type: 'improvement',
          message: 'Try to play notes more clearly - aim for cleaner attacks',
          priority: 2,
        });
      }
    }
  }

  // Onset/rhythm feedback
  if (result.onsets && result.onsets.count > 0) {
    if (result.onsets.max_strength > 0.7) {
      feedback.push({
        type: 'strength',
        message: 'Strong, clear note attacks - good articulation!',
        priority: 1,
      });
    } else if (result.onsets.max_strength < 0.3) {
      feedback.push({
        type: 'tip',
        message: 'Try to articulate notes more clearly for better onset detection',
        priority: 1,
      });
    }
  }

  // Dynamics feedback
  if (result.dynamics) {
    const velocity = result.dynamics.midi_velocity;
    if (velocity > 100) {
      feedback.push({
        type: 'tip',
        message: 'Very loud playing - consider using more dynamic range',
        priority: 1,
      });
    } else if (velocity < 30) {
      feedback.push({
        type: 'tip',
        message: 'Playing quite softly - try to use more dynamic contrast',
        priority: 1,
      });
    } else if (velocity >= 50 && velocity <= 80) {
      feedback.push({
        type: 'strength',
        message: 'Good dynamic control - playing in the comfortable range',
        priority: 1,
      });
    }
  }

  return feedback;
}

/**
 * Parse AI feedback from JSON string
 */
function parseAIFeedback(feedbackJson: string | undefined): Feedback[] {
  if (!feedbackJson) return [];

  try {
    const parsed = JSON.parse(feedbackJson);
    const feedback: Feedback[] = [];

    if (parsed.strengths && Array.isArray(parsed.strengths)) {
      parsed.strengths.forEach((strength: string) => {
        feedback.push({
          type: 'strength',
          message: strength,
          priority: 3,
        });
      });
    }

    if (parsed.improvements && Array.isArray(parsed.improvements)) {
      parsed.improvements.forEach((improvement: string) => {
        feedback.push({
          type: 'improvement',
          message: improvement,
          priority: 3,
        });
      });
    }

    if (parsed.tips && Array.isArray(parsed.tips)) {
      parsed.tips.forEach((tip: string) => {
        feedback.push({
          type: 'tip',
          message: tip,
          priority: 2,
        });
      });
    }

    return feedback;
  } catch (error) {
    console.error('Failed to parse AI feedback:', error);
    return [];
  }
}

export function FeedbackPanel({
  latestResult,
  analysisResult,
  theme = 'light',
}: FeedbackPanelProps) {
  const [realtimeFeedback, setRealtimeFeedback] = useState<Feedback[]>([]);
  const [aiFeedback, setAiFeedback] = useState<Feedback[]>([]);

  // Generate real-time feedback
  useEffect(() => {
    if (!latestResult) return;

    const feedback = generateRealtimeFeedback(latestResult);
    setRealtimeFeedback(feedback);

    // Auto-clear real-time feedback after 5 seconds
    const timer = setTimeout(() => {
      setRealtimeFeedback([]);
    }, 5000);

    return () => clearTimeout(timer);
  }, [latestResult]);

  // Parse AI feedback from analysis result
  useEffect(() => {
    if (analysisResult?.feedback_json) {
      const feedback = parseAIFeedback(analysisResult.feedback_json);
      setAiFeedback(feedback);
    }
  }, [analysisResult]);

  // Combine and sort feedback by priority
  const allFeedback = [...realtimeFeedback, ...aiFeedback]
    .sort((a, b) => b.priority - a.priority)
    .slice(0, 5); // Show top 5 items

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';

  // Feedback type styles
  const getFeedbackStyles = (type: Feedback['type']) => {
    switch (type) {
      case 'strength':
        return {
          icon: '✓',
          bgColor: isDark ? 'bg-green-900/20' : 'bg-green-50',
          borderColor: isDark ? 'border-green-700' : 'border-green-200',
          iconColor: isDark ? 'text-green-400' : 'text-green-600',
          textColor: isDark ? 'text-green-100' : 'text-green-900',
        };
      case: 'improvement':
        return {
          icon: '!',
          bgColor: isDark ? 'bg-yellow-900/20' : 'bg-yellow-50',
          borderColor: isDark ? 'border-yellow-700' : 'border-yellow-200',
          iconColor: isDark ? 'text-yellow-400' : 'text-yellow-600',
          textColor: isDark ? 'text-yellow-100' : 'text-yellow-900',
        };
      case 'tip':
        return {
          icon: '💡',
          bgColor: isDark ? 'bg-blue-900/20' : 'bg-blue-50',
          borderColor: isDark ? 'border-blue-700' : 'border-blue-200',
          iconColor: isDark ? 'text-blue-400' : 'text-blue-600',
          textColor: isDark ? 'text-blue-100' : 'text-blue-900',
        };
    }
  };

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${textColor}`}>Performance Feedback</h3>
        {analysisResult && (
          <div className="flex items-center gap-2 text-sm">
            <span className={mutedColor}>Overall Score:</span>
            <span className={`font-semibold ${textColor}`}>
              {analysisResult.overall_score
                ? `${(analysisResult.overall_score * 100).toFixed(0)}%`
                : 'N/A'}
            </span>
          </div>
        )}
      </div>

      {/* Feedback Items */}
      <div className="space-y-2">
        {allFeedback.length === 0 ? (
          <div className={`text-center py-6 ${mutedColor}`}>
            <p>Keep playing to receive real-time feedback!</p>
            <p className="text-sm mt-2">
              I'll analyze your pitch, rhythm, and dynamics
            </p>
          </div>
        ) : (
          allFeedback.map((feedback, index) => {
            const styles = getFeedbackStyles(feedback.type);
            return (
              <div
                key={index}
                className={`flex items-start gap-3 p-3 rounded-lg border ${styles.bgColor} ${styles.borderColor}`}
              >
                <div className={`text-lg font-semibold ${styles.iconColor} flex-shrink-0`}>
                  {styles.icon}
                </div>
                <div className="flex-1">
                  <p className={`text-sm ${styles.textColor}`}>{feedback.message}</p>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Score Breakdown (if available) */}
      {analysisResult && (
        <div className="pt-3 border-t" style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
          <div className="grid grid-cols-3 gap-3 text-sm">
            {analysisResult.pitch_accuracy !== undefined && (
              <div className="text-center">
                <div className={mutedColor}>Pitch</div>
                <div className={`font-semibold ${textColor}`}>
                  {(analysisResult.pitch_accuracy * 100).toFixed(0)}%
                </div>
              </div>
            )}
            {analysisResult.rhythm_accuracy !== undefined && (
              <div className="text-center">
                <div className={mutedColor}>Rhythm</div>
                <div className={`font-semibold ${textColor}`}>
                  {(analysisResult.rhythm_accuracy * 100).toFixed(0)}%
                </div>
              </div>
            )}
            {analysisResult.dynamics_range !== undefined && (
              <div className="text-center">
                <div className={mutedColor}>Dynamics</div>
                <div className={`font-semibold ${textColor}`}>
                  {(analysisResult.dynamics_range * 100).toFixed(0)}%
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className={`text-xs ${mutedColor} pt-2 border-t`} style={{ borderColor: isDark ? '#374151' : '#e5e7eb' }}>
        <p>Real-time feedback updates every few seconds based on your playing</p>
      </div>
    </div>
  );
}
