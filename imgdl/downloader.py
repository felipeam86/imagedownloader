#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import hashlib
import logging
import random
from concurrent import futures
from io import BytesIO
from pathlib import Path
from pprint import pformat
from time import sleep

import attr
import requests
from PIL import Image
from tqdm import tqdm, tqdm_notebook

from .settings import config
from .utils import to_bytes

logger = logging.getLogger(__name__)


@attr.s
class ImageDownloader(object):
    """Image downloader that converts to common format and creates thumbs.

    Downloads images and converts them to JPG format and RGB mode. If specified
    it generates thumbnails of the images.

    Parameters
    ----------
    store_path : str
        Root path where images should be stored
    n_workers : int
        Number of simultaneous threads to use
    timeout : float
        Timeout to be given to the url request
    thumbs : bool
        If True, create thumbnails of sizes according to self.thumbs_size
    thumbs_size : dict | list
        Dictionary of the kind {name: (width, height)} indicating the thumbnail
        sizes to be created
    min_wait : float
        Minimum wait time between image downloads
    max_wait : float
        Maximum wait time between image downloads
    proxies : str | list
        Proxy or list of proxies to use for the requests
    headers : dict
        headers to be given to requests
    user_agent : str
        User agent to be used for the requests
    notebook : bool
        If True, use the notebook version of tqdm
    debug : bool
        If True, log urls that could not be downloaded
    """

    store_path = attr.ib(converter=lambda v: Path(v).expanduser(), default=config['STORE_PATH'])
    n_workers = attr.ib(converter=int, default=config['N_WORKERS'])
    timeout = attr.ib(converter=float, default=config['TIMEOUT'])
    thumbs = attr.ib(converter=bool, default=config['THUMBS'])
    thumbs_size = attr.ib(default=config['THUMBS_SIZES'])
    min_wait = attr.ib(converter=float, default=config['MIN_WAIT'])
    max_wait = attr.ib(converter=float, default=config['MAX_WAIT'])
    proxies = attr.ib(default=config['PROXIES'])
    headers = attr.ib(converter=dict, default=config['HEADERS'])
    user_agent = attr.ib(converter=str, default=config['USER_AGENT'])
    notebook = attr.ib(converter=bool, default=False)
    debug = attr.ib(converter=bool, default=False)

    @user_agent.validator
    def update_headers(self, attribute, value):
        if value is not None:
            self.headers.update({'User-Agent': value})

    @proxies.validator
    def resolve_proxies(self, attribute, value):

        def format_as_dict(proxy):
            return {
                "http": proxy,
                "https": proxy
            }

        self.proxies = None
        if isinstance(value, str):
            self.proxies = [format_as_dict(value)]
        elif isinstance(value, list) and len(value) > 0:
            self.proxies = [format_as_dict(proxy) for proxy in value]
        elif value is not None:
            raise ValueError("proxies should be either a string, a list of strings or None")

    @thumbs_size.validator
    def resolve_thumbs_size(self, attribute, value):
        thumbs_size = value or {}
        if self.thumbs:
            if isinstance(thumbs_size, dict):
                for k, v in thumbs_size.items():
                    if not (isinstance(v, (tuple, list)) and
                            (len(v) == 2) and
                            isinstance(v[0], int) and
                            isinstance(v[1], int)):

                        raise ValueError(f"Wrong type of thumbs_size for key '{k}' --> '{v}'"
                                         f" should be a tuple of ints of size 2")
                self.thumbs_size = thumbs_size
            elif isinstance(thumbs_size, list):
                for v in thumbs_size:
                    if not isinstance(v, int):
                        raise ValueError(f"Wrong type for thumbs_size '{v}' --> should be an int")
                self.thumbs_size = {
                    str(thumb): (thumb, thumb)
                    for thumb in thumbs_size
                }
            else:
                raise Exception("thumbs_size must be a dictionary or a list")
        else:
            self.thumbs_size = {}

    @notebook.validator
    def set_tqdm(self, attribute, value):
        self.tqdm = tqdm_notebook if value else tqdm

    def __attrs_post_init__(self):
        self._makedirs()

    def get_proxy(self):
        if isinstance(self.proxies, list):
            return random.choice(self.proxies)
        else:
            return self.proxies

    def _makedirs(self):

        subdirs = ['.']
        if hasattr(self, 'thumbs_size'):
            subdirs += [f'thumbs/{size}' for size in self.thumbs_size.keys()]

        for subdir in subdirs:
            Path(self.store_path, subdir).mkdir(exist_ok=True, parents=True)

    def __call__(self, urls, force=False):
        """Download url or list of urls

        Parameters
        ----------
        urls : str | list
            url or list of urls to be downloaded

        force : bool
            If True force the download even if the files already exists

        Returns
        -------
        paths : str | list
            If url is a str, path where the image was stored.
            If url is iterable the list of image paths is returned. If
            image failed to download, None is given instead of image path
        """

        if self.debug:
            title = '\033[92mImage downloader called with the following arguments :\033[0m'
            arguments = pformat(attr.asdict(self))
            separation = '=' * max(map(len, arguments.split("\n")))
            print(f"{separation}\n{title}\n{arguments}\n{separation}")

        if not isinstance(urls, (str, collections.Iterable)):
            raise ValueError("urls should be str or iterable")

        if isinstance(urls, str):
            return str(self.download_image(urls, force=force))

        with futures.ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            n_fail = 0
            future_to_url = {
                executor.submit(self.download_image, url, force): (i, url)
                for i, url in enumerate(urls)
            }
            total = len(future_to_url)
            paths = [None] * total
            for future in self.tqdm(futures.as_completed(future_to_url), total=total, miniters=1):
                i, url = future_to_url[future]
                if future.exception() is None:
                    paths[i] = str(future.result())
                else:
                    n_fail += 1
                    if self.debug:
                        logger.error(f'Error: {future.exception()}')
                        logger.error(f'For url: {url}')

            logger.info(f"{n_fail} images failed to download")

        return paths

    def download_image(self, url, force=False):
        """Download image, create thumbnails, store and return checksum.

        Downloads image of the given url. If self.thumbs is True, it creates
        thumbnails of sizes according to self.thumbs_size. The md5 checksum of
        the image is returned for checking duplicates.

        If the image path already exists, it considers that the file has
        already been downloaded and does not downloaded again.


        Parameters
        ----------
        url : str
            url of the image to be downloaded

        force : bool
            If True force the download even if the file already exists

        Returns
        -------
        path : str
            Path where the image was stored
        """
        orig_img = None
        path = self.file_path(url)
        if not path.exists() or force:
            response = requests.get(
                url,
                timeout=self.timeout,
                proxies=self.get_proxy(),
                headers=self.headers
            )
            orig_img = Image.open(BytesIO(response.content))
            img, buf = self.convert_image(orig_img)
            self._persist_file(path, buf)
            # Only wait if image had to be downloaded
            sleep(random.uniform(self.min_wait, self.max_wait))

        for thumb_id, size in self.thumbs_size.items():
            thumb_path = self.thumb_path(url, thumb_id)
            if not thumb_path.exists() or force:
                orig_img = orig_img or Image.open(str(path))
                thumb_image, thumb_buf = self.convert_image(orig_img, size)
                self._persist_file(thumb_path, thumb_buf)

        return path

    @staticmethod
    def _persist_file(path, buf):
        with path.open('wb') as f:
            f.write(buf.getvalue())

    @staticmethod
    def convert_image(img, size=None):
        """Convert images to JPG, RGB mode and given size if any.

        Parameters
        ----------
        img : Pil.Image
        size : tuple
            tuple of (width, height)

        Returns
        -------
        img : Pil.Image
            Converted image in Pil format
        buf : BytesIO
            Buffer of the converted image
        """
        if img.format == 'PNG' and img.mode == 'RGBA':
            background = Image.new('RGBA', img.size, (255, 255, 255))
            background.paste(img, img)
            img = background.convert('RGB')
        elif img.mode == 'P':
            img = img.convert("RGBA")
            background = Image.new('RGBA', img.size, (255, 255, 255))
            background.paste(img, img)
            img = background.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        if size:
            img = img.copy()
            img.thumbnail(size, Image.ANTIALIAS)

        buf = BytesIO()
        img.save(buf, 'JPEG')
        return img, buf

    def file_path(self, url):
        """Hash url to get file path of full image
        """
        image_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        return Path(self.store_path, image_guid + '.jpg')

    def thumb_path(self, url, thumb_id):
        """Hash url to get file path of thumbnail
        """
        thumb_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        return Path(self.store_path, 'thumbs', thumb_id, thumb_guid + '.jpg')


def download(urls,
             store_path=config['STORE_PATH'],
             n_workers=config['N_WORKERS'],
             timeout=config['TIMEOUT'],
             thumbs=config['THUMBS'],
             thumbs_size=config['THUMBS_SIZES'],
             min_wait=config['MIN_WAIT'],
             max_wait=config['MAX_WAIT'],
             proxies=config['PROXIES'],
             headers=config['HEADERS'],
             user_agent=config['USER_AGENT'],
             notebook=False,
             debug=False,
             force=False):
    """Asynchronously download images using multiple threads.

    Parameters
    ----------
    urls : iterator
        Iterator of urls
    store_path : str
        Root path where images should be stored
    n_workers : int
        Number of simultaneous threads to use
    timeout : float
        Timeout to be given to the url request
    thumbs : bool
        If True, create thumbnails of sizes according to thumbs_size
    thumbs_size : dict
        Dictionary of the kind {name: (width, height)} indicating the thumbnail
        sizes to be created
    min_wait : float
        Minimum wait time between image downloads
    max_wait : float
        Maximum wait time between image downloads
    proxies : list | dict
        Proxy or list of proxies to use for the requests
    headers : dict
        headers to be given to requests
    user_agent : str
        User agent to be used for the requests
    notebook : bool
        If True, use the notebook version of tqdm
    debug : bool
        If True, log urls that could not be downloaded
    force : bool
        If True force the download even if the files already exists

    Returns
    -------
    paths : str | list
        If url is a str, path where the image was stored.
        If url is iterable the list of image paths is returned. If
        image failed to download, None is given instead of image path
    """
    downloader = ImageDownloader(
        store_path,
        n_workers=n_workers,
        thumbs=thumbs,
        thumbs_size=thumbs_size,
        timeout=timeout,
        min_wait=min_wait,
        max_wait=max_wait,
        proxies=proxies,
        headers=headers,
        user_agent=user_agent,
        notebook=notebook,
        debug=debug
    )

    return downloader(urls, force=force)
