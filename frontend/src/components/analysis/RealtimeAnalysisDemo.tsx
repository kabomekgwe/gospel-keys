/**
 * Real-Time Analysis Demo Component
 * STORY-3.1: WebSocket Real-Time Analysis
 *
 * Demo UI for testing the complete real-time analysis pipeline:
 * Microphone → AudioWorklet → WebSocket → Rust Analysis → Results Display
 */

import { useState } from 'react';
import { useRealtimeAnalysis } from '../../hooks/useRealtimeAnalysis';
import type { AnalysisResult } from '../../hooks/useWebSocketAnalysis';

export function RealtimeAnalysisDemo() {
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResult[]>([]);

  const {
    isRecording,
    isConnected,
    latestResult,
    latency,
    startAnalysis,
    stopAnalysis,
    error,
    chunksProcessed,
  } = useRealtimeAnalysis({
    onAnalysis: (result) => {
      // Keep last 10 results for display
      setAnalysisHistory((prev) => [...prev.slice(-9), result]);
    },
  });

  const handleToggle = async () => {
    if (isRecording) {
      stopAnalysis();
      setAnalysisHistory([]);
    } else {
      await startAnalysis();
    }
  };

  // Format note display with octave
  const formatNote = (result: AnalysisResult | null) => {
    if (!result?.pitch || !result.pitch.is_voiced) {
      return '---';
    }
    return result.pitch.note_name;
  };

  // Format frequency
  const formatFrequency = (result: AnalysisResult | null) => {
    if (!result?.pitch || !result.pitch.is_voiced) {
      return '---';
    }
    return `${result.pitch.frequency.toFixed(2)} Hz`;
  };

  // Format confidence
  const formatConfidence = (result: AnalysisResult | null) => {
    if (!result?.pitch) {
      return '---';
    }
    return `${(result.pitch.confidence * 100).toFixed(1)}%`;
  };

  // Get dynamic level from MIDI velocity
  const getDynamicLevel = (velocity: number): string => {
    if (velocity < 20) return 'pp (pianissimo)';
    if (velocity < 40) return 'p (piano)';
    if (velocity < 60) return 'mp (mezzo-piano)';
    if (velocity < 80) return 'mf (mezzo-forte)';
    if (velocity < 100) return 'f (forte)';
    return 'ff (fortissimo)';
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Real-Time Audio Analysis</h1>
        <p className="text-gray-600">
          Test the WebSocket-based real-time pitch, onset, and dynamics detection
        </p>
      </div>

      {/* Control Panel */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">Controls</h2>
            <p className="text-sm text-gray-600">
              Start recording to analyze audio from your microphone
            </p>
          </div>
          <button
            onClick={handleToggle}
            disabled={!isConnected && !isRecording}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
              isRecording
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : isConnected
                ? 'bg-green-500 hover:bg-green-600 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isRecording ? '🛑 Stop Analysis' : '🎤 Start Analysis'}
          </button>
        </div>

        {/* Status Indicators */}
        <div className="grid grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <div className="text-sm text-gray-600">Connection</div>
            <div className={`font-semibold ${isConnected ? 'text-green-600' : 'text-gray-400'}`}>
              {isConnected ? '✓ Connected' : '○ Disconnected'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Recording</div>
            <div className={`font-semibold ${isRecording ? 'text-red-600' : 'text-gray-400'}`}>
              {isRecording ? '● Recording' : '○ Stopped'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Chunks Processed</div>
            <div className="font-semibold text-blue-600">{chunksProcessed}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Latency</div>
            <div className="font-semibold text-purple-600">
              {latency ? `${latency.toFixed(1)}ms` : '---'}
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-red-800 font-semibold">Error</div>
            <div className="text-red-600 text-sm">{error.message}</div>
          </div>
        )}
      </div>

      {/* Live Analysis Results */}
      {latestResult && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Live Analysis</h2>

          <div className="grid grid-cols-2 gap-6">
            {/* Pitch Detection */}
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-700">Pitch Detection</h3>
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-blue-600 text-center mb-2">
                  {formatNote(latestResult)}
                </div>
                <div className="text-center text-gray-600">
                  {formatFrequency(latestResult)}
                </div>
                <div className="text-center text-sm text-gray-500 mt-2">
                  Confidence: {formatConfidence(latestResult)}
                </div>
              </div>
            </div>

            {/* Dynamics Analysis */}
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-700">Dynamics</h3>
              <div className="bg-green-50 rounded-lg p-4">
                {latestResult.dynamics.length > 0 ? (
                  <>
                    <div className="text-2xl font-bold text-green-600 text-center mb-2">
                      {getDynamicLevel(latestResult.dynamics[latestResult.dynamics.length - 1].midi_velocity)}
                    </div>
                    <div className="text-center text-gray-600">
                      {latestResult.dynamics[latestResult.dynamics.length - 1].db_level.toFixed(1)} dB
                    </div>
                    <div className="text-center text-sm text-gray-500 mt-2">
                      Velocity: {latestResult.dynamics[latestResult.dynamics.length - 1].midi_velocity}/127
                    </div>
                  </>
                ) : (
                  <div className="text-center text-gray-400 py-4">No dynamics detected</div>
                )}
              </div>
            </div>
          </div>

          {/* Onsets */}
          <div className="mt-6">
            <h3 className="font-semibold text-gray-700 mb-2">Recent Onsets</h3>
            <div className="bg-purple-50 rounded-lg p-4">
              {latestResult.onsets.length > 0 ? (
                <div className="space-y-2">
                  {latestResult.onsets.slice(-3).map((onset, idx) => (
                    <div key={idx} className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        {onset.timestamp.toFixed(3)}s
                      </span>
                      <span className="text-purple-600">
                        Strength: {(onset.strength * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-400">No onsets detected</div>
              )}
            </div>
          </div>

          {/* Performance Metrics */}
          {latestResult.metadata && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold text-gray-700 mb-2">Performance Metrics</h3>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Avg Latency:</span>
                  <span className="ml-2 font-semibold">
                    {latestResult.metadata.avg_latency_ms.toFixed(2)}ms
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Current Latency:</span>
                  <span className="ml-2 font-semibold">
                    {latestResult.metadata.current_latency_ms.toFixed(2)}ms
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Chunks:</span>
                  <span className="ml-2 font-semibold">
                    {latestResult.metadata.chunks_processed}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Analysis History */}
      {analysisHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent History (Last 10)</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {analysisHistory.map((result, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
              >
                <div className="flex items-center space-x-4">
                  <span className="font-mono text-gray-500">#{analysisHistory.length - idx}</span>
                  <span className="font-semibold text-blue-600">
                    {formatNote(result)}
                  </span>
                  <span className="text-gray-600">{formatFrequency(result)}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-gray-600">
                    {result.onsets.length} onsets
                  </span>
                  <span className="text-gray-600">
                    {result.dynamics.length} dynamics
                  </span>
                  {result.metadata && (
                    <span className="text-purple-600">
                      {result.metadata.current_latency_ms.toFixed(1)}ms
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-2">How to Use</h2>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
          <li>Click "Start Analysis" and allow microphone access when prompted</li>
          <li>Sing or play notes into your microphone</li>
          <li>Watch the real-time pitch, onset, and dynamics detection</li>
          <li>Check the latency metrics (target: &lt;100ms, actual: ~20ms)</li>
          <li>Click "Stop Analysis" when done</li>
        </ol>
        <div className="mt-4 text-sm text-gray-600">
          <strong>Note:</strong> Make sure the backend server is running on localhost:8000
        </div>
      </div>
    </div>
  );
}
