import tempfile as _tempfile
import difflib as _difflib
import shutil as _shutil
import sys as _sys
import os as _os




class Path:

    @staticmethod
    def get(cwd:bool = False, base_dir:bool = False) -> str|list:
        paths = []
        if cwd:
            paths.append(_os.getcwd())
        if base_dir:
            if getattr(_sys, 'frozen', False):
                base_path = _os.path.dirname(_sys.executable)
            else:
                main_module = _sys.modules['__main__']
                if hasattr(main_module, '__file__'):
                    base_path = _os.path.dirname(_os.path.abspath(main_module.__file__))
                elif hasattr(main_module, '__spec__') and main_module.__spec__ and getattr(main_module.__spec__, 'origin', None):
                    base_path = _os.path.dirname(_os.path.abspath(main_module.__spec__.origin))
                else:
                    raise RuntimeError('Can only get base directory if ran from a file.')
            paths.append(base_path)
        return paths[0] if len(paths) == 1 else paths

    @staticmethod
    def extend(path:str, search_in:str|list[str] = None, raise_error:bool = False, correct_path:bool = False) -> str:
        if path in (None, ''):
            return path
        def get_closest_match(dir:str, part:str) -> str|None:
            try:
                files_and_dirs = _os.listdir(dir)
                matches = _difflib.get_close_matches(part, files_and_dirs, n=1, cutoff=0.6)
                return matches[0] if matches else None
            except:
                return None
        def find_path(start:str, parts:list[str]) -> str|None:
            current = start
            for part in parts:
                if _os.path.isfile(current):
                    return current
                closest_match = get_closest_match(current, part) if correct_path else part
                current = _os.path.join(current, closest_match) if closest_match else None
                if current is None:
                    return None
            return current if _os.path.exists(current) and current != start else None
        def expand_env_path(p:str) -> str:
            if not '%' in p:
                return p
            parts = p.split('%')
            for i in range(1, len(parts), 2):
                if parts[i].upper() in _os.environ:
                    parts[i] = _os.environ[parts[i].upper()]
            return ''.join(parts)
        path = _os.path.normpath(expand_env_path(path))
        if _os.path.isabs(path):
            drive, rel_path = _os.path.splitdrive(path)
            rel_path = rel_path.lstrip(_os.sep)
            search_dirs = [drive + _os.sep] if drive else [_os.sep]
        else:
            rel_path = path.lstrip(_os.sep)
            base_dir = Path.get(base_dir=True)
            search_dirs = [_os.getcwd(), base_dir, _os.path.expanduser('~'), _tempfile.gettempdir()]
        if search_in:
            search_dirs.extend([search_in] if isinstance(search_in, str) else search_in)
        path_parts = rel_path.split(_os.sep)
        for search_dir in search_dirs:
            full_path = _os.path.join(search_dir, rel_path)
            if _os.path.exists(full_path):
                return full_path
            match = find_path(search_dir, path_parts) if correct_path else None
            if match: return match
        if raise_error:
            raise FileNotFoundError(f'Path \'{path}\' not found in specified directories.')
        return _os.path.join(search_dirs[0], rel_path)

    @staticmethod
    def remove(path:str, only_content:bool = False) -> None:
        if not _os.path.exists(path):
            return None
        if not only_content:
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
                    raise Exception(f'Failed to delete {file_path}. Reason: {e}')
