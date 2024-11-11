from .xx_data import *
from .xx_file import *

import json as _json
import os as _os




class Json:

    @staticmethod
    def read(json_file:str, comment_start:str = '>>', comment_end:str = '<<', return_original:bool = False) -> dict|tuple[dict,dict]:
        """Read JSON files, ignoring comments.\n
        -------------------------------------------------------------------------
        If only `comment_start` is found at the beginning of an item,<br>
        the whole item is counted as a comment and therefore ignored.<br>
        If `comment_start` and `comment_end` are found inside an item,<br>
        the the section from `comment_start` to `comment_end` is ignored.<br>
        If `return_original` is set to `True`, the original JSON is returned<br>
        additionally. (returns: `[processed_json, original_json]`)"""
        file_path = File._make_path(json_file, 'json', prefer_base_dir=True)
        with open(file_path, 'r') as f:
            content = f.read()
        try:
            data = _json.loads(content)
        except _json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON in '{file_path}':  {str(e)}")
        processed_data = Data.remove_comments(data, comment_start, comment_end)
        if not processed_data:
            raise ValueError(f"The JSON file '{file_path}' is empty or contains only comments.")
        return (processed_data, data) if return_original else processed_data

    @staticmethod
    def create(content:dict, new_file:str = 'config', indent:int = 2, compactness:int = 1, force:bool = False) -> str:
        file_path = File._make_path(new_file, 'json', prefer_base_dir=True)
        if _os.path.exists(file_path) and not force:
            with open(file_path, 'r', encoding='utf-8') as existing_f:
                existing_content = _json.load(existing_f)
                if existing_content == content:
                    raise FileExistsError(f'Already created this file. (nothing changed)')
            raise FileExistsError('File already exists.')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(Data.to_str(content, indent, compactness, as_json=True))
        full_path = _os.path.abspath(file_path)
        return full_path

    @staticmethod
    def update(json_file:str, update_values:str|list[str], comment_start:str = '>>', comment_end:str = '<<', sep:tuple[str,str] = ('->', '::')) -> None:
        """Function to easily update single/multiple values inside JSON files.\n
        --------------------------------------------------------------------------------------------------------
        The param `json_file` is the path to the JSON file or just the name of the JSON file to be updated.\n
        --------------------------------------------------------------------------------------------------------
        The param `update_values` is a sort of path (or a list of paths) to the value/s to be updated, with<br>
        the new value at the end of the path.<br>
        In this example:
        ```\n {
          'healthy': {
            'fruit': ['apples', 'bananas', 'oranges'],
            'vegetables': ['carrots', 'broccoli', 'celery']
          }
        }\n```
        ... if you want to change the value of `'apples'` to `'strawberries'`, `update_values` would<br>
        be `healthy->fruit->apples::strawberries` or if you don't know that the value to update<br>
        is `apples` you can also use the position of the value, so `healthy->fruit->0::strawberries`.\n
        ⇾ **If the path from `update_values` doesn't exist, it will be created.**\n
        --------------------------------------------------------------------------------------------------------
        If only `comment_start` is found at the beginning of an item, the whole item is counted<br>
        as a comment and therefore ignored. If `comment_start` and `comment_end` are found<br>
        inside an item, the the section from `comment_start` to `comment_end` is ignored."""
        if isinstance(update_values, str):
            update_values = [update_values]
        valid_entries = [(parts[0].strip(), parts[1]) for update_value in update_values if len(parts := update_value.split(str(sep[1]).strip())) == 2]
        value_paths, new_values = (zip(*valid_entries) if valid_entries else ([], []))
        processed_data, data = Json.read(json_file, comment_start, comment_end, return_original=True)
        update = []
        for value_path, new_value in zip(value_paths, new_values):
            path_id = Data.get_path_id(processed_data, value_path)
            update.append(f'{path_id}::{new_value}')
        updated = Data.set_value_by_path_id(data, update)
        Json.create(updated, json_file, force=True)
