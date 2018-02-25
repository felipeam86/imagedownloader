# -*- coding: utf-8 -*-

from glob import glob
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from imagedownloader.settings import config
from imagedownloader import download

import pandas as pd

images_file = Path(__file__).parent / 'wikimedia.csv'


def test_download():

    with images_file.open('r') as fh:
        urls = [url.strip('\n') for url in fh.readlines()]

    store_path = TemporaryDirectory()
    store_path.cleanup()
    config['STORE_PATH'] = store_path.name

    from pprint import pprint
    pprint(config)

    paths = download(
        urls,
        store_path=config['STORE_PATH'],
        thumbs=True,
        thumbs_size=config['THUMBS_SIZES'],
        n_workers=config['N_WORKERS'],
        timeout=config['TIMEOUT'],
        min_wait=config['MIN_WAIT'],
        max_wait=config['MAX_WAIT'],
        proxies=config['PROXIES'],
        headers=config['HEADERS'],
        force=False,
        notebook=False,
    )

    downloaded = len([
        path for path in paths
        if path is not None
    ])

    subdirs = ['.']
    for thumb_id, size in config['THUMBS_SIZES'].items():
        subdirs += [f'thumbs/{thumb_id}']
    print(subdirs)

    for subdir in subdirs:
        subdir_path = Path(config['STORE_PATH'], subdir)
        assert subdir_path.exists(), \
            f"Image directory {subdir_path} should exist after download"
        nb_images = len(glob(str(subdir_path / '*.jpg')))
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


def test_raise_exception_with_single_call_wrong_url():
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
