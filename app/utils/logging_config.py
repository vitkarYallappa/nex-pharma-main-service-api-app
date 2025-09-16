"""
Simple logging configuration for FastAPI application.
Basic file logging with timestamp, filename, and method.
"""
import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional

from app.config.settings import settings


class SimpleFormatter(logging.Formatter):
    """Simple formatter with just timestamp, filename, and method."""
    
    def format(self, record):
        # Get just the filename without path
        filename = os.path.basename(record.pathname)
        
        # Format: timestamp | filename:line | method | level | message
        formatted = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {filename}:{record.lineno} | {record.funcName} | {record.levelname} | {record.getMessage()}"
        
        return formatted


class NoiseFilter(logging.Filter):
    """Filter out noisy log messages."""
    
    def filter(self, record):
        # Filter out file watcher spam
        if record.funcName == '_log_changes':
            return False
        
        # Filter out other noisy messages
        message = record.getMessage()
        if 'change detected' in message.lower():
            return False
        if 'watchdog' in message.lower():
            return False
        if record.name.startswith('watchfiles'):
            return False
        
        return True


def setup_logging() -> None:
    """Configure simple logging for the application."""
    # Create logs directory if it doesn't exist
    os.makedirs(settings.log_dir, exist_ok=True)
    
    # Create simple formatter
    formatter = SimpleFormatter()
    
    # Create noise filter
    noise_filter = NoiseFilter()
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.effective_log_level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.effective_log_level))
    console_handler.setFormatter(formatter)
    console_handler.addFilter(noise_filter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(settings.log_dir, 'app.log'),
        maxBytes=settings.log_max_file_size_mb * 1024 * 1024,
        backupCount=settings.log_max_backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, settings.effective_log_level))
    file_handler.setFormatter(formatter)
    file_handler.addFilter(noise_filter)
    root_logger.addHandler(file_handler)
    
    # Configure third-party loggers to be less noisy
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)
    
    # Disable file watcher and other noisy loggers
    logging.getLogger('watchfiles').setLevel(logging.WARNING)
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    logging.getLogger('filelock').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name) 