"""
Utilities package for Gaming Voice Chat Translator
Contains configuration, logging, and other utility modules
"""

# Import main utilities for easy access
try:
    from .config import Config
    from .logger import setup_logging, get_logger
    from .constants import (
        APP_NAME, APP_VERSION, UI_COLORS, GAMING_LANGUAGES, 
        EXPORT_FORMATS, ERROR_MESSAGES, SUCCESS_MESSAGES
    )
    
    __all__ = [
        "Config",
        "setup_logging", 
        "get_logger",
        "APP_NAME",
        "APP_VERSION", 
        "UI_COLORS",
        "GAMING_LANGUAGES",
        "EXPORT_FORMATS",
        "ERROR_MESSAGES",
        "SUCCESS_MESSAGES"
    ]
    
except ImportError:
    # Allow package to be imported even if some modules are missing
    __all__ = []