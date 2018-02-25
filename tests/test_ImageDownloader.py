# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from imagedownloader.downloader import ImageDownloader


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


def test_thumbs_size_init():
    fail_message = "ValueError should be raised if thumbs_size contains string on tuple"
    with pytest.raises(ValueError, message=fail_message):
        ImageDownloader(thumbs_size={'string on tuple': (1, 'e')}, thumbs=True)
    with pytest.raises(ValueError, message=fail_message):
        ImageDownloader(thumbs_size=[50, 100, 'string on list'], thumbs=True)

    assert ImageDownloader(thumbs_size=[50, 100], thumbs=False).thumbs_size == {}, \
        "When thumbs=False, thumbs_size should be an empty dictionary"

    with_thumbs_size_list = ImageDownloader(thumbs_size=[50, 100], thumbs=True)
    assert with_thumbs_size_list.thumbs_size == {'50': (50, 50), '100': (100, 100)}, \
        "When thumbs_size is a list, it should be converted to a dictionary"


def test_make_dirs_no_thumbs():

    store_path = TemporaryDirectory()
    store_path.cleanup()
    assert not Path(store_path.name).exists()

    _ = ImageDownloader(store_path=store_path.name)
    assert Path(store_path.name).exists(),\
        "store_path should have been created"

    store_path.cleanup()


def test_make_dirs_with_thumbs():

    store_path = TemporaryDirectory()
    store_path.cleanup()
    assert not Path(store_path.name).exists()

    _ = ImageDownloader(
        store_path=store_path.name,
        thumbs=True,
        thumbs_size=[10, 20]
    )
    assert Path(store_path.name).exists(),\
        "{store_path} should have been created"

    assert Path(store_path.name, 'thumbs', '10').exists(),\
        "{store_path}/thumbs/10 should have been created"

    assert Path(store_path.name, 'thumbs', '20').exists(),\
        "{store_path}/thumbs/10 should have been created"

    store_path.cleanup()


