"""
**DEPRECATED MODULE** – Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead.

This module is kept temporarily so existing internal callers and downstream code
that relies on the string-based bracket-syntax (`"[b](Hello)"`) keep working
until they are migrated to the new operator API. It will be removed in a
future release.

--------------------------------------------------------------------------------------------------------------------

This module provides the `FormatCodes` class, which includes methods to print and work with strings that
contain special formatting codes, which are then converted to ANSI codes for pretty terminal output.

--------------------------------------------------------------------------------------------------------------------
### The Easy Formatting

First, let's take a look at a small example of what a highly styled
print string with formatting could look like using this module:
```
This here is just unformatted text. [b|u|br:blue](Next we have text that is bright blue + bold + underlined.)\\n
[#000|bg:#F67](Then there's also black text with a red background.) And finally the ([i](boring)) plain text again.
```

How all of this exactly works is explained in the sections below. 🠫

--------------------------------------------------------------------------------------------------------------------
#### Formatting Codes and Keys

In this module, you can apply styles and colors using simple formatting codes.
These formatting codes consist of one or multiple different formatting keys in between square brackets.

If a formatting code is placed in a print-string, the formatting of that code
will be applied to everything behind it until its formatting is reset.
If applying multiple styles and colors in the same place, instead of writing
the formatting keys all into separate brackets (e.g. `[x][y][z]`),
they can also be put in a single pair of brackets, separated by pipes (e.g. `[x|y|z]`).

A list of all possible formatting keys can be found under all possible formatting keys.

--------------------------------------------------------------------------------------------------------------------
#### Auto Resetting Formatting Codes

Certain formatting can automatically be reset, behind a certain
amount of text, just like shown in the following example:
```
This is plain text, [br:blue](which is bright blue now.) Now it was automatically reset to plain again.
```

This will only reset formatting codes, that have a specific reset listed below.
That means if you use it where another formatting is already applied,
that formatting is still there after the automatic reset:
```
[cyan]This is cyan text, [dim](which is dimmed now.) Now it's not dimmed any more but still cyan.
```

If you want to ignore the auto-reset functionality of `()` brackets,
you can put a `\\` or `/` between them and the formatting code:
```
[cyan]This is cyan text, [u]/(which is underlined now.) And now it is still underlined and cyan.
```

--------------------------------------------------------------------------------------------------------------------
#### All possible Formatting Keys

*   RGB colors:
    Change the text color directly with an RGB color inside the square brackets.
    (With or without `rgb()` brackets doesn't matter.)
    Examples:
    -   `[rgb(115, 117, 255)]`
    -   `[(255, 0, 136)]`
    -   `[255, 0, 136]`
*   HEX colors:
    Change the text color directly with a HEX color inside the square brackets.
    (Whether the `RGB` or `RRGGBB` HEX format is used,
    and if there's a `#` or `0x` prefix, doesn't matter.)
    Examples:
    -   `[0x7788FF]`
    -   `[#7788FF]`
    -   `[7788FF]`
    -   `[0x78F]`
    -   `[#78F]`
    -   `[78F]`
*   Background RGB / HEX colors:
    Change the background color directly with an RGB or HEX color inside
    the square brackets, using the `background:` `BG:` prefix.
    (Same RGB / HEX formatting code rules as for text color.)
    Examples:
    -   `[bg:rgb(115, 117, 255)]`
    -   `[bg:(255, 0, 136)]`
    -   `[bg:#7788FF]`
    -   `[bg:#78F]`
*   Standard terminal colors:
    Change the text color to one of the standard terminal colors
    by just writing the color name in the square brackets.
    -   `[black]`
    -   `[red]`
    -   `[green]`
    -   `[yellow]`
    -   `[blue]`
    -   `[magenta]`
    -   `[cyan]`
    -   `[white]`
*   Bright terminal colors:
    Use the prefix `br:` to use the bright variant of the standard terminal color.
    Examples:
    -   `[br:black]`
    -   `[br:red]`
    -   …
*   Background terminal colors:
    Use the prefix `bg:` to set the background to a standard terminal color.
    Examples:
    -   `[bg:black]`
    -   `[bg:red]`
    -   …
*   Bright background terminal colors:
    Combine the prefixes `bg:` and `br:` to set the background to a bright terminal color.
    Examples:
    -   `[bg:br:black]`
    -   `[bg:br:red]`
    -   …
*   Text styles:
    Use the built-in text formatting to change the style of the text.
    There are long and short forms for each formatting code.
    (Not all terminals support all text styles.)
    -   `[bold]` `[b]`
    -   `[dim]`
    -   `[italic]` `[i]`
    -   `[underline]` `[u]`
    -   `[inverse]` `[invert]` `[in]`
    -   `[hidden]` `[hide]` `[h]`
    -   `[strikethrough]` `[s]`
    -   `[double-underline]` `[du]`
*   Specific reset:
    Use these reset codes to remove a specific style, color or background.
    Again, there are long and short forms for each reset code.
    -   `[_bold]` `[_b]`
    -   `[_dim]`
    -   `[_italic]` `[_i]`
    -   `[_underline]` `[_u]`
    -   `[_inverse]` `[_invert]` `[_in]`
    -   `[_hidden]` `[_hide]` `[_h]`
    -   `[_strikethrough]` `[_s]`
    -   `[_double-underline]` `[_du]`
    -   `[_color]` `[_c]`
    -   `[_background]` `[_bg]`
*   Total reset:
    This will reset all previously applied formatting codes.
    -   `[_]`
*   Hyperlinks:
    Create a clickable hyperlink using the `link:` prefix followed by any URL.
    Auto-reset braces are required to define the visible, clickable text.
    Examples:
    -   `[link:file:///path/to/file.txt](open file)`
    -   `[link:https://example.com|br:blue](click here)`

--------------------------------------------------------------------------------------------------------------------
#### Additional Formatting Codes when a `default_color` is set

1.  `[*]` resets everything, just like `[_]`, but the text color will remain in `default_color`
    (if no `default_color` is set, it resets everything, exactly like `[_]`)
2.  `[default]` will just color the text in `default_color`
    (if no `default_color` is set, it's treated as an invalid formatting code)
3.  `[background:default]` `[BG:default]` will color the background in `default_color`
    (if no `default_color` is set, both are treated as invalid formatting codes)\n

Unlike the standard terminal colors, the default color can be changed by using the following modifiers:

*   `[l]` will lighten the `default_color` text by `brightness_steps`%.
*   `[ll]` will lighten the `default_color` text by `2 × brightness_steps`%.
*   `[lll]` will lighten the `default_color` text by `3 × brightness_steps`%.
*   …
*   Same thing for darkening:
*   `[d]` will darken the `default_color` text by `brightness_steps`%.
*   `[dd]` will darken the `default_color` text by `2 × brightness_steps`%.
*   `[ddd]` will darken the `default_color` text by `3 × brightness_steps`%.
*   …

Per default, you can also use `+` and `-` to get lighter and darker `default_color` versions.
All of these lighten/darken formatting codes are treated as invalid if no `default_color` is set.
"""

from .base.types import FormattableString, Rgba, Hexa
from .base.decorators import deprecated
from .base.consts import ANSI

from .string import String
from .regex import LazyRegex, Regex
from .color import Color, rgba, hexa

from typing import Optional, Literal, Final, overload, cast
from itertools import chain as _chain
import ctypes as _ctypes
import regex as _rx
import sys as _sys
import os as _os


_TERMINAL_ANSI_CONFIGURED: bool = False
"""Whether the terminal was already configured to be able to interpret and render ANSI formatting."""

_ANSI_SEQ_1: Final[FormattableString] = ANSI.seq(1)
"""ANSI escape sequence with a single placeholder."""
_DEFAULT_COLOR_MODS: Final[dict[str, str]] = {
    "lighten": "+l",
    "darken": "-d",
}
"""Formatting codes for lightening and darkening the `default_color`."""
_PREFIX: Final[dict[str, set[str]]] = {
    "bg": {"bg"},
    "br": {"br"},
}
"""Formatting code prefixes for setting background- and bright-colors."""
_PREFIX_VALUES: Final[frozenset[str]] = frozenset(_chain.from_iterable(_PREFIX.values()))
"""Flat frozenset of all prefix values, precomputed for fast membership tests."""
_PREFIX_RX: Final[dict[str, str]] = {
    "bg": rf"(?:{'|'.join(_PREFIX['bg'])})\s*:",
    "br": rf"(?:{'|'.join(_PREFIX['br'])})\s*:",
}
"""Regex patterns for matching background- and bright-color prefixes."""

_PATTERNS = LazyRegex(
    star_reset=r"\[\s*([^]_]*?)\s*\*\s*([^]_]*?)\]",
    star_reset_inside=r"([^|]*?)\s*\*\s*([^|]*)",
    ansi_seq=ANSI.CHAR + r"(?:\].*?(?:\x1b\\|\x07)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_])",
    link=r"(?i)^\s*link\s*:\s*(.+?)\s*$",
    formatting=(
        Regex.brackets("[", "]", is_group=True, ignore_in_strings=False) + r"(?:([/\\]?)"
        + Regex.brackets("(", ")", is_group=True, strip_spaces=False, ignore_in_strings=False) + r")?"
    ),
    escape_char=r"(\s*)(\/|\\)",
    escape_char_cond=r"(\s*\[\s*)(\/|\\)(?!\2+)",
    bg_opt_default=r"(?i)((?:" + _PREFIX_RX["bg"] + r")?)\s*default",
    bg_default=r"(?i)" + _PREFIX_RX["bg"] + r"\s*default",
    modifier=(
        r"(?i)^((?:BG\s*:)?)\s*("
        + "|".join([f"{_rx.escape(m)}+" for m in _DEFAULT_COLOR_MODS["lighten"] + _DEFAULT_COLOR_MODS["darken"]]) + r")$"
    ),
    rgb=r"(?i)^\s*(" + _PREFIX_RX["bg"] + r")?\s*(?:rgb|rgba)?\s*\(?\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)?\s*$",
    hex=r"(?i)^\s*(" + _PREFIX_RX["bg"] + r")?\s*(?:#|0x)?([0-9A-F]{6}|[0-9A-F]{3})\s*$",
)


def _build_ansi_flat() -> dict[str, str]:
    """Build flat mapping from every individual format key (including all aliases)
    to its fully-formed ANSI escape sequence string (precomputed once)."""

    flat: dict[str, str] = {}

    for map_key, code in ANSI.CODES_MAP.items():
        ansi_str = _ANSI_SEQ_1.format(code)
        if isinstance(map_key, tuple):
            for k in map_key:
                flat[k] = ansi_str
        else:
            flat[map_key] = ansi_str

    return flat


_ANSI_FLAT: Final[dict[str, str]] = _build_ansi_flat()
"""Precomputed direct-lookup table from format key to ANSI escape sequence."""

_NORMALIZE_KEY_CACHE: dict[str, str] = {}
"""Cache for `FormatCodes._normalize_key` results."""
_NORMALIZE_KEY_CACHE_MAX: Final[int] = 4096

_REPLACEMENT_CACHE: dict[str, str] = {}
"""Cache for `FormatCodes._get_replacement` results when no `default_color` is set."""
_REPLACEMENT_CACHE_MAX: Final[int] = 4096

_TO_ANSI_CACHE: dict[tuple[str, Optional[tuple[int, int, int]], int], str] = {}
"""Cache for full `FormatCodes.to_ansi` results on the public entry path."""
_TO_ANSI_CACHE_MAX: Final[int] = 1024
_TO_ANSI_CACHE_MAX_LEN: Final[int] = 8192
"""Strings longer than this are not cached end-to-end."""


@deprecated(
    "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
)
class FormatCodes:
    """This class provides methods to print and work with strings that contain special formatting codes,
    which are then converted to ANSI codes for pretty terminal output."""

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def print(
        cls,
        *values: object,
        default_color: Optional[Rgba | Hexa] = None,
        brightness_steps: int = 20,
        sep: str = " ",
        end: str = "\n",
        flush: bool = True,
    ) -> None:
        """A print function, whose print `values` can be formatted using formatting codes.\n
        -----------------------------------------------------------------------------------------------------
        *   `values` – The values to print.
        *   `default_color` – The default text color to use if no other text color was applied.
        *   `brightness_steps` – The amount to increase/decrease default-color brightness per modifier code.
        *   `sep` – The separator to use between multiple values.
        *   `end` – The string to append at the end of the printed values.
        *   `flush` – Whether to flush the output buffer after printing.
        -----------------------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes,<br>
        see the `format_codes` module documentation."""

        cls._config_terminal()
        _sys.stdout.write(cls.to_ansi(sep.join(map(str, values)) + end, default_color, brightness_steps))

        if flush:
            _sys.stdout.flush()

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def input(
        cls,
        prompt: object = "",
        /,
        default_color: Optional[Rgba | Hexa] = None,
        brightness_steps: int = 20,
        *,
        reset_ansi: bool = False,
    ) -> str:
        """An input, whose `prompt` can be formatted using formatting codes.\n
        ------------------------------------------------------------------------------------------------------
        *   `prompt` – The prompt to show to the user.
        *   `default_color` – The default text color to use if no other text color was applied.
        *   `brightness_steps` – The amount to increase/decrease default-color brightness per modifier code.
        *   `reset_ansi` – If true, all ANSI formatting will be reset, after the user confirmed the input<br>
            and the program continues to run.
        ------------------------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes,<br>
        see the `format_codes` module documentation."""

        cls._config_terminal()
        user_input = input(cls.to_ansi(str(prompt), default_color, brightness_steps))

        if reset_ansi:
            _sys.stdout.write(f"{ANSI.CHAR}[0m")

        return user_input

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def to_ansi(
        cls,
        string: str,
        /,
        default_color: Optional[Rgba | Hexa] = None,
        brightness_steps: int = 20,
        *,
        _default_start: bool = True,
        _validate_default: bool = True,
    ) -> str:
        """Convert the formatting codes inside a string to ANSI formatting.\n
        -----------------------------------------------------------------------------------------------------
        *   `string` – The string that contains the formatting codes to convert.
        *   `default_color` – The default text color to use if no other text color was applied.
        *   `brightness_steps` – The amount to increase/decrease default-color brightness per modifier code.
        *   `_default_start` – Whether to start the string with the `default_color` ANSI code, if set.
        *   `_validate_default` – Whether to validate the `default_color` before use<br>
            (expects valid RGBA color or None, if not validated).
        -----------------------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes,<br>
        see the `format_codes` module documentation."""

        if not (0 < brightness_steps <= 100):
            raise ValueError(f"The 'brightness_steps' parameter must be in range [1, 100] inclusive, got {brightness_steps!r}")

        # FAST PATH: NO FORMATTING CODES POSSIBLE WITHOUT '['
        if "[" not in string:
            return cls._no_bracket_fast_path(
                string,
                default_color,
                _default_start=_default_start,
                _validate_default=_validate_default,
            )

        # END-TO-END CACHE LOOKUP (PUBLIC ENTRY PATH ONLY)
        cache_key = (
            cls._build_cache_key(string, default_color, brightness_steps) \
            if _default_start and _validate_default else None
        )
        if cache_key is not None and (cached := _TO_ANSI_CACHE.get(cache_key)) is not None:
            return cached

        if _validate_default:
            use_default, default_color = cls._validate_default_color(default_color)
        else:
            use_default = default_color is not None
            default_color = cast(Optional[rgba], default_color)

        string = cls._apply_star_reset(string, use_default)

        string = "\n".join(
            _PATTERNS.formatting.sub(
                _ReplaceKeysHelper(
                    cls,
                    use_default=use_default,
                    default_color=default_color,
                    brightness_steps=brightness_steps,
                ), line
            ) for line in string.split("\n")
        )

        result = (
            ((cls._get_default_ansi(default_color) or "") if _default_start else "") \
            + string
        ) if default_color is not None else string

        if cache_key is not None:
            cls._store_in_cache(cache_key, result)

        return result

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def escape(
        cls,
        string: str,
        /,
        default_color: Optional[Rgba | Hexa] = None,
        *,
        _escape_char: Literal["/", "\\"] = "/",
    ) -> str:
        """Escapes all valid formatting codes in the string, so they are visible when output<br>
        to the terminal using `FormatCodes.print()`. Invalid formatting codes remain unchanged.\n
        -----------------------------------------------------------------------------------------
        *   `string` – The string that contains the formatting codes to escape.
        *   `default_color` – The default text color to use if no other text color was applied.
        *   `_escape_char` – The character to use to escape formatting codes (`/` or `\\`).
        -----------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes,<br>
        see the `format_codes` module documentation."""

        use_default, default_color = cls._validate_default_color(default_color)

        return "\n".join(
            _PATTERNS.formatting.sub(
                _EscapeFormatCodeHelper(cls, use_default=use_default, default_color=default_color, escape_char=_escape_char),
                line,
            ) for line in string.split("\n")
        )

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def escape_ansi(cls, ansi_string: str, /) -> str:
        """Escapes all ANSI codes in the string, so they are visible when output to the terminal.\n
        --------------------------------------------------------------------------------------------
        *   `ansi_string` – The string that contains the ANSI codes to escape."""

        return ansi_string.replace(ANSI.CHAR, ANSI.CHAR_ESCAPED)

    @overload
    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove(
        cls,
        string: str,
        /,
        default_color: Optional[Rgba | Hexa] = None,
        *,
        get_removals: Literal[True],
        _ignore_linebreaks: bool = False,
    ) -> tuple[str, tuple[tuple[int, str], ...]]:
        ...

    @overload
    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove(
        cls,
        string: str,
        /,
        default_color: Optional[Rgba | Hexa] = None,
        *,
        get_removals: Literal[False] = False,
        _ignore_linebreaks: bool = False,
    ) -> str:
        ...

    @overload
    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove(
        cls,
        string: str,
        /,
        default_color: Optional[Rgba | Hexa] = None,
        *,
        get_removals: bool = False,
        _ignore_linebreaks: bool = False,
    ) -> str | tuple[str, tuple[tuple[int, str], ...]]:
        ...

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove(
        cls,
        string: str,
        /,
        default_color: Optional[Rgba | Hexa] = None,
        *,
        get_removals: bool = False,
        _ignore_linebreaks: bool = False,
    ) -> str | tuple[str, tuple[tuple[int, str], ...]]:
        """Removes all formatting codes from the string with optional tracking of removed codes.\n
        -----------------------------------------------------------------------------------------------------------
        *   `string` – The string that contains the formatting codes to remove.
        *   `default_color` – The default text color to use if no other text color was applied.
        *   `get_removals` – If true, additionally to the cleaned string, a list of tuples will be returned,<br>
            where each tuple contains the position of the removed formatting code and the removed formatting code.
        *   `_ignore_linebreaks` – Whether to ignore line breaks for the removal positions."""

        return cls.remove_ansi(
            cls.to_ansi(string, default_color=default_color),
            get_removals=get_removals,
            _ignore_linebreaks=_ignore_linebreaks,
        )

    @overload
    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove_ansi(
        cls,
        ansi_string: str,
        /,
        *,
        get_removals: Literal[True],
        _ignore_linebreaks: bool = False,
    ) -> tuple[str, tuple[tuple[int, str], ...]]:
        ...

    @overload
    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove_ansi(
        cls,
        ansi_string: str,
        /,
        *,
        get_removals: Literal[False] = False,
        _ignore_linebreaks: bool = False,
    ) -> str:
        ...

    @overload
    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove_ansi(
        cls,
        ansi_string: str,
        /,
        *,
        get_removals: bool = False,
        _ignore_linebreaks: bool = False,
    ) -> str | tuple[str, tuple[tuple[int, str], ...]]:
        ...

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.format_codes` (`F`, `FC`, `Term`) instead. This will be completely removed in an upcoming future update."
    )
    def remove_ansi(
        cls,
        ansi_string: str,
        /,
        *,
        get_removals: bool = False,
        _ignore_linebreaks: bool = False,
    ) -> str | tuple[str, tuple[tuple[int, str], ...]]:
        """Removes all ANSI codes from the string with optional tracking of removed codes.\n
        ---------------------------------------------------------------------------------------------------------
        *   `ansi_string` – The string that contains the ANSI codes to remove.
        *   `get_removals` – If true, additionally to the cleaned string, a list of tuples will be returned,<br>
            where each tuple contains the position of the removed ansi code and the removed ansi code.
        *   `_ignore_linebreaks` – Whether to ignore line breaks for the removal positions."""

        if get_removals:
            removals: list[tuple[int, str]] = []

            clean_string = _PATTERNS.ansi_seq.sub(
                _RemAnsiSeqHelper(removals),
                ansi_string.replace("\n", "") if _ignore_linebreaks else ansi_string  # REMOVE LINEBREAKS FOR POSITIONS
            )
            if _ignore_linebreaks:
                clean_string = _PATTERNS.ansi_seq.sub("", ansi_string)  # BUT KEEP LINEBREAKS IN RETURNED CLEAN STRING

            return clean_string, tuple(removals)

        else:
            return _PATTERNS.ansi_seq.sub("", ansi_string)

    @classmethod
    def _config_terminal(cls) -> None:
        """Internal method which configures the terminal to be able to interpret and render ANSI formatting.\n
        -------------------------------------------------------------------------------------------------------
        This method will only do something the first time it's called. Subsequent calls will do nothing."""

        global _TERMINAL_ANSI_CONFIGURED
        if not _TERMINAL_ANSI_CONFIGURED:
            _sys.stdout.flush()
            if _os.name == "nt":
                try:
                    # ENABLE VT100 MODE ON WINDOWS TO BE ABLE TO USE ANSI CODES
                    kernel32 = getattr(_ctypes, "windll").kernel32
                    handle = kernel32.GetStdHandle(-11)
                    mode = _ctypes.c_ulong()
                    kernel32.GetConsoleMode(handle, _ctypes.byref(mode))
                    kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                except Exception:
                    pass
            _TERMINAL_ANSI_CONFIGURED = True  # type: ignore[assignment]

    @classmethod
    def _no_bracket_fast_path(
        cls,
        string: str,
        default_color: Optional[Rgba | Hexa],
        *,
        _default_start: bool,
        _validate_default: bool,
    ) -> str:
        """Handle fast path when the string contains no `[` bracket."""

        if _validate_default:
            _, default_color = cls._validate_default_color(default_color)

        if _default_start and default_color is not None:
            prefix = cls._get_default_ansi(cast(rgba, default_color))
            if prefix:
                return prefix + string

        return string

    @classmethod
    def _build_cache_key(
        cls,
        string: str,
        default_color: Optional[Rgba | Hexa],
        brightness_steps: int,
    ) -> Optional[tuple[str, Optional[tuple[int, int, int]], int]]:
        """Build a cache key for `to_ansi`, returning None if caching should be skipped."""

        if len(string) > _TO_ANSI_CACHE_MAX_LEN:
            return None

        if default_color is None:
            return (string, None, brightness_steps)

        if isinstance(default_color, tuple) and len(default_color) >= 3:
            try:
                dc_key = (int(default_color[0]), int(default_color[1]), int(default_color[2]))
                return (string, dc_key, brightness_steps)
            except (TypeError, ValueError):
                return None

        return None  # HEX STRINGS AND OTHER TYPES SKIP CACHE

    @staticmethod
    def _store_in_cache(
        cache_key: tuple[str, Optional[tuple[int, int, int]], int],
        result: str,
        /,
    ) -> None:
        """Store a `to_ansi` result in the end-to-end cache, evicting all entries if at capacity."""

        if len(_TO_ANSI_CACHE) >= _TO_ANSI_CACHE_MAX:
            _TO_ANSI_CACHE.clear()

        _TO_ANSI_CACHE[cache_key] = result

    @staticmethod
    def _validate_default_color(default_color: Optional[Rgba | Hexa], /) -> tuple[bool, Optional[rgba]]:
        """Internal method to validate and convert `default_color` to a `rgba` color object."""

        if default_color is None:
            return False, None
        if Color.is_valid_hexa(default_color, allow_alpha=False):
            return True, hexa(cast(str | int, default_color)).to_rgba()
        elif Color.is_valid_rgba(default_color, allow_alpha=False):
            return True, Color._parse_rgba(cast(Rgba, default_color))
        raise ValueError(
            f"The 'default_color' parameter must be either a valid RGBA or HEXA color, or None, got {default_color!r}"
        )

    @staticmethod
    def _apply_star_reset(string: str, use_default: bool, /) -> str:
        """Replace `[*]` star-reset tokens with the appropriate reset sequences."""

        if "*" not in string:
            return string
        if use_default:
            return _PATTERNS.star_reset.sub(r"[\1_|default\2]", string)  # REPLACE `[…|*|…]` WITH `[…|_|default|…]`

        return _PATTERNS.star_reset.sub(r"[\1_\2]", string)  # REPLACE `[…|*|…]` WITH `[…|_|…]`

    @staticmethod
    def _formats_to_keys(formats: str, /) -> list[str]:
        """Internal method to convert a string of multiple format
        keys to a list of individual, stripped format keys."""

        return [key.strip() for key in formats.split("|") if key.strip()]

    @classmethod
    def _get_replacement(cls, format_key: str, default_color: Optional[rgba], /, brightness_steps: int = 20) -> str:
        """Internal method that gives you the corresponding ANSI code for the given format key.\n
        If `default_color` is not `None`, the text color will be `default_color` if all formats<br>
        are reset or you can get lighter or darker version of `default_color` (also as BG)"""

        # FAST PATH WHEN NO DEFAULT COLOR: USE CACHED RESULTS
        if default_color is None and (cached := _REPLACEMENT_CACHE.get(format_key)) is not None:
            return cached

        _format_key = format_key
        format_key = cls._normalize_key(format_key)  # NORMALIZE KEY AND SAVE ORIGINAL

        # DIRECT LOOKUP IN PRECOMPUTED FLAT TABLE (NO O(N) SCAN OVER CODES_MAP)
        flat_hit = _ANSI_FLAT.get(format_key)

        if default_color is not None and ( \
            new_default_color := cls._get_default_ansi(default_color, format_key, brightness_steps)
        ):
            return new_default_color

        if flat_hit is not None:
            return flat_hit

        rgb_match = _PATTERNS.rgb.match(format_key)
        hex_match = _PATTERNS.hex.match(format_key)

        result = _format_key
        try:
            if rgb_match:
                is_bg = rgb_match.group(1)
                red, green, blue = map(int, rgb_match.groups()[1:])
                if Color.is_valid_rgba((red, green, blue)):
                    result = ANSI.SEQ_BG_COLOR.format(red, green,
                                                      blue) if is_bg else ANSI.SEQ_FG_COLOR.format(red, green, blue)

            elif hex_match:
                is_bg = hex_match.group(1)
                rgb = Color.to_rgba(hex_match.group(2))
                result = (
                    ANSI.SEQ_BG_COLOR.format(rgb[0], rgb[1], rgb[2])
                    if is_bg else ANSI.SEQ_FG_COLOR.format(rgb[0], rgb[1], rgb[2])
                )

        except Exception:
            pass

        if default_color is None:
            if len(_REPLACEMENT_CACHE) >= _REPLACEMENT_CACHE_MAX:
                _REPLACEMENT_CACHE.clear()
            _REPLACEMENT_CACHE[_format_key] = result

        return result

    @staticmethod
    def _get_default_ansi(
        default_color: rgba,
        /,
        format_key: Optional[str] = None,
        brightness_steps: Optional[int] = None,
        *,
        _modifiers: tuple[str, str] = (_DEFAULT_COLOR_MODS["lighten"], _DEFAULT_COLOR_MODS["darken"]),
    ) -> Optional[str]:
        """Internal method to get the `default_color` and lighter/darker versions of it as ANSI code."""

        _default_color: tuple[int, int, int] = (default_color[0], default_color[1], default_color[2])

        if brightness_steps is None or (format_key and _PATTERNS.bg_opt_default.search(format_key)):
            return (ANSI.SEQ_BG_COLOR if format_key and _PATTERNS.bg_default.search(format_key) else ANSI.SEQ_FG_COLOR).format(
                *_default_color
            )

        if format_key is None or not (match := _PATTERNS.modifier.match(format_key)):
            return None

        is_bg, modifiers = match.groups()
        adjust = 0

        for mod in _modifiers[0] + _modifiers[1]:
            adjust = String.single_char_repeats(modifiers, mod)
            if adjust and adjust > 0:
                modifiers = mod
                break

        new_rgb = _default_color

        if adjust == 0:
            return None

        elif modifiers in _modifiers[0]:
            adjusted_rgb = Color.adjust_lightness(default_color, (brightness_steps / 100) * adjust)
            new_rgb = (adjusted_rgb[0], adjusted_rgb[1], adjusted_rgb[2])

        elif modifiers in _modifiers[1]:
            adjusted_rgb = Color.adjust_lightness(default_color, -(brightness_steps / 100) * adjust)
            new_rgb = (adjusted_rgb[0], adjusted_rgb[1], adjusted_rgb[2])

        return (ANSI.SEQ_BG_COLOR if is_bg else ANSI.SEQ_FG_COLOR).format(*new_rgb[:3])

    @staticmethod
    def _normalize_key(format_key: str, /) -> str:
        """Internal method to normalize the given format key."""

        if (cached := _NORMALIZE_KEY_CACHE.get(format_key)) is not None:
            return cached

        k_parts = format_key.replace(" ", "").lower().split(":")

        prefix_str = "".join(
            f"{prefix_key.lower()}:" for prefix_key, prefix_values in _PREFIX.items()
            if any(k_part in prefix_values for k_part in k_parts)
        )

        result = prefix_str + ":".join(
            part for part in k_parts \
            if part not in _PREFIX_VALUES
        )

        if len(_NORMALIZE_KEY_CACHE) >= _NORMALIZE_KEY_CACHE_MAX:
            _NORMALIZE_KEY_CACHE.clear()
        _NORMALIZE_KEY_CACHE[format_key] = result

        return result


class _EscapeFormatCodeHelper:
    """Internal, callable helper class to escape formatting codes."""

    def __init__(
        self,
        cls: type[FormatCodes],
        *,
        use_default: bool,
        default_color: Optional[rgba],
        escape_char: Literal["/", "\\"],
    ):
        self.cls = cls
        self.use_default = use_default
        self.default_color = default_color
        self.escape_char: Literal["/", "\\"] = escape_char

    def __call__(self, match: _rx.Match[str], /) -> str:
        formats, auto_reset_txt = match.group(1), match.group(3)

        # CHECK IF ALREADY ESCAPED OR CONTAINS NO FORMATTING
        if not formats or _PATTERNS.escape_char_cond.match(match.group(0)):
            return match.group(0)

        # TEMPORARILY REPLACE `*` FOR VALIDATION
        _formats = formats
        if self.use_default:
            _formats = _PATTERNS.star_reset_inside.sub(r"\1_|default\2", formats)
        else:
            _formats = _PATTERNS.star_reset_inside.sub(r"\1_\2", formats)

        has_link = False
        has_invalid_key = False
        for format_key in self.cls._formats_to_keys(_formats):
            if _PATTERNS.link.match(format_key):
                has_link = True
            elif self.cls._get_replacement(format_key, self.default_color) == format_key:
                has_invalid_key = True

        if has_link or not has_invalid_key:
            # ESCAPE THE FORMATTING CODE
            escaped = f"[{self.escape_char}{formats}]"
            if auto_reset_txt:
                # RECURSIVELY ESCAPE FORMATTING IN AUTO-RESET TEXT
                escaped_auto_reset = self.cls.escape(auto_reset_txt, self.default_color, _escape_char=self.escape_char)
                escaped += f"({escaped_auto_reset})"
            return escaped

        else:
            # KEEP INVALID FORMATTING CODES AS-IS
            result = f"[{formats}]"
            if auto_reset_txt:
                # STILL RECURSIVELY PROCESS AUTO-RESET TEXT
                escaped_auto_reset = self.cls.escape(auto_reset_txt, self.default_color, _escape_char=self.escape_char)
                result += f"({escaped_auto_reset})"
            return result


class _RemAnsiSeqHelper:
    """Internal, callable helper class to remove ANSI sequences and track their removal positions."""

    def __init__(self, removals: list[tuple[int, str]], /):
        self.removals = removals

    def __call__(self, match: _rx.Match[str], /) -> str:
        start_pos = match.start() - sum(len(removed) for _, removed in self.removals)

        if self.removals and self.removals[-1][0] == start_pos:
            start_pos = self.removals[-1][0]

        self.removals.append((start_pos, match.group()))

        return ""


class _ReplaceKeysHelper:
    """Internal, callable helper class to replace formatting keys with their respective ANSI codes."""

    def __init__(
        self,
        cls: type[FormatCodes],
        *,
        use_default: bool,
        default_color: Optional[rgba],
        brightness_steps: int,
    ):
        self.cls = cls
        self.use_default = use_default
        self.default_color = default_color
        self.brightness_steps = brightness_steps

        # INSTANCE VARIABLES FOR CURRENT PROCESSING STATE
        self.formats: str = ""
        self.original_formats: str = ""
        self.formats_escaped: bool = False
        self.auto_reset_escaped: bool = False
        self.auto_reset_txt: Optional[str] = None
        self.format_keys: list[str] = []
        self.ansi_formats: list[str] = []
        self.ansi_resets: list[str] = []

    def __call__(self, match: _rx.Match[str], /) -> str:
        self.original_formats = self.formats = match.group(1)
        self.auto_reset_escaped = bool(match.group(2))
        self.auto_reset_txt = match.group(3)

        # CHECK IF THERE'S ESCAPED FORMAT CODES
        self.formats_escaped = bool(_PATTERNS.escape_char_cond.match(match.group(0)))
        if self.formats_escaped:
            self.original_formats = self.formats = _PATTERNS.escape_char.sub(r"\1", self.formats)

        # HANDLE HYPERLINK FORMAT
        all_keys = self.cls._formats_to_keys(self.formats)
        if (result := self.handle_link(match, all_keys)) is not None:
            return result

        self.process_formats_and_auto_reset()

        # IF THERE ARE NO FORMATS OR ALL FORMATS ARE INVALID, RETURN THE ORIGINAL STRING
        if not self.formats:
            return match.group(0)

        self.convert_to_ansi()
        return self.build_output(match)

    def handle_link(self, match: _rx.Match[str], all_keys: list[str], /) -> Optional[str]:
        """Handle a hyperlink format code, returning the OSC 8 sequence or None if not a link."""

        link_key = next((key for key in all_keys if _PATTERNS.link.match(key)), None)

        if link_key is None:
            return None
        if self.auto_reset_txt is None:
            return match.group(0)  # LINK WITHOUT DISPLAY BRACES IS INVALID
        if self.formats_escaped:
            return f"[{self.original_formats}]({self.auto_reset_txt})"

        link_url = _PATTERNS.link.match(link_key).group(1)  # type: ignore[union-attr]
        display = self.auto_reset_txt

        if other_keys := [key for key in all_keys if key != link_key]:
            # APPLY REMAINING FORMAT CODES TO DISPLAY TEXT WITH AUTO-RESET
            display = "[{}]({})".format("|".join(other_keys), display)

        if other_keys or ("[" in display and "]" in display):
            display = self.cls.to_ansi(
                display,
                self.default_color,
                self.brightness_steps,
                _default_start=False,
                _validate_default=False,
            )

        return ANSI.SEQ_LINK_OPEN.format(link_url) + display + ANSI.SEQ_LINK_CLOSE

    def process_formats_and_auto_reset(self) -> None:
        """Process nested formatting in both formats and auto-reset text."""

        # PROCESS AUTO-RESET TEXT IF IT CONTAINS NESTED FORMATTING
        if self.auto_reset_txt and self.auto_reset_txt.count("[") > 0 and self.auto_reset_txt.count("]") > 0:
            self.auto_reset_txt = self.cls.to_ansi(
                self.auto_reset_txt,
                self.default_color,
                self.brightness_steps,
                _default_start=False,
                _validate_default=False,
            )

        # PROCESS NESTED FORMATTING IN FORMATS
        if self.formats and self.formats.count("[") > 0 and self.formats.count("]") > 0:
            self.formats = self.cls.to_ansi(
                self.formats,
                self.default_color,
                self.brightness_steps,
                _default_start=False,
                _validate_default=False,
            )

    def convert_to_ansi(self) -> None:
        """Convert format keys to ANSI codes and generate resets if needed."""

        self.format_keys = self.cls._formats_to_keys(self.formats)
        self.ansi_formats = [(
            ansi_code \
            if (ansi_code := self.cls._get_replacement(format_key, self.default_color, self.brightness_steps)) != format_key
            else f"[{format_key}]"
        ) for format_key in self.format_keys]

        # GENERATE RESET CODES IF AUTO-RESET IS ACTIVE
        if self.auto_reset_txt and not self.auto_reset_escaped:
            self.gen_reset_codes()
        else:
            self.ansi_resets = []

    def gen_reset_codes(self) -> None:
        """Generate appropriate ANSI reset codes for each format key."""

        default_color_resets = ("_bg", "default") if self.use_default else ("_bg", "_c")
        reset_keys: list[str] = []

        for format_key in self.format_keys:
            k_lower = format_key.lower()
            k_set = set(k_lower.split(":"))

            # BACKGROUND COLOR FORMAT
            if _PREFIX["bg"] & k_set and len(k_set) <= 3:
                if k_set & _PREFIX["br"]:
                    # BRIGHT BACKGROUND COLOR – RESET BOTH BG AND COLOR
                    for i in range(len(format_key)):
                        if self.is_valid_color(format_key[i:]):
                            reset_keys.extend(default_color_resets)
                            break

                else:
                    # REGULAR BACKGROUND COLOR – RESET ONLY BG
                    for i in range(len(format_key)):
                        if self.is_valid_color(format_key[i:]):
                            reset_keys.append("_bg")
                            break

            # TEXT COLOR FORMAT
            elif self.is_valid_color(format_key) or any(
                k_lower.startswith(pref_colon := f"{prefix}:") and self.is_valid_color(format_key[len(pref_colon):]) \
                for prefix in _PREFIX["br"]
            ):
                reset_keys.append(default_color_resets[1])

            # TEXT STYLE FORMAT
            else:
                reset_keys.append(f"_{format_key}")

        # CONVERT RESET KEYS TO ANSI CODES
        self.ansi_resets = [
            ansi_code for reset_key in reset_keys if ( \
                ansi_code := self.cls._get_replacement(reset_key, self.default_color, self.brightness_steps)
            ).startswith(f"{ANSI.CHAR}{ANSI.START}")
        ]

    def build_output(self, match: _rx.Match[str], /) -> str:
        """Build the final output string based on processed formats and resets."""

        # CHECK IF ALL FORMATS WERE VALID
        has_single_valid_ansi = len(self.ansi_formats) == 1 and self.ansi_formats[0].count(f"{ANSI.CHAR}{ANSI.START}") >= 1
        all_formats_valid = all(ansi_format.startswith(f"{ANSI.CHAR}{ANSI.START}") for ansi_format in self.ansi_formats)

        if not has_single_valid_ansi and not all_formats_valid:
            return match.group(0)

        # HANDLE ESCAPED FORMATTING
        if self.formats_escaped:
            return f"[{self.original_formats}]({self.auto_reset_txt})" if self.auto_reset_txt else f"[{self.original_formats}]"

        # BUILD NORMAL OUTPUT WITH FORMATS AND RESETS
        output = "".join(self.ansi_formats)

        # ADD AUTO-RESET TEXT
        if self.auto_reset_escaped and self.auto_reset_txt:
            output = self.cls.to_ansi(
                self.auto_reset_txt,
                self.default_color,
                self.brightness_steps,
                _default_start=False,
                _validate_default=False,
            )
            output += f"({output})"
        elif self.auto_reset_txt:
            output += self.auto_reset_txt

        # ADD RESET CODES IF NOT ESCAPED
        if not self.auto_reset_escaped:
            output += "".join(self.ansi_resets)

        return output

    def is_valid_color(self, color: str, /) -> bool:
        """Check whether the given color string is a valid formatting-key color."""

        return bool(
            color in ANSI.COLOR_MAP \
            or Color.is_valid_rgba(color)
            or Color.is_valid_hexa(color)
        )
