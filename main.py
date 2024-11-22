from transcriber.audio_transcriber import AudioTranscriber
from utils.config_loader import ConfigLoader
from utils.device_manager import DeviceManager
from utils.audio_manager import AudioManager
from validators.config_validator import ConfigValidator

def display_startup_message():
    config = ConfigLoader.load_config("config.json")
    version = config.get("version", "0.1")
    print(f"""
╔═══════════════════════════════════╗
║ 👄   Skald (STT Transcriber)   🎙️ ║
║      Created by @shoewind1997     ║
║ 👂     Version {version:<6}          📝 ║
╚═══════════════════════════════════╝
    """)

def main():
    try:
        display_startup_message()
        transcriber = AudioTranscriber()
        transcriber.start_recording()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 