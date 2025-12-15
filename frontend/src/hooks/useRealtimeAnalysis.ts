/**
 * High-level hook for real-time audio analysis
 * STORY-3.1: WebSocket Real-Time Analysis
 *
 * Combines AudioWorklet (audio capture) + WebSocket (analysis) for
 * a complete real-time analysis solution.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { useWebSocketAnalysis, type AnalysisResult, type UseWebSocketAnalysisConfig } from './useWebSocketAnalysis';

export interface UseRealtimeAnalysisConfig extends Omit<UseWebSocketAnalysisConfig, 'onAnalysis'> {
  onAnalysis?: (result: AnalysisResult) => void;
  chunkSize?: number;
  enablePassthrough?: boolean; // Hear yourself while recording
}

export interface UseRealtimeAnalysisReturn {
  // Recording state
  isRecording: boolean;
  isConnected: boolean;
  error: Error | null;

  // Analysis results
  latestResult: AnalysisResult | null;
  latency: number | null;

  // Controls
  startAnalysis: () => Promise<void>;
  stopAnalysis: () => void;

  // Performance
  chunksProcessed: number;
}

/**
 * Hook for real-time audio analysis with microphone input
 *
 * Handles:
 * - Microphone permission and setup
 * - AudioWorklet for low-latency capture
 * - WebSocket connection for analysis
 * - Automatic cleanup
 *
 * @example
 * ```tsx
 * function PerformanceMonitor() {
 *   const {
 *     isRecording,
 *     startAnalysis,
 *     stopAnalysis,
 *     latestResult,
 *     error,
 *   } = useRealtimeAnalysis({
 *     onAnalysis: (result) => {
 *       console.log('Pitch:', result.pitch?.note_name);
 *       console.log('Latency:', result.metadata?.current_latency_ms);
 *     },
 *   });
 *
 *   return (
 *     <div>
 *       <button onClick={isRecording ? stopAnalysis : startAnalysis}>
 *         {isRecording ? 'Stop' : 'Start'} Analysis
 *       </button>
 *       {error && <div>Error: {error.message}</div>}
 *       {latestResult && (
 *         <div>
 *           <div>Note: {latestResult.pitch?.note_name}</div>
 *           <div>Frequency: {latestResult.pitch?.frequency.toFixed(2)} Hz</div>
 *         </div>
 *       )}
 *     </div>
 *   );
 * }
 * ```
 */
export function useRealtimeAnalysis(
  config: UseRealtimeAnalysisConfig = {}
): UseRealtimeAnalysisReturn {
  const {
    chunkSize = 512,
    enablePassthrough = false,
    onAnalysis,
    ...wsConfig
  } = config;

  // State
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [chunksProcessed, setChunksProcessed] = useState(0);

  // Refs for audio objects
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const destinationRef = useRef<MediaStreamAudioDestinationNode | null>(null);

  // WebSocket hook
  const {
    isConnected,
    latestResult,
    latency,
    connect,
    disconnect,
    sendAudioChunk,
  } = useWebSocketAnalysis({
    ...wsConfig,
    onAnalysis: (result) => {
      onAnalysis?.(result);
    },
    onError: (err) => {
      setError(err);
      wsConfig.onError?.(err);
    },
  });

  /**
   * Initialize audio context and worklet
   */
  const initAudioContext = useCallback(async () => {
    try {
      // Create or resume audio context
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext({
          sampleRate: 44100,
          latencyHint: 'interactive', // Low latency
        });
      }

      const audioContext = audioContextRef.current;

      // Resume if suspended
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      // Register AudioWorklet module
      await audioContext.audioWorklet.addModule('/audio-processor.js');

      console.log('Audio context initialized:', audioContext.sampleRate, 'Hz');
      return audioContext;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to initialize audio context');
      setError(error);
      throw error;
    }
  }, []);

  /**
   * Request microphone access and set up audio pipeline
   */
  const setupAudioPipeline = useCallback(
    async (audioContext: AudioContext) => {
      try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: false, // We want raw audio
            noiseSuppression: false,
            autoGainControl: false,
            sampleRate: 44100,
          },
        });

        mediaStreamRef.current = stream;

        // Create source from microphone
        const source = audioContext.createMediaStreamSource(stream);
        sourceNodeRef.current = source;

        // Create AudioWorklet node
        const workletNode = new AudioWorkletNode(audioContext, 'audio-processor');
        workletNodeRef.current = workletNode;

        // Set chunk size
        workletNode.port.postMessage({
          command: 'setChunkSize',
          chunkSize: chunkSize,
        });

        // Listen for audio chunks from worklet
        workletNode.port.onmessage = (event) => {
          if (event.data.type === 'audio') {
            // Send to WebSocket for analysis
            sendAudioChunk(event.data.audioData);
            setChunksProcessed(event.data.chunkNumber);
          } else if (event.data.type === 'stats') {
            console.log('AudioWorklet stats:', event.data.data);
          }
        };

        // Connect audio graph
        source.connect(workletNode);

        if (enablePassthrough) {
          // Connect to speakers (hear yourself)
          workletNode.connect(audioContext.destination);
        } else {
          // Silent destination (no monitoring)
          const destination = audioContext.createMediaStreamDestination();
          destinationRef.current = destination;
          workletNode.connect(destination);
        }

        console.log('Audio pipeline established');
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to setup audio pipeline');
        setError(error);
        throw error;
      }
    },
    [chunkSize, enablePassthrough, sendAudioChunk]
  );

  /**
   * Start real-time analysis
   */
  const startAnalysis = useCallback(async () => {
    try {
      setError(null);
      setChunksProcessed(0);

      // Initialize audio context and worklet
      const audioContext = await initAudioContext();

      // Connect to WebSocket
      connect();

      // Wait a bit for WebSocket to connect
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Set up audio pipeline
      await setupAudioPipeline(audioContext);

      setIsRecording(true);
      console.log('Real-time analysis started');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to start analysis');
      setError(error);
      console.error('Error starting analysis:', error);
    }
  }, [initAudioContext, connect, setupAudioPipeline]);

  /**
   * Stop real-time analysis
   */
  const stopAnalysis = useCallback(() => {
    // Stop media stream tracks
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    // Disconnect audio nodes
    if (sourceNodeRef.current) {
      sourceNodeRef.current.disconnect();
      sourceNodeRef.current = null;
    }

    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    if (destinationRef.current) {
      destinationRef.current = null;
    }

    // Disconnect WebSocket
    disconnect();

    setIsRecording(false);
    setChunksProcessed(0);
    console.log('Real-time analysis stopped');
  }, [disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAnalysis();

      // Close audio context
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    // State
    isRecording,
    isConnected,
    error,

    // Results
    latestResult,
    latency,

    // Controls
    startAnalysis,
    stopAnalysis,

    // Performance
    chunksProcessed,
  };
}
