from .string import String
from .regex import Regex
from .data import Data

import regex as _rx


class Code:

    @staticmethod
    def add_indent(code: str, indent: int) -> str:
        """Adds `indent` spaces at the beginning of each line."""
        indented_lines = [" " * indent + line for line in code.splitlines()]
        return "\n".join(indented_lines)

    @staticmethod
    def get_tab_spaces(code: str) -> int:
        """Will try to get the amount of spaces used for indentation."""
        code_lines = String.get_lines(code, remove_empty_lines=True)
        indents = [len(line) - len(line.lstrip()) for line in code_lines]
        non_zero_indents = [i for i in indents if i > 0]
        return min(non_zero_indents) if non_zero_indents else 0

    @staticmethod
    def change_tab_size(code: str, new_tab_size: int, remove_empty_lines: bool = False) -> str:
        """Replaces all tabs with `new_tab_size` spaces.\n
        ----------------------------------------------------------------------------------
        If `remove_empty_lines` is `True`, empty lines will be removed in the process."""
        code_lines = String.get_lines(code, remove_empty_lines=True)
        lines = code_lines if remove_empty_lines else String.get_lines(code)
        tab_spaces = Code.get_tab_spaces(code)
        if (tab_spaces == new_tab_size) or tab_spaces == 0:
            if remove_empty_lines:
                return "\n".join(code_lines)
            return code
        result = []
        for line in lines:
            stripped = line.lstrip()
            indent_level = (len(line) - len(stripped)) // tab_spaces
            new_indent = " " * (indent_level * new_tab_size)
            result.append(new_indent + stripped)
        return "\n".join(result)

    @staticmethod
    def get_func_calls(code: str) -> list:
        """Will try to get all function calls and return them as a list."""
        funcs = _rx.findall(r"(?i)" + Regex.func_call(), code)
        nested_func_calls = []
        for _, func_attrs in funcs:
            nested_calls = _rx.findall(r"(?i)" + Regex.func_call(), func_attrs)
            if nested_calls:
                nested_func_calls.extend(nested_calls)
        return list(Data.remove_duplicates(funcs + nested_func_calls))

    @staticmethod
    def is_js(code: str, funcs: list[str] = ["__", "$t", "$lang"]) -> bool:
        """Will check if the code is very likely to be JavaScript."""
        if not code or len(code.strip()) < 3:
            return False
        for func in funcs:
            if _rx.match(r"^[\s\n]*" + _rx.escape(func) + r"\([^\)]*\)[\s\n]*$", code):
                return True
        direct_js_patterns = [
            r"^[\s\n]*\$\(['\"][^'\"]+['\"]\)\.[\w]+\([^\)]*\);?[\s\n]*$",  # jQuery calls
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
        funcs_pattern = r"(" + "|".join(_rx.escape(f) for f in funcs) + r")" + Regex.brackets("()")
        js_indicators = [(r"\b(var|let|const)\s+[\w_$]+", 2),  # JS variable declarations
                         (r"\$[\w_$]+\s*=", 2),  # jQuery-style variables
                         (r"\$[\w_$]+\s*\(", 2),  # jQuery function calls
                         (r"\bfunction\s*[\w_$]*\s*\(", 2),  # Function declarations
                         (r"[\w_$]+\s*=\s*function\s*\(", 2),  # Function assignments
                         (r"\b[\w_$]+\s*=>\s*[\{\(]", 2),  # Arrow functions
                         (r"\(function\s*\(\)\s*\{", 2),  # IIFE pattern
                         (funcs_pattern, 2),  # Custom predefined functions
                         (r"\b(true|false|null|undefined)\b", 1),  # JS literals
                         (r"===|!==|\+\+|--|\|\||&&", 1.5),  # JS-specific operators
                         (r"\bnew\s+[\w_$]+\s*\(", 1.5),  # Object instantiation with new
                         (r"\b(document|window|console|Math|Array|Object|String|Number)\.", 2),  # JS objects
                         (r"\basync\s+function|\bawait\b", 2),  # Async/await
                         (r"\b(if|for|while|switch)\s*\([^)]*\)\s*\{", 1),  # Control structures with braces
                         (r"\btry\s*\{[^}]*\}\s*catch\s*\(", 1.5),  # Try-catch
                         (r";[\s\n]*$", 0.5),  # Semicolon line endings
                         ]
        js_score = 0
        line_endings = [line.strip() for line in code.splitlines() if line.strip()]
        semicolon_endings = sum(1 for line in line_endings if line.endswith(';'))
        if semicolon_endings >= 1:
            js_score += min(semicolon_endings, 2)
        opening_braces = code.count('{')
        closing_braces = code.count('}')
        if opening_braces > 0 and opening_braces == closing_braces:
            js_score += 1
        for pattern, score in js_indicators:
            regex = _rx.compile(pattern, _rx.IGNORECASE)
            matches = regex.findall(code)
            if matches:
                js_score += len(matches) * score
        return js_score >= 2
