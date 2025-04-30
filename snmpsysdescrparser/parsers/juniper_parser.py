"""
Parser implementation for Juniper Networks devices.
"""
import re
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser


class JuniperParser(DeviceParser):
    """Parser for Juniper Networks devices."""

    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.

        Args:
            raw (str): The raw sysDescr string to parse.
        """
        super().__init__(raw)
        # Device identifier constants
        self._vendor = "Juniper Networks"
        self._os = "JUNOS"

    def can_parse(self) -> bool:
        """Determine if the raw sysDescr string is from a Juniper device.

        Returns:
            bool: True if this parser can handle the string, False otherwise.
        """
        return self.raw.startswith(self._vendor)

    def parse(self) -> DeviceInfo:
        """Parse the raw sysDescr string from a Juniper device.

        Returns:
            DeviceInfo: A DeviceInfo object with extracted information.
        """
        device = DeviceInfo(self.raw)
        device.vendor = self._vendor
        device.os = self._os

        # Extract model and version information
        self._extract_model_and_version(device)

        # Extract build date if present
        self._extract_build_date(device)

        # Extract copyright information if present
        self._extract_copyright(device)

        # Extract hardware type if specified
        self._extract_hardware_type(device)

        return device

    def _extract_model_and_version(self, device: DeviceInfo) -> None:
        """Extract model and version information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Pattern for EX series switches
        ex_pattern = r'(\w+\d+(?:-\d+\w+))\s+Ethernet\s+Switch,\s+kernel\s+JUNOS\s+([\d.RS-]+)'
        ex_match = re.search(ex_pattern, self.raw, re.IGNORECASE)

        if ex_match:
            device.model = ex_match.group(1)
            device.version = ex_match.group(2)
            return

        # More generic pattern for other Juniper devices
        generic_pattern = r'(\w+[-\d\w]+)[,\s]+kernel\s+JUNOS\s+([\d.RS-]+)'
        generic_match = re.search(generic_pattern, self.raw)

        if generic_match:
            device.model = generic_match.group(1)
            device.version = generic_match.group(2)

    def _extract_build_date(self, device: DeviceInfo) -> None:
        """Extract build date information if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        build_match = re.search(r'Build date:\s+([-\d]+\s+[:.\d]+\s+\w+)', self.raw)
        if build_match:
            device.set_attr("build_date", build_match.group(1))

    def _extract_copyright(self, device: DeviceInfo) -> None:
        """Extract copyright information if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        copyright_match = re.search(r'Copyright\s+\(c\)\s+(.*?)(?:$|,)', self.raw)
        if copyright_match:
            device.set_attr("copyright", copyright_match.group(1).strip())

    def _extract_hardware_type(self, device: DeviceInfo) -> None:
        """Extract hardware type if explicitly stated in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        if "Ethernet Switch" in self.raw:
            device.set_attr("hardware_type", "Switch")
        elif "Router" in self.raw:
            device.set_attr("hardware_type", "Router")
        elif "Firewall" in self.raw:
            device.set_attr("hardware_type", "Firewall")
