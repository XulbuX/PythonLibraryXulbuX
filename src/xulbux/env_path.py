"""
Provides utilities for interacting with the system's PATH environment variable.

This includes adding, checking, and removing paths, as well as resolving
script or executable locations.
"""

from . import file_sys as _file_sys_module

import os as _os
import subprocess as _subprocess
import sys as _sys
from pathlib import Path
from typing import Literal, overload


@overload
def paths(*, as_list: Literal[True]) -> list[Path]: ...
@overload
def paths(*, as_list: Literal[False] = False) -> Path: ...
@overload
def paths(*, as_list: bool = False) -> Path | list[Path]: ...


def paths(*, as_list: bool = False) -> Path | list[Path]:
    """Get the PATH environment variable.\n
    ---------------------------------------------------------------------------------------------------
    *   `as_list` – If true, returns the paths as a list of `Path`s; otherwise, as a single `Path`."""

    paths_str = _os.environ.get("PATH", "")

    if as_list:
        return [Path(path) for path in paths_str.split(_os.pathsep) if path]

    return Path(paths_str)


def has_path(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> bool:
    """Check if a path is present in the PATH environment variable.\n
    ---------------------------------------------------------------------------
    *   `path` – The path to check for.
    *   `cwd` – If true, uses the current working directory as the path.
    *   `base_dir` – If true, uses the script's base directory as the path."""

    return bool(_get(path, cwd=cwd, base_dir=base_dir).resolve() in {path.resolve() for path in paths(as_list=True)})


def add_path(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> None:
    """Add a path to the PATH environment variable.\n
    ---------------------------------------------------------------------------
    *   `path` – The path to add.
    *   `cwd` – If true, uses the current working directory as the path.
    *   `base_dir` – If true, uses the script's base directory as the path."""

    path_obj = _get(path, cwd=cwd, base_dir=base_dir)

    if not has_path(path_obj):
        _persistent(path_obj)


def remove_path(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> None:
    """Remove a path from the PATH environment variable.\n
    ---------------------------------------------------------------------------
    *   `path` – The path to remove.
    *   `cwd` – If true, uses the current working directory as the path.
    *   `base_dir` – If true, uses the script's base directory as the path."""

    path_obj = _get(path, cwd=cwd, base_dir=base_dir)

    if has_path(path_obj):
        _persistent(path_obj, remove=True)


def _get(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> Path:
    """Internal method to get the normalized `path`, CWD path or script directory path.\n
    --------------------------------------------------------------------------------------
    Raise an error if no path is provided and neither `cwd` or `base_dir` is true."""

    if cwd:
        if base_dir:
            raise ValueError("Both 'cwd' and 'base_dir' cannot be True at the same time.")
        return _file_sys_module.get_cwd()
    elif base_dir:
        return _file_sys_module.get_script_dir()

    if path is None:
        raise ValueError("No path provided.\nPlease provide a 'path' or set either 'cwd' or 'base_dir' to True.")

    return Path(path) if isinstance(path, str) else path


def _persistent(path: Path, /, *, remove: bool = False) -> None:
    """Internal method to add or remove a path from the PATH environment variable,<br>
    persistently, across sessions, as well as the current session."""

    current_paths = paths(as_list=True)
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
    _os.environ["PATH"] = new_path = _os.pathsep.join(dict.fromkeys([path for path in path_strings if path]))

    # Windows:
    if _sys.platform == "win32":
        try:
            winreg = __import__("winreg")
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)

        except Exception as exc:
            raise RuntimeError(f"Failed to update PATH in registry:\n  {str(exc).replace('\n', '  \n')}") from exc

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
                file.write(f'{content.rstrip()}\n# Added by `python-lib-xulbux`.\nexport PATH="{new_path}"\n')

            file.truncate()

        _subprocess.run(f"source {shell_rc_file}", shell=True, executable="/bin/bash")
