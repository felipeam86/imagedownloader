from pathlib import Path

from PIL import Image

from imgdl.storage import local

TEST_URL = "http://www.fake.image_url1.png"
TEST_URL_HASH = "4300ba94477e4050e3dd6ab8a9f6699d60ad7dd8"

TEST_IMAGE = Image.new("RGB", (200, 200))


class TestLocalStorage:
    def test_init(self, tmp_path):
        s = local.LocalStorage(store_path=tmp_path)
        assert isinstance(s.store_path, Path)
        assert s.store_path.exists()

    def test_get_filepath(self, tmp_path):
        s = local.LocalStorage(store_path=tmp_path)
        filepath = s.get_filepath(TEST_URL)
        assert filepath == s.store_path / (TEST_URL_HASH + ".jpg")

    def test_save_and_exists(self, tmp_path):
        s = local.LocalStorage(store_path=tmp_path)
        filepath = s.store_path / "test.jpg"
        s.save(TEST_IMAGE, filepath)
        assert filepath.exists()
        assert s.exists(filepath)
