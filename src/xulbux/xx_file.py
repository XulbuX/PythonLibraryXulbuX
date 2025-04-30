from .xx_string import String

import os as _os


class SameContentFileExistsError(FileExistsError):
    ...


class File:

    @staticmethod
    def rename_extension(
        file: str,
        new_extension: str,
        full_extension: bool = False,
        camel_case_filename: bool = False,
    ) -> str:
        """Rename the extension of a file.\n
        --------------------------------------------------------------------------
        If `full_extension` is true, everything after the first dot in the
        filename will be treated as the extension to replace (e.g. `.tar.gz`).
        Otherwise, only the part after the last dot is replaced (e.g. `.gz`).\n
        If the `camel_case_filename` parameter is true, the filename will be made
        CamelCase in addition to changing the files extension."""
        normalized_file = _os.path.normpath(file)
        directory, filename_with_ext = _os.path.split(normalized_file)
        if full_extension:
            try:
                first_dot_index = filename_with_ext.index('.')
                filename = filename_with_ext[:first_dot_index]
            except ValueError:
                filename = filename_with_ext
        else:
            filename, _ = _os.path.splitext(filename_with_ext)
        if camel_case_filename:
            filename = String.to_camel_case(filename)
        if new_extension and not new_extension.startswith('.'):
            new_extension = '.' + new_extension
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
