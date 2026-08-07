"""
This module provides the `StyledText` class together with the `S` and `Term` classes<br>
for building richly styled terminal output using a typed, operator-based syntax.

-----------------------------------------------------------------------------------------------------------
### The Easy Styling

First, let's take a look at a small example of what a<br>
highly styled output could look like using this module:

```python
StyledText(
    "This here is just unstyled text. " + (S.BOLD | S.UNDERLINE | S.BR.BLUE)(
        "Next we have text that is bright blue + bold + underlined."
    ),
    (S.hex("#000") | S.BG.hex("#F67"))(
        "Then there's also black text with a red background."
    ) + " And finally the " + S.ITALIC("(boring)") + " plain text again.",
).print()
```

How all of this exactly works is explained in the sections below. 🠫

-----------------------------------------------------------------------------------------------------------
#### Styles and Groups

In this module, you apply styles and colors using `S` attributes.<br>
Every style attribute supports two operators:

*   `|` combines two or more styles into a single immutable group, e.g.<br>
    `S.BOLD | S.RED`  →  bold + red foreground
*   `()` applies the style (or group) to the given text and auto-resets the style after it, e.g.<br>
    `S.BOLD("hello")`  →  bold "hello", reset back to normal afterwards<br>
    `(S.BOLD | S.RED)("hello")`  →  same idea, combined

A list of all possible style attributes can be found below.

-----------------------------------------------------------------------------------------------------------
#### Auto Resetting Styles

Every `_Style`, `_StyleGroup`, `_ColorStyle` or `_Link` call automatically generates the<br>
matching reset sequence behind its text, just like shown in the following example:

```python
StyledText(
    "This is plain text, "
    + S.BR.BLUE("which is bright blue now.")
    + " Now it was automatically reset to plain again.",
).print()
```

Only the specific styles that were applied are reset; other styling in scope is left intact:

```python
StyledText(
    S.CYAN("This is cyan text, ", S.DIM("which is dimmed now."),
           " Now it's not dimmed any more but still cyan."),
).print()
```

-----------------------------------------------------------------------------------------------------------
#### Bare (Open-Only) Styles

Passing a style object *without calling it* emits only its opening ANSI sequence at that<br>
position, with no matching close/reset appended. This is the typed equivalent of `[…]`<br>
(open bracket without closing braces) from the legacy string syntax:

```python
StyledText(
    S.RED, "error: something went wrong ", S.RESET,
    "back to normal",
).print()
```

Any style type supports bare usage: `S.RED` (`_Style`), `S.hex("#F67")` (`_ColorStyle`),<br>
`S.link("url")` (`_Link`), and `S.BOLD | S.RED` (`_StyleGroup`).<br>
Bare styles can also appear inside tuples and nested calls:

```python
StyledText(
    S.DIM("a", S.RED, "b", S.RESET_COLOR, "c"),
).print()
```

-----------------------------------------------------------------------------------------------------------
#### Nesting and Multi-Segment Groups

A style call accepts either a single piece of text or any number of mixed segments.<br>
Strings, nested `_StyledSequence` calls, bare style objects, and raw tuples can be mixed freely:

*   `S.X("text")`               – Apply `X` to `"text"`, auto-reset after.
*   `S.X | S.Y`                 – Combine `X` and `Y` into a single group.
*   `(S.X | S.Y)("text")`       – Apply the group to `"text"`.
*   `S.X("a", S.Y("b"), "c")`   – Nested multi-segment: `Y` is applied only to `"b"`.
*   `S.X`                       – Bare: emit only the opening sequence, no auto-reset.
*   `("a", S.X("b"), "c")`      – Same-line group; passed as a single tuple to `StyledText(…)`.

Inside `StyledText(*segments, sep="\\n")`, every positional argument is treated as one<br>
logical line and joined by `sep`. An empty string argument `""` therefore produces a blank line.

-----------------------------------------------------------------------------------------------------------
#### All Possible Style Attributes

*   Text styles:
    -   `S.BOLD`
    -   `S.DIM`
    -   `S.ITALIC`
    -   `S.UNDERLINE`
    -   `S.INVERSE`
    -   `S.HIDDEN`
    -   `S.STRIKE`
    -   `S.DOUBLE_UNDERLINE`
*   Standard foreground colors:
    -   `S.BLACK`, `S.RED`, `S.GREEN`, `S.YELLOW`,
        `S.BLUE`, `S.MAGENTA`, `S.CYAN`, `S.WHITE`
*   Bright foreground colors (`S.BR.*`):
    -   `S.BR.BLACK`, `S.BR.RED`, `S.BR.GREEN`, …
*   Standard background colors (`S.BG.*`):
    -   `S.BG.BLACK`, `S.BG.RED`, `S.BG.GREEN`, …
*   Bright background colors (`S.BG.BR.*`):
    -   `S.BG.BR.RED`, `S.BG.BR.GREEN`, …
*   24-bit true-color (foreground / background):
    -   `S.rgb(255, 96, 112)`
    -   `S.hex("#FF6070")`  or  `S.hex("F67")`
    -   `S.BG.rgb(0, 0, 0)`
    -   `S.BG.hex("#000")`
*   Hyperlinks (OSC 8):
    -   `S.link("https://example.com")("click here")`
    -   `(S.link("…") | S.BR.BLUE)("click here")`
*   Specific resets (only needed in advanced use; auto-reset usually covers it):
    -   `S.RESET_BOLD`, `S.RESET_DIM`, `S.RESET_ITALIC`, `S.RESET_UNDERLINE`,
        `S.RESET_INVERSE`, `S.RESET_HIDDEN`, `S.RESET_STRIKE`,
        `S.RESET_COLOR`, `S.RESET_BG`
*   Total reset (resets every previously applied styles):
    -   `S.RESET`

-----------------------------------------------------------------------------------------------------------
#### Terminal Control – the `Term` class

`Term` exposes commonly used non-styling ANSI sequences for cursor- and screen-control.<br>
These are plain strings (or string-returning helpers), so they can be passed directly into a<br>
`StyledText(…)` call or written to `sys.stdout`:

*   `Term.CLEAR_LINE`       – Erase the entire current line.
*   `Term.CLEAR_SCREEN`     – Erase the whole screen.
*   `Term.HIDE_CURSOR`      – Hide the cursor.
*   `Term.SHOW_CURSOR`      – Show the cursor.
*   `Term.ALT_SCREEN`       – Enter the alternate screen buffer.
*   `Term.MAIN_SCREEN`      – Leave the alternate screen buffer.
*   `Term.up(n)`            – Move the cursor up by `n` rows.
*   `Term.down(n)`          – Move the cursor down by `n` rows.
*   `Term.right(n)`         – Move the cursor right by `n` columns.
*   `Term.left(n)`          – Move the cursor left by `n` columns.
*   `Term.move(row, col)`   – Move the cursor to an absolute `(row, col)` position.
*   `Term.title(text)`      – Set the terminal window / tab title (OSC 2).
*   `Term.save()`           – Save the current cursor position.
*   `Term.restore()`        – Restore the previously saved cursor position.
"""

from __future__ import annotations

from .base.consts import ANSI

import ctypes as _ctypes
import os as _os
import sys as _sys
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Final, TextIO, cast

if TYPE_CHECKING:
    import sys
    from collections.abc import Iterable, Iterator
    import regex as _rx

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs

_terminal_ansi_configured: bool = False
"""Whether the terminal was already configured to be able to interpret and render ANSI styling."""

_ANSI_SEQ_RX: Final[_rx.Pattern[str]] = ANSI.SEQ_PATTERN
"""Module shorthand for `ANSI.SEQ_PATTERN`.<br>
Matches any ANSI escape sequence (CSI, OSC, or single-character)."""

_RESET_MAP: Final[dict[int, int]] = {
    # Text styles:
    1: 22,
    2: 22,
    3: 23,
    4: 24,
    7: 27,
    8: 28,
    9: 29,
    21: 24,
    # FG colors:
    30: 39,
    31: 39,
    32: 39,
    33: 39,
    34: 39,
    35: 39,
    36: 39,
    37: 39,
    # BG colors:
    40: 49,
    41: 49,
    42: 49,
    43: 49,
    44: 49,
    45: 49,
    46: 49,
    47: 49,
    # Bright FG colors:
    90: 39,
    91: 39,
    92: 39,
    93: 39,
    94: 39,
    95: 39,
    96: 39,
    97: 39,
    # Bright BG colors:
    100: 49,
    101: 49,
    102: 49,
    103: 49,
    104: 49,
    105: 49,
    106: 49,
    107: 49,
}
"""Mapping from ANSI style integer to its matching reset integer.\n
Codes that fully reset everything (`0`) or have no useful specific reset are intentionally omitted."""

_STANDARD_SEQS: Final[dict[int, tuple[tuple[str, ...], tuple[str, ...]]],] = {
    cid: ((f"{ANSI.CHAR}[{cid}m",), (f"{ANSI.CHAR}[{reset}m",)) for cid, reset in _RESET_MAP.items()
}
"""Pre-computed `(opens, closes)` tuple pairs for every standard single-code SGR style.\n
Used as a fast path in `_build_open_close` to avoid per-call list and string allocations."""


####################################################### CORE TYPES #######################################################


class _StyleGroup:
    """An immutable, ordered group of styles produced by `|`.\n
    ------------------------------------------------------------------
    Supports further `|` chaining and `()` application."""

    __slots__: Final[tuple[str, ...]] = ("_codes",)

    def __init__(self, *codes: BaseStyle) -> None:
        self._codes: tuple[BaseStyle, ...] = codes

    def __iter__(self) -> Iterator[BaseStyle]:
        """Iterating a `_StyleGroup` yields its individual styles in order."""

        return iter(self._codes)

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this style group with another style or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(*self._codes, *other._codes)

        return _StyleGroup(*self._codes, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this style group with another style or group via `|`."""

        return _StyleGroup(other, *self._codes)

    def __call__(self, *text: RenderSegment) -> _StyledSequence:
        """Applies this style group to the given text, auto-resetting after."""

        opens, closes = _build_open_close(self)
        return _StyledSequence(opens, closes, text[0] if len(text) == 1 else text)

    def __matmul__(self, text: Renderable) -> _StyledSequence:
        """Applies this style group to the given text, auto-resetting after."""

        opens, closes = _build_open_close(self)
        return _StyledSequence(opens, closes, text)

    def __repr__(self) -> str:
        """Returns a string representation of this style group, showing its individual codes."""

        return f"_StyleGroup{self._codes!r}"


class _Style:
    """A single ANSI style integer.\n
    ----------------------------------------------------------------------------
    Supports two operators:
    *   `|`  combines two or more codes into a `_StyleGroup` → `S.BOLD | S.RED`
    *   `()` applies the code to text, auto-resetting after → `S.BOLD("hello")`
    ----------------------------------------------------------------------------
    """

    __slots__: Final[tuple[str, ...]] = ("_oc", "_value")
    _oc: tuple[tuple[str, ...], tuple[str, ...]]

    def __init__(self, value: int, /) -> None:
        self._value: int = value

    def __int__(self) -> int:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self._value == other
        if isinstance(other, _Style):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this style with another code or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(self, *other)

        return _StyleGroup(self, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this style with another code or group via `|`."""

        return _StyleGroup(other, self)

    def __call__(self, *text: RenderSegment) -> _StyledSequence:
        """Applies this style code to the given text, auto-resetting after."""

        try:
            oc = self._oc

        except AttributeError:
            cached = _STANDARD_SEQS.get(int(self))
            oc = _build_open_close(_StyleGroup(self)) if cached is None else cached
            self._oc = oc

        return _StyledSequence(oc[0], oc[1], text[0] if len(text) == 1 else text)

    def __matmul__(self, text: Renderable) -> _StyledSequence:
        """Applies this style code to the given text, auto-resetting after."""

        try:
            oc = self._oc

        except AttributeError:
            cached = _STANDARD_SEQS.get(int(self))
            oc = _build_open_close(_StyleGroup(self)) if cached is None else cached
            self._oc = oc

        return _StyledSequence(oc[0], oc[1], text)


class _ColorStyle:
    """A 24-bit true-color style – foreground or background.\n
    ---------------------------------------------------------------------
    >>> S.rgb(255, 96, 112)("text")             # Custom FG color
    >>> S.BG.rgb(0, 0, 0)("text")               # Custom BG color
    >>> S.hex("#FF6070")("text")                # Hex FG color
    >>> (S.BOLD | S.rgb(255, 96, 112))("text")  # Combined with style"""

    __slots__: Final[tuple[str, ...]] = ("_bg", "_blue", "_close_seq", "_green", "_open_seq", "_red")

    def __init__(self, red: int, green: int, blue: int, /, *, bg: bool = False) -> None:
        self._red: int = red
        self._green: int = green
        self._blue: int = blue
        self._bg: bool = bg
        self._open_seq: str
        self._close_seq: str

        if bg:
            self._open_seq = ANSI.SEQ_BG_COLOR.format(red, green, blue)
            self._close_seq = f"{ANSI.CHAR}[{S.RESET_BG}m"
        else:
            self._open_seq = ANSI.SEQ_FG_COLOR.format(red, green, blue)
            self._close_seq = f"{ANSI.CHAR}[{S.RESET_FG}m"

    @classmethod
    def from_hex(cls, color: str, /, *, bg: bool = False) -> _ColorStyle:
        """Create a `_ColorStyle` from a HEX color string (e.g., `#FF6070` or `F67`)."""

        if (hex_str := color.strip().lstrip("#")).lower().startswith("0x"):
            hex_str = hex_str[2:]
        if len(hex_str) == 3:
            hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2

        return cls(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), bg=bg)

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this color style with another style or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(self, *other._codes)

        return _StyleGroup(self, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this color style with another style or group via `|`."""

        return _StyleGroup(other, self)

    def __call__(self, *text: RenderSegment) -> _StyledSequence:
        """Applies this color style to the given text, auto-resetting after."""

        return _StyledSequence((self._open_seq,), (self._close_seq,), text[0] if len(text) == 1 else text)

    def __matmul__(self, text: Renderable) -> _StyledSequence:
        """Applies this color style to the given text, auto-resetting after."""

        return _StyledSequence((self._open_seq,), (self._close_seq,), text)

    def __repr__(self) -> str:
        """Returns a string representation of this color style, indicating<br>
        whether it's foreground or background and its RGB values."""

        return f"_ColorStyle({'bg' if self._bg else 'fg'} {self._red},{self._green},{self._blue})"


class _Link:
    """An OSC 8 hyperlink. Combine with other styles via `|` to add text styling.\n
    ---------------------------------------------------------------------------------
    >>> S.link("https://example.com")("click here")
    >>> (S.link("https://example.com") | S.BR.BLUE)("click here")"""

    __slots__: Final[tuple[str, ...]] = ("_close_seq", "_open_seq", "_url")

    def __init__(self, url: str | Path, /) -> None:
        self._url: str = url.resolve().as_uri() if isinstance(url, Path) else url
        self._open_seq: str = ANSI.SEQ_LINK_OPEN.format(self._url)
        self._close_seq: str = ANSI.SEQ_LINK_CLOSE

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this link style with another style or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(self, *other._codes)

        return _StyleGroup(self, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this link style with another style or group via `|`."""

        return _StyleGroup(other, self)

    def __call__(self, *text: RenderSegment) -> _StyledSequence:
        """Applies this link style to the given text, auto-resetting after."""

        return _StyledSequence((self._open_seq,), (self._close_seq,), text[0] if len(text) == 1 else text)

    def __matmul__(self, text: Renderable) -> _StyledSequence:
        """Applies this link style to the given text, auto-resetting after."""

        return _StyledSequence((self._open_seq,), (self._close_seq,), text)

    def __repr__(self) -> str:
        """Returns a string representation of this link style, showing the URL it points to."""

        return f"_Link({self._url!r})"


class _StyledSequence:
    """Pre-computed ANSI open/close sequences applied to text.\n
    -------------------------------------------------------------------------------------------
    The renderer emits the opening ANSI codes, then `text`, then the matching reset codes.<br>
    `text` may be a plain `str`, a nested `_StyledSequence`, or a tuple of mixed segments."""

    __slots__: Final[tuple[str, ...]] = ("_closes", "_opens", "text")

    def __init__(self, opens: tuple[str, ...], closes: tuple[str, ...], text: Renderable) -> None:
        self._opens: tuple[str, ...] = opens
        self._closes: tuple[str, ...] = closes
        self.text: Renderable = text

    def __repr__(self) -> str:
        """Returns a string representation of this styled segment, showing its opens and text."""

        return f"_StyledSequence(opens={self._opens!r}, text={self.text!r})"


##################### PUBLIC TYPE HELPERS #####################

type BaseStyle = _Style | _ColorStyle | _Link
"""Any single style code, color style, or link style that can be combined via `|` and applied to text."""


def is_base_style(obj: object, /) -> TypeIs[BaseStyle]:
    """Returns true if `obj` is an instance that matches the `BaseStyle` type."""

    return isinstance(obj, (_Style, _ColorStyle, _Link))


type AnyStyle = BaseStyle | _StyleGroup
"""Any single style or group of styles that can be combined via `|` and applied to text."""


def is_any_style(obj: object, /) -> TypeIs[AnyStyle]:
    """Returns true if `obj` is an instance that matches the `AnyStyle` type."""

    return isinstance(obj, (_Style, _ColorStyle, _Link, _StyleGroup))


type RenderSegment = str | _StyledSequence | AnyStyle
"""A single segment: a plain string, a nested styled segment, or a bare style object (open-only)."""


def is_render_segment(obj: object, /) -> TypeIs[RenderSegment]:
    """Returns true if `obj` is an instance that matches the `RenderSegment` type."""

    return isinstance(obj, (str, _StyledSequence, _Style, _ColorStyle, _Link, _StyleGroup))


type Renderable = RenderSegment | tuple[RenderSegment, ...]
"""Anything that can be styled or rendered.<br>
Can be passed to a `_Style` call, or as a positional argument to `StyledText(…)`."""


def is_renderable(obj: object, /) -> TypeIs[Renderable]:
    """Returns true if `obj` is an instance that matches the `Renderable` type."""

    return isinstance(obj, (str, _StyledSequence, _Style, _ColorStyle, _Link, _StyleGroup, tuple))


#################################################### NAMESPACE HELPERS ###################################################


class _BgBrNS:
    """Namespace for bright background colors, reachable as `S.BG.BR.*`."""

    BLACK: ClassVar[_Style] = _Style(100)
    """Bright black background."""
    RED: ClassVar[_Style] = _Style(101)
    """Bright red background."""
    GREEN: ClassVar[_Style] = _Style(102)
    """Bright green background."""
    YELLOW: ClassVar[_Style] = _Style(103)
    """Bright yellow background."""
    BLUE: ClassVar[_Style] = _Style(104)
    """Bright blue background."""
    MAGENTA: ClassVar[_Style] = _Style(105)
    """Bright magenta background."""
    CYAN: ClassVar[_Style] = _Style(106)
    """Bright cyan background."""
    WHITE: ClassVar[_Style] = _Style(107)
    """Bright white background."""


class _BgNS:
    """Namespace for background colors, reachable as `S.BG.*`."""

    BLACK: ClassVar[_Style] = _Style(40)
    """Black background."""
    RED: ClassVar[_Style] = _Style(41)
    """Red background."""
    GREEN: ClassVar[_Style] = _Style(42)
    """Green background."""
    YELLOW: ClassVar[_Style] = _Style(43)
    """Yellow background."""
    BLUE: ClassVar[_Style] = _Style(44)
    """Blue background."""
    MAGENTA: ClassVar[_Style] = _Style(45)
    """Magenta background."""
    CYAN: ClassVar[_Style] = _Style(46)
    """Cyan background."""
    WHITE: ClassVar[_Style] = _Style(47)
    """White background."""
    BR: ClassVar[type[_BgBrNS]] = _BgBrNS

    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _ColorStyle:
        """24-bit background color from RGB components.\n
        `S.BG.rgb(0, 0, 0)("text")`"""

        return _ColorStyle(red, green, blue, bg=True)

    @staticmethod
    def hex(color: str, /) -> _ColorStyle:
        """24-bit background color from HEX string.\n
        `S.BG.hex("#202020")("text")`"""

        return _ColorStyle.from_hex(color, bg=True)


class _BrNS:
    """Namespace for bright foreground colors, reachable as `S.BR.*`."""

    BLACK: ClassVar[_Style] = _Style(90)
    """Bright black foreground."""
    RED: ClassVar[_Style] = _Style(91)
    """Bright red foreground."""
    GREEN: ClassVar[_Style] = _Style(92)
    """Bright green foreground."""
    YELLOW: ClassVar[_Style] = _Style(93)
    """Bright yellow foreground."""
    BLUE: ClassVar[_Style] = _Style(94)
    """Bright blue foreground."""
    MAGENTA: ClassVar[_Style] = _Style(95)
    """Bright magenta foreground."""
    CYAN: ClassVar[_Style] = _Style(96)
    """Bright cyan foreground."""
    WHITE: ClassVar[_Style] = _Style(97)
    """Bright white foreground."""


####################################################### STYLE ATTRS ######################################################


class S:
    """All available ANSI style codes.\n
    -----------------------------------------------------------------------------------------
    Every attribute supports `|` for combining and `()` for applying to text:

    >>> S.BOLD("hello")                   # Bold, auto-reset after
    >>> (S.BOLD | S.RED)("hello")         # Bold + red, auto-reset after
    >>> S.BR.GREEN("hello")               # Bright green
    >>> S.BG.BLACK("hello")               # Black background
    >>> S.DIM("# ", S.ITALIC("comment"))  # Nested: dim wraps italic inside

    For a full list of available attributes, see the `ansi` module documentation."""

    ######################### TOTAL RESET #########################
    RESET: ClassVar[_Style] = _Style(0)
    """Reset all styling to default."""

    ####################### SPECIFIC RESETS #######################
    RESET_BOLD: ClassVar[_Style] = _Style(22)
    """Reset bold (also resets dim, as they share the same code)."""
    RESET_DIM: ClassVar[_Style] = _Style(22)
    """Reset dim (also resets bold, as they share the same code)."""
    RESET_ITALIC: ClassVar[_Style] = _Style(23)
    """Reset italic."""
    RESET_UNDERLINE: ClassVar[_Style] = _Style(24)
    """Reset underline and double underline."""
    RESET_INVERSE: ClassVar[_Style] = _Style(27)
    """Reset inverse."""
    RESET_HIDDEN: ClassVar[_Style] = _Style(28)
    """Reset hidden."""
    RESET_STRIKETHROUGH: ClassVar[_Style] = _Style(29)
    """Reset strikethrough."""
    RESET_FG: ClassVar[_Style] = _Style(39)
    """Reset foreground color."""
    RESET_BG: ClassVar[_Style] = _Style(49)
    """Reset background color."""

    ######################### TEXT STYLES #########################
    BOLD: ClassVar[_Style] = _Style(1)
    """Bold text.\n
    Note that this is also reset by `RESET_DIM`."""
    DIM: ClassVar[_Style] = _Style(2)
    """Dim text.\n
    Note that this is also reset by `RESET_BOLD`."""
    ITALIC: ClassVar[_Style] = _Style(3)
    """Italic text."""
    UNDERLINE: ClassVar[_Style] = _Style(4)
    """Underline text."""
    INVERSE: ClassVar[_Style] = _Style(7)
    """Inverse colors (swap foreground and background colors)."""
    HIDDEN: ClassVar[_Style] = _Style(8)
    """Hidden (invisible) text."""
    STRIKETHROUGH: ClassVar[_Style] = _Style(9)
    """Strikethrough text."""
    DOUBLE_UNDERLINE: ClassVar[_Style] = _Style(21)
    """Double underline text."""

    ###################### STANDARD FG COLORS #####################
    BLACK: ClassVar[_Style] = _Style(30)
    """Black foreground."""
    RED: ClassVar[_Style] = _Style(31)
    """Red foreground."""
    GREEN: ClassVar[_Style] = _Style(32)
    """Green foreground."""
    YELLOW: ClassVar[_Style] = _Style(33)
    """Yellow foreground."""
    BLUE: ClassVar[_Style] = _Style(34)
    """Blue foreground."""
    MAGENTA: ClassVar[_Style] = _Style(35)
    """Magenta foreground."""
    CYAN: ClassVar[_Style] = _Style(36)
    """Cyan foreground."""
    WHITE: ClassVar[_Style] = _Style(37)
    """White foreground."""

    ######################### NAMESPACES ##########################
    BR: ClassVar[type[_BrNS]] = _BrNS
    BG: ClassVar[type[_BgNS]] = _BgNS

    #################### CUSTOM COLORS & LINKS ####################
    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _ColorStyle:
        """24-bit foreground color.\n
        `S.rgb(255, 96, 112)("text")`"""

        return _ColorStyle(red, green, blue)

    @staticmethod
    def hex(color: str, /) -> _ColorStyle:
        """24-bit foreground color from HEX string.\n
        `S.hex("#FF6070")("text")` or `S.hex("F67")`"""

        return _ColorStyle.from_hex(color)

    @staticmethod
    def link(url: str | Path, /) -> _Link:
        """Clickable hyperlink. Accepts strings or `pathlib.Path` objects.\n
        If a `pathlib.Path` is passed, it is automatically resolved and converted to a URI.\n
        --------------------------------------------------------------------------------------
        >>> S.link("https://example.com")("click here")
        >>> S.link(Path("docs/readme.md"))("open file")"""

        return _Link(url)


#################################################### TERMINAL CONTROL ####################################################


class Term:
    """Common ANSI terminal control sequences (cursor, screen, title)<br>
    as plain strings or string-returning static methods.\n
    ----------------------------------------------------------------------------------
    Values can be passed straight into an `StyledText(…)` call or written to `sys.stdout`."""

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


####################################################### StyledText #######################################################


class StyledText:
    """Build a styled string from a sequence of segments<br>
    (strings, `_StyledSequence` calls, or raw tuples), joined by `sep`.\n
    ------------------------------------------------------------------------------------------------------
    *   `segments` – Any number of segments to render. Each positional argument represents one logical line.
    *   `sep` – The separator inserted between two adjacent positional arguments (default `""`).
    ------------------------------------------------------------------------------------------------------
    After construction the instance exposes:
    *   `ansi` – The fully rendered ANSI escape string, ready to be written to a terminal.
    *   `raw` – `ansi` with every ANSI escape sequence stripped; computed on demand.
    *   `code_positions` – A tuple of `(position, sequence)` pairs giving<br>
        the start offset of every ANSI escape sequence inside `ansi`; computed on demand.
    ------------------------------------------------------------------------------------------------------
    For exact information about how to use the operator syntax,<br>
    see the `ansi` module documentation."""

    __slots__: Final[tuple[str, ...]] = ("_ansi_parts", "ansi")

    def __init__(self, /, *segments: Renderable, sep: str = "") -> None:
        ansi_parts: list[str] = []

        for i, segment in enumerate(segments):
            if i > 0 and sep:
                ansi_parts.append(sep)
            self._render(segment, ansi_parts)

        self.ansi: str = "".join(ansi_parts)

    @property
    def raw(self) -> str:
        """The rendered output with every ANSI escape sequence stripped (the "plain" text)."""

        return _ANSI_SEQ_RX.sub("", self.ansi)

    @property
    def code_positions(self) -> tuple[tuple[int, str], ...]:
        """A tuple of `(position, sequence)` pairs giving the<br>
        start offset of every ANSI escape sequence inside `ansi`."""

        return tuple((match.start(), match.group()) for match in _ANSI_SEQ_RX.finditer(self.ansi))

    @property
    def raw_code_positions(self) -> tuple[tuple[int, str], ...]:
        """A tuple of `(position, sequence)` pairs giving the start offset of every ANSI escape<br>
        sequence relative to the plain `raw` text (i.e., as if all escape sequences were removed).\n
        ---------------------------------------------------------------------------------------------
        This is the counterpart to `code_positions`, which reports offsets inside the rendered<br>
        `ansi` string. It is useful for re-inserting the styling after processing the plain text<br>
        (e.g., wrapping or splitting it), since the positions stay valid against `raw`."""

        result: list[tuple[int, str]] = []
        consumed = 0

        for match in _ANSI_SEQ_RX.finditer(self.ansi):
            result.append((match.start() - consumed, match.group()))
            consumed += len(match.group())

        return tuple(result)

    def __add__(self, other: StyledText | str, /) -> StyledText:
        """Concatenate a `StyledText` object with another `StyledText` object or a plain string."""

        result = StyledText.__new__(StyledText)
        result.ansi = self.ansi + (other.ansi if isinstance(other, StyledText) else other)

        return result

    def __radd__(self, other: str, /) -> StyledText:
        """Concatenate a plain string with a `StyledText` object from the left."""

        result = StyledText.__new__(StyledText)
        result.ansi = other + self.ansi

        return result

    def __iadd__(self, other: StyledText | str, /) -> StyledText:
        """Append another `StyledText` object or a plain string in place (`+=`)."""

        self.ansi += other.ansi if isinstance(other, StyledText) else other
        return self

    def __mul__(self, n: int, /) -> StyledText:
        """Repeat the rendered output `n` times, e.g., `StyledText(S.CYAN("─")) * 40`."""

        result = StyledText.__new__(StyledText)
        result.ansi = self.ansi * n

        return result

    def __rmul__(self, n: int, /) -> StyledText:
        """Repeat the rendered output `n` times, e.g., `40 * StyledText(S.CYAN("─"))`."""

        result = StyledText.__new__(StyledText)
        result.ansi = self.ansi * n

        return result

    def __len__(self) -> int:
        """Return the visible character count (ANSI sequences stripped)."""

        return len(self.raw)

    def join(self, iterable: Iterable[Renderable], /) -> StyledText:
        """Join a sequence of segments using the current `StyledText` object as the separator.\n
        ----------------------------------------------------------------------------------
        *   `iterable` – The segments to join, e.g., a list of strings or `StyledText` objects."""

        return StyledText(*iterable, sep=self.ansi)

    def ljust(self, width: int, fill_char: str = " ", /) -> StyledText:
        """Return the `StyledText` object left justified in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string, including the original `StyledText` content.
        *   `fill_char` – The character to use for padding (default is a space)."""

        result = StyledText.__new__(StyledText)
        result.ansi = self.ansi + (fill_char * max(0, width - len(self)))

        return result

    def rjust(self, width: int, fill_char: str = " ", /) -> StyledText:
        """Return the `StyledText` object right justified in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string, including the original `StyledText` content.
        *   `fill_char` – The character to use for padding (default is a space)."""

        result = StyledText.__new__(StyledText)
        result.ansi = (fill_char * max(0, width - len(self))) + self.ansi

        return result

    def center(self, width: int, fill_char: str = " ", /) -> StyledText:
        """Return the `StyledText` object centered in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string, including the original `StyledText` content.
        *   `fill_char` – The character to use for padding (default is a space)."""

        padding = max(0, width - len(self))
        left = padding // 2
        right = padding - left

        result = StyledText.__new__(StyledText)
        result.ansi = (fill_char * left) + self.ansi + (fill_char * right)

        return result

    def __str__(self) -> str:
        """Stringifying a `StyledText` instance yields its rendered<br>
        ANSI string, ready to be written to a terminal."""

        return self.ansi

    def __repr__(self) -> str:
        """Returns a string representation of this `StyledText` instance, showing its rendered ANSI string."""

        return f"StyledText(ansi={self.ansi!r})"

    def print(self, /, *, end: str = "\n", flush: bool = True, file: TextIO | None = None) -> None:
        """Write the rendered ANSI string straight to `sys.stdout` (configuring the terminal<br>
        for ANSI on first use) or to a custom file-like object.\n
        -----------------------------------------------------------------------------------------
        *   `end` – The string to append at the end of the output (default `"\\n"`).
        *   `flush` – Whether to flush the output stream after writing (default `True`).
        *   `file` – The file-like object to write to (default `sys.stdout`)."""

        _config_terminal()
        target = file or _sys.stdout

        target.write(self.ansi + end)

        if flush:
            target.flush()

    def input(self, /, *, reset_ansi: bool = False) -> str:
        """Use the rendered ANSI string as an input prompt and return the user's input.\n
        ----------------------------------------------------------------------------------
        *   `reset_ansi` – If true, all ANSI styling will be reset after<br>
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

    def _render(self, segment: object, ansi_parts: list[str]) -> None:
        """Internal method to recursively render a `segment`, dispatching by runtime type.\n
        -----------------------------------------------------------------------------------------
        Strings are emitted as raw text; `_StyledSequence` segments are wrapped in their<br>
        opening and closing ANSI sequences; `tuple` segments are flattened in order.<br>
        Bare style objects (`_Style`, `_ColorStyle`, `_Link`, `_StyleGroup`) emit only their<br>
        opening sequence with no matching close."""

        if isinstance(segment, str):
            ansi_parts.append(segment)
            return

        elif isinstance(segment, _StyledSequence):
            for piece in segment._opens:
                ansi_parts.append(piece)
            self._render(segment.text, ansi_parts)
            for piece in segment._closes:
                ansi_parts.append(piece)
            return

        elif isinstance(segment, tuple):
            for tuple_part in cast("tuple[object, ...]", segment):
                self._render(tuple_part, ansi_parts)
            return

        elif isinstance(segment, _Style):
            ansi_parts.append(f"{ANSI.CHAR}[{int(segment)}m")
            return

        elif isinstance(segment, (_ColorStyle, _Link)):
            ansi_parts.append(segment._open_seq)
            return

        elif isinstance(segment, _StyleGroup):
            for piece in _build_open_close(segment)[0]:
                ansi_parts.append(piece)
            return

        else:
            # Fallback; coerce unknown objects to str:
            ansi_parts.append(str(segment))


#################################################### INTERNAL HELPERS ####################################################


def _build_open_close(group: _StyleGroup, /) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Internal function to build the opening and closing ANSI sequences for a `_StyleGroup`.\n
    ------------------------------------------------------------------------------------------
    Returns a `(opens, closes)` pair of tuples. Multiple opens / closes are emitted<br>
    only when both an OSC 8 hyperlink and SGR codes are present (OSC wraps SGR)."""

    return _BuildOpenClose(group).build()


def _config_terminal() -> None:
    """Configure the terminal to be able to interpret and render ANSI styling.\n
    This function only does something the first time it is called. Subsequent calls are no-ops."""

    global _terminal_ansi_configured
    if _terminal_ansi_configured:
        return

    _sys.stdout.flush()

    if _os.name == "nt":
        try:
            kernel32 = _ctypes.windll.kernel32  # type: ignore
            handle = kernel32.GetStdHandle(-11)  # type: ignore
            mode = _ctypes.c_ulong()  # type: ignore
            kernel32.GetConsoleMode(handle, _ctypes.byref(mode))  # type: ignore
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # type: ignore
        except Exception:
            pass

    _terminal_ansi_configured = True


class _BuildOpenClose:
    """Internal, callable helper class to build the opening and closing ANSI sequences for a `_StyleGroup`."""

    def __init__(self, group: _StyleGroup, /) -> None:
        self.group: _StyleGroup = group
        self.sgr_open: list[str] = []
        self.sgr_close: list[str] = []
        self.link_url: str | None = None

    def build(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if (
            len(codes := self.group._codes) == 1
            and type(codes[0]) is _Style
            and (cached := _STANDARD_SEQS.get(int(codes[0]))) is not None
        ):
            return cached

        for code in self.group:
            self._process_code(code)

        return self._build_result()

    def _process_code(self, code: BaseStyle) -> None:
        if isinstance(code, _Link):
            self.link_url = code._url
        elif isinstance(code, _ColorStyle):
            if code._bg:
                self.sgr_open.append(f"48;2;{code._red};{code._green};{code._blue}")
                self.sgr_close.append("49")
            else:
                self.sgr_open.append(f"38;2;{code._red};{code._green};{code._blue}")
                self.sgr_close.append("39")
        else:
            cid = int(code)
            self.sgr_open.append(str(cid))
            if (reset := _RESET_MAP.get(cid)) is not None:
                self.sgr_close.append(str(reset))

    def _build_result(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        seen: set[str] = set()
        dedup_close: list[str] = []

        for close_code in self.sgr_close:
            if close_code not in seen:
                seen.add(close_code)
                dedup_close.append(close_code)

        opens: list[str] = []
        closes: list[str] = []

        if self.link_url is not None:
            opens.append(ANSI.SEQ_LINK_OPEN.format(self.link_url))
        if self.sgr_open:
            opens.append(f"{ANSI.CHAR}[{';'.join(self.sgr_open)}m")
        if dedup_close:
            closes.append(f"{ANSI.CHAR}[{';'.join(dedup_close)}m")
        if self.link_url is not None:
            closes.append(ANSI.SEQ_LINK_CLOSE)

        return tuple(opens), tuple(closes)
