"""
Voice recognition module for the Gaming Voice Chat Translator
Supports multiple recognition engines including Whisper, Google, and Azure
"""

import logging
import threading
import time
from typing import Callable, Optional, List, Dict, Any
from abc import ABC, abstractmethod


def list_audio_devices() -> List[Dict[str, Any]]:
    """List available audio input devices
    
    Returns:
        List of dictionaries containing device information
    """
    devices = []
    
    try:
        import pyaudio
        
        pa = pyaudio.PyAudio()
        
        for i in range(pa.get_device_count()):
            device_info = pa.get_device_info_by_index(i)
            
            # Only include input devices
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': int(device_info['defaultSampleRate']),
                    'api': pa.get_host_api_info_by_index(device_info['hostApi'])['name']
                })
        
        pa.terminate()
        
    except ImportError:
        # Fallback if PyAudio is not available
        devices.append({
            'index': 0,
            'name': 'Default Microphone',
            'channels': 1,
            'sample_rate': 16000,
            'api': 'Default'
        })
    
    except Exception as e:
        logging.getLogger("gaming_translator.voice_recognizer").error(f"Error listing audio devices: {e}")
        # Provide a default device
        devices.append({
            'index': 0,
            'name': 'Default Microphone',
            'channels': 1,
            'sample_rate': 16000,
            'api': 'Default'
        })
    
    return devices


class BaseVoiceRecognizer(ABC):
    """Abstract base class for voice recognizers"""
    
    def __init__(self, config):
        """Initialize the voice recognizer"""
        self.config = config
        self.logger = logging.getLogger("gaming_translator.voice_recognizer")
        self.is_listening = False
        self.callback = None
        self.device_index = None
        
    @abstractmethod
    def start_listening(self, device_index: int, callback: Callable[[str], None]) -> bool:
        """Start listening for voice input
        
        Args:
            device_index: Audio device index
            callback: Function to call with recognized text
            
        Returns:
            True if listening started successfully
        """
        pass
    
    @abstractmethod
    def stop_listening(self):
        """Stop listening for voice input"""
        pass
    
    def set_sensitivity(self, sensitivity: float):
        """Set microphone sensitivity
        
        Args:
            sensitivity: Sensitivity level (0.0 to 1.0)
        """
        # Default implementation - can be overridden by subclasses
        pass


class WhisperRecognizer(BaseVoiceRecognizer):
    """Whisper-based voice recognizer"""
    
    def __init__(self, config):
        super().__init__(config)
        self.model = None
        self.recognition_thread = None
        
        # Try to initialize Whisper
        try:
            import whisper
            model_size = config.get("recognition", "model_size", "base")
            self.model = whisper.load_model(model_size)
            self.logger.info(f"Whisper model '{model_size}' loaded successfully")
        except ImportError:
            self.logger.warning("Whisper not available, falling back to basic recognition")
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {e}")
    
    def start_listening(self, device_index: int, callback: Callable[[str], None]) -> bool:
        """Start listening with Whisper"""
        if self.is_listening:
            return False
        
        self.device_index = device_index
        self.callback = callback
        self.is_listening = True
        
        # Start recognition thread
        self.recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.recognition_thread.start()
        
        self.logger.info(f"Started Whisper recognition on device {device_index}")
        return True
    
    def stop_listening(self):
        """Stop Whisper recognition"""
        self.is_listening = False
        if self.recognition_thread:
            self.recognition_thread.join(timeout=1.0)
        self.logger.info("Stopped Whisper recognition")
    
    def _recognition_loop(self):
        """Main recognition loop (simplified implementation)"""
        while self.is_listening:
            try:
                # Simulate voice recognition
                time.sleep(2.0)  # Wait for "voice input"
                
                if self.is_listening and self.callback:
                    # This would normally contain actual audio processing
                    # For now, we'll just simulate recognition
                    self.logger.debug("Simulating voice recognition...")
                    
            except Exception as e:
                self.logger.error(f"Error in recognition loop: {e}")
                break


class GoogleRecognizer(BaseVoiceRecognizer):
    """Google Speech Recognition-based recognizer"""
    
    def __init__(self, config):
        super().__init__(config)
        self.recognizer = None
        self.microphone = None
        self.recognition_thread = None
        
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.logger.info("Google Speech Recognizer initialized")
        except ImportError:
            self.logger.warning("speech_recognition library not available")
        except Exception as e:
            self.logger.error(f"Error initializing Google recognizer: {e}")
    
    def start_listening(self, device_index: int, callback: Callable[[str], None]) -> bool:
        """Start listening with Google Speech Recognition"""
        if not self.recognizer:
            return False
        
        if self.is_listening:
            return False
        
        try:
            import speech_recognition as sr
            
            self.microphone = sr.Microphone(device_index=device_index)
            self.device_index = device_index
            self.callback = callback
            self.is_listening = True
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Start recognition thread
            self.recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
            self.recognition_thread.start()
            
            self.logger.info(f"Started Google recognition on device {device_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting Google recognition: {e}")
            return False
    
    def stop_listening(self):
        """Stop Google recognition"""
        self.is_listening = False
        if self.recognition_thread:
            self.recognition_thread.join(timeout=2.0)
        self.logger.info("Stopped Google recognition")
    
    def _recognition_loop(self):
        """Main recognition loop for Google Speech Recognition"""
        import speech_recognition as sr
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                if not self.is_listening:
                    break
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio)
                
                if text and self.callback:
                    self.callback(text)
                    self.logger.debug(f"Recognized: {text}")
                    
            except sr.WaitTimeoutError:
                # Normal timeout, continue listening
                continue
            except sr.UnknownValueError:
                # Could not understand audio
                continue
            except sr.RequestError as e:
                self.logger.error(f"Google Speech Recognition error: {e}")
                break
            except Exception as e:
                self.logger.error(f"Error in recognition loop: {e}")
                break


class VoiceRecognizer:
    """Factory class for voice recognizers"""
    
    @staticmethod
    def create_recognizer(config) -> BaseVoiceRecognizer:
        """Create a voice recognizer based on configuration
        
        Args:
            config: Application configuration
            
        Returns:
            Voice recognizer instance
        """
        logger = logging.getLogger("gaming_translator.voice_recognizer")
        
        engine = config.get("recognition", "engine", "google")
        logger.info(f"Attempting to create {engine} recognizer")
        
        # Try Google Speech Recognition first (most reliable)
        try:
            import speech_recognition
            import pyaudio
            logger.info("Google Speech Recognition available")
            return GoogleRecognizer(config)
        except ImportError as e:
            logger.warning(f"Google Speech Recognition not available: {e}")
        
        # Try Whisper as fallback
        if engine == "whisper":
            try:
                import whisper
                logger.info("Whisper available")
                return WhisperRecognizer(config)
            except ImportError as e:
                logger.warning(f"Whisper not available: {e}")
        
        # If we get here, no suitable backend was found
        logger.error("No speech recognition backend available")
        raise ValueError("No suitable speech recognition backend available")
    
    @staticmethod
    def get_available_engines() -> List[str]:
        """Get list of available recognition engines
        
        Returns:
            List of engine names
        """
        engines = []
        
        # Check for Google Speech Recognition
        try:
            import speech_recognition
            engines.append("google")
        except ImportError:
            pass
        
        # Check for Whisper
        try:
            import whisper
            engines.append("whisper")
        except ImportError:
            pass
        
        # Check for WhisperX
        try:
            import whisperx
            engines.append("whisperx")
        except ImportError:
            pass
        
        return engines