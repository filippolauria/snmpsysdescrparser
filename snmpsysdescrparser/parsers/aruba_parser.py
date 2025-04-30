"""
Parser implementation for Aruba Networks devices.
"""
import re
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser


class ArubaParser(DeviceParser):
    """Parser for Aruba Networks devices."""

    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.

        Args:
            raw (str): The raw sysDescr string to parse.
        """
        super().__init__(raw)

        # Device identifier constants
        self._vendor = "Aruba"

    def can_parse(self) -> bool:
        """Determine if the raw sysDescr string is from an Aruba device.

        Returns:
            bool: True if this parser can handle the string, False otherwise.
        """
        return self.raw.startswith(self._vendor)

    def parse(self) -> DeviceInfo:
        """Parse the raw sysDescr string from an Aruba device.

        Returns:
            DeviceInfo: A DeviceInfo object with extracted information.
        """
        device = DeviceInfo(self.raw)
        device.vendor = self._vendor

        # Extract model information
        self._extract_model_info(device)

        # Extract firmware version information
        self._extract_firmware_version(device)

        # Extract ROM version if present
        self._extract_rom_version(device)

        # Extract product line and additional info
        self._extract_additional_info(device)

        return device

    def _extract_model_info(self, device: DeviceInfo) -> None:
        """Extract model information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract part number (e.g., "JL256A")
        part_number_match = re.search(r'Aruba\s+([A-Z0-9]+)', self.raw)
        if part_number_match:
            device.set_attr("part_number", part_number_match.group(1))

        # Extract full model (e.g., "2930F-48G-PoE+-4SFP+")
        model_match = re.search(r'([0-9]+[A-Za-z0-9\-+]+)\s+Switch', self.raw)
        if model_match:
            device.model = model_match.group(1)

            # Set hardware type based on the explicit mention of "Switch"
            device.set_attr("hardware_type", "Switch")

    def _extract_firmware_version(self, device: DeviceInfo) -> None:
        """Extract firmware version from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract firmware version (e.g., "WC.16.11.0004")
        firmware_match = re.search(r'revision\s+([A-Z]+\.[0-9.]+)', self.raw)
        if firmware_match:
            device.version = firmware_match.group(1)
            device.os = "ArubaOS-Switch"

    def _extract_rom_version(self, device: DeviceInfo) -> None:
        """Extract ROM version if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract ROM version (e.g., "WC.16.01.0010")
        rom_match = re.search(r'ROM\s+([A-Z]+\.[0-9.]+)', self.raw)
        if rom_match:
            device.set_attr("rom_version", rom_match.group(1))

    def _extract_additional_info(self, device: DeviceInfo) -> None:
        """Extract additional information if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Add product series if it can be directly extracted from the model
        if device.model:
            # Extract the series prefix (e.g., "2930F" from "2930F-48G-PoE+-4SFP+")
            series_match = re.search(r'^([0-9]+[A-Za-z]+)', device.model)
            if series_match:
                device.set_attr("series", series_match.group(1))

            # Check if it's explicitly mentioned as PoE capable
            if "PoE" in device.model:
                device.set_attr("poe_capable", True)
