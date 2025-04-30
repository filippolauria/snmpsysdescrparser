"""
Parser implementation for HP ProCurve devices.
"""
import re
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser


class HPParser(DeviceParser):
    """Parser for HP ProCurve devices."""

    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.

        Args:
            raw (str): The raw sysDescr string to parse.
        """
        super().__init__(raw)

        # Device identifier constants
        self._vendor = "HP"
        self._os = "ProCurve"
        self._family = "ProCurve"  # Family name used in can_parse

    def can_parse(self) -> bool:
        """Determine if this string is from an HP device.

        Returns:
            bool: True if this parser can handle the string, False otherwise.
        """
        return self.raw.startswith(self._family) or f"{self._vendor} {self._family}" in self.raw

    def parse(self) -> DeviceInfo:
        """Parse the raw sysDescr string from an HP device.

        Returns:
            DeviceInfo: A DeviceInfo object with extracted information.
        """
        device = DeviceInfo(self.raw)
        device.vendor = self._vendor
        device.os = self._os

        # Extract model information
        self._extract_model_info(device)

        # Extract version information
        self._extract_version_info(device)

        # Extract ROM version if present
        self._extract_rom_version(device)

        # Extract build information if present
        self._extract_build_info(device)

        return device

    def _extract_model_info(self, device: DeviceInfo) -> None:
        """Extract model information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract full model string (e.g., "ProCurve J9087A Switch 2610-24-PWR")
        model_match = re.search(r'(ProCurve\s+[A-Za-z0-9\-]+\s+Switch\s+[A-Za-z0-9\-]+)', self.raw)
        if model_match:
            device.model = model_match.group(1)

            # Extract part number if directly specified
            part_number_match = re.search(r'ProCurve\s+([A-Z0-9]+)', self.raw)
            if part_number_match:
                device.set_attr("part_number", part_number_match.group(1))

            # Extract model number if directly specified
            model_number_match = re.search(r'Switch\s+([A-Za-z0-9\-]+)', self.raw)
            if model_number_match:
                device.set_attr("model_number", model_number_match.group(1))

    def _extract_version_info(self, device: DeviceInfo) -> None:
        """Extract version information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract firmware version (e.g., "R.11.107")
        version_match = re.search(r'revision\s+([A-Z]\.[0-9\.]+)', self.raw)
        if version_match:
            device.version = version_match.group(1)

    def _extract_rom_version(self, device: DeviceInfo) -> None:
        """Extract ROM version if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        rom_match = re.search(r'ROM\s+([A-Z]\.[0-9\.]+)', self.raw)
        if rom_match:
            device.set_attr("rom_version", rom_match.group(1))

    def _extract_build_info(self, device: DeviceInfo) -> None:
        """Extract build information if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        build_match = re.search(r'\(\/sw\/code\/build\/(.*?)\)', self.raw)
        if build_match:
            device.set_attr("build_id", build_match.group(1))
