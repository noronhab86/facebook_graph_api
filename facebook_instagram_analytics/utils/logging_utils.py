"""
Logging utilities for Facebook Instagram Analytics.
Provides structured logging configuration.
"""

import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from facebook_instagram_analytics.config import LOG_LEVEL, LOG_FILE

# Define log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Define log colors for console output
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[41m',  # Red background
    'RESET': '\033[0m'       # Reset color
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to the log level names in console output."""
    
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)


def get_logger(name, log_file=LOG_FILE, log_level=LOG_LEVEL):
    """
    Configure and return a logger with the given name.
    
    Args:
        name (str): Logger name (typically the module name)
        log_file (str): Path to the log file
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Convert log level string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Avoid adding handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create rotating file handler (10 MB max size, 5 backup files)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


class LogPerformance:
    """Context manager to log the execution time of a code block."""
    
    def __init__(self, logger, operation_name):
        self.logger = logger
        self.operation_name = operation_name
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        if exc_type:
            self.logger.error(
                f"{self.operation_name} failed after {execution_time:.2f} seconds: {exc_val}"
            )
        else:
            self.logger.debug(
                f"Completed {self.operation_name} in {execution_time:.2f} seconds"
            )
