from abc import ABC, abstractmethod
from typing import Dict, Any


"""
Device information model for SNMP sysDescr parsing.
"""


class DeviceInfo:
    """Base class for storing device information extracted from SNMP sysDescr strings.

    This class provides a structured representation of network device information
    extracted from SNMP sysDescr strings, including vendor, model, operating system,
    and version information.
    """
    def __init__(self, raw: str):
        """Initialize a new DeviceInfo object.

        Args:
            raw (str): The original raw sysDescr string
        """
        # Dictionary to store all attributes (both core and vendor-specific)
        self._attrs: Dict[str, Any] = {
            "raw": raw  # Original sysDescr string is always stored
        }

    @property
    def raw(self) -> str:
        """Get the raw sysDescr string.

        Returns:
            str: The original raw sysDescr string
        """
        return self._attrs["raw"]

    @property
    def vendor(self) -> str:
        """Get the device vendor name.

        Returns:
            str: The device vendor name
        """
        return self._attrs.get("vendor", "")

    @vendor.setter
    def vendor(self, value: str) -> None:
        """Set the device vendor name.

        Args:
            value (str): The device vendor name
        """
        self._attrs["vendor"] = value

    @property
    def model(self) -> str:
        """Get the device model.

        Returns:
            str: The device model
        """
        return self._attrs.get("model", "")

    @model.setter
    def model(self, value: str) -> None:
        """Set the device model.

        Args:
            value (str): The device model
        """
        self._attrs["model"] = value

    @property
    def os(self) -> str:
        """Get the operating system name.

        Returns:
            str: The operating system name
        """
        return self._attrs.get("os", "")

    @os.setter
    def os(self, value: str) -> None:
        """Set the operating system name.

        Args:
            value (str): The operating system name
        """
        self._attrs["os"] = value

    @property
    def version(self) -> str:
        """Get the OS/firmware version.

        Returns:
            str: The OS/firmware version
        """
        return self._attrs.get("version", "")

    @version.setter
    def version(self, value: str) -> None:
        """Set the OS/firmware version.

        Args:
            value (str): The OS/firmware version
        """
        self._attrs["version"] = value

    def set_attr(self, key: str, value: Any) -> None:
        """Set any attribute (core or vendor-specific).

        Args:
            key (str): The attribute name
            value (Any): The attribute value
        """
        self._attrs[key] = value

    def get_attr(self, key: str, default: Any = None) -> Any:
        """Get any attribute (core or vendor-specific).

        Args:
            key (str): The attribute name
            default (Any, optional): Default value if attribute doesn't exist

        Returns:
            Any: The attribute value or default if not found
        """
        return self._attrs.get(key, default)

    def __str__(self) -> str:
        """Return a string representation of the device information.

        Returns:
            str: Formatted device information
        """
        # Core attributes first
        result = (f"Vendor: {self.vendor}\n"
                  f"Model: {self.model}\n"
                  f"OS: {self.os}\n"
                  f"Version: {self.version}\n")

        # Then any other attributes (excluding core and raw)
        core_attrs = {"vendor", "model", "os", "version", "raw"}
        for key, value in sorted(self._attrs.items()):
            if key not in core_attrs:
                result += f"{key}: {value}\n"

        # Raw string at the end
        result += f"Raw: {self.raw}"
        return result

    def dict(self) -> Dict[str, Any]:
        """Convert device information to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing all device information.
        """
        return self._attrs.copy()


"""
Base abstract parser for SNMP sysDescr strings.
This module defines the abstract base class for all device-specific parsers,
establishing the interface that must be implemented by all concrete parsers.
"""


class DeviceParser(ABC):
    """Abstract base class for device-specific parsers.

    This class defines the interface that all device-specific parsers must implement.
    Concrete parser implementations should inherit from this class and provide
    implementations for the abstract methods.
    """
    def __init__(self, raw: str):
        """Initialize the parser with a raw sysDescr string.

        Args:
            raw (str): The raw sysDescr string to parse.
        """
        self.raw = raw

    @abstractmethod
    def parse(self) -> DeviceInfo:
        """Parse a raw sysDescr string and extract structured device information.

        Returns:
            DeviceInfo: A DeviceInfo object with extracted information.
        """
        pass

    @abstractmethod
    def can_parse(self) -> bool:
        """Determine if this parser can handle the given string.

        This method should quickly check if the given string appears to be from
        a device type that this parser can handle.

        Returns:
            bool: True if this parser can handle the string, False otherwise.
        """
        pass
