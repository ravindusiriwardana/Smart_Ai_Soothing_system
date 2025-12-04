import time
import sounddevice as sd

from config import CATEGORIES, SAMPLE_RATE, SEGMENT_SIZE
from cry_model.cry_classifier import CryClassifier
from rl_agent.q_learning_agent import QLearningAgent
from audio.audio_utils import AudioBuffer
from tts_soother.parent_soother import SimpleSoother
from music.music_player import MusicPlayer

# ===============================
# Initialize Components
# ===============================
audio_buffer = AudioBuffer(SEGMENT_SIZE)
cry_model = CryClassifier("./cry_model/cry_lstm_model00.h5", CATEGORIES)
agent = QLearningAgent(CATEGORIES, ["voice", "music"])
agent.load("./data/q_table/q_table.pkl")

soother = SimpleSoother(
    model_name="tts_models/en/ljspeech/glow-tts",  # Use a local or TTS API model
    parent_name="Mommy",
    parent_voice_path="./audio/parents_audio/parent_voice_16k.wav"
)

music_player = MusicPlayer()

# ===============================
# Start Audio Stream
# ===============================
stream = sd.InputStream(
    channels=1,
    samplerate=SAMPLE_RATE,
    callback=audio_buffer.callback,
    blocksize=1024
)
stream.start()

# ===============================
# Main Interaction Loop
# ===============================
try:
    while True:
        time.sleep(10)  # Wait for audio segment to fill
        segment = audio_buffer.get_audio_segment()

        if len(segment) < SEGMENT_SIZE:
            continue

        # Predict baby's emotion
        state, conf = cry_model.predict(segment)
        print(f"Baby state: {state} ({conf*100:.2f}%)")

        # RL agent chooses action
        action = agent.choose_action(state)

        # Execute action
        if action == "voice":
            soother.soothe(state)
        else:
            music_player.play_music(state)

        # Update agent
        next_state, reward = state, 1  # simple reward logic
        agent.update(state, action, reward, next_state)
        agent.save("./data/q_table/q_table.pkl")

except KeyboardInterrupt:
    print("Stopping system...")

finally:
    stream.stop()
    stream.close()