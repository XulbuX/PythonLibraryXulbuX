# ruff:file-ignore[ambiguous-unicode-character-string]

"""
Provides constant values used throughout the library.

Includes character sets and ANSI escape sequences.
"""

from .types import AllTextChars, FormattableString

from typing import Final
import regex as _rx
from regex import Pattern


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
