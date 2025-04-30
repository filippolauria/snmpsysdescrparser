"""
Parser implementation for Ruckus Wireless devices.
"""
import re
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser


class RuckusParser(DeviceParser):
    """Parser for Ruckus Wireless devices."""

    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.

        Args:
            raw (str): The raw sysDescr string to parse.
        """
        super().__init__(raw)
        # Device identifier constants
        self._vendor = "Ruckus Wireless"
        self._os = "IronWare"
        self._family = "ICX"

    def can_parse(self) -> bool:
        """Determine if the raw sysDescr string is from a Ruckus device.

        Returns:
            bool: True if this parser can handle the string, False otherwise.
        """
        return self.raw.startswith(self._vendor) or "Ruckus" in self.raw

    def parse(self) -> DeviceInfo:
        """Parse the raw sysDescr string from a Ruckus device.

        Returns:
            DeviceInfo: A DeviceInfo object with extracted information.
        """
        device = DeviceInfo(self.raw)
        device.vendor = self._vendor

        # Extract model information
        self._extract_model(device)

        # Extract OS and version information
        self._extract_os_and_version(device)

        # Extract build information
        self._extract_build_info(device)

        return device

    def _extract_model(self, device: DeviceInfo) -> None:
        """Extract model information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract full model number (e.g., "ICX7250-48")
        model_match = re.search(r'(ICX[\w-]+)', self.raw)
        if model_match:
            device.model = model_match.group(1)

            # Extract model number for additional information
            if "-" in device.model:
                # Store base model and specific variant
                parts = device.model.split("-")
                if len(parts) >= 1:
                    device.set_attr("base_model", parts[0])
                if len(parts) >= 2:
                    device.set_attr("model_variant", parts[1])

    def _extract_os_and_version(self, device: DeviceInfo) -> None:
        """Extract OS and version information from the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Check for IronWare OS
        if self._os in self.raw:
            device.os = self._os

            # Extract version using pattern
            version_match = re.search(r'IronWare\s+Version\s+([\w.]+)', self.raw)
            if version_match:
                device.version = version_match.group(1)

                # Extract label information if present
                label_match = re.search(r'labeled\s+as\s+(\w+)', self.raw)
                if label_match:
                    device.set_attr("version_label", label_match.group(1))

    def _extract_build_info(self, device: DeviceInfo) -> None:
        """Extract build information if present in the sysDescr string.

        Args:
            device: The DeviceInfo object to populate
        """
        # Extract build date and time if present
        build_match = re.search(r'Compiled\s+on\s+([\w ]+)\s+at\s+([\d:]+)', self.raw)
        if build_match:
            build_date = build_match.group(1)
            build_time = build_match.group(2)
            device.set_attr("build_date", build_date)
            device.set_attr("build_time", build_time)
            device.set_attr("build_datetime", f"{build_date} {build_time}")
