from __future__ import annotations

import csv
import json
import sys
from typing import Callable, Dict, Iterable, Optional, TextIO, Type, List, \
    Protocol, Any

from .filing import Filing

_formatters: Dict[str, Callable[[str], Formatter]] = {}
"""
A static container for Formatter factories.
"""


class FormatterException(Exception):
    pass


def get_formatter(name: str, destination: str) -> Optional[Formatter]:
    """
    Retrieve the registered formatter with the given name, or return
    `None` if it wasn't found.
    """
    constructor = _formatters.get(name, None)
    if constructor is None:
        return None
    return constructor(destination)


def register(name: str, factory: Callable[[str], Formatter]) -> None:
    """
    Register a new formatter with the given name. This allows it
    to be specified on the command line by its name.
    """
    _formatters[name] = factory


def registered_formatters() -> List[str]:
    """
    Return the names of all registered formatters.
    """
    return list(_formatters.keys())


class Formatter:
    """
    An abstract class that defines the structure of an object that
    can be used to output one or more filings for human or machine
    consumption.
    """

    def prologue(self) -> None:
        """
        A method that will be called before any filings are written
        to give the formatter a chance to prepare its output.
        """
        raise NotImplementedError()

    def write(self, filing: Filing) -> None:
        """
        A method called to output a single filing.
        """
        raise NotImplementedError()

    def write_all(self, filings: Iterable[Filing]) -> None:
        """
        A method called to output multiple filings.
        """
        for filing in filings:
            self.write(filing)

    def epilogue(self) -> None:
        """
        A method that will be called after all filings have been
        written to give the formatter a chance to close out its
        output.
        """
        raise NotImplementedError()


def register_formatter(
    name: str,
) -> Callable[[Type[Formatter]], Type[Formatter]]:
    """
    A decorator that allows a class to be registered as a formatter.
    Registered formatters must have a one-parameter constructor that
    accepts a string. This will be either the destination that was
    specified for the formatter or `None` if there was no destination
    specified. The formatter must work reasonably in either case.
    """

    def _decorator(cls: Type[Formatter]) -> Type[Formatter]:
        register(name, cls)
        return cls

    return _decorator


@register_formatter("file")
class FileFormatter(Formatter):
    """
    A formatter that writes to a file-like object.

    >>> f = FileFormatter(":stdout:")
    >>> f.prologue()
    >>> f.epilogue()
    """

    _file: Optional[TextIO] = None

    _has_written: bool = False

    _path: str

    def __init__(self, destination: str):
        self._path = destination

    def prologue(self) -> None:
        if self._file is not None:
            return

        if self._path == ":stdout:":
            self._file = sys.stdout
        elif self._path == ":stderr:":
            self._file = sys.stderr
        else:
            self._file = open(self._path, "w")

    def write(self, filing: Filing) -> None:
        if self._file is None:
            raise FormatterException("must call prologue() before write()")

        if self._has_written:
            self._file.write("\n")
        else:
            self._has_written = True

        # TODO: Come up with a way to let the user specify which fields to use
        self._file.write(f"Business Name:          {filing.business_name}\n")
        self._file.write(f"Formation Year:         {filing.formation_year}\n")
        self._file.write(
            f"Principal Officer Name: {filing.principal_officer_name}\n"
        )
        self._file.write(f"Website Address:        {filing.website_address}\n")

    def epilogue(self) -> None:
        if self._file is None:
            raise FormatterException("must call prologue() before epilogue()")

        if self._path != ":stdout:" and self._path != ":stderr:":
            self._file.close()

        self._file = None


@register_formatter("json")
class JSONFormatter(Formatter):
    """
    A formatter that outputs JSON-encoded filings.

    >>> f = JSONFormatter(":stdout:")
    >>> f.prologue()
    {"filings": [
    >>> f.epilogue()
    ]}

    """

    _file: Optional[TextIO] = None

    _has_written: bool = False

    _path: str

    def __init__(self, destination: str):
        self._path = destination

    def prologue(self) -> None:
        if self._file is not None:
            return

        if self._path == ":stdout:":
            self._file = sys.stdout
        elif self._path == ":stderr:":
            self._file = sys.stderr
        else:
            self._file = open(self._path, "w")

        self._file.write('{"filings": [')

    def write(self, filing: Filing) -> None:
        if self._file is None:
            raise FormatterException("must call prologue() before write()")

        if self._has_written:
            self._file.write(",")
        else:
            self._has_written = True

        json.dump(filing.to_json(), self._file)

    def epilogue(self) -> None:
        if self._file is None:
            raise FormatterException("must call prologue() before epilogue()")

        self._file.write("]}\n")

        if self._path != ":stdout:" and self._path != ":stderr:":
            self._file.close()

        self._file = None


class CSVWriterProtocol(Protocol):
    """
    A helper to let us type annotate the CSVFormatter.
    """
    def writerow(self, row: Iterable[Any]) -> None:
        ...


@register_formatter("csv")
class CSVFormatter(Formatter):
    """
    A Formatter implementation that creates CSV-formatted files.
    """

    _file: Optional[TextIO] = None

    _has_written: bool = False

    _path: str

    _writer: Optional[CSVWriterProtocol] = None

    def __init__(self, destination: str):
        self._path = destination

    def prologue(self) -> None:
        if self._file is not None:
            return

        if self._path == ":stdout:":
            self._file = sys.stdout
        elif self._path == ":stderr:":
            self._file = sys.stderr
        else:
            self._file = open(self._path, "w")

        self._writer = csv.writer(self._file)

        # TODO: Write column headers? How do we choose?

    def write(self, filing: Filing) -> None:
        if self._file is None:
            return

        if self._has_written:
            self._file.write(",")
        else:
            self._has_written = True

        # TODO: Write data from filing, choosing the same fields as prologue

    def epilogue(self) -> None:
        if self._file is None:
            return

        if self._path not in (":stdout:", ":stderr:"):
            self._file.close()

        self._file = None
        self._writer = None
