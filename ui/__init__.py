"""
User Interface package for Gaming Voice Chat Translator
Contains the main window, overlay, and other UI components
"""

# Import main UI components for easy access
try:
    from .main_window import GamingTranslatorApp
    
    __all__ = [
        "GamingTranslatorApp"
    ]
    
except ImportError:
    # Allow package to be imported even if some modules are missing
    __all__ = []