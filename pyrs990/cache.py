import os
from logging import getLogger
from typing import Container, Dict, Optional

from .constants import DEFAULT_CACHE_PATH

_logger = getLogger(__name__)


class Cache(Container):
    """
    A generic, abstract, cache to allow fast lookups for XML filings or
    CSV index files. This exists to keep us from having to download
    large or numerous files every time we update the site or data.

    TODO: Add a mechanism for invalidating / replacing cached documents
    """

    def get(self, cache_key: str) -> Optional[str]:
        """
        Fetch a document from the cache.
        """
        raise NotImplementedError()

    def put(self, cache_key: str, content: str) -> str:
        """
        Cache a document.
        """
        raise NotImplementedError()


class MemoryCache(Cache):
    """
    A naive, in-memory cache that does no eviction or invalidation.

    >>> c = MemoryCache()
    >>> c.get("foo")
    >>> c.put("foo", "bar")
    'bar'
    >>> c.get("foo")
    'bar'
    """

    _dict: Dict[str, str]

    def __contains__(self, __x: object) -> bool:
        return __x in self._dict

    def __init__(self):
        self._dict = {}

    def get(self, cache_key: str) -> Optional[str]:
        content = self._dict.get(cache_key, None)
        if content is None:
            _logger.debug(f"cache miss fetching cache key '{cache_key}'")
        _logger.debug(f"cache hit fetching cache key '{cache_key}'")
        return content

    def put(self, cache_key: str, content: str) -> str:
        _logger.debug(f"caching cache key '{cache_key}'")
        self._dict[cache_key] = content
        return content


class DirectoryCache(Cache):
    """
    A simple on-disk cache that saves documents to the given
    directory.

    TODO: Opened files need to be closed
    TODO: OMG so much edge case and error checking, seriously

    >>> import os.path as p
    >>> import tempfile as tf
    >>> d = tf.mkdtemp()
    >>> c = DirectoryCache(".xml", d)
    >>> c.get("foo")
    >>> c.put("foo", "bar")
    'bar'
    >>> p.exists(f"{d}/foo.xml")
    True
    """

    _extension: str

    _path: str

    def __contains__(self, __x: object) -> bool:
        pass

    def __init__(self, extension: str, path: str = DEFAULT_CACHE_PATH):
        if extension.startswith("."):
            self._extension = extension
        else:
            self._extension = f".{extension}"

        if path == "":
            # Use the default directory
            # TODO: Better error checking here, what if it's a file?
            if not os.path.isdir(DEFAULT_CACHE_PATH):
                os.mkdir(DEFAULT_CACHE_PATH)
            self._path = DEFAULT_CACHE_PATH
            return

        if os.path.exists(path):
            # Attempt to use the existing directory
            if not os.path.isdir(path):
                raise ValueError(f"path '{path}' is not a directory")

            self._path = path
            return

        os.mkdir(path)
        self._path = path

    def get(self, cache_key: str) -> Optional[str]:
        path = os.path.join(self._path, f"{cache_key}{self._extension}")
        if os.path.exists(path) and os.path.isfile(path):
            _logger.debug(f"cache hit fetching cache key '{cache_key}'")
            with open(path) as cache_file:
                return cache_file.read()
        _logger.debug(f"cache miss fetching cache key '{cache_key}'")
        return None

    def put(self, cache_key: str, content: str) -> str:
        _logger.debug(f"caching cache key '{cache_key}'")
        path = os.path.join(self._path, f"{cache_key}{self._extension}")
        with open(path, "w") as cache_file:
            cache_file.write(content)
        return content
