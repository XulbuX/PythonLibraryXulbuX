"""
This module provides the `Json` class, which offers methods to read, create and update JSON files,
with support for comments inside the JSON data.
"""

from .data import Data
from .file import File
from .path import Path

from typing import Any
import json as _json


class Json:
    """This class provides methods to read, create and update JSON files,
    with support for comments inside the JSON data."""

    @staticmethod
    def read(
        json_file: str,
        comment_start: str = ">>",
        comment_end: str = "<<",
        return_original: bool = False,
    ) -> dict | tuple[dict, dict]:
        """Read JSON files, ignoring comments.\n
        ------------------------------------------------------------------------------------
        - `json_file` -⠀the path (relative or absolute) to the JSON file to read
        - `comment_start` -⠀the string that indicates the start of a comment
        - `comment_end` -⠀the string that indicates the end of a comment
        - `return_original` -⠀if true, the original JSON data is returned additionally:<br>
          ```python
        (processed_json, original_json)
          ```\n
        ------------------------------------------------------------------------------------
        For more detailed information about the comment handling,
        see the `Data.remove_comments()` method documentation."""
        if not isinstance(json_file, str):
            raise TypeError(f"The 'json_file' parameter must be a string, got {type(json_file)}")
        # THE 'comment_start' PARAM IS CHECKED IN 'Data.remove_comments()'
        # THE 'comment_end' PARAM IS CHECKED IN 'Data.remove_comments()'
        if not isinstance(return_original, bool):
            raise TypeError(f"The 'return_original' parameter must be a boolean, got {type(return_original)}")

        if not json_file.endswith(".json"):
            json_file += ".json"
        if (file_path := Path.extend_or_make(json_file, prefer_script_dir=True)) is None:
            raise FileNotFoundError(f"Could not find JSON file: {json_file}")

        with open(file_path, "r") as f:
            content = f.read()

        try:
            data = _json.loads(content)
        except _json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON in '{file_path}':  {str(e)}")

        if not (processed_data := dict(Data.remove_comments(data, comment_start, comment_end))):
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
        ---------------------------------------------------------------------------
        - `json_file` -⠀the path (relative or absolute) to the JSON file to create
        - `data` -⠀the dictionary data to write to the JSON file
        - `indent` -⠀the amount of spaces to use for indentation
        - `compactness` -⠀can be `0`, `1` or `2` and indicates how compact
          the data should be formatted (see `Data.to_str()` for more info)
        - `force` -⠀if true, will overwrite existing files
          without throwing an error (errors explained below)\n
        ---------------------------------------------------------------------------
        The method will throw a `FileExistsError` if a file with the same
        name already exists and a `SameContentFileExistsError` if a file
        with the same name and same content already exists."""
        if not isinstance(json_file, str):
            raise TypeError(f"The 'json_file' parameter must be a string, got {type(json_file)}")
        # THE 'data' PARAM IS CHECKED IN 'Data.to_str()'
        # THE 'indent' PARAM IS CHECKED IN 'Data.to_str()'
        # THE 'compactness' PARAM IS CHECKED IN 'Data.to_str()'
        if not isinstance(force, bool):
            raise TypeError(f"The 'force' parameter must be a boolean, got {type(force)}")

        if not json_file.endswith(".json"):
            json_file += ".json"

        File.create(
            file_path=(file_path := Path.extend_or_make(json_file, prefer_script_dir=True)),
            content=Data.to_str(data=data, indent=indent, compactness=compactness, as_json=True),
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
        """Update single/multiple values inside JSON files,
        without needing to know the rest of the data.\n
        -----------------------------------------------------------------------------------
        - `json_file` -⠀the path (relative or absolute) to the JSON file to update
        - `update_values` -⠀a dictionary with the paths to the values to update
          and the new values to set (see explanation below – section 2)
        - `comment_start` -⠀the string that indicates the start of a comment
        - `comment_end` -⠀the string that indicates the end of a comment
        - `path_sep` -⠀the separator used inside the value-paths in `update_values`\n
        -----------------------------------------------------------------------------------
        For more detailed information about the comment handling,
        see the `Data.remove_comments()` method documentation.\n
        -----------------------------------------------------------------------------------
        The `update_values` is a dictionary, where the keys are the paths
        to the data to update, and the values are the new values to set.\n
        For example for this JSON data:
        ```python
        {
            "healthy": {
                "fruits": ["apples", "bananas", "oranges"],
                "vegetables": ["carrots", "broccoli", "celery"]
            }
        }
        ```
        ... the `update_values` dictionary could look like this:
        ```python
        {
            # CHANGE FIRST LIST-VALUE UNDER 'fruits' TO "strawberries"
            "healthy->fruits->0": "strawberries",
            # CHANGE VALUE OF KEY 'vegetables' TO [1, 2, 3]
            "healthy->vegetables": [1, 2, 3]
        }
        ```
        In this example, if you want to change the value of `"apples"`,
        you can use `healthy->fruits->apples` as the value-path.<br>
        If you don't know that the first list item is `"apples"`,
        you can use the items list index inside the value-path, so `healthy->fruits->0`.\n
        ⇾ If the given value-path doesn't exist, it will be created."""
        # THE 'json_file' PARAM IS CHECKED IN 'Json.read()'
        if not isinstance(update_values, dict):
            raise TypeError(f"The 'update_values' parameter must be a dictionary, got {type(update_values)}")
        # THE 'comment_start' PARAM IS CHECKED IN 'Json.read()'
        # THE 'comment_end' PARAM IS CHECKED IN 'Json.read()'
        # THE 'path_sep' PARAM IS CHECKED IN 'Data.get_path_id()'

        processed_data, data = Json.read(
            json_file=json_file,
            comment_start=comment_start,
            comment_end=comment_end,
            return_original=True,
        )

        def create_nested_path(data_obj: dict, path_keys: list[str], value: Any) -> dict:
            last_idx, current = len(path_keys) - 1, data_obj

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
                        raise TypeError(f"Cannot set key '{key}' on {type(current)}")

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
                        raise TypeError(f"Cannot navigate through {type(current)}")

            return data_obj

        update = {}
        for val_path, new_val in update_values.items():
            try:
                if (path_id := Data.get_path_id(data=processed_data, value_paths=val_path, path_sep=path_sep)) is not None:
                    update[path_id] = new_val
                else:
                    data = create_nested_path(data, val_path.split(path_sep), new_val)
            except Exception:
                data = create_nested_path(data, val_path.split(path_sep), new_val)

        if update and "update" in locals():
            data = Data.set_value_by_path_id(data, update)

        Json.create(json_file=json_file, data=dict(data), force=True)
