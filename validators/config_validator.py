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
                "buffer_size_multiplier"
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
        
        # Validate specific values
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