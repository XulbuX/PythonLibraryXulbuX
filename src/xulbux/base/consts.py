# ruff:file-ignore[ambiguous-unicode-character-string]

"""
Provides constant values used throughout the library.

Includes color hex codes, ANSI sequences,
character sets, and default styling settings.
"""

from .types import AllTextChars, FormattableString

from typing import Final
import regex as _rx
from regex import Pattern


class COLOR:
    """Hexadecimal color presets."""

    WHITE: Final[str] = "#F1F2FF"
    LIGHT_GRAY: Final[str] = "#B6B7C0"
    GRAY: Final[str] = "#7B7C8D"
    DARK_GRAY: Final[str] = "#67686C"
    BLACK: Final[str] = "#202125"
    RED: Final[str] = "#FF606A"
    CORAL: Final[str] = "#FF7069"
    ORANGE: Final[str] = "#FF876A"
    TANGERINE: Final[str] = "#FF9962"
    GOLD: Final[str] = "#FFAF60"
    YELLOW: Final[str] = "#FFD260"
    LIME: Final[str] = "#C9F16E"
    GREEN: Final[str] = "#7EE787"
    NEON_GREEN: Final[str] = "#4CFF85"
    TEAL: Final[str] = "#50EAAF"
    CYAN: Final[str] = "#3EDEE6"
    ICE: Final[str] = "#77DBEF"
    LIGHT_BLUE: Final[str] = "#60AAFF"
    BLUE: Final[str] = "#8085FF"
    LAVENDER: Final[str] = "#9B7DFF"
    PURPLE: Final[str] = "#AD68FF"
    MAGENTA: Final[str] = "#C860FF"
    PINK: Final[str] = "#F162EF"
    ROSE: Final[str] = "#FF609F"


class CHARS:
    """Character set constants for text validation and filtering."""

    ALL: Final[AllTextChars] = AllTextChars()
    """Sentinel value indicating all characters are allowed."""

    DIGITS: Final[str] = "0123456789"
    """Numeric digits: `0`-`9`"""
    FLOAT_DIGITS: Final[str] = "." + DIGITS
    """Numeric digits with decimal point: `0`-`9` and `.`"""
    HEX_DIGITS: Final[str] = "#" + DIGITS + "abcdefABCDEF"
    """Hexadecimal digits: `0`-`9`, `a`-`f`, `A`-`F`, and `#`"""

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

    CHAR_ESCAPED: Final[str] = r"\x1b"
    """Printable ANSI escape character."""
    CHAR: Final[str] = "\x1b"
    """ANSI escape character."""

    SEQ_FG_COLOR: Final[FormattableString] = f"{CHAR}[38;2;{{}};{{}};{{}}m"
    """RGB foreground color sequence with placeholders for red, green, and blue values."""
    SEQ_BG_COLOR: Final[FormattableString] = f"{CHAR}[48;2;{{}};{{}};{{}}m"
    """RGB background color sequence with placeholders for red, green, and blue values."""

    SEQ_LINK_OPEN: Final[FormattableString] = f"{CHAR}]8;;{{}}{CHAR}\\"
    """OSC 8 hyperlink opening sequence with a placeholder for the URL."""
    SEQ_LINK_CLOSE: Final[str] = f"{CHAR}]8;;{CHAR}\\"
    """OSC 8 hyperlink closing sequence."""

    SEQ_PATTERN: Final[Pattern[str]] = _rx.compile(CHAR + r"(?:\].*?(?:\x1b\\|\x07)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_])")
    """Compiled regex pattern matching any ANSI escape sequence (CSI, OSC, or single-character)."""
