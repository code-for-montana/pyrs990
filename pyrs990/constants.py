AWS_FILING_TEMPLATE = (
    "https://s3.amazonaws.com/irs-form-990/{document}_public.xml"
)
"""
A URL template that uses the AWS S3 bucket maintained by the IRS. For
use with `HTTPDownloader` to download filing documents.
"""

AWS_INDEX_TEMPLATE = (
    "https://s3.amazonaws.com/irs-form-990/index_{document}.csv"
)
"""
A URL template that uses the AWS S3 bucket maintained by the IRS. For
use with the `HTTPDownloader` to download index documents.
"""

import importlib.resources as pkg_resources

version = pkg_resources.read_text("pyrs990", "version.txt")
CURRENT_VERSION = version

DEFAULT_CACHE_PATH = ".pyrs990-cache"

IRS_BMF_TEMPLATE = "https://www.irs.gov/pub/irs-soi/eo_{document}.csv"
"""
A URL template for downloading the Business Master File data from
the IRS web site. This provides us with location data without
having to download every single filing.
"""

PROGRAM_DESCRIPTION = (
    "A utility to extract and serialize IRS Form 990 "
    + "data on non-profit organizations."
)

PROGRAM_NAME = "pyrs990"
