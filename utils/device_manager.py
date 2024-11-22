import torch
from utils.config_loader import ConfigLoader

class DeviceManager:
    @staticmethod
    def get_device_and_compute_type():
        config = ConfigLoader.load_config()
        default_compute_types = {
            "cuda": "float16",
            "mps": "float32",
            "cpu": "int8"
        }
        compute_types = config.get("compute", default_compute_types)
        
        try:
            if torch.cuda.is_available():
                return "cuda", compute_types["cuda"]
            elif torch.backends.mps.is_available():
                return "mps", compute_types["mps"]
            return "cpu", compute_types["cpu"]
        except ImportError:
            return "cpu", compute_types["cpu"]