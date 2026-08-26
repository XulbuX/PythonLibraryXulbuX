"""
Provides comprehensive tools for terminal output and interaction.

Features include styled logging, progress bars, interactive prompts,
and command-line argument parsing.
"""

from . import color as _color_module
from .ansi import (
    AnyStyle,
    BaseStyle,
    FgColorStyle,
    Renderable,
    S,
    StyledText,
    TextRenderable,
    _StyledSequence,
    is_any_style,
    is_fg_color_style,
    is_text_renderable,
)
from .base.consts import ANSI, CHARS
from .base.decorators import mypyc_attr
from .base.types import AllTextChars, Hexa, ProgressUpdater, Rgba, SeqOrSet
from .regex import LazyRegex

import ctypes as _ctypes
import getpass as _getpass
import os as _os
import re as _re
import shutil as _shutil
import subprocess as _subprocess
import sys as _sys
import threading as _threading
import time as _time
from collections.abc import Callable, Generator, Iterable, Sequence
from contextlib import contextmanager, suppress
from contextlib import suppress as _suppress
from pathlib import Path
from typing import Any, Final, Literal, NoReturn, TextIO, TypedDict, cast, overload
import prompt_toolkit as _pt
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import ValidationError, Validator

_PATTERNS: Final[LazyRegex] = LazyRegex(
    animation=r"(?i){(?:animation|a)}",
    bar=r"(?i){(?:bar|b)}",
    cli_opt_prefix=r"^[\W_]+",
    cli_placeholder=r"(?i)^[A-Z0-9_-]+\??$",
    cli_token=r"""--?[^\s=]+=(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s]+)|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s]+""",
    current=r"(?i){(?:current|c)(?::(.))?}",
    hr=r"(?i){hr}",
    hr_l_nl=r"(?i)(?<=\n){hr}(?!\n)",
    hr_no_nl=r"(?i)(?<!\n){hr}(?!\n)",
    hr_r_nl=r"(?i)(?<!\n){hr}(?=\n)",
    label=r"(?i){(?:label|l)}",
    percentage=r"(?i){(?:percentage|percent|p)(?::\.([0-9])+f)?}",
    total=r"(?i){(?:total|t)(?::(.))?}",
)

_LOG_TITLE_CACHE: dict[tuple[str, str], str] = {}
"""Cache of rendered log-title ANSI strings, keyed by `(padded_title, style_repr)`."""
_LOG_TITLE_CACHE_MAX: Final[int] = 256
"""Maximum number of entries kept in `_LOG_TITLE_CACHE`."""

_ANSI_RESET: Final[str] = StyledText(S.RESET).ansi
"""The ANSI full-reset sequence (`ESC[0m`)."""

_OPT_SEP_DEFAULT: Final[object] = object()
"""Sentinel object used as default for `opt_value_sep` in `ArgumentParser.parse()`."""

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


def _wrap_text(obj: TextRenderable | object, width: int) -> list[StyledText]:
    """Internal helper to word-wrap a string or `StyledText` while preserving styles and line breaks."""

    return _to_styled_text(obj).wrap(width)


def _is_number(text: str, /) -> bool:
    """Internal helper to check whether a string represents a numeric literal (e.g., `-5`, `3.14`)."""

    if not text:
        return False

    if text[0].isdigit() or (text[0] == "-" and len(text) > 1 and (text[1].isdigit() or text[1] == ".")):
        try:
            float(text)
            return True
        except ValueError:
            return False

    return False


class ArgConfigDict(TypedDict):
    """Configuration dictionary for an argument or option."""

    is_arg: bool
    opts: frozenset[str] | None
    nargs: int | Literal["?", "*", "+"]
    expects_value: str | None
    optional_value: bool
    choices: Iterable[str] | None
    required: bool
    help: TextRenderable | None


class ParsedArgData:
    """Represents the result of a parsed command-line argument or option.\n
    ----------------------------------------------------------------------------------------------------
    *   `exists` – Whether the argument or option was found in the command-line input or not.
    *   `is_arg` – Whether the value was provided as a positional argument.
    *   `values` – The tuple of values associated with the argument or option.
    *   `opt` – The specific option that was found (e.g., `-v`, `-vv`, `-vvv`),
        or `None` for arguments.\n
    ----------------------------------------------------------------------------------------------------
    When the `ParsedArgData` instance is accessed as a boolean
    it will correspond to the `exists` attribute."""

    def __init__(
        self,
        exists: bool = False,
        values: tuple[str, ...] = (),
        is_arg: bool = False,
        opt: str | None = None,
    ) -> None:
        self.exists: bool = exists
        """Whether the argument or option was found in the command-line input or not."""
        self.values: tuple[str, ...] = values
        """The tuple of values associated with the argument or option."""
        self.is_arg: bool = is_arg
        """Whether the value was provided as a positional argument."""
        self.opt: str | None = opt
        """The specific option string that was found (e.g., `-v`, `-vv`, `-vvv`), or `None` for arguments."""

    @property
    def is_opt(self) -> bool:
        """Whether the value was provided as a flagged option."""

        return not self.is_arg if self.exists else False

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
        """Get the parsed value, optionally casting it
        to a specified type and providing a fallback default.\n
        ----------------------------------------------------------------------------------------------------
        *   `cast_type` – The type to cast to (e.g., `int`, `Path`, …).
        *   `default` – The fallback value if `exists` is false or if no values exist.\n
        ----------------------------------------------------------------------------------------------------
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
        """Get all parsed values, optionally casting them
        to a specified type and providing a fallback default.\n
        ----------------------------------------------------------------------------------------------------
        *   `cast_type` – The type to cast to (e.g., `int`, `Path`, …).
        *   `default` – The fallback value if `exists` is false or if no values exist.\n
        ----------------------------------------------------------------------------------------------------
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
        return f"ParsedArgData(exists={self.exists}, values={self.values}, is_arg={self.is_arg}, opt={self.opt!r})"


class ParsedArgs:
    """Container for the result of `ArgumentParser.parse()`."""

    def __init__(self) -> None:
        self._args: dict[str, ParsedArgData] = {}

    def _add_arg(self, alias: str, data: ParsedArgData) -> None:
        """Internal method to add a parsed argument to the container."""

        self._args[alias] = data

    def __getattr__(self, name: str) -> ParsedArgData:
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        try:
            return self._args[name]
        except KeyError as exc:
            defined_aliases = ", ".join([repr(key) for key in sorted(self._args.keys())])
            defined_msg = f"Available arguments: {defined_aliases}" if defined_aliases else ""
            raise AttributeError(f"Argument '{name}' is not defined on '{type(self).__name__}'\n{defined_msg}") from exc

    def __repr__(self) -> str:
        return f"ParsedArgs(args={self._args})"


class ArgumentParser:
    """An advanced command-line argument parser with built-in help generation and validation.\n
    ----------------------------------------------------------------------------------------------------
    *   `title` – An optional title for the help print (e.g., `"CLI Tool"`).
    *   `subtitle` – An optional subtitle (e.g., `"A simple command-line utility"`).
    *   `notice` – Optional notice or warning text to display right after the title.
    *   `usage` – An optional explicit usage string, containing placeholders:
        -   `{cmd}` – The command name (e.g., `cli-tool`).
        -   `{args}` – The arguments placeholder (`<input> [output...]`).
        -   `{opts}` – The options placeholder (`[options]`).
    *   `controls` – A sequence of tuples `(control_key, help)`, where `control_key`<br>
        can be a single key string or an iterable of strings (e.g., `("WASD", "⏶⏴⏷⏵")`).
    *   `examples` – A list of tuples `(example_command, comment)`.
    *   `epilog` – Optional footer text to append to the help print.
    *   `accent_color` – Optional accent color for the help print (e.g., `S.BR.MAGENTA`).
    *   `prefix_chars` – Characters that prefix options (default: `"-"`).
    *   `opt_value_sep` – String separating option from value (default: `"="`).
    *   `intermixed` – Whether options and positional arguments can be intermixed (default: `True`).
    *   `help_opts` – A set of options that trigger the help print (default: `{"-h", "--help"}`)."""

    def __init__(
        self,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        notice: TextRenderable | object | None = None,
        usage: TextRenderable | str | None = None,
        controls: Sequence[tuple[str | SeqOrSet[str], TextRenderable]] | None = None,
        examples: Sequence[tuple[str, TextRenderable]] | None = None,
        epilog: TextRenderable | object | None = None,
        prefix_chars: str = "-",
        opt_value_sep: str | None = "=",
        intermixed: bool = True,
        help_opts: SeqOrSet[str] = frozenset({"-h", "--help"}),
    ) -> None:

        if not prefix_chars:
            raise ValueError("The 'prefix_chars' parameter cannot be empty")

        self.title: str | None = title
        """An optional title for the help print (e.g., `"CLI Tool"`)."""
        self.subtitle: str | None = subtitle
        """An optional subtitle (e.g., `"A simple command-line utility"`)."""
        self.notice: TextRenderable | object | None = notice
        """Optional notice or warning text to display after the title."""
        self.usage: TextRenderable | str | None = usage
        """An optional explicit usage string."""
        self.controls: Sequence[tuple[str | SeqOrSet[str], TextRenderable]] | None = controls
        """A sequence of tuples `(control_key, help)`."""
        self.examples: Sequence[tuple[str, TextRenderable]] | None = examples
        """A sequence of tuples `(example_command, comment)`."""
        self.epilog: TextRenderable | object | None = epilog
        """Optional footer text to append to the help print."""
        self.prefix_chars: str = prefix_chars
        """Characters that prefix options (e.g., `"-"`, `"-/"`)."""
        self.opt_value_sep: str | None = opt_value_sep
        """String separating an option from its value (e.g., `"="`)."""
        self.intermixed: bool = intermixed
        """Whether options and positional arguments can be intermixed."""

        escaped_prefixes = "".join([_re.escape(char) for char in prefix_chars])
        self._opt_pattern: _re.Pattern[str] = _re.compile(rf"^[{escaped_prefixes}]{{1,2}}(?:\?|[\w][\w\-]*)$")

        self.help_opts: frozenset[str] = frozenset(help_opts)
        """A set of options that trigger the help print."""

        for opt in self.help_opts:
            if not self._opt_pattern.fullmatch(opt):
                raise ValueError(
                    f"The 'help_opts' parameter contains invalid option {opt!r}\n"
                    f"Options must start with prefix chars {self.prefix_chars!r} and contain valid characters"
                )

        self._arg_configs: dict[str, ArgConfigDict] = {}
        self._args_order: list[str] = []

    def add_arg(
        self,
        name: str,
        /,
        *,
        nargs: int | Literal["?", "*", "+"] = 1,
        choices: Iterable[str] | None = None,
        required: bool | None = None,
        help: TextRenderable | None = None,
    ) -> None:
        """Define a new positional argument to parse.\n
        ----------------------------------------------------------------------------------------------------
        *   `name` – The argument name (e.g., `"input_file"`).
        *   `nargs` – Arguments value count: integer ≥ 1, `"?"` (0 or 1), `"*"` (≥ 0), or `"+"` (≥ 1).
        *   `choices` – Optional iterable of allowed strings for this argument's value.
        *   `required` – Whether the argument must be provided (auto-deduced from `nargs` if omitted).
        *   `help` – Help text describing the argument."""

        if name.startswith("_"):
            raise ValueError(f"The argument name cannot start with an underscore, got {name!r}")

        for char in self.prefix_chars:
            if name.startswith(char):
                raise ValueError(f"The argument name {name!r} cannot start with prefix char {char!r}")

        if name in self._arg_configs:
            raise ValueError(f"The argument '{name}' is already defined on this 'ArgumentParser', got {name!r}")

        if isinstance(nargs, int):
            if nargs < 1:
                raise ValueError(f"The 'nargs' parameter must be an integer >= 1, got {nargs!r}")
        elif nargs not in {"?", "*", "+"}:
            raise ValueError(f"The 'nargs' parameter must be an integer >= 1 or one of '?', '*', '+', got {nargs!r}")

        self._arg_configs[name] = {
            "is_arg": True,
            "opts": None,
            "nargs": nargs,
            "expects_value": None,
            "optional_value": False,
            "choices": choices,
            "required": (nargs not in {"?", "*"}) if required is None else required,
            "help": help,
        }
        self._args_order.append(name)

    def add_opt(
        self,
        opts: SeqOrSet[str],
        alias: str | None = None,
        /,
        *,
        expects_value: str | Literal[False] = False,
        choices: Iterable[str] | None = None,
        required: bool = False,
        help: TextRenderable | None = None,
    ) -> None:
        """Define a new flagged option to parse.\n
        ----------------------------------------------------------------------------------------------------
        *   `opts` – A collection of option strings (e.g., `{"-f", "--file"}`).
        *   `alias` – Optional explicit attribute name on `ParsedArgs` (auto-deduced if omitted).
        *   `expects_value` – `False` for a boolean option, or a string placeholder (e.g., `"PATH"`).<br>
            Append `?` (e.g., `"PATH?"` or `"VAL?"`) to make the expected value optional.
        *   `choices` – Optional iterable of allowed strings for this option's value.
        *   `required` – Whether the option must be provided.
        *   `help` – Help text describing the option."""

        if len(opts) == 0:
            raise ValueError("The 'opts' parameter cannot be empty")

        for opt in opts:
            if not self._opt_pattern.fullmatch(opt):
                raise ValueError(
                    f"The 'opts' parameter contains invalid option {opt!r}, options must start with prefix chars "
                    f"{self.prefix_chars!r} and contain valid characters"
                )

        if overlap := set(opts).intersection(self.help_opts):
            raise ValueError(f"The 'opts' parameter options {overlap} overlap with help options {self.help_opts}")

        for existing_arg, existing_cfg in self._arg_configs.items():
            if existing_cfg["opts"] is not None and (overlap := set(opts).intersection(existing_cfg["opts"])):
                raise ValueError(
                    f"The 'opts' parameter options {overlap} overlap with "
                    f"existing argument '{existing_arg}' options {existing_cfg['opts']}"
                )

        if (target_alias := self._deduce_alias(opts) if alias is None else alias).startswith("_"):
            raise ValueError(f"The 'alias' parameter cannot start with an underscore, got {target_alias!r}")
        elif target_alias in self._arg_configs:
            raise ValueError(f"The alias '{target_alias}' is already defined on this 'ArgumentParser'")

        placeholder: str | None
        optional_value: bool

        if expects_value is False:
            optional_value = False
            placeholder = None
        elif type(expects_value) is str and _PATTERNS.cli_placeholder.fullmatch(expects_value):
            if expects_value.endswith("?"):
                optional_value = True
                placeholder = expects_value[:-1]
            else:
                optional_value = False
                placeholder = expects_value
        else:
            raise ValueError(
                "The 'expects_value' parameter must be False or a string containing only letters, digits, "
                f"underscores, or hyphens (optionally ending with '?'), got {expects_value!r}"
            )

        self._arg_configs[target_alias] = {
            "is_arg": False,
            "opts": frozenset(opts),
            "nargs": 1,
            "expects_value": placeholder,
            "optional_value": optional_value,
            "choices": choices,
            "required": required,
            "help": help,
        }

    def _sort_opts(self, opts: Iterable[str]) -> list[str]:
        """Internal method to sort a set of options for help printing."""

        return sorted(opts, key=lambda opt: (len(opt) - len(_PATTERNS.cli_opt_prefix.sub("", opt)), opt))

    def _opts_to_st(self, opts: Iterable[str]) -> StyledText:
        """Internal method to convert a set of options into a<br>
        nicely formatted `StyledText` object for help printing."""

        return StyledText(", ").join([S.BR.BLUE(opt) for opt in self._sort_opts(opts)])

    def _deduce_alias(self, opts: Iterable[str]) -> str:
        """Internal helper to deduce a clean Python attribute name from option strings."""

        return self._sort_opts(opts)[-1].lstrip(self.prefix_chars).replace("-", "_")

    def _add_title_box_to_output(
        self,
        output: list[Renderable],
        console_width: int,
        *,
        title: TextRenderable | object | None = None,
        subtitle: TextRenderable | object | None = None,
        inline_subtitle: bool = True,
        box_color: FgColorStyle | None = None,
    ) -> None:
        """Internal method to add a title and subtitle banner box to the output."""

        title_obj = self.title if title is None else title
        sub_obj = self.subtitle if subtitle is None else subtitle

        if not title_obj and not sub_obj:
            return

        title_st = _to_styled_text(title_obj) if title_obj else None
        sub_st = _to_styled_text(sub_obj) if sub_obj else None

        inner_width = max(console_width - 4, 1)
        single_line_len = (len(title_st.raw) if title_st else 0) + (len(sub_st.raw) + 3 if sub_st else 0)
        has_newlines = ("\n" in title_st.raw if title_st else False) or ("\n" in sub_st.raw if sub_st else False)

        box_bg_st: AnyStyle = (S.hex("000") | box_color.to_bg()) if is_fg_color_style(box_color) else (S.RESET | S.INVERSE)
        box_fg_st: AnyStyle = box_color if is_fg_color_style(box_color) else S.RESET

        if inline_subtitle and title_st and not has_newlines and ((single_line_len + 4) <= console_width):
            title_renderable: Renderable = (S.BOLD(title_st), " — ", sub_st) if sub_st else S.BOLD(title_st)

            output.extend([
                box_fg_st("▄" * console_width),
                box_bg_st("  ", title_renderable, " " * (console_width - 2 - single_line_len)),
                box_fg_st("▀" * console_width),
                "",
            ])

        else:
            output.append(box_fg_st("▄" * console_width))

            if title_st:
                for title_line in _wrap_text(S.BOLD(title_st), inner_width):
                    output.append(box_bg_st("  ", title_line, " " * max(0, inner_width - len(title_line)), "  "))

            if sub_st:
                for subtitle_line in _wrap_text(sub_st, inner_width):
                    output.append(box_bg_st("  ", subtitle_line, " " * max(0, inner_width - len(subtitle_line)), "  "))

            output.extend([box_fg_st("▀" * console_width), ""])

    def _add_usage_to_output(
        self,
        output: list[Renderable],
        cmd_st: StyledText,
        args_st: StyledText,
        opts_st: StyledText,
    ) -> None:
        """Internal method to add the usage line to the help output."""

        if self.usage is None:
            usage_parts: list[Renderable | StyledText] = [(S.RESET, S.BOLD("Usage:")), cmd_st]

            if args_st.raw:
                usage_parts.append(args_st)
            if opts_st.raw:
                usage_parts.append(opts_st)

            output.append(StyledText(" ").join(usage_parts))

        else:
            output.append(
                (self.usage if isinstance(self.usage, StyledText) else StyledText(self.usage))
                .ansi.replace("{cmd}", cmd_st.ansi)
                .replace("{args}", args_st.ansi)
                .replace("{opts}", opts_st.ansi)
            )

        output.append("")

    def _get_args_help_items(self) -> list[tuple[StyledText, Renderable]]:
        """Internal method to collect help items for positional arguments."""

        args_items: list[tuple[StyledText, Renderable]] = []

        for name in self._args_order:
            cfg = self._arg_configs[name]
            l_br, r_br = ("<", ">") if cfg["required"] else ("[", "]")

            match nargs := cfg["nargs"]:
                case "*" | "+":
                    label_st = StyledText(S.BR.CYAN(f"{l_br}{name}...{r_br}"))
                case int(n) if n > 1:
                    label_st = StyledText(S.BR.CYAN(l_br, name, " "), S.DIM(f"[{nargs}]"), S.BR.CYAN(r_br))
                case _:
                    label_st = StyledText(S.BR.CYAN(f"{l_br}{name}{r_br}"))

            args_items.append((label_st, cfg["help"] or ""))

        return args_items

    def _get_opts_help_items(self, has_opts: bool) -> list[tuple[StyledText, Renderable]]:
        """Internal method to collect help items for options."""

        if not has_opts and not self.help_opts:
            return []

        opts_items: list[tuple[StyledText, Renderable]] = [
            (self._opts_to_st(self.help_opts), "Show this help message and exit")
        ]

        sep_st: Renderable = S.DIM(self.opt_value_sep) if self.opt_value_sep else " "

        for _, cfg in self._arg_configs.items():
            if cfg["opts"] is not None:
                opt_st = self._opts_to_st(cfg["opts"])

                if cfg["expects_value"] is not None:
                    if cfg["optional_value"]:
                        opt_st += (S.BR.BLUE(sep_st, cfg["expects_value"]), (S.BOLD | S.BLUE)("?"))
                    else:
                        opt_st += S.BR.BLUE(sep_st, cfg["expects_value"])

                opts_items.append((opt_st, cfg["help"] or ""))

        return opts_items

    def _get_controls_help_items(self) -> list[tuple[StyledText, Renderable]]:
        """Internal method to collect help items for controls."""

        if not self.controls:
            return []

        controls_items: list[tuple[StyledText, Renderable]] = []

        for control, help in self.controls:
            key_list = [control] if isinstance(control, str) else list(control)
            formatted_keys = [StyledText(S.BR.RED(S.DIM("+").join(k.split("+")))) for k in key_list]
            controls_items.append((StyledText(", ").join(formatted_keys), help))

        return controls_items

    def _add_section_to_output(
        self,
        output: list[Renderable],
        title: str,
        items: list[tuple[StyledText, Renderable]],
        max_col_width: int,
        console_width: int,
    ) -> None:
        """Internal method to add a section with aligned items to the help output."""

        if not items:
            return

        output.append((S.RESET, S.BOLD(title)))

        desc_col = max_col_width + 6
        desc_width = max(console_width - desc_col, 10)

        for left_st, help in items:
            if not help:
                output.append(("  ", left_st))
                continue

            wrapped_lines = _wrap_text(help, desc_width)

            output.append(("  ", left_st, " " * (max_col_width - len(left_st.raw) + 4), wrapped_lines[0]))
            for continuation_line in wrapped_lines[1:]:
                output.append((" " * desc_col, continuation_line))

        output.append("")

    def _highlight_token(
        self,
        token: str,
        cmd_name: str,
        all_opts: set[str],
        value_opts: set[str],
        state: list[bool],
    ) -> str:
        """Internal helper to syntax-highlight a single CLI token."""

        # state: [expecting_value, seen_pos, saw_double_dash]

        if token.startswith("{cmd}"):
            suffix = token[5:]
            state[0] = False
            return StyledText(S.BR.GREEN(cmd_name), S.DIM(suffix) if suffix else "").ansi

        if token == "--":
            state[0] = False
            state[2] = True
            return StyledText(S.BR.BLUE(token)).ansi

        if state[2] or state[0]:
            is_opt_val = state[0]
            state[0] = False
            return StyledText(S.BR.BLUE(token) if is_opt_val else S.BR.CYAN(token)).ansi

        if self.opt_value_sep and self.opt_value_sep in token:
            opt_prefix, opt_val = token.split(self.opt_value_sep, 1)
            if opt_prefix in all_opts or ((self.intermixed or not state[1]) and self._opt_pattern.fullmatch(opt_prefix)):
                return StyledText(S.BR.BLUE(opt_prefix, S.DIM(self.opt_value_sep), opt_val)).ansi
            state[1] = True
            return StyledText(S.BR.CYAN(token)).ansi

        if token in all_opts:
            if not self.intermixed and state[1]:
                return StyledText(S.BR.CYAN(token)).ansi
            if token in value_opts:
                state[0] = True
            return StyledText(S.BR.BLUE(token)).ansi

        if _is_number(token):
            state[1] = True
            return StyledText(S.BR.CYAN(token)).ansi

        if self._opt_pattern.fullmatch(token):
            if not self.intermixed and state[1]:
                return StyledText(S.BR.CYAN(token)).ansi
            return StyledText(S.BR.BLUE(token)).ansi

        state[1] = True
        return StyledText(S.BR.CYAN(token)).ansi

    def _highlight_example(self, example_cmd: str, cmd_name: str) -> StyledText:
        """Internal method to syntax-highlight the left command part of an example."""

        all_opts: set[str] = set()
        value_opts: set[str] = set()

        for arg_config in self._arg_configs.values():
            if arg_config["opts"] is not None:
                for opt in arg_config["opts"]:
                    all_opts.add(opt)
                    if arg_config["expects_value"] is not None:
                        value_opts.add(opt)

        parts: list[str] = []
        last_idx: int = 0
        state: list[bool] = [False, False, False]

        for match in _PATTERNS.cli_token.finditer(example_cmd):
            parts.append(example_cmd[last_idx : match.start()])
            parts.append(self._highlight_token(match.group(0), cmd_name, all_opts, value_opts, state))
            last_idx = match.end()

        parts.append(example_cmd[last_idx:])
        result = StyledText.__new__(StyledText)
        result.ansi = "".join(parts)

        return result

    def _add_examples_to_output(
        self,
        output: list[Renderable],
        cmd_name_ext: tuple[str, str],
        console_width: int,
    ) -> None:
        """Internal method to add the examples section to the help output."""

        if not self.examples:
            return

        output.append((S.RESET, S.BOLD("Examples:")))

        highlighted_examples: list[tuple[StyledText, Renderable]] = [
            (self._highlight_example(example_cmd, cmd_name_ext[0]), comment) for example_cmd, comment in self.examples
        ]
        max_example_len = max([len(cmd_st.raw) for cmd_st, _ in highlighted_examples], default=0)

        fits_wide = True
        for _, comment in highlighted_examples:
            desc_raw_len = 2 + len(comment if isinstance(comment, str) else StyledText(comment).raw)
            line_len = 2 + max_example_len + 4 + desc_raw_len

            if line_len > console_width:
                fits_wide = False
                break

        if fits_wide:
            for cmd_st, comment in highlighted_examples:
                output.append(("  ", cmd_st, " " * (max_example_len - len(cmd_st.raw) + 4), S.DIM("# ", S.ITALIC(comment))))

        else:
            for cmd_st, comment in highlighted_examples:
                for desc_line in _wrap_text(comment, max(console_width - 4, 10)):
                    output.append(("  ", S.DIM("# ", S.ITALIC(desc_line))))
                output.append(("  ", cmd_st))

        output.append("")

    def print_help(self) -> None:
        """Print the generated help screen."""

        cmd_exe = Path(_sys.argv[0])
        cmd_name_ext: tuple[str, str] = (cmd_exe.stem, cmd_exe.suffix)

        has_opts = False
        for cfg in self._arg_configs.values():
            if cfg["opts"] is not None:
                has_opts = True
                break

        args_items = self._get_args_help_items()
        opts_items = self._get_opts_help_items(has_opts)
        controls_items = self._get_controls_help_items()

        cmd_st = StyledText(S.BR.GREEN(cmd_name_ext[0], S.DIM(cmd_name_ext[1]) if cmd_name_ext[1] else ""))
        args_st = StyledText(" ").join([item[0] for item in args_items])
        opts_st = StyledText(S.BR.BLUE("[options]") if has_opts else "")

        max_col_width = max(
            [len(left_st.raw) for left_st, _ in (*args_items, *opts_items, *controls_items)],
            default=0,
        )

        console_width = get_width()
        output: list[Renderable] = [""]

        self._add_title_box_to_output(output, console_width)

        if self.notice is not None:
            output.append(_to_styled_text(self.notice))
            output.append("")

        self._add_usage_to_output(output, cmd_st, args_st, opts_st)
        self._add_section_to_output(output, "Arguments:", args_items, max_col_width, console_width)
        self._add_section_to_output(output, "Options:", opts_items, max_col_width, console_width)
        self._add_section_to_output(output, "Controls:", controls_items, max_col_width, console_width)
        self._add_examples_to_output(output, cmd_name_ext, console_width)

        if self.epilog is not None:
            output.append(_to_styled_text(self.epilog))
            output.append("")

        StyledText(*output, "", sep="\n").print(flush=True)

    def _error(self, message: TextRenderable | object, exit_code: int = 1) -> NoReturn:
        """Internal method to print an error message with a help notice and exit the program."""

        title = self.title or (Path(_sys.argv[0]).stem if _sys.argv and _sys.argv[0] else "")

        console_width = get_width()
        output: list[Renderable] = [""]

        self._add_title_box_to_output(
            output,
            console_width,
            title=f"{title} ERROR" if title else "ERROR",
            subtitle=_to_styled_text(message),
            inline_subtitle=False,
            box_color=S.BR.RED,
        )

        help_opt_st = S.BR.BLUE(self._sort_opts(self.help_opts)[-1] if self.help_opts else "--help")
        output.append(S.DIM("  Run with ", help_opt_st, " for usage and available options."))

        StyledText(*output, "\n", sep="\n").print(flush=True)

        raise SystemExit(exit_code)

    def _build_opt_map(self) -> dict[str, str]:
        """Internal method to build a mapping of options to their corresponding argument aliases."""

        opt_map: dict[str, str] = {}

        for alias, cfg in self._arg_configs.items():
            if cfg["opts"] is not None:
                for opt in cfg["opts"]:
                    opt_map[opt] = alias

        return opt_map

    def _consume_opt(
        self,
        raw_args: list[str],
        i: int,
        potential_opt: str,
        potential_val: str | None,
        alias: str,
        opt_map: dict[str, str],
        parsed_data: dict[str, dict[str, Any]],
        allow_space_value: bool,
    ) -> int:
        """Internal helper to consume an option and its value during argument parsing."""

        cfg = self._arg_configs[alias]
        parsed_data[alias]["exists"] = True
        parsed_data[alias]["opt"] = potential_opt

        if cfg["expects_value"] is None:
            return i

        if potential_val is not None:
            parsed_data[alias]["values"].append(potential_val)
            return i

        if (
            allow_space_value
            and i + 1 < len(raw_args)
            and raw_args[i + 1] not in opt_map
            and raw_args[i + 1] not in self.help_opts
            and raw_args[i + 1] != "--"
        ):
            parsed_data[alias]["values"].append(raw_args[i + 1])
            return i + 1

        if not cfg["optional_value"]:
            opt_details: list[Renderable] = [f"Option '{potential_opt}' requires a value"]
            extra: list[str] = []

            if cfg["expects_value"]:
                extra.append(f"expected <{cfg['expects_value']}>")
            if cfg["choices"]:
                extra.append(f"choices: {', '.join(cfg['choices'])}")

            if extra:
                opt_details.append(S.DIM(f" ({'; '.join(extra)})"))

            self._error(StyledText(*opt_details))

        return i

    def _parse_args_loop(
        self,
        raw_args: list[str],
        opt_map: dict[str, str],
        parsed_data: dict[str, dict[str, Any]],
        arg_tokens: list[str],
        opt_value_sep: str | None,
        allow_space_value: bool,
        intermixed: bool,
    ) -> None:
        """Internal method to loop through the raw arguments and populate the parsed data."""

        i = 0

        while i < len(raw_args):
            arg = raw_args[i]

            if arg == "--":
                arg_tokens.extend(raw_args[i + 1 :])
                break

            if opt_value_sep and opt_value_sep in arg:
                parts = arg.split(opt_value_sep, 1)
                potential_opt, potential_val = parts[0], parts[1]
            else:
                potential_opt, potential_val = arg, None

            if potential_opt in self.help_opts:
                self.print_help()
                raise SystemExit(0)

            if potential_opt in opt_map:
                i = self._consume_opt(
                    raw_args,
                    i,
                    potential_opt,
                    potential_val,
                    opt_map[potential_opt],
                    opt_map,
                    parsed_data,
                    allow_space_value,
                )

            elif _is_number(arg) or not self._opt_pattern.fullmatch(potential_opt):
                if not intermixed:
                    arg_tokens.extend(raw_args[i:])
                    break
                arg_tokens.append(arg)

            else:
                self._error(f"Unrecognized option: '{potential_opt}'")

            i += 1

    def _calculate_remaining_min(self, arg_idx: int) -> int:
        """Internal helper to calculate minimum positional tokens required by subsequent arguments."""

        total = 0
        for next_name in self._args_order[arg_idx + 1 :]:
            sub_cfg = self._arg_configs[next_name]
            if sub_cfg["required"]:
                sub_nargs = sub_cfg["nargs"]
                if isinstance(sub_nargs, int):
                    total += sub_nargs
                elif sub_nargs == "+":
                    total += 1

        return total

    def _consume_arg(
        self,
        name: str,
        cfg: ArgConfigDict,
        arg_tokens: list[str],
        token_idx: int,
        available: int,
        num_tokens: int,
        parsed_data: dict[str, dict[str, Any]],
    ) -> int:
        """Internal helper to consume positional tokens for a specific positional argument configuration."""

        nargs = cfg["nargs"]

        if isinstance(nargs, int):
            if available >= nargs and token_idx + nargs <= num_tokens:
                parsed_data[name]["values"] = arg_tokens[token_idx : token_idx + nargs]
                parsed_data[name]["exists"] = True

                return token_idx + nargs

            if not cfg["required"] and available == 0:
                parsed_data[name]["values"] = []
                parsed_data[name]["exists"] = False

                return token_idx

            arg_details: list[Renderable] = [f"Missing required argument '{name}'"]
            if cfg["choices"]:
                arg_details.append(S.DIM(f" (choices: {', '.join(cfg['choices'])})"))

            self._error(StyledText(*arg_details))

        if (count := min(available, 1) if nargs == "?" else available) < 1:
            parsed_data[name]["values"] = []
            parsed_data[name]["exists"] = False

            if cfg["required"]:
                arg_details_req: list[Renderable] = [f"Missing required argument '{name}'"]
                if cfg["choices"]:
                    arg_details_req.append(S.DIM(f" (choices: {', '.join(cfg['choices'])})"))

                self._error(StyledText(*arg_details_req))

            return token_idx

        parsed_data[name]["values"] = arg_tokens[token_idx : token_idx + count]
        parsed_data[name]["exists"] = True

        return token_idx + count

    def _resolve_args(
        self,
        parsed_data: dict[str, dict[str, Any]],
        arg_tokens: list[str],
    ) -> None:
        """Internal method to resolve positional arguments and assign them to the appropriate aliases."""

        num_tokens = len(arg_tokens)

        if not self._args_order:
            if num_tokens > 0:
                self._error(f"Unrecognized argument: '{arg_tokens[0]}'")
            return

        token_idx = 0

        for arg_idx, name in enumerate(self._args_order):
            available = max(0, num_tokens - token_idx - self._calculate_remaining_min(arg_idx))
            token_idx = self._consume_arg(
                name, self._arg_configs[name], arg_tokens, token_idx, available, num_tokens, parsed_data
            )

        if token_idx < num_tokens:
            self._error(f"Unrecognized argument: '{arg_tokens[token_idx]}'")

    def _validate_parsed_data(self, parsed_data: dict[str, dict[str, Any]]) -> None:
        """Internal method to validate the parsed data against the argument configurations."""

        for alias, cfg in self._arg_configs.items():
            if cfg["required"] and not parsed_data[alias]["exists"]:
                if cfg["is_arg"]:
                    arg_details: list[Renderable] = [f"Missing required argument '{alias}'"]
                    if cfg["choices"]:
                        arg_details.append(S.DIM(f" (choices: {', '.join(cfg['choices'])})"))

                    self._error(StyledText(*arg_details))

                else:
                    self._error(
                        StyledText(
                            f"Missing required option '{alias}'",
                            S.DIM(f" ({', '.join(self._sort_opts(cast('Iterable[str]', cfg['opts'])))})"),
                        )
                    )

            if cfg["choices"] and parsed_data[alias]["exists"]:
                for val in parsed_data[alias]["values"]:
                    if val not in cfg["choices"]:
                        choice_details: list[Renderable] = [f"Invalid choice '{val}' for '{alias}'"]
                        if cfg["opts"] is not None:
                            choice_details.append(S.DIM(f" ({', '.join(self._sort_opts(cfg['opts']))})"))
                        choice_details.append(f"\nAllowed: {', '.join(cfg['choices'])}")

                        self._error(StyledText(*choice_details))

    def parse(
        self,
        *,
        skip: int = 0,
        opt_value_sep: str | object | None = _OPT_SEP_DEFAULT,
        allow_space_value: bool = True,
        intermixed: bool | None = None,
    ) -> ParsedArgs:
        """Parse `sys.argv` and return the strongly-typed `ParsedArgs` object.\n
        ----------------------------------------------------------------------------------------------------
        *   `skip` – Number of arguments to skip at the start.
        *   `opt_value_sep` – String separating option from value (e.g., `"="` for `--foo=bar`).<br>
            Defaults to `self.opt_value_sep` if omitted. Set to `None` to disable.
        *   `allow_space_value` – Whether to allow space-separated values
            for options (e.g., `--foo bar`).
        *   `intermixed` – Whether options and positional arguments can be intermixed<br>
            (defaults to `self.intermixed` if not specified).\n
        ----------------------------------------------------------------------------------------------------
        Returns the `ParsedArgs` container."""

        raw_args = _sys.argv[1 + skip :]
        result = ParsedArgs()

        opt_map = self._build_opt_map()
        parsed_data: dict[str, dict[str, Any]] = {
            alias: {"exists": False, "values": [], "is_arg": cfg["is_arg"], "opt": None}
            for alias, cfg in self._arg_configs.items()
        }
        arg_tokens: list[str] = []

        should_intermix = self.intermixed if intermixed is None else intermixed
        resolved_opt_sep = self.opt_value_sep if opt_value_sep is _OPT_SEP_DEFAULT else cast("str | None", opt_value_sep)

        self._parse_args_loop(
            raw_args,
            opt_map,
            parsed_data,
            arg_tokens,
            resolved_opt_sep,
            allow_space_value,
            should_intermix,
        )
        self._resolve_args(parsed_data, arg_tokens)
        self._validate_parsed_data(parsed_data)

        for alias, data in parsed_data.items():
            result._add_arg(
                alias,
                ParsedArgData(exists=data["exists"], values=tuple(data["values"]), is_arg=data["is_arg"], opt=data["opt"]),
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
            kernel32 = _ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.GetStdHandle(-11)  # pyright:ignore[reportUnknownMemberType,reportUnknownVariableType]
            mode = _ctypes.c_ulong()

            if kernel32.GetConsoleMode(handle, _ctypes.byref(mode)):  # pyright:ignore[reportUnknownMemberType]
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
) -> NoReturn: ...
@overload
def pause_exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    pause: bool = ...,
    exit: Literal[False] = ...,
    exit_code: int = ...,
) -> None: ...
@overload
def pause_exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
) -> None: ...


def pause_exit(
    prompt: TextRenderable | object = "",
    /,
    *,
    pause: bool = True,
    exit: bool = False,
    exit_code: int = 0,
) -> None:
    """Will print the `prompt` and then pause and/or exit the program based on the given options.\n
    ----------------------------------------------------------------------------------------------------
    *   `prompt` – The message to print before pausing/exiting (any object, or a `StyledText` object).
    *   `pause` – Whether to pause and wait for a key press after printing the prompt.
    *   `exit` – Whether to exit the program after printing
        the prompt (and pausing if `pause` is true).
    *   `exit_code` – The exit code to use when exiting the program."""

    _to_styled_text(prompt).print(end="", flush=True)

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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    tab_size: int = 8,
    title_px: int = 1,
    title_mx: int = 2,
) -> None:
    """Prints a nicely formatted log message.\n
    ----------------------------------------------------------------------------------------------------
    *   `title` – The title of the log message (e.g., `DEBUG`, `WARN`, `FAIL`, …).
    *   `prompt` – The log message (any object, or a `StyledText` object for styled output).
    *   `start` – Something to print before the log is printed.
    *   `end` – Something to print after the log is printed (e.g., `\\n`).
    *   `title_bg_color` – The background color of the `title`<br>
        (an `S` background style, RGBA, or HEXA color).
    *   `default_color` – The default text color of the `prompt` (RGBA or HEXA).
    *   `tab_size` – The tab size used for the log (default is 8 – matches terminal tabs).
    *   `title_px` – The horizontal padding (in chars) to the title (if `title_bg_color` is set).
    *   `title_mx` – The horizontal margin (in chars) to the title.\n
    ----------------------------------------------------------------------------------------------------
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

    # Convert the prompt to styled text and apply the optional default color:
    prompt_st: _StyledSequence | StyledText = _to_styled_text(prompt)
    if default_color is not None:
        prompt_st = _as_fg_style(default_color, param_name="default_color")(prompt_st)

    # Wrap prompt text to the next line with proper indentation after the title and tab:
    joined_prompt = StyledText(f"\n{' ' * title_len + tab}").join(prompt_st.wrap(wrap_len))

    if title == "":
        StyledText(f"{start}{mx}", joined_prompt, sep="").print(end=end)
    else:
        title_ansi = _render_log_title(f"{px}{title}{px}", title_style)
        StyledText(f"{start}{mx}", title_ansi, f"{mx}{tab}", joined_prompt, sep="").print(end=end)


def _log_preset(
    title: str,
    prompt: TextRenderable | object,
    title_bg_color: BaseStyle | Rgba | Hexa | None,
    start: str,
    end: str,
    default_color: FgColorStyle | Rgba | Hexa | None,
    pause: bool,
    do_exit: bool,
    exit_code: int,
    /,
) -> None:
    log(title, prompt, start=start, end=end, title_bg_color=title_bg_color, default_color=default_color)
    pause_exit("", pause=pause, exit=do_exit, exit_code=exit_code)


def debug(
    prompt: TextRenderable | object = "Point in program reached.",
    /,
    *,
    active: bool = True,
    start: str = "",
    end: str = "\n",
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 0,
) -> None:
    """A preset for `log()`: `DEBUG` log message with the options to pause<br>
    at the message and exit the program after the message was printed.\n
    If `active` is false, no debug message will be printed."""

    if active:
        _log_preset("DEBUG", prompt, S.BG.BR.YELLOW, start, end, default_color, pause, exit, exit_code)


def info(
    prompt: TextRenderable | object = "Program running.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 0,
) -> None:
    """A preset for `log()`: `INFO` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("INFO", prompt, S.BG.BR.BLUE, start, end, default_color, pause, exit, exit_code)


@overload
def done(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True],
    exit_code: int = ...,
) -> NoReturn: ...
@overload
def done(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False] = ...,
    exit_code: int = ...,
) -> None: ...
@overload
def done(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
) -> None: ...


def done(
    prompt: TextRenderable | object = "Program finished.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 0,
) -> None:
    """A preset for `log()`: `DONE` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("DONE", prompt, S.BG.BR.GREEN, start, end, default_color, pause, exit, exit_code)


@overload
def warn(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True],
    exit_code: int = ...,
) -> NoReturn: ...
@overload
def warn(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False] = ...,
    exit_code: int = ...,
) -> None: ...
@overload
def warn(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
) -> None: ...


def warn(
    prompt: TextRenderable | object = "Important message.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = False,
    exit_code: int = 1,
) -> None:
    """A preset for `log()`: `WARN` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("WARN", prompt, S.BG.BR.YELLOW, start, end, default_color, pause, exit, exit_code)


@overload
def fail(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True] = ...,
    exit_code: int = ...,
) -> NoReturn: ...
@overload
def fail(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False],
    exit_code: int = ...,
) -> None: ...
@overload
def fail(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
) -> None: ...


def fail(
    prompt: TextRenderable | object = "Program error.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = True,
    exit_code: int = 1,
) -> None:
    """A preset for `log()`: `FAIL` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    _log_preset("FAIL", prompt, S.BG.BR.RED, start, end, default_color, pause, exit, exit_code)


@overload
def exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[True] = ...,
    exit_code: int = ...,
) -> NoReturn: ...
@overload
def exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: Literal[False],
    exit_code: int = ...,
) -> None: ...
@overload
def exit(
    prompt: TextRenderable | object = ...,
    /,
    *,
    start: str = ...,
    end: str = ...,
    default_color: FgColorStyle | Rgba | Hexa | None = ...,
    pause: bool = ...,
    exit: bool,
    exit_code: int = ...,
) -> None: ...


def exit(
    prompt: TextRenderable | object = "Program ended.",
    /,
    *,
    start: str = "",
    end: str = "\n",
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    pause: bool = False,
    exit: bool = True,
    exit_code: int = 0,
) -> None:
    """A preset for `log()`: `EXIT` log message with the options to pause<br>
    at the message and exit the program after the message was printed."""

    log("EXIT", prompt, start=start, end=end, title_bg_color=S.BG.BR.MAGENTA, default_color=default_color)
    pause_exit("", pause=pause, exit=exit, exit_code=exit_code)


def log_box_filled(
    *values: TextRenderable | object,
    start: str = "",
    end: str = "\n",
    box_bg_color: AnyStyle | Rgba | Hexa | None = None,
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    w_padding: int = 2,
    w_full: bool = False,
    indent: int = 0,
) -> None:
    """Will print a box with a colored background, containing a log message.\n
    ----------------------------------------------------------------------------------------------------
    *   `*values` – The box content (any objects, or `StyledText` objects, one per line).
    *   `start` – Something to print before the log box is printed (e.g., `\\n`).
    *   `end` – Something to print after the log box is printed (e.g., `\\n`).
    *   `box_bg_color` – The background color of the box<br>
        (an `S` background style, RGBA, or HEXA color).
    *   `default_color` – The default text color of the `*values`.
    *   `w_padding` – The horizontal padding (in chars) to the box content.
    *   `w_full` – Whether to make the box be the full terminal width or not.
    *   `indent` – The indentation of the box (in chars).\n
    ----------------------------------------------------------------------------------------------------
    To style the content, pass `StyledText` objects. For more detailed<br>
    information about styling, see the `ansi` module documentation."""

    if w_padding < 0:
        raise ValueError(f"The 'w_padding' parameter must be a non-negative integer, got {w_padding!r}")
    if indent < 0:
        raise ValueError(f"The 'indent' parameter must be a non-negative integer, got {indent!r}")

    fg_style = _as_fg_style(default_color, fallback="#000", param_name="default_color")

    # If no box BG color is set, use the console foreground color as the box BG (via inversion):
    bg_style: AnyStyle = (
        (S.RESET_FG | S.INVERSE | fg_style) if box_bg_color is None else _as_bg_style(box_bg_color, param_name="box_bg_color")
    )

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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    w_padding: int = 1,
    w_full: bool = False,
    indent: int = 0,
    border_chars: tuple[str, str, str, str, str, str, str, str, str, str, str] | None = None,
) -> None:
    """Will print a bordered box, containing a log message.\n
    ----------------------------------------------------------------------------------------------------
    *   `*values` – The box content (any objects, or `StyledText` objects, one per line).
    *   `start` – Something to print before the log box is printed (e.g., `\\n`).
    *   `end` – Something to print after the log box is printed (e.g., `\\n`).
    *   `border_type` – One of the predefined border character sets.
    *   `border_style` – The style of the border (an `S` style, RGBA, or HEXA color).
    *   `default_color` – The default text color of the `*values`.
    *   `w_padding` – The horizontal padding (in chars) to the box content.
    *   `w_full` – Whether to make the box be the full terminal width or not.
    *   `indent` – The indentation of the box (in chars).
    *   `border_chars` – Define your own border characters set (overwrites `border_type`).\n
    ----------------------------------------------------------------------------------------------------
    You can insert horizontal rules to split the box content by using `{hr}` in the `*values`.\n
    ----------------------------------------------------------------------------------------------------
    To style the content, pass `StyledText` objects. For more detailed<br>
    information about styling, see the `ansi` module documentation.\n
    ----------------------------------------------------------------------------------------------------
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
                raise ValueError(f"List values must be single-char strings, got {border_chars!r}")

    border_open = StyledText(_as_fg_style(border_style, param_name="border_style")).ansi
    content_open = (
        StyledText(_as_fg_style(default_color, param_name="default_color")).ansi if default_color is not None else ""
    )
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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
    default_is_yes: bool = True,
) -> bool:
    """Ask a yes/no question.\n
    ----------------------------------------------------------------------------------------------------
    *   `prompt` – The input prompt (any object, or a `StyledText` object for styled output).
    *   `start` – Something to print before the input.
    *   `end` – Something to print after the input (e.g., `\\n`).
    *   `default_color` – The default text color of the `prompt`.
    *   `default_is_yes` – The default answer if the user just presses enter.\n
    ----------------------------------------------------------------------------------------------------
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
    head_seg = _as_fg_style(default_color, param_name="default_color")(head) if default_color is not None else head

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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
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
    *   `reset_ansi` – Whether to reset the ANSI codes after the user confirms the input.\n
    ------------------------------------------------------------------------------------------
    To style the `prompt`, pass a `StyledText` object. For more detailed<br>
    information about styling, see the `ansi` module documentation."""

    kb = KeyBindings()
    kb.add("c-d", eager=True)(_multiline_input_submit)

    head = f"{start}{_to_styled_text(prompt).ansi}"
    head_seg = _as_fg_style(default_color, param_name="default_color")(head) if default_color is not None else head
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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
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
    default_color: FgColorStyle | Rgba | Hexa | None = None,
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
    ----------------------------------------------------------------------------------------------------
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
    *   `output_type` – The type (class) to convert the input to before returning it.\n
    ----------------------------------------------------------------------------------------------------
    To style the `prompt`, pass a `StyledText` object. For more detailed<br>
    information about styling, see the `ansi` module documentation.\n
    ----------------------------------------------------------------------------------------------------
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
        prompt_ansi = StyledText(_as_fg_style(default_color, param_name="default_color")(prompt_ansi)).ansi

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
        import msvcrt as _msvcrt

        _msvcrt.getch()  # type: ignore[attr-defined]

    else:
        import termios as _termios
        import tty as _tty

        fd = _sys.stdin.fileno()
        old_settings = _termios.tcgetattr(fd)  # type:ignore[attr-defined]

        try:
            _tty.setraw(fd)  # type:ignore[attr-defined]
            _sys.stdin.read(1)
        finally:
            _termios.tcsetattr(fd, _termios.TCSADRAIN, old_settings)  # type:ignore[attr-defined]


def _resolve_title_colors(title_bg_color: object, /) -> tuple[AnyStyle, BaseStyle]:
    """Resolves the log title's background style and its matching foreground style.\n
    ----------------------------------------------------------------------------------------------------
    *   `title_bg_color` – An `S` background style (black text is used on it) or an<br>
        RGBA/HEXA color (the best-contrast black or white text is computed for it)."""

    if is_any_style(title_bg_color):
        return title_bg_color, S.BLACK

    if _color_module.is_valid_rgba(title_bg_color) or _color_module.is_valid_hexa(title_bg_color):
        hexa_bg = _color_module.to_hexa(title_bg_color)
        return S.BG.hex(str(hexa_bg)), S.hex(str(_color_module.text_color_for_on_bg(hexa_bg)))

    raise ValueError(
        "The 'title_bg_color' parameter must be a valid background style (e.g., 'S.BG.BLUE'), "
        f"RGBA color, or HEXA color, got {title_bg_color!r}"
    )


def _as_bg_style(color: object, /, *, param_name: str = "box_bg_color") -> AnyStyle:
    """Resolves an `S` background style or an RGBA/HEXA color to an `S` background style."""

    if is_any_style(color):
        return color
    if _color_module.is_valid_rgba(color) or _color_module.is_valid_hexa(color):
        return S.BG.hex(str(_color_module.to_hexa(color)))

    raise ValueError(
        f"The {param_name!r} parameter must be a valid background style (e.g., 'S.BG.BLUE'), "
        f"RGBA color, or HEXA color, got {color!r}"
    )


def _as_fg_style(color: object, /, *, fallback: str = "#000", param_name: str = "color") -> AnyStyle:
    """Resolves an `S` style, an RGBA/HEXA color, or `None` (returns fallback) to an `S` foreground style."""

    if color is None:
        return S.hex(fallback)
    if is_any_style(color):
        return color
    if _color_module.is_valid_rgba(color) or _color_module.is_valid_hexa(color):
        return S.hex(str(_color_module.to_hexa(color)))

    raise ValueError(
        f"The {param_name!r} parameter must be a valid style (e.g., 'S.DIM | S.BR.BLUE'), "
        f"RGBA color, or HEXA color, got {color!r}"
    )


def _persist_style(ansi_text: str, style_open: str, /) -> str:
    """Re-inserts `style_open` right after every ANSI escape sequence in `ansi_text`,<br>
    so the style keeps applying even across (e.g., full) resets contained in the text."""

    if not style_open or ANSI.CHAR not in ansi_text:
        return ansi_text

    return ANSI.SEQ_PATTERN.sub(r"\g<0>" + style_open.replace("\\", r"\\"), ansi_text)


def _render_log_title(text: str, style: AnyStyle, /) -> str:
    """Renders (and caches) the styled log title as an ANSI string.\n
    ----------------------------------------------------------------------------------------------------
    Since consecutive log calls often reuse the exact same title and style,<br>
    the rendered string is cached and reused instead of being rebuilt."""

    key = (text, repr(style))

    if (cached := _LOG_TITLE_CACHE.get(key)) is None:
        cached = StyledText(style(text)).ansi
        if len(_LOG_TITLE_CACHE) < _LOG_TITLE_CACHE_MAX:
            _LOG_TITLE_CACHE[key] = cached

    return cached


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

        with _suppress(Exception):
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

    def remove_text_event(self, event: KeyPressEvent, /, *, is_backspace: bool = False) -> None:
        """Handles text removal events (backspace/delete)."""

        with _suppress(Exception):
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
    ----------------------------------------------------------------------------------------------------
    *   `min_width` – The min width of the progress bar in chars.
    *   `max_width` – The max width of the progress bar in chars.
    *   `format` – The format strings used to render the progress bar, containing placeholders:
        -   `{label}` `{l}`
        -   `{bar}` `{b}`
        -   `{current}` `{c}`
            (optional `:<char>` format specifier for thousands separator, e.g., `{c:,}`)
        -   `{total}` `{t}`
            (optional `:<char>` format specifier for thousands separator, e.g., `{t:,}`)
        -   `{percentage}` `{percent}` `{p}` (optional `:.<num>f` format specifier to round<br>
            to specified number of decimal places, e.g., `{p:.1f}`)
    *   `limited_format` – A simplified format string used when the terminal width is too small<br>
        for the normal `format`.
    *   `chars` – A tuple of characters ordered from full to empty progress:<br>
        The first character represents completely filled sections.<br>
        Intermediate characters create smooth transitions<br>
        The last character represents empty sections.\n
    ----------------------------------------------------------------------------------------------------
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
        ----------------------------------------------------------------------------------------------------
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
        ----------------------------------------------------------------------------------------------------
        *   `format` – The format strings used to render the progress bar, containing placeholders:
            -   `{label}` `{l}`
            -   `{bar}` `{b}`
            -   `{current}` `{c}`
                (optional `:<char>` format specifier for thousands separator, e.g., `{c:,}`)
            -   `{total}` `{t}`
                (optional `:<char>` format specifier for thousands separator, e.g., `{t:,}`)
            -   `{percentage}` `{percent}` `{p}` (optional `:.<num>f` format specifier to round<br>
                to specified number of decimal places, e.g., `{p:.1f}`)
        *   `limited_format` – A simplified format strings used when the terminal width is too small.
        *   `sep` – The separator string used to join multiple format strings.\n
        ----------------------------------------------------------------------------------------------------
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

    def set_chars(self, chars: SeqOrSet[str], /) -> None:
        """Set the characters used to render the progress bar.\n
        ----------------------------------------------------------------------------------------------------
        *   `chars` – A collection of characters ordered from full to empty progress:<br>
            The first character represents completely filled sections.<br>
            Intermediate characters create smooth transitions.<br>
            The last character represents empty sections.<br>
            If `None`, uses default Unicode block characters.\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        ProgressBar.set_chars(("█", "▓", "▒", "░", " "))
        ```"""

        if len(chars_tuple := tuple(chars)) < 2:
            raise ValueError(f"The 'chars' parameter must contain at least two characters, got {chars!r}")

        for char in chars_tuple:
            if len(char) != 1:
                raise ValueError(f"All elements in 'chars' must be single-character strings, got {char!r}")

        self.chars = chars_tuple

    def show_progress(self, current: int, total: int, /, label: StyledText | str | None = None) -> None:
        """Show or update the progress bar.\n
        ----------------------------------------------------------------------------------------------------
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
        ----------------------------------------------------------------------------------------------------
        *   `total` – The total value representing 100% progress (must be greater than `0`).
        *   `label` – An optional label which is inserted at the `{label}` or `{l}` placeholder.\n
        ----------------------------------------------------------------------------------------------------
        The returned callable accepts keyword arguments.<br>
        At least one of these parameters must be provided:
        *   `current` – Update the current progress value.
        *   `label` – Update the progress label.\n
        ----------------------------------------------------------------------------------------------------
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
    ----------------------------------------------------------------------------------------------------
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
            raise TypeError("Either the keyword argument 'current' or 'label' must be provided")

        if current is not None:
            self.current_progress = current
        if label is not None:
            self.current_label = label

        self.progress_bar.show_progress(self.current_progress, self.total, label=self.current_label)


class Throbber(_StdoutInterceptorMixin):
    """A terminal throbber for indeterminate processes with customizable appearance.<br>
    This class intercepts stdout to allow printing while the animation is active.\n
    ----------------------------------------------------------------------------------------------------
    *   `label` – The current label text.
    *   `format` – The format string used to render the throbber, containing placeholders:
        -   `{label}` `{l}`
        -   `{animation}` `{a}`
    *   `frames` – A tuple of strings representing the animation frames.
    *   `interval` – The time in seconds between each animation frame.\n
    ----------------------------------------------------------------------------------------------------
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
        self._frame_idx: int = 0
        self._stop_event: _threading.Event | None = None
        self._animation_thread: _threading.Thread | None = None

    def set_format(
        self, format: list[TextRenderable] | tuple[TextRenderable, ...] | TextRenderable, *, sep: str | None = None
    ) -> None:
        """Set the format string used to render the throbber.\n
        ----------------------------------------------------------------------------------------------------
        *   `format` – The format strings used to render the throbber, containing placeholders:
            -   `{label}` `{l}`
            -   `{animation}` `{a}`
        *   `sep` – The separator string used to join multiple format strings.\n
        ----------------------------------------------------------------------------------------------------
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

    def set_frames(self, frames: SeqOrSet[str], /) -> None:
        """Set the frames used for the throbber animation.\n
        ----------------------------------------------------------------------------------------------------
        *   `frames` – A collection of strings representing the animation frames."""

        if len(frames_tuple := tuple(frames)) < 2:
            raise ValueError(f"The 'frames' parameter must contain at least two frames, got {frames!r}")

        self.frames = frames_tuple

    def set_interval(self, interval: int | float, /) -> None:
        """Set the time interval between each animation frame.\n
        ----------------------------------------------------------------------------------------------------
        *   `interval` – The time in seconds between each animation frame."""

        if interval <= 0:
            raise ValueError(f"The 'interval' parameter must be a positive number, got {interval!r}")

        self.interval = interval

    def start(self, label: StyledText | str | None = None, /) -> None:
        """Start the throbber animation and intercept stdout.\n
        ----------------------------------------------------------------------------------------------------
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
            self._frame_idx = 0

            self._clear_intercept_line()
            self._stop_intercepting()

    def update_label(self, label: StyledText | str | None, /) -> None:
        """Update the throbber's label text.\n
        ----------------------------------------------------------------------------------------------------
        *   `new_label` – The new label text."""

        self.label = label

    @contextmanager
    def context(self, label: StyledText | str | None = None, /) -> Generator[Callable[[StyledText | str], None], None, None]:
        """Context manager for automatic cleanup. Returns a function to update the label.\n
        ----------------------------------------------------------------------------------------------------
        *   `label` – The label to display alongside the throbber.\n
        ----------------------------------------------------------------------------------------------------
        The returned callable accepts a single parameter:
        *   `new_label` – The new label text.\n
        ----------------------------------------------------------------------------------------------------
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

        self._frame_idx = 0
        while self._stop_event and not self._stop_event.is_set():
            try:
                if not self.active or not self._original_stdout:
                    break

                self._flush_buffer()

                frame = self.frames[self._frame_idx % len(self.frames)] + _ANSI_RESET
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
                self._frame_idx += 1

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
