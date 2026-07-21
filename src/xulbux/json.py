"""
This module provides functions to read, create, and update JSON files,<br>
with support for comments inside the JSON data.
"""

from . import data as _data_module
from . import file as _file_module
from . import file_sys as _file_sys_module

import json as _json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast, overload

if TYPE_CHECKING:
    from .base.types import DataObj


@overload
def read(
    json_file: Path | str, /, *, comment_start: str = ">>", comment_end: str = "<<", return_original: Literal[True]
) -> tuple[dict[str, Any], dict[str, Any]]: ...


@overload
def read(
    json_file: Path | str, /, *, comment_start: str = ">>", comment_end: str = "<<", return_original: Literal[False] = False
) -> dict[str, Any]: ...


def read(
    json_file: Path | str, /, *, comment_start: str = ">>", comment_end: str = "<<", return_original: bool = False
) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
    """Read JSON files, ignoring comments.\n
    --------------------------------------------------------------------------------------
    *   `json_file` – The path (relative or absolute) to the JSON file to read.
    *   `comment_start` – The string that indicates the start of a comment.
    *   `comment_end` – The string that indicates the end of a comment.
    *   `return_original` – If true, the original JSON data is returned additionally:<br>
        ```python
        (processed_json, original_json)
        ```
    --------------------------------------------------------------------------------------
    For more detailed information about the comment handling,<br>
    see the `_data_module.remove_comments()` method documentation."""

    if (json_path := Path(json_file) if isinstance(json_file, str) else json_file).suffix != ".json":
        json_path = json_path.with_suffix(".json")
    file_path = _file_sys_module.extend_or_make_path(json_path, prefer_script_dir=True)

    with open(file_path) as file:
        content = file.read()

    try:
        data = _json.loads(content)
    except _json.JSONDecodeError as exc:
        raise ValueError(f"Error parsing JSON in {file_path!r}:\n  {'\n  '.join(str(exc).splitlines())}") from exc

    if not (processed_data := dict(_data_module.remove_comments(data, comment_start=comment_start, comment_end=comment_end))):
        raise ValueError(f"The JSON file {file_path!r} contains no data")

    return (processed_data, data) if return_original else processed_data


def create(
    json_file: Path | str, data: dict[str, Any], /, *, indent: int = 2, compactness: Literal[0, 1, 2] = 1, force: bool = False
) -> Path:
    """Create a nicely formatted JSON file from a dictionary.\n
    ------------------------------------------------------------------------------
    *   `json_file` – The path (relative or absolute) to the JSON file to create.
    *   `data` – The dictionary data to write to the JSON file.
    *   `indent` – The amount of spaces to use for indentation.
    *   `compactness` – Can be `0`, `1` or `2` and indicates how compact<br>
        the data should be formatted (see `_data_module.render()` for more info).
    *   `force` – If true, will overwrite existing files<br>
        without throwing an error (errors explained below).
    ------------------------------------------------------------------------------
    The method will throw a `FileExistsError` if a file with the same<br>
    name already exists and a `SameContentFileExistsError` if a file<br>
    with the same name and same content already exists."""

    if (json_path := Path(json_file) if isinstance(json_file, str) else json_file).suffix != ".json":
        json_path = json_path.with_suffix(".json")

    file_path = _file_sys_module.extend_or_make_path(json_path, prefer_script_dir=True)
    _file_module.create(
        file_path,
        _data_module.render(data, indent=indent, compactness=compactness, as_json=True, syntax_highlighting=False).raw,
        force=force,
    )

    return file_path


def update(
    json_file: Path | str,
    update_values: dict[str, Any],
    /,
    *,
    comment_start: str = ">>",
    comment_end: str = "<<",
    path_sep: str = "->",
) -> None:
    """Update single/multiple values inside JSON files,<br>
    without needing to know the rest of the data.\n
    -----------------------------------------------------------------------------------
    *   `json_file` – The path (relative or absolute) to the JSON file to update.
    *   `update_values` – A dictionary with the paths to the values to update<br>
        and the new values to set (see explanation below – section 2).
    *   `comment_start` – The string that indicates the start of a comment.
    *   `comment_end` – The string that indicates the end of a comment.
    *   `path_sep` – The separator used inside the value-paths in `update_values`.
    -----------------------------------------------------------------------------------
    For more detailed information about the comment handling,<br>
    see the `_data_module.remove_comments()` method documentation.\n
    -----------------------------------------------------------------------------------
    The `update_values` is a dictionary, where the keys are the paths<br>
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
    … the `update_values` dictionary could look like this:
    ```python
    {
        # Change first list-value under `fruits` to "strawberries":
        "healthy->fruits->0": "strawberries",
        # Change value of key `vegetables` to [1, 2, 3]:
        "healthy->vegetables": [1, 2, 3]
    }
    ```
    In this example, if you want to change the value of `"apples"`,<br>
    you can use `healthy->fruits->apples` as the value-path.\n
    If you don't know that the first list item is `"apples"`,<br>
    you can use the items list index inside the value-path, so `healthy->fruits->0`.\n
    ⇾ If the given value-path doesn't exist, it will be created."""

    processed_data, data = read(json_file, comment_start=comment_start, comment_end=comment_end, return_original=True)

    update: dict[str, Any] = {}
    for val_path, new_val in update_values.items():
        try:
            if (path_id := _data_module.get_path_id(cast("DataObj", processed_data), val_path, path_sep=path_sep)) is not None:
                update[path_id] = new_val
            else:
                data = _create_nested_path(data, val_path.split(path_sep), new_val)
        except Exception:
            data = _create_nested_path(data, val_path.split(path_sep), new_val)

    if update:
        data = _data_module.set_value_by_path_id(data, update)

    create(json_file, data, force=True)


def _create_nested_path(data_obj: dict[str, Any], path_keys: list[str], value: Any, /) -> dict[str, Any]:
    """Internal method that creates nested dictionaries/lists based on the<br>
    given path keys and sets the specified value at the end of the path."""

    last_idx, current = len(path_keys) - 1, data_obj

    for i, key in enumerate(path_keys):
        if i == last_idx:
            if isinstance(current, dict):
                current[key] = value

            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                while len(cast("list[Any]", current)) <= idx:
                    cast("list[Any]", current).append(None)
                current[idx] = value

            else:
                raise TypeError(f"Cannot set key '{key}' on {type(cast('Any', current))}")

        else:
            next_key = path_keys[i + 1]
            if isinstance(current, dict):
                if key not in current:
                    current[key] = [] if next_key.isdigit() else {}
                current = cast("dict[str, Any]", current)[key]  # type: ignore[unnecessary-cast]

            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                while len(cast("list[Any]", current)) <= idx:
                    cast("list[Any]", current).append(None)
                if current[idx] is None:
                    current[idx] = [] if next_key.isdigit() else {}
                current = cast("list[Any]", current)[idx]

            else:
                raise TypeError(f"Cannot navigate through {type(cast('Any', current))}")

    return data_obj
