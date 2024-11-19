"""
Functions for modifying and checking the systems environment-variables:
- `EnvVars.get_paths()`
- `EnvVars.has_path()`
- `EnvVars.add_path()`
"""

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
            EnvVars.__persistent(path, add=True)

    @staticmethod
    def remove_path(
        path: str = None,
        cwd: bool = False,
        base_dir: bool = False,
    ) -> None:
        """Remove a path from the PATH environment variable."""
        path = EnvVars.__get(path, cwd, base_dir)
        if EnvVars.has_path(path):
            EnvVars.__persistent(path, remove=True)

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
    def __persistent(path: str, add: bool = False, remove: bool = False) -> None:
        """Add or remove a path from PATH persistently across sessions as well as the current session."""
        if add == remove:
            raise ValueError("Either add or remove must be True, but not both.")
        current_paths = EnvVars.get_paths(as_list=True)
        path = _os.path.normpath(path)
        if remove:
            current_paths = [p for p in current_paths if _os.path.normpath(p) != path]
        elif add:
            current_paths.append(path)
        final_paths = EnvVars.__sort_paths(current_paths)
        new_path = _os.pathsep.join(final_paths)
        _os.environ["PATH"] = new_path
        if _sys.platform == "win32":  # Windows
            try:
                import winreg as _winreg

                key = _winreg.OpenKey(
                    _winreg.HKEY_CURRENT_USER,
                    "Environment",
                    0,
                    _winreg.KEY_ALL_ACCESS,
                )
                _winreg.SetValueEx(key, "PATH", 0, _winreg.REG_EXPAND_SZ, new_path)
                _winreg.CloseKey(key)
            except ImportError:
                print("Warning: Unable to make persistent changes on Windows.")
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
                    f.write(f'{content.rstrip()}\n# Added by XulbuX\nexport PATH="{new_path}"\n')
                f.truncate()
            _os.system(f"source {shell_rc_file}")
