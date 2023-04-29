from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .base import BaseStorage


@dataclass
class LocalStorage(BaseStorage):
    store_path: Path

    def __post_init__(self):
        self.store_path = Path(self.store_path)
        Path(self.store_path).mkdir(exist_ok=True, parents=True)

    def exists(self, path: Path):
        return Path(path).exists()

    def save(self, img: Image.Image, path: Path):
        img.save(path)

    def get_filepath(self, url):
        return self.store_path / self.get_filename(url)
