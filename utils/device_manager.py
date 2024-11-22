import torch

class DeviceManager:
    @staticmethod
    def get_device_and_compute_type():
        """Determine the best available device and compute type"""
        try:
            if torch.cuda.is_available():
                try:
                    from faster_whisper import WhisperModel
                    model = WhisperModel("tiny", device="cuda", compute_type="float16")
                    return "cuda", "float16"
                except (ImportError, RuntimeError):
                    print("\nGPU detected but CUDNN libraries not found.")
                    print("For better performance, install CUDNN using:")
                    print("  conda: conda install -c conda-forge cudnn")
                    print("  pip:   pip install nvidia-cudnn-cu11==8.5.0.96")
                    print("\nFalling back to CPU...\n")
                    return "cpu", "float32"
            elif torch.backends.mps.is_available():  # Apple Silicon
                return "mps", "float32"
            return "cpu", "float32"
        except ImportError:
            return "cpu", "float32" 