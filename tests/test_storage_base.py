import pytest

from imgdl.storage import base

TEST_URL = "http://www.fake.image_url1.png"
TEST_URL_HASH = "4300ba94477e4050e3dd6ab8a9f6699d60ad7dd8"


class TestBaseStorage:
    def test_exists(self):
        s = base.BaseStorage()
        with pytest.raises(NotImplementedError):
            s.exists(TEST_URL)

    def test_save(self):
        s = base.BaseStorage()
        with pytest.raises(NotImplementedError):
            s.save("", TEST_URL)

    def test_get_filepath(self):
        s = base.BaseStorage()
        with pytest.raises(NotImplementedError):
            s.get_filepath(TEST_URL)

    def test_get_filename(self, tmp_path):
        s = base.BaseStorage()
        filename = s.get_filename(TEST_URL)
        assert filename == TEST_URL_HASH + ".jpg"
