import os

import magic


def get_file_extension(
    file_path: str,
) -> str:
    return os.path.splitext(file_name)


def get_file_mimetype(
    file_path: str,
) -> str:
    return magic.from_file(file_path, mime=True)
