from setuptools import setup, find_packages
import json
import os

# Read version from config.json or config.json.example if config.json doesn't exist
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
example_config_path = os.path.join(os.path.dirname(__file__), 'config.json.example')

try:
    # Try to read from config.json first
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    # Fall back to config.json.example if config.json doesn't exist
    elif os.path.exists(example_config_path):
        with open(example_config_path) as f:
            config = json.load(f)
    else:
        config = {"version": "1.0"}

    version = config.get('version', '1.0')
    # Validate version format
    if not str(version).replace(".", "").isdigit():
        version = '1.0'
except (FileNotFoundError, json.JSONDecodeError):
    version = '1.0'

setup(
    name="skald",
    version=version,
    packages=find_packages(),
    scripts=['skald-server', 'skald-client'],
    install_requires=[
        'numpy',
        'sounddevice',
        'faster-whisper',
        'pyperclip',
        'torch'
    ]
)