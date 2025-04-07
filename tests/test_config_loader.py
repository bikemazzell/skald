import pytest
import os
import json
from pathlib import Path
from utils.config_loader import ConfigLoader

class TestConfigLoader:
    @pytest.fixture
    def mock_config(self, tmp_path):
        config = {
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
                "event_wait_timeout": 0.1
            },
            "whisper": {
                "model": "base",
                "language": "en",
                "task": "transcribe"
            },
            "debug": {
                "print_status": True,
                "print_transcriptions": True
            },
            "server": {
                "socket_path": "/tmp/test.sock",
                "socket_timeout": 1.0
            }
        }

        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

        os.environ['SKALD_ROOT'] = str(tmp_path)
        return config_path

    def test_load_valid_config(self, mock_config):
        config = ConfigLoader.load_config(mock_config.name)
        assert config["version"] == "1.0"
        assert config["audio"]["sample_rate"] == 16000

    def test_missing_config(self):
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_config("nonexistent.json")

    def test_invalid_json(self, tmp_path):
        bad_config = tmp_path / "bad_config.json"
        bad_config.write_text("{invalid json")
        os.environ['SKALD_ROOT'] = str(tmp_path)
        with pytest.raises(ValueError):
            ConfigLoader.load_config(bad_config.name)