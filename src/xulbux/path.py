"""
This module provides the `Path` class, which includes methods to work with file and directory paths.
"""

from .base.exceptions import PathNotFoundError

from typing import Optional, cast
import tempfile as _tempfile
import difflib as _difflib
import shutil as _shutil
import sys as _sys
import os as _os


class _Cwd:

    def __get__(self, obj, owner=None):
        return _os.getcwd()


class _ScriptDir:

    def __get__(self, obj, owner=None):
        if getattr(_sys, "frozen", False):
            base_path = _os.path.dirname(_sys.executable)
        else:
            main_module = _sys.modules["__main__"]
            if hasattr(main_module, "__file__") and main_module.__file__ is not None:
                base_path = _os.path.dirname(_os.path.abspath(main_module.__file__))
            elif (hasattr(main_module, "__spec__") and main_module.__spec__ and main_module.__spec__.origin is not None):
                base_path = _os.path.dirname(_os.path.abspath(main_module.__spec__.origin))
            else:
                raise RuntimeError("Can only get base directory if accessed from a file.")
        return base_path


class Path:
    """This class provides methods to work with file and directory paths."""

    cwd: str = cast(str, _Cwd())
    """The path to the current working directory."""
    script_dir: str = cast(str, _ScriptDir())
    """The path to the directory of the current script."""

    @staticmethod
    def extend(
        rel_path: str,
        search_in: Optional[str | list[str]] = None,
        raise_error: bool = False,
        use_closest_match: bool = False,
    ) -> Optional[str]:
        """Tries to resolve and extend a relative path to an absolute path.\n
        -------------------------------------------------------------------------------------------
        - `rel_path` -⠀the relative path to extend
        - `search_in` -⠀a directory or a list of directories to search in,
          in addition to the predefined directories (see exact procedure below)
        - `raise_error` -⠀if true, raises a `PathNotFoundError` if
          the path couldn't be found (otherwise it returns `None`)
        - `use_closest_match` -⠀if true, it will try to find the closest matching file/folder
          names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`\n
        -------------------------------------------------------------------------------------------
        If the `rel_path` couldn't be located in predefined directories,
        it will be searched in the `search_in` directory/s.<br>
        If the `rel_path` is still not found, it returns `None` or
        raises a `PathNotFoundError` if `raise_error` is true."""
        search_dirs: list[str] = []

        if not isinstance(rel_path, str):
            raise TypeError(f"The 'rel_path' parameter must be a string, got {type(rel_path)}")
        if search_in is not None:
            if isinstance(search_in, str):
                search_dirs.extend([search_in])
            elif isinstance(search_in, list):
                if not all(isinstance(item, str) for item in search_in):
                    raise TypeError("All items in the 'search_in' list must be strings.")
                search_dirs.extend(search_in)
            else:
                raise TypeError(f"The 'search_in' parameter must be a string or a list of strings, got {type(search_in)}")
        if not isinstance(raise_error, bool):
            raise TypeError(f"The 'raise_error' parameter must be a boolean, got {type(raise_error)}")
        if not isinstance(use_closest_match, bool):
            raise TypeError(f"The 'use_closest_match' parameter must be a boolean, got {type(use_closest_match)}")

        if rel_path == "":
            if raise_error:
                raise PathNotFoundError("Path is empty.")
            else:
                return None
        elif _os.path.isabs(rel_path):
            return rel_path

        def get_closest_match(dir: str, part: str) -> Optional[str]:
            try:
                matches = _difflib.get_close_matches(part, _os.listdir(dir), n=1, cutoff=0.6)
                return matches[0] if matches else None
            except Exception:
                return None

        def find_path(start: str, parts: list[str]) -> Optional[str]:
            current = start

            for part in parts:
                if _os.path.isfile(current):
                    return current
                closest_match = get_closest_match(current, part) if use_closest_match else part
                current = _os.path.join(current, closest_match) if closest_match else None
                if current is None:
                    return None

            return current if _os.path.exists(current) and current != start else None

        def expand_env_path(p: str) -> str:
            if "%" not in p:
                return p

            for i in range(1, len(parts := p.split("%")), 2):
                if parts[i].upper() in _os.environ:
                    parts[i] = _os.environ[parts[i].upper()]

            return "".join(parts)

        rel_path = _os.path.normpath(expand_env_path(rel_path))

        if _os.path.isabs(rel_path):
            drive, rel_path = _os.path.splitdrive(rel_path)
            rel_path = rel_path.lstrip(_os.sep)
            search_dirs.extend([(drive + _os.sep) if drive else _os.sep])
        else:
            rel_path = rel_path.lstrip(_os.sep)
            search_dirs.extend([_os.getcwd(), Path.script_dir, _os.path.expanduser("~"), _tempfile.gettempdir()])

        for search_dir in search_dirs:
            if _os.path.exists(full_path := _os.path.join(search_dir, rel_path)):
                return full_path
            if (match := find_path(search_dir, rel_path.split(_os.sep)) if use_closest_match else None):
                return match

        if raise_error:
            raise PathNotFoundError(f"Path '{rel_path}' not found in specified directories.")
        else:
            return None

    @staticmethod
    def extend_or_make(
        rel_path: str,
        search_in: Optional[str | list[str]] = None,
        prefer_script_dir: bool = True,
        use_closest_match: bool = False,
    ) -> str:
        """Tries to locate and extend a relative path to an absolute path, and if the `rel_path`
        couldn't be located, it generates a path, as if it was located.\n
        -------------------------------------------------------------------------------------------
        - `rel_path` -⠀the relative path to extend or make
        - `search_in` -⠀a directory or a list of directories to search in,
          in addition to the predefined directories (see exact procedure below)
        - `prefer_script_dir` -⠀if true, the script directory is preferred
          when making a new path (otherwise the CWD is preferred)
        - `use_closest_match` -⠀if true, it will try to find the closest matching file/folder
          names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`\n
        -------------------------------------------------------------------------------------------
        If the `rel_path` couldn't be located in predefined directories,
        it will be searched in the `search_in` directory/s.<br>
        If the `rel_path` is still not found, it will makes a path
        that points to where the `rel_path` would be in the script directory,
        even though the `rel_path` doesn't exist there.<br>
        If `prefer_script_dir` is false, it will instead make a path
        that points to where the `rel_path` would be in the CWD."""
        # THE 'rel_path' PARAM IS CHECKED IN 'Path.extend()'
        # THE 'search_in' PARAM IS CHECKED IN 'Path.extend()'
        if not isinstance(prefer_script_dir, bool):
            raise TypeError(f"The 'prefer_script_dir' parameter must be a boolean, got {type(prefer_script_dir)}")
        # THE 'use_closest_match' PARAM IS CHECKED IN 'Path.extend()'

        try:
            return str(Path.extend( \
                rel_path=rel_path,
                search_in=search_in,
                raise_error=True,
                use_closest_match=use_closest_match,
            ))
        except PathNotFoundError:
            return _os.path.join(
                Path.script_dir if prefer_script_dir else _os.getcwd(),
                _os.path.normpath(rel_path),
            )

    @staticmethod
    def remove(path: str, only_content: bool = False) -> None:
        """Removes the directory or the directory's content at the specified path.\n
        -----------------------------------------------------------------------------
        - `path` -⠀the path to the directory or file to remove
        - `only_content` -⠀if true, only the content of the directory is removed
          and the directory itself is kept"""
        if not isinstance(path, str):
            raise TypeError(f"The 'path' parameter must be a string, got {type(path)}")
        if not isinstance(only_content, bool):
            raise TypeError(f"The 'only_content' parameter must be a boolean, got {type(only_content)}")

        if not _os.path.exists(path):
            return None

        if not only_content:
            if _os.path.isfile(path) or _os.path.islink(path):
                _os.unlink(path)
            elif _os.path.isdir(path):
                _shutil.rmtree(path)

        elif _os.path.isdir(path):
            for filename in _os.listdir(path):
                file_path = _os.path.join(path, filename)
                try:
                    if _os.path.isfile(file_path) or _os.path.islink(file_path):
                        _os.unlink(file_path)
                    elif _os.path.isdir(file_path):
                        _shutil.rmtree(file_path)
                except Exception as e:
                    raise Exception(f"Failed to delete {file_path}. Reason: {e}")
