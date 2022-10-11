#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import random
from collections.abc import Iterable
from concurrent import futures
from io import BytesIO
from pathlib import Path
from pprint import pformat
from time import sleep

import attr
import requests
from PIL import Image
from tqdm.auto import tqdm

from .settings import config, get_logger
from .utils import to_bytes

logger = get_logger(
    __name__,
    filename=config.get("LOGFILE", "imgdl.log"),
    streamhandler=True,
)


@attr.s
class ImageDownloader(object):
    """Image downloader that converts to common format.

    Downloads images and converts them to JPG format and RGB mode.

    Parameters
    ----------
    store_path : str
        Root path where images should be stored
    n_workers : int
        Number of simultaneous threads to use
    timeout : float
        Timeout to be given to the url request
    min_wait : float
        Minimum wait time between image downloads
    max_wait : float
        Maximum wait time between image downloads
    session : requests.Session
        requests session
    debug : bool
        If True, log urls that could not be downloaded
    """

    store_path = attr.ib(converter=lambda v: Path(v).expanduser(), default=config['STORE_PATH'])
    n_workers = attr.ib(converter=int, default=config['N_WORKERS'])
    timeout = attr.ib(converter=float, default=config['TIMEOUT'])
    min_wait = attr.ib(converter=float, default=config['MIN_WAIT'])
    max_wait = attr.ib(converter=float, default=config['MAX_WAIT'])
    session = attr.ib(default=requests.Session())
    debug = attr.ib(converter=bool, default=False)


    def __call__(self, urls, paths=None, force=False):
        """Download url or list of urls

        Parameters
        ----------
        urls : str | list
            url or list of urls to be downloaded
        
        path : str | list
            path or list of paths where the image(s) should be stored

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

        if not isinstance(urls, (str, Iterable)):
            raise ValueError("urls should be str or iterable")

        if isinstance(urls, str):
            return str(self._download_image(urls, paths, force=force))

        with futures.ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            n_fail = 0
            future_to_url = {
                executor.submit(self._download_image, url, paths, force): (i, url)
                for i, url in enumerate(urls)
            }
            total = len(future_to_url)
            paths = [None] * total
            for future in tqdm(futures.as_completed(future_to_url), total=total, miniters=1):
                i, url = future_to_url[future]
                if future.exception() is None:
                    paths[i] = str(future.result())
                else:
                    n_fail += 1

            logger.warning(f"{n_fail} images failed to download")

        return paths

    def _download_image(self, url, path=None, force=False, session=None, timeout=None):
        """Download image and convert to jpeg rgb mode.

        If the image path already exists, it considers that the file has
        already been downloaded and does not downloaded again.


        Parameters
        ----------
        url : str
            url of the image to be downloaded
        
        path : str
            path where the image should be stored

        force : bool
            If True force the download even if the file already exists

        session : requests.Session
            An instance of requests.Session with which image will be downloaded.
            Useful when you want to use the same session for several downloads.

        timeout : float
            Timeout to be given to the url request

        Returns
        -------
        path : str
            Path where the image was stored
        """
        metadata = {
            'success': False,
            'url': url,
        }
        path = Path(path) if path is not None else Path(self.store_path, hashlib.sha1(to_bytes(url)).hexdigest() + '.jpg')
        if path.exists() and not force:
            metadata.update({
                'success': True,
                'filepath': path
            })
            logger.info("On cache", extra=metadata)
            return path
        try:
            session = session or requests.Session()
            timeout = timeout or self.timeout
            metadata['session'] = {
                'headers': dict(session.headers),
                'timeout': timeout,
            }
            response = session.get(url, timeout=timeout)
            metadata['response'] = {
                'headers': dict(response.headers),
                'status_code': response.status_code,
            }
            orig_img = Image.open(BytesIO(response.content))
            img, buf = self.convert_image(orig_img)
            with path.open('wb') as f:
                f.write(buf.getvalue())
            metadata.update({
                'success': True,
                'filepath': path,
            })

            logger.info("Downloaded", extra=metadata)
            sleep(random.uniform(self.min_wait, self.max_wait))
        except Exception as e:
            metadata['Exception'] = {
                'type': type(e),
                'msg': str(e),
            }
            logger.error(f"Failed", extra=metadata)
            raise e
        return path

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


def download(urls,
             paths=None,
             store_path=config['STORE_PATH'],
             n_workers=config['N_WORKERS'],
             timeout=config['TIMEOUT'],
             min_wait=config['MIN_WAIT'],
             max_wait=config['MAX_WAIT'],
             session=requests.Session(),
             debug=False,
             force=False):
    """Asynchronously download images using multiple threads.

    Parameters
    ----------
    urls : iterator
        Iterator of urls    
    path : list
        list of paths where the images should be stored
    store_path : str
        Root path where images should be stored
    n_workers : int
        Number of simultaneous threads to use
    timeout : float
        Timeout to be given to the url request
    min_wait : float
        Minimum wait time between image downloads
    max_wait : float
        Maximum wait time between image downloads
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
    Path(store_path).mkdir(exist_ok=True, parents=True)
    downloader = ImageDownloader(
        store_path=store_path,
        n_workers=n_workers,
        timeout=timeout,
        min_wait=min_wait,
        max_wait=max_wait,
        session=session,
        debug=debug,
    )

    return downloader(urls, paths=paths, force=force)
