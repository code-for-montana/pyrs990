import logging
from io import StringIO
from typing import Dict, Iterable, TextIO

import requests

from .cache import Cache

_logger = logging.getLogger(__name__)


class DownloaderException(Exception):
    pass


class Downloader:
    """
    A class responsible for fetching documents based on an identifier.
    """

    def fetch(self, document: str,) -> TextIO:
        raise NotImplementedError()

    def fetch_all(self, documents: Iterable[str],) -> Iterable[TextIO]:
        raise NotImplementedError()


class FakeDownloader(Downloader):
    """
    A fake for testing pieces of the package that rely on a Downloader
    implementation. Give it a dictionary of document keys (strings)
    and document contents (file-like objects) and it does the rest.
    """

    _documents: Dict[str, TextIO]

    def __init__(self, documents: Dict[str, TextIO]):
        self._documents = documents

    def fetch(self, document: str,) -> TextIO:
        return self._documents[document]

    def fetch_all(self, documents: Iterable[str],) -> Iterable[TextIO]:
        return [self.fetch(d) for d in documents]


class HTTPDownloader(Downloader):
    """
    A downloader implementation that uses a template URL to fetch documents
    using HTTP. The cache is checked before any requests are made.

    The cache will always be checked before a network request is made.

    The `url_template` passed to the constructor should be a valid Python
    format string. The only context made available to it will be a key called
    `document` which will match the object ID of the filing to be
    downloaded, or the year of the index to be downloaded.

    If the download fails for any reason a `DownloaderException` will be
    raised. Its message will include the body of the response.

    TODO: Remove "requests" dependency and just use the std lib
    """

    _cache: Cache

    _url_template: str

    def __init__(
        self, url_template: str, cache: Cache,
    ):
        self._cache = cache
        self._url_template = url_template

    def fetch(self, document: str,) -> TextIO:
        _logger.info(f"fetching document '{document}'")
        content = self._cache.get(document)
        if content is None:
            _logger.info("cache miss")
            url = self._url_template.format(document=document)
            _logger.info(f"downloading '{url}'")
            response = requests.get(url)
            _logger.info(f"download finished '{response.reason}'")

            # Encoding sniffing works way better than just trusting
            # the Content-Type header
            response.encoding = response.apparent_encoding

            # We're pretty loose with what we assume to be a successful
            # download here but that should be fine for now.
            if response.status_code < 200 or response.status_code > 299:
                _logger.warning(f"download failed '{response.status_code}'")
                raise DownloaderException(response.text)

            content = self._cache.put(document, response.text)
        else:
            _logger.info("cache hit")

        return StringIO(content)

    def fetch_all(self, documents: Iterable[str],) -> Iterable[TextIO]:
        for document in documents:
            yield self.fetch(document)
