"""
This module provides the `FormatCodes` (alias `FC`) class together with the `Format` (alias `F`)<br>
and `Term` classes for building richly formatted terminal output using a typed, operator-based syntax.

-----------------------------------------------------------------------------------------------------------
### The Easy Formatting

First, let's take a look at a small example of what a<br>
highly styled output could look like using this module:

```python
FormatCodes(
    "This here is just unformatted text. " + (F.BOLD | F.UNDERLINE | F.BR.BLUE)(
        "Next we have text that is bright blue + bold + underlined."
    ),
    (F.hex("#000") | F.BG.hex("#F67"))(
        "Then there's also black text with a red background."
    ) + " And finally the " + F.ITALIC("(boring)") + " plain text again.",
).print()
```

How all of this exactly works is explained in the sections below. 🠫

-----------------------------------------------------------------------------------------------------------
#### Format Codes and Groups

In this module, you apply styles and colors using `Format` (or its short alias `F`) attributes.<br>
Every format attribute supports two operators:

*   `|` combines two or more format codes into a single immutable group, e.g.<br>
    `F.BOLD | F.RED`  →  bold + red foreground
*   `()` applies the format (or group) to the given text and auto-resets the formatting after it, e.g.<br>
    `F.BOLD("hello")`  →  bold "hello", reset back to normal afterwards<br>
    `(F.BOLD | F.RED)("hello")`  →  same idea, combined

A list of all possible format attributes can be found below.

-----------------------------------------------------------------------------------------------------------
#### Auto Resetting Formats

Every `_Fmt`, `_FmtGroup`, `_ColorFmt` or `_LinkFmt` call automatically generates the<br>
matching reset sequence behind its text, just like shown in the following example:

```python
FormatCodes(
    "This is plain text, "
    + F.BR.BLUE("which is bright blue now.")
    + " Now it was automatically reset to plain again.",
).print()
```

Only the specific formats that were applied are reset; other formatting in scope is left intact:

```python
FormatCodes(
    F.CYAN("This is cyan text, ", F.DIM("which is dimmed now."),
           " Now it's not dimmed any more but still cyan."),
).print()
```

-----------------------------------------------------------------------------------------------------------
#### Bare (Open-Only) Formats

Passing a format object *without calling it* emits only its opening ANSI sequence at that<br>
position, with no matching close/reset appended. This is the typed equivalent of `[…]`<br>
(open bracket without closing braces) from the legacy string syntax:

```python
FormatCodes(
    F.RED, "error: something went wrong ", F.RESET,
    "back to normal",
).print()
```

Any format type supports bare usage: `F.RED` (`_Fmt`), `F.hex("#F67")` (`_ColorFmt`),<br>
`F.link("url")` (`_LinkFmt`), and `F.BOLD | F.RED` (`_FmtGroup`).<br>
Bare formats can also appear inside tuples and nested calls:

```python
FormatCodes(
    F.DIM("a", F.RED, "b", F.RESET_COLOR, "c"),
).print()
```

-----------------------------------------------------------------------------------------------------------
#### Nesting and Multi-Segment Groups

A format call accepts either a single piece of text or any number of mixed segments.<br>
Strings, nested `_Styled` calls, bare format objects, and raw tuples can be mixed freely:

*   `F.X("text")`               – Apply `X` to `"text"`, auto-reset after.
*   `F.X | F.Y`                 – Combine `X` and `Y` into a single group.
*   `(F.X | F.Y)("text")`       – Apply the group to `"text"`.
*   `F.X("a", F.Y("b"), "c")`   – Nested multi-segment: `Y` is applied only to `"b"`.
*   `F.X`                       – Bare: emit only the opening sequence, no auto-reset.
*   `("a", F.X("b"), "c")`      – Same-line group – passed as a single tuple to `FormatCodes(…)`.

Inside `FormatCodes(*segments, sep="\\n")`, every positional argument is treated as one<br>
logical line and joined by `sep`. An empty string argument `""` therefore produces a blank line.

-----------------------------------------------------------------------------------------------------------
#### All Possible Format Attributes

*   Text styles:
    -   `F.BOLD`
    -   `F.DIM`
    -   `F.ITALIC`
    -   `F.UNDERLINE`
    -   `F.INVERSE`
    -   `F.HIDDEN`
    -   `F.STRIKE`
    -   `F.DOUBLE_UNDERLINE`
*   Standard foreground colors:
    -   `F.BLACK`, `F.RED`, `F.GREEN`, `F.YELLOW`,
        `F.BLUE`, `F.MAGENTA`, `F.CYAN`, `F.WHITE`
*   Bright foreground colors (`F.BR.*`):
    -   `F.BR.BLACK`, `F.BR.RED`, `F.BR.GREEN`, …
*   Standard background colors (`F.BG.*`):
    -   `F.BG.BLACK`, `F.BG.RED`, `F.BG.GREEN`, …
*   Bright background colors (`F.BG.BR.*`):
    -   `F.BG.BR.RED`, `F.BG.BR.GREEN`, …
*   24-bit true-color (foreground / background):
    -   `F.rgb(255, 96, 112)`
    -   `F.hex("#FF6070")`  or  `F.hex("F67")`
    -   `F.BG.rgb(0, 0, 0)`
    -   `F.BG.hex("#000")`
*   Hyperlinks (OSC 8):
    -   `F.link("https://example.com")("click here")`
    -   `(F.link("…") | F.BR.BLUE)("click here")`
*   Specific resets (only needed in advanced use; auto-reset usually covers it):
    -   `F.RESET_BOLD`, `F.RESET_DIM`, `F.RESET_ITALIC`, `F.RESET_UNDERLINE`,
        `F.RESET_INVERSE`, `F.RESET_HIDDEN`, `F.RESET_STRIKE`,
        `F.RESET_COLOR`, `F.RESET_BG`
*   Total reset (resets every previously applied formatting):
    -   `F.RESET`

-----------------------------------------------------------------------------------------------------------
#### Terminal Control – the `Term` class

`Term` exposes commonly used non-formatting ANSI sequences for cursor- and screen-control.<br>
These are plain strings (or string-returning helpers), so they can be passed directly into a<br>
`FormatCodes(…)` call or written to `sys.stdout`:

*   `Term.CLEAR_LINE`        – Erase the entire current line.
*   `Term.CLEAR_SCREEN`      – Erase the whole screen.
*   `Term.HIDE_CURSOR`       – Hide the cursor.
*   `Term.SHOW_CURSOR`       – Show the cursor.
*   `Term.ALT_SCREEN`        – Enter the alternate screen buffer.
*   `Term.MAIN_SCREEN`       – Leave the alternate screen buffer.
*   `Term.up(n)`             – Move the cursor up by `n` rows.
*   `Term.down(n)`           – Move the cursor down by `n` rows.
*   `Term.right(n)`          – Move the cursor right by `n` columns.
*   `Term.left(n)`           – Move the cursor left by `n` columns.
*   `Term.move(row, col)`    – Move the cursor to an absolute `(row, col)` position.
*   `Term.title(text)`       – Set the terminal window / tab title (OSC 2).
*   `Term.save()`            – Save the current cursor position.
*   `Term.restore()`         – Restore the previously saved cursor position.
"""

from __future__ import annotations

from .base.consts import ANSI
from .base.decorators import mypyc_attr

from typing import TypeAlias, ClassVar, Iterator, Optional, Final, Union, cast
import ctypes as _ctypes
import regex as _rx
import sys as _sys
import os as _os


_terminal_ansi_configured: bool = False
"""Whether the terminal was already configured to be able to interpret and render ANSI formatting."""


def _config_terminal() -> None:
    """Configure the terminal to be able to interpret and render ANSI formatting.\n
    This function only does something the first time it is called. Subsequent calls are no-ops."""

    global _terminal_ansi_configured
    if _terminal_ansi_configured:
        return

    _sys.stdout.flush()

    if _os.name == "nt":
        try:
            kernel32 = getattr(_ctypes, "windll").kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = _ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, _ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

    _terminal_ansi_configured = True


_ANSI_SEQ_RX: Final = _rx.compile(ANSI.CHAR + r"(?:\].*?(?:\x1b\\|\x07)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_])")
"""Regex pattern matching any ANSI escape sequence (CSI, OSC, or single-character)."""

_RESET_MAP: Final[dict[int, int]] = {
    ######################### TEXT STYLES #########################
    1: 22, 2: 22, 3: 23, 4: 24, 7: 27, 8: 28, 9: 29, 21: 24,
    ########################## FG COLORS ##########################
    30: 39, 31: 39, 32: 39, 33: 39, 34: 39, 35: 39, 36: 39, 37: 39,
    ########################## BG COLORS ##########################
    40: 49, 41: 49, 42: 49, 43: 49, 44: 49, 45: 49, 46: 49, 47: 49,
    ####################### BRIGHT FG COLORS ######################
    90: 39, 91: 39, 92: 39, 93: 39, 94: 39, 95: 39, 96: 39, 97: 39,
    ####################### BRIGHT BG COLORS ######################
    100: 49, 101: 49, 102: 49, 103: 49, 104: 49, 105: 49, 106: 49, 107: 49
}
"""Mapping from format code integer to its matching reset integer.\n
Codes that fully reset everything (`0`) or have no useful specific reset are intentionally omitted."""

_STANDARD_SEQS: Final[
    dict[int, tuple[tuple[str, ...], tuple[str, ...]]],
] = {cid: ((f"{ANSI.CHAR}[{cid}m", ), (f"{ANSI.CHAR}[{reset}m", ))
     for cid, reset in _RESET_MAP.items()}
"""Pre-computed `(opens, closes)` tuple pairs for every standard single-code SGR format.\n
Used as a fast path in `_build_open_close` to avoid per-call list and string allocations."""

################################################## CORE TYPES ##################################################


class _FmtGroup:
    """An immutable, ordered group of format codes produced by `|`.\n
    ------------------------------------------------------------------
    Supports further `|` chaining and `()` application."""

    __slots__ = ("_codes", )

    def __init__(self, *codes: _AnyFmt) -> None:
        self._codes: tuple[_AnyFmt, ...] = codes

    def __iter__(self) -> Iterator[_AnyFmt]:
        """Iterating a `_FmtGroup` yields its individual format codes in order."""

        return iter(self._codes)

    def __or__(self, other: _AnyFmt | _FmtGroup) -> _FmtGroup:
        """Combines this format group with another format or group via `|`."""

        if isinstance(other, _FmtGroup):
            return _FmtGroup(*self._codes, *other._codes)

        return _FmtGroup(*self._codes, other)

    def __ror__(self, other: _AnyFmt) -> _FmtGroup:
        """Combines this format group with another format or group via `|`."""

        return _FmtGroup(other, *self._codes)

    def __call__(self, *text: _Segment) -> _Styled:
        """Applies this format group to the given text, auto-resetting after."""

        opens, closes = _build_open_close(self)
        return _Styled(opens, closes, text[0] if len(text) == 1 else text)

    def __matmul__(self, text: _Text) -> _Styled:
        """Applies this format group to the given text, auto-resetting after."""

        opens, closes = _build_open_close(self)
        return _Styled(opens, closes, text)

    def __repr__(self) -> str:
        """Returns a string representation of this format group, showing its individual codes."""

        return f"_FmtGroup{self._codes!r}"


@mypyc_attr(native_class=False)
class _Fmt(int):
    """A single ANSI format code integer.\n
    ----------------------------------------------------------------------------
    Supports two operators:
    *   `|`  combines two or more codes into a `_FmtGroup` → `F.BOLD | F.RED`
    *   `()` applies the code to text, auto-resetting after → `F.BOLD("hello")`
    ----------------------------------------------------------------------------
    Marked `native_class=False` because MyPyC does not support<br>
    subclassing the built-in `int` type in a native class."""

    _oc: tuple[tuple[str, ...], tuple[str, ...]]

    def __or__(self, other: _AnyFmt | _FmtGroup) -> _FmtGroup:  # type: ignore[override]
        """Combines this format code with another code or group via `|`."""

        if isinstance(other, _FmtGroup):
            return _FmtGroup(self, *other)

        return _FmtGroup(self, other)

    def __ror__(self, other: _AnyFmt) -> _FmtGroup:  # type: ignore[override]
        """Combines this format code with another code or group via `|`."""

        return _FmtGroup(other, self)

    def __call__(self, *text: _Segment) -> _Styled:
        """Applies this format code to the given text, auto-resetting after."""

        try:
            oc = self._oc

        except AttributeError:
            cached = _STANDARD_SEQS.get(int(self))
            oc = _build_open_close(_FmtGroup(self)) if cached is None else cached
            self._oc = oc

        return _Styled(oc[0], oc[1], text[0] if len(text) == 1 else text)

    def __matmul__(self, text: _Text) -> _Styled:
        """Applies this format code to the given text, auto-resetting after."""

        try:
            oc = self._oc

        except AttributeError:
            cached = _STANDARD_SEQS.get(int(self))
            oc = _build_open_close(_FmtGroup(self)) if cached is None else cached
            self._oc = oc

        return _Styled(oc[0], oc[1], text)


class _ColorFmt:
    """A 24-bit true-color format – foreground or background.\n
    ---------------------------------------------------------------------
    >>> F.rgb(255, 96, 112)("text")             # CUSTOM FG COLOR
    >>> F.BG.rgb(0, 0, 0)("text")               # CUSTOM BG COLOR
    >>> F.hex("#FF6070")("text")                # HEX FG COLOR
    >>> (F.BOLD | F.rgb(255, 96, 112))("text")  # COMBINED WITH STYLE"""

    __slots__ = ("_red", "_green", "_blue", "_bg", "_open_seq", "_close_seq")

    def __init__(self, red: int, green: int, blue: int, /, *, bg: bool = False) -> None:
        self._red, self._green, self._blue, self._bg = red, green, blue, bg
        if bg:
            self._open_seq = ANSI.SEQ_BG_COLOR.format(red, green, blue)
            self._close_seq = f"{ANSI.CHAR}[{F.RESET_BG}m"
        else:
            self._open_seq = ANSI.SEQ_FG_COLOR.format(red, green, blue)
            self._close_seq = f"{ANSI.CHAR}[{F.RESET_FG}m"

    @classmethod
    def from_hex(cls, color: str, /, *, bg: bool = False) -> _ColorFmt:
        """Create a `_ColorFmt` from a HEX color string (e.g. `#FF6070` or `F67`)."""

        if (hex_str := color.strip().lstrip("#")).lower().startswith("0x"):
            hex_str = hex_str[2:]
        if len(hex_str) == 3:
            hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2

        return cls(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), bg=bg)

    def __or__(self, other: _AnyFmt | _FmtGroup) -> _FmtGroup:
        """Combines this color format with another format or group via `|`."""

        if isinstance(other, _FmtGroup):
            return _FmtGroup(self, *other._codes)

        return _FmtGroup(self, other)

    def __ror__(self, other: _AnyFmt) -> _FmtGroup:
        """Combines this color format with another format or group via `|`."""

        return _FmtGroup(other, self)

    def __call__(self, *text: _Segment) -> _Styled:
        """Applies this color format to the given text, auto-resetting after."""

        return _Styled((self._open_seq, ), (self._close_seq, ), text[0] if len(text) == 1 else text)

    def __matmul__(self, text: _Text) -> _Styled:
        """Applies this color format to the given text, auto-resetting after."""

        return _Styled((self._open_seq, ), (self._close_seq, ), text)

    def __repr__(self) -> str:
        """Returns a string representation of this color format, indicating<br>
        whether it's foreground or background and its RGB values."""

        return f"_ColorFmt({'bg' if self._bg else 'fg'} {self._red},{self._green},{self._blue})"


class _LinkFmt:
    """An OSC 8 hyperlink. Combine with other formats via `|` to add text styling.\n
    ---------------------------------------------------------------------------------
    >>> F.link("https://example.com")("click here")
    >>> (F.link("https://example.com") | F.BR.BLUE)("click here")"""

    __slots__ = ("_url", "_open_seq", "_close_seq")

    def __init__(self, url: str, /) -> None:
        self._url = url
        self._open_seq = ANSI.SEQ_LINK_OPEN.format(url)
        self._close_seq = ANSI.SEQ_LINK_CLOSE

    def __or__(self, other: _AnyFmt | _FmtGroup) -> _FmtGroup:
        """Combines this link format with another format or group via `|`."""

        if isinstance(other, _FmtGroup):
            return _FmtGroup(self, *other._codes)

        return _FmtGroup(self, other)

    def __ror__(self, other: _AnyFmt) -> _FmtGroup:
        """Combines this link format with another format or group via `|`."""

        return _FmtGroup(other, self)

    def __call__(self, *text: _Segment) -> _Styled:
        """Applies this link format to the given text, auto-resetting after."""

        return _Styled((self._open_seq, ), (self._close_seq, ), text[0] if len(text) == 1 else text)

    def __matmul__(self, text: _Text) -> _Styled:
        """Applies this link format to the given text, auto-resetting after."""

        return _Styled((self._open_seq, ), (self._close_seq, ), text)

    def __repr__(self) -> str:
        """Returns a string representation of this link format, showing the URL it points to."""

        return f"_LinkFmt({self._url!r})"


_AnyFmt: TypeAlias = Union["_Fmt", "_ColorFmt", "_LinkFmt"]
"""Any single format code, color format, or link format<br>
that can be combined via `|` and applied to text."""
_Segment: TypeAlias = Union[str, "_Styled", _AnyFmt, _FmtGroup]
"""A single segment: a plain string, a nested styled segment, or a bare format object (open-only)."""
_Text: TypeAlias = Union[str, "_Styled", _AnyFmt, _FmtGroup, "tuple[_Segment, ...]"]
"""Anything that can be passed to a `_Fmt`/`_FmtGroup`/`_ColorFmt`/`_LinkFmt` call."""
_Renderable: TypeAlias = Union[str, "_Styled", _AnyFmt, _FmtGroup, "tuple[_Segment, ...]"]
"""Anything that can be passed as a positional argument to `FormatCodes(…)`."""


class _Styled:
    """Pre-computed ANSI open/close sequences applied to text.\n
    -------------------------------------------------------------------------------------------
    The renderer emits the opening ANSI codes, then `text`, then the matching reset codes.<br>
    `text` may be a plain `str`, a nested `_Styled`, or a tuple of mixed segments."""

    __slots__ = ("_opens", "_closes", "text")

    def __init__(self, opens: tuple[str, ...], closes: tuple[str, ...], text: _Text) -> None:
        self._opens = opens
        self._closes = closes
        self.text = text

    def __repr__(self) -> str:
        """Returns a string representation of this styled segment, showing its opens and text."""

        return f"_Styled(opens={self._opens!r}, text={self.text!r})"


################################################## NAMESPACE HELPERS ##################################################


class _BgBrNS:
    """Namespace for bright background colors, reachable as `F.BG.BR.*`."""

    BLACK: ClassVar[_Fmt] = _Fmt(100)
    """Bright black background."""
    RED: ClassVar[_Fmt] = _Fmt(101)
    """Bright red background."""
    GREEN: ClassVar[_Fmt] = _Fmt(102)
    """Bright green background."""
    YELLOW: ClassVar[_Fmt] = _Fmt(103)
    """Bright yellow background."""
    BLUE: ClassVar[_Fmt] = _Fmt(104)
    """Bright blue background."""
    MAGENTA: ClassVar[_Fmt] = _Fmt(105)
    """Bright magenta background."""
    CYAN: ClassVar[_Fmt] = _Fmt(106)
    """Bright cyan background."""
    WHITE: ClassVar[_Fmt] = _Fmt(107)
    """Bright white background."""


class _BgNS:
    """Namespace for background colors, reachable as `F.BG.*`."""

    BLACK: ClassVar[_Fmt] = _Fmt(40)
    """Black background."""
    RED: ClassVar[_Fmt] = _Fmt(41)
    """Red background."""
    GREEN: ClassVar[_Fmt] = _Fmt(42)
    """Green background."""
    YELLOW: ClassVar[_Fmt] = _Fmt(43)
    """Yellow background."""
    BLUE: ClassVar[_Fmt] = _Fmt(44)
    """Blue background."""
    MAGENTA: ClassVar[_Fmt] = _Fmt(45)
    """Magenta background."""
    CYAN: ClassVar[_Fmt] = _Fmt(46)
    """Cyan background."""
    WHITE: ClassVar[_Fmt] = _Fmt(47)
    """White background."""
    BR: ClassVar[type[_BgBrNS]] = _BgBrNS

    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _ColorFmt:
        """24-bit background color from RGB components.\n
        `F.BG.rgb(0, 0, 0)("text")`"""

        return _ColorFmt(red, green, blue, bg=True)

    @staticmethod
    def hex(color: str, /) -> _ColorFmt:
        """24-bit background color from HEX string.\n
        `F.BG.hex("#202020")("text")`"""

        return _ColorFmt.from_hex(color, bg=True)


class _BrNS:
    """Namespace for bright foreground colors, reachable as `F.BR.*`."""

    BLACK: ClassVar[_Fmt] = _Fmt(90)
    """Bright black foreground."""
    RED: ClassVar[_Fmt] = _Fmt(91)
    """Bright red foreground."""
    GREEN: ClassVar[_Fmt] = _Fmt(92)
    """Bright green foreground."""
    YELLOW: ClassVar[_Fmt] = _Fmt(93)
    """Bright yellow foreground."""
    BLUE: ClassVar[_Fmt] = _Fmt(94)
    """Bright blue foreground."""
    MAGENTA: ClassVar[_Fmt] = _Fmt(95)
    """Bright magenta foreground."""
    CYAN: ClassVar[_Fmt] = _Fmt(96)
    """Bright cyan foreground."""
    WHITE: ClassVar[_Fmt] = _Fmt(97)
    """Bright white foreground."""


################################################## FORMAT CODES ##################################################


class Format:
    """All available ANSI format codes.\n
    -----------------------------------------------------------------------------------------
    Every attribute supports `|` for combining and `()` for applying to text:

    >>> F.BOLD("hello")                   # BOLD, AUTO-RESET AFTER
    >>> (F.BOLD | F.RED)("hello")         # BOLD + RED, AUTO-RESET AFTER
    >>> F.BR.GREEN("hello")               # BRIGHT GREEN
    >>> F.BG.BLACK("hello")               # BLACK BACKGROUND
    >>> F.DIM("# ", F.ITALIC("comment"))  # NESTED: DIM WRAPS ITALIC INSIDE

    For a full list of available attributes, see the `format_codes` module documentation."""

    ######################### TOTAL RESET #########################
    RESET: ClassVar[_Fmt] = _Fmt(0)
    """Reset all formatting to default."""

    ####################### SPECIFIC RESETS #######################
    RESET_BOLD: ClassVar[_Fmt] = _Fmt(22)
    """Reset bold (also resets dim, as they share the same code)."""
    RESET_DIM: ClassVar[_Fmt] = _Fmt(22)
    """Reset dim (also resets bold, as they share the same code)."""
    RESET_ITALIC: ClassVar[_Fmt] = _Fmt(23)
    """Reset italic."""
    RESET_UNDERLINE: ClassVar[_Fmt] = _Fmt(24)
    """Reset underline and double underline."""
    RESET_INVERSE: ClassVar[_Fmt] = _Fmt(27)
    """Reset inverse."""
    RESET_HIDDEN: ClassVar[_Fmt] = _Fmt(28)
    """Reset hidden."""
    RESET_STRIKETHROUGH: ClassVar[_Fmt] = _Fmt(29)
    """Reset strikethrough."""
    RESET_FG: ClassVar[_Fmt] = _Fmt(39)
    """Reset foreground color."""
    RESET_BG: ClassVar[_Fmt] = _Fmt(49)
    """Reset background color."""

    ######################### TEXT STYLES #########################
    BOLD: ClassVar[_Fmt] = _Fmt(1)
    """Bold text.\n
    Note that this is also reset by `RESET_DIM`."""
    DIM: ClassVar[_Fmt] = _Fmt(2)
    """Dim text.\n
    Note that this is also reset by `RESET_BOLD`."""
    ITALIC: ClassVar[_Fmt] = _Fmt(3)
    """Italic text."""
    UNDERLINE: ClassVar[_Fmt] = _Fmt(4)
    """Underline text."""
    INVERSE: ClassVar[_Fmt] = _Fmt(7)
    """Inverse colors (swap foreground and background colors)."""
    HIDDEN: ClassVar[_Fmt] = _Fmt(8)
    """Hidden (invisible) text."""
    STRIKETHROUGH: ClassVar[_Fmt] = _Fmt(9)
    """Strikethrough text."""
    DOUBLE_UNDERLINE: ClassVar[_Fmt] = _Fmt(21)
    """Double underline text."""

    ###################### STANDARD FG COLORS #####################
    BLACK: ClassVar[_Fmt] = _Fmt(30)
    """Black foreground."""
    RED: ClassVar[_Fmt] = _Fmt(31)
    """Red foreground."""
    GREEN: ClassVar[_Fmt] = _Fmt(32)
    """Green foreground."""
    YELLOW: ClassVar[_Fmt] = _Fmt(33)
    """Yellow foreground."""
    BLUE: ClassVar[_Fmt] = _Fmt(34)
    """Blue foreground."""
    MAGENTA: ClassVar[_Fmt] = _Fmt(35)
    """Magenta foreground."""
    CYAN: ClassVar[_Fmt] = _Fmt(36)
    """Cyan foreground."""
    WHITE: ClassVar[_Fmt] = _Fmt(37)
    """White foreground."""

    ######################### NAMESPACES ##########################
    BR: ClassVar[type[_BrNS]] = _BrNS
    BG: ClassVar[type[_BgNS]] = _BgNS

    #################### CUSTOM COLORS & LINKS ####################
    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _ColorFmt:
        """24-bit foreground color.\n
        `F.rgb(255, 96, 112)("text")`"""

        return _ColorFmt(red, green, blue)

    @staticmethod
    def hex(color: str, /) -> _ColorFmt:
        """24-bit foreground color from HEX string.\n
        `F.hex("#FF6070")("text")` or `F.hex("F67")`"""

        return _ColorFmt.from_hex(color)

    @staticmethod
    def link(url: str, /) -> _LinkFmt:
        """Clickable hyperlink.\n
        `F.link("https://example.com")("click here")`"""

        return _LinkFmt(url)


F = Format  # SHORT ALIAS

################################################## TERMINAL CONTROL ##################################################


class Term:
    """Common ANSI terminal control sequences (cursor, screen, title)<br>
    as plain strings or string-returning static methods.\n
    ------------------------------------------------------------------------------------------
    Values can be passed straight into a `FormatCodes(…)` call or written to `sys.stdout`."""

    CLEAR_LINE: ClassVar[str] = f"{ANSI.CHAR}[2K"
    """Erase the entire current line."""
    CLEAR_SCREEN: ClassVar[str] = f"{ANSI.CHAR}[2J"
    """Erase the whole screen."""
    HIDE_CURSOR: ClassVar[str] = f"{ANSI.CHAR}[?25l"
    """Hide the cursor."""
    SHOW_CURSOR: ClassVar[str] = f"{ANSI.CHAR}[?25h"
    """Show the cursor."""
    ALT_SCREEN: ClassVar[str] = f"{ANSI.CHAR}[?1049h"
    """Enter the alternate screen buffer."""
    MAIN_SCREEN: ClassVar[str] = f"{ANSI.CHAR}[?1049l"
    """Leave the alternate screen buffer."""

    @staticmethod
    def up(n: int = 1, /) -> str:
        """Move the cursor up by `n` rows."""

        return f"{ANSI.CHAR}[{n}A"

    @staticmethod
    def down(n: int = 1, /) -> str:
        """Move the cursor down by `n` rows."""

        return f"{ANSI.CHAR}[{n}B"

    @staticmethod
    def right(n: int = 1, /) -> str:
        """Move the cursor right by `n` columns."""

        return f"{ANSI.CHAR}[{n}C"

    @staticmethod
    def left(n: int = 1, /) -> str:
        """Move the cursor left by `n` columns."""

        return f"{ANSI.CHAR}[{n}D"

    @staticmethod
    def move(row: int, col: int, /) -> str:
        """Move the cursor to absolute position `(row, col)` (1-based)."""

        return f"{ANSI.CHAR}[{row};{col}H"

    @staticmethod
    def title(text: str, /) -> str:
        """Set the terminal window / tab title (OSC 2)."""

        return f"{ANSI.CHAR}]2;{text}\x07"

    @staticmethod
    def save() -> str:
        """Save the current cursor position."""

        return f"{ANSI.CHAR}[s"

    @staticmethod
    def restore() -> str:
        """Restore the previously saved cursor position."""

        return f"{ANSI.CHAR}[u"


################################################## FORMATCODES ##################################################


def _build_open_close(group: _FmtGroup, /) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Build the opening and closing ANSI sequences for a `_FmtGroup`.\n
    ------------------------------------------------------------------------------------
    Returns a `(opens, closes)` pair of tuples. Multiple opens / closes are emitted<br>
    only when both an OSC 8 hyperlink and SGR codes are present (OSC wraps SGR)."""

    # FAST PATH: SINGLE STANDARD _Fmt CODE (REALLY COMMON)
    if len(codes := group._codes) == 1 and type(codes[0]) is _Fmt:
        if (cached := _STANDARD_SEQS.get(int(codes[0]))) is not None:
            return cached

    sgr_open: list[str] = []
    sgr_close: list[str] = []
    link_url: Optional[str] = None

    for code in group:
        if isinstance(code, _LinkFmt):
            link_url = code._url

        elif isinstance(code, _ColorFmt):
            if code._bg:
                sgr_open.append(f"48;2;{code._red};{code._green};{code._blue}")
                sgr_close.append("49")
            else:
                sgr_open.append(f"38;2;{code._red};{code._green};{code._blue}")
                sgr_close.append("39")

        else:
            cid = int(code)
            sgr_open.append(str(cid))
            if (reset := _RESET_MAP.get(cid)) is not None:
                sgr_close.append(str(reset))

    # DE-DUPE WHILE PRESERVING ORDER FOR CLEANER OUTPUT
    seen: set[str] = set()
    dedup_close: list[str] = []

    for close_code in sgr_close:
        if close_code not in seen:
            seen.add(close_code)
            dedup_close.append(close_code)

    opens: list[str] = []
    closes: list[str] = []

    if link_url is not None:
        opens.append(ANSI.SEQ_LINK_OPEN.format(link_url))
    if sgr_open:
        opens.append(f"{ANSI.CHAR}[{';'.join(sgr_open)}m")
    if dedup_close:
        closes.append(f"{ANSI.CHAR}[{';'.join(dedup_close)}m")
    if link_url is not None:
        closes.append(ANSI.SEQ_LINK_CLOSE)

    return tuple(opens), tuple(closes)


class FormatCodes:
    """Build a formatted string from a sequence of segments<br>
    (strings, `_Styled` calls, or raw tuples), joined by `sep`.\n
    ------------------------------------------------------------------------------------------------------
    *   `segments` – Any number of segments to render. Each positional argument represents one logical line.
    *   `sep` – The separator inserted between two adjacent positional arguments (default `"\\n"`).
    ------------------------------------------------------------------------------------------------------
    After construction the instance exposes:
    *   `ansi` – The fully rendered ANSI escape string, ready to be written to a terminal.
    *   `raw` – `ansi` with every ANSI escape sequence stripped; computed on demand.
    *   `code_positions` – A tuple of `(position, sequence)` pairs giving<br>
        the start offset of every ANSI escape sequence inside `ansi`; computed on demand.
    ------------------------------------------------------------------------------------------------------
    For exact information about how to use the operator syntax,<br>
    see the `format_codes` module documentation."""

    __slots__ = ("_ansi_parts", "ansi")

    def __init__(self, /, *segments: _Renderable, sep: str = "\n") -> None:
        self._ansi_parts: list[str] = []

        for i, segment in enumerate(segments):
            if i > 0:
                self._ansi_parts.append(sep)
            self._render(segment)

        self.ansi: str = "".join(self._ansi_parts)

    @property
    def raw(self) -> str:
        """The rendered output with every ANSI escape sequence stripped (the "plain" text)."""

        return _ANSI_SEQ_RX.sub("", self.ansi)

    @property
    def code_positions(self) -> tuple[tuple[int, str], ...]:
        """A tuple of `(position, sequence)` pairs giving the<br>
        start offset of every ANSI escape sequence inside `ansi`."""

        return tuple((match.start(), match.group()) for match in _ANSI_SEQ_RX.finditer(self.ansi))

    def __str__(self) -> str:
        """Stringifying a `FormatCodes` instance yields its rendered<br>
        ANSI string, ready to be written to a terminal."""

        return self.ansi

    def __repr__(self) -> str:
        """Returns a string representation of this `FormatCodes` instance, showing its rendered ANSI string."""

        return f"FormatCodes(ansi={self.ansi!r})"

    def print(self, /, *, end: str = "\n", flush: bool = True) -> None:
        """Write the rendered ANSI string straight to `sys.stdout` (configuring the terminal<br>
        for ANSI on first use). Faster than the built-in `print()` for large outputs.\n
        -----------------------------------------------------------------------------------------
        *   `end` – The string to append at the end of the output (default `"\\n"`).
        *   `flush` – Whether to flush `sys.stdout` after writing (default `True`)."""

        _config_terminal()
        _sys.stdout.write(self.ansi + end)

        if flush:
            _sys.stdout.flush()

    def input(self, /, *, reset_ansi: bool = False) -> str:
        """Use the rendered ANSI string as an input prompt and return the user's input.\n
        ----------------------------------------------------------------------------------
        *   `reset_ansi` – If true, all ANSI formatting will be reset after<br>
            the user confirmed the input and the program continues to run."""

        _config_terminal()
        user_input = input(self.ansi)

        if reset_ansi:
            _sys.stdout.write(f"{ANSI.CHAR}[0m")

        return user_input

    @staticmethod
    def remove_ansi(ansi_string: str, /) -> str:
        """Remove every ANSI escape sequence from `ansi_string`, returning the plain text.\n
        -------------------------------------------------------------------------------------
        *   `ansi_string` – The string that contains the ANSI codes to remove."""

        return _ANSI_SEQ_RX.sub("", ansi_string)

    def _render(self, segment: object) -> None:
        """Internal method to recursively render a `segment`, dispatching by runtime type.\n
        ------------------------------------------------------------------------------------
        Strings are emitted as raw text; `_Styled` segments are wrapped in their opening<br>
        and closing ANSI sequences; `tuple` segments are flattened in order.<br>
        Bare format objects (`_Fmt`, `_ColorFmt`, `_LinkFmt`, `_FmtGroup`) emit only<br>
        their opening sequence with no matching close."""

        if isinstance(segment, str):
            self._ansi_parts.append(segment)
            return
        if isinstance(segment, _Styled):
            for piece in segment._opens:
                self._ansi_parts.append(piece)
            self._render(segment.text)
            for piece in segment._closes:
                self._ansi_parts.append(piece)
            return
        if isinstance(segment, tuple):
            for tuple_part in cast("tuple[object, ...]", segment):
                self._render(tuple_part)
            return
        if isinstance(segment, _Fmt):
            self._ansi_parts.append(f"{ANSI.CHAR}[{int(segment)}m")
            return
        if isinstance(segment, _ColorFmt):
            self._ansi_parts.append(segment._open_seq)
            return
        if isinstance(segment, _LinkFmt):
            self._ansi_parts.append(segment._open_seq)
            return
        if isinstance(segment, _FmtGroup):
            for piece in _build_open_close(segment)[0]:
                self._ansi_parts.append(piece)
            return

        # FALLBACK – COERCE UNKNOWN OBJECTS TO STR
        self._ansi_parts.append(str(segment))


FC = FormatCodes  # SHORT ALIAS
