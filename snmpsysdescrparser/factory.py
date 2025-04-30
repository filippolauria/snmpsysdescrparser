"""
Factory implementation for SNMP sysDescr parser selection with dynamic parser discovery.
"""

from typing import List, Type, ClassVar

from snmpsysdescrparser.core.device import DeviceInfo, DeviceParser
from snmpsysdescrparser.core.utils import discover_parsers
from snmpsysdescrparser.core.log import get_logger

# Get module logger
logger = get_logger("factory")


class DeviceParserFactory:
    """Factory for creating the appropriate parser based on the sysDescr string."""

    # Registry of available parsers (will be populated dynamically)
    _parsers: ClassVar[List[Type[DeviceParser]]] = []

    # Flag to track if parsers have been loaded
    _parsers_loaded: ClassVar[bool] = False

    @classmethod
    def _load_parsers(cls) -> None:
        """Load all available parsers from the parsers package."""
        if cls._parsers_loaded:
            return

        logger.info("Loading parsers dynamically...")

        # First try to access _parser_classes directly from the parsers module
        try:
            from snmpsysdescrparser import parsers
            if hasattr(parsers, '_parser_classes'):
                cls._parsers = parsers._parser_classes
                logger.info(f"Loaded {len(cls._parsers)} parsers from parsers._parser_classes")
            else:
                logger.info("No _parser_classes attribute found, using discover_parsers()")
                cls._parsers = discover_parsers("snmpsysdescrparser.parsers")

        except (ImportError, AttributeError) as e:
            logger.warning(f"Error importing parsers module: {e}, using discover_parsers()")
            cls._parsers = discover_parsers("snmpsysdescrparser.parsers")

        cls._parsers_loaded = True
        logger.info(f"Total parsers loaded: {len(cls._parsers)}")

        # Log the loaded parsers
        for parser in cls._parsers:
            logger.debug(f"  - {parser.__name__}")

    @classmethod
    def register_parser(cls, parser_class: Type[DeviceParser]) -> None:
        """Register a new parser to the factory.

        Args:
            parser_class (Type[DeviceParser]): Parser class to register.
        """
        # Ensure parsers are loaded
        cls._load_parsers()

        if parser_class not in cls._parsers:
            cls._parsers.append(parser_class)
            logger.info(f"Registered parser: {parser_class.__name__}")

    @classmethod
    def get_parser(cls, sysDescr: str) -> DeviceParser:
        """Return an appropriate parser for the given string.

        Args:
            sysDescr (str): The raw sysDescr string to parse.

        Returns:
            DeviceParser: An instance of the appropriate parser.

        Raises:
            ValueError: If no parser is available for the given string.
        """
        # Ensure parsers are loaded
        cls._load_parsers()

        # Try each parser
        for parser_class in cls._parsers:
            try:
                logger.debug(f"Trying parser: {parser_class.__name__}")
                parser_obj = parser_class(sysDescr)
                if parser_obj.can_parse():
                    logger.info(f"Parser '{parser_class.__name__}' can parse the string")
                    return parser_obj
            except Exception as e:
                logger.error(f"In '{parser_class.__name__}', 'can_parse' has an error: {e}")

        # No parser found for this string
        raise ValueError(f"No parser available for '{sysDescr}'")

    @classmethod
    def parse(cls, sysDescr: str) -> DeviceInfo:
        """Directly parse the string using the appropriate parser.

        Args:
            sysDescr (str): The raw sysDescr string to parse.

        Returns:
            DeviceInfo: A DeviceInfo object with extracted information.

        Raises:
            ValueError: If no parser is available for the given string.
        """
        return cls.get_parser(sysDescr).parse()

    @classmethod
    def get_available_parsers(cls) -> List[str]:
        """Get a list of names of all available parsers.

        Returns:
            List[str]: List of parser class names
        """
        # Ensure parsers are loaded
        cls._load_parsers()
        return [parser.__name__ for parser in cls._parsers]
