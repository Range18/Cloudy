from os import path
from urllib.parse import quote


def encode_relative_path(src_path, root):
    rel_path = path.relpath(src_path, root).replace("\\", "/")
    return quote(f"/{rel_path}")
