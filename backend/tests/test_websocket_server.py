#!/usr/bin/env python3
"""
Test script for WebSocket real-time analysis server
STORY-3.1: WebSocket Real-Time Analysis

Tests WebSocket connection, audio streaming, and analysis results.
"""

import asyncio
import websockets
import json
import numpy as np
import base64
import time


async def test_websocket_connection():
    """Test basic WebSocket connection"""
    print("=" * 80)
    print("TEST 1: WebSocket Connection")
    print("=" * 80)

    uri = "ws://localhost:8000/ws/analyze"

    try:
        async with websockets.connect(uri) as websocket:
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)

            print(f"✅ Connected: {data['type']}")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Sample Rate: {data['sample_rate']} Hz")
            print(f"   Message: {data['message']}")

            assert data["type"] == "connected"
            assert data["sample_rate"] == 44100

            print("\n✅ PASSED: WebSocket connection successful")
            return data["session_id"]

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        raise


async def test_audio_streaming():
    """Test audio streaming and analysis"""
    print("\n" + "=" * 80)
    print("TEST 2: Audio Streaming & Analysis")
    print("=" * 80)

    uri = "ws://localhost:8000/ws/analyze"

    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()

        # Generate test audio (440 Hz sine wave - A4)
        sample_rate = 44100
        duration = 2.0  # 2 seconds
        chunk_size = 512  # Samples per chunk

        num_chunks = int((duration * sample_rate) / chunk_size)
        print(f"\n📊 Sending {num_chunks} audio chunks...")

        latencies = []
        analysis_count = 0

        for i in range(num_chunks):
            # Generate sine wave chunk
            t_start = i * chunk_size / sample_rate
            t_end = (i + 1) * chunk_size / sample_rate
            t = np.linspace(t_start, t_end, chunk_size, endpoint=False)
            audio_chunk = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)

            # Encode to base64
            audio_bytes = audio_chunk.tobytes()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

            # Send audio chunk
            send_time = time.time()
            await websocket.send(json.dumps({
                "type": "audio",
                "data": audio_b64
            }))

            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                receive_time = time.time()

                data = json.loads(response)

                if data["type"] == "analysis":
                    analysis_count += 1
                    latency_ms = (receive_time - send_time) * 1000
                    latencies.append(latency_ms)

                    # Print first and last analysis results
                    if analysis_count == 1 or i == num_chunks - 1:
                        print(f"\n📍 Analysis #{analysis_count}:")
                        if data["data"]["pitch"]:
                            pitch = data["data"]["pitch"]
                            print(f"   Pitch: {pitch['frequency']:.2f} Hz (Note: {pitch['note_name']})")
                            print(f"   Confidence: {pitch['confidence']:.3f}")
                        print(f"   Onsets detected: {len(data['data']['onsets'])}")
                        print(f"   Dynamics events: {len(data['data']['dynamics'])}")

                        if "metadata" in data["data"]:
                            meta = data["data"]["metadata"]
                            print(f"   Latency: {meta['current_latency_ms']:.2f}ms")

            except asyncio.TimeoutError:
                pass  # No response yet (buffer not full)

            # Throttle to real-time (optional for testing)
            # await asyncio.sleep(chunk_size / sample_rate)

        print(f"\n📊 Results:")
        print(f"   Chunks sent: {num_chunks}")
        print(f"   Analysis responses: {analysis_count}")

        if latencies:
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            print(f"   Avg latency: {avg_latency:.2f}ms")
            print(f"   P95 latency: {p95_latency:.2f}ms")

            # Check target (<100ms)
            if avg_latency < 100:
                print(f"   ✅ Latency target met ({avg_latency:.2f}ms < 100ms)")
            else:
                print(f"   ⚠️  Latency exceeds target ({avg_latency:.2f}ms >= 100ms)")

        print("\n✅ PASSED: Audio streaming and analysis successful")


async def test_ping_pong():
    """Test keep-alive ping/pong"""
    print("\n" + "=" * 80)
    print("TEST 3: Ping/Pong Keep-Alive")
    print("=" * 80)

    uri = "ws://localhost:8000/ws/analyze"

    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()

        # Send ping
        await websocket.send(json.dumps({"type": "ping"}))

        # Wait for pong
        response = await websocket.recv()
        data = json.loads(response)

        assert data["type"] == "pong"
        print(f"✅ Pong received: {data['type']}")
        print(f"   Timestamp: {data['timestamp']}")

        print("\n✅ PASSED: Ping/pong working")


async def test_session_stats():
    """Test session statistics endpoint"""
    print("\n" + "=" * 80)
    print("TEST 4: Session Statistics")
    print("=" * 80)

    uri = "ws://localhost:8000/ws/analyze"

    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()

        # Send a few audio chunks
        for _ in range(5):
            audio_chunk = np.random.randn(512).astype(np.float32)
            audio_bytes = audio_chunk.tobytes()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

            await websocket.send(json.dumps({
                "type": "audio",
                "data": audio_b64
            }))

            # Wait for response
            try:
                await asyncio.wait_for(websocket.recv(), timeout=0.5)
            except asyncio.TimeoutError:
                pass

        # Request session stats
        await websocket.send(json.dumps({"type": "stats"}))

        # Wait for stats response
        response = await websocket.recv()
        data = json.loads(response)

        assert data["type"] == "stats"
        stats = data["data"]

        print(f"📊 Session Statistics:")
        print(f"   Session ID: {stats['session_id']}")
        print(f"   Uptime: {stats['uptime_seconds']:.2f}s")
        print(f"   Chunks processed: {stats['chunks_processed']}")
        print(f"   Avg latency: {stats['avg_latency_ms']:.2f}ms")
        print(f"   Buffer size: {stats['buffer_size']}")

        print("\n✅ PASSED: Session statistics working")


async def test_concurrent_sessions():
    """Test multiple concurrent WebSocket sessions"""
    print("\n" + "=" * 80)
    print("TEST 5: Concurrent Sessions (3 clients)")
    print("=" * 80)

    async def client_session(client_id: int, duration: float = 1.0):
        """Simulate a single client"""
        uri = "ws://localhost:8000/ws/analyze"

        async with websockets.connect(uri) as websocket:
            # Connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            session_id = data["session_id"]
            print(f"   Client {client_id}: Connected (session {session_id[:8]}...)")

            # Send audio chunks
            sample_rate = 44100
            chunk_size = 512
            num_chunks = int((duration * sample_rate) / chunk_size)

            for _ in range(num_chunks):
                audio_chunk = (np.sin(2 * np.pi * 440 * np.linspace(0, chunk_size / sample_rate, chunk_size)) * 0.5).astype(np.float32)
                audio_bytes = audio_chunk.tobytes()
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

                await websocket.send(json.dumps({
                    "type": "audio",
                    "data": audio_b64
                }))

                try:
                    await asyncio.wait_for(websocket.recv(), timeout=0.1)
                except asyncio.TimeoutError:
                    pass

            print(f"   Client {client_id}: Completed")

    # Run 3 concurrent clients
    await asyncio.gather(
        client_session(1, 1.0),
        client_session(2, 1.0),
        client_session(3, 1.0)
    )

    print("\n✅ PASSED: Concurrent sessions working")


async def main():
    """Run all WebSocket tests"""
    print("🎹 WebSocket Real-Time Analysis Test Suite")
    print("STORY-3.1: WebSocket Real-Time Analysis")
    print("\n⚠️  NOTE: FastAPI server must be running on localhost:8000")
    print()

    try:
        # Run tests
        await test_websocket_connection()
        await test_audio_streaming()
        await test_ping_pong()
        await test_session_stats()
        await test_concurrent_sessions()

        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ WebSocket server implementation successful")
        print("✅ Ready for frontend integration")

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
