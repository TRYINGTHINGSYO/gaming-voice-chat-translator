"""
Logging setup and configuration for the Gaming Voice Chat Translator
Provides centralized logging configuration with file and console output
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console_logging: bool = True,
    file_logging: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """Setup application logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default location
        console_logging: Enable console output
        file_logging: Enable file output
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    
    # Create root logger
    root_logger = logging.getLogger("gaming_translator")
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if file_logging:
        if log_file is None:
            # Default log file location
            log_dir = Path.home() / ".gaming_translator" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "gaming_translator.log"
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set logging level for third-party libraries to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger("gaming_translator.logger")
    logger.info("=" * 50)
    logger.info("Gaming Voice Chat Translator - Logging Started")
    logger.info(f"Log Level: {logging.getLevelName(log_level)}")
    if file_logging and log_file:
        logger.info(f"Log File: {log_file}")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info("=" * 50)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"gaming_translator.{name}")


def log_exception(logger: logging.Logger, message: str = "An exception occurred"):
    """Log an exception with full traceback
    
    Args:
        logger: Logger instance
        message: Custom message to include
    """
    logger.exception(message)


def log_performance(logger: logging.Logger, operation: str, duration: float):
    """Log performance timing information
    
    Args:
        logger: Logger instance
        operation: Description of the operation
        duration: Duration in seconds
    """
    if duration > 1.0:
        logger.warning(f"Slow operation: {operation} took {duration:.2f}s")
    else:
        logger.debug(f"Performance: {operation} took {duration:.3f}s")


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            log_performance(self.logger, self.operation, duration)


def setup_debug_logging():
    """Setup debug-level logging for development"""
    setup_logging(
        log_level=logging.DEBUG,
        console_logging=True,
        file_logging=True
    )


def setup_production_logging():
    """Setup production-level logging"""
    setup_logging(
        log_level=logging.INFO,
        console_logging=False,
        file_logging=True
    )


def disable_logging():
    """Disable all logging (for testing)"""
    logging.disable(logging.CRITICAL)


def enable_logging():
    """Re-enable logging after disabling"""
    logging.disable(logging.NOTSET)


# Custom log levels
TRACE = 5
logging.addLevelName(TRACE, "TRACE")

def trace(self, message, *args, **kwargs):
    """Log a message with severity 'TRACE'"""
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)

# Add trace method to Logger class
logging.Logger.trace = trace