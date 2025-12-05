import asyncio
import websockets
from websockets import ServerConnection
from websockets.legacy.protocol import broadcast
import json
from typing import List, Dict, Any

JOIN: List[ServerConnection] = []

HOST: List[ServerConnection] = []

# async def receive_events(websocket: ServerConnection):
#     try:
#         async for message in websocket:
#             try:
#                 if websocket in HOST:
#                     await broadcast_message(JOIN, json.dumps(message))
#                 else:
#                     event = { 'test': 'there' }
#                     response = await HOST[0].send(json.dumps(event))
#                     print(response)
#                     await websocket.send(json.dumps(response))
                    
#             except json.JSONDecodeError:
#                 print(f"Invalid JSON received: {message}")
#             except Exception as e:
#                 print(f"Error processing message: {str(e)}")
#     except websockets.ConnectionClosed:
#         print("Connection closed")

async def remote_join(websocket: ServerConnection):
    print(f'receiving remote {websocket}')
    JOIN.append(websocket)
    try:
        async for message in websocket:
            await HOST[0].send(message)

    finally:
        JOIN.remove(websocket)

async def host_init(websocket: ServerConnection):
    print(f'receiving host {websocket}')
    if HOST:  # Only allow one host
        await websocket.close(1008, "Host already exists")
        return
    
    if len(HOST) > 1:
        HOST[0] = websocket
    else:
        HOST.append(websocket)
    try:
        async for message in websocket:
            print(f"receiving message from host: {message}")
            websockets.broadcast(JOIN, message)
    except Exception as e:
        print(f"Host error: {str(e)}")
    finally:
        HOST.remove(websocket)
        # Only clear JOIN if this was the last host
        if not HOST:
            JOIN.clear()

async def handle(websocket: ServerConnection):
    try:
        message = await websocket.recv()
        event = json.loads(message)

        if "join" in event:
            await remote_join(websocket)
        else:
            await host_init(websocket)
    except Exception as e:
        print(f"Handle error: {str(e)}")
        await websocket.close(1011, str(e))

async def main():
    print("Starting WebSocket server on ws://localhost:8765")
    async with websockets.serve(handle, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())