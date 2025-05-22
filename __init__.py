"""
Gaming Voice Chat Translator Package
A real-time voice translator for gaming with support for multiple languages
"""

__version__ = "2.0.0"
__author__ = "Gaming Translator Team"
__description__ = "Real-time voice translator for gaming"

# Package metadata
__all__ = [
    "Config",
    "GamingTranslatorApp",
    "__version__",
    "__author__",
    "__description__"
]

# Import main components for easy access
try:
    from gaming_translator.utils.config import Config
    from gaming_translator.ui.main_window import GamingTranslatorApp
except ImportError:
    # Allow package to be imported even if dependencies are missing
    # This is useful for setup.py and other installation scripts
    Config = None
    GamingTranslatorApp = None


def get_version():
    """Get the current version of the package"""
    return __version__


def main():
    """Main entry point for the application"""
    try:
        from gaming_translator.__main__ import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error importing main application: {e}")
        print("Please ensure all dependencies are installed.")
        return 1
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())