import asyncio
import websockets

async def connect_and_send():
    """
    Connects to the WebSocket server, sends messages, and receives echoes.
    """
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, WebSocket Server!")
        print("Sent: Hello, WebSocket Server!")
        response = await websocket.recv()
        print(f"Received: {response}")

        await websocket.send("How are you?")
        print("Sent: How are you?")
        response = await websocket.recv()
        print(f"Received: {response}")

if __name__ == "__main__":
    asyncio.run(connect_and_send())