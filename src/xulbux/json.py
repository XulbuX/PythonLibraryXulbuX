from .data import Data
from .file import File
from .path import Path

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
        file_path = Path.extend_or_make(json_file, prefer_script_dir=True)
        if file_path is None:
            raise FileNotFoundError(f"Could not find JSON file: {json_file}")
        with open(file_path, "r") as f:
            content = f.read()
        try:
            data = _json.loads(content)
        except _json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON in '{file_path}':  {str(e)}")
        processed_data = dict(Data.remove_comments(data, comment_start, comment_end))
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
        file_path = Path.extend_or_make(json_file, prefer_script_dir=True)
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
        ----------------------------------------------------------------------------------------------------
        The `update_values` parameter is a dictionary, where the keys are the paths to the data to update,
        and the values are the new values to set.\n
        Example: For this JSON data:
        ```python
        {
            "healthy": {
                "fruit": ["apples", "bananas", "oranges"],
                "vegetables": ["carrots", "broccoli", "celery"]
            }
        }
        ```
        ... the `update_values` dictionary could look like this:
        ```python
        {
            # CHANGE VALUE "apples" TO "strawberries"
            "healthy->fruit->0": "strawberries",
            # CHANGE VALUE UNDER KEY "vegetables" TO [1, 2, 3]
            "healthy->vegetables": [1, 2, 3]
        }
        ```
        In this example, if you want to change the value of `"apples"`, you can use `healthy->fruit->apples`
        as the value-path. If you don't know that the first list item is `"apples"`, you can use the items
        list index inside the value-path, so `healthy->fruit->0`.\n
        ⇾ If the given value-path doesn't exist, it will be created.\n
        -----------------------------------------------------------------------------------------------------
        If only `comment_start` is found at the beginning of an item, the whole item is counted as a comment
        and therefore completely ignored. If `comment_start` and `comment_end` are found inside an item, the
        section from `comment_start` to `comment_end` is counted as a comment and ignored."""
        processed_data, data = Json.read(json_file, comment_start, comment_end, return_original=True)

        def create_nested_path(data_obj: dict, path_keys: list[str], value: Any) -> dict:
            current = data_obj
            last_idx = len(path_keys) - 1
            for i, key in enumerate(path_keys):
                if i == last_idx:
                    if isinstance(current, dict):
                        current[key] = value
                    elif isinstance(current, list) and key.isdigit():
                        idx = int(key)
                        while len(current) <= idx:
                            current.append(None)
                        current[idx] = value
                    else:
                        raise TypeError(f"Cannot set key '{key}' on {type(current).__name__}")
                else:
                    next_key = path_keys[i + 1]
                    if isinstance(current, dict):
                        if key not in current:
                            current[key] = [] if next_key.isdigit() else {}
                        current = current[key]
                    elif isinstance(current, list) and key.isdigit():
                        idx = int(key)
                        while len(current) <= idx:
                            current.append(None)
                        if current[idx] is None:
                            current[idx] = [] if next_key.isdigit() else {}
                        current = current[idx]
                    else:
                        raise TypeError(f"Cannot navigate through '{type(current).__name__}'")
            return data_obj

        update = {}
        for value_path, new_value in update_values.items():
            try:
                path_id = Data.get_path_id(
                    data=processed_data,
                    value_paths=value_path,
                    path_sep=path_sep,
                )
                if path_id is not None:
                    update[path_id] = new_value
                else:
                    keys = value_path.split(path_sep)
                    keys = value_path.split(path_sep)
                    data = create_nested_path(data, keys, new_value)
            except Exception:
                keys = value_path.split(path_sep)
                data = create_nested_path(data, keys, new_value)
        if "update" in locals() and update:
            data = Data.set_value_by_path_id(data, update)
        Json.create(json_file=json_file, data=dict(data), force=True)
