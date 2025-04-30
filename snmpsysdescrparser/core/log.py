"""
Logging configuration for SNMP sysDescr Parser.
"""
import logging
import sys
from typing import Dict, Optional

# Mapping from string log levels to numeric values
LOG_LEVELS: Dict[str, int] = {
    "none": logging.CRITICAL + 10,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Root logger for the package
ROOT_LOGGER_NAME = "snmpsysdescrparser"


def setup_logger(level: str) -> logging.Logger:
    """
    Set up logging configuration for the package.

    Args:
        level: The minimum logging level
              Can be an integer level, a string ('debug', 'info', etc.),
              or 'none' to disable logging (default)

    Returns:
        logging.Logger: Configured logger
    """
    # Convert string level to numeric level if needed

    level = level.strip().lower()
    if level in LOG_LEVELS:
        level = LOG_LEVELS[level]
    else:
        valid_levels = ", ".join(LOG_LEVELS.keys())
        raise ValueError(f"Invalid log level: {level}. Valid levels are: {valid_levels}")

    # Create the logger for the package
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    logger.setLevel(level)

    # Only add handlers if none exist to avoid duplicate loggers
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)
    else:
        # Update existing handlers
        for handler in logger.handlers:
            handler.setLevel(level)

    return logger


def get_logger(suffix: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the package prefix.

    Args:
        suffix: The name suffix for the logger (optional)

    Returns:
        Logger: A configured logger
    """
    prefix = ROOT_LOGGER_NAME
    logger_name = prefix if not suffix else f"{prefix}.{suffix}"
    return logging.getLogger(logger_name)


# Create a default logger with logging disabled
logger = setup_logger("none")


def set_level(level: str) -> None:
    """
    Set the logging level for all package loggers.

    Args:
        level: The minimum logging level
              Can be an integer level, a string ('debug', 'info', etc.),
              or 'none' to disable logging
    """
    setup_logger(level)
