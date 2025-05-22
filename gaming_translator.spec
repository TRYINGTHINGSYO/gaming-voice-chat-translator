# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Gaming Voice Chat Translator
Build with: pyinstaller gaming_translator.spec
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Get the path to the main script
main_script = os.path.join('gaming_translator', '__main__.py')

# Get base directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Define additional data files to include
added_files = [
    # Include assets directory
    (os.path.join(base_dir, 'gaming_translator', 'assets'), 'assets'),
]

# Define additional Python packages
hidden_imports = [
    'pyaudio',
    'speech_recognition',
    'googletrans',
    'pyttsx3',
    'gtts',
    'pygame',
    'torch',
    'reportlab',
    'numpy'
]

# Define WhisperX model files (if available)
try:
    import torch
    import whisperx
    whisperx_dir = Path(whisperx.__file__).parent
    print(f"WhisperX directory: {whisperx_dir}")
    
    # Add WhisperX model files
    whisperx_assets = [
        (os.path.join(whisperx_dir, 'assets'), os.path.join('whisperx', 'assets')),
    ]
    added_files.extend(whisperx_assets)
    
    # Add WhisperX-specific imports
    whisperx_imports = [
        'whisperx',
        'transformers',
        'huggingface_hub',
        'tokenizers',
        'sacremoses',
        'sentencepiece',
        'ffmpeg'
    ]
    hidden_imports.extend(whisperx_imports)
except ImportError:
    print("WhisperX not found, skipping WhisperX-specific files")

# Create the analysis
a = Analysis(
    [main_script],
    pathex=[base_dir],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Bundle everything
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GamingTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(base_dir, 'gaming_translator', 'assets', 'app_icon.ico'),
)

# Create the distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GamingTranslator',
)

# For macOS, create a .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='GamingTranslator.app',
        icon=os.path.join(base_dir, 'gaming_translator', 'assets', 'app_icon.icns'),
        bundle_identifier='com.gaming_translator',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'NSMicrophoneUsageDescription': 'This app needs microphone access for voice recognition.',
            'CFBundleShortVersionString': '1.1.0',
        },
    )