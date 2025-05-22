"""
Voice synthesis module for text-to-speech capabilities
"""

import os
import time
import logging
import threading
import tempfile
from abc import ABC, abstractmethod

class VoiceSynthesizer(ABC):
    """Base voice synthesizer interface"""
    
    def __init__(self, config):
        """Initialize the voice synthesizer with configuration"""
        self.logger = logging.getLogger("gaming_translator.voice_synthesizer")
        self.config = config
    
    @abstractmethod
    def speak_text(self, text, language="en"):
        """Speak the given text in the specified language"""
        pass
    
    @staticmethod
    def create_synthesizer(config):
        """Factory method to create the appropriate synthesizer"""
        logger = logging.getLogger("gaming_translator.voice_synthesizer")
        
        # Get configured backend
        backend = config.get_backend_config("tts")
        
        logger.info(f"Creating voice synthesizer with backend: {backend}")
        
        # Create and return appropriate synthesizer
        if backend == "pyttsx3":
            try:
                return PyttsxSynthesizer(config)
            except ImportError:
                logger.warning("pyttsx3 not available, trying other backends")
                backend = "gtts"
        
        if backend == "gtts":
            try:
                return GTTSSynthesizer(config)
            except ImportError:
                logger.error("Google TTS not available")
                raise ImportError("No TTS backend available")
        
        # If we get here, no suitable backend was found
        raise ValueError(f"No suitable TTS backend available")


class PyttsxSynthesizer(VoiceSynthesizer):
    """pyttsx3-based voice synthesizer"""
    
    def __init__(self, config):
        """Initialize with pyttsx3"""
        super().__init__(config)
        
        try:
            import pyttsx3
            
            # Initialize engine
            self.engine = pyttsx3.init()
            
            # Configure properties
            rate = config.get_int("tts", "rate", 150)
            volume = config.get_float("tts", "volume", 0.9)
            
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            self.logger.info(f"pyttsx3 initialized with rate={rate}, volume={volume}")
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
            raise
    
    def speak_text(self, text, language="en"):
        """Speak text using pyttsx3"""
        if not text:
            return
        
        # Note: pyttsx3 doesn't support language selection well,
        # it uses the system voices so we ignore the language parameter
        
        threading.Thread(
            target=self._speak_worker,
            args=(text,),
            daemon=True
        ).start()
    
    def _speak_worker(self, text):
        """Background thread for speaking"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"pyttsx3 error: {e}")


class GTTSSynthesizer(VoiceSynthesizer):
    """Google Text-to-Speech based voice synthesizer"""
    
    def __init__(self, config):
        """Initialize with Google TTS"""
        super().__init__(config)
        
        try:
            from gtts import gTTS
            import pygame
            
            # Just ensure the imports work, actual initialization happens in speak_text
            pygame.mixer.init()
            pygame.mixer.quit()
            
            self.logger.info("Google TTS initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google TTS: {e}")
            raise
    
    def speak_text(self, text, language="en"):
        """Speak text using Google TTS"""
        if not text:
            return
        
        threading.Thread(
            target=self._speak_worker,
            args=(text, language),
            daemon=True
        ).start()
    
    def _speak_worker(self, text, language):
        """Background thread for speaking with Google TTS"""
        try:
            from gtts import gTTS
            import pygame
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_filename = temp_file.name
            
            # Generate audio with gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(temp_filename)
            
            # Play audio with pygame
            pygame.mixer.init()
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            pygame.mixer.quit()
            os.unlink(temp_filename)
            
        except Exception as e:
            self.logger.error(f"Google TTS error: {e}")
            
            # Clean up on error
            try:
                os.unlink(temp_filename)
            except:
                pass


class MultiLanguageVoiceSynthesizer(VoiceSynthesizer):
    """Voice synthesizer with support for multiple languages"""
    
    def __init__(self, config):
        """Initialize with multiple backends for different languages"""
        super().__init__(config)
        
        # Create primary synthesizer
        try:
            self.default_synthesizer = VoiceSynthesizer.create_synthesizer(config)
            
            # Language-specific synthesizers
            self.language_synthesizers = {}
            
            # pyttsx3 is better for English
            if config.get_backend_config("tts") != "pyttsx3":
                try:
                    import pyttsx3
                    self.language_synthesizers["en"] = PyttsxSynthesizer(config)
                    self.logger.info("Added pyttsx3 for English language")
                except ImportError:
                    pass
            
            # gTTS is better for non-English languages
            if config.get_backend_config("tts") != "gtts":
                try:
                    from gtts import gTTS
                    import pygame
                    for lang_code in ["es", "fr", "de", "it", "pt", "zh-CN", "ja", "ko", "ru"]:
                        self.language_synthesizers[lang_code] = GTTSSynthesizer(config)
                    self.logger.info("Added Google TTS for non-English languages")
                except ImportError:
                    pass
            
            self.logger.info("Multi-language synthesizer initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize multi-language synthesizer: {e}")
            raise
    
    def speak_text(self, text, language="en"):
        """Speak text using the appropriate synthesizer for the language"""
        if not text:
            return
        
        # Get appropriate synthesizer for the language
        synthesizer = self.language_synthesizers.get(language, self.default_synthesizer)
        
        # Speak the text with the selected synthesizer
        synthesizer.speak_text(text, language)


# Audio utilities
def play_audio_file(file_path):
    """Play an audio file"""
    try:
        import pygame
        
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.quit()
        return True
    except Exception as e:
        logging.getLogger("gaming_translator").error(f"Error playing audio: {e}")
        return False