"""
Provides comprehensive tools for terminal output and interaction.

Features include styled logging, progress bars, interactive prompts,
and command-line argument parsing.
"""

from . import color as _color_module
from . import string as _string_module
from .ansi import AnyStyle, BaseStyle, ColorStyle, S, StyledText, TextRenderable, is_any_style, is_text_renderable
from .base.consts import ANSI, CHARS
from .base.decorators import mypyc_attr
from .base.types import AllTextChars, Hexa, ProgressUpdater, Rgba
from .regex import LazyRegex

import ctypes as _ctypes
import getpass as _getpass
import os as _os
import shutil as _shutil
import subprocess as _subprocess
import sys as _sys
import threading as _threading
import time as _time
from collections.abc import Callable, Generator, Iterable
from contextlib import contextmanager, suppress
from itertools import chain
from pathlib import Path
from typing import Any, Final, Literal, NoReturn, TextIO, TypedDict, cast, overload
import prompt_toolkit as _pt
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import ValidationError, Validator

_PATTERNS: Final[LazyRegex] = LazyRegex(
    flag_prefix=r"^[\W_]+",
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

_LOG_TITLE_CACHE: dict[tuple[str, str], str] = {}
"""Cache of rendered log-title ANSI strings, keyed by `(padded_title, style_repr)`."""
_LOG_TITLE_CACHE_MAX: Final[int] = 256
"""Maximum number of entries kept in `_LOG_TITLE_CACHE`."""

_ANSI_RESET: Final[str] = StyledText(S.RESET).ansi
"""The ANSI full-reset sequence (`ESC[0m`)."""

_DEFAULT_BAR_FORMAT: Final[list[TextRenderable]] = [
    "{l}",
    (S.BR.MAGENTA | S.BG.BLACK)("{b}"),
    (S.BOLD("{c:,}"), "/{t:,}"),
    (S.DIM | S.BR.MAGENTA)("(", S.ITALIC("{p}%"), ")"),
]
"""Default `ProgressBar` format, styled with the operator-based API."""
_DEFAULT_LIMITED_BAR_FORMAT: Final[list[TextRenderable]] = ["{l}", (S.BR.MAGENTA | S.BG.BLACK)("{b}")]
"""Default simplified `ProgressBar` format used when the terminal is too narrow."""
_DEFAULT_THROBBER_FORMAT: Final[list[TextRenderable]] = [S.BR.MAGENTA("{a}"), "{l}"]
"""Default `Throbber` format, styled with the operator-based API."""

# fmt: off
FRAMES_STANDARD: Final[tuple[str, ...]] = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
"""Throbber `frames` preset: A standard, clean, and modern Braille circular spinner."""
FRAMES_WINDMILL: Final[tuple[str, ...]] = ("⠓⠆", "⠳⠄", "⠹⠄", "⠽ ", "⠼⠁", "⠞⠁", "⠖⠃", "⠓⠃", "⠓⠆", "⠙⠆", "⠹⠄", "⠸⠅", "⠼⠁", "⠴⠃", "⠖⠃", "⠖⠆")  # ruff:ignore[line-too-long]
"""Throbber `frames` preset: A wide, dual-character Braille windmill animation."""
# fmt: on


def _compile_format(fmt: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable) -> list[str]:
    """Internal function to compile a format specification into a list of ANSI strings."""

    if isinstance(fmt, (list, tuple)):
        return [StyledText(part).ansi if not isinstance(part, str) else part for part in fmt]

    return [StyledText(fmt).ansi if not isinstance(fmt, str) else fmt]


def _to_styled_text(obj: TextRenderable | object) -> StyledText:
    """Internal function to convert an object into a `StyledText` instance."""

    if isinstance(obj, StyledText):
        return obj
    elif is_text_renderable(obj):
        return StyledText(*obj) if isinstance(obj, tuple) else StyledText(obj)

    return StyledText(str(obj))


class ArgConfigDict(TypedDict):
    """Configuration dictionary for an argument/flag."""

    flags_or_pos: set[str] | frozenset[str] | Literal["before", "after"]
    expects_value: str | bool
    choices: Iterable[str] | None
    required: bool
    description: TextRenderable | None


class ParsedArgData:
    """Represents the result of a parsed command-line argument.\n
    ------------------------------------------------------------------------------------------------------------
    *   `exists` – Whether the argument was found in the command-line input or not.
    *   `is_pos` – Whether the argument is a positional `"before"`/`"after"` argument or not.
    *   `values` – The tuple of values associated with the argument.
    *   `flag` – The specific flag that was found (e.g., `-v`, `-vv`, `-vvv`), or `None` for positional args.\n
    ------------------------------------------------------------------------------------------------------------
    When the `ParsedArgData` instance is accessed as a boolean it will correspond to the `exists` attribute."""

    def __init__(
        self,
        exists: bool = False,
        values: tuple[str, ...] = (),
        is_pos: bool = False,
        flag: str | None = None,
    ) -> None:
        self.exists: bool = exists
        """Whether the argument was found in the command-line input or not."""
        self.values: tuple[str, ...] = values
        """The tuple of values associated with the argument."""
        self.is_pos: bool = is_pos
        """Whether the argument is a positional `"before"`/`"after"` argument or not."""
        self.flag: str | None = flag
        """The specific flag that was found (e.g., `-v`, `-vv`, `-vvv`), or `None` for positional args."""

    @overload
    def val(self) -> str | None: ...
    @overload
    def val[D](self, *, default: D) -> str | D: ...
    @overload
    def val[T](self, cast_type: Callable[[str], T] | type[T], default: None = None) -> T | None: ...
    @overload
    def val[T, D](self, cast_type: Callable[[str], T] | type[T], default: D) -> T | D: ...

    def val(
        self,
        cast_type: Callable[[str], Any] | type[Any] = str,
        default: Any = None,
    ) -> Any:
        """Get the parsed value, optionally casting it to a specified type and providing a fallback default.\n
        -------------------------------------------------------------------------------------------------------
        *   `cast_type` – The type to cast to (e.g., `int`, `Path`, …).
        *   `default` – The fallback value if `exists` is false or if no values exist.\n
        -------------------------------------------------------------------------------------------------------
        Raises a `ValueError` if the value cannot be cast to the specified type."""

        if not self.exists or not self.values:
            return default

        try:
            return cast_type(self.values[0])
        except Exception as exc:
            raise ValueError(f"Failed to cast value '{self.values[0]}' to {cast_type}") from exc

    @overload
    def vals(self) -> tuple[str, ...]: ...
    @overload
    def vals[D](self, *, default: D) -> tuple[str, ...] | D: ...
    @overload
    def vals[T](self, cast_type: Callable[[str], T] | type[T], default: tuple[()] = ()) -> tuple[T, ...]: ...
    @overload
    def vals[T, D](self, cast_type: Callable[[str], T] | type[T], default: D) -> tuple[T, ...] | D: ...

    def vals(
        self,
        cast_type: Callable[[str], Any] | type[Any] = str,
        default: Any = (),
    ) -> Any:
        """Get all parsed values, optionally casting them to a specified type and providing a fallback default.\n
        ----------------------------------------------------------------------------------------------------------
        *   `cast_type` – The type to cast to (e.g., `int`, `Path`, …).
        *   `default` – The fallback value if `exists` is false or if no values exist.\n
        ----------------------------------------------------------------------------------------------------------
        Raises a `ValueError` if any value cannot be cast to the specified type."""

        if not self.exists or not self.values:
            return default

        current_val: Any = None

        try:
            return tuple([cast_type(current_val := val) for val in self.values])
        except Exception as exc:
            raise ValueError(f"Failed to cast value '{current_val}' to {cast_type}") from exc

    def __bool__(self) -> bool:
        return self.exists

    def __str__(self) -> str:
        if not self.exists:
            return ""
        return " ".join(self.values)

    def __repr__(self) -> str:
        return f"ParsedArgData(exists={self.exists}, values={self.values}, is_pos={self.is_pos}, flag={self.flag!r})"


class ParsedArgs:
    """Container for the result of `ArgumentParser.parse()`.\n
    -------------------------------------------------------------------------------
    *   `unknown_flags` – Any arguments that were not recognized by the parser."""

    def __init__(self) -> None:
        self.unknown_flags: list[str] = []
        """Any arguments that were not recognized by the parser."""

        self._args: dict[str, ParsedArgData] = {}

    def _add_arg(self, alias: str, data: ParsedArgData) -> None:
        """Internal method to add a parsed argument to the container."""

        self._args[alias] = data

    def __getattr__(self, name: str) -> ParsedArgData:
        try:
            return self._args[name]
        except KeyError as exc:
            raise AttributeError(f"'ParsedArgs' object has no attribute '{name}'") from exc

    def __repr__(self) -> str:
        return f"ParsedArgs(unknown_flags={self.unknown_flags}, args={self._args})"


class ArgumentParser:
    """An advanced command-line argument parser with built-in help generation and validation.\n
    -----------------------------------------------------------------------------------------------------------
    *   `title` – An optional title for the help print (e.g., `"CLI Tool"`).
    *   `subtitle` – An optional subtitle (e.g., `"A simple command-line utility"`).
    *   `usage` – An optional explicit usage string, containing placeholders:
        -   `{cmd}` – The command name (e.g., `cli-tool`).
        -   `{pos_before}` – The `"before"` positional argument placeholder (e.g., `<input>`).
        -   `{opts}` – The options placeholder (`[options]`).
        -   `{pos_after}` – The `"after"` positional argument placeholder (e.g., `<output>`).
    *   `examples` – A list of tuples `(example_command, description)`.
    *   `epilog` – Optional footer text to append to the help print.
    *   `help_flags` – A set of flags that trigger the help print (default: `{"-h", "--help"}`)."""

    def __init__(
        self,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        usage: TextRenderable | str | None = None,
        controls: list[tuple[str, TextRenderable]] | None = None,
        examples: list[tuple[str, TextRenderable]] | None = None,
        epilog: TextRenderable | object | None = None,
        help_flags: set[str] | frozenset[str] = frozenset({"-h", "--help"}),
    ) -> None:

        self.title: str | None = title
        """An optional title for the help print (e.g., `"CLI Tool"`)."""
        self.subtitle: str | None = subtitle
        """An optional subtitle (e.g., `"A simple command-line utility"`)."""
        self.usage: TextRenderable | str | None = usage
        """An optional explicit usage string."""
        self.controls: list[tuple[str, TextRenderable]] | None = controls
        """A list of tuples `(control_key, description)`."""
        self.examples: list[tuple[str, TextRenderable]] | None = examples
        """A list of tuples `(example_command, description)`."""
        self.epilog: TextRenderable | object | None = epilog
        """Optional footer text to append to the help print."""
        self.help_flags: frozenset[str] = frozenset(help_flags)
        """A set of flags that trigger the help print."""

        self._arg_configs: dict[str, ArgConfigDict] = {}

    @overload
    def add_arg(
        self,
        alias: str,
        flags_or_pos: Literal["before", "after"],
        /,
        *,
        expects_value: str = ...,
        choices: Iterable[str] | None = None,
        required: bool = False,
        description: TextRenderable | None = None,
    ) -> None: ...
    @overload
    def add_arg(
        self,
        alias: str,
        flags_or_pos: set[str] | frozenset[str],
        /,
        *,
        expects_value: str | bool = False,
        choices: Iterable[str] | None = None,
        required: bool = False,
        description: TextRenderable | None = None,
    ) -> None: ...

    def add_arg(
        self,
        alias: str,
        flags_or_pos: set[str] | frozenset[str] | Literal["before", "after"],
        /,
        *,
        expects_value: str | bool = False,
        choices: Iterable[str] | None = None,
        required: bool = False,
        description: TextRenderable | None = None,
    ) -> None:
        """Define a new argument/flag to parse.\n
        ---------------------------------------------------------------------------------------------
        *   `alias` – The attribute name to access the parsed values in the `ParsedArgs` object.
        *   `flags_or_pos` – A set of flags (e.g., `{"-f", "--flag"}`),<br>
            or the literal `"before"` or `"after"` to capture positional values.
        *   `description` – Help text describing the argument.
        *   `expects_value` – `False` for a boolean flag, `True` for a value flag (shows `VAL`),<br>
            or a string (e.g., `"PATH"`) for a specific placeholder.
        *   `choices` – Optional iterable of allowed strings for this argument's value.
        *   `required` – *bool*, `True` if the argument must be provided."""

        if isinstance(flags_or_pos, str):
            if flags_or_pos not in {"before", "after"}:
                raise ValueError("Positional argument must be 'before' or 'after'")
            if isinstance(expects_value, bool) and not expects_value:
                expects_value = "VAL"

        else:
            if overlap := set(flags_or_pos).intersection(self.help_flags):
                raise ValueError(f"Argument flags {overlap} overlap with help flags.")

            for existing_cfg in self._arg_configs.values():
                if isinstance(existing_cfg["flags_or_pos"], (set, frozenset)) and (
                    overlap := set(flags_or_pos).intersection(existing_cfg["flags_or_pos"])
                ):
                    raise ValueError(f"Argument flags {overlap} overlap with an existing argument.")

        self._arg_configs[alias] = {
            "flags_or_pos": frozenset(flags_or_pos) if isinstance(flags_or_pos, (set, frozenset)) else flags_or_pos,
            "expects_value": expects_value,
            "choices": choices,
            "required": required,
            "description": description,
        }

    def _flags_to_st(self, flags: Iterable[str]) -> StyledText:
        """Internal method to convert a set of flags into a nicely formatted `StyledText` object for help printing."""

        return StyledText(", ").join(
            S.BR.BLUE(flag)
            for flag in sorted(flags, key=lambda flg: (len(flg) - len(_PATTERNS.flag_prefix.sub("", flg)), flg))
        )

    def _add_title_to_help_output(self, output: list[TextRenderable], console_width: int) -> None:
        """Internal method to add the title and subtitle to the help output."""

        if self.title:
            title: TextRenderable
            box_w: int

            if self.subtitle:
                title = (S.BOLD(self.title), f" — {self.subtitle}")
                box_w = len(self.title) + len(self.subtitle) + 7
            else:
                title = S.BOLD(self.title)
                box_w = len(self.title) + 4

            output.extend(["▄" * box_w, (S.INVERSE | S.BG.BLACK)("  ", title, "  "), "▀" * box_w, ""])

    def _add_usage_to_help_output(
        self,
        output: list[TextRenderable],
        cmd_st: StyledText,
        before_pos_st: StyledText,
        after_pos_st: StyledText,
        opts_st: StyledText,
    ) -> None:
        """Internal method to add the usage line to the help output."""

        if self.usage is None:
            output.append(StyledText(" ").join((S.BOLD("Usage:"), cmd_st, before_pos_st, opts_st, after_pos_st)))
        else:
            output.append(
                (self.usage if isinstance(self.usage, StyledText) else StyledText(self.usage))
                .ansi.replace("{cmd}", cmd_st.ansi)
                .replace("{pos_before}", before_pos_st.ansi)
                .replace("{opts}", opts_st.ansi)
                .replace("{pos_after}", after_pos_st.ansi)
            )

        output.append("")

    def _add_args_to_help_output(
        self,
        output: list[TextRenderable],
        before_pos: str | None,
        after_pos: str | None,
        pos_before_st: StyledText,
        pos_after_st: StyledText,
    ) -> None:
        """Internal method to add the positional arguments section to the help output."""

        if before_pos or after_pos:
            output.append(S.BOLD("Arguments:"))

            if before_pos:
                output.append((f"  {pos_before_st.ansi} ", self._arg_configs[before_pos]["description"] or ""))
            if after_pos:
                output.append((f"  {pos_after_st.ansi} ", self._arg_configs[after_pos]["description"] or ""))

            output.append("")

    def _add_opts_to_help_output(self, output: list[TextRenderable], has_opts: bool) -> None:
        """Internal method to add the options section to the help output."""

        if not has_opts and not self.help_flags:
            return

        output.append(S.BOLD("Options:"))

        opts_list: list[tuple[StyledText, TextRenderable]] = []
        opts_list.append((self._flags_to_st(self.help_flags), "Show this help message and exit"))

        for _, cfg in self._arg_configs.items():
            if isinstance(cfg["flags_or_pos"], (set, frozenset)):
                flag_st = self._flags_to_st(cfg["flags_or_pos"])

                if cfg["expects_value"] is not False:
                    flag_st += S.BR.BLUE(S.DIM("="), "VAL" if cfg["expects_value"] is True else str(cfg["expects_value"]))

                opts_list.append((flag_st, cfg["description"] or ""))

        max_flag_len = max([len(flag_st.raw) for flag_st, _ in opts_list], default=0)

        for flag_st, desc in opts_list:
            output.append(("  ", flag_st, " " * (max_flag_len - len(flag_st.raw)), "    ", desc))

        output.append("")

    def _add_controls_to_help_output(self, output: list[TextRenderable]) -> None:
        """Internal method to add the controls section to the help output."""

        if self.controls:
            output.append(S.BOLD("Controls:"))

            max_ctrl_len = max([len(control_key) for control_key, _ in self.controls], default=0)

            for ctrl, desc in self.controls:
                styled_ctrl = S.BR.RED(S.DIM("+").join(ctrl.split("+")))
                output.append(("  ", styled_ctrl, " " * (max_ctrl_len - len(ctrl)), "    ", desc))

            output.append("")

    def _add_examples_to_help_output(self, output: list[TextRenderable], cmd_name_ext: tuple[str, str]) -> None:
        """Internal method to add the examples section to the help output."""

        if self.examples:
            output.append(S.BOLD("Examples:"))

            for ex, desc in self.examples:
                output.append((
                    f"  {ex.replace('{cmd}', StyledText(S.BR.GREEN(cmd_name_ext[0])).ansi)}    ",
                    S.DIM("# ", S.ITALIC(desc)),
                ))

            output.append("")

    def print_help(self, error_message: str | None = None) -> None:
        """Print the generated help screen.\n
        -------------------------------------------------------------------------------
        *   `error_message` – An optional error message to print at the top in red."""

        before_pos: str | None = None
        after_pos: str | None = None

        for alias, cfg in self._arg_configs.items():
            if cfg["flags_or_pos"] == "before":
                before_pos = alias
            elif cfg["flags_or_pos"] == "after":
                after_pos = alias

        cmd_exe = Path(_sys.argv[0])
        cmd_name_ext: tuple[str, str] = (cmd_exe.stem, cmd_exe.suffix)

        has_opts = False
        for cfg in self._arg_configs.values():
            if isinstance(cfg["flags_or_pos"], (set, frozenset)):
                has_opts = True
                break

        cmd_st = StyledText(S.BR.GREEN(cmd_name_ext[0], S.DIM(cmd_name_ext[1]) if cmd_name_ext[1] else ""))
        before_pos_st = StyledText(S.BR.CYAN(f"<{before_pos}>") if before_pos else "")
        after_pos_st = StyledText(S.BR.CYAN(f"<{after_pos}>") if after_pos else "")
        opts_st = StyledText(S.BR.BLUE("[options]") if has_opts else "")

        console_width = get_width()
        output: list[TextRenderable] = [""]

        if error_message:
            output.extend([S.RED(S.BOLD("[ERROR] ")), error_message, ""])

        self._add_title_to_help_output(output, console_width)
        self._add_usage_to_help_output(output, cmd_st, before_pos_st, after_pos_st, opts_st)
        self._add_args_to_help_output(output, before_pos, after_pos, before_pos_st, after_pos_st)
        self._add_opts_to_help_output(output, has_opts)
        self._add_controls_to_help_output(output)
        self._add_examples_to_help_output(output, cmd_name_ext)

        if self.epilog:
            output.append(self.epilog if isinstance(self.epilog, StyledText) else str(self.epilog))
            output.append("")

        StyledText(*output, sep="\n").print(flush=True)

    def _build_flag_map(self) -> dict[str, str]:
        """Internal method to build a mapping of flags to their corresponding argument aliases."""

        flag_map: dict[str, str] = {}

        for alias, cfg in self._arg_configs.items():
            if isinstance(cfg["flags_or_pos"], (set, frozenset)):
                for flag in cast("Iterable[str]", cfg["flags_or_pos"]):
                    flag_map[flag] = alias

        return flag_map

    def _parse_args_loop(
        self,
        raw_args: list[str],
        flag_map: dict[str, str],
        parsed_data: dict[str, dict[str, Any]],
        unknown_flags: list[str],
        positional_values: list[str],
        flag_value_sep: str | None,
        allow_space_value: bool,
    ) -> None:
        """Internal method to loop through the raw arguments and populate the parsed data."""

        i = 0

        while i < len(raw_args):
            arg = raw_args[i]

            if flag_value_sep and flag_value_sep in arg:
                parts = arg.split(flag_value_sep, 1)
                potential_flag, potential_val = parts[0], parts[1]
            else:
                potential_flag, potential_val = arg, None

            if potential_flag in self.help_flags:
                self.print_help()
                raise SystemExit(0)

            if potential_flag in flag_map:
                alias = flag_map[potential_flag]
                cfg = self._arg_configs[alias]
                parsed_data[alias]["exists"] = True
                parsed_data[alias]["flag"] = potential_flag

                if cfg["expects_value"]:
                    if potential_val is not None:
                        parsed_data[alias]["values"].append(potential_val)
                    elif (
                        allow_space_value
                        and i + 1 < len(raw_args)
                        and raw_args[i + 1] not in flag_map
                        and raw_args[i + 1] not in self.help_flags
                    ):
                        parsed_data[alias]["values"].append(raw_args[i + 1])
                        i += 1
                    else:
                        self.print_help(f"Argument '{potential_flag}' requires a value.")
                        raise SystemExit(1)

            elif arg.startswith("-"):
                unknown_flags.append(arg)
            else:
                positional_values.append(arg)

            i += 1

    def _resolve_positionals(
        self,
        parsed_data: dict[str, dict[str, Any]],
        positional_values: list[str],
        unknown_flags: list[str],
    ) -> None:
        """Internal method to resolve positional arguments and assign them to the appropriate aliases."""

        before_pos = None
        after_pos = None
        for alias, cfg in self._arg_configs.items():
            if cfg["flags_or_pos"] == "before":
                before_pos = alias
            elif cfg["flags_or_pos"] == "after":
                after_pos = alias

        if before_pos and positional_values:
            parsed_data[before_pos]["exists"] = True
            parsed_data[before_pos]["values"].append(positional_values.pop(0))
            parsed_data[before_pos]["is_pos"] = True

        if after_pos and positional_values:
            parsed_data[after_pos]["exists"] = True
            parsed_data[after_pos]["values"].extend(positional_values)
            parsed_data[after_pos]["is_pos"] = True
            positional_values.clear()

        if positional_values:
            unknown_flags.extend(positional_values)

    def _validate_parsed_data(self, parsed_data: dict[str, dict[str, Any]]) -> None:
        """Internal method to validate the parsed data against the argument configurations."""

        for alias, cfg in self._arg_configs.items():
            if cfg["required"] and not parsed_data[alias]["exists"]:
                if isinstance(cfg["flags_or_pos"], (set, frozenset)):
                    flag_str = f" ({'/'.join(cast('Iterable[str]', cfg['flags_or_pos']))})"
                else:
                    flag_str = f" (positional {cfg['flags_or_pos']})"

                self.print_help(f"Missing required argument: {alias}{flag_str}")
                raise SystemExit(1)

            if cfg["choices"] and parsed_data[alias]["exists"]:
                for val in parsed_data[alias]["values"]:
                    if val not in cfg["choices"]:
                        self.print_help(f"Invalid choice '{val}' for argument '{alias}'. Allowed: {', '.join(cfg['choices'])}")
                        raise SystemExit(1)

    def parse(self, *, skip: int = 0, flag_value_sep: str | None = "=", allow_space_value: bool = True) -> ParsedArgs:
        """Parse `sys.argv` and return the strongly-typed `ParsedArgs` object.\n
        ---------------------------------------------------------------------------------------------------
        *   `skip` – Number of arguments to skip at the start.
        *   `flag_value_sep` – String separating flag from value (e.g., `"="` for `--foo=bar`).<br>
            Set to `None` to disable.
        *   `allow_space_value` – Whether to allow space-separated values for flags (e.g., `--foo bar`).\n
        ---------------------------------------------------------------------------------------------------
        Returns the `ParsedArgs` container."""

        raw_args = _sys.argv[1 + skip :]
        result = ParsedArgs()

        for flag in self.help_flags:
            if flag in raw_args:
                self.print_help()
                raise SystemExit(0)

        flag_map = self._build_flag_map()
        parsed_data: dict[str, dict[str, Any]] = {
            alias: {"exists": False, "values": [], "is_pos": False, "flag": None} for alias in self._arg_configs
        }
        unknown_flags: list[str] = []
        positional_values: list[str] = []

        self._parse_args_loop(
            raw_args, flag_map, parsed_data, unknown_flags, positional_values, flag_value_sep, allow_space_value
        )
        self._resolve_positionals(parsed_data, positional_values, unknown_flags)
        self._validate_parsed_data(parsed_data)

        result.unknown_flags = unknown_flags
        for alias, data in parsed_data.items():
            result._add_arg(
                alias,
                ParsedArgData(exists=data["exists"], values=tuple(data["values"]), is_pos=data["is_pos"], flag=data["flag"]),
            )

        return result


def get_width() -> int:
    """The terminal width in characters."""

    try:
        return _os.get_terminal_size().columns
    except OSError:
        return 80


def get_height() -> int:
    """The terminal height in lines."""

    try:
        return _os.get_terminal_size().lines
    except OSError:
        return 24


def get_size() -> tuple[int, int]:
    """A tuple with the terminal width and height in characters and lines."""

    try:
        size = _os.get_terminal_size()
        return (size.columns, size.lines)
    except OSError:
        return (80, 24)


def get_user() -> str:
    """The name of the current user."""

    return _os.getenv("USER") or _os.getenv("USERNAME") or _getpass.getuser()


def is_tty() -> bool:
    """Whether the terminal is connected to a TTY or not."""

    return _sys.stdout.isatty()


def get_encoding() -> str:
    """The encoding used by the terminal (e.g., `utf-8`, `cp1252`, …)."""

    try:
        encoding = _sys.stdout.encoding
        return "utf-8" if encoding is None else encoding
    except (AttributeError, Exception):
        return "utf-8"


def supports_color() -> bool:
    """Whether the terminal supports ANSI color codes or not."""

    if not is_tty():
        return False

    if _os.name == "nt":
        # Check if VT100 mode is enabled on Windows:
        with suppress(Exception):
            kernel32 = _ctypes.windll.kernel32  # type: ignore
            handle = kernel32.GetStdHandle(-11)  # type: ignore
            mode = _ctypes.c_ulong()  # type: ignore

            if kernel32.GetConsoleMode(handle, _ctypes.byref(mode)):  # type: ignore
                return (mode.value & 0x0004) != 0

        return False

    return _os.getenv("TERM", "").lower() not in {"", "dumb"}


@overload
def pause_exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    pause: bool = ...,
    exit: Literal[True],
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> NoReturn: ...
@overload
def pause_exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    pause: bool = ...,
    exit: Literal[False] = ...,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...
@overload
def pause_exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...


def pause_exit(
    prompt: TextRenderable | object = "",
    /,
    *,
    pause: bool = True,
    exit: bool = False,
    exit_code: int = 0,
    reset_ansi: bool = False,
) -> None:
    """Will print the `prompt` and then pause and/or exit the program based on the given options.\n
    -----------------------------------------------------------------------------------------------------
    *   `prompt` – The message to print before pausing/exiting (any object, or a `StyledText` object).
    *   `pause` – Whether to pause and wait for a key press after printing the prompt.
    *   `exit` – Whether to exit the program after printing the prompt (and pausing if `pause` is true).
    *   `exit_code` – The exit code to use when exiting the program.
    *   `reset_ansi` – Whether to reset the ANSI formatting after printing the prompt."""

    styled = _to_styled_text(prompt)
    if reset_ansi:
        styled += StyledText(S.RESET)

    styled.print(end="", flush=True)

    if pause:
        _read_single_key()
    if exit:
        raise SystemExit(exit_code)


def cls() -> None:
    """Will clear the terminal in addition to completely resetting the ANSI formats."""

    if _shutil.which("cls"):
        _subprocess.run(["cls"])
    elif _shutil.which("clear"):
        _subprocess.run(["clear"])
    print("\033[0m", end="", flush=True)


def log(
    title: str | None = None,
    prompt: TextRenderable | object = "",
    /,
    *,
    start: str = "",
    end: str = "\n",
    title_bg_color: BaseStyle | Rgba | Hexa | None = None,
    default_color: ColorStyle | Rgba | Hexa | None = None,
    tab_size: int = 8,
    title_px: int = 1,
    title_mx: int = 2,
) -> None:
    """Prints a nicely formatted log message.\n
    ----------------------------------------------------------------------------------------------
    *   `title` – The title of the log message (e.g., `DEBUG`, `WARN`, `FAIL`, …).
    *   `prompt` – The log message (any object, or a `StyledText` object for styled output).
    *   `start` – Something to print before the log is printed.
    *   `end` – Something to print after the log is printed (e.g., `\\n`).
    *   `title_bg_color` – The background color of the `title`<br>
        (an `S` background style, RGBA, or HEXA color).
    *   `default_color` – The default text color of the `prompt` (RGBA or HEXA).
    *   `tab_size` – The tab size used for the log (default is 8 – matches terminal tabs).
    *   `title_px` – The horizontal padding (in chars) to the title (if `title_bg_color` is set).
    *   `title_mx` – The horizontal margin (in chars) to the title.
    ----------------------------------------------------------------------------------------------
    To style the `prompt`, pass a `StyledText` object. For more detailed<br>
    information about styling, see the `ansi` module documentation."""

    if tab_size < 0:
        raise ValueError(f"The 'tab_size' parameter must be a non-negative integer, got {tab_size!r}")
    if title_px < 0:
        raise ValueError(f"The 'title_px' parameter must be a non-negative integer, got {title_px!r}")
    if title_mx < 0:
        raise ValueError(f"The 'title_mx' parameter must be a non-negative integer, got {title_mx!r}")

    title = "" if title is None else title.strip()

    title_style: AnyStyle
    if title_bg_color is not None:
        bg_style, fg_style = _resolve_title_colors(title_bg_color)
        title_style = S.BOLD | fg_style | bg_style
    else:
        title_style = S.BOLD
        title_px = 0  # Remove padding if title has no BG color.

    # Padding = space inside title BG color
    # Margin = space outside title BG color
    px, mx = " " * title_px, " " * title_mx

    # Title length including padding and margin:
    title_len: int = len(title) + (title_px * 2) + (title_mx * 2)

    # Distance to next tab stop:
    tab: str = " " * (-title_len % tab_size)

    # Position where prompt needs to wrap to next line:
    wrap_len: int = get_width() - (title_len + len(tab))

    # Get the prompt's plain text and its ANSI codes with their (linebreak-independent) positions:
    clean_prompt = (prompt_st := _to_styled_text(prompt)).raw
    removals = tuple([(pos - clean_prompt.count("\n", 0, pos), seq) for pos, seq in prompt_st.raw_code_positions])

    # Split prompt into lines and then split each line into chunks that fit within the wrap length:
    prompt_lst: list[str] = list(chain.from_iterable(_process_lines(clean_prompt, wrap_len)))

    # Add back the removed ANSI codes to their original positions in the wrapped prompt:
    wrapped = f"\n{' ' * title_len}{tab}".join(_add_back_removed_parts(prompt_lst, removals))

    prompt_segment = _as_fg_style(default_color)(wrapped) if default_color is not None else wrapped

    if title == "":
        StyledText(f"{start}{mx}", prompt_segment, sep="").print(end=end)
    else:
        title_ansi = _render_log_title(f"{px}{title}{px}", title_style)
        StyledText(f"{start}{mx}", title_ansi, f"{mx}{tab}", prompt_segment, sep="").print(end=end)


def _log_preset(
    title: str,
    prompt: TextRenderable | object,
    title_bg_color: BaseStyle | Rgba | Hexa | None,
    start: str,
    end: str,
    default_color: ColorStyle | Rgba | Hexa | None,
    pause: bool,
    do_exit: bool,
    exit_code: int,
    reset_ansi: bool,
    /,
) -> None:
    log(title, prompt, start=start, end=end, title_bg_color=title_bg_color, default_color=default_color)
    pause_exit("", pause=pause, exit=do_exit, exit_code=exit_code, reset_ansi=reset_ansi)


def debug(
    prompt: TextRenderable | object = "Point in program reached.",
    /,
    *,
    active: bool = True,
    start: str = "",
    end: str = "\n",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 0,
    reset_ansi: bool = True,
) -> None:
    """A preset for `log()`: `DEBUG` log message with the options to pause<br>
    at the message and exit the program after the message was printed.\n
    If `active` is false, no debug message will be printed."""

    if active:
        _log_preset("DEBUG", prompt, S.BG.BR.YELLOW, start, end, default_color, pause, exit, exit_code, reset_ansi)


def info(
    prompt: TextRenderable | object = "Program running.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 0,
    reset_ansi: bool = True,
) -> None:
    """A preset for `log()`: `INFO` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("INFO", prompt, S.BG.BR.BLUE, start, end, default_color, pause, exit, exit_code, reset_ansi)


@overload
def done(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True],
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> NoReturn: ...
@overload
def done(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False] = ...,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...
@overload
def done(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...


def done(
    prompt: TextRenderable | object = "Program finished.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 0,
    reset_ansi: bool = True,
) -> None:
    """A preset for `log()`: `DONE` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("DONE", prompt, S.BG.BR.GREEN, start, end, default_color, pause, exit, exit_code, reset_ansi)


@overload
def warn(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True],
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> NoReturn: ...
@overload
def warn(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False] = ...,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...
@overload
def warn(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...


def warn(
    prompt: TextRenderable | object = "Important message.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 1,
    reset_ansi: bool = True,
) -> None:
    """A preset for `log()`: `WARN` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("WARN", prompt, S.BG.BR.YELLOW, start, end, default_color, pause, exit, exit_code, reset_ansi)


@overload
def fail(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True] = ...,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> NoReturn: ...
@overload
def fail(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False],
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...
@overload
def fail(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...


def fail(
    prompt: TextRenderable | object = "Program error.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = True,
    exit_code: int = 1,
    reset_ansi: bool = True,
) -> None:
    """A preset for `log()`: `FAIL` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("FAIL", prompt, S.BG.BR.RED, start, end, default_color, pause, exit, exit_code, reset_ansi)


@overload
def exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True] = ...,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> NoReturn: ...
@overload
def exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False],
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...
@overload
def exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: ColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
    reset_ansi: bool = ...,
) -> None: ...


def exit(
    prompt: TextRenderable | object = "Program ended.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = True,
    exit_code: int = 0,
    reset_ansi: bool = True,
) -> None:
    """A preset for `log()`: `EXIT` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    log("EXIT", prompt, start=start, end=end, title_bg_color=S.BG.BR.MAGENTA, default_color=default_color)
    pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)


def log_box_filled(
    *values: TextRenderable | object,
    start: str = "",
    end: str = "\n",
    box_bg_color: AnyStyle | Rgba | Hexa | None = None,
    default_color: ColorStyle | Rgba | Hexa | None = None,
    w_padding: int = 2,
    w_full: bool = False,
    indent: int = 0,
) -> None:
    """Will print a box with a colored background, containing a log message.\n
    --------------------------------------------------------------------------------------
    *   `*values` – The box content (any objects, or `StyledText` objects, one per line).
    *   `start` – Something to print before the log box is printed (e.g., `\\n`).
    *   `end` – Something to print after the log box is printed (e.g., `\\n`).
    *   `box_bg_color` – The background color of the box<br>
        (an `S` background style, RGBA, or HEXA color).
    *   `default_color` – The default text color of the `*values`.
    *   `w_padding` – The horizontal padding (in chars) to the box content.
    *   `w_full` – Whether to make the box be the full terminal width or not.
    *   `indent` – The indentation of the box (in chars).
    --------------------------------------------------------------------------------------
    To style the content, pass `StyledText` objects. For more detailed<br>
    information about styling, see the `ansi` module documentation."""

    if w_padding < 0:
        raise ValueError(f"The 'w_padding' parameter must be a non-negative integer, got {w_padding!r}")
    if indent < 0:
        raise ValueError(f"The 'indent' parameter must be a non-negative integer, got {indent!r}")

    fg_style = _as_fg_style(default_color, fallback="#000")

    # If no box BG color is set, use the console foreground color as the box BG (via inversion):
    bg_style: AnyStyle = (S.RESET_FG | S.INVERSE | fg_style) if box_bg_color is None else _as_bg_style(box_bg_color)

    open_seq = StyledText(fg_style | bg_style).ansi
    bg_open = StyledText(bg_style).ansi
    reset = StyledText(S.RESET).ansi

    ansi_lines, plain_lines, max_line_len = _prepare_log_box(values)

    spaces_l = " " * indent
    pady = " " * (get_width() if w_full else max_line_len + (2 * w_padding))
    pad_w_full = (get_width() - (max_line_len + (2 * w_padding))) if w_full else 0

    box_lines: list[str] = [f"{spaces_l}{open_seq}{pady}{reset}"]

    for ansi_line, plain_line in zip(ansi_lines, plain_lines, strict=False):
        right_pad = " " * ((w_padding + max_line_len - len(plain_line)) + pad_w_full)
        box_lines.append(f"{spaces_l}{open_seq}{' ' * w_padding}{_persist_style(ansi_line, bg_open)}{right_pad}{reset}")

    box_lines.append(f"{spaces_l}{open_seq}{pady}{reset}")

    StyledText(start + "\n".join(box_lines)).print(end=end)


def log_box_bordered(
    *values: TextRenderable | object,
    start: str = "",
    end: str = "\n",
    border_type: Literal["standard", "rounded", "strong", "double"] = "rounded",
    border_style: AnyStyle | Rgba | Hexa = S.BR.BLACK,
    default_color: ColorStyle | Rgba | Hexa | None = None,
    w_padding: int = 1,
    w_full: bool = False,
    indent: int = 0,
    border_chars: tuple[str, str, str, str, str, str, str, str, str, str, str] | None = None,
) -> None:
    """Will print a bordered box, containing a log message.\n
    ---------------------------------------------------------------------------------------------
    *   `*values` – The box content (any objects, or `StyledText` objects, one per line).
    *   `start` – Something to print before the log box is printed (e.g., `\\n`).
    *   `end` – Something to print after the log box is printed (e.g., `\\n`).
    *   `border_type` – One of the predefined border character sets.
    *   `border_style` – The style of the border (an `S` style, RGBA, or HEXA color).
    *   `default_color` – The default text color of the `*values`.
    *   `w_padding` – The horizontal padding (in chars) to the box content.
    *   `w_full` – Whether to make the box be the full terminal width or not.
    *   `indent` – The indentation of the box (in chars).
    *   `border_chars` – Define your own border characters set (overwrites `border_type`).
    ---------------------------------------------------------------------------------------------
    You can insert horizontal rules to split the box content by using `{hr}` in the `*values`.\n
    ---------------------------------------------------------------------------------------------
    To style the content, pass `StyledText` objects. For more detailed<br>
    information about styling, see the `ansi` module documentation.\n
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
    if border_chars is not None:
        if len(border_chars) != 11:
            raise ValueError(f"The 'border_chars' parameter must contain exactly 11 characters, got {len(border_chars)}")
        for char in border_chars:
            if len(char) != 1:
                raise ValueError(
                    f"The 'border_chars' parameter must only contain single-character strings, got {border_chars!r}"
                )

    border_open = StyledText(_as_fg_style(border_style)).ansi
    content_open = StyledText(_as_fg_style(default_color)).ansi if default_color is not None else ""
    reset = StyledText(S.RESET).ansi

    borders = {
        "standard": ("┌", "─", "┐", "│", "┘", "─", "└", "│", "├", "─", "┤"),
        "rounded": ("╭", "─", "╮", "│", "╯", "─", "╰", "│", "├", "─", "┤"),
        "strong": ("┏", "━", "┓", "┃", "┛", "━", "┗", "┃", "┣", "━", "┫"),
        "double": ("╔", "═", "╗", "║", "╝", "═", "╚", "║", "╠", "═", "╣"),
    }
    border_chars = borders.get(border_type, borders["standard"]) if border_chars is None else border_chars

    ansi_lines, plain_lines, max_line_len = _prepare_log_box(values, has_rules=True)

    spaces_l = " " * indent
    pad_w_full = (get_width() - (max_line_len + (2 * w_padding)) - (len(border_chars[1] * 2))) if w_full else 0

    border_t_line = border_chars[1] * (get_width() - (len(border_chars[1] * 2)) if w_full else max_line_len + (2 * w_padding))
    border_b_line = border_chars[5] * (get_width() - (len(border_chars[5] * 2)) if w_full else max_line_len + (2 * w_padding))
    h_rule_line = border_chars[9] * (get_width() - (len(border_chars[9] * 2)) if w_full else max_line_len + (2 * w_padding))

    border_l = f"{border_open}{border_chars[7]}{reset}"
    border_r = f"{border_open}{border_chars[3]}{reset}"
    border_t = f"{spaces_l}{border_open}{border_chars[0]}{border_t_line}{border_chars[2]}{reset}"
    border_b = f"{spaces_l}{border_open}{border_chars[6]}{border_b_line}{border_chars[4]}{reset}"

    h_rule = f"{spaces_l}{border_open}{border_chars[8]}{h_rule_line}{border_chars[10]}{reset}"

    box_lines: list[str] = []
    for ansi_line, plain_line in zip(ansi_lines, plain_lines, strict=False):
        if _PATTERNS.hr.match(plain_line):
            box_lines.append(h_rule)
            continue
        right_pad = " " * ((w_padding + max_line_len - len(plain_line)) + pad_w_full)
        box_lines.append(f"{spaces_l}{border_l}{' ' * w_padding}{content_open}{ansi_line}{reset}{right_pad}{border_r}")

    StyledText(
        f"{start}{border_t}{reset}\n" + "\n".join(box_lines) + ("\n" if box_lines else "") + f"{border_b}{reset}"
    ).print(end=end)


def confirm(
    prompt: TextRenderable | object = "Do you want to continue?",
    /,
    *,
    start: StyledText | str = "",
    end: StyledText | str = "",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    default_is_yes: bool = True,
) -> bool:
    """Ask a yes/no question.\n
    ------------------------------------------------------------------------------------------
    *   `prompt` – The input prompt (any object, or a `StyledText` object for styled output).
    *   `start` – Something to print before the input.
    *   `end` – Something to print after the input (e.g., `\\n`).
    *   `default_color` – The default text color of the `prompt`.
    *   `default_is_yes` – The default answer if the user just presses enter.
    ------------------------------------------------------------------------------------------
    To style the `prompt`, pass a `StyledText` object. For more detailed<br>
    information about styling, see the `ansi` module documentation."""

    yes_no = S.DIM(
        "(",
        *(S.BOLD("Y"), S.DIM) if default_is_yes else "y",
        "/",
        *(S.BOLD("N"), S.DIM) if not default_is_yes else "n",
        "): ",
    )
    head = f"{_to_styled_text(start)}{_to_styled_text(prompt).ansi} "
    head_seg = _as_fg_style(default_color)(head) if default_color is not None else head

    confirmed = input(StyledText(head_seg, S.RESET, yes_no).ansi).strip().lower() in (
        {"", "y", "yes"} if default_is_yes else {"y", "yes"}
    )

    if end:
        _to_styled_text(end).print(end="", flush=True)

    return confirmed


def multiline_input(
    prompt: TextRenderable | object = "",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    show_keybindings: bool = True,
    input_prefix: str = " ⮡ ",
    reset_ansi: bool = True,
) -> str:
    """An input where users can write (and paste) text over multiple lines.\n
    ------------------------------------------------------------------------------------------
    *   `prompt` – The input prompt (any object, or a `StyledText` object for styled output).
    *   `start` – Something to print before the input.
    *   `end` – Something to print after the input (e.g., `\\n`).
    *   `default_color` – The default text color of the `prompt`.
    *   `show_keybindings` – Whether to show the special keybindings or not.
    *   `input_prefix` – The prefix of the input line.
    *   `reset_ansi` – Whether to reset the ANSI codes after the input or not.
    ------------------------------------------------------------------------------------------
    To style the `prompt`, pass a `StyledText` object. For more detailed<br>
    information about styling, see the `ansi` module documentation."""

    kb = KeyBindings()
    kb.add("c-d", eager=True)(_multiline_input_submit)

    head = f"{start}{_to_styled_text(prompt).ansi}"
    head_seg = _as_fg_style(default_color)(head) if default_color is not None else head
    StyledText(head_seg).print()
    if show_keybindings:
        StyledText(S.DIM("[", S.BOLD("CTRL+D"), " : end of input]")).print()
    input_string = _pt.prompt(input_prefix, multiline=True, wrap_lines=True, key_bindings=kb)
    StyledText(S.RESET if reset_ansi else "").print(end=end[1:] if end.startswith("\n") else end)

    return input_string


@overload
def input(
    prompt: TextRenderable | object = "",
    /,
    *,
    start: str = "",
    end: str = "",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    placeholder: str | None = None,
    mask_char: str | None = None,
    min_len: int | None = None,
    max_len: int | None = None,
    allowed_chars: str | AllTextChars = CHARS.ALL,
    allow_paste: bool = True,
    validator: Callable[[str], str | None] | None = None,
    default_val: str | None = None,
    output_type: type[str] = str,
) -> str: ...
@overload
def input[T](
    prompt: TextRenderable | object = "",
    /,
    *,
    start: str = "",
    end: str = "",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    placeholder: str | None = None,
    mask_char: str | None = None,
    min_len: int | None = None,
    max_len: int | None = None,
    allowed_chars: str | AllTextChars = CHARS.ALL,
    allow_paste: bool = True,
    validator: Callable[[str], str | None] | None = None,
    default_val: T,
    output_type: type[T] = ...,
) -> T: ...
@overload
def input[T](
    prompt: TextRenderable | object = "",
    /,
    *,
    start: str = "",
    end: str = "",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    placeholder: str | None = None,
    mask_char: str | None = None,
    min_len: int | None = None,
    max_len: int | None = None,
    allowed_chars: str | AllTextChars = CHARS.ALL,
    allow_paste: bool = True,
    validator: Callable[[str], str | None] | None = None,
    default_val: T | None = None,
    output_type: type[T],
) -> T: ...


def input(
    prompt: TextRenderable | object = "",
    /,
    *,
    start: str = "",
    end: str = "",
    default_color: ColorStyle | Rgba | Hexa | None = None,
    placeholder: str | None = None,
    mask_char: str | None = None,
    min_len: int | None = None,
    max_len: int | None = None,
    allowed_chars: str | AllTextChars = CHARS.ALL,
    allow_paste: bool = True,
    validator: Callable[[str], str | None] | None = None,
    default_val: Any = None,
    output_type: type[Any] = str,
) -> Any:
    """Acts like a standard Python `input()` a bunch of cool extra features.\n
    ------------------------------------------------------------------------------------------
    *   `prompt` – The input prompt (any object, or a `StyledText` object for styled output).
    *   `start` – Something to print before the input.
    *   `end` – Something to print after the input (e.g., `\\n`).
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
    ------------------------------------------------------------------------------------------
    To style the `prompt`, pass a `StyledText` object. For more detailed<br>
    information about styling, see the `ansi` module documentation.\n
    ------------------------------------------------------------------------------------------
    #### Example Usage

    **Using a custom validator function:**

    ```python
    import xulbux as xx


    def email_validator(user_input: str) -> Optional[str]:
        if not re.match(r"[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}", user_input):
            return "Enter a valid E-Mail address (example@domain.com)"


    user_input = xx.console.input(
        prompt="E-Mail: ",
        placeholder="example@domain.com",
        validator=email_validator,
    )
    ```"""

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
    prompt_ansi = _to_styled_text(prompt).ansi
    if default_color is not None:
        prompt_ansi = StyledText(_as_fg_style(default_color)(prompt_ansi)).ansi
    session: _pt.PromptSession[str] = _pt.PromptSession(
        message=_pt.formatted_text.ANSI(prompt_ansi),
        validator=_ConsoleInputValidator(helper.get_text, mask_char=mask_char, min_len=min_len, validator=validator),
        validate_while_typing=True,
        key_bindings=kb,
        bottom_toolbar=helper.bottom_toolbar,
        placeholder=_pt.formatted_text.ANSI(StyledText((S.ITALIC | S.BR.BLACK)(placeholder)).ansi) if placeholder else "",
        style=custom_style,
    )
    StyledText(start).print(end="", flush=True)
    session.prompt()
    StyledText(end).print(end="", flush=True)

    if (result_text := helper.get_text()) in {"", None}:
        if default_val is not None:
            return default_val
        result_text = ""

    if output_type is str:
        return result_text

    else:
        try:
            return output_type(result_text)

        except (ValueError, TypeError):
            if default_val is not None:
                return default_val
            raise


def _read_single_key() -> None:
    """Wait for a single key press without requiring elevated privileges.<br>
    Falls back to reading a line when stdin is not a TTY (e.g., piped input)."""

    if not _sys.stdin.isatty():
        _sys.stdin.readline()
        return

    if _sys.platform == "win32":
        import msvcrt as _msvcrt  # type: ignore[import-not-found]

        _msvcrt.getch()  # type: ignore[attr-defined]

    else:
        import termios as _termios  # type: ignore[import-not-found]
        import tty as _tty  # type: ignore[import-not-found]

        fd = _sys.stdin.fileno()
        old_settings = _termios.tcgetattr(fd)  # type: ignore[attr-defined]

        try:
            _tty.setraw(fd)  # type: ignore[attr-defined]
            _sys.stdin.read(1)
        finally:
            _termios.tcsetattr(fd, _termios.TCSADRAIN, old_settings)  # type: ignore[attr-defined]


def _resolve_title_colors(title_bg_color: AnyStyle | Rgba | Hexa, /) -> tuple[AnyStyle, BaseStyle]:
    """Resolves the log title's background style and its matching foreground style.\n
    ------------------------------------------------------------------------------------
    *   `title_bg_color` – An `S` background style (black text is used on it) or an<br>
        RGBA/HEXA color (the best-contrast black or white text is computed for it)."""

    if is_any_style(title_bg_color):
        return title_bg_color, S.BLACK

    if _color_module.is_valid_rgba(title_bg_color) or _color_module.is_valid_hexa(title_bg_color):
        hexa_bg = _color_module.to_hexa(title_bg_color)
        return S.BG.hex(str(hexa_bg)), S.hex(str(_color_module.text_color_for_on_bg(hexa_bg)))

    raise ValueError(
        "The 'title_bg_color' parameter must be a valid ANSI background style, "
        f"RGBA value, or HEXA value, got {title_bg_color!r}"
    )


def _as_bg_style(color: AnyStyle | Rgba | Hexa, /) -> AnyStyle:
    """Resolves an `S` background style or an RGBA/HEXA color to an `S` background style."""

    if is_any_style(color):
        return color
    if _color_module.is_valid_rgba(color) or _color_module.is_valid_hexa(color):
        return S.BG.hex(str(_color_module.to_hexa(color)))

    raise ValueError(
        f"The 'box_bg_color' parameter must be a valid ANSI background style, RGBA value, or HEXA value, got {color!r}"
    )


def _as_fg_style(color: AnyStyle | Rgba | Hexa | None, /, *, fallback: str = "#000") -> AnyStyle:
    """Resolves an `S` style, an RGBA/HEXA color, or `None` (returns fallback) to an `S` foreground style."""

    if color is None:
        return S.hex(fallback)
    if is_any_style(color):
        return color
    if _color_module.is_valid_rgba(color) or _color_module.is_valid_hexa(color):
        return S.hex(str(_color_module.to_hexa(color)))

    raise ValueError(f"The 'color' parameter must be a valid ANSI style, RGBA value, or HEXA value, got {color!r}")


def _persist_style(ansi_text: str, style_open: str, /) -> str:
    """Re-inserts `style_open` right after every ANSI escape sequence in `ansi_text`,<br>
    so the style keeps applying even across (e.g., full) resets contained in the text."""

    if not style_open or ANSI.CHAR not in ansi_text:
        return ansi_text

    return ANSI.SEQ_PATTERN.sub(r"\g<0>" + style_open.replace("\\", r"\\"), ansi_text)


def _process_lines(clean_prompt: str, wrap_len: int) -> Generator[tuple[Literal[""]] | list[str], Any, None]:
    """Splits the clean prompt into lines and then splits each line into chunks that fit within the wrap length."""
    if not clean_prompt:
        yield ("",)
        return

    for line in clean_prompt.splitlines():
        lst = _string_module.split_count(line, wrap_len)
        yield lst if lst else ("",)


def _add_back_removed_parts(split_string: list[str], removals: tuple[tuple[int, str], ...], /) -> list[str]:
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

        i = _find_string_part(pos, cumulative_pos)
        adjusted_pos = (pos - cumulative_pos[i]) + offset_adjusts[i]
        parts = [result[i][:adjusted_pos], removal, result[i][adjusted_pos:]]
        result[i] = "".join(parts)
        offset_adjusts[i] += len(removal)

    return result


def _render_log_title(text: str, style: AnyStyle, /) -> str:
    """Renders (and caches) the styled log title as an ANSI string.\n
    ----------------------------------------------------------------------------
    Since consecutive log calls often reuse the exact same title and style,<br>
    the rendered string is cached and reused instead of being rebuilt."""

    key = (text, repr(style))

    if (cached := _LOG_TITLE_CACHE.get(key)) is None:
        cached = StyledText(style(text)).ansi
        if len(_LOG_TITLE_CACHE) < _LOG_TITLE_CACHE_MAX:
            _LOG_TITLE_CACHE[key] = cached

    return cached


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


def _split_hr_parts(val_str: str, /) -> list[str]:
    """Splits `val_str` into parts around any `{hr}` markers, keeping each marker as its own part."""

    result_parts: list[str] = []
    current_pos = 0

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

        elif should_split_after:
            result_parts.append(val_str[current_pos:end])
            current_pos = end

    if current_pos < len(val_str):
        result_parts.append(val_str[current_pos:])
    if not result_parts:
        result_parts.append(val_str)

    return result_parts


def _prepare_log_box(
    values: list[TextRenderable | object] | tuple[TextRenderable | object, ...], /, *, has_rules: bool = False
) -> tuple[list[str], list[str], int]:
    """Prepares the log box content, returning the ANSI lines,<br>
    their plain-text counterparts, and the maximum visible line length."""

    ansi_lines: list[str] = []
    plain_lines: list[str] = []

    for val in values:
        if is_text_renderable(val) and not isinstance(val, str):
            st = val if isinstance(val, StyledText) else (StyledText(*val) if isinstance(val, tuple) else StyledText(val))
            for ansi_line, plain_line in zip(st.ansi.split("\n"), st.raw.split("\n"), strict=False):
                ansi_lines.append(ansi_line)
                plain_lines.append(plain_line)
            continue

        val_str: str = str(val)
        parts: list[str] = _split_hr_parts(val_str) if has_rules else [val_str]

        for part in parts:
            for line in part.splitlines():
                ansi_lines.append(line)
                plain_lines.append(line)

    max_line_len = max([len(line) for line in plain_lines], default=0)

    return ansi_lines, plain_lines, max_line_len


def _multiline_input_submit(event: KeyPressEvent, /) -> None:
    event.app.exit(result=event.app.current_buffer.document.text)


class _ConsoleInputHelper:
    """Helper class to manage input processing and events."""

    def __init__(
        self,
        mask_char: str | None,
        min_len: int | None,
        max_len: int | None,
        allowed_chars: str | AllTextChars,
        allow_paste: bool,
        validator: Callable[[str], str | None] | None,
    ) -> None:
        self.mask_char: str | None = mask_char
        self.min_len: int | None = min_len
        self.max_len: int | None = max_len
        self.allowed_chars: str | AllTextChars = allowed_chars
        self.allow_paste: bool = allow_paste
        self.validator: Callable[[str], str | None] | None = validator

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
                toolbar_msgs.append(StyledText((S.BOLD | S.hex("#FFF") | S.BG.RED)(" Text too long! ")).ansi)
            if self.validator and text_to_check and (validation_error_msg := self.validator(text_to_check)) not in {"", None}:
                toolbar_msgs.append(
                    StyledText((S.BOLD | S.hex("#000") | S.BG.BR.RED), f" {validation_error_msg} ", S.RESET_BG, sep="").ansi
                )
            if self.filtered_chars:
                plural = "" if len(char_list := "".join(sorted(self.filtered_chars))) == 1 else "s"
                toolbar_msgs.append(
                    StyledText((S.BOLD | S.hex("#000") | S.BG.YELLOW)(f"( Char{plural} '{char_list}' not allowed )")).ansi
                )
                self.filtered_chars.clear()
            if self.min_len and len(text_to_check) < self.min_len:
                toolbar_msgs.append(
                    StyledText(
                        (S.BOLD | S.hex("#000") | S.BG.YELLOW)(f"( Need {self.min_len - len(text_to_check)} more chars )")
                    ).ansi
                )
            if self.tried_pasting:
                toolbar_msgs.append(StyledText((S.BOLD | S.hex("#000") | S.BG.BR.YELLOW)("( Pasting disabled )")).ansi)
                self.tried_pasting = False
            if self.max_len and len(text_to_check) == self.max_len:
                toolbar_msgs.append(StyledText((S.BOLD | S.hex("#000") | S.BG.BR.YELLOW)("( Maximum length reached )")).ansi)

            return _pt.formatted_text.ANSI(" ".join(toolbar_msgs))

        except Exception:
            return _pt.formatted_text.ANSI("")

    def process_insert_text(self, text: str, /) -> tuple[str, set[str]]:
        """Processes the inserted text according to the allowed characters and max length."""

        removed_chars: set[str] = set()

        if not text:
            return "", removed_chars

        processed_text = "".join([char for char in text if ord(char) >= 32])

        if self.allowed_chars is not CHARS.ALL:
            filtered_text = ""
            for char in processed_text:
                if char in cast("str", self.allowed_chars):
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
                        self.result_text = self.result_text[: cursor_pos - 1] + self.result_text[cursor_pos:]
                        buffer.delete_before_cursor(1)
                else:
                    if cursor_pos < len(self.result_text):
                        self.result_text = self.result_text[:cursor_pos] + self.result_text[cursor_pos + 1 :]
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
        mask_char: str | None,
        min_len: int | None,
        validator: Callable[[str], str | None] | None,
    ) -> None:
        self.get_text: Callable[[], str] = get_text
        self.mask_char: str | None = mask_char
        self.min_len: int | None = min_len
        self.validator: Callable[[str], str | None] | None = validator

    def validate(self, document: Document) -> None:
        """Validates the input text according to the minimum length and custom validator function."""

        text_to_validate = self.get_text() if self.mask_char else document.text
        if self.min_len and len(text_to_validate) < self.min_len:
            raise ValidationError(message="", cursor_position=len(document.text))
        if self.validator and self.validator(text_to_validate) not in {"", None}:
            raise ValidationError(message="", cursor_position=len(document.text))


class _StdoutInterceptorMixin:
    active: bool
    _original_stdout: TextIO | None
    _buffer: list[str]
    _last_line_len: int

    def _start_intercepting(self) -> None:
        self.active = True
        self._original_stdout = cast("TextIO", _sys.stdout)
        _sys.stdout = _InterceptedOutput(self, self._original_stdout)

    def _stop_intercepting(self) -> None:
        if self._original_stdout:
            self._flush_buffer()
            _sys.stdout = self._original_stdout
            self._original_stdout = None
        self.active = False
        self._buffer.clear()
        self._last_line_len = 0
        self._reset_state()

    def _emergency_cleanup(self) -> None:
        with suppress(Exception):
            self._stop_intercepting()

    def _clear_intercept_line(self) -> None:
        if self._last_line_len > 0 and self._original_stdout:
            self._original_stdout.write(f"{ANSI.CHAR}[2K\r")
            self._original_stdout.flush()

    def _flush_buffer(self) -> None:
        if self._buffer and self._original_stdout:
            self._clear_intercept_line()
            for content in self._buffer:
                self._original_stdout.write(content)
            self._original_stdout.flush()
            self._buffer.clear()

    def _redraw_display(self) -> None:
        pass

    def _reset_state(self) -> None:
        pass


@mypyc_attr(native_class=False)
class _InterceptedOutput:
    """Custom stdout wrapper that captures output and stores it in the progress bar buffer."""

    def __init__(self, status_indicator: _StdoutInterceptorMixin, original_stdout: TextIO, /) -> None:
        self.status_indicator: _StdoutInterceptorMixin = status_indicator
        self.original_stdout: TextIO = original_stdout

    def write(self, content: str, /) -> int:
        try:
            if content and content != "\r":
                self.status_indicator._buffer.append(content)
            return len(content)
        except Exception:
            self.status_indicator._emergency_cleanup()
            raise

    def flush(self) -> None:
        try:
            if self.status_indicator.active and self.status_indicator._buffer:
                self.status_indicator._flush_buffer()
                self.status_indicator._redraw_display()
        except Exception:
            self.status_indicator._emergency_cleanup()
            raise

    def __getattr__(self, name: str, /) -> Any:
        return getattr(self.original_stdout, name)


class ProgressBar(_StdoutInterceptorMixin):
    """A terminal progress bar with smooth transitions and customizable appearance.\n
    -------------------------------------------------------------------------------------------------------
    *   `min_width` – The min width of the progress bar in chars.
    *   `max_width` – The max width of the progress bar in chars.
    *   `format` – The format strings used to render the progress bar, containing placeholders:
        -   `{label}` `{l}`
        -   `{bar}` `{b}`
        -   `{current}` `{c}` (optional `:<char>` format specifier for thousands separator, e.g., `{c:,}`)
        -   `{total}` `{t}` (optional `:<char>` format specifier for thousands separator, e.g., `{t:,}`)
        -   `{percentage}` `{percent}` `{p}` (optional `:.<num>f` format specifier to round<br>
            to specified number of decimal places, e.g., `{p:.1f}`)
    *   `limited_format` – A simplified format string used when the terminal width is too small<br>
        for the normal `format`.
    *   `chars` – A tuple of characters ordered from full to empty progress:<br>
        The first character represents completely filled sections.<br>
        Intermediate characters create smooth transitions<br>
        The last character represents empty sections.
    -------------------------------------------------------------------------------------------------------
    The formats can additionally be styled by embedding ANSI from the operator-based API.<br>
    For more detailed information, see the `ansi` module documentation."""

    def __init__(
        self,
        *,
        min_width: int = 10,
        max_width: int = 25,
        format: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable = _DEFAULT_BAR_FORMAT,
        limited_format: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable = _DEFAULT_LIMITED_BAR_FORMAT,
        sep: str = " ",
        chars: tuple[str, ...] = ("█", "▉", "▊", "▋", "▌", "▍", "▎", "▏", " "),
    ) -> None:
        self.active: bool = False
        """Whether the progress bar is currently active (intercepting stdout) or not."""
        self.min_width: int
        """The min width of the progress bar in chars."""
        self.max_width: int
        """The max width of the progress bar in chars."""
        self.format: list[str]
        """The format strings used to render the progress bar (joined by `sep`)."""
        self.limited_format: list[str]
        """The simplified format strings used when the terminal width is too small."""
        self.sep: str
        """The separator string used to join multiple bar-format strings."""
        self.chars: tuple[str, ...]
        """A tuple of characters ordered from full to empty progress."""

        self.set_width(min_width, max_width)
        self.set_format(format, limited_format, sep=sep)
        self.set_chars(chars)

        self._buffer: list[str] = []
        self._original_stdout: TextIO | None = None
        self._current_progress_str: str = ""
        self._last_line_len: int = 0
        self._last_update_time: float = 0.0
        self._min_update_interval: float = 0.02  # 20ms = max 50 updates/second

    def set_width(self, min_width: int | None = None, max_width: int | None = None) -> None:
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

    def set_format(
        self,
        format: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable | None = None,
        limited_format: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable | None = None,
        *,
        sep: str | None = None,
    ) -> None:
        """Set the format string used to render the progress bar.\n
        -------------------------------------------------------------------------------------------------------
        *   `format` – The format strings used to render the progress bar, containing placeholders:
            -   `{label}` `{l}`
            -   `{bar}` `{b}`
            -   `{current}` `{c}` (optional `:<char>` format specifier for thousands separator, e.g., `{c:,}`)
            -   `{total}` `{t}` (optional `:<char>` format specifier for thousands separator, e.g., `{t:,}`)
            -   `{percentage}` `{percent}` `{p}` (optional `:.<num>f` format specifier to round<br>
                to specified number of decimal places, e.g., `{p:.1f}`)
        *   `limited_format` – A simplified format strings used when the terminal width is too small.
        *   `sep` – The separator string used to join multiple format strings.
        -------------------------------------------------------------------------------------------------------
        The formats can additionally be styled by embedding ANSI from the operator-based API.<br>
        For more detailed information, see the `ansi` module documentation."""

        if format is not None:
            compiled_bar = _compile_format(format)
            has_bar = False
            for part in compiled_bar:
                if _PATTERNS.bar.search(part):
                    has_bar = True
                    break
            if not has_bar:
                raise ValueError(
                    f"The 'format' parameter value must contain the '{{bar}}' or '{{b}}' placeholder, got {format!r}"
                )

            self.format = compiled_bar

        if limited_format is not None:
            compiled_limited = _compile_format(limited_format)
            has_limited = False

            for part in compiled_limited:
                if _PATTERNS.bar.search(part):
                    has_limited = True
                    break

            if not has_limited:
                raise ValueError(
                    "The 'limited_format' parameter value must contain the "
                    f"'{{bar}}' or '{{b}}' placeholder, got {limited_format!r}"
                )

            self.limited_format = compiled_limited

        if sep is not None:
            self.sep = sep

    def set_chars(self, chars: tuple[str, ...], /) -> None:
        """Set the characters used to render the progress bar.\n
        -----------------------------------------------------------------------------
        *   `chars` – A tuple of characters ordered from full to empty progress:<br>
            The first character represents completely filled sections.<br>
            Intermediate characters create smooth transitions.<br>
            The last character represents empty sections.<br>
            If `None`, uses default Unicode block characters.\n
        -----------------------------------------------------------------------------
        #### Example Usage

        ```python
        ProgressBar.set_chars(("█", "▓", "▒", "░", " "))
        ```"""

        if len(chars) < 2:
            raise ValueError(f"The 'chars' parameter must contain at least two characters (full and empty), got {chars!r}")
        else:
            for char in chars:
                if len(char) != 1:
                    raise ValueError(f"All elements of 'chars' must be single-character strings, got {chars!r}")

        self.chars = chars

    def show_progress(self, current: int, total: int, /, label: StyledText | str | None = None) -> None:
        """Show or update the progress bar.\n
        ----------------------------------------------------------------------------------------------
        *   `current` – The current progress value (below `0` or greater than `total` hides the bar).
        *   `total` – The total value representing 100% progress (must be greater than `0`).
        *   `label` – An optional label which is inserted at the `{label}` or `{l}` placeholder."""

        # Throttle updates (unless it's the first/final update):
        current_time = _time.time()
        if (
            not (not self._last_update_time or current >= total or current < 0)
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
            self._clear_intercept_line()
            self._stop_intercepting()

    @contextmanager
    def progress_context(self, total: int, /, label: StyledText | str | None = None) -> Generator[ProgressUpdater, None, None]:
        """Context manager for automatic cleanup. Returns a function to update progress.\n
        -----------------------------------------------------------------------------------------
        *   `total` – The total value representing 100% progress (must be greater than `0`).
        *   `label` – An optional label which is inserted at the `{label}` or `{l}` placeholder.
        -----------------------------------------------------------------------------------------
        The returned callable accepts keyword arguments.<br>
        At least one of these parameters must be provided:
        *   `current` – Update the current progress value.
        *   `label` – Update the progress label.
        -----------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        with ProgressBar().progress_context(500, "Loading...") as update_progress:
            update_progress(0)  # Show empty bar at start.

            for i in range(400):
                # Do some work...
                update_progress(i)  # Update progress

            update_progress("Finalizing...")  # Update label.

            for i in range(400, 500):
                # Do some work...
                update_progress(i, f"Finalizing ({i})")  # Update both.
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

    def _draw_progress_bar(self, current: int, total: int, /, label: StyledText | str | None = None) -> None:
        if total <= 0 or not self._original_stdout:
            return

        percentage = min(100, (current / total) * 100)

        formatted, bar_width = self._get_formatted_info_and_bar_width(self.format, current, total, percentage, label)
        if bar_width < self.min_width:
            formatted, bar_width = self._get_formatted_info_and_bar_width(
                self.limited_format, current, total, percentage, label
            )

        bar = self._create_bar(current, total, max(1, bar_width)) + _ANSI_RESET
        progress_text = _PATTERNS.bar.sub(bar.replace("\\", r"\\"), formatted)

        self._current_progress_str = progress_text
        self._last_line_len = len(progress_text)
        self._original_stdout.write(f"{ANSI.CHAR}[2K\r{progress_text}")
        self._original_stdout.flush()

    def _get_formatted_info_and_bar_width(
        self, format: list[str], current: int, total: int, percentage: float, /, label: StyledText | str | None = None
    ) -> tuple[str, int]:
        fmt_parts: list[str] = []
        label_ansi = _to_styled_text(label).ansi if label is not None else ""

        for part in format:
            fmt_part = _PATTERNS.label.sub(label_ansi.replace("\\", r"\\"), part)
            fmt_part = _PATTERNS.current.sub(
                lambda match: f"{current:,}".replace(",", match.group(1)) if match.group(1) else str(current), fmt_part
            )
            fmt_part = _PATTERNS.total.sub(
                lambda match: f"{total:,}".replace(",", match.group(1)) if match.group(1) else str(total), fmt_part
            )
            fmt_part = _PATTERNS.percentage.sub(
                lambda match: f"{percentage:.{match.group(1) if match.group(1) else '1'}f}", fmt_part
            )
            if fmt_part:
                fmt_parts.append(fmt_part)

        fmt_str = self.sep.join(fmt_parts)

        bar_space = get_width() - len(StyledText.remove_ansi(_PATTERNS.bar.sub("", fmt_str)))
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

    def _reset_state(self) -> None:
        self._last_update_time = 0.0
        self._current_progress_str = ""

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

    def __init__(self, progress_bar: ProgressBar, total: int, label: StyledText | str | None, /) -> None:
        self.progress_bar: ProgressBar = progress_bar
        self.total: int = total
        self.current_label: StyledText | str | None = label
        self.current_progress: int = 0

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


class Throbber(_StdoutInterceptorMixin):
    """A terminal throbber for indeterminate processes with customizable appearance.<br>
    This class intercepts stdout to allow printing while the animation is active.\n
    -----------------------------------------------------------------------------------------
    *   `label` – The current label text.
    *   `format` – The format string used to render the throbber, containing placeholders:
        -   `{label}` `{l}`
        -   `{animation}` `{a}`
    *   `frames` – A tuple of strings representing the animation frames.
    *   `interval` – The time in seconds between each animation frame.
    -----------------------------------------------------------------------------------------
    The format can additionally be styled by embedding ANSI from the operator-based API.<br>
    For more detailed information, see the `ansi` module documentation."""

    def __init__(
        self,
        *,
        label: StyledText | str | None = None,
        format: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable = _DEFAULT_THROBBER_FORMAT,
        sep: str = " ",
        frames: tuple[str, ...] = FRAMES_STANDARD,
        interval: float = 0.08,
    ) -> None:
        self.format: list[str]
        """The format strings used to render the throbber (joined by `sep`)."""
        self.sep: str
        """The separator string used to join multiple throbber-format strings."""
        self.frames: tuple[str, ...]
        """A tuple of strings representing the animation frames."""
        self.interval: float
        """The time in seconds between each animation frame."""
        self.label: StyledText | str | None
        """The current label text."""
        self.active: bool = False
        """Whether the throbber is currently active (intercepting stdout) or not."""

        self.update_label(label)
        self.set_format(format, sep=sep)
        self.set_frames(frames)
        self.set_interval(interval)

        self._buffer: list[str] = []
        self._original_stdout: TextIO | None = None
        self._current_animation_str: str = ""
        self._last_line_len: int = 0
        self._frame_index: int = 0
        self._stop_event: _threading.Event | None = None
        self._animation_thread: _threading.Thread | None = None

    def set_format(
        self, format: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable, *, sep: str | None = None
    ) -> None:
        """Set the format string used to render the throbber.\n
        -----------------------------------------------------------------------------------------
        *   `format` – The format strings used to render the throbber, containing placeholders:
            -   `{label}` `{l}`
            -   `{animation}` `{a}`
        *   `sep` – The separator string used to join multiple format strings.
        -----------------------------------------------------------------------------------------
        The format can additionally be styled by embedding ANSI from the operator-based API.<br>
        For more detailed information, see the `ansi` module documentation."""

        compiled_throbber = _compile_format(format)
        has_animation = False

        for fmt in compiled_throbber:
            if _PATTERNS.animation.search(fmt):
                has_animation = True
                break

        if not has_animation:
            raise ValueError(
                "At least one format string in 'format' must contain the "
                f"'{{animation}}' or '{{a}}' placeholder, got {format!r}"
            )

        self.format = compiled_throbber
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

    def start(self, label: StyledText | str | None = None, /) -> None:
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

            self._clear_intercept_line()
            self._stop_intercepting()

    def update_label(self, label: StyledText | str | None, /) -> None:
        """Update the throbber's label text.\n
        -----------------------------------------
        *   `new_label` – The new label text."""

        self.label = label

    @contextmanager
    def context(self, label: StyledText | str | None = None, /) -> Generator[Callable[[StyledText | str], None], None, None]:
        """Context manager for automatic cleanup. Returns a function to update the label.\n
        ------------------------------------------------------------------------------------
        *   `label` – The label to display alongside the throbber.\n
        ------------------------------------------------------------------------------------
        The returned callable accepts a single parameter:
        *   `new_label` – The new label text.\n
        ------------------------------------------------------------------------------------
        #### Example Usage

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

                frame = self.frames[self._frame_index % len(self.frames)] + _ANSI_RESET
                label_ansi = _to_styled_text(self.label).ansi if self.label is not None else ""
                formatted = self.sep.join(
                    fmt_part
                    for part in self.format
                    if (
                        fmt_part := _PATTERNS.animation.sub(
                            frame.replace("\\", r"\\"), _PATTERNS.label.sub(label_ansi.replace("\\", r"\\"), part)
                        )
                    )
                )

                self._current_animation_str = formatted
                self._last_line_len = len(formatted)
                self._redraw_display()
                self._frame_index += 1

            except Exception:
                self._emergency_cleanup()
                break

            if self._stop_event:
                self._stop_event.wait(self.interval)

    def _reset_state(self) -> None:
        self._current_animation_str = ""

    def _redraw_display(self) -> None:
        if self._current_animation_str and self._original_stdout:
            self._original_stdout.write(f"{ANSI.CHAR}[2K\r{self._current_animation_str}")
            self._original_stdout.flush()
