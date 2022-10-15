import hashlib
import random
from collections.abc import Iterable
from concurrent import futures
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from time import sleep

import requests
from PIL import Image
from tqdm.auto import tqdm

from .settings import config, get_logger
from .utils import to_bytes

logger = get_logger(__name__)


@dataclass
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
    """

    store_path: Path = config.STORE_PATH
    n_workers: int = config.N_WORKERS
    timeout: float = config.TIMEOUT
    min_wait: float = config.MIN_WAIT
    max_wait: float = config.MAX_WAIT
    session: requests.Session = requests.Session()

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
            for future in tqdm(
                futures.as_completed(future_to_url), total=total, miniters=1
            ):
                i, url = future_to_url[future]
                if future.exception() is None:
                    paths[i] = str(future.result())
                else:
                    n_fail += 1

            logger.warning(f"{n_fail} images failed to download")

        return paths

    def _download_image(self, url, path=None, force=False):
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

        Returns
        -------
        path : str
            Path where the image was stored
        """
        metadata = {
            "success": False,
            "url": url,
            "session": {
                "headers": dict(self.session.headers),
                "timeout": self.timeout,
            },
        }
        path = (
            Path(path)
            if path is not None
            else Path(self.store_path, hashlib.sha1(to_bytes(url)).hexdigest() + ".jpg")
        )
        if path.exists() and not force:
            metadata.update({"success": True, "filepath": path})
            logger.info("On cache", extra=metadata)
            return path
        try:

            response = self.session.get(url, timeout=self.timeout)
            orig_img = Image.open(BytesIO(response.content))
            img = self.convert_image(orig_img)
            img.save(path)

            metadata.update(
                {
                    "success": True,
                    "filepath": path,
                    "response": {
                        "headers": dict(response.headers),
                        "status_code": response.status_code,
                    },
                }
            )

            logger.info("Downloaded", extra=metadata)
            sleep(random.uniform(self.min_wait, self.max_wait))
        except Exception as e:
            metadata.update(
                {
                    "Exception": {
                        "type": type(e),
                        "msg": str(e),
                    },
                }
            )
            logger.error(f"Failed", extra=metadata)
            raise e
        return path

    def get(self, url):
        response = self.session.get(url, timeout=self.timeout)
        return Image.open(BytesIO(response.content))

    @staticmethod
    def convert_image(img):
        """Convert images to JPG, RGB mode and given size if any.

        Parameters
        ----------
        img : Pil.Image

        Returns
        -------
        img : Pil.Image
            Converted image in Pil format
        buf : BytesIO
            Buffer of the converted image
        """
        if img.format == "PNG" and img.mode == "RGBA":
            background = Image.new("RGBA", img.size, (255, 255, 255))
            background.paste(img, img)
            img = background.convert("RGB")
        elif img.mode == "P":
            img = img.convert("RGBA")
            background = Image.new("RGBA", img.size, (255, 255, 255))
            background.paste(img, img)
            img = background.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        return img

    @staticmethod
    def resize_image(img, size):
        """Resize an image to a given size."""
        img = img.copy()
        img.thumbnail(size, Image.ANTIALIAS)
        return img


def download(
    urls,
    paths=None,
    store_path=config.STORE_PATH,
    n_workers=config.N_WORKERS,
    timeout=config.TIMEOUT,
    min_wait=config.MIN_WAIT,
    max_wait=config.MAX_WAIT,
    session=requests.Session(),
    force=False,
):
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
    )

    return downloader(urls, paths=paths, force=force)
