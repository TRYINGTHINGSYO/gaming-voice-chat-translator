"""
Configuration management for the Gaming Voice Chat Translator
Handles loading, saving, and managing application settings
"""

import os
import configparser
import logging
from pathlib import Path
from typing import Any, Optional


class Config:
    """Configuration manager for the Gaming Voice Chat Translator"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration manager
        
        Args:
            config_file: Optional path to config file. If None, uses default location.
        """
        self.logger = logging.getLogger("gaming_translator.utils.config")
        
        # Determine config file location
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Default config location
            config_dir = Path.home() / ".gaming_translator"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = config_dir / "config.ini"
        
        # Initialize ConfigParser
        self.config = configparser.ConfigParser()
        
        # Set up default configuration
        self._setup_defaults()
        
        # Load existing config if it exists
        self.load()
        
        # Add GPU detection
        self.has_gpu = self._detect_gpu()
        
        self.logger.info(f"Configuration initialized: {self.config_file}")
    
    def _detect_gpu(self) -> bool:
        """Detect if CUDA-capable GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def _setup_defaults(self):
        """Set up default configuration values"""
        # UI Settings
        self.config["ui"] = {
            "window_size": "900x700",
            "theme": "dark",
            "font_size": "10",
            "always_on_top": "false",
            "minimize_to_tray": "true"
        }
        
        # Audio Settings
        self.config["audio"] = {
            "input_volume": "0.8",
            "output_volume": "0.7",
            "input_device": "",
            "output_device": "",
            "noise_suppression": "true",
            "echo_cancellation": "true"
        }
        
        # Recognition Settings
        self.config["recognition"] = {
            "engine": "whisper",  # whisper, google, azure, etc.
            "model_size": "base",  # tiny, base, small, medium, large
            "language": "auto",
            "device_index": "",
            "sample_rate": "16000",
            "chunk_duration": "1.0",
            "energy_threshold": "300",
            "dynamic_energy_threshold": "true",
            "pause_threshold": "0.8",
            "timeout": "5.0"
        }
        
        # Translation Settings
        self.config["translation"] = {
            "service": "google",  # google, libre, azure, etc.
            "my_language": "en",
            "target_language": "es",
            "auto_detect": "true",
            "cache_translations": "true",
            "api_key": "",
            "custom_endpoint": ""
        }
        
        # TTS Settings
        self.config["tts"] = {
            "engine": "pyttsx3",  # pyttsx3, gtts, azure, etc.
            "voice": "default",
            "rate": "150",
            "volume": "0.8",
            "language": "auto"
        }
        
        # Session Settings
        self.config["session"] = {
            "auto_save": "true",
            "save_interval": "300",  # seconds
            "max_history": "100",
            "export_format": "json",
            "save_session_on_exit": "true"
        }
        
        # Overlay Settings
        self.config["overlay"] = {
            "enabled": "false",
            "position_x": "100",
            "position_y": "100",
            "width": "400",
            "height": "300",
            "opacity": "0.9",
            "auto_hide": "false",
            "hide_delay": "5.0"
        }
        
        # Hotkeys Settings
        self.config["hotkeys"] = {
            "toggle_listening": "ctrl+l",
            "toggle_overlay": "ctrl+o",
            "translate_and_speak": "ctrl+t",
            "push_to_talk": "",
            "mute_toggle": "ctrl+m"
        }
        
        # Logging Settings
        self.config["logging"] = {
            "level": "INFO",
            "file_logging": "true",
            "console_logging": "true",
            "max_log_size": "10485760",  # 10MB
            "backup_count": "5"
        }
        
        # First run flag
        self.config["internal"] = {
            "first_run": "true",
            "version": "2.0.0",
            "last_updated": ""
        }
    
    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                self.logger.info("Using default configuration")
        else:
            self.logger.info("No existing config found, using defaults")
    
    def save(self):
        """Save configuration to file"""
        try:
            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """Get configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Default value if key not found
            
        Returns:
            Configuration value as string
        """
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get configuration value as boolean
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Default value if key not found
            
        Returns:
            Configuration value as boolean
        """
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get configuration value as integer
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Default value if key not found
            
        Returns:
            Configuration value as integer
        """
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get configuration value as float
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Default value if key not found
            
        Returns:
            Configuration value as float
        """
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
    
    def remove(self, section: str, key: Optional[str] = None):
        """Remove configuration section or key
        
        Args:
            section: Configuration section
            key: Configuration key (if None, removes entire section)
        """
        if key is None:
            # Remove entire section
            if self.config.has_section(section):
                self.config.remove_section(section)
        else:
            # Remove specific key
            if self.config.has_section(section):
                self.config.remove_option(section, key)
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config.clear()
        self._setup_defaults()
        self.logger.info("Configuration reset to defaults")
    
    def is_first_run(self) -> bool:
        """Check if this is the first run of the application"""
        return self.get_bool("internal", "first_run", True)
    
    def mark_first_run_complete(self):
        """Mark the first run as complete"""
        self.set("internal", "first_run", "false")
        from datetime import datetime
        self.set("internal", "last_updated", datetime.now().isoformat())
        self.save()
    
    def get_section(self, section: str) -> dict:
        """Get all values from a configuration section
        
        Args:
            section: Configuration section name
            
        Returns:
            Dictionary of key-value pairs from the section
        """
        if self.config.has_section(section):
            return dict(self.config.items(section))
        return {}
    
    def has_section(self, section: str) -> bool:
        """Check if configuration section exists
        
        Args:
            section: Configuration section name
            
        Returns:
            True if section exists, False otherwise
        """
        return self.config.has_section(section)
    
    def has_option(self, section: str, key: str) -> bool:
        """Check if configuration option exists
        
        Args:
            section: Configuration section name
            key: Configuration key
            
        Returns:
            True if option exists, False otherwise
        """
        return self.config.has_option(section, key)
    
    def update_from_dict(self, config_dict: dict):
        """Update configuration from dictionary
        
        Args:
            config_dict: Dictionary with section->key->value structure
        """
        for section, values in config_dict.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            for key, value in values.items():
                self.config.set(section, key, str(value))
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary
        
        Returns:
            Dictionary representation of configuration
        """
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config.items(section))
        return result
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"Config(file={self.config_file}, sections={list(self.config.sections())})"
    
    def __repr__(self) -> str:
        """Detailed string representation of configuration"""
        return self.__str__()
    
    def get_backend_config(self, backend_type: str):
        """Get configuration for a specific backend
        
        Args:
            backend_type: Type of backend (recognition, translation, tts)
            
        Returns:
            Backend type string or configuration dictionary
        """
        # For compatibility with existing code that expects strings
        if backend_type == "recognition":
            return self.get("recognition", "engine", "google")
        elif backend_type == "translation":
            return self.get("translation", "service", "google")
        elif backend_type == "tts":
            return self.get("tts", "engine", "pyttsx3")
        else:
            # Return full section for other types
            return self.get_section(backend_type)
    
    def get_recognition_config(self) -> dict:
        """Get voice recognition configuration"""
        return self.get_backend_config("recognition")
    
    def get_translation_config(self) -> dict:
        """Get translation configuration"""
        return self.get_backend_config("translation")
    
    def get_tts_config(self) -> dict:
        """Get text-to-speech configuration"""
        return self.get_backend_config("tts")
    
    def get_audio_config(self) -> dict:
        """Get audio configuration"""
        return self.get_backend_config("audio")
    
    def get_session_config(self) -> dict:
        """Get session configuration"""
        return self.get_backend_config("session")
    
    def get_overlay_config(self) -> dict:
        """Get overlay configuration"""
        return self.get_backend_config("overlay")
    
    def get_hotkeys_config(self) -> dict:
        """Get hotkeys configuration"""
        return self.get_backend_config("hotkeys")


# Convenience function for creating a global config instance
_global_config = None

def get_config(config_file: Optional[Path] = None) -> Config:
    """Get global configuration instance
    
    Args:
        config_file: Optional path to config file
        
    Returns:
        Global Config instance
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(config_file)
    return _global_config


def reset_global_config():
    """Reset the global configuration instance"""
    global _global_config
    _global_config = None