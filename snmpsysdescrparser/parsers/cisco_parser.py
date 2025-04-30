"""
Parser implementation for Cisco devices.
"""
import re
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser


class CiscoParser(DeviceParser):
    """Parser for Cisco devices."""

    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.

        Args:
            raw: The raw sysDescr string to parse
        """
        super().__init__(raw)

        # Specific constants
        self._vendor = "Cisco"
        self._os = "IOS"

    def can_parse(self) -> bool:
        """
        Determine if this parser can handle the string.
        Must be implemented as a method that takes no parameter and returns a boolean value.
        """
        return "Cisco" in self.raw

    def parse(self) -> DeviceInfo:
        """
        Parse the raw sysDescr string.
        Must return a DeviceInfo object with extracted information.
        """
        device = DeviceInfo(self.raw)

        # Set core attributes
        device.vendor = self._vendor

        # Determine OS variant and set device.os
        self._determine_os_variant(device)

        # Extract software platform if present
        self._extract_software_platform(device)

        # Extract hardware type if present
        self._extract_hardware_info(device)

        # Extract version information if present
        self._extract_version_info(device)

        # Extract build information if present
        self._extract_build_info(device)

        # Extract additional metadata if present
        self._extract_metadata(device)

        return device

    def _determine_os_variant(self, device: DeviceInfo) -> None:
        """Determine the OS variant based on the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        if "IOS-XE" in self.raw or "IOSXE" in self.raw:
            device.os = "IOS-XE"
        elif "NX-OS" in self.raw:
            device.os = "NX-OS"
        else:
            device.os = self._os

    def _extract_software_platform(self, device: DeviceInfo) -> None:
        """Extract software platform information if present.

        Args:
            device: The DeviceInfo object to populate
        """
        software_match = re.search(r'\((CAT[A-Z0-9]+_([A-Z0-9]+))\)', self.raw)
        if software_match:
            sw_platform = software_match.group(1)
            sw_type = software_match.group(2)
            device.set_attr("software_platform", sw_platform)
            device.set_attr("software_type", sw_type)

    def _extract_hardware_info(self, device: DeviceInfo) -> None:
        """Extract hardware information if explicitly stated.

        Args:
            device: The DeviceInfo object to populate
        """
        # Set hardware type based on explicit mention
        if "Switch" in self.raw:
            device.set_attr("hardware_type", "Switch")

            # Try to extract switch model if present
            # But avoid capturing "L3" or other descriptors that aren't actual models
            if "Catalyst" in self.raw:
                # Look for model numbers that contain digits after "Catalyst"
                series_match = re.search(r'Catalyst\s+(\d+[A-Za-z0-9\-\/]+)', self.raw)
                if series_match:
                    device.model = series_match.group(1)
                # Don't set model if we only find descriptors like "L3" without numbers

        elif "Router" in self.raw:
            device.set_attr("hardware_type", "Router")
            # Try to extract router model if present
            router_match = re.search(r'((?:I|A|C)SR\s+\d+)', self.raw)
            if router_match:
                device.model = router_match.group(1)

        elif "Firewall" in self.raw:
            device.set_attr("hardware_type", "Firewall")

    def _extract_version_info(self, device: DeviceInfo) -> None:
        """Extract version information if present.

        Args:
            device: The DeviceInfo object to populate
        """
        version_match = re.search(r'Version\s+(\d+\.\d+\.\d+(?:\w+)?)', self.raw)
        if version_match:
            device.version = version_match.group(1)

        # Capture release type if explicitly mentioned
        release_match = re.search(r'(RELEASE SOFTWARE|DEVELOPMENT TEST SOFTWARE|ENGINEERING RELEASE)', self.raw)
        if release_match:
            device.set_attr("release_type", release_match.group(1))

    def _extract_build_info(self, device: DeviceInfo) -> None:
        """Extract build information if present.

        Args:
            device: The DeviceInfo object to populate
        """
        build_match = re.search(r'Compiled\s+(.*?\d+:\d+)(?:\s+by\s+(\w+))?', self.raw)
        if build_match:
            build_date = build_match.group(1).strip()
            compiler = build_match.group(2) if build_match.group(2) else ""

            device.set_attr("build_date", build_date)

            # Add compiler as separate attribute if present
            if compiler:
                device.set_attr("compiled_by", compiler)

    def _extract_metadata(self, device: DeviceInfo) -> None:
        """Extract additional metadata if explicitly stated.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract copyright information if present
        copyright_match = re.search(r'Copyright\s+\(c\)\s+(.*?)(?:\n|Compiled)', self.raw, re.DOTALL)
        if copyright_match:
            copyright_info = copyright_match.group(1).strip()
            device.set_attr("copyright", copyright_info)

        # Extract technical support URL if present
        support_match = re.search(r'Technical Support:\s+(http[s]?://[^\s]+)', self.raw)
        if support_match:
            device.set_attr("support_url", support_match.group(1))

        # Extract product family if explicitly mentioned in brackets
        if "[" in self.raw and "]" in self.raw:
            family_match = re.search(r'\[(.*?)\]', self.raw)
            if family_match:
                device.set_attr("product_family", family_match.group(1))
