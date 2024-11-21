import re as _re


class String:

    @staticmethod
    def to_type(string: str) -> any:
        """Will convert a string to a type."""
        if string.lower() in ("true", "false"):  # BOOLEAN
            return string.lower() == "true"
        elif string.lower() in ("none", "null", "undefined"):  # NONE
            return None
        elif string.startswith("[") and string.endswith("]"):  # LIST
            return [String.to_type(item.strip()) for item in string[1:-1].split(",") if item.strip()]
        elif string.startswith("(") and string.endswith(")"):  # TUPLE
            return tuple(String.to_type(item.strip()) for item in string[1:-1].split(",") if item.strip())
        elif string.startswith("{") and string.endswith("}"):  # SET
            return {String.to_type(item.strip()) for item in string[1:-1].split(",") if item.strip()}
        elif string.startswith("{") and string.endswith("}") and ":" in string:  # DICTIONARY
            return {
                String.to_type(k.strip()): String.to_type(v.strip())
                for k, v in (item.split(":") for item in string[1:-1].split(",") if item.strip())
            }
        try:  # NUMBER (INT OR FLOAT)
            if "." in string or "e" in string.lower():
                return float(string)
            else:
                return int(string)
        except ValueError:
            pass
        if string.startswith(("'", '"')) and string.endswith(("'", '"')):  # STRING (WITH OR WITHOUT QUOTES)
            return string[1:-1]
        try:  # COMPLEX
            return complex(string)
        except ValueError:
            pass
        return string  # IF NOTHING ELSE MATCHES, RETURN AS IS

    @staticmethod
    def normalize_spaces(string: str, tab_spaces: int = 4) -> str:
        """Replaces all special space characters with normal spaces.<br>
        Also replaces tab characters with `tab_spaces` spaces."""
        return (
            string.replace("\t", " " * tab_spaces)
            .replace("\u2000", " ")
            .replace("\u2001", " ")
            .replace("\u2002", " ")
            .replace("\u2003", " ")
            .replace("\u2004", " ")
            .replace("\u2005", " ")
            .replace("\u2006", " ")
            .replace("\u2007", " ")
            .replace("\u2008", " ")
            .replace("\u2009", " ")
            .replace("\u200A", " ")
        )

    @staticmethod
    def escape(string: str, str_quotes: str = '"') -> str:
        """Escapes the special characters and quotes inside a string.\n
        ----------------------------------------------------------------------------
        `str_quotes` can be either `"` or `'` and should match the quotes,<br>
        the string will be put inside of. So if your string will be `"string"`,<br>
        you should pass `"` to the parameter `str_quotes`.<br>
        That way, if the string includes the same quotes, they will be escaped."""
        string = (
            string.replace("\\", r"\\")
            .replace("\n", r"\n")
            .replace("\r", r"\r")
            .replace("\t", r"\t")
            .replace("\b", r"\b")
            .replace("\f", r"\f")
            .replace("\a", r"\a")
        )
        if str_quotes == '"':
            string = string.replace(r"\\'", "'").replace(r'"', r"\"")
        elif str_quotes == "'":
            string = string.replace(r'\\"', '"').replace(r"'", r"\'")
        return string

    @staticmethod
    def is_empty(string: str, spaces_are_empty: bool = False):
        """Returns `True` if the string is empty and `False` otherwise.<br>
        If `spaces_are_empty` is true, it will also return `True` if the string is only spaces."""
        return (string in (None, "")) or (spaces_are_empty and isinstance(string, str) and not string.strip())

    @staticmethod
    def single_char_repeats(string: str, char: str) -> int | bool:
        """If the string consists of only the same `char`, it returns the number of times it is present.<br>
        If the string doesn't consist of only the same character, it returns `False`.
        """
        if len(string) == len(char) * string.count(char):
            return string.count(char)
        else:
            return False

    @staticmethod
    def decompose(case_string: str, seps: str = "-_", lower_all: bool = True) -> list[str]:
        """Will decompose the string (*any type of casing, also mixed*) into parts."""
        return [(part.lower() if lower_all else part) for part in _re.split(rf"(?<=[a-z])(?=[A-Z])|[{seps}]", case_string)]

    @staticmethod
    def to_camel_case(string: str) -> str:
        """Will convert the string of any type of casing to camel case."""
        return "".join(part.capitalize() for part in String.decompose(string))

    @staticmethod
    def to_snake_case(string: str, sep: str = "_", screaming: bool = False) -> str:
        """Will convert the string of any type of casing to snake case."""
        return sep.join(part.upper() if screaming else part for part in String.decompose(string))

    @staticmethod
    def get_string_lines(string: str, remove_empty_lines: bool = False) -> list[str]:
        """Will split the string into lines."""
        if not remove_empty_lines:
            return string.splitlines()
        lines = string.splitlines()
        if not lines:
            return []
        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return []
        return non_empty_lines

    @staticmethod
    def remove_consecutive_empty_lines(string: str, max_consecutive: int = 0) -> str:
        """Will remove consecutive empty lines from the string.\n
        ----------------------------------------------------------------------------------------------
        If `max_consecutive` is `0`, it will remove all consecutive empty lines.<br>
        If `max_consecutive` is bigger than `0`, it will only allow `max_consecutive` consecutive<br>
        empty lines and everything above it will be cut down to `max_consecutive` empty lines.
        """
        return _re.sub(r"(\n\s*){2,}", r"\1" * (max_consecutive + 1), string)

    @staticmethod
    def split_count(string: str, count: int) -> list[str]:
        """Will split the string every `count` characters."""
        return [string[i : i + count] for i in range(0, len(string), count)]

    @staticmethod
    def multi_strip(string: str, strip_chars: str = " _-") -> str:
        """Will remove all leading and trailing `strip_chars` from the string."""
        for char in string:
            if char in strip_chars:
                string = string[1:]
            else:
                break
        for char in string[::-1]:
            if char in strip_chars:
                string = string[:-1]
            else:
                break
        return string

    @staticmethod
    def multi_lstrip(string: str, strip_chars: str = " _-") -> str:
        """Will remove all leading `strip_chars` from the string."""
        for char in string:
            if char in strip_chars:
                string = string[1:]
            else:
                break
        return string

    @staticmethod
    def multi_rstrip(string: str, strip_chars: str = " _-") -> str:
        """Will remove all trailing `strip_chars` from the string."""
        for char in string[::-1]:
            if char in strip_chars:
                string = string[:-1]
            else:
                break
        return string
