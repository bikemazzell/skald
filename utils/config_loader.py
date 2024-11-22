import json
from pathlib import Path
import os

class ConfigLoader:
    @staticmethod
    def load_config(config_filename="config.json"):
        script_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        config_path = script_dir / config_filename
        
        if not config_path.is_file():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        if not str(config_path).endswith('.json'):
            raise ValueError("Config file must be a JSON file")
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}") 