from setuptools import setup, find_packages
import json
import os

# Read version from config.json
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(config_path) as f:
        config = json.load(f)
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