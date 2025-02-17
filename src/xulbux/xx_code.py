from .xx_string import String
from .xx_regex import Regex
from .xx_data import Data

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
        return Data.remove_duplicates(funcs + nested_func_calls)

    @staticmethod
    def is_js(code: str, funcs: list = ["__", "$t", "$lang"]) -> bool:
        """Will check if the code is very likely to be JavaScript."""
        funcs = "|".join(funcs)
        js_pattern = _rx.compile(
            Regex.outside_strings(
                r"""^(?:
                (\$[\w_]+)\s*                      # JQUERY-STYLE VARIABLES
                |(\$[\w_]+\s*\()                   # JQUERY-STYLE FUNCTION CALLS
                |((""" + funcs + r")" + Regex.brackets("()") + r"""\s*) # PREDEFINED FUNCTION CALLS
                |(\bfunction\s*\()                 # FUNCTION DECLARATIONS
                |(\b(var|let|const)\s+[\w_]+\s*=)  # VARIABLE DECLARATIONS
                |(\b(if|for|while|switch)\s*\()    # CONTROL STRUCTURES
                |(\b(return|throw)\s+)             # RETURN OR THROW STATEMENTS
                |(\bnew\s+[\w_]+\()                # OBJECT INSTANTIATION
                |(\b[\w_]+\s*=>\s*{)               # ARROW FUNCTIONS
                |(\b(true|false|null|undefined)\b) # JAVASCRIPT LITERALS
                |(\b(document|window|console)\.)   # BROWSER OBJECTS
                |(\b[\w_]+\.(forEach|map|filter|reduce)\() # ARRAY METHODS
                |(/[^/\n\r]*?/[gimsuy]*)           # REGULAR EXPRESSIONS
                |(===|!==|\+\+|--|\|\||&&)         # JAVASCRIPT-SPECIFIC OPERATORS
                |(\bclass\s+[\w_]+)                # CLASS DECLARATIONS
                |(\bimport\s+.*?from\s+)           # IMPORT STATEMENTS
                |(\bexport\s+(default\s+)?)        # EXPORT STATEMENTS
                |(\basync\s+function)              # ASYNC FUNCTIONS
                |(\bawait\s+)                      # AWAIT KEYWORD
                |(\btry\s*{)                       # TRY-CATCH BLOCKS
                |(\bcatch\s*\()
                |(\bfinally\s*{)
                |(\byield\s+)                      # GENERATOR FUNCTIONS
                |(\[.*?\]\s*=)                     # DESTRUCTURING ASSIGNMENT
                |(\.\.\.)                          # SPREAD OPERATOR
                |(==|!=|>=|<=|>|<)                 # COMPARISON OPERATORS
                |(\+=|-=|\*=|/=|%=|\*\*=)          # COMPOUND ASSIGNMENT OPERATORS
                |(\+|-|\*|/|%|\*\*)                # ARITHMETIC OPERATORS
                |(&|\||\^|~|<<|>>|>>>)             # BITWISE OPERATORS
                |(\?|:)                            # TERNARY OPERATOR
                |(\bin\b)                          # IN OPERATOR
                |(\binstanceof\b)                  # INSTANCEOF OPERATOR
                |(\bdelete\b)                      # DELETE OPERATOR
                |(\btypeof\b)                      # TYPEOF OPERATOR
                |(\bvoid\b)                        # VOID OPERATOR
                )[\s\S]*$"""
            ), _rx.VERBOSE | _rx.IGNORECASE
        )
        return bool(js_pattern.fullmatch(code))
