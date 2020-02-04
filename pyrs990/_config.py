from __future__ import annotations

from typing import Iterator, NamedTuple

from ._options import Options


class Config(NamedTuple):
    """
    A container for global configuration options to allow hierarchical
    specification through a configuration file, environment variables,
    and built-in constant values.
    """

    @staticmethod
    def config_file_paths() -> Iterator[str]:
        # check system global path
        # check home directory
        # check CWD
        # check directories above CWD???
        pass

    @staticmethod
    def from_options(options: Options) -> Config:
        pass
