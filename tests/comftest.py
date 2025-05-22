"""
Pytest configuration and fixtures for Gaming Voice Chat Translator tests
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add the parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from gaming_translator.utils.config import AppConfig
from gaming_translator.core.session_manager import SessionManager, VoiceMessage

@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files during tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_config(temp_config_dir):
    """Create a test configuration instance"""
    config_path = temp_config_dir / "test_config.ini"
    config = AppConfig(config_path)
    return config

@pytest.fixture
def mock_audio_device():
    """Mock audio device for testing voice recognition"""
    device = Mock()
    device.name = "Test Microphone"
    device.index = 0
    device.channels = 1
    device.sample_rate = 16000
    return device

@pytest.fixture
def sample_voice_messages():
    """Create sample voice messages for testing"""
    messages = [
        VoiceMessage("Hello team", "en", is_outgoing=True, translation="Hola equipo"),
        VoiceMessage("Good game", "en", is_outgoing=True, translation="Buen juego"),
        VoiceMessage("Nice shot", "en", is_outgoing=False, translation="Buen tiro"),
    ]
    return messages

@pytest.fixture
def test_session_manager(test_config, temp_config_dir):
    """Create a test session manager"""
    # Override session save directory for tests
    test_config.set("session", "save_dir", str(temp_config_dir / "sessions"))
    session_manager = SessionManager(test_config)
    return session_manager

@pytest.fixture
def mock_translator():
    """Mock translator for testing"""
    translator = Mock()
    translator.translate_text.return_value = "Mocked translation"
    translator.detect_language.return_value = "en"
    return translator

@pytest.fixture
def mock_voice_synthesizer():
    """Mock voice synthesizer for testing"""
    synthesizer = Mock()
    synthesizer.speak_text.return_value = None
    return synthesizer

@pytest.fixture
def mock_whisperx():
    """Mock WhisperX for testing without requiring actual installation"""
    mock_whisperx = MagicMock()
    mock_result = {
        "segments": [
            {"text": "Hello world", "start": 0.0, "end": 2.0}
        ]
    }
    mock_whisperx.load_model.return_value.transcribe.return_value = mock_result
    return mock_whisperx

# Test data constants
TEST_LANGUAGES = {
    'en': {'name': 'English', 'flag': '🇺🇸'},
    'es': {'name': 'Spanish', 'flag': '🇪🇸'},
    'fr': {'name': 'French', 'flag': '🇫🇷'},
}

TEST_AUDIO_SAMPLE = b'\x00\x01' * 1024  # Mock 16-bit audio data

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "gpu: mark test as requiring GPU"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )