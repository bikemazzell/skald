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
        try:
            original_content = pyperclip.paste()
            pyperclip.copy("test")
            pyperclip.copy(original_content)  # Restore original content
            return True
        except Exception as e:
            print("Clipboard functionality not available.")
            print("On Linux, install one of these packages:")
            print("  sudo apt-get install xclip")
            print("  sudo apt-get install xsel")
            return False

    def audio_callback(self, indata, frames, time, status):
        if status and self.config["debug"]["print_status"]:
            print(f"Status: {status}")
        
        audio_data = np.mean(indata, axis=1) if indata.ndim > 1 else indata.copy()
        self.audio_buffer.extend(audio_data)
        
        buffer_size = len(self.audio_buffer)
        chunk_size = int(self.chunk_duration * self.sample_rate)
        
        if buffer_size >= chunk_size:
            chunk = list(self.audio_buffer)[:chunk_size]
            self.audio_queue.put(np.array(chunk))
            for _ in range(chunk_size):
                self.audio_buffer.popleft()
        
        if self._check_silence(audio_data):
            if self.audio_buffer:
                self.audio_queue.put(np.array(list(self.audio_buffer)))
                self.audio_buffer.clear()
            self.recording.clear()

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
        full_transcription = []
        seen_transcriptions = set()
        last_processed_text = None
        self._processing_complete = False
        
        try:
            while self.recording.is_set() or not self.audio_queue.empty():
                try:
                    audio_chunk = self.audio_queue.get(timeout=1)
                    
                    # Check if the audio chunk contains any signal
                    max_abs = np.max(np.abs(audio_chunk))
                    if max_abs < 1e-10:  # Effectively silent
                        continue
                    
                    # Normalize non-silent audio
                    audio_chunk = audio_chunk / max_abs
                    
                    segments, info = self.model.transcribe(
                        audio_chunk,
                        language=self.config["whisper"]["language"],
                        task=self.config["whisper"]["task"],
                        beam_size=5
                    )
                    
                    chunk_text = []
                    for segment in segments:
                        if segment.text.strip():
                            chunk_text.append(segment.text.strip())
                    
                    if chunk_text:
                        combined_text = " ".join(chunk_text)
                        if combined_text not in seen_transcriptions:
                            seen_transcriptions.add(combined_text)
                            full_transcription.append(combined_text)
                            last_processed_text = combined_text
                    
                    if self.clipboard_available and full_transcription:
                        try:
                            complete_text = " ".join(full_transcription)
                            pyperclip.copy(complete_text)
                        except Exception:
                            pass
                        
                except queue.Empty:
                    continue
                except Exception:
                    continue
            
            if full_transcription:
                complete_text = " ".join(full_transcription)
                print("\nComplete Transcription:")
                print(complete_text)
                
                if self.clipboard_available:
                    try:
                        pyperclip.copy(complete_text)
                    except Exception:
                        pass
        
        finally:
            self._processing_complete = True

    def start_recording(self):
        """Start recording and processing audio"""
        max_duration = self.config["audio"]["max_duration"]
        shutdown_timeout = self.config["processing"]["shutdown_timeout"]
        event_wait_timeout = self.config["processing"]["event_wait_timeout"]
        start_time = time.time()
        processing_thread = None
        
        try:
            AudioManager.play_start_tone(self.config)
            processing_thread = threading.Thread(target=self.process_audio)
            processing_thread.start()

            with sd.InputStream(callback=self.audio_callback,
                              channels=self.config["audio"]["channels"],
                              samplerate=self.sample_rate):
                print("Recording... (Press Ctrl+C to stop)")
                while self.recording.is_set() and (time.time() - start_time) < max_duration:
                    self.recording.wait(timeout=event_wait_timeout)

        except KeyboardInterrupt:
            self.recording.clear()
            if self.audio_buffer:
                self.audio_queue.put(np.array(list(self.audio_buffer)))
            
        finally:
            if processing_thread and processing_thread.is_alive():
                processing_thread.join(timeout=shutdown_timeout)
            self.cleanup()

    def cleanup(self):
        """Silent cleanup"""
        self.recording.clear()
        if hasattr(self, '_processing_complete') and self._processing_complete:
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