"""
Device-specific parsers for SNMP sysDescr strings.
Dynamic discovery of all available parsers.
"""

from pathlib import Path
import importlib

from snmpsysdescrparser.core.device import DeviceParser
from snmpsysdescrparser.core.utils import get_parser_class_from_module, validate_parser_class
from snmpsysdescrparser.core.log import get_logger

# Get module logger
logger = get_logger("parsers")

# Get the directory where this file is located
_current_dir = Path(__file__).parent.absolute()

# Get all Python files in the directory that match the naming convention
_parser_files = [f.stem for f in _current_dir.glob('*_parser.py')]
logger.info(f"Found {len(_parser_files)} parser files: {', '.join(_parser_files)}")

# List to store the discovered parser classes
_parser_classes = []
__all__ = []

# Import each parser module and add its parser class to the list
for module_name in _parser_files:
    try:
        # Convert filename to module name (e.g., 'hp_parser' -> 'snmpsysdescrparser.parsers.hp_parser')
        full_module_name = f"snmpsysdescrparser.parsers.{module_name}"
        logger.debug(f"Importing module: {full_module_name}")

        # Import the module
        module = importlib.import_module(full_module_name)

        # Get the class from the module
        parser_class = get_parser_class_from_module(module)

        if not parser_class:
            logger.warning(f"{module_name} has no parser class.")
            continue

        # Validate the parser class
        valid, error_msg = validate_parser_class(parser_class)
        if not valid:
            logger.warning(f"Invalid parser class in {module_name}: {error_msg}")
            continue

        # If all checks pass, add the class to the list
        class_name = parser_class.__name__
        _parser_classes.append(parser_class)
        __all__.append(class_name)

        # Make the class available at the package level
        globals()[class_name] = parser_class
        logger.info(f"Successfully loaded parser: {class_name}")

    except (ImportError, AttributeError) as e:
        # Just skip any modules that can't be imported properly
        logger.error(f"Failed to import parser from {module_name}: {e}")
    except Exception as e:
        logger.exception(f"Error loading parser {module_name}: {e}")

# Log information about loaded parsers
if _parser_classes:
    logger.info(f"Loaded {len(_parser_classes)} parsers: {', '.join(__all__)}")
else:
    logger.warning("No parsers were loaded!")
