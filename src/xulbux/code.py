"""
This module provides the `Code` class, which offers methods to work with code strings.
"""

from .data import Data
from .regex import Regex
from .string import String

from typing import Any
import regex as _rx


class Code:
    """This class includes methods to work with code strings."""

    @classmethod
    def add_indent(cls, code: str, indent: int, /) -> str:
        """Adds `indent` spaces at the beginning of each line.\n
        -----------------------------------------------------------------------------
        *   `code` – The code to indent.
        *   `indent` – The amount of spaces to add at the beginning of each line."""

        if indent < 0:
            raise ValueError(f"The 'indent' parameter must be non-negative, got {indent!r}")

        return "\n".join(" " * indent + line for line in code.splitlines())

    @classmethod
    def get_tab_spaces(cls, code: str, /) -> int:
        """Will try to get the amount of spaces used for indentation.\n
        ----------------------------------------------------------------
        *   `code` – The code to analyze."""

        indents = [len(line) - len(line.lstrip()) for line in String.get_lines(code, remove_empty_lines=True)]
        return min(non_zero_indents) if (non_zero_indents := [indt for indt in indents if indt > 0]) else 0

    @classmethod
    def change_tab_size(cls, code: str, new_tab_size: int, /, *, remove_empty_lines: bool = False) -> str:
        """Replaces all tabs with `new_tab_size` spaces.\n
        -----------------------------------------------------------------------------------
        *   `code` – The code to modify the tab size of.
        *   `new_tab_size` – The new amount of spaces per tab.
        *   `remove_empty_lines` – If true, empty lines will be removed in the process."""

        if new_tab_size < 0:
            raise ValueError(f"The 'new_tab_size' parameter must be non-negative, got {new_tab_size!r}")

        code_lines = String.get_lines(code, remove_empty_lines=remove_empty_lines)

        if ((tab_spaces := cls.get_tab_spaces(code)) == new_tab_size) or tab_spaces == 0:
            if remove_empty_lines:
                return "\n".join(code_lines)
            return code

        result: list[str] = []
        for line in code_lines:
            indent_level = (len(line) - len(stripped := line.lstrip())) // tab_spaces
            result.append((" " * (indent_level * new_tab_size)) + stripped)

        return "\n".join(result)

    @classmethod
    def get_func_calls(cls, code: str, /) -> list[list[Any]]:
        """Will try to get all function calls and return them as a list.\n
        -------------------------------------------------------------------
        *   `code` – The code to analyze."""

        nested_func_calls: list[list[Any]] = []

        for _, func_attrs in (funcs := _rx.findall(r"(?i)" + Regex.func_call(), code)):
            if nested_calls := _rx.findall(r"(?i)" + Regex.func_call(), func_attrs):
                nested_func_calls.extend(nested_calls)

        return list(Data.remove_duplicates(funcs + nested_func_calls))

    @classmethod
    def is_js(cls, code: str, /, *, funcs: set[str] = {"__", "$t", "$lang"}) -> bool:
        """Will check if the code is very likely to be JavaScript.\n
        ---------------------------------------------------------------
        *   `code` – The code to analyze.
        *   `funcs` – A list of custom function names to check for."""

        if len(code.strip()) < 3:
            return False

        for fn in funcs:
            if _rx.match(r"^[\s\n]*" + _rx.escape(fn) + r"\([^\)]*\)[\s\n]*$", code):
                return True

        direct_js_patterns = [
            r"""^[\s\n]*\$\(["'][^"']+["']\)\.[\w]+\([^\)]*\);?[\s\n]*$""",  # jQuery calls
            r"^[\s\n]*\$\.[a-zA-Z]\w*\([^\)]*\);?[\s\n]*$",  # $.ajax(), etc.
            r"^[\s\n]*\(\s*function\s*\(\)\s*\{.*\}\s*\)\(\);?[\s\n]*$",  # IIFE
            r"^[\s\n]*document\.[a-zA-Z]\w*\([^\)]*\);?[\s\n]*$",  # document.getElementById()
            r"^[\s\n]*window\.[a-zA-Z]\w*\([^\)]*\);?[\s\n]*$",  # window.alert()
            r"^[\s\n]*console\.[a-zA-Z]\w*\([^\)]*\);?[\s\n]*$",  # console.log()
        ]
        for pattern in direct_js_patterns:
            if _rx.match(pattern, code):
                return True

        arrow_function_patterns = [
            r"^[\s\n]*\b[\w_]+\s*=\s*\([^\)]*\)\s*=>\s*[^;{]*[;]?[\s\n]*$",  # const x = (y) => y*2;
            r"^[\s\n]*\b[\w_]+\s*=\s*[\w_]+\s*=>\s*[^;{]*[;]?[\s\n]*$",  # const x = y => y*2;
            r"^[\s\n]*\(\s*[\w_,\s]+\s*\)\s*=>\s*[^;{]*[;]?[\s\n]*$",  # (x) => x*2
            r"^[\s\n]*[\w_]+\s*=>\s*[^;{]*[;]?[\s\n]*$",  # x => x*2
        ]
        for pattern in arrow_function_patterns:
            if _rx.match(pattern, code):
                return True

        js_score = 0.0
        funcs_pattern = r"(" + "|".join(_rx.escape(fn) for fn in funcs) + r")" + Regex.brackets("()")
        js_indicators: list[tuple[str, float]] = [
            (r"\b(var|let|const)\s+[\w_$]+", 2.0),  # JS variable declarations
            (r"\$[\w_$]+\s*=", 2.0),  # jQuery-style variables
            (r"\$[\w_$]+\s*\(", 2.0),  # jQuery function calls
            (r"\bfunction\s*[\w_$]*\s*\(", 2.0),  # Function declarations
            (r"[\w_$]+\s*=\s*function\s*\(", 2.0),  # Function assignments
            (r"\b[\w_$]+\s*=>\s*[\{\(]", 2.0),  # Arrow functions
            (r"\(function\s*\(\)\s*\{", 2.0),  # IIFE pattern
            (funcs_pattern, 2.0),  # Custom predefined functions
            (r"\b(true|false|null|undefined)\b", 1.0),  # JS literals
            (r"===|!==|\+\+|--|\|\||&&", 1.5),  # JS-specific operators
            (r"\bnew\s+[\w_$]+\s*\(", 1.5),  # Object instantiation with `new`
            (r"\b(document|window|console|Math|Array|Object|String|Number)\.", 2.0),  # JS objects
            (r"\basync\s+function|\bawait\b", 2.0),  # async/await
            (r"\b(if|for|while|switch)\s*\([^)]*\)\s*\{", 1.0),  # Control structures with braces
            (r"\btry\s*\{[^}]*\}\s*catch\s*\(", 1.5),  # Try-catch
            (r";[\s\n]*$", 0.5),  # Semicolon line endings
        ]

        line_endings = [line.strip() for line in code.splitlines() if line.strip()]
        if (semicolon_endings := sum(1 for line in line_endings if line.endswith(";"))) >= 1:
            js_score += min(semicolon_endings, 2)
        if (opening_braces := code.count("{")) > 0 and opening_braces == code.count("}"):
            js_score += 1

        for pattern, score in js_indicators:
            if matches := _rx.compile(pattern, _rx.IGNORECASE).findall(code):
                js_score += len(matches) * score

        return js_score >= 2.0
