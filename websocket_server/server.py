import asyncio
import websockets
import json


class WebSocketServer:
    def __init__(self):
        self.clients = set()
        self.loop = None  # event loop for this server thread

    async def handler(self, websocket):
        self.clients.add(websocket)
        print("📡 Client connected!")

        try:
            async for msg in websocket:
                print("Client says:", msg)

        except websockets.exceptions.ConnectionClosed:
            pass

        finally:
            if websocket in self.clients:
                self.clients.remove(websocket)
                print("❌ Client disconnected")

    def start_server(self, host="0.0.0.0", port=8765):

        async def run():
            async with websockets.serve(self.handler, host, port):
                print(f"✅ WebSocket running at ws://{host}:{port}")
                await asyncio.Future()  # keep running forever

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(run())
        self.loop.run_forever()

    async def broadcast_emotion(self, emotion_data):
        if not self.clients:
            return

        msg = json.dumps(emotion_data)
        dead_clients = []

        for client in self.clients:
            try:
                await client.send(msg)
            except:
                dead_clients.append(client)

        for dc in dead_clients:
            if dc in self.clients:
                self.clients.remove(dc)

    def broadcast_threadsafe(self, emotion_data):
        if self.loop is None:
            print("⚠️ WebSocket server not ready yet!")
            return

        asyncio.run_coroutine_threadsafe(
            self.broadcast_emotion(emotion_data),
            self.loop
        )