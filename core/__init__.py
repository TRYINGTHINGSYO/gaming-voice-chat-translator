"""
Core package for Gaming Voice Chat Translator
Contains voice recognition, translation, TTS, and session management
"""

# Import core components for easy access (with error handling)
__all__ = []

try:
    from .voice_recognizer import VoiceRecognizer, list_audio_devices
    __all__.extend(["VoiceRecognizer", "list_audio_devices"])
except ImportError:
    pass

try:
    from .translator import Translator, CachedTranslator
    __all__.extend(["Translator", "CachedTranslator"])
except ImportError:
    pass

try:
    from .synthesizer import VoiceSynthesizer, MultiLanguageVoiceSynthesizer
    __all__.extend(["VoiceSynthesizer", "MultiLanguageVoiceSynthesizer"])
except ImportError:
    pass

try:
    from .session_manager import SessionManager, VoiceMessage
    __all__.extend(["SessionManager", "VoiceMessage"])
except ImportError:
    pass