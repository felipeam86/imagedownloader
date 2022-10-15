import hashlib


def md5sum(fname):
    """Calculate the md5 checksum of a file without reading its whole content
    in memory.
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def to_bytes(text, encoding=None, errors="strict"):
    """Return the binary representation of `text`. If `text`
    is already a bytes object, return it as-is."""
    if isinstance(text, bytes):
        return text
    if not isinstance(text, str):
        raise TypeError(
            "to_bytes must receive a str or bytes "
            "object, got %s" % type(text).__name__
        )
    if encoding is None:
        encoding = "utf-8"
    return text.encode(encoding, errors)
