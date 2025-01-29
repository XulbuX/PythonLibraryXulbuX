import re as _re


class String:

    @staticmethod
    def to_type(string: str) -> any:
        """Will convert a string to the found type."""
        string = string.strip()  # Clean up whitespace
        # BOOLEAN
        if _re.match(r"(?i)^(true|false)$", string):
            return string.lower() == "true"
        # NONE
        elif _re.match(r"(?i)^(none|null|undefined)$", string):
            return None
        # INTEGER
        elif _re.match(r"^-?\d+$", string):
            return int(string)
        # FLOAT
        elif _re.match(r"^-?\d+\.\d+$", string):
            return float(string)
        # COMPLEX
        elif _re.match(r"^(-?\d+(\.\d+)?[+-]\d+(\.\d+)?j)$", string):
            return complex(string)
        # QUOTED STRING
        elif _re.match(r'^["\'](.*)["\']$', string):
            return string[1:-1]
        # BYTES
        elif _re.match(r"^b['\"](.*)['\"]$", string):
            return bytes(string[2:-1], "utf-8")
        # LIST
        elif _re.match(r"^\[(.*)\]$", string):
            return [
                String.to_type(item.strip()) for item in _re.findall(r"(?:[^,\[\]]+|\[.*?\]|\(.*?\)|\{.*?\})+", string[1:-1])
            ]
        # TUPLE
        elif _re.match(r"^\((.*)\)$", string):
            return tuple(
                String.to_type(item.strip()) for item in _re.findall(r"(?:[^,\(\)]+|\[.*?\]|\(.*?\)|\{.*?\})+", string[1:-1])
            )
        # DICTIONARY
        elif _re.match(r"^\{(.*)\}$", string) and ":" in string:
            return {
                String.to_type(k.strip()): String.to_type(v.strip())
                for k, v in _re.findall(
                    r"((?:[^:,{}]+|\[.*?\]|\(.*?\)|\{.*?\})+)\s*:\s*((?:[^:,{}]+|\[.*?\]|\(.*?\)|\{.*?\})+)", string[1:-1]
                )
            }
        # SET
        elif _re.match(r"^\{(.*?)\}$", string):
            return {
                String.to_type(item.strip()) for item in _re.findall(r"(?:[^,{}]+|\[.*?\]|\(.*?\)|\{.*?\})+", string[1:-1])
            }
        # RETURN AS IS (str)
        return string

    @staticmethod
    def normalize_spaces(string: str, tab_spaces: int = 4) -> str:
        """Replaces all special space characters with normal spaces.
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
        """Escapes Python's special characters (e.g. `\n`, `\t`, ...) and quotes inside the string.\n
        ----------------------------------------------------------------------------------------------
        `str_quotes` can be either `"` or `'` and should match the quotes, the string will be put
        inside of. So if your string will be `"string"`, you should pass `"` to the parameter
        `str_quotes`. That way, if the string includes the same quotes, they will be escaped."""
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
        """Returns `True` if the string is empty and `False` otherwise.\n
        -------------------------------------------------------------------------------------------
        If `spaces_are_empty` is true, it will also return `True` if the string is only spaces."""
        return (string in (None, "")) or (spaces_are_empty and isinstance(string, str) and not string.strip())

    @staticmethod
    def single_char_repeats(string: str, char: str) -> int | bool:
        """- If the string consists of only the same `char`, it returns the number of times it is present.
        - If the string doesn't consist of only the same character, it returns `False`."""
        if len(string) == len(char) * string.count(char):
            return string.count(char)
        else:
            return False

    @staticmethod
    def decompose(case_string: str, seps: str = "-_", lower_all: bool = True) -> list[str]:
        """Will decompose the string (any type of casing, also mixed) into parts."""
        return [
            (part.lower() if lower_all else part)
            for part in _re.split(rf"(?<=[a-z])(?=[A-Z])|[{_re.escape(seps)}]", case_string)
        ]

    @staticmethod
    def to_camel_case(string: str, upper: bool = True) -> str:
        """Will convert the string of any type of casing to `UpperCamelCase` or `lowerCamelCase` if `upper` is false."""
        parts = String.decompose(string)
        return ("" if upper else parts[0].lower()) + "".join(part.capitalize() for part in (parts if upper else parts[1:]))

    @staticmethod
    def to_delimited_case(string: str, delimiter: str = "_", screaming: bool = False) -> str:
        """Will convert the string of any type of casing to casing delimited by `delimiter`."""
        return delimiter.join(part.upper() if screaming else part for part in String.decompose(string))

    @staticmethod
    def get_lines(string: str, remove_empty_lines: bool = False) -> list[str]:
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
        --------------------------------------------------------------------------------------------
        - If `max_consecutive` is `0`, it will remove all consecutive empty lines.
        - If `max_consecutive` is bigger than `0`, it will only allow `max_consecutive` consecutive
        empty lines and everything above it will be cut down to `max_consecutive` empty lines."""
        return _re.sub(r"(\n\s*){2,}", r"\1" * (max_consecutive + 1), string)

    @staticmethod
    def split_count(string: str, count: int) -> list[str]:
        """Will split the string every `count` characters."""
        return [string[i : i + count] for i in range(0, len(string), count)]
