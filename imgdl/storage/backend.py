from pathlib import Path
from typing import Union

from .base import BaseStorage
from .local import LocalStorage

try:
    from .gcloud import GoogleStorage

    GCLOUD = True
except ImportError:
    GCLOUD = False


def resolve_storage_backend(store_path: Union[Path, str]) -> BaseStorage:
    if isinstance(store_path, str) and store_path.startswith("gs://"):
        if not GCLOUD:
            raise ImportError(
                "Cannot use google storage backend. "
                "If you want to proceed, please install google-cloud-storage"
            )
        uri = store_path.replace("gs://", "")
        if "/" in uri:
            bucket_name, bucket_path = uri.split("/", maxsplit=1)
        else:
            bucket_name = uri
            bucket_path = ""

        return GoogleStorage(bucket_name=bucket_name, bucket_path=bucket_path)

    else:
        return LocalStorage(store_path=Path(store_path))
