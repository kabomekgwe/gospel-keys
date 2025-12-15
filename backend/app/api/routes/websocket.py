"""
WebSocket endpoint for real-time audio analysis
STORY-3.1: WebSocket Real-Time Analysis

Provides bidirectional communication for:
- Audio streaming (frontend → backend)
- Real-time analysis results (backend → frontend)
- Session management and state tracking
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException
from typing import Dict, List, Optional
import asyncio
import numpy as np
import uuid
import time
import base64
import logging

# Real Rust audio analysis functions
from rust_audio_engine import detect_pitch, detect_onsets_python, analyze_dynamics_python

router = APIRouter()
logger = logging.getLogger(__name__)

# Active WebSocket sessions
active_sessions: Dict[str, "WebSocketSession"] = {}


class WebSocketSession:
    """
    Manages a single WebSocket session for real-time audio analysis.

    Handles:
    - Audio buffer management
    - Analysis pipeline orchestration
    - Result streaming back to client
    - Session state tracking
    """

    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.sample_rate = 44100

        # Audio buffers
        self.audio_buffer: List[float] = []
        self.onset_buffer: List[float] = []

        # Buffer configuration
        self.chunk_size = 4096  # ~93ms at 44.1kHz for pitch detection
        self.onset_buffer_size = 8192  # ~185ms for onset detection
        self.overlap_size = 512  # 11ms overlap for continuity

        # Performance tracking
        self.chunks_processed = 0
        self.total_latency_ms = 0.0
        self.created_at = time.time()

        logger.info(f"Session {session_id} created")

    async def process_audio_chunk(self, audio_data: bytes) -> Optional[dict]:
        """
        Process incoming audio chunk and return analysis results.

        Args:
            audio_data: PCM audio bytes (Float32 format)

        Returns:
            Analysis results dict or None if buffer not full yet
        """
        start_time = time.time()

        try:
            # Decode audio bytes to float array
            samples = np.frombuffer(audio_data, dtype=np.float32).tolist()

            # Add to buffer
            self.audio_buffer.extend(samples)

            # Process when buffer is full enough
            if len(self.audio_buffer) >= self.chunk_size:
                # Extract chunk to analyze
                buffer_chunk = self.audio_buffer[:self.chunk_size]

                # Run analysis pipeline
                results = await self.analyze_buffer(buffer_chunk)

                # Trim processed samples, keep overlap for continuity
                self.audio_buffer = self.audio_buffer[self.chunk_size - self.overlap_size:]

                # Update performance metrics
                self.chunks_processed += 1
                latency_ms = (time.time() - start_time) * 1000
                self.total_latency_ms += latency_ms

                # Add performance metadata to results
                results["metadata"] = {
                    "chunks_processed": self.chunks_processed,
                    "avg_latency_ms": self.total_latency_ms / self.chunks_processed,
                    "current_latency_ms": latency_ms
                }

                return results

            return None

        except Exception as e:
            logger.error(f"Error processing audio chunk in session {self.session_id}: {e}")
            raise

    async def analyze_buffer(self, buffer: List[float]) -> dict:
        """
        Run complete analysis pipeline on audio buffer.

        Pipeline:
        1. Pitch detection (YIN algorithm)
        2. Onset detection (spectral flux)
        3. Dynamics analysis (RMS/peak/dB)

        Args:
            buffer: Audio samples to analyze

        Returns:
            Analysis results with pitch, onsets, dynamics
        """
        # Pitch detection (fast, synchronous)
        pitch_result = detect_pitch(buffer, self.sample_rate)

        # Accumulate longer buffer for onset detection
        self.onset_buffer.extend(buffer)
        onsets = []
        dynamics = []

        # Only run onset/dynamics when we have enough samples
        if len(self.onset_buffer) >= self.onset_buffer_size:
            try:
                # Onset detection
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

            except Exception as e:
                logger.error(f"Error in onset/dynamics analysis: {e}")

            # Keep last chunk for continuity
            self.onset_buffer = self.onset_buffer[-self.chunk_size:]

        # Format results
        return {
            "pitch": pitch_result,
            "onsets": onsets[-5:] if len(onsets) > 5 else onsets,  # Last 5 onsets
            "dynamics": dynamics[-5:] if len(dynamics) > 5 else dynamics,  # Last 5
            "timestamp": time.time(),
            "buffer_size": len(self.onset_buffer)
        }

    def get_stats(self) -> dict:
        """Get session statistics."""
        uptime = time.time() - self.created_at
        avg_latency = self.total_latency_ms / self.chunks_processed if self.chunks_processed > 0 else 0

        return {
            "session_id": self.session_id,
            "uptime_seconds": uptime,
            "chunks_processed": self.chunks_processed,
            "avg_latency_ms": avg_latency,
            "buffer_size": len(self.audio_buffer),
            "onset_buffer_size": len(self.onset_buffer)
        }


@router.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio analysis.

    Protocol:
        Client → Server:
            {"type": "audio", "data": "<base64_audio>"}
            {"type": "ping"}
            {"type": "stats"}

        Server → Client:
            {"type": "connected", "session_id": "...", "sample_rate": 44100}
            {"type": "analysis", "data": {...}}
            {"type": "pong"}
            {"type": "stats", "data": {...}}
            {"type": "error", "message": "..."}

    Connection lifecycle:
        1. Client connects
        2. Server accepts and creates session
        3. Server sends connection confirmation
        4. Client streams audio chunks
        5. Server analyzes and responds with results
        6. On disconnect, server cleans up session
    """
    # Accept connection
    await websocket.accept()

    # Generate unique session ID
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
            "chunk_size": 512,
            "message": "WebSocket connection established. Ready to receive audio."
        })

        logger.info(f"Session {session_id} connected. Active sessions: {len(active_sessions)}")

        # Main message loop
        while True:
            # Receive message from client
            message = await websocket.receive_json()

            if message["type"] == "audio":
                # Decode base64 audio data
                try:
                    audio_bytes = base64.b64decode(message["data"])
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Invalid audio data: {str(e)}"
                    })
                    continue

                # Process audio chunk
                results = await session.process_audio_chunk(audio_bytes)

                # Send results if available
                if results:
                    await websocket.send_json({
                        "type": "analysis",
                        "data": results
                    })

            elif message["type"] == "ping":
                # Keep-alive ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": time.time()
                })

            elif message["type"] == "stats":
                # Request session statistics
                stats = session.get_stats()
                await websocket.send_json({
                    "type": "stats",
                    "data": stats
                })

            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message.get('type')}"
                })

    except WebSocketDisconnect:
        # Client disconnected normally
        logger.info(f"Session {session_id} disconnected normally")

    except Exception as e:
        # Unexpected error
        logger.error(f"Error in session {session_id}: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass  # Connection already closed

    finally:
        # Clean up session
        if session_id in active_sessions:
            del active_sessions[session_id]
            logger.info(f"Session {session_id} cleaned up. Active sessions: {len(active_sessions)}")


@router.get("/ws/sessions")
async def get_active_sessions():
    """
    Get list of active WebSocket sessions (for monitoring).

    Returns:
        List of session statistics
    """
    return {
        "active_sessions": len(active_sessions),
        "sessions": [
            session.get_stats()
            for session in active_sessions.values()
        ]
    }
