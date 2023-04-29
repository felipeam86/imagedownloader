from unittest.mock import patch

import pytest
from google.cloud.storage import Client

from imgdl.storage import gcloud
from imgdl.storage.gcloud import Bucket

TEST_URL = "http://www.fake.image_url1.png"
TEST_URL_HASH = "4300ba94477e4050e3dd6ab8a9f6699d60ad7dd8"


class TestGoogleStorage:
    def test_init_with_bucket_only(self):
        with patch("google.cloud.storage.Bucket", spec=Bucket):
            with patch("google.cloud.storage.Client", spec=Client) as mock_client:
                storage = gcloud.GoogleStorage(
                    bucket_name="non_existing_bucket_12345",
                    client=mock_client,
                )
                assert storage.bucket_name == "non_existing_bucket_12345"
                assert storage.bucket_path == ""

    def test_init_with_bucket_path_ending_with_slash(self):
        with patch("google.cloud.storage.Bucket", spec=Bucket):
            with patch("google.cloud.storage.Client", spec=Client) as mock_client:
                storage = gcloud.GoogleStorage(
                    bucket_name="non_existing_bucket_12345",
                    bucket_path="path/",
                    client=mock_client,
                )
                assert storage.bucket_name == "non_existing_bucket_12345"
                assert storage.bucket_path == "path/"

    def test_init_with_bucket_path_ending_without_slash(self):
        with patch("google.cloud.storage.Bucket", spec=Bucket):
            with patch("google.cloud.storage.Client", spec=Client) as mock_client:
                storage = gcloud.GoogleStorage(
                    bucket_name="non_existing_bucket_12345",
                    bucket_path="path",
                    client=mock_client,
                )
                assert storage.bucket_name == "non_existing_bucket_12345"
                assert storage.bucket_path == "path/"

    def test_fails_when_bucket_does_not_exist(self):
        with patch("imgdl.storage.gcloud.Bucket", spec=Bucket) as mock_bucket:
            mock_bucket.return_value.exists.return_value = False
            with patch("google.cloud.storage.Client", spec=Client) as mock_client:
                with pytest.raises(ValueError):
                    gcloud.GoogleStorage(
                        bucket_name="non_existing_bucket_12345",
                        bucket_path="path",
                        client=mock_client,
                    )

    def test_get_filepath(self, tmp_path):
        with patch("google.cloud.storage.Bucket", spec=Bucket):
            with patch("google.cloud.storage.Client", spec=Client) as mock_client:
                storage = gcloud.GoogleStorage(
                    bucket_name="non_existing_bucket_12345",
                    bucket_path="path",
                    client=mock_client,
                )
                assert storage.bucket_name == "non_existing_bucket_12345"
                assert storage.bucket_path == "path/"
                filepath = storage.get_filepath(TEST_URL)
                assert filepath == storage.bucket_path + (TEST_URL_HASH + ".jpg")

                storage = gcloud.GoogleStorage(
                    bucket_name="non_existing_bucket_12345",
                    bucket_path="path/",
                    client=mock_client,
                )
                assert storage.bucket_name == "non_existing_bucket_12345"
                assert storage.bucket_path == "path/"
                filepath = storage.get_filepath(TEST_URL)
                assert filepath == storage.bucket_path + (TEST_URL_HASH + ".jpg")
