from __future__ import annotations

from logging import getLogger
from typing import Dict, Optional, TextIO

from defusedxml import ElementTree

_logger = getLogger(__name__)


class Querier:
    """
    A Querier is a helper for extracting data from a filing XML file. It
    provides helper methods for getting typed data using XPaths.

    >>> querier = Querier.from_path("fixtures/filing.xml")
    >>> querier.find_str("/IRS990/FormationYr")
    '2004'
    >>> querier.find_int("/IRS990/TotalEmployeeCnt")
    19
    """

    _namespaces: Dict[str, str]

    _tree: ElementTree

    @staticmethod
    def from_path(xml_path: str) -> Querier:
        """
        A factory primarily intended for testing and interactive (REPL or
        Jupyter) use.
        """
        _logger.debug(f"create querier for '{xml_path}'")
        with open(xml_path) as xml_file:
            return Querier.from_file(xml_file)

    @staticmethod
    def from_file(xml_file: TextIO) -> Querier:
        """
        The standard factory which accepts a file-like object.
        """
        content = xml_file.read()

        # The XML files seem to come back with some kind of unicode identifier
        # sequence at the beginning and Python's XML processing barfs on it. So
        # here we strip it off to make sure that "<" (opening bracket for the
        # doctype) is the first character.
        while not content.startswith("<"):
            content = content[1:]

        byte_content = content.encode("utf-8")
        _logger.debug(f"hydrate querier: '{str(byte_content[:40])}'")

        tree = ElementTree.fromstring(byte_content)

        return Querier(tree)

    def __init__(self, tree: ElementTree):
        self._namespaces = {
            "efile": "http://www.irs.gov/efile",
        }
        self._tree = tree

    def find_float(self, path: str) -> Optional[float]:
        """
        Extract a field from the XML document adn convert
        it to a float before returning it.
        """
        _logger.debug(f"find float at '{path}'")

        raw_value = self.find_str(path)
        _logger.debug(f"found float - '{raw_value}'")

        if raw_value is None:
            return None

        return float(raw_value)

    def find_int(self, path: str) -> Optional[int]:
        """
        Extract a field from the XML document and
        convert it to an integer before returning it.
        """

        _logger.debug(f"find int at '{path}'")

        raw_value = self.find_str(path)
        _logger.debug(f"found int - '{raw_value}'")

        if raw_value is None:
            return None

        return int(raw_value)

    def find_str(self, path: str) -> Optional[str]:
        """
        Extract a field from the XML document and return
        it exactly as it was contained in the document.
        """

        _logger.debug(f"find str at '{path}'")

        full_path = self._add_namespace(path)
        _logger.debug(f"find str at '{full_path}'")

        element = self._tree.find(full_path, namespaces=self._namespaces)

        if element is None:
            _logger.debug(f"found str - '{None}'")
            return None

        element_content: str = element.text

        _logger.debug(f"found str - '{element_content}'")
        return element_content

    @staticmethod
    def _add_namespace(path: str) -> str:
        """
        Add the default namespace to all path segments
        and try to guess if we need to prepend any additional tags.
        """
        relative_path = path.lstrip("/")

        explicit_header = relative_path.startswith("ReturnHeader")
        explicit_data = relative_path.startswith("ReturnData")

        if not (explicit_header or explicit_data):
            # We assume ReturnData if nothing else was specified
            # because that's how the IRSx documentation formats
            # the paths.
            relative_path = f"ReturnData/{relative_path}"

        segments = [f"efile:{tag}" for tag in relative_path.split("/")]

        full_path = "/".join(segments)
        return full_path
