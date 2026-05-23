import os
import time
import re
import unicodedata
import soundfile as sf
import pygame
import numpy as np
import librosa

from TTS.api import TTS 

# LLM Imports (Ensure you have langchain-ollama installed)
try:
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    print("❌ ERROR: 'langchain_ollama' not found. Please run: pip install langchain-ollama langchain")
    ChatOllama = None

class SimpleSoother:
    def __init__(self, 
                 model_name="gemma:2b", 
                 tts_model_name="tts_models/multilingual/multi-dataset/your_tts",
                 parent_name="Parent", 
                 parent_voice_path=None):
        
        self.parent_name = parent_name
        self.parent_voice_path = parent_voice_path
        self.model_name = model_name
        self.tts_model_name = tts_model_name

        # --- Initialize LLM ---
        print("🔄 Loading LLM...")
        if ChatOllama:
            try:
                # Ensure Ollama is running (ollama serve)
                self.llm = ChatOllama(model=model_name, temperature=0.7)
                self.prompt_template = ChatPromptTemplate.from_messages([
                    ("system", f"You are a loving parent named {self.parent_name}. "
                               "Your infant is crying. Generate a very short, comforting, soothing sentence (max 10 words)."),
                ])
                print(f"✅ LLM model loaded: {model_name}")
            except Exception as e:
                print(f"❌ Failed to load LLM model '{model_name}': {e}")
                self.llm = None
        else:
            self.llm = None

        # --- Initialize TTS ---
        print("🔄 Loading TTS model...")
        try:
            # The TTS class handles downloading and synthesizer creation automatically
            self.synthesizer = TTS(model_name=tts_model_name, gpu=False)
            print(f"✅ TTS model loaded: {tts_model_name}")
        except Exception as e:
            print(f"❌ Failed to load TTS model '{tts_model_name}': {e}")
            self.synthesizer = None

    def clean_text(self, text):
        text = text.encode("ascii", "ignore").decode()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        text = re.sub(r"[^a-zA-Z0-9.,!?'\- ]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # --- Preprocess parent voice ---
    @staticmethod
    def preprocess_parent_voice(input_path, output_path="parent_voice_clean_16k.wav", sr=16000):
        try:
            print(f"🎤 Processing parent voice: {input_path}")
            y, sr = librosa.load(input_path, sr=sr)
            y_trimmed, _ = librosa.effects.trim(y, top_db=20)
            
            # Simple spectral gating
            stft = librosa.stft(y_trimmed)
            magnitude, phase = librosa.magphase(stft)
            noise_est = np.median(magnitude, axis=1, keepdims=True)
            mask = magnitude >= noise_est
            stft_clean = stft * mask
            y_denoised = librosa.istft(stft_clean)
            
            y_normalized = librosa.util.normalize(y_denoised)
            sf.write(output_path, y_normalized, sr)
            print("✅ Parent voice processed and saved.")
            return output_path
        except Exception as e:
            print(f"⚠️ Error processing voice: {e}")
            return None

    # --- Generate soothing phrase ---
    def get_soothing_phrase(self, emotion):
        if not self.llm:
            print("⚠️ No LLM loaded. Using fallback.")
            return "Shhh, mommy is here. Everything is okay."
            
        print(f"🧠 Generating phrase for emotion: {emotion}...")
        try:
            chain = self.prompt_template | self.llm
            response = chain.invoke({"human": f"The baby is feeling: {emotion}"})
            return response.content
        except Exception as e:
            print(f"⚠️ LLM Error: {e}")
            return "Shhh, it's okay."

    def speak(self, text, output_file="parent_voice.wav"):
        if not self.synthesizer:
            print("❌ ERROR: No TTS synthesizer loaded.")
            return

        cleaned = self.clean_text(text)
        print(f"🧹 Cleaned text for TTS: '{cleaned}'")

        tts_args = {"text": cleaned, "file_path": output_file}

        # Check if the model supports voice cloning (speaker_wav)
        if self.synthesizer.is_multi_speaker:
            if self.parent_voice_path:
                processed_wav = self.preprocess_parent_voice(self.parent_voice_path)
                if processed_wav:
                    tts_args["speaker_wav"] = processed_wav
            else:
                print("⚠️ Model is multi-speaker but no parent_voice_path provided.")

        try:
            # .tts_to_file() handles the synthesis and saving in one go
            self.synthesizer.tts_to_file(**tts_args)
            print(f"📁 Saved audio to: {output_file}")
            
        except Exception as e:
            print("❌ ERROR during TTS synthesis:", e)
            return

        # Play audio
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()

            print("🔊 Playing audio...")
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            print("✅ Playback complete!")
            pygame.mixer.quit()

        except Exception as e:
            print("⚠️ Playback error:", e)

    def soothe(self, emotion):
        phrase = self.get_soothing_phrase(emotion)
        print(f"👶 Emotion: {emotion} → Saying: '{phrase}'")
        self.speak(phrase)

if __name__ == "__main__":
    soother = SimpleSoother(
        model_name="gemma:2b", 
        parent_voice_path="mom_recording.wav" 
    )

    soother.soothe("hungry")