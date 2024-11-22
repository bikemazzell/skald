from setuptools import setup, find_packages

setup(
    name="skald",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'faster-whisper>=0.10.0',
        'torch>=2.0.0',
        'numpy>=1.20.0',
        'pyperclip',
        'scipy',
        'sounddevice'
    ],
    python_requires='>=3.7',
) 