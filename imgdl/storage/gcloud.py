from dataclasses import dataclass, field
from io import BytesIO

from google.cloud.storage import Bucket, Client
from PIL import Image

from .base import BaseStorage


@dataclass
class GoogleStorage(BaseStorage):
    bucket_name: str
    bucket_path: str = ""
    client: Client = field(default_factory=Client)

    def __post_init__(self):
        self.bucket = Bucket(client=self.client, name=self.bucket_name)
        if not self.bucket.exists():
            raise ValueError("Bucket does not exists or you do not have permission")

        if (len(self.bucket_path) > 0) and (self.bucket_path[-1] != "/"):
            self.bucket_path += "/"

    def exists(self, path: str):
        return self.bucket.blob(path).exists()

    def save(self, img: Image.Image, path: str):
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        blob = self.bucket.blob(path)
        blob.upload_from_string(buffer.getvalue(), content_type="image/jpg")

    def get_filepath(self, url):
        return self.bucket_path + self.get_filename(url)
