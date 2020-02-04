from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator

from .downloader import Downloader
from .filing import Filing, FilingFilter
from .index import Index
from .querier import Querier


class Result:
    """
    A lazily-evaluated query result based on the given index and downloader.

    The result can be filtered by providing a callback to the `Result.filter`
    method. This will return a new, independent `Result` that will apply all
    filters already applied by the previous `Result`, plus the one that was
    provided to the method.

    TODO: Enforce immutability assumption
    Right now this type is designed to be immutable so that a given Result
    always produces the same results and you can't accidentally change it
    during iteration, for example. But indices are no longer immutable
    because it was easier that way. However, we may need to go back to
    immutable indices, or copy the data we need from the index when it is
    used to create a Result so that the Result doesn't actually depend on
    the actual Index instance.
    """

    _downloader: Downloader

    _filters: Iterable[FilingFilter]

    _index: Index

    def __init__(
        self,
        downloader: Downloader,
        index: Index,
        filters: Iterable[FilingFilter] = (),
    ):
        self._downloader = downloader
        self._filters = filters
        self._index = index

    def __iter__(self) -> Iterator[Filing]:
        for record in self._index:
            xml_file = self._downloader.fetch(record.annual_record.object_id)
            querier = Querier.from_file(xml_file)
            filing = Filing(querier)
            passed = True
            for cb in self._filters:
                if not cb(filing):
                    passed = False
                    break
            if passed:
                yield filing

    def add_filter(self, cb: FilingFilter,) -> Result:
        """
        Apply a filter to the returned filings. Filings that don't pass the
        given function will not be yielded by the result.
        """
        return Result(
            self._downloader, self._index, list(self._filters) + [cb],
        )

    def download_count(self) -> int:
        """
        The number of filing documents that will be downloaded when this
        Result object is iterated. This may be different from the number
        of Filings actually produced upon iteration since some of them
        may be filtered out here (which requires downloading them first).
        """
        return len(self._index)

    def skip(self, n: int) -> Result:
        """
        Return a result that is identical to this one but doesn't contain the
        first `n` results.
        """
        # TODO: Implement me

    def take(self, n: int) -> Result:
        """
        Return a result that is identical to this one but contains only the
        first `n` results.
        """
        # TODO: Implement me

    def to_json(self) -> Dict[str, Any]:
        """
        Convert the result into JSON suitable for use as data for modules.

        TODO: Think about additional metadata we might want
        """
        return {
            "filings": [f.to_json() for f in self],
        }
