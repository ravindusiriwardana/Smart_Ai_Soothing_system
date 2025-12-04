SAMPLE_RATE = 16000
N_MFCC = 40
MAX_LEN = 216
SEGMENT_DURATION = 10
SEGMENT_SIZE = SAMPLE_RATE * SEGMENT_DURATION

CATEGORIES = ['belly pain', 'burping', 'discomfort', 'hungry', 'laugh',
              'lonely', 'noise', 'scared', 'silence', 'tired']

EMOTION_TO_CATEGORY = {
    "belly pain": "loud_high_pitched",
    "burping": "rhythmic_rising_pitch",
    "discomfort": "medium_pitch_whiny",
    "hungry": "rhythmic_rising_pitch",
    "laugh": "playful_upbeat",
    "lonely": "warm_soft_comforting",
    "noise": "neutral_noise_blocker",
    "scared": "trembling_pitch",
    "silence": "baseline_state",
    "tired": "low_energy_whining"
}

MUSIC_BASE_DIR = "/Users/ravindudinuththara/Desktop/Smart_Ai_Soothing_system/data/lullabies/categorized_music"