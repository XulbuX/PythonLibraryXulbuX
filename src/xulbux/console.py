"""
This module provides the `Console`, `ProgressBar`, and `Throbber` classes
which offer methods for logging and other actions within the terminal.
"""

from .base.types import ProgressUpdater, AllTextChars, ArgParseConfigs, ArgParseConfig, ArgData, Rgba, Hexa
from .base.decorators import mypyc_attr
from .base.consts import CHARS, ANSI

from .format_codes import _PATTERNS as _FC_PATTERNS, FormatCodes
from .string import String
from .color import Color
from .regex import LazyRegex

from typing import ValuesView, Generator, Callable, KeysView, Optional, Literal, TypeVar, TextIO, Any, overload, cast
from prompt_toolkit.key_binding import KeyPressEvent, KeyBindings
from prompt_toolkit.validation import ValidationError, Validator
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style
from prompt_toolkit.keys import Keys
from contextlib import contextmanager
from itertools import chain
from io import StringIO
import prompt_toolkit as _pt
import subprocess as _subprocess
import threading as _threading
import getpass as _getpass
import ctypes as _ctypes
import shutil as _shutil
import regex as _rx
import time as _time
import sys as _sys
import os as _os


T = TypeVar("T")

_PATTERNS = LazyRegex(
    hr=r"(?i){hr}",
    hr_no_nl=r"(?i)(?<!\n){hr}(?!\n)",
    hr_r_nl=r"(?i)(?<!\n){hr}(?=\n)",
    hr_l_nl=r"(?i)(?<=\n){hr}(?!\n)",
    label=r"(?i){(?:label|l)}",
    bar=r"(?i){(?:bar|b)}",
    current=r"(?i){(?:current|c)(?::(.))?}",
    total=r"(?i){(?:total|t)(?::(.))?}",
    percentage=r"(?i){(?:percentage|percent|p)(?::\.([0-9])+f)?}",
    animation=r"(?i){(?:animation|a)}",
)


class ParsedArgData:
    """Represents the result of a parsed command-line argument, containing the attributes listed below.\n
    ------------------------------------------------------------------------------------------------------------
    *   `exists` – Whether the argument was found in the command-line arguments or not.
    *   `is_pos` – Whether the argument is a positional `"before"`/`"after"` argument or not.
    *   `values` – The list of values associated with the argument.
    *   `flag` – The specific flag that was found (e.g. `-v`, `-vv`, `-vvv`), or `None` for positional args.
    ------------------------------------------------------------------------------------------------------------
    When the `ParsedArgData` instance is accessed as a boolean it will correspond to the `exists` attribute."""

    def __init__(self, *, exists: bool, values: list[str], is_pos: bool, flag: Optional[str] = None):
        self.exists: bool = exists
        """Whether the argument was found or not."""
        self.is_pos: bool = is_pos
        """Whether the argument is a positional argument or not."""
        self.values: list[str] = values
        """The list of values associated with the argument."""
        self.flag: Optional[str] = flag
        """The specific flag that was found (e.g. `-v`, `-vv`, `-vvv`), or `None` for positional args."""

    def __bool__(self) -> bool:
        """Whether the argument was found or not (i.e. the `exists` attribute)."""

        return self.exists

    def __eq__(self, other: object, /) -> bool:
        """Check if two `ParsedArgData` objects are equal by comparing their attributes."""

        if not isinstance(other, ParsedArgData):
            return False
        return (
            self.exists == other.exists \
            and self.is_pos == other.is_pos
            and self.values == other.values
            and self.flag == other.flag
        )

    def __ne__(self, other: object, /) -> bool:
        """Check if two `ParsedArgData` objects are not equal by comparing their attributes."""

        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"ParsedArgData(\n  exists = {self.exists!r},\n  is_pos = {self.is_pos!r},\n  values = {self.values!r},\n  flag = {self.flag!r}\n)"

    def __str__(self) -> str:
        return self.__repr__()

    def dict(self) -> ArgData:
        """Returns the argument result as a dictionary."""

        return ArgData(exists=self.exists, is_pos=self.is_pos, values=self.values, flag=self.flag)

    @overload
    def get(self, index: int, /) -> Optional[str]:
        ...

    @overload
    def get(self, index: int, /, default: None) -> Optional[str]:
        ...

    @overload
    def get(self, index: int, /, default: str) -> str:
        ...

    def get(self, index: int, /, default: Optional[str] = None) -> Optional[str]:
        """Safely access a value from the `values` list by index.\n
        -------------------------------------------------------------------
        *   `index` – The index of the value to access.
        *   `default` – The fallback value if the index is out of range.
        -------------------------------------------------------------------
        Returns the value at `index` if it exists, otherwise `default`."""

        if 0 <= index < len(self.values):
            return self.values[index]
        return default


@mypyc_attr(native_class=False)
class ParsedArgs:
    """Container for parsed command-line arguments, allowing attribute-style access.\n
    -------------------------------------------------------------------------------------
    *   `**parsed_args` – A mapping of argument aliases to their corresponding data<br>
        saved in an `ParsedArgData` object.
    -------------------------------------------------------------------------------------
    For example, if an argument `foo` was parsed, it can be accessed via `args.foo`.<br>
    Each such attribute (e.g. `args.foo`) is an instance of `ParsedArgData`."""

    RESERVED_ALIASES: frozenset[str] = frozenset({
        "all_exist", "any_exist", "dict", "existing", "get", "is_empty", "items", "keys", "missing", "values"
    })
    """Alias names that are reserved and cannot be used as argument aliases."""

    def __init__(self, **parsed_args: ParsedArgData):
        for alias_name, parsed_arg_data in parsed_args.items():
            setattr(self, alias_name, parsed_arg_data)

    def __len__(self):
        """The number of arguments stored in the `ParsedArgs` object."""

        return len(vars(self))

    def __contains__(self, key: str, /) -> bool:
        """Checks if an argument with the given alias exists in the `ParsedArgs` object."""

        return key in vars(self)

    def __bool__(self) -> bool:
        """Whether the `ParsedArgs` object contains any arguments."""

        return len(self) > 0

    def __getattr__(self, name: str, /) -> ParsedArgData:
        raise AttributeError(f"'{type(self).__name__}' object has no attribute {name}")

    def __getitem__(self, key: str | int, /) -> ParsedArgData:
        if isinstance(key, int):
            return list(self.values())[key]
        return getattr(self, key)

    def __iter__(self) -> Generator[tuple[str, ParsedArgData], None, None]:
        for key, val in cast(dict[str, ParsedArgData], vars(self)).items():
            yield (key, val)

    def __eq__(self, other: object, /) -> bool:
        """Check if two `ParsedArgs` objects are equal by comparing their stored arguments."""

        if not isinstance(other, ParsedArgs):
            return False
        return vars(self) == vars(other)

    def __ne__(self, other: object, /) -> bool:
        """Check if two `ParsedArgs` objects are not equal by comparing their stored arguments."""

        return not self.__eq__(other)

    def __repr__(self) -> str:
        if not self:
            return "ParsedArgs()"
        return "ParsedArgs(\n  " + ",\n  ".join(
            f"{key} = " + "\n  ".join(repr(val).splitlines()) \
            for key, val in self.__iter__()
        ) + "\n)"

    def __str__(self) -> str:
        return self.__repr__()

    def dict(self) -> dict[str, ArgData]:
        """Returns the arguments as a dictionary."""

        return {key: val.dict() for key, val in self.__iter__()}

    def get(self, key: str, /, default: Any = None) -> ParsedArgData | Any:
        """Returns the argument result for the given alias, or `default` if not found."""

        return getattr(self, key, default)

    def keys(self) -> KeysView[str]:
        """Returns the argument aliases as `dict_keys([…])`."""

        return vars(self).keys()

    def values(self) -> ValuesView[ParsedArgData]:
        """Returns the argument results as `dict_values([…])`."""

        return vars(self).values()

    def items(self) -> Generator[tuple[str, ParsedArgData], None, None]:
        """Yields tuples of `(alias, ParsedArgData)`."""

        for key, val in self.__iter__():
            yield (key, val)

    def existing(self) -> Generator[tuple[str, ParsedArgData], None, None]:
        """Yields tuples of `(alias, ParsedArgData)` for existing arguments only."""

        for key, val in self.__iter__():
            if val.exists:
                yield (key, val)

    def missing(self) -> Generator[tuple[str, ParsedArgData], None, None]:
        """Yields tuples of `(alias, ParsedArgData)` for missing arguments only."""

        for key, val in self.__iter__():
            if not val.exists:
                yield (key, val)

    @property
    def is_empty(self) -> bool:
        """Whether no argument was found and none have any values (not even defaults)."""

        return all(not val.exists and not val.values for val in cast(dict[str, ParsedArgData], vars(self)).values())

    @property
    def any_exist(self) -> bool:
        """Whether at least one argument was explicitly found."""

        return any(val.exists for val in cast(dict[str, ParsedArgData], vars(self)).values())

    @property
    def all_exist(self) -> bool:
        """Whether all arguments were explicitly found."""

        return all(val.exists for val in cast(dict[str, ParsedArgData], vars(self)).values())


@mypyc_attr(native_class=False)
class _ConsoleMeta(type):

    @property
    def width(cls) -> int:
        """The terminal width in characters."""

        try:
            return _os.get_terminal_size().columns
        except OSError:
            return 80

    @property
    def height(cls) -> int:
        """The terminal height in lines."""

        try:
            return _os.get_terminal_size().lines
        except OSError:
            return 24

    @property
    def size(cls) -> tuple[int, int]:
        """A tuple with the terminal width and height in characters and lines."""

        try:
            size = _os.get_terminal_size()
            return (size.columns, size.lines)
        except OSError:
            return (80, 24)

    @property
    def user(cls) -> str:
        """The name of the current user."""

        return _os.getenv("USER") or _os.getenv("USERNAME") or _getpass.getuser()

    @property
    def is_tty(cls) -> bool:
        """Whether the terminal is connected to a TTY or not."""

        return _sys.stdout.isatty()

    @property
    def encoding(cls) -> str:
        """The encoding used by the terminal (e.g. `utf-8`, `cp1252`, …)."""

        try:
            encoding = _sys.stdout.encoding
            return encoding if encoding is not None else "utf-8"
        except (AttributeError, Exception):
            return "utf-8"

    @property
    def supports_color(cls) -> bool:
        """Whether the terminal supports ANSI color codes or not."""

        if not cls.is_tty:
            return False

        if _os.name == "nt":
            # CHECK IF VT100 MODE IS ENABLED ON WINDOWS
            try:
                kernel32 = getattr(_ctypes, "windll").kernel32
                handle = kernel32.GetStdHandle(-11)
                mode = _ctypes.c_ulong()
                if kernel32.GetConsoleMode(handle, _ctypes.byref(mode)):
                    return (mode.value & 0x0004) != 0
            except Exception:
                pass

            return False

        return _os.getenv("TERM", "").lower() not in {"", "dumb"}


class Console(metaclass=_ConsoleMeta):
    """This class provides methods for logging and other actions within the terminal."""

    @classmethod
    def get_args(
        cls,
        arg_parse_configs: ArgParseConfigs,
        /,
        *,
        skip: int = 0,
        flag_value_sep: Optional[str] = "=",
        allow_space_value: bool = True,
    ) -> ParsedArgs:
        """Will search for the specified args in the command-line arguments
        and return the results as a special `ParsedArgs` object.\n
        ---------------------------------------------------------------------------------------------------------
        *   `arg_parse_configs` – A dictionary where each key is an alias name for the argument<br>
            and the key's value is the parsing configuration for that argument.
        *   `skip` – The number of leading command-line arguments to skip before parsing;<br>
            useful when the first N args are a command/subcommand and not relevant to the caller.
        *   `flag_value_sep` – The character/s used to separate flags from their values;<br>
            pass `None` to disable separator-based syntax (e.g. `--flag=value`) entirely.
        *   `allow_space_value` – Whether to allow space-separated flag values (e.g. `--flag value`)<br>
            in addition to the separator-based syntax; enabled by default.
        ---------------------------------------------------------------------------------------------------------
        The `arg_parse_configs` dictionary can have the following structures for each item:
        1.  Simple set of flags (when no default value is needed):
            ```python
            "alias_name": {"-f", "--flag"}
            ```
        2.  Dictionary with the`"flags"` set, plus a specified `"default"` value:
            ```python
            "alias_name": {
                "flags": {"-f", "--flag"},
                "default": "some_value",
            }
            ```
        3.  Positional value collection using the literals `"before"` or `"after"`:
            ```python
            # COLLECT ALL NON-FLAGGED VALUES THAT APPEAR BEFORE THE FIRST FLAG
            "alias_name": "before"
            # COLLECT ALL NON-FLAGGED VALUES THAT APPEAR AFTER THE LAST FLAG'S VALUE
            "alias_name": "after"
            ```
        #### Example usage:
        If you call the `get_args()` method in your script like this:
        ```python
        parsed_args = Console.get_args({
            "text_before": "before",   # POSITIONAL VALUES BEFORE FIRST FLAG
            "arg1": {"-A", "--arg1"},  # NORMAL FLAGS
            "arg2": {                  # FLAGS WITH SPECIFIED DEFAULT VALUE
                "flags": {"-B", "--arg2"},
                "default": "default value"
            },
            "text_after": "after",     # POSITIONAL VALUES AFTER LAST FLAG'S VALUE
        })
        ```
        … and execute the script via the command line like this:\n
        `$ python script.py "Hello" "World" --arg1=42 "Goodbye"`\n
        … the `get_args()` method would return a `ParsedArgs` object with the following structure:
        ```python
        ParsedArgs(
            # FOUND 2 VALUES BEFORE THE FIRST FLAG
            text_before = ParsedArgData(exists=True, is_pos=True, values=["Hello", "World"], flag=None),
            # FOUND ONE OF THE SPECIFIED FLAGS WITH A VALUE
            arg1 = ParsedArgData(exists=True, is_pos=False, values=["42"], flag="--arg1"),
            # DIDN'T FIND ANY OF THE SPECIFIED FLAGS, USED THE DEFAULT VALUE
            arg2 = ParsedArgData(exists=False, is_pos=False, values=["default value"], flag=None),
            # FOUND 1 VALUE AFTER THE LAST FLAG'S VALUE
            text_after = ParsedArgData(exists=True, is_pos=True, values=["Goodbye"], flag=None),
        )
        ```
        ---------------------------------------------------------------------------------------------------------
        NOTE: When `allow_space_value` is `True`, a value that directly follows a flag (e.g. `--flag value`)<br>
        is consumed as that flag's value and is not available as a positional `"after"` argument."""

        if skip < 0:
            raise ValueError(f"The 'skip' parameter must be a non-negative integer, got {skip!r}")
        if flag_value_sep is not None and not flag_value_sep:
            raise ValueError(f"The 'flag_value_sep' parameter must be a non-empty string or None, got {flag_value_sep!r}")

        return _ConsoleArgsParseHelper(
            arg_parse_configs,
            skip=skip,
            flag_value_sep=flag_value_sep,
            allow_space_value=allow_space_value,
        )()

    @classmethod
    def pause_exit(
        cls,
        prompt: object = "",
        /,
        *,
        pause: bool = True,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = False,
    ) -> None:
        """Will print the `prompt` and then pause and/or exit the program based on the given options.\n
        -----------------------------------------------------------------------------------------------------
        *   `prompt` – The message to print before pausing/exiting.
        *   `pause` – Whether to pause and wait for a key press after printing the prompt.
        *   `exit` – Whether to exit the program after printing the prompt (and pausing if `pause` is true).
        *   `exit_code` – The exit code to use when exiting the program.
        *   `reset_ansi` – Whether to reset the ANSI formatting after printing the prompt."""

        FormatCodes.print(prompt, end="", flush=True)
        if reset_ansi:
            FormatCodes.print("[_]", end="")
        if pause:
            cls._read_single_key()
        if exit:
            _sys.exit(exit_code)

    @classmethod
    def cls(cls) -> None:
        """Will clear the terminal in addition to completely resetting the ANSI formats."""

        if _shutil.which("cls"):
            _subprocess.run(["cls"])
        elif _shutil.which("clear"):
            _subprocess.run(["clear"])
        print("\033[0m", end="", flush=True)

    @classmethod
    def log(
        cls,
        title: Optional[str] = None,
        prompt: object = "",
        /,
        *,
        start: str = "",
        end: str = "\n",
        title_bg_color: Optional[str | Rgba | Hexa] = None,
        default_color: Optional[Rgba | Hexa] = None,
        tab_size: int = 8,
        title_px: int = 1,
        title_mx: int = 2,
    ) -> None:
        """Prints a nicely formatted log message.\n
        ----------------------------------------------------------------------------------------------
        *   `title` – The title of the log message (e.g. `DEBUG`, `WARN`, `FAIL`, …).
        *   `prompt` – The log message.
        *   `format_linebreaks` – Whether to format (indent after) the line breaks or not.
        *   `start` – Something to print before the log is printed.
        *   `end` – Something to print after the log is printed (e.g. `\\n`).
        *   `title_bg_color` – The background color of the `title` (terminal color, RGBA, or HEXA).
        *   `default_color` – The default text color of the `prompt` (RGBA or HEXA).
        *   `tab_size` – The tab size used for the log (default is 8 – matches terminal tabs).
        *   `title_px` – The horizontal padding (in chars) to the title (if `title_bg_color` is set).
        *   `title_mx` – The horizontal margin (in chars) to the title.
        ----------------------------------------------------------------------------------------------
        The log message can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see `format_codes` module documentation."""

        if tab_size < 0:
            raise ValueError(f"The 'tab_size' parameter must be a non-negative integer, got {tab_size!r}")
        if title_px < 0:
            raise ValueError(f"The 'title_px' parameter must be a non-negative integer, got {title_px!r}")
        if title_mx < 0:
            raise ValueError(f"The 'title_mx' parameter must be a non-negative integer, got {title_mx!r}")

        title_fg: str = "_c"
        title = "" if title is None else title.strip().upper()

        if has_title_bg := title_bg_color is not None:
            if str(title_bg_color).replace(" ", "").lower() in ANSI.COLOR_VARIANTS_MAP:
                title_fg = "black"
            elif Color.is_valid_rgba(title_bg_color) or Color.is_valid_hexa(title_bg_color):
                title_bg_color = Color.to_hexa(title_bg_color)
                title_fg = str(Color.text_color_for_on_bg(title_bg_color))
            else:
                raise ValueError(
                    f"The 'title_bg_color' parameter must be a valid terminal color, RGBA value, or HEXA value, got {title_bg_color!r}"
                )
        else:
            title_px = 0  # REMOVE PADDING IF TITLE HAS NO BG COLOR

        # PADDING = SPACE INSIDE TITLE BG COLOR
        # MARGIN = SPACE OUTSIDE TITLE BG COLOR
        px, mx = " " * title_px, " " * title_mx

        # TITLE LENGTH INCLUDING PADDING AND MARGIN
        title_len: int = len(title) + (title_px * 2) + (title_mx * 2)

        # CALCULATE DISTANCE TO NEXT TAB STOP
        tab: str = " " * (-title_len % tab_size)

        # POSITION WHERE PROMPT NEEDS TO WRAP TO NEXT LINE
        wrap_len: int = cls.width - (title_len + len(tab))

        # REMOVE ALL FORMAT CODES AS THEY WON'T AFFECT THE VISIBLE LENGTH OF THE PROMPT
        clean_prompt, removals = (*FormatCodes.remove(str(prompt), get_removals=True, _ignore_linebreaks=True), )

        # SPLIT PROMPT INTO LINES AND THEN SPLIT EACH LINE INTO CHUNKS THAT FIT WITHIN THE WRAP LENGTH
        prompt_lst: list[str] = list(chain.from_iterable(cls._process_lines(clean_prompt, wrap_len)))

        # ADD BACK REMOVED FORMAT CODES TO THEIR ORIGINAL POSITIONS IN THE PROMPT
        prompt = f"\n{' ' * title_len}{tab}".join(cls._add_back_removed_parts(prompt_lst, removals))

        out: str = (
            # LOG WITHOUT A TITLE
            f"{start}{mx}{f'[{default_color}]' if default_color else ''}{prompt}[_]" if title == "" else
            # LOG WITH A TITLE
            f"{start}{mx}[b|{title_fg}{f'|bg:{title_bg_color}' if has_title_bg else ''}]{px}{title}{px}[_]{mx}"
            f"{tab}{f'[{default_color}]' if default_color else ''}{prompt}[_]"
        )

        FormatCodes.print(out, default_color=default_color, end=end)

    @classmethod
    def debug(
        cls,
        prompt: object = "Point in program reached.",
        /,
        *,
        active: bool = True,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `DEBUG` log message with the options to pause<br>
        at the message and exit the program after the message was printed.\n
        If `active` is false, no debug message will be printed."""

        if active:
            cls.log(
                "DEBUG",
                prompt,
                start=start,
                end=end,
                title_bg_color="br:yellow",
                default_color=default_color,
            )
            cls.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @classmethod
    def info(
        cls,
        prompt: object = "Program running.",
        /,
        *,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `INFO` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""

        cls.log(
            "INFO",
            prompt,
            start=start,
            end=end,
            title_bg_color="br:blue",
            default_color=default_color,
        )
        cls.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @classmethod
    def done(
        cls,
        prompt: object = "Program finished.",
        /,
        *,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `DONE` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""

        cls.log(
            "DONE",
            prompt,
            start=start,
            end=end,
            title_bg_color="br:green",
            default_color=default_color,
        )
        cls.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @classmethod
    def warn(
        cls,
        prompt: object = "Important message.",
        /,
        *,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 1,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `WARN` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""

        cls.log(
            "WARN",
            prompt,
            start=start,
            end=end,
            title_bg_color="br:yellow",
            default_color=default_color,
        )
        cls.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @classmethod
    def fail(
        cls,
        prompt: object = "Program error.",
        /,
        *,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = True,
        exit_code: int = 1,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `FAIL` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""

        cls.log(
            "FAIL",
            prompt,
            start=start,
            end=end,
            title_bg_color="br:red",
            default_color=default_color,
        )
        cls.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @classmethod
    def exit(
        cls,
        prompt: object = "Program ended.",
        /,
        *,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = True,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `EXIT` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""

        cls.log(
            "EXIT",
            prompt,
            start=start,
            end=end,
            title_bg_color="br:magenta",
            default_color=default_color,
        )
        cls.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @classmethod
    def log_box_filled(
        cls,
        *values: object,
        start: str = "",
        end: str = "\n",
        box_bg_color: Optional[str | Rgba | Hexa] = None,
        default_color: Optional[Rgba | Hexa] = None,
        w_padding: int = 2,
        w_full: bool = False,
        indent: int = 0,
    ) -> None:
        """Will print a box with a colored background, containing a formatted log message.\n
        --------------------------------------------------------------------------------------
        *   `*values` – The box content (each value is on a new line).
        *   `start` – Something to print before the log box is printed (e.g. `\\n`).
        *   `end` – Something to print after the log box is printed (e.g. `\\n`).
        *   `box_bg_color` – The background color of the box (terminal color, RGBA, or HEXA).
        *   `default_color` – The default text color of the `*values`.
        *   `w_padding` – The horizontal padding (in chars) to the box content.
        *   `w_full` – Whether to make the box be the full terminal width or not.
        *   `indent` – The indentation of the box (in chars).
        --------------------------------------------------------------------------------------
        The box content can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see `format_codes` module documentation."""

        if w_padding < 0:
            raise ValueError(f"The 'w_padding' parameter must be a non-negative integer, got {w_padding!r}")
        if indent < 0:
            raise ValueError(f"The 'indent' parameter must be a non-negative integer, got {indent!r}")

        if box_bg_color is not None:
            if str(box_bg_color).replace(" ", "").lower() in ANSI.COLOR_VARIANTS_MAP:
                pass
            elif Color.is_valid_rgba(box_bg_color) or Color.is_valid_hexa(box_bg_color):
                box_bg_color = Color.to_hexa(box_bg_color)
            else:
                raise ValueError(
                    f"The 'box_bg_color' parameter must be a valid terminal color, RGBA value, or HEXA value, got {box_bg_color!r}"
                )

        lines, unfmt_lines, max_line_len = cls._prepare_log_box(values, default_color)

        spaces_l = " " * indent
        pady = " " * (cls.width if w_full else max_line_len + (2 * w_padding))
        pad_w_full = (cls.width - (max_line_len + (2 * w_padding))) if w_full else 0

        default_color = default_color or "#000"
        bg_fc = f"_c|invert|bg:{default_color}" if box_bg_color is None else f"bg:{box_bg_color}"

        lines = [( \
            f"{spaces_l}[{bg_fc}]{' ' * w_padding}"
            + _FC_PATTERNS.formatting.sub(_ConsoleLogBoxBgReplacer(bg_fc), line)
            + (" " * ((w_padding + max_line_len - len(unfmt)) + pad_w_full))
            + "[*]"
        ) for line, unfmt in zip(lines, unfmt_lines)]

        FormatCodes.print(
            ( \
                f"{start}{spaces_l}[{bg_fc}]{pady}[*]\n"
                + "\n".join(lines)
                + ("\n" if lines else "")
                + f"{spaces_l}[{bg_fc}]{pady}[_]"
            ),
            default_color=default_color,
            sep="\n",
            end=end,
        )

    @classmethod
    def log_box_bordered(
        cls,
        *values: object,
        start: str = "",
        end: str = "\n",
        border_type: Literal["standard", "rounded", "strong", "double"] = "rounded",
        border_style: str | Rgba | Hexa = "br:black",
        default_color: Optional[Rgba | Hexa] = None,
        w_padding: int = 1,
        w_full: bool = False,
        indent: int = 0,
        _border_chars: Optional[tuple[str, str, str, str, str, str, str, str, str, str, str]] = None,
    ) -> None:
        """Will print a bordered box, containing a formatted log message.\n
        ---------------------------------------------------------------------------------------------
        *   `*values` – The box content (each value is on a new line).
        *   `start` – Something to print before the log box is printed (e.g. `\\n`).
        *   `end` – Something to print after the log box is printed (e.g. `\\n`).
        *   `border_type` – One of the predefined border character sets.
        *   `border_style` – The style of the border (special formatting codes).
        *   `default_color` – The default text color of the `*values`.
        *   `w_padding` – The horizontal padding (in chars) to the box content.
        *   `w_full` – Whether to make the box be the full terminal width or not.
        *   `indent` – The indentation of the box (in chars).
        *   `_border_chars` – Define your own border characters set (overwrites `border_type`).
        ---------------------------------------------------------------------------------------------
        You can insert horizontal rules to split the box content by using `{hr}` in the `*values`.\n
        ---------------------------------------------------------------------------------------------
        The box content can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see `format_codes` module documentation.\n
        ---------------------------------------------------------------------------------------------
        The `border_type` can be one of the following:
        *   `"standard" = ('┌', '─', '┐', '│', '┘', '─', '└', '│', '├', '─', '┤')`
        *   `"rounded" = ('╭', '─', '╮', '│', '╯', '─', '╰', '│', '├', '─', '┤')`
        *   `"strong" = ('┏', '━', '┓', '┃', '┛', '━', '┗', '┃', '┣', '━', '┫')`
        *   `"double" = ('╔', '═', '╗', '║', '╝', '═', '╚', '║', '╠', '═', '╣')`\n
        The order of the characters is always:
        1.  top-left corner
        2.  top border
        3.  top-right corner
        4.  right border
        5.  bottom-right corner
        6.  bottom border
        7.  bottom-left corner
        8.  left border
        9.  left horizontal rule connector
        10. horizontal rule
        11. right horizontal rule connector"""

        if w_padding < 0:
            raise ValueError(f"The 'w_padding' parameter must be a non-negative integer, got {w_padding!r}")
        if indent < 0:
            raise ValueError(f"The 'indent' parameter must be a non-negative integer, got {indent!r}")
        if _border_chars is not None:
            if len(_border_chars) != 11:
                raise ValueError(f"The '_border_chars' parameter must contain exactly 11 characters, got {len(_border_chars)}")
            if not all(len(char) == 1 for char in _border_chars):
                raise ValueError(
                    f"The '_border_chars' parameter must only contain single-character strings, got {_border_chars!r}"
                )

        if Color.is_valid(border_style):
            border_style = Color.to_hexa(border_style)

        borders = {
            "standard": ("┌", "─", "┐", "│", "┘", "─", "└", "│", "├", "─", "┤"),
            "rounded": ("╭", "─", "╮", "│", "╯", "─", "╰", "│", "├", "─", "┤"),
            "strong": ("┏", "━", "┓", "┃", "┛", "━", "┗", "┃", "┣", "━", "┫"),
            "double": ("╔", "═", "╗", "║", "╝", "═", "╚", "║", "╠", "═", "╣"),
        }
        border_chars = borders.get(border_type, borders["standard"]) if _border_chars is None else _border_chars

        lines, unfmt_lines, max_line_len = cls._prepare_log_box(values, default_color, has_rules=True)

        spaces_l = " " * indent
        pad_w_full = (cls.width - (max_line_len + (2 * w_padding)) - (len(border_chars[1] * 2))) if w_full else 0

        border_l = f"[{border_style}]{border_chars[7]}[*]"
        border_r = f"[{border_style}]{border_chars[3]}[_]"
        border_t = f"{spaces_l}[{border_style}]{border_chars[0]}{border_chars[1] * (cls.width - (len(border_chars[1] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[2]}[_]"
        border_b = f"{spaces_l}[{border_style}]{border_chars[6]}{border_chars[5] * (cls.width - (len(border_chars[5] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[4]}[_]"

        h_rule = f"{spaces_l}[{border_style}]{border_chars[8]}{border_chars[9] * (cls.width - (len(border_chars[9] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[10]}[_]"

        lines = [( \
            h_rule if _PATTERNS.hr.match(line) else f"{spaces_l}{border_l}{' ' * w_padding}{line}[_]"
            + " " * ((w_padding + max_line_len - len(unfmt)) + pad_w_full)
            + border_r
        ) for line, unfmt in zip(lines, unfmt_lines)]

        FormatCodes.print(
            ( \
                f"{start}{border_t}[_]\n"
                + "\n".join(lines)
                + ("\n" if lines else "")
                + f"{border_b}[_]"
            ),
            default_color=default_color,
            sep="\n",
            end=end,
        )

    @classmethod
    def confirm(
        cls,
        prompt: object = "Do you want to continue?",
        /,
        *,
        start: str = "",
        end: str = "",
        default_color: Optional[Rgba | Hexa] = None,
        default_is_yes: bool = True,
    ) -> bool:
        """Ask a yes/no question.\n
        ------------------------------------------------------------------------------------
        *   `prompt` – The input prompt.
        *   `start` – Something to print before the input.
        *   `end` – Something to print after the input (e.g. `\\n`).
        *   `default_color` – The default text color of the `prompt`.
        *   `default_is_yes` – The default answer if the user just presses enter.
        ------------------------------------------------------------------------------------
        The prompt can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see the `format_codes` module documentation."""

        confirmed = cls.input(
            FormatCodes.to_ansi(
                f"{start}{str(prompt)} [_|dim](({'Y' if default_is_yes else 'y'}/{'n' if default_is_yes else 'N'}): )",
                default_color=default_color,
            )
        ).strip().lower() in ({"", "y", "yes"} if default_is_yes else {"y", "yes"})

        if end:
            FormatCodes.print(end, end="")
        return confirmed

    @classmethod
    def multiline_input(
        cls,
        prompt: object = "",
        /,
        *,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        show_keybindings: bool = True,
        input_prefix: str = " ⮡ ",
        reset_ansi: bool = True,
    ) -> str:
        """An input where users can write (and paste) text over multiple lines.\n
        ---------------------------------------------------------------------------------------
        *   `prompt` – The input prompt.
        *   `start` – Something to print before the input.
        *   `end` – Something to print after the input (e.g. `\\n`).
        *   `default_color` – The default text color of the `prompt`.
        *   `show_keybindings` – Whether to show the special keybindings or not.
        *   `input_prefix` – The prefix of the input line.
        *   `reset_ansi` – Whether to reset the ANSI codes after the input or not.
        ---------------------------------------------------------------------------------------
        The input prompt can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see the `format_codes` module documentation."""

        kb = KeyBindings()
        kb.add("c-d", eager=True)(cls._multiline_input_submit)

        FormatCodes.print(start + str(prompt), default_color=default_color)
        if show_keybindings:
            FormatCodes.print("[dim][[b](CTRL+D)[dim] : end of input][_dim]")
        input_string = _pt.prompt(input_prefix, multiline=True, wrap_lines=True, key_bindings=kb)
        FormatCodes.print("[_]" if reset_ansi else "", end=end[1:] if end.startswith("\n") else end)

        return input_string

    @overload
    @classmethod
    def input(
        cls,
        prompt: object = "",
        /,
        *,
        start: str = "",
        end: str = "",
        default_color: Optional[Rgba | Hexa] = None,
        placeholder: Optional[str] = None,
        mask_char: Optional[str] = None,
        min_len: Optional[int] = None,
        max_len: Optional[int] = None,
        allowed_chars: str | AllTextChars = CHARS.ALL,
        allow_paste: bool = True,
        validator: Optional[Callable[[str], Optional[str]]] = None,
        default_val: Optional[str] = None,
        output_type: type[str] = str,
    ) -> str:
        ...

    @overload
    @classmethod
    def input(
        cls,
        prompt: object = "",
        /,
        *,
        start: str = "",
        end: str = "",
        default_color: Optional[Rgba | Hexa] = None,
        placeholder: Optional[str] = None,
        mask_char: Optional[str] = None,
        min_len: Optional[int] = None,
        max_len: Optional[int] = None,
        allowed_chars: str | AllTextChars = CHARS.ALL,
        allow_paste: bool = True,
        validator: Optional[Callable[[str], Optional[str]]] = None,
        default_val: Optional[T] = None,
        output_type: type[T] = ...,
    ) -> T:
        ...

    @classmethod
    def input(
        cls,
        prompt: object = "",
        /,
        *,
        start: str = "",
        end: str = "",
        default_color: Optional[Rgba | Hexa] = None,
        placeholder: Optional[str] = None,
        mask_char: Optional[str] = None,
        min_len: Optional[int] = None,
        max_len: Optional[int] = None,
        allowed_chars: str | AllTextChars = CHARS.ALL,
        allow_paste: bool = True,
        validator: Optional[Callable[[str], Optional[str]]] = None,
        default_val: Any = None,
        output_type: type[Any] = str,
    ) -> Any:
        """Acts like a standard Python `input()` a bunch of cool extra features.\n
        ----------------------------------------------------------------------------------------
        *   `prompt` – The input prompt.
        *   `start` – Something to print before the input.
        *   `end` – Something to print after the input (e.g. `\\n`).
        *   `default_color` – The default text color of the `prompt`.
        *   `placeholder` – A placeholder text that is shown when the input is empty.
        *   `mask_char` – If set, the input will be masked with this character.
        *   `min_len` – The minimum length of the input (required to submit).
        *   `max_len` – The maximum length of the input (can't write further if reached).
        *   `allowed_chars` – A string of characters that are allowed to be inputted<br>
            (default allows all characters).
        *   `allow_paste` – Whether to allow pasting text into the input or not.
        *   `validator` – A function that takes the input string and returns a string error<br>
            message if invalid, or nothing if valid.
        *   `default_val` – The default value to return if the input is empty.
        *   `output_type` – The type (class) to convert the input to before returning it.
        ----------------------------------------------------------------------------------------
        The input prompt can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see the `format_codes` module documentation."""

        if mask_char is not None and len(mask_char) != 1:
            raise ValueError(f"The 'mask_char' parameter must be a single character, got {mask_char!r}")
        if min_len is not None and min_len < 0:
            raise ValueError(f"The 'min_len' parameter must be a non-negative integer, got {min_len!r}")
        if max_len is not None and max_len < 0:
            raise ValueError(f"The 'max_len' parameter must be a non-negative integer, got {max_len!r}")

        helper = _ConsoleInputHelper(
            mask_char=mask_char,
            min_len=min_len,
            max_len=max_len,
            allowed_chars=allowed_chars,
            allow_paste=allow_paste,
            validator=validator,
        )

        kb = KeyBindings()
        kb.add(Keys.Delete)(helper.handle_delete)
        kb.add(Keys.Backspace)(helper.handle_backspace)
        kb.add(Keys.ControlA)(helper.handle_control_a)
        kb.add(Keys.BracketedPaste)(helper.handle_paste)
        kb.add(Keys.Any)(helper.handle_any)

        custom_style = Style.from_dict({"bottom-toolbar": "noreverse"})
        session: _pt.PromptSession[str] = _pt.PromptSession(
            message=_pt.formatted_text.ANSI(FormatCodes.to_ansi(str(prompt), default_color=default_color)),
            validator=_ConsoleInputValidator(
                helper.get_text,
                mask_char=mask_char,
                min_len=min_len,
                validator=validator,
            ),
            validate_while_typing=True,
            key_bindings=kb,
            bottom_toolbar=helper.bottom_toolbar,
            placeholder=_pt.formatted_text.ANSI(FormatCodes.to_ansi(f"[i|br:black]{placeholder}[_i|_c]"))
            if placeholder else "",
            style=custom_style,
        )
        FormatCodes.print(start, end="")
        session.prompt()
        FormatCodes.print(end, end="")

        if (result_text := helper.get_text()) in {"", None}:
            if default_val is not None:
                return default_val
            result_text = ""

        if output_type == str:
            return result_text

        else:
            try:
                return output_type(result_text)  # type: ignore[call-arg]
            except (ValueError, TypeError):
                if default_val is not None:
                    return default_val
                raise

    @staticmethod
    def _read_single_key() -> None:
        """Wait for a single key press without requiring elevated privileges.<br>
        Falls back to reading a line when stdin is not a TTY (e.g. piped input)."""

        if not _sys.stdin.isatty():
            _sys.stdin.readline()
            return

        if _sys.platform == "win32":
            import msvcrt as _msvcrt  # type: ignore[import-not-found]
            _msvcrt.getch()  # type: ignore[attr-defined]

        else:
            import tty as _tty  # type: ignore[import-not-found]
            import termios as _termios  # type: ignore[import-not-found]

            fd = _sys.stdin.fileno()
            old_settings = _termios.tcgetattr(fd)  # type: ignore[attr-defined]

            try:
                _tty.setraw(fd)  # type: ignore[attr-defined]
                _sys.stdin.read(1)
            finally:
                _termios.tcsetattr(fd, _termios.TCSADRAIN, old_settings)  # type: ignore[attr-defined]

    @staticmethod
    def _process_lines(clean_prompt: str, wrap_len: int) -> Generator[tuple[Literal[""]] | list[str], Any, None]:
        """Splits the clean prompt into lines and then splits each line into chunks that fit within the wrap length."""

        for line in clean_prompt.splitlines():
            lst = String.split_count(line, wrap_len)
            yield ("", ) if not lst else lst

    @classmethod
    def _add_back_removed_parts(cls, split_string: list[str], removals: tuple[tuple[int, str], ...], /) -> list[str]:
        """Adds back the removed parts into the split string parts at their original positions."""

        cumulative_pos = [0]
        for length in [len(part) for part in split_string]:
            cumulative_pos.append(cumulative_pos[-1] + length)

        result, offset_adjusts = split_string.copy(), [0] * len(split_string)
        last_idx, total_length = len(split_string) - 1, cumulative_pos[-1]

        for pos, removal in removals:
            if pos >= total_length:
                result[last_idx] = result[last_idx] + removal
                continue

            i = cls._find_string_part(pos, cumulative_pos)
            adjusted_pos = (pos - cumulative_pos[i]) + offset_adjusts[i]
            parts = [result[i][:adjusted_pos], removal, result[i][adjusted_pos:]]
            result[i] = "".join(parts)
            offset_adjusts[i] += len(removal)

        return result

    @staticmethod
    def _find_string_part(pos: int, cumulative_pos: list[int], /) -> int:
        """Finds the index of the string part that contains the given position."""

        left, right = 0, len(cumulative_pos) - 1

        while left < right:
            mid = (left + right) // 2

            if cumulative_pos[mid] <= pos < cumulative_pos[mid + 1]:
                return mid
            elif pos < cumulative_pos[mid]:
                right = mid
            else:
                left = mid + 1

        return left

    @staticmethod
    def _prepare_log_box(
        values: list[object] | tuple[object, ...],
        /,
        default_color: Optional[Rgba | Hexa] = None,
        *,
        has_rules: bool = False,
    ) -> tuple[list[str], list[str], int]:
        """Prepares the log box content and returns it along with the max line length."""

        if has_rules:
            lines: list[str] = []

            for val in values:
                result_parts: list[str] = []
                val_str, current_pos = str(val), 0

                for match in _PATTERNS.hr.finditer(val_str):
                    start, end = match.span()
                    should_split_before = start > 0 and val_str[start - 1] != "\n"
                    should_split_after = end < len(val_str) and val_str[end] != "\n"

                    if should_split_before:
                        if start > current_pos:
                            result_parts.append(val_str[current_pos:start])
                        if should_split_after:
                            result_parts.append(match.group())
                            current_pos = end
                        else:
                            current_pos = start

                    else:
                        if should_split_after:
                            result_parts.append(val_str[current_pos:end])
                            current_pos = end

                if current_pos < len(val_str):
                    result_parts.append(val_str[current_pos:])

                if not result_parts:
                    result_parts.append(val_str)

                for part in result_parts:
                    lines.extend(part.splitlines())

        else:
            lines = [line for val in values for line in str(val).splitlines()]

        unfmt_lines = [FormatCodes.remove(line, default_color) for line in lines]
        max_line_len = max(len(line) for line in unfmt_lines) if unfmt_lines else 0

        return lines, unfmt_lines, max_line_len

    @staticmethod
    def _multiline_input_submit(event: KeyPressEvent, /) -> None:
        event.app.exit(result=event.app.current_buffer.document.text)


class _ConsoleArgsParseHelper:
    """Internal, callable helper class to parse command-line arguments."""

    def __init__(
        self,
        arg_parse_configs: ArgParseConfigs,
        /,
        *,
        skip: int = 0,
        flag_value_sep: Optional[str],
        allow_space_value: bool = True,
    ):
        self.arg_parse_configs = arg_parse_configs
        self.flag_value_sep = flag_value_sep
        self.allow_space_value = allow_space_value

        self.parsed_args: dict[str, ParsedArgData] = {}
        self.positional_configs: dict[str, str] = {}
        self.arg_lookup: dict[str, str] = {}

        self.args = _sys.argv[1 + skip:]
        self.args_len = len(self.args)
        self.pos_before_configured = False
        self.pos_after_configured = False
        self.first_flag_pos: Optional[int] = None
        self.last_flag_pos: Optional[int] = None

    def __call__(self) -> ParsedArgs:
        self.parse_arg_configs()
        self.find_flag_positions()
        self.process_flagged_args()
        self.process_positional_args()

        return ParsedArgs(**self.parsed_args)

    def parse_arg_configs(self) -> None:
        """Parse the `arg_parse_configs` configuration and build lookup structures."""

        for alias, config in self.arg_parse_configs.items():
            if not alias.isidentifier():
                raise ValueError(f"Invalid argument alias '{alias}'.\n"
                                 "Aliases must be valid Python identifiers.")
            if alias in ParsedArgs.RESERVED_ALIASES:
                raise ValueError(
                    f"Invalid argument alias '{alias}'.\n"
                    f"The following names are reserved and cannot be used as aliases:\n"
                    f"{', '.join(sorted(ParsedArgs.RESERVED_ALIASES))}"
                )

            # PARSE ARG CONFIG & BUILD FLAG LOOKUP FOR NON-POSITIONAL ARGS
            if (flags := self._parse_arg_config(alias, config)) is not None:
                for flag in flags:
                    if flag in self.arg_lookup:
                        raise ValueError(
                            f"Duplicate flag '{flag}' found. It's assigned to both '{self.arg_lookup[flag]}' and '{alias}'."
                        )
                    self.arg_lookup[flag] = alias

    def _parse_arg_config(self, alias: str, config: ArgParseConfig, /) -> Optional[set[str]]:
        """Parse an individual argument configuration."""

        # POSITIONAL ARGUMENT CONFIGURATION
        if isinstance(config, str):
            if config == "before":
                if self.pos_before_configured:
                    raise ValueError("Only one alias can use the value 'before' for positional argument collection.")
                self.pos_before_configured = True
            elif config == "after":
                if self.pos_after_configured:
                    raise ValueError("Only one alias can use the value 'after' for positional argument collection.")
                self.pos_after_configured = True
            else:
                raise ValueError(
                    f"Invalid positional argument type '{config}' under alias '{alias}'.\n"
                    "Must be either 'before' or 'after'."
                )

            self.positional_configs[alias] = config
            self.parsed_args[alias] = ParsedArgData(exists=False, values=[], is_pos=True)

            return None  # NO FLAGS TO RETURN FOR POSITIONAL ARGS

        # NORMAL SET OF FLAGS
        elif isinstance(config, set):
            if not config:
                raise ValueError(
                    f"The flag set under alias '{alias}' is empty.\n"
                    "The set must contain at least one flag to search for."
                )

            self.parsed_args[alias] = ParsedArgData(exists=False, values=[], is_pos=False)

            return config

        # SET OF FLAGS WITH SPECIFIED DEFAULT VALUE
        else:
            if not config["flags"]:
                raise ValueError(
                    f"No flags provided under alias '{alias}'.\n"
                    "The 'flags'-key set must contain at least one flag to search for."
                )

            self.parsed_args[alias] = ParsedArgData(
                exists=False,
                values=[config["default"]],
                is_pos=False,
            )

            return config["flags"]

    def find_flag_positions(self) -> None:
        """Find positions of first and last flags for positional argument collection."""

        i = 0
        while i < self.args_len:
            arg = self.args[i]

            # CHECK FOR FLAG WITH INLINE SEPARATOR ('--flag=value')
            if self.flag_value_sep and self.flag_value_sep in arg:
                if arg.split(self.flag_value_sep, 1)[0].strip() in self.arg_lookup:
                    if self.first_flag_pos is None:
                        self.first_flag_pos = i
                    self.last_flag_pos = i
                    i += 1
                    continue

            # CHECK FOR STANDALONE FLAG
            if arg in self.arg_lookup:
                if self.first_flag_pos is None:
                    self.first_flag_pos = i
                self.last_flag_pos = i

                # CHECK FOR SEPARATOR IN NEXT TOKENS ('--flag', '=', 'value')
                if self.flag_value_sep and i + 1 < self.args_len and self.args[i + 1].strip() == self.flag_value_sep:
                    if i + 2 < self.args_len:
                        i += 3  # SKIP FLAG, SEPARATOR, AND VALUE
                        continue
                    else:
                        i += 2  # SKIP FLAG AND SEPARATOR
                        continue

                # CHECK FOR SPACE-SEPARATED VALUE ('--flag value')
                if self.allow_space_value and i + 1 < self.args_len:
                    next_arg = self.args[i + 1]
                    if self._is_flag_value(next_arg):
                        i += 2  # SKIP FLAG AND ITS SPACE-SEPARATED VALUE
                        continue

            i += 1

    def process_positional_args(self) -> None:
        """Collect positional `"before"`/`"after"` arguments."""

        for alias, pos_type in self.positional_configs.items():
            if pos_type == "before":
                self._collect_before_arg(alias)
            elif pos_type == "after":
                self._collect_after_arg(alias)
            else:
                raise ValueError(
                    f"Invalid positional argument type '{pos_type}' for alias '{alias}'.\n"
                    "Must be either 'before' or 'after'."
                )

    def _collect_before_arg(self, alias: str, /) -> None:
        """Collect positional `"before"` arguments."""

        before_args: list[str] = []
        end_pos: int = self.first_flag_pos if self.first_flag_pos is not None else self.args_len

        for i in range(end_pos):
            if self._is_positional_arg(arg := self.args[i], allow_separator=False):
                before_args.append(arg)

        if before_args:
            self.parsed_args[alias].values = before_args
            self.parsed_args[alias].exists = len(before_args) > 0

    def _collect_after_arg(self, alias: str, /) -> None:
        """Collect positional `"after"` arguments."""

        after_args: list[str] = []
        start_pos: int = (self.last_flag_pos + 1) if self.last_flag_pos is not None else 0

        # SKIP THE VALUE AFTER THE LAST FLAG IF IT HAS A SEPARATOR
        if self.last_flag_pos is not None:
            # CHECK IF LAST FLAG HAS INLINE VALUE ('--flag=value')
            if self.flag_value_sep and self.flag_value_sep in self.args[self.last_flag_pos]:
                start_pos = self.last_flag_pos + 1  # VALUE IS INLINE, START AFTER THIS POSITION
            # CHECK IF NEXT TOKEN IS SEPARATOR ('--flag', '=', 'value')
            elif self.flag_value_sep and start_pos < self.args_len and self.args[start_pos].strip() == self.flag_value_sep:
                if start_pos + 1 < self.args_len:
                    start_pos += 2  # SKIP SEPARATOR AND VALUE
                else:
                    start_pos += 1  # SKIP SEPARATOR ONLY
            # CHECK IF NEXT TOKEN IS SPACE-SEPARATED VALUE ('--flag value')
            elif self.allow_space_value and start_pos < self.args_len and self._is_flag_value(self.args[start_pos]):
                start_pos += 1  # SKIP SPACE-SEPARATED VALUE
            # NO SEPARATOR = FLAG HAS NO VALUE = START COLLECTING FROM NEXT POSITION

        for i in range(start_pos, self.args_len):
            arg = self.args[i]
            # DON'T INCLUDE FLAGS OR SEPARATORS
            if self.flag_value_sep and arg == self.flag_value_sep:
                continue
            elif self._is_positional_arg(arg):
                after_args.append(arg)

        if after_args:
            self.parsed_args[alias].values = after_args
            self.parsed_args[alias].exists = len(after_args) > 0

    def _is_positional_arg(self, arg: str, /, *, allow_separator: bool = True) -> bool:
        """Check if an argument is positional (not a flag or separator)."""

        if (self.flag_value_sep \
                and self.flag_value_sep in arg
                and arg.split(self.flag_value_sep, 1)[0].strip() not in self.arg_lookup):
            return True
        if arg not in self.arg_lookup and (allow_separator or not self.flag_value_sep or arg != self.flag_value_sep):
            return True
        return False

    def _is_flag_value(self, arg: str, /) -> bool:
        """Check if an argument can be treated as a space-separated flag value<br>
        (i.e. it is not a known flag, not the separator, and not a `flag=value` token)."""

        if arg in self.arg_lookup:
            return False
        if self.flag_value_sep and arg.strip() == self.flag_value_sep:
            return False
        if (self.flag_value_sep \
                and self.flag_value_sep in arg
                and arg.split(self.flag_value_sep, 1)[0].strip() in self.arg_lookup):
            return False
        return True

    def process_flagged_args(self) -> None:
        """Process flagged arguments."""

        i = 0

        while i < self.args_len:
            arg = self.args[i]

            # CASE 1: FLAG WITH INLINE SEPARATOR ('--flag=value')
            if self.flag_value_sep and self.flag_value_sep in arg:
                parts = arg.split(self.flag_value_sep, 1)

                if (potential_flag := (parts := arg.split(self.flag_value_sep, 1))[0].strip()) in self.arg_lookup:
                    alias = self.arg_lookup[potential_flag]
                    self.parsed_args[alias].exists = True
                    self.parsed_args[alias].flag = potential_flag

                    if len(parts) > 1 and (val := parts[1].strip()):
                        self.parsed_args[alias].values = [val]

                    i += 1
                    continue

            # CASE 2: STANDALONE FLAG
            if arg in self.arg_lookup:
                alias = self.arg_lookup[arg]
                self.parsed_args[alias].exists = True
                self.parsed_args[alias].flag = arg

                # CHECK FOR SEPARATOR IN NEXT TOKENS ('--flag', '=', 'value')
                if self.flag_value_sep and i + 1 < self.args_len and self.args[i + 1].strip() == self.flag_value_sep:
                    if i + 2 < self.args_len:
                        if (val := self.args[i + 2]) not in self.arg_lookup and val != self.flag_value_sep:
                            self.parsed_args[alias].values = [val]
                            i += 3
                            continue
                    i += 2
                    continue

                # CHECK FOR SPACE-SEPARATED VALUE ('--flag value')
                if self.allow_space_value and i + 1 < self.args_len and self._is_flag_value(next_arg := self.args[i + 1]):
                    self.parsed_args[alias].values = [next_arg]
                    i += 2
                    continue
                # NO SEPARATOR = JUST A FLAG WITHOUT VALUE

            i += 1


class _ConsoleLogBoxBgReplacer:
    """Internal, callable class to replace matched text with background-format-code text for log boxes."""

    def __init__(self, bg_fc: str, /) -> None:
        self.bg_fc = bg_fc

    def __call__(self, match: _rx.Match[str], /) -> str:
        return f"{match.group(0)}[{self.bg_fc}]"


class _ConsoleInputHelper:
    """Helper class to manage input processing and events."""

    def __init__(
        self,
        mask_char: Optional[str],
        min_len: Optional[int],
        max_len: Optional[int],
        allowed_chars: str | AllTextChars,
        allow_paste: bool,
        validator: Optional[Callable[[str], Optional[str]]],
    ) -> None:
        self.mask_char = mask_char
        self.min_len = min_len
        self.max_len = max_len
        self.allowed_chars = allowed_chars
        self.allow_paste = allow_paste
        self.validator = validator

        self.result_text: str = ""
        self.filtered_chars: set[str] = set()
        self.tried_pasting: bool = False

    def get_text(self) -> str:
        """Returns the current result text."""

        return self.result_text

    def bottom_toolbar(self) -> _pt.formatted_text.ANSI:
        """Generates the bottom toolbar text based on the current input state."""

        try:
            if self.mask_char:
                text_to_check = self.result_text
            else:
                app = _pt.application.get_app()
                text_to_check = app.current_buffer.text

            toolbar_msgs: list[str] = []
            if self.max_len and len(text_to_check) > self.max_len:
                toolbar_msgs.append("[b|#FFF|bg:red]( Text too long! )")
            if self.validator and text_to_check and (validation_error_msg := self.validator(text_to_check)) not in {"", None}:
                toolbar_msgs.append(f"[b|#000|bg:br:red] {validation_error_msg} [_bg]")
            if self.filtered_chars:
                plural = "" if len(char_list := "".join(sorted(self.filtered_chars))) == 1 else "s"
                toolbar_msgs.append(f"[b|#000|bg:yellow]( Char{plural} '{char_list}' not allowed )")
                self.filtered_chars.clear()
            if self.min_len and len(text_to_check) < self.min_len:
                toolbar_msgs.append(f"[b|#000|bg:yellow]( Need {self.min_len - len(text_to_check)} more chars )")
            if self.tried_pasting:
                toolbar_msgs.append("[b|#000|bg:br:yellow]( Pasting disabled )")
                self.tried_pasting = False
            if self.max_len and len(text_to_check) == self.max_len:
                toolbar_msgs.append("[b|#000|bg:br:yellow]( Maximum length reached )")

            return _pt.formatted_text.ANSI(FormatCodes.to_ansi(" ".join(toolbar_msgs)))

        except Exception:
            return _pt.formatted_text.ANSI("")

    def process_insert_text(self, text: str, /) -> tuple[str, set[str]]:
        """Processes the inserted text according to the allowed characters and max length."""

        removed_chars: set[str] = set()

        if not text:
            return "", removed_chars

        processed_text = "".join(char for char in text if ord(char) >= 32)
        if self.allowed_chars is not CHARS.ALL:
            filtered_text = ""
            for char in processed_text:
                if char in cast(str, self.allowed_chars):
                    filtered_text += char
                else:
                    removed_chars.add(char)
            processed_text = filtered_text

        if self.max_len:
            if (remaining_space := self.max_len - len(self.result_text)) > 0:
                if len(processed_text) > remaining_space:
                    processed_text = processed_text[:remaining_space]
            else:
                processed_text = ""

        return processed_text, removed_chars

    def insert_text_event(self, event: KeyPressEvent, /) -> None:
        """Handles text insertion events (typing/pasting)."""

        try:
            if not (insert_text := event.data):
                return

            buffer = event.app.current_buffer
            cursor_pos = buffer.cursor_position
            insert_text, filtered_chars = self.process_insert_text(insert_text)
            self.filtered_chars.update(filtered_chars)

            if insert_text:
                self.result_text = self.result_text[:cursor_pos] + insert_text + self.result_text[cursor_pos:]
                if self.mask_char:
                    buffer.insert_text(self.mask_char[0] * len(insert_text))
                else:
                    buffer.insert_text(insert_text)

        except Exception:
            pass

    def remove_text_event(self, event: KeyPressEvent, /, *, is_backspace: bool = False) -> None:
        """Handles text removal events (backspace/delete)."""

        try:
            buffer = event.app.current_buffer
            cursor_pos = buffer.cursor_position
            has_selection = buffer.selection_state is not None

            if has_selection:
                start, end = buffer.document.selection_range()
                self.result_text = self.result_text[:start] + self.result_text[end:]
                buffer.cursor_position = start
                buffer.delete(end - start)
            else:
                if is_backspace:
                    if cursor_pos > 0:
                        self.result_text = self.result_text[:cursor_pos - 1] + self.result_text[cursor_pos:]
                        buffer.delete_before_cursor(1)
                else:
                    if cursor_pos < len(self.result_text):
                        self.result_text = self.result_text[:cursor_pos] + self.result_text[cursor_pos + 1:]
                        buffer.delete(1)

        except Exception:
            pass

    def handle_delete(self, event: KeyPressEvent, /) -> None:
        self.remove_text_event(event)

    def handle_backspace(self, event: KeyPressEvent, /) -> None:
        self.remove_text_event(event, is_backspace=True)

    @staticmethod
    def handle_control_a(event: KeyPressEvent, /) -> None:
        buffer = event.app.current_buffer
        buffer.cursor_position = 0
        buffer.start_selection()
        buffer.cursor_position = len(buffer.text)

    def handle_paste(self, event: KeyPressEvent, /) -> None:
        if self.allow_paste:
            self.insert_text_event(event)
        else:
            self.tried_pasting = True

    def handle_any(self, event: KeyPressEvent, /) -> None:
        self.insert_text_event(event)


class _ConsoleInputValidator(Validator):

    def __init__(
        self,
        get_text: Callable[[], str],
        /,
        *,
        mask_char: Optional[str],
        min_len: Optional[int],
        validator: Optional[Callable[[str], Optional[str]]],
    ):
        self.get_text = get_text
        self.mask_char = mask_char
        self.min_len = min_len
        self.validator = validator

    def validate(self, document: Document) -> None:
        """Validates the input text according to the minimum length and custom validator function."""

        text_to_validate = self.get_text() if self.mask_char else document.text
        if self.min_len and len(text_to_validate) < self.min_len:
            raise ValidationError(message="", cursor_position=len(document.text))
        if self.validator and self.validator(text_to_validate) not in {"", None}:
            raise ValidationError(message="", cursor_position=len(document.text))


class ProgressBar:
    """A terminal progress bar with smooth transitions and customizable appearance.\n
    ------------------------------------------------------------------------------------------------------
    *   `min_width` – The min width of the progress bar in chars.
    *   `max_width` – The max width of the progress bar in chars.
    *   `bar_format` – The format strings used to render the progress bar, containing placeholders:
        -   `{label}` `{l}`
        -   `{bar}` `{b}`
        -   `{current}` `{c}` (optional `:<char>` format specifier for thousands separator, e.g. `{c:,}`)
        -   `{total}` `{t}` (optional `:<char>` format specifier for thousands separator, e.g. `{t:,}`)
        -   `{percentage}` `{percent}` `{p}` (optional `:.<num>f` format specifier to round<br>
            to specified number of decimal places, e.g. `{p:.1f}`)
    *   `limited_bar_format` – A simplified format string used when the terminal width is too small<br>
        for the normal `bar_format`.
    *   `chars` – A tuple of characters ordered from full to empty progress:<br>
        The first character represents completely filled sections.<br>
        Intermediate characters create smooth transitions<br>
        The last character represents empty sections.
    ------------------------------------------------------------------------------------------------------
    The bar format (also limited) can additionally be formatted with special formatting codes.<br>
    For more detailed information about formatting codes, see the `format_codes` module documentation."""

    def __init__(
        self,
        *,
        min_width: int = 10,
        max_width: int = 50,
        bar_format: list[str] | tuple[str, ...] = ["{l}", "[bg:black]({b})", "[b]({c:,})/{t:,}", "[dim](([i]({p}%)))"],
        limited_bar_format: list[str] | tuple[str, ...] = ["[bg:black]({b})"],
        sep: str = " ",
        chars: tuple[str, ...] = ("█", "▉", "▊", "▋", "▌", "▍", "▎", "▏", " "),
    ):
        self.active: bool = False
        """Whether the progress bar is currently active (intercepting stdout) or not."""
        self.min_width: int
        """The min width of the progress bar in chars."""
        self.max_width: int
        """The max width of the progress bar in chars."""
        self.bar_format: list[str] | tuple[str, ...]
        """The format strings used to render the progress bar (joined by `sep`)."""
        self.limited_bar_format: list[str] | tuple[str, ...]
        """The simplified format strings used when the terminal width is too small."""
        self.sep: str
        """The separator string used to join multiple bar-format strings."""
        self.chars: tuple[str, ...]
        """A tuple of characters ordered from full to empty progress."""

        self.set_width(min_width, max_width)
        self.set_bar_format(bar_format, limited_bar_format, sep=sep)
        self.set_chars(chars)

        self._buffer: list[str] = []
        self._original_stdout: Optional[TextIO] = None
        self._current_progress_str: str = ""
        self._last_line_len: int = 0
        self._last_update_time: float = 0.0
        self._min_update_interval: float = 0.02  # 20ms = MAX 50 UPDATES/SECOND

    def set_width(self, min_width: Optional[int] = None, max_width: Optional[int] = None) -> None:
        """Set the width of the progress bar.\n
        -----------------------------------------------------------------
        *   `min_width` – The min width of the progress bar in chars.
        *   `max_width` – The max width of the progress bar in chars."""

        if min_width is not None:
            if min_width < 1:
                raise ValueError(f"The 'min_width' parameter must be a positive integer, got {min_width!r}")

            self.min_width = max(1, min_width)

        if max_width is not None:
            if max_width < 1:
                raise ValueError(f"The 'max_width' parameter must be a positive integer, got {max_width!r}")

            self.max_width = max(self.min_width, max_width)

    def set_bar_format(
        self,
        bar_format: Optional[list[str] | tuple[str, ...]] = None,
        limited_bar_format: Optional[list[str] | tuple[str, ...]] = None,
        *,
        sep: Optional[str] = None,
    ) -> None:
        """Set the format string used to render the progress bar.\n
        ------------------------------------------------------------------------------------------------------
        *   `bar_format` – The format strings used to render the progress bar, containing placeholders:
            -   `{label}` `{l}`
            -   `{bar}` `{b}`
            -   `{current}` `{c}` (optional `:<char>` format specifier for thousands separator, e.g. `{c:,}`)
            -   `{total}` `{t}` (optional `:<char>` format specifier for thousands separator, e.g. `{t:,}`)
            -   `{percentage}` `{percent}` `{p}` (optional `:.<num>f` format specifier to round<br>
                to specified number of decimal places, e.g. `{p:.1f}`)
        *   `limited_bar_format` – A simplified format strings used when the terminal width is too small.
        *   `sep` – The separator string used to join multiple format strings.
        ------------------------------------------------------------------------------------------------------
        The bar format (also limited) can additionally be formatted with special formatting codes.<br>
        For more detailed information about formatting codes, see the `format_codes` module documentation."""

        if bar_format is not None:
            if not any(_PATTERNS.bar.search(part) for part in bar_format):
                raise ValueError(
                    f"The 'bar_format' parameter value must contain the '{{bar}}' or '{{b}}' placeholder, got {bar_format!r}"
                )

            self.bar_format = bar_format

        if limited_bar_format is not None:
            if not any(_PATTERNS.bar.search(part) for part in limited_bar_format):
                raise ValueError(
                    f"The 'limited_bar_format' parameter value must contain the '{{bar}}' or '{{b}}' placeholder, got {limited_bar_format!r}"
                )

            self.limited_bar_format = limited_bar_format

        if sep is not None:
            self.sep = sep

    def set_chars(self, chars: tuple[str, ...], /) -> None:
        """Set the characters used to render the progress bar.\n
        -----------------------------------------------------------------------------
        *   `chars` – A tuple of characters ordered from full to empty progress:<br>
            The first character represents completely filled sections.<br>
            Intermediate characters create smooth transitions.<br>
            The last character represents empty sections.<br>
            If `None`, uses default Unicode block characters."""

        if len(chars) < 2:
            raise ValueError(f"The 'chars' parameter must contain at least two characters (full and empty), got {chars!r}")
        elif not all(len(char) == 1 for char in chars):
            raise ValueError(f"All elements of 'chars' must be single-character strings, got {chars!r}")

        self.chars = chars

    def show_progress(self, current: int, total: int, /, label: Optional[str] = None) -> None:
        """Show or update the progress bar.\n
        ----------------------------------------------------------------------------------------------
        *   `current` – The current progress value (below `0` or greater than `total` hides the bar).
        *   `total` – The total value representing 100% progress (must be greater than `0`).
        *   `label` – An optional label which is inserted at the `{label}` or `{l}` placeholder."""

        # THROTTLE UPDATES (UNLESS IT'S THE FIRST/FINAL UPDATE)
        current_time = _time.time()
        if (
            not (self._last_update_time == 0.0 or current >= total or current < 0) \
            and (current_time - self._last_update_time) < self._min_update_interval
        ):
            return
        self._last_update_time = current_time

        if current < 0:
            raise ValueError(f"The 'current' parameter must be a non-negative integer, got {current!r}")
        if total <= 0:
            raise ValueError(f"The 'total' parameter must be a positive integer, got {total!r}")

        try:
            if not self.active:
                self._start_intercepting()
            self._flush_buffer()
            self._draw_progress_bar(current, total, label or "")
            if current < 0 or current > total:
                self.hide_progress()
        except Exception:
            self._emergency_cleanup()
            raise

    def hide_progress(self) -> None:
        """Hide the progress bar and restore normal terminal output."""

        if self.active:
            self._clear_progress_line()
            self._stop_intercepting()

    @contextmanager
    def progress_context(self, total: int, /, label: Optional[str] = None) -> Generator[ProgressUpdater, None, None]:
        """Context manager for automatic cleanup. Returns a function to update progress.\n
        -----------------------------------------------------------------------------------------
        *   `total` – The total value representing 100% progress (must be greater than `0`).
        *   `label` – An optional label which is inserted at the `{label}` or `{l}` placeholder.
        -----------------------------------------------------------------------------------------
        The returned callable accepts keyword arguments.<br>
        At least one of these parameters must be provided:
        *   `current` – Update the current progress value.
        *   `label` – Update the progress label.

        #### Example usage:
        ```python
        with ProgressBar().progress_context(500, "Loading...") as update_progress:
            update_progress(0)  # Show empty bar at start

            for i in range(400):
                # Do some work...
                update_progress(i)  # Update progress

            update_progress(label="Finalizing...")  # Update label

            for i in range(400, 500):
                # Do some work...
                update_progress(i, f"Finalizing ({i})")  # Update both
        ```"""

        if total <= 0:
            raise ValueError(f"The 'total' parameter must be a positive integer, got {total!r}")

        try:
            yield _ProgressContextHelper(self, total, label)
        except Exception:
            self._emergency_cleanup()
            raise
        finally:
            self.hide_progress()

    def _draw_progress_bar(self, current: int, total: int, /, label: Optional[str] = None) -> None:
        if total <= 0 or not self._original_stdout:
            return

        percentage = min(100, (current / total) * 100)

        formatted, bar_width = self._get_formatted_info_and_bar_width(self.bar_format, current, total, percentage, label)
        if bar_width < self.min_width:
            formatted, bar_width = self._get_formatted_info_and_bar_width(
                self.limited_bar_format, current, total, percentage, label
            )

        bar = f"{self._create_bar(current, total, max(1, bar_width))}[*]"
        progress_text = _PATTERNS.bar.sub(FormatCodes.to_ansi(bar), formatted)

        self._current_progress_str = progress_text
        self._last_line_len = len(progress_text)
        self._original_stdout.write(f"{ANSI.CHAR}[2K\r{progress_text}")
        self._original_stdout.flush()

    def _get_formatted_info_and_bar_width(
        self,
        bar_format: list[str] | tuple[str, ...],
        current: int,
        total: int,
        percentage: float,
        /,
        label: Optional[str] = None,
    ) -> tuple[str, int]:
        fmt_parts: list[str] = []

        for part in bar_format:
            fmt_part = _PATTERNS.label.sub(label or "", part)
            fmt_part = _PATTERNS.current.sub(_ProgressBarCurrentReplacer(current), fmt_part)
            fmt_part = _PATTERNS.total.sub(_ProgressBarTotalReplacer(total), fmt_part)
            fmt_part = _PATTERNS.percentage.sub(_ProgressBarPercentageReplacer(percentage), fmt_part)
            if fmt_part:
                fmt_parts.append(fmt_part)

        fmt_str = self.sep.join(fmt_parts)
        fmt_str = FormatCodes.to_ansi(fmt_str)

        bar_space = Console.width - len(FormatCodes.remove_ansi(_PATTERNS.bar.sub("", fmt_str)))
        bar_width = min(bar_space, self.max_width) if bar_space > 0 else 0

        return fmt_str, bar_width

    def _create_bar(self, current: int, total: int, bar_width: int, /) -> str:
        progress = current / total if total > 0 else 0
        bar: list[str] = []

        for i in range(bar_width):
            pos_progress = (i + 1) / bar_width
            if progress >= pos_progress:
                bar.append(self.chars[0])
            elif progress >= pos_progress - (1 / bar_width):
                remainder = (progress - (pos_progress - (1 / bar_width))) * bar_width
                char_idx = len(self.chars) - 1 - min(int(remainder * len(self.chars)), len(self.chars) - 1)
                bar.append(self.chars[char_idx])
            else:
                bar.append(self.chars[-1])
        return "".join(bar)

    def _start_intercepting(self) -> None:
        self.active = True
        self._original_stdout = _sys.stdout
        _sys.stdout = _InterceptedOutput(self)

    def _stop_intercepting(self) -> None:
        if self._original_stdout:
            _sys.stdout = self._original_stdout
            self._original_stdout = None
        self.active = False
        self._buffer.clear()
        self._last_line_len = 0
        self._last_update_time = 0.0
        self._current_progress_str = ""

    def _emergency_cleanup(self) -> None:
        """Emergency cleanup to restore stdout in case of exceptions."""

        try:
            self._stop_intercepting()
        except Exception:
            pass

    def _clear_progress_line(self) -> None:
        if self._last_line_len > 0 and self._original_stdout:
            self._original_stdout.write(f"{ANSI.CHAR}[2K\r")
            self._original_stdout.flush()

    def _flush_buffer(self) -> None:
        if self._buffer and self._original_stdout:
            self._clear_progress_line()
            for content in self._buffer:
                self._original_stdout.write(content)
                self._original_stdout.flush()
            self._buffer.clear()

    def _redraw_display(self) -> None:
        if self._current_progress_str and self._original_stdout:
            self._original_stdout.write(f"{ANSI.CHAR}[2K\r{self._current_progress_str}")
            self._original_stdout.flush()


class _ProgressContextHelper:
    """Internal, callable helper class to update the progress bar's current value and/or label.\n
    ------------------------------------------------------------------------------------------------
    *   `current` – The current progress value.
    *   `label` – The progress label.
    *   `type_checking` – Whether to check the parameters' types:<br>
        Is false per default to save performance, but can be set to true for debugging purposes."""

    def __init__(self, progress_bar: ProgressBar, total: int, label: Optional[str], /):
        self.progress_bar = progress_bar
        self.total = total
        self.current_label = label
        self.current_progress = 0

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        current, label = None, None

        if (num_args := len(args)) == 1:
            current = args[0]
        elif num_args == 2:
            current, label = args[0], args[1]
        else:
            raise TypeError(f"update_progress() takes 1 or 2 positional arguments, got {len(args)}")

        if current is not None and "current" in kwargs:
            current = kwargs["current"]
        if label is None and "label" in kwargs:
            label = kwargs["label"]

        if current is None and label is None:
            raise TypeError("Either the keyword argument 'current' or 'label' must be provided.")

        if current is not None:
            self.current_progress = current
        if label is not None:
            self.current_label = label

        self.progress_bar.show_progress(self.current_progress, self.total, label=self.current_label)


class _ProgressBarCurrentReplacer:
    """Internal, callable class to replace `{current}` placeholder with formatted number."""

    def __init__(self, current: int, /) -> None:
        self.current = current

    def __call__(self, match: _rx.Match[str], /) -> str:
        if (sep := match.group(1)):
            return f"{self.current:,}".replace(",", sep)
        return str(self.current)


class _ProgressBarTotalReplacer:
    """Internal, callable class to replace `{total}` placeholder with formatted number."""

    def __init__(self, total: int, /) -> None:
        self.total = total

    def __call__(self, match: _rx.Match[str], /) -> str:
        if (sep := match.group(1)):
            return f"{self.total:,}".replace(",", sep)
        return str(self.total)


class _ProgressBarPercentageReplacer:
    """Internal, callable class to replace `{percentage}` placeholder with formatted float."""

    def __init__(self, percentage: float, /) -> None:
        self.percentage = percentage

    def __call__(self, match: _rx.Match[str], /) -> str:
        return f"{self.percentage:.{match.group(1) if match.group(1) else '1'}f}"


class Throbber:
    """A terminal throbber for indeterminate processes with customizable appearance.<br>
    This class intercepts stdout to allow printing while the animation is active.\n
    ------------------------------------------------------------------------------------------------
    *   `label` – The current label text.
    *   `throbber_format` – The format string used to render the throbber, containing placeholders:
        -   `{label}` `{l}`
        -   `{animation}` `{a}`
    *   `frames` – A tuple of strings representing the animation frames.
    *   `interval` – The time in seconds between each animation frame.
    ------------------------------------------------------------------------------------------------
    The `throbber_format` can additionally be formatted with special formatting codes. For more<br>
    detailed information about formatting codes, see the `format_codes` module documentation."""

    def __init__(
        self,
        *,
        label: Optional[str] = None,
        throbber_format: list[str] | tuple[str, ...] = ["{l}", "[b]({a}) "],
        sep: str = " ",
        frames: tuple[str, ...] = ("·  ", "·· ", "···", " ··", "  ·", "  ·", " ··", "···", "·· ", "·  "),
        interval: float = 0.2,
    ):
        self.throbber_format: list[str] | tuple[str, ...]
        """The format strings used to render the throbber (joined by `sep`)."""
        self.sep: str
        """The separator string used to join multiple throbber-format strings."""
        self.frames: tuple[str, ...]
        """A tuple of strings representing the animation frames."""
        self.interval: float
        """The time in seconds between each animation frame."""
        self.label: Optional[str]
        """The current label text."""
        self.active: bool = False
        """Whether the throbber is currently active (intercepting stdout) or not."""

        self.update_label(label)
        self.set_format(throbber_format, sep=sep)
        self.set_frames(frames)
        self.set_interval(interval)

        self._buffer: list[str] = []
        self._original_stdout: Optional[TextIO] = None
        self._current_animation_str: str = ""
        self._last_line_len: int = 0
        self._frame_index: int = 0
        self._stop_event: Optional[_threading.Event] = None
        self._animation_thread: Optional[_threading.Thread] = None

    def set_format(self, throbber_format: list[str] | tuple[str, ...], *, sep: Optional[str] = None) -> None:
        """Set the format string used to render the throbber.\n
        -------------------------------------------------------------------------------------------------
        *   `throbber_format` – The format strings used to render the throbber, containing placeholders:
            -   `{label}` `{l}`
            -   `{animation}` `{a}`
        *   `sep` – The separator string used to join multiple format strings."""

        if not any(_PATTERNS.animation.search(fmt) for fmt in throbber_format):
            raise ValueError(
                f"At least one format string in 'throbber_format' must contain the '{{animation}}' or '{{a}}' placeholder, got {throbber_format!r}"
            )

        self.throbber_format = throbber_format
        self.sep = sep or self.sep

    def set_frames(self, frames: tuple[str, ...], /) -> None:
        """Set the frames used for the throbber animation.\n
        ------------------------------------------------------------------------
        *   `frames` – A tuple of strings representing the animation frames."""

        if len(frames) < 2:
            raise ValueError(f"The 'frames' parameter must contain at least two frames, got {frames!r}")

        self.frames = frames

    def set_interval(self, interval: int | float, /) -> None:
        """Set the time interval between each animation frame.\n
        ----------------------------------------------------------------------
        *   `interval` – The time in seconds between each animation frame."""

        if interval <= 0:
            raise ValueError(f"The 'interval' parameter must be a positive number, got {interval!r}")

        self.interval = interval

    def start(self, label: Optional[str] = None, /) -> None:
        """Start the throbber animation and intercept stdout.\n
        --------------------------------------------------------------
        *   `label` – The label to display alongside the throbber."""

        if self.active:
            return

        self.label = label or self.label
        self._start_intercepting()
        self._stop_event = _threading.Event()
        self._animation_thread = _threading.Thread(target=self._animation_loop, daemon=True)
        self._animation_thread.start()

    def stop(self) -> None:
        """Stop and hide the throbber and restore normal terminal output."""

        if self.active:
            if self._stop_event:
                self._stop_event.set()
            if self._animation_thread:
                self._animation_thread.join()

            self._stop_event = None
            self._animation_thread = None
            self._frame_index = 0

            self._clear_throbber_line()
            self._stop_intercepting()

    def update_label(self, label: Optional[str], /) -> None:
        """Update the throbber's label text.\n
        -----------------------------------------
        *   `new_label` – The new label text."""

        self.label = label

    @contextmanager
    def context(self, label: Optional[str] = None, /) -> Generator[Callable[[str], None], None, None]:
        """Context manager for automatic cleanup. Returns a function to update the label.\n
        ------------------------------------------------------------------------------------
        *   `label` – The label to display alongside the throbber.
        ------------------------------------------------------------------------------------
        The returned callable accepts a single parameter:
        *   `new_label` – The new label text.

        #### Example usage:
        ```python
        with Throbber().context("Starting...") as update_label:
            time.sleep(2)
            update_label("Processing...")
            time.sleep(3)
            update_label("Finishing...")
            time.sleep(2)
        ```"""

        try:
            self.start(label)
            yield self.update_label
        except Exception:
            self._emergency_cleanup()
            raise
        finally:
            self.stop()

    def _animation_loop(self) -> None:
        """The internal thread target that runs the animation loop."""

        self._frame_index = 0
        while self._stop_event and not self._stop_event.is_set():
            try:
                if not self.active or not self._original_stdout:
                    break

                self._flush_buffer()

                frame = FormatCodes.to_ansi(f"{self.frames[self._frame_index % len(self.frames)]}[*]")
                formatted = FormatCodes.to_ansi(self.sep.join(
                    fmt_part for part in self.throbber_format if \
                    (fmt_part := _PATTERNS.animation.sub(frame, _PATTERNS.label.sub(self.label or "", part)))
                ))

                self._current_animation_str = formatted
                self._last_line_len = len(formatted)
                self._redraw_display()
                self._frame_index += 1

            except Exception:
                self._emergency_cleanup()
                break

            if self._stop_event:
                self._stop_event.wait(self.interval)

    def _start_intercepting(self) -> None:
        self.active = True
        self._original_stdout = _sys.stdout
        _sys.stdout = _InterceptedOutput(self)

    def _stop_intercepting(self) -> None:
        if self._original_stdout:
            _sys.stdout = self._original_stdout
            self._original_stdout = None
        self.active = False
        self._buffer.clear()
        self._last_line_len = 0
        self._current_animation_str = ""

    def _emergency_cleanup(self) -> None:
        """Emergency cleanup to restore stdout in case of exceptions."""

        try:
            self._stop_intercepting()
        except Exception:
            pass

    def _clear_throbber_line(self) -> None:
        if self._last_line_len > 0 and self._original_stdout:
            self._original_stdout.write(f"{ANSI.CHAR}[2K\r")
            self._original_stdout.flush()

    def _flush_buffer(self) -> None:
        if self._buffer and self._original_stdout:
            self._clear_throbber_line()
            for content in self._buffer:
                self._original_stdout.write(content)
                self._original_stdout.flush()
            self._buffer.clear()

    def _redraw_display(self) -> None:
        if self._current_animation_str and self._original_stdout:
            self._original_stdout.write(f"{ANSI.CHAR}[2K\r{self._current_animation_str}")
            self._original_stdout.flush()


@mypyc_attr(native_class=False)
class _InterceptedOutput:
    """Custom StringIO that captures output and stores it in the progress bar buffer."""

    def __init__(self, status_indicator: ProgressBar | Throbber, /):
        self.status_indicator = status_indicator
        self.string_io = StringIO()

    def write(self, content: str, /) -> int:
        self.string_io.write(content)
        try:
            if content and content != "\r":
                self.status_indicator._buffer.append(content)
            return len(content)
        except Exception:
            self.status_indicator._emergency_cleanup()
            raise

    def flush(self) -> None:
        self.string_io.flush()
        try:
            if self.status_indicator.active and self.status_indicator._buffer:
                self.status_indicator._flush_buffer()
                self.status_indicator._redraw_display()
        except Exception:
            self.status_indicator._emergency_cleanup()
            raise

    def __getattr__(self, name: str, /) -> Any:
        return getattr(self.string_io, name)
