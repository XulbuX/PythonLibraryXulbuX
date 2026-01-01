"""
This module provides the `File` class, which includes
methods to work with files and file paths.
"""

from .base.exceptions import SameContentFileExistsError
from .string import String

import os as _os


class File:
    """This class includes methods to work with files and file paths."""

    @classmethod
    def rename_extension(
        cls,
        file_path: str,
        new_extension: str,
        full_extension: bool = False,
        camel_case_filename: bool = False,
    ) -> str:
        """Rename the extension of a file.\n
        ----------------------------------------------------------------------------
        - `file_path` -⠀the path to the file whose extension should be changed
        - `new_extension` -⠀the new extension for the file (with or without dot)
        - `full_extension` -⠀whether to replace the full extension (e.g. `.tar.gz`)
          or just the last part of it (e.g. `.gz`)
        - `camel_case_filename` -⠀whether to convert the filename to CamelCase
          in addition to changing the files extension"""
        normalized_file = _os.path.normpath(file_path)
        directory, filename_with_ext = _os.path.split(normalized_file)

        if full_extension:
            try:
                first_dot_index = filename_with_ext.index(".")
                filename = filename_with_ext[:first_dot_index]
            except ValueError:
                filename = filename_with_ext
        else:
            filename, _ = _os.path.splitext(filename_with_ext)

        if camel_case_filename:
            filename = String.to_camel_case(filename)
        if new_extension and not new_extension.startswith("."):
            new_extension = "." + new_extension

        return _os.path.join(directory, f"{filename}{new_extension}")

    @classmethod
    def create(cls, file_path: str, content: str = "", force: bool = False) -> str:
        """Create a file with ot without content.\n
        ------------------------------------------------------------------
        - `file_path` -⠀the path where the file should be created
        - `content` -⠀the content to write into the file
        - `force` -⠀if true, will overwrite existing files
          without throwing an error (errors explained below)\n
        ------------------------------------------------------------------
        The method will throw a `FileExistsError` if a file with the same
        name already exists and a `SameContentFileExistsError` if a file
        with the same name and same content already exists."""
        if _os.path.exists(file_path) and not force:
            with open(file_path, "r", encoding="utf-8") as existing_file:
                existing_content = existing_file.read()
                if existing_content == content:
                    raise SameContentFileExistsError("Already created this file. (nothing changed)")
            raise FileExistsError("File already exists.")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return _os.path.abspath(file_path)
