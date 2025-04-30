# SNMP sysDescr Parser

A Python library for parsing SNMP sysDescr strings from various network devices.

## Overview

This library provides a robust, extensible framework for parsing SNMP sysDescr strings from network devices. It extracts structured information such as vendor, model, operating system, and version from raw sysDescr strings.

The parser uses the [Factory pattern](https://en.wikipedia.org/wiki/Factory_method_pattern) to automatically select the appropriate parser for each device type.

## Supported Devices

Currently, the following device types are supported:

- Aruba switches
- HP ProCurve switches
- Juniper Networks switches (EX series)
- MikroTik RouterOS devices
- Palo Alto Networks firewalls
- Ruckus ICX switches

## Installation (dev)

```bash
apt install git virtualenv
git clone https://github.com/filippolauria/snmpsysdescrparser
cd snmpsysdescrparser
virtualenv env
source env/bin/activate
pip install -r requirements-dev.txt
pip install -e ".[dev]"
```

## Usage

### Basic usage

```python
from snmpsysdescrparser import DeviceParserFactory

# Example sysDescr string
sysdescr = "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107, ROM R.10.06 (/sw/code/build/nemo)"

# Parse the string
device_info = DeviceParserFactory.parse(sysdescr)

# Access structured data
print(f"Vendor: {device_info.vendor}")
print(f"Model: {device_info.model}")
print(f"OS: {device_info.os}")
print(f"Version: {device_info.version}")

# Get as dictionary
info_dict = device_info.dict()
print(info_dict)
```

### Command-line usage

The package can be used directly from the command line with various options:

```bash
# Basic usage: parse a single string
snmpsysdescrparser "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107, ROM R.10.06"

# Output in JSON format
snmpsysdescrparser --json "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107"

# Increase verbosity (sets log level to DEBUG)
snmpsysdescrparser --verbose "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107"

# Set specific log level
snmpsysdescrparser --log-level debug "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107"

# List all available parsers
snmpsysdescrparser --list-parsers

# Run test mode with example strings
snmpsysdescrparser --test
```

Alternative usage through the Python module:

```bash
# Using the module directly
python -m snmpsysdescrparser "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107"

# Run test mode with example strings
python -m snmpsysdescrparser --test
```

For help on all available options:

```bash
snmpsysdescrparser --help
```

## Extending

You can add support for new device types by creating a new parser class following these rules:

1. Create a file named `vendor_parser.py` in the `parsers` directory (replace "vendor" with your vendor name in lowercase)
2. Implement a class named `VendorParser` (with capitalized vendor name) that extends `DeviceParser`
3. Implement the required methods: `can_parse()` and `parse()`
4. The class will be automatically discovered and used by the factory

Here's an example of how to implement a new parser:

```python
from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser

class VendorParser(DeviceParser):
    """Parser for Vendor."""
    
    def __init__(self, raw: str):
        """Initialize the parser with the raw sysDescr string.
        
        Args:
            raw: The raw sysDescr string to parse
        """
        super().__init__(raw)

        # Specific constants
        self._vendor = "Vendor's Name"
        self._os = "Vendor's OS"
        # ...
    
    def can_parse(self) -> bool:
        """
        Determine if this parser can handle the string.
        Must be implemented as a method that takes no parameter and returns a boolean value.
        """

        # e.g.
        return self.raw.startswith(self._vendor)
    
    def parse(self) -> DeviceInfo:
        """
        Parse the raw sysDescr string.
        Must return a DeviceInfo object with extracted information.
        """
        device = DeviceInfo(self.raw)
        device.vendor = self._vendor
        device.os = self._os
        
        # Extract model and version with regex
        # ...
        
        return device
```

### Implementation Requirements

For a parser to be correctly discovered and loaded:

1. The filename must follow the pattern `vendor_parser.py`
2. The class name is detected automatically:
   - First attempt: `VendorParser` (capitalized vendor name, **preferred**)
   - Second attempt: `VENDORParser` (uppercase vendor name)
3. The class must extend the `DeviceParser` abstract base class
4. The class must implement:
   - A `can_parse` instance method that takes no parameters (except `self`) and returns a boolean value
   - A `parse` instance method that takes no parameters (except `self`) and returns a `DeviceInfo` object
5. Optionally, you can override the `__init__` constructor to initialize vendor-specific constants or perform other setup, but make sure to call `super().__init__(raw)` to properly initialize the base class

The system performs strict validation of these requirements and will automatically discover and load all properly implemented parsers without any need for explicit registration.

## License

This project is licensed under the MIT License - see the LICENSE file for details.