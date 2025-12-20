"""
This module contains constant values used throughout the library.
"""

from .types import FormattableString, AllTextChars

from typing import Final


class COLOR:
    """Hexadecimal color presets."""

    WHITE: Final = "#F1F2FF"
    LIGHT_GRAY: Final = "#B6B7C0"
    GRAY: Final = "#7B7C8D"
    DARK_GRAY: Final = "#67686C"
    BLACK: Final = "#202125"
    RED: Final = "#FF606A"
    CORAL: Final = "#FF7069"
    ORANGE: Final = "#FF876A"
    TANGERINE: Final = "#FF9962"
    GOLD: Final = "#FFAF60"
    YELLOW: Final = "#FFD260"
    LIME: Final = "#C9F16E"
    GREEN: Final = "#7EE787"
    NEON_GREEN: Final = "#4CFF85"
    TEAL: Final = "#50EAAF"
    CYAN: Final = "#3EDEE6"
    ICE: Final = "#77DBEF"
    LIGHT_BLUE: Final = "#60AAFF"
    BLUE: Final = "#8085FF"
    LAVENDER: Final = "#9B7DFF"
    PURPLE: Final = "#AD68FF"
    MAGENTA: Final = "#C860FF"
    PINK: Final = "#F162EF"
    ROSE: Final = "#FF609F"


class CHARS:
    """Character set constants for text validation and filtering."""

    ALL: Final = AllTextChars()
    """Sentinel value indicating all characters are allowed."""

    DIGITS: Final = "0123456789"
    """Numeric digits: `0`-`9`"""
    FLOAT_DIGITS: Final = "." + DIGITS
    """Numeric digits with decimal point: `0`-`9` and `.`"""
    HEX_DIGITS: Final = "#" + DIGITS + "abcdefABCDEF"
    """Hexadecimal digits: `0`-`9`, `a`-`f`, `A`-`F`, and `#`"""

    LOWERCASE: Final = "abcdefghijklmnopqrstuvwxyz"
    """Lowercase ASCII letters: `a`-`z`"""
    LOWERCASE_EXTENDED: Final = LOWERCASE + "äëïöüÿàèìòùáéíóúýâêîôûãñõåæç"
    """Lowercase ASCII letters with diacritic marks."""
    UPPERCASE: Final = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    """Uppercase ASCII letters: `A`-`Z`"""
    UPPERCASE_EXTENDED: Final = UPPERCASE + "ÄËÏÖÜÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÅÆÇß"
    """Uppercase ASCII letters with diacritic marks."""

    LETTERS: Final = LOWERCASE + UPPERCASE
    """All ASCII letters: `a`-`z` and `A`-`Z`"""
    LETTERS_EXTENDED: Final = LOWERCASE_EXTENDED + UPPERCASE_EXTENDED
    """All ASCII letters with diacritic marks."""

    SPECIAL_ASCII: Final = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    """Standard ASCII special characters and symbols."""
    SPECIAL_ASCII_EXTENDED: Final = SPECIAL_ASCII + "ø£Ø×ƒªº¿®¬½¼¡«»░▒▓│┤©╣║╗╝¢¥┐└┴┬├─┼╚╔╩╦╠═╬¤ðÐı┘┌█▄¦▀µþÞ¯´≡­±‗¾¶§÷¸°¨·¹³²■ "
    """Standard and extended ASCII special characters."""
    STANDARD_ASCII: Final = DIGITS + LETTERS + SPECIAL_ASCII
    """All standard ASCII characters (letters, digits, and symbols)."""
    FULL_ASCII: Final = DIGITS + LETTERS_EXTENDED + SPECIAL_ASCII_EXTENDED
    """Complete ASCII character set including extended characters."""


class ANSI:
    """Constants and utilities for ANSI escape code sequences."""

    ESCAPED_CHAR: Final = "\\x1b"
    """Printable ANSI escape character."""
    CHAR: Final = "\x1b"
    """ANSI escape character."""
    START: Final = "["
    """Start of an ANSI escape sequence."""
    SEP: Final = ";"
    """Separator between ANSI escape sequence parts."""
    END: Final = "m"
    """End of an ANSI escape sequence."""

    @classmethod
    def seq(cls, placeholders: int = 1) -> FormattableString:
        """Generates an ANSI escape sequence with the specified number of placeholders."""
        return cls.CHAR + cls.START + cls.SEP.join(["{}" for _ in range(placeholders)]) + cls.END

    SEQ_COLOR: Final[FormattableString] = CHAR + START + "38" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """ANSI escape sequence with three placeholders for setting the RGB text color."""
    SEQ_BG_COLOR: Final[FormattableString] = CHAR + START + "48" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """ANSI escape sequence with three placeholders for setting the RGB background color."""

    COLOR_MAP: Final[tuple[str, ...]] = (
        ########### DEFAULT CONSOLE COLOR NAMES ############
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
    )
    """The standard terminal color names."""

    CODES_MAP: Final[dict[str | tuple[str, ...], int]] = {
        ################# SPECIFIC RESETS ##################
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
        ################### TEXT STYLES ####################
        ("bold", "b"): 1,
        ("dim", "d"): 2,
        ("italic", "i"): 3,
        ("underline", "u"): 4,
        ("inverse", "invert", "in"): 7,
        ("hidden", "hide", "h"): 8,
        ("strikethrough", "s"): 9,
        ("double-underline", "du"): 21,
        ################## DEFAULT COLORS ##################
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        ############## BRIGHT DEFAULT COLORS ###############
        "br:black": 90,
        "br:red": 91,
        "br:green": 92,
        "br:yellow": 93,
        "br:blue": 94,
        "br:magenta": 95,
        "br:cyan": 96,
        "br:white": 97,
        ############ DEFAULT BACKGROUND COLORS #############
        "bg:black": 40,
        "bg:red": 41,
        "bg:green": 42,
        "bg:yellow": 43,
        "bg:blue": 44,
        "bg:magenta": 45,
        "bg:cyan": 46,
        "bg:white": 47,
        ######### BRIGHT DEFAULT BACKGROUND COLORS #########
        "bg:br:black": 100,
        "bg:br:red": 101,
        "bg:br:green": 102,
        "bg:br:yellow": 103,
        "bg:br:blue": 104,
        "bg:br:magenta": 105,
        "bg:br:cyan": 106,
        "bg:br:white": 107,
    }
    """Dictionary mapping format keys to their corresponding ANSI code numbers."""
