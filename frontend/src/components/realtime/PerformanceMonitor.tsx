/**
 * PerformanceMonitor Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Parent component that combines all real-time performance visualizations:
 * - PitchVisualization - Real-time pitch accuracy
 * - RhythmGrid - Onset timing visualization
 * - DynamicsMeter - Velocity tracking
 * - FeedbackPanel - AI-powered suggestions
 *
 * Integrates with:
 * - STORY-3.1: WebSocket real-time analysis (useRealtimeAnalysis hook)
 * - STORY-3.2: Database API for saving sessions and retrieving feedback
 */

import { useState, useEffect } from 'react';
import { useRealtimeAnalysis } from '../../hooks/useRealtimeAnalysis';
import { realtimeAnalysisApi, type AnalysisResult as DBAnalysisResult } from '../../lib/api';
import { PitchVisualization } from './PitchVisualization';
import { RhythmGrid } from './RhythmGrid';
import { DynamicsMeter } from './DynamicsMeter';
import { FeedbackPanel } from './FeedbackPanel';

export interface PerformanceMonitorProps {
  /** User ID for session tracking */
  userId: number;
  /** Piece being practiced (optional) */
  pieceName?: string;
  /** Music genre */
  genre?: string;
  /** Target tempo in BPM */
  targetTempo?: number;
  /** Difficulty level */
  difficultyLevel?: 'beginner' | 'intermediate' | 'advanced';
  /** Color theme */
  theme?: 'light' | 'dark';
  /** Callback when session is created */
  onSessionCreated?: (sessionId: string) => void;
  /** Callback when session ends */
  onSessionEnded?: (sessionId: string, duration: number) => void;
}

export function PerformanceMonitor({
  userId,
  pieceName,
  genre,
  targetTempo = 120,
  difficultyLevel,
  theme = 'light',
  onSessionCreated,
  onSessionEnded,
}: PerformanceMonitorProps) {
  // Real-time analysis hook (STORY-3.1)
  const {
    isRecording,
    isConnected,
    latestResult,
    latency,
    startAnalysis,
    stopAnalysis,
    error,
    chunksProcessed,
  } = useRealtimeAnalysis();

  // Session state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStartTime, setSessionStartTime] = useState<number | null>(null);
  const [dbAnalysisResult, setDbAnalysisResult] = useState<DBAnalysisResult | null>(null);

  // Start recording and create database session
  const handleStart = async () => {
    try {
      // Create database session (STORY-3.2)
      const session = await realtimeAnalysisApi.createSession({
        user_id: userId,
        piece_name: pieceName,
        genre,
        target_tempo: targetTempo,
        difficulty_level: difficultyLevel,
      });

      setSessionId(session.id);
      setSessionStartTime(Date.now());
      onSessionCreated?.(session.id);

      // Start real-time analysis
      await startAnalysis();
    } catch (err) {
      console.error('Failed to start session:', err);
    }
  };

  // Stop recording and end database session
  const handleStop = async () => {
    if (!sessionId) return;

    try {
      // Stop real-time analysis
      stopAnalysis();

      // End database session (STORY-3.2)
      const endedSession = await realtimeAnalysisApi.endSession(sessionId);

      const duration = sessionStartTime ? (Date.now() - sessionStartTime) / 1000 : 0;
      onSessionEnded?.(sessionId, duration);

      // Clear state
      setSessionId(null);
      setSessionStartTime(null);
    } catch (err) {
      console.error('Failed to end session:', err);
    }
  };

  // Update chunks processed in database periodically
  useEffect(() => {
    if (!sessionId || !isRecording) return;

    const interval = setInterval(async () => {
      try {
        await realtimeAnalysisApi.updateChunksProcessed(sessionId, 10);
      } catch (err) {
        console.error('Failed to update chunks:', err);
      }
    }, 5000); // Every 5 seconds

    return () => clearInterval(interval);
  }, [sessionId, isRecording, chunksProcessed]);

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-900' : 'bg-gray-50';
  const cardBg = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';

  return (
    <div className={`${bgColor} min-h-screen p-6`}>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className={`${cardBg} rounded-lg shadow-md p-6`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className={`text-3xl font-bold ${textColor}`}>
                Performance Monitor
              </h1>
              {pieceName && (
                <p className={`text-lg ${mutedColor} mt-1`}>{pieceName}</p>
              )}
            </div>

            {/* Control Button */}
            <button
              onClick={isRecording ? handleStop : handleStart}
              disabled={!isConnected && !isRecording}
              className={`px-8 py-4 rounded-lg font-semibold text-lg transition-all transform active:scale-95 ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg'
                  : isConnected
                  ? 'bg-green-500 hover:bg-green-600 text-white shadow-lg'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isRecording ? '⏹ Stop Analysis' : '▶ Start Practice'}
            </button>
          </div>

          {/* Status Bar */}
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
                }`}
              />
              <span className={mutedColor}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {isRecording && (
              <>
                <div className="flex items-center gap-2">
                  <span className={mutedColor}>Latency:</span>
                  <span className={`font-semibold ${textColor}`}>
                    {latency ? `${latency.toFixed(0)}ms` : 'N/A'}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className={mutedColor}>Chunks:</span>
                  <span className={`font-semibold ${textColor}`}>{chunksProcessed}</span>
                </div>

                {sessionStartTime && (
                  <div className="flex items-center gap-2">
                    <span className={mutedColor}>Duration:</span>
                    <span className={`font-semibold ${textColor}`}>
                      {Math.floor((Date.now() - sessionStartTime) / 1000)}s
                    </span>
                  </div>
                )}
              </>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">Error: {error.message}</p>
            </div>
          )}
        </div>

        {/* Visualization Grid */}
        {isRecording ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Row */}
            <PitchVisualization latestResult={latestResult} theme={theme} />
            <RhythmGrid
              latestResult={latestResult}
              targetTempo={targetTempo}
              theme={theme}
            />

            {/* Bottom Row */}
            <DynamicsMeter latestResult={latestResult} theme={theme} />
            <FeedbackPanel
              latestResult={latestResult}
              analysisResult={dbAnalysisResult}
              theme={theme}
            />
          </div>
        ) : (
          <div className={`${cardBg} rounded-lg shadow-md p-12 text-center`}>
            <div className="max-w-md mx-auto space-y-4">
              <div className="text-6xl mb-4">🎹</div>
              <h2 className={`text-2xl font-bold ${textColor}`}>
                Ready to Practice?
              </h2>
              <p className={`text-lg ${mutedColor}`}>
                Click "Start Practice" to begin real-time performance analysis
              </p>
              <div className={`text-sm ${mutedColor} mt-6 space-y-2`}>
                <p>📊 Real-time pitch, rhythm, and dynamics tracking</p>
                <p>💡 AI-powered performance feedback</p>
                <p>📈 Automatic session recording and progress tracking</p>
              </div>
            </div>
          </div>
        )}

        {/* Session Info */}
        {sessionId && (
          <div className={`${cardBg} rounded-lg shadow-md p-4`}>
            <div className="flex items-center justify-between text-sm">
              <span className={mutedColor}>Session ID:</span>
              <span className={`font-mono ${textColor}`}>{sessionId}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
