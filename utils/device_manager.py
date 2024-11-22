import torch

class DeviceManager:
    @staticmethod
    def get_device_and_compute_type():
        try:
            if torch.cuda.is_available():
                try:
                    from faster_whisper import WhisperModel
                    model = WhisperModel("tiny", device="cuda", compute_type="float16")
                    return "cuda", "float16"
                except (ImportError, RuntimeError, OSError) as e:
                    print("\nGPU detected but CUDA/cuDNN libraries not properly configured:")
                    print(f"Error: {str(e)}")
                    print("\nFor GPU support, install CUDA and cuDNN:")
                    print("  conda: conda install -c conda-forge cudnn --solver=classic")
                    print("  pip:   pip install nvidia-cudnn-cu11")
                    print("\nFalling back to CPU...\n")
                    return "cpu", "int8"
            elif torch.backends.mps.is_available():  # Apple Silicon
                return "mps", "float32"
            return "cpu", "int8"
        except ImportError:
            return "cpu", "int8"