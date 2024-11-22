```
╔═╗╦╔═╔═╗╦  ╔╦╗
╚═╗╠╩╗╠═╣║   ║║
╚═╝╩ ╩╩ ╩╩═╝═╩╝
```
# Skald - Voice to Text Transcriber
> Created by [@shoewind1997](https://github.com/bikemazzell)

Skald is a lightweight speech-to-text tool that converts your voice to text in real-time. It runs quietly in the background without any graphical interface, automatically copying transcriptions to your clipboard. The application consists of two parts: a background server that handles the transcription, and a client that can be bound to a hotkey for easy start/stop control. Named after the ancient Nordic poets and storytellers known as skalds, this tool makes it effortless to transform your spoken words into written text with a single keystroke.

## Features

- 🎤 Real-time microphone input capture
- 🤖 Advanced speech recognition using Faster Whisper
- 📋 Automatic clipboard copying of transcribed text
- ⏱️ Configurable timeout settings
- 🛑 Interrupt recording with Ctrl+C
- 💪 Optional audio cue when recording starts
- 💪 Multiple whisper models supported (tiny to large-v3)
- 🎯 Optimized for both CPU and GPU processing

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
conda create -n skald python=3.11  # or your preferred Python version
conda activate skald
conda install sounddevice pyperclip numpy scipy
conda install pytorch torchvision torchaudio -c pytorch
pip install faster-whisper  # not available in conda
cp config.json.example config.json
chmod +x skald-server skald-client  # Make scripts executable
```

## System Requirements

### Environment Setup
- Python 3.8 or higher
- Conda environment recommended for dependency management
- Server must run in environment with all dependencies
- Client can run in any Python environment

### Server Dependencies
- faster-whisper
- sounddevice
- pyperclip
- torch
- numpy
- scipy

### Client Dependencies
- Standard Python libraries only (no special requirements)

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

### 1. System Dependencies
#### FFmpeg Installation
##### Windows
```bash
winget install FFmpeg
```

##### macOS
```bash
brew install ffmpeg
```

##### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install ffmpeg
```

#### Linux-specific Dependencies
##### Clipboard Support (Required)
Install either xclip or xsel for clipboard functionality:
```bash
sudo apt update && sudo apt install xclip
# OR
sudo apt update && sudo apt install xsel
```
Note: Without either xclip or xsel, clipboard operations will not work on Linux.

##### Auto-paste Support (Optional)
Install xdotool for auto-paste functionality:
```bash
sudo apt update && sudo apt install xdotool
```
Note: If xdotool is not available, auto-paste will be disabled but copying to clipboard will still work (as long as xclip/xsel is installed).

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
            "duration": 150,          // Tone duration in milliseconds (50-1000)
            "fade_ms": 5             // Fade in/out duration in milliseconds (0-100)
        }
    },
    "processing": {
        "shutdown_timeout": 30,       // Maximum seconds to wait for processing to complete
        "event_wait_timeout": 0.1,    // Timeout for event checking in seconds
        "auto_paste": true           // Automatically paste after copying to clipboard
    },
    "whisper": {
        "model": "large",            // Whisper model size (tiny, base, small, medium, large)
        "language": "en",            // Target language code
        "task": "transcribe",        // Task type (transcribe or translate)
        "beam_size": 5               // Controls the breadth of the beam search (higher values = more accurate but slower)
    },
    "compute": {
        "cuda": "float16",           // Compute type for CUDA GPU (float16, float32, int8)
        "mps": "float32",            // Compute type for Apple Silicon GPU
        "cpu": "int8"                // Compute type for CPU
    },
    "server": {
        "socket_path": "/tmp/skald.sock",  // Unix socket path for client-server communication
        "socket_timeout": 1.0              // Socket timeout in seconds
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
- `auto_paste`: When true, automatically pastes text after copying to clipboard

#### Whisper Settings
- `model`: Larger models are more accurate but slower and use more memory
- `language`: Supports multiple languages (see Whisper documentation)
- `device`: Auto-detects best available computing device
- `beam_size`: Controls the breadth of the beam search (higher values = more accurate but slower)

#### Compute Settings
- `compute`: Specifies precision for different compute devices
  - `cuda`: GPU compute type (typically float16 for best performance)
  - `mps`: Apple Silicon compute type (typically float32)
  - `cpu`: CPU compute type (typically int8 for efficiency)

#### Server Settings
- `socket_path`: Location of Unix socket for client-server communication
- `socket_timeout`: Timeout for socket operations in seconds

#### Start Tone Settings
- `fade_ms`: Duration of fade in/out effect for start tone (0-100ms)

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

1. Start the server (keep it running in background):
```bash
conda activate skald  # Ensure you're in the right environment
./skald-server
```

2. In another terminal, use the client to control recording:
```bash
./skald-client start  # Begin recording
./skald-client stop   # Stop recording manually
```

Recording will automatically stop when either:
- Silence is detected for `silence_duration` seconds (default: 3s)
- Maximum duration is reached (`max_duration` seconds, default: 300s)
- Manual stop command is sent (`./skald-client stop`)

The transcribed text will automatically be:
1. Copied to your clipboard
2. Pasted immediately (if auto_paste is enabled in config)

#### Auto-Stop Settings
```json
{
    "audio": {
        "silence_threshold": 0.01,    // Volume level below which is considered silence (0-1)
        "silence_duration": 3,        // Seconds of silence before auto-stopping
        "max_duration": 300,         // Maximum recording duration in seconds
    }
}
```
You can adjust these values in your config.json to control when recording automatically stops.

You can run the client from any directory, but the server must be running first.

### Auto-Paste Feature
On Linux systems, auto-paste requires xdotool:
```bash
sudo apt-get install xdotool  # one-time installation
```

If xdotool is not available, auto-paste will be disabled but copying to clipboard will still work.


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