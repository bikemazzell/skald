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

### GPU Support (Optional)

If you want to use GPU acceleration:

1. Install CUDA and cuDNN:
```bash
# Using conda (recommended)
conda install -c conda-forge cudnn --solver=classic

# Or using pip (alternative)
pip install nvidia-cudnn-cu11
```

2. Update config.json to use GPU:
```json
{
    "whisper": {
        "model": "base",
        "device": "cuda",
        "compute_type": "float16"
    }
}
```

Note: If GPU setup fails, Skald will automatically fall back to CPU processing. You can verify your GPU setup with:
```bash
nvidia-smi  # Should show GPU info
python -c "import torch; print(torch.cuda.is_available())"  # Should print True
```

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

Using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Or using conda:
```bash
conda create -n skald python=3.8
conda activate skald
conda install sounddevice
conda install -c conda-forge faster-whisper
conda install pytorch torchvision torchaudio -c pytorch
conda install numpy scipy pyperclip
```

### 3. Configuration
Copy the example config and edit as needed:
```bash
cp config.json.example config.json
```

Example configuration:
```json
{
    "version": "0.1",
    "audio": {
        "sample_rate": 16000,        // Audio sample rate (16000, 32000, 44100, or 48000)
        "silence_threshold": 0.01,    // Volume level below which is considered silence (0-1)
        "silence_duration": 3,        // Seconds of silence before stopping
        "chunk_duration": 30,         // Duration in seconds for each processing chunk
        "channels": 1,               // Audio channels (1 for mono, 2 for stereo)
        "max_duration": 300,         // Maximum recording duration in seconds
        "buffer_size_multiplier": 2,  // Buffer size multiplier for audio processing
        "start_tone": {
            "enabled": true,          // Play a tone when recording starts
            "frequency": 440,         // Tone frequency in Hz (20-20000)
            "duration": 150           // Tone duration in milliseconds (50-1000)
        }
    },
    "processing": {
        "shutdown_timeout": 30,       // Maximum seconds to wait for processing to complete
        "event_wait_timeout": 0.1     // Timeout for event checking in seconds
    },
    "whisper": {
        "model": "large",            // Whisper model size (tiny, base, small, medium, large)
        "language": "en",            // Target language code
        "task": "transcribe",        // Task type (transcribe or translate)
        "device": "auto"             // Computing device (auto, cpu, cuda, mps)
    },
    "debug": {
        "print_status": true,        // Print audio device status messages
        "print_transcriptions": true  // Print transcriptions as they occur
    }
}
```

## Configuration Options

#### Audio Settings
- `sample_rate`: Higher rates provide better quality but use more resources
- `silence_threshold`: Lower values are more sensitive to silence
- `silence_duration`: Longer duration prevents false stops
- `chunk_duration`: Longer chunks may be more accurate but take longer to process
- `max_duration`: Prevents infinite recordings
- `start_tone`: Provides audible feedback when recording begins

#### Processing Settings
- `shutdown_timeout`: Ensures graceful shutdown with enough time for processing
- `event_wait_timeout`: Controls responsiveness of the recording loop

#### Whisper Settings
- `model`: Larger models are more accurate but slower and use more memory
- `language`: Supports multiple languages (see Whisper documentation)
- `device`: Auto-detects best available computing device

#### Debug Settings
Control verbosity of output during operation

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

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This software is free for non-commercial use. For commercial use, please contact the author.