import pytest
import numpy as np
from utils.audio_manager import AudioManager
import sounddevice as sd

class TestAudioManager:
    @pytest.fixture
    def mock_config(self):
        return {
            "audio": {
                "sample_rate": 16000,
                "start_tone": {
                    "enabled": True,
                    "frequency": 440,
                    "duration": 150,
                    "fade_ms": 5
                }
            }
        }

    def test_initialize_audio(self, mocker):
        mock_device = {"name": "Test Device", "max_input_channels": 2}
        mocker.patch('sounddevice.query_devices', return_value=[mock_device])
        mocker.patch('sounddevice.query_devices', return_value=mock_device)
        
        device = AudioManager.initialize_audio()
        assert device["name"] == "Test Device"
        
    def test_play_start_tone(self, mock_config, mocker):
        mock_play = mocker.patch('sounddevice.play')
        AudioManager.play_start_tone(mock_config)
        assert mock_play.called

    def test_play_start_tone_disabled(self, mock_config):
        mock_config["audio"]["start_tone"]["enabled"] = False
        AudioManager.play_start_tone(mock_config)
        # Should complete without error when disabled 