"""
Constants and configuration values for the Gaming Voice Chat Translator
Contains application metadata, UI colors, supported languages, and export formats
"""

# Application Information
APP_NAME = "Gaming Voice Chat Translator"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Real-time voice translator for gaming"
APP_AUTHOR = "Gaming Translator Team"
APP_URL = "https://github.com/gaming-translator/gaming-voice-chat-translator"

# UI Color Scheme (Dark Theme)
UI_COLORS = {
    "BG_COLOR": "#2b2b2b",           # Main background
    "CARD_BG": "#3c3c3c",           # Card/panel background
    "TEXT_COLOR": "#ffffff",         # Primary text
    "ACCENT_COLOR": "#4a9eff",       # Accent/highlight color
    "SUCCESS_COLOR": "#4caf50",      # Success/positive actions
    "WARNING_COLOR": "#ff9800",      # Warning/caution
    "ERROR_COLOR": "#f44336",        # Error/danger
    "MUTED_COLOR": "#888888",        # Secondary/muted text
    "BORDER_COLOR": "#555555",       # Borders and separators
    "HOVER_COLOR": "#484848",        # Hover states
    "SELECTED_COLOR": "#1976d2",     # Selected states
    "DISABLED_COLOR": "#666666",     # Disabled elements
}

# Supported Gaming Languages with flags and language codes
GAMING_LANGUAGES = {
    # Major gaming languages
    "en": {"name": "English", "flag": "🇺🇸", "tts_available": True},
    "es": {"name": "Spanish", "flag": "🇪🇸", "tts_available": True},
    "fr": {"name": "French", "flag": "🇫🇷", "tts_available": True},
    "de": {"name": "German", "flag": "🇩🇪", "tts_available": True},
    "it": {"name": "Italian", "flag": "🇮🇹", "tts_available": True},
    "pt": {"name": "Portuguese", "flag": "🇵🇹", "tts_available": True},
    "ru": {"name": "Russian", "flag": "🇷🇺", "tts_available": True},
    "ja": {"name": "Japanese", "flag": "🇯🇵", "tts_available": True},
    "ko": {"name": "Korean", "flag": "🇰🇷", "tts_available": True},
    "zh": {"name": "Chinese (Simplified)", "flag": "🇨🇳", "tts_available": True},
    "zh-tw": {"name": "Chinese (Traditional)", "flag": "🇹🇼", "tts_available": True},
    
    # European languages
    "nl": {"name": "Dutch", "flag": "🇳🇱", "tts_available": True},
    "pl": {"name": "Polish", "flag": "🇵🇱", "tts_available": True},
    "sv": {"name": "Swedish", "flag": "🇸🇪", "tts_available": True},
    "no": {"name": "Norwegian", "flag": "🇳🇴", "tts_available": True},
    "da": {"name": "Danish", "flag": "🇩🇰", "tts_available": True},
    "fi": {"name": "Finnish", "flag": "🇫🇮", "tts_available": True},
    "cs": {"name": "Czech", "flag": "🇨🇿", "tts_available": True},
    "hu": {"name": "Hungarian", "flag": "🇭🇺", "tts_available": True},
    "ro": {"name": "Romanian", "flag": "🇷🇴", "tts_available": True},
    "bg": {"name": "Bulgarian", "flag": "🇧🇬", "tts_available": True},
    "hr": {"name": "Croatian", "flag": "🇭🇷", "tts_available": True},
    "sk": {"name": "Slovak", "flag": "🇸🇰", "tts_available": True},
    "sl": {"name": "Slovenian", "flag": "🇸🇮", "tts_available": True},
    "et": {"name": "Estonian", "flag": "🇪🇪", "tts_available": False},
    "lv": {"name": "Latvian", "flag": "🇱🇻", "tts_available": False},
    "lt": {"name": "Lithuanian", "flag": "🇱🇹", "tts_available": False},
    "el": {"name": "Greek", "flag": "🇬🇷", "tts_available": True},
    
    # Other popular languages
    "ar": {"name": "Arabic", "flag": "🇸🇦", "tts_available": True},
    "he": {"name": "Hebrew", "flag": "🇮🇱", "tts_available": True},
    "tr": {"name": "Turkish", "flag": "🇹🇷", "tts_available": True},
    "hi": {"name": "Hindi", "flag": "🇮🇳", "tts_available": True},
    "th": {"name": "Thai", "flag": "🇹🇭", "tts_available": True},
    "vi": {"name": "Vietnamese", "flag": "🇻🇳", "tts_available": True},
    "id": {"name": "Indonesian", "flag": "🇮🇩", "tts_available": True},
    "ms": {"name": "Malay", "flag": "🇲🇾", "tts_available": True},
    "tl": {"name": "Filipino", "flag": "🇵🇭", "tts_available": True},
    
    # Nordic and Baltic
    "is": {"name": "Icelandic", "flag": "🇮🇸", "tts_available": False},
    
    # African languages
    "sw": {"name": "Swahili", "flag": "🇰🇪", "tts_available": False},
    "af": {"name": "Afrikaans", "flag": "🇿🇦", "tts_available": True},
    
    # American languages
    "pt-br": {"name": "Portuguese (Brazil)", "flag": "🇧🇷", "tts_available": True},
    "es-mx": {"name": "Spanish (Mexico)", "flag": "🇲🇽", "tts_available": True},
    
    # Other
    "uk": {"name": "Ukrainian", "flag": "🇺🇦", "tts_available": True},
    "be": {"name": "Belarusian", "flag": "🇧🇾", "tts_available": False},
    "ca": {"name": "Catalan", "flag": "🏴󠁥󠁳󠁣󠁴󠁿", "tts_available": True},
    "eu": {"name": "Basque", "flag": "🏴󠁥󠁳󠁰󠁶󠁿", "tts_available": False},
    "ga": {"name": "Irish", "flag": "🇮🇪", "tts_available": True},
    "cy": {"name": "Welsh", "flag": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "tts_available": True},
    "mt": {"name": "Maltese", "flag": "🇲🇹", "tts_available": False},
}

# Export formats for conversation sessions
EXPORT_FORMATS = {
    "json": {
        "name": "JSON",
        "extension": ".json",
        "description": "Machine-readable JSON format with full metadata"
    },
    "txt": {
        "name": "Plain Text",
        "extension": ".txt",
        "description": "Simple text format for easy reading"
    },
    "csv": {
        "name": "CSV",
        "extension": ".csv",
        "description": "Comma-separated values for spreadsheet import"
    },
    "html": {
        "name": "HTML",
        "extension": ".html",
        "description": "Web page format with styling"
    },
    "md": {
        "name": "Markdown",
        "extension": ".md",
        "description": "Markdown format for documentation"
    },
    "pdf": {
        "name": "PDF",
        "extension": ".pdf",
        "description": "Portable Document Format (requires reportlab)"
    }
}

# Audio Configuration
AUDIO_CONFIG = {
    "SAMPLE_RATE": 16000,
    "CHUNK_SIZE": 1024,
    "CHANNELS": 1,
    "FORMAT": "int16",
    "MAX_RECORDING_TIME": 30,  # seconds
    "SILENCE_THRESHOLD": 300,
    "PAUSE_THRESHOLD": 0.8,
}

# Recognition Engines
RECOGNITION_ENGINES = {
    "whisper": {
        "name": "OpenAI Whisper",
        "description": "High-quality offline speech recognition",
        "requires_internet": False,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "models": ["tiny", "base", "small", "medium", "large"]
    },
    "whisperx": {
        "name": "WhisperX",
        "description": "Enhanced Whisper with faster processing",
        "requires_internet": False,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "models": ["tiny", "base", "small", "medium", "large"]
    },
    "google": {
        "name": "Google Speech Recognition",
        "description": "Google's cloud-based speech recognition",
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "models": ["default"]
    },
    "azure": {
        "name": "Azure Speech Services",
        "description": "Microsoft's cloud speech recognition",
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "models": ["default"]
    }
}

# Translation Services
TRANSLATION_SERVICES = {
    "google": {
        "name": "Google Translate",
        "description": "Google's translation service",
        "requires_api_key": False,
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "rate_limit": "100/day (free)"
    },
    "libre": {
        "name": "LibreTranslate",
        "description": "Open-source translation service",
        "requires_api_key": False,
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "rate_limit": "5/minute (free)"
    },
    "azure": {
        "name": "Azure Translator",
        "description": "Microsoft's translation service",
        "requires_api_key": True,
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "rate_limit": "2M chars/month (free tier)"
    },
    "openai": {
        "name": "OpenAI GPT Translation",
        "description": "AI-powered contextual translation",
        "requires_api_key": True,
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "rate_limit": "Varies by plan"
    }
}

# Text-to-Speech Engines
TTS_ENGINES = {
    "pyttsx3": {
        "name": "PyTTSx3",
        "description": "Offline text-to-speech engine",
        "requires_internet": False,
        "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru"],
        "quality": "medium",
        "speed": "fast"
    },
    "gtts": {
        "name": "Google Text-to-Speech",
        "description": "Google's cloud TTS service",
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "quality": "high",
        "speed": "medium"
    },
    "azure": {
        "name": "Azure Speech Services",
        "description": "Microsoft's cloud TTS service",
        "requires_internet": True,
        "supported_languages": list(GAMING_LANGUAGES.keys()),
        "quality": "high",
        "speed": "fast"
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "description": "AI voice synthesis service",
        "requires_internet": True,
        "supported_languages": ["en", "es", "fr", "de", "it", "pt", "pl", "hi"],
        "quality": "very_high",
        "speed": "medium"
    }
}

# Default Hotkeys
DEFAULT_HOTKEYS = {
    "toggle_listening": "ctrl+l",
    "toggle_overlay": "ctrl+o",
    "translate_and_speak": "ctrl+t",
    "push_to_talk": "",
    "mute_toggle": "ctrl+m",
    "new_session": "ctrl+n",
    "save_session": "ctrl+s",
    "load_session": "ctrl+shift+o",
    "hide_overlay": "escape"
}

# File Paths and Directories
PATHS = {
    "USER_DATA_DIR": "~/.gaming_translator",
    "CONFIG_DIR": "~/.gaming_translator",
    "LOGS_DIR": "~/.gaming_translator/logs",
    "SESSIONS_DIR": "~/.gaming_translator/sessions",
    "CACHE_DIR": "~/.gaming_translator/cache",
    "MODELS_DIR": "~/.gaming_translator/models",
    "TEMP_DIR": "~/.gaming_translator/temp"
}

# Network Configuration
NETWORK_CONFIG = {
    "REQUEST_TIMEOUT": 10,  # seconds
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 1,  # seconds
    "USER_AGENT": f"{APP_NAME}/{APP_VERSION}",
    "LIBRE_TRANSLATE_URL": "https://libretranslate.de/translate",
    "BACKUP_LIBRE_URLS": [
        "https://translate.argosopentech.com/translate",
        "https://libretranslate.com/translate"
    ]
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "RECOGNITION_WARNING_TIME": 5.0,  # seconds
    "TRANSLATION_WARNING_TIME": 3.0,  # seconds
    "TTS_WARNING_TIME": 2.0,  # seconds
    "MAX_MEMORY_USAGE": 512,  # MB
    "MAX_CACHE_SIZE": 100,  # MB
}

# Gaming-specific Terms and Phrases
GAMING_PHRASES = {
    "common": [
        "gg", "good game", "well played", "nice shot", "push", "retreat",
        "help", "enemy spotted", "reloading", "cover me", "go go go",
        "behind you", "watch out", "on my way", "need backup", "clear",
        "let's go", "ready", "not ready", "wait", "stop", "follow me"
    ],
    "fps": [
        "headshot", "flanking", "camping", "rushing", "sniping", "spray",
        "burst fire", "scope", "knife", "grenade", "flashbang", "smoke",
        "reload", "ammo", "armor", "health", "medkit", "revive"
    ],
    "moba": [
        "gank", "ward", "jungle", "lane", "tower", "inhibitor", "baron",
        "dragon", "last hit", "farm", "carry", "support", "tank", "adc",
        "mid", "top", "bot", "recall", "teleport", "ultimate"
    ],
    "mmo": [
        "quest", "dungeon", "raid", "boss", "loot", "gear", "level up",
        "experience", "guild", "party", "heal", "tank", "dps", "buff",
        "debuff", "cooldown", "mana", "stamina", "inventory", "trade"
    ]
}

# Error Messages
ERROR_MESSAGES = {
    "NO_MICROPHONE": "No microphone detected. Please check your audio devices.",
    "RECOGNITION_FAILED": "Speech recognition failed. Please try again.",
    "TRANSLATION_FAILED": "Translation service unavailable. Check internet connection.",
    "TTS_FAILED": "Text-to-speech synthesis failed.",
    "CONFIG_LOAD_ERROR": "Failed to load configuration. Using defaults.",
    "CONFIG_SAVE_ERROR": "Failed to save configuration.",
    "SESSION_SAVE_ERROR": "Failed to save session.",
    "SESSION_LOAD_ERROR": "Failed to load session.",
    "EXPORT_ERROR": "Failed to export session.",
    "NETWORK_ERROR": "Network connection error.",
    "API_KEY_MISSING": "API key required for this service.",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded. Please wait before trying again.",
    "UNSUPPORTED_LANGUAGE": "Language not supported by selected service.",
    "AUDIO_DEVICE_ERROR": "Audio device error. Please check connections.",
    "DEPENDENCY_MISSING": "Required dependency missing. Check installation.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "SESSION_SAVED": "Session saved successfully.",
    "SESSION_LOADED": "Session loaded successfully.",
    "SESSION_EXPORTED": "Session exported successfully.",
    "CONFIG_SAVED": "Configuration saved successfully.",
    "CONFIG_RESET": "Configuration reset to defaults.",
    "LISTENING_STARTED": "Voice recognition started.",
    "LISTENING_STOPPED": "Voice recognition stopped.",
    "TRANSLATION_SUCCESS": "Translation completed.",
    "TTS_SUCCESS": "Text-to-speech completed.",
    "OVERLAY_SHOWN": "Game overlay activated.",
    "OVERLAY_HIDDEN": "Game overlay hidden.",
}

# Window and UI Configuration
UI_CONFIG = {
    "MIN_WINDOW_WIDTH": 800,
    "MIN_WINDOW_HEIGHT": 600,
    "DEFAULT_WINDOW_WIDTH": 900,
    "DEFAULT_WINDOW_HEIGHT": 700,
    "OVERLAY_MIN_WIDTH": 300,
    "OVERLAY_MIN_HEIGHT": 200,
    "OVERLAY_DEFAULT_WIDTH": 400,
    "OVERLAY_DEFAULT_HEIGHT": 300,
    "FONT_SIZES": {
        "small": 8,
        "normal": 10,
        "large": 12,
        "xlarge": 14,
        "title": 18
    },
    "MARGINS": {
        "small": 5,
        "normal": 10,
        "large": 15,
        "xlarge": 20
    }
}

# Session Configuration
SESSION_CONFIG = {
    "MAX_MESSAGES": 1000,
    "AUTO_SAVE_INTERVAL": 300,  # seconds
    "MESSAGE_FADE_TIME": 10,  # seconds for overlay
    "MAX_OVERLAY_MESSAGES": 5,
    "CONVERSATION_HISTORY_LIMIT": 100
}

# Cache Configuration
CACHE_CONFIG = {
    "TRANSLATION_CACHE_SIZE": 1000,
    "TTS_CACHE_SIZE": 100,
    "CACHE_EXPIRY_DAYS": 30,
    "ENABLE_DISK_CACHE": True,
    "CACHE_COMPRESSION": True
}

# Development and Debug
DEBUG_CONFIG = {
    "ENABLE_DEBUG_MODE": False,
    "LOG_AUDIO_LEVELS": False,
    "LOG_NETWORK_REQUESTS": False,
    "SAVE_RAW_AUDIO": False,
    "PERFORMANCE_MONITORING": True,
    "MEMORY_MONITORING": False
}

# Version Information
VERSION_INFO = {
    "MAJOR": 2,
    "MINOR": 0,
    "PATCH": 0,
    "BUILD": "stable",
    "RELEASE_DATE": "2024-12-19",
    "PYTHON_MIN_VERSION": "3.8",
    "PYTHON_RECOMMENDED": "3.11"
}

# Feature Flags
FEATURES = {
    "WHISPER_SUPPORT": True,
    "AZURE_SUPPORT": True,
    "LIBRE_TRANSLATE": True,
    "OVERLAY_SUPPORT": True,
    "HOTKEY_SUPPORT": True,
    "SESSION_EXPORT": True,
    "AUTO_LANGUAGE_DETECTION": True,
    "VOICE_ACTIVITY_DETECTION": True,
    "NOISE_SUPPRESSION": False,  # Experimental
    "ECHO_CANCELLATION": False,  # Experimental
    "REAL_TIME_TRANSLATION": True,
    "CONVERSATION_HISTORY": True
}