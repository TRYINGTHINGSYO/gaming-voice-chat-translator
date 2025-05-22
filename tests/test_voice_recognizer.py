"""
Tests for the voice recognition module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import threading
import time

from gaming_translator.core.voice_recognizer import (
    VoiceRecognizer, GoogleRecognizer, WhisperXRecognizer, list_audio_devices
)

class TestVoiceRecognizerFactory:
    """Test the voice recognizer factory method"""
    
    def test_create_google_recognizer(self, test_config):
        """Test creating Google recognizer"""
        test_config.set("recognition", "backend", "google")
        
        with patch('gaming_translator.core.voice_recognizer.GoogleRecognizer'):
            recognizer = VoiceRecognizer.create_recognizer(test_config)
            assert recognizer is not None
    
    def test_create_whisperx_recognizer(self, test_config):
        """Test creating WhisperX recognizer"""
        test_config.set("recognition", "backend", "whisperx")
        
        with patch('gaming_translator.core.voice_recognizer.WhisperXRecognizer'):
            recognizer = VoiceRecognizer.create_recognizer(test_config)
            assert recognizer is not None
    
    def test_fallback_to_google(self, test_config):
        """Test fallback from WhisperX to Google when WhisperX unavailable"""
        test_config.set("recognition", "backend", "whisperx")
        
        with patch('gaming_translator.core.voice_recognizer.WhisperXRecognizer', 
                   side_effect=ImportError("WhisperX not available")):
            with patch('gaming_translator.core.voice_recognizer.GoogleRecognizer'):
                recognizer = VoiceRecognizer.create_recognizer(test_config)
                assert recognizer is not None

class TestGoogleRecognizer:
    """Test the Google Speech Recognition implementation"""
    
    @patch('speech_recognition.Recognizer')
    @patch('pyaudio.PyAudio')
    def test_initialization(self, mock_pyaudio, mock_recognizer, test_config):
        """Test Google recognizer initialization"""
        recognizer = GoogleRecognizer(test_config)
        assert recognizer.recognizer is not None
        assert not recognizer.is_listening
    
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    @patch('pyaudio.PyAudio')
    def test_start_listening_success(self, mock_pyaudio, mock_microphone, mock_recognizer, test_config):
        """Test successful start of listening"""
        recognizer = GoogleRecognizer(test_config)
        callback = Mock()
        
        # Mock microphone context manager
        mock_mic_instance = Mock()
        mock_microphone.return_value.__enter__ = Mock(return_value=mock_mic_instance)
        mock_microphone.return_value.__exit__ = Mock(return_value=None)
        
        success = recognizer.start_listening(0, callback)
        assert success
        assert recognizer.is_listening
        assert recognizer.callback == callback
    
    @patch('speech_recognition.Recognizer')
    @patch('pyaudio.PyAudio')
    def test_stop_listening(self, mock_pyaudio, mock_recognizer, test_config):
        """Test stopping listening"""
        recognizer = GoogleRecognizer(test_config)
        recognizer.is_listening = True
        
        recognizer.stop_listening()
        assert not recognizer.is_listening
    
    @patch('speech_recognition.Recognizer')
    @patch('pyaudio.PyAudio')
    def test_process_audio_success(self, mock_pyaudio, mock_recognizer, test_config):
        """Test successful audio processing"""
        recognizer = GoogleRecognizer(test_config)
        callback = Mock()
        recognizer.callback = callback
        
        # Mock recognizer to return text
        mock_audio = Mock()
        recognizer.recognizer.recognize_google.return_value = "Hello world"
        
        recognizer._process_audio(mock_audio)
        callback.assert_called_once_with("Hello world")
    
    @patch('speech_recognition.Recognizer')
    @patch('pyaudio.PyAudio')
    def test_process_audio_unknown_value(self, mock_pyaudio, mock_recognizer, test_config):
        """Test audio processing with unknown value error"""
        import speech_recognition as sr
        
        recognizer = GoogleRecognizer(test_config)
        callback = Mock()
        recognizer.callback = callback
        
        # Mock recognizer to raise UnknownValueError
        mock_audio = Mock()
        recognizer.recognizer.recognize_google.side_effect = sr.UnknownValueError()
        
        recognizer._process_audio(mock_audio)
        callback.assert_not_called()

class TestWhisperXRecognizer:
    """Test the WhisperX implementation"""
    
    @patch('whisperx.load_model')
    @patch('torch.cuda.is_available', return_value=True)
    @patch('pyaudio.PyAudio')
    def test_initialization_with_gpu(self, mock_pyaudio, mock_cuda, mock_load_model, test_config):
        """Test WhisperX initialization with GPU"""
        test_config.set("recognition", "use_gpu", "true")
        test_config.has_gpu = True
        
        recognizer = WhisperXRecognizer(test_config)
        assert recognizer.device == "cuda"
        assert recognizer.use_gpu
    
    @patch('whisperx.load_model')
    @patch('torch.cuda.is_available', return_value=False)
    @patch('pyaudio.PyAudio')
    def test_initialization_without_gpu(self, mock_pyaudio, mock_cuda, mock_load_model, test_config):
        """Test WhisperX initialization without GPU"""
        test_config.has_gpu = False
        
        recognizer = WhisperXRecognizer(test_config)
        assert recognizer.device == "cpu"
        assert not recognizer.use_gpu
    
    @patch('whisperx.load_model')
    @patch('pyaudio.PyAudio')
    def test_lazy_model_loading(self, mock_pyaudio, mock_load_model, test_config):
        """Test that WhisperX model is loaded lazily"""
        recognizer = WhisperXRecognizer(test_config)
        assert recognizer.model is None
        
        recognizer._lazy_load_model()
        mock_load_model.assert_called_once()
        assert recognizer.model is not None
    
    @patch('whisperx.load_model')
    @patch('pyaudio.PyAudio')
    def test_start_listening_success(self, mock_pyaudio, mock_load_model, test_config):
        """Test successful start of WhisperX listening"""
        recognizer = WhisperXRecognizer(test_config)
        callback = Mock()
        
        success = recognizer.start_listening(0, callback)
        assert success
        assert recognizer.is_listening
        assert recognizer.callback == callback

class TestAudioDevices:
    """Test audio device listing functionality"""
    
    @patch('pyaudio.PyAudio')
    def test_list_audio_devices(self, mock_pyaudio):
        """Test listing audio devices"""
        # Mock PyAudio device info
        mock_pa_instance = Mock()
        mock_pyaudio.return_value = mock_pa_instance
        mock_pa_instance.get_device_count.return_value = 2
        
        def mock_device_info(index):
            if index == 0:
                return {
                    'name': 'Test Microphone',
                    'maxInputChannels': 1,
                    'defaultSampleRate': 44100.0
                }
            else:
                return {
                    'name': 'Test Speaker',
                    'maxInputChannels': 0,  # Output device
                    'defaultSampleRate': 44100.0
                }
        
        mock_pa_instance.get_device_info_by_index.side_effect = mock_device_info
        
        devices = list_audio_devices()
        
        # Should only return input devices
        assert len(devices) == 1
        assert devices[0]['name'] == 'Test Microphone'
        assert devices[0]['index'] == 0
        assert devices[0]['channels'] == 1
    
    @patch('pyaudio.PyAudio', side_effect=ImportError("PyAudio not available"))
    def test_list_audio_devices_no_pyaudio(self, mock_pyaudio):
        """Test listing devices when PyAudio is not available"""
        devices = list_audio_devices()
        assert devices == []

@pytest.mark.integration
class TestVoiceRecognitionIntegration:
    """Integration tests for voice recognition"""
    
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    @patch('pyaudio.PyAudio')
    def test_end_to_end_recognition_flow(self, mock_pyaudio, mock_microphone, mock_recognizer, test_config):
        """Test complete recognition flow"""
        recognizer = GoogleRecognizer(test_config)
        
        # Mock microphone context manager
        mock_mic_instance = Mock()
        mock_microphone.return_value.__enter__ = Mock(return_value=mock_mic_instance)
        mock_microphone.return_value.__exit__ = Mock(return_value=None)
        
        # Mock audio data and recognition
        mock_audio = Mock()
        recognizer.recognizer.listen.return_value = mock_audio
        recognizer.recognizer.recognize_google.return_value = "Integration test"
        
        callback_results = []
        def test_callback(text):
            callback_results.append(text)
        
        # Start listening
        success = recognizer.start_listening(0, test_callback)
        assert success
        
        # Simulate processing
        recognizer._process_audio(mock_audio)
        
        # Verify callback was called
        assert "Integration test" in callback_results
        
        # Stop listening
        recognizer.stop_listening()
        assert not recognizer.is_listening