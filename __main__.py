#!/usr/bin/env python3
"""
Entry point for the Gaming Voice Chat Translator application.
This file allows the application to be run as a module with:
python -m gaming_translator
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from gaming_translator.utils.config import Config
from gaming_translator.utils.logger import setup_logging
from gaming_translator.ui.main_window import GamingTranslatorApp


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Gaming Voice Chat Translator - Real-time voice translation for gaming",
        prog="gaming_translator"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (default: auto-detect)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (default: logs/gaming_translator.log)"
    )
    
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset configuration to defaults"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Gaming Voice Chat Translator v2.0.0"
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check for required and optional dependencies"""
    print("Checking dependencies...")
    
    required_deps = [
        ("tkinter", "tkinter", "GUI framework (usually included with Python)"),
        ("pyaudio", "pyaudio", "Audio input/output"),
        ("speech_recognition", "speech_recognition", "Speech recognition"),
        ("googletrans", "googletrans", "Translation service"),
        ("pyttsx3", "pyttsx3", "Text-to-speech")
    ]
    
    optional_deps = [
        ("whisperx", "whisperx", "Advanced speech recognition (optional)"),
        ("pygame", "pygame", "Audio playback for GTTS (optional)"),
        ("gtts", "gtts", "Google Text-to-Speech (optional)"),
        ("reportlab", "reportlab", "PDF export (optional)"),
        ("requests", "requests", "HTTP requests for LibreTranslate (optional)")
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required dependencies
    print("\nRequired dependencies:")
    for name, import_name, description in required_deps:
        try:
            __import__(import_name)
            print(f"  ✓ {name} - {description}")
        except ImportError:
            print(f"  ✗ {name} - {description}")
            missing_required.append((name, import_name, description))
    
    # Check optional dependencies
    print("\nOptional dependencies:")
    for name, import_name, description in optional_deps:
        try:
            __import__(import_name)
            print(f"  ✓ {name} - {description}")
        except ImportError:
            print(f"  ✗ {name} - {description}")
            missing_optional.append((name, import_name, description))
    
    # Report results
    if missing_required:
        print(f"\n❌ Missing {len(missing_required)} required dependencies:")
        for name, _, description in missing_required:
            print(f"  - {name}: {description}")
        
        print("\nInstall required dependencies with:")
        print("pip install pyaudio speechrecognition googletrans==4.0.0-rc1 pyttsx3")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing {len(missing_optional)} optional dependencies:")
        for name, _, description in missing_optional:
            print(f"  - {name}: {description}")
        
        print("\nInstall optional dependencies with:")
        print("pip install pygame gtts reportlab requests")
        print("pip install git+https://github.com/m-bain/whisperx.git")
    
    print(f"\n✅ All required dependencies are installed!")
    if not missing_optional:
        print("✅ All optional dependencies are also installed!")
    
    return True


def setup_application_logging(args):
    """Setup application logging based on arguments"""
    log_level = getattr(logging, args.log_level.upper())
    
    # Determine log file path
    if args.log_file:
        log_file = Path(args.log_file)
    else:
        # Default log file location
        log_dir = Path.home() / ".gaming_translator" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "gaming_translator.log"
    
    # Setup logging
    setup_logging(log_level, log_file)
    
    logger = logging.getLogger("gaming_translator.main")
    logger.info(f"Gaming Voice Chat Translator starting...")
    logger.info(f"Log level: {args.log_level}")
    logger.info(f"Log file: {log_file}")
    
    return logger


def load_configuration(args, logger):
    """Load application configuration"""
    try:
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                logger.error(f"Configuration file not found: {config_path}")
                sys.exit(1)
            config = Config(config_path)
        else:
            # Use default config location
            config = Config()
        
        # Reset config if requested
        if args.reset_config:
            logger.info("Resetting configuration to defaults...")
            config.reset_to_defaults()
            config.save()
            print("Configuration reset to defaults.")
        
        logger.info(f"Configuration loaded from: {config.config_file}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        print(f"Error: Failed to load configuration: {e}")
        sys.exit(1)


def main():
    """Main entry point for the application"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Check dependencies if requested
        if args.check_deps:
            success = check_dependencies()
            sys.exit(0 if success else 1)
        
        # Setup logging
        logger = setup_application_logging(args)
        
        # Load configuration
        config = load_configuration(args, logger)
        
        # Check dependencies before starting GUI
        logger.info("Checking required dependencies...")
        try:
            import tkinter
            import pyaudio
            import speech_recognition
            import googletrans
            import pyttsx3
        except ImportError as e:
            logger.error(f"Missing required dependency: {e}")
            print(f"Error: Missing required dependency: {e}")
            print("Run with --check-deps to see all missing dependencies.")
            sys.exit(1)
        
        # Create and start the application
        logger.info("Creating application instance...")
        app = GamingTranslatorApp(config)
        
        logger.info("Starting application GUI...")
        app.start()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        if 'logger' in locals():
            logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()