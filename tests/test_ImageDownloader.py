# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from imgdl.downloader import ImageDownloader


def test_headers_init():
    assert ImageDownloader(user_agent="robot").headers['User-Agent'] == "robot", \
        "Failed to change User-Agent in the headers"


def test_proxies():

    dummy_proxy = "http://proxy.provider.com:4015"
    dummy_proxy_dict = {"http": dummy_proxy, "https": dummy_proxy}
    str_proxy = ImageDownloader(proxies=dummy_proxy)
    assert str_proxy.proxies == [dummy_proxy_dict]

    list_proxy = ImageDownloader(proxies=[dummy_proxy])
    assert list_proxy.proxies == [dummy_proxy_dict]

    assert ImageDownloader(proxies=None).proxies is None

    with pytest.raises(ValueError, message="Empty list not allowed"):
        ImageDownloader(proxies=[])

    with pytest.raises(ValueError, message="Dictionary not allowed"):
        ImageDownloader(proxies=dummy_proxy_dict)

def test_make_dirs():

    store_path = TemporaryDirectory()
    store_path.cleanup()
    assert not Path(store_path.name).exists()

    _ = ImageDownloader(store_path=store_path.name)
    assert Path(store_path.name).exists(),\
        "store_path should have been created"

    store_path.cleanup()
