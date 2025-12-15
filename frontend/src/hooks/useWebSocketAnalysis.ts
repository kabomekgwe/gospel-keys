/**
 * WebSocket hook for real-time audio analysis
 * STORY-3.1: WebSocket Real-Time Analysis
 *
 * Provides real-time audio streaming and analysis results via WebSocket.
 * Integrates with AudioWorklet for low-latency audio capture.
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// Analysis result types
export interface PitchResult {
  frequency: number;
  note_name: string;
  confidence: number;
  is_voiced: boolean;
}

export interface OnsetEvent {
  timestamp: number;
  sample_index: number;
  strength: number;
  confidence: number;
}

export interface DynamicsEvent {
  timestamp: number;
  rms_level: number;
  peak_level: number;
  db_level: number;
  midi_velocity: number;
}

export interface AnalysisResult {
  pitch: PitchResult | null;
  onsets: OnsetEvent[];
  dynamics: DynamicsEvent[];
  timestamp: number;
  buffer_size?: number;
  metadata?: {
    chunks_processed: number;
    avg_latency_ms: number;
    current_latency_ms: number;
  };
}

export interface SessionStats {
  session_id: string;
  uptime_seconds: number;
  chunks_processed: number;
  avg_latency_ms: number;
  buffer_size: number;
  onset_buffer_size?: number;
}

// WebSocket message types
type WSMessageType = 'audio' | 'ping' | 'stats';
type WSResponseType = 'connected' | 'analysis' | 'pong' | 'stats' | 'error';

interface WSMessage {
  type: WSMessageType;
  data?: string; // base64 audio for 'audio' type
}

interface WSResponse {
  type: WSResponseType;
  session_id?: string;
  sample_rate?: number;
  chunk_size?: number;
  message?: string;
  data?: AnalysisResult | SessionStats;
  timestamp?: number;
}

// Hook configuration
export interface UseWebSocketAnalysisConfig {
  wsUrl?: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onAnalysis?: (result: AnalysisResult) => void;
  onError?: (error: Error) => void;
  onConnectionChange?: (connected: boolean) => void;
}

export interface UseWebSocketAnalysisReturn {
  // Connection state
  isConnected: boolean;
  sessionId: string | null;
  error: Error | null;

  // Latest analysis results
  latestResult: AnalysisResult | null;
  sessionStats: SessionStats | null;

  // Actions
  connect: () => void;
  disconnect: () => void;
  sendAudioChunk: (audioData: Float32Array) => void;
  requestStats: () => void;
  ping: () => void;

  // Performance metrics
  latency: number | null;
}

/**
 * React hook for WebSocket-based real-time audio analysis
 *
 * @example
 * ```tsx
 * const {
 *   isConnected,
 *   sendAudioChunk,
 *   latestResult,
 *   connect,
 *   disconnect,
 * } = useWebSocketAnalysis({
 *   onAnalysis: (result) => {
 *     console.log('Pitch:', result.pitch?.note_name);
 *     console.log('Onsets:', result.onsets.length);
 *   },
 * });
 *
 * // Connect when component mounts
 * useEffect(() => {
 *   connect();
 *   return () => disconnect();
 * }, []);
 *
 * // Stream audio from AudioWorklet
 * audioWorklet.port.onmessage = (event) => {
 *   if (isConnected) {
 *     sendAudioChunk(event.data.audioData);
 *   }
 * };
 * ```
 */
export function useWebSocketAnalysis(
  config: UseWebSocketAnalysisConfig = {}
): UseWebSocketAnalysisReturn {
  const {
    wsUrl = 'ws://localhost:8000/ws/analyze',
    autoConnect = false,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onAnalysis,
    onError,
    onConnectionChange,
  } = config;

  // State
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [latestResult, setLatestResult] = useState<AnalysisResult | null>(null);
  const [sessionStats, setSessionStats] = useState<SessionStats | null>(null);
  const [latency, setLatency] = useState<number | null>(null);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Send JSON message to WebSocket
   */
  const sendMessage = useCallback((message: WSMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  /**
   * Send audio chunk for analysis
   */
  const sendAudioChunk = useCallback(
    (audioData: Float32Array) => {
      if (!isConnected) return;

      // Convert Float32Array to base64
      const buffer = new ArrayBuffer(audioData.length * 4);
      const view = new Float32Array(buffer);
      view.set(audioData);

      // Create base64 string
      const bytes = new Uint8Array(buffer);
      let binary = '';
      for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const base64 = btoa(binary);

      sendMessage({
        type: 'audio',
        data: base64,
      });
    },
    [isConnected, sendMessage]
  );

  /**
   * Request session statistics
   */
  const requestStats = useCallback(() => {
    sendMessage({ type: 'stats' });
  }, [sendMessage]);

  /**
   * Send ping (keep-alive)
   */
  const ping = useCallback(() => {
    sendMessage({ type: 'ping' });
  }, [sendMessage]);

  /**
   * Handle WebSocket messages
   */
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const response: WSResponse = JSON.parse(event.data);

        switch (response.type) {
          case 'connected':
            setSessionId(response.session_id || null);
            setIsConnected(true);
            reconnectAttemptsRef.current = 0;
            onConnectionChange?.(true);
            console.log(
              `WebSocket connected: Session ${response.session_id}, ` +
              `Sample rate: ${response.sample_rate}Hz`
            );
            break;

          case 'analysis':
            const result = response.data as AnalysisResult;
            setLatestResult(result);
            if (result.metadata) {
              setLatency(result.metadata.current_latency_ms);
            }
            onAnalysis?.(result);
            break;

          case 'pong':
            // Keep-alive acknowledged
            break;

          case 'stats':
            const stats = response.data as SessionStats;
            setSessionStats(stats);
            break;

          case 'error':
            const err = new Error(response.message || 'WebSocket error');
            setError(err);
            onError?.(err);
            console.error('WebSocket error:', response.message);
            break;

          default:
            console.warn('Unknown message type:', response);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    },
    [onAnalysis, onError, onConnectionChange]
  );

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(() => {
    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connection opened');
      };

      ws.onmessage = handleMessage;

      ws.onerror = (event) => {
        const err = new Error('WebSocket connection error');
        setError(err);
        onError?.(err);
        console.error('WebSocket error:', event);
      };

      ws.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        setIsConnected(false);
        setSessionId(null);
        onConnectionChange?.(false);

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(
            `Reconnecting... (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else {
          const err = new Error('Max reconnection attempts reached');
          setError(err);
          onError?.(err);
        }
      };

      wsRef.current = ws;

      // Start ping interval (every 30 seconds)
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
      pingIntervalRef.current = setInterval(() => {
        ping();
      }, 30000);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to connect');
      setError(error);
      onError?.(error);
    }
  }, [wsUrl, handleMessage, onError, onConnectionChange, reconnectInterval, maxReconnectAttempts, ping]);

  /**
   * Disconnect from WebSocket server
   */
  const disconnect = useCallback(() => {
    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Clear ping interval
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setSessionId(null);
    reconnectAttemptsRef.current = maxReconnectAttempts; // Prevent auto-reconnect
  }, [maxReconnectAttempts]);

  // Auto-connect on mount if configured
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [autoConnect]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    // Connection state
    isConnected,
    sessionId,
    error,

    // Analysis results
    latestResult,
    sessionStats,

    // Actions
    connect,
    disconnect,
    sendAudioChunk,
    requestStats,
    ping,

    // Performance
    latency,
  };
}
