from __future__ import annotations

import csv
from logging import getLogger
from typing import Any, Dict, Iterator, List, NamedTuple, NewType, TextIO

from .downloader import Downloader
from .types import EIN

_logger = getLogger(__name__)


ANNUAL_FIELD_NAMES: List[str] = [
    "RETURN_ID",
    "FILING_TYPE",
    "EIN",
    "TAX_PERIOD",
    "SUB_DATE",
    "TAXPAYER_NAME",
    "RETURN_TYPE",
    "DLN",
    "OBJECT_ID",
]


AnnualYear = NewType("AnnualYear", int)
"""
A filing year supported by the software. This will generally only
include 2017-2019, at least for now.
"""


AnnualRecordDict = NewType("AnnualRecordDict", Dict[str, str])
"""
A dictionary presumed to have the keys listed in `ANNUAL_FIELD_NAMES`
so that it can be used to create an instance of `AnnualRecord`.
"""


class AnnualRecord(NamedTuple):
    """
    A single record from an annual index (such as those hosted at
    https://registry.opendata.aws/irs990/) that can be used to get
    an object ID that will allow the actual filing to be retrieved
    from the internet.

    TODO: Audit the descriptions for correctness and completeness
    """

    @staticmethod
    def from_csv(index_file: TextIO,) -> Iterator[AnnualRecord]:
        for row in csv.DictReader(index_file):
            record = AnnualRecord.from_dict(AnnualRecordDict(row))
            yield record

    @staticmethod
    def from_dict(d: AnnualRecordDict,) -> AnnualRecord:
        params: Dict[str, str] = {}
        try:
            for name in ANNUAL_FIELD_NAMES:
                params[name.lower()] = d[name]
        except KeyError as e:
            _logger.error(f"malformed index row - '{e}' - '{d}'")
            raise
        return AnnualRecord(**params)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"AnnualRecord(taxpayer_name='{self.taxpayer_name}', ein='{self.ein}')"

    def to_dict(self) -> Dict[str, Any]:
        """
        Support for JSON serialization.
        """
        return dict(self.__dict__)

    return_id: str
    """Unique identifier for the tax filing."""

    filing_type: str
    """Type of filing, for example: 'EFILE'."""

    ein: str
    """Tax ID number of the organization."""

    tax_period: str
    """TODO: Find out what this is, exactly."""

    sub_date: str
    """Date the filing was submitted to the IRS."""

    taxpayer_name: str
    """Name of the organization that submitted the filing."""

    return_type: str
    """Type of form that was submitted, for example: '990'."""

    dln: str
    """TODO: Figure out what this is"""

    object_id: str
    """The unique identifier for this filing, used to download data."""


AnnualIndex = Dict[EIN, AnnualRecord]
"""
An Annual index as fetched from the IRS AWS bucket. It is representative
of all the filings received in the respective year, though it only
provides limited filtering ability because it doesn't include any
geographic information.
"""


# This is the global register for Annual indices. Since a given index
# should never change at runtime, we cache them for efficiency. Only
# the indices that are required will be created and they can be reused
# without significant additional cost.
_annual_indices: Dict[AnnualYear, AnnualIndex] = {}


def get_annual_index(year: AnnualYear, downloader: Downloader) -> AnnualIndex:
    """
    Get an AnnualIndex for the given year, using the given Downloader
    to retrieve the appropriate file. The provided Downloader must be
    able to accept a four-digit year as its document key.

    >>> from pyrs990.downloader import FakeDownloader
    >>> documents = {"2018": open("fixtures/annual_index.csv")}
    >>> downloader = FakeDownloader(documents)
    >>> index0 = get_annual_index(AnnualYear(2018), downloader)
    >>> index1 = get_annual_index(AnnualYear(2018), downloader)
    >>> id(index0) == id(index1)
    True
    >>> len(index0)
    2
    >>> "133085892" in index0
    True
    """
    if year in _annual_indices:
        return _annual_indices[year]

    index: AnnualIndex = {}
    _annual_indices[year] = index

    index_file = downloader.fetch(str(year))
    for record in AnnualRecord.from_csv(index_file):
        index[EIN(record.ein)] = record
    return index
