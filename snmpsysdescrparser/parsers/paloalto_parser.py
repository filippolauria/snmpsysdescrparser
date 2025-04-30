"""
Parser implementation for Palo Alto Networks devices.
"""
import re
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser


class PaloaltoParser(DeviceParser):
    """Parser for Palo Alto Networks devices."""

    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.

        Args:
            raw (str): The raw sysDescr string to parse.
        """
        super().__init__(raw)
        # Device identifier constants
        self._vendor = "Palo Alto Networks"
        self._os = "PANOS"

    def can_parse(self) -> bool:
        """Determine if the raw sysDescr string is from a Palo Alto Networks device.

        Returns:
            bool: True if this parser can handle the string, False otherwise.
        """
        return self._vendor in self.raw

    def parse(self) -> DeviceInfo:
        """Parse the raw sysDescr string from a Palo Alto Networks device.

        Returns:
            DeviceInfo: A DeviceInfo object with extracted information.
        """
        device = DeviceInfo(self.raw)
        device.vendor = self._vendor
        device.os = self._os

        # Extract model information
        self._extract_model(device)

        # Extract version if present
        self._extract_version(device)

        # Extract additional information directly from the sysDescr
        self._extract_additional_info(device)

        return device

    def _extract_model(self, device: DeviceInfo) -> None:
        """Extract model information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """

        # Generic pattern for Palo Alto devices
        m = re.search(r'^Palo\s+Alto\s+Networks\s+([A-Za-z0-9-]+)', self.raw)
        if m:
            device.model = m.group(1)

    def _extract_version(self, device: DeviceInfo) -> None:
        """Extract version information if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Look for version in various formats
        version_match = re.search(r'(?:version|PANOS)\s+((?:\d+\.)+\d+)', self.raw, re.IGNORECASE)
        if version_match:
            device.version = version_match.group(1)

    def _extract_additional_info(self, device: DeviceInfo) -> None:
        """Extract any additional information directly stated in the sysDescr.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract hardware type if explicitly mentioned
        if "firewall" in self.raw.lower():
            device.set_attr("hardware_type", "Firewall")
        elif "panorama" in self.raw.lower():
            device.set_attr("hardware_type", "Management")

        # Check if it's explicitly mentioned as virtual
        if "vm-series" in self.raw.lower() or "vm series" in self.raw.lower():
            device.set_attr("is_virtual", True)

        # Extract serial number if present
        serial_match = re.search(r'serial\s+(\w+)', self.raw, re.IGNORECASE)
        if serial_match:
            device.set_attr("serial", serial_match.group(1))

        # Extract hostname if present
        hostname_match = re.search(r'hostname\s+(\S+)', self.raw, re.IGNORECASE)
        if hostname_match:
            device.set_attr("hostname", hostname_match.group(1))
