import json
from pathlib import Path

class ConfigLoader:
    @staticmethod
    def load_config(config_path):
        """Load configuration from JSON file"""
        # Validate path
        path = Path(config_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found at {path}")
        
        # Ensure it's in the expected directory
        if not str(path).endswith('.json'):
            raise ValueError("Config file must be a JSON file")
        
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}") 