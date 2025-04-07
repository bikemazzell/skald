import pytest
from validators.config_validator import ConfigValidator

class TestConfigValidator:
    @pytest.fixture
    def valid_config(self):
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
                "event_wait_timeout": 0.1
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

    def test_valid_config(self, valid_config):
        # Should not raise any exceptions
        ConfigValidator.validate_config(valid_config)

    def test_missing_version(self, valid_config):
        invalid_config = valid_config.copy()
        del invalid_config["version"]

        with pytest.raises(ValueError, match="Missing field 'version'"):
            ConfigValidator.validate_config(invalid_config)

    def test_invalid_version_format(self, valid_config):
        invalid_config = valid_config.copy()
        invalid_config["version"] = "abc"

        with pytest.raises(ValueError, match="Version must be in format"):
            ConfigValidator.validate_config(invalid_config)

    def test_missing_section(self, valid_config):
        invalid_config = valid_config.copy()
        del invalid_config["audio"]

        with pytest.raises(ValueError, match="Missing section 'audio'"):
            ConfigValidator.validate_config(invalid_config)

    def test_missing_field(self, valid_config):
        invalid_config = valid_config.copy()
        del invalid_config["audio"]["sample_rate"]

        with pytest.raises(ValueError, match="Missing field 'sample_rate'"):
            ConfigValidator.validate_config(invalid_config)

    def test_invalid_sample_rate(self, valid_config):
        invalid_config = valid_config.copy()
        invalid_config["audio"]["sample_rate"] = 12345  # Invalid sample rate

        with pytest.raises(ValueError, match="Sample rate must be"):
            ConfigValidator.validate_config(invalid_config)

    def test_invalid_silence_threshold(self, valid_config):
        invalid_config = valid_config.copy()
        invalid_config["audio"]["silence_threshold"] = 2.0  # Should be between 0 and 1

        with pytest.raises(ValueError, match="Silence threshold must be between"):
            ConfigValidator.validate_config(invalid_config)
