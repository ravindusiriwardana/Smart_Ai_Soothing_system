import asyncio
import websockets
import json
import time
import random
from threading import Thread
import sounddevice as sd

from config import CATEGORIES, SAMPLE_RATE, SEGMENT_SIZE
from cry_model.cry_classifier import CryClassifier
from rl_agent.q_learning_agent import QLearningAgent
from audio.audio_utils import AudioBuffer
from tts_soother.parent_soother import SimpleSoother
from music.music_player import MusicPlayer
from websocket_server.server import WebSocketServer


# ============================================================
# 🟦 DUMMY POSTURE DETECTION FUNCTION (NEW)
# ============================================================
def detect_posture():
    """
    Dummy posture evaluator.
    Randomly returns 'safe' or 'risky'.
    """
    return random.choice(["safe", "risky"])


# ============================================================
# 🟦 WEBSOCKET SERVER
# ============================================================
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

    async def broadcast_emotion(self, data):
        if not self.clients:
            return

        msg = json.dumps(data)
        dead_clients = []

        for client in self.clients:
            try:
                await client.send(msg)
            except:
                dead_clients.append(client)

        for dc in dead_clients:
            if dc in self.clients:
                self.clients.remove(dc)

    def broadcast_threadsafe(self, data):
        if self.loop is None:
            print("⚠️ WebSocket server not ready yet!")
            return

        asyncio.run_coroutine_threadsafe(
            self.broadcast_emotion(data),
            self.loop
        )


# ============================================================
# 🟦 START WEBSOCKET SERVER IN THREAD
# ============================================================
ws_server = WebSocketServer()

def run_ws_server():
    ws_server.start_server(host="0.0.0.0", port=8765)

ws_thread = Thread(target=run_ws_server, daemon=True)
ws_thread.start()


# ============================================================
# 🟦 INITIALIZE COMPONENTS
# ============================================================
audio_buffer = AudioBuffer(SEGMENT_SIZE)
cry_model = CryClassifier("./cry_model/cry_lstm_model00.h5", CATEGORIES)

agent = QLearningAgent(CATEGORIES, ["voice", "music"])
agent.load("./data/q_table/q_table.pkl")

soother = SimpleSoother(
    model_name="tts_models/en/ljspeech/glow-tts",
    parent_name="Mommy",
    parent_voice_path="./audio/parents_audio/parent_voice_16k.wav"
)

music_player = MusicPlayer()

# ============================================================
# 🟦 START AUDIO STREAM
# ============================================================
stream = sd.InputStream(
    channels=1,
    samplerate=SAMPLE_RATE,
    callback=audio_buffer.callback,
    blocksize=1024
)
stream.start()


# ============================================================
# 🟦 MAIN LOOP
# ============================================================
try:
    while True:
        time.sleep(10)
        segment = audio_buffer.get_audio_segment()

        if len(segment) < SEGMENT_SIZE:
            continue

        # --- Emotion prediction ---
        state, conf = cry_model.predict(segment)
        print(f"🍼 Baby state: {state} ({conf*100:.2f}%)")

        # --- Dummy posture detection ---
        posture_status = detect_posture()
        print(f"🧘 Posture: {posture_status}")

        # --- Send emotion + posture to Flutter ---
        ws_server.broadcast_threadsafe({
            "emotion": state,
            "confidence": float(conf),
            "posture": posture_status
        })

        # --- RL Agent Action ---
        action = agent.choose_action(state)

        if action == "voice":
            soother.soothe(state)
        else:
            music_player.play_music(state)

        # --- Update RL agent ---
        next_state, reward = state, 1
        agent.update(state, action, reward, next_state)
        agent.save("./data/q_table/q_table.pkl")

except KeyboardInterrupt:
    print("Stopping system...")

finally:
    stream.stop()
    stream.close()