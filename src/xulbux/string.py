"""
Provides utility functions for advanced string manipulation.

Includes methods for casing, stripping, finding differences,
and safely converting to numeric or boolean types.
"""

from . import data as _data_module
from . import regex as _regex_module
from .regex import LazyRegex

import ast as _ast
import json as _json
from typing import Any, Final, Literal
import regex as _rx

_PATTERNS: Final[LazyRegex] = LazyRegex(
    arrow_function_patterns=(
        r"^[\s\n]*(?:\b[\w_]+\s*=\s*\([^\)]*\)\s*=>\s*[^;{]*[;]?|"
        r"\b[\w_]+\s*=\s*[\w_]+\s*=>\s*[^;{]*[;]?|"
        r"\(\s*[\w_,\s]+\s*\)\s*=>\s*[^;{]*[;]?|"
        r"[\w_]+\s*=>\s*[^;{]*[;]?)[\s\n]*$"
    ),
    consecutive_empty_lines=r"(\n\s*){2,}",
    decompose_default=r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|[\-_]",
    default_js_funcs2=r"(?i)(?:__|\\\$t|\\\$lang)" + _regex_module.brackets(),
    default_js_funcs_direct=r"^[\s\n]*(?:__|\\\$t|\\\$lang)\([^\)]*\)[\s\n]*$",
    direct_js_patterns=(
        r"^[\s\n]*(?:\$\([\"'][^\"']+[\"']\)\.[\w]+\([^\)]*\);?|"
        r"\$\.[a-zA-Z]\w*\([^\)]*\);?|"
        r"\(\s*function\s*\(\)\s*\{.*\}\s*\)\(\);?|"
        r"document\.[a-zA-Z]\w*\([^\)]*\);?|"
        r"window\.[a-zA-Z]\w*\([^\)]*\);?|"
        r"console\.[a-zA-Z]\w*\([^\)]*\);?)[\s\n]*$"
    ),
    func_call=r"(?i)" + _regex_module.func_call(),
    js_indicators_arrow_func=r"(?i)\b[\w_$]+\s*=>\s*[\{\(]",
    js_indicators_async=r"(?i)\basync\s+function|\bawait\b",
    js_indicators_control=r"(?i)\b(if|for|while|switch)\s*\([^)]*\)\s*\{",
    js_indicators_func_assign=r"(?i)[\w_$]+\s*=\s*function\s*\(",
    js_indicators_func_decl=r"(?i)\bfunction\s*[\w_$]*\s*\(",
    js_indicators_iife=r"(?i)\(function\s*\(\)\s*\{",
    js_indicators_jquery_call=r"(?i)\$[\w_$]+\s*\(",
    js_indicators_jquery_var=r"(?i)\$[\w_$]+\s*=",
    js_indicators_literals=r"(?i)\b(true|false|null|undefined)\b",
    js_indicators_new=r"(?i)\bnew\s+[\w_$]+\s*\(",
    js_indicators_objects=r"(?i)\b(document|window|console|Math|Array|Object|String|Number)\.",
    js_indicators_operators=r"(?i)===|!==|\+\+|--|\|\||&&",
    js_indicators_semicolon=r"(?i);[\s\n]*$",
    js_indicators_try_catch=r"(?i)\btry\s*\{[^}]*\}\s*catch\s*\(",
    js_indicators_var_let_const=r"(?i)\b(var|let|const)\s+[\w_$]+",
)

_DEFAULT_JS_FUNCS: Final[frozenset[str]] = frozenset({"__", "$t", "$lang"})
"""Default function identifiers frequently used in localized JavaScript frameworks."""

_JS_INDICATOR_SCORES: Final[dict[str, float]] = {
    "js_indicators_arrow_func": 2.0,
    "js_indicators_async": 2.0,
    "js_indicators_control": 1.0,
    "js_indicators_func_assign": 2.0,
    "js_indicators_func_decl": 2.0,
    "js_indicators_iife": 2.0,
    "js_indicators_jquery_call": 2.0,
    "js_indicators_jquery_var": 2.0,
    "js_indicators_literals": 1.0,
    "js_indicators_new": 1.5,
    "js_indicators_objects": 2.0,
    "js_indicators_operators": 1.5,
    "js_indicators_semicolon": 0.5,
    "js_indicators_try_catch": 1.5,
    "js_indicators_var_let_const": 2.0,
}
"""Scoring weights assigned to JavaScript-indicative syntactic patterns."""

_SPACE_TRANS_CACHE: dict[int, dict[int, str | int | None]] = {}
"""Cache mapping tab space widths to compiled translation tables for space normalization."""


def to_type(string: str, /) -> Any:
    """Will convert a string to the found type, including complex nested structures.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to convert.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    val1 = xx.string.to_type("12345")
    val2 = xx.string.to_type("[1, 2, 3]")
    val3 = xx.string.to_type('{"enabled": true, "timeout": 30}')
    ```

    <!-- DOCS: <AttachedCode> -->
    Parsed Types:

    ```python
    val1 = 12345  # int
    val2 = [1, 2, 3]  # list[int]
    val3 = {"enabled": True, "timeout": 30}  # dict[str, Any]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    try:
        return _ast.literal_eval(string := string.strip())
    except (ValueError, SyntaxError):
        try:
            return _json.loads(string)
        except _json.JSONDecodeError:
            return string


def normalize_spaces(string: str, /, tab_spaces: int = 4) -> str:
    """Replaces all special space characters with normal spaces.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to normalize.
    *   `tab_spaces` – Number of spaces to replace tab chars with."""

    if tab_spaces < 0:
        raise ValueError(f"The 'tab_spaces' parameter must be non-negative, got {tab_spaces!r}")

    if tab_spaces not in _SPACE_TRANS_CACHE:
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
        _SPACE_TRANS_CACHE[tab_spaces] = str.maketrans(table)

    return string.translate(_SPACE_TRANS_CACHE[tab_spaces])


def escape(string: str, /, str_quotes: Literal["'", '"'] | None = None) -> str:
    """Escapes Python's special characters (e.g., `\\n`, `\\t`, …) and quotes inside the string.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to escape.
    *   `str_quotes` – The type of quotes the string will be put inside of
        (or `None` to not escape quotes):<br>
        Can be either `"` or `'` and should match the quotes, the string will be put inside of.<br>
        So if your string will be `"string"`, `str_quotes` should be `"`.<br>
        That way, if the string includes the same quotes, they will be escaped."""

    string = (
        string
        .replace("\\", r"\\")
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


def is_empty(string: str | None, /, *, spaces_are_empty: bool = False) -> bool:
    """Returns `True` if the string is considered empty and `False` otherwise.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to check (or `None`, which is considered empty).
    *   `spaces_are_empty` – If true, strings consisting only of spaces are also considered empty."""

    return not string or (spaces_are_empty and not string.strip())


def count_char_repeats(string: str, char: str, /) -> int:
    """*   If the string consists of only the same `char`,
        it returns the number of times it is present.<br>
    *   If the string is empty or doesn't consist of only the same character, it returns `0`.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to check.
    *   `char` – The character to check for repetition."""

    if len(char) != 1:
        raise ValueError(f"The 'char' parameter must be a single character, got {char!r}")

    char_count = string.count(char)
    return char_count if len(string) == char_count else 0


def decompose(string: str, /, seps: str = "-_", *, lower_all: bool = True) -> list[str]:
    """Will decompose the string (any type of casing, also mixed) into parts.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to decompose.
    *   `seps` – Additional separators to split the string at.
    *   `lower_all` – If true, all parts will be converted to lowercase.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    parts = xx.string.decompose("myHTTPServer_port-config")
    ```

    <!-- DOCS: <AttachedCode> -->
    Decomposed Parts:

    ```python
    ["my", "http", "server", "port", "config"]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    if seps == "-_":
        parts = _PATTERNS.decompose_default.split(string)
    else:
        parts = _rx.split(rf"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|[{_rx.escape(seps)}]", string)

    return [(part.lower() if lower_all else part) for part in parts]


def to_camel_case(string: str, /, *, upper: bool = True) -> str:
    """Will convert the string of any type of casing to CamelCase.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to convert.
    *   `upper` – If true, it will convert to UpperCamelCase, otherwise to lowerCamelCase.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    upper_camel = xx.string.to_camel_case("my_var_name")  # MyVarName
    lower_camel = xx.string.to_camel_case("my_var_name", upper=False)  # myVarName
    ```"""

    parts = decompose(string)

    return ("" if upper else parts[0].lower()) + "".join([part.capitalize() for part in (parts if upper else parts[1:])])


def to_delimited_case(string: str, /, delimiter: str = "_", *, screaming: bool = False) -> str:
    """Will convert the string of any type of casing to delimited case.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to convert.
    *   `delimiter` – The delimiter to use between parts.
    *   `screaming` – Whether to convert all parts to uppercase.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    kebab = xx.string.to_delimited_case("MyVarName", delimiter="-")  # my-var-name
    screaming_snake = xx.string.to_delimited_case("MyVarName", screaming=True)  # MY_VAR_NAME
    ```"""

    return delimiter.join([part.upper() if screaming else part for part in decompose(string)])


def get_lines(string: str, /, *, remove_empty_lines: bool = False) -> list[str]:
    """Will split the string into lines.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to split.
    *   `remove_empty_lines` – If true, it will remove all empty lines from the result."""

    if not remove_empty_lines:
        return string.splitlines()
    elif not (lines := string.splitlines()) or not (non_empty_lines := [line for line in lines if line.strip()]):
        return []
    else:
        return non_empty_lines


def remove_consecutive_empty_lines(string: str, /, max_consecutive: int = 0) -> str:
    """Will remove consecutive empty lines from the string.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to process.
    *   `max_consecutive` – The maximum number of allowed consecutive empty lines:<br>
        -   If `0`, it will remove all consecutive empty lines.
        -   If bigger than `0`, it will only allow `max_consecutive` consecutive empty lines<br>
            and everything above it will be cut down to `max_consecutive` empty lines."""

    if max_consecutive < 0:
        raise ValueError(f"The 'max_consecutive' parameter must be non-negative, got {max_consecutive!r}")

    return _PATTERNS.consecutive_empty_lines.sub("\n" * (max_consecutive + 1), string)


def chunk(string: str, chunk_size: int, /) -> list[str]:
    """Splits the string into chunks of `chunk_size` characters.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to split.
    *   `chunk_size` – The number of characters per chunk.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    chunks = xx.string.chunk("abcdefghi", 3)  # ["abc", "def", "ghi"]
    ```"""

    if chunk_size <= 0:
        raise ValueError(f"The 'chunk_size' parameter must be a positive integer, got {chunk_size!r}")

    return [string[i : i + chunk_size] for i in range(0, len(string), chunk_size)]


def add_indent(string: str, indent: int, /) -> str:
    """Adds `indent` spaces at the beginning of each line.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to indent.
    *   `indent` – The amount of spaces to add at the beginning of each line."""

    if indent < 0:
        raise ValueError(f"The 'indent' parameter must be non-negative, got {indent!r}")

    return "\n".join([" " * indent + line for line in string.splitlines()])


def get_tab_spaces(string: str, /) -> int:
    """Will try to get the amount of spaces used for indentation.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to analyze."""

    indents = [len(line) - len(line.lstrip()) for line in get_lines(string, remove_empty_lines=True)]
    return min(non_zero_indents) if (non_zero_indents := [indt for indt in indents if indt > 0]) else 0


def change_tab_spaces(string: str, space_count: int, /, *, remove_empty_lines: bool = False) -> str:
    """Rescales indentation across lines to use `space_count` spaces per indentation level.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to modify the indentation of.
    *   `space_count` – The new number of spaces per indentation level.
    *   `remove_empty_lines` – If true, empty lines will be removed in the process."""

    if space_count < 0:
        raise ValueError(f"The 'space_count' parameter must be non-negative, got {space_count!r}")

    code_lines = get_lines(string, remove_empty_lines=remove_empty_lines)

    if ((tab_spaces := get_tab_spaces(string)) == space_count) or tab_spaces == 0:
        if remove_empty_lines:
            return "\n".join(code_lines)
        return string

    result: list[str] = []
    for line in code_lines:
        indent_level = (len(line) - len(stripped := line.lstrip())) // tab_spaces
        result.append((" " * (indent_level * space_count)) + stripped)

    return "\n".join(result)


def extract_func_calls(code: str, /) -> list[tuple[str, str]]:
    """Will try to get all function calls and return them as a list.\n
    ----------------------------------------------------------------------------------------------------
    *   `code` – The code to analyze.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    code_snippet = "result = math.sqrt(foo.bar(10)) + calculate()"
    calls = xx.string.extract_func_calls(code_snippet)
    ```

    <!-- DOCS: <AttachedCode> -->
    Extracted Calls:

    ```python
    [
        ("sqrt", "foo.bar(10)"),
        ("calculate", ""),
        ("bar", "10"),
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    nested_func_calls: list[tuple[str, str]] = []

    for _, func_attrs in (funcs := _PATTERNS.func_call.findall(code)):
        if nested_calls := _PATTERNS.func_call.findall(func_attrs):
            nested_func_calls.extend(nested_calls)

    return list(_data_module.remove_duplicates(funcs + nested_func_calls))


def _matches_js_funcs_direct(code: str, funcs: set[str] | frozenset[str], /) -> bool:
    """Internal helper to test if code matches a direct top-level JavaScript function call."""

    if funcs == _DEFAULT_JS_FUNCS:
        return bool(_PATTERNS.default_js_funcs_direct.match(code))

    return bool(_rx.match(r"^[\s\n]*(" + "|".join([_rx.escape(fn) for fn in funcs]) + r")\([^\)]*\)[\s\n]*$", code))


def is_js(code: str, /, *, funcs: set[str] | frozenset[str] = _DEFAULT_JS_FUNCS) -> bool:
    """Will check if the code is very likely to be JavaScript.\n
    ----------------------------------------------------------------------------------------------------
    *   `code` – The code to analyze.
    *   `funcs` – A list of custom function names to check for.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    js_code = "const add = (a, b) => { return a + b; };"
    result = xx.string.is_js(js_code)
    ```

    <!-- DOCS: <AttachedCode> -->
    Result:

    ```python
    True
    ```
    <!-- DOCS: </AttachedCode> -->"""

    if len(code.strip()) < 3:
        return False

    elif (
        (funcs and _matches_js_funcs_direct(code, funcs))
        or _PATTERNS.direct_js_patterns.match(code)
        or _PATTERNS.arrow_function_patterns.match(code)
    ):
        return True

    js_score = 0.0

    if funcs:
        if funcs == _DEFAULT_JS_FUNCS:
            matches = _PATTERNS.default_js_funcs2.findall(code)
        else:
            funcs_pattern2 = r"(" + "|".join([_rx.escape(fn) for fn in funcs]) + r")" + _regex_module.brackets()
            matches = _rx.compile(funcs_pattern2, _rx.IGNORECASE).findall(code)

        if matches:
            js_score += len(matches) * 2.0

    line_endings = [line.strip() for line in code.splitlines() if line.strip()]

    if (semicolon_endings := sum([1 for line in line_endings if line.endswith(";")])) >= 1:  # ruff:ignore[unnecessary-comprehension-in-call]
        js_score += min(semicolon_endings, 2)
    if (opening_braces := code.count("{")) > 0 and opening_braces == code.count("}"):
        js_score += 1

    for attr, score in _JS_INDICATOR_SCORES.items():
        if matches := getattr(_PATTERNS, attr).findall(code):
            js_score += len(matches) * score

    return js_score >= 2.0
