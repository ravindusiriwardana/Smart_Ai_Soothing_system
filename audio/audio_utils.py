from collections import deque
import sounddevice as sd
import numpy as np

class AudioBuffer:
    def __init__(self, segment_size):
        self.buffer = deque(maxlen=segment_size)

    def callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.buffer.extend(indata[:,0])

    def get_audio_segment(self):
        return np.array(self.buffer)