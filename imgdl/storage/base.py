import hashlib


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
