from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from logging import getLogger
from typing import Any, Callable, Dict, Optional

from .querier import Querier

_logger = getLogger(__name__)


def float_factory(path: str) -> Dict[str, Callable[[Querier], Optional[float]]]:
    """
    A helper that returns the correct metadata for a field that receives a
    float value and requires only a simple XPath query.
    """

    def _get_float(querier: Querier) -> Optional[float]:
        return querier.find_float(path)

    return {"factory": _get_float}


def int_factory(path: str) -> Dict[str, Callable[[Querier], Optional[int]]]:
    """
    A helper that returns the correct metadata for a field that receives a
    int value and requires only a simple XPath query.
    """

    def _get_int(querier: Querier) -> Optional[int]:
        return querier.find_int(path)

    return {"factory": _get_int}


def str_factory(path: str) -> Dict[str, Callable[[Querier], Optional[str]]]:
    """
    A helper that returns the correct metadata for a field that receives a
    str value and requires only a simple XPath query.
    """

    def _get_str(querier: Querier) -> Optional[str]:
        return querier.find_str(path)

    return {"factory": _get_str}


def two_part_str_factory(
    path1: str, path2: str, sep="\n"
) -> Dict[str, Callable[[Querier], Optional[str]]]:
    """
    A helper that returns a two-part string field with the parts
    split by the given separator.
    """

    def _factory(querier: Querier) -> Optional[str]:
        line1 = querier.find_str(path1)
        line2 = querier.find_str(path2)
        full: str = sep.join([l for l in [line1, line2] if l is not None])
        if full == "":
            return None
        return full

    return {"factory": _factory}


@dataclass(init=False)
class Filing:
    """
    Encapsulate a Filing as a semantic object with appropriately named
    fields.

    TODO: Write some doctests, build a Querier just like in its tests
    TODO: Explain how to add a new field
    TODO: Consider making this "frozen", see Python docs for implications

    >>> from pyrs990.querier import Querier
    >>> q = Querier.from_path("fixtures/filing.xml")
    >>> f = Filing(q)
    >>> f.formation_year
    2004
    >>> f.employee_count
    19
    >>> f.business_name
    'VOICE OF SAN DIEGO'
    >>> type(f.to_json())
    <class 'dict'>
    """

    activity_or_mission_description: Optional[str] = field(
        metadata=str_factory("/IRS990/ActivityOrMissionDesc")
    )
    business_name: Optional[str] = field(
        metadata=two_part_str_factory(
            "/ReturnHeader/Filer/BusinessName/BusinessNameLine1Txt",
            "/ReturnHeader/Filer/BusinessName/BusinessNameLine2Txt",
            sep=" ",
        )
    )
    formation_year: Optional[int] = field(
        metadata=int_factory("/IRS990/FormationYr")
    )
    gross_receipts: Optional[int] = field(
        metadata=int_factory("/IRS990/GrossReceiptsAmt")
    )
    employee_count: Optional[int] = field(
        metadata=int_factory("/IRS990/TotalEmployeeCnt")
    )
    principal_officer_name: Optional[str] = field(
        metadata=str_factory("/IRS990/PrincipalOfficerNm")
    )
    tax_year: Optional[int] = field(metadata=int_factory("/ReturnHeader/TaxYr"))
    us_address: Optional[str] = field(
        metadata=two_part_str_factory(
            "/IRS990/USAddress/AddressLine1Txt",
            "/IRS990/USAddress/AddressLine2Txt",
        )
    )
    us_city_name: Optional[str] = field(
        metadata=str_factory("/IRS990/USAddress/CityNm")
    )
    us_zip_code: Optional[str] = field(
        metadata=str_factory("/IRS990/USAddress/ZIPCd")
    )
    website_address: Optional[str] = field(
        metadata=str_factory("/IRS990/WebsiteAddressTxt")
    )

    def __init__(self, querier: Querier):
        for declaredField in fields(self):
            value = declaredField.metadata["factory"](querier)
            setattr(self, declaredField.name, value)

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)


FilingFilter = Callable[[Filing], bool]
