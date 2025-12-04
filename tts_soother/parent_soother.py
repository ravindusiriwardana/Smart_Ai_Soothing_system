import os
import time
import re
import unicodedata
import soundfile as sf
import pygame
from TTS.api import TTS


class SimpleSoother:
    def __init__(self, model_name="tts_models/en/ljspeech/glow-tts",
                 parent_name="Parent", parent_voice_path=None):

        self.parent_name = parent_name
        self.parent_voice_path = parent_voice_path
        self.model_name = model_name.lower()

        print("🔄 Loading TTS model...")

        try:
            self.synthesizer = TTS(model_name=model_name, gpu=False)
            print("✅ TTS model loaded successfully!")
        except Exception as e:
            print("❌ ERROR: Failed to load TTS model!")
            print("Reason:", e)
            self.synthesizer = None

    # ----------------------------------------------------------------------
    # REMOVE ALL UNSUPPORTED CHARACTERS
    # ----------------------------------------------------------------------
    def clean_text(self, text):
        # Remove emojis and symbols
        text = text.encode("ascii", "ignore").decode()

        # Normalize unicode
        text = unicodedata.normalize("NFKD", text)

        # Remove combining characters
        text = "".join(c for c in text if not unicodedata.combining(c))

        # Remove anything not letters, numbers, punctuation, or space
        text = re.sub(r"[^a-zA-Z0-9.,!?'\- ]+", " ", text)

        # Replace multiple spaces with one
        text = re.sub(r"\s+", " ", text).strip()

        return text

    # ----------------------------------------------------------------------

    def preprocess_parent_voice(self, path):
        if "xtts" not in self.model_name:
            return None
        try:
            print(f"🎤 Loading parent reference voice: {path}")
            audio, sr = sf.read(path)
            print("✅ Parent voice loaded.")
            return audio
        except Exception as e:
            print("⚠️ Could not load parent voice:", e)
            return None

    # ----------------------------------------------------------------------

    def get_soothing_phrase(self, emotion):
        phrases = {
            "hungry": "It’s okay sweetheart, mommy will give you milk now.",
            "discomfort": "I know baby… let mommy help you feel better.",
            "belly pain": "Shhh… mommy is here, it will be okay.",
            "burping": "It’s okay darling, let mommy help you burp.",
            "laugh": "Oh sweetie, it's okay. Mommy is here. Let's snuggle close.",
            "scared": "Shhh baby, mommy is right here. No need to be afraid.",
            "default": "Mommy is here with you. Everything is okay."
        }
        return phrases.get(emotion, phrases["default"])

    # ----------------------------------------------------------------------

    def speak(self, text, output_file="parent_voice.wav"):
        if not self.synthesizer:
            print("❌ ERROR: No TTS synthesizer loaded.")
            return

        cleaned = self.clean_text(text)
        print(f"🧹 Cleaned text for TTS: '{cleaned}'")

        tts_args = {"text": cleaned}

        if "xtts" in self.model_name:
            tts_args["language_name"] = "en"
            if self.parent_voice_path:
                audio = self.preprocess_parent_voice(self.parent_voice_path)
                if audio is not None:
                    tts_args["speaker_wav"] = audio

        try:
            audio = self.synthesizer.tts(**tts_args)
        except Exception as e:
            print("❌ ERROR during TTS synthesis:", e)
            return

        try:
            sf.write(output_file, audio, 22050)
            print(f"📁 Saved audio to: {output_file}")
        except Exception as e:
            print("❌ Unable to save WAV file:", e)
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

        except Exception as e:
            print("⚠️ Playback error:", e)

    # ----------------------------------------------------------------------

    def soothe(self, emotion):
        phrase = self.get_soothing_phrase(emotion)
        print(f"👶 Emotion: {emotion} → Saying: '{phrase}'")
        self.speak(phrase)