"""
Functions for modifying and checking the systems environment-variables:
- `EnvVars.get_paths()`
- `EnvVars.has_path()`
- `EnvVars.add_path()`
"""

from .xx_console import Console
from .xx_data import Data
from .xx_path import Path


import os as _os
import sys as _sys


class EnvVars:

    @staticmethod
    def get_paths(as_list: bool = False) -> str | list:
        """Get the PATH environment variable."""
        paths = _os.environ.get("PATH", "")
        return paths.split(_os.pathsep) if as_list else paths

    @staticmethod
    def has_path(path: str = None, cwd: bool = False, base_dir: bool = False) -> bool:
        """Check if a path is present in the PATH environment variable."""
        if cwd:
            path = _os.getcwd()
        elif base_dir:
            path = Path.get(base_dir=True)
        elif path is None:
            raise ValueError("A path must be provided or either 'cwd' or 'base_dir' must be True.")
        paths = EnvVars.get_paths(as_list=True)
        return _os.path.normpath(path) in [_os.path.normpath(p) for p in paths]

    @staticmethod
    def add_path(
        path: str = None,
        cwd: bool = False,
        base_dir: bool = False,
    ) -> None:
        """Add a path to the PATH environment variable."""
        path = EnvVars.__get(path, cwd, base_dir)
        if not EnvVars.has_path(path):
            paths = EnvVars.get_paths(as_list=True)
            paths.append(path)
            final_paths = EnvVars.__sort_paths(paths)
            _os.environ["PATH"] = _os.pathsep.join(final_paths)
            EnvVars.__make_persistent(path)

    @staticmethod
    def remove_path(
        path: str = None,
        cwd: bool = False,
        base_dir: bool = False,
    ) -> None:
        """Remove a path from the PATH environment variable."""
        path = EnvVars.__get(path, cwd, base_dir)
        if EnvVars.has_path(path):
            paths = EnvVars.get_paths(as_list=True)
            paths = [p for p in paths if _os.path.normpath(p) != path]
            final_paths = EnvVars.__sort_paths(paths)
            _os.environ["PATH"] = _os.pathsep.join(final_paths)
            EnvVars.__make_persistent(path, remove=True)

    @staticmethod
    def __get(
        path: str = None,
        cwd: bool = False,
        base_dir: bool = False,
    ) -> list:
        """Get and/or normalize the paths.<br>
        Raise an error if no path is provided and<br>
        neither `cwd` or `base_dir` is `True`."""
        if cwd:
            path = _os.getcwd()
        elif base_dir:
            path = Path.get(base_dir=True)
        elif path is None:
            raise ValueError("A path must be provided or either 'cwd' or 'base_dir' must be True.")
        return _os.path.normpath(path)

    @staticmethod
    def __add_sort_paths(add_path: str, current_paths: str) -> str:
        """Add a path to the existing paths-string and sort it again."""
        final_paths = Data.remove_empty_items(
            Data.remove_duplicates(f"{add_path}{_os.pathsep}{current_paths}".split(_os.pathsep))
        ).sort()
        return f"{_os.pathsep.join(final_paths)}{_os.pathsep}"

    @staticmethod
    def __make_persistent(path: str, remove: bool = False) -> None:
        """Make PATH changes persistent across sessions."""
        if _sys.platform == "win32":  # Windows
            try:
                import winreg as _winreg

                key = _winreg.OpenKey(
                    _winreg.HKEY_CURRENT_USER,
                    "Environment",
                    0,
                    _winreg.KEY_ALL_ACCESS,
                )
                current_path = _winreg.QueryValueEx(key, "PATH")[0]
                if remove:
                    new_path = _os.pathsep.join([p for p in current_path.split(_os.pathsep) if _os.path.normpath(p) != path])
                else:
                    new_path = f"{current_path}{_os.pathsep}{path}"
                _winreg.SetValueEx(key, "PATH", 0, _winreg.REG_EXPAND_SZ, new_path)
                _winreg.CloseKey(key)
            except ImportError:
                Console.warn("Unable to make persistent changes on Windows.")
        else:  # UNIX-like (Linux/macOS)
            shell_rc_file = _os.path.expanduser(
                "~/.bashrc" if _os.path.exists(_os.path.expanduser("~/.bashrc")) else "~/.zshrc"
            )
            with open(shell_rc_file, "r+") as f:
                content = f.read()
                f.seek(0)
                if remove:
                    new_content = [line for line in content.splitlines() if not line.endswith(f':{path}"')]
                    f.write("\n".join(new_content))
                else:
                    f.write(f'{content.rstrip()}\n# Added by XulbuX\nexport PATH="$PATH:{path}"\n')
                f.truncate()
            _os.system(f"source {shell_rc_file}")
