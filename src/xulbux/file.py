"""
This module provides the `File` class, which includes
methods to work with files and file paths.
"""

from .base.exceptions import SameContentFileExistsError
from .string import String

from pathlib import Path


class File:
    """This class includes methods to work with files and file paths."""

    @classmethod
    def rename_extension(
        cls,
        file_path: Path | str,
        new_extension: str,
        /,
        *,
        full_extension: bool = False,
        camel_case_filename: bool = False,
    ) -> Path:
        """Rename the extension of a file.\n
        ----------------------------------------------------------------------------------
        *   `file_path` – The path to the file whose extension should be changed.
        *   `new_extension` – The new extension for the file (with or without dot).
        *   `full_extension` – Whether to replace the full extension (e.g. `.tar.gz`)<br>
            or just the last part of it (e.g. `.gz`).
        *   `camel_case_filename` – Whether to convert the filename to CamelCase<br>
            in addition to changing the files extension."""

        path = Path(file_path)
        filename_with_ext = path.name

        if full_extension:
            try:
                first_dot_index = filename_with_ext.index(".")
                filename = filename_with_ext[:first_dot_index]
            except ValueError:
                filename = filename_with_ext
        else:
            filename = path.stem

        if camel_case_filename:
            filename = String.to_camel_case(filename)
        if new_extension and not new_extension.startswith("."):
            new_extension = "." + new_extension

        return path.parent / f"{filename}{new_extension}"

    @classmethod
    def create(cls, file_path: Path | str, content: str = "", /, *, force: bool = False) -> Path:
        """Create a file with ot without content.\n
        ----------------------------------------------------------------------
        *   `file_path` – The path where the file should be created.
        *   `content` – The content to write into the file.
        *   `force` – If true, will overwrite existing files without<br>
            throwing an error (errors explained below).
        ----------------------------------------------------------------------
        The method will throw a `FileExistsError` if a file with the same<br>
        name already exists and a `SameContentFileExistsError` if a file<br>
        with the same name and same content already exists."""

        path = Path(file_path)

        if path.exists() and not force:
            with open(path, "r", encoding="utf-8") as existing_file:
                existing_content = existing_file.read()
                if existing_content == content:
                    raise SameContentFileExistsError("Already created this file. (nothing changed)")
            raise FileExistsError("File already exists.")

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

        return path.resolve()
