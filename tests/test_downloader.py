# -*- coding: utf-8 -*-

from glob import glob
from pathlib import Path
from tempfile import TemporaryDirectory

from imagedownloader.settings import config
from imagedownloader import download

import pandas as pd

images_file = Path(__file__).parent / 'wikimedia.csv'

def test_download():

    images = pd.read_csv(str(images_file), names=['url'])
    store_path = TemporaryDirectory()
    store_path.cleanup()
    config['STORE_PATH'] = store_path.name

    from pprint import pprint
    pprint(config)

    results = download(
        images['url'],
        store_path=config['STORE_PATH'],
        thumbs=config['THUMBS'],
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
        response
        for url, response in results.items()
        if response is not None
    ])

    subdirs = ['full']
    for thumb_id, size in config['THUMBS_SIZES'].items():
        subdirs += [f'thumbs/{thumb_id}']
    print(subdirs)

    for subdir in subdirs:
        subdir_path = Path(config['STORE_PATH'], subdir)
        assert subdir_path.exists(), \
            f"Image directory {subdir_path} should exist after download"
        nb_images = len(glob(str(subdir_path / '*')))
        assert nb_images == downloaded, \
            f"Image directory {subdir_path} should contain {downloaded} " \
            f"images after download, but has {nb_images}"

    store_path.cleanup()
