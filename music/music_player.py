import os
import random
import time
import pygame
from config import EMOTION_TO_CATEGORY, MUSIC_BASE_DIR

pygame.mixer.init()

class MusicPlayer:
    def play_music(self, emotion):
        category = EMOTION_TO_CATEGORY.get(emotion.lower().strip(), "baseline_state")
        folder = os.path.join(MUSIC_BASE_DIR, category)
        if not os.path.exists(folder):
            print(f"⚠️ Music folder not found: {folder}")
            return
        songs = [f for f in os.listdir(folder) if f.lower().endswith(('.mp3','.wav'))]
        if not songs:
            print(f"⚠️ No songs found in {folder}")
            return
        song_file = random.choice(songs)
        song_path = os.path.join(folder, song_file)
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)