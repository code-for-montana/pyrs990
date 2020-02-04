from __future__ import annotations

from logging import getLogger
from typing import (
    Callable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
    Union,
    cast,
)

from .annual_record import AnnualIndex, AnnualRecord, AnnualYear
from .bmf_record import BMFIndex, BMFRecord, BMFRegion
from .types import EIN

_logger = getLogger(__name__)


class IndexRecord(NamedTuple):
    """
    A composite index record that holds an AnnualRecord and a BMFRecord
    that both represent the same organization, as indicated by the EIN
    field. In all cases the two records here should have the same `ein`
    value.
    """

    annual_record: AnnualRecord
    bmf_record: BMFRecord

    @staticmethod
    def field_names() -> Set[str]:
        return set(AnnualRecord._fields + BMFRecord._fields)

    def get_field(self, name: str):
        if hasattr(self.annual_record, name):
            return getattr(self.annual_record, name)
        if hasattr(self.bmf_record, name):
            return getattr(self.bmf_record, name)
        raise KeyError(f"field '{name}' not found in record")

    def has_field(self, name: str):
        return hasattr(self.annual_record, name) or hasattr(
            self.bmf_record, name
        )


IndexFilter = Callable[[IndexRecord], bool]
"""
A callback that can specify whether a given record should be kept
as part of the collection of Filings produced by the index.
"""


class Index:
    """
    An Index provides a way to access a collection of filing documents that
    have been filtered in a reasonably efficient manner using the various
    fields in the annual and BMF (Business Master File) datasets.

    Years (annual) and regions (BMF) can be added to the index to set its
    initial pool of data. Filters, which further pare down the data actually
    fetched, may also be added at-will.

    Once the user wishes to fetch the collection of documents specified
    by the applied filters, the Index may be iterated directly to access
    each index record. The object ID necessary to fetch the document is
    provided on the annual index. Additionally, the object_ids() method may
    be used to access the object IDs directly.
    """

    _annual_indices: List[AnnualIndex] = []

    _annual_years: Set[AnnualYear] = set()

    _bmf_indices: List[BMFIndex] = []

    _bmf_regions: Set[BMFRegion] = set()

    _filters: Set[IndexFilter] = set()

    _length: Optional[int] = None

    def __iter__(self) -> Iterator[IndexRecord]:
        # TODO: Be smarter about which one to iterate first based on filters
        # TODO: Consider whether re-instantiating all these tuples is too slow
        for annual_index in self._annual_indices:
            for bmf_index in self._bmf_indices:
                for annual_record in annual_index.values():
                    ein = EIN(annual_record.ein)
                    if ein not in bmf_index:
                        _logger.info(f"EIN not found in BMF index: {ein}")
                        continue

                    bmf_record = bmf_index[ein]

                    index_record = IndexRecord(annual_record, bmf_record)
                    passed = True
                    for cb in self._filters:
                        if not cb(index_record):
                            passed = False
                            break

                    if passed:
                        yield index_record

    def __len__(self) -> int:
        if self._length is not None:
            return self._length

        # TODO: This is stupid, don't instantiate the tuples, just count
        length = 0
        for _ in self:
            length += 1

        self._length = length
        return self._length

    def add_annual_index(
        self, year: AnnualYear, annual_index: AnnualIndex
    ) -> None:
        if year not in self._annual_years:
            self._length = None
            self._annual_indices.append(annual_index)
            self._annual_years.add(year)

    def add_bmf_index(self, region: BMFRegion, bmf_index: BMFIndex) -> None:
        if region not in self._bmf_regions:
            self._length = None
            self._bmf_indices.append(bmf_index)
            self._bmf_regions.add(region)

    def add_filter(self, cb: IndexFilter) -> None:
        if cb not in self._filters:
            self._length = None
            self._filters.add(cb)

    def object_ids(self) -> Iterator[str]:
        """
        Iterate over the object IDs that correspond to the filing documents
        reflected by this Index.
        """
        for record in self:
            yield record.annual_record.object_id

    def remove_filter(self, cb: IndexFilter) -> None:
        if cb in self._filters:
            self._length = None
            self._filters.remove(cb)

    def remove_index(self, index: Union[AnnualIndex, BMFIndex]) -> None:
        if index in self._annual_indices:
            self._length = None
            self._annual_indices.remove(cast(AnnualIndex, index))
        if index in self._bmf_indices:
            self._length = None
            self._bmf_indices.remove(cast(BMFIndex, index))
