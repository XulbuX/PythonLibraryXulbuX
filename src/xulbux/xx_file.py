from .xx_string import String
from .xx_path import Path

import os as _os


class File:

    @staticmethod
    def rename_extension(
        file: str,
        new_extension: str,
        camel_case_filename: bool = False,
    ) -> str:
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
    def create(
        file: str,
        content: str = "",
        force: bool = False,
    ) -> str:
        """Create a file with ot without content.\n
        ------------------------------------------------------------------------
        The function will throw a `FileExistsError` if the file already exists.
        To always overwrite the file, set the `force` parameter to `True`."""
        if _os.path.exists(file) and not force:
            with open(file, "r", encoding="utf-8") as existing_file:
                existing_content = existing_file.read()
                if existing_content == content:
                    raise FileExistsError("Already created this file. (nothing changed)")
            raise FileExistsError("File already exists.")
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)
        full_path = _os.path.abspath(file)
        return full_path

    @staticmethod
    def extend_or_make_path(
        file: str,
        search_in: str | list[str] = None,
        prefer_base_dir: bool = True,
        correct_paths: bool = False,
    ) -> str:
        """Tries to find the file and extend the path to be absolute and if the file was not found:\n
        Generate the absolute path to the file in the CWD or the running program's base-directory.\n
        ----------------------------------------------------------------------------------------------
        If the `file` is not found in predefined directories, it will be searched in the `search_in`
        directory/directories. If the file is still not found, it will return the path to the file in
        the base-dir per default or to the file in the CWD if `prefer_base_dir` is set to `False`.\n
        ----------------------------------------------------------------------------------------------
        If `correct_paths` is true, it is possible to have typos in the `search_in` path/s and it
        will still find the file if it is under one of those paths."""
        try:
            return Path.extend(file, search_in, raise_error=True, correct_path=correct_paths)
        except FileNotFoundError:
            return _os.path.join(Path.get(base_dir=True), file) if prefer_base_dir else _os.path.join(_os.getcwd(), file)
