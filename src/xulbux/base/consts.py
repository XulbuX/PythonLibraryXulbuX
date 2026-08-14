# ruff:file-ignore[ambiguous-unicode-character-string]

"""
Provides constant values used throughout the library.

Includes color hex codes, ANSI sequences,
character sets, and default styling settings.
"""

from .decorators import deprecated
from .types import AllTextChars, FormattableString

from typing import Annotated, Final
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

    START: Final[
        Annotated[
            str,
            deprecated(
                "Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead. "
                "This will be completely removed in an upcoming update."
            ),
        ]
    ] = "["
    """**DEPRECATED** – Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead.
    This will be completely removed in an upcoming update.\n
    Start of an ANSI escape sequence."""
    SEP: Final[
        Annotated[
            str,
            deprecated(
                "Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead. "
                "This will be completely removed in an upcoming update."
            ),
        ]
    ] = ";"
    """**DEPRECATED** – Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead.
    This will be completely removed in an upcoming update.\n
    Separator between ANSI escape sequence parts."""
    END: Final[
        Annotated[
            str,
            deprecated(
                "Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead. "
                "This will be completely removed in an upcoming update."
            ),
        ]
    ] = "m"
    """**DEPRECATED** – Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead.
    This will be completely removed in an upcoming update.\n
    End of an ANSI escape sequence."""

    @classmethod
    @deprecated(
        "Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead. "
        "This will be completely removed in an upcoming update."
    )
    def seq(cls, placeholders: int = 1, /) -> FormattableString:
        """**DEPRECATED** – Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead.
        This will be completely removed in an upcoming update.\n
        Generates an ANSI escape sequence with the specified number of placeholders."""

        return cls.CHAR + cls.START + cls.SEP.join(["{}" for _ in range(placeholders)]) + cls.END

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

    COLOR_MAP: Final[
        Annotated[
            set[str],
            deprecated(
                "Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead. "
                "This will be completely removed in an upcoming update."
            ),
        ]
    ] = {"black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"}
    """**DEPRECATED** – Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead.
    This will be completely removed in an upcoming update.\n
    The standard terminal color names."""

    COLOR_VARIANTS_MAP: Final[
        Annotated[
            set[str],
            deprecated(
                "Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead. "
                "This will be completely removed in an upcoming update."
            ),
        ]
    ] = COLOR_MAP | {"br:black", "br:red", "br:green", "br:yellow", "br:blue", "br:magenta", "br:cyan", "br:white"}
    """**DEPRECATED** – Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead.
    This will be completely removed in an upcoming update.\n
    All color variants that can be used in formatting."""

    CODES_MAP: Final[
        Annotated[
            dict[str | tuple[str, ...], int],
            deprecated(
                "Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead. "
                "This will be completely removed in an upcoming update."
            ),
        ]
    ] = {
        # ***************** SPECIFIC RESETS ******************
        "_": 0,
        ("_bold", "_b"): 22,
        ("_dim", "_d"): 22,
        ("_italic", "_i"): 23,
        ("_underline", "_u"): 24,
        ("_double-underline", "_du"): 24,
        ("_inverse", "_invert", "_in"): 27,
        ("_hidden", "_hide", "_h"): 28,
        ("_strikethrough", "_s"): 29,
        ("_color", "_c"): 39,
        ("_background", "_bg"): 49,
        # ******************* TEXT STYLES ********************
        ("bold", "b"): 1,
        ("dim", "d"): 2,
        ("italic", "i"): 3,
        ("underline", "u"): 4,
        ("inverse", "invert", "in"): 7,
        ("hidden", "hide", "h"): 8,
        ("strikethrough", "s"): 9,
        ("double-underline", "du"): 21,
        # ****************** DEFAULT COLORS ******************
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        # ************** BRIGHT DEFAULT COLORS ***************
        "br:black": 90,
        "br:red": 91,
        "br:green": 92,
        "br:yellow": 93,
        "br:blue": 94,
        "br:magenta": 95,
        "br:cyan": 96,
        "br:white": 97,
        # ************ DEFAULT BACKGROUND COLORS *************
        "bg:black": 40,
        "bg:red": 41,
        "bg:green": 42,
        "bg:yellow": 43,
        "bg:blue": 44,
        "bg:magenta": 45,
        "bg:cyan": 46,
        "bg:white": 47,
        # ********* BRIGHT DEFAULT BACKGROUND COLORS *********
        "bg:br:black": 100,
        "bg:br:red": 101,
        "bg:br:green": 102,
        "bg:br:yellow": 103,
        "bg:br:blue": 104,
        "bg:br:magenta": 105,
        "bg:br:cyan": 106,
        "bg:br:white": 107,
    }
    """**DEPRECATED** – Use the operator-based API in `xulbux.ansi` (`StyledText`, `S`, `Term`) instead.
    This will be completely removed in an upcoming update.\n
    Dictionary mapping format keys to their corresponding ANSI code numbers."""
