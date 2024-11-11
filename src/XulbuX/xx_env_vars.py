"""
Functions for modifying and checking the systems environment-variables:
- `EnvVars.get_paths()`
- `EnvVars.has_path()`
- `EnvVars.add_path()`
"""


from .xx_data import *
from .xx_path import *

import os as _os




class EnvVars:

    @staticmethod
    def get_paths(as_list:bool = False) -> str|list:
        paths = _os.environ.get('PATH')
        return paths.split(_os.pathsep) if as_list else paths

    @staticmethod
    def has_path(path:str = None, cwd:bool = False, base_dir:bool = False) -> bool:
        if cwd: path = _os.getcwd()
        if base_dir: path = Path.get(base_dir=True)
        paths = EnvVars.get_paths()
        return path in paths

    @staticmethod
    def __add_sort_paths(add_path:str, current_paths:str) -> str:
        final_paths = Data.remove_empty_items(Data.remove_duplicates(f'{add_path};{current_paths}'.split(_os.pathsep)))
        final_paths.sort()
        return f'{_os.pathsep.join(final_paths)};'

    @staticmethod
    def add_path(add_path:str = None, cwd:bool = False, base_dir:bool = False, persistent:bool = True) -> None:
        if cwd:
            add_path = _os.getcwd()
        if base_dir:
            add_path = Path.get(base_dir=True)
        if not EnvVars.has_path(add_path):
            final_paths = EnvVars.__add_sort_paths(add_path, EnvVars.get_paths())
            _os.environ['PATH'] = final_paths
            if persistent:
                if _os.name == 'nt':  # Windows
                    try:
                        import winreg
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
                        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, final_paths)
                        winreg.CloseKey(key)
                    except ImportError: raise ImportError('Unable to make persistent changes on Windows.')
                else:  # UNIX-LIKE (Linux/macOS)
                    shell_rc_file = _os.path.expanduser('~/.bashrc' if _os.path.exists(_os.path.expanduser('~/.bashrc')) else '~/.zshrc')
                    with open(shell_rc_file, 'a') as f:
                        f.write(f'\n# Added by XulbuX\nexport PATH="$PATH:{add_path}"\n')
                    _os.system(f'source {shell_rc_file}')
        else:
            raise ValueError(f'{add_path} is already in PATH.')
