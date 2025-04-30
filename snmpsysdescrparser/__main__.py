#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for the SNMP sysDescr Parser.
This module allows the parser to be run from the command line.

Usage:
    python -m snmpsysdescrparser "SNMP sysDescr string"

Example:
    python -m snmpsysdescrparser "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107, ROM R.10.06"
    python -m snmpsysdescrparser --verbose "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107"
    python -m snmpsysdescrparser --log-level debug "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107"
"""

import sys
import json
import argparse
from typing import List

from snmpsysdescrparser.factory import DeviceParserFactory
from snmpsysdescrparser.core.log import set_level, LOG_LEVELS


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Parse SNMP sysDescr strings from network devices."
    )

    # Add verbosity options
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity (sets log level to DEBUG)"
    )
    verbosity_group.add_argument(
        "--log-level",
        choices=list(LOG_LEVELS.keys()),
        default="none",  # Default to disabled logging
        help="Set the logging level (default: none - logging disabled)"
    )

    # Main operation modes
    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument(
        "sysdescr",
        nargs="?",
        help="SNMP sysDescr string to parse"
    )
    operation_group.add_argument(
        "--list-parsers",
        action="store_true",
        help="List all available parsers"
    )
    operation_group.add_argument(
        "--test",
        action="store_true",
        help="Run tests with example strings"
    )

    # Output format options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    return parser.parse_args()


def main() -> None:
    """
    Main function for the command-line interface.

    Parses a sysDescr string provided as a command-line argument.
    """
    args = parse_args()

    # Set verbosity level
    if args.verbose:
        set_level("debug")
    else:
        set_level(args.log_level)

    # Handle different operation modes
    if args.list_parsers:
        parsers = DeviceParserFactory.get_available_parsers()
        print(f"Available parsers ({len(parsers)}):")
        for parser in parsers:
            print(f" - {parser}")
        return

    if args.test:
        test()
        return

    if not args.sysdescr:
        print("Error: No sysDescr string provided", file=sys.stderr)
        print("Usage: python -m snmpsysdescrparser \"SNMP sysDescr string\"", file=sys.stderr)
        sys.exit(1)

    try:
        device_info = DeviceParserFactory.parse(args.sysdescr)
        if args.json:
            print(json.dumps(device_info.dict(), indent=2))
        else:
            print("\nParsed Device Information:")
            print(f"Vendor:  {device_info.vendor}")
            print(f"Model:   {device_info.model}")
            print(f"OS:      {device_info.os}")
            print(f"Version: {device_info.version}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def test() -> None:
    """Test function with example sysDescr strings."""
    test_strings: List[str] = [
        "ProCurve J9087A Switch 2610-24-PWR, revision R.11.107, ROM R.10.06 (/sw/code/build/nemo)",
        "Ruckus Wireless, Inc. ICX7250-48, IronWare Version 08.0.90kT213 Compiled on Feb 23 2021 at 00:02:43 labeled as SPR08090k",
        (
            "Juniper Networks, Inc. ex4200-24t Ethernet Switch, kernel JUNOS 15.1R7.9, "
            "Build date: 2018-09-11 05:57:13 UTC Copyright (c) 1996-2018 Juniper Networks, Inc."
        ),
        (
            "Juniper Networks, Inc. ex4300-48p Ethernet Switch, kernel JUNOS 19.1R3-S5.3, "
            "Build date: 2021-03-24 12:08:04 UTC Copyright (c) 1996-2021 Juniper Networks, Inc."
        ),
        (
            "Juniper Networks, Inc. ex4600-40f Ethernet Switch, kernel JUNOS 19.1R3-S5.3, "
            "Build date: 2021-03-24 12:06:39 UTC Copyright (c) 1996-2021 Juniper Networks, Inc."
        ),
        "RouterOS CCR1009-8G-1S-1S+",
        "Palo Alto Networks PA-5400f series firewall",
        "\n".join([
            "Cisco IOS Software [Dublin], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.12.4, RELEASE SOFTWARE (fc3)",
            "Technical Support: http://www.cisco.com/techsupport",
            "Copyright (c) 1986-2024 by Cisco Systems, Inc.",
            "Compiled Tue 23-Jul-24 09:40 by mcpre"
        ]),
        "Aruba JL256A 2930F-48G-PoE+-4SFP+ Switch, revision WC.16.11.0004, ROM WC.16.01.0010",
    ]

    print("Testing SNMP sysDescr parser with example strings...")
    print("-" * 60)

    for raw_str in test_strings:
        print(f"INPUT: {raw_str[:60]}...")
        try:
            device_info = DeviceParserFactory.parse(raw_str)
            print(f"OUTPUT: {json.dumps(device_info.dict(), indent=2)}")
        except ValueError as e:
            print(f"ERROR: {e}")
        print("-" * 60)


if __name__ == "__main__":
    main()
