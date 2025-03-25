from .xx_string import String
from .xx_path import Path

import os as _os


# YAPF: disable
class SameContentFileExistsError(FileExistsError): ...
# YAPF: enable


class File:

    @staticmethod
    def rename_extension(file: str, new_extension: str, camel_case_filename: bool = False) -> str:
        """Rename the extension of a file.\n
        --------------------------------------------------------------------------
        If the `camel_case_filename` parameter is true, the filename will be made
        CamelCase in addition to changing the files extension."""
        directory, filename_with_ext = _os.path.split(file)
        filename = filename_with_ext.split(".")[0]
        if camel_case_filename:
            filename = String.to_camel_case(filename)
        return _os.path.join(directory, f"{filename}{new_extension}")

    @staticmethod
    def create(file: str, content: str = "", force: bool = False) -> str:
        """Create a file with ot without content.\n
        ----------------------------------------------------------------------
        The function will throw a `FileExistsError` if a file with the same
        name already exists and a `SameContentFileExistsError` if a file with
        the same name and content already exists.
        To always overwrite the file, set the `force` parameter to `True`."""
        if _os.path.exists(file) and not force:
            with open(file, "r", encoding="utf-8") as existing_file:
                existing_content = existing_file.read()
                if existing_content == content:
                    raise SameContentFileExistsError("Already created this file. (nothing changed)")
            raise FileExistsError("File already exists.")
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)
        full_path = _os.path.abspath(file)
        return full_path
