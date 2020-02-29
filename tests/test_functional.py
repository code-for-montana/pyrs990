"""
These tests run the command line tool in a subprocess. They are not
intended to be comprehensive, more of a smoke test to ensure that we
haven't broken any core functionality or the user interface.

It is a good idea (in general) to pass the "--use-disk-cache" flag
inside each test so that they will run faster locally. This isn't
problematic because they will run from scratch in CI since it always
starts with a sterile environment.

If you require some kind of input file, place it in the fixtures/
directory under the top level directory and reference it like this:
"fixtures/myfile.whatever" in command line arguments.

Test cases we want to add:

  - multiple years
  - multiple regions
  - filing filters
  - json and csv format
"""

import subprocess as sp
from typing import NamedTuple

import pytest

from pyrs990.constants import CURRENT_VERSION, PROGRAM_NAME


class Return(NamedTuple):
    stdout: str
    stderr: str
    status: int


def runit(*args: str) -> Return:
    """
    Run the command line tool with the provided command line arguments.
    This takes care of running it through poetry so that the tests can
    focus solely on parameter variations.
    """
    result = sp.run(
        ["poetry", "run", "python", "-m", PROGRAM_NAME] + list(args),
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
    ret = runit(
        "--taxpayer_name", "TAMARACK GRIEF RESOURCE CENTER", "--use-disk-cache",
    )
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
    ret = runit("--zip", "59801", "--dry-run", "--use-disk-cache")
    assert ret.status == 0
    assert (
        ret.stdout
        == """This would download 60 documents and process 0 total documents
"""
    )
