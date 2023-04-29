from unittest.mock import patch

import pytest

from imgdl.storage.backend import GoogleStorage, LocalStorage, resolve_storage_backend
from imgdl.storage.gcloud import Bucket, Client


class TestResoveBackend:
    def test_local_storage(self, tmp_path):
        storage = resolve_storage_backend(tmp_path)
        assert isinstance(storage, LocalStorage)

    def test_google_storage_with_bucket_only(self, tmp_path):
        with patch("google.cloud.storage.Bucket.exists", spec=Bucket):
            with patch("imgdl.storage.gcloud.Client", spec=Client):
                storage = resolve_storage_backend("gs://non_existing_bucket_12345")
                assert isinstance(storage, GoogleStorage)
                assert storage.bucket_name == "non_existing_bucket_12345"
                assert storage.bucket_path == ""

    def test_google_storagewith_bucket_and_path(self, tmp_path):
        with patch("google.cloud.storage.Bucket.exists", spec=Bucket):
            with patch("google.cloud.storage.Client", spec=Client):
                storage = resolve_storage_backend("gs://non_existing_bucket_12345/path")
                assert isinstance(storage, GoogleStorage)
                assert storage.bucket_name == "non_existing_bucket_12345"
                assert storage.bucket_path == "path/"

    def test_without_google_cloud_installed(self):
        with patch("imgdl.storage.backend.GCLOUD", False):
            with pytest.raises(ImportError):
                resolve_storage_backend("gs://prediktia-1-0")
