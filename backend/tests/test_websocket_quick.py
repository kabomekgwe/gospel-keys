#!/usr/bin/env python3
"""
Quick smoke test for WebSocket server
Tests basic connection and ping/pong
"""

import asyncio
import websockets
import json
import sys


async def test_connection_and_ping():
    """Test WebSocket connection and ping/pong"""
    uri = "ws://localhost:8000/ws/analyze"

    try:
        print("Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            # Wait for connection confirmation
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            print(f"✅ Connected: {data['type']}")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Sample Rate: {data['sample_rate']}")

            # Send ping
            print("\nSending ping...")
            await websocket.send(json.dumps({"type": "ping"}))

            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            print(f"✅ Received pong: {data['type']}")

            # Request stats
            print("\nRequesting stats...")
            await websocket.send(json.dumps({"type": "stats"}))

            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            print(f"✅ Received stats:")
            print(f"   Chunks processed: {data['data']['chunks_processed']}")
            print(f"   Buffer size: {data['data']['buffer_size']}")

            print("\n🎉 All tests PASSED!")
            return 0

    except asyncio.TimeoutError:
        print("❌ FAILED: Timeout waiting for response")
        return 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_connection_and_ping())
    sys.exit(exit_code)
