from logging import getLogger

from ._options import Options
from .annual_record import AnnualYear, get_annual_index
from .bmf_record import BMFRegion, get_bmf_index
from .constants import AWS_FILING_TEMPLATE, AWS_INDEX_TEMPLATE, IRS_BMF_TEMPLATE
from .downloader import HTTPDownloader
from .filters import filter_filings, filter_index_record
from .formatter import Formatter
from .index import Index
from .result import Result

# TODO: Split output methods into their own module (JSON, human-readable)

_logger = getLogger(__name__)


LIMIT_BEFORE_CONFIRM = 100
"""
If more than this number of documents will be downloaded, interactively
confirm before starting unless the --no-confirm flag was passed.
"""


def _message_count(download_count: int, cache_count: int) -> str:
    return (
        f"This would download {download_count} documents "
        + f"and process 0 total documents"
    )


def _confirm(
    download_count: int, cache_count: int, formatter: Formatter
) -> bool:
    # TODO: Give the formatter a crack at the prompt message
    message = _message_count(download_count, cache_count,)
    raw = input(message + ", continue? [yN] ",)
    return raw.strip().lower().startswith("y")


def run(options: Options):
    annual_downloader = HTTPDownloader(AWS_INDEX_TEMPLATE, options.index_cache,)
    bmf_downloader = HTTPDownloader(IRS_BMF_TEMPLATE, options.index_cache,)

    index = Index()
    for year in options.years:
        _logger.debug(f"applying year filter for {year}")
        typed_year = AnnualYear(int(year))
        index.add_annual_index(
            typed_year, get_annual_index(typed_year, annual_downloader,),
        )

    for region in options.regions:
        _logger.debug(f"applying region filter for {region}")
        typed_region = BMFRegion(region)
        index.add_bmf_index(
            typed_region, get_bmf_index(typed_region, bmf_downloader,),
        )

    if len(options.index_filters) > 0:
        _logger.debug(f"applying index filters: {options.index_filters}")
        index.add_filter(filter_index_record(options.index_filters))

    filing_downloader = HTTPDownloader(
        AWS_FILING_TEMPLATE, options.filing_cache,
    )
    result = Result(filing_downloader, index,)
    if len(options.filing_filters) > 0:
        _logger.debug(f"applying filing filters: {options.filing_filters}")
        result = result.add_filter(filter_filings(options.filing_filters))

    formatter = options.formatter
    download_count = result.download_count()

    # TODO: Have it check the cache and adjust downloads, process separately
    # TODO: Formatter should get a chance to modify / format messages

    if options.dry_run:
        _logger.debug(f"performing dry-run")
        print(_message_count(download_count, 0))
        return

    if not options.no_confirm and download_count > LIMIT_BEFORE_CONFIRM:
        _logger.debug(f"downloading {download_count} documents, confirming")
        if not _confirm(download_count, 0, formatter):
            _logger.debug(f"user aborted")
            # TODO: Use the formatter for this output
            print("Aborting")
            return

    formatter.prologue()
    formatter.write_all(result)
    formatter.epilogue()
