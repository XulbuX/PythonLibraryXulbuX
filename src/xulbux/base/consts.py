# ruff:file-ignore[ambiguous-unicode-character-string]

"""
Provides constant values used throughout the library.

Includes character sets and ANSI escape sequences.
"""

from .types import AllTextChars, FormattableString

from typing import Final
import regex as _rx
from regex import Pattern


class ANSI:
    """Constants and utilities for ANSI escape code sequences."""

    # ********************** ESCAPE CHARACTERS **********************

    CHAR_ESCAPED: Final[str] = r"\x1b"
    """Printable ANSI escape character."""
    CHAR: Final[str] = "\x1b"
    """ANSI escape character."""

    # *********************** COLOR SEQUENCES ***********************

    SEQ_FG_COLOR: Final[FormattableString] = f"{CHAR}[38;2;{{}};{{}};{{}}m"
    """RGB foreground color sequence with placeholders for red, green, and blue values."""
    SEQ_BG_COLOR: Final[FormattableString] = f"{CHAR}[48;2;{{}};{{}};{{}}m"
    """RGB background color sequence with placeholders for red, green, and blue values."""
    SEQ_FG_COLOR_256: Final[FormattableString] = f"{CHAR}[38;5;{{}}m"
    """256-color foreground sequence with placeholder for color index (0-255)."""
    SEQ_BG_COLOR_256: Final[FormattableString] = f"{CHAR}[48;5;{{}}m"
    """256-color background sequence with placeholder for color index (0-255)."""

    # *********************** LINK SEQUENCES ************************

    SEQ_LINK_OPEN: Final[FormattableString] = f"{CHAR}]8;;{{}}{CHAR}\\"
    """OSC 8 hyperlink opening sequence with a placeholder for the URL."""
    SEQ_LINK_CLOSE: Final[str] = f"{CHAR}]8;;{CHAR}\\"
    """OSC 8 hyperlink closing sequence."""

    # *********************** REGEX PATTERNS ************************

    SEQ_PATTERN: Final[Pattern[str]] = _rx.compile(CHAR + r"(?:\].*?(?:\x1b\\|\x07)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_c]|[0-9=><])")
    """Compiled regex pattern matching any ANSI escape sequence (CSI, OSC, or single-character)."""


class CHARS:
    """Character set constants for text validation and filtering."""

    # *********************** SENTINEL VALUES ***********************

    ALL: Final[AllTextChars] = AllTextChars()
    """Sentinel value indicating all characters are allowed."""

    # *************************** DIGITS ****************************

    DIGITS: Final[str] = "0123456789"
    """Numeric digits: `0`-`9`"""
    FLOAT_DIGITS: Final[str] = "." + DIGITS
    """Numeric digits with decimal point: `0`-`9` and `.`"""
    HEX_DIGITS: Final[str] = "#" + DIGITS + "abcdefABCDEF"
    """Hexadecimal digits: `0`-`9`, `a`-`f`, `A`-`F`, and `#`"""

    # *************************** LETTERS ***************************

    LOWERCASE: Final[str] = "abcdefghijklmnopqrstuvwxyz"
    """Lowercase ASCII letters: `a`-`z`"""
    LOWERCASE_EXTENDED: Final[str] = LOWERCASE + "äëïöüÿàèìòùáéíóúýâêîôûãñõåæç"
    """Lowercase ASCII letters with diacritic marks."""
    UPPERCASE: Final[str] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    """Uppercase ASCII letters: `A`-`Z`"""
    UPPERCASE_EXTENDED: Final[str] = UPPERCASE + "ÄËÏÖÜÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÅÆÇß"
    """Uppercase ASCII letters with diacritic marks."""
    LETTERS: Final[str] = LOWERCASE + UPPERCASE
    """All ASCII letters: `a`-`z` and `A`-`Z`"""
    LETTERS_EXTENDED: Final[str] = LOWERCASE_EXTENDED + UPPERCASE_EXTENDED
    """All ASCII letters with diacritic marks."""

    # ******************** SPECIAL & FULL ASCII *********************

    SPECIAL_ASCII: Final[str] = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    """Standard ASCII special characters and symbols."""
    SPECIAL_ASCII_EXTENDED: Final[str] = (
        SPECIAL_ASCII + "ø£Ø×ƒªº¿®¬½¼¡«»░▒▓│┤©╣║╗╝¢¥┐└┴┬├─┼╚╔╩╦╠═╬¤ðÐı┘┌█▄¦▀µþÞ¯´≡­±‗¾¶§÷¸°¨·¹³²■ "
    )
    """Standard and extended ASCII special characters."""
    STANDARD_ASCII: Final[str] = DIGITS + LETTERS + SPECIAL_ASCII
    """All standard ASCII characters (letters, digits, and symbols)."""
    FULL_ASCII: Final[str] = DIGITS + LETTERS_EXTENDED + SPECIAL_ASCII_EXTENDED
    """Complete ASCII character set including extended characters."""


class KEYS:
    """Terminal key sequences and scan code constants for cross-platform input parsing."""

    # ********************** DIRECTIONAL KEYS ***********************

    UP: Final[frozenset[str]] = frozenset(("\x1b[A", "\x1bOA", "\x00H", "\xe0H"))
    """Up arrow key sequences."""
    DOWN: Final[frozenset[str]] = frozenset(("\x1b[B", "\x1bOB", "\x00P", "\xe0P"))
    """Down arrow key sequences."""
    LEFT: Final[frozenset[str]] = frozenset(("\x1b[D", "\x1bOD", "\x00K", "\xe0K"))
    """Left arrow key sequences."""
    RIGHT: Final[frozenset[str]] = frozenset(("\x1b[C", "\x1bOC", "\x00M", "\xe0M"))
    """Right arrow key sequences."""
    ARROWS: Final[frozenset[str]] = UP | DOWN | LEFT | RIGHT
    """All directional arrow key sequences."""
    SHIFT_UP: Final[frozenset[str]] = frozenset(("\x1b[1;2A", "\x1b[a"))
    """`Shift+Up` arrow key sequences."""
    SHIFT_DOWN: Final[frozenset[str]] = frozenset(("\x1b[1;2B", "\x1b[b"))
    """`Shift+Down` arrow key sequences."""
    SHIFT_LEFT: Final[frozenset[str]] = frozenset(("\x1b[1;2D", "\x1b[d"))
    """`Shift+Left` arrow key sequences."""
    SHIFT_RIGHT: Final[frozenset[str]] = frozenset(("\x1b[1;2C", "\x1b[c"))
    """`Shift+Right` arrow key sequences."""
    CTRL_UP: Final[frozenset[str]] = frozenset(("\x1b[1;5A", "\x1b[5A", "\x00\x8d", "\xe0\x8d"))
    """`Ctrl+Up` arrow key sequences."""
    CTRL_DOWN: Final[frozenset[str]] = frozenset(("\x1b[1;5B", "\x1b[5B", "\x00\x91", "\xe0\x91"))
    """`Ctrl+Down` arrow key sequences."""
    CTRL_LEFT: Final[frozenset[str]] = frozenset(("\x1b[1;5D", "\x1b[5D", "\x1bOd", "\x00s", "\xe0s"))
    """`Ctrl+Left` arrow key sequences."""
    CTRL_RIGHT: Final[frozenset[str]] = frozenset(("\x1b[1;5C", "\x1b[5C", "\x1bOc", "\x00t", "\xe0t"))
    """`Ctrl+Right` arrow key sequences."""
    ALT_UP: Final[frozenset[str]] = frozenset(("\x1b[1;3A", "\x1b\x1b[A", "\x00\x98", "\xe0\x98"))
    """`Alt+Up` arrow key sequences."""
    ALT_DOWN: Final[frozenset[str]] = frozenset(("\x1b[1;3B", "\x1b\x1b[B", "\x00\xa0", "\xe0\xa0"))
    """`Alt+Down` arrow key sequences."""
    ALT_LEFT: Final[frozenset[str]] = frozenset(("\x1b[1;3D", "\x1b\x1b[D", "\x00\x9b", "\xe0\x9b", "\x1bb"))
    """`Alt+Left` arrow key sequences."""
    ALT_RIGHT: Final[frozenset[str]] = frozenset(("\x1b[1;3C", "\x1b\x1b[C", "\x00\x9d", "\xe0\x9d", "\x1bf"))
    """`Alt+Right` arrow key sequences."""

    # ********************* NAVIGATION & EDITING *********************

    HOME: Final[frozenset[str]] = frozenset(("\x1b[H", "\x1b[1~", "\x1b[7~", "\x1bOH", "\x00G", "\xe0G"))
    """Home key sequences."""
    END: Final[frozenset[str]] = frozenset(("\x1b[F", "\x1b[4~", "\x1b[8~", "\x1bOF", "\x00O", "\xe0O"))
    """End key sequences."""
    CTRL_HOME: Final[frozenset[str]] = frozenset(("\x1b[1;5H", "\x1b[1;5~", "\x00w", "\xe0w"))
    """`Ctrl+Home` key sequences."""
    CTRL_END: Final[frozenset[str]] = frozenset(("\x1b[1;5F", "\x1b[4;5~", "\x00u", "\xe0u"))
    """`Ctrl+End` key sequences."""
    PAGE_UP: Final[frozenset[str]] = frozenset(("\x1b[5~", "\x00I", "\xe0I"))
    """Page Up key sequences."""
    PAGE_DOWN: Final[frozenset[str]] = frozenset(("\x1b[6~", "\x00Q", "\xe0Q"))
    """Page Down key sequences."""
    CTRL_PAGE_UP: Final[frozenset[str]] = frozenset(("\x1b[5;5~", "\x00\x84", "\xe0\x84"))
    """`Ctrl+Page Up` key sequences."""
    CTRL_PAGE_DOWN: Final[frozenset[str]] = frozenset(("\x1b[6;5~", "\x00v", "\xe0v"))
    """`Ctrl+Page Down` key sequences."""
    INSERT: Final[frozenset[str]] = frozenset(("\x1b[2~", "\x00R", "\xe0R"))
    """Insert key sequences."""
    DELETE: Final[frozenset[str]] = frozenset(("\x1b[3~", "\x1b[P", "\x00S", "\xe0S"))
    """Delete key sequences."""
    CTRL_DELETE: Final[frozenset[str]] = frozenset(("\x1b[3;5~", "\x00\x93", "\xe0\x93"))
    """`Ctrl+Delete` key sequences."""
    BACKSPACE: Final[frozenset[str]] = frozenset(("\x7f", "\x08", "\x1b[127u"))
    """Backspace key representations."""
    ALT_BACKSPACE: Final[frozenset[str]] = frozenset(("\x1b\x7f", "\x1b\x08", "\x00\x0e", "\xe0\x0e"))
    """`Alt+Backspace` key representations."""
    TAB: Final[frozenset[str]] = frozenset(("\t", "\x1b[9u"))
    """Horizontal tab representations."""
    BACKTAB: Final[frozenset[str]] = frozenset(("\x1b[Z", "\x1b[9;2u", "\x00\x0f", "\xe0\x0f"))
    """Backtab and `Shift+Tab` key sequences."""

    # *********************** ACTION & CONTROL ***********************

    CTRL_A: Final[frozenset[str]] = frozenset(("\x01",))
    """`Ctrl+A` key representation (Home / Select All)."""
    CTRL_C: Final[frozenset[str]] = frozenset(("\x03",))
    """`Ctrl+C` key representation (Interrupt / Copy / Cancel)."""
    CTRL_D: Final[frozenset[str]] = frozenset(("\x04",))
    """`Ctrl+D` key representation (EOF / Exit / Forward-Delete)."""
    CTRL_E: Final[frozenset[str]] = frozenset(("\x05",))
    """`Ctrl+E` key representation (End)."""
    CTRL_K: Final[frozenset[str]] = frozenset(("\x0b",))
    """`Ctrl+K` key representation (Delete to end of line)."""
    CTRL_L: Final[frozenset[str]] = frozenset(("\x0c",))
    """`Ctrl+L` key representation (Clear Screen)."""
    CTRL_U: Final[frozenset[str]] = frozenset(("\x15",))
    """`Ctrl+U` key representation (Clear to start of line)."""
    CTRL_W: Final[frozenset[str]] = frozenset(("\x17",))
    """`Ctrl+W` key representation (Delete word backward)."""
    CTRL_Z: Final[frozenset[str]] = frozenset(("\x1a",))
    """`Ctrl+Z` key representation (Suspend / Undo)."""
    ENTER: Final[frozenset[str]] = frozenset(("\r", "\x1b[13u", "\x1bOM"))
    """Enter, Return, and Application Keypad Enter key representations."""
    CTRL_ENTER: Final[frozenset[str]] = frozenset((
        "\n",
        "\x1b[13;5u",
        "\x1b[13;6u",
        "\x1b[27;5;13~",
        "\x1b[27;6;13~",
        "\x1b[10;5u",
        "\x00\n",
        "\xe0\n",
    ))
    """`Ctrl+Enter` and `Ctrl+Shift+Enter` key sequences."""
    SHIFT_ENTER: Final[frozenset[str]] = frozenset(("\x1b[13;2u", "\x1b[27;2;13~"))
    """`Shift+Enter` key sequences."""
    ESCAPE: Final[frozenset[str]] = frozenset(("\x1b", "\x1b[27u", "\x1b\x1b"))
    """Escape and double-escape key representations."""
    SPACE: Final[frozenset[str]] = frozenset((" ", "\x1b[32u"))
    """Space character representations."""

    # ************************ FUNCTION KEYS *************************

    F1: Final[frozenset[str]] = frozenset(("\x1bOP", "\x1b[11~", "\x1b[[A", "\x00;", "\xe0;"))
    """`F1` function key sequences."""
    F2: Final[frozenset[str]] = frozenset(("\x1bOQ", "\x1b[12~", "\x1b[[B", "\x00<", "\xe0<"))
    """`F2` function key sequences."""
    F3: Final[frozenset[str]] = frozenset(("\x1bOR", "\x1b[13~", "\x1b[[C", "\x00=", "\xe0="))
    """`F3` function key sequences."""
    F4: Final[frozenset[str]] = frozenset(("\x1bOS", "\x1b[14~", "\x1b[[D", "\x00>", "\xe0>"))
    """`F4` function key sequences."""
    F5: Final[frozenset[str]] = frozenset(("\x1b[15~", "\x1b[[E", "\x00?", "\xe0?"))
    """`F5` function key sequences."""
    F6: Final[frozenset[str]] = frozenset(("\x1b[17~", "\x00@", "\xe0@"))
    """`F6` function key sequences."""
    F7: Final[frozenset[str]] = frozenset(("\x1b[18~", "\x00A", "\xe0A"))
    """`F7` function key sequences."""
    F8: Final[frozenset[str]] = frozenset(("\x1b[19~", "\x00B", "\xe0B"))
    """`F8` function key sequences."""
    F9: Final[frozenset[str]] = frozenset(("\x1b[20~", "\x00C", "\xe0C"))
    """`F9` function key sequences."""
    F10: Final[frozenset[str]] = frozenset(("\x1b[21~", "\x00D", "\xe0D"))
    """`F10` function key sequences."""
    F11: Final[frozenset[str]] = frozenset(("\x1b[23~", "\x00\x85", "\xe0\x85"))
    """`F11` function key sequences."""
    F12: Final[frozenset[str]] = frozenset(("\x1b[24~", "\x00\x86", "\xe0\x86"))
    """`F12` function key sequences."""
