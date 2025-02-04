from ._consts_ import DEFAULT
from .xx_format_codes import FormatCodes
from .xx_string import String

from typing import TypeAlias, Union
import base64 as _base64
import math as _math
import re as _re


DataStructure: TypeAlias = Union[list, tuple, set, frozenset, dict]


class Data:

    @staticmethod
    def serialize_bytes(data: bytes | bytearray) -> dict[str, str]:
        """Converts bytes or bytearray to a JSON-compatible format (dictionary) with explicit keys."""
        if isinstance(data, (bytes, bytearray)):
            key = "bytearray" if isinstance(data, bytearray) else "bytes"
            try:
                return {key: data.decode("utf-8"), "encoding": "utf-8"}
            except UnicodeDecodeError:
                pass
            return {key: _base64.b64encode(data).decode("utf-8"), "encoding": "base64"}
        raise TypeError("Unsupported data type")

    @staticmethod
    def deserialize_bytes(obj: dict[str, str]) -> bytes | bytearray:
        """Converts a JSON-compatible bytes/bytearray format (dictionary) back to its original type."""
        for key in ("bytes", "bytearray"):
            if key in obj and "encoding" in obj:
                if obj["encoding"] == "utf-8":
                    data = obj[key].encode("utf-8")
                elif obj["encoding"] == "base64":
                    data = _base64.b64decode(obj[key].encode("utf-8"))
                else:
                    raise ValueError("Unknown encoding method")
                return bytearray(data) if key == "bytearray" else data
        raise ValueError("Invalid serialized data")

    @staticmethod
    def chars_count(data: DataStructure) -> int:
        """The sum of all the characters amount including the keys in dictionaries."""
        if isinstance(data, dict):
            return sum(len(str(k)) + len(str(v)) for k, v in data.items())
        return sum(len(str(item)) for item in data)

    @staticmethod
    def strip(data: DataStructure) -> DataStructure:
        """Removes leading and trailing whitespaces from the data structure's items."""
        if isinstance(data, dict):
            return {k: Data.strip(v) for k, v in data.items()}
        return type(data)(map(Data.strip, data))

    @staticmethod
    def remove_empty_items(data: DataStructure, spaces_are_empty: bool = False) -> DataStructure:
        """Removes empty items from the data structure.
        If `spaces_are_empty` is true, it will count items with only spaces as empty."""
        if isinstance(data, dict):
            return {
                k: (
                    v
                    if not isinstance(v, (list, tuple, set, frozenset, dict))
                    else Data.remove_empty_items(v, spaces_are_empty)
                )
                for k, v in data.items()
                if not String.is_empty(v, spaces_are_empty)
            }
        if isinstance(data, (list, tuple, set, frozenset)):
            return type(data)(
                item
                for item in (
                    (
                        item
                        if not isinstance(item, (list, tuple, set, frozenset, dict))
                        else Data.remove_empty_items(item, spaces_are_empty)
                    )
                    for item in data
                    if not String.is_empty(item, spaces_are_empty)
                )
                if item not in ((), {}, set(), frozenset())
            )
        return data

    @staticmethod
    def remove_duplicates(data: DataStructure) -> DataStructure:
        """Removes all duplicates from the data structure."""
        if isinstance(data, dict):
            return {k: Data.remove_duplicates(v) for k, v in data.items()}
        if isinstance(data, (list, tuple)):
            return type(data)(
                Data.remove_duplicates(item) if isinstance(item, (list, tuple, set, frozenset, dict)) else item
                for item in dict.fromkeys(data)
            )
        if isinstance(data, (set, frozenset)):
            return type(data)(
                Data.remove_duplicates(item) if isinstance(item, (list, tuple, set, frozenset, dict)) else item
                for item in data
            )
        return data

    @staticmethod
    def remove_comments(
        data: DataStructure,
        comment_start: str = ">>",
        comment_end: str = "<<",
        comment_sep: str = "",
    ) -> DataStructure:
        """Remove comments from a list, tuple or dictionary.\n
        ----------------------------------------------------------------------------------------------------------------------
        - The `data` parameter is your list, tuple or dictionary, where the comments should get removed from.
        - The `comment_start` parameter is the string that marks the start of a comment inside `data`. (default: `>>`)
        - The `comment_end` parameter is the string that marks the end of a comment inside `data`. (default: `<<`)
        - The `comment_sep` parameter is a string with which a comment will be replaced, if it is in the middle of a value.\n
        ----------------------------------------------------------------------------------------------------------------------
        Examples:
        ```python
        data = {
            "key1": [
                ">> COMMENT IN THE BEGINNING OF THE STRING <<  value1",
                "value2  >> COMMENT IN THE END OF THE STRING",
                "val>> COMMENT IN THE MIDDLE OF THE STRING <<ue3",
                ">> FULL VALUE IS A COMMENT  value4"
            ],
            ">> FULL KEY + ALL ITS VALUES ARE A COMMENT  key2": [
                "value",
                "value",
                "value"
            ],
            "key3": ">> ALL THE KEYS VALUES ARE COMMENTS  value"
        }

        processed_data = Data.remove_comments(
            data,
            comment_start=">>",
            comment_end="<<",
            comment_sep="__"
        )
        ```\n
        ----------------------------------------------------------------------------------------------------------------------
        For this example, `processed_data` will be:
        ```python
        {
            "key1": [
                "value1",
                "value2",
                "val__ue3"
            ],
            "key3": None
        }
        ```\n
        - For `key1`, all the comments will just be removed, except at `value3` and `value4`:
          - `value3` The comment is removed and the parts left and right are joined through `comment_sep`.
          - `value4` The whole value is removed, since the whole value was a comment.
        - For `key2`, the key, including its whole values will be removed.
        - For `key3`, since all its values are just comments, the key will still exist, but with a value of `None`."""
        if comment_end:
            pattern = _re.compile(
                rf"^((?:(?!{_re.escape(comment_start)}).)*){_re.escape(comment_start)}(?:(?:(?!{_re.escape(comment_end)}).)*)(?:{_re.escape(comment_end)})?(.*?)$"
            )

        def process_string(s: str) -> str | None:
            if comment_end:
                match = pattern.match(s)
                if match:
                    start, end = match.group(1).strip(), match.group(2).strip()
                    return f"{start}{comment_sep if start and end else ''}{end}" or None
                return s.strip() or None
            else:
                return None if s.lstrip().startswith(comment_start) else s.strip() or None

        def process_item(item: any) -> any:
            if isinstance(item, dict):
                return {
                    k: v for k, v in ((process_item(key), process_item(value)) for key, value in item.items()) if k is not None
                }
            if isinstance(item, (list, tuple, set, frozenset)):
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
        --------------------------------------------------------------------------------------------
        Ignores the specified (found) key/s or item/s from `ignore_paths`. Comments are not ignored
        when comparing. `comment_start` and `comment_end` are only used to correctly recognize the
        keys in the `ignore_paths`.\n
        --------------------------------------------------------------------------------------------
        The paths from `ignore_paths` and the `path_sep` parameter work exactly the same way as for
        the function `Data.get_path_id()`. See its documentation for more details."""

        def process_ignore_paths(
            ignore_paths: str | list[str],
        ) -> list[list[str]]:
            if isinstance(ignore_paths, str):
                ignore_paths = [ignore_paths]
            return [path.split(path_sep) for path in ignore_paths if path]

        def compare(
            d1: DataStructure,
            d2: DataStructure,
            ignore_paths: list[list[str]],
            current_path: list[str] = [],
        ) -> bool:
            if any(current_path == path[: len(current_path)] for path in ignore_paths):
                return True
            if type(d1) != type(d2):
                return False
            if isinstance(d1, dict):
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
    ) -> str | list[str]:
        """Generates a unique ID based on the path to a specific value within a nested data structure.\n
        -------------------------------------------------------------------------------------------------
        The `data` parameter is the list, tuple, or dictionary, which the id should be generated for.\n
        -------------------------------------------------------------------------------------------------
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
        index of the value, so `healthy->fruit->0`.\n
        -------------------------------------------------------------------------------------------------
        The comments marked with `comment_start` and `comment_end` will be removed, before trying to get
        the path id.\n
        -------------------------------------------------------------------------------------------------
        The `path_sep` param is the separator between the keys/indexes in the path (default is `->` just
        like in the example above).\n
        -------------------------------------------------------------------------------------------------
        If `ignore_not_found` is `True`, the function will return `None` if the value is not found
        instead of raising an error."""

        def process_path(path: str, data_obj: list | tuple | set | frozenset | dict) -> str | None:
            keys = path.split(path_sep)
            path_ids = []
            max_id_length = 0
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
                elif isinstance(data_obj, (list, tuple, set, frozenset)):
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
    def get_value_by_path_id(data: DataStructure, path_id: str, get_key: bool = False) -> any:
        """Retrieves the value from `data` using the provided `path_id`.\n
        -------------------------------------------------------------------------------------------------
        Input your `data` along with a `path_id` that was created before using `Data.get_path_id()`.
        If `get_key` is true and the final item is in a dict, it returns the key instead of the value.\n
        -------------------------------------------------------------------------------------------------
        The function will return the value (or key) from the path ID location, as long as the structure
        of `data` hasn't changed since creating the path ID to that value."""

        def get_nested(data: list | tuple | set | frozenset | dict, path: list[int], get_key: bool) -> any:
            parent = None
            for i, idx in enumerate(path):
                if isinstance(data, dict):
                    keys = list(data.keys())
                    if i == len(path) - 1 and get_key:
                        return keys[idx]
                    parent = data
                    data = data[keys[idx]]
                elif isinstance(data, (list, tuple, set, frozenset)):
                    if i == len(path) - 1 and get_key:
                        if parent is None or not isinstance(parent, dict):
                            raise ValueError("Cannot get key from a non-dict parent")
                        return next(key for key, value in parent.items() if value is data)
                    parent = data
                    data = list(data)[idx]  # CONVERT TO LIST FOR INDEXING
                else:
                    raise TypeError(f"Unsupported type '{type(data)}' at path '{path[:i+1]}'")
            return data

        return get_nested(data, Data.__sep_path_id(path_id), get_key)

    @staticmethod
    def set_value_by_path_id(
        data: DataStructure,
        update_values: str | list[str],
        sep: str = "::",
    ) -> list | tuple | dict:
        """Updates the value/s from `update_values` in the `data`.\n
        --------------------------------------------------------------------------------
        Input a list, tuple or dict as `data`, along with `update_values`, which is a
        path ID that was created before using `Data.get_path_id()`, together with the
        new value to be inserted where the path ID points to. The path ID and the new
        value are separated by `sep`, which per default is `::`.\n
        --------------------------------------------------------------------------------
        The value from path ID will be changed to the new value, as long as the
        structure of `data` hasn't changed since creating the path ID to that value."""

        def update_nested(
            data: list | tuple | set | frozenset | dict, path: list[int], value: any
        ) -> list | tuple | set | frozenset | dict:
            if len(path) == 1:
                if isinstance(data, dict):
                    keys = list(data.keys())
                    data = dict(data)
                    data[keys[path[0]]] = value
                elif isinstance(data, (list, tuple, set, frozenset)):
                    data = list(data)
                    data[path[0]] = value
                    data = type(data)(data)
            else:
                if isinstance(data, dict):
                    keys = list(data.keys())
                    key = keys[path[0]]
                    data = dict(data)
                    data[key] = update_nested(data[key], path[1:], value)
                elif isinstance(data, (list, tuple, set, frozenset)):
                    data = list(data)
                    data[path[0]] = update_nested(data[path[0]], path[1:], value)
                    data = type(data)(data)
            return data

        if isinstance(update_values, str):
            update_values = [update_values]
        valid_entries = [
            (parts[0].strip(), parts[1])
            for update_value in update_values
            if len(parts := update_value.split(str(sep).strip())) == 2
        ]
        if not valid_entries:
            raise ValueError(f"No valid update_values found: {update_values}")
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
        _syntax_hl: dict[str, str] = {},
    ) -> str:
        """Get nicely formatted data structure-strings.\n
        ------------------------------------------------------------------------------
        The indentation spaces-amount can be set with with `indent`.
        There are three different levels of `compactness`:
        - `0` expands everything possible
        - `1` only expands if there's other lists, tuples or dicts inside of data or,
          if the data's content is longer than `max_width`
        - `2` keeps everything collapsed (all on one line)\n
        ------------------------------------------------------------------------------
        If `as_json` is set to `True`, the output will be in valid JSON format."""
        if syntax_hl := bool(_syntax_hl):
            sep = f"[{_syntax_hl['punctuation']}]{sep}[_]"
            punct = {
                "'": f"[{_syntax_hl['punctuation']}]'[_]",
                '"': f'[{_syntax_hl["punctuation"]}]"[_]',
                ":": f"[{_syntax_hl['punctuation']}]:[_]",
                "(": f"[{_syntax_hl['punctuation']}]/([_]",
                ")": f"[{_syntax_hl['punctuation']}])[_]",
                "[": f"[{_syntax_hl['punctuation']}][[_]",
                "]": f"[{_syntax_hl['punctuation']}]][_]",
                "{": f"[{_syntax_hl['punctuation']}]{{[_]",
                "}": f"[{_syntax_hl['punctuation']}]}}[_]",
            }
        else:
            punct = {
                "'": "'",
                '"': '"',
                ":": ":",
                "(": "(",
                ")": ")",
                "[": "[",
                "]": "]",
                "{": "{",
                "}": "}",
            }

        def format_value(value: any, current_indent: int = None) -> str:
            if current_indent is not None and isinstance(value, dict):
                return format_dict(value, current_indent + indent)
            elif current_indent is not None and hasattr(value, "__dict__"):
                return format_dict(value.__dict__, current_indent + indent)
            elif current_indent is not None and isinstance(value, (list, tuple, set, frozenset)):
                return format_sequence(value, current_indent + indent)
            elif isinstance(value, (bytes, bytearray)):
                return format_value(Data.serialize_bytes(value), current_indent)
            elif isinstance(value, bool):
                val = str(value).lower() if as_json else str(value)
                return f"[{_syntax_hl['literal']}]{val}[_]" if syntax_hl else val
            elif isinstance(value, (int, float)):
                val = "null" if as_json and (_math.isinf(value) or _math.isnan(value)) else str(value)
                return f"[{_syntax_hl['number']}]{val}[_]" if syntax_hl else val
            elif isinstance(value, complex):
                return (
                    format_value(str(value).strip("()"))
                    if as_json
                    else (
                        f"{punct['(']}[{_syntax_hl['number']}]{str(value).strip('()')}[_]{punct[')']}"
                        if syntax_hl
                        else str(value)
                    )
                )
            elif value is None:
                val = "null" if as_json else "None"
                return f"[{_syntax_hl['literal']}]{val}[_]" if syntax_hl else val
            else:
                return (
                    (
                        f"{punct[r'\"']}[{_syntax_hl['str']}]{String.escape(str(value), r'\"')}[_]{punct[r'\"']}"
                        if syntax_hl
                        else f"{punct[r'\"']}{String.escape(str(value), r'\"')}{punct[r'\"']}"
                    )
                    if as_json
                    else (
                        f'{punct["'"]}[{_syntax_hl["str"]}]{String.escape(str(value), "'")}[_]{punct["'"]}'
                        if syntax_hl
                        else f'{punct["'"]}{String.escape(str(value), "'")}{punct["'"]}'
                    )
                )

        def should_expand(seq: list | tuple | dict) -> bool:
            if compactness == 0:
                return True
            if compactness == 2:
                return False
            complex_items = sum(1 for item in seq if isinstance(item, (list, tuple, dict, set, frozenset)))
            return (
                complex_items > 1
                or (complex_items == 1 and len(seq) > 1)
                or Data.chars_count(seq) + (len(seq) * len(sep)) > max_width
            )

        def format_dict(d: dict, current_indent: int) -> str:
            if not d or compactness == 2:
                return (
                    punct["{"]
                    + sep.join(f"{format_value(k)}{punct[':']} {format_value(v, current_indent)}" for k, v in d.items())
                    + punct["}"]
                )
            if not should_expand(d.values()):
                return (
                    punct["{"]
                    + sep.join(f"{format_value(k)}{punct[':']} {format_value(v, current_indent)}" for k, v in d.items())
                    + punct["}"]
                )
            items = []
            for k, val in d.items():
                formatted_value = format_value(val, current_indent)
                items.append(f"{' ' * (current_indent + indent)}{format_value(k)}{punct[':']} {formatted_value}")
            return punct["{"] + "\n" + f"{sep}\n".join(items) + f"\n{' ' * current_indent}" + punct["}"]

        def format_sequence(seq, current_indent: int) -> str:
            if as_json:
                seq = list(seq)
            if not seq or compactness == 2:
                return (
                    punct["["] + sep.join(format_value(item, current_indent) for item in seq) + punct["]"]
                    if isinstance(seq, list)
                    else punct["("] + sep.join(format_value(item, current_indent) for item in seq) + punct[")"]
                )
            if not should_expand(seq):
                return (
                    punct["["] + sep.join(format_value(item, current_indent) for item in seq) + punct["]"]
                    if isinstance(seq, list)
                    else punct["("] + sep.join(format_value(item, current_indent) for item in seq) + punct[")"]
                )
            items = [format_value(item, current_indent) for item in seq]
            formatted_items = f"{sep}\n".join(f'{" " * (current_indent + indent)}{item}' for item in items)
            if isinstance(seq, list):
                return f"{punct['[']}\n{formatted_items}\n{' ' * current_indent}{punct[']']}"
            else:
                return f"{punct['(']}\n{formatted_items}\n{' ' * current_indent}{punct[')']}"

        return format_dict(data, 0) if isinstance(data, dict) else format_sequence(data, 0)

    @staticmethod
    def print(
        data: DataStructure,
        indent: int = 4,
        compactness: int = 1,
        max_width: int = 127,
        sep: str = ", ",
        end: str = "\n",
        as_json: bool = False,
        syntax_highlighting: dict[str, str] = {
            "str": DEFAULT.color["blue"],
            "number": DEFAULT.color["magenta"],
            "literal": DEFAULT.color["cyan"],
            "punctuation": DEFAULT.color["darkgray"],
        },
    ) -> None:
        """Print nicely formatted data structures.\n
        ------------------------------------------------------------------------------
        The indentation spaces-amount can be set with with `indent`.
        There are three different levels of `compactness`:
        - `0` expands everything possible
        - `1` only expands if there's other lists, tuples or dicts inside of data or,
          if the data's content is longer than `max_width`
        - `2` keeps everything collapsed (all on one line)\n
        ------------------------------------------------------------------------------
        If `as_json` is set to `True`, the output will be in valid JSON format.\n
        ------------------------------------------------------------------------------
        The `syntax_highlighting` parameter is a dictionary with 4 keys for each part
        of the data:
        - `str`
        - `number`
        - `literal`
        - `punctuation`\n
        The key's values are the formatting codes to apply to this data part. For no
        syntax highlighting, set `syntax_highlighting` to `{}` or `None`.\n
        For more detailed information about formatting codes, see `xx_format_codes`
        module documentation."""
        FormatCodes.print(
            Data.to_str(data, indent, compactness, max_width, sep, as_json, syntax_highlighting),
            end=end,
        )

    @staticmethod
    def __sep_path_id(path_id: str) -> list[int]:
        if path_id.count(">") != 1:
            raise ValueError(f"Invalid path ID: {path_id}")
        id_part_len = int(path_id.split(">")[0])
        path_ids_str = path_id.split(">")[1]
        return [int(path_ids_str[i : i + id_part_len]) for i in range(0, len(path_ids_str), id_part_len)]
