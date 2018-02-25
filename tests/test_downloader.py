# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from imgdl.settings import config
from imgdl import download

images_file = Path(__file__).parent / 'wikimedia.csv'


def test_download():

    urls = images_file.read_text().strip().split()
    store_path = TemporaryDirectory()
    store_path.cleanup()

    paths = download(
        urls,
        store_path=store_path.name,
        thumbs=True,
        force=False,
        notebook=False,
        debug=True,
    )

    downloaded = len([
        path for path in paths
        if path is not None
    ])

    subdirs = [Path(store_path.name)]
    for thumb_id, size in config['THUMBS_SIZES'].items():
        subdirs += [Path(store_path.name, 'thumbs', thumb_id)]

    for subdir_path in subdirs:
        assert subdir_path.exists(), \
            f"Image directory {subdir_path} should exist after download"
        nb_images = len(list(subdir_path.glob('*.jpg')))
        assert nb_images == downloaded, \
            f"Image directory {subdir_path} should contain {downloaded} " \
            f"images after download, but has {nb_images}"

    for path in paths:
        if path is not None:
            assert Path(path).exists(), f"{path} does not exist"

    store_path.cleanup()


def test_wrong_url_on_iterable_returns_none():
    paths = download(['http://www.fake.image_url.png'])
    assert paths[0] is None, "If image from an iterable cannot be downloaded, " \
                             "it should return None"


def test_wrong_url_with_single_call_raise_exception():
    fail_message = "Expected an exception if image cannot be downloaded on single call"
    with pytest.raises(Exception, message=fail_message):
        _ = download('http://www.fake.image_url.png')


def test_call_generator():
    def iterator():
        yield 'http://www.fake.image_url1.png'
        yield 'http://www.fake.image_url2.png'
        yield 'http://www.fake.image_url3.png'

    paths = download(iterator())

    assert len(paths) == 3, "Expected a list of Nones of length 3"
