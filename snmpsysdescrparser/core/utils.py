"""
Utility functions for parser discovery and validation.

This module contains shared utility functions for discovering,
validating and loading parser classes.
"""

import importlib
import inspect
from pathlib import Path
from typing import Any, List, Tuple, Type
from types import ModuleType

from snmpsysdescrparser.core.device import DeviceParser


def validate_can_parse_method(parser_class) -> Tuple[bool, str]:
    """
    Validate the 'can_parse' method of a parser class.

    Args:
        parser_class: The parser class to validate.

    Returns:
        tuple: (bool, str) - Success flag and error message (if any).
    """
    can_parse_str = "can_parse"
    class_name = parser_class.__name__

    # Check if the class has a 'can_parse' class method
    if not hasattr(parser_class, can_parse_str):
        return False, f"In '{class_name}', '{can_parse_str}' method is not implemented."

    # Check if 'can_parse' is a class method (or staticmethod)
    can_parse_method = getattr(parser_class, can_parse_str)

    # Check if 'can_parse' is callable
    if not callable(can_parse_method):
        return False, f"In '{class_name}', '{can_parse_str}' method must be callable."

    # Get the signature of the 'can_parse' method
    try:
        can_parse_sig = inspect.signature(can_parse_method)
    except ValueError:
        return False, f"In '{class_name}', '{can_parse_str}' method signature cannot be inspected."

    # Check parameter count
    param_count = len(can_parse_sig.parameters)
    if param_count != 1:
        return False, f"In '{class_name}', '{can_parse_str}' method should have no parameter (other than 'self')."

    # Get the return annotation
    return_annotation = can_parse_sig.return_annotation

    # Check if the return annotation is bool or absent
    if return_annotation != inspect.Signature.empty and return_annotation != bool:
        return False, f"In '{class_name}', '{can_parse_str}' method should return a bool value."

    return True, ""


def validate_parse_method(parser_class) -> Tuple[bool, str]:
    """
    Validate the 'parse' method of a parser class.

    Args:
        parser_class: The parser class to validate.

    Returns:
        tuple: (bool, str) - Success flag and error message (if any).
    """
    parse_str = "parse"
    class_name = parser_class.__name__

    # Check if the class has a 'parse' method
    if not hasattr(parser_class, parse_str):
        return False, f"In '{class_name}', '{parse_str}' method is not implemented."

    parse_method = getattr(parser_class, parse_str)

    # Check if 'parse' is callable
    if not callable(parse_method):
        return False, f"In '{class_name}', '{parse_str}' method must be callable."

    try:
        parse_sig = inspect.signature(parse_method)
    except ValueError:
        return False, f"In '{class_name}', '{parse_str}' method signature cannot be inspected."

    # Check if it has the correct parameters (at least self and raw_str)
    param_count = len(parse_sig.parameters)
    if param_count != 1:
        return False, f"In '{class_name}', '{parse_str}' method should have no parameter (other than 'self')."

    # Check return annotation for parse method
    parse_return = parse_sig.return_annotation

    if parse_return == inspect.Signature.empty:
        # No return annotation is provided, we'll be permissive here
        pass
    else:
        # Get the name attribute safely using getattr with a default
        return_name = getattr(parse_return, '__name__', str(parse_return))
        if return_name != 'DeviceInfo':
            return False, f"In '{class_name}', '{parse_str}' method should return a DeviceInfo object."

    return True, ""


def validate_parser_class(parser_class) -> Tuple[bool, str]:
    """
    Validate a parser class against all requirements.

    Args:
        parser_class: The parser class to validate.

    Returns:
        tuple: (bool, str) - Success flag and error message (if any).
    """
    # Check if it's a class and subclass of DeviceParser
    if not inspect.isclass(parser_class):
        return False, f"'{parser_class}' is not a class."

    if not issubclass(parser_class, DeviceParser):
        return False, f"'{parser_class.__name__}' should be a subclass of DeviceParser."

    if parser_class == DeviceParser:
        return False, f"'{parser_class.__name__}' is the abstract base class, not a specific parser."

    # Validate required methods
    validators = [validate_can_parse_method, validate_parse_method]
    for validator in validators:
        valid, error_msg = validator(parser_class)
        if not valid:
            return False, error_msg

    return True, ""


def get_parser_class_from_module(module: ModuleType) -> Any:
    """
    Extract the parser class from a module based on naming conventions.

    Args:
        module: The module to extract the parser class from.

    Returns:
        The parser class if found, None otherwise.
    """
    # Get the module name from the module object
    module_name = module.__name__.split('.')[-1]

    # Detect the parser class name from the module name
    vendor = module_name.split('_')[0]

    # Try different transformations to get the class name
    possible_vendors = [vendor.capitalize(), vendor.upper()]
    for possible_vendor in possible_vendors:
        class_name = f"{possible_vendor}Parser"
        if hasattr(module, class_name):
            return getattr(module, class_name)
    return None


def discover_parsers(package_path: str) -> List[Type[DeviceParser]]:
    """
    Discover all parser classes in a package directory.

    Args:
        package_path: The import path to the package containing parsers.

    Returns:
        List of discovered parser classes.
    """
    discovered_parsers = []

    try:
        # Import the package
        package = importlib.import_module(package_path)

        # Get the directory of the package
        package_dir = Path(package.__file__).parent.absolute()

        # Find all parser modules
        parser_files = [f.stem for f in package_dir.glob('*_parser.py')]

        # Process each parser file
        for module_name in parser_files:
            try:
                # Import the module
                full_module_name = f"{package_path}.{module_name}"
                module = importlib.import_module(full_module_name)

                # Get the parser class
                parser_class = get_parser_class_from_module(module)

                if not parser_class:
                    print(f"Warning: No parser class found in '{module_name}'")
                    continue

                # Validate the parser class
                valid, error_msg = validate_parser_class(parser_class)
                if not valid:
                    print(f"Warning: {error_msg}")
                    continue

                # Add to discovered parsers
                discovered_parsers.append(parser_class)

            except (ImportError, AttributeError) as e:
                print(f"Warning: Failed to import parser from '{module_name}': {e}")
            except Exception as e:
                print(f"Error processing {module_name}: {e}")

    except Exception as e:
        print(f"Error discovering parsers: {e}")

    return discovered_parsers
