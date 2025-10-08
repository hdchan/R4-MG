import asyncio
import websockets

async def echo(websocket):
    """
    Handles incoming WebSocket connections and echoes back received messages.
    """
    print(f"Client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received message from {websocket.remote_address}: {message}")
            await websocket.send(f"Echo: {message}")  # Echo the message back
    except websockets.ConnectionClosed:
        print(f"Client from {websocket.remote_address} disconnected")

async def main():
    """
    Starts the WebSocket server.
    """
    print("Starting WebSocket server on ws://localhost:8765")
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())