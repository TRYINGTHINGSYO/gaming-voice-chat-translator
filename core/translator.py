"""
Translation module for the Gaming Voice Chat Translator
Supports multiple translation services including Google Translate and LibreTranslate
"""

import logging
import time
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    """Abstract base class for translators"""
    
    def __init__(self, config):
        """Initialize the translator"""
        self.config = config
        self.logger = logging.getLogger("gaming_translator.translator")
    
    @abstractmethod
    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Optional[str]:
        """Translate text
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto for auto-detect)
            
        Returns:
            Translated text or None if translation failed
        """
        pass
    
    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code
        """
        pass


class GoogleTranslator(BaseTranslator):
    """Google Translate-based translator"""
    
    def __init__(self, config):
        super().__init__(config)
        self.translator = None
        
        try:
            from googletrans import Translator as GoogleTranslator_
            self.translator = GoogleTranslator_()
            self.logger.info("Google Translator initialized")
        except ImportError:
            self.logger.warning("googletrans library not available")
            raise
        except Exception as e:
            self.logger.error(f"Error initializing Google Translator: {e}")
            raise
    
    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Optional[str]:
        """Translate text using Google Translate"""
        if not text or not self.translator:
            return None
        
        try:
            # Skip translation if source and target are the same
            if source_language == target_language and source_language != "auto":
                return text
            
            result = self.translator.translate(text, src=source_language, dest=target_language)
            self.logger.debug(f"Translated '{text}' to '{result.text}'")
            return result.text
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return None
    
    def detect_language(self, text: str) -> str:
        """Detect language using Google Translate"""
        if not text or not self.translator:
            return "en"
        
        try:
            detected = self.translator.detect(text)
            self.logger.debug(f"Detected language: {detected.lang}")
            return detected.lang
        except Exception as e:
            self.logger.error(f"Language detection error: {e}")
            return "en"


class Translator:
    """Factory class for translators"""
    
    @staticmethod
    def create_translator(config):
        """Create a translator based on configuration
        
        Args:
            config: Application configuration
            
        Returns:
            Translator instance
        """
        logger = logging.getLogger("gaming_translator.translator")
        
        service = config.get("translation", "service", "google")
        logger.info(f"Attempting to create {service} translator")
        
        # Try Google Translate
        try:
            from googletrans import Translator as GoogleTranslator_
            logger.info("Google Translate available")
            return GoogleTranslator(config)
        except ImportError as e:
            logger.error(f"Google Translate not available: {e}")
            raise ValueError("No suitable translation backend available")


class CachedTranslator(BaseTranslator):
    """Translator with caching for improved performance"""
    
    def __init__(self, config, base_translator=None):
        super().__init__(config)
        
        if base_translator is None:
            base_translator = Translator.create_translator(config)
        
        self.base_translator = base_translator
        self.cache = {}
        self.cache_size = config.get_int("translation", "cache_size", 1000)
        
        self.logger.info("Cached translator initialized")
    
    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Optional[str]:
        """Translate text with caching"""
        if not text:
            return None
        
        # Create cache key
        cache_key = (text, source_language, target_language)
        
        # Check cache
        if cache_key in self.cache:
            self.logger.debug("Cache hit for translation")
            return self.cache[cache_key]
        
        # Translate
        result = self.base_translator.translate_text(text, target_language, source_language)
        
        # Cache result
        if result and len(self.cache) < self.cache_size:
            self.cache[cache_key] = result
        
        return result
    
    def detect_language(self, text: str) -> str:
        """Detect language using base translator"""
        return self.base_translator.detect_language(text)