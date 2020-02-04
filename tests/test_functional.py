import subprocess as sp
from typing import NamedTuple

import pytest

from pyrs990.constants import CURRENT_VERSION, PROGRAM_NAME


class Return(NamedTuple):
    stdout: str
    stderr: str
    status: int


def runit(*args: str) -> Return:
    result = sp.run(
        ["pipenv", "run", "python", "-m", PROGRAM_NAME] + list(args),
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    return Return(
        stdout=result.stdout, stderr=result.stderr, status=result.returncode,
    )


@pytest.mark.subprocess
def test_cli_version() -> None:
    ret = runit("--version")
    assert ret.status == 0
    assert ret.stdout == f"{CURRENT_VERSION}\n"


@pytest.mark.network
@pytest.mark.subprocess
def test_filter_by_taxpayer_name() -> None:
    ret = runit("--taxpayer_name", "TAMARACK GRIEF RESOURCE CENTER")
    assert ret.status == 0
    assert (
        ret.stdout
        == """Business Name:          TAMARACK GRIEF RESOURCE CENTER INC
Formation Year:         2008
Principal Officer Name: TINA BARRETT
Website Address:        WWW.TAMARACKGRIEFRESOURCECENTER.ORG
"""
    )


def test_dry_run_with_some_results() -> None:
    ret = runit("--zip", "59801", "--dry-run")
    assert ret.status == 0
    assert (
        ret.stdout
        == """This would download 60 documents and process 0 total documents
"""
    )


@pytest.mark.subprocess
def test_extract_filing() -> None:
    pass
