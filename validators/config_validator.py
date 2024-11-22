class ConfigValidator:
    @staticmethod
    def validate_config(config):
        required_fields = {
            "audio": [
                "sample_rate", 
                "silence_threshold", 
                "silence_duration", 
                "chunk_duration", 
                "channels",
                "max_duration",
                "buffer_size_multiplier",
                "start_tone"
            ],
            "whisper": ["model", "language", "task"],
            "debug": ["print_status", "print_transcriptions"]
        }
        
        for section, fields in required_fields.items():
            if section not in config:
                raise ValueError(f"Missing section '{section}' in config")
            for field in fields:
                if field not in config[section]:
                    raise ValueError(f"Missing field '{field}' in section '{section}'")
        
        if config["audio"]["sample_rate"] not in [16000, 32000, 44100, 48000]:
            raise ValueError("Sample rate must be 16000, 32000, 44100, or 48000")
        
        if not 0 < config["audio"]["silence_threshold"] < 1:
            raise ValueError("Silence threshold must be between 0 and 1")
        
        if config["audio"]["channels"] not in [1, 2]:
            raise ValueError("Channels must be 1 or 2")
        
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if config["whisper"]["model"] not in valid_models:
            raise ValueError(f"Model must be one of: {', '.join(valid_models)}")
        
        if config["audio"]["max_duration"] <= 0:
            raise ValueError("max_duration must be positive")
        
        if config["audio"]["buffer_size_multiplier"] <= 0:
            raise ValueError("buffer_size_multiplier must be positive")
        
        if "start_tone" in config["audio"]:
            tone_config = config["audio"]["start_tone"]
            if not isinstance(tone_config, dict):
                raise ValueError("start_tone must be an object")
            if "enabled" not in tone_config:
                raise ValueError("start_tone must have 'enabled' field")
            if tone_config["enabled"]:
                if "frequency" not in tone_config:
                    raise ValueError("start_tone must have 'frequency' when enabled")
                if "duration" not in tone_config:
                    raise ValueError("start_tone must have 'duration' when enabled")
                if not 20 <= tone_config["frequency"] <= 20000:
                    raise ValueError("frequency must be between 20 and 20000 Hz")
                if not 50 <= tone_config["duration"] <= 1000:
                    raise ValueError("duration must be between 50 and 1000 ms") 