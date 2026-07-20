"""
This module provides the `String` class, which includes
various utility methods for string manipulation and conversion.
"""

import ast as _ast
import json as _json
import re as _re
from typing import Any, Literal


class String:
    """This class provides various utility methods for string manipulation and conversion."""

    @classmethod
    def to_type(cls, string: str, /) -> Any:
        """Will convert a string to the found type, including complex nested structures.\n
        -----------------------------------------------------------------------------------
        *   `string` – The string to convert."""

        try:
            return _ast.literal_eval(string := string.strip())
        except (ValueError, SyntaxError):
            try:
                return _json.loads(string)
            except _json.JSONDecodeError:
                return string

    @classmethod
    def normalize_spaces(cls, string: str, /, tab_spaces: int = 4) -> str:
        """Replaces all special space characters with normal spaces.\n
        ------------------------------------------------------------------
        *   `string` – The string to normalize.
        *   `tab_spaces` – Number of spaces to replace tab chars with."""

        if tab_spaces < 0:
            raise ValueError(f"The 'tab_spaces' parameter must be non-negative, got {tab_spaces!r}")

        table: dict[str, str | int | None] = {
            "\t": " " * tab_spaces,
            "\u2000": " ",
            "\u2001": " ",
            "\u2002": " ",
            "\u2003": " ",
            "\u2004": " ",
            "\u2005": " ",
            "\u2006": " ",
            "\u2007": " ",
            "\u2008": " ",
            "\u2009": " ",
            "\u200a": " ",
        }

        return string.translate(str.maketrans(table))

    @classmethod
    def escape(cls, string: str, /, str_quotes: Literal["'", '"'] | None = None) -> str:
        """Escapes Python's special characters (e.g., `\\n`, `\\t`, …) and quotes inside the string.\n
        -------------------------------------------------------------------------------------------------------------
        *   `string` – The string to escape.
        *   `str_quotes` – The type of quotes the string will be put inside of (or `None` to not escape quotes):<br>
            Can be either `"` or `'` and should match the quotes, the string will be put inside of.<br>
            So if your string will be `"string"`, `str_quotes` should be `"`.<br>
            That way, if the string includes the same quotes, they will be escaped."""

        string = (
            string.replace("\\", "\\\\")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
            .replace("\b", "\\b")
            .replace("\f", "\\f")
            .replace("\a", "\\a")
        )

        if str_quotes == '"':
            return string.replace("\\'", "'").replace('"', '\\"')
        elif str_quotes == "'":
            return string.replace('\\"', '"').replace("'", "\\'")
        else:
            return string

    @classmethod
    def is_empty(cls, string: str | None, /, *, spaces_are_empty: bool = False) -> bool:
        """Returns `True` if the string is considered empty and `False` otherwise.\n
        --------------------------------------------------------------------------------------------------
        *   `string` – The string to check (or `None`, which is considered empty).
        *   `spaces_are_empty` – If true, strings consisting only of spaces are also considered empty."""

        return bool((string in {"", None}) or (spaces_are_empty and isinstance(string, str) and not string.strip()))

    @classmethod
    def single_char_repeats(cls, string: str, char: str, /) -> int:
        """*   If the string consists of only the same `char`, it returns the number of times it is present.<br>
        *   If the string is empty or doesn't consist of only the same character, it returns `0`.\n
        ---------------------------------------------------------------------------------------------------------
        *   `string` – The string to check.
        *   `char` – The character to check for repetition."""

        if len(char) != 1:
            raise ValueError(f"The 'char' parameter must be a single character, got {char!r}")

        if len(string) == string.count(char):
            return string.count(char)
        else:
            return 0

    @classmethod
    def decompose(cls, case_string: str, /, seps: str = "-_", *, lower_all: bool = True) -> list[str]:
        """Will decompose the string (any type of casing, also mixed) into parts.\n
        ----------------------------------------------------------------------------
        *   `case_string` – The string to decompose.
        *   `seps` – Additional separators to split the string at.
        *   `lower_all` – If true, all parts will be converted to lowercase."""

        return [
            (part.lower() if lower_all else part)
            for part in _re.split(rf"(?<=[a-z])(?=[A-Z])|[{_re.escape(seps)}]", case_string)
        ]

    @classmethod
    def to_camel_case(cls, string: str, /, *, upper: bool = True) -> str:
        """Will convert the string of any type of casing to CamelCase.\n
        ------------------------------------------------------------------------------------------
        *   `string` – The string to convert.
        *   `upper` – If true, it will convert to UpperCamelCase, otherwise to lowerCamelCase."""

        parts = cls.decompose(string)

        return ("" if upper else parts[0].lower()) + "".join(part.capitalize() for part in (parts if upper else parts[1:]))

    @classmethod
    def to_delimited_case(cls, string: str, /, delimiter: str = "_", *, screaming: bool = False) -> str:
        """Will convert the string of any type of casing to delimited case.\n
        -----------------------------------------------------------------------
        *   `string` – The string to convert.
        *   `delimiter` – The delimiter to use between parts.
        *   `screaming` – Whether to convert all parts to uppercase."""

        return delimiter.join(part.upper() if screaming else part for part in cls.decompose(string))

    @classmethod
    def get_lines(cls, string: str, /, *, remove_empty_lines: bool = False) -> list[str]:
        """Will split the string into lines.\n
        ---------------------------------------------------------------------------------------
        *   `string` – The string to split.
        *   `remove_empty_lines` – If true, it will remove all empty lines from the result."""

        if not remove_empty_lines:
            return string.splitlines()
        elif not (lines := string.splitlines()) or not (non_empty_lines := [line for line in lines if line.strip()]):
            return []
        else:
            return non_empty_lines

    @classmethod
    def remove_consecutive_empty_lines(cls, string: str, /, max_consecutive: int = 0) -> str:
        """Will remove consecutive empty lines from the string.\n
        ---------------------------------------------------------------------------------------------
        *   `string` – The string to process.
        *   `max_consecutive` – The maximum number of allowed consecutive empty lines:<br>
            -   If `0`, it will remove all consecutive empty lines.
            -   If bigger than `0`, it will only allow `max_consecutive` consecutive empty lines<br>
                and everything above it will be cut down to `max_consecutive` empty lines."""

        if max_consecutive < 0:
            raise ValueError(f"The 'max_consecutive' parameter must be non-negative, got {max_consecutive!r}")

        return _re.sub(r"(\n\s*){2,}", r"\1" * (max_consecutive + 1), string)

    @classmethod
    def split_count(cls, string: str, count: int, /) -> list[str]:
        """Will split the string every `count` characters.\n
        -----------------------------------------------------
        *   `string` – The string to split.
        *   `count` – The number of characters per part."""

        if count <= 0:
            raise ValueError(f"The 'count' parameter must be a positive integer, got {count!r}")

        return [string[i : i + count] for i in range(0, len(string), count)]
