# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from imgdl.downloader import ImageDownloader


def test_make_dirs():

    store_path = TemporaryDirectory()
    store_path.cleanup()
    assert not Path(store_path.name).exists()

    _ = ImageDownloader(store_path=store_path.name)
    assert Path(store_path.name).exists(),\
        "store_path should have been created"

    store_path.cleanup()
