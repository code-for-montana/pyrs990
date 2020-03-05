import re
from typing import List, Mapping, Pattern

from .filing import Filing, FilingFilter
from .index import IndexFilter, IndexRecord


class FieldNotFound(Exception):
    name: str

    def __init__(self, name: str):
        self.name = name


def filter_filings(filters: Mapping[str, str],) -> FilingFilter:
    patterns: List[Pattern] = []
    for field_name, filter_text in filters.items():
        patterns.append(re.compile(filter_text, flags=re.IGNORECASE))

    def _filter(filing: Filing) -> bool:
        passed = True
        for i, f in enumerate(filters):
            if not hasattr(filing, f):
                raise FieldNotFound(f)
            value = getattr(filing, f)
            if value is None:
                return False
            pattern = patterns[i]
            match = pattern.search(str(value))
            if match is None:
                passed = False
                break
        return passed

    return _filter


def filter_index_record(filters: Mapping[str, str],) -> IndexFilter:
    patterns: List[Pattern] = []
    for field_name, filter_text in filters.items():
        patterns.append(re.compile(filter_text, flags=re.IGNORECASE))

    def _filter(record: IndexRecord) -> bool:
        passed = True
        for i, f in enumerate(filters):
            if not record.has_field(f):
                raise FieldNotFound(f)
            value = record.get_field(f)
            if value is None:
                return False
            pattern = patterns[i]
            match = pattern.search(str(value))
            if match is None:
                passed = False
                break
        return passed

    return _filter
