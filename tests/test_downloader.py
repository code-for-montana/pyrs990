import pytest

from pyrs990 import (
    AWS_FILING_TEMPLATE,
    DownloaderException,
    HTTPDownloader,
    MemoryCache,
)


@pytest.mark.network
def test_HTTPDownloader_fetch_with_aws():
    downloader = HTTPDownloader(AWS_FILING_TEMPLATE, MemoryCache())
    reader = downloader.fetch("201541349349307794")
    content = reader.read()
    assert "<?xml" in content


@pytest.mark.network
def test_HTTPDownloader_fetch_bad_url():
    downloader = HTTPDownloader(AWS_FILING_TEMPLATE, MemoryCache())
    with pytest.raises(DownloaderException):
        downloader.fetch("nonsense")


@pytest.mark.skip("TODO")
def test_HTTPDownloader_fetch_checks_cache():
    # Give it a cache that is loaded with a bogus object_id
    # It should find the data even though it doesn't exist in AWS
    pass
