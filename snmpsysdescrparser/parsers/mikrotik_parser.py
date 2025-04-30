"""
Parser implementation for MikroTik devices.
"""
import re
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser


class MikrotikParser(DeviceParser):
    """Parser for MikroTik devices."""

    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.

        Args:
            raw (str): The raw sysDescr string to parse.
        """
        super().__init__(raw)
        # Device identifier constants
        self._vendor = "MikroTik"
        self._os = "RouterOS"

    def can_parse(self) -> bool:
        """Determine if the raw sysDescr string is from a MikroTik device.

        Returns:
            bool: True if this parser can handle the string, False otherwise.
        """
        return self.raw.startswith(self._os)

    def parse(self) -> DeviceInfo:
        """Parse the raw sysDescr string from a MikroTik device.

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

        # Extract additional information if present
        self._extract_additional_info(device)

        return device

    def _extract_model(self, device: DeviceInfo) -> None:
        """Extract model information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Basic pattern for extracting model after RouterOS
        model_match = re.search(f'^{self._os}\\s+([\\w-]+)', self.raw)
        if model_match:
            device.model = model_match.group(1)

            # If it's a known model pattern, also extract the hardware type
            self._determine_hardware_type(device)

    def _extract_version(self, device: DeviceInfo) -> None:
        """Extract version information if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Look for version after model like "RouterOS CCR1009-8G-1S-1S+ v6.47.9"
        version_match = re.search(r'(?:(?:version\s+)|v)((?:\d+\.)+\d+)', self.raw)
        if version_match:
            device.version = version_match.group(1)

    def _determine_hardware_type(self, device: DeviceInfo) -> None:
        """Determine hardware type if directly indicated in the model string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Only use information that is directly derivable from the model string
        if device.model:
            # CCR is explicitly "Cloud Core Router" from the model name
            # hEX is explicitly a type of router from the model name
            if device.model.startswith("CCR") or "hEX" in device.model:
                device.set_attr("hardware_type", "Router")
            # CRS is explicitly "Cloud Router Switch" from the model name
            elif device.model.startswith("CRS"):
                device.set_attr("hardware_type", "Switch")
            # RB is explicitly "RouterBoard" from the model name
            elif device.model.startswith("RB"):
                device.set_attr("hardware_type", "RouterBoard")

    def _extract_additional_info(self, device: DeviceInfo) -> None:
        """Extract any additional information explicitly stated in the sysDescr.

        Args:
            device: The DeviceInfo object to populate
        """
        # Sometimes serial numbers are included after "sn" or similar
        serial_match = re.search(r'(?:sn|serial)[: ]+([a-z0-9]+)', self.raw, re.IGNORECASE)
        if serial_match:
            device.set_attr("serial", serial_match.group(1))

        # Architecture might be mentioned
        arch_match = re.search(r'(?:mipsbe|tile|arm|x86|powerpc)', self.raw, re.IGNORECASE)
        if arch_match:
            device.set_attr("architecture", arch_match.group(0))
