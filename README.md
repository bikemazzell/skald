```
╔═╗╦╔═╔═╗╦  ╔╦╗
╚═╗╠╩╗╠═╣║   ║║
╚═╝╩ ╩╩ ╩╩═╝═╩╝
```
# Skald - Voice to Text Transcriber
> Created by [@shoewind1997](https://github.com/bikemazzell)

Skald is a simple, no-UI speech-to-text application that listens to your microphone input and automatically transcribes it to text, copying the result directly to your clipboard. Named after the ancient Nordic poets and storytellers, Skald makes capturing your spoken words as text effortless.
The idea is to bind the script execution to a hotkey, so you can start and stop the transcription with a single keystroke.

## Privacy & Offline Usage

Skald is designed with privacy in mind:
- 🔒 Completely offline after initial model download
- 🚫 No data sent to external servers
- 💻 All processing happens locally on your machine
- 🗑️ Audio data is processed in memory and not saved to disk
- 🤖 Uses local AI models for transcription

This makes Skald ideal for transcribing sensitive or confidential information, as your voice data never leaves your computer.

## Quick Start
```bash
git clone https://github.com/bikemazzell/skald.git
cd skald
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp config.json.example config.json
python main.py
```

## Features

- 🎤 Real-time microphone input capture
- 🤖 Advanced speech recognition using Faster Whisper
- 📋 Automatic clipboard copying of transcribed text
- ⏱️ Configurable timeout settings
- 🛑 Interrupt recording with Ctrl+C
- 💪 Optional audio cue when recording starts
- 💪 Multiple whisper models supported (tiny to large-v3)
- 🎯 Optimized for both CPU and GPU processing

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 4GB RAM
- 2GB free disk space
- Microphone

### Optional Requirements
- CUDA-compatible GPU (for faster processing)
- 8GB+ RAM (for larger models)

## Dependencies Installation

### 1. FFmpeg Installation
#### Windows
```bash
winget install FFmpeg
```

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install ffmpeg
```

### 2. Python Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration
Copy the example config and edit as needed:
```bash
cp config.json.example config.json
```

Example configuration:
```json
{
    "audio": {
        "sample_rate": 16000,
        "silence_threshold": 0.03,
        "silence_duration": 2,
        "chunk_duration": 30,
        "channels": 1,
        "max_duration": 300,
        "buffer_size_multiplier": 2,
        "start_tone": {
            "enabled": true,
            "frequency": 440,
            "duration": 100
        }
    },
    "whisper": {
        "model": "base",
        "device": "cpu",
        "compute_type": "int8"
    },
    "debug": {
        "print_status": true,
        "print_transcriptions": true
    }
}
```

## Model Selection

| Model | Parameters | Use Case | Speed | Accuracy |
|-------|------------|----------|--------|-----------|
| tiny | 39M | Quick tests, low resource environments | ⚡⚡⚡⚡⚡ | ⭐ |
| base | 74M | Basic transcription | ⚡⚡⚡⚡ | ⭐⭐ |
| small | 244M | Balanced performance | ⚡⚡⚡ | ⭐⭐⭐ |
| medium | 769M | Better accuracy | ⚡⚡ | ⭐⭐⭐⭐ |
| large | 1550M | Best accuracy | ⚡ | ⭐⭐⭐⭐⭐ |

## Usage

1. Start the application:
```bash
python main.py
```

2. When you hear the start tone (if enabled), begin speaking into your microphone. Skald will listen until:
   - You press Ctrl+C
   - A configurable silence timeout is reached (default: 2 seconds)

3. The transcribed text will automatically be copied to your clipboard

Note: The start tone can be enabled/disabled and customized in the config.json file. When enabled, it provides an audio cue that the application is ready to record.

## Troubleshooting

### Common Issues:

1. **No microphone input detected:**
   - Check your microphone settings in your OS
   - Ensure PyAudio is properly installed
   - Verify microphone permissions

2. **FFmpeg not found:**
   - Verify FFmpeg installation: `ffmpeg -version`
   - Add FFmpeg to your system PATH
   - Reinstall FFmpeg using the instructions above

3. **CUDA errors:**
   - Verify CUDA installation: `nvidia-smi`
   - Update GPU drivers
   - Switch to "cpu" in config.json if GPU support isn't needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you find this project helpful, please consider giving it a star ⭐️

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
