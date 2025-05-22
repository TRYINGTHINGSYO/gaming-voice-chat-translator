#!/usr/bin/env python3
"""
Setup script for Gaming Voice Chat Translator
"""

import os
import sys
from setuptools import setup, find_packages

# Check Python version
if sys.version_info < (3, 8):
    sys.exit("Python 3.8 or higher is required to run this application")

# Get version from package
with open(os.path.join('gaming_translator', '__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break
    else:
        version = '1.1.0'  # Default version if not found

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Define base requirements
base_requirements = [
    'pyaudio>=0.2.11',
    'SpeechRecognition>=3.8.1',
    'googletrans==4.0.0-rc1',
    'pyttsx3>=2.90',
    'gtts>=2.2.3',
    'pygame>=2.1.0',
    'reportlab>=3.6.6',
]

# Optional requirements for enhanced functionality
optional_requirements = {
    'whisperx': [
        'git+https://github.com/m-bain/whisperx.git',
        'torch>=1.10.0',
        'numpy>=1.20.0',
        'transformers>=4.18.0',
    ],
    'dev': [
        'pytest>=7.0.0',
        'black>=22.1.0',
        'isort>=5.10.1',
        'pyinstaller>=5.1',
    ],
}

# Setup configuration
setup(
    name='gaming-translator',
    version=version,
    description='Real-time voice translation for gaming chat',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Gaming Translator Team',
    author_email='info@gamingtranslator.example.com',
    url='https://github.com/example/gaming-translator',
    packages=find_packages(),
    include_package_data=True,
    install_requires=base_requirements,
    extras_require=optional_requirements,
    entry_points={
        'console_scripts': [
            'gaming-translator=gaming_translator.__main__:main',
        ],
        'gui_scripts': [
            'gaming-translator-gui=gaming_translator.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Communications :: Chat',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Utilities',
    ],
    python_requires='>=3.8',
    keywords='gaming, translation, voice, chat, real-time, speech recognition',
    project_urls={
        'Bug Reports': 'https://github.com/example/gaming-translator/issues',
        'Source': 'https://github.com/example/gaming-translator',
        'Documentation': 'https://github.com/example/gaming-translator/wiki',
    },
    package_data={
        'gaming_translator': [
            'assets/*',
        ],
    },
)