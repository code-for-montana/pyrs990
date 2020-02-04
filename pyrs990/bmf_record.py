from __future__ import annotations

import csv
from logging import getLogger
from typing import Any, Dict, Iterable, List, NamedTuple, NewType, TextIO

from .downloader import Downloader
from .types import EIN

_logger = getLogger(__name__)


BMF_FIELD_NAMES: List[str] = [
    "EIN",
    "NAME",
    "ICO",
    "STREET",
    "CITY",
    "STATE",
    "ZIP",
    "GROUP",
    "SUBSECTION",
    "AFFILIATION",
    "CLASSIFICATION",
    "RULING",
    "DEDUCTIBILITY",
    "FOUNDATION",
    "ACTIVITY",
    "ORGANIZATION",
    "STATUS",
    "TAX_PERIOD",
    "ASSET_CD",
    "INCOME_CD",
    "FILING_REQ_CD",
    "PF_FILING_REQ_CD",
    "ACCT_PD",
    "ASSET_AMT",
    "INCOME_AMT",
    "REVENUE_AMT",
    "NTEE_CD",
    "SORT_NAME",
]

BMFRegion = NewType("BMFRegion", str)

BMFRecordDict = NewType("BMFRecordDict", Dict[str, str])
"""
A dictionary presumed to have the keys listed in `BMF_FIELD_NAMES`
so that it can be used to create an instance of `BMFRecord`.
"""


class BMFRecord(NamedTuple):
    """
    A single record from a BMF (Business Master File) index.

    See https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf
    for more information about the data, including field descriptions.

    >>> from pyrs990.downloader import FakeDownloader
    >>> documents = {"mt": open("fixtures/bmf_index.csv")}
    >>> downloader = FakeDownloader(documents)
    >>> index0 = get_bmf_index(BMFRegion("mt"), downloader)
    >>> index1 = get_bmf_index(BMFRegion("mt"), downloader)
    >>> id(index0) == id(index1)
    True
    >>> len(index0)
    2
    >>> "010571299" in index0
    True
    """

    @staticmethod
    def from_csv(index_file: TextIO,) -> Iterable[BMFRecord]:
        records: List[BMFRecord] = []
        for row in csv.DictReader(index_file):
            record = BMFRecord.from_dict(row)
            records.append(record)
        return records

    @staticmethod
    def from_dict(d: Dict[str, str],) -> BMFRecord:
        params: Dict[str, str] = {}
        try:
            for name in BMF_FIELD_NAMES:
                params[name.lower()] = d[name]
        except KeyError as e:
            _logger.error(f"malformed index row - '{e}' - '{d}'")
            raise
        return BMFRecord(**params)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"BMFRecord(name='{self.name}', ein='{self.ein}')"

    def to_dict(self) -> Dict[str, Any]:
        """
        Support for JSON serialization.
        """
        return dict(self.__dict__)

    ein: str
    name: str
    ico: str
    street: str
    city: str
    state: str
    zip: str
    group: str
    subsection: str
    affiliation: str
    classification: str
    ruling: str
    deductibility: str
    foundation: str
    activity: str
    organization: str
    status: str
    tax_period: str
    asset_cd: str
    income_cd: str
    filing_req_cd: str
    pf_filing_req_cd: str
    acct_pd: str
    asset_amt: str
    income_amt: str
    revenue_amt: str
    ntee_cd: str
    sort_name: str


BMFIndex = Dict[EIN, BMFRecord]

_bmf_indices: Dict[BMFRegion, BMFIndex] = {}


def get_bmf_index(region: BMFRegion, downloader: Downloader) -> BMFIndex:
    if region in _bmf_indices:
        return _bmf_indices[region]

    index: BMFIndex = {}
    _bmf_indices[region] = index

    index_file = downloader.fetch(str(region))
    for record in BMFRecord.from_csv(index_file):
        index[EIN(record.ein)] = record
    return index
