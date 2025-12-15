# STORY-3.1: WebSocket Real-Time Analysis

**Epic**: EPIC-3 (Integration & Infrastructure)
**Status**: 📋 Planned
**Priority**: Must Have
**Effort**: 13 story points
**Dependencies**: Phase 2 (EPIC-2) complete
**Target**: Week 1-3 of Phase 3

---

## User Story

**As a** piano student practicing in real-time
**I want** immediate feedback on my performance as I play
**So that** I can adjust my technique during practice, not after

---

## Acceptance Criteria

- [ ] WebSocket server implemented with FastAPI
- [ ] Audio streaming from frontend to backend (PCM format)
- [ ] Real-time analysis pipeline (pitch + onset + dynamics)
- [ ] Analysis results streamed back to frontend (<100ms latency)
- [ ] Connection recovery on disconnect
- [ ] Session state management
- [ ] Error handling and logging
- [ ] Load testing (10+ concurrent sessions)
- [ ] Python API for WebSocket client
- [ ] Frontend hooks for WebSocket integration

---

## Technical Specification

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Audio Capture (Web Audio API)                       │   │
│  │  - navigator.mediaDevices.getUserMedia()             │   │
│  │  - AudioContext + AudioWorklet                       │   │
│  │  - PCM encoding (Float32Array)                       │   │
│  └───────────────────┬──────────────────────────────────┘   │
└────────────────────┬─┘                                       │
                     │ WebSocket (bidirectional)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WebSocket Endpoint (/ws/analyze)                    │   │
│  │  - Accept audio chunks (512-1024 samples)            │   │
│  │  - Buffer management                                 │   │
│  │  - Session tracking                                  │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Analysis Pipeline (Async Queue)                     │   │
│  │  - detect_pitch(chunk, 44100)                        │   │
│  │  - detect_onsets_python(buffer, 44100, ...)          │   │
│  │  - analyze_dynamics_python(buffer, onsets, ...)      │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Result Broadcaster                                  │   │
│  │  - Format JSON response                              │   │
│  │  - Send via WebSocket                                │   │
│  │  - Track latency metrics                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Backend WebSocket Server (Days 1-3)

#### File: `backend/app/api/routes/websocket.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import numpy as np
from rust_audio_engine import detect_pitch, detect_onsets_python, analyze_dynamics_python

router = APIRouter()

# Session management
active_sessions: Dict[str, WebSocketSession] = {}

class WebSocketSession:
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.audio_buffer = []
        self.buffer_size = 4096  # ~93ms at 44.1kHz
        self.sample_rate = 44100
        self.onset_buffer = []

    async def process_audio_chunk(self, audio_data: bytes) -> dict:
        """
        Process incoming audio chunk and return analysis results.

        Args:
            audio_data: PCM audio bytes (Float32 format)

        Returns:
            Analysis results dict with pitch, onsets, dynamics
        """
        # Decode audio bytes to float array
        samples = np.frombuffer(audio_data, dtype=np.float32).tolist()

        # Add to buffer
        self.audio_buffer.extend(samples)

        # Process when buffer is full enough
        if len(self.audio_buffer) >= self.buffer_size:
            buffer = self.audio_buffer[:self.buffer_size]

            # Run analysis pipeline
            results = await self.analyze_buffer(buffer)

            # Trim processed samples, keep overlap for onset detection
            overlap = 512  # Keep 11ms overlap
            self.audio_buffer = self.audio_buffer[self.buffer_size - overlap:]

            return results

        return None

    async def analyze_buffer(self, buffer: list) -> dict:
        """
        Run complete analysis pipeline on audio buffer.
        """
        # Pitch detection
        pitch_result = detect_pitch(buffer, self.sample_rate)

        # Onset detection (needs longer buffer, accumulate)
        self.onset_buffer.extend(buffer)
        onsets = []
        dynamics = []

        if len(self.onset_buffer) >= 8192:  # ~185ms
            onsets = detect_onsets_python(
                self.onset_buffer,
                self.sample_rate,
                hop_size=256,
                threshold=0.15
            )

            # Dynamics analysis on detected onsets
            if len(onsets) > 0:
                dynamics = analyze_dynamics_python(
                    self.onset_buffer,
                    onsets,
                    self.sample_rate
                )

            # Keep last 4096 samples for continuity
            self.onset_buffer = self.onset_buffer[-4096:]

        return {
            "pitch": pitch_result,
            "onsets": onsets[-5:] if len(onsets) > 5 else onsets,  # Last 5 onsets
            "dynamics": dynamics[-5:] if len(dynamics) > 5 else dynamics,
            "timestamp": asyncio.get_event_loop().time()
        }


@router.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio analysis.

    Protocol:
        Client → Server: {"type": "audio", "data": <base64_audio>}
        Server → Client: {"type": "analysis", "data": {...}}

    Connection lifecycle:
        1. Client connects
        2. Server creates session
        3. Client streams audio chunks
        4. Server analyzes and responds
        5. Client disconnects
        6. Server cleans up session
    """
    await websocket.accept()

    # Generate session ID
    import uuid
    session_id = str(uuid.uuid4())

    # Create session
    session = WebSocketSession(websocket, session_id)
    active_sessions[session_id] = session

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "sample_rate": 44100,
            "chunk_size": 512
        })

        # Main message loop
        while True:
            # Receive message
            message = await websocket.receive_json()

            if message["type"] == "audio":
                # Decode base64 audio data
                import base64
                audio_bytes = base64.b64decode(message["data"])

                # Process audio chunk
                results = await session.process_audio_chunk(audio_bytes)

                # Send results if available
                if results:
                    await websocket.send_json({
                        "type": "analysis",
                        "data": results
                    })

            elif message["type"] == "ping":
                # Keep-alive
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        # Clean up session
        del active_sessions[session_id]
        print(f"Session {session_id} disconnected")

    except Exception as e:
        # Log error and close
        print(f"Error in session {session_id}: {e}")
        del active_sessions[session_id]
        await websocket.close()
```

---

### Phase 2: Frontend WebSocket Client (Days 4-7)

#### File: `frontend/src/hooks/useWebSocketAnalysis.ts`

```typescript
import { useEffect, useRef, useState } from 'react';

interface AnalysisResult {
  pitch: {
    frequency: number;
    confidence: number;
    midi_note: number;
    note_name: string;
  } | null;
  onsets: Array<{
    timestamp: number;
    strength: number;
    confidence: number;
  }>;
  dynamics: Array<{
    timestamp: number;
    rms_level: number;
    db_level: number;
    midi_velocity: number;
  }>;
  timestamp: number;
}

interface UseWebSocketAnalysisOptions {
  sampleRate?: number;
  chunkSize?: number;
  onResult?: (result: AnalysisResult) => void;
  onError?: (error: Error) => void;
}

export function useWebSocketAnalysis(options: UseWebSocketAnalysisOptions = {}) {
  const {
    sampleRate = 44100,
    chunkSize = 512,
    onResult,
    onError,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [latency, setLatency] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  // Connect to WebSocket
  const connect = async () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/analyze');

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === 'connected') {
          sessionIdRef.current = message.session_id;
          console.log('Session ID:', message.session_id);
        } else if (message.type === 'analysis') {
          // Calculate latency
          const now = Date.now();
          const serverTime = message.data.timestamp * 1000;
          setLatency(now - serverTime);

          // Call result callback
          if (onResult) {
            onResult(message.data);
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) {
          onError(new Error('WebSocket connection error'));
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        sessionIdRef.current = null;
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect:', error);
      if (onError) {
        onError(error as Error);
      }
    }
  };

  // Start recording and analysis
  const startRecording = async () => {
    if (!isConnected || !wsRef.current) {
      throw new Error('WebSocket not connected');
    }

    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create AudioContext
      const audioContext = new AudioContext({ sampleRate });
      audioContextRef.current = audioContext;

      // Create source from microphone
      const source = audioContext.createMediaStreamSource(stream);

      // Load and create AudioWorklet for processing
      await audioContext.audioWorklet.addModule('/audio-processor.js');
      const workletNode = new AudioWorkletNode(audioContext, 'audio-processor', {
        processorOptions: { chunkSize },
      });

      workletNodeRef.current = workletNode;

      // Handle audio chunks from worklet
      workletNode.port.onmessage = (event) => {
        const audioData = event.data; // Float32Array

        // Convert to base64 for WebSocket transmission
        const buffer = audioData.buffer;
        const base64 = btoa(
          new Uint8Array(buffer).reduce(
            (data, byte) => data + String.fromCharCode(byte),
            ''
          )
        );

        // Send to backend
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: 'audio',
              data: base64,
            })
          );
        }
      };

      // Connect nodes
      source.connect(workletNode);
      // Note: Don't connect to destination (no playback needed)

      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      if (onError) {
        onError(error as Error);
      }
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    setIsRecording(false);
  };

  // Disconnect WebSocket
  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
      disconnect();
    };
  }, []);

  return {
    isConnected,
    isRecording,
    latency,
    connect,
    disconnect,
    startRecording,
    stopRecording,
  };
}
```

#### File: `frontend/public/audio-processor.js`

```javascript
// AudioWorklet processor for capturing audio chunks

class AudioProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.chunkSize = options.processorOptions?.chunkSize || 512;
    this.buffer = [];
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (!input || !input[0]) {
      return true;
    }

    // Get mono channel (or downmix if stereo)
    const samples = input[0];
    this.buffer.push(...samples);

    // When buffer reaches chunk size, send to main thread
    if (this.buffer.length >= this.chunkSize) {
      const chunk = new Float32Array(this.buffer.splice(0, this.chunkSize));
      this.port.postMessage(chunk);
    }

    return true; // Keep processor alive
  }
}

registerProcessor('audio-processor', AudioProcessor);
```

---

### Phase 3: Testing & Optimization (Days 8-10)

#### Load Testing Script

```python
# backend/test_websocket_load.py

import asyncio
import websockets
import json
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

async def simulate_client(client_id: int, duration_seconds: int = 30):
    """
    Simulate a single client sending audio for analysis.
    """
    uri = "ws://localhost:8000/ws/analyze"

    async with websockets.connect(uri) as websocket:
        # Wait for connection confirmation
        message = await websocket.recv()
        print(f"Client {client_id}: {message}")

        # Generate fake audio chunks
        chunk_size = 512
        sample_rate = 44100
        chunks_to_send = int((duration_seconds * sample_rate) / chunk_size)

        latencies = []
        start_time = time.time()

        for i in range(chunks_to_send):
            # Generate sine wave chunk (440 Hz)
            t = np.linspace(
                i * chunk_size / sample_rate,
                (i + 1) * chunk_size / sample_rate,
                chunk_size
            )
            audio_chunk = np.sin(2 * np.pi * 440 * t).astype(np.float32)

            # Encode and send
            import base64
            audio_bytes = audio_chunk.tobytes()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

            send_time = time.time()
            await websocket.send(json.dumps({
                "type": "audio",
                "data": audio_b64
            }))

            # Wait for response
            response = await websocket.recv()
            receive_time = time.time()

            latency_ms = (receive_time - send_time) * 1000
            latencies.append(latency_ms)

            # Throttle to real-time
            await asyncio.sleep(chunk_size / sample_rate)

        elapsed = time.time() - start_time
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)

        print(f"Client {client_id} completed:")
        print(f"  Duration: {elapsed:.2f}s")
        print(f"  Avg latency: {avg_latency:.2f}ms")
        print(f"  P95 latency: {p95_latency:.2f}ms")

async def load_test(num_clients: int = 10, duration: int = 30):
    """
    Run load test with multiple concurrent clients.
    """
    print(f"Starting load test with {num_clients} clients...")

    tasks = [
        simulate_client(i, duration)
        for i in range(num_clients)
    ]

    await asyncio.gather(*tasks)
    print(f"Load test complete!")

if __name__ == "__main__":
    asyncio.run(load_test(num_clients=10, duration=30))
```

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| WebSocket latency | <100ms | Round-trip time (send → receive) |
| Analysis throughput | >10 concurrent users | Load testing |
| Memory per session | <50MB | Backend monitoring |
| CPU per session | <10% | Single core usage |
| Reconnection time | <2s | After disconnect |

---

## Error Handling

### Connection Errors
- Automatic reconnection (exponential backoff)
- User notification on persistent failure
- Session state recovery

### Audio Errors
- Microphone permission denied → Clear error message
- Audio device not found → Fallback to file upload
- Buffer overflow → Drop oldest samples

### Analysis Errors
- Rust panic → Catch and log, continue session
- Invalid audio data → Skip chunk, continue
- Timeout → Return partial results

---

## Testing Strategy

### Unit Tests
- Session management (create, update, delete)
- Audio buffer handling
- Result formatting

### Integration Tests
- Full WebSocket connection lifecycle
- Audio streaming → analysis → results
- Concurrent sessions

### E2E Tests (Playwright)
- Connect → Record → Analyze → Display results
- Disconnect and reconnect
- Multiple tabs/windows

---

## Definition of Done

- [ ] Backend WebSocket server implemented
- [ ] Frontend WebSocket client hook
- [ ] Audio worklet processor
- [ ] Load testing (10+ clients)
- [ ] All tests passing
- [ ] Latency <100ms P95
- [ ] Code reviewed
- [ ] Documentation complete

---

**Created**: December 15, 2025
**Assigned To**: Full-Stack Team
