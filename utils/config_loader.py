import json
from pathlib import Path
import os

class ConfigLoader:
    @staticmethod
    def load_config(config_filename="config.json"):
        project_root = os.environ.get('SKALD_ROOT')
        if not project_root:
            raise RuntimeError("SKALD_ROOT environment variable not set")
            
        config_path = Path(project_root) / config_filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}") 