"""
This module provides the `Path` class, which includes methods to work with file and directory paths.
"""

from .base.exceptions import PathNotFoundError

from typing import Optional
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

    cwd: str = _Cwd()  # type: ignore[assignment]
    """The path to the current working directory."""
    script_dir: str = _ScriptDir()  # type: ignore[assignment]
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
        if rel_path in {"", None}:
            if raise_error:
                raise PathNotFoundError("Path is empty.")
            return None
        elif _os.path.isabs(rel_path):
            return rel_path

        def get_closest_match(dir: str, part: str) -> Optional[str]:
            try:
                files_and_dirs = _os.listdir(dir)
                matches = _difflib.get_close_matches(part, files_and_dirs, n=1, cutoff=0.6)
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
            parts = p.split("%")
            for i in range(1, len(parts), 2):
                if parts[i].upper() in _os.environ:
                    parts[i] = _os.environ[parts[i].upper()]
            return "".join(parts)

        rel_path = _os.path.normpath(expand_env_path(rel_path))
        if _os.path.isabs(rel_path):
            drive, rel_path = _os.path.splitdrive(rel_path)
            rel_path = rel_path.lstrip(_os.sep)
            search_dirs = [(drive + _os.sep) if drive else _os.sep]
        else:
            rel_path = rel_path.lstrip(_os.sep)
            base_dir = Path.script_dir
            search_dirs = [
                _os.getcwd(),
                base_dir,
                _os.path.expanduser("~"),
                _tempfile.gettempdir(),
            ]
        if search_in:
            search_dirs.extend([search_in] if isinstance(search_in, str) else search_in)
        path_parts = rel_path.split(_os.sep)
        for search_dir in search_dirs:
            full_path = _os.path.join(search_dir, rel_path)
            if _os.path.exists(full_path):
                return full_path
            match = find_path(search_dir, path_parts) if use_closest_match else None
            if match:
                return match
        if raise_error:
            raise PathNotFoundError(f"Path '{rel_path}' not found in specified directories.")
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
        try:
            return str(Path.extend(rel_path, search_in, raise_error=True, use_closest_match=use_closest_match))
        except PathNotFoundError:
            normalized_rel_path = _os.path.normpath(rel_path)
            base = Path.script_dir if prefer_script_dir else _os.getcwd()
            return _os.path.join(base, normalized_rel_path)

    @staticmethod
    def remove(path: str, only_content: bool = False) -> None:
        """Removes the directory or the directory's content at the specified path.\n
        -----------------------------------------------------------------------------
        - `path` -⠀the path to the directory or file to remove
        - `only_content` -⠀if true, only the content of the directory is removed
          and the directory itself is kept"""
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
