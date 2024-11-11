from .xx_string import *
from .xx_path import *

import os as _os




class File:

    @staticmethod
    def _make_path(filename:str, filetype:str, search_in:str|list[str] = None, prefer_base_dir:bool = True, correct_path:bool = False) -> str:
        """Get the path to a file in the cwd, the base-dir, or predefined directories.\n
        --------------------------------------------------------------------------------------
        If the `filename` is not found in the above directories, it will be searched<br>
        in the `search_in` directory/directories. If the file is still not found, it will<br>
        return the path to the file in the base-dir per default or to the file in the<br>
        cwd if `prefer_base_dir` is set to `False`."""
        if not filename.lower().endswith(f'.{filetype.lower()}'):
            filename = f'{filename}.{filetype.lower()}'
        try:
            return Path.extend(filename, search_in, True, correct_path)
        except FileNotFoundError:
            return _os.path.join(Path.get(base_dir=True), filename) if prefer_base_dir else _os.path.join(_os.getcwd(), filename)

    @staticmethod
    def rename_extension(file_path:str, new_extension:str) -> str:
        directory, filename_with_ext = _os.path.split(file_path)
        filename = filename_with_ext.split('.')[0]
        camel_case_filename = String.to_camel_case(filename)
        new_filename = f'{camel_case_filename}{new_extension}'
        new_file_path = _os.path.join(directory, new_filename)
        return new_file_path

    @staticmethod
    def create(content:str = '', file:str = 'new_file.txt', force:bool = False) -> str:
        """Create a file with ot without content.\n
        ----------------------------------------------------------------------------
        The function will throw a `FileExistsError` if the file already exists.<br>
        To overwrite the file, set the `force` parameter to `True`."""
        if _os.path.exists(file) and not force:
            with open(file, 'r', encoding='utf-8') as existing_file:
                existing_content = existing_file.read()
                if existing_content == content:
                    raise FileExistsError('Already created this file. (nothing changed)')
            raise FileExistsError('File already exists.')
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        full_path = _os.path.abspath(file)
        return full_path
