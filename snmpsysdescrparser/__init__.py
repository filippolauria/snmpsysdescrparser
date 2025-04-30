"""
SNMP sysDescr Parser - A library for parsing SNMP sysDescr information from various network devices.

This package provides a set of tools to parse and extract structured information from
SNMP sysDescr strings for different network devices.
"""

import importlib.metadata

from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser
from snmpsysdescrparser.factory import DeviceParserFactory
from snmpsysdescrparser.core.log import setup_logger, get_logger, set_level

# Get version from package metadata
try:
    __version__ = importlib.metadata.version("snmpsysdescrparser")
except importlib.metadata.PackageNotFoundError:
    # Package is not installed, use a default version
    __version__ = "0.0.0"

__all__ = ["DeviceInfo", "DeviceParser", "DeviceParserFactory", "setup_logger", "get_logger", "set_log_level"]

# Setup default logger with logging disabled
logger = get_logger()


def set_log_level(level: str) -> None:
    """
    Set the logging level for the package.

    This is a convenience function that allows users to set the logging level
    without having to import the log module directly.

    Args:
        level: The logging level to set ('debug', 'info', 'warning', 'error', 'critical', 'none').

    Example:
        >>> import snmpsysdescrparser
        >>> snmpsysdescrparser.set_log_level("debug")  # Enable debug logging
        >>> snmpsysdescrparser.set_log_level("none")   # Disable logging
    """
    set_level(level)
    logger = get_logger()
    if level != "none" and level > 0:  # Don't log if logging is disabled
        logger.info(f"Log level set to: {level}")
