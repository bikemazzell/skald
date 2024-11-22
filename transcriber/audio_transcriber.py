import sounddevice as sd
import numpy as np
import threading
import queue
from faster_whisper import WhisperModel
import pyperclip
from collections import deque
import time
import torch

from validators.config_validator import ConfigValidator
from utils.config_loader import ConfigLoader
from utils.device_manager import DeviceManager
from utils.audio_manager import AudioManager

class AudioTranscriber:
    def __init__(self, config_path="config.json"):
        self.config = ConfigLoader.load_config(config_path)
        ConfigValidator.validate_config(self.config)
        
        # Initialize managers
        AudioManager.initialize_audio()
        device, compute_type = DeviceManager.get_device_and_compute_type()
        
        # Initialize from config
        self.sample_rate = self.config["audio"]["sample_rate"]
        self.silence_threshold = self.config["audio"]["silence_threshold"]
        self.silence_duration = self.config["audio"]["silence_duration"]
        self.chunk_duration = self.config["audio"]["chunk_duration"]
        
        # Calculate buffer size based on config
        buffer_multiplier = self.config["audio"]["buffer_size_multiplier"]
        max_buffer_size = int(self.chunk_duration * self.sample_rate * buffer_multiplier)
        self.audio_buffer = deque(maxlen=max_buffer_size)
        
        self._lock = threading.Lock()
        self.recording = threading.Event()
        self.recording.set()
        self.silence_counter = 0
        self.audio_queue = queue.Queue()
        
        self._initialize_whisper(device, compute_type)
        
        # Check clipboard availability
        self.clipboard_available = self._check_clipboard()

    def _initialize_whisper(self, device, compute_type):
        """Initialize Whisper model"""
        try:
            self.model = WhisperModel(
                self.config["whisper"]["model"],
                device=device,
                compute_type=compute_type
            )
            print(f"Using device: {device} with compute type: {compute_type}")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def _check_clipboard(self):
        """Check if clipboard functionality is available"""
        try:
            pyperclip.copy("test")
            return True
        except Exception as e:
            print("Clipboard functionality not available.")
            print("On Linux, install one of these packages:")
            print("  sudo apt-get install xclip")
            print("  sudo apt-get install xsel")
            return False

    def audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream"""
        if status and self.config["debug"]["print_status"]:
            print(f"Status: {status}")
        
        # Convert to mono if necessary
        audio_data = np.mean(indata, axis=1) if indata.ndim > 1 else indata.copy()
        
        # Check for silence
        if self._check_silence(audio_data):
            self.recording.clear()
        
        self.audio_buffer.extend(audio_data)
        
        # Process chunks when they reach configured duration
        if len(self.audio_buffer) >= self.chunk_duration * self.sample_rate:
            chunk = list(self.audio_buffer)[:int(self.chunk_duration * self.sample_rate)]
            self.audio_queue.put(np.array(chunk))
            self.audio_buffer.clear()

    def _check_silence(self, audio_data):
        """Check for silence in audio data"""
        if np.abs(audio_data).mean() < self.silence_threshold:
            self.silence_counter += len(audio_data) / self.sample_rate
            return self.silence_counter >= self.silence_duration
        else:
            self.silence_counter = 0
            return False

    def process_audio(self):
        """Process audio chunks with Whisper"""
        full_transcription = []  # Store all transcribed segments
        
        while self.recording.is_set() or not self.audio_queue.empty():
            try:
                audio_chunk = self.audio_queue.get(timeout=1)
                # Normalize audio
                audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))
                
                # Transcribe with Whisper using config settings
                segments, info = self.model.transcribe(
                    audio_chunk,
                    language=self.config["whisper"]["language"],
                    task=self.config["whisper"]["task"],
                    beam_size=5
                )
                
                # Handle transcription result
                for segment in segments:
                    if segment.text.strip():
                        transcribed_text = segment.text.strip()
                        full_transcription.append(transcribed_text)
                        
                        if self.config["debug"]["print_transcriptions"]:
                            print(f"Transcribed: {transcribed_text}")
                        
                        # Copy the complete transcription to clipboard
                        if self.clipboard_available:
                            try:
                                complete_text = " ".join(full_transcription)
                                pyperclip.copy(complete_text)
                            except Exception as e:
                                print(f"Failed to copy to clipboard: {e}")
            
            except queue.Empty:
                continue

    def start_recording(self):
        """Start recording and processing audio"""
        max_duration = self.config["audio"]["max_duration"]
        start_time = time.time()
        
        try:
            # Play tone before starting recording
            AudioManager.play_start_tone(self.config)
            
            # Start processing thread
            processing_thread = threading.Thread(target=self.process_audio)
            processing_thread.start()

            # Start audio stream
            with sd.InputStream(callback=self.audio_callback,
                              channels=self.config["audio"]["channels"],
                              samplerate=self.sample_rate):
                print("Recording... (Press Ctrl+C to stop)")
                while self.recording.is_set() and (time.time() - start_time) < max_duration:
                    sd.sleep(100)

            # Process remaining audio in buffer
            if self.audio_buffer:
                self.audio_queue.put(np.array(list(self.audio_buffer)))
            
            # Wait for processing to complete
            processing_thread.join()
            
        except KeyboardInterrupt:
            print("\nRecording stopped.")
            self.recording.clear()
        except sd.PortAudioError as e:
            raise RuntimeError(f"Audio device error: {e}")
        except Exception as e:
            print(f"Error during recording: {e}")

    def cleanup(self):
        """Cleanup resources"""
        self.recording.clear()
        # Clear buffers
        self.audio_buffer.clear()
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def get_device(self):
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():  # For Apple M1/M2
            return "mps"
        return "cpu"