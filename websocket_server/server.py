import asyncio
import websockets
import json

# Connected clients
clients = set()

async def handler(websocket, path):
    # Register client
    clients.add(websocket)
    print(f"New client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            pass  # We don't expect messages from client for now
    except:
        pass
    finally:
        clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

async def broadcast_emotion(emotion_data):
    if clients:
        message = json.dumps(emotion_data)
        await asyncio.wait([client.send(message) for client in clients])

def start_server(host="0.0.0.0", port=8765):
    loop = asyncio.get_event_loop()
    ws_server = websockets.serve(handler, host, port)
    loop.run_until_complete(ws_server)
    print(f"WebSocket server started at ws://{host}:{port}")
    loop.run_forever()