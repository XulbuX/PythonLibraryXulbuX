"""
Provides tools for parsing and transforming source code.

Includes methods for removing comments, formatting docstrings,
and stripping ANSI escape sequences.
"""

from . import data as _data_module
from . import regex as _regex_module
from . import string as _string_module
from .regex import LazyRegex

from typing import Any, Final
import regex as _rx

_PATTERNS: Final[LazyRegex] = LazyRegex(
    arrow_function_patterns=(
        r"^[\s\n]*(?:\b[\w_]+\s*=\s*\([^\)]*\)\s*=>\s*[^;{]*[;]?|"
        r"\b[\w_]+\s*=\s*[\w_]+\s*=>\s*[^;{]*[;]?|"
        r"\(\s*[\w_,\s]+\s*\)\s*=>\s*[^;{]*[;]?|"
        r"[\w_]+\s*=>\s*[^;{]*[;]?)[\s\n]*$"
    ),
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


def add_indent(code: str, indent: int, /) -> str:
    """Adds `indent` spaces at the beginning of each line.\n
    -----------------------------------------------------------------------------
    *   `code` – The code to indent.
    *   `indent` – The amount of spaces to add at the beginning of each line."""

    if indent < 0:
        raise ValueError(f"The 'indent' parameter must be non-negative, got {indent!r}")

    return "\n".join([" " * indent + line for line in code.splitlines()])


def get_tab_spaces(code: str, /) -> int:
    """Will try to get the amount of spaces used for indentation.\n
    ----------------------------------------------------------------
    *   `code` – The code to analyze."""

    indents = [len(line) - len(line.lstrip()) for line in _string_module.get_lines(code, remove_empty_lines=True)]
    return min(non_zero_indents) if (non_zero_indents := [indt for indt in indents if indt > 0]) else 0


def change_tab_size(code: str, new_tab_size: int, /, *, remove_empty_lines: bool = False) -> str:
    """Replaces all tabs with `new_tab_size` spaces.\n
    -----------------------------------------------------------------------------------
    *   `code` – The code to modify the tab size of.
    *   `new_tab_size` – The new amount of spaces per tab.
    *   `remove_empty_lines` – If true, empty lines will be removed in the process."""

    if new_tab_size < 0:
        raise ValueError(f"The 'new_tab_size' parameter must be non-negative, got {new_tab_size!r}")

    code_lines = _string_module.get_lines(code, remove_empty_lines=remove_empty_lines)

    if ((tab_spaces := get_tab_spaces(code)) == new_tab_size) or tab_spaces == 0:
        if remove_empty_lines:
            return "\n".join(code_lines)
        return code

    result: list[str] = []
    for line in code_lines:
        indent_level = (len(line) - len(stripped := line.lstrip())) // tab_spaces
        result.append((" " * (indent_level * new_tab_size)) + stripped)

    return "\n".join(result)


def get_func_calls(code: str, /) -> list[list[Any]]:
    """Will try to get all function calls and return them as a list.\n
    -------------------------------------------------------------------
    *   `code` – The code to analyze."""

    nested_func_calls: list[list[Any]] = []

    for _, func_attrs in (funcs := _PATTERNS.func_call.findall(code)):
        if nested_calls := _PATTERNS.func_call.findall(func_attrs):
            nested_func_calls.extend(nested_calls)

    return list(_data_module.remove_duplicates(funcs + nested_func_calls))


def is_js(code: str, /, *, funcs: set[str] | frozenset[str] = frozenset({"__", "$t", "$lang"})) -> bool:
    """Will check if the code is very likely to be JavaScript.\n
    ---------------------------------------------------------------
    *   `code` – The code to analyze.
    *   `funcs` – A list of custom function names to check for."""

    if len(code.strip()) < 3:
        return False

    if funcs:
        funcs_pattern_direct = r"^[\s\n]*(" + "|".join([_rx.escape(fn) for fn in funcs]) + r")\([^\)]*\)[\s\n]*$"
        if _rx.match(funcs_pattern_direct, code):
            return True

    if _PATTERNS.direct_js_patterns.match(code):
        return True

    if _PATTERNS.arrow_function_patterns.match(code):
        return True

    js_score = 0.0
    if funcs:
        funcs_pattern2 = r"(" + "|".join([_rx.escape(fn) for fn in funcs]) + r")" + _regex_module.brackets("()")
        if matches := _rx.compile(funcs_pattern2, _rx.IGNORECASE).findall(code):
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
