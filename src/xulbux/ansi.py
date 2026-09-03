"""
This module provides the `S` and `Term` classes for building richly styled<br>
terminal output using a typed, operator-based syntax.

---

### The Easy Styling

First, let's take a look at a small example of what a highly styled output could look like using this module:

```python
S(
    ("First normal & unstyled text. ", \
(S.BOLD | S.UNDERLINE | S.BR.BLUE)("Bright blue, bold, and underlined text.")),
    ((S.hex("#000") | S.BG.hex("#F67"))("Black text with a red background."), \
" And then ", S.ITALIC("(boring)"), " plain text again."),
    sep="\\n",
).print()
```

<!-- DOCS: <TerminalOutput>
First normal & unstyled text. <span class="b u br-blue">Bright blue, bold, and underlined text.</span>
<span class="#000 bg-#F67">Black text with a red background.</span> And then (<span class="i">boring</span>) plain text again.
</TerminalOutput> -->

How all of this exactly works is explained in the sections below. 🠫


### Styles and Groups

In this module, you apply styles and colors using `S` attributes.<br>
Every style attribute supports two operators:

*   `|` combines two or more styles into a single immutable group, e.g.<br>
    `S.BOLD | S.RED`  →  bold + red foreground
*   `()` applies the style (or group) to the given text and auto-resets the style after it, e.g.<br>
    `S.BOLD("hello")`  →  bold "hello", reset back to normal afterwards<br>
    `(S.BOLD | S.RED)("hello")`  →  same idea, combined

A list of all possible style attributes can be found below.


### Auto Resetting Styles

Every `_Style`, `_StyleGroup`, `_ColorStyle` or `_Link` call automatically generates the<br>
matching reset sequence behind its text, just like shown in the following example:

```python
S(
    ("This is plain text, ", S.BR.BLUE("which is bright blue now.")),
    "Now it was automatically reset to plain again.",
    sep="\\n",
).print()
```

<!-- DOCS: <TerminalOutput>
This is plain text, <span class="br-blue">which is bright blue now.</span>
Now it was automatically reset to plain again.
</TerminalOutput> -->

Only the specific styles that were applied are reset; other styling in scope is left intact:

```python
S.CYAN(
    "This is cyan text, ", S.DIM("which is dimmed now."),
    "\\nNow it's not dimmed any more but still cyan.",
).print()
```

<!-- DOCS: <TerminalOutput>
<span class="cyan">This is cyan text, <span class="dim">which is dimmed now.</span></span>
<span class="cyan">Now it's not dimmed any more but still cyan.</span>
</TerminalOutput> -->


### Bare (Open-Only) Styles

Passing a style object *without calling it* emits only its opening ANSI sequence at that<br>
position, with no matching close/reset appended. This is the typed equivalent of `[…]`<br>
(open bracket without closing braces) from the legacy string syntax:

```python
S(
    S.RED, "[ERROR] Something went wrong!",
    S.RESET, " Back to normal.",
).print()
```

<!-- DOCS: <TerminalOutput>
<span class="red">[ERROR] Something went wrong!</span> Back to normal.
</TerminalOutput> -->

Any style type supports bare usage: `S.RED` (`_Style`), `S.hex("#F67")` (`_ColorStyle`),<br>
`S.link("url")` (`_Link`), and `S.BOLD | S.RED` (`_StyleGroup`).<br>
Bare styles can also appear inside tuples and nested calls:

```python
S.ITALIC("a", S.MAGENTA, "B", S.RESET_FG, "c").print()
```

<!-- DOCS: <TerminalOutput>
<span class="i">a<span class="magenta">B</span>c</span>
</TerminalOutput> -->


### Nesting and Multi-Segment Groups

A style call accepts either a single piece of text or any number of mixed segments.<br>
Strings, `S` objects, bare style objects, and raw tuples can be mixed freely:

*   `S.X("text")`               – Apply `X` to `"text"`, auto-reset after.
*   `S.X | S.Y`                 – Combine `X` and `Y` into a single group.
*   `(S.X | S.Y)("text")`       – Apply the group to `"text"`.
*   `S.X("a", S.Y("b"), "c")`   – Nested multi-segment: `Y` is applied only to `"b"`.
*   `S.X`                       – Bare: emit only the opening sequence, no auto-reset.
*   `("a", S.X("b"), "c")`      – Same-line group; passed as a single tuple to `S(…)`.

Inside `S(*segments, sep="\\n")`, every positional argument is treated as one<br>
logical line and joined by `sep`. An empty string argument `""` therefore produces a blank line.


### All Possible Style Attributes

*   Text styles:
    -   `S.BOLD`
    -   `S.DIM`
    -   `S.ITALIC`
    -   `S.UNDERLINE`
    -   `S.INVERSE`
    -   `S.BLINK`
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
    -   `S.BG.rgb(0, 100, 255)`
    -   `S.BG.hex("#0064FF")`  or  `S.BG.hex("06F")`
*   256-color palette (foreground / background):
    -   `S.color256(210)`
    -   `S.BG.color256(69)`
*   Hyperlinks (OSC 8):
    -   `S.link("https://example.com")("click here")`
    -   `(S.link("…") | S.BR.BLUE)("click here")`
*   Specific resets (only needed in advanced use; auto-reset usually covers it):
    -   `S.RESET_BOLD`, `S.RESET_DIM`, `S.RESET_ITALIC`, `S.RESET_UNDERLINE`,
        `S.RESET_BLINK`, `S.RESET_INVERSE`, `S.RESET_HIDDEN`, `S.RESET_STRIKE`,
        `S.RESET_COLOR`, `S.RESET_BG`
*   Total reset (resets every previously applied styles):
    -   `S.RESET`


### Terminal Control – the `Term` class

`Term` exposes commonly used non-styling ANSI sequences for cursor- and screen-control.<br>
These are plain strings (or string-returning helpers), so they can be passed directly into a<br>
`S(…)` call or written to `sys.stdout`:

*   `CLEAR_LINE`                         – Erase the entire current line.
*   `CLEAR_LINE_TO_END`                  – Erase from the cursor to the end of the line.
*   `CLEAR_LINE_TO_START`                – Erase from the line start to the cursor.
*   `CLEAR_SCREEN`                       – Erase the whole screen.
*   `CLEAR_SCREEN_TO_END`                – Erase from the cursor to the end of the screen.
*   `CLEAR_SCREEN_TO_START`              – Erase from the screen start to the cursor.
*   `CLEAR_SCROLLBACK`                   – Erase the scrollback buffer.
*   `CUR_HIDE` / `CUR_SHOW`              – Hide/show the cursor.
*   `CUR_HOME`                           – Move cursor to home position (0, 0).
*   `CUR_SAVE` / `CUR_RESTORE`           – Save/restore cursor position (ANSI.SYS).
*   `CUR_SAVE_DEC` / `CUR_RESTORE_DEC`   – Save/restore cursor position (DEC ESC 7/8).
*   `ALT_SCREEN`                         – Enter the alternate screen buffer.
*   `MAIN_SCREEN`                        – Leave the alternate screen buffer.
*   `BELL`                               – Terminal bell signal (`\\x07`).
*   `up(n)`                              – Move the cursor up by `n` rows.
*   `down(n)`                            – Move the cursor down by `n` rows.
*   `right(n)`                           – Move the cursor right by `n` columns.
*   `left(n)`                            – Move the cursor left by `n` columns.
*   `row(row)`                           – Move the cursor to an absolute row position (1-based, VPA).
*   `col(col)`                           – Move the cursor to an absolute column position (1-based, CHA).
*   `move(row, col)`                     – Move the cursor to an absolute `(row, col)` position.
*   `scroll_up(n)`                       – Scroll page up by `n` lines.
*   `scroll_down(n)`                     – Scroll page down by `n` lines.
*   `title(text)`                        – Set the terminal window / tab title (OSC 2).
*   `cursor_shape(shape)`                – Change cursor shape (DECSCUSR 1-6).
*   `clipboard_copy(text)`               – Copy text to system clipboard via OSC 52.
*   `cwd(path)`                          – Notify terminal of current working directory via OSC 7.
"""

from __future__ import annotations

from .base.consts import ANSI

import base64 as _base64
import ctypes as _ctypes
import os as _os
import sys as _sys
import textwrap as _textwrap
from contextlib import suppress as _suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal, Self, TextIO, cast, overload

if TYPE_CHECKING:
    from .color import hexa, rgba

    import sys
    from collections.abc import Iterable, Iterator
    import regex as _rx

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs

_terminal_configured: bool = False
"""Whether the terminal was already configured to be able to interpret and render ANSI styling."""

_ANSI_SEQ_RX: Final[_rx.Pattern[str]] = ANSI.SEQ_PATTERN
"""Module shorthand for `ANSI.SEQ_PATTERN`.<br>
Matches any ANSI escape sequence (CSI, OSC, or single-character)."""

# fmt:off
_RESET_MAP: Final[dict[int, int]] = {
    # Text styles:
    1: 22, 2: 22, 3: 23, 4: 24, 5: 25, 7: 27, 8: 28, 9: 29, 21: 24,
    # FG colors:
    30: 39, 31: 39, 32: 39, 33: 39, 34: 39, 35: 39, 36: 39, 37: 39,
    # BG colors:
    40: 49, 41: 49, 42: 49, 43: 49, 44: 49, 45: 49, 46: 49, 47: 49,
    # Bright FG colors:
    90: 39, 91: 39, 92: 39, 93: 39, 94: 39, 95: 39, 96: 39, 97: 39,
    # Bright BG colors:
    100: 49, 101: 49, 102: 49, 103: 49, 104: 49, 105: 49, 106: 49, 107: 49,
}
"""Mapping from ANSI style integer to its matching reset integer.\n
Codes that fully reset everything (`0`) or have no useful specific reset are intentionally omitted."""
# fmt:on

_STANDARD_SEQS: Final[dict[int, tuple[tuple[str, ...], tuple[str, ...]]],] = {
    cid: ((f"{ANSI.CHAR}[{cid}m",), (f"{ANSI.CHAR}[{reset}m",)) for cid, reset in _RESET_MAP.items()
}
"""Pre-computed `(opens, closes)` tuple pairs for every standard single-code SGR style.\n
Used as a fast path in `_build_open_close` to avoid per-call list and string allocations."""

_CUBE_STEPS: Final[tuple[int, ...]] = (0, 95, 135, 175, 215, 255)
"""RGB channel steps for the 6×6×6 color cube in 256-color palettes."""  # ruff:ignore[ambiguous-unicode-character-string]

_CURSOR_SHAPES: Final[dict[str, int]] = {
    "blinking_bar": 5,
    "blinking_block": 1,
    "blinking_underline": 3,
    "steady_bar": 6,
    "steady_block": 2,
    "steady_underline": 4,
}
"""Mapping from cursor shape description names to their corresponding DECSCUSR numeric codes."""


# ***************************************************** INTERNAL HELPERS ******************************************************


def _ansi256_to_rgb(code: int, /) -> tuple[int, int, int]:
    """Internal function to convert an ANSI 256-color palette index in range `[16, 255]` to an `(R, G, B)` tuple."""

    if code < 232:
        offset = code - 16
        return (_CUBE_STEPS[offset // 36], _CUBE_STEPS[(offset // 6) % 6], _CUBE_STEPS[offset % 6])

    gray = 8 + (code - 232) * 10
    return (gray, gray, gray)


def _build_open_close(group: _StyleGroup, /) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Internal function to build the opening and closing ANSI sequences for a `_StyleGroup`.\n
    ----------------------------------------------------------------------------------------------------
    Returns a `(opens, closes)` pair of tuples. Multiple opens / closes are emitted<br>
    only when both an OSC 8 hyperlink and SGR codes are present (OSC wraps SGR)."""

    return _BuildOpenClose(group).build()


def _config_terminal() -> None:
    """Internal function to configure the terminal to be able to interpret and render ANSI styling.\n
    This function only does something the first time it is called. Subsequent calls are no-ops."""

    global _terminal_configured
    if _terminal_configured:
        return

    _sys.stdout.flush()

    if _os.name == "nt":
        with _suppress(Exception):
            kernel32 = _ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.GetStdHandle(-11)  # pyright:ignore[reportUnknownMemberType,reportUnknownVariableType]
            mode = _ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, _ctypes.byref(mode))  # pyright:ignore[reportUnknownMemberType]
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # pyright:ignore[reportUnknownMemberType]

    _terminal_configured = True


class _BuildOpenClose:
    """Internal, callable helper class to build the opening and closing ANSI sequences for a `_StyleGroup`."""

    __slots__: tuple[str, ...] = ("group", "link_url", "sgr_close", "sgr_open")

    def __init__(self, group: _StyleGroup, /) -> None:
        self.group: _StyleGroup = group
        self.sgr_open: list[str] = []
        self.sgr_close: list[str] = []
        self.link_url: str | None = None

    def build(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Build the opening and closing ANSI sequences for the given `_StyleGroup`.\n
        ----------------------------------------------------------------------------------------------------
        Returns a `(opens, closes)` pair of tuples. Multiple opens / closes are emitted<br>
        only when both an OSC 8 hyperlink and SGR codes are present (OSC wraps SGR)."""

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
        """Internal helper to process a single style code and append its opening and closing sequences."""

        if isinstance(code, _Link):
            self.link_url = code._url

        elif isinstance(code, _ColorStyle):
            if code._bg:
                self.sgr_open.append(f"48;2;{code._red};{code._green};{code._blue}")
                self.sgr_close.append("49")
            else:
                self.sgr_open.append(f"38;2;{code._red};{code._green};{code._blue}")
                self.sgr_close.append("39")

        elif isinstance(code, _Color256Style):
            if code._bg:
                self.sgr_open.append(f"48;5;{code._code}")
                self.sgr_close.append("49")
            else:
                self.sgr_open.append(f"38;5;{code._code}")
                self.sgr_close.append("39")

        else:
            self.sgr_open.append(str(cid := int(code)))
            if (reset := _RESET_MAP.get(cid)) is not None:
                self.sgr_close.append(str(reset))

    def _build_result(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Internal helper to build the final `(opens, closes)` result tuples."""

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


def _render_styled(opens: tuple[str, ...], closes: tuple[str, ...], segments: tuple[Renderable, ...]) -> S:
    """Internal helper to construct an `S` object wrapped in opening and closing ANSI sequences."""

    ansi_parts: list[str] = list(opens)
    for segment in segments:
        _render_segment(segment, ansi_parts)
    for close in closes:
        ansi_parts.append(close)

    return S("".join(ansi_parts))


def _render_segment(segment: object, ansi_parts: list[str]) -> None:
    """Internal helper to recursively render a segment into `ansi_parts`."""

    if isinstance(segment, str):
        ansi_parts.append(segment)
        return

    elif isinstance(segment, _SBase):
        ansi_parts.append(segment.ansi)
        return

    elif isinstance(segment, tuple):
        for tuple_part in cast("tuple[object, ...]", segment):
            _render_segment(tuple_part, ansi_parts)
        return

    else:
        # Fallback; coerce unknown objects to str:
        ansi_parts.append(str(segment))


# ******************************************************** BASE CLASS *********************************************************


class _SBase:
    """Common base class for styled text (`S`)
    and bare ANSI style builders (`_Style`, `_ColorStyle`, `_Link`, `_StyleGroup`).\n
    ----------------------------------------------------------------------------------------------------
    Provides all string inspection properties, mathematical operators, and text formatting methods."""

    __slots__: tuple[str, ...] = ("ansi",)
    ansi: str

    def __call__(self, *text: Renderable) -> S:
        """Dummy method required to prevent a MyPyC C-struct memory layout bug.\n
        ----------------------------------------------------------------------------------------------------
        If subclasses define `__call__` but the native base class does not, MyPyC injects a<br>
        `vectorcallfunc` pointer into the subclass struct. This breaks the memory offset<br>
        for inherited fields (like `ansi`), causing a segmentation fault when accessed."""

        raise NotImplementedError

    # ************************* PROPERTIES **************************

    @property
    def raw(self) -> str:
        """The rendered output with every ANSI escape sequence stripped (the "plain" text)."""

        return _ANSI_SEQ_RX.sub("", self.ansi)

    @property
    def code_positions(self) -> tuple[tuple[int, str], ...]:
        """A tuple of `(position, sequence)` pairs giving the<br>
        start offset of every ANSI escape sequence inside `ansi`."""

        return tuple([(match.start(), match.group()) for match in _ANSI_SEQ_RX.finditer(self.ansi)])

    @property
    def raw_code_positions(self) -> tuple[tuple[int, str], ...]:
        """A tuple of `(position, sequence)` pairs giving the start offset of every ANSI escape<br>
        sequence relative to the plain `raw` text (i.e., as if all escape sequences were removed).\n
        ----------------------------------------------------------------------------------------------------
        This is the counterpart to `code_positions`, which reports offsets inside the rendered<br>
        `ansi` string. It is useful for re-inserting the styling after processing the plain text<br>
        (e.g., wrapping or splitting it), since the positions stay valid against `raw`."""

        result: list[tuple[int, str]] = []
        consumed = 0

        for match in _ANSI_SEQ_RX.finditer(self.ansi):
            result.append((match.start() - consumed, match.group()))
            consumed += len(match.group())

        return tuple(result)

    # ************************** OPERATORS **************************

    def __add__(self, other: Renderable, /) -> S:
        """Concatenate an `_SBase` object with another renderable object."""

        return S(self, other)

    def __radd__(self, other: Renderable, /) -> S:
        """Concatenate another renderable object with an `_SBase` object from the left."""

        return S(other, self)

    def __iadd__(self, other: Renderable, /) -> S:
        """Append another renderable object in place (`+=`)."""

        self.ansi = S(self, other).ansi
        return cast("S", self)

    def __mul__(self, n: int, /) -> S:
        """Repeat this `_SBase` object `n` times."""

        return S(*([self] * max(0, n)))

    def __rmul__(self, n: int, /) -> S:
        """Repeat this `_SBase` object `n` times from the left."""

        return self * n

    def __len__(self) -> int:
        """Return the visible length (character count of plain `raw` text)."""

        return len(self.raw)

    def __getitem__(self, key: slice, /) -> S:
        """Slice the styled text by character positions in the plain unstyled (`raw`) text.<br>
        ANSI escape codes are preserved and redistributed over the sliced segment."""

        raw_text = self.raw
        start, stop, step = key.indices(len(raw_text))

        if step != 1:
            raise ValueError("Styled text slicing only supports a step of 1.")

        return self._slice(start, stop, raw_text, self.raw_code_positions)

    def _slice(self, start: int, stop: int, raw_text: str, raw_code_positions: tuple[tuple[int, str], ...]) -> S:
        """Internal fast-path for slicing with precomputed `raw_text` and `raw_code_positions`."""

        if start >= stop:
            return S("")

        prefix_codes: list[str] = []
        middle_codes: list[tuple[int, str]] = []
        suffix_codes: list[str] = []

        for pos, seq in raw_code_positions:
            if pos <= start:
                prefix_codes.append(seq)
            elif start < pos < stop:
                middle_codes.append((pos - start, seq))
            else:
                suffix_codes.append(seq)

        sliced_raw = raw_text[start:stop]
        result_parts: list[str] = list(prefix_codes)
        last_index = 0

        for pos, seq in middle_codes:
            result_parts.append(sliced_raw[last_index:pos])
            result_parts.append(seq)
            last_index = pos

        result_parts.append(sliced_raw[last_index:])
        result_parts.extend(suffix_codes)

        return S("".join(result_parts))

    def __contains__(self, item: object, /) -> bool:
        """Check if a substring or plain string is contained in the rendered output or plain text."""

        if isinstance(item, str):
            return item in self.ansi or item in self.raw

        return False

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is an `_SBase` instance or string with identical ANSI text."""

        if isinstance(other, _SBase):
            return self.ansi == other.ansi
        elif isinstance(other, str):
            return self.ansi == other

        return False

    def __bool__(self) -> bool:
        """Return `True` if the unstyled plain text is non-empty."""

        return bool(self.raw)

    def __str__(self) -> str:
        """Return the fully rendered ANSI string."""

        return self.ansi

    def __repr__(self) -> str:
        """Return the debug string representation of the `_SBase` object."""

        return f"S({self.ansi!r})"

    # *************************** METHODS ***************************

    def join(self, iterable: Iterable[Renderable], /) -> S:
        """Join a sequence of segments using the current object as the separator.\n
        ----------------------------------------------------------------------------------------------------
        *   `iterable` – The segments to join, e.g., a list of strings or `S` objects.\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S(", ").join(["Apple", S.BOLD("Banana"), "Cherry"]).print()
        ```

        <!-- DOCS: <TerminalOutput>
        Apple, <span class="b">Banana</span>, Cherry
        </TerminalOutput> -->"""

        return S(*iterable, sep=self.ansi)

    def ljust(self, width: int, fill_char: Renderable = " ", /) -> S:
        """Return the object left justified in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string.
        *   `fill_char` – The character to use for padding (default is a space).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.RED("Text").ljust(10, ".").print()
        ```

        <!-- DOCS: <TerminalOutput>
        <span class="red">Text</span>......
        </TerminalOutput> -->"""

        if (raw_len := len(self.raw)) >= width:
            return cast("S", self) if type(self) is S else S(self)

        return self + fill_char * (width - raw_len)

    def rjust(self, width: int, fill_char: Renderable = " ", /) -> S:
        """Return the object right justified in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string.
        *   `fill_char` – The character to use for padding (default is a space).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.GREEN("Text").rjust(10, ".").print()
        ```

        <!-- DOCS: <TerminalOutput>
        ......<span class="green">Text</span>
        </TerminalOutput> -->"""

        if (raw_len := len(self.raw)) >= width:
            return cast("S", self) if type(self) is S else S(self)

        return fill_char * (width - raw_len) + self

    def center(self, width: int, fill_char: Renderable = " ", /) -> S:
        """Return the object centered in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string.
        *   `fill_char` – The character to use for padding (default is a space).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.BOLD("Text").center(10, "-").print()
        ```

        <!-- DOCS: <TerminalOutput>
        ---<span class="b">Text</span>---
        </TerminalOutput> -->"""

        if (raw_len := len(self.raw)) >= width:
            return cast("S", self) if type(self) is S else S(self)

        total_pad = width - raw_len
        left_pad = total_pad // 2
        right_pad = total_pad - left_pad

        return fill_char * left_pad + self + fill_char * right_pad

    def wrap(self, width: int, /) -> list[S]:
        """Wrap the object to fit within a given line width<br>
        (in visible characters), preserving ANSI styling across all wrapped lines.\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The maximum visible width of each line."""

        if not (raw_text := self.raw) or width <= 0:
            return [cast("S", self) if type(self) is S else S(self)]

        raw_code_positions = self.raw_code_positions
        result: list[S] = []
        current_offset = 0

        for paragraph in raw_text.split("\n"):
            if not paragraph:
                result.append(S(""))
                current_offset += 1
                continue

            for line in _textwrap.wrap(paragraph, width=width, replace_whitespace=False, drop_whitespace=False):
                line_len = len(line)
                result.append(self._slice(current_offset, current_offset + line_len, raw_text, raw_code_positions))
                current_offset += line_len
            current_offset += 1

        return result

    def print(self, /, *, end: str = "\n", flush: bool = True, file: TextIO | None = None) -> None:
        """Write the rendered ANSI string straight to `sys.stdout` (configuring the terminal<br>
        for ANSI on first use) or to a custom file-like object.\n
        ----------------------------------------------------------------------------------------------------
        *   `end` – The string to append at the end of the output (default `"\\n"`).
        *   `flush` – Whether to flush the output stream after writing (default `True`).
        *   `file` – The file-like object to write to (default `sys.stdout`).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.GREEN("Operation successful!").print()
        ```

        <!-- DOCS: <TerminalOutput>
        <span class="green">Operation successful!</span>
        </TerminalOutput> -->"""

        if file is None:
            _config_terminal()
            out = _sys.stdout
        else:
            out = file

        out.write(self.ansi + end)

        if flush:
            out.flush()

    def input(self, /, *, reset_ansi: bool = False) -> str:
        """Use the rendered ANSI string as an input prompt and return the user's input.\n
        ----------------------------------------------------------------------------------------------------
        *   `reset_ansi` – If true, all ANSI styling will be reset after<br>
            the user confirmed the input and the program continues to run.\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.BOLD("Enter value: ").input()
        ```

        <!-- DOCS: <TerminalOutput>
        <span class="b">Enter value: </span>
        </TerminalOutput> -->"""

        _config_terminal()
        user_input = input(self.ansi)

        if reset_ansi:
            _sys.stdout.write(f"{ANSI.CHAR}[0m")

        return user_input


# ***************************************************** STYLE SUBCLASSES ******************************************************


class _Style(_SBase):
    """A single ANSI style integer.\n
    ----------------------------------------------------------------------------------------------------
    Supports two operators:
    *   `|`  combines two or more codes into a `_StyleGroup` → `S.BOLD | S.RED`
    *   `()` applies the code to text, auto-resetting after → `S.BOLD("hello")`"""

    __slots__: tuple[str, ...] = ("_oc", "_value")
    _oc: tuple[tuple[str, ...], tuple[str, ...]]

    def __init__(self, value: int, /) -> None:
        self._value: int = value
        self.ansi = f"{ANSI.CHAR}[{value}m"

    def __int__(self) -> int:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"_Style({self._value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self._value == other
        elif isinstance(other, _Style):
            return self._value == other._value
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this style with another code or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(self, *other._codes)

        return _StyleGroup(self, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this style with another code or group via `|`."""

        return _StyleGroup(other, self)

    def __call__(self, *text: Renderable) -> S:
        """Applies this style code to the given text, auto-resetting after."""

        try:
            oc = self._oc
        except AttributeError:
            cached = _STANDARD_SEQS.get(int(self))
            oc = _build_open_close(_StyleGroup(self)) if cached is None else cached
            self._oc = oc

        return _render_styled(oc[0], oc[1], text)

    def __matmul__(self, text: Renderable) -> S:
        """Applies this style code to the given text, auto-resetting after."""

        try:
            oc = self._oc
        except AttributeError:
            cached = _STANDARD_SEQS.get(int(self))
            oc = _build_open_close(_StyleGroup(self)) if cached is None else cached
            self._oc = oc

        return _render_styled(oc[0], oc[1], (text,))

    def as_fg(self) -> _Style:
        """Convert to the corresponding foreground style."""

        return self

    def as_bg(self) -> _Style:
        """Convert to the corresponding background style."""

        return self


class _ColorStyle(_SBase):
    """A 24-bit true-color style – foreground or background.\n
    ----------------------------------------------------------------------------------------------------
    >>> S.rgb(112, 118, 255)("text")             # Custom FG color
    >>> S.BG.rgb(112, 118, 255)("text")          # Custom BG color
    >>> S.hex("#7075FF")("text")                 # Hex FG color
    >>> (S.BOLD | S.rgb(112, 118, 255))("text")  # Combined with style"""

    __slots__: tuple[str, ...] = ("_bg", "_blue", "_close_seq", "_green", "_open_seq", "_red")

    def __init__(self, red: int, green: int, blue: int, /, *, bg: bool = False) -> None:
        self._red: int = red
        self._green: int = green
        self._blue: int = blue
        self._bg: bool = bg

        if bg:
            self._open_seq: str = ANSI.SEQ_BG_COLOR.format(red, green, blue)
            self._close_seq: str = f"{ANSI.CHAR}[49m"
        else:
            self._open_seq = ANSI.SEQ_FG_COLOR.format(red, green, blue)
            self._close_seq = f"{ANSI.CHAR}[39m"

        self.ansi = self._open_seq

    @classmethod
    def from_hex(cls: type[Self], color: str | int | hexa, /, *, bg: bool | None = None) -> Self:
        """Create a color style from a HEX string, HEX integer, or `hexa` object."""

        if isinstance(color, int):
            if not (0x000000 <= color <= 0xFFFFFF):
                raise ValueError(f"Expected 24-bit HEX integer in range [0x000000, 0xFFFFFF] inclusive, got 0x{color:X}")

            red, green, blue = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
            return cls(red, green, blue, bg=bg) if bg is not None else cls(red, green, blue)

        if (hex_str := str(color).strip().lstrip("#")).lower().startswith("0x"):
            hex_str = hex_str[2:]
        if len(hex_str) == 3:
            hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2

        if bg is None:
            return cls(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

        return cls(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), bg=bg)

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this color style with another style or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(self, *other._codes)

        return _StyleGroup(self, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this color style with another style or group via `|`."""

        return _StyleGroup(other, self)

    def __call__(self, *text: Renderable) -> S:
        """Applies this color style to the given text, auto-resetting after."""

        return _render_styled((self._open_seq,), (self._close_seq,), text)

    def __matmul__(self, text: Renderable) -> S:
        """Applies this color style to the given text, auto-resetting after."""

        return _render_styled((self._open_seq,), (self._close_seq,), (text,))

    def __repr__(self) -> str:
        """Returns a string representation of this color style, indicating<br>
        whether it's foreground or background and its RGB values."""

        return f"_ColorStyle({'bg' if self._bg else 'fg'} {self._red},{self._green},{self._blue})"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_ColorStyle` with identical RGB values and background flag."""

        if isinstance(other, _ColorStyle):
            return (
                self._red == other._red and self._green == other._green and self._blue == other._blue and self._bg == other._bg
            )
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash((self._red, self._green, self._blue, self._bg))

    def as_fg(self) -> _FgColorStyle:
        """Convert to the corresponding foreground color style."""

        return _FgColorStyle(self._red, self._green, self._blue)

    def as_bg(self) -> _BgColorStyle:
        """Convert to the corresponding background color style."""

        return _BgColorStyle(self._red, self._green, self._blue)

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this color."""

        luminance = 0.2126 * self._red + 0.7152 * self._green + 0.0722 * self._blue
        return _FgColorStyle(255, 255, 255) if luminance < 128 else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this color."""

        luminance = 0.2126 * self._red + 0.7152 * self._green + 0.0722 * self._blue
        return _BgColorStyle(255, 255, 255) if luminance < 128 else _BgColorStyle(0, 0, 0)


class _FgColorStyle(_ColorStyle):
    """A 24-bit true-color foreground style."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgColorStyle:
        """Convert to the corresponding foreground color style."""

        return self

    def as_bg(self) -> _BgColorStyle:
        """Convert to the corresponding background color style."""

        return _BgColorStyle(self._red, self._green, self._blue)

    def with_text_bg(self) -> _StyleGroup:
        """Returns a style group combining this foreground color with an optimal high-contrast text background."""

        return self | self.as_text_bg()


class _BgColorStyle(_ColorStyle):
    """A 24-bit true-color background style."""

    __slots__: tuple[str, ...] = ()

    def __init__(self, red: int, green: int, blue: int, /, *, bg: bool = True) -> None:
        super().__init__(red, green, blue, bg=bg)

    def as_fg(self) -> _FgColorStyle:
        """Convert to the corresponding foreground color style."""

        return _FgColorStyle(self._red, self._green, self._blue)

    def as_bg(self) -> _BgColorStyle:
        """Convert to the corresponding background color style."""

        return self

    def with_text_fg(self) -> _StyleGroup:
        """Returns a style group combining this background color with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()


class _FgStyle(_Style):
    """A single ANSI foreground color code."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgStyle:
        """Convert to the corresponding foreground color style."""

        return self

    def as_bg(self) -> _BgStyle:
        """Convert to the corresponding background color style."""

        return _BgStyle(self._value + 10)

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this foreground."""

        return _FgColorStyle(255, 255, 255) if self._value in {30, 90} else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this foreground."""

        return _BgColorStyle(255, 255, 255) if self._value in {30, 90} else _BgColorStyle(0, 0, 0)

    def with_text_bg(self) -> _StyleGroup:
        """Returns a style group combining this foreground color with an optimal high-contrast text background."""

        return self | self.as_text_bg()


class _BgStyle(_Style):
    """A single ANSI background color code."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgStyle:
        """Convert to the corresponding foreground color style."""

        return _FgStyle(self._value - 10)

    def as_bg(self) -> _BgStyle:
        """Convert to the corresponding background color style."""

        return self

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this background."""

        return _FgColorStyle(255, 255, 255) if self._value in {40, 100} else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this background."""

        return _BgColorStyle(255, 255, 255) if self._value in {40, 100} else _BgColorStyle(0, 0, 0)

    def with_text_fg(self) -> _StyleGroup:
        """Returns a style group combining this background color with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()


class _Color256Style(_SBase):
    """An 8-bit / 256-color palette style – foreground or background.\n
    ----------------------------------------------------------------------------------------------------
    *   `code` – The 256-color palette index in range [0, 255] inclusive.
    *   `bg` – Whether this style applies to the background instead of the foreground.\n
    ----------------------------------------------------------------------------------------------------
    >>> S.color256(196)("text")     # Red FG from 256-color palette
    >>> S.BG.color256(21)("text")   # Blue BG from 256-color palette"""

    __slots__: tuple[str, ...] = ("_bg", "_close_seq", "_code", "_open_seq")

    def __init__(self, code: int, /, *, bg: bool = False) -> None:
        if not (0 <= code <= 255):
            raise ValueError(f"Expected 256-color index in range [0, 255] inclusive, got {code!r}")

        self._code: int = code
        self._bg: bool = bg

        if bg:
            self._open_seq: str = ANSI.SEQ_BG_COLOR_256.format(code)
            self._close_seq: str = f"{ANSI.CHAR}[49m"
        else:
            self._open_seq = ANSI.SEQ_FG_COLOR_256.format(code)
            self._close_seq = f"{ANSI.CHAR}[39m"

        self.ansi = self._open_seq

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this 256-color style with another style or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(self, *other._codes)

        return _StyleGroup(self, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this 256-color style with another style or group via `|`."""

        return _StyleGroup(other, self)

    def __call__(self, *text: Renderable) -> S:
        """Applies this 256-color style to the given text, auto-resetting after."""

        return _render_styled((self._open_seq,), (self._close_seq,), text)

    def __matmul__(self, text: Renderable) -> S:
        """Applies this 256-color style to the given text, auto-resetting after."""

        return _render_styled((self._open_seq,), (self._close_seq,), (text,))

    def __repr__(self) -> str:
        """Returns a string representation of this 256-color style."""

        return f"_Color256Style({'bg' if self._bg else 'fg'} {self._code})"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_Color256Style` with identical color code and background flag."""

        if isinstance(other, _Color256Style):
            return self._code == other._code and self._bg == other._bg
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash((self._code, self._bg))

    def as_fg(self) -> _FgColor256Style:
        """Convert to the corresponding foreground color style."""

        return _FgColor256Style(self._code)

    def as_bg(self) -> _BgColor256Style:
        """Convert to the corresponding background color style."""

        return _BgColor256Style(self._code)

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this color."""

        if self._code < 16:
            return _FgColorStyle(255, 255, 255) if self._code in {0, 8} else _FgColorStyle(0, 0, 0)

        red, green, blue = _ansi256_to_rgb(self._code)
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return _FgColorStyle(255, 255, 255) if luminance < 128 else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this color."""

        if self._code < 16:
            return _BgColorStyle(255, 255, 255) if self._code in {0, 8} else _BgColorStyle(0, 0, 0)

        red, green, blue = _ansi256_to_rgb(self._code)
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return _BgColorStyle(255, 255, 255) if luminance < 128 else _BgColorStyle(0, 0, 0)


class _FgColor256Style(_Color256Style):
    """A 256-color palette foreground style."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgColor256Style:
        """Convert to the corresponding foreground color style."""

        return self

    def as_bg(self) -> _BgColor256Style:
        """Convert to the corresponding background color style."""

        return _BgColor256Style(self._code)

    def with_text_bg(self) -> _StyleGroup:
        """Returns a style group combining this foreground color with an optimal high-contrast text background."""

        return self | self.as_text_bg()


class _BgColor256Style(_Color256Style):
    """A 256-color palette background style."""

    __slots__: tuple[str, ...] = ()

    def __init__(self, code: int, /, *, bg: bool = True) -> None:
        super().__init__(code, bg=bg)

    def as_fg(self) -> _FgColor256Style:
        """Convert to the corresponding foreground color style."""

        return _FgColor256Style(self._code)

    def as_bg(self) -> _BgColor256Style:
        """Convert to the corresponding background color style."""

        return self

    def with_text_fg(self) -> _StyleGroup:
        """Returns a style group combining this background color with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()


class _Link(_SBase):
    """An OSC 8 hyperlink. Combine with other styles via `|` to add text styling.\n
    ----------------------------------------------------------------------------------------------------
    >>> S.link("https://example.com")("click here")
    >>> (S.link("https://example.com") | S.BR.BLUE)("click here")"""

    __slots__: tuple[str, ...] = ("_close_seq", "_open_seq", "_url")

    def __init__(self, url: str | Path, /) -> None:
        self._url: str = url.resolve().as_uri() if isinstance(url, Path) else url
        self._open_seq: str = ANSI.SEQ_LINK_OPEN.format(self._url)
        self._close_seq: str = ANSI.SEQ_LINK_CLOSE
        self.ansi = self._open_seq

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this link style with another style or group via `|`."""

        if isinstance(other, _StyleGroup):
            return _StyleGroup(self, *other._codes)

        return _StyleGroup(self, other)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this link style with another style or group via `|`."""

        return _StyleGroup(other, self)

    def __call__(self, *text: Renderable) -> S:
        """Applies this link style to the given text, auto-resetting after."""

        return _render_styled((self._open_seq,), (self._close_seq,), text)

    def __matmul__(self, text: Renderable) -> S:
        """Applies this link style to the given text, auto-resetting after."""

        return _render_styled((self._open_seq,), (self._close_seq,), (text,))

    def __repr__(self) -> str:
        """Returns a string representation of this link style, showing the URL it points to."""

        return f"_Link({self._url!r})"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_Link` pointing to the same URL."""

        if isinstance(other, _Link):
            return self._url == other._url
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash(self._url)

    def as_fg(self) -> _Link:
        """Convert to the corresponding foreground style."""

        return self

    def as_bg(self) -> _Link:
        """Convert to the corresponding background style."""

        return self


class _StyleGroup(_SBase):
    """An immutable, ordered group of styles produced by `|`.\n
    ----------------------------------------------------------------------------------------------------
    Supports further `|` chaining and `()` application."""

    __slots__: tuple[str, ...] = ("_codes", "_oc")

    def __init__(self, *codes: BaseStyle) -> None:
        self._codes: tuple[BaseStyle, ...] = codes
        self._oc = _build_open_close(self)
        self.ansi = "".join(self._oc[0])

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

    def __call__(self, *text: Renderable) -> S:
        """Applies this style group to the given text, auto-resetting after."""

        return _render_styled(self._oc[0], self._oc[1], text)

    def __matmul__(self, text: Renderable) -> S:
        """Applies this style group to the given text, auto-resetting after."""

        return _render_styled(self._oc[0], self._oc[1], (text,))

    def __repr__(self) -> str:
        """Returns a string representation of this style group, showing its individual codes."""

        return f"_StyleGroup{self._codes!r}"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_StyleGroup` with identical style codes in identical order."""

        if isinstance(other, _StyleGroup):
            return self._codes == other._codes
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash(self._codes)

    def as_fg(self) -> _StyleGroup:
        """Convert all background color styles in this group to foreground color styles."""

        return _StyleGroup(*[code.as_fg() for code in self._codes])

    def as_bg(self) -> _StyleGroup:
        """Convert all foreground color styles in this group to background color styles."""

        return _StyleGroup(*[code.as_bg() for code in self._codes])

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on the background in this group."""

        for code in reversed(self._codes):
            if isinstance(code, (_BgStyle, _BgColorStyle, _BgColor256Style)):
                return code.as_text_fg()

        return _FgColorStyle(255, 255, 255)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind the foreground in this group."""

        for code in reversed(self._codes):
            if isinstance(code, (_FgStyle, _FgColorStyle, _FgColor256Style)):
                return code.as_text_bg()

        return _BgColorStyle(0, 0, 0)

    def with_text_fg(self) -> _StyleGroup:
        """Returns a new style group combining this group with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()

    def with_text_bg(self) -> _StyleGroup:
        """Returns a new style group combining this group with an optimal high-contrast text background."""

        return self | self.as_text_bg()


# ***************************************************** NAMESPACE HELPERS *****************************************************


class _BgBrNS:
    """Namespace for bright background colors, reachable as `S.BG.BR.*`."""

    BLACK: ClassVar[_BgStyle] = _BgStyle(100)
    """Bright black (gray) background."""
    RED: ClassVar[_BgStyle] = _BgStyle(101)
    """Bright red background."""
    GREEN: ClassVar[_BgStyle] = _BgStyle(102)
    """Bright green background."""
    YELLOW: ClassVar[_BgStyle] = _BgStyle(103)
    """Bright yellow background."""
    BLUE: ClassVar[_BgStyle] = _BgStyle(104)
    """Bright blue background."""
    MAGENTA: ClassVar[_BgStyle] = _BgStyle(105)
    """Bright magenta background."""
    CYAN: ClassVar[_BgStyle] = _BgStyle(106)
    """Bright cyan background."""
    WHITE: ClassVar[_BgStyle] = _BgStyle(107)
    """Bright white background."""


class _BgNS:
    """Namespace for background styles and colors, reachable as `S.BG.*`."""

    BR: ClassVar[type[_BgBrNS]] = _BgBrNS
    """Access bright background colors (e.g., `S.BG.BR.RED`)."""

    BLACK: ClassVar[_BgStyle] = _BgStyle(40)
    """Black background."""
    RED: ClassVar[_BgStyle] = _BgStyle(41)
    """Red background."""
    GREEN: ClassVar[_BgStyle] = _BgStyle(42)
    """Green background."""
    YELLOW: ClassVar[_BgStyle] = _BgStyle(43)
    """Yellow background."""
    BLUE: ClassVar[_BgStyle] = _BgStyle(44)
    """Blue background."""
    MAGENTA: ClassVar[_BgStyle] = _BgStyle(45)
    """Magenta background."""
    CYAN: ClassVar[_BgStyle] = _BgStyle(46)
    """Cyan background."""
    WHITE: ClassVar[_BgStyle] = _BgStyle(47)
    """White background."""

    # ********************** CUSTOM BG COLORS ***********************

    @overload
    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _BgColorStyle: ...
    @overload
    @staticmethod
    def rgb(color: rgba, /) -> _BgColorStyle: ...

    @staticmethod
    def rgb(*args: Any) -> _BgColorStyle:
        """24-bit background color from RGB components or an `rgba` object.\n
        `S.BG.rgb(112, 118, 255)("text")` or `S.BG.rgb(my_rgba)("text")`"""

        if len(args) == 3:
            return _BgColorStyle(args[0], args[1], args[2])

        return _BgColorStyle(args[0][0], args[0][1], args[0][2])

    @staticmethod
    def hex(color: str | int | hexa, /) -> _BgColorStyle:
        """24-bit background color from HEX string, HEX integer, or `hexa` object.\n
        `S.BG.hex("#67F")("text")`, `S.BG.hex(0x7075FF)`, or `S.BG.hex(my_hexa)("text")`"""

        return _BgColorStyle.from_hex(color, bg=True)

    @staticmethod
    def color256(code: int, /) -> _BgColor256Style:
        """256-color palette background color (code in range [0, 255] inclusive).\n
        `S.BG.color256(196)("text")`"""

        return _BgColor256Style(code)


class _BrNS:
    """Namespace for bright foreground colors, reachable as `S.BR.*`."""

    BLACK: ClassVar[_FgStyle] = _FgStyle(90)
    """Bright black (gray) foreground."""
    RED: ClassVar[_FgStyle] = _FgStyle(91)
    """Bright red foreground."""
    GREEN: ClassVar[_FgStyle] = _FgStyle(92)
    """Bright green foreground."""
    YELLOW: ClassVar[_FgStyle] = _FgStyle(93)
    """Bright yellow foreground."""
    BLUE: ClassVar[_FgStyle] = _FgStyle(94)
    """Bright blue foreground."""
    MAGENTA: ClassVar[_FgStyle] = _FgStyle(95)
    """Bright magenta foreground."""
    CYAN: ClassVar[_FgStyle] = _FgStyle(96)
    """Bright cyan foreground."""
    WHITE: ClassVar[_FgStyle] = _FgStyle(97)
    """Bright white foreground."""


# ******************************************************* STYLE & TEXT ********************************************************


class S(_SBase):
    """Build a styled string from a sequence of segments (strings, `S` objects, bare styles, or raw<br>
    tuples), joined by `sep`, or use class-level style attributes and methods to apply ANSI styling.\n
    ----------------------------------------------------------------------------------------------------
    *   `segments` – Any number of segments to render.
        Each positional argument represents one logical line.
    *   `sep` – The separator inserted between two adjacent positional arguments (default `""`).\n
    ----------------------------------------------------------------------------------------------------
    After construction the instance exposes:
    *   `ansi` – The fully rendered ANSI escape string, ready to be written to a terminal.
    *   `raw` – `ansi` with every ANSI escape sequence stripped (computed on demand).
    *   `code_positions` – A tuple of `(position, sequence)` pairs giving<br>
        the start offset of every ANSI escape sequence inside `ansi` (computed on demand).\n
    ----------------------------------------------------------------------------------------------------
    Every style attribute supports `|` for combining and `()` for applying to text.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    from xulbux import S

    # Combine styles using operator `|`:
    status = (S.BOLD | S.BR.GREEN)("SUCCESS")

    # Nesting and joining styled items:
    header = S(S.BOLD("Options: "), S(", ").join([S.CYAN("fast"), S.CYAN("safe")]))

    # Direct terminal printing:
    status.print()
    ```"""

    __slots__: tuple[str, ...] = ()

    # ************************* TOTAL RESET *************************

    RESET: ClassVar[_Style] = _Style(0)
    """Reset all styling to default."""

    # *********************** SPECIFIC RESETS ***********************

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
    RESET_BLINK: ClassVar[_Style] = _Style(25)
    """Reset blink."""
    RESET_FG: ClassVar[_Style] = _Style(39)
    """Reset foreground color."""
    RESET_BG: ClassVar[_Style] = _Style(49)
    """Reset background color."""

    # ************************* TEXT STYLES *************************

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
    BLINK: ClassVar[_Style] = _Style(5)
    """Blinking text."""
    INVERSE: ClassVar[_Style] = _Style(7)
    """Inverse colors (swap foreground and background colors)."""
    HIDDEN: ClassVar[_Style] = _Style(8)
    """Hidden (invisible) text."""
    STRIKETHROUGH: ClassVar[_Style] = _Style(9)
    """Strikethrough text."""
    DOUBLE_UNDERLINE: ClassVar[_Style] = _Style(21)
    """Double underline text."""

    # ********************* STANDARD FG COLORS **********************

    BLACK: ClassVar[_FgStyle] = _FgStyle(30)
    """Black foreground."""
    RED: ClassVar[_FgStyle] = _FgStyle(31)
    """Red foreground."""
    GREEN: ClassVar[_FgStyle] = _FgStyle(32)
    """Green foreground."""
    YELLOW: ClassVar[_FgStyle] = _FgStyle(33)
    """Yellow foreground."""
    BLUE: ClassVar[_FgStyle] = _FgStyle(34)
    """Blue foreground."""
    MAGENTA: ClassVar[_FgStyle] = _FgStyle(35)
    """Magenta foreground."""
    CYAN: ClassVar[_FgStyle] = _FgStyle(36)
    """Cyan foreground."""
    WHITE: ClassVar[_FgStyle] = _FgStyle(37)
    """Bright white foreground."""

    # ************************* NAMESPACES **************************

    BR: ClassVar[type[_BrNS]] = _BrNS
    BG: ClassVar[type[_BgNS]] = _BgNS

    # ******************** CUSTOM COLORS & LINKS ********************

    @overload
    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _FgColorStyle: ...
    @overload
    @staticmethod
    def rgb(color: rgba, /) -> _FgColorStyle: ...

    @staticmethod
    def rgb(*args: Any) -> _FgColorStyle:
        """24-bit foreground color from RGB components or an `rgba` object.\n
        `S.rgb(112, 118, 255)("text")` or `S.rgb(my_rgba)("text")`"""

        if len(args) == 3:
            return _FgColorStyle(args[0], args[1], args[2])

        return _FgColorStyle(args[0][0], args[0][1], args[0][2])

    @staticmethod
    def hex(color: str | int | hexa, /) -> _FgColorStyle:
        """24-bit foreground color from HEX string, HEX integer, or `hexa` object.\n
        `S.hex("#67F")("text")`, `S.hex(0x7075FF)`, or `S.hex(my_hexa)("text")`"""

        return _FgColorStyle.from_hex(color)

    @staticmethod
    def color256(code: int, /) -> _FgColor256Style:
        """256-color palette foreground color (code in range [0, 255] inclusive).\n
        `S.color256(196)("text")`"""

        return _FgColor256Style(code)

    @staticmethod
    def link(url: str | Path, /) -> _Link:
        """Clickable hyperlink. Accepts strings or `pathlib.Path` objects.<br>
        If a `pathlib.Path` is passed, it is automatically resolved and converted to a URI.\n
        ----------------------------------------------------------------------------------------------------
        >>> S.link("https://example.com")("click here")
        >>> S.link(Path("docs/readme.md"))("open file")"""

        return _Link(url)

    # *********************** INITIALIZATION ************************

    def __init__(self, /, *segments: Renderable, sep: str = "") -> None:
        ansi_parts: list[str] = []

        for i, segment in enumerate(segments):
            if i > 0 and sep:
                ansi_parts.append(sep)

            _render_segment(segment, ansi_parts)

        self.ansi = "".join(ansi_parts)


# **************************************************** PUBLIC TYPE HELPERS ****************************************************


type FgColorStyle = _FgStyle | _FgColorStyle | _FgColor256Style
"""A single foreground color style code (e.g., `S.RED`, `S.BR.BLUE`, `S.hex("#67F")`, `S.color256(196)`).<br>
Excludes background colors and non-color styles like `S.BOLD`."""


def is_fg_color_style(obj: object, /) -> TypeIs[FgColorStyle]:
    """Returns true if `obj` is an instance that matches the `FgColorStyle` type."""

    if isinstance(obj, (_FgColorStyle, _FgColor256Style, _FgStyle)):
        return True
    elif isinstance(obj, _Style):
        return (30 <= (val := obj._value) <= 37) or (90 <= val <= 97)
    elif isinstance(obj, (_ColorStyle, _Color256Style)):
        return not obj._bg

    return False


type BgColorStyle = _BgStyle | _BgColorStyle | _BgColor256Style
"""A single background color style code (e.g., `S.BG.RED`, `S.BG.hex("#67F")`, `S.BG.color256(196)`).<br>
Excludes foreground colors and non-color styles like `S.BOLD`."""


def is_bg_color_style(obj: object, /) -> TypeIs[BgColorStyle]:
    """Returns true if `obj` is an instance that matches the `BgColorStyle` type."""

    if isinstance(obj, (_BgColorStyle, _BgColor256Style, _BgStyle)):
        return True
    elif isinstance(obj, _Style):
        return (40 <= (val := obj._value) <= 47) or (100 <= val <= 107)
    elif isinstance(obj, (_ColorStyle, _Color256Style)):
        return obj._bg

    return False


type ColorStyle = FgColorStyle | BgColorStyle
"""Any single foreground or background color style code (e.g., `S.RED`, `S.BG.BLUE`, `S.hex("#67F")`).<br>
Excludes non-color styles like `S.BOLD`."""


def is_color_style(obj: object, /) -> TypeIs[ColorStyle]:
    """Returns true if `obj` is an instance that matches the `ColorStyle` type."""

    return is_fg_color_style(obj) or is_bg_color_style(obj)


type BaseStyle = _Style | _ColorStyle | _Color256Style | _Link
"""Any single style code, color style, or link style that can be combined via `|` and applied to text."""


def is_base_style(obj: object, /) -> TypeIs[BaseStyle]:
    """Returns true if `obj` is an instance that matches the `BaseStyle` type."""

    return isinstance(obj, (_Style, _ColorStyle, _Color256Style, _Link))


type AnyStyle = BaseStyle | _StyleGroup
"""Any single style or group of styles that can be combined via `|` and applied to text."""


def is_any_style(obj: object, /) -> TypeIs[AnyStyle]:
    """Returns true if `obj` is an instance that matches the `AnyStyle` type."""

    return isinstance(obj, (_Style, _ColorStyle, _Color256Style, _Link, _StyleGroup))


type TextSegment = str | S
"""A single segment that contains actual text: a plain string or a styled `S` object.<br>
Strictly excludes bare style objects (e.g., `S.RED`, `S.BOLD | S.BLUE`) that do not contain text."""


def is_text_segment(obj: object, /) -> TypeIs[TextSegment]:
    """Returns true if `obj` is an instance that matches the `TextSegment` type (has actual text)."""

    return isinstance(obj, (str, S))


type RenderSegment = str | _SBase
"""A single segment: a plain string, a bare style object (open-only), or a styled `S` object."""


def is_render_segment(obj: object, /) -> TypeIs[RenderSegment]:
    """Returns true if `obj` is an instance that matches the `RenderSegment` type."""

    return isinstance(obj, (str, _SBase))


type TextRenderable = TextSegment | tuple[TextRenderable, ...]
"""Anything that contains actual textual content to be rendered, strictly excluding bare styles.<br>
Can be passed to a `_Style` call, or as a positional argument to `S(…)`. Can be arbitrarily nested in tuples."""


def is_text_renderable(obj: object, /) -> TypeIs[TextRenderable]:
    """Returns true if `obj` is an instance that matches the `TextRenderable` type."""

    if isinstance(obj, (str, S)):
        return True

    elif isinstance(obj, tuple):
        # Don't use `all()` as for-loop is more performant:
        for item in cast("tuple[Any, ...]", obj):  # ruff:ignore[reimplemented-builtin]
            if not is_text_renderable(item):
                return False
        return True

    return False


type Renderable = RenderSegment | tuple[Renderable, ...]
"""Anything that can be styled or rendered.<br>
Can be passed to a `_Style` call, or as a positional argument to `S(…)`. Can be arbitrarily nested in tuples."""


def is_renderable(obj: object, /) -> TypeIs[Renderable]:
    """Returns true if `obj` is an instance that matches the `Renderable` type."""

    if isinstance(obj, (str, _SBase)):
        return True

    elif isinstance(obj, tuple):
        # Don't use `all()` as for-loop is more performant:
        for item in cast("tuple[Any, ...]", obj):  # ruff:ignore[reimplemented-builtin]
            if not is_renderable(item):
                return False
        return True

    return False


# ***************************************************** TERMINAL CONTROL ******************************************************


class Term:
    """Common ANSI terminal control sequences (cursor, screen, title, clipboard, modes)<br>
    as plain strings or string-returning static methods.\n
    ----------------------------------------------------------------------------------------------------
    Values can be passed straight into an `S(…)` call or written to `sys.stdout`.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import sys
    from xulbux import Term

    # Switch to alternate screen and hide cursor:
    sys.stdout.write(Term.ALT_SCREEN + Term.CUR_HIDE)
    sys.stdout.flush()

    # Move cursor up 2 rows and clear line:
    sys.stdout.write(Term.up(2) + Term.CLEAR_LINE)
    sys.stdout.flush()

    # Restore main screen and cursor:
    sys.stdout.write(Term.CUR_SHOW + Term.MAIN_SCREEN)
    sys.stdout.flush()
    ```"""

    BELL: ClassVar[str] = "\x07"
    """Terminal bell character to trigger an audio or visual alert."""
    CLEAR_LINE: ClassVar[str] = f"{ANSI.CHAR}[2K"
    """Erase the entire current line."""
    CLEAR_LINE_TO_END: ClassVar[str] = f"{ANSI.CHAR}[0K"
    """Erase from the cursor to the end of the current line."""
    CLEAR_LINE_TO_START: ClassVar[str] = f"{ANSI.CHAR}[1K"
    """Erase from the beginning of the line up to the cursor."""
    CLEAR_SCREEN: ClassVar[str] = f"{ANSI.CHAR}[2J"
    """Erase the whole screen."""
    CLEAR_SCREEN_TO_END: ClassVar[str] = f"{ANSI.CHAR}[0J"
    """Erase from the cursor to the end of the screen."""
    CLEAR_SCREEN_TO_START: ClassVar[str] = f"{ANSI.CHAR}[1J"
    """Erase from the beginning of the screen up to the cursor."""
    CLEAR_SCROLLBACK: ClassVar[str] = f"{ANSI.CHAR}[3J"
    """Erase the terminal scrollback history buffer."""
    CUR_HIDE: ClassVar[str] = f"{ANSI.CHAR}[?25l"
    """Hide the cursor."""
    CUR_SHOW: ClassVar[str] = f"{ANSI.CHAR}[?25h"
    """Show the cursor."""
    CUR_HOME: ClassVar[str] = f"{ANSI.CHAR}[H"
    """Move the cursor to the home position (0,0) (CUP/HVP)."""
    CUR_SAVE: ClassVar[str] = f"{ANSI.CHAR}[s"
    """Save the current cursor position (ANSI.SYS / SCO)."""
    CUR_RESTORE: ClassVar[str] = f"{ANSI.CHAR}[u"
    """Restore the previously saved cursor position (ANSI.SYS / SCO)."""
    CUR_SAVE_DEC: ClassVar[str] = f"{ANSI.CHAR}7"
    """Save cursor position and attributes (DEC private sequence ESC 7)."""
    CUR_RESTORE_DEC: ClassVar[str] = f"{ANSI.CHAR}8"
    """Restore cursor position and attributes (DEC private sequence ESC 8)."""
    ALT_SCREEN: ClassVar[str] = f"{ANSI.CHAR}[?1049h"
    """Enter the alternate screen buffer."""
    MAIN_SCREEN: ClassVar[str] = f"{ANSI.CHAR}[?1049l"
    """Leave the alternate screen buffer."""
    BRACKETED_PASTE_ENABLE: ClassVar[str] = f"{ANSI.CHAR}[?2004h"
    """Enable bracketed paste mode (wraps pasted text in paste brackets)."""
    BRACKETED_PASTE_DISABLE: ClassVar[str] = f"{ANSI.CHAR}[?2004l"
    """Disable bracketed paste mode."""
    LINE_WRAP_ENABLE: ClassVar[str] = f"{ANSI.CHAR}[?7h"
    """Enable line wrapping (DECAWM)."""
    LINE_WRAP_DISABLE: ClassVar[str] = f"{ANSI.CHAR}[?7l"
    """Disable line wrapping (DECAWM)."""
    RESET: ClassVar[str] = f"{ANSI.CHAR}c"
    """Hard reset to initial state (RIS)."""
    SOFT_RESET: ClassVar[str] = f"{ANSI.CHAR}[!p"
    """Soft terminal reset to sensible defaults (DECSTR)."""

    @staticmethod
    def up(n: int = 1, /) -> str:
        """Move the cursor up by `n` rows."""

        return f"{ANSI.CHAR}[{n}A"

    @staticmethod
    def down(n: int = 1, /) -> str:
        """Move the cursor down by `n` rows."""

        return f"{ANSI.CHAR}[{n}B"

    @staticmethod
    def left(n: int = 1, /) -> str:
        """Move the cursor left by `n` columns."""

        return f"{ANSI.CHAR}[{n}D"

    @staticmethod
    def right(n: int = 1, /) -> str:
        """Move the cursor right by `n` columns."""

        return f"{ANSI.CHAR}[{n}C"

    @staticmethod
    def prev_line(n: int = 1, /) -> str:
        """Move the cursor to the beginning of the previous line, `n` lines up."""

        return f"{ANSI.CHAR}[{n}F"

    @staticmethod
    def next_line(n: int = 1, /) -> str:
        """Move the cursor to the beginning of the next line, `n` lines down."""

        return f"{ANSI.CHAR}[{n}E"

    @staticmethod
    def row(row: int = 1, /) -> str:
        """Move the cursor to absolute row `row` in the current column (1-based, VPA)."""

        return f"{ANSI.CHAR}[{row}d"

    @staticmethod
    def col(col: int = 1, /) -> str:
        """Move the cursor to absolute column `col` in the current row (1-based, CHA)."""

        return f"{ANSI.CHAR}[{col}G"

    @staticmethod
    def move(row: int, col: int, /) -> str:
        """Move the cursor to absolute position `(row, col)` (1-based, CUP)."""

        return f"{ANSI.CHAR}[{row};{col}H"

    @staticmethod
    def insert_lines(n: int = 1, /) -> str:
        """Insert `n` blank lines at the current row (IL)."""

        return f"{ANSI.CHAR}[{n}L"

    @staticmethod
    def delete_lines(n: int = 1, /) -> str:
        """Delete `n` lines starting from the current row (DL)."""

        return f"{ANSI.CHAR}[{n}M"

    @staticmethod
    def insert_chars(n: int = 1, /) -> str:
        """Insert `n` blank characters at the current cursor position (ICH)."""

        return f"{ANSI.CHAR}[{n}@"

    @staticmethod
    def delete_chars(n: int = 1, /) -> str:
        """Delete `n` characters at the current cursor position (DCH)."""

        return f"{ANSI.CHAR}[{n}P"

    @staticmethod
    def scroll_up(n: int = 1, /) -> str:
        """Scroll page up by `n` lines."""

        return f"{ANSI.CHAR}[{n}S"

    @staticmethod
    def scroll_down(n: int = 1, /) -> str:
        """Scroll page down by `n` lines."""

        return f"{ANSI.CHAR}[{n}T"

    @staticmethod
    def title(text: str, /) -> str:
        """Set the terminal window / tab title (OSC 2)."""

        return f"{ANSI.CHAR}]2;{text}\x07"

    @staticmethod
    def cursor_shape(
        shape: Literal[
            1,
            2,
            3,
            4,
            5,
            6,
            "blinking_block",
            "steady_block",
            "blinking_underline",
            "steady_underline",
            "blinking_bar",
            "steady_bar",
        ],
        /,
    ) -> str:
        """Set the terminal cursor shape (DECSCUSR).\n
        ----------------------------------------------------------------------------------------------------
        *   `shape` – An integer in range [1, 6] inclusive, or a string name of the shape:
            - `1` `"blinking_block"`
            - `2` `"steady_block"`
            - `3` `"blinking_underline"`
            - `4` `"steady_underline"`
            - `5` `"blinking_bar"`
            - `6` `"steady_bar"`"""

        if (shape_num := _CURSOR_SHAPES.get(shape) if isinstance(shape, str) else shape) not in {1, 2, 3, 4, 5, 6}:
            raise ValueError(
                f"Expected cursor shape in [1, 6] inclusive, or one of {list(_CURSOR_SHAPES.keys())!r}, got {shape!r}"
            )

        return f"{ANSI.CHAR}[{shape_num} q"

    @staticmethod
    def clipboard_copy(text: str, /) -> str:
        """Copy `text` to the system clipboard (OSC 52)."""

        encoded = _base64.b64encode(text.encode("utf-8")).decode("ascii")
        return f"{ANSI.CHAR}]52;c;{encoded}{ANSI.CHAR}\\"

    @staticmethod
    def cwd(path: str | Path, /) -> str:
        """Notify the terminal of the current working directory (OSC 7)."""

        uri = path.resolve().as_uri() if isinstance(path, Path) else path
        return f"{ANSI.CHAR}]7;{uri}{ANSI.CHAR}\\"
