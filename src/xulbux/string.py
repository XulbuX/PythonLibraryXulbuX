"""
This module provides the `String` class, which includes
various utility methods for string manipulation and conversion.
"""

from typing import Optional, Literal, Any
import json as _json
import ast as _ast
import re as _re


class String:
    """This class provides various utility methods for string manipulation and conversion."""

    @staticmethod
    def to_type(string: str) -> Any:
        """Will convert a string to the found type, including complex nested structures.\n
        -----------------------------------------------------------------------------------
        - `string` -⠀the string to convert"""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")

        try:
            return _ast.literal_eval(string := string.strip())
        except (ValueError, SyntaxError):
            try:
                return _json.loads(string)
            except _json.JSONDecodeError:
                return string

    @staticmethod
    def normalize_spaces(string: str, tab_spaces: int = 4) -> str:
        """Replaces all special space characters with normal spaces.\n
        ---------------------------------------------------------------
        - `tab_spaces` -⠀number of spaces to replace tab chars with"""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(tab_spaces, int):
            raise ValueError(f"The 'tab_spaces' parameter must be an integer, got {type(tab_spaces)}")
        elif tab_spaces < 0:
            raise ValueError(f"The 'tab_spaces' parameter must be non-negative, got {tab_spaces!r}")

        return string.replace("\t", " " * tab_spaces).replace("\u2000", " ").replace("\u2001", " ").replace("\u2002", " ") \
            .replace("\u2003", " ").replace("\u2004", " ").replace("\u2005", " ").replace("\u2006", " ") \
            .replace("\u2007", " ").replace("\u2008", " ").replace("\u2009", " ").replace("\u200A", " ")

    @staticmethod
    def escape(string: str, str_quotes: Optional[Literal["'", '"']] = None) -> str:
        """Escapes Python's special characters (e.g. `\\n`, `\\t`, ...) and quotes inside the string.\n
        --------------------------------------------------------------------------------------------------------
        - `string` -⠀the string to escape
        - `str_quotes` -⠀the type of quotes the string will be put inside of (or None to not escape quotes)<br>
          Can be either `"` or `'` and should match the quotes, the string will be put inside of.<br>
          So if your string will be `"string"`, `str_quotes` should be `"`.<br>
          That way, if the string includes the same quotes, they will be escaped."""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(str_quotes, (str, type(None))):
            raise ValueError(f"The 'str_quotes' parameter must be a string or None, got {type(str_quotes)}")

        string = string.replace("\\", r"\\").replace("\n", r"\n").replace("\r", r"\r").replace("\t", r"\t") \
            .replace("\b", r"\b").replace("\f", r"\f").replace("\a", r"\a")

        if str_quotes == '"':
            return string.replace("\\'", "'").replace('"', r"\"")
        elif str_quotes == "'":
            return string.replace('\\"', '"').replace("'", r"\'")
        else:
            return string

    @staticmethod
    def is_empty(string: Optional[str], spaces_are_empty: bool = False) -> bool:
        """Returns `True` if the string is considered empty and `False` otherwise.\n
        -----------------------------------------------------------------------------------------------
        - `string` -⠀the string to check (or `None`, which is considered empty)
        - `spaces_are_empty` -⠀if true, strings consisting only of spaces are also considered empty"""
        if not isinstance(string, (str, type(None))):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(spaces_are_empty, bool):
            raise TypeError(f"The 'spaces_are_empty' parameter must be a boolean, got {type(spaces_are_empty)}")

        return bool(
            (string in {"", None}) or \
            (spaces_are_empty and isinstance(string, str) and not string.strip())
        )

    @staticmethod
    def single_char_repeats(string: str, char: str) -> int | bool:
        """- If the string consists of only the same `char`, it returns the number of times it is present.
        - If the string doesn't consist of only the same character, it returns `False`.\n
        ---------------------------------------------------------------------------------------------------
        - `string` -⠀the string to check
        - `char` -⠀the character to check for repetition"""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(char, str):
            raise ValueError(f"The 'char' parameter must be a string, got {type(char)}")
        elif len(char) != 1:
            raise ValueError(f"The 'char' parameter must be a single character, got {char!r}")

        if len(string) == (len(char) * string.count(char)):
            return string.count(char)
        else:
            return False

    @staticmethod
    def decompose(case_string: str, seps: str = "-_", lower_all: bool = True) -> list[str]:
        """Will decompose the string (any type of casing, also mixed) into parts.\n
        ----------------------------------------------------------------------------
        - `case_string` -⠀the string to decompose
        - `seps` -⠀additional separators to split the string at
        - `lower_all` -⠀if true, all parts will be converted to lowercase"""
        if not isinstance(case_string, str):
            raise TypeError(f"The 'case_string' parameter must be a string, got {type(case_string)}")
        if not isinstance(seps, str):
            raise TypeError(f"The 'seps' parameter must be a string, got {type(seps)}")
        if not isinstance(lower_all, bool):
            raise TypeError(f"The 'lower_all' parameter must be a boolean, got {type(lower_all)}")

        return [
            (part.lower() if lower_all else part) \
            for part in _re.split(rf"(?<=[a-z])(?=[A-Z])|[{_re.escape(seps)}]", case_string)
        ]

    @staticmethod
    def to_camel_case(string: str, upper: bool = True) -> str:
        """Will convert the string of any type of casing to CamelCase.\n
        -----------------------------------------------------------------
        - `string` -⠀the string to convert
        - `upper` -⠀if true, it will convert to UpperCamelCase,
          otherwise to lowerCamelCase"""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(upper, bool):
            raise TypeError(f"The 'upper' parameter must be a boolean, got {type(upper)}")

        parts = String.decompose(string)

        return (
            ("" if upper else parts[0].lower()) + \
            "".join(part.capitalize() for part in (parts if upper else parts[1:]))
        )

    @staticmethod
    def to_delimited_case(string: str, delimiter: str = "_", screaming: bool = False) -> str:
        """Will convert the string of any type of casing to delimited case.\n
        -----------------------------------------------------------------------
        - `string` -⠀the string to convert
        - `delimiter` -⠀the delimiter to use between parts
        - `screaming` -⠀whether to convert all parts to uppercase"""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(delimiter, str):
            raise TypeError(f"The 'delimiter' parameter must be a string, got {type(delimiter)}")
        if not isinstance(screaming, bool):
            raise TypeError(f"The 'screaming' parameter must be a boolean, got {type(screaming)}")

        return delimiter.join(
            part.upper() if screaming else part \
            for part in String.decompose(string)
        )

    @staticmethod
    def get_lines(string: str, remove_empty_lines: bool = False) -> list[str]:
        """Will split the string into lines.\n
        ------------------------------------------------------------------------------------
        - `string` -⠀the string to split
        - `remove_empty_lines` -⠀if true, it will remove all empty lines from the result"""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(remove_empty_lines, bool):
            raise TypeError(f"The 'remove_empty_lines' parameter must be a boolean, got {type(remove_empty_lines)}")

        if not remove_empty_lines:
            return string.splitlines()
        elif not (lines := string.splitlines()):
            return []
        elif not (non_empty_lines := [line for line in lines if line.strip()]):
            return []
        else:
            return non_empty_lines

    @staticmethod
    def remove_consecutive_empty_lines(string: str, max_consecutive: int = 0) -> str:
        """Will remove consecutive empty lines from the string.\n
        -------------------------------------------------------------------------------------
        - `string` -⠀the string to process
        - `max_consecutive` -⠀the maximum number of allowed consecutive empty lines.<br>
          * If `0`, it will remove all consecutive empty lines.
          * If bigger than `0`, it will only allow `max_consecutive` consecutive empty lines
            and everything above it will be cut down to `max_consecutive` empty lines."""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(max_consecutive, int):
            raise ValueError(f"The 'max_consecutive' parameter must be an integer, got {type(max_consecutive)}")
        elif max_consecutive < 0:
            raise ValueError(f"The 'max_consecutive' parameter must be non-negative, got {max_consecutive!r}")

        return _re.sub(r"(\n\s*){2,}", r"\1" * (max_consecutive + 1), string)

    @staticmethod
    def split_count(string: str, count: int) -> list[str]:
        """Will split the string every `count` characters.\n
        -----------------------------------------------------
        - `string` -⠀the string to split
        - `count` -⠀the number of characters per part"""
        if not isinstance(string, str):
            raise TypeError(f"The 'string' parameter must be a string, got {type(string)}")
        if not isinstance(count, int):
            raise ValueError(f"The 'count' parameter must be an integer, got {type(count)}")
        elif count <= 0:
            raise ValueError(f"The 'count' parameter must be a positive integer, got {count!r}")

        return [string[i:i + count] for i in range(0, len(string), count)]
