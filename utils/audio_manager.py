import sounddevice as sd

class AudioManager:
    @staticmethod
    def initialize_audio():
        """Initialize and test audio device"""
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            if not default_input:
                raise RuntimeError("No input device found")
            return default_input
        except sd.PortAudioError as e:
            raise RuntimeError(f"Audio device initialization failed: {e}") 