import os

import magic

# Get File Extension from file name
def get_file_extension(
    file_path: str,
) -> str:
    return os.path.splitext(file_path)[1]

# Get File's MIME Type from file
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
def get_file_mimetype(
    file_path: str,
) -> str:
    return magic.from_file(file_path, mime=True)
