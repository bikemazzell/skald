import sounddevice as sd
import numpy as np
import time

class AudioManager:
    _initialized = False
    _default_input = None
    
    @classmethod
    def initialize_audio(cls):
        if cls._initialized:
            return cls._default_input
            
        try:
            devices = sd.query_devices()
            cls._default_input = sd.query_devices(kind='input')
            if not cls._default_input:
                raise RuntimeError("No input device found")
            cls._initialized = True
            return cls._default_input
        except sd.PortAudioError as e:
            raise RuntimeError(f"Audio device initialization failed: {e}")

    @staticmethod
    def play_start_tone(config):
        tone_config = config["audio"]["start_tone"]
        if not tone_config.get("enabled", False):
            return

        try:
            sample_rate = config["audio"]["sample_rate"]
            t = np.linspace(0, tone_config["duration"]/1000, 
                          int(sample_rate * tone_config["duration"]/1000))
            tone = np.sin(2 * np.pi * tone_config["frequency"] * t)
            
            fade_ms = tone_config.get("fade_ms", 5)
            fade_len = int(fade_ms * sample_rate / 1000)
            fade_in = np.linspace(0, 1, fade_len)
            fade_out = np.linspace(1, 0, fade_len)
            tone[:fade_len] *= fade_in
            tone[-fade_len:] *= fade_out

            sd.play(tone, sample_rate, blocking=True)
        except Exception as e:
            print(f"Warning: Could not play start tone: {e}") 