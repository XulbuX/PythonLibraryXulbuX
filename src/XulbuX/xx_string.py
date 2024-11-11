import re as _re




class String:

    @staticmethod
    def to_type(value:str) -> any:
        """Will convert a string to a type."""
        if value.lower() in ['true', 'false']:  # BOOLEAN
            return value.lower() == 'true'
        elif value.lower() in ['none', 'null', 'undefined']:  # NONE
            return None
        elif value.startswith('[') and value.endswith(']'):  # LIST
            return [String.to_type(item.strip()) for item in value[1:-1].split(',') if item.strip()]
        elif value.startswith('(') and value.endswith(')'):  # TUPLE
            return tuple(String.to_type(item.strip()) for item in value[1:-1].split(',') if item.strip())
        elif value.startswith('{') and value.endswith('}'):  # SET
            return {String.to_type(item.strip()) for item in value[1:-1].split(',') if item.strip()}
        elif value.startswith('{') and value.endswith('}') and ':' in value:  # DICTIONARY
            return {String.to_type(k.strip()): String.to_type(v.strip()) for k, v in [item.split(':') for item in value[1:-1].split(',') if item.strip()]}
        try:  # NUMBER (INT OR FLOAT)
            if '.' in value or 'e' in value.lower():
                return float(value)
            else:
                return int(value)
        except ValueError: pass
        if value.startswith(("'", '"')) and value.endswith(("'", '"')):  # STRING (WITH OR WITHOUT QUOTES)
            return value[1:-1]
        try:  # COMPLEX
            return complex(value)
        except ValueError: pass
        return value  # IF NOTHING ELSE MATCHES, RETURN AS IS

    @staticmethod
    def get_repeated_symbol(string:str, symbol:str) -> int|bool:
        """If the string consists of one repeating `symbol`, it returns the number of times it is repeated.<br>
        If the string doesn't consist of one repeating symbol, it returns `False`."""
        if len(string) == len(symbol) * string.count(symbol):
            return string.count(symbol)
        else:
            return False

    @staticmethod
    def decompose(case_string:str, seps:str = '-_', lower_all:bool = True) -> list[str]:
        """Will decompose the string (*any type of casing, also mixed*) into parts."""
        return [(part.lower() if lower_all else part) for part in _re.split(rf'(?<=[a-z])(?=[A-Z])|[{seps}]', case_string)]

    @staticmethod
    def to_camel_case(string:str) -> str:
        """Will convert the string of any type of casing to camel case."""
        return ''.join(part.capitalize() for part in String.decompose(string))

    @staticmethod
    def to_snake_case(string:str, sep:str = '_', screaming:bool = False) -> str:
        """Will convert the string of any type of casing to snake case."""
        return sep.join(part.upper() if screaming else part for part in String.decompose(string))

    @staticmethod
    def get_string_lines(string:str, remove_empty_lines:bool = False) -> list[str]:
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
    def remove_consecutive_empty_lines(string:str, max_consecutive:int = 0) -> str:
        """Will remove consecutive empty lines from the string.\n
        ----------------------------------------------------------------------------------------------
        If `max_consecutive` is `0`, it will remove all consecutive empty lines.<br>
        If `max_consecutive` is bigger than `0`, it will only allow `max_consecutive` consecutive<br>
        empty lines and everything above it will be cut down to `max_consecutive` empty lines."""
        return _re.sub(r'(\n\s*){2,}', r'\1' * (max_consecutive + 1), string)

    @staticmethod
    def split_every_chars(string:str, split:int) -> list[str]:
        """Will split the string every `split` characters."""
        return [string[i:i + split] for i in range(0, len(string), split)]

    @staticmethod
    def multi_strip(string:str, strip_chars:str = ' _-') -> str:
        """Will remove all leading and trailing `strip_chars` from the string."""
        for char in string:
            if char in strip_chars:
                string = string[1:]
            else: break
        for char in string[::-1]:
            if char in strip_chars:
                string = string[:-1]
            else: break
        return string

    @staticmethod
    def multi_lstrip(string:str, strip_chars:str = ' _-') -> str:
        """Will remove all leading `strip_chars` from the string."""
        for char in string:
            if char in strip_chars:
                string = string[1:]
            else: break
        return string

    @staticmethod
    def multi_rstrip(string:str, strip_chars:str = ' _-') -> str:
        """Will remove all trailing `strip_chars` from the string."""
        for char in string[::-1]:
            if char in strip_chars:
                string = string[:-1]
            else: break
        return string
