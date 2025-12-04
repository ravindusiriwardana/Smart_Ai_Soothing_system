import numpy as np
import librosa
from tensorflow.keras.models import load_model
from config import SAMPLE_RATE, N_MFCC, MAX_LEN

class CryClassifier:
    def __init__(self, model_path, categories):
        self.model = load_model(model_path)
        self.categories = categories
        print("✅ Cry model loaded!")

    def extract_features(self, audio):
        mfcc = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=N_MFCC).T
        if mfcc.shape[0] < MAX_LEN:
            pad_width = MAX_LEN - mfcc.shape[0]
            mfcc = np.pad(mfcc, ((0, pad_width), (0,0)), mode='constant')
        else:
            mfcc = mfcc[:MAX_LEN, :]
        return np.expand_dims(mfcc, axis=0)

    def predict(self, audio):
        try:
            features = self.extract_features(audio)
            pred = self.model.predict(features, verbose=0)
            idx = np.argmax(pred)
            return self.categories[idx], pred[0][idx]
        except Exception as e:
            print("Prediction error:", e)
            return None, 0.0