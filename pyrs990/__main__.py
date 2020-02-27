import sys

from . import app
from ._options import Options, _log_levels, parser

if __name__ == "__main__":
    import logging

    logging.basicConfig()
    logger = logging.getLogger(__package__)

    args = parser.parse_args(sys.argv[1:])

    # We do this kinda janky like without the Options instance
    # so that we can log inside the Options factory.
    if args.log_level != "none":
        logger.setLevel(_log_levels[args.log_level])

    options = Options.from_args(args)

    app.run(options)
