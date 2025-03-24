from .xx_data import Data
from .xx_file import File

from typing import Any
import json as _json


class Json:

    @staticmethod
    def read(
        json_file: str,
        comment_start: str = ">>",
        comment_end: str = "<<",
        return_original: bool = False,
    ) -> dict | tuple[dict, dict]:
        """Read JSON files, ignoring comments.\n
        ------------------------------------------------------------------
        If only `comment_start` is found at the beginning of an item,
        the whole item is counted as a comment and therefore ignored.
        If `comment_start` and `comment_end` are found inside an item,
        the the section from `comment_start` to `comment_end` is ignored.
        If `return_original` is true, the original JSON is returned
        additionally. (returns: `[processed_json, original_json]`)"""
        if not json_file.endswith(".json"):
            json_file += ".json"
        file_path = File.extend_or_make_path(json_file, prefer_base_dir=True)
        with open(file_path, "r") as f:
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
    def create(
        json_file: str,
        data: dict,
        indent: int = 2,
        compactness: int = 1,
        force: bool = False,
    ) -> str:
        """Create a nicely formatted JSON file from a dictionary.\n
        ----------------------------------------------------------------------
        The `indent` is the amount of spaces to use for indentation.\n
        The `compactness` can be `0`, `1` or `2` and indicates how compact
        the data should be formatted (see `Data.to_str()`).\n
        The function will throw a `FileExistsError` if a file with the same
        name already exists and a `SameContentFileExistsError` if a file with
        the same name and content already exists.
        To always overwrite the file, set the `force` parameter to `True`."""
        if not json_file.endswith(".json"):
            json_file += ".json"
        file_path = File.extend_or_make_path(json_file, prefer_base_dir=True)
        File.create(
            file=file_path,
            content=Data.to_str(data, indent, compactness, as_json=True),
            force=force,
        )
        return file_path

    @staticmethod
    def update(
        json_file: str,
        update_values: dict[str, Any],
        comment_start: str = ">>",
        comment_end: str = "<<",
        path_sep: str = "->",
    ) -> None:
        """Update single/multiple values inside JSON files, without needing to know the rest of the data.\n
        ------------------------------------------------------------------------------------------------------
        The param `json_file` is the path to the JSON file or just the name of the JSON file to be updated.\n
        ------------------------------------------------------------------------------------------------------
        The param `update_values` is a dictionary where the keys are paths to the data to update and the
        values are the new values to set, for example in this JSON data:
        ```python
        {
          'healthy': {
            'fruit': ['apples', 'bananas', 'oranges'],
            'vegetables': ['carrots', 'broccoli', 'celery']
          }
        }
        ```
        ... the `update_values` dictionary could look like this:
        ```python
        {
            "healthy->fruit->0": "strawberries",  # UPDATE A SPECIFIC LIST ITEM
            "healthy->vegetables": ["new value", "other new value"]  # REPLACE AN ENTIRE LIST
        }
        ```
        ... if you want to change the value of `'apples'` to `'strawberries'`, you can use
        `{ "healthy->fruit->apples": "strawberries" }` or if you don't know that the value to update is
        `apples` you can also use the index of the value: `{ "healthy->fruit->0": "strawberries" }`.\n
        ⇾ If the path from `update_values` doesn't exist, it will be created.\n
        ------------------------------------------------------------------------------------------------------
        If only `comment_start` is found at the beginning of an item, the whole item is counted as a comment
        and therefore ignored. If `comment_start` and `comment_end` are found inside an item, the the section
        from `comment_start` to `comment_end` is ignored."""
        processed_data, data = Json.read(json_file, comment_start, comment_end, return_original=True)
        update = {}
        for value_path, new_value in update_values.items():
            update[Data.get_path_id(data=processed_data, value_paths=value_path, path_sep=path_sep)] = new_value
        Json.create(json_file=json_file, data=Data.set_value_by_path_id(data, update), force=True)
