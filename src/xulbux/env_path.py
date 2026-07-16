"""
This module provides the `EnvPath` class, which includes
methods to work with the PATH environment variable.
"""

from .file_sys import FileSys

from typing import Optional, Literal, overload
from pathlib import Path
import subprocess as _subprocess
import sys as _sys
import os as _os


class EnvPath:
    """This class includes methods to work with the PATH environment variable."""

    @overload
    @classmethod
    def paths(cls, *, as_list: Literal[True]) -> list[Path]:
        ...

    @overload
    @classmethod
    def paths(cls, *, as_list: Literal[False] = False) -> Path:
        ...

    @overload
    @classmethod
    def paths(cls, *, as_list: bool = False) -> Path | list[Path]:
        ...

    @classmethod
    def paths(cls, *, as_list: bool = False) -> Path | list[Path]:
        """Get the PATH environment variable.\n
        ---------------------------------------------------------------------------------------------------
        *   `as_list` – If true, returns the paths as a list of `Path`s; otherwise, as a single `Path`."""

        paths_str = _os.environ.get("PATH", "")

        if as_list:
            return [Path(path) for path in paths_str.split(_os.pathsep) if path]

        return Path(paths_str)

    @classmethod
    def has_path(cls, path: Optional[Path | str] = None, /, *, cwd: bool = False, base_dir: bool = False) -> bool:
        """Check if a path is present in the PATH environment variable.\n
        ---------------------------------------------------------------------------
        *   `path` – The path to check for.
        *   `cwd` – If true, uses the current working directory as the path.
        *   `base_dir` – If true, uses the script's base directory as the path."""

        return bool(
            cls._get(path, cwd=cwd, base_dir=base_dir).resolve() \
            in {path.resolve() for path in cls.paths(as_list=True)}
        )

    @classmethod
    def add_path(cls, path: Optional[Path | str] = None, /, *, cwd: bool = False, base_dir: bool = False) -> None:
        """Add a path to the PATH environment variable.\n
        ---------------------------------------------------------------------------
        *   `path` – The path to add.
        *   `cwd` – If true, uses the current working directory as the path.
        *   `base_dir` – If true, uses the script's base directory as the path."""

        path_obj = cls._get(path, cwd=cwd, base_dir=base_dir)

        if not cls.has_path(path_obj):
            cls._persistent(path_obj)

    @classmethod
    def remove_path(cls, path: Optional[Path | str] = None, /, *, cwd: bool = False, base_dir: bool = False) -> None:
        """Remove a path from the PATH environment variable.\n
        ---------------------------------------------------------------------------
        *   `path` – The path to remove.
        *   `cwd` – If true, uses the current working directory as the path.
        *   `base_dir` – If true, uses the script's base directory as the path."""

        path_obj = cls._get(path, cwd=cwd, base_dir=base_dir)

        if cls.has_path(path_obj):
            cls._persistent(path_obj, remove=True)

    @staticmethod
    def _get(path: Optional[Path | str] = None, /, *, cwd: bool = False, base_dir: bool = False) -> Path:
        """Internal method to get the normalized `path`, CWD path or script directory path.\n
        --------------------------------------------------------------------------------------
        Raise an error if no path is provided and neither `cwd` or `base_dir` is true."""

        if cwd:
            if base_dir:
                raise ValueError("Both 'cwd' and 'base_dir' cannot be True at the same time.")
            return FileSys.cwd
        elif base_dir:
            return FileSys.script_dir

        if path is None:
            raise ValueError("No path provided.\nPlease provide a 'path' or set either 'cwd' or 'base_dir' to True.")

        return Path(path) if isinstance(path, str) else path

    @classmethod
    def _persistent(cls, path: Path, /, *, remove: bool = False) -> None:
        """Internal method to add or remove a path from the PATH environment variable,<br>
        persistently, across sessions, as well as the current session."""

        current_paths = cls.paths(as_list=True)
        path_resolved = path.resolve()

        if remove:
            # Filter out the path to remove:
            current_paths = [path for path in current_paths if path.resolve() != path_resolved]
        else:
            # Add the new path if not already present:
            if path_resolved not in {path.resolve() for path in current_paths}:
                current_paths = [*current_paths, path_resolved]

        # Convert to strings only for setting the environment variable:
        path_strings = [str(path) for path in current_paths]
        _os.environ["PATH"] = new_path = _os.pathsep.join(dict.fromkeys(filter(bool, path_strings)))

        # Windows:
        if _sys.platform == "win32":
            try:
                _winreg = __import__("winreg")
                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Environment", 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(key, "PATH", 0, _winreg.REG_EXPAND_SZ, new_path)
                _winreg.CloseKey(key)

            except Exception as exc:
                raise RuntimeError("Failed to update PATH in registry:\n  " + str(exc).replace("\n", "  \n"))

        # Unix-like (Linux/macOS):
        else:
            home_path = Path.home()
            bashrc = home_path / ".bashrc"
            zshrc = home_path / ".zshrc"
            shell_rc_file = bashrc if bashrc.exists() else zshrc

            with open(shell_rc_file, "r+") as file:
                content = file.read()
                file.seek(0)

                if remove:
                    new_content = [line for line in content.splitlines() if not line.endswith(f':{path_resolved}"')]
                    file.write("\n".join(new_content))
                else:
                    file.write(f"{content.rstrip()}\n# Added by `python-lib-xulbux`.\n"
                               f'export PATH="{new_path}"\n')

                file.truncate()

            _subprocess.run(f"source {shell_rc_file}", shell=True, executable='/bin/bash')
