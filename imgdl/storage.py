import hashlib
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


class BaseStorage:
    def exists(self, path):
        raise NotImplementedError

    def save(self, img, path):
        raise NotImplementedError

    def get_filepath(self, url):
        raise NotImplementedError

    def get_filename(self, url):
        url_bytes = url.encode("utf-8", "strict")
        url_hash = hashlib.sha1(url_bytes).hexdigest()
        return url_hash + ".jpg"


@dataclass
class LocalStorage(BaseStorage):
    store_path: Path

    def __post_init__(self):
        self.store_path = Path(self.store_path)
        Path(self.store_path).mkdir(exist_ok=True, parents=True)

    def exists(self, path: Path):
        return path.exists()

    def save(self, img: Image.Image, path: Path):
        img.save(path)

    def get_filepath(self, url):
        return self.store_path / self.get_filename(url)
