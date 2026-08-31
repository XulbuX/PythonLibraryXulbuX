"""
Provides utilities for processing and managing complex data structures.

This includes deep merging, nested key access, recursive sorting,
syntax-highlighted rendering, and data type conversions.
"""

from . import string as _string_module
from .ansi import AnyStyle, S
from .base.types import DataObj as DataObjType
from .base.types import SeqOrSet, is_data_obj, is_seq_or_set
from .regex import LazyRegex

import base64 as _base64
import math as _math
from typing import Any, Final, Literal, cast, overload
import regex as _rx

_PATTERNS: Final[LazyRegex] = LazyRegex(remove_comments_default=r"^((?:(?!>>).)*)>>(?:(?:(?!<<).)*)(?:<<)?(.*?)$")

_DEFAULT_SYNTAX_HL: Final[dict[str, AnyStyle]] = {
    "str": S.BR.BLUE,
    "number": S.BR.MAGENTA,
    "literal": S.MAGENTA,
    "type": S.ITALIC | S.GREEN,
    "punctuation": S.BR.BLACK,
}
"""Default syntax highlighting styles for data structure rendering."""


def chars_count(data: DataObjType, /) -> int:
    """The sum of all the characters amount including the keys in dictionaries.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The data structure to count the characters from."""

    count = 0

    if isinstance(data, dict):
        for key, val in data.items():
            count += len(str(key)) + (chars_count(val) if is_data_obj(val) else len(str(val)))
    else:
        for item in data:
            count += chars_count(item) if is_data_obj(item) else len(str(item))

    return count


def strip[DataObj: DataObjType](data: DataObj, /) -> DataObj:
    """Removes leading and trailing whitespaces from the data structure's items.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The data structure to strip the items from."""

    if isinstance(data, dict):
        return type(data)({key.strip(): (strip(val) if is_data_obj(val) else val.strip()) for key, val in data.items()})

    else:
        return cast(
            "DataObj",
            type(data)([strip(item) if is_data_obj(item) else item.strip() for item in data]),
        )


def remove_empty_items[DataObj: DataObjType](data: DataObj, /, *, spaces_are_empty: bool = False) -> DataObj:
    """Removes empty items from the data structure.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The data structure to remove empty items from.
    *   `spaces_are_empty` – If true, it will count items with only spaces as empty."""

    if isinstance(data, dict):
        return type(data)({
            key: (val if not is_data_obj(val) else remove_empty_items(val, spaces_are_empty=spaces_are_empty))
            for key, val in data.items()
            if not _string_module.is_empty(val, spaces_are_empty=spaces_are_empty)
        })

    else:
        processed_items = [
            (item if not is_data_obj(item) else remove_empty_items(item, spaces_are_empty=spaces_are_empty))
            for item in data
            if not (isinstance(item, (str, type(None))) and _string_module.is_empty(item, spaces_are_empty=spaces_are_empty))
        ]

        return type(data)([
            item for item in processed_items if not (not item and isinstance(item, (list, tuple, dict, set, frozenset)))
        ])


def remove_duplicates[DataObj: DataObjType](data: DataObj, /) -> DataObj:
    """Removes all duplicates from the data structure.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The data structure to remove duplicates from."""

    if isinstance(data, dict):
        return type(data)({key: remove_duplicates(val) if is_data_obj(val) else val for key, val in data.items()})

    elif isinstance(data, (list, tuple)):
        processed: list[Any] = [remove_duplicates(item) if is_data_obj(item) else item for item in data]

        try:
            result: list[Any] = list(dict.fromkeys(processed))

        except TypeError:
            # Unhashable items (lists, dicts, sets); fall back to O(n²) equality check.
            result = []
            for item in processed:
                if item not in result:
                    result.append(item)

        return type(data)(result)

    else:
        processed_elements: set[Any] = set()
        for item in data:
            processed_item = remove_duplicates(item) if is_data_obj(item) else item
            processed_elements.add(processed_item)
        return type(data)(processed_elements)


def remove_comments[DataObj: DataObjType](
    data: DataObj,
    /,
    *,
    comment_start: str = ">>",
    comment_end: str = "<<",
    comment_sep: str = "",
) -> DataObj:
    """Remove comments from a list, tuple or dictionary.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – List, tuple or dictionary, where the comments should get removed from.
    *   `comment_start` – The string that marks the start of a comment inside `data`.
    *   `comment_end` – The string that marks the end of a comment inside `data`.
    *   `comment_sep` – The string with which a comment will be replaced,
        if it is in the middle of a value.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    data = {
        "key1": [
            ">> Comment in the beginning of the string. <<  value1",
            "value2  >> Comment in the end of the string.",
            "val>> Comment in the middle of the string. <<ue3",
            ">> Full value is a comment.  value4",
        ],
        ">> Full key + all its values are a comment.  key2": [
            "value",
            "value",
            "value",
        ],
        "key3": ">> All the keys values are comments.  value",
    }

    processed_data = xx.data.remove_comments(
        data,
        comment_start=">>",
        comment_end="<<",
        comment_sep="__",
    )
    ```

    <!-- DOCS: <AttachedCode> -->
    Processed data:

    ```python
    {
        "key1": [
            "value1",
            "value2",
            "val__ue3"
        ],
        "key3": None
    }
    ```
    <!-- DOCS: </AttachedCode> -->

    *   For `key1`, all the comments will just be removed, except at `value3` and `value4`:
        -   `value3` The comment is removed and the parts
            left and right are joined through `comment_sep`.
        -   `value4` The whole value is removed, since the whole value was a comment.
    *   For `key2`, the key, including its whole values will be removed.
    *   For `key3`, since all its values are just comments,
        the key will still exist, but with a value of `None`."""

    if not comment_start:
        raise ValueError(f"The 'comment_start' parameter must be a non-empty string, got {comment_start!r}") from None

    return cast(
        "DataObj",
        _DataRemoveCommentsHelper(data, comment_start=comment_start, comment_end=comment_end, comment_sep=comment_sep)(),
    )


def is_equal(
    data1: DataObjType,
    data2: DataObjType,
    /,
    ignore_paths: str | list[str] = "",
    *,
    path_sep: str = "->",
    comment_start: str = ">>",
    comment_end: str = "<<",
) -> bool:
    """Compares two structures and returns `True` if they are equal and `False` otherwise.\n
    ⇾ Will not detect, if a key-name has changed, only if removed or added.\n
    ----------------------------------------------------------------------------------------------------
    *   `data1` – The first data structure to compare.
    *   `data2` – The second data structure to compare.
    *   `ignore_paths` – A path or list of paths to key/s and item/s to ignore during comparison:<br>
        Comments are not ignored when comparing. `comment_start` and `comment_end` are only used<br>
        to correctly recognize the keys in the `ignore_paths`.
    *   `path_sep` – The separator between the keys/indexes in the `ignore_paths`.
    *   `comment_start` – The string that marks the start of a comment inside `data1` and `data2`.
    *   `comment_end` – The string that marks the end of a comment inside `data1` and `data2`.\n
    ----------------------------------------------------------------------------------------------------
    The paths from `ignore_paths` and the `path_sep` parameter work exactly the same way as for<br>
    `get_path_id()`. See its documentation for more details.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    dict_a = {"user": "alice", "timestamp": 1600000000, "role": "admin"}
    dict_b = {"user": "alice", "timestamp": 1700000000, "role": "admin"}

    # Compare while ignoring volatile fields:
    same = xx.data.is_equal(dict_a, dict_b, ignore_paths="timestamp")
    ```

    <!-- DOCS: <AttachedCode> -->
    Result:

    ```python
    True
    ```
    <!-- DOCS: </AttachedCode> -->"""

    if not path_sep:
        raise ValueError(f"The 'path_sep' parameter must be a non-empty string, got {path_sep!r}") from None

    if isinstance(ignore_paths, str):
        ignore_paths = [ignore_paths]

    return _compare_nested(
        remove_comments(data1, comment_start=comment_start, comment_end=comment_end),
        remove_comments(data2, comment_start=comment_start, comment_end=comment_end),
        ignore_paths=[str(path).split(path_sep) for path in ignore_paths if path],
    )


@overload
def get_path_id(
    data: DataObjType,
    value_paths: str,
    /,
    *,
    path_sep: str = "->",
    comment_start: str = ">>",
    comment_end: str = "<<",
    ignore_not_found: bool = False,
) -> str | None: ...
@overload
def get_path_id(
    data: DataObjType,
    value_paths: list[str],
    /,
    *,
    path_sep: str = "->",
    comment_start: str = ">>",
    comment_end: str = "<<",
    ignore_not_found: bool = False,
) -> list[str | None]: ...
@overload
def get_path_id(
    data: DataObjType,
    value_paths: str | list[str],
    /,
    *,
    path_sep: str = "->",
    comment_start: str = ">>",
    comment_end: str = "<<",
    ignore_not_found: bool = False,
) -> str | list[str | None] | None: ...


def get_path_id(
    data: DataObjType,
    value_paths: str | list[str],
    /,
    *,
    path_sep: str = "->",
    comment_start: str = ">>",
    comment_end: str = "<<",
    ignore_not_found: bool = False,
) -> str | list[str | None] | None:
    """Generates a unique ID based on the path to a specific value within a nested data structure.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The list, tuple, or dictionary, which the id should be generated for.
    *   `value_paths` – A path or list of paths to the value/s
        to generate the id for (explained below).
    *   `path_sep` – The separator between the keys/indexes in the `value_paths`.
    *   `comment_start` – The string that marks the start of a comment inside `data`.
    *   `comment_end` – The string that marks the end of a comment inside `data`.
    *   `ignore_not_found` – If true, the function will return `None`<br>
        if the value is not found instead of raising an error.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    data = {
        "server": {
            "host": "localhost",
            "ports": [80, 443],
        }
    }

    # Generate path ID for the HTTPS port:
    path_id = xx.data.get_path_id(data, "server->ports->1")
    ```

    <!-- DOCS: <AttachedCode> -->
    Generated Path ID:

    ```python
    "1>011"
    ```
    <!-- DOCS: </AttachedCode> -->"""

    if not path_sep:
        raise ValueError(f"The 'path_sep' parameter must be a non-empty string, got {path_sep!r}") from None

    data = remove_comments(data, comment_start=comment_start, comment_end=comment_end)

    if isinstance(value_paths, str):
        return _DataGetPathIdHelper(value_paths, path_sep=path_sep, data_obj=data, ignore_not_found=ignore_not_found)()

    results = [
        _DataGetPathIdHelper(path, path_sep=path_sep, data_obj=data, ignore_not_found=ignore_not_found)()
        for path in value_paths
    ]

    return results if len(results) > 1 else results[0] if results else None


def get_value_by_path_id(data: DataObjType, path_id: str, /, *, get_key: bool = False) -> Any:
    """Retrieves the value from `data` using the provided `path_id`,<br>
    as long as the data structure hasn't changed since creating the path ID.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The list, tuple, or dictionary to retrieve the value from.
    *   `path_id` – The path ID to the value to retrieve, created before using `get_path_id()`.
    *   `get_key` – If true and the final item is in a dict,
        it returns the key instead of the value.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    data = {"server": {"host": "localhost", "ports": [80, 443]}}
    path_id = xx.data.get_path_id(data, "server->ports->1")

    # Retrieve the value at the generated path ID:
    port = xx.data.get_value_by_path_id(data, path_id)
    ```

    <!-- DOCS: <AttachedCode> -->
    Retrieved Port Value:

    ```python
    443
    ```
    <!-- DOCS: </AttachedCode> -->"""

    parent: DataObjType | None = None
    path = _sep_path_id(path_id)
    current_data: Any = data

    for i, path_idx in enumerate(path):
        if isinstance(current_data, dict):
            dict_data = cast("dict[Any, Any]", current_data)
            keys: list[str] = list(dict_data.keys())

            if i == len(path) - 1 and get_key:
                return keys[path_idx]

            parent = dict_data
            current_data = dict_data[keys[path_idx]]

        elif is_seq_or_set(current_data):
            if i == len(path) - 1 and get_key:
                if parent is None or not isinstance(parent, dict):
                    raise ValueError(f"Cannot get key from a non-dict parent at path '{path[: i + 1]}'") from None

                for key, value in parent.items():
                    if value is current_data:
                        return key

                raise StopIteration

            parent = current_data
            current_data = list(current_data)[path_idx]  # Convert to list for indexing.

        else:
            raise TypeError(f"Unsupported type '{type(current_data)}' at path '{path[: i + 1]}'")

    return current_data


def set_value_by_path_id[DataObj: DataObjType](data: DataObj, update_values: dict[str, Any], /) -> DataObj:
    """Updates the value/s from `update_values` in the `data`, as long as the<br>
    data structure hasn't changed since creating the path ID to that value.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The list, tuple, or dictionary to update the value/s in.
    *   `update_values` – A dictionary where keys are path IDs<br>
        and values are the new values to insert.
        The path IDs should have been created using `get_path_id()`.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    data = {"server": {"host": "localhost", "ports": [80, 443]}}
    path_id = xx.data.get_path_id(data, "server->ports->1")

    # Update the value at the generated path ID:
    updated = xx.data.set_value_by_path_id(data, {path_id: 8443})
    ```

    <!-- DOCS: <AttachedCode> -->
    Updated Structure:

    ```python
    {
        "server": {
            "host": "localhost",
            "ports": [80, 8443],  # 2nd port updated from 443 to 8443
        }
    }
    ```
    <!-- DOCS: </AttachedCode> -->"""

    if not (valid_update_values := list(update_values.items())):
        raise ValueError(f"No valid 'update_values' found in dictionary:\n{update_values!r}") from None

    for path_id, new_val in valid_update_values:
        data = _set_nested_val(data, _sep_path_id(path_id), new_val)

    return data


def render(
    data: DataObjType,
    /,
    *,
    indent: int = 4,
    compactness: Literal[0, 1, 2] = 1,
    max_width: int = 127,
    sep: str = ", ",
    as_json: bool = False,
    syntax_highlighting: dict[str, AnyStyle] | bool | None = False,
) -> S:
    """Get nicely formatted data structures as an `S` object.\n
    ----------------------------------------------------------------------------------------------------
    *   `data` – The data structure to format.
    *   `indent` – The amount of spaces to use for indentation.
    *   `compactness` – The level of compactness for the output (explained below – section 1).
    *   `max_width` – The maximum width of a line before expanding (only used if `compactness` is `1`).
    *   `sep` – The separator between items in the data structure.
    *   `as_json` – if true, the output will be in valid JSON format.
    *   `syntax_highlighting` – A dictionary defining the syntax highlighting styles
        (explained below – section 2) or `True` to apply default syntax highlighting styles<br>
        or `False`/`None` to disable syntax highlighting.\n
    ----------------------------------------------------------------------------------------------------
    There are three different levels of `compactness`:
    *   `0` expands everything possible.
    *   `1` expands only when necessary (based element complexity and the `max_width` parameter).
    *   `2` keeps everything collapsed (all on one line).\n
    ----------------------------------------------------------------------------------------------------
    The `syntax_highlighting` dictionary has 5 keys for each part of the data.<br>
    The key's values are the `S` style attributes (or combined style groups)
    to apply to this data part.<br>
    The styling can be changed by simply adding the key with the new value<br>
    inside the `syntax_highlighting` dictionary.\n
    The keys with their default values are:
    *   `str: S.BR.BLUE`
    *   `number: S.BR.MAGENTA`
    *   `literal: S.MAGENTA`
    *   `type: S.ITALIC | S.GREEN`
    *   `punctuation: S.BR.BLACK`\n
    ----------------------------------------------------------------------------------------------------
    The returned `S` object exposes the rendered ANSI string via `.ansi` (or `str(…)`)\n
    and the plain, un-styled text via `.raw`.\n
    For more detailed information about styling, see the `ansi` module documentation.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    data = {
        "name": "xulbux",
        "version": 2.0,
        "items": ["ansi", "data"],
        "ok": True,
    }

    # Format and print with syntax highlighting:
    styled_output = xx.data.render(data, indent=2, max_width=60, syntax_highlighting=True)
    styled_output.print()
    ```

    <!-- DOCS: <TerminalOutput>
    <span class="br-black">{</span>
      <span class="br-black">"</span><span class="br-blue">name</span><span class="br-black">": \
"</span><span class="br-blue">xulbux</span><span class="br-black">",</span>
      <span class="br-black">"</span><span class="br-blue">version</span><span class="br-black">": \
</span><span class="br-magenta">2.0</span><span class="br-black">,</span>
      <span class="br-black">"</span><span class="br-blue">items</span><span class="br-black">": \
["</span><span class="br-blue">ansi</span><span class="br-black">", \
"</span><span class="br-blue">data</span><span class="br-black">"],</span>
      <span class="br-black">"</span><span class="br-blue">ok</span><span class="br-black">": \
</span><span class="magenta">True</span>
    <span class="br-black">}</span>
    </TerminalOutput> -->"""

    if indent < 0:
        raise ValueError(f"The 'indent' parameter must be a non-negative integer, got {indent!r}") from None
    if max_width <= 0:
        raise ValueError(f"The 'max_width' parameter must be a positive integer, got {max_width!r}") from None

    return _DataRenderHelper(
        data,
        indent=indent,
        compactness=compactness,
        max_width=max_width,
        sep=sep,
        as_json=as_json,
        syntax_highlighting=syntax_highlighting,
    )()


def _compare_nested(data1: Any, data2: Any, /, ignore_paths: list[list[str]], current_path: list[str] | None = None) -> bool:  # ruff:ignore[complex-structure]
    """Internal method to recursively compare two nested data structures while ignoring specified paths."""

    if current_path is None:
        current_path = []

    for path in ignore_paths:
        if current_path[: len(path)] == path:
            return True

    if type(data1) is not type(data2):
        return False

    if isinstance(data1, dict) and isinstance(data2, dict):
        dict_data1, dict_data2 = cast("dict[Any, Any]", data1), cast("dict[Any, Any]", data2)

        if set(dict_data1.keys()) != set(dict_data2.keys()):
            return False

        for key in dict_data1:
            if not _compare_nested(
                dict_data1[key], dict_data2[key], ignore_paths=ignore_paths, current_path=[*current_path, key]
            ):
                return False

        return True

    elif isinstance(data1, (list, tuple)) and isinstance(data2, (list, tuple)):
        array_data1, array_data2 = cast("SeqOrSet[Any]", data1), cast("SeqOrSet[Any]", data2)

        if len(array_data1) != len(array_data2):
            return False

        for i, (item1, item2) in enumerate(zip(array_data1, array_data2, strict=False)):
            if not _compare_nested(item1, item2, ignore_paths=ignore_paths, current_path=[*current_path, str(i)]):
                return False

        return True

    elif isinstance(data1, (set, frozenset)):
        return data1 == data2

    return data1 == data2


def _sep_path_id(path_id: str, /) -> list[int]:
    """Internal method to separate a path-ID string into its ID parts as a list of integers."""

    if len(split_id := path_id.split(">")) == 2:
        id_part_len, path_id_parts = split_id

        if id_part_len.isdigit() and path_id_parts.isdigit():
            id_part_len_int = int(id_part_len)

            if id_part_len_int > 0 and (len(path_id_parts) % id_part_len_int == 0):
                return [int(path_id_parts[i : i + id_part_len_int]) for i in range(0, len(path_id_parts), id_part_len_int)]

    raise ValueError(f"Path ID '{path_id}' is an invalid format") from None


def _set_nested_val(data: DataObjType, id_path: list[int], value: Any, /) -> Any:
    """Internal method to set a value in a nested data structure based on the provided ID path."""

    current_data: Any = data

    if len(id_path) == 1:
        if isinstance(current_data, dict):
            dict_data = cast("dict[Any, Any]", current_data)
            keys, dict_data = list(dict_data.keys()), dict(dict_data)
            dict_data[keys[id_path[0]]] = value
            return dict_data
        elif is_seq_or_set(current_data):
            was_t, current_data = type(current_data), list(current_data)
            current_data[id_path[0]] = value
            return was_t(current_data)

    else:
        if isinstance(current_data, dict):
            dict_data = cast("dict[Any, Any]", current_data)
            keys, dict_data = list(dict_data.keys()), dict(dict_data)
            dict_data[keys[id_path[0]]] = _set_nested_val(dict_data[keys[id_path[0]]], id_path[1:], value)
            return dict_data
        elif is_seq_or_set(current_data):
            was_t, current_data = type(current_data), list(current_data)
            current_data[id_path[0]] = _set_nested_val(current_data[id_path[0]], id_path[1:], value)
            return was_t(current_data)

    return current_data


class _DataRemoveCommentsHelper:
    """Internal, callable helper class to remove all comments from nested data structures."""

    def __init__(self, data: DataObjType, /, *, comment_start: str, comment_end: str, comment_sep: str) -> None:
        self.data: DataObjType = data
        self.comment_start: str = comment_start
        self.comment_end: str = comment_end
        self.comment_sep: str = comment_sep

        self.pattern: _rx.Pattern[str] | None

        if comment_start == ">>" and comment_end == "<<":
            self.pattern = _PATTERNS.remove_comments_default
        else:
            self.pattern = (
                _rx.compile(
                    rf"""(?x)^(
                            (?:(?!{_rx.escape(comment_start)}).)*
                        )
                        {_rx.escape(comment_start)}
                        (?:(?:(?!{_rx.escape(comment_end)}).)*)
                        (?:{_rx.escape(comment_end)})?
                        (.*?)$"""
                )
                if len(comment_end) > 0
                else None
            )

    def __call__(self) -> DataObjType:
        return self.remove_nested_comments(self.data)

    def remove_nested_comments(self, item: Any, /) -> Any:
        """Recursively removes comments from the given item, which can be a dictionary, list, tuple, or string."""

        if isinstance(item, dict):
            dict_item = cast("dict[Any, Any]", item)
            return {
                key: val
                for key, val in [
                    (self.remove_nested_comments(key), self.remove_nested_comments(val)) for key, val in dict_item.items()
                ]
                if key is not None
            }

        if is_seq_or_set(item):
            processed = [cleaned for val in item if (cleaned := self.remove_nested_comments(val)) is not None]
            return type(item)(processed)

        if isinstance(item, str):
            if self.pattern:
                if match := self.pattern.match(item):
                    start, end = match.group(1).strip(), match.group(2).strip()
                    return f"{start}{self.comment_sep if start and end else ''}{end}" or None
                return item.strip() or None
            else:
                return None if item.lstrip().startswith(self.comment_start) else item.strip() or None

        return item


class _DataGetPathIdHelper:
    """Internal, callable helper class to process a data path and generate its unique path ID."""

    def __init__(self, path: str, /, *, path_sep: str, data_obj: DataObjType, ignore_not_found: bool) -> None:
        self.keys: list[str] = path.split(path_sep)
        self.data_obj: DataObjType = data_obj
        self.ignore_not_found: bool = ignore_not_found

        self.path_ids: list[str] = []
        self.max_id_length: int = 0
        self.current_data: Any = data_obj

    def __call__(self) -> str | None:
        for key in self.keys:
            if not self.process_key(key):
                break

        if not self.path_ids:
            return None

        return f"{self.max_id_length}>{''.join([id.zfill(self.max_id_length) for id in self.path_ids])}"

    def process_key(self, key: str, /) -> bool:
        """Process a single key and update `path_ids`. Returns `False` if processing should stop."""

        idx: int | None = None

        if isinstance(self.current_data, dict):
            if (idx := self.process_dict_key(key)) is None:
                return False
        elif is_seq_or_set(self.current_data):
            if (idx := self.process_iterable_key(key)) is None:
                return False
        else:
            return False

        self.path_ids.append(str(idx))
        self.max_id_length = max(self.max_id_length, len(str(idx)))
        return True

    def process_dict_key(self, key: str, /) -> int | None:
        """Process a key for dictionary data. Returns the index or `None` if not found."""

        if key.isdigit():
            if self.ignore_not_found:
                return None
            raise TypeError(f"Key '{key}' is invalid for a dict type")

        try:
            idx = list(self.current_data.keys()).index(key)
            self.current_data = self.current_data[key]
            return idx

        except (ValueError, KeyError):
            if self.ignore_not_found:
                return None
            raise KeyError(f"Key '{key}' not found in dict") from None

    def process_iterable_key(self, key: str, /) -> int | None:
        """Process a key for iterable data. Returns the index or `None` if not found."""

        idx = -1
        try:
            idx = int(key)
            self.current_data = list(self.current_data)[idx]
            return idx

        except IndexError:
            if self.ignore_not_found:
                return None
            raise IndexError(f"Index {idx} out of range") from None

        except ValueError:
            try:
                idx = list(self.current_data).index(key)
                self.current_data = list(self.current_data)[idx]
                return idx

            except ValueError:
                if self.ignore_not_found:
                    return None
                raise ValueError(f"Value '{key}' not found in '{type(self.current_data).__name__}'") from None


class _DataRenderHelper:
    """Internal, callable helper class to format data structures as `S` objects."""

    def __init__(
        self,
        data: DataObjType,
        /,
        *,
        indent: int,
        compactness: Literal[0, 1, 2],
        max_width: int,
        sep: str,
        as_json: bool,
        syntax_highlighting: dict[str, AnyStyle] | bool | None,
    ) -> None:
        self.data: DataObjType = data
        self.indent: int = indent
        self.compactness: Literal[0, 1, 2] = compactness
        self.max_width: int = max_width
        self.as_json: bool = as_json

        self.styles: dict[str, AnyStyle] = _DEFAULT_SYNTAX_HL.copy()
        self.do_syntax_hl: bool = syntax_highlighting is not None and syntax_highlighting is not False

        if self.do_syntax_hl:
            if syntax_highlighting is True:
                pass
            elif isinstance(syntax_highlighting, dict):
                self.styles.update({key: val for key, val in syntax_highlighting.items() if key in self.styles})
            else:
                raise TypeError(f"The 'syntax_highlighting' parameter must be a dict or bool, got {type(syntax_highlighting)}")

            sep = self._hl("punctuation", sep)

        self.sep: str = sep

        self.punct: dict[str, str] = {
            char: (self._hl("punctuation", char) if self.do_syntax_hl else char) for char in "'\":)([]{},"
        }

    def _hl(self, key: str, text: str, /) -> str:
        """Applies the syntax-highlighting style registered for `key` to `text`, returning the rendered ANSI string."""

        return self.styles[key](text).ansi

    def __call__(self) -> S:
        if isinstance(self.data, dict):
            formatted = self.format_dict(self.data, 0)
        elif is_seq_or_set(self.data):
            formatted = self.format_sequence(self.data, 0)
        else:
            formatted = self.format_value(self.data, None)

        return S(_rx.sub(r"\s+(?=\n)", "", formatted))

    def format_value(self, value: Any, /, current_indent: int | None = None) -> str:
        """Formats a single value based on its type and the current indentation level."""

        if current_indent is not None and isinstance(value, dict):
            return self.format_dict(cast("dict[Any, Any]", value), current_indent + self.indent)

        elif current_indent is not None and hasattr(value, "__dict__"):
            return self.format_dict(value.__dict__, current_indent + self.indent)

        elif current_indent is not None and is_seq_or_set(value):
            return self.format_sequence(value, current_indent + self.indent)

        elif current_indent is not None and isinstance(value, (bytes, bytearray)):
            try:
                decoded = value.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                decoded = _base64.b64encode(value).decode("utf-8")
                encoding = "base64"

            if self.as_json:
                return self.format_value(decoded)

            key = "bytearray" if isinstance(value, bytearray) else "bytes"
            type_label = self._hl("type", key) if self.do_syntax_hl else key
            return type_label + self.format_sequence((decoded, encoding), current_indent + self.indent)

        elif isinstance(value, bool):
            val = str(value).lower() if self.as_json else str(value)
            return self._hl("literal", val) if self.do_syntax_hl else val

        elif isinstance(value, (int, float)):
            val = "null" if self.as_json and (_math.isinf(value) or _math.isnan(value)) else str(value)
            return self._hl("number", val) if self.do_syntax_hl else val

        elif current_indent is not None and isinstance(value, complex):
            if self.as_json:
                return self.format_value(str(value).strip("()"))
            type_label = self._hl("type", "complex") if self.do_syntax_hl else "complex"
            return type_label + self.format_sequence((value.real, value.imag), current_indent + self.indent)

        elif value is None:
            val = "null" if self.as_json else "None"
            return self._hl("literal", val) if self.do_syntax_hl else val

        else:
            quote, escaped = '"', _string_module.escape(str(value), '"')
            inner = self._hl("str", escaped) if self.do_syntax_hl else escaped
            return self.punct[quote] + inner + self.punct[quote]

    def get_complexity(self, data: Any, /) -> int:  # ruff:ignore[complex-structure]
        """Calculates the complexity of a data structure based on its nested elements."""

        complex_types: tuple[type, ...] = (list, tuple, dict, set, frozenset)
        if self.as_json:
            complex_types += (bytes, bytearray)

        if not isinstance(data, complex_types):
            return 0

        score = 1
        if isinstance(data, dict):
            for val in cast("dict[Any, Any]", data).values():
                score += self.get_complexity(val)
        elif isinstance(data, list):
            for item in cast("list[Any]", data):
                score += self.get_complexity(item)
        elif isinstance(data, tuple):
            for item in cast("tuple[Any, ...]", data):
                score += self.get_complexity(item)
        elif isinstance(data, set):
            for item in cast("set[Any]", data):
                score += self.get_complexity(item)
        elif isinstance(data, frozenset):
            for item in cast("frozenset[Any]", data):
                score += self.get_complexity(item)

        return score

    def should_expand(self, seq: SeqOrSet[Any], /) -> bool:
        """Determines whether a sequence should be expanded based on its content and the current compactness settings."""

        if self.compactness == 0:
            return True
        if self.compactness == 2:
            return False

        complex_types: tuple[type, ...] = (list, tuple, dict, set, frozenset)
        if self.as_json:
            complex_types += (bytes, bytearray)

        complex_items = sum([1 for item in seq if isinstance(item, complex_types)])  # ruff:ignore[unnecessary-comprehension-in-call]
        complexity = sum([self.get_complexity(item) for item in seq])  # ruff:ignore[unnecessary-comprehension-in-call]

        return (complex_items > 1 and complexity > 2) or chars_count(seq) + (len(seq) * len(self.sep)) > self.max_width

    def format_dict(self, data_dict: dict[Any, Any], current_indent: int, /) -> str:
        """Formats a dictionary as a string, applying indentation and compactness rules."""

        if self.compactness == 2 or not data_dict or not self.should_expand(list(data_dict.values())):
            return (
                self.punct["{"]
                + self.sep.join(
                    f"{self.format_value(key)}{self.punct[':']} {self.format_value(val, current_indent)}"
                    for key, val in data_dict.items()
                )
                + self.punct["}"]
            )

        items: list[str] = []
        for key, val in data_dict.items():
            formatted_value = self.format_value(val, current_indent)
            items.append(f"{' ' * (current_indent + self.indent)}{self.format_value(key)}{self.punct[':']} {formatted_value}")

        return self.punct["{"] + "\n" + f"{self.sep}\n".join(items) + f"\n{' ' * current_indent}" + self.punct["}"]

    def format_sequence(self, seq: SeqOrSet[Any], current_indent: int, /) -> str:
        """Formats a list or tuple as a string, applying indentation and compactness rules."""

        if self.as_json:
            seq = list(seq)

        if isinstance(seq, list):
            brackets = (self.punct["["], self.punct["]"])
            prefix = ""
            empty = self.punct["["] + self.punct["]"]
        elif isinstance(seq, set):
            brackets = (self.punct["{"], self.punct["}"])
            prefix = ""
            empty = (self._hl("type", "set") if self.do_syntax_hl else "set") + self.punct["("] + self.punct[")"]
        elif isinstance(seq, frozenset):
            brackets = (self.punct["("] + self.punct["{"], self.punct["}"] + self.punct[")"])
            prefix = self._hl("type", "frozenset") if self.do_syntax_hl else "frozenset"
            empty = prefix + self.punct["("] + self.punct[")"]
        else:
            brackets = (self.punct["("], self.punct[")"])
            prefix = ""
            empty = self.punct["("] + self.punct[")"]

        if not seq:
            return empty

        trailing_comma = self.punct[","] if not self.as_json and isinstance(seq, tuple) and len(seq) == 1 else ""

        if self.compactness == 2 or not self.should_expand(seq):
            items_str = self.sep.join([self.format_value(item, current_indent) for item in seq])
            return f"{prefix}{brackets[0]}{items_str}{trailing_comma}{brackets[1]}"

        items = [self.format_value(item, current_indent) for item in seq]
        formatted_items = f"{self.sep}\n".join([f"{' ' * (current_indent + self.indent)}{item}" for item in items])

        return f"{prefix}{brackets[0]}\n{formatted_items}{trailing_comma}\n{' ' * current_indent}{brackets[1]}"
