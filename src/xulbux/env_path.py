from typing import Optional
import sys as _sys
import os as _os


class EnvPath:

    @staticmethod
    def paths(as_list: bool = False) -> str | list:
        """Get the PATH environment variable.\n
        ------------------------------------------------------------------------------
        - `as_list` -⠀if true, returns the paths as a list; otherwise, as a string"""
        if not isinstance(as_list, bool):
            raise TypeError(f"The 'as_list' parameter must be a boolean, got {type(as_list)}")

        paths = _os.environ.get("PATH", "")
        return paths.split(_os.pathsep) if as_list else paths

    @staticmethod
    def has_path(path: Optional[str] = None, cwd: bool = False, base_dir: bool = False) -> bool:
        """Check if a path is present in the PATH environment variable.\n
        ------------------------------------------------------------------------
        - `path` -⠀the path to check for
        - `cwd` -⠀if true, uses the current working directory as the path
        - `base_dir` -⠀if true, uses the script's base directory as the path"""
        if not isinstance(path, (str, type(None))):
            raise TypeError(f"The 'path' parameter must be a string or None, got {type(path)}")
        if not isinstance(cwd, bool):
            raise TypeError(f"The 'cwd' parameter must be a boolean, got {type(cwd)}")
        if not isinstance(base_dir, bool):
            raise TypeError(f"The 'base_dir' parameter must be a boolean, got {type(base_dir)}")

        return _os.path.normpath(EnvPath.__get(path, cwd, base_dir)) \
            in {_os.path.normpath(p) for p in EnvPath.paths(as_list=True)}

    @staticmethod
    def add_path(path: Optional[str] = None, cwd: bool = False, base_dir: bool = False) -> None:
        """Add a path to the PATH environment variable.\n
        ------------------------------------------------------------------------
        - `path` -⠀the path to add
        - `cwd` -⠀if true, uses the current working directory as the path
        - `base_dir` -⠀if true, uses the script's base directory as the path"""
        if not isinstance(path, (str, type(None))):
            raise TypeError(f"The 'path' parameter must be a string or None, got {type(path)}")
        if not isinstance(cwd, bool):
            raise TypeError(f"The 'cwd' parameter must be a boolean, got {type(cwd)}")
        if not isinstance(base_dir, bool):
            raise TypeError(f"The 'base_dir' parameter must be a boolean, got {type(base_dir)}")

        if not EnvPath.has_path(path := EnvPath.__get(path, cwd, base_dir)):
            EnvPath.__persistent(path)

    @staticmethod
    def remove_path(path: Optional[str] = None, cwd: bool = False, base_dir: bool = False) -> None:
        """Remove a path from the PATH environment variable.\n
        ------------------------------------------------------------------------
        - `path` -⠀the path to remove
        - `cwd` -⠀if true, uses the current working directory as the path
        - `base_dir` -⠀if true, uses the script's base directory as the path"""
        if not isinstance(path, (str, type(None))):
            raise TypeError(f"The 'path' parameter must be a string or None, got {type(path)}")
        if not isinstance(cwd, bool):
            raise TypeError(f"The 'cwd' parameter must be a boolean, got {type(cwd)}")
        if not isinstance(base_dir, bool):
            raise TypeError(f"The 'base_dir' parameter must be a boolean, got {type(base_dir)}")

        if EnvPath.has_path(path := EnvPath.__get(path, cwd, base_dir)):
            EnvPath.__persistent(path, remove=True)

    @staticmethod
    def __get(path: Optional[str] = None, cwd: bool = False, base_dir: bool = False) -> str:
        """Get and/or normalize the given path, CWD or base directory.\n
        ------------------------------------------------------------------------------------
        Raise an error if no path is provided and neither `cwd` or `base_dir` is `True`."""
        if not isinstance(path, (str, type(None))):
            raise TypeError(f"The 'path' parameter must be a string or None, got {type(path)}")
        if not isinstance(cwd, bool):
            raise TypeError(f"The 'cwd' parameter must be a boolean, got {type(cwd)}")
        if not isinstance(base_dir, bool):
            raise TypeError(f"The 'base_dir' parameter must be a boolean, got {type(base_dir)}")

        return _os.path.normpath(EnvPath.__get(path, cwd, base_dir))

    @staticmethod
    def __persistent(path: str, remove: bool = False) -> None:
        """Add or remove a path from PATH persistently across sessions as well as the current session."""

        current_paths = list(EnvPath.paths(as_list=True))
        path = _os.path.normpath(path)

        if remove:
            current_paths = [p for p in current_paths if _os.path.normpath(p) != _os.path.normpath(path)]
        else:
            current_paths.append(path)

        _os.environ["PATH"] = new_path = _os.pathsep.join(sorted(set(filter(bool, current_paths))))

        if _sys.platform == "win32":  # WINDOWS
            try:
                import winreg as _winreg

                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Environment", 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(key, "PATH", 0, _winreg.REG_EXPAND_SZ, new_path)
                _winreg.CloseKey(key)
            except ImportError:
                print("Warning: Unable to make persistent changes on Windows.")

        else:  # UNIX-LIKE (LINUX/macOS)
            shell_rc_file = _os.path.expanduser(
                "~/.bashrc" if _os.path.exists(_os.path.expanduser("~/.bashrc")) else "~/.zshrc"
            )
            with open(shell_rc_file, "r+") as f:
                content = f.read()
                f.seek(0)
                if remove:
                    new_content = [l for l in content.splitlines() if not l.endswith(f':{path}"')]
                    f.write("\n".join(new_content))
                else:
                    f.write(f'{content.rstrip()}\n# Added by XulbuX\nexport PATH="{new_path}"\n')
                f.truncate()
            _os.system(f"source {shell_rc_file}")
