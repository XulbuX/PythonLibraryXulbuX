"""
Provides file system and path resolution utilities.

Includes fuzzy matching, recursive searching, safe directory creation,
and dynamic access to common paths like `cwd` and `home`.
"""

from . import string as _string_module
from .base.exceptions import PathNotFoundError, SameContentFileExistsError
from .base.types import PathsList

import difflib as _difflib
import os as _os
import shutil as _shutil
import sys as _sys
import tempfile as _tempfile
from contextlib import suppress as _suppress
from pathlib import Path


def get_cwd() -> Path:
    """The path to the current working directory."""

    return Path.cwd()


def get_home() -> Path:
    """The path to the user's home directory."""

    return Path.home()


def get_script_dir() -> Path:
    """The path to the directory of the current script."""

    if getattr(_sys, "frozen", False):
        base_path = Path(_sys.executable).parent

    else:
        main_module = _sys.modules["__main__"]

        if hasattr(main_module, "__file__") and main_module.__file__ is not None:
            base_path = Path(main_module.__file__).resolve().parent
        elif hasattr(main_module, "__spec__") and main_module.__spec__ and main_module.__spec__.origin is not None:
            base_path = Path(main_module.__spec__.origin).resolve().parent
        else:
            raise RuntimeError("Can only get base directory if accessed from a file")

    return base_path


def resolve_path(
    rel_path: Path | str,
    /,
    search_in: Path | str | PathsList | None = None,
    *,
    fuzzy_match: bool = False,
    raise_error: bool = False,
) -> Path | None:
    """Tries to resolve and extend a relative path to an absolute path.\n
    ----------------------------------------------------------------------------------------------------
    *   `rel_path` – The relative path to extend.
    *   `search_in` – A directory or a list of directories to search in,<br>
        in addition to the predefined directories (see exact procedure below).
    *   `fuzzy_match` – If true, it will try to find the closest matching file/folder<br>
        names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`.
    *   `raise_error` – If true, raises a `PathNotFoundError` if<br>
        the path couldn't be found (otherwise it returns `None`).\n
    ----------------------------------------------------------------------------------------------------
    If the `rel_path` couldn't be located in predefined directories,<br>
    it will be searched in the `search_in` directory/s.\n
    If the `rel_path` is still not found, it returns `None` or<br>
    raises a `PathNotFoundError` if `raise_error` is true.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Resolve a relative file with fuzzy matching:
    resolved_path = xx.file_sys.resolve_path("config.json", search_in="./settings", fuzzy_match=True)
    ```"""

    search_dirs: list[Path] = []
    path: Path

    if isinstance(rel_path, str):
        if rel_path == "":
            if raise_error:
                raise PathNotFoundError("Given 'rel_path' is an empty string")
            return None
        else:
            path = Path(rel_path)
    else:
        path = rel_path

    if path.is_absolute():
        return path

    if search_in is not None:
        if isinstance(search_in, (str, Path)):
            search_dirs.extend([Path(search_in)])
        else:
            search_dirs.extend([Path(path) for path in search_in])

    return _ResolvePathHelper(path, search_dirs=search_dirs, fuzzy_match=fuzzy_match, raise_error=raise_error)()


def resolve_or_create_path(
    rel_path: Path | str,
    /,
    search_in: Path | str | PathsList | None = None,
    *,
    prefer_script_dir: bool = True,
    fuzzy_match: bool = False,
) -> Path:
    """Tries to locate and extend a relative path to an absolute path, and if<br>
    the `rel_path` couldn't be located, it generates a path, as if it was located.\n
    ----------------------------------------------------------------------------------------------------
    *   `rel_path` – The relative path to extend or make.
    *   `search_in` – A directory or a list of directories to search in,<br>
        in addition to the predefined directories (see exact procedure below).
    *   `prefer_script_dir` – If true, the script directory is preferred<br>
        when making a new path (otherwise the CWD is preferred).
    *   `fuzzy_match` – If true, it will try to find the closest matching file/folder<br>
        names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`.\n
    ----------------------------------------------------------------------------------------------------
    If the `rel_path` couldn't be located in predefined directories,<br>
    it will be searched in the `search_in` directory/s.\n
    If the `rel_path` is still not found, it will makes a path<br>
    that points to where the `rel_path` would be in the script directory,<br>
    even though the `rel_path` doesn't exist there.\n
    If `prefer_script_dir` is false, it will instead make a path<br>
    that points to where the `rel_path` would be in the CWD.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Resolve existing file or compute fallback path in script directory:
    target_path = xx.file_sys.resolve_or_create_path("data/cache.json")
    ```"""

    try:
        return resolve_path(rel_path, search_in=search_in, raise_error=True, fuzzy_match=fuzzy_match) or Path()

    except PathNotFoundError:
        path = Path(str(rel_path))
        base_dir = get_script_dir() if prefer_script_dir else Path.cwd()
        return base_dir / path


def create_file(file_path: Path | str, content: str = "", /, *, force: bool = False) -> Path:
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
    file_path = xx.file_sys.create_file("output/result.txt", "Generated content", force=True)
    ```"""

    path = Path(file_path)

    if path.exists() and not force:
        with open(path, encoding="utf-8") as existing_file:
            if existing_file.read() == content:
                raise SameContentFileExistsError("Already created this file (nothing changed)")
        raise FileExistsError("File already exists")

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    return path.resolve()


def rename_file_ext(
    file_path: Path | str,
    new_extension: str,
    /,
    *,
    full_extension: bool = False,
    camel_case_filename: bool = False,
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
    new_path = xx.file_sys.rename_file_ext("archive.tar.gz", ".zip")  # archive.tar.zip

    # Replace full compound extension and convert to CamelCase:
    new_path = xx.file_sys.rename_file_ext(
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


def remove(path: Path | str, /, *, only_content: bool = False) -> None:
    """Removes the directory or the directory's content at the specified path.\n
    ----------------------------------------------------------------------------------------------------
    *   `path` – The path to the directory or file to remove.
    *   `only_content` – If true, only the content of the directory<br>
        is removed and the directory itself is kept."""

    if not (path_obj := Path(path)).exists():
        return None

    def _remove_item(item: Path) -> None:
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                _shutil.rmtree(item)
        except Exception as exc:
            raise RuntimeError(f"Failed to delete {item!r}:\n  {'\n  '.join(str(exc).splitlines())}") from exc

    if not only_content:
        _remove_item(path_obj)
    elif path_obj.is_dir():
        for child in path_obj.iterdir():
            _remove_item(child)
    else:
        raise NotADirectoryError(f"Cannot remove only_content of non-directory {path_obj!r}")


class _ResolvePathHelper:
    """Internal, callable helper class to find and resolve a relative path to an absolute path."""

    def __init__(self, rel_path: Path, /, search_dirs: list[Path], *, fuzzy_match: bool, raise_error: bool) -> None:
        self.rel_path: Path = rel_path
        self.search_dirs: list[Path] = search_dirs
        self.fuzzy_match: bool = fuzzy_match
        self.raise_error: bool = raise_error

    def __call__(self) -> Path | None:
        """Find the matching path for `self.rel_path` in `self.search_dirs`."""

        expanded_path = self.expand_env_vars(self.rel_path)

        if expanded_path.is_absolute():
            # Add root to search dirs:
            if expanded_path.drive:
                self.search_dirs.extend([Path(expanded_path.drive + _os.sep)])
            else:
                self.search_dirs.extend([Path(_os.sep)])

            expanded_path = Path(*expanded_path.parts[1:])  # Remove root from path parts for searching.

        else:
            # Add predefined search dirs:
            predefined_dirs = [get_cwd(), get_home()]
            with _suppress(RuntimeError):
                predefined_dirs.append(get_script_dir())
            predefined_dirs.append(Path(_tempfile.gettempdir()))
            self.search_dirs.extend(predefined_dirs)

        return self.search_in_dirs(expanded_path)

    @staticmethod
    def expand_env_vars(path: Path, /) -> Path:
        """Expand all environment variables in the given path."""

        if "%" not in (str_path := str(path)) and "$" not in str_path:
            return path

        return Path(_os.path.expandvars(str_path))

    def search_in_dirs(self, path: Path, /) -> Path | None:
        """Search for the path in all configured directories."""

        for search_dir in self.search_dirs:
            if (full_path := search_dir / path).exists():
                return full_path
            elif self.fuzzy_match and (match := self.find_path(search_dir, path, fuzzy_match=self.fuzzy_match)) is not None:
                return match

        if self.raise_error:
            raise PathNotFoundError(f"Path {self.rel_path!r} not found in specified directories")

        return None

    def find_path(self, base_dir: Path, target_path: Path, /, *, fuzzy_match: bool) -> Path | None:
        """Find a path by traversing the given parts from the base directory,<br>
        optionally using closest matches for each part."""

        current_path: Path = base_dir

        for part in target_path.parts:
            if current_path.is_file():
                return current_path
            elif (closest_match := self.get_closest_match(current_path, part) if fuzzy_match else part) is None:
                return None
            current_path = current_path / closest_match

        return current_path if current_path.exists() and current_path != base_dir else None

    @staticmethod
    def get_closest_match(directory: Path, path_part: str, /) -> str | None:
        """Internal method to get the closest matching file or folder name<br>
        in the given directory for the given path part."""

        try:
            return (
                matches[0]
                if (
                    matches := _difflib.get_close_matches(
                        path_part, [item.name for item in directory.iterdir()], n=1, cutoff=0.6
                    )
                )
                else None
            )

        except Exception:
            return None
