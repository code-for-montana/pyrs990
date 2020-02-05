from __future__ import annotations

import dataclasses as dc
import json
import logging
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, NamedTuple

from .cache import Cache, DirectoryCache, MemoryCache
from .constants import (
    CURRENT_VERSION,
    DEFAULT_CACHE_PATH,
    PROGRAM_DESCRIPTION,
    PROGRAM_NAME,
)
from .filing import Filing
from .formatter import (
    FileFormatter,
    Formatter,
    get_formatter,
    registered_formatters,
)
from .index import IndexRecord

_log_levels = {
    "none": -100,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
    "fatal": logging.FATAL,
}

_logger = logging.getLogger(__name__)


parser = ArgumentParser(
    prog=PROGRAM_NAME,
    description=PROGRAM_DESCRIPTION,
    epilog="A project of *Code for Montana*.",
)

parser.add_argument(
    "--version", "-v", action="version", version=CURRENT_VERSION,
)

parser.add_argument(
    "--use-disk-cache",
    action="store_true",
    default=False,
    help="cache index and filing documents to disk",
)

parser.add_argument(
    "--cache-path",
    type=str,
    default=DEFAULT_CACHE_PATH,
    help="path to use for reading and writing cache data",
)

parser.add_argument(
    "--dry-run",
    action="store_true",
    default=False,
    help="report how many documents would be "
    + "downloaded / process and nothing else",
)

parser.add_argument(
    "--load-filters",
    action="append",
    type=str,
    help="read filters from a JSON file",
)

parser.add_argument(
    "--log-level",
    type=str,
    choices=_log_levels.keys(),
    default="none",
    help="set the log level, no logging is done by default",
)

parser.add_argument(
    "--no-confirm",
    action="store_true",
    default=False,
    help="do not interactively confirm large downloads, for shell scripts",
)

parser.add_argument(
    "--save-filters", type=str, help="save the filters applied to a JSON file",
)

if "json" in registered_formatters():
    parser.add_argument(
        "--to-json",
        action="store_true",
        default=False,
        help="output extracted data to JSON, equivalent to --formatter=json",
    )

parser.add_argument(
    "--formatter",
    type=str,
    choices=registered_formatters(),
    default=registered_formatters()[0],
    help="output formatter, use --destination to specify file name",
)

parser.add_argument(
    "--destination",
    type=str,
    default=":stdout:",
    help="file to which output should be written (or ':stdout:', ':stderr:')",
)

parser.add_argument(
    "--regions",
    type=str,
    default="mt",
    help="regions to search, comma-separated "
    + "(two character state abbreviations, for most)",
)

parser.add_argument(
    "--years",
    type=str,
    default=":current:",
    help="years to search, comma-separated "
    + "(':current:' is the most recent completed year)",
)

# -------------------- #
# Index record filters #
# -------------------- #

for index_filter_field_name in IndexRecord.field_names():
    parser.add_argument(
        f"--{index_filter_field_name}",
        type=str,
        help=f"apply a filter to the {index_filter_field_name} index field",
    )

# -------------- #
# Filing filters #
# -------------- #

for filing_filter_field_name in dc.fields(Filing):
    name = filing_filter_field_name.name
    parser.add_argument(
        f"--{filing_filter_field_name.name}",
        type=str,
        help=f"apply a filter to the {name} filing field",
    )


class Options(NamedTuple):
    @staticmethod
    def from_args(args: Namespace) -> Options:
        if hasattr(args, "to_json") and args.to_json:
            formatter = get_formatter("json", args.destination)
        else:
            formatter = get_formatter(args.formatter, args.destination)
        if formatter is None:
            formatter = FileFormatter(args.destination)

        index_cache: Cache
        filing_cache: Cache
        if args.use_disk_cache:
            index_cache = DirectoryCache(".csv", args.cache_path)
            filing_cache = DirectoryCache(".xml", args.cache_path)
        else:
            index_cache = MemoryCache()
            filing_cache = MemoryCache()

        # Gather all the index filters
        index_filters: Dict[str, str] = {}
        for index_field_name in IndexRecord.field_names():
            if hasattr(args, index_field_name):
                value = getattr(args, index_field_name)
                if value is not None:
                    index_filters[index_field_name] = value
        _logger.debug(f"extracted index filters: {index_filters}")

        # Gather all the filing filters
        filing_filters: Dict[str, str] = {}
        for filing_field_name in dc.fields(Filing):
            name = filing_field_name.name
            if hasattr(args, name):
                value = getattr(args, name)
                if value is not None:
                    filing_filters[name] = value
        _logger.debug(f"extracted filing filters: {filing_filters}")

        # Check for JSON files specifying filters
        if args.load_filters is not None:
            for filters_path in args.load_filters:
                with open(filters_path) as filters_file:
                    filters_data: Dict[str, Any] = json.load(filters_file)

                # JSON file has two top-level keys, "index" and "filing"

                index_data: Dict[str, str] = filters_data["index"]
                if index_data is not None:
                    index_filters.update(index_data)

                filing_data: Dict[str, str] = filters_data["filing"]
                if filing_data is not None:
                    filing_filters.update(filing_data)

        # Save filters if we need to do so
        if args.save_filters is not None:
            payload = {
                "index": index_filters,
                "filing": filing_filters,
            }
            with open(args.save_filters, "w") as saveFile:
                json.dump(payload, saveFile)

        # Figure out the years we want
        years: List[str] = []
        years_str = args.years.split(",")
        for year_str in years_str:
            if year_str == ":current:":
                # We use last year since it is most likely to have
                # complete, or at least reasonably complete, data.
                # The other problem is that the current year probably
                # doesn't even exist until a couple months into the
                # year so the user would get mysterious 404s.
                years.append(str(datetime.today().year - 1))
                continue
            years.append(year_str)

        # Choose our regions
        regions: List[str] = []
        regions_str = args.regions.split(",")
        for region_str in regions_str:
            regions.append(region_str)

        return Options(
            dry_run=args.dry_run,
            formatter=formatter,
            filing_cache=filing_cache,
            index_cache=index_cache,
            log_level=_log_levels[args.log_level],
            log_level_human=args.log_level,
            no_confirm=args.no_confirm,
            filing_filters=filing_filters,
            index_filters=index_filters,
            to_json=args.to_json,
            regions=regions,
            years=years,
        )

    dry_run: bool

    formatter: Formatter

    filing_cache: Cache

    index_cache: Cache

    log_level: int

    log_level_human: str

    no_confirm: bool

    regions: Iterable[str]

    years: Iterable[str]

    filing_filters: Mapping[str, str] = {}

    index_filters: Mapping[str, str] = {}

    to_json: bool = False
