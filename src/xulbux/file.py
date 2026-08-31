"""
Provides high-level object-oriented file manipulation.

Features include secure reading, writing, caching, locking,
and formatting file sizes or line counts.
"""

from . import string as _string_module
from .base.exceptions import SameContentFileExistsError

from pathlib import Path


def rename_extension(
    file_path: Path | str, new_extension: str, /, *, full_extension: bool = False, camel_case_filename: bool = False
) -> Path:
    """Rename the extension of a file.\n
    ----------------------------------------------------------------------------------------------------
    *   `file_path` – The path to the file whose extension should be changed.
    *   `new_extension` – The new extension for the file (with or without dot).
    *   `full_extension` – Whether to replace the full extension (e.g., `.tar.gz`)<br>
        or just the last part of it (e.g., `.gz`).
    *   `camel_case_filename` – Whether to convert the filename to CamelCase<br>
        in addition to changing the files extension.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Rename single extension:
    new_path = xx.file.rename_extension("archive.tar.gz", ".zip")  # archive.tar.zip

    # Replace full compound extension and convert to CamelCase:
    new_path = xx.file.rename_extension(
        "my_data_file.tar.gz",
        ".zip",
        full_extension=True,
        camel_case_filename=True,
    )  # MyDataFile.zip
    ```"""

    path = Path(file_path)
    filename_with_ext = path.name

    if full_extension:
        try:
            filename = filename_with_ext[: filename_with_ext.index(".")]
        except ValueError:
            filename = filename_with_ext
    else:
        filename = path.stem

    if camel_case_filename:
        filename = _string_module.to_camel_case(filename)
    if new_extension and not new_extension.startswith("."):
        new_extension = "." + new_extension

    return path.parent / f"{filename}{new_extension}"


def create(file_path: Path | str, content: str = "", /, *, force: bool = False) -> Path:
    """Create a file with or without content.\n
    ----------------------------------------------------------------------------------------------------
    *   `file_path` – The path where the file should be created.
    *   `content` – The content to write into the file.
    *   `force` – If true, will overwrite existing files without<br>
        throwing an error (errors explained below).\n
    ----------------------------------------------------------------------------------------------------
    The method will throw a `FileExistsError` if a file with the same<br>
    name already exists and a `SameContentFileExistsError` if a file<br>
    with the same name and same content already exists.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Create file safely or force overwrite:
    file_path = xx.file.create("output/result.txt", "Generated content", force=True)
    ```"""

    path = Path(file_path)

    if path.exists() and not force:
        with open(path, encoding="utf-8") as existing_file:
            existing_content = existing_file.read()
            if existing_content == content:
                raise SameContentFileExistsError("Already created this file (nothing changed)")
        raise FileExistsError("File already exists")

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    return path.resolve()
