"""
Simple tracing/logging module for BinaryOptionsTools V1
Compatible with BinaryOptionsToolsV2.tracing interface
"""
import logging
import os
from datetime import datetime


def start_logs(log_dir: str = "logs", log_level: str = "INFO"):
    """
    Initialize logging configuration
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup file handler
    log_filename = os.path.join(log_dir, f"trading_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Setup specific loggers
    loggers = [
        "PocketOption",
        "PocketOptionAsync", 
        "BinaryOptionsTools",
        "SatoreBotAPI"
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    logging.info(f"Logging initialized - Level: {log_level}, Log file: {log_filename}")


def get_logger(name: str = None):
    """Get a logger instance"""
    return logging.getLogger(name or "BinaryOptionsTools")
