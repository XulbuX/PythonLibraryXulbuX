from .base.consts import COLOR
from .format_codes import FormatCodes
from .string import String
from .regex import Regex

from typing import TypeAlias, Optional, Union, Any
import base64 as _base64
import math as _math
import re as _re


DataStructure: TypeAlias = Union[list, tuple, set, frozenset, dict]
IndexIterable: TypeAlias = Union[list, tuple, set, frozenset]


class Data:

    @staticmethod
    def serialize_bytes(data: bytes | bytearray) -> dict[str, str]:
        """Converts bytes or bytearray to a JSON-compatible format (dictionary) with explicit keys.\n
        ----------------------------------------------------------------------------------------------
        - `data` -⠀the bytes or bytearray to serialize"""
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"The 'data' parameter must be a bytes or bytearray object, got {type(data)}")

        key = "bytearray" if isinstance(data, bytearray) else "bytes"

        try:
            return {key: data.decode("utf-8"), "encoding": "utf-8"}
        except UnicodeDecodeError:
            pass

        return {key: _base64.b64encode(data).decode("utf-8"), "encoding": "base64"}

    @staticmethod
    def deserialize_bytes(obj: dict[str, str]) -> bytes | bytearray:
        """Tries to converts a JSON-compatible bytes/bytearray format (dictionary) back to its original type.\n
        --------------------------------------------------------------------------------------------------------
        - `obj` -⠀the dictionary to deserialize\n
        --------------------------------------------------------------------------------------------------------
        If the serialized object was created with `Data.serialize_bytes()`, it will work.
        If it fails to decode the data, it will raise a `ValueError`."""
        if not isinstance(obj, dict):
            raise TypeError(f"The 'obj' parameter must be a dictionary, got {type(obj)}")

        for key in ("bytes", "bytearray"):
            if key in obj and "encoding" in obj:
                if obj["encoding"] == "utf-8":
                    data = obj[key].encode("utf-8")
                elif obj["encoding"] == "base64":
                    data = _base64.b64decode(obj[key].encode("utf-8"))
                else:
                    raise ValueError(f"Unknown encoding method '{obj['encoding']}'")

                return bytearray(data) if key == "bytearray" else data

        raise ValueError(f"Invalid serialized data:\n  {obj}")

    @staticmethod
    def chars_count(data: DataStructure) -> int:
        """The sum of all the characters amount including the keys in dictionaries.\n
        ------------------------------------------------------------------------------
        - `data` -⠀the data structure to count the characters from"""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")

        chars_count = 0

        if isinstance(data, dict):
            for k, v in data.items():
                chars_count += len(str(k)) + (Data.chars_count(v) if isinstance(v, DataStructure) else len(str(v)))

        elif isinstance(data, IndexIterable):
            for item in data:
                chars_count += Data.chars_count(item) if isinstance(item, DataStructure) else len(str(item))

        return chars_count

    @staticmethod
    def strip(data: DataStructure) -> DataStructure:
        """Removes leading and trailing whitespaces from the data structure's items.\n
        -------------------------------------------------------------------------------
        - `data` -⠀the data structure to strip the items from"""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")

        if isinstance(data, dict):
            return {k.strip(): Data.strip(v) if isinstance(v, DataStructure) else v.strip() for k, v in data.items()}

        if isinstance(data, IndexIterable):
            return type(data)(Data.strip(item) if isinstance(item, DataStructure) else item.strip() for item in data)

        raise TypeError(f"Unsupported data structure type: {type(data)}")

    @staticmethod
    def remove_empty_items(data: DataStructure, spaces_are_empty: bool = False) -> DataStructure:
        """Removes empty items from the data structure.\n
        ---------------------------------------------------------------------------------
        - `data` -⠀the data structure to remove empty items from.
        - `spaces_are_empty` -⠀if true, it will count items with only spaces as empty"""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")

        if isinstance(data, dict):
            return {
                k: (v if not isinstance(v, DataStructure) else Data.remove_empty_items(v, spaces_are_empty))
                for k, v in data.items() if not String.is_empty(v, spaces_are_empty)
            }

        if isinstance(data, IndexIterable):
            return type(data)(
                item for item in
                (
                    (item if not isinstance(item, DataStructure) else Data.remove_empty_items(item, spaces_are_empty)) \
                    for item in data if not (isinstance(item, (str, type(None))) and String.is_empty(item, spaces_are_empty))
                )
                if item not in ([], (), {}, set(), frozenset())
            )

        raise TypeError(f"Unsupported data structure type: {type(data)}")

    @staticmethod
    def remove_duplicates(data: DataStructure) -> DataStructure:
        """Removes all duplicates from the data structure.\n
        -----------------------------------------------------------
        - `data` -⠀the data structure to remove duplicates from"""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")

        if isinstance(data, dict):
            return {k: Data.remove_duplicates(v) if isinstance(v, DataStructure) else v for k, v in data.items()}

        if isinstance(data, (list, tuple)):
            result = []
            for item in data:
                processed_item = Data.remove_duplicates(item) if isinstance(item, DataStructure) else item
                is_duplicate = False

                for existing_item in result:
                    if processed_item == existing_item:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    result.append(processed_item)

            return type(data)(result)

        if isinstance(data, (set, frozenset)):
            processed_elements = set()
            for item in data:
                processed_item = Data.remove_duplicates(item) if isinstance(item, DataStructure) else item
                processed_elements.add(processed_item)
            return type(data)(processed_elements)

        raise TypeError(f"Unsupported data structure type: {type(data)}")

    @staticmethod
    def remove_comments(
        data: DataStructure,
        comment_start: str = ">>",
        comment_end: str = "<<",
        comment_sep: str = "",
    ) -> DataStructure:
        """Remove comments from a list, tuple or dictionary.\n
        ---------------------------------------------------------------------------------------------------------------
        - `data` -⠀list, tuple or dictionary, where the comments should get removed from
        - `comment_start` -⠀the string that marks the start of a comment inside `data`
        - `comment_end` -⠀the string that marks the end of a comment inside `data`
        - `comment_sep` -⠀the string with which a comment will be replaced, if it is in the middle of a value\n
        ---------------------------------------------------------------------------------------------------------------
        Examples:
        ```python
        data = {
            "key1": [
                ">> COMMENT IN THE BEGINNING OF THE STRING <<  value1",
                "value2  >> COMMENT IN THE END OF THE STRING",
                "val>> COMMENT IN THE MIDDLE OF THE STRING <<ue3",
                ">> FULL VALUE IS A COMMENT  value4",
            ],
            ">> FULL KEY + ALL ITS VALUES ARE A COMMENT  key2": [
                "value",
                "value",
                "value",
            ],
            "key3": ">> ALL THE KEYS VALUES ARE COMMENTS  value",
        }

        processed_data = Data.remove_comments(
            data,
            comment_start=">>",
            comment_end="<<",
            comment_sep="__",
        )
        ```\n
        ---------------------------------------------------------------------------------------------------------------
        For this example, `processed_data` will be:
        ```python
        {
            "key1": [
                "value1",
                "value2",
                "val__ue3",
            ],
            "key3": None,
        }
        ```\n
        - For `key1`, all the comments will just be removed, except at `value3` and `value4`:
          * `value3` The comment is removed and the parts left and right are joined through `comment_sep`.
          * `value4` The whole value is removed, since the whole value was a comment.
        - For `key2`, the key, including its whole values will be removed.
        - For `key3`, since all its values are just comments, the key will still exist, but with a value of `None`."""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")
        if not isinstance(comment_start, str):
            raise TypeError(f"The 'comment_start' parameter must be a string, got {type(comment_start)}")
        elif len(comment_start) == 0:
            raise ValueError("The 'comment_start' parameter must not be an empty string.")
        if not isinstance(comment_end, str):
            raise TypeError(f"The 'comment_end' parameter must be a string, got {type(comment_end)}")
        if not isinstance(comment_sep, str):
            raise TypeError(f"The 'comment_sep' parameter must be a string, got {type(comment_sep)}")

        pattern = _re.compile(Regex._clean( \
                rf"""^(
                (?:(?!{_re.escape(comment_start)}).)*
            )
            {_re.escape(comment_start)}
            (?:(?:(?!{_re.escape(comment_end)}).)*)
            (?:{_re.escape(comment_end)})?
            (.*?)$"""
        )) if len(comment_end) > 0 else None

        def process_string(s: str) -> Optional[str]:
            if pattern:
                if (match := pattern.match(s)):
                    start, end = match.group(1).strip(), match.group(2).strip()
                    return f"{start}{comment_sep if start and end else ''}{end}" or None
                return s.strip() or None
            else:
                return None if s.lstrip().startswith(comment_start) else s.strip() or None

        def process_item(item: Any) -> Any:
            if isinstance(item, dict):
                return {
                    k: v
                    for k, v in ((process_item(key), process_item(value)) for key, value in item.items()) if k is not None
                }
            if isinstance(item, IndexIterable):
                processed = (v for v in map(process_item, item) if v is not None)
                return type(item)(processed)
            if isinstance(item, str):
                return process_string(item)
            return item

        return process_item(data)

    @staticmethod
    def is_equal(
        data1: DataStructure,
        data2: DataStructure,
        ignore_paths: str | list[str] = "",
        path_sep: str = "->",
        comment_start: str = ">>",
        comment_end: str = "<<",
    ) -> bool:
        """Compares two structures and returns `True` if they are equal and `False` otherwise.\n
        ⇾ Will not detect, if a key-name has changed, only if removed or added.\n
        ------------------------------------------------------------------------------------------------
        - `data1` -⠀the first data structure to compare
        - `data2` -⠀the second data structure to compare
        - `ignore_paths` -⠀a path or list of paths to key/s and item/s to ignore during comparison:<br>
          Comments are not ignored when comparing. `comment_start` and `comment_end` are only used
          to correctly recognize the keys in the `ignore_paths`.
        - `path_sep` -⠀the separator between the keys/indexes in the `ignore_paths`
        - `comment_start` -⠀the string that marks the start of a comment inside `data1` and `data2`
        - `comment_end` -⠀the string that marks the end of a comment inside `data1` and `data2`\n
        ------------------------------------------------------------------------------------------------
        The paths from `ignore_paths` and the `path_sep` parameter work exactly the same way as for
        the method `Data.get_path_id()`. See its documentation for more details."""
        if not isinstance(data1, DataStructure):
            raise TypeError(f"The 'data1' parameter must be a data structure, got {type(data1)}")
        if not isinstance(data2, DataStructure):
            raise TypeError(f"The 'data2' parameter must be a data structure, got {type(data2)}")
        if not isinstance(ignore_paths, (str, list)):
            raise TypeError(f"The 'ignore_paths' parameter must be a string or list of strings, got {type(ignore_paths)}")
        if not isinstance(path_sep, str):
            raise TypeError(f"The 'path_sep' parameter must be a string, got {type(path_sep)}")
        elif len(path_sep) == 0:
            raise ValueError("The 'path_sep' parameter must not be an empty string.")
        # THE 'comment_start' PARAM IS CHECKED IN 'Data.remove_comments()'
        # THE 'comment_end' PARAM IS CHECKED IN 'Data.remove_comments()'

        def process_ignore_paths(ignore_paths: str | list[str], ) -> list[list[str]]:
            if isinstance(ignore_paths, str):
                ignore_paths = [ignore_paths]
            return [str(path).split(path_sep) for path in ignore_paths if path]

        def compare(
            d1: DataStructure,
            d2: DataStructure,
            ignore_paths: list[list[str]],
            current_path: list[str] = [],
        ) -> bool:
            if any(current_path == path[:len(current_path)] for path in ignore_paths):
                return True
            if type(d1) is not type(d2):
                return False
            if isinstance(d1, dict) and isinstance(d2, dict):
                if set(d1.keys()) != set(d2.keys()):
                    return False
                return all(compare(d1[key], d2[key], ignore_paths, current_path + [key]) for key in d1)
            if isinstance(d1, (list, tuple)):
                if len(d1) != len(d2):
                    return False
                return all(
                    compare(item1, item2, ignore_paths, current_path + [str(i)])
                    for i, (item1, item2) in enumerate(zip(d1, d2))
                )
            if isinstance(d1, (set, frozenset)):
                return d1 == d2
            return d1 == d2

        processed_data1 = Data.remove_comments(data1, comment_start, comment_end)
        processed_data2 = Data.remove_comments(data2, comment_start, comment_end)
        processed_ignore_paths = process_ignore_paths(ignore_paths)

        return compare(processed_data1, processed_data2, processed_ignore_paths)

    @staticmethod
    def get_path_id(
        data: DataStructure,
        value_paths: str | list[str],
        path_sep: str = "->",
        comment_start: str = ">>",
        comment_end: str = "<<",
        ignore_not_found: bool = False,
    ) -> Optional[str | list[Optional[str]]]:
        """Generates a unique ID based on the path to a specific value within a nested data structure.\n
        --------------------------------------------------------------------------------------------------
        -`data` -⠀the list, tuple, or dictionary, which the id should be generated for
        - `value_paths` -⠀a path or list of paths to the value/s to generate the id for (explained below)
        - `path_sep` -⠀the separator between the keys/indexes in the `value_paths`
        - `comment_start` -⠀the string that marks the start of a comment inside `data`
        - `comment_end` -⠀the string that marks the end of a comment inside `data`
        - `ignore_not_found` -⠀if true, the function will return `None` if the value is not found
          instead of raising an error\n
        --------------------------------------------------------------------------------------------------
        The param `value_path` is a sort of path (or a list of paths) to the value/s to be updated.
        In this example:
        ```python
        {
            "healthy": {
                "fruit": ["apples", "bananas", "oranges"],
                "vegetables": ["carrots", "broccoli", "celery"]
            }
        }
        ```
        ... if you want to change the value of `"apples"` to `"strawberries"`, the value path would be
        `healthy->fruit->apples` or if you don't know that the value is `"apples"` you can also use the
        index of the value, so `healthy->fruit->0`."""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")
        if not isinstance(value_paths, (str, list)):
            raise TypeError(f"The 'value_paths' parameter must be a string or list of strings, got {type(value_paths)}")
        if not isinstance(path_sep, str):
            raise TypeError(f"The 'path_sep' parameter must be a string, got {type(path_sep)}")
        elif len(path_sep) == 0:
            raise ValueError("The 'path_sep' parameter must not be an empty string.")
        # THE 'comment_start' PARAM IS CHECKED IN 'Data.remove_comments()'
        # THE 'comment_end' PARAM IS CHECKED IN 'Data.remove_comments()'
        if not isinstance(ignore_not_found, bool):
            raise TypeError(f"The 'ignore_not_found' parameter must be a boolean, got {type(ignore_not_found)}")

        def process_path(path: str, data_obj: DataStructure) -> Optional[str]:
            keys = path.split(path_sep)
            path_ids, max_id_length = [], 0

            for key in keys:
                if isinstance(data_obj, dict):
                    if key.isdigit():
                        if ignore_not_found:
                            return None
                        raise TypeError(f"Key '{key}' is invalid for a dict type.")

                    try:
                        idx = list(data_obj.keys()).index(key)
                        data_obj = data_obj[key]
                    except (ValueError, KeyError):
                        if ignore_not_found:
                            return None
                        raise KeyError(f"Key '{key}' not found in dict.")

                elif isinstance(data_obj, IndexIterable):
                    try:
                        idx = int(key)
                        data_obj = list(data_obj)[idx]  # CONVERT TO LIST FOR INDEXING
                    except ValueError:
                        try:
                            idx = list(data_obj).index(key)
                            data_obj = list(data_obj)[idx]
                        except ValueError:
                            if ignore_not_found:
                                return None
                            raise ValueError(f"Value '{key}' not found in '{type(data_obj).__name__}'")

                else:
                    break

                path_ids.append(str(idx))
                max_id_length = max(max_id_length, len(str(idx)))

            if not path_ids:
                return None
            return f"{max_id_length}>{''.join(id.zfill(max_id_length) for id in path_ids)}"

        data = Data.remove_comments(data, comment_start, comment_end)
        if isinstance(value_paths, str):
            return process_path(value_paths, data)

        results = [process_path(path, data) for path in value_paths]
        return results if len(results) > 1 else results[0] if results else None

    @staticmethod
    def get_value_by_path_id(data: DataStructure, path_id: str, get_key: bool = False) -> Any:
        """Retrieves the value from `data` using the provided `path_id`, as long as the data structure
        hasn't changed since creating the path ID.\n
        --------------------------------------------------------------------------------------------------
        - `data` -⠀the list, tuple, or dictionary to retrieve the value from
        - `path_id` -⠀the path ID to the value to retrieve, created before using `Data.get_path_id()`
        - `get_key` -⠀if true and the final item is in a dict, it returns the key instead of the value"""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")
        if not isinstance(path_id, str):
            raise TypeError(f"The 'path_id' parameter must be a string, got {type(path_id)}")
        if not isinstance(get_key, bool):
            raise TypeError(f"The 'get_key' parameter must be a boolean, got {type(get_key)}")

        def get_nested(data: DataStructure, path: list[int], get_key: bool) -> Any:
            parent = None
            for i, idx in enumerate(path):
                if isinstance(data, dict):
                    keys = list(data.keys())
                    if i == len(path) - 1 and get_key:
                        return keys[idx]
                    parent = data
                    data = data[keys[idx]]

                elif isinstance(data, IndexIterable):
                    if i == len(path) - 1 and get_key:
                        if parent is None or not isinstance(parent, dict):
                            raise ValueError(f"Cannot get key from a non-dict parent at path '{path[:i+1]}'")
                        return next(key for key, value in parent.items() if value is data)
                    parent = data
                    data = list(data)[idx]  # CONVERT TO LIST FOR INDEXING

                else:
                    raise TypeError(f"Unsupported type '{type(data)}' at path '{path[:i+1]}'")

            return data

        return get_nested(data, Data.__sep_path_id(path_id), get_key)

    @staticmethod
    def set_value_by_path_id(data: DataStructure, update_values: dict[str, Any]) -> DataStructure:
        """Updates the value/s from `update_values` in the `data`, as long as the data structure
        hasn't changed since creating the path ID to that value.\n
        -----------------------------------------------------------------------------------------
        - `data` -⠀the list, tuple, or dictionary to update the value/s in
        - `update_values` -⠀a dictionary where keys are path IDs and values are the new values
          to insert, for example:
          ```python
        { "1>012": "new value", "1>31": ["new value 1", "new value 2"], ... }
          ```
          The path IDs should have been created using `Data.get_path_id()`."""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")
        if not isinstance(update_values, dict):
            raise TypeError(f"The 'update_values' parameter must be a dictionary, got {type(update_values)}")

        def update_nested(data: DataStructure, path: list[int], value: Any) -> DataStructure:
            if len(path) == 1:
                if isinstance(data, dict):
                    keys, data = list(data.keys()), dict(data)
                    data[keys[path[0]]] = value
                elif isinstance(data, IndexIterable):
                    was_t, data = type(data), list(data)
                    data[path[0]] = value
                    data = was_t(data)
            else:
                if isinstance(data, dict):
                    keys, data = list(data.keys()), dict(data)
                    data[keys[path[0]]] = update_nested(data[keys[path[0]]], path[1:], value)
                elif isinstance(data, IndexIterable):
                    was_t, data = type(data), list(data)
                    data[path[0]] = update_nested(data[path[0]], path[1:], value)
                    data = was_t(data)
            return data

        valid_entries = [(path_id, new_val) for path_id, new_val in update_values.items()]
        if not valid_entries:
            raise ValueError(f"No valid 'update_values' found in dictionary:\n{update_values!r}")

        for path_id, new_val in valid_entries:
            path = Data.__sep_path_id(path_id)
            data = update_nested(data, path, new_val)

        return data

    @staticmethod
    def to_str(
        data: DataStructure,
        indent: int = 4,
        compactness: int = 1,
        max_width: int = 127,
        sep: str = ", ",
        as_json: bool = False,
        _syntax_highlighting: dict[str, str] | bool = False,
    ) -> str:
        """Get nicely formatted data structure-strings.\n
        -------------------------------------------------------------------------------------------------
        - `data` -⠀the data structure to format
        - `indent` -⠀the amount of spaces to use for indentation
        - `compactness` -⠀the level of compactness for the output (explained below)
        - `max_width` -⠀the maximum width of a line before expanding (only used if `compactness` is `1`)
        - `sep` -⠀the separator between items in the data structure
        - `as_json` -⠀if true, the output will be in valid JSON format\n
        -------------------------------------------------------------------------------------------------
        There are three different levels of `compactness`:
        - `0` expands everything possible
        - `1` only expands if there's other lists, tuples or dicts inside of data or,
          if the data's content is longer than `max_width`
        - `2` keeps everything collapsed (all on one line)"""
        if not isinstance(data, DataStructure):
            raise TypeError(f"The 'data' parameter must be a data structure, got {type(data)}")
        if not isinstance(indent, int):
            raise TypeError(f"The 'indent' parameter must be an integer, got {type(indent)}")
        elif indent < 0:
            raise ValueError("The 'indent' parameter must be a non-negative integer.")
        if not isinstance(compactness, int):
            raise TypeError(f"The 'compactness' parameter must be an integer, got {type(compactness)}")
        elif compactness not in {0, 1, 2}:
            raise ValueError("The 'compactness' parameter must be 0, 1, or 2.")
        if not isinstance(max_width, int):
            raise TypeError(f"The 'max_width' parameter must be an integer, got {type(max_width)}")
        elif max_width <= 0:
            raise ValueError("The 'max_width' parameter must be a positive integer.")
        if not isinstance(sep, str):
            raise TypeError(f"The 'sep' parameter must be a string, got {type(sep)}")
        if not isinstance(as_json, bool):
            raise TypeError(f"The 'as_json' parameter must be a boolean, got {type(as_json)}")
        if not isinstance(_syntax_highlighting, (dict, bool, type(None))):
            raise TypeError(
                f"The 'syntax_highlighting' parameter must be a dict, bool, or None, got {type(_syntax_highlighting)}"
            )

        _syntax_hl = {}

        if do_syntax_hl := _syntax_highlighting not in {None, False}:
            if _syntax_highlighting is True:
                _syntax_highlighting = {}
            elif not isinstance(_syntax_highlighting, dict):
                raise TypeError(f"Expected 'syntax_highlighting' to be a dict or bool. Got: {type(_syntax_highlighting)}")

            _syntax_hl = {
                "str": (f"[{COLOR.BLUE}]", "[_c]"),
                "number": (f"[{COLOR.MAGENTA}]", "[_c]"),
                "literal": (f"[{COLOR.CYAN}]", "[_c]"),
                "type": (f"[i|{COLOR.LIGHT_BLUE}]", "[_i|_c]"),
                "punctuation": (f"[{COLOR.DARK_GRAY}]", "[_c]"),
            }
            _syntax_hl.update({
                k: (f"[{v}]", "[_]") if k in _syntax_hl and v not in {"", None} else ("", "")
                for k, v in _syntax_highlighting.items()
            })

            sep = f"{_syntax_hl['punctuation'][0]}{sep}{_syntax_hl['punctuation'][1]}"

        punct_map = {"(": ("/(", "("), **{char: char for char in "'\":)[]{}"}}
        punct = {
            k: ((f"{_syntax_hl['punctuation'][0]}{v[0]}{_syntax_hl['punctuation'][1]}" if do_syntax_hl else v[1])
                if isinstance(v, (list, tuple)) else
                (f"{_syntax_hl['punctuation'][0]}{v}{_syntax_hl['punctuation'][1]}" if do_syntax_hl else v))
            for k, v in punct_map.items()
        }

        def format_value(value: Any, current_indent: Optional[int] = None) -> str:
            if current_indent is not None and isinstance(value, dict):
                return format_dict(value, current_indent + indent)
            elif current_indent is not None and hasattr(value, "__dict__"):
                return format_dict(value.__dict__, current_indent + indent)
            elif current_indent is not None and isinstance(value, IndexIterable):
                return format_sequence(value, current_indent + indent)
            elif current_indent is not None and isinstance(value, (bytes, bytearray)):
                obj_dict = Data.serialize_bytes(value)
                return (
                    format_dict(obj_dict, current_indent + indent) if as_json else (
                        f"{_syntax_hl['type'][0]}{(k := next(iter(obj_dict)))}{_syntax_hl['type'][1]}"
                        + format_sequence((obj_dict[k], obj_dict["encoding"]), current_indent + indent) if do_syntax_hl else
                        (k := next(iter(obj_dict)))
                        + format_sequence((obj_dict[k], obj_dict["encoding"]), current_indent + indent)
                    )
                )
            elif isinstance(value, bool):
                val = str(value).lower() if as_json else str(value)
                return f"{_syntax_hl['literal'][0]}{val}{_syntax_hl['literal'][1]}" if do_syntax_hl else val
            elif isinstance(value, (int, float)):
                val = "null" if as_json and (_math.isinf(value) or _math.isnan(value)) else str(value)
                return f"{_syntax_hl['number'][0]}{val}{_syntax_hl['number'][1]}" if do_syntax_hl else val
            elif current_indent is not None and isinstance(value, complex):
                return (
                    format_value(str(value).strip("()")) if as_json else (
                        f"{_syntax_hl['type'][0]}complex{_syntax_hl['type'][1]}"
                        + format_sequence((value.real, value.imag), current_indent + indent)
                        if do_syntax_hl else f"complex{format_sequence((value.real, value.imag), current_indent + indent)}"
                    )
                )
            elif value is None:
                val = "null" if as_json else "None"
                return f"{_syntax_hl['literal'][0]}{val}{_syntax_hl['literal'][1]}" if do_syntax_hl else val
            else:
                return ((
                    punct['"'] + _syntax_hl["str"][0] + String.escape(str(value), '"') + _syntax_hl["str"][1]
                    + punct['"'] if do_syntax_hl else punct['"'] + String.escape(str(value), '"') + punct['"']
                ) if as_json else (
                    punct["'"] + _syntax_hl["str"][0] + String.escape(str(value), "'") + _syntax_hl["str"][1]
                    + punct["'"] if do_syntax_hl else punct["'"] + String.escape(str(value), "'") + punct["'"]
                ))

        def should_expand(seq: IndexIterable) -> bool:
            if compactness == 0:
                return True
            if compactness == 2:
                return False

            complex_types = (list, tuple, dict, set, frozenset) + ((bytes, bytearray) if as_json else ())
            complex_items = sum(1 for item in seq if isinstance(item, complex_types))

            return (
                complex_items > 1 or (complex_items == 1 and len(seq) > 1) or Data.chars_count(seq) +
                (len(seq) * len(sep)) > max_width
            )

        def format_dict(d: dict, current_indent: int) -> str:
            if compactness == 2 or not d or not should_expand(list(d.values())):
                return punct["{"] \
                    + sep.join(
                        f"{format_value(k)}{punct[':']} {format_value(v, current_indent)}"
                        for k, v in d.items()
                    ) \
                    + punct["}"]

            items = []
            for k, val in d.items():
                formatted_value = format_value(val, current_indent)
                items.append(f"{' ' * (current_indent + indent)}{format_value(k)}{punct[':']} {formatted_value}")

            return punct["{"] + "\n" + f"{sep}\n".join(items) + f"\n{' ' * current_indent}" + punct["}"]

        def format_sequence(seq, current_indent: int) -> str:
            if as_json:
                seq = list(seq)

            brackets = (punct["["], punct["]"]) if isinstance(seq, list) else (punct["("], punct[")"])

            if compactness == 2 or not seq or not should_expand(seq):
                return f"{brackets[0]}{sep.join(format_value(item, current_indent) for item in seq)}{brackets[1]}"

            items = [format_value(item, current_indent) for item in seq]
            formatted_items = f"{sep}\n".join(f'{" " * (current_indent + indent)}{item}' for item in items)

            return f"{brackets[0]}\n{formatted_items}\n{' ' * current_indent}{brackets[1]}"

        return _re.sub(r"\s+(?=\n)", "", format_dict(data, 0) if isinstance(data, dict) else format_sequence(data, 0))

    @staticmethod
    def print(
        data: DataStructure,
        indent: int = 4,
        compactness: int = 1,
        max_width: int = 127,
        sep: str = ", ",
        end: str = "\n",
        as_json: bool = False,
        syntax_highlighting: dict[str, str] | bool = {},
    ) -> None:
        """Print nicely formatted data structures.\n
        ---------------------------------------------------------------------------------------------------------------
        - `data` -⠀the data structure to format and print
        - `indent` -⠀the amount of spaces to use for indentation
        - `compactness` -⠀the level of compactness for the output (explained below – section 1)
        - `max_width` -⠀the maximum width of a line before expanding (only used if `compactness` is `1`)
        - `sep` -⠀the separator between items in the data structure
        - `end` -⠀the string appended after the last value, default a newline `\\n`
        - `as_json` -⠀if true, the output will be in valid JSON format
        - `syntax_highlighting` -⠀a dictionary defining the syntax highlighting styles (explained below – section 2)\n
        ---------------------------------------------------------------------------------------------------------------
        There are three different levels of `compactness`:
        - `0` expands everything possible
        - `1` only expands if there's other lists, tuples or dicts inside of data or,
          if the data's content is longer than `max_width`
        - `2` keeps everything collapsed (all on one line)\n
        ---------------------------------------------------------------------------------------------------------------
        The `syntax_highlighting` parameter is a dictionary with 5 keys for each part of the data.<br>
        The key's values are the formatting codes to apply to this data part.<br>
        The formatting can be changed by simply adding the key with the new value inside the
        `syntax_highlighting` dictionary.\n
        The keys with their default values are:
        - `str: COLOR.BLUE`
        - `number: COLOR.MAGENTA`
        - `literal: COLOR.CYAN`
        - `type: "i|" + COLOR.LIGHT_BLUE`
        - `punctuation: COLOR.DARK_GRAY`\n
        For no syntax highlighting, set `syntax_highlighting` to `False` or `None`.\n
        ---------------------------------------------------------------------------------------------------------------
        For more detailed information about formatting codes, see `format_codes` module documentation."""
        FormatCodes.print(
            Data.to_str(
                data=data,
                indent=indent,
                compactness=compactness,
                max_width=max_width,
                sep=sep,
                as_json=as_json,
                _syntax_highlighting=syntax_highlighting,
            ),
            end=end,
        )

    @staticmethod
    def __sep_path_id(path_id: str) -> list[int]:
        if len(split_id := path_id.split(">")) == 2:
            id_part_len, path_id_parts = split_id

            if (id_part_len.isdigit() and path_id_parts.isdigit()):
                id_part_len = int(id_part_len)

                if id_part_len > 0 and (len(path_id_parts) % id_part_len == 0):
                    return [int(path_id_parts[i:i + id_part_len]) for i in range(0, len(path_id_parts), id_part_len)]

        raise ValueError(f"Path ID '{path_id}' is an invalid format.")
