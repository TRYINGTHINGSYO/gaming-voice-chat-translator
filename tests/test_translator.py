"""
Tests for the translation module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from gaming_translator.core.translator import (
    Translator, GoogleTranslator, TranslationCache, CachedTranslator
)

class TestTranslatorFactory:
    """Test the translator factory method"""
    
    def test_create_google_translator(self, test_config):
        """Test creating Google translator"""
        test_config.set("translation", "backend", "google")
        
        with patch('gaming_translator.core.translator.GoogleTranslator'):
            translator = Translator.create_translator(test_config)
            assert translator is not None
    
    def test_invalid_backend(self, test_config):
        """Test creating translator with invalid backend"""
        test_config.set("translation", "backend", "invalid")
        
        with pytest.raises(ValueError):
            Translator.create_translator(test_config)

class TestGoogleTranslator:
    """Test the Google Translate implementation"""
    
    @patch('googletrans.Translator')
    def test_initialization(self, mock_googletrans, test_config):
        """Test Google translator initialization"""
        translator = GoogleTranslator(test_config)
        assert translator.translator is not None
    
    @patch('googletrans.Translator')
    def test_translate_text_success(self, mock_googletrans, test_config):
        """Test successful text translation"""
        translator = GoogleTranslator(test_config)
        
        # Mock translation result
        mock_result = Mock()
        mock_result.text = "Hola mundo"
        translator.translator.translate.return_value = mock_result
        
        result = translator.translate_text("Hello world", "es", "en")
        assert result == "Hola mundo"
        translator.translator.translate.assert_called_once_with(
            "Hello world", src="en", dest="es"
        )
    
    @patch('googletrans.Translator')
    def test_translate_text_with_detection(self, mock_googletrans, test_config):
        """Test translation with automatic language detection"""
        translator = GoogleTranslator(test_config)
        
        # Mock language detection
        mock_detection = Mock()
        mock_detection.lang = "en"
        translator.translator.detect.return_value = mock_detection
        
        # Mock translation result
        mock_result = Mock()
        mock_result.text = "Hola mundo"
        translator.translator.translate.return_value = mock_result
        
        result = translator.translate_text("Hello world", "es")
        assert result == "Hola mundo"
        translator.translator.detect.assert_called_once_with("Hello world")
    
    @patch('googletrans.Translator')
    def test_translate_same_language(self, mock_googletrans, test_config):
        """Test translation when source and target languages are the same"""
        translator = GoogleTranslator(test_config)
        
        result = translator.translate_text("Hello world", "en", "en")
        assert result == "Hello world"
        translator.translator.translate.assert_not_called()
    
    @patch('googletrans.Translator')
    def test_translate_empty_text(self, mock_googletrans, test_config):
        """Test translation with empty text"""
        translator = GoogleTranslator(test_config)
        
        result = translator.translate_text("", "es", "en")
        assert result is None
    
    @patch('googletrans.Translator')
    def test_translate_error_handling(self, mock_googletrans, test_config):
        """Test translation error handling"""
        translator = GoogleTranslator(test_config)
        translator.translator.translate.side_effect = Exception("API Error")
        
        result = translator.translate_text("Hello world", "es", "en")
        assert result is None
    
    @patch('googletrans.Translator')
    def test_detect_language_success(self, mock_googletrans, test_config):
        """Test successful language detection"""
        translator = GoogleTranslator(test_config)
        
        mock_detection = Mock()
        mock_detection.lang = "es"
        translator.translator.detect.return_value = mock_detection
        
        result = translator.detect_language("Hola mundo")
        assert result == "es"
    
    @patch('googletrans.Translator')
    def test_detect_language_empty_text(self, mock_googletrans, test_config):
        """Test language detection with empty text"""
        translator = GoogleTranslator(test_config)
        
        result = translator.detect_language("")
        assert result == "en"  # Default to English
    
    @patch('googletrans.Translator')
    def test_detect_language_error(self, mock_googletrans, test_config):
        """Test language detection error handling"""
        translator = GoogleTranslator(test_config)
        translator.translator.detect.side_effect = Exception("Detection error")
        
        result = translator.detect_language("Hello world")
        assert result == "en"  # Default to English on error

class TestTranslationCache:
    """Test the translation cache implementation"""
    
    def test_cache_initialization(self):
        """Test cache initialization"""
        cache = TranslationCache(max_size=100)
        assert cache.max_size == 100
        assert len(cache.cache) == 0
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0
    
    def test_cache_miss(self):
        """Test cache miss"""
        cache = TranslationCache()
        result = cache.get("hello", "en", "es")
        assert result is None
        assert cache.stats["misses"] == 1
        assert cache.stats["hits"] == 0
    
    def test_cache_hit(self):
        """Test cache hit"""
        cache = TranslationCache()
        cache.set("hello", "en", "es", "hola")
        
        result = cache.get("hello", "en", "es")
        assert result == "hola"
        assert cache.stats["hits"] == 1
        assert cache.stats["misses"] == 0
    
    def test_cache_size_limit(self):
        """Test cache size limiting"""
        cache = TranslationCache(max_size=2)
        
        # Fill cache beyond limit
        cache.set("hello", "en", "es", "hola")
        cache.set("world", "en", "es", "mundo")
        cache.set("test", "en", "es", "prueba")
        
        # Cache should be cleaned when limit is exceeded
        assert len(cache.cache) <= 2
    
    def test_cache_clear(self):
        """Test cache clearing"""
        cache = TranslationCache()
        cache.set("hello", "en", "es", "hola")
        cache.set("world", "en", "es", "mundo")
        
        cache.clear()
        assert len(cache.cache) == 0
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = TranslationCache()
        
        # Generate some hits and misses
        cache.get("hello", "en", "es")  # miss
        cache.set("hello", "en", "es", "hola")
        cache.get("hello", "en", "es")  # hit
        cache.get("world", "en", "es")  # miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 33.33333333333333  # 1/3 * 100
        assert stats["size"] == 1

class TestCachedTranslator:
    """Test the cached translator implementation"""
    
    def test_initialization_with_base_translator(self, test_config):
        """Test cached translator initialization with base translator"""
        base_translator = Mock()
        cached_translator = CachedTranslator(test_config, base_translator)
        
        assert cached_translator.translator == base_translator
        assert cached_translator.cache is not None
    
    @patch('gaming_translator.core.translator.Translator.create_translator')
    def test_initialization_without_base_translator(self, mock_create, test_config):
        """Test cached translator initialization without base translator"""
        mock_translator = Mock()
        mock_create.return_value = mock_translator
        
        cached_translator = CachedTranslator(test_config)
        assert cached_translator.translator == mock_translator
    
    def test_translate_with_cache_miss(self, test_config):
        """Test translation with cache miss"""
        base_translator = Mock()
        base_translator.translate_text.return_value = "hola"
        base_translator.detect_language.return_value = "en"
        
        cached_translator = CachedTranslator(test_config, base_translator)
        
        result = cached_translator.translate_text("hello", "es", "en")
        assert result == "hola"
        base_translator.translate_text.assert_called_once_with("hello", "es", "en")
    
    def test_translate_with_cache_hit(self, test_config):
        """Test translation with cache hit"""
        base_translator = Mock()
        base_translator.detect_language.return_value = "en"
        
        cached_translator = CachedTranslator(test_config, base_translator)
        
        # First call - cache miss
        cached_translator.cache.set("hello", "en", "es", "hola")
        
        # Second call - cache hit
        result = cached_translator.translate_text("hello", "es", "en")
        assert result == "hola"
        base_translator.translate_text.assert_not_called()
    
    def test_translate_with_auto_detect(self, test_config):
        """Test translation with automatic language detection"""
        base_translator = Mock()
        base_translator.translate_text.return_value = "hola"
        base_translator.detect_language.return_value = "en"
        
        cached_translator = CachedTranslator(test_config, base_translator)
        
        result = cached_translator.translate_text("hello", "es")
        assert result == "hola"
        base_translator.detect_language.assert_called_once_with("hello")
        base_translator.translate_text.assert_called_once_with("hello", "es", "en")
    
    def test_detect_language_delegation(self, test_config):
        """Test language detection delegation to base translator"""
        base_translator = Mock()
        base_translator.detect_language.return_value = "es"
        
        cached_translator = CachedTranslator(test_config, base_translator)
        
        result = cached_translator.detect_language("hola")
        assert result == "es"
        base_translator.detect_language.assert_called_once_with("hola")
    
    def test_get_cache_stats(self, test_config):
        """Test getting cache statistics"""
        base_translator = Mock()
        cached_translator = CachedTranslator(test_config, base_translator)
        
        stats = cached_translator.get_cache_stats()
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
    
    def test_clear_cache(self, test_config):
        """Test clearing the cache"""
        base_translator = Mock()
        cached_translator = CachedTranslator(test_config, base_translator)
        
        # Add something to cache
        cached_translator.cache.set("hello", "en", "es", "hola")
        assert len(cached_translator.cache.cache) == 1
        
        # Clear cache
        cached_translator.clear_cache()
        assert len(cached_translator.cache.cache) == 0

@pytest.mark.integration
class TestTranslationIntegration:
    """Integration tests for translation"""
    
    @patch('googletrans.Translator')
    def test_end_to_end_translation(self, mock_googletrans, test_config):
        """Test complete translation flow"""
        # Create cached translator
        base_translator = GoogleTranslator(test_config)
        cached_translator = CachedTranslator(test_config, base_translator)
        
        # Mock Google Translate responses
        mock_detection = Mock()
        mock_detection.lang = "en"
        base_translator.translator.detect.return_value = mock_detection
        
        mock_result = Mock()
        mock_result.text = "Hola mundo"
        base_translator.translator.translate.return_value = mock_result
        
        # First translation (cache miss)
        result1 = cached_translator.translate_text("Hello world", "es")
        assert result1 == "Hola mundo"
        
        # Second translation (cache hit)
        result2 = cached_translator.translate_text("Hello world", "es")
        assert result2 == "Hola mundo"
        
        # Verify cache was used
        stats = cached_translator.get_cache_stats()
        assert stats["hits"] >= 1