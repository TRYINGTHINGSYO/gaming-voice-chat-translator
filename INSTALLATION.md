# Installation Guide

This guide provides detailed instructions for installing the Gaming Voice Chat Translator on different operating systems.

## Table of Contents
- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Linux Installation](#linux-installation)
- [Installing from Source](#installing-from-source)
- [WhisperX Installation](#whisperx-installation)
- [GPU Acceleration Setup](#gpu-acceleration-setup)
- [AutoHotkey Integration](#autohotkey-integration)
- [Troubleshooting](#troubleshooting)

## Windows Installation

### Method 1: Standalone Executable (Recommended for most users)

1. Download the latest release from [GitHub Releases](https://github.com/example/gaming-translator/releases)
2. Extract the zip file to a location of your choice
3. Run `GamingTranslator.exe`

### Method 2: Python Package (For Python users)

1. Ensure you have Python 3.8 or higher installed
   ```
   python --version
   ```

2. Install the package using pip
   ```
   pip install gaming-translator
   ```

3. Run the application
   ```
   gaming-translator
   ```

### Method 3: Installing with WhisperX for better accuracy

1. Install with WhisperX support
   ```
   pip install gaming-translator[whisperx]
   ```

2. Run the application
   ```
   gaming-translator
   ```

## macOS Installation

1. Ensure you have Python 3.8 or higher installed
   ```
   python3 --version
   ```

2. Install PortAudio (required for PyAudio)
   ```
   brew install portaudio
   ```

3. Install the package using pip
   ```
   pip3 install gaming-translator
   ```

4. Run the application
   ```
   gaming-translator
   ```

## Linux Installation

### Ubuntu/Debian-based distributions

1. Install required system dependencies
   ```
   sudo apt-get update
   sudo apt-get install python3-dev python3-pip portaudio19-dev
   ```

2. Install the package using pip
   ```
   pip3 install gaming-translator
   ```

3. Run the application
   ```
   gaming-translator
   ```

### Fedora/RHEL-based distributions

1. Install required system dependencies
   ```
   sudo dnf install python3-devel python3-pip portaudio-devel
   ```

2. Install the package using pip
   ```
   pip3 install gaming-translator
   ```

3. Run the application
   ```
   gaming-translator
   ```

## Installing from Source

1. Clone the repository
   ```
   git clone https://github.com/example/gaming-translator.git
   cd gaming-translator
   ```

2. Install the package in development mode
   ```
   pip install -e .
   ```

3. For development tools, install the dev extras
   ```
   pip install -e ".[dev]"
   ```

4. Run the application
   ```
   python -m gaming_translator
   ```

## WhisperX Installation

WhisperX provides significantly better accuracy for gaming terminology and supports GPU acceleration.

1. Install the gaming-translator with WhisperX support
   ```
   pip install gaming-translator[whisperx]
   ```

2. If you encounter issues with the WhisperX installation, you can install it separately:
   ```
   pip install git+https://github.com/m-bain/whisperx.git
   pip install torch numpy transformers
   ```

3. Enable WhisperX in the application settings:
   - Go to Settings → Recognition → Backend
   - Select "WhisperX" from the dropdown

## GPU Acceleration Setup

For optimal performance with WhisperX:

### NVIDIA GPUs

1. Install the latest NVIDIA drivers for your GPU

2. Install CUDA and cuDNN:
   - Download and install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
   - Download and install [cuDNN](https://developer.nvidia.com/cudnn)

3. Verify the installation with PyTorch:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should return True
   print(torch.cuda.get_device_name(0))  # Should show your GPU name
   ```

4. Enable GPU acceleration in the application settings:
   - Go to Settings → Recognition → Use GPU
   - Toggle the option to "On"

## AutoHotkey Integration

To enable in-game chat integration:

1. Download and install [AutoHotkey](https://www.autohotkey.com/)

2. Configure AutoHotkey integration in the application:
   - Go to Settings → AutoHotkey
   - Select your game from the presets or configure manually
   - Test the integration with the "Test" button

## Troubleshooting

### Common Issues

#### "No module named 'pyaudio'"
```
pip install pyaudio
```
If this fails on Windows, try using a pre-compiled wheel:
```
pip install pipwin
pipwin install pyaudio
```

#### "No module named 'whisperx'"
```
pip install git+https://github.com/m-bain/whisperx.git
```

#### "Error: No audio devices found"
- Ensure your microphone is properly connected
- Check if your microphone is detected in your system settings
- Try a different USB port if using a USB microphone

#### "AutoHotkey not found"
- Make sure AutoHotkey is installed
- Try reinstalling AutoHotkey
- Restart the application after installing AutoHotkey

#### Performance Issues
- If using WhisperX without GPU: try using Google Speech Recognition instead
- If the application is slow: close other resource-intensive applications
- If overlay causes performance issues: reduce opacity or minimize when not in use

### Getting Help

If you continue to experience issues:

1. Check the log files located in:
   - Windows: `%USERPROFILE%\.gaming_translator\logs\`
   - macOS/Linux: `~/.gaming_translator/logs/`

2. Create an issue on [GitHub](https://github.com/example/gaming-translator/issues) with:
   - Your operating system
   - Python version
   - Detailed description of the problem
   - Relevant log file content