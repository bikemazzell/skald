import pytest
import torch
from utils.device_manager import DeviceManager
from utils.config_loader import ConfigLoader

class TestDeviceManager:
    @pytest.fixture
    def mock_config(self):
        return {
            "compute": {
                "cuda": "float16",
                "mps": "float32",
                "cpu": "int8"
            }
        }

    def test_get_device_cpu_fallback(self, mocker, mock_config):
        mocker.patch('torch.cuda.is_available', return_value=False)
        mocker.patch('torch.backends.mps.is_available', return_value=False)
        mocker.patch('utils.config_loader.ConfigLoader.load_config', return_value=mock_config)

        device, compute_type = DeviceManager.get_device_and_compute_type()
        assert device == "cpu"
        assert compute_type == "int8"

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_get_device_cuda(self, mocker, mock_config):
        mocker.patch('utils.config_loader.ConfigLoader.load_config', return_value=mock_config)

        device, compute_type = DeviceManager.get_device_and_compute_type()
        assert device == "cuda"
        assert compute_type == "float16"