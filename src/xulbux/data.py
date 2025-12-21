"""
This module provides the `Data` class, which offers
methods to work with nested data structures.
"""

from .base.types import DataStructureTypes, IndexIterableTypes, DataStructure, IndexIterable

from .format_codes import FormatCodes
from .string import String
from .regex import Regex

from typing import Optional, Literal, Final, Any, cast
import base64 as _base64
import math as _math
import re as _re


_DEFAULT_SYNTAX_HL: Final[dict[str, tuple[str, str]]] = {
    "str": (f"[br:blue]", "[_c]"),
    "number": (f"[br:magenta]", "[_c]"),
    "literal": (f"[magenta]", "[_c]"),
    "type": (f"[i|green]", "[_i|_c]"),
    "punctuation": (f"[br:black]", "[_c]"),
}
"""Default syntax highlighting styles for data structure rendering."""


class Data:
    """This class includes methods to work with nested data structures (dictionaries and lists)."""

    @classmethod
    def serialize_bytes(cls, data: bytes | bytearray) -> dict[str, str]:
        """Converts bytes or bytearray to a JSON-compatible format (dictionary) with explicit keys.\n
        ----------------------------------------------------------------------------------------------
        - `data` -⠀the bytes or bytearray to serialize"""
        key = "bytearray" if isinstance(data, bytearray) else "bytes"

        try:
            return {key: cast(bytes | bytearray, data).decode("utf-8"), "encoding": "utf-8"}
        except UnicodeDecodeError:
            pass

        return {key: _base64.b64encode(data).decode("utf-8"), "encoding": "base64"}

    @classmethod
    def deserialize_bytes(cls, obj: dict[str, str]) -> bytes | bytearray:
        """Tries to converts a JSON-compatible bytes/bytearray format (dictionary) back to its original type.\n
        --------------------------------------------------------------------------------------------------------
        - `obj` -⠀the dictionary to deserialize\n
        --------------------------------------------------------------------------------------------------------
        If the serialized object was created with `Data.serialize_bytes()`, it will work.
        If it fails to decode the data, it will raise a `ValueError`."""
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

    @classmethod
    def chars_count(cls, data: DataStructure) -> int:
        """The sum of all the characters amount including the keys in dictionaries.\n
        ------------------------------------------------------------------------------
        - `data` -⠀the data structure to count the characters from"""
        chars_count = 0

        if isinstance(data, dict):
            for k, v in data.items():
                chars_count += len(str(k)) + (cls.chars_count(v) if isinstance(v, DataStructureTypes) else len(str(v)))

        elif isinstance(data, IndexIterableTypes):
            for item in data:
                chars_count += cls.chars_count(item) if isinstance(item, DataStructureTypes) else len(str(item))

        return chars_count

    @classmethod
    def strip(cls, data: DataStructure) -> DataStructure:
        """Removes leading and trailing whitespaces from the data structure's items.\n
        -------------------------------------------------------------------------------
        - `data` -⠀the data structure to strip the items from"""
        if isinstance(data, dict):
            return {k.strip(): cls.strip(v) if isinstance(v, DataStructureTypes) else v.strip() for k, v in data.items()}

        if isinstance(data, IndexIterableTypes):
            return type(data)(cls.strip(item) if isinstance(item, DataStructureTypes) else item.strip() for item in data)

        raise TypeError(f"Unsupported data structure type: {type(data)}")

    @classmethod
    def remove_empty_items(cls, data: DataStructure, spaces_are_empty: bool = False) -> DataStructure:
        """Removes empty items from the data structure.\n
        ---------------------------------------------------------------------------------
        - `data` -⠀the data structure to remove empty items from.
        - `spaces_are_empty` -⠀if true, it will count items with only spaces as empty"""
        if isinstance(data, dict):
            return {
                k: (v if not isinstance(v, DataStructureTypes) else cls.remove_empty_items(v, spaces_are_empty))
                for k, v in data.items() if not String.is_empty(v, spaces_are_empty)
            }

        if isinstance(data, IndexIterableTypes):
            return type(data)(
                item for item in
                (
                    (item if not isinstance(item, DataStructureTypes) else cls.remove_empty_items(item, spaces_are_empty)) \
                    for item in data if not (isinstance(item, (str, type(None))) and String.is_empty(item, spaces_are_empty))
                )
                if item not in ([], (), {}, set(), frozenset())
            )

        raise TypeError(f"Unsupported data structure type: {type(data)}")

    @classmethod
    def remove_duplicates(cls, data: DataStructure) -> DataStructure:
        """Removes all duplicates from the data structure.\n
        -----------------------------------------------------------
        - `data` -⠀the data structure to remove duplicates from"""
        if isinstance(data, dict):
            return {k: cls.remove_duplicates(v) if isinstance(v, DataStructureTypes) else v for k, v in data.items()}

        if isinstance(data, (list, tuple)):
            result: list[Any] = []
            for item in data:
                processed_item = cls.remove_duplicates(item) if isinstance(item, DataStructureTypes) else item
                is_duplicate: bool = False

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
                processed_item = cls.remove_duplicates(item) if isinstance(item, DataStructureTypes) else item
                processed_elements.add(processed_item)
            return type(data)(processed_elements)

        raise TypeError(f"Unsupported data structure type: {type(data)}")

    @classmethod
    def remove_comments(
        cls,
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
        #### Examples:
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
        if len(comment_start) == 0:
            raise ValueError("The 'comment_start' parameter string must not be empty.")

        return _DataRemoveCommentsHelper(
            data=data,
            comment_start=comment_start,
            comment_end=comment_end,
            comment_sep=comment_sep,
        )()

    @classmethod
    def is_equal(
        cls,
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
        if len(path_sep) == 0:
            raise ValueError("The 'path_sep' parameter string must not be empty.")

        if isinstance(ignore_paths, str):
            ignore_paths = [ignore_paths]

        return cls._compare_nested(
            data1=cls.remove_comments(data1, comment_start, comment_end),
            data2=cls.remove_comments(data2, comment_start, comment_end),
            ignore_paths=[str(path).split(path_sep) for path in ignore_paths if path],
        )

    @classmethod
    def get_path_id(
        cls,
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
        #### In this example:
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
        if len(path_sep) == 0:
            raise ValueError("The 'path_sep' parameter string must not be empty.")

        data = cls.remove_comments(data, comment_start, comment_end)
        if isinstance(value_paths, str):
            return cls._get_path_id(value_paths, path_sep, data, ignore_not_found)

        results = [cls._get_path_id(path, path_sep, data, ignore_not_found) for path in value_paths]
        return results if len(results) > 1 else results[0] if results else None

    @classmethod
    def get_value_by_path_id(cls, data: DataStructure, path_id: str, get_key: bool = False) -> Any:
        """Retrieves the value from `data` using the provided `path_id`, as long as the data structure
        hasn't changed since creating the path ID.\n
        --------------------------------------------------------------------------------------------------
        - `data` -⠀the list, tuple, or dictionary to retrieve the value from
        - `path_id` -⠀the path ID to the value to retrieve, created before using `Data.get_path_id()`
        - `get_key` -⠀if true and the final item is in a dict, it returns the key instead of the value"""
        parent: Optional[DataStructure] = None
        path = cls._sep_path_id(path_id)

        for i, path_idx in enumerate(path):
            if isinstance(data, dict):
                keys = list(data.keys())
                if i == len(path) - 1 and get_key:
                    return keys[path_idx]
                parent = data
                data = data[keys[path_idx]]

            elif isinstance(data, IndexIterableTypes):
                if i == len(path) - 1 and get_key:
                    if parent is None or not isinstance(parent, dict):
                        raise ValueError(f"Cannot get key from a non-dict parent at path '{path[:i+1]}'")
                    return next(key for key, value in parent.items() if value is data)
                parent = data
                data = list(data)[path_idx]  # CONVERT TO LIST FOR INDEXING

            else:
                raise TypeError(f"Unsupported type '{type(data)}' at path '{path[:i+1]}'")

        return data

    @classmethod
    def set_value_by_path_id(cls, data: DataStructure, update_values: dict[str, Any]) -> DataStructure:
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
        if not (valid_update_values := [(path_id, new_val) for path_id, new_val in update_values.items()]):
            raise ValueError(f"No valid 'update_values' found in dictionary:\n{update_values!r}")

        for path_id, new_val in valid_update_values:
            data = cls._set_nested_val(data, id_path=cls._sep_path_id(path_id), value=new_val)

        return data

    @classmethod
    def render(
        cls,
        data: DataStructure,
        indent: int = 4,
        compactness: Literal[0, 1, 2] = 1,
        max_width: int = 127,
        sep: str = ", ",
        as_json: bool = False,
        syntax_highlighting: dict[str, str] | bool = False,
    ) -> str:
        """Get nicely formatted data structure-strings.\n
        ---------------------------------------------------------------------------------------------------------------
        - `data` -⠀the data structure to format
        - `indent` -⠀the amount of spaces to use for indentation
        - `compactness` -⠀the level of compactness for the output (explained below – section 1)
        - `max_width` -⠀the maximum width of a line before expanding (only used if `compactness` is `1`)
        - `sep` -⠀the separator between items in the data structure
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
        - `str: "br:blue"`
        - `number: "br:magenta"`
        - `literal: "magenta"`
        - `type: "i|green"`
        - `punctuation: "br:black"`\n
        For no syntax highlighting, set `syntax_highlighting` to `False` or `None`.\n
        ---------------------------------------------------------------------------------------------------------------
        For more detailed information about formatting codes, see the `format_codes` module documentation."""
        if indent < 0:
            raise ValueError("The 'indent' parameter must be a non-negative integer.")
        if max_width <= 0:
            raise ValueError("The 'max_width' parameter must be a positive integer.")

        return _DataRenderHelper(
            cls,
            data=data,
            indent=indent,
            compactness=compactness,
            max_width=max_width,
            sep=sep,
            as_json=as_json,
            syntax_highlighting=syntax_highlighting,
        )()

    @classmethod
    def print(
        cls,
        data: DataStructure,
        indent: int = 4,
        compactness: Literal[0, 1, 2] = 1,
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
        - `str: "br:blue"`
        - `number: "br:magenta"`
        - `literal: "magenta"`
        - `type: "i|green"`
        - `punctuation: "br:black"`\n
        For no syntax highlighting, set `syntax_highlighting` to `False` or `None`.\n
        ---------------------------------------------------------------------------------------------------------------
        For more detailed information about formatting codes, see the `format_codes` module documentation."""
        FormatCodes.print(
            cls.render(
                data=data,
                indent=indent,
                compactness=compactness,
                max_width=max_width,
                sep=sep,
                as_json=as_json,
                syntax_highlighting=syntax_highlighting,
            ),
            end=end,
        )

    @classmethod
    def _compare_nested(
        cls,
        data1: Any,
        data2: Any,
        ignore_paths: list[list[str]],
        current_path: list[str] = [],
    ) -> bool:
        if any(current_path == path[:len(current_path)] for path in ignore_paths):
            return True
        if type(data1) is not type(data2):
            return False
        if isinstance(data1, dict) and isinstance(data2, dict):
            if set(data1.keys()) != set(data2.keys()):
                return False
            return all(cls._compare_nested(data1[key], data2[key], ignore_paths, current_path + [key]) for key in data1)
        if isinstance(data1, (list, tuple)):
            if len(data1) != len(data2):
                return False
            return all(
                cls._compare_nested(item1, item2, ignore_paths, current_path + [str(i)])
                for i, (item1, item2) in enumerate(zip(data1, data2))
            )
        if isinstance(data1, (set, frozenset)):
            return data1 == data2
        return data1 == data2

    @staticmethod
    def _sep_path_id(path_id: str) -> list[int]:
        """Internal method to separate a path-ID string into its ID parts as a list of integers."""
        if len(split_id := path_id.split(">")) == 2:
            id_part_len, path_id_parts = split_id

            if (id_part_len.isdigit() and path_id_parts.isdigit()):
                id_part_len_int = int(id_part_len)

                if id_part_len_int > 0 and (len(path_id_parts) % id_part_len_int == 0):
                    return [int(path_id_parts[i:i + id_part_len_int]) for i in range(0, len(path_id_parts), id_part_len_int)]

        raise ValueError(f"Path ID '{path_id}' is an invalid format.")

    @staticmethod
    def _get_path_id(path: str, path_sep: str, data_obj: Any, ignore_not_found: bool) -> Optional[str]:
        """Internal method to process a single data-path and generate its path ID."""
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

            elif isinstance(data_obj, IndexIterableTypes):
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

        if not path_ids: return None
        return f"{max_id_length}>{''.join(id.zfill(max_id_length) for id in path_ids)}"

    @classmethod
    def _set_nested_val(cls, data: Any, id_path: list[int], value: Any) -> Any:
        """Internal method to set a value in a nested data structure based on the provided ID path."""
        if len(id_path) == 1:
            if isinstance(data, dict):
                keys, data = list(data.keys()), dict(data)
                data[keys[id_path[0]]] = value
            elif isinstance(data, IndexIterableTypes):
                was_t, data = type(data), list(data)
                data[id_path[0]] = value
                data = was_t(data)

        else:
            if isinstance(data, dict):
                keys, data = list(data.keys()), dict(data)
                data[keys[id_path[0]]] = cls._set_nested_val(data[keys[id_path[0]]], id_path[1:], value)
            elif isinstance(data, IndexIterableTypes):
                was_t, data = type(data), list(data)
                data[id_path[0]] = cls._set_nested_val(data[id_path[0]], id_path[1:], value)
                data = was_t(data)

        return data


class _DataRemoveCommentsHelper:
    """Internal, callable helper class to remove all comments from nested data structures."""

    def __init__(self, data: DataStructure, comment_start: str, comment_end: str, comment_sep: str):
        self.data = data
        self.comment_start = comment_start
        self.comment_end = comment_end
        self.comment_sep = comment_sep

        self.pattern = _re.compile(Regex._clean( \
            rf"""^(
                (?:(?!{_re.escape(comment_start)}).)*
            )
            {_re.escape(comment_start)}
            (?:(?:(?!{_re.escape(comment_end)}).)*)
            (?:{_re.escape(comment_end)})?
            (.*?)$"""
        )) if len(comment_end) > 0 else None

    def __call__(self) -> DataStructure:
        return self.rem_nested_comments(self.data)

    def rem_nested_comments(self, item: Any) -> Any:
        if isinstance(item, dict):
            return {
                key: val
                for key, val in ( \
                    (self.rem_nested_comments(k), self.rem_nested_comments(v)) for k, v in item.items()
                ) if key is not None
            }

        if isinstance(item, IndexIterableTypes):
            processed = (v for v in map(self.rem_nested_comments, item) if v is not None)
            return type(item)(processed)

        if isinstance(item, str):
            if self.pattern:
                if (match := self.pattern.match(item)):
                    start, end = match.group(1).strip(), match.group(2).strip()
                    return f"{start}{self.comment_sep if start and end else ''}{end}" or None
                return item.strip() or None
            else:
                return None if item.lstrip().startswith(self.comment_start) else item.strip() or None

        return item


class _DataRenderHelper:
    """Internal, callable helper class to format data structures as strings."""

    def __init__(
        self,
        cls: type[Data],
        data: DataStructure,
        indent: int,
        compactness: Literal[0, 1, 2],
        max_width: int,
        sep: str,
        as_json: bool,
        syntax_highlighting: dict[str, str] | bool,
    ):
        self.cls = cls
        self.data = data
        self.indent = indent
        self.compactness = compactness
        self.max_width = max_width
        self.as_json = as_json

        self.syntax_hl: dict[str, tuple[str, str]] = _DEFAULT_SYNTAX_HL.copy()
        self.do_syntax_hl = syntax_highlighting not in {None, False}

        if self.do_syntax_hl:
            if syntax_highlighting is True:
                syntax_highlighting = {}
            elif not isinstance(syntax_highlighting, dict):
                raise TypeError(f"Expected 'syntax_highlighting' to be a dict or bool. Got: {type(syntax_highlighting)}")

            self.syntax_hl.update({
                k: (f"[{v}]", "[_]") if k in self.syntax_hl and v not in {"", None} else ("", "")
                for k, v in syntax_highlighting.items()
            })

            sep = f"{self.syntax_hl['punctuation'][0]}{sep}{self.syntax_hl['punctuation'][1]}"

        self.sep = sep

        punct_map: dict[str, str | tuple[str, str]] = {"(": ("/(", "("), **{c: c for c in "'\":)[]{}"}}
        self.punct: dict[str, str] = {
            k: ((f"{self.syntax_hl['punctuation'][0]}{v[0]}{self.syntax_hl['punctuation'][1]}" if self.do_syntax_hl else v[1])
                if isinstance(v, (list, tuple)) else
                (f"{self.syntax_hl['punctuation'][0]}{v}{self.syntax_hl['punctuation'][1]}" if self.do_syntax_hl else v))
            for k, v in punct_map.items()
        }

    def __call__(self) -> str:
        return _re.sub(
            r"\s+(?=\n)", "",
            self.format_dict(self.data, 0) if isinstance(self.data, dict) else self.format_sequence(self.data, 0)
        )

    def format_value(self, value: Any, current_indent: Optional[int] = None) -> str:
        if current_indent is not None and isinstance(value, dict):
            return self.format_dict(value, current_indent + self.indent)
        elif current_indent is not None and hasattr(value, "__dict__"):
            return self.format_dict(value.__dict__, current_indent + self.indent)
        elif current_indent is not None and isinstance(value, IndexIterableTypes):
            return self.format_sequence(value, current_indent + self.indent)
        elif current_indent is not None and isinstance(value, (bytes, bytearray)):
            obj_dict = self.cls.serialize_bytes(value)
            return (
                self.format_dict(obj_dict, current_indent + self.indent) if self.as_json else (
                    f"{self.syntax_hl['type'][0]}{(k := next(iter(obj_dict)))}{self.syntax_hl['type'][1]}"
                    + self.format_sequence((obj_dict[k], obj_dict["encoding"]), current_indent + self.indent)
                    if self.do_syntax_hl else (k := next(iter(obj_dict)))
                    + self.format_sequence((obj_dict[k], obj_dict["encoding"]), current_indent + self.indent)
                )
            )
        elif isinstance(value, bool):
            val = str(value).lower() if self.as_json else str(value)
            return f"{self.syntax_hl['literal'][0]}{val}{self.syntax_hl['literal'][1]}" if self.do_syntax_hl else val
        elif isinstance(value, (int, float)):
            val = "null" if self.as_json and (_math.isinf(value) or _math.isnan(value)) else str(value)
            return f"{self.syntax_hl['number'][0]}{val}{self.syntax_hl['number'][1]}" if self.do_syntax_hl else val
        elif current_indent is not None and isinstance(value, complex):
            return (
                self.format_value(str(value).strip("()")) if self.as_json else (
                    f"{self.syntax_hl['type'][0]}complex{self.syntax_hl['type'][1]}"
                    + self.format_sequence((value.real, value.imag), current_indent + self.indent) if self.do_syntax_hl else
                    f"complex{self.format_sequence((value.real, value.imag), current_indent + self.indent)}"
                )
            )
        elif value is None:
            val = "null" if self.as_json else "None"
            return f"{self.syntax_hl['literal'][0]}{val}{self.syntax_hl['literal'][1]}" if self.do_syntax_hl else val
        else:
            return ((
                self.punct['"'] + self.syntax_hl["str"][0] + String.escape(str(value), '"') + self.syntax_hl["str"][1]
                + self.punct['"'] if self.do_syntax_hl else self.punct['"'] + String.escape(str(value), '"') + self.punct['"']
            ) if self.as_json else (
                self.punct["'"] + self.syntax_hl["str"][0] + String.escape(str(value), "'") + self.syntax_hl["str"][1]
                + self.punct["'"] if self.do_syntax_hl else self.punct["'"] + String.escape(str(value), "'") + self.punct["'"]
            ))

    def should_expand(self, seq: IndexIterable) -> bool:
        if self.compactness == 0:
            return True
        if self.compactness == 2:
            return False

        complex_types: tuple[type, ...] = (list, tuple, dict, set, frozenset)
        if self.as_json: complex_types += (bytes, bytearray)

        complex_items = sum(1 for item in seq if isinstance(item, complex_types))

        return complex_items > 1 \
            or (complex_items == 1 and len(seq) > 1) \
            or self.cls.chars_count(seq) + (len(seq) * len(self.sep)) > self.max_width

    def format_dict(self, d: dict, current_indent: int) -> str:
        if self.compactness == 2 or not d or not self.should_expand(list(d.values())):
            return self.punct["{"] + self.sep.join(
                f"{self.format_value(k)}{self.punct[':']} {self.format_value(v, current_indent)}" for k, v in d.items()
            ) + self.punct["}"]

        items = []
        for k, val in d.items():
            formatted_value = self.format_value(val, current_indent)
            items.append(f"{' ' * (current_indent + self.indent)}{self.format_value(k)}{self.punct[':']} {formatted_value}")

        return self.punct["{"] + "\n" + f"{self.sep}\n".join(items) + f"\n{' ' * current_indent}" + self.punct["}"]

    def format_sequence(self, seq, current_indent: int) -> str:
        if self.as_json:
            seq = list(seq)

        brackets = (self.punct["["], self.punct["]"]) if isinstance(seq, list) else (self.punct["("], self.punct[")"])

        if self.compactness == 2 or not seq or not self.should_expand(seq):
            return f"{brackets[0]}{self.sep.join(self.format_value(item, current_indent) for item in seq)}{brackets[1]}"

        items = [self.format_value(item, current_indent) for item in seq]
        formatted_items = f"{self.sep}\n".join(f'{" " * (current_indent + self.indent)}{item}' for item in items)

        return f"{brackets[0]}\n{formatted_items}\n{' ' * current_indent}{brackets[1]}"
