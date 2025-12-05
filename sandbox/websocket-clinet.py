import asyncio
import websockets
import json
async def connect_and_send():
    """
    Connects to the WebSocket server, sends messages, and receives echoes.
    """
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        event = {
            'join': 'stuff'
        }
        await websocket.send(json.dumps(event))
        response = await websocket.recv()
        print(json.loads(response))
        # event = {
        #     'type': 'action'
        # }
        # await websocket.send(json.dumps(event))
        # response = websockets.
        

if __name__ == "__main__":
    asyncio.run(connect_and_send())