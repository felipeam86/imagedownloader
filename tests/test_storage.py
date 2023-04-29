from pathlib import Path

import pytest
from PIL import Image

from imgdl import storage

TEST_URL = "http://www.fake.image_url1.png"
TEST_URL_HASH = "4300ba94477e4050e3dd6ab8a9f6699d60ad7dd8"

TEST_IMAGE = Image.new("RGB", (200, 200))


class TestBaseStorage:
    def test_exists(self):
        s = storage.BaseStorage()
        with pytest.raises(NotImplementedError):
            s.exists(TEST_URL)

    def test_save(self):
        s = storage.BaseStorage()
        with pytest.raises(NotImplementedError):
            s.save("", TEST_URL)

    def test_get_filepath(self):
        s = storage.BaseStorage()
        with pytest.raises(NotImplementedError):
            s.get_filepath(TEST_URL)

    def test_get_filename(self, tmp_path):
        s = storage.BaseStorage()
        filename = s.get_filename(TEST_URL)
        assert filename == TEST_URL_HASH + ".jpg"


class TestLocalStorage:
    def test_init(self, tmp_path):
        s = storage.LocalStorage(store_path=tmp_path)
        assert isinstance(s.store_path, Path)
        assert s.store_path.exists()

    def test_get_filepath(self, tmp_path):
        s = storage.LocalStorage(store_path=tmp_path)
        filepath = s.get_filepath(TEST_URL)
        assert filepath == s.store_path / (TEST_URL_HASH + ".jpg")

    def test_save_and_exists(self, tmp_path):
        s = storage.LocalStorage(store_path=tmp_path)
        filepath = s.store_path / "test.jpg"
        s.save(TEST_IMAGE, filepath)
        assert filepath.exists()
