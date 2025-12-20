"""
This module provides the `FormatCodes` class, which includes methods to print and work with strings that
contain special formatting codes, which are then converted to ANSI codes for pretty console output.

------------------------------------------------------------------------------------------------------------------------------------
### The Easy Formatting

First, let's take a look at a small example of what a highly styled print string with formatting could look like using this module:
```
This here is just unformatted text. [b|u|br:blue](Next we have text that is bright blue + bold + underlined.)\\n
[#000|bg:#F67](Then there's also black text with a red background.) And finally the ([i](boring)) plain text again.
```

How all of this exactly works is explained in the sections below. 🠫

------------------------------------------------------------------------------------------------------------------------------------
#### Formatting Codes and Keys

In this module, you can apply styles and colors using simple formatting codes.
These formatting codes consist of one or multiple different formatting keys in between square brackets.

If a formatting code is placed in a print-string, the formatting of that code will be applied to everything behind it until its
formatting is reset. If applying multiple styles and colors in the same place, instead of writing the formatting keys all into
separate brackets (e.g. `[x][y][z]`), they can also be put in a single pair of brackets, separated by pipes (e.g. `[x|y|z]`).

A list of all possible formatting keys can be found under all possible formatting keys.

------------------------------------------------------------------------------------------------------------------------------------
#### Auto Resetting Formatting Codes

Certain formatting can automatically be reset, behind a certain amount of text, just like shown in the following example:
```
This is plain text, [br:blue](which is bright blue now.) Now it was automatically reset to plain again.
```

This will only reset formatting codes, that have a specific reset listed below.
That means if you use it where another formatting is already applied, that formatting is still there after the automatic reset:
```
[cyan]This is cyan text, [dim](which is dimmed now.) Now it's not dimmed any more but still cyan.
```

If you want to ignore the auto-reset functionality of `()` brackets, you can put a `\\` or `/` between them and
the formatting code:
```
[cyan]This is cyan text, [u]/(which is underlined now.) And now it is still underlined and cyan.
```

------------------------------------------------------------------------------------------------------------------------------------
#### All possible Formatting Keys

- RGB colors:
  Change the text color directly with an RGB color inside the square brackets. (With or without `rgb()` brackets doesn't matter.)
  Examples:
  - `[rgb(115, 117, 255)]`
  - `[(255, 0, 136)]`
  - `[255, 0, 136]`
- HEX colors:
  Change the text color directly with a HEX color inside the square brackets. (Whether the `RGB` or `RRGGBB` HEX format is used,
  and if there's a `#` or `0x` prefix, doesn't matter.)
  Examples:
  - `[0x7788FF]`
  - `[#7788FF]`
  - `[7788FF]`
  - `[0x78F]`
  - `[#78F]`
  - `[78F]`
- background RGB / HEX colors:
  Change the background color directly with an RGB or HEX color inside the square brackets, using the `background:` `BG:` prefix.
  (Same RGB / HEX formatting code rules as for text color.)
  Examples:
  - `[background:rgb(115, 117, 255)]`
  - `[BG:(255, 0, 136)]`
  - `[background:#7788FF]`
  - `[BG:#78F]`
- standard console colors:
  Change the text color to one of the standard console colors by just writing the color name in the square brackets.
  - `[black]`
  - `[red]`
  - `[green]`
  - `[yellow]`
  - `[blue]`
  - `[magenta]`
  - `[cyan]`
  - `[white]`
- bright console colors:
  Use the prefix `bright:` `BR:` to use the bright variant of the standard console color.
  Examples:
  - `[bright:black]` `[BR:black]`
  - `[bright:red]` `[BR:red]`
  - ...
- Background console colors:
  Use the prefix `background:` `BG:` to set the background to a standard console color. (Not all consoles support bright
  standard colors.)
  Examples:
  - `[background:black]` `[BG:black]`
  - `[background:red]` `[BG:red]`
  - ...
- Bright background console colors:
  Combine the prefixes `background:` / `BG:` and `bright:` / `BR:` to set the background to a bright console color.
  (The order of the prefixes doesn't matter.)
  Examples:
  - `[background:bright:black]` `[BG:BR:black]`
  - `[background:bright:red]` `[BG:BR:red]`
  - ...
- Text styles:
  Use the built-in text formatting to change the style of the text. There are long and short forms for each formatting code.
  (Not all consoles support all text styles.)
  - `[bold]` `[b]`
  - `[dim]`
  - `[italic]` `[i]`
  - `[underline]` `[u]`
  - `[inverse]` `[invert]` `[in]`
  - `[hidden]` `[hide]` `[h]`
  - `[strikethrough]` `[s]`
  - `[double-underline]` `[du]`
- Specific reset:
  Use these reset codes to remove a specific style, color or background. Again, there are long and
  short forms for each reset code.
  - `[_bold]` `[_b]`
  - `[_dim]`
  - `[_italic]` `[_i]`
  - `[_underline]` `[_u]`
  - `[_inverse]` `[_invert]` `[_in]`
  - `[_hidden]` `[_hide]` `[_h]`
  - `[_strikethrough]` `[_s]`
  - `[_double-underline]` `[_du]`
  - `[_color]` `[_c]`
  - `[_background]` `[_bg]`
- Total reset:
  This will reset all previously applied formatting codes.
  - `[_]`

------------------------------------------------------------------------------------------------------------------------------------
#### Additional Formatting Codes when a `default_color` is set

1. `[*]` resets everything, just like `[_]`, but the text color will remain in `default_color`
  (if no `default_color` is set, it resets everything, exactly like `[_]`)
2. `[default]` will just color the text in `default_color`
  (if no `default_color` is set, it's treated as an invalid formatting code)
3. `[background:default]` `[BG:default]` will color the background in `default_color`
  (if no `default_color` is set, both are treated as invalid formatting codes)\n

Unlike the standard console colors, the default color can be changed by using the following modifiers:

- `[l]` will lighten the `default_color` text by `brightness_steps`%
- `[ll]` will lighten the `default_color` text by `2 × brightness_steps`%
- `[lll]` will lighten the `default_color` text by `3 × brightness_steps`%
- ... etc. Same thing for darkening:
- `[d]` will darken the `default_color` text by `brightness_steps`%
- `[dd]` will darken the `default_color` text by `2 × brightness_steps`%
- `[ddd]` will darken the `default_color` text by `3 × brightness_steps`%
- ... etc.
Per default, you can also use `+` and `-` to get lighter and darker `default_color` versions.
All of these lighten/darken formatting codes are treated as invalid if no `default_color` is set.
"""

from .base.types import Match, Rgba, Hexa
from .base.consts import ANSI

from .string import String
from .regex import LazyRegex, Regex
from .color import Color, rgba

from typing import Optional, Literal, cast
import ctypes as _ctypes
import regex as _rx
import sys as _sys
import os as _os


_CONSOLE_ANSI_CONFIGURED: bool = False

_ANSI_SEQ_1: str = ANSI.seq(1)
_DEFAULT_COLOR_MODS: dict[str, str] = {
    "lighten": "+l",
    "darken": "-d",
}
_PREFIX: dict[str, set[str]] = {
    "BG": {"background", "bg"},
    "BR": {"bright", "br"},
}
_PREFIX_RX: dict[str, str] = {
    "BG": rf"(?:{'|'.join(_PREFIX['BG'])})\s*:",
    "BR": rf"(?:{'|'.join(_PREFIX['BR'])})\s*:",
}

# PRECOMPILE REGULAR EXPRESSIONS
_PATTERNS = LazyRegex(
    star_reset=r"\[\s*([^]_]*?)\s*\*\s*([^]_]*?)\]",
    star_reset_inside=r"([^|]*?)\s*\*\s*([^|]*)",
    ansi_seq=ANSI.CHAR + r"(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])",
    formatting=(
        Regex.brackets("[", "]", is_group=True, ignore_in_strings=False) + r"(?:([/\\]?)"
        + Regex.brackets("(", ")", is_group=True, strip_spaces=False, ignore_in_strings=False) + r")?"
    ),
    escape_char=r"(\s*)(\/|\\)",
    escape_char_cond=r"(\s*\[\s*)(\/|\\)(?!\2+)",
    bg_opt_default=r"(?i)((?:" + _PREFIX_RX["BG"] + r")?)\s*default",
    bg_default=r"(?i)" + _PREFIX_RX["BG"] + r"\s*default",
    modifier=(
        r"(?i)^((?:BG\s*:)?)\s*("
        + "|".join([f"{_rx.escape(m)}+" for m in _DEFAULT_COLOR_MODS["lighten"] + _DEFAULT_COLOR_MODS["darken"]]) + r")$"
    ),
    rgb=r"(?i)^\s*(" + _PREFIX_RX["BG"] + r")?\s*(?:rgb|rgba)?\s*\(?\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)?\s*$",
    hex=r"(?i)^\s*(" + _PREFIX_RX["BG"] + r")?\s*(?:#|0x)?([0-9A-F]{6}|[0-9A-F]{3})\s*$",
)


class FormatCodes:
    """This class provides methods to print and work with strings that contain special formatting codes,
    which are then converted to ANSI codes for pretty console output."""

    @classmethod
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
        --------------------------------------------------------------------------------------------------
        - `values` -⠀the values to print
        - `default_color` -⠀the default text color to use if no other text color was applied
        - `brightness_steps` -⠀the amount to increase/decrease default-color brightness per modifier code
        - `sep` -⠀the separator to use between multiple values
        - `end` -⠀the string to append at the end of the printed values
        - `flush` -⠀whether to flush the output buffer after printing\n
        --------------------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes,
        see the `format_codes` module documentation."""
        cls._config_console()
        _sys.stdout.write(cls.to_ansi(sep.join(map(str, values)) + end, default_color, brightness_steps))

        if flush:
            _sys.stdout.flush()

    @classmethod
    def input(
        cls,
        prompt: object = "",
        default_color: Optional[Rgba | Hexa] = None,
        brightness_steps: int = 20,
        reset_ansi: bool = False,
    ) -> str:
        """An input, whose `prompt` can be formatted using formatting codes.\n
        --------------------------------------------------------------------------------------------------
        - `prompt` -⠀the prompt to show to the user
        - `default_color` -⠀the default text color to use if no other text color was applied
        - `brightness_steps` -⠀the amount to increase/decrease default-color brightness per modifier code
        - `reset_ansi` -⠀if true, all ANSI formatting will be reset, after the user confirmed the input
          and the program continues to run\n
        --------------------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes, see the
        `format_codes` module documentation."""
        cls._config_console()
        user_input = input(cls.to_ansi(str(prompt), default_color, brightness_steps))

        if reset_ansi:
            _sys.stdout.write(f"{ANSI.CHAR}[0m")
        return user_input

    @classmethod
    def to_ansi(
        cls,
        string: str,
        default_color: Optional[Rgba | Hexa] = None,
        brightness_steps: int = 20,
        _default_start: bool = True,
        _validate_default: bool = True,
    ) -> str:
        """Convert the formatting codes inside a string to ANSI formatting.\n
        --------------------------------------------------------------------------------------------------
        - `string` -⠀the string that contains the formatting codes to convert
        - `default_color` -⠀the default text color to use if no other text color was applied
        - `brightness_steps` -⠀the amount to increase/decrease default-color brightness per modifier code
        - `_default_start` -⠀whether to start the string with the `default_color` ANSI code, if set
        - `_validate_default` -⠀whether to validate the `default_color` before use
          (expects valid RGBA color or None, if not validated)\n
        --------------------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes,
        see the `format_codes` module documentation."""
        if not (0 < brightness_steps <= 100):
            raise ValueError("The 'brightness_steps' parameter must be between 1 and 100.")

        if _validate_default:
            use_default, default_color = cls.__validate_default_color(default_color)
        else:
            use_default = default_color is not None
            default_color = cast(Optional[rgba], default_color)

        if use_default:
            string = _PATTERNS.star_reset.sub(r"[\1_|default\2]", string)  # REPLACE `[…|*|…]` WITH `[…|_|default|…]`
        else:
            string = _PATTERNS.star_reset.sub(r"[\1_\2]", string)  # REPLACE `[…|*|…]` WITH `[…|_|…]`

        def is_valid_color(color: str) -> bool:
            return bool((color in ANSI.COLOR_MAP) or Color.is_valid_rgba(color) or Color.is_valid_hexa(color))

        def replace_keys(match: Match) -> str:
            _formats = formats = match.group(1)
            auto_reset_escaped = match.group(2)
            auto_reset_txt = match.group(3)

            if formats_escaped := bool(_PATTERNS.escape_char_cond.match(match.group(0))):
                _formats = formats = _PATTERNS.escape_char.sub(r"\1", formats)  # REMOVE / OR \\

            if auto_reset_txt and auto_reset_txt.count("[") > 0 and auto_reset_txt.count("]") > 0:
                auto_reset_txt = cls.to_ansi(
                    auto_reset_txt,
                    default_color,
                    brightness_steps,
                    _default_start=False,
                    _validate_default=False,
                )

            if not formats:
                return match.group(0)

            if formats.count("[") > 0 and formats.count("]") > 0:
                formats = cls.to_ansi(
                    formats,
                    default_color,
                    brightness_steps,
                    _default_start=False,
                    _validate_default=False,
                )

            format_keys = cls.__formats_to_keys(formats)
            ansi_formats = [
                r if (r := cls.__get_replacement(k, default_color, brightness_steps)) != k else f"[{k}]" for k in format_keys
            ]

            if auto_reset_txt and not auto_reset_escaped:
                reset_keys: list[str] = []
                default_color_resets = ("_bg", "default") if use_default else ("_bg", "_c")

                for k in format_keys:
                    k_lower = k.lower()
                    k_set = set(k_lower.split(":"))

                    if _PREFIX["BG"] & k_set and len(k_set) <= 3:
                        if k_set & _PREFIX["BR"]:
                            for i in range(len(k)):
                                if is_valid_color(k[i:]):
                                    reset_keys.extend(default_color_resets)
                                    break
                        else:
                            for i in range(len(k)):
                                if is_valid_color(k[i:]):
                                    reset_keys.append("_bg")
                                    break

                    elif is_valid_color(k) or any(
                            k_lower.startswith(pref_colon := f"{prefix}:") and is_valid_color(k[len(pref_colon):])
                            for prefix in _PREFIX["BR"]):
                        reset_keys.append(default_color_resets[1])

                    else:
                        reset_keys.append(f"_{k}")

                ansi_resets = [
                    r for k in reset_keys
                    if (r := cls.__get_replacement(k, default_color, brightness_steps)).startswith(f"{ANSI.CHAR}{ANSI.START}")
                ]

            else:
                ansi_resets = []

            if (
                not (len(ansi_formats) == 1 and ansi_formats[0].count(f"{ANSI.CHAR}{ANSI.START}") >= 1) and \
                not all(f.startswith(f"{ANSI.CHAR}{ANSI.START}") for f in ansi_formats)  # FORMATTING WAS INVALID
            ):
                return match.group(0)
            elif formats_escaped:  # FORMATTING WAS VALID BUT ESCAPED
                return f"[{_formats}]({auto_reset_txt})" if auto_reset_txt else f"[{_formats}]"
            else:
                return (
                    "".join(ansi_formats) + (
                        f"({cls.to_ansi(auto_reset_txt, default_color, brightness_steps, _default_start=False, _validate_default=False)})"
                        if auto_reset_escaped and auto_reset_txt else auto_reset_txt if auto_reset_txt else ""
                    ) + ("" if auto_reset_escaped else "".join(ansi_resets))
                )

        string = "\n".join(_PATTERNS.formatting.sub(replace_keys, line) for line in string.split("\n"))
        return (((cls.__get_default_ansi(default_color) or "") if _default_start else "")
                + string) if default_color is not None else string

    @classmethod
    def escape(
        cls,
        string: str,
        default_color: Optional[Rgba | Hexa] = None,
        _escape_char: Literal["/", "\\"] = "/",
    ) -> str:
        """Escapes all valid formatting codes in the string, so they are visible when output
        to the console using `FormatCodes.print()`. Invalid formatting codes remain unchanged.\n
        -----------------------------------------------------------------------------------------
        - `string` -⠀the string that contains the formatting codes to escape
        - `default_color` -⠀the default text color to use if no other text color was applied
        - `_escape_char` -⠀the character to use to escape formatting codes (`/` or `\\`)\n
        -----------------------------------------------------------------------------------------
        For exact information about how to use special formatting codes,
        see the `format_codes` module documentation."""
        use_default, default_color = cls.__validate_default_color(default_color)

        def escape_format_code(match: Match) -> str:
            """Escape formatting code if it contains valid format keys."""
            formats, auto_reset_txt = match.group(1), match.group(3)

            # CHECK IF ALREADY ESCAPED OR CONTAINS NO FORMATTING
            if not formats or _PATTERNS.escape_char_cond.match(match.group(0)):
                return match.group(0)

            # TEMPORARILY REPLACE `*` FOR VALIDATION
            _formats = formats
            if use_default:
                _formats = _PATTERNS.star_reset_inside.sub(r"\1_|default\2", formats)
            else:
                _formats = _PATTERNS.star_reset_inside.sub(r"\1_\2", formats)

            if all((cls.__get_replacement(k, default_color) != k) for k in cls.__formats_to_keys(_formats)):
                # ESCAPE THE FORMATTING CODE
                escaped = f"[{_escape_char}{formats}]"
                if auto_reset_txt:
                    # RECURSIVELY ESCAPE FORMATTING IN AUTO-RESET TEXT
                    escaped_auto_reset = cls.escape(auto_reset_txt, default_color, _escape_char)
                    escaped += f"({escaped_auto_reset})"
                return escaped
            else:
                # KEEP INVALID FORMATTING CODES AS-IS
                result = f"[{formats}]"
                if auto_reset_txt:
                    # STILL RECURSIVELY PROCESS AUTO-RESET TEXT
                    escaped_auto_reset = cls.escape(auto_reset_txt, default_color, _escape_char)
                    result += f"({escaped_auto_reset})"
                return result

        return "\n".join(_PATTERNS.formatting.sub(escape_format_code, l) for l in string.split("\n"))

    @classmethod
    def escape_ansi(cls, ansi_string: str) -> str:
        """Escapes all ANSI codes in the string, so they are visible when output to the console.\n
        -------------------------------------------------------------------------------------------
        - `ansi_string` -⠀the string that contains the ANSI codes to escape"""
        return ansi_string.replace(ANSI.CHAR, ANSI.ESCAPED_CHAR)

    @classmethod
    def remove(
        cls,
        string: str,
        default_color: Optional[Rgba | Hexa] = None,
        get_removals: bool = False,
        _ignore_linebreaks: bool = False,
    ) -> str | tuple[str, tuple[tuple[int, str], ...]]:
        """Removes all formatting codes from the string with optional tracking of removed codes.\n
        --------------------------------------------------------------------------------------------------------
        - `string` -⠀the string that contains the formatting codes to remove
        - `default_color` -⠀the default text color to use if no other text color was applied
        - `get_removals` -⠀if true, additionally to the cleaned string, a list of tuples will be returned,
          where each tuple contains the position of the removed formatting code and the removed formatting code
        - `_ignore_linebreaks` -⠀whether to ignore line breaks for the removal positions"""
        return cls.remove_ansi(
            cls.to_ansi(string, default_color=default_color),
            get_removals=get_removals,
            _ignore_linebreaks=_ignore_linebreaks,
        )

    @classmethod
    def remove_ansi(
        cls,
        ansi_string: str,
        get_removals: bool = False,
        _ignore_linebreaks: bool = False,
    ) -> str | tuple[str, tuple[tuple[int, str], ...]]:
        """Removes all ANSI codes from the string with optional tracking of removed codes.\n
        ---------------------------------------------------------------------------------------------------
        - `ansi_string` -⠀the string that contains the ANSI codes to remove
        - `get_removals` -⠀if true, additionally to the cleaned string, a list of tuples will be returned,
          where each tuple contains the position of the removed ansi code and the removed ansi code
        - `_ignore_linebreaks` -⠀whether to ignore line breaks for the removal positions"""
        if get_removals:
            removals: list[tuple[int, str]] = []

            def replacement(match: Match) -> str:
                start_pos = match.start() - sum(len(removed) for _, removed in removals)
                if removals and removals[-1][0] == start_pos:
                    start_pos = removals[-1][0]
                removals.append((start_pos, match.group()))
                return ""

            clean_string = _PATTERNS.ansi_seq.sub(
                replacement,
                ansi_string.replace("\n", "") if _ignore_linebreaks else ansi_string  # REMOVE LINEBREAKS FOR POSITIONS
            )
            if _ignore_linebreaks:
                clean_string = _PATTERNS.ansi_seq.sub("", ansi_string)  # BUT KEEP LINEBREAKS IN RETURNED CLEAN STRING

            return clean_string, tuple(removals)

        else:
            return _PATTERNS.ansi_seq.sub("", ansi_string)

    @classmethod
    def _config_console(cls) -> None:
        """Internal method which configure the console to be able to interpret and render ANSI formatting.\n
        -----------------------------------------------------------------------------------------------------
        This method will only do something the first time it's called. Subsequent calls will do nothing."""
        global _CONSOLE_ANSI_CONFIGURED
        if not _CONSOLE_ANSI_CONFIGURED:
            _sys.stdout.flush()
            if _os.name == "nt":
                try:
                    # ENABLE VT100 MODE ON WINDOWS TO BE ABLE TO USE ANSI CODES
                    kernel32 = getattr(_ctypes, "windll").kernel32
                    h = kernel32.GetStdHandle(-11)
                    mode = _ctypes.c_ulong()
                    kernel32.GetConsoleMode(h, _ctypes.byref(mode))
                    kernel32.SetConsoleMode(h, mode.value | 0x0004)
                except Exception:
                    pass
            _CONSOLE_ANSI_CONFIGURED = True

    @classmethod
    def __formats_to_keys(cls, formats: str) -> list[str]:
        return [k.strip() for k in formats.split("|") if k.strip()]

    @classmethod
    def __validate_default_color(cls, default_color: Optional[Rgba | Hexa]) -> tuple[bool, Optional[rgba]]:
        """Validate and convert `default_color` to rgba format."""
        if default_color is None:
            return False, None
        if Color.is_valid_rgba(default_color, False):
            return True, cast(rgba, default_color)
        elif Color.is_valid_hexa(default_color, False):
            return True, Color.to_rgba(default_color)
        raise TypeError("The 'default_color' parameter must be either a valid RGBA or HEXA color, or None.")

    @classmethod
    def __get_default_ansi(
        cls,
        default_color: rgba,
        format_key: Optional[str] = None,
        brightness_steps: Optional[int] = None,
        _modifiers: tuple[str, str] = (_DEFAULT_COLOR_MODS["lighten"], _DEFAULT_COLOR_MODS["darken"]),
    ) -> Optional[str]:
        """Get the `default_color` and lighter/darker versions of it as ANSI code."""
        if not isinstance(default_color, rgba):
            return None
        _default_color: tuple[int, int, int] = tuple(default_color)[:3]
        if brightness_steps is None or (format_key and _PATTERNS.bg_opt_default.search(format_key)):
            return (ANSI.SEQ_BG_COLOR if format_key and _PATTERNS.bg_default.search(format_key) else ANSI.SEQ_COLOR).format(
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
            new_rgb = tuple(Color.adjust_lightness(default_color, (brightness_steps / 100) * adjust))
        elif modifiers in _modifiers[1]:
            new_rgb = tuple(Color.adjust_lightness(default_color, -(brightness_steps / 100) * adjust))
        return (ANSI.SEQ_BG_COLOR if is_bg else ANSI.SEQ_COLOR).format(*new_rgb[:3])

    @classmethod
    def __get_replacement(cls, format_key: str, default_color: Optional[rgba], brightness_steps: int = 20) -> str:
        """Gives you the corresponding ANSI code for the given format key.
        If `default_color` is not `None`, the text color will be `default_color` if all formats
        are reset or you can get lighter or darker version of `default_color` (also as BG)"""
        _format_key, format_key = format_key, cls.__normalize_key(format_key)  # NORMALIZE KEY AND SAVE ORIGINAL
        if default_color and (new_default_color := cls.__get_default_ansi(default_color, format_key, brightness_steps)):
            return new_default_color
        for map_key in ANSI.CODES_MAP:
            if (isinstance(map_key, tuple) and format_key in map_key) or format_key == map_key:
                return _ANSI_SEQ_1.format(
                    next((
                        v for k, v in ANSI.CODES_MAP.items() if format_key == k or (isinstance(k, tuple) and format_key in k)
                    ), None)
                )
        rgb_match = _PATTERNS.rgb.match(format_key)
        hex_match = _PATTERNS.hex.match(format_key)
        try:
            if rgb_match:
                is_bg = rgb_match.group(1)
                r, g, b = map(int, rgb_match.groups()[1:])
                if Color.is_valid_rgba((r, g, b)):
                    return ANSI.SEQ_BG_COLOR.format(r, g, b) if is_bg else ANSI.SEQ_COLOR.format(r, g, b)
            elif hex_match:
                is_bg = hex_match.group(1)
                rgb = Color.to_rgba(hex_match.group(2))
                return (
                    ANSI.SEQ_BG_COLOR.format(rgb[0], rgb[1], rgb[2])
                    if is_bg else ANSI.SEQ_COLOR.format(rgb[0], rgb[1], rgb[2])
                )
        except Exception:
            pass
        return _format_key

    @classmethod
    def __normalize_key(cls, format_key: str) -> str:
        """Normalizes the given format key."""
        k_parts = format_key.replace(" ", "").lower().split(":")
        prefix_str = "".join(
            f"{prefix_key.lower()}:" for prefix_key, prefix_values in _PREFIX.items()
            if any(k_part in prefix_values for k_part in k_parts)
        )
        return prefix_str + ":".join(
            part for part in k_parts if part not in {val
                                                     for values in _PREFIX.values()
                                                     for val in values}
        )
