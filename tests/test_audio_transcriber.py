import pytest
import numpy as np
import threading
import queue
import platform
import shutil
from unittest.mock import MagicMock, patch
from transcriber.audio_transcriber import AudioTranscriber

class TestAudioTranscriber:
    @pytest.fixture
    def mock_config(self):
        return {
            "version": "1.0",
            "audio": {
                "sample_rate": 16000,
                "silence_threshold": 0.01,
                "silence_duration": 3,
                "chunk_duration": 30,
                "channels": 1,
                "max_duration": 300,
                "buffer_size_multiplier": 2,
                "start_tone": {"enabled": False}
            },
            "processing": {
                "shutdown_timeout": 30,
                "event_wait_timeout": 0.1,
                "auto_paste": False
            },
            "whisper": {
                "model": "tiny",
                "language": "en",
                "task": "transcribe"
            },
            "debug": {
                "print_status": False,
                "print_transcriptions": False
            },
            "server": {
                "socket_path": "/tmp/test.sock",
                "socket_timeout": 1.0
            }
        }

    @pytest.fixture
    def transcriber(self, mock_config, mocker):
        # Mock all external dependencies
        mocker.patch('faster_whisper.WhisperModel')
        mocker.patch('utils.device_manager.DeviceManager.get_device_and_compute_type', return_value=("cpu", "int8"))
        mocker.patch('utils.audio_manager.AudioManager.initialize_audio')
        mocker.patch('transcriber.audio_transcriber.AudioTranscriber._check_clipboard', return_value=True)

        # Create transcriber with mock config
        return AudioTranscriber(config=mock_config)

    def test_audio_callback(self, transcriber):
        # Create mock audio data
        audio_data = np.zeros((1600, 1), dtype=np.float32)
        audio_data[800:801] = 1.0  # Add a spike

        transcriber.audio_callback(audio_data, 1600, 0, None)
        assert len(transcriber.audio_buffer) > 0

    def test_silence_detection(self, transcriber, mocker):
        # We need to mock the silence counter since it's incremented over time
        # Set silence counter to exceed the silence duration threshold
        transcriber.silence_counter = transcriber.silence_duration + 1
        silent_data = np.zeros(1600, dtype=np.float32)
        assert transcriber._check_silence(silent_data)

        # Reset counter and test with noisy data
        transcriber.silence_counter = 0
        noisy_data = np.random.randn(1600) * 0.1
        assert not transcriber._check_silence(noisy_data)

    def test_process_audio(self, transcriber, mocker):
        # Mock the model
        mock_model = mocker.MagicMock()
        mock_segment = mocker.MagicMock()
        mock_segment.text = "test transcription"
        mock_model.transcribe.return_value = ([mock_segment], None)
        transcriber.model = mock_model

        # Mock clipboard operations
        mocker.patch('pyperclip.copy')

        # Add test audio to queue
        test_audio = np.random.randn(16000)  # 1 second of audio
        transcriber.audio_queue.put(test_audio)

        # Clear recording flag to make the process exit quickly
        transcriber.recording.clear()

        # Process the audio
        transcriber.process_audio()

        # Verify model was called
        assert mock_model.transcribe.called

    def test_reset_state(self, transcriber):
        # Set some initial state
        transcriber.silence_counter = 10
        transcriber.recording.clear()

        # Reset state
        transcriber.reset_state()

        # Verify state was reset
        assert transcriber.silence_counter == 0
        assert transcriber.recording.is_set()
        assert transcriber.audio_queue.empty()

    def test_cleanup(self, transcriber):
        # Add some data to the queue
        test_audio = np.random.randn(1600)
        transcriber.audio_queue.put(test_audio)
        transcriber.audio_buffer.extend(test_audio)
        transcriber._processing_complete = True

        # Call cleanup
        transcriber.cleanup()

        # Verify cleanup happened
        assert not transcriber.recording.is_set()
        assert len(transcriber.audio_buffer) == 0
        assert transcriber.audio_queue.empty()

    @patch('platform.system', return_value='Linux')
    @patch('shutil.which', return_value='/usr/bin/xdotool')
    def test_autopaste_detection_linux(self, mock_which, mock_platform, mock_config, mocker):
        # Ensure auto_paste is enabled in config
        config = mock_config.copy()
        config['processing']['auto_paste'] = True

        # Mock dependencies
        mocker.patch('faster_whisper.WhisperModel')
        mocker.patch('utils.device_manager.DeviceManager.get_device_and_compute_type', return_value=("cpu", "int8"))
        mocker.patch('utils.audio_manager.AudioManager.initialize_audio')
        mocker.patch('transcriber.audio_transcriber.AudioTranscriber._check_clipboard', return_value=True)

        # Create transcriber
        transcriber = AudioTranscriber(config=config)

        # Verify auto-paste was detected
        assert transcriber.can_autopaste == True